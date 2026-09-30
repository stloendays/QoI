#!/usr/bin/env python3
"""WP-C runner: codec-shaped perturbation family for QSQ.

Executes the fixed construction of analysis/extensions_20260928/PROTOCOL.md (WP-C):

  * per development material m and codec c in {ZFP, SZ3, SPERR}, regenerate the base-rung
    reconstruction at nominal relative tolerance 1e-5 with the frozen codec wrappers and the
    stored `nominal_tolerance_absolute` (smallest available base rung if 1e-5 is absent; the rung
    used is recorded per row);
  * residual r = rho_tilde - rho;
  * probes delta_{m,c,k} = eps_m * roll(r, v_k) / ||r||_inf, k = 0..5, with v_k drawn from
    Generator(PCG64(stream)), stream = first 8 bytes (little-endian) of
    SHA-256("QSQ-codecshape|material_id|codec|k"); k = 0 is unshifted;
  * one Bader re-solve per probe with the frozen Bader semantics (external_end_to_end.run_bader).

Frozen inputs are read only. Source densities are fetched by URL, verified by SHA-256 and cached
on disk (outside the repository). Each material is checkpointed as one JSON file so that a restart
resumes. Every planned row ends as either an outcome row or a failure row.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
import time
import traceback
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
CODECS = ("ZFP", "SZ3", "SPERR")
CODEC_ARG = {"ZFP": "zfp", "SZ3": "sz3", "SPERR": "sperr"}
K_VALUES = (0, 1, 2, 3, 4, 5)
TARGET_RUNG = 1e-5
LINF_REL_TOL = 1e-12
OLD_SEEDS = {20260905, 1, 2, 3, 4}

OUTCOME_FIELDS = [
    "material_id", "system_type", "corpus", "codec", "k", "stream_seed", "shift_vector",
    "base_rung_relative", "base_rung_is_1e-5", "nominal_tolerance_absolute",
    "frozen_realized_Linf", "reproduced_realized_Linf", "residual_reproduction_abs_log10_ratio",
    "epsilon", "measured_Linf", "measured_Linf_rel_dev", "measured_L2_rms", "mean_perturbation_e",
    "reference_min_density", "perturbed_min_density", "perturbed_negative_voxels",
    "bader_response_max_e", "bader_response_mean_e", "bader_response_median_e",
    "baseline_bader_charges_json", "perturbed_bader_charges_json",
    "baseline_labels_sha256", "perturbed_labels_sha256",
    "n_voxels_reassigned", "frac_voxels_reassigned",
    "baseline_num_vacuum_voxels", "perturbed_num_vacuum_voxels",
    "baseline_vacuum_charge_e", "perturbed_vacuum_charge_e",
    "npoints", "natoms", "source_sha256", "source_bytes", "loader",
    "codec_seconds", "bader_seconds", "status",
]
FAILURE_FIELDS = [
    "material_id", "codec", "k", "stream_seed", "epsilon", "npoints", "status", "stage", "error",
]
SPECTRA_FIELDS_HEAD = [
    "material_id", "system_type", "corpus", "codec", "base_rung_relative",
    "nominal_tolerance_absolute", "reproduced_realized_Linf", "residual_L2_rms",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-validation-dir", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path, required=True, help="density blob cache (outside the repo)")
    p.add_argument("--work-dir", type=Path, required=True, help="per-material checkpoints (outside the repo)")
    p.add_argument("--output-dir", type=Path, default=HERE)
    p.add_argument("--workers", type=int, default=6)
    p.add_argument("--numba-threads", type=int, default=4)
    p.add_argument("--download-threads", type=int, default=6)
    p.add_argument("--k-values", type=str, default=",".join(str(k) for k in K_VALUES))
    p.add_argument("--materials", type=str, default="", help="comma-separated subset (testing only)")
    p.add_argument("--prefetch-only", action="store_true")
    return p.parse_args()


# ----------------------------------------------------------------------------- helpers

def sha256_hex(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def stream_seed(material_id: str, codec: str, k: int) -> int:
    msg = f"QSQ-codecshape|{material_id}|{codec}|{k}".encode()
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "little")


def shift_vector(material_id: str, codec: str, k: int, shape: tuple[int, int, int]) -> tuple[int, list[int]]:
    seed = stream_seed(material_id, codec, k)
    rng = np.random.Generator(np.random.PCG64(seed))
    v = [int(rng.integers(0, n)) for n in shape]
    return seed, v


def labels_hash(labels: np.ndarray) -> str:
    x = np.ascontiguousarray(np.asarray(labels, dtype=np.int32))
    h = hashlib.sha256()
    h.update(str(tuple(x.shape)).encode())
    h.update(b"|")
    h.update(x.tobytes(order="C"))
    return h.hexdigest()


def charges_json(charges: np.ndarray) -> str:
    return json.dumps([float(x) for x in np.asarray(charges, dtype=np.float64)], separators=(",", ":"))


def load_amplitudes(repo: Path) -> dict[str, float]:
    path = repo / "stability" / "stability_floor_A1_per_seed.csv"
    by_material: dict[str, list[float]] = defaultdict(list)
    seeds: dict[str, set[int]] = defaultdict(set)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_material[row["material_id"]].append(float(row["probe_linf"]))
            seeds[row["material_id"]].add(int(row["seed"]))
    out: dict[str, float] = {}
    for material, values in by_material.items():
        if seeds[material] != OLD_SEEDS:
            raise RuntimeError(f"old QSQ seed set drift for {material}: {seeds[material]}")
        if not np.allclose(values, values[0], rtol=0.0, atol=0.0):
            raise RuntimeError(f"old QSQ amplitude not unique for {material}")
        out[material] = values[0]
    return out


def load_base_rungs(repo: Path) -> dict[tuple[str, str], dict[str, Any]]:
    """Per (material, codec): the 1e-5 base rung if present, else the smallest available base rung."""
    path = repo / "benchmark" / "master_benchmark_full.csv"
    cand: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["ladder"] != "base":
                continue
            cand[(row["material_id"], row["codec"])].append(row)
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for key, rows in cand.items():
        rows.sort(key=lambda r: float(r["nominal_tolerance_relative"]))
        exact = [r for r in rows if float(r["nominal_tolerance_relative"]) == TARGET_RUNG]
        chosen = exact[0] if exact else rows[0]
        if len(exact) > 1:
            raise RuntimeError(f"duplicate 1e-5 base rows for {key}")
        out[key] = {
            "rung": float(chosen["nominal_tolerance_relative"]),
            "is_target": bool(exact),
            "abs_bound": float(chosen["nominal_tolerance_absolute"]),
            "frozen_linf": float(chosen["realized_Linf"]),
            "stability_floor_A1_e": float(chosen["stability_floor_A1_e"]),
        }
    return out


def cached_blob_path(cache_dir: Path, meta: dict[str, str]) -> Path:
    return cache_dir / f"{meta['material_id']}.blob"


def fetch_cached(meta: dict[str, str], cache_dir: Path, dev) -> bytes:
    path = cached_blob_path(cache_dir, meta)
    if path.exists():
        blob = path.read_bytes()
        if sha256_hex(blob) == meta["sha256"] and len(blob) == int(meta["source_bytes"]):
            return blob
        path.unlink()
    last: Exception | None = None
    for attempt in range(4):
        try:
            blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(blob)
            os.replace(tmp, path)
            return blob
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(5.0 * (attempt + 1))
    raise RuntimeError(f"download failed after retries: {type(last).__name__}: {last}")


# ----------------------------------------------------------------------------- per material

def run_material(task: dict[str, Any]) -> dict[str, Any]:
    """Runs one material end to end; returns {'outcomes': [...], 'failures': [...], 'spectra': [...]}."""
    os.environ.setdefault("NUMBA_NUM_THREADS", str(task["numba_threads"]))
    repo = Path(task["repo"])
    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    sys.path.insert(0, str(repo / "analysis" / "hartree_spectral_mechanism"))
    sys.path.insert(0, str(task["frozen_validation"]))
    import development_compatibility_smoke as dev  # type: ignore
    import external_end_to_end as core  # type: ignore
    import run_shard as spec  # type: ignore  (Nyquist-safe spectral convention)

    meta = task["meta"]
    mid = meta["material_id"]
    eps = float(task["epsilon"])
    k_values = list(task["k_values"])
    rungs = task["rungs"]
    outcomes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    spectra: list[dict[str, Any]] = []

    def fail_all(stage: str, err: str, codecs=CODECS, ks=None) -> None:
        for codec in codecs:
            for k in (ks if ks is not None else k_values):
                failures.append({
                    "material_id": mid, "codec": codec, "k": k,
                    "stream_seed": stream_seed(mid, codec, k) if k > 0 else "",
                    "epsilon": eps, "npoints": meta["npoints"],
                    "status": "FAILED", "stage": stage, "error": err,
                })

    t_material = time.time()
    try:
        blob = fetch_cached(meta, Path(task["cache_dir"]), dev)
    except Exception as exc:  # noqa: BLE001
        fail_all("download", f"{type(exc).__name__}: {exc}")
        return {"material_id": mid, "outcomes": outcomes, "failures": failures, "spectra": spectra,
                "seconds": time.time() - t_material}

    with tempfile.TemporaryDirectory(prefix="qoi_wpc_") as td:
        workdir = Path(td)
        try:
            grid, loader = dev.build_grid(meta, blob, workdir)
            field = np.asarray(grid.total, dtype=np.float64)
            expected_shape = dev.parse_shape(meta["ngrid"])
            if tuple(field.shape) != expected_shape:
                raise RuntimeError(f"grid shape mismatch {field.shape} != {expected_shape}")
            if field.size != int(meta["npoints"]):
                raise RuntimeError(f"npoints mismatch {field.size} != {meta['npoints']}")
            if len(grid.structure) != int(meta["natoms"]):
                raise RuntimeError(f"structure natoms mismatch {len(grid.structure)} != {meta['natoms']}")
            if not np.all(np.isfinite(field)):
                raise RuntimeError("reference field contains non-finite values")
            t0 = time.time()
            baseline = core.run_bader(grid)
            baseline_seconds = time.time() - t0
            q_orig = np.asarray(baseline["charges"], dtype=np.float64)
            labels_orig = np.asarray(baseline["atom_labels"])
            if q_orig.size != int(meta["natoms"]):
                raise RuntimeError(f"Bader natoms mismatch {q_orig.size} != {meta['natoms']}")
            q_fixed = core.fixed_basin_charges(field, labels_orig, int(q_orig.size))
            self_error = float(np.max(np.abs(q_fixed - q_orig)))
            if self_error > 1e-7:
                raise RuntimeError(f"fixed-basin reference self-check failed: {self_error:.6g} e")
            baseline_hash = labels_hash(labels_orig)
            lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)
            g2 = spec.reciprocal_g2(tuple(field.shape), lattice)
            nyq = spec.nyquist_mask(tuple(field.shape))
        except Exception as exc:  # noqa: BLE001
            fail_all("reference", f"{type(exc).__name__}: {exc}")
            return {"material_id": mid, "outcomes": outcomes, "failures": failures, "spectra": spectra,
                    "seconds": time.time() - t_material}

        for codec in CODECS:
            rung = rungs[codec]
            try:
                t0 = time.time()
                reconstructed, _nbytes, _cfg = core.codec_roundtrip(CODEC_ARG[codec], field, float(rung["abs_bound"]), workdir)
                codec_seconds = time.time() - t0
                reconstructed = np.asarray(reconstructed, dtype=np.float64)
                r = reconstructed - field
                del reconstructed
                if not np.all(np.isfinite(r)):
                    raise RuntimeError("residual contains non-finite values")
                r_linf = float(np.max(np.abs(r)))
                if r_linf <= 0.0:
                    raise RuntimeError("zero residual: codec round trip was lossless at this rung")
                repro = abs(float(np.log10(r_linf / float(rung["frozen_linf"]))))
                # Nyquist-safe radial spectrum of the residual (frozen convention).
                sm, bins = spec.spectral_metrics(r, g2, nyq)
                srow = {
                    "material_id": mid, "system_type": meta["system_type"], "corpus": meta["corpus"],
                    "codec": codec, "base_rung_relative": rung["rung"],
                    "nominal_tolerance_absolute": rung["abs_bound"],
                    "reproduced_realized_Linf": r_linf,
                    "residual_L2_rms": float(np.sqrt(np.mean(r * r))),
                    **sm,
                }
                for b in bins:
                    srow[f"radial_bin_{int(b['bin_index']):02d}_error_energy_fraction"] = b["error_energy_fraction"]
                spectra.append(srow)
            except Exception as exc:  # noqa: BLE001
                fail_all("codec_or_spectrum", f"{type(exc).__name__}: {exc}", codecs=(codec,))
                continue

            scale = eps / r_linf
            for k in k_values:
                seed: int | str = ""
                v = [0, 0, 0]
                try:
                    if k > 0:
                        seed, v = shift_vector(mid, codec, k, tuple(field.shape))
                        delta = np.roll(r, shift=tuple(v), axis=(0, 1, 2)) * scale
                    else:
                        delta = r * scale
                    measured_linf = float(np.max(np.abs(delta)))
                    rel_dev = abs(measured_linf - eps) / eps
                    if rel_dev > LINF_REL_TOL:
                        raise RuntimeError(f"probe L_inf {measured_linf!r} deviates from epsilon {eps!r} by {rel_dev:.3e} relative")
                    perturbed = field + delta
                    if not np.all(np.isfinite(perturbed)):
                        raise RuntimeError("perturbed field contains non-finite values")
                    perturbed_grid = core.clone_grid_with_total(grid, perturbed)
                    t0 = time.time()
                    result = core.run_bader(perturbed_grid)
                    bader_seconds = time.time() - t0
                    q_new = np.asarray(result["charges"], dtype=np.float64)
                    labels_new = np.asarray(result["atom_labels"])
                    if q_new.shape != q_orig.shape:
                        raise RuntimeError(f"perturbed Bader charge shape mismatch {q_new.shape} != {q_orig.shape}")
                    if labels_new.shape != labels_orig.shape:
                        raise RuntimeError(f"perturbed basin-label shape mismatch {labels_new.shape} != {labels_orig.shape}")
                    dq = np.abs(q_new - q_orig)
                    reassigned = int(np.count_nonzero(labels_new != labels_orig))
                    outcomes.append({
                        "material_id": mid, "system_type": meta["system_type"], "corpus": meta["corpus"],
                        "codec": codec, "k": k, "stream_seed": seed, "shift_vector": json.dumps(v),
                        "base_rung_relative": rung["rung"], "base_rung_is_1e-5": rung["is_target"],
                        "nominal_tolerance_absolute": rung["abs_bound"],
                        "frozen_realized_Linf": rung["frozen_linf"], "reproduced_realized_Linf": r_linf,
                        "residual_reproduction_abs_log10_ratio": repro,
                        "epsilon": eps, "measured_Linf": measured_linf, "measured_Linf_rel_dev": rel_dev,
                        "measured_L2_rms": float(np.sqrt(np.mean(delta * delta))),
                        "mean_perturbation_e": float(np.mean(delta)),
                        "reference_min_density": float(np.min(field)),
                        "perturbed_min_density": float(np.min(perturbed)),
                        "perturbed_negative_voxels": int(np.count_nonzero(perturbed < 0)),
                        "bader_response_max_e": float(np.max(dq)),
                        "bader_response_mean_e": float(np.mean(dq)),
                        "bader_response_median_e": float(np.median(dq)),
                        "baseline_bader_charges_json": charges_json(q_orig),
                        "perturbed_bader_charges_json": charges_json(q_new),
                        "baseline_labels_sha256": baseline_hash,
                        "perturbed_labels_sha256": labels_hash(labels_new),
                        "n_voxels_reassigned": reassigned,
                        "frac_voxels_reassigned": reassigned / field.size,
                        "baseline_num_vacuum_voxels": int(baseline["num_vacuum_voxels"]),
                        "perturbed_num_vacuum_voxels": int(result["num_vacuum_voxels"]),
                        "baseline_vacuum_charge_e": float(baseline["vacuum_charge_e"]),
                        "perturbed_vacuum_charge_e": float(result["vacuum_charge_e"]),
                        "npoints": int(field.size), "natoms": int(q_orig.size),
                        "source_sha256": meta["sha256"], "source_bytes": int(meta["source_bytes"]),
                        "loader": loader, "codec_seconds": codec_seconds, "bader_seconds": bader_seconds,
                        "status": "SUCCESS",
                    })
                except Exception as exc:  # noqa: BLE001
                    failures.append({
                        "material_id": mid, "codec": codec, "k": k, "stream_seed": seed,
                        "epsilon": eps, "npoints": meta["npoints"], "status": "FAILED",
                        "stage": "probe_or_bader", "error": f"{type(exc).__name__}: {exc}",
                    })
            del r
    return {"material_id": mid, "outcomes": outcomes, "failures": failures, "spectra": spectra,
            "baseline_bader_seconds": baseline_seconds, "fixed_basin_self_error_e": self_error,
            "seconds": time.time() - t_material}


def _worker(task: dict[str, Any]) -> dict[str, Any]:
    try:
        return run_material(task)
    except Exception:  # noqa: BLE001 - never lose a material silently
        mid = task["meta"]["material_id"]
        err = traceback.format_exc(limit=3).strip().splitlines()[-1]
        failures = []
        for codec in CODECS:
            for k in task["k_values"]:
                failures.append({
                    "material_id": mid, "codec": codec, "k": k,
                    "stream_seed": stream_seed(mid, codec, k) if k > 0 else "",
                    "epsilon": task["epsilon"], "npoints": task["meta"]["npoints"],
                    "status": "FAILED", "stage": "worker_crash", "error": err,
                })
        return {"material_id": mid, "outcomes": [], "failures": failures, "spectra": [], "seconds": float("nan")}


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    args = parse_args()
    repo = args.repo_root.resolve()
    frozen_validation = args.frozen_validation_dir.resolve()
    cache_dir = args.cache_dir.resolve(); cache_dir.mkdir(parents=True, exist_ok=True)
    work_dir = args.work_dir.resolve(); (work_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    outdir = args.output_dir.resolve(); outdir.mkdir(parents=True, exist_ok=True)
    k_values = [int(x) for x in args.k_values.split(",") if x.strip()]
    os.environ["NUMBA_NUM_THREADS"] = str(args.numba_threads)

    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev  # type: ignore

    metadata = dev.load_metadata(repo)
    dev_materials = sorted(m for m, r in metadata.items() if r["corpus"].startswith("dev"))
    if args.materials:
        wanted = set(args.materials.split(","))
        dev_materials = [m for m in dev_materials if m in wanted]
    amplitudes = load_amplitudes(repo)
    rungs = load_base_rungs(repo)

    t_start = time.time()
    # Stage 1: prefetch and cache every density (verified by SHA-256).
    pending_dl = [m for m in dev_materials if not cached_blob_path(cache_dir, metadata[m]).exists()]
    print(f"[prefetch] {len(dev_materials)} materials, {len(pending_dl)} to download", flush=True)
    dl_failures: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=args.download_threads) as ex:
        futs = {ex.submit(fetch_cached, metadata[m], cache_dir, dev): m for m in pending_dl}
        for i, fut in enumerate(as_completed(futs), 1):
            m = futs[fut]
            try:
                fut.result()
            except Exception as exc:  # noqa: BLE001
                dl_failures[m] = f"{type(exc).__name__}: {exc}"
            if i % 10 == 0 or i == len(futs):
                print(f"[prefetch] {i}/{len(futs)} done, {len(dl_failures)} failed, {time.time()-t_start:.0f}s", flush=True)
    if args.prefetch_only:
        print(json.dumps({"download_failures": dl_failures}, indent=2))
        return 0

    # Stage 2: per-material execution with checkpoints (restart-safe).
    ckpt_dir = work_dir / "checkpoints"
    todo = [m for m in dev_materials if not (ckpt_dir / f"{m}.json").exists()]
    print(f"[run] {len(todo)}/{len(dev_materials)} materials remaining; k={k_values}; workers={args.workers}; numba_threads={args.numba_threads}", flush=True)
    tasks = []
    for m in todo:
        tasks.append({
            "repo": str(repo), "frozen_validation": str(frozen_validation), "cache_dir": str(cache_dir),
            "meta": metadata[m], "epsilon": amplitudes[m], "k_values": k_values,
            "rungs": {c: rungs[(m, c)] for c in CODECS}, "numba_threads": args.numba_threads,
        })
    # Largest grids first so the tail of the pool is short.
    tasks.sort(key=lambda t: -int(t["meta"]["npoints"]))

    import multiprocessing as mp
    done = 0
    if tasks:
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=args.workers) as pool:
            for res in pool.imap_unordered(_worker, tasks):
                done += 1
                m = res["material_id"]
                tmp = ckpt_dir / f"{m}.json.tmp"
                tmp.write_text(json.dumps(res), encoding="utf-8")
                os.replace(tmp, ckpt_dir / f"{m}.json")
                print(f"[run] {done}/{len(tasks)} {m} ok={len(res['outcomes'])} fail={len(res['failures'])} "
                      f"{res.get('seconds', float('nan')):.1f}s elapsed={time.time()-t_start:.0f}s", flush=True)

    # Stage 3: aggregate checkpoints into the package CSVs.
    outcomes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    spectra: list[dict[str, Any]] = []
    material_records: list[dict[str, Any]] = []
    for m in dev_materials:
        p = ckpt_dir / f"{m}.json"
        if not p.exists():
            for codec in CODECS:
                for k in k_values:
                    failures.append({"material_id": m, "codec": codec, "k": k,
                                     "stream_seed": stream_seed(m, codec, k) if k > 0 else "",
                                     "epsilon": amplitudes[m], "npoints": metadata[m]["npoints"],
                                     "status": "FAILED", "stage": "not_run", "error": "no checkpoint"})
            continue
        res = json.loads(p.read_text(encoding="utf-8"))
        outcomes.extend(res["outcomes"]); failures.extend(res["failures"]); spectra.extend(res["spectra"])
        material_records.append({"material_id": m, "seconds": res.get("seconds"),
                                 "baseline_bader_seconds": res.get("baseline_bader_seconds"),
                                 "fixed_basin_self_error_e": res.get("fixed_basin_self_error_e"),
                                 "n_outcomes": len(res["outcomes"]), "n_failures": len(res["failures"])})
    outcomes.sort(key=lambda r: (r["material_id"], CODECS.index(r["codec"]), int(r["k"])))
    failures.sort(key=lambda r: (r["material_id"], CODECS.index(r["codec"]), int(r["k"])))
    spectra.sort(key=lambda r: (r["material_id"], CODECS.index(r["codec"])))
    write_csv(outdir / "probe_outcomes.csv", outcomes, OUTCOME_FIELDS)
    write_csv(outdir / "failures.csv", failures, FAILURE_FIELDS)
    spec_fields = list(SPECTRA_FIELDS_HEAD)
    for row in spectra:
        for key in row:
            if key not in spec_fields:
                spec_fields.append(key)
    write_csv(outdir / "spectra.csv", spectra, spec_fields)
    planned = len(dev_materials) * len(CODECS) * len(k_values)
    manifest = {
        "materials": len(dev_materials), "codecs": list(CODECS), "k_values": k_values,
        "solves_planned": planned, "solves_succeeded": len(outcomes), "solves_failed": len(failures),
        "accounted": len(outcomes) + len(failures), "codec_roundtrips_planned": len(dev_materials) * len(CODECS),
        "spectra_rows": len(spectra), "download_failures": dl_failures,
        "wall_seconds_this_invocation": time.time() - t_start,
        "material_records": material_records,
    }
    (outdir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "material_records"}, indent=2))
    if manifest["accounted"] != planned:
        return 3
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
