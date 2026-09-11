#!/usr/bin/env python3
"""Run one deterministic shard of the prospective P2 fresh QSQ probe test.

The original five-seed QSQ gate is never modified by this script. The 59 new
streams are pre-registered held-out perturbations. Every planned seed is written
as either a successful measurement or an explicit failure.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import resource
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from development_compatibility_smoke import build_grid, fetch_exact, load_metadata, parse_shape

OLD_SEEDS = {20260905, 1, 2, 3, 4}
FRESH_SEEDS = set(range(10000, 10059))

SUCCESS_FIELDS = [
    "material_id", "system_type", "corpus", "family", "seed_label", "stream_seed",
    "epsilon", "measured_Linf", "measured_L2_rms", "mean_perturbation_e",
    "reference_min_density", "perturbed_min_density", "perturbed_negative_voxels",
    "bader_response_max_e", "bader_response_mean_e", "bader_response_median_e",
    "baseline_bader_charges_json", "perturbed_bader_charges_json",
    "baseline_labels_sha256", "perturbed_labels_sha256", "n_voxels_reassigned",
    "frac_voxels_reassigned", "baseline_num_vacuum_voxels", "perturbed_num_vacuum_voxels",
    "baseline_vacuum_charge_e", "perturbed_vacuum_charge_e", "npoints", "natoms",
    "source_sha256", "source_bytes", "field_fingerprint", "bader_seconds",
    "process_peak_rss_kb_after", "status",
]
FAILURE_FIELDS = [
    "material_id", "family", "seed_label", "stream_seed", "epsilon", "field_fingerprint",
    "npoints", "status", "stage", "error",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-validation-dir", type=Path, required=True)
    p.add_argument("--work-order", type=Path, required=True)
    p.add_argument("--shard-count", type=int, required=True)
    p.add_argument("--shard-index", type=int, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def shard_for(material_id: str, n: int) -> int:
    digest = hashlib.sha256(("QSQ-P2|" + material_id).encode()).digest()
    return int.from_bytes(digest[:8], "big") % n


def expected_stream_seed(material: str, label: int) -> int:
    msg = f"QSQ-heldout|{material}|iid_uniform|{label}".encode()
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "little")


def labels_hash(labels: np.ndarray) -> str:
    x = np.ascontiguousarray(np.asarray(labels, dtype=np.int32))
    h = hashlib.sha256()
    h.update(str(tuple(x.shape)).encode())
    h.update(b"|")
    h.update(x.tobytes(order="C"))
    return h.hexdigest()


def charges_json(charges: np.ndarray) -> str:
    return json.dumps([float(x) for x in np.asarray(charges, dtype=np.float64)], separators=(",", ":"))


def load_old_amplitudes(repo_root: Path) -> dict[str, float]:
    path = repo_root / "stability" / "stability_floor_A1_per_seed.csv"
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


def check_reference(meta: dict[str, str], grid, field: np.ndarray, core) -> tuple[dict[str, Any], np.ndarray, np.ndarray, dict[str, Any]]:
    expected_shape = parse_shape(meta["ngrid"])
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
    elapsed = time.time() - t0
    q_orig = np.asarray(baseline["charges"], dtype=np.float64)
    labels_orig = np.asarray(baseline["atom_labels"])
    if q_orig.size != int(meta["natoms"]):
        raise RuntimeError(f"Bader natoms mismatch {q_orig.size} != {meta['natoms']}")
    q_fixed = core.fixed_basin_charges(field, labels_orig, int(q_orig.size))
    self_error = float(np.max(np.abs(q_fixed - q_orig)))
    if self_error > 1e-7:
        raise RuntimeError(f"fixed-basin reference self-check failed: {self_error:.6g} e")
    return {"baseline_bader_seconds": elapsed, "fixed_basin_self_error_e": self_error}, q_orig, labels_orig, baseline


def run_material(
    *, material_id: str, material_jobs: list[dict[str, str]], meta: dict[str, str], old_epsilon: float,
    core, out_success: list[dict[str, Any]], out_failure: list[dict[str, Any]], material_records: list[dict[str, Any]],
) -> None:
    for job in material_jobs:
        if job["family"] != "iid_uniform":
            raise RuntimeError(f"unexpected P2 family {job['family']}")
        label = int(job["seed_label"])
        if label not in FRESH_SEEDS or label in OLD_SEEDS:
            raise RuntimeError(f"unexpected fresh seed label {label}")
        expected = expected_stream_seed(material_id, label)
        if int(job["stream_seed"]) != expected:
            raise RuntimeError(f"stream seed mismatch for {material_id}/{label}")
        if float(job["epsilon"]) != old_epsilon:
            raise RuntimeError(f"epsilon mismatch for {material_id}/{label}")
        if int(float(job["npoints"])) != int(meta["npoints"]):
            raise RuntimeError(f"work-order npoints mismatch for {material_id}/{label}")
        if job["field_fingerprint"] != meta["sha256"]:
            raise RuntimeError(f"field fingerprint mismatch for {material_id}/{label}")

    blob = fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
    with tempfile.TemporaryDirectory(prefix="qoi_p2_") as td:
        workdir = Path(td)
        grid, loader = build_grid(meta, blob, workdir)
        field = np.asarray(grid.total, dtype=np.float64)
        ref_info, q_orig, labels_orig, baseline = check_reference(meta, grid, field, core)
        baseline_hash = labels_hash(labels_orig)
        material_records.append({
            "material_id": material_id,
            "loader": loader,
            "source_sha256": meta["sha256"],
            "source_bytes": int(meta["source_bytes"]),
            "epsilon": old_epsilon,
            "npoints": int(field.size),
            "natoms": int(q_orig.size),
            "baseline_labels_sha256": baseline_hash,
            **ref_info,
            "jobs_planned": len(material_jobs),
        })

        for job in sorted(material_jobs, key=lambda r: int(r["seed_label"])):
            label = int(job["seed_label"])
            stream_seed = int(job["stream_seed"])
            try:
                rng = np.random.Generator(np.random.PCG64(stream_seed))
                noise = rng.uniform(-old_epsilon, old_epsilon, size=field.shape).astype(np.float64, copy=False)
                measured_linf = float(np.max(np.abs(noise))) if noise.size else 0.0
                if measured_linf > old_epsilon * (1 + 8 * np.finfo(np.float64).eps):
                    raise RuntimeError(f"realized perturbation exceeds epsilon: {measured_linf} > {old_epsilon}")
                perturbed = field + noise
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
                out_success.append({
                    "material_id": material_id,
                    "system_type": meta["system_type"],
                    "corpus": meta["corpus"],
                    "family": "iid_uniform",
                    "seed_label": label,
                    "stream_seed": stream_seed,
                    "epsilon": old_epsilon,
                    "measured_Linf": measured_linf,
                    "measured_L2_rms": float(np.sqrt(np.mean(noise * noise))),
                    "mean_perturbation_e": float(np.mean(noise)),
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
                    "npoints": int(field.size),
                    "natoms": int(q_orig.size),
                    "source_sha256": meta["sha256"],
                    "source_bytes": int(meta["source_bytes"]),
                    "field_fingerprint": job["field_fingerprint"],
                    "bader_seconds": bader_seconds,
                    "process_peak_rss_kb_after": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
                    "status": "SUCCESS",
                })
            except Exception as exc:
                out_failure.append({
                    "material_id": material_id,
                    "family": job["family"],
                    "seed_label": label,
                    "stream_seed": stream_seed,
                    "epsilon": job["epsilon"],
                    "field_fingerprint": job["field_fingerprint"],
                    "npoints": job["npoints"],
                    "status": "FAILED",
                    "stage": "perturbation_or_bader",
                    "error": f"{type(exc).__name__}: {exc}",
                })


def main() -> int:
    args = parse_args()
    if args.shard_count <= 0 or not 0 <= args.shard_index < args.shard_count:
        raise SystemExit("invalid shard parameters")
    repo = args.repo_root.resolve()
    outdir = args.output_dir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    frozen_validation = args.frozen_validation_dir.resolve()
    sys.path.insert(0, str(frozen_validation))
    import external_end_to_end as core  # type: ignore

    metadata = load_metadata(repo)
    amplitudes = load_old_amplitudes(repo)
    with args.work_order.open(newline="", encoding="utf-8") as f:
        all_jobs = [r for r in csv.DictReader(f) if r.get("status") == "PREPARED_NOT_EXECUTED"]
    jobs = [r for r in all_jobs if shard_for(r["material_id"], args.shard_count) == args.shard_index]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for job in jobs:
        grouped[job["material_id"]].append(job)

    success: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    material_records: list[dict[str, Any]] = []
    for material_id in sorted(grouped):
        material_jobs = grouped[material_id]
        meta = metadata.get(material_id)
        epsilon = amplitudes.get(material_id)
        if meta is None or epsilon is None:
            err = "material missing from metadata or old QSQ amplitude table"
            for job in material_jobs:
                failures.append({**job, "status": "FAILED", "stage": "preflight", "error": err})
            continue
        try:
            run_material(
                material_id=material_id, material_jobs=material_jobs, meta=meta, old_epsilon=epsilon,
                core=core, out_success=success, out_failure=failures, material_records=material_records,
            )
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}"
            for job in material_jobs:
                failures.append({**job, "status": "FAILED", "stage": "source_or_reference", "error": err})

    success.sort(key=lambda r: (r["material_id"], int(r["seed_label"])))
    failures.sort(key=lambda r: (r["material_id"], int(r["seed_label"])))
    with (outdir / f"outcomes_shard_{args.shard_index:02d}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SUCCESS_FIELDS, extrasaction="ignore")
        w.writeheader(); w.writerows(success)
    with (outdir / f"failures_shard_{args.shard_index:02d}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FAILURE_FIELDS, extrasaction="ignore")
        w.writeheader(); w.writerows(failures)
    manifest = {
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "materials": len(grouped),
        "jobs_planned": len(jobs),
        "outcomes_success": len(success),
        "outcomes_failed": len(failures),
        "accounted": len(success) + len(failures),
        "material_records": material_records,
    }
    (outdir / f"manifest_shard_{args.shard_index:02d}.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    if manifest["accounted"] != manifest["jobs_planned"]:
        return 3
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
