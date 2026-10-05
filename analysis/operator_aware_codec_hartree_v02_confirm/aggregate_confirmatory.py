#!/usr/bin/env python3
"""Aggregate the frozen 242-material QOAC-H v0.2 held-out confirmation."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

TAU = 1e-6
EXPECTED_MATERIALS = 242
EXPECTED_SETTINGS = 25
EXPECTED_ROWS = EXPECTED_MATERIALS * EXPECTED_SETTINGS
EXPECTED_BASELINE_MISSING = {"mp-1038991"}
BOOTSTRAP_SEED = 20261005
BOOTSTRAP_N = 20000
Z95 = 1.959963984540054


def read_many(root: Path, pattern: str) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for path in sorted(root.glob(pattern)):
        if path.stat().st_size == 0:
            continue
        parts.append(pd.read_csv(path))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def truthy_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "t"})


def bootstrap_ratio_stats(values: np.ndarray) -> dict[str, float | list[float]]:
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 1 or len(x) == 0 or np.any(~np.isfinite(x)) or np.any(x < 0):
        raise ValueError("invalid bootstrap ratio vector")

    median = float(np.median(x))
    geometric_mean = (
        0.0 if np.any(x <= 0)
        else float(np.exp(np.mean(np.log(x))))
    )

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    med = np.empty(BOOTSTRAP_N, dtype=np.float64)
    geo = np.empty(BOOTSTRAP_N, dtype=np.float64)
    n = len(x)
    for i in range(BOOTSTRAP_N):
        sample = x[rng.integers(0, n, n)]
        med[i] = np.median(sample)
        geo[i] = (
            0.0 if np.any(sample <= 0)
            else np.exp(np.mean(np.log(sample)))
        )

    return {
        "n": int(n),
        "median": median,
        "median_bootstrap_95_ci": [
            float(np.quantile(med, 0.025)),
            float(np.quantile(med, 0.975)),
        ],
        "geometric_mean": geometric_mean,
        "geometric_mean_bootstrap_95_ci": [
            float(np.quantile(geo, 0.025)),
            float(np.quantile(geo, 0.975)),
        ],
        "p10": float(np.quantile(x, 0.10)),
        "p90": float(np.quantile(x, 0.90)),
    }


def wilson_interval(successes: int, n: int) -> tuple[float, float]:
    if n <= 0:
        return (math.nan, math.nan)
    phat = successes / n
    denom = 1.0 + Z95 * Z95 / n
    center = (phat + Z95 * Z95 / (2.0 * n)) / denom
    half = (
        Z95
        * math.sqrt(phat * (1.0 - phat) / n + Z95 * Z95 / (4.0 * n * n))
        / denom
    )
    return (max(0.0, center - half), min(1.0, center + half))


def load_baselines(path: Path, ids: set[str]) -> dict[str, dict[str, float | str]]:
    best: dict[str, dict[str, float | str]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mid = row["material_id"]
            if mid not in ids:
                continue
            if str(row.get("scientific_reproduction_gate_pass", "")).strip().lower() not in {
                "true", "1", "yes", "t"
            }:
                continue
            try:
                err = float(row["hartree_error_rel_RMSE"])
                cr = float(row["reproduced_compression_ratio"])
            except (TypeError, ValueError):
                continue
            if not (np.isfinite(err) and np.isfinite(cr) and cr > 0 and err < TAU):
                continue
            current = best.get(mid)
            if current is None or cr > float(current["compression_ratio"]):
                best[mid] = {
                    "codec": row["codec"],
                    "compression_ratio": cr,
                    "hartree_error": err,
                    "nominal_tolerance_relative": float(row["nominal_tolerance_relative"]),
                    "frozen_row_index_within_material": int(float(row["frozen_row_index_within_material"])),
                }
    return best


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

    manifest = pd.read_csv(args.manifest)
    if len(manifest) != EXPECTED_MATERIALS or manifest.material_id.nunique() != EXPECTED_MATERIALS:
        raise RuntimeError("held-out manifest cardinality drift")
    if not truthy_series(manifest["eligible_tau_1e-6"]).all():
        raise RuntimeError("held-out manifest includes a non-eligible material")
    if not np.all(
        manifest.hartree_qsq_response_scale_rel_RMSE.to_numpy(dtype=float) < TAU
    ):
        raise RuntimeError("held-out QSQ response scale violates tau=1e-6")

    ids = set(manifest.material_id)
    rows = read_many(args.shards_root, "rows_shard_*.csv")
    failures = read_many(args.shards_root, "failures_shard_*.csv")
    planned = read_many(args.shards_root, "planned_shard_*.csv")

    if set(planned.material_id) != ids:
        missing = sorted(ids - set(planned.material_id))
        extra = sorted(set(planned.material_id) - ids)
        raise RuntimeError(f"planned population mismatch missing={missing[:8]} extra={extra[:8]}")
    if len(rows) != EXPECTED_ROWS:
        raise RuntimeError(f"successful row count {len(rows)} != {EXPECTED_ROWS}")
    if len(failures) != 0:
        raise RuntimeError(f"confirmatory execution contains {len(failures)} failures")
    counts = rows.groupby("material_id").size()
    if set(counts.index) != ids or not np.all(counts.values == EXPECTED_SETTINGS):
        raise RuntimeError("not exactly 25 successful rows for every held-out material")

    baseline = load_baselines(
        repo / "analysis" / "hartree_qsq_full" / "results" / "hartree_codec_rows.csv",
        ids,
    )
    baseline_missing = ids - set(baseline)
    if baseline_missing != EXPECTED_BASELINE_MISSING:
        raise RuntimeError(
            f"frozen baseline missing-set drift: {sorted(baseline_missing)}"
        )

    comp_rows: list[dict] = []
    selected_rows: list[dict] = []

    for mid in sorted(ids):
        g = rows[rows.material_id == mid].copy()
        cert = g[truthy_series(g["dual_certified_tau_1e-6"])].copy()
        best_q = cert.loc[cert.compression_ratio.idxmax()] if len(cert) else None
        base = baseline.get(mid)

        if best_q is not None:
            selected_rows.append(best_q.to_dict())

        if base is not None:
            if best_q is None:
                ratio = 0.0
                q_cr = math.nan
                q_hist = q_safe = q_cons = math.nan
                q_alpha = math.nan
            else:
                q_cr = float(best_q.compression_ratio)
                ratio = q_cr / float(base["compression_ratio"])
                q_hist = float(best_q.hartree_error_rel_RMSE_historical)
                q_safe = float(best_q.hartree_error_rel_RMSE_safe)
                q_cons = float(best_q.hartree_error_rel_conservative_alias)
                q_alpha = float(best_q.alpha_rel_ptp)
        else:
            ratio = math.nan
            q_cr = float(best_q.compression_ratio) if best_q is not None else math.nan
            q_hist = (
                float(best_q.hartree_error_rel_RMSE_historical)
                if best_q is not None else math.nan
            )
            q_safe = (
                float(best_q.hartree_error_rel_RMSE_safe)
                if best_q is not None else math.nan
            )
            q_cons = (
                float(best_q.hartree_error_rel_conservative_alias)
                if best_q is not None else math.nan
            )
            q_alpha = float(best_q.alpha_rel_ptp) if best_q is not None else math.nan

        manifest_row = manifest[manifest.material_id == mid].iloc[0]
        comp_rows.append({
            "material_id": mid,
            "system_type": str(manifest_row.system_type),
            "formula": str(manifest_row.formula),
            "qsq_response_scale_rel_RMSE": float(
                manifest_row.hartree_qsq_response_scale_rel_RMSE
            ),
            "qoac_dual_certified": bool(best_q is not None),
            "qoac_best_cr": q_cr,
            "qoac_best_alpha_rel_ptp": q_alpha,
            "qoac_best_historical_error": q_hist,
            "qoac_best_safe_error": q_safe,
            "qoac_best_conservative_error": q_cons,
            "baseline_available": bool(base is not None),
            "baseline_codec": str(base["codec"]) if base is not None else "",
            "baseline_best_cr": (
                float(base["compression_ratio"]) if base is not None else math.nan
            ),
            "baseline_hartree_error": (
                float(base["hartree_error"]) if base is not None else math.nan
            ),
            "cr_ratio_qoac_over_baseline_primary": ratio,
            "qoac_beats_baseline": bool(np.isfinite(ratio) and ratio > 1.0),
            "qoac_certification_failure_counted_as_zero_ratio": bool(
                base is not None and best_q is None
            ),
        })

    comp = pd.DataFrame(comp_rows)
    selected = pd.DataFrame(selected_rows)

    certified_n = int(comp.qoac_dual_certified.sum())
    certified_fraction = certified_n / EXPECTED_MATERIALS

    paired = comp[comp.baseline_available].copy()
    if len(paired) != 241:
        raise RuntimeError(f"paired population {len(paired)} != 241")
    ratios = paired.cr_ratio_qoac_over_baseline_primary.to_numpy(dtype=float)
    overall = bootstrap_ratio_stats(ratios)

    wins = int(np.sum(ratios > 1.0))
    win_fraction = wins / len(ratios)
    win_ci = wilson_interval(wins, len(ratios))

    subgroup: dict[str, dict] = {}
    for label in ("bulk", "slab"):
        g = paired[paired.system_type == label]
        values = g.cr_ratio_qoac_over_baseline_primary.to_numpy(dtype=float)
        stats = bootstrap_ratio_stats(values)
        swins = int(np.sum(values > 1.0))
        stats["wins"] = swins
        stats["win_fraction"] = swins / len(values)
        stats["win_fraction_wilson_95_ci"] = list(wilson_interval(swins, len(values)))
        subgroup[label] = stats

    certified_only = paired[paired.qoac_dual_certified].copy()
    certified_only_stats = bootstrap_ratio_stats(
        certified_only.cr_ratio_qoac_over_baseline_primary.to_numpy(dtype=float)
    )

    baseline_codec_counts = {
        str(k): int(v)
        for k, v in paired.baseline_codec.value_counts().sort_index().items()
    }

    missing_row = comp[comp.material_id == "mp-1038991"].iloc[0]
    missing_baseline_outcome = {
        "material_id": "mp-1038991",
        "qoac_dual_certified": bool(missing_row.qoac_dual_certified),
        "qoac_best_cr": (
            float(missing_row.qoac_best_cr)
            if np.isfinite(missing_row.qoac_best_cr) else None
        ),
        "qoac_best_historical_error": (
            float(missing_row.qoac_best_historical_error)
            if np.isfinite(missing_row.qoac_best_historical_error) else None
        ),
        "qoac_best_conservative_error": (
            float(missing_row.qoac_best_conservative_error)
            if np.isfinite(missing_row.qoac_best_conservative_error) else None
        ),
    }

    pipeline_gate = bool(
        len(rows) == EXPECTED_ROWS
        and len(failures) == 0
        and set(planned.material_id) == ids
        and np.all(counts.values == EXPECTED_SETTINGS)
    )
    coverage_gate = certified_fraction >= 0.95
    overall_gate = bool(
        overall["median"] > 1.0
        and overall["median_bootstrap_95_ci"][0] > 1.0
    )
    win_gate = bool(
        win_fraction >= 0.75
        and win_ci[0] > 0.50
    )
    subgroup_gate = bool(
        subgroup["bulk"]["median"] > 1.0
        and subgroup["bulk"]["median_bootstrap_95_ci"][0] > 1.0
        and subgroup["slab"]["median"] > 1.0
        and subgroup["slab"]["median_bootstrap_95_ci"][0] > 1.0
    )

    confirmatory_go = bool(
        pipeline_gate
        and coverage_gate
        and overall_gate
        and win_gate
        and subgroup_gate
    )

    selected_cr = comp.loc[
        comp.qoac_dual_certified & np.isfinite(comp.qoac_best_cr), "qoac_best_cr"
    ].to_numpy(dtype=float)

    summary = {
        "status": "COMPLETE",
        "role": "DISJOINT_HELD_OUT_CONFIRMATION",
        "population": {
            "held_out_materials": EXPECTED_MATERIALS,
            "bulk": int((manifest.system_type == "bulk").sum()),
            "slab": int((manifest.system_type == "slab").sum()),
            "tuning_materials_excluded": 12,
            "planned_settings": EXPECTED_ROWS,
            "successful_settings": int(len(rows)),
            "failures": int(len(failures)),
            "qsq_eligible_tau_1e-6": int(
                np.sum(
                    manifest.hartree_qsq_response_scale_rel_RMSE.to_numpy(dtype=float)
                    < TAU
                )
            ),
        },
        "qoac_certification": {
            "dual_certified_materials": certified_n,
            "dual_certified_fraction": certified_fraction,
            "best_cr_p10": float(np.quantile(selected_cr, 0.10)) if len(selected_cr) else None,
            "best_cr_median": float(np.median(selected_cr)) if len(selected_cr) else None,
            "best_cr_p90": float(np.quantile(selected_cr, 0.90)) if len(selected_cr) else None,
        },
        "paired_competitive_population": {
            "materials": int(len(paired)),
            "preidentified_baseline_missing": sorted(EXPECTED_BASELINE_MISSING),
            "baseline_codec_counts": baseline_codec_counts,
            "certification_failures_counted_as_zero_ratio": int(
                paired.qoac_certification_failure_counted_as_zero_ratio.sum()
            ),
        },
        "primary_competitive_result": {
            **overall,
            "wins": wins,
            "win_fraction": win_fraction,
            "win_fraction_wilson_95_ci": list(win_ci),
        },
        "certified_only_sensitivity": certified_only_stats,
        "subgroups": subgroup,
        "baseline_missing_material_outcome": missing_baseline_outcome,
        "gates": {
            "pipeline_accounting_exact": pipeline_gate,
            "dual_certification_coverage_ge_95pct": coverage_gate,
            "overall_median_ratio_and_ci_lower_gt_1": overall_gate,
            "win_fraction_ge_75pct_and_wilson_lower_gt_0p50": win_gate,
            "bulk_and_slab_median_ci_lower_gt_1": subgroup_gate,
        },
        "confirmatory_go": confirmatory_go,
        "interpretation": (
            "CONFIRMATORY_GO"
            if confirmatory_go
            else "CONFIRMATORY_NO_GO"
        ),
    }

    rows.to_csv(out / "confirmatory_rows.csv", index=False)
    failures.to_csv(out / "failures.csv", index=False)
    comp.to_csv(out / "material_comparison.csv", index=False)
    selected.to_csv(out / "selected_qoac_rows.csv", index=False)
    manifest.to_csv(out / "HELDOUT_MANIFEST.csv", index=False)

    subgroup_rows = []
    for label, s in subgroup.items():
        subgroup_rows.append({
            "system_type": label,
            "n": s["n"],
            "median_ratio": s["median"],
            "median_ci_low": s["median_bootstrap_95_ci"][0],
            "median_ci_high": s["median_bootstrap_95_ci"][1],
            "geometric_mean_ratio": s["geometric_mean"],
            "geometric_mean_ci_low": s["geometric_mean_bootstrap_95_ci"][0],
            "geometric_mean_ci_high": s["geometric_mean_bootstrap_95_ci"][1],
            "wins": s["wins"],
            "win_fraction": s["win_fraction"],
            "win_ci_low": s["win_fraction_wilson_95_ci"][0],
            "win_ci_high": s["win_fraction_wilson_95_ci"][1],
        })
    pd.DataFrame(subgroup_rows).to_csv(out / "subgroup_summary.csv", index=False)

    (out / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    report = [
        "# QOAC-H v0.2 disjoint held-out confirmation",
        "",
        f"Status: **{summary['interpretation']}**",
        "",
        f"- Held-out materials: **{EXPECTED_MATERIALS}** "
        f"({summary['population']['bulk']} bulk, {summary['population']['slab']} slab).",
        f"- Planned/evaluated settings: **{EXPECTED_ROWS}/{len(rows)}**; failures: **{len(failures)}**.",
        f"- Dual-certified QOAC-H materials: **{certified_n}/{EXPECTED_MATERIALS} "
        f"({certified_fraction:.1%})**.",
        f"- Pre-comparable materials: **{len(paired)}**; baseline-missing material fixed in advance: "
        f"**mp-1038991**.",
        "",
        "## Primary competitive result",
        "",
        f"- Median CR ratio QOAC-H / best existing baseline: **{overall['median']:.4g}** "
        f"(bootstrap 95% CI **[{overall['median_bootstrap_95_ci'][0]:.4g}, "
        f"{overall['median_bootstrap_95_ci'][1]:.4g}]**).",
        f"- Geometric-mean CR ratio: **{overall['geometric_mean']:.4g}** "
        f"(bootstrap 95% CI **[{overall['geometric_mean_bootstrap_95_ci'][0]:.4g}, "
        f"{overall['geometric_mean_bootstrap_95_ci'][1]:.4g}]**).",
        f"- Wins: **{wins}/{len(paired)} ({win_fraction:.1%})**; Wilson 95% CI "
        f"**[{win_ci[0]:.1%}, {win_ci[1]:.1%}]**.",
        "",
        "## Generality guardrails",
        "",
        f"- Bulk median ratio: **{subgroup['bulk']['median']:.4g}** "
        f"(95% CI **[{subgroup['bulk']['median_bootstrap_95_ci'][0]:.4g}, "
        f"{subgroup['bulk']['median_bootstrap_95_ci'][1]:.4g}]**).",
        f"- Slab median ratio: **{subgroup['slab']['median']:.4g}** "
        f"(95% CI **[{subgroup['slab']['median_bootstrap_95_ci'][0]:.4g}, "
        f"{subgroup['slab']['median_bootstrap_95_ci'][1]:.4g}]**).",
        "",
        "## Frozen GO criteria",
        "",
        f"- Exact pipeline/accounting: **{pipeline_gate}**.",
        f"- Dual-certification coverage >=95%: **{coverage_gate}**.",
        f"- Overall median ratio and CI lower bound >1: **{overall_gate}**.",
        f"- Win fraction >=75% and Wilson lower bound >50%: **{win_gate}**.",
        f"- Bulk and slab each have median-ratio CI lower bound >1: **{subgroup_gate}**.",
        "",
        f"Confirmatory decision: **{'GO' if confirmatory_go else 'NO-GO'}**.",
        "",
        "The claim is Hartree-specific. These results do not certify Bader/topological fidelity or universal field fidelity.",
    ]
    (out / "RESULTS.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
