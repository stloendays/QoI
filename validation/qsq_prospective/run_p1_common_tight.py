#!/usr/bin/env python3
"""Execute one deterministic shard of the P1 common tight-ladder work order.

The historical benchmark is immutable. Successful rows from this script are
additive prospective measurements stored under validation/qsq_prospective.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
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

TAUS = (1e-4, 1e-3, 1e-2)
MASTER_COLUMNS = [
    "material_id", "system_type", "corpus", "formula", "codec", "codec_config", "ladder",
    "nominal_tolerance_relative", "nominal_tolerance_absolute", "realized_Linf",
    "realized_Linf_over_nominal", "bound_respected", "rmse", "mean_signed_error", "raw_bytes",
    "compressed_bytes", "compression_ratio", "bits_per_value", "Bader_error_fixed_e",
    "Bader_error_resolved_e", "fixed_basin_understatement", "electron_count_abs_dev",
    "n_voxels_reassigned", "frac_voxels_reassigned", "stability_floor_A1_e",
    "stability_floor_A_archived_e", "eligible_A1_at_0.0001", "certified_at_0.0001",
    "certified_at_0.0001_ignoring_eligibility", "eligible_A1_at_0.001", "certified_at_0.001",
    "certified_at_0.001_ignoring_eligibility", "eligible_A1_at_0.01", "certified_at_0.01",
    "certified_at_0.01_ignoring_eligibility", "npoints", "natoms", "value_ptp", "encode_seconds",
    "bader_seconds", "field_sha256_prefix",
]
CONFIG_LABEL = {
    "ZFP": "zfpy fixed-accuracy",
    "SZ3": "pysz ABS INTERP_LORENZO",
    "SPERR": "hdf5plugin Sperr absolute, single chunk",
}
CORE_CODEC = {"ZFP": "zfp", "SZ3": "sz3", "SPERR": "sperr"}


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
    digest = hashlib.sha256(("QSQ-P1|" + material_id).encode()).digest()
    return int.from_bytes(digest[:8], "big") % n


def load_stability(repo_root: Path) -> dict[str, dict[str, str]]:
    path = repo_root / "benchmark" / "master_benchmark_full.csv"
    out: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out.setdefault(row["material_id"], row)
    return out


def check_reference(meta: dict[str, str], grid, field: np.ndarray, core) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    expected_shape = parse_shape(meta["ngrid"])
    if tuple(field.shape) != expected_shape:
        raise RuntimeError(f"grid shape mismatch {field.shape} != {expected_shape}")
    if field.size != int(meta["npoints"]):
        raise RuntimeError(f"npoints mismatch {field.size} != {meta['npoints']}")
    if len(grid.structure) != int(meta["natoms"]):
        raise RuntimeError(f"structure natoms mismatch {len(grid.structure)} != {meta['natoms']}")
    if not np.all(np.isfinite(field)):
        raise RuntimeError("reference field contains non-finite values")
    value_ptp = float(np.ptp(field))
    if not value_ptp > 0:
        raise RuntimeError("reference field has non-positive ptp")

    t0 = time.time()
    original = core.run_bader(grid)
    original_seconds = time.time() - t0
    q_orig = np.asarray(original["charges"], dtype=np.float64)
    labels_orig = np.asarray(original["atom_labels"])
    if q_orig.size != int(meta["natoms"]):
        raise RuntimeError(f"Bader natoms mismatch {q_orig.size} != {meta['natoms']}")
    q_fixed = core.fixed_basin_charges(field, labels_orig, int(q_orig.size))
    self_error = float(np.max(np.abs(q_fixed - q_orig)))
    if self_error > 1e-7:
        raise RuntimeError(f"fixed-basin reference self-check failed: {self_error:.6g} e")
    return {
        "value_ptp": value_ptp,
        "original_bader_seconds": original_seconds,
        "fixed_basin_self_error_e": self_error,
    }, q_orig, labels_orig


def make_master_row(
    *, meta: dict[str, str], stab: dict[str, str], job: dict[str, str], field: np.ndarray,
    reconstructed: np.ndarray, compressed_bytes: int, encode_seconds: float, bader_seconds: float,
    q_orig: np.ndarray, q_resolved: np.ndarray, labels_orig: np.ndarray, labels_resolved: np.ndarray,
    fixed_charges: np.ndarray, value_ptp: float,
) -> dict[str, Any]:
    codec = job["codec"]
    rel = float(job["nominal_tolerance_relative"])
    abs_bound = rel * value_ptp
    delta = reconstructed - field
    realized = float(np.max(np.abs(delta)))
    rmse = float(np.sqrt(np.mean(delta * delta)))
    mse = float(np.mean(delta))
    fixed_error = float(np.max(np.abs(fixed_charges - q_orig)))
    resolved_error = float(np.max(np.abs(q_resolved - q_orig)))
    understatement = resolved_error / fixed_error if fixed_error > 0 else float("inf")
    reassigned = int(np.count_nonzero(labels_resolved != labels_orig))
    npoints = int(field.size)
    floor = float(stab["stability_floor_A1_e"])
    archived_floor = float(stab["stability_floor_A_archived_e"])

    row: dict[str, Any] = {
        "material_id": meta["material_id"],
        "system_type": meta["system_type"],
        "corpus": meta["corpus"],
        "formula": meta["formula"],
        "codec": codec,
        "codec_config": CONFIG_LABEL[codec],
        "ladder": "tight",
        "nominal_tolerance_relative": rel,
        "nominal_tolerance_absolute": abs_bound,
        "realized_Linf": realized,
        "realized_Linf_over_nominal": realized / abs_bound,
        "bound_respected": bool(realized <= abs_bound * (1 + 1e-6) + 1e-15),
        "rmse": rmse,
        "mean_signed_error": mse,
        "raw_bytes": int(field.nbytes),
        "compressed_bytes": int(compressed_bytes),
        "compression_ratio": float(field.nbytes / compressed_bytes),
        "bits_per_value": float(8 * compressed_bytes / npoints),
        "Bader_error_fixed_e": fixed_error,
        "Bader_error_resolved_e": resolved_error,
        "fixed_basin_understatement": understatement,
        "electron_count_abs_dev": abs(mse),
        "n_voxels_reassigned": reassigned,
        "frac_voxels_reassigned": reassigned / npoints,
        "stability_floor_A1_e": floor,
        "stability_floor_A_archived_e": archived_floor,
        "npoints": npoints,
        "natoms": int(q_orig.size),
        "value_ptp": value_ptp,
        "encode_seconds": encode_seconds,
        "bader_seconds": bader_seconds,
        "field_sha256_prefix": meta["sha256"],
    }
    for tau in TAUS:
        if tau == 1e-4:
            suffix = "0.0001"
        elif tau == 1e-3:
            suffix = "0.001"
        else:
            suffix = "0.01"
        eligible = floor < tau
        numerical_pass = resolved_error < tau
        row[f"eligible_A1_at_{suffix}"] = eligible
        row[f"certified_at_{suffix}"] = bool(eligible and numerical_pass)
        row[f"certified_at_{suffix}_ignoring_eligibility"] = numerical_pass
    return row


def main() -> int:
    args = parse_args()
    if args.shard_count <= 0 or not 0 <= args.shard_index < args.shard_count:
        raise SystemExit("invalid shard parameters")
    repo_root = args.repo_root.resolve()
    outdir = args.output_dir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    frozen_validation = args.frozen_validation_dir.resolve()
    sys.path.insert(0, str(frozen_validation))
    import external_end_to_end as core  # type: ignore

    metadata = load_metadata(repo_root)
    stability = load_stability(repo_root)
    with args.work_order.open(newline="", encoding="utf-8") as f:
        jobs_all = list(csv.DictReader(f))
    jobs_all = [j for j in jobs_all if j.get("status") == "PREPARED_NOT_EXECUTED"]
    jobs = [j for j in jobs_all if shard_for(j["material_id"], args.shard_count) == args.shard_index]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for job in jobs:
        grouped[job["material_id"]].append(job)

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    material_records: list[dict[str, Any]] = []

    for material_id in sorted(grouped):
        material_jobs = sorted(grouped[material_id], key=lambda j: (j["codec"], float(j["nominal_tolerance_relative"])))
        meta = metadata.get(material_id)
        stab = stability.get(material_id)
        if meta is None or stab is None:
            err = "material missing from metadata or frozen master stability fields"
            for job in material_jobs:
                failures.append({**job, "stage": "preflight", "error": err})
            continue
        try:
            blob = fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="qoi_p1_") as td:
                workdir = Path(td)
                grid, loader = build_grid(meta, blob, workdir)
                field = np.asarray(grid.total, dtype=np.float64)
                ref_info, q_orig, labels_orig = check_reference(meta, grid, field, core)
                material_records.append({
                    "material_id": material_id,
                    "loader": loader,
                    "source_sha256": meta["sha256"],
                    **ref_info,
                    "jobs_planned": len(material_jobs),
                })

                for job in material_jobs:
                    codec_label = job["codec"]
                    rel = float(job["nominal_tolerance_relative"])
                    abs_bound = rel * ref_info["value_ptp"]
                    row_workdir = workdir / f"{codec_label}_{rel:.0e}"
                    row_workdir.mkdir(exist_ok=True)
                    try:
                        t0 = time.time()
                        reconstructed, compressed_bytes, _ = core.codec_roundtrip(
                            CORE_CODEC[codec_label], field, abs_bound, row_workdir
                        )
                        encode_seconds = time.time() - t0
                        reconstructed = np.asarray(reconstructed, dtype=np.float64)
                        if reconstructed.shape != field.shape:
                            raise RuntimeError(f"reconstruction shape mismatch {reconstructed.shape} != {field.shape}")
                        realized = float(np.max(np.abs(reconstructed - field)))
                        if realized > abs_bound * (1 + 1e-6) + 1e-15:
                            raise RuntimeError(f"codec error-bound violation {realized:.9g} > {abs_bound:.9g}")

                        fixed_charges = core.fixed_basin_charges(reconstructed, labels_orig, int(q_orig.size))
                        recon_grid = core.clone_grid_with_total(grid, reconstructed)
                        t1 = time.time()
                        resolved = core.run_bader(recon_grid)
                        bader_seconds = time.time() - t1
                        q_resolved = np.asarray(resolved["charges"], dtype=np.float64)
                        labels_resolved = np.asarray(resolved["atom_labels"])
                        if q_resolved.shape != q_orig.shape:
                            raise RuntimeError(f"resolved charge shape mismatch {q_resolved.shape} != {q_orig.shape}")

                        row = make_master_row(
                            meta=meta, stab=stab, job=job, field=field, reconstructed=reconstructed,
                            compressed_bytes=int(compressed_bytes), encode_seconds=encode_seconds,
                            bader_seconds=bader_seconds, q_orig=q_orig, q_resolved=q_resolved,
                            labels_orig=labels_orig, labels_resolved=labels_resolved,
                            fixed_charges=fixed_charges, value_ptp=float(ref_info["value_ptp"]),
                        )
                        rows.append(row)
                    except Exception as exc:
                        failures.append({**job, "stage": "codec_or_bader_row", "error": f"{type(exc).__name__}: {exc}"})
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}"
            for job in material_jobs:
                failures.append({**job, "stage": "source_or_reference", "error": err})

    rows_path = outdir / f"rows_shard_{args.shard_index:02d}.csv"
    with rows_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MASTER_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    failure_fields = ["material_id", "codec", "nominal_tolerance_relative", "codec_config", "field_fingerprint", "status", "stage", "error"]
    fail_path = outdir / f"failures_shard_{args.shard_index:02d}.csv"
    with fail_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=failure_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(failures)

    manifest = {
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "materials": len(grouped),
        "jobs_planned": len(jobs),
        "rows_success": len(rows),
        "rows_failed": len(failures),
        "accounted": len(rows) + len(failures),
        "material_records": material_records,
    }
    (outdir / f"manifest_shard_{args.shard_index:02d}.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    if manifest["accounted"] != manifest["jobs_planned"]:
        return 3
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
