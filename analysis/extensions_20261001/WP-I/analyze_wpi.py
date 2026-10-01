#!/usr/bin/env python3
"""Aggregate WP-I G3 reference-only sensitivity checkpoints."""
from __future__ import annotations
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
WPG = HERE.parents[1] / "extensions_20260930" / "WP-G"
CK = HERE / "vanda" / "results" / "checkpoints"
TAUS = (1e-4, 1e-3, 1e-2)
SEED = 20261001
NBOOT = 2000


def mcnemar(a, b):
    n01, n10 = int(np.sum(~a & b)), int(np.sum(a & ~b))
    p = binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    return n01, n10, p


def main():
    wpg = pd.read_csv(WPG / "reference.csv").set_index("material_id")
    checks = {Path(p).stem: json.load(open(p, encoding="utf-8")) for p in glob.glob(str(CK / "*.json"))}
    if len(checks) != 53:
        raise RuntimeError("expected 53 checkpoints, got %d" % len(checks))

    mats, probes, fails = [], [], []
    for mid in sorted(checks):
        d = checks[mid]
        row = {
            "material_id": mid, "status": d["status"],
            "g1_floor_e": wpg.loc[mid, "g1_floor_e"] if mid in wpg.index else np.nan,
            "g2_floor_e": wpg.loc[mid, "g2_floor_e"] if mid in wpg.index else np.nan,
            "g3_floor_e": d.get("g3_floor_e"),
            "g3_reassigned_median": d.get("g3_reassigned_median"),
            "bader_solves": d.get("bader_solves"),
        }
        mats.append(row)
        for p in d.get("probes", []):
            probes.append({"material_id": mid, **p})
        if d["status"] != "SUCCESS":
            fails.append({"material_id": mid, "stage": d.get("stage"), "error": d.get("error")})

    M = pd.DataFrame(mats)
    P = pd.DataFrame(probes)
    F = pd.DataFrame(fails)
    M.to_csv(HERE / "material_summary.csv", index=False)
    P.to_csv(HERE / "reference_only_probes.csv", index=False)
    F.to_csv(HERE / "failures.csv", index=False)

    ok = M[M.status == "SUCCESS"].copy()
    rng = np.random.default_rng(SEED)
    rows = []
    for tau in TAUS:
        e1 = ok.g1_floor_e < tau
        e2 = ok.g2_floor_e < tau
        e3 = ok.g3_floor_e < tau
        a31 = mcnemar(e3.values, e1.values)
        a32 = mcnemar(e3.values, e2.values)
        rows.append({
            "analysis": "eligibility", "tau_e": tau, "n": len(ok),
            "eligible_g1": int(e1.sum()), "eligible_g2": int(e2.sum()), "eligible_g3": int(e3.sum()),
            "mcnemar_g3_vs_g1": "%d/%d p=%.3g" % a31,
            "mcnemar_g3_vs_g2": "%d/%d p=%.3g" % a32,
        })

    ratio32 = ok.g3_floor_e.values / np.maximum(ok.g2_floor_e.values, 1e-12)
    ratio31 = ok.g3_floor_e.values / np.maximum(ok.g1_floor_e.values, 1e-12)
    for label, x in (("g3_over_g2", ratio32), ("g3_over_g1", ratio31)):
        boots = [np.median(x[rng.integers(0, len(x), len(x))]) for _ in range(NBOOT)]
        rows.append({
            "analysis": "floor_ratio", "comparison": label, "n": len(x),
            "median": float(np.median(x)),
            "ci_low": float(np.quantile(boots, 0.025)),
            "ci_high": float(np.quantile(boots, 0.975)),
        })

    pg = pd.read_csv(WPG / "probes.csv")
    g2_reassign_med = float(pg.groupby("material_id").g2_reassigned_frac.median().median())
    g3_reassign_med = float(P.groupby("material_id").g3_reassigned_frac.median().median())
    rows.append({
        "analysis": "mechanism", "n": len(ok),
        "frac_g3_ge_0p5_g2": float(np.mean(ratio32 >= 0.5)),
        "frac_g3_ge_0p9_g2": float(np.mean(ratio32 >= 0.9)),
        "median_g2_reassigned": g2_reassign_med,
        "median_g3_reassigned": g3_reassign_med,
        "reassignment_ratio": g3_reassign_med / max(g2_reassign_med, 1e-300),
    })

    S = pd.DataFrame(rows)
    S.to_csv(HERE / "summary.csv", index=False)

    e3 = S[(S.analysis == "eligibility") & (S.tau_e == 1e-3)].iloc[0]
    mech = S[S.analysis == "mechanism"].iloc[0]
    r = S[(S.analysis == "floor_ratio") & (S.comparison == "g3_over_g2")].iloc[0]
    non_eval = 1 - e3.eligible_g3 / e3.n
    accept = non_eval >= 0.80 and r["median"] >= 0.5 and mech.reassignment_ratio >= 0.5

    L = [
        "# WP-I — Partition-reference-only sensitivity decomposition", "",
        "Analyzable materials: %d/53." % len(ok),
        "",
        "## Primary endpoint at tau = 1e-3 e", "",
        "- G3 non-evaluable: %d/%d (%.1f%%)." % (e3.n - e3.eligible_g3, e3.n, 100 * non_eval),
        "- Median f_G3/f_G2: %.3f." % r["median"],
        "- Median reassignment ratio G3/G2: %.3f." % mech.reassignment_ratio,
        "- Pre-declared dominance criterion: **%s**." % ("MET" if accept else "NOT MET"),
        "",
        "Interpretation: G3 perturbs only the partition-defining all-electron reference while keeping CHGCAR exact.",
        "The dominance statement is used only if all three pre-declared criteria are met.",
    ]
    (HERE / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
