#!/usr/bin/env python3
"""Aggregate QOAC-H v0.2 engineering results against v0.1 and frozen baselines."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

TAU = 1e-6
EXPECTED_MATERIALS = 12
EXPECTED_SETTINGS_PER_MATERIAL = 25
SPERR_FLOOR_CASES = {"mp-1103974", "mp-1188002", "mp-22490"}


def read_many(root: Path, pattern: str) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for path in sorted(root.glob(pattern)):
        if path.stat().st_size == 0:
            continue
        parts.append(pd.read_csv(path))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes", "t"})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--shards-root", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    rows = read_many(args.shards_root, "rows_shard_*.csv")
    failures = read_many(args.shards_root, "failures_shard_*.csv")
    planned = read_many(args.shards_root, "planned_shard_*.csv")
    manifest = pd.read_csv(args.manifest)

    if len(manifest) != EXPECTED_MATERIALS or manifest.material_id.nunique() != EXPECTED_MATERIALS:
        raise RuntimeError("engineering manifest must contain exactly 12 unique materials")
    expected_ids = set(manifest.material_id)
    if set(planned.material_id) != expected_ids:
        raise RuntimeError("planned shard population does not equal frozen v0.1 manifest")
    if set(rows.material_id) - expected_ids:
        raise RuntimeError("unexpected material appeared in v0.2 rows")

    setting_failures = (
        int((failures.stage == "setting").sum())
        if len(failures) and "stage" in failures.columns else 0
    )
    material_failures = (
        int((failures.stage == "material").sum())
        if len(failures) and "stage" in failures.columns else 0
    )
    expected_rows = EXPECTED_MATERIALS * EXPECTED_SETTINGS_PER_MATERIAL
    if len(rows) + setting_failures != expected_rows:
        raise RuntimeError(
            f"incomplete setting accounting: rows={len(rows)} "
            f"setting_failures={setting_failures} expected={expected_rows}"
        )
    if material_failures:
        raise RuntimeError(f"material-level failures present: {material_failures}")

    counts = rows.groupby("material_id").size()
    if set(counts.index) != expected_ids or not np.all(counts.values == EXPECTED_SETTINGS_PER_MATERIAL):
        raise RuntimeError("successful row counts are not exactly 25 per material")

    v01 = pd.read_csv(
        repo / "analysis" / "operator_aware_codec_hartree"
        / "results" / "competitive_material.csv"
    )
    v01 = v01[v01.material_id.isin(expected_ids)].copy()
    if len(v01) != EXPECTED_MATERIALS or v01.material_id.nunique() != EXPECTED_MATERIALS:
        raise RuntimeError("v0.1 competitive authority does not cover exact engineering cohort")

    comparison_rows = []
    for mid in sorted(expected_ids):
        g = rows[rows.material_id == mid].copy()
        dual = bool_series(g["dual_certified_tau_1e-6"])
        cert = g[dual].copy()
        v1 = v01[v01.material_id == mid].iloc[0]

        best = cert.loc[cert.compression_ratio.idxmax()] if len(cert) else None
        max_any = g.loc[g.compression_ratio.idxmax()]
        baseline_cr = float(v1.baseline_best_cr)
        v01_cr = float(v1.qoac_best_cr)

        comparison_rows.append({
            "material_id": mid,
            "system_type": str(g.iloc[0].system_type),
            "v02_dual_certified": bool(best is not None),
            "v02_best_cr": float(best.compression_ratio) if best is not None else np.nan,
            "v02_best_alpha_rel_ptp": float(best.alpha_rel_ptp) if best is not None else np.nan,
            "v02_best_historical_error": float(best.hartree_error_rel_RMSE_historical) if best is not None else np.nan,
            "v02_best_safe_error": float(best.hartree_error_rel_RMSE_safe) if best is not None else np.nan,
            "v02_best_conservative_error": float(best.hartree_error_rel_conservative_alias) if best is not None else np.nan,
            "v02_max_observed_cr": float(max_any.compression_ratio),
            "v02_max_alpha_rel_ptp": float(max_any.alpha_rel_ptp),
            "v01_best_cr": v01_cr,
            "baseline_best_cr": baseline_cr,
            "baseline_codec": str(v1.baseline_codec),
            "v02_over_v01_cr": float(best.compression_ratio / v01_cr) if best is not None else np.nan,
            "v02_over_baseline_cr": float(best.compression_ratio / baseline_cr) if best is not None else np.nan,
            "v02_beats_baseline": bool(best is not None and best.compression_ratio > baseline_cr),
            "max_cr_exceeds_baseline": bool(float(max_any.compression_ratio) > baseline_cr),
            "is_v01_sperr_floor_case": mid in SPERR_FLOOR_CASES,
        })

    comp = pd.DataFrame(comparison_rows)
    comparable = comp[np.isfinite(comp.v02_over_baseline_cr)].copy()
    certified_n = int(comp.v02_dual_certified.sum())
    median_v02_over_v01 = float(np.median(comp.v02_over_v01_cr.dropna()))
    median_v02_over_baseline = float(np.median(comp.v02_over_baseline_cr.dropna()))
    wins = int(comp.v02_beats_baseline.sum())

    floor = comp[comp.is_v01_sperr_floor_case].copy()
    floor_all_ceiling_fixed = bool(
        len(floor) == len(SPERR_FLOOR_CASES)
        and floor.max_cr_exceeds_baseline.all()
    )

    promotion_ready = bool(
        len(rows) == expected_rows
        and len(failures) == 0
        and certified_n == EXPECTED_MATERIALS
        and median_v02_over_v01 > 1.05
        and median_v02_over_baseline > 1.05
        and wins >= 9
        and floor_all_ceiling_fixed
    )

    summary = {
        "status": "COMPLETE",
        "role": "ENGINEERING_TUNING_NOT_CONFIRMATORY",
        "pilot_materials": EXPECTED_MATERIALS,
        "rows_success": int(len(rows)),
        "failures": int(len(failures)),
        "primary_tau": TAU,
        "dual_certified_materials": certified_n,
        "median_cr_ratio_v02_over_v01": median_v02_over_v01,
        "median_cr_ratio_v02_over_best_existing_baseline": median_v02_over_baseline,
        "materials_v02_beats_best_existing_baseline": wins,
        "sperr_floor_cases": {
            "materials": sorted(SPERR_FLOOR_CASES),
            "all_max_cr_exceed_baseline": floor_all_ceiling_fixed,
            "detail": {
                r.material_id: {
                    "max_v02_cr": float(r.v02_max_observed_cr),
                    "baseline_cr": float(r.baseline_best_cr),
                    "ceiling_ratio": float(r.v02_max_observed_cr / r.baseline_best_cr),
                }
                for _, r in floor.iterrows()
            },
        },
        "promotion_criteria": {
            "all_12_accounted_zero_failures": bool(len(rows) == expected_rows and len(failures) == 0),
            "all_12_dual_certified": certified_n == EXPECTED_MATERIALS,
            "median_v02_over_v01_gt_1p05": median_v02_over_v01 > 1.05,
            "median_v02_over_baseline_gt_1p05": median_v02_over_baseline > 1.05,
            "wins_ge_9_of_12": wins >= 9,
            "all_three_sperr_floor_ceiling_fixed": floor_all_ceiling_fixed,
        },
        "promotion_ready_for_held_out_confirmation": promotion_ready,
        "interpretation": (
            "PROMOTION_READY_FOR_HELD_OUT_CONFIRMATION"
            if promotion_ready
            else "ENGINEERING_NOT_YET_PROMOTION_READY"
        ),
    }

    rows.to_csv(out / "engineering_rows.csv", index=False)
    failures.to_csv(out / "failures.csv", index=False)
    comp.to_csv(out / "material_comparison.csv", index=False)
    manifest.to_csv(out / "ENGINEERING_MANIFEST.csv", index=False)
    (out / "ENGINEERING_SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    floor_lines = []
    for _, r in floor.iterrows():
        floor_lines.append(
            f"- {r.material_id}: max v0.2 CR {r.v02_max_observed_cr:.4g} "
            f"vs baseline {r.baseline_best_cr:.4g} "
            f"(ceiling ratio {r.v02_max_observed_cr / r.baseline_best_cr:.4g})"
        )

    report = [
        "# QOAC-H v0.2 engineering results",
        "",
        f"Status: **{summary['interpretation']}**",
        "",
        "This is a tuning-cohort engineering result, not an independent confirmatory claim.",
        "",
        f"- Successful rows: **{len(rows)}/{expected_rows}**; failures: **{len(failures)}**.",
        f"- Dual-certified materials at tau={TAU:g}: **{certified_n}/12**.",
        f"- Median CR(v0.2) / CR(v0.1): **{median_v02_over_v01:.4g}**.",
        f"- Median CR(v0.2) / best existing baseline: **{median_v02_over_baseline:.4g}**.",
        f"- Materials beating best existing baseline: **{wins}/12**.",
        f"- All three prior SPERR rate ceilings removed: **{floor_all_ceiling_fixed}**.",
        "",
        "## Prior SPERR-leading rate-floor cases",
        "",
        *floor_lines,
        "",
        "## Promotion decision",
        "",
        f"- Ready for held-out confirmation: **{promotion_ready}**.",
        "",
        "A positive promotion decision means only that the architecture is worth freezing and testing on a disjoint cohort or the full development population.",
    ]
    (out / "RESULTS.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
