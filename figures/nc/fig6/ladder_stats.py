"""Gain ladder for NC Fig. 6: per-material CR ratios between successive Part A arms, both fresh cohorts.

Rungs: A6 (best of ZFP, SZ3, SPERR) -> A5 (operational optimum in the blind L2 metric, Hartree-certified) ->
A1 (closed-form law) -> A3 (operational optimum in the operator metric). Every ratio is the median over the
confirmatory materials of the per-material ratio, with the Part A aggregator's bootstrap (seed 20261006, 10,000
resamples). Ratios that the aggregator already reports (A3/A5, A3/A1, A1/A6) are asserted equal to SUMMARY.json.

    D:/Tools/pur_bridge_env/Scripts/python.exe ladder_stats.py   -> LADDER_STATS.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common as C  # noqa: E402

SEED, NBOOT = 20261006, 10000


def boot(x):
    x = np.asarray(x, float)
    rng = np.random.default_rng(SEED)
    m = np.median(x[rng.integers(0, x.size, (NBOOT, x.size))], axis=1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


D = C.part_a()
S = C.summaries()
ORDER = {c: list(pd.read_csv(os.path.join(C.FRESH, f)).material_id)
         for c, f in (("bulk", "P1_CONFIRMATORY_MANIFEST.csv"), ("slab", "P3B_CONFIRMATORY_MANIFEST.csv"))}
PAIRS = (("A5", "A6"), ("A1", "A5"), ("A3", "A1"), ("A3", "A5"), ("A1", "A6"), ("A3", "A6"))
out = {"source": "analysis/general_qoac_law/results/run_{P1,P3B}_CONFIRMATORY/part_a_material.csv (confirmatory ids)",
       "bootstrap": {"seed": SEED, "resamples": NBOOT}}
for coh in ("bulk", "slab"):
    out[coh] = {}
    for tau in C.TAUS:
        t = D[(D.cohort == coh) & np.isclose(D.tau, tau)].set_index("material_id").reindex(ORDER[coh])  # aggregator order
        res = {}
        for num, den in PAIRS:
            r = (t[num] / t[den]).dropna()
            key = "%s_over_%s" % (num, den)
            res[key] = {"n": int(r.size), "wins": int((r > 1).sum()), "median": float(np.median(r)), "ci95": boot(r)}
            ref = S[coh]["part_A"][C.TAU_KEY[tau]].get(key)
            if ref is not None:
                assert abs(res[key]["median"] - ref["median"]) < 1e-9 * ref["median"], (coh, tau, key)
                assert np.allclose(res[key]["ci95"], ref["ci95"], rtol=1e-9), (coh, tau, key, res[key]["ci95"], ref["ci95"])
        res["median_cr"] = {a: float(np.median(t[a].dropna())) for a in ("A6", "A5", "A1", "A3")}
        out[coh][C.TAU_KEY[tau]] = res
json.dump(out, open(os.path.join(HERE, "LADDER_STATS.json"), "w"), indent=1)
for coh in ("bulk", "slab"):
    v = out[coh]["tau_1e-06"]
    print(coh, {k: round(v[k]["median"], 3) for k in v if k != "median_cr"}, {k: round(x, 1) for k, x in v["median_cr"].items()})
