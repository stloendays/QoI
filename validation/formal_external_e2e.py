#!/usr/bin/env python3
"""Formal frozen external rate-fidelity driver.

This driver reproduces the development benchmark's staged sampling policy on the
untouched external corpus while preserving the same failure granularity:

1. Base ladder: every material and codec.
2. Tight ladder: only materials Protocol A.1-eligible at 1e-3 e.
3. Base ladder runs tight -> loose and stops after the first *successful*
   resolved-Bader row with error >= 0.05 e, retaining the boundary row.
4. A codec/tolerance Bader failure is a row-level failure, exactly as in the
   released development failure registry. It does not erase successful rows for
   the same material.
5. Provenance/parser/original-Bader failures are material-level pipeline failures.

No parameter is selected or tuned from external outcomes.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np

import external_end_to_end as core

TIGHT_ELIGIBILITY_TAU = 1e-3
EARLY_STOP_QOI_E = 0.05
BASE_SPLIT_REL = 1e-5


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--material-id", action="append", default=[])
    p.add_argument("--domain", choices=["bulk", "vacuum2d"], default=None)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--shard-count", type=int, default=1)
    p.add_argument("--shard-index", type=int, default=0)
    p.add_argument("--codecs", default="zfp,sz3,sperr")
    p.add_argument("--output-dir", default="validation/formal_results")
    return p.parse_args()


def staged_ladders(codecs: list[str]) -> tuple[dict[str, list[float]], dict[str, list[float]]]:
    all_ladders = core.load_frozen_tolerance_ladders(codecs)
    base: dict[str, list[float]] = {}
    tight: dict[str, list[float]] = {}
    for codec, values in all_ladders.items():
        ascending = sorted(values)
        base[codec] = [x for x in ascending if x >= BASE_SPLIT_REL]
        tight[codec] = [x for x in ascending if x < BASE_SPLIT_REL]
        if not base[codec]:
            raise RuntimeError(f"No base-ladder tolerances recovered for {codec}")
    return base, tight


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        if fieldnames:
            with path.open("w", newline="") as f:
                csv.DictWriter(f, fieldnames=fieldnames).writeheader()
        else:
            path.write_text("")
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def row_failure(
    record: dict[str, Any],
    codec: str,
    rel_tol: float,
    ladder_stage: str,
    failure_stage: str,
    exc: Exception,
) -> dict[str, Any]:
    if failure_stage == "resolved_bader":
        category = "bader_solver_failure"
    elif failure_stage == "codec_roundtrip":
        category = "codec_failure"
    else:
        category = "row_pipeline_failure"
    return {
        "material_id": record["material_id"],
        "corpus": "external",
        "domain": record["domain"],
        "ladder": "tight" if ladder_stage.startswith("tight") else "base",
        "codec": core.CODEC_NAMES[codec],
        "nominal_tolerance_relative": rel_tol,
        "stage": f"{codec}@{rel_tol:g}:{failure_stage}",
        "category": category,
        "detail": f"{type(exc).__name__}: {exc}",
    }


def run_material_formal(
    record: dict[str, Any],
    floor: float,
    codecs: list[str],
    base_ladders: dict[str, list[float]],
    tight_ladders: dict[str, list[float]],
    output_dir: Path,
    row_failures: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run one material, isolating failures at codec/tolerance row granularity."""
    from baderkit import Grid

    rows: list[dict[str, Any]] = []
    material_row_failures_before = len(row_failures)
    tight_enabled = bool(floor < TIGHT_ELIGIBILITY_TAU)
    row_attempts = 0

    with tempfile.TemporaryDirectory(prefix="qoi_formal_e2e_") as td:
        workdir = Path(td)
        chgcar, provenance = core.materialize_chgcar(record, workdir)
        grid = Grid.from_dynamic(chgcar)
        core.audit_grid(record, grid)
        field = np.asarray(grid.total, dtype=np.float64)
        if not np.all(np.isfinite(field)):
            raise RuntimeError("non-finite values in source field")
        value_ptp = float(np.ptp(field))
        if not value_ptp > 0:
            raise RuntimeError("source field has zero peak-to-peak range")

        t_bader0 = time.time()
        original = core.run_bader(grid)
        original_bader_cold_seconds = time.time() - t_bader0
        q_orig = original["charges"]
        labels_orig = original["atom_labels"]
        n_atoms = int(q_orig.size)

        q_fixed_orig = core.fixed_basin_charges(field, labels_orig, n_atoms)
        fixed_self_error = float(np.max(np.abs(q_fixed_orig - q_orig)))
        if fixed_self_error > 1e-7:
            raise RuntimeError(
                f"Fixed-basin self-check failed: max difference {fixed_self_error:.3e} e"
            )

        material_meta = {
            "material_id": record["material_id"],
            "domain": record["domain"],
            "formula": record.get("formula", ""),
            "npoints": int(field.size),
            "natoms_bader": n_atoms,
            "value_ptp": value_ptp,
            "raw_bytes": int(field.nbytes),
            "source_density_min": float(np.min(field)),
            "source_density_max": float(np.max(field)),
            "source_has_negative_density": bool(np.min(field) < 0),
            "stability_floor_A1_e": floor,
            "bader_method": core.BADER_METHOD,
            "bader_vacuum_tol": core.BADER_VACUUM_TOL,
            "bader_persistence_tol": core.BADER_PERSISTENCE_TOL,
            "bader_nna_cutoff": core.BADER_NNA_CUTOFF,
            "original_n_maxima": original["n_maxima"],
            "original_num_vacuum_voxels": original["num_vacuum_voxels"],
            "original_vacuum_charge_e": original["vacuum_charge_e"],
            "fixed_basin_selfcheck_max_e": fixed_self_error,
            "original_bader_cold_seconds": original_bader_cold_seconds,
            "timing_note": "original includes cold/JIT overhead; do not compare as codec speed",
            **provenance,
        }

        for codec in codecs:
            ordered: list[tuple[str, float]] = []
            if tight_enabled:
                ordered.extend(("tight_A1_eligible_1e-3", x) for x in tight_ladders[codec])
            ordered.extend(("base", x) for x in base_ladders[codec])

            for ladder_stage, rel_tol in ordered:
                row_attempts += 1
                abs_bound = float(rel_tol * value_ptp)
                failure_stage = "codec_roundtrip"
                try:
                    t_codec = time.time()
                    reconstructed, compressed_bytes, codec_config = core.codec_roundtrip(
                        codec, field, abs_bound, workdir
                    )
                    codec_seconds = time.time() - t_codec

                    failure_stage = "reconstruction_audit"
                    if reconstructed.shape != field.shape:
                        raise RuntimeError(
                            f"shape mismatch {reconstructed.shape} != {field.shape}"
                        )
                    if not np.all(np.isfinite(reconstructed)):
                        raise RuntimeError("reconstruction contains non-finite values")
                    delta = reconstructed - field
                    realized_linf = float(np.max(np.abs(delta)))
                    rmse = float(np.sqrt(np.mean(delta * delta)))
                    mean_signed_error = float(np.mean(delta))
                    bound_respected = bool(
                        realized_linf <= abs_bound * (1.0 + 1e-6) + 1e-15
                    )

                    failure_stage = "fixed_basin"
                    q_fixed = core.fixed_basin_charges(reconstructed, labels_orig, n_atoms)
                    fixed_metrics = core.error_metrics(q_fixed - q_orig, "Bader_error_fixed")

                    failure_stage = "resolved_bader"
                    recon_grid = core.clone_grid_with_total(grid, reconstructed)
                    t_bader = time.time()
                    resolved = core.run_bader(recon_grid)
                    bader_seconds = time.time() - t_bader
                    q_resolved = resolved["charges"]
                    if q_resolved.shape != q_orig.shape:
                        raise RuntimeError(
                            f"Bader charge shape changed: {q_resolved.shape} != {q_orig.shape}"
                        )
                    resolved_metrics = core.error_metrics(
                        q_resolved - q_orig, "Bader_error_resolved"
                    )

                    failure_stage = "topology_diagnostics"
                    labels_resolved = resolved["atom_labels"]
                    if labels_resolved.shape != labels_orig.shape:
                        raise RuntimeError("Resolved atom-label grid shape changed")
                    atom_domain_migration_fraction = float(
                        np.mean(labels_resolved != labels_orig)
                    )
                    vacuum_label = n_atoms
                    vacuum_mask_orig = labels_orig == vacuum_label
                    vacuum_mask_resolved = labels_resolved == vacuum_label
                    vacuum_mask_change_fraction = float(
                        np.mean(vacuum_mask_orig != vacuum_mask_resolved)
                    )

                    resolved_error = resolved_metrics["Bader_error_resolved_max_e"]
                    early_stop_boundary = bool(
                        ladder_stage == "base" and resolved_error >= EARLY_STOP_QOI_E
                    )
                    row: dict[str, Any] = {
                        **material_meta,
                        "codec": core.CODEC_NAMES[codec],
                        "codec_config": codec_config,
                        "ladder_stage": ladder_stage,
                        "formal_tight_eligible_at_1e-3": tight_enabled,
                        "retained_by_frozen_policy": True,
                        "early_stop_boundary": early_stop_boundary,
                        "nominal_tolerance_relative": rel_tol,
                        "nominal_tolerance_absolute": abs_bound,
                        "realized_Linf": realized_linf,
                        "realized_Linf_over_nominal": realized_linf / abs_bound,
                        "bound_respected": bound_respected,
                        "rmse": rmse,
                        "mean_signed_error": mean_signed_error,
                        "compressed_bytes": int(compressed_bytes),
                        "compression_ratio": float(field.nbytes / compressed_bytes),
                        "bits_per_value": float(8.0 * compressed_bytes / field.size),
                        **fixed_metrics,
                        **resolved_metrics,
                        "Bader_error_fixed_e": fixed_metrics["Bader_error_fixed_max_e"],
                        "Bader_error_resolved_e": resolved_error,
                        "resolved_n_maxima": resolved["n_maxima"],
                        "bader_maxima_count_changed": bool(
                            resolved["n_maxima"] != original["n_maxima"]
                        ),
                        "atom_domain_migration_fraction": atom_domain_migration_fraction,
                        "vacuum_mask_change_fraction": vacuum_mask_change_fraction,
                        "resolved_num_vacuum_voxels": resolved["num_vacuum_voxels"],
                        "resolved_vacuum_charge_e": resolved["vacuum_charge_e"],
                        "encode_decode_seconds": codec_seconds,
                        "resolved_bader_seconds": bader_seconds,
                    }
                    row.update(core.verdict_fields(floor, resolved_error))
                    rows.append(row)
                    print(
                        json.dumps(
                            {
                                "material": record["material_id"],
                                "codec": codec,
                                "rel_tol": rel_tol,
                                "ladder": ladder_stage,
                                "linf_over_nominal": row["realized_Linf_over_nominal"],
                                "fixed_error_e": row["Bader_error_fixed_e"],
                                "resolved_error_e": row["Bader_error_resolved_e"],
                                "migration_fraction": atom_domain_migration_fraction,
                                "compression_ratio": row["compression_ratio"],
                                "early_stop_boundary": early_stop_boundary,
                            },
                            sort_keys=True,
                        ),
                        flush=True,
                    )
                    if early_stop_boundary:
                        break

                except Exception as exc:
                    failure = row_failure(
                        record,
                        codec,
                        rel_tol,
                        ladder_stage,
                        failure_stage,
                        exc,
                    )
                    row_failures.append(failure)
                    print(json.dumps({"row_failure": failure}, sort_keys=True), file=sys.stderr, flush=True)
                    # Row failures do not establish the 0.05-e early-stop condition.
                    # Continue the frozen ladder, matching the released registry semantics.
                    continue

        (output_dir / f"{record['material_id']}_original_bader.json").write_text(
            json.dumps(
                {
                    "atom_charges": q_orig.tolist(),
                    "n_maxima": original["n_maxima"],
                    "num_vacuum_voxels": original["num_vacuum_voxels"],
                    "vacuum_charge_e": original["vacuum_charge_e"],
                },
                indent=2,
            )
        )

    audit = {
        "material_id": record["material_id"],
        "domain": record["domain"],
        "stability_floor_A1_e": floor,
        "tight_enabled": tight_enabled,
        "n_row_attempts": row_attempts,
        "n_rows_computed": len(rows),
        "n_rows_retained": len(rows),
        "n_row_failures": len(row_failures) - material_row_failures_before,
        "n_early_stop_boundaries": sum(bool(r["early_stop_boundary"]) for r in rows),
        "n_rows_dropped_post_early_stop": 0,
        "status": "COMPLETE",
    }
    return rows, audit


def main() -> int:
    args = parse_args()
    codecs = [x.strip().lower() for x in args.codecs.split(",") if x.strip()]
    invalid = sorted(set(codecs) - set(core.CODEC_NAMES))
    if invalid:
        raise SystemExit(f"Invalid codecs: {invalid}")

    base_ladders, tight_ladders = staged_ladders(codecs)
    records = core.load_manifest()
    floors = core.load_floors()

    if args.material_id:
        wanted = set(args.material_id)
        records = [r for r in records if r["material_id"] in wanted]
        missing = wanted - {r["material_id"] for r in records}
        if missing:
            raise SystemExit(f"Material IDs absent from frozen manifest: {sorted(missing)}")
    if args.domain:
        records = [r for r in records if r["domain"] == args.domain]
    if args.limit:
        records = records[: args.limit]

    if args.shard_count < 1:
        raise SystemExit("--shard-count must be >= 1")
    if not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("--shard-index must satisfy 0 <= index < count")
    records = [
        record
        for index, record in enumerate(records)
        if index % args.shard_count == args.shard_index
    ]
    if not records:
        raise SystemExit("No records selected")

    outdir = core.ROOT / args.output_dir
    outdir.mkdir(parents=True, exist_ok=True)

    formal_rows: list[dict[str, Any]] = []
    material_failures: list[dict[str, Any]] = []
    row_failures: list[dict[str, Any]] = []
    material_audit: list[dict[str, Any]] = []

    metadata = {
        "formal_external_protocol": "frozen_staged_v2_row_failure_isolation",
        "manifest_sha256": core.sha256_hex(core.MANIFEST.read_bytes()),
        "stability_floor_sha256": core.sha256_hex(core.FLOORS.read_bytes()),
        "protocol_A1_sha256": core.sha256_hex(core.PROTOCOL_A1.read_bytes()),
        "master_benchmark_sha256": core.sha256_hex(core.MASTER_BENCHMARK.read_bytes()),
        "base_split_relative": BASE_SPLIT_REL,
        "tight_eligibility_tau_e": TIGHT_ELIGIBILITY_TAU,
        "early_stop_resolved_Bader_error_e": EARLY_STOP_QOI_E,
        "row_failure_semantics": "record_and_continue; never silently count as pass",
        "material_failure_semantics": "hard pipeline failure",
        "base_ladders": base_ladders,
        "tight_ladders": tight_ladders,
        "codecs": codecs,
        "selected_materials": [r["material_id"] for r in records],
        "shard_count": args.shard_count,
        "shard_index": args.shard_index,
        "packages": core.package_versions(),
        "bader": {
            "method": core.BADER_METHOD,
            "vacuum_tol": core.BADER_VACUUM_TOL,
            "persistence_tol": core.BADER_PERSISTENCE_TOL,
            "nna_cutoff": core.BADER_NNA_CUTOFF,
        },
    }
    (outdir / "run_metadata.json").write_text(json.dumps(metadata, indent=2))

    for record in records:
        mid = record["material_id"]
        try:
            if mid not in floors:
                raise RuntimeError("missing Protocol A.1 stability floor")
            rows, audit = run_material_formal(
                record,
                floors[mid],
                codecs,
                base_ladders,
                tight_ladders,
                outdir,
                row_failures,
            )
            formal_rows.extend(rows)
            material_audit.append(audit)
        except Exception as exc:
            material_failures.append(
                {
                    "material_id": mid,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            material_audit.append(
                {
                    "material_id": mid,
                    "domain": record["domain"],
                    "stability_floor_A1_e": floors.get(mid, ""),
                    "tight_enabled": "",
                    "n_row_attempts": 0,
                    "n_rows_computed": 0,
                    "n_rows_retained": 0,
                    "n_row_failures": 0,
                    "n_early_stop_boundaries": 0,
                    "n_rows_dropped_post_early_stop": 0,
                    "status": "PIPELINE_FAILURE",
                }
            )
            print(
                json.dumps(
                    {"material": mid, "status": "PIPELINE_FAILURE", "error": repr(exc)}
                ),
                file=sys.stderr,
                flush=True,
            )

    write_csv(outdir / "formal_external_e2e_rows.csv", formal_rows)
    write_csv(outdir / "material_audit.csv", material_audit)
    write_csv(
        outdir / "formal_external_e2e_failures.csv",
        material_failures,
        ["material_id", "error_type", "error"],
    )
    write_csv(
        outdir / "formal_external_e2e_row_failures.csv",
        row_failures,
        [
            "material_id",
            "corpus",
            "domain",
            "ladder",
            "codec",
            "nominal_tolerance_relative",
            "stage",
            "category",
            "detail",
        ],
    )

    summary = {
        "n_materials_selected": len(records),
        "n_materials_complete": sum(x["status"] == "COMPLETE" for x in material_audit),
        "n_material_failures": len(material_failures),
        "n_row_failures": len(row_failures),
        "n_rows_retained": len(formal_rows),
        "all_codec_bounds_respected": bool(formal_rows)
        and all(bool(r["bound_respected"]) for r in formal_rows),
        "n_tight_eligible_materials": sum(
            bool(x["tight_enabled"])
            for x in material_audit
            if x["status"] == "COMPLETE"
        ),
        "n_certified_at_1e-4": sum(bool(r["certified_at_1e-4"]) for r in formal_rows),
        "n_certified_at_1e-3": sum(bool(r["certified_at_1e-3"]) for r in formal_rows),
        "n_certified_at_1e-2": sum(bool(r["certified_at_1e-2"]) for r in formal_rows),
        "n_maxima_count_changes": sum(
            bool(r["bader_maxima_count_changed"]) for r in formal_rows
        ),
        "median_realized_Linf_over_nominal_by_codec": {
            core.CODEC_NAMES[c]: (
                float(
                    np.median(
                        [
                            r["realized_Linf_over_nominal"]
                            for r in formal_rows
                            if r["codec"] == core.CODEC_NAMES[c]
                        ]
                    )
                )
                if any(r["codec"] == core.CODEC_NAMES[c] for r in formal_rows)
                else None
            )
            for c in codecs
        },
        "material_failure_ids": [f["material_id"] for f in material_failures],
        "row_failure_ids": sorted({f["material_id"] for f in row_failures}),
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"summary": summary}, sort_keys=True), flush=True)

    # Row-level failures are an expected, explicit benchmark outcome and do not
    # invalidate the material or shard. Material-level failures do.
    return 0 if not material_failures and formal_rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
