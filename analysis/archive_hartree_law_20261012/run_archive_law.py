#!/usr/bin/env python3
"""Run the frozen Hartree-contract archive-law study for one MP object.

The scientific loader and writer primitives are imported from the frozen WP-F
and general-law implementations.  This runner deliberately evaluates only
the law (A1) and pointwise (A6) arms named by the archive-law protocol.
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import os
import sys
import tempfile
import time
import traceback
import zlib
from pathlib import Path
from typing import Any, Iterable

import numpy as np

try:
    import resource  # type: ignore
except ImportError:  # pragma: no cover - Windows has no resource module.
    resource = None  # type: ignore


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WP_F_DIR = REPO / "analysis" / "extensions_20260930" / "WP-F"
LAW_DIR = REPO / "analysis" / "general_qoac_law"
if str(WP_F_DIR) not in sys.path:
    sys.path.insert(0, str(WP_F_DIR))
if str(LAW_DIR) not in sys.path:
    sys.path.insert(0, str(LAW_DIR))

# These imports are intentional: they are the frozen loader/seeds and the
# exact law-run module imported by general_qoac_law.run_part_a.
import run_wpf as wpf  # type: ignore  # noqa: E402
import run_part_a as law_part_a  # type: ignore  # noqa: E402


ENG = law_part_a.eng
TAUS = (1e-4, 1e-6, 1e-8)
CODECS = ("zfp", "sz3", "sperr")
MANIFEST_NAME = "MANIFEST.tsv"


class ArchiveFailure(RuntimeError):
    """An input-side failure that should be recorded as a download failure."""

    category = "download"


def tau_key(tau: float) -> str:
    return str(float(tau))


def sample_csv_path(path: Path | None = None) -> Path:
    return (path or (REPO / "analysis" / "extensions_20260930" / "WP-F" / "sample.csv")).resolve()


def load_tasks(path: Path | None = None) -> list[dict[str, str]]:
    """Return the frozen WP-F sample in committed order."""
    with sample_csv_path(path).open(newline="", encoding="utf-8") as handle:
        tasks = list(csv.DictReader(handle))
    if len(tasks) != 300:
        raise ValueError(f"expected 300 WP-F sample tasks, found {len(tasks)}")
    required = {"stratum", "rank_in_stratum", "task_id", "key", "bytes", "url"}
    if not tasks or not required.issubset(tasks[0]):
        raise ValueError(f"sample.csv is missing required columns: {sorted(required)}")
    if len({row["task_id"] for row in tasks}) != 300:
        raise ValueError("sample.csv task_id values are not unique")
    return tasks


def list_task_lines(tasks: Iterable[dict[str, str]]) -> list[str]:
    """Format task ids and strata for the Vanda task-list files."""
    return [f"{row['task_id']}\t{row['stratum']}" for row in tasks]


def read_manifest(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise ArchiveFailure(f"prefetch manifest not found: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        task_id = row.get("task_id", "")
        if task_id:
            out[task_id] = row
    return out


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def read_prefetched(task: dict[str, str], inputs: Path) -> tuple[bytes, dict[str, str]]:
    """Read and verify one staged object against MANIFEST.tsv and sample.csv."""
    manifest = read_manifest(inputs / MANIFEST_NAME)
    row = manifest.get(task["task_id"])
    if row is None:
        raise ArchiveFailure(f"task is absent from prefetch manifest: {task['task_id']}")
    expected = int(task["bytes"])
    manifest_expected = int(row.get("expected_bytes", "-1"))
    if manifest_expected != expected:
        raise ArchiveFailure(
            f"manifest expected bytes disagree with sample: {manifest_expected} != {expected}"
        )
    if row.get("status", "OK") != "OK":
        raise ArchiveFailure(f"prefetch status is {row.get('status')!r}")
    relpath = row.get("path") or f"{task['task_id']}.json.gz"
    source = (inputs / relpath).resolve()
    if source.parent != inputs.resolve():
        raise ArchiveFailure(f"manifest path escapes inputs directory: {relpath!r}")
    if not source.is_file():
        raise ArchiveFailure(f"prefetched object not found: {source}")
    blob = source.read_bytes()
    actual_bytes = len(blob)
    actual_sha = sha256_bytes(blob)
    manifest_bytes = int(row.get("actual_bytes", "-1"))
    manifest_sha = row.get("sha256", "").lower()
    if actual_bytes != manifest_bytes:
        raise ArchiveFailure(f"prefetch byte-count mismatch: {actual_bytes} != {manifest_bytes}")
    if actual_sha != manifest_sha:
        raise ArchiveFailure(f"prefetch SHA-256 mismatch: {actual_sha} != {manifest_sha}")
    if actual_bytes != expected:
        raise ArchiveFailure(f"sample byte-count mismatch: {actual_bytes} != {expected}")
    return blob, row


def peak_rss_bytes() -> int:
    if resource is None:
        return 0
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # Linux reports KiB; macOS reports bytes.  Vanda is Linux.
    return value * 1024 if sys.platform.startswith("linux") else value


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(temp, path)


def failure_category(stage: str, exc: BaseException) -> str:
    if isinstance(exc, MemoryError):
        return "memory"
    if isinstance(exc, (TimeoutError,)):  # explicit per-object walltime guards.
        return "walltime"
    if stage in {"manifest", "download"}:
        return "download"
    if stage in {"load", "parse"}:
        return "parse"
    if stage in {"load_memory", "qsq_memory"}:
        return "memory"
    if stage == "qsq":
        return "qsq"
    if stage.startswith("writer") or stage in {"A1", "A6"}:
        return "solver"
    if stage == "worker":
        return "worker"
    return stage or "other"


def failure_record(task: dict[str, str], stage: str, exc: BaseException) -> dict[str, Any]:
    return {
        "task_id": task["task_id"],
        "stratum": task["stratum"],
        "stage": stage,
        "category": failure_category(stage, exc),
        "error": f"{type(exc).__name__}: {exc}",
    }


def stored_bytes(
    *,
    status: str,
    eligible: bool | None,
    certified_bytes: int | None,
    lossless_bytes: int,
    frame_bytes: int,
) -> tuple[int, str]:
    """Apply protocol §5 for one writer at one tolerance."""
    if status != "SUCCESS":
        return int(frame_bytes), "failed: current MP json.gz"
    if eligible is True and certified_bytes is not None:
        return int(certified_bytes), "certified stream"
    if eligible is True:
        return int(lossless_bytes), "lossless (eligible, none certified)"
    return int(lossless_bytes), "lossless (non-evaluable)"


def initialize_runtime(repo_root: Path, frozen_validation_dir: Path) -> tuple[Any, Any]:
    """Initialize the same WP-F external loader stack used by run_wpf.py."""
    wpf.REPO = repo_root.resolve()
    wpf.FROZEN_VALIDATION = frozen_validation_dir.resolve()
    wpf._CORE = None
    wpf._DEV = None
    wpf._init()
    return wpf._CORE, wpf._DEV


def qsq_floor(
    field: np.ndarray,
    lattice: np.ndarray,
    seeds: Iterable[int] = wpf.SEEDS,
) -> dict[str, Any]:
    """Compute the Hartree QSQ floor with the frozen WP-F five probes."""
    ref_h, ref_s = ENG.v02.reference_hartree_rms(field, lattice)
    epsilon = float(np.max(np.abs(field.astype(np.float32).astype(np.float64) - field)))
    probes = []
    for seed in seeds:
        noise = np.random.Generator(np.random.PCG64(seed)).uniform(
            -epsilon, epsilon, size=field.shape
        )
        eh, es, _, _ = ENG.certify(field + noise, field, lattice, ref_h, ref_s)
        probes.append(
            {
                "seed": int(seed),
                "hartree_historical": float(eh),
                "hartree_safe": float(es),
                "response": float(max(eh, es)),
            }
        )
        del noise
    floor = max((probe["response"] for probe in probes), default=0.0)
    return {
        "reference_rms_historical": float(ref_h),
        "reference_rms_safe": float(ref_s),
        "epsilon": epsilon,
        "floor_hartree": float(floor),
        "probes": probes,
    }


def writer_row(
    *,
    writer: str,
    tau: float,
    rec: np.ndarray,
    raw_bytes: int,
    stream_bytes: int,
    field: np.ndarray,
    lattice: np.ndarray,
    ref_h: float,
    ref_s: float,
    parameter: str,
    seconds: float,
    codec: str = "",
) -> dict[str, Any]:
    eh, es, linf, rmse = ENG.certify(rec, field, lattice, ref_h, ref_s)
    return {
        "writer": writer,
        "tau": float(tau),
        "certified": bool(eh < tau and es < tau),
        "stream_bytes": int(stream_bytes),
        "cr": float(raw_bytes / stream_bytes),
        "hartree_historical": float(eh),
        "hartree_safe": float(es),
        "density_linf": float(linf),
        "density_rmse": float(rmse),
        "parameter": parameter,
        "codec": codec,
        "seconds": float(seconds),
    }


def prepare_law(field: np.ndarray, lattice: np.ndarray, ref_h: float) -> tuple[Any, Any]:
    """Prepare A1 exactly as the law run prepares its operator analysis."""
    analysis = ENG.v3.analyze(
        field,
        lattice,
        prior="operator",
        reference_historical_rms=ref_h,
        d_floor_rel=1e-3 * min(ENG.TAUS) ** 2 / 32,
    )
    spec = ENG.Spec(analysis.prep, analysis.ref_cons_spec, analysis.ref_safe_spec)
    return analysis, spec


def run_law_writer(
    *,
    field: np.ndarray,
    lattice: np.ndarray,
    ptp: float,
    tau: float,
    ref_h: float,
    ref_s: float,
    analysis: Any,
    spec: Any,
    work: Path,
) -> dict[str, Any] | None:
    """Run only the A1 continuous-alpha path from run_engineering.material."""
    prep = analysis.prep
    q2 = prep.topology.q**2
    t0 = time.time()
    alpha = ENG.bisect_scale(
        lambda scale: spec.ok(scale * q2, tau),
        1e-14 * ptp,
        1e3 * ptp,
    )
    if alpha is None:
        return None
    for _ in range(40):
        blob, _ = ENG.v02.encode_prepared(prep, alpha=alpha, beta=2.0, zlib_level=6)
        rec, _, _ = ENG.v02.decode_blob(blob)
        row = writer_row(
            writer="L",
            tau=tau,
            rec=np.asarray(rec, dtype=np.float64),
            raw_bytes=int(field.nbytes),
            stream_bytes=len(blob),
            field=field,
            lattice=lattice,
            ref_h=ref_h,
            ref_s=ref_s,
            parameter=f"alpha_rel={alpha / ptp:.9g}",
            seconds=time.time() - t0,
        )
        if row["certified"]:
            return row
        alpha *= 0.99
    return None


def run_pointwise_writer(
    *,
    core: Any,
    field: np.ndarray,
    lattice: np.ndarray,
    ptp: float,
    tau: float,
    ref_h: float,
    ref_s: float,
    work: Path,
    failures: list[dict[str, Any]],
    task: dict[str, str],
) -> dict[str, Any] | None:
    """Run only the A6 equal-search pointwise paths and select the best CR."""
    candidates = []
    for codec in CODECS:
        t0 = time.time()
        seen: dict[float, tuple[int, np.ndarray]] = {}

        def okc(abs_tol: float) -> bool:
            rec, nbytes, _ = core.codec_roundtrip(codec, field, float(abs_tol), work)
            rec = np.asarray(rec, dtype=np.float64)
            eh, es = ENG.v02.hartree_error_metrics(rec - field, lattice, ref_h, ref_s)
            good = bool(eh < tau and es < tau)
            if good:
                seen[float(abs_tol)] = (int(nbytes), rec)
            return good

        try:
            ENG.bisect_scale(okc, 1e-14 * ptp, 1.0 * ptp)
            if seen:
                abs_tol = max(seen, key=lambda value: field.nbytes / seen[value][0])
                nbytes, rec = seen[abs_tol]
                row = writer_row(
                    writer="P",
                    tau=tau,
                    rec=rec,
                    raw_bytes=int(field.nbytes),
                    stream_bytes=nbytes,
                    field=field,
                    lattice=lattice,
                    ref_h=ref_h,
                    ref_s=ref_s,
                    parameter=f"codec={codec};abs_tol_rel={abs_tol / ptp:.9g}",
                    codec=codec.upper(),
                    seconds=time.time() - t0,
                )
                if row["certified"]:
                    candidates.append(row)
        except MemoryError:
            raise
        except Exception as exc:  # one codec failure does not erase other A6 codecs.
            failures.append(failure_record(task, f"writer_A6_{codec}", exc))
        finally:
            gc.collect()
    return max(candidates, key=lambda row: row["cr"]) if candidates else None


def finalize_result(out: dict[str, Any], checkpoint: Path, started: float) -> dict[str, Any]:
    out["wall_seconds"] = float(time.time() - started)
    out["peak_rss_bytes"] = peak_rss_bytes()
    out["complete"] = True
    atomic_json(checkpoint, out)
    return out


def run_task(
    task: dict[str, str],
    *,
    inputs: Path,
    checkpoints: Path,
    repo_root: Path,
    frozen_validation_dir: Path,
    force: bool = False,
) -> dict[str, Any]:
    """Run one task and atomically write its terminal checkpoint."""
    checkpoint = checkpoints / f"{task['task_id']}.json"
    if checkpoint.exists() and not force:
        try:
            old = json.loads(checkpoint.read_text(encoding="utf-8"))
            if old.get("complete") is True:
                print(f"SKIP {task['task_id']} checkpoint complete", flush=True)
                return old
        except Exception:
            pass

    started = time.time()
    out: dict[str, Any] = {
        "task_id": task["task_id"],
        "stratum": task["stratum"],
        "key": task["key"],
        "frame_bytes": int(task["bytes"]),
        "status": "SUCCESS",
        "failures": [],
        "writers": {},
        "storage": {},
    }

    try:
        blob, manifest_row = read_prefetched(task, inputs)
        out.update(
            json_bytes=len(blob),
            source_sha256=manifest_row.get("sha256"),
            size_matches_frame=True,
        )
    except Exception as exc:
        out["status"] = "FAILED"
        out["failures"].append(failure_record(task, "download", exc))
        out["json_bytes"] = int(task["bytes"])
        for tau in TAUS:
            out["storage"][tau_key(tau)] = {"L": int(task["bytes"]), "P": int(task["bytes"])}
        return finalize_result(out, checkpoint, started)

    try:
        core, dev = initialize_runtime(repo_root, frozen_validation_dir)
    except Exception as exc:
        out["status"] = "FAILED"
        out["failures"].append(failure_record(task, "load", exc))
        for tau in TAUS:
            out["storage"][tau_key(tau)] = {"L": int(task["bytes"]), "P": int(task["bytes"])}
        return finalize_result(out, checkpoint, started)

    try:
        with tempfile.TemporaryDirectory(prefix="qoi_archive_law_") as temp_dir:
            work = Path(temp_dir)
            grid, _ = dev.build_grid(
                {"source": "Materials Project", "url": task["url"]}, blob, work
            )
            del blob
            field = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
            if not np.all(np.isfinite(field)):
                raise ValueError("non-finite reference field")
            lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)
            ptp = float(np.ptp(field))
            if not np.isfinite(ptp) or ptp <= 0.0:
                raise ValueError(f"invalid field peak-to-peak value: {ptp}")
            out.update(
                shape="x".join(map(str, field.shape)),
                npoints=int(field.size),
                natoms=int(len(grid.structure)),
                raw64_bytes=int(8 * field.size),
                lossless_bytes=len(zlib.compress(np.ascontiguousarray(field).tobytes(), 6)),
            )
            # This is the frozen WP-F epsilon expression, applied to the same field.
            out["epsilon"] = float(
                np.max(np.abs(field.astype(np.float32).astype(np.float64) - field))
            )
    except MemoryError as exc:
        out["status"] = "FAILED"
        out["failures"].append(failure_record(task, "load_memory", exc))
        for tau in TAUS:
            out["storage"][tau_key(tau)] = {"L": int(task["bytes"]), "P": int(task["bytes"])}
        return finalize_result(out, checkpoint, started)
    except Exception as exc:
        out["status"] = "FAILED"
        out["failures"].append(failure_record(task, "load", exc))
        for tau in TAUS:
            out["storage"][tau_key(tau)] = {"L": int(task["bytes"]), "P": int(task["bytes"])}
        return finalize_result(out, checkpoint, started)

    try:
        qsq = qsq_floor(field, lattice)
        out.update(qsq)
        floor = float(qsq["floor_hartree"])
        out["eligible"] = {tau_key(tau): bool(floor < tau) for tau in TAUS}
    except MemoryError as exc:
        out["status"] = "FAILED"
        out["failures"].append(failure_record(task, "qsq_memory", exc))
        for tau in TAUS:
            out["storage"][tau_key(tau)] = {"L": int(task["bytes"]), "P": int(task["bytes"])}
        return finalize_result(out, checkpoint, started)
    except Exception as exc:
        out["status"] = "FAILED"
        out["failures"].append(failure_record(task, "qsq", exc))
        for tau in TAUS:
            out["storage"][tau_key(tau)] = {"L": int(task["bytes"]), "P": int(task["bytes"])}
        return finalize_result(out, checkpoint, started)

    # A1's spectral preparation is shared across the three tolerance searches.
    law_analysis = law_spec = None
    try:
        law_analysis, law_spec = prepare_law(
            field, lattice, float(qsq["reference_rms_historical"])
        )
    except MemoryError as exc:
        out["status"] = "FAILED"
        out["failures"].append(failure_record(task, "writer_A1_memory", exc))
    except Exception as exc:
        out["failures"].append(failure_record(task, "writer_A1", exc))

    try:
        with tempfile.TemporaryDirectory(prefix="qoi_archive_law_writers_") as temp_dir:
            work = Path(temp_dir)
            for tau in TAUS:
                key = tau_key(tau)
                out["writers"][key] = {"L": None, "P": None}
                if out["eligible"][key]:
                    if law_analysis is not None and law_spec is not None:
                        try:
                            out["writers"][key]["L"] = run_law_writer(
                                field=field,
                                lattice=lattice,
                                ptp=ptp,
                                tau=tau,
                                ref_h=float(qsq["reference_rms_historical"]),
                                ref_s=float(qsq["reference_rms_safe"]),
                                analysis=law_analysis,
                                spec=law_spec,
                                work=work,
                            )
                        except MemoryError as exc:
                            out["status"] = "FAILED"
                            out["failures"].append(failure_record(task, "writer_A1_memory", exc))
                            break
                        except Exception as exc:
                            out["failures"].append(failure_record(task, "writer_A1", exc))
                    try:
                        out["writers"][key]["P"] = run_pointwise_writer(
                            core=core,
                            field=field,
                            lattice=lattice,
                            ptp=ptp,
                            tau=tau,
                            ref_h=float(qsq["reference_rms_historical"]),
                            ref_s=float(qsq["reference_rms_safe"]),
                            work=work,
                            failures=out["failures"],
                            task=task,
                        )
                    except MemoryError as exc:
                        out["status"] = "FAILED"
                        out["failures"].append(failure_record(task, "writer_A6_memory", exc))
                        break
                    except Exception as exc:
                        out["failures"].append(failure_record(task, "writer_A6", exc))

                row_l = out["writers"][key]["L"]
                row_p = out["writers"][key]["P"]
                out["storage"][key] = {
                    "L": stored_bytes(
                        status=out["status"],
                        eligible=out["eligible"][key],
                        certified_bytes=(int(row_l["stream_bytes"]) if row_l and row_l["certified"] else None),
                        lossless_bytes=int(out["lossless_bytes"]),
                        frame_bytes=int(task["bytes"]),
                    )[0],
                    "P": stored_bytes(
                        status=out["status"],
                        eligible=out["eligible"][key],
                        certified_bytes=(int(row_p["stream_bytes"]) if row_p and row_p["certified"] else None),
                        lossless_bytes=int(out["lossless_bytes"]),
                        frame_bytes=int(task["bytes"]),
                    )[0],
                }
            del law_analysis, law_spec
            gc.collect()
    except MemoryError as exc:
        out["status"] = "FAILED"
        out["failures"].append(failure_record(task, "writer_memory", exc))
        for tau in TAUS:
            out["storage"][tau_key(tau)] = {"L": int(task["bytes"]), "P": int(task["bytes"])}
    except Exception as exc:
        out["status"] = "FAILED"
        out["failures"].append(failure_record(task, "writer", exc))
        for tau in TAUS:
            out["storage"][tau_key(tau)] = {"L": int(task["bytes"]), "P": int(task["bytes"])}

    if out["status"] != "SUCCESS":
        for tau in TAUS:
            out["storage"][tau_key(tau)] = {
                "L": int(task["bytes"]),
                "P": int(task["bytes"]),
            }

    return finalize_result(out, checkpoint, started)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id")
    parser.add_argument("--list-tasks", action="store_true")
    parser.add_argument("--sample-csv", type=Path)
    parser.add_argument("--stratum", choices=("D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10a", "D10b", "D10c"))
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--checkpoints", type=Path, default=HERE / "checkpoints")
    parser.add_argument("--repo-root", type=Path, default=REPO)
    parser.add_argument("--frozen-validation-dir", type=Path)
    parser.add_argument("--force", action="store_true", help="rerun even when a complete checkpoint exists")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = load_tasks(args.sample_csv)
    if args.list_tasks:
        for line in list_task_lines(tasks):
            task_id, stratum = line.split("\t")
            if args.stratum is None or stratum == args.stratum:
                print(line)
        return 0
    if not args.task_id:
        raise SystemExit("--task-id is required unless --list-tasks is used")
    if args.inputs is None:
        raise SystemExit("--inputs is required for a task run")
    if args.frozen_validation_dir is None:
        raise SystemExit("--frozen-validation-dir is required for a task run")
    task_by_id = {task["task_id"]: task for task in tasks}
    if args.task_id not in task_by_id:
        raise SystemExit(f"unknown WP-F task id: {args.task_id}")
    result = run_task(
        task_by_id[args.task_id],
        inputs=args.inputs.resolve(),
        checkpoints=args.checkpoints.resolve(),
        repo_root=args.repo_root.resolve(),
        frozen_validation_dir=args.frozen_validation_dir.resolve(),
        force=args.force,
    )
    print(
        f"{result['task_id']} {result['status']} wall={result.get('wall_seconds', 0):.1f}s "
        f"rss={result.get('peak_rss_bytes', 0)} floor={result.get('floor_hartree')}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
