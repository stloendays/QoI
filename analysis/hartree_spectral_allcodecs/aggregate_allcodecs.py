#!/usr/bin/env python3
"""Aggregate the SPERR extension with the frozen ZFP/SZ3 mechanism audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PAIR_SPECS = {
    "ZFP/SZ3": {"pairs": 457, "materials": 214, "target": 0.07762205663818565},
    "ZFP/SPERR": {"pairs": 465, "materials": 206, "target": 0.6701967245270835},
    "SZ3/SPERR": {"pairs": 1847, "materials": 254, "target": 6.768201959029507},
}
BOOT_REPS = 2000
BOOT_SEED = 20260927


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--shards-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def read_many(root: Path, pattern: str) -> pd.DataFrame:
    files = sorted(root.rglob(pattern))
    if not files:
        raise RuntimeError(f"no files matched {pattern}")
    frames = []
    for p in files:
        try:
            frames.append(pd.read_csv(p))
        except pd.errors.EmptyDataError:
            pass
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def center_ci(df: pd.DataFrame, column: str) -> tuple[float, float, float, int]:
    z = df[["material_id", column]].copy()
    z[column] = pd.to_numeric(z[column], errors="coerce")
    z = z[np.isfinite(z[column]) & (z[column] > 0)]
    logs = z.groupby("material_id")[column].apply(
        lambda s: float(np.median(np.log10(s.astype(float))))
    )
    vals = logs.to_numpy(float)
    if not len(vals):
        return np.nan, np.nan, np.nan, 0
    center = float(10 ** np.median(vals))
    rng = np.random.default_rng(BOOT_SEED)
    boots = np.empty(BOOT_REPS, dtype=float)
    for i in range(BOOT_REPS):
        sample = rng.choice(vals, size=len(vals), replace=True)
        boots[i] = 10 ** np.median(sample)
    return center, float(np.quantile(boots, .025)), float(np.quantile(boots, .975)), int(len(vals))


def scalar_material_median(df: pd.DataFrame, column: str) -> tuple[float, int]:
    z = df[["material_id", column]].copy()
    z[column] = pd.to_numeric(z[column], errors="coerce")
    z = z[np.isfinite(z[column])]
    per = z.groupby("material_id")[column].median()
    if not len(per):
        return np.nan, 0
    return float(per.median()), int(len(per))


def directional_material_fraction(df: pd.DataFrame, column: str, relation: str) -> float:
    z = df[["material_id", column]].copy()
    z[column] = pd.to_numeric(z[column], errors="coerce")
    z = z[np.isfinite(z[column]) & (z[column] > 0)]
    per_log = z.groupby("material_id")[column].apply(
        lambda s: float(np.median(np.log10(s.astype(float))))
    )
    if relation == "lt1":
        return float((per_log < 0).mean())
    if relation == "gt1":
        return float((per_log > 0).mean())
    raise ValueError(relation)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def radial_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["pair_label", "codec", "bin_index", "q_low", "q_high"], as_index=False)
        .agg(
            median_error_energy_fraction=("error_energy_fraction", "median"),
            p25_error_energy_fraction=("error_energy_fraction", lambda s: float(np.quantile(s, .25))),
            p75_error_energy_fraction=("error_energy_fraction", lambda s: float(np.quantile(s, .75))),
            median_hartree_weighted_fraction=("hartree_weighted_fraction", "median"),
            p25_hartree_weighted_fraction=("hartree_weighted_fraction", lambda s: float(np.quantile(s, .25))),
            p75_hartree_weighted_fraction=("hartree_weighted_fraction", lambda s: float(np.quantile(s, .75))),
            n=("pair_id", "count"),
        )
    )


def main() -> int:
    args = parse_args()
    repo = args.repo_root.resolve()
    root = args.shards_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    # Frozen confirmatory ZFP/SZ3 evidence.
    base_dir = repo / "analysis" / "hartree_spectral_mechanism" / "results"
    zsz_pairs = pd.read_csv(base_dir / "matched_pair_mechanism.csv")
    zsz_pairs["pair_label"] = "ZFP/SZ3"
    zsz_pairs["codec_a"] = "ZFP"
    zsz_pairs["codec_b"] = "SZ3"

    zsz_detail = pd.read_csv(base_dir / "reconstruction_spectral_metrics.csv")
    zsz_detail["pair_label"] = "ZFP/SZ3"
    zsz_detail["codec_a"] = "ZFP"
    zsz_detail["codec_b"] = "SZ3"

    zsz_radial_summary = pd.read_csv(base_dir / "radial_spectrum_summary.csv")
    zsz_radial_summary["pair_label"] = "ZFP/SZ3"

    # New SPERR comparisons.
    new_pairs = read_many(root, "pairs_*_shard_*.csv")
    new_detail = read_many(root, "detail_*_shard_*.csv")
    new_radial = read_many(root, "radial_*_shard_*.csv")
    planned = read_many(root, "planned_*_shard_*.csv")

    expected_new_pairs = PAIR_SPECS["ZFP/SPERR"]["pairs"] + PAIR_SPECS["SZ3/SPERR"]["pairs"]
    if len(new_pairs) != expected_new_pairs:
        raise RuntimeError(f"new-pair accounting drift: {len(new_pairs)} != {expected_new_pairs}")
    if len(new_detail) != 2 * expected_new_pairs:
        raise RuntimeError(f"new-detail accounting drift: {len(new_detail)} != {2 * expected_new_pairs}")

    all_pairs = pd.concat([zsz_pairs, new_pairs], ignore_index=True, sort=False)
    all_detail = pd.concat([zsz_detail, new_detail], ignore_index=True, sort=False)

    for label, spec in PAIR_SPECS.items():
        g = all_pairs[all_pairs["pair_label"] == label]
        if len(g) != spec["pairs"]:
            raise RuntimeError(f"{label} pair accounting drift: {len(g)} != {spec['pairs']}")
        if g["material_id"].nunique() != spec["materials"]:
            raise RuntimeError(
                f"{label} material accounting drift: {g['material_id'].nunique()} != {spec['materials']}"
            )

    all_pairs.to_csv(out / "all_pair_mechanism.csv", index=False)
    all_detail.to_csv(out / "all_reconstruction_spectral_metrics.csv", index=False)

    new_radial_summary = radial_summary(new_radial)
    common_cols = [
        "pair_label", "codec", "bin_index", "q_low", "q_high",
        "median_error_energy_fraction", "p25_error_energy_fraction", "p75_error_energy_fraction",
        "median_hartree_weighted_fraction", "p25_hartree_weighted_fraction",
        "p75_hartree_weighted_fraction", "n",
    ]
    zsz_radial_summary = zsz_radial_summary[common_cols]
    pair_radial = pd.concat([zsz_radial_summary, new_radial_summary[common_cols]], ignore_index=True)
    pair_radial.to_csv(out / "pair_radial_spectrum_summary.csv", index=False)

    ratio_metrics = [
        "target_historical_hartree_ratio",
        "reproduced_historical_hartree_ratio",
        "nyquist_safe_hartree_ratio",
        "sqrt_hartree_weighted_ratio",
        "sqrt_total_safe_error_energy_ratio",
        "sqrt_spectral_hartree_susceptibility_ratio",
        "low_G_fraction_ratio",
        "high_G_fraction_ratio",
        "hartree_weighted_low_G_fraction_ratio",
    ]

    summary_rows: list[dict[str, Any]] = []
    pair_diag: dict[str, Any] = {}
    all_core_checks = True

    for label, spec in PAIR_SPECS.items():
        g = all_pairs[all_pairs["pair_label"] == label].copy()
        centers: dict[str, float] = {}
        for col in ratio_metrics:
            c, lo, hi, nmat = center_ci(g, col)
            centers[col] = c
            summary_rows.append({
                "pair_label": label,
                "metric": col,
                "material_level_center": c,
                "ci_low": lo,
                "ci_high": hi,
                "n_materials": nmat,
            })

        structure_share, _ = scalar_material_median(g, "spectral_structure_abs_log_share")
        centroid_delta, _ = scalar_material_median(g, "spectral_centroid_delta_qmax")
        max_parseval = float(pd.to_numeric(g["max_safe_parseval_relative_error"], errors="coerce").max())
        identity_log = np.abs(
            np.log10(pd.to_numeric(g["nyquist_safe_hartree_ratio"], errors="coerce").to_numpy(float))
            - np.log10(pd.to_numeric(g["sqrt_hartree_weighted_ratio"], errors="coerce").to_numpy(float))
        )
        max_identity_log = float(np.nanmax(identity_log))

        target_center = centers["target_historical_hartree_ratio"]
        reproduced_center = centers["reproduced_historical_hartree_ratio"]
        safe_center = centers["nyquist_safe_hartree_ratio"]
        susceptibility_center = centers["sqrt_spectral_hartree_susceptibility_ratio"]
        energy_center = centers["sqrt_total_safe_error_energy_ratio"]

        checks = {
            "target_center_matches_frozen": abs(math.log10(target_center / spec["target"])) < 1e-8,
            "historical_hartree_reproduced": abs(math.log10(reproduced_center / target_center)) < 1e-4,
            "safe_parseval_identity": max_parseval < 1e-10,
            "safe_hartree_equals_weighted_spectrum": max_identity_log < 1e-10,
            "nyquist_correction_robust": abs(math.log10(safe_center / reproduced_center)) < 0.05,
        }
        all_core_checks = all_core_checks and all(checks.values())

        direction = "lt1" if spec["target"] < 1 else "gt1"
        pair_diag[label] = {
            "target_ratio": spec["target"],
            "centers": centers,
            "median_material_spectral_structure_abs_log_share": structure_share,
            "median_material_spectral_centroid_delta_qmax": centroid_delta,
            "materials_spectral_susceptibility_in_historical_effect_direction_fraction":
                directional_material_fraction(g, "sqrt_spectral_hartree_susceptibility_ratio", direction),
            "materials_low_G_fraction_in_historical_effect_direction_fraction":
                directional_material_fraction(g, "low_G_fraction_ratio", direction),
            "max_safe_parseval_relative_error": max_parseval,
            "max_abs_log10_safe_vs_weighted_identity_error": max_identity_log,
            "checks": checks,
            "magnitude_alone_insufficient":
                abs(math.log10(energy_center)) < abs(math.log10(safe_center)),
        }

    pd.DataFrame(summary_rows).to_csv(out / "allcodec_mechanism_ratio_summary.csv", index=False)

    # Bulk/slab robustness.
    sys_rows: list[dict[str, Any]] = []
    for (label, stype), g in all_pairs.groupby(["pair_label", "system_type"]):
        for col in [
            "nyquist_safe_hartree_ratio",
            "sqrt_total_safe_error_energy_ratio",
            "sqrt_spectral_hartree_susceptibility_ratio",
            "low_G_fraction_ratio",
        ]:
            c, lo, hi, nmat = center_ci(g, col)
            sys_rows.append({
                "pair_label": label,
                "system_type": stype,
                "metric": col,
                "material_level_center": c,
                "ci_low": lo,
                "ci_high": hi,
                "n_materials": nmat,
                "n_pairs": int(len(g)),
            })
    pd.DataFrame(sys_rows).to_csv(out / "system_type_mechanism_summary.csv", index=False)

    s_zfp_sz3 = pair_diag["ZFP/SZ3"]["centers"]["sqrt_spectral_hartree_susceptibility_ratio"]
    s_zfp_sperr = pair_diag["ZFP/SPERR"]["centers"]["sqrt_spectral_hartree_susceptibility_ratio"]
    s_sz3_sperr = pair_diag["SZ3/SPERR"]["centers"]["sqrt_spectral_hartree_susceptibility_ratio"]

    susceptibility_order = s_zfp_sz3 < 1 and s_zfp_sperr < 1 and s_sz3_sperr > 1

    c_zfp_sz3 = pair_diag["ZFP/SZ3"]["median_material_spectral_centroid_delta_qmax"]
    c_zfp_sperr = pair_diag["ZFP/SPERR"]["median_material_spectral_centroid_delta_qmax"]
    c_sz3_sperr = pair_diag["SZ3/SPERR"]["median_material_spectral_centroid_delta_qmax"]
    centroid_order = c_zfp_sz3 > 0 and c_zfp_sperr > 0 and c_sz3_sperr < 0

    l_zfp_sz3 = pair_diag["ZFP/SZ3"]["centers"]["low_G_fraction_ratio"]
    l_zfp_sperr = pair_diag["ZFP/SPERR"]["centers"]["low_G_fraction_ratio"]
    l_sz3_sperr = pair_diag["SZ3/SPERR"]["centers"]["low_G_fraction_ratio"]
    low_g_order = l_zfp_sz3 < 1 and l_zfp_sperr < 1 and l_sz3_sperr > 1

    status = (
        "THREE_CODEC_OPERATOR_SPECTRAL_ORDER_SUPPORTED"
        if all_core_checks and susceptibility_order
        else "THREE_CODEC_GENERALIZATION_NOT_CLOSED"
    )

    summary = {
        "status": status,
        "population": {
            label: {
                "matched_pairs": spec["pairs"],
                "materials": spec["materials"],
            }
            for label, spec in PAIR_SPECS.items()
        },
        "pair_diagnostics": pair_diag,
        "cross_codec_checks": {
            "all_reproduction_and_operator_identity_checks_pass": bool(all_core_checks),
            "spectral_hartree_susceptibility_order_ZFP_lt_SPERR_lt_SZ3": bool(susceptibility_order),
            "spectral_centroid_order_ZFP_gt_SPERR_gt_SZ3": bool(centroid_order),
            "low_G_fraction_order_ZFP_lt_SPERR_lt_SZ3": bool(low_g_order),
        },
        "interpretation_rule": (
            "Operator susceptibility is primary because it is defined by the exact Hartree weighting. "
            "Centroid and low-G fractions are supporting coarse spectral summaries."
        ),
    }
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Three-codec Hartree spectral generalization",
        "",
        f"Status: **{status}**",
        "",
        "| pair | historical H ratio | safe H ratio | sqrt(total spectral E ratio) | "
        "sqrt(Hartree susceptibility ratio) | spectral log-share |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label in ["ZFP/SZ3", "ZFP/SPERR", "SZ3/SPERR"]:
        d = pair_diag[label]
        c = d["centers"]
        lines.append(
            f"| {label} | {c['reproduced_historical_hartree_ratio']:.6g} | "
            f"{c['nyquist_safe_hartree_ratio']:.6g} | "
            f"{c['sqrt_total_safe_error_energy_ratio']:.6g} | "
            f"{c['sqrt_spectral_hartree_susceptibility_ratio']:.6g} | "
            f"{d['median_material_spectral_structure_abs_log_share']:.1%} |"
        )
    lines += [
        "",
        "## Cross-codec structure",
        "",
        f"- Hartree spectral susceptibility ordering ZFP < SPERR < SZ3: **{susceptibility_order}**",
        f"- Spectral centroid ordering ZFP > SPERR > SZ3: **{centroid_order}**",
        f"- Low-G error-fraction ordering ZFP < SPERR < SZ3: **{low_g_order}**",
        "",
        "The exact operator-weighted susceptibility is the primary mechanism variable. "
        "Centroid and low-G fraction are supporting descriptors.",
        "",
        "The frozen manuscript and frozen ZFP/SZ3 confirmatory branch remain unchanged.",
    ]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    hashes = []
    for p in sorted(out.iterdir()):
        if p.is_file():
            hashes.append(f"{sha256(p)}  {p.name}")
    (out / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")

    print(
        f"HARTREE_SPECTRAL_ALLCODECS_AGGREGATE_PASS status={status} "
        f"new_pairs={len(new_pairs)} total_pairs={len(all_pairs)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
