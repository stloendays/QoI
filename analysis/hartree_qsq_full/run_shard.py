#!/usr/bin/env python3
"""Run one shard of the full-population Hartree-QSQ generality study.

Scientific scope is frozen in DESIGN.md. This runner:
- uses the 254-material prospective-QSQ development cohort;
- verifies exact source bytes and development loader identity;
- computes five-seed Hartree reference responses at the frozen QSQ amplitude;
- regenerates every frozen successful ZFP/SZ3/SPERR reconstruction row;
- gates regenerated realized L-infinity against the frozen benchmark row;
- computes Hartree-potential relative RMSE/Linf on the same reconstruction.

No Bader calculation is rerun. Frozen Bader errors are carried as contrast only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

SEEDS = (20260905, 1, 2, 3, 4)
CODECS = {"zfp": "ZFP", "sz3": "SZ3", "sperr": "SPERR"}
PTP_RTOL = 1e-12
PTP_ATOL = 1e-12
LINF_RTOL = 2e-6
LINF_ATOL = 2e-12


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-validation-dir", type=Path, required=True)
    p.add_argument("--shard-count", type=int, required=True)
    p.add_argument("--shard-index", type=int, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def finite_float(x: Any) -> float | None:
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def shard_for(material_id: str, n: int) -> int:
    d = hashlib.sha256(("HARTREE-QSQ-FULL|" + material_id).encode()).digest()
    return int.from_bytes(d[:8], "big") % n


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cohort(repo: Path) -> list[str]:
    path = repo / "analysis" / "research_upgrade" / "p2_fresh_probe_material_summary.csv"
    mids: list[str] = []
    seen: set[str] = set()
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mid = row["material_id"]
            if mid not in seen:
                seen.add(mid)
                mids.append(mid)
    if len(mids) != 254:
        raise RuntimeError(f"development cohort drift: expected 254, got {len(mids)}")
    return mids


def load_metadata(repo: Path) -> dict[str, dict[str, str]]:
    with (repo / "materials_metadata.csv").open(newline="", encoding="utf-8") as f:
        return {r["material_id"]: r for r in csv.DictReader(f)}


def load_amplitudes(repo: Path, cohort: set[str]) -> dict[str, float]:
    path = repo / "stability" / "stability_floor_A1_per_seed.csv"
    vals: dict[str, list[float]] = defaultdict(list)
    seeds: dict[str, set[int]] = defaultdict(set)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mid = row["material_id"]
            if mid not in cohort:
                continue
            vals[mid].append(float(row["probe_linf"]))
            seeds[mid].add(int(row["seed"]))
    out: dict[str, float] = {}
    for mid in cohort:
        if seeds[mid] != set(SEEDS):
            raise RuntimeError(f"historical QSQ seed-set drift for {mid}: {seeds[mid]}")
        v = vals[mid]
        if len(v) != len(SEEDS) or not np.allclose(v, v[0], rtol=0.0, atol=0.0):
            raise RuntimeError(f"historical QSQ amplitude drift for {mid}")
        out[mid] = float(v[0])
    return out


def load_benchmark_rows(repo: Path, cohort: set[str]) -> dict[str, list[dict[str, str]]]:
    path = repo / "benchmark" / "master_benchmark_full.csv"
    by_material: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {
            "material_id", "codec", "nominal_tolerance_relative",
            "nominal_tolerance_absolute", "realized_Linf", "value_ptp",
            "compression_ratio", "compressed_bytes",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"master benchmark missing columns: {sorted(missing)}")
        for row in reader:
            mid = row["material_id"]
            codec = row["codec"].strip().lower()
            if mid not in cohort or codec not in CODECS:
                continue
            if finite_float(row.get("nominal_tolerance_absolute")) is None:
                continue
            if finite_float(row.get("realized_Linf")) is None:
                continue
            by_material[mid].append(row)
    missing_materials = sorted(cohort - set(by_material))
    if missing_materials:
        raise RuntimeError(f"cohort materials absent from master benchmark: {missing_materials[:8]} (n={len(missing_materials)})")
    return by_material


def write_csv(path: Path, rows: list[dict[str, Any]], preferred_fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(preferred_fields)
    extra = sorted({k for r in rows for k in r} - set(fields))
    fields.extend(extra)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    args = parse_args()
    if args.shard_count <= 0 or not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("invalid shard parameters")

    repo = args.repo_root.resolve()
    frozen_validation = args.frozen_validation_dir.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    sys.path.insert(0, str(repo / "analysis"))
    sys.path.insert(0, str(frozen_validation))

    import development_compatibility_smoke as dev  # type: ignore
    import external_end_to_end as core  # type: ignore
    from hartree_potential_pilot.run_hartree_pilot import reciprocal_g2, hartree_potential  # type: ignore

    cohort_all = load_cohort(repo)
    cohort_set = set(cohort_all)
    metadata = load_metadata(repo)
    amplitudes = load_amplitudes(repo, cohort_set)
    benchmark = load_benchmark_rows(repo, cohort_set)

    planned = [mid for mid in cohort_all if shard_for(mid, args.shard_count) == args.shard_index]

    qsq_rows: list[dict[str, Any]] = []
    codec_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    material_records: list[dict[str, Any]] = []

    for mid in planned:
        meta = metadata.get(mid)
        if meta is None:
            failures.append({"material_id": mid, "stage": "metadata", "error": "missing materials_metadata row"})
            continue

        try:
            blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="hartree_qsq_full_") as td:
                workdir = Path(td)
                grid, loader = dev.build_grid(meta, blob, workdir)
                field = np.asarray(grid.total, dtype=np.float64)
                expected_shape = dev.parse_shape(meta["ngrid"])
                if tuple(field.shape) != expected_shape:
                    raise RuntimeError(f"shape mismatch {field.shape} != {expected_shape}")
                if field.size != int(meta["npoints"]):
                    raise RuntimeError(f"npoints mismatch {field.size} != {meta['npoints']}")
                if len(grid.structure) != int(meta["natoms"]):
                    raise RuntimeError(f"natoms mismatch {len(grid.structure)} != {meta['natoms']}")
                if not np.all(np.isfinite(field)):
                    raise RuntimeError("reference field contains non-finite values")

                value_ptp = float(np.ptp(field))
                frozen_ptps = [
                    finite_float(r.get("value_ptp")) for r in benchmark[mid]
                    if finite_float(r.get("value_ptp")) is not None
                ]
                if not frozen_ptps:
                    raise RuntimeError("no frozen value_ptp for material")
                expected_ptp = float(frozen_ptps[0])
                if not np.isclose(value_ptp, expected_ptp, rtol=PTP_RTOL, atol=PTP_ATOL):
                    raise RuntimeError(f"value_ptp mismatch {value_ptp} != {expected_ptp}")

                epsilon = amplitudes[mid]
                f32 = field.astype(np.float32).astype(np.float64)
                eps_recomputed = float(np.max(np.abs(f32 - field)))
                amp_atol = max(1e-15, 16 * np.finfo(np.float64).eps * max(1.0, abs(epsilon)))
                amp_ok = bool(np.isclose(eps_recomputed, epsilon, rtol=1e-10, atol=amp_atol))
                if not amp_ok:
                    raise RuntimeError(f"float32 amplitude mismatch {eps_recomputed} != {epsilon}")

                lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)
                g2 = reciprocal_g2(field.shape, lattice)
                v0 = hartree_potential(field, g2)
                v0_rms = float(np.sqrt(np.mean(v0 * v0)))
                v0_ptp = float(np.ptp(v0))
                if not np.isfinite(v0_rms) or v0_rms <= 0:
                    raise RuntimeError(f"invalid Hartree reference RMS {v0_rms}")

                seed_responses: list[float] = []
                for seed in SEEDS:
                    rng = np.random.Generator(np.random.PCG64(seed))
                    noise = rng.uniform(-epsilon, epsilon, size=field.shape).astype(np.float64, copy=False)
                    measured_linf = float(np.max(np.abs(noise))) if noise.size else 0.0
                    if measured_linf > epsilon * (1 + 16 * np.finfo(np.float64).eps):
                        raise RuntimeError(f"noise exceeds epsilon for seed {seed}")
                    dv = hartree_potential(noise, g2)
                    rel_rmse = float(np.sqrt(np.mean(dv * dv)) / v0_rms)
                    rel_linf = float(np.max(np.abs(dv)) / v0_rms)
                    if not (np.isfinite(rel_rmse) and np.isfinite(rel_linf)):
                        raise RuntimeError(f"non-finite Hartree seed response for {seed}")
                    seed_responses.append(rel_rmse)
                    qsq_rows.append({
                        "material_id": mid,
                        "corpus": meta["corpus"],
                        "system_type": meta["system_type"],
                        "source": meta["source"],
                        "formula": meta["formula"],
                        "seed": seed,
                        "epsilon": epsilon,
                        "measured_noise_Linf": measured_linf,
                        "hartree_response_rel_RMSE": rel_rmse,
                        "hartree_response_rel_Linf_over_Vrms": rel_linf,
                        "mean_noise": float(np.mean(noise)),
                        "npoints": int(field.size),
                        "source_sha256": meta["sha256"],
                    })

                response_scale = float(max(seed_responses))
                material_records.append({
                    "material_id": mid,
                    "corpus": meta["corpus"],
                    "system_type": meta["system_type"],
                    "source": meta["source"],
                    "formula": meta["formula"],
                    "loader": loader,
                    "npoints": int(field.size),
                    "natoms": int(meta["natoms"]),
                    "value_ptp": value_ptp,
                    "epsilon": epsilon,
                    "epsilon_recomputed": eps_recomputed,
                    "V_orig_rms": v0_rms,
                    "V_orig_ptp": v0_ptp,
                    "hartree_qsq_response_scale_rel_RMSE": response_scale,
                    "hartree_qsq_response_median_rel_RMSE": float(np.median(seed_responses)),
                    "benchmark_rows_planned": len(benchmark[mid]),
                    "source_sha256": meta["sha256"],
                })

                for idx, frozen in enumerate(benchmark[mid]):
                    codec = frozen["codec"].strip().lower()
                    try:
                        abs_bound = float(frozen["nominal_tolerance_absolute"])
                        reconstructed, compressed_bytes, codec_config = core.codec_roundtrip(
                            codec, field, abs_bound, workdir
                        )
                        reconstructed = np.asarray(reconstructed, dtype=np.float64)
                        if reconstructed.shape != field.shape:
                            raise RuntimeError(f"shape mismatch {reconstructed.shape} != {field.shape}")
                        if not np.all(np.isfinite(reconstructed)):
                            raise RuntimeError("non-finite reconstructed field")

                        delta = reconstructed - field
                        realized_linf = float(np.max(np.abs(delta)))
                        frozen_linf = float(frozen["realized_Linf"])
                        linf_match = bool(np.isclose(
                            realized_linf, frozen_linf, rtol=LINF_RTOL, atol=LINF_ATOL
                        ))
                        bound_respected = bool(
                            realized_linf <= abs_bound * (1 + 1e-6) + 1e-15
                        )

                        dv = hartree_potential(delta, g2)
                        hartree_rmse = float(np.sqrt(np.mean(dv * dv)) / v0_rms)
                        hartree_linf = float(np.max(np.abs(dv)) / v0_rms)
                        if not (np.isfinite(hartree_rmse) and np.isfinite(hartree_linf)):
                            raise RuntimeError("non-finite Hartree reconstruction error")

                        frozen_bytes = int(float(frozen["compressed_bytes"]))
                        compression_ratio_reproduced = float(field.nbytes / int(compressed_bytes))
                        bader = finite_float(frozen.get("Bader_error_resolved_e"))
                        frozen_cr = finite_float(frozen.get("compression_ratio"))

                        codec_rows.append({
                            "material_id": mid,
                            "corpus": meta["corpus"],
                            "system_type": meta["system_type"],
                            "source": meta["source"],
                            "formula": meta["formula"],
                            "codec": CODECS[codec],
                            "codec_config_reproduced": codec_config,
                            "ladder": frozen.get("ladder", ""),
                            "nominal_tolerance_relative": finite_float(frozen.get("nominal_tolerance_relative")),
                            "nominal_tolerance_absolute": abs_bound,
                            "frozen_realized_Linf": frozen_linf,
                            "reproduced_realized_Linf": realized_linf,
                            "realized_Linf_match": linf_match,
                            "bound_respected": bound_respected,
                            "frozen_compressed_bytes": frozen_bytes,
                            "reproduced_compressed_bytes": int(compressed_bytes),
                            "compressed_bytes_exact": int(compressed_bytes) == frozen_bytes,
                            "frozen_compression_ratio": frozen_cr,
                            "reproduced_compression_ratio": compression_ratio_reproduced,
                            "hartree_qsq_response_scale_rel_RMSE": response_scale,
                            "hartree_error_rel_RMSE": hartree_rmse,
                            "hartree_error_rel_Linf_over_Vrms": hartree_linf,
                            "frozen_Bader_error_resolved_e": bader,
                            "frozen_stability_floor_A1_e": finite_float(frozen.get("stability_floor_A1_e")),
                            "value_ptp": value_ptp,
                            "npoints": int(field.size),
                            "source_sha256": meta["sha256"],
                            "scientific_reproduction_gate_pass": bool(linf_match and bound_respected),
                            "frozen_row_index_within_material": idx,
                        })
                    except Exception as exc:
                        failures.append({
                            "material_id": mid,
                            "stage": "codec_row",
                            "codec": frozen.get("codec", ""),
                            "nominal_tolerance_relative": frozen.get("nominal_tolerance_relative", ""),
                            "nominal_tolerance_absolute": frozen.get("nominal_tolerance_absolute", ""),
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                        })

        except Exception as exc:
            failures.append({
                "material_id": mid,
                "stage": "source_or_reference",
                "error_type": type(exc).__name__,
                "error": str(exc),
            })

    qsq_rows.sort(key=lambda r: (r["material_id"], int(r["seed"])))
    codec_rows.sort(key=lambda r: (
        r["material_id"], r["codec"],
        float(r["nominal_tolerance_absolute"]), int(r["frozen_row_index_within_material"])
    ))
    failures.sort(key=lambda r: (
        r.get("material_id", ""), r.get("stage", ""),
        str(r.get("codec", "")), str(r.get("nominal_tolerance_absolute", ""))
    ))

    write_csv(
        out / f"hartree_qsq_per_seed_shard_{args.shard_index:02d}.csv",
        qsq_rows,
        ["material_id", "corpus", "system_type", "source", "formula", "seed", "epsilon",
         "measured_noise_Linf", "hartree_response_rel_RMSE",
         "hartree_response_rel_Linf_over_Vrms", "mean_noise", "npoints", "source_sha256"],
    )
    write_csv(
        out / f"hartree_codec_rows_shard_{args.shard_index:02d}.csv",
        codec_rows,
        ["material_id", "corpus", "system_type", "source", "formula", "codec",
         "ladder", "nominal_tolerance_relative", "nominal_tolerance_absolute",
         "frozen_realized_Linf", "reproduced_realized_Linf", "realized_Linf_match",
         "bound_respected", "frozen_compressed_bytes", "reproduced_compressed_bytes",
         "compressed_bytes_exact", "frozen_compression_ratio", "reproduced_compression_ratio",
         "hartree_qsq_response_scale_rel_RMSE", "hartree_error_rel_RMSE",
         "hartree_error_rel_Linf_over_Vrms", "frozen_Bader_error_resolved_e",
         "frozen_stability_floor_A1_e", "value_ptp", "npoints", "source_sha256",
         "scientific_reproduction_gate_pass"],
    )
    write_csv(
        out / f"failures_shard_{args.shard_index:02d}.csv",
        failures,
        ["material_id", "stage", "codec", "nominal_tolerance_relative",
         "nominal_tolerance_absolute", "error_type", "error"],
    )

    manifest = {
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "materials_planned": planned,
        "n_materials_planned": len(planned),
        "n_material_records": len(material_records),
        "n_qsq_rows": len(qsq_rows),
        "n_codec_rows": len(codec_rows),
        "n_failures": len(failures),
        "n_scientific_gate_fail_rows": sum(
            not bool(r["scientific_reproduction_gate_pass"]) for r in codec_rows
        ),
        "material_records": material_records,
        "inputs": {
            "master_benchmark_sha256": sha256_file(repo / "benchmark" / "master_benchmark_full.csv"),
            "materials_metadata_sha256": sha256_file(repo / "materials_metadata.csv"),
            "p2_material_summary_sha256": sha256_file(
                repo / "analysis" / "research_upgrade" / "p2_fresh_probe_material_summary.csv"
            ),
            "qsq_seed_table_sha256": sha256_file(repo / "stability" / "stability_floor_A1_per_seed.csv"),
        },
        "timing_epoch_seconds": time.time(),
    }
    (out / f"manifest_shard_{args.shard_index:02d}.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps({
        "status": "ACCOUNTED",
        "shard": args.shard_index,
        "materials_planned": len(planned),
        "materials_reference_complete": len(material_records),
        "qsq_rows": len(qsq_rows),
        "codec_rows": len(codec_rows),
        "failures": len(failures),
        "scientific_gate_fail_rows": manifest["n_scientific_gate_fail_rows"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
