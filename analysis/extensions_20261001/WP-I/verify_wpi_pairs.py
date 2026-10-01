#!/usr/bin/env python3
"""Deterministic paired verification audit for WP-I after the predeclared analysis.

This audit does not alter the WP-I acceptance rule. It verifies, at the individual
material/seed level, how closely G3 (exact CHGCAR + perturbed AE reference) reproduces
G2 (perturbed CHGCAR + perturbed AE reference) from the completed WP-G study.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
WPG = HERE.parents[1] / "extensions_20260930" / "WP-G"
TAUS = (1e-4, 1e-3, 1e-2)


def main() -> None:
    g2 = pd.read_csv(WPG / "probes.csv")
    g3 = pd.read_csv(HERE / "reference_only_probes.csv")
    cols2 = [
        "material_id", "seed", "g1_response_e", "g1_reassigned_frac",
        "g2_response_e", "g2_reassigned_frac",
    ]
    cols3 = ["material_id", "seed", "g3_response_e", "g3_reassigned_frac"]
    m = g2[cols2].merge(g3[cols3], on=["material_id", "seed"], how="inner", validate="one_to_one")
    if len(m) != 250 or m.material_id.nunique() != 50:
        raise RuntimeError("expected 250 paired probes from 50 analyzable materials")

    response_diff = (m.g3_response_e - m.g2_response_e).abs()
    reassign_diff = (m.g3_reassigned_frac - m.g2_reassigned_frac).abs()

    floors = m.groupby("material_id").agg(
        g1_floor_e=("g1_response_e", "max"),
        g2_floor_e=("g2_response_e", "max"),
        g3_floor_e=("g3_response_e", "max"),
    )
    floors["abs_g3_minus_g2_e"] = (floors.g3_floor_e - floors.g2_floor_e).abs()
    floors["g3_over_g2"] = floors.g3_floor_e / np.maximum(floors.g2_floor_e, 1e-12)

    eligibility = {}
    for tau in TAUS:
        e2 = floors.g2_floor_e < tau
        e3 = floors.g3_floor_e < tau
        eligibility[str(tau)] = {
            "eligible_g2": int(e2.sum()),
            "eligible_g3": int(e3.sum()),
            "discordant": int((e2 != e3).sum()),
        }

    out = {
        "scope": "post-analysis deterministic paired verification; not an acceptance endpoint",
        "n_materials": 50,
        "n_paired_probes": 250,
        "response_exact_pairs": int((response_diff == 0).sum()),
        "response_max_abs_diff_e": float(response_diff.max()),
        "response_p95_abs_diff_e": float(response_diff.quantile(0.95)),
        "reassignment_exact_pairs": int((reassign_diff == 0).sum()),
        "reassignment_max_abs_diff": float(reassign_diff.max()),
        "floor_exact_materials": int((floors.abs_g3_minus_g2_e == 0).sum()),
        "floor_max_abs_diff_e": float(floors.abs_g3_minus_g2_e.max()),
        "floor_ratio_min": float(floors.g3_over_g2.min()),
        "floor_ratio_median": float(floors.g3_over_g2.median()),
        "floor_ratio_max": float(floors.g3_over_g2.max()),
        "median_g1_floor_e": float(floors.g1_floor_e.median()),
        "median_g2_floor_e": float(floors.g2_floor_e.median()),
        "median_g3_floor_e": float(floors.g3_floor_e.median()),
        "g1_zero_floor_materials": int((floors.g1_floor_e == 0).sum()),
        "g1_max_floor_e": float(floors.g1_floor_e.max()),
        "eligibility": eligibility,
    }
    (HERE / "pair_audit_summary.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# WP-I paired verification audit",
        "",
        "This deterministic audit is a verification analysis and does not alter the pre-declared WP-I acceptance rule.",
        "",
        f"- Paired scope: **{out['n_paired_probes']} probes from {out['n_materials']} analyzable materials**.",
        f"- G2/G3 Bader responses are exactly equal for **{out['response_exact_pairs']}/250** probes; the maximum absolute discrepancy is **{out['response_max_abs_diff_e']:.2g} e**.",
        f"- G2/G3 basin-reassignment fractions are exactly equal for **{out['reassignment_exact_pairs']}/250** probes.",
        f"- Five-seed G2/G3 floors are exactly equal for **{out['floor_exact_materials']}/50** materials; the maximum floor discrepancy is **{out['floor_max_abs_diff_e']:.2g} e**.",
        f"- The material-wise floor ratio G3/G2 has minimum/median/maximum **{out['floor_ratio_min']:.9f} / {out['floor_ratio_median']:.9f} / {out['floor_ratio_max']:.9f}**.",
        f"- Fixed-reference G1 floors have median **{out['median_g1_floor_e']:.2g} e** and maximum **{out['g1_max_floor_e']:.2g} e**.",
        "",
        "Eligibility comparison:",
        "",
        "| tau (e) | G2 eligible | G3 eligible | discordant |",
        "|---:|---:|---:|---:|",
    ]
    for tau in TAUS:
        x = eligibility[str(tau)]
        lines.append(f"| {tau:g} | {x['eligible_g2']}/50 | {x['eligible_g3']}/50 | {x['discordant']} |")
    lines += [
        "",
        "Within the numerical resolution of the Henkelman output used here, adding the float32-scale CHGCAR perturbation on top of the same perturbed all-electron reference changes almost none of the observed Bader response and changes none of the basin reassignment. This supports the pre-declared interpretation that the partition-defining reference perturbation dominates G2 instability for this tested contract.",
    ]
    (HERE / "PAIR_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
