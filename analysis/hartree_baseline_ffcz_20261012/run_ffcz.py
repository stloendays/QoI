#!/usr/bin/env python3
"""Run the frozen FFCz Hartree-baseline search, one material/configuration at a time."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import tempfile
import time
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np


HERE = Path(__file__).resolve().parent
REPO_DEFAULT = HERE.parents[1]
sys.path.insert(0, str(REPO_DEFAULT / "analysis" / "qoac_v03_rdo"))
sys.path.insert(0, str(REPO_DEFAULT / "validation" / "qsq_prospective"))
import run_engineering as eng  # noqa: E402

import codecs_ffcz as C  # noqa: E402


TAUS = (1e-4, 1e-6, 1e-8)
INTERVALS = {"REL": (1e-14, 1.0), "PTW": (1e-14, 10.0)}
INTERVAL = INTERVALS
LO_ERROR_CAP = 1e-2
FRESH = "analysis/fresh_population_20261006"
LAW = "analysis/general_qoac_law/results"
BP = "analysis/hartree_baselines_mgard_qpet_20261007/results"
COHORTS = {
    "P1_CONFIRMATORY": f"{FRESH}/P1_CONFIRMATORY_MANIFEST.csv",
    "P3B_CONFIRMATORY": f"{FRESH}/P3B_CONFIRMATORY_MANIFEST.csv",
}
SHAKEDOWN = (f"{FRESH}/P1_ENGINEERING_MANIFEST.csv", "mp-3148759")

# The exact LF-byte SHA-256 table frozen in FFCz PROTOCOL.md §9.
INPUT_SHA256 = {
    f"{FRESH}/P1_CONFIRMATORY_MANIFEST.csv": "3297d6c17959c7a70bf157f7157283f45ddb046fdc460acaa8a8570ab4de7331",
    f"{FRESH}/P3B_CONFIRMATORY_MANIFEST.csv": "e7c447d5f8dc3b263c7b5b4b9d1f8344ad9c8ed41e5b72fa333c37ad14b70f97",
    f"{FRESH}/P1_ENGINEERING_MANIFEST.csv": "480bc38667544eb4023276ad9def91eff451b4f1dbccb7cde76fb707b66fd6a9",
    f"{LAW}/run_P1_CONFIRMATORY/part_a_material.csv": "5760ae206af28c4d916088ce4ab8061053975934ea38f58904e34aa12bfb715e",
    f"{LAW}/run_P3B_CONFIRMATORY/part_a_material.csv": "cee4ec409461573f79716ef34279b6bab38416b9054b21620facb0837ecad2f1",
    f"{BP}/run_P1_CONFIRMATORY/material.csv": "ff5e1a030ca5a53720f2e8214821638ef1081ec1e970dd2a2d294ed618e2fea5",
    f"{BP}/run_P3B_CONFIRMATORY/material.csv": "f8ac369450119243e30bb27b8bde4eb6b8586a113394bb802181012fc01b15ba",
    "analysis/hartree_baselines_mgard_qpet_20261007/run_mq.py": "ff14686adfe584073705fd7f82f92b4623c49082d2b2c989b2dbdbb2f8d03467",
    "analysis/qoac_v03_rdo/run_engineering.py": "6cbdf8e31b4749cebb65a78582a8bec3032baf89073524b9c21065b65a7f3123",
    "analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py": "f78dd40aba7f2a25727d4df08d621f3456244bfb14f404423551900c3504ce1a",
    "validation/qsq_prospective/development_compatibility_smoke.py": "d51a31d7838d09175292e5024e7f969347c4de2e011446f6de863f2f3c0683bf",
}


@dataclass(frozen=True)
class Config:
    config_id: str
    codec: str
    eps_rel: float
    mode: str


def _eps_label(value: float) -> str:
    return {1e-2: "1e-2", 1e-3: "1e-3", 1e-4: "1e-4"}[float(value)]


CONFIGS = tuple(
    Config(f"{codec.upper()}_eb{_eps_label(eps)}_{mode}", codec, eps, mode)
    for codec in ("zfp", "sz3", "sperr")
    for eps in (1e-2, 1e-3, 1e-4)
    for mode in ("REL", "PTW")
)
CONFIG_BY_ID = {config.config_id: config for config in CONFIGS}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def check_inputs(repo: Path) -> list[str]:
    errors = []
    for relative, expected in INPUT_SHA256.items():
        path = Path(repo) / relative
        if not path.is_file():
            errors.append(f"{relative}: missing")
            continue
        actual = lf_sha256(path)
        if actual != expected:
            errors.append(f"{relative}: {actual} != {expected}")
    return errors


def _read_manifest(repo: Path, relative: str) -> list[dict[str, str]]:
    with (Path(repo) / relative).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def manifest_ids(repo: Path, phase: str) -> list[str]:
    if phase == "probe":
        return [SHAKEDOWN[1]]
    ids: list[str] = []
    for relative in COHORTS.values():
        ids.extend(row["material_id"] for row in _read_manifest(repo, relative))
    return ids


def task_ids(repo: Path, phase: str = "run") -> list[str]:
    return [f"{material_id}:{config.config_id}" for material_id in manifest_ids(repo, phase) for config in CONFIGS]


def _safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text))


def _task_slug(material_id: str, config_id: str) -> str:
    return f"{_safe_name(material_id)}__{_safe_name(config_id)}"


def parse_task(task: str) -> tuple[str, Config]:
    try:
        material_id, config_id = task.rsplit(":", 1)
        return material_id, CONFIG_BY_ID[config_id]
    except (ValueError, KeyError) as exc:
        raise ValueError(f"invalid task {task!r}; expected <material_id>:<config_id>") from exc


def _manifest_meta(repo: Path, phase: str, material_id: str) -> dict[str, str]:
    relatives = [SHAKEDOWN[0]] if phase == "probe" else list(COHORTS.values())
    for relative in relatives:
        for row in _read_manifest(repo, relative):
            if row["material_id"] == material_id:
                return row
    raise KeyError(f"material {material_id!r} not found in {phase} manifest")


def _staged_relative_path(inputs: Path, material_id: str) -> Path:
    return Path(inputs) / "materials" / f"{_safe_name(material_id)}.source"


def _read_staged_blob(meta: dict[str, str], inputs: Path) -> bytes:
    source = _staged_relative_path(inputs, meta["material_id"])
    if not source.is_file():
        raise RuntimeError(f"staged source missing: {source}")
    blob = source.read_bytes()
    actual = hashlib.sha256(blob).hexdigest()
    if actual != meta["sha256"]:
        raise RuntimeError(f"source SHA256 mismatch for {meta['material_id']}: {actual} != {meta['sha256']}")
    if len(blob) != int(meta["source_bytes"]):
        raise RuntimeError(f"source byte-count mismatch for {meta['material_id']}: {len(blob)} != {meta['source_bytes']}")
    return blob


def load_material(meta: dict[str, str], repo: Path, inputs: Path) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Use BP's fetch/build path, with only a local byte-source adapter."""
    sys.path.insert(0, str(Path(repo) / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev  # noqa: PLC0415

    blob = _read_staged_blob(meta, inputs)
    with tempfile.TemporaryDirectory(prefix="ffcz_load_") as temporary:
        grid, loader = dev.build_grid(meta, blob, Path(temporary))
        field = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
        lattice = np.asarray(grid.structure.lattice.matrix, dtype=float)
    if field.size != int(meta["npoints"]):
        raise RuntimeError(f"npoints mismatch {field.size} != {meta['npoints']}")
    if not np.all(np.isfinite(field)):
        raise RuntimeError("input field contains non-finite values")
    ptp = float(np.ptp(field))
    rh, rs = eng.v02.reference_hartree_rms(field, lattice)
    info = {
        "material_id": meta["material_id"],
        "loader": loader,
        "source_sha256_verified": True,
        "source_bytes": int(meta["source_bytes"]),
        "npoints": int(field.size),
        "shape": "x".join(str(v) for v in field.shape),
        "ptp": ptp,
        "raw_bytes": int(field.nbytes),
    }
    return field, lattice, info | {"hartree_reference_historical": rh, "hartree_reference_safe": rs}


def _error_text(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {getattr(exc, 'stderr', None) or exc}"[:600]


def search(ev: Callable[[float], dict[str, Any] | None], tau: float, lo: float, hi: float,
           cap: float = LO_ERROR_CAP) -> tuple[float | None, dict[float, dict[str, Any]], int]:
    """BP §4 lower-bound rule plus the unchanged engineering bisection."""
    skipped = 0
    while ev(lo) is None and lo * 10.0 <= cap * (1.0 + 1e-12):
        lo *= 10.0
        skipped += 1
    if ev(lo) is None:
        return None, {}, -1
    seen: dict[float, dict[str, Any]] = {}

    def ok(value: float) -> bool:
        result = ev(float(value))
        good = result is not None and result["hartree_hist"] < tau and result["hartree_safe"] < tau
        if good:
            seen[float(value)] = result
        return bool(good)

    eng.bisect_scale(ok, lo, hi)
    if not seen:
        return None, seen, skipped
    best = max(seen, key=lambda value: (-int(seen[value]["bytes"]), float(value)))
    return float(best), seen, skipped


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    names = list(fieldnames or [])
    for row in rows:
        for key in row:
            if key not in names:
                names.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=names or ["material_id"])
        writer.writeheader()
        writer.writerows(rows)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def _checkpoint_path(output_dir: Path, material_id: str, config: Config) -> Path:
    return Path(output_dir) / "checkpoints" / f"{_task_slug(material_id, config.config_id)}.json"


def _is_complete(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return bool(payload.get("complete")) and payload.get("status") in {"complete", "failed"}
    except (OSError, json.JSONDecodeError):
        return False


def run_task(repo: Path, inputs: Path, output_dir: Path, phase: str, material_id: str, config: Config,
             ffcz_exe: str | Path | None = None, runner: Callable[..., tuple[np.ndarray, int, int, dict[str, Any]]] = C.run_ffcz_roundtrip) -> dict[str, Any]:
    checkpoint = _checkpoint_path(output_dir, material_id, config)
    if _is_complete(checkpoint):
        return {"material_id": material_id, "config": config.config_id, "status": "skipped", "checkpoint": str(checkpoint)}

    started = time.time()
    rows: list[dict[str, Any]] = []
    evals: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    info: dict[str, Any] = {"material_id": material_id, "config": config.config_id, "phase": phase}
    status = "complete"
    try:
        meta = _manifest_meta(repo, phase, material_id)
        field, lattice, load_info = load_material(meta, repo, inputs)
        info |= load_info
        raw_bytes = int(field.nbytes)
        ptp = float(info["ptp"])
        spatial_bound = float(config.eps_rel * ptp)
        source_raw: Path
        with tempfile.TemporaryDirectory(prefix=f"ffcz_{_safe_name(material_id)}_{config.config_id}_") as temporary:
            workdir = Path(temporary)
            source_raw = workdir / "rho.raw"
            np.ascontiguousarray(field, dtype="<f8").tofile(source_raw)
            base_cache: dict[tuple[str, float], C.BaseArtifact] = {}
            base_errors: dict[tuple[str, float], str] = {}
            cache: dict[float, dict[str, Any] | None] = {}

            def evaluate(r_value: float) -> dict[str, Any] | None:
                r_value = float(r_value)
                if r_value in cache:
                    return cache[r_value]
                key = (config.codec, float(config.eps_rel))
                t0 = time.perf_counter()
                result: dict[str, Any] | None = None
                error = ""
                try:
                    if key in base_errors:
                        raise C.CodecExecutionError(base_errors[key])
                    if key not in base_cache:
                        base_cache[key] = C.prepare_base(
                            config.codec, field, spatial_bound, workdir / f"base_{config.codec}_eb{_eps_label(config.eps_rel)}",
                            name="base", source_raw=source_raw,
                        )
                    reconstructed, base_bytes, edits_bytes, details = runner(
                        C.resolve_ffcz(ffcz_exe), source_raw, base_cache[key], spatial_bound, config.mode, r_value,
                        workdir, tag=f"{config.config_id}_{r_value:.17g}",
                    )
                    eh, es, linf, rmse = eng.certify(reconstructed, field, lattice,
                                                       float(info["hartree_reference_historical"]),
                                                       float(info["hartree_reference_safe"]))
                    result = {
                        "bytes": int(C.stored_bytes(base_bytes, edits_bytes)),
                        "base_stream_bytes": int(base_bytes),
                        "edits_bytes": int(edits_bytes),
                        "hartree_hist": float(eh),
                        "hartree_safe": float(es),
                        "density_Linf": float(linf),
                        "density_RMSE": float(rmse),
                        "seconds": float(time.perf_counter() - t0),
                        "error": "",
                    }
                    result.update({key_: value for key_, value in details.items() if key_ not in result})
                except Exception as exc:  # Execution error is a non-passing point, per BP §4.
                    error = _error_text(exc)
                    if key not in base_cache:
                        base_errors[key] = error
                eval_row = {
                    "material_id": material_id,
                    "config": config.config_id,
                    "codec": config.codec.upper(),
                    "eps_b_rel": config.eps_rel,
                    "eps_b": spatial_bound,
                    "mode": config.mode,
                    "r": r_value,
                    "error": error,
                    "seconds": float(time.perf_counter() - t0),
                }
                if result is not None:
                    eval_row.update({key_: value for key_, value in result.items() if key_ != "error"})
                evals.append(eval_row)
                if error:
                    failures.append(eval_row.copy())
                cache[r_value] = result
                return result

            for tau in TAUS:
                search_started = time.perf_counter()
                n_before = len(evals)
                lo, hi = INTERVALS[config.mode]
                best, seen, skipped = search(evaluate, tau, lo, hi, LO_ERROR_CAP)
                row: dict[str, Any] = {
                    "material_id": material_id,
                    "config": config.config_id,
                    "codec": config.codec.upper(),
                    "eps_b_rel": config.eps_rel,
                    "eps_b": spatial_bound,
                    "mode": config.mode,
                    "tau": tau,
                    "certified": best is not None,
                    "lo_decades_skipped": skipped,
                    "n_evals_new": len(evals) - n_before,
                    "n_passing": len(seen),
                    "search_seconds": float(time.perf_counter() - search_started),
                    "param": f"{config.config_id};r={best:.9g}" if best is not None else "",
                    "r": best if best is not None else "",
                }
                if best is not None:
                    result = seen[best]
                    row.update({key_: value for key_, value in result.items() if key_ != "error"})
                    row["cr"] = float(raw_bytes / result["bytes"])
                else:
                    row["cr"] = ""
                rows.append(row)
    except Exception:
        status = "failed"
        failures.append({"material_id": material_id, "config": config.config_id, "arm": "material",
                         "error": traceback.format_exc()[-1200:]})

    info["seconds"] = float(time.time() - started)
    info["status"] = status
    payload = {
        "complete": True,
        "status": status,
        "material_id": material_id,
        "config": asdict(config),
        "info": info,
        "rows": rows,
        "evals": evals,
        "failures": failures,
    }
    _atomic_json(checkpoint, payload)
    slug = _task_slug(material_id, config.config_id)
    raw_dir = Path(output_dir) / "results_raw"
    _write_csv(raw_dir / f"rows_{slug}.csv", rows)
    _write_csv(raw_dir / f"evals_{slug}.csv", evals)
    _write_csv(raw_dir / f"failures_{slug}.csv", failures)
    _atomic_json(raw_dir / f"info_{slug}.json", info)
    return {"material_id": material_id, "config": config.config_id, "status": status,
            "rows": len(rows), "evals": len(evals), "failures": len(failures), "seconds": info["seconds"]}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_DEFAULT)
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    parser.add_argument("--phase", choices=("probe", "run"))
    parser.add_argument("--task")
    parser.add_argument("--ffcz-exe")
    parser.add_argument("--check-inputs", action="store_true")
    parser.add_argument("--list-tasks", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    repo = args.repo_root.resolve()
    if args.check_inputs:
        errors = check_inputs(repo)
        print("input hashes: OK" if not errors else "input hashes: " + " | ".join(errors))
        return 0 if not errors else 1
    if args.list_tasks:
        for task in task_ids(repo, "run"):
            print(task)
        return 0
    if args.phase is None:
        raise SystemExit("--phase probe|run is required unless --check-inputs or --list-tasks is used")
    if args.inputs is None:
        raise SystemExit("--inputs is required for staged execution")
    if args.task:
        material_id, config = parse_task(args.task)
        if material_id not in manifest_ids(repo, args.phase):
            raise SystemExit(f"task material {material_id!r} is not in the {args.phase} population")
        results = [run_task(repo, args.inputs.resolve(), args.output_dir.resolve(), args.phase, material_id, config, args.ffcz_exe)]
    else:
        results = []
        for task in task_ids(repo, args.phase):
            material_id, config = parse_task(task)
            results.append(run_task(repo, args.inputs.resolve(), args.output_dir.resolve(), args.phase, material_id, config, args.ffcz_exe))
    for result in results:
        print(json.dumps(result, sort_keys=True), flush=True)
    return 0 if all(result["status"] in {"complete", "skipped"} for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
