#!/usr/bin/env python3
"""Provenance-addendum implementation of the frozen residual permutation test.

Scientific semantics remain those in
protocol/ERROR_GEOMETRY_PERMUTATION_V0_1_PREREGISTRATION.md.
The only change from v2 is the frozen provenance addendum: the paired
unshuffled baseline is recomputed in the same pinned environment as the
shuffled counterfactuals, while the released Windows Bader value is retained
as an explicit reconciliation field rather than an exact pass/fail oracle.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mechanism"))
sys.path.insert(0, str(ROOT / "validation"))

import residual_spatial_permutation_v2 as v2
import external_end_to_end as core
from baderkit import Grid


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--list-materials", action="store_true")
    p.add_argument("--material-id")
    p.add_argument("--output-dir")
    p.add_argument("--aggregate-root")
    return p.parse_args()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    if not rows:
        if fields:
            with path.open("w", newline="") as f:
                csv.DictWriter(f, fieldnames=fields).writeheader()
        else:
            path.write_text("")
        return
    fields = fields or list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def process(material_id: str, outdir: Path) -> int:
    if material_id not in v2.selected_materials():
        raise RuntimeError(f"{material_id} is not in the preregistered selected set")

    record = v2.source_record(material_id)
    mech = v2.mechanism_rows(material_id)
    if set(mech) != set(v2.CODECS):
        raise RuntimeError(f"{material_id}: incomplete released mechanism rows {sorted(mech)}")

    outdir.mkdir(parents=True, exist_ok=True)
    permutation_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    reconciliation: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix=f"qoi_geom_v3_{material_id}_") as td:
        workdir = Path(td)
        chgcar, source_sha, source_bytes = v2.load_mp_chgcar(record, workdir)
        grid = Grid.from_dynamic(chgcar)
        field = np.asarray(grid.total, dtype=np.float64)
        if field.size != int(record["npoints"]):
            raise RuntimeError(f"npoints mismatch {field.size} != {record['npoints']}")
        if not np.all(np.isfinite(field)):
            raise RuntimeError("source field contains non-finite values")

        original = core.run_bader(grid)
        q0 = np.asarray(original["charges"], dtype=np.float64)
        labels0 = np.asarray(original["atom_labels"])
        ptp = float(np.ptp(field))
        field_flat = field.ravel()
        density_order = np.argsort(field_flat, kind="stable")
        strata = np.array_split(density_order, v2.N_STRATA)

        provenance = {
            "material_id": material_id,
            "source_url": record["url"],
            "source_sha256_verified": source_sha,
            "source_bytes_verified": source_bytes,
            "npoints": int(field.size),
            "natoms_bader": int(q0.size),
            "value_ptp": ptp,
            "operating_point_source": "mechanism/basin_error_decomposition_summary.csv",
            "baseline_policy": "same-run pinned-environment baseline per provenance addendum",
            "primary_relative_tolerance": v2.PRIMARY_TOL,
            "n_density_rank_strata": v2.N_STRATA,
            "permutation_seeds": list(v2.SEEDS),
        }
        (outdir / "provenance.json").write_text(json.dumps(provenance, indent=2))

        for codec_name in v2.CODECS:
            codec = codec_name.lower()
            released = mech[codec_name]
            abs_bound = v2.PRIMARY_TOL * ptp
            recon, compressed_bytes, mode = core.codec_roundtrip(codec, field, abs_bound, workdir)
            recon = np.asarray(recon, dtype=np.float64)
            delta = recon - field
            dflat = delta.ravel()

            linf = float(np.max(np.abs(dflat)))
            rmse = float(np.sqrt(np.mean(dflat * dflat)))
            mean_signed = float(np.mean(dflat))
            mae = float(np.mean(np.abs(dflat)))
            actual_cr = float(field.nbytes / compressed_bytes)

            expected_linf = float(released["linf"])
            expected_cr = float(released["compression_ratio"])
            legacy_bader_error = float(released["dq_total_max_e"])

            if not v2.close(linf, expected_linf, 2e-6, 2e-10):
                raise RuntimeError(
                    f"{material_id} {codec_name}: Linf provenance mismatch {linf:.12g} vs {expected_linf:.12g}"
                )
            if not v2.close(actual_cr, expected_cr, 2e-6, 2e-8):
                raise RuntimeError(
                    f"{material_id} {codec_name}: compression-ratio provenance mismatch {actual_cr:.12g} vs {expected_cr:.12g}"
                )

            baseline_1 = core.run_bader(core.clone_grid_with_total(grid, recon))
            baseline_2 = core.run_bader(core.clone_grid_with_total(grid, recon))
            q1 = np.asarray(baseline_1["charges"], dtype=np.float64)
            q1_repeat = np.asarray(baseline_2["charges"], dtype=np.float64)
            repeat_max_charge_diff = float(np.max(np.abs(q1 - q1_repeat)))
            if repeat_max_charge_diff > 1e-12:
                raise RuntimeError(
                    f"{material_id} {codec_name}: same-run Bader baseline is not deterministic; max charge diff {repeat_max_charge_diff:.3e} e"
                )

            observed_error = float(np.max(np.abs(q1 - q0)))
            observed_reassigned = float(np.mean(np.asarray(baseline_1["atom_labels"]) != labels0))
            legacy_abs_diff = observed_error - legacy_bader_error
            legacy_rel_diff = (
                legacy_abs_diff / legacy_bader_error if legacy_bader_error > 0 else float("nan")
            )
            reconciliation.append({
                "material_id": material_id,
                "codec": codec_name,
                "relative_tolerance": v2.PRIMARY_TOL,
                "released_resolved_bader_error_e": legacy_bader_error,
                "current_unshuffled_resolved_bader_error_e": observed_error,
                "current_minus_released_e": legacy_abs_diff,
                "relative_difference": legacy_rel_diff,
                "same_run_repeat_max_charge_difference_e": repeat_max_charge_diff,
                "released_linf": expected_linf,
                "current_linf": linf,
                "released_compression_ratio": expected_cr,
                "current_compression_ratio": actual_cr,
            })

            for seed in v2.SEEDS:
                rng = np.random.default_rng(seed)
                shuffled = np.empty_like(dflat)
                for indices in strata:
                    values = dflat[indices].copy()
                    rng.shuffle(values)
                    shuffled[indices] = values

                sh_linf = float(np.max(np.abs(shuffled)))
                sh_rmse = float(np.sqrt(np.mean(shuffled * shuffled)))
                sh_mean = float(np.mean(shuffled))
                sh_mae = float(np.mean(np.abs(shuffled)))
                audit = (
                    v2.close(sh_linf, linf, 0.0, 1e-14 * max(1.0, linf))
                    and v2.close(sh_rmse, rmse, 1e-13, 1e-15)
                    and v2.close(sh_mean, mean_signed, 1e-12, 1e-15)
                    and v2.close(sh_mae, mae, 1e-13, 1e-15)
                )
                if not audit:
                    raise RuntimeError(
                        f"{material_id} {codec_name} seed {seed}: residual multiset audit failed"
                    )

                try:
                    sh_field = field + shuffled.reshape(field.shape)
                    sh_bader = core.run_bader(core.clone_grid_with_total(grid, sh_field))
                    sh_error = float(
                        np.max(np.abs(np.asarray(sh_bader["charges"], dtype=np.float64) - q0))
                    )
                    sh_reassigned = float(
                        np.mean(np.asarray(sh_bader["atom_labels"]) != labels0)
                    )
                    status, error_type, detail = "SUCCESS", "", ""
                except Exception as exc:
                    sh_error, sh_reassigned = float("nan"), float("nan")
                    status, error_type, detail = "BADER_FAILURE", type(exc).__name__, str(exc)
                    failures.append({
                        "material_id": material_id,
                        "codec": codec_name,
                        "seed": seed,
                        "error_type": error_type,
                        "detail": detail,
                    })

                permutation_rows.append({
                    "material_id": material_id,
                    "codec": codec_name,
                    "relative_tolerance": v2.PRIMARY_TOL,
                    "seed": seed,
                    "status": status,
                    "observed_bader_error_e": observed_error,
                    "shuffled_bader_error_e": sh_error,
                    "released_legacy_bader_error_e": legacy_bader_error,
                    "observed_frac_voxels_reassigned": observed_reassigned,
                    "shuffled_frac_voxels_reassigned": sh_reassigned,
                    "observed_realized_linf": linf,
                    "shuffled_realized_linf": sh_linf,
                    "linf_abs_difference": abs(sh_linf - linf),
                    "observed_rmse": rmse,
                    "shuffled_rmse": sh_rmse,
                    "rmse_abs_difference": abs(sh_rmse - rmse),
                    "observed_mean_signed_error": mean_signed,
                    "shuffled_mean_signed_error": sh_mean,
                    "mean_signed_abs_difference": abs(sh_mean - mean_signed),
                    "observed_mae": mae,
                    "shuffled_mae": sh_mae,
                    "mae_abs_difference": abs(sh_mae - mae),
                    "compression_ratio": actual_cr,
                    "compressed_bytes": compressed_bytes,
                    "codec_mode": mode,
                    "released_mechanism_linf": expected_linf,
                    "norm_audit_ok": audit,
                    "same_run_baseline_repeat_max_charge_difference_e": repeat_max_charge_diff,
                    "error_type": error_type,
                    "error_detail": detail,
                })

    write_csv(outdir / "permutation_rows.csv", permutation_rows)
    write_csv(
        outdir / "failures.csv",
        failures,
        ["material_id", "codec", "seed", "error_type", "detail"],
    )
    write_csv(outdir / "baseline_reconciliation.csv", reconciliation)
    print(json.dumps({
        "material_id": material_id,
        "rows": len(permutation_rows),
        "failures": len(failures),
        "all_norm_audits": all(v2.as_bool(r["norm_audit_ok"]) for r in permutation_rows),
        "max_abs_legacy_bader_difference_e": max(abs(float(r["current_minus_released_e"])) for r in reconciliation),
    }))
    return 0


def aggregate(root: Path, outdir: Path) -> int:
    # Frozen scientific aggregation remains exactly the v2/preregistered one.
    rc = v2.aggregate(root, outdir)
    if rc != 0:
        return rc

    reconciliation: list[dict[str, str]] = []
    for path in sorted(root.rglob("baseline_reconciliation.csv")):
        reconciliation.extend(v2.read_csv(path))
    if not reconciliation:
        raise RuntimeError("No baseline reconciliation files found")

    expected_pairs = len(v2.selected_materials()) * len(v2.CODECS)
    if len(reconciliation) != expected_pairs:
        raise RuntimeError(
            f"Baseline reconciliation coverage mismatch: {len(reconciliation)} != {expected_pairs}"
        )

    write_csv(outdir / "legacy_baseline_reconciliation_all.csv", reconciliation)
    diffs = [float(r["current_minus_released_e"]) for r in reconciliation]
    abs_diffs = [abs(x) for x in diffs]
    relative = [abs(float(r["relative_difference"])) for r in reconciliation if math.isfinite(float(r["relative_difference"]))]
    repeats = [float(r["same_run_repeat_max_charge_difference_e"]) for r in reconciliation]

    summary = {
        "n_material_codec_operating_points": len(reconciliation),
        "max_abs_current_minus_released_bader_error_e": max(abs_diffs),
        "median_abs_current_minus_released_bader_error_e": float(np.median(abs_diffs)),
        "max_abs_relative_difference": max(relative) if relative else None,
        "median_abs_relative_difference": float(np.median(relative)) if relative else None,
        "max_same_run_repeat_charge_difference_e": max(repeats),
        "n_current_above_released": sum(x > 0 for x in diffs),
        "n_current_below_released": sum(x < 0 for x in diffs),
        "n_equal_within_1e-12_e": sum(abs(x) <= 1e-12 for x in diffs),
    }
    (outdir / "LEGACY_BASELINE_RECONCILIATION.json").write_text(json.dumps(summary, indent=2))

    report = outdir / "RESIDUAL_SPATIAL_PERMUTATION_REPORT.md"
    existing = report.read_text()
    existing += (
        "\n## Legacy Bader baseline reconciliation\n\n"
        "The 2026-09-01 development release used an under-specified historical Windows Bader environment. "
        "Per the frozen provenance addendum, the permutation estimand uses same-run unshuffled baselines in the current pinned environment; legacy values remain visible rather than overwritten.\n\n"
        f"- material/codec operating points reconciled: **{summary['n_material_codec_operating_points']}**\n"
        f"- median |current - released| resolved-Bader error: **{summary['median_abs_current_minus_released_bader_error_e']:.6g} e**\n"
        f"- maximum |current - released| resolved-Bader error: **{summary['max_abs_current_minus_released_bader_error_e']:.6g} e**\n"
        f"- maximum same-run repeated-baseline charge difference: **{summary['max_same_run_repeat_charge_difference_e']:.3g} e**\n"
        "\nThese reconciliation differences are provenance/platform sensitivity and are not counted as permutation effects.\n"
    )
    report.write_text(existing)
    print("legacy_reconciliation", json.dumps(summary, sort_keys=True))
    return 0


def main() -> int:
    a = parse_args()
    if a.list_materials:
        print(json.dumps(v2.selected_materials()))
        return 0
    if a.material_id:
        if not a.output_dir:
            raise SystemExit("--output-dir required")
        return process(a.material_id, Path(a.output_dir))
    if a.aggregate_root:
        if not a.output_dir:
            raise SystemExit("--output-dir required")
        return aggregate(Path(a.aggregate_root), Path(a.output_dir))
    raise SystemExit("choose --list-materials, --material-id, or --aggregate-root")


if __name__ == "__main__":
    raise SystemExit(main())
