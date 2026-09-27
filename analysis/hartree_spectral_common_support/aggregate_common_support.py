#!/usr/bin/env python3
"""Aggregate the three-way common-support Hartree spectral audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PAIRS = ("ZFP/SZ3", "ZFP/SPERR", "SZ3/SPERR")
BOOT_REPS = 2000
BOOT_SEED = 20260927
ORDER_THRESHOLD = 0.75


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--protocol-dir", type=Path, required=True)
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
    if len(vals) == 0:
        return np.nan, np.nan, np.nan, 0
    center = float(10 ** np.median(vals))
    rng = np.random.default_rng(BOOT_SEED)
    boots = np.empty(BOOT_REPS, dtype=float)
    for i in range(BOOT_REPS):
        sample = rng.choice(vals, size=len(vals), replace=True)
        boots[i] = 10 ** np.median(sample)
    return center, float(np.quantile(boots, .025)), float(np.quantile(boots, .975)), int(len(vals))


def median_ci_scalar(values: np.ndarray) -> tuple[float, float, float]:
    vals = np.asarray(values, float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return np.nan, np.nan, np.nan
    center = float(np.median(vals))
    rng = np.random.default_rng(BOOT_SEED)
    boots = np.empty(BOOT_REPS)
    for i in range(BOOT_REPS):
        sample = rng.choice(vals, size=len(vals), replace=True)
        boots[i] = np.median(sample)
    return center, float(np.quantile(boots, .025)), float(np.quantile(boots, .975))


def material_codec_table(detail: pd.DataFrame, value: str) -> pd.DataFrame:
    z = detail[["material_id", "codec", value]].copy()
    z[value] = pd.to_numeric(z[value], errors="coerce")
    z = z[np.isfinite(z[value])]
    return (
        z.groupby(["material_id", "codec"])[value]
        .median()
        .unstack("codec")
    )


def ordering_fraction(table: pd.DataFrame, kind: str) -> tuple[float, int]:
    needed = ["SPERR", "ZFP", "SZ3"]
    z = table.dropna(subset=needed)
    if kind == "ascending":
        ok = (z["SPERR"] < z["ZFP"]) & (z["ZFP"] < z["SZ3"])
    elif kind == "descending":
        ok = (z["SPERR"] > z["ZFP"]) & (z["ZFP"] > z["SZ3"])
    else:
        raise ValueError(kind)
    return float(ok.mean()) if len(z) else np.nan, int(len(z))


def order_string(row: pd.Series, descending: bool = False) -> str:
    vals = {c: float(row[c]) for c in ["ZFP", "SZ3", "SPERR"]}
    return (" > " if descending else " < ").join(
        sorted(vals, key=vals.get, reverse=descending)
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    args = parse_args()
    protocol_dir = args.protocol_dir.resolve()
    root = args.shards_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    protocol = pd.read_csv(protocol_dir / "common_support_triples.csv")
    match_summary = json.loads(
        (protocol_dir / "MATCHING_SUMMARY.json").read_text(encoding="utf-8")
    )
    expected_triples = int(match_summary["matched_triples"])
    expected_materials = int(match_summary["matched_materials"])

    detail = read_many(root, "detail_shard_*.csv")
    pairs = read_many(root, "pairs_shard_*.csv")
    triples = read_many(root, "triples_shard_*.csv")
    radial = read_many(root, "radial_shard_*.csv")
    planned = read_many(root, "planned_shard_*.csv")

    if len(triples) != expected_triples:
        raise RuntimeError(f"triple accounting drift: {len(triples)} != {expected_triples}")
    if triples["triple_id"].nunique() != expected_triples:
        raise RuntimeError("triple IDs are not unique")
    if triples["material_id"].nunique() != expected_materials:
        raise RuntimeError(
            f"material accounting drift: {triples['material_id'].nunique()} != {expected_materials}"
        )
    if planned["material_id"].nunique() != expected_materials:
        raise RuntimeError("planned material accounting drift")
    if len(detail) != 3 * expected_triples:
        raise RuntimeError(f"detail accounting drift: {len(detail)} != {3*expected_triples}")
    if len(pairs) != 3 * expected_triples:
        raise RuntimeError(f"pair accounting drift: {len(pairs)} != {3*expected_triples}")

    protocol_ids = set(protocol["triple_id"].astype(int))
    if set(triples["triple_id"].astype(int)) != protocol_ids:
        raise RuntimeError("executed triple IDs do not equal protocol triple IDs")

    detail = detail.sort_values(["triple_id", "codec"]).reset_index(drop=True)
    pairs = pairs.sort_values(["triple_id", "pair_label"]).reset_index(drop=True)
    triples = triples.sort_values("triple_id").reset_index(drop=True)

    protocol.to_csv(out / "common_support_triples.csv", index=False)
    detail.to_csv(out / "reconstruction_spectral_metrics.csv", index=False)
    pairs.to_csv(out / "pair_mechanism.csv", index=False)
    triples.to_csv(out / "triple_ordering.csv", index=False)

    radial_summary = (
        radial.groupby(["codec", "bin_index", "q_low", "q_high"], as_index=False)
        .agg(
            median_error_energy_fraction=("error_energy_fraction", "median"),
            p25_error_energy_fraction=("error_energy_fraction", lambda s: float(np.quantile(s, .25))),
            p75_error_energy_fraction=("error_energy_fraction", lambda s: float(np.quantile(s, .75))),
            median_hartree_weighted_fraction=("hartree_weighted_fraction", "median"),
            p25_hartree_weighted_fraction=("hartree_weighted_fraction", lambda s: float(np.quantile(s, .25))),
            p75_hartree_weighted_fraction=("hartree_weighted_fraction", lambda s: float(np.quantile(s, .75))),
            n=("triple_id", "count"),
        )
    )
    radial_summary.to_csv(out / "radial_spectrum_summary.csv", index=False)

    ratio_metrics = [
        "historical_hartree_ratio",
        "nyquist_safe_hartree_ratio",
        "sqrt_hartree_weighted_ratio",
        "sqrt_total_safe_error_energy_ratio",
        "sqrt_spectral_hartree_susceptibility_ratio",
        "low_G_fraction_ratio",
        "high_G_fraction_ratio",
    ]
    ratio_rows: list[dict[str, Any]] = []
    pair_centers: dict[str, dict[str, tuple[float, float, float]]] = {}
    for label in PAIRS:
        g = pairs[pairs["pair_label"] == label]
        pair_centers[label] = {}
        for metric in ratio_metrics:
            c, lo, hi, nmat = center_ci(g, metric)
            pair_centers[label][metric] = (c, lo, hi)
            ratio_rows.append({
                "pair_label": label,
                "metric": metric,
                "material_level_center": c,
                "ci_low": lo,
                "ci_high": hi,
                "n_materials": nmat,
                "n_triples": int(len(g)),
            })
    pd.DataFrame(ratio_rows).to_csv(out / "common_support_ratio_summary.csv", index=False)

    # Exact operator identities.
    max_parseval = float(pd.to_numeric(detail["safe_parseval_relative_error"], errors="coerce").max())
    id_log = np.abs(
        np.log10(pd.to_numeric(pairs["nyquist_safe_hartree_ratio"], errors="coerce").to_numpy(float))
        - np.log10(pd.to_numeric(pairs["sqrt_hartree_weighted_ratio"], errors="coerce").to_numpy(float))
    )
    max_identity_log = float(np.nanmax(id_log))

    # Material-level common-population orderings.
    susc_table = material_codec_table(detail, "spectral_hartree_susceptibility")
    centroid_table = material_codec_table(detail, "spectral_centroid_qmax")
    lowg_table = material_codec_table(detail, "low_G_fraction")
    energy_table = material_codec_table(detail, "safe_error_energy")
    hartree_table = material_codec_table(detail, "nyquist_safe_hartree_rel_RMSE")

    susc_fraction, susc_n = ordering_fraction(susc_table, "ascending")
    centroid_fraction, centroid_n = ordering_fraction(centroid_table, "descending")
    lowg_fraction, lowg_n = ordering_fraction(lowg_table, "ascending")

    material_orders = []
    common_mats = sorted(
        set(susc_table.dropna(subset=["SPERR", "ZFP", "SZ3"]).index)
        & set(centroid_table.dropna(subset=["SPERR", "ZFP", "SZ3"]).index)
        & set(lowg_table.dropna(subset=["SPERR", "ZFP", "SZ3"]).index)
        & set(energy_table.dropna(subset=["SPERR", "ZFP", "SZ3"]).index)
        & set(hartree_table.dropna(subset=["SPERR", "ZFP", "SZ3"]).index)
    )
    type_map = triples.drop_duplicates("material_id").set_index("material_id")["system_type"].to_dict()
    for mid in common_mats:
        material_orders.append({
            "material_id": mid,
            "system_type": type_map[mid],
            "susceptibility_order_ascending": order_string(susc_table.loc[mid], False),
            "centroid_order_descending": order_string(centroid_table.loc[mid], True),
            "low_G_fraction_order_ascending": order_string(lowg_table.loc[mid], False),
            "spectral_energy_order_ascending": order_string(energy_table.loc[mid], False),
            "safe_hartree_order_ascending": order_string(hartree_table.loc[mid], False),
            "susceptibility_SPERR_lt_ZFP_lt_SZ3":
                bool(susc_table.loc[mid, "SPERR"] < susc_table.loc[mid, "ZFP"] < susc_table.loc[mid, "SZ3"]),
            "centroid_SPERR_gt_ZFP_gt_SZ3":
                bool(centroid_table.loc[mid, "SPERR"] > centroid_table.loc[mid, "ZFP"] > centroid_table.loc[mid, "SZ3"]),
            "low_G_SPERR_lt_ZFP_lt_SZ3":
                bool(lowg_table.loc[mid, "SPERR"] < lowg_table.loc[mid, "ZFP"] < lowg_table.loc[mid, "SZ3"]),
        })
    material_orders_df = pd.DataFrame(material_orders)
    material_orders_df.to_csv(out / "material_ordering.csv", index=False)

    # Pre-specified CI direction checks for susceptibility.
    z_sz = pair_centers["ZFP/SZ3"]["sqrt_spectral_hartree_susceptibility_ratio"]
    z_sp = pair_centers["ZFP/SPERR"]["sqrt_spectral_hartree_susceptibility_ratio"]
    sz_sp = pair_centers["SZ3/SPERR"]["sqrt_spectral_hartree_susceptibility_ratio"]
    susceptibility_ci_order = z_sz[2] < 1.0 and z_sp[1] > 1.0 and sz_sp[1] > 1.0

    core_identity = max_parseval < 1e-10 and max_identity_log < 1e-10
    material_order_pass = susc_fraction >= ORDER_THRESHOLD
    status = (
        "COMMON_SUPPORT_OPERATOR_ORDER_SUPPORTED"
        if core_identity and susceptibility_ci_order and material_order_pass
        else "COMMON_SUPPORT_ORDER_NOT_ESTABLISHED"
    )

    # System-type robustness on the exact common population.
    system_rows: list[dict[str, Any]] = []
    for (label, stype), g in pairs.groupby(["pair_label", "system_type"]):
        for metric in [
            "nyquist_safe_hartree_ratio",
            "sqrt_total_safe_error_energy_ratio",
            "sqrt_spectral_hartree_susceptibility_ratio",
            "low_G_fraction_ratio",
        ]:
            c, lo, hi, nmat = center_ci(g, metric)
            system_rows.append({
                "pair_label": label,
                "system_type": stype,
                "metric": metric,
                "material_level_center": c,
                "ci_low": lo,
                "ci_high": hi,
                "n_materials": nmat,
                "n_triples": int(len(g)),
            })
    system_df = pd.DataFrame(system_rows)
    system_df.to_csv(out / "system_type_summary.csv", index=False)

    order_system = []
    for stype, g in material_orders_df.groupby("system_type"):
        order_system.append({
            "system_type": stype,
            "n_materials": int(len(g)),
            "susceptibility_SPERR_lt_ZFP_lt_SZ3_fraction":
                float(g["susceptibility_SPERR_lt_ZFP_lt_SZ3"].mean()),
            "centroid_SPERR_gt_ZFP_gt_SZ3_fraction":
                float(g["centroid_SPERR_gt_ZFP_gt_SZ3"].mean()),
            "low_G_SPERR_lt_ZFP_lt_SZ3_fraction":
                float(g["low_G_SPERR_lt_ZFP_lt_SZ3"].mean()),
        })
    pd.DataFrame(order_system).to_csv(out / "system_type_ordering.csv", index=False)

    structure_shares = (
        pairs.groupby(["material_id", "pair_label"])["spectral_structure_abs_log_share"]
        .median()
        .unstack("pair_label")
    )
    share_summary = {}
    for label in PAIRS:
        vals = structure_shares[label].dropna().to_numpy(float)
        c, lo, hi = median_ci_scalar(vals)
        share_summary[label] = {
            "median_material_abs_log_share": c,
            "bootstrap_ci_low": lo,
            "bootstrap_ci_high": hi,
        }

    summary = {
        "status": status,
        "population": match_summary,
        "checks": {
            "safe_parseval_identity": bool(max_parseval < 1e-10),
            "safe_hartree_equals_weighted_spectrum_identity": bool(max_identity_log < 1e-10),
            "susceptibility_pairwise_CIs_support_SPERR_lt_ZFP_lt_SZ3": bool(susceptibility_ci_order),
            "material_order_fraction_at_least_0p75": bool(material_order_pass),
        },
        "operator_identity_diagnostics": {
            "max_safe_parseval_relative_error": max_parseval,
            "max_abs_log10_safe_vs_weighted_identity_error": max_identity_log,
        },
        "material_ordering": {
            "SPERR_lt_ZFP_lt_SZ3_susceptibility_fraction": susc_fraction,
            "n_materials": susc_n,
            "SPERR_gt_ZFP_gt_SZ3_centroid_fraction": centroid_fraction,
            "centroid_n_materials": centroid_n,
            "SPERR_lt_ZFP_lt_SZ3_low_G_fraction": lowg_fraction,
            "low_G_n_materials": lowg_n,
            "pre_registered_primary_threshold": ORDER_THRESHOLD,
        },
        "pair_centers": {
            label: {
                metric: {
                    "center": vals[0],
                    "ci_low": vals[1],
                    "ci_high": vals[2],
                }
                for metric, vals in metrics.items()
            }
            for label, metrics in pair_centers.items()
        },
        "spectral_structure_abs_log_share": share_summary,
    }
    (out / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Three-way common-support Hartree spectral audit",
        "",
        f"Status: **{status}**",
        "",
        f"- Common-support triples: **{expected_triples}**",
        f"- Materials: **{expected_materials}**",
        f"- Maximum triple span: **{float(protocol['span_dex'].max()):.5f} dex**",
        f"- Maximum safe Parseval relative error: **{max_parseval:.3e}**",
        "",
        "## Common-population pair decomposition",
        "",
        "| pair | safe Hartree ratio | sqrt(total E ratio) | sqrt(spectral susceptibility ratio) |",
        "|---|---:|---:|---:|",
    ]
    for label in PAIRS:
        c = pair_centers[label]
        lines.append(
            f"| {label} | {c['nyquist_safe_hartree_ratio'][0]:.6g} | "
            f"{c['sqrt_total_safe_error_energy_ratio'][0]:.6g} | "
            f"{c['sqrt_spectral_hartree_susceptibility_ratio'][0]:.6g} |"
        )
    lines += [
        "",
        "## Material-level ordering",
        "",
        f"- SPERR < ZFP < SZ3 Hartree susceptibility: **{susc_fraction:.1%}** of {susc_n} materials",
        f"- SPERR > ZFP > SZ3 spectral centroid: **{centroid_fraction:.1%}** of {centroid_n} materials",
        f"- SPERR < ZFP < SZ3 low-G fraction: **{lowg_fraction:.1%}** of {lowg_n} materials",
        "",
        "The susceptibility ordering is the primary common-support mechanism test. "
        "Centroid and low-G fraction are supporting descriptors.",
        "",
        "No frozen manuscript or prior mechanism branch was modified.",
    ]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    hashes = []
    for p in sorted(out.iterdir()):
        if p.is_file():
            hashes.append(f"{sha256(p)}  {p.name}")
    (out / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")

    print(
        f"COMMON_SUPPORT_AGGREGATE_PASS status={status} "
        f"triples={expected_triples} materials={expected_materials}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
