#!/usr/bin/env python3
"""Evaluate the HB v2 confirmatory criteria (analysis/qoac_hb_v2/DESIGN.md at 8a784a4) on an aggregate of
aggregate_joint_v2.py.

Criteria, verbatim from HB v2 (written there for N = 48):
  1. >= 46/48 analyzable and certified (E1 definition: R3 at its best joint post-processor certified at all three tau_B).
  2. Joint overhead at tau_B = 1e-4: median <= 1.10 and fixed-seed (20261007, 10,000 resamples) bootstrap CI upper
     bound <= 1.15.
  3. Utility at tau_B = 1e-4: >= 36/48 wins, median > 1.10, and bootstrap CI lower bound > 1.00.
     (Utility = CR_R3,joint(best post) / max over {J, T1, GF} of the joint CR at each base's best post-processor.)

Statistics as HB v2 computed them (reproduced exactly from analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST by
test_evaluate_criteria.py):
  - denominators of the counts in 1 and 3 = all planned materials; a FAILED or MISSING material counts as not
    certified and not a win;
  - count thresholds keep HB v2's fractions 46/48 and 36/48 of the planned N (required = ceil(N * k / 48));
  - joint overhead = joint_v2_best_post.csv `joint_overhead` of R3 (CR_hartree_only / CR_joint), over materials where
    both certify;
  - utility ratio over materials where R3 certifies; a sole certifier (no other base certifies) is +inf, a win, and
    enters the median as 1e9 (the aggregate_joint_v2.py convention); win = ratio > 1;
  - bootstrap: values in manifest order, numpy default_rng(20261007) fresh per statistic, 10,000 resamples with
    replacement (rng.integers(0, n, (10000, n))), median of each, 2.5 and 97.5 percentiles;
  - a statistic over an empty set fails its criterion.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

FOCUS = "R3"
OTHERS = ("J", "T1", "GF")
TAUS = (1e-3, 1e-4, 1e-5)
PRIMARY_TAU = 1e-4
SEED = 20261007
RESAMPLES = 10_000
SOLE_CERTIFIER_RATIO = 1e9
C1_FRACTION = (46, 48)
C3_FRACTION = (36, 48)


def bootstrap_median_ci(x: np.ndarray) -> tuple[float, float]:
    n = len(x)
    rng = np.random.default_rng(SEED)
    meds = np.median(x[rng.integers(0, n, (RESAMPLES, n))], axis=1)
    lo, hi = np.percentile(meds, [2.5, 97.5])
    return float(lo), float(hi)


def required(n: int, frac: tuple[int, int]) -> int:
    return math.ceil(n * frac[0] / frac[1] - 1e-12)


def evaluate(results_dir: Path, material_ids: list[str]) -> dict:
    B = pd.read_csv(results_dir / "joint_v2_best_post.csv", dtype={"material_id": str, "base": str})
    B["tau"] = B["tau_bader"].astype(float)
    mats = pd.read_csv(results_dir / "materials.csv", dtype={"material_id": str})
    status = dict(zip(mats["material_id"], mats.get("status", pd.Series(dtype=str))))
    n = len(material_ids)

    def cr(base, tau):
        g = B[(B["base"] == base) & np.isclose(B["tau"], tau)].set_index("material_id")["best_joint_cr"]
        return g.reindex(material_ids).astype(float)

    # 1. analyzable and certified at all three tau_B
    cert_all = pd.Series(True, index=material_ids)
    for t in TAUS:
        cert_all &= cr(FOCUS, t).notna()
    c1_n = int(cert_all.sum())
    c1_req = required(n, C1_FRACTION)
    c1 = {"value": c1_n, "n": n, "required": c1_req, "threshold": f">= {C1_FRACTION[0]}/{C1_FRACTION[1]} of N",
          "pass": c1_n >= c1_req}

    # 2. joint overhead at tau_B = 1e-4
    g = B[(B["base"] == FOCUS) & np.isclose(B["tau"], PRIMARY_TAU)].set_index("material_id")["joint_overhead"]
    ov = g.reindex(material_ids).astype(float).to_numpy()
    ov = ov[~np.isnan(ov)]
    if ov.size:
        med = float(np.median(ov)); lo, hi = bootstrap_median_ci(ov)
        ok = med <= 1.10 and hi <= 1.15
    else:
        med = lo = hi = None; ok = False
    c2 = {"n": int(ov.size), "median": med, "ci_low": lo, "ci_high": hi,
          "threshold": "median <= 1.10 and CI upper <= 1.15", "pass": bool(ok)}

    # 3. utility at tau_B = 1e-4
    r3 = cr(FOCUS, PRIMARY_TAU)
    other = pd.concat([cr(b, PRIMARY_TAU) for b in OTHERS], axis=1).max(axis=1, skipna=True)
    ratio = np.where(r3.notna() & other.notna(), r3 / other.where(other.notna(), 1.0),
                     np.where(r3.notna(), np.inf, np.nan))
    wins = int(np.sum(ratio[~np.isnan(ratio)] > 1))
    rr = ratio[~np.isnan(ratio)]
    rr_med = np.where(np.isfinite(rr), rr, SOLE_CERTIFIER_RATIO)
    c3_req = required(n, C3_FRACTION)
    if rr.size:
        med3 = float(np.median(rr_med)); lo3, hi3 = bootstrap_median_ci(rr_med)
        ok3 = wins >= c3_req and med3 > 1.10 and lo3 > 1.00
        mn = float(np.min(rr))
    else:
        med3 = lo3 = hi3 = mn = None; ok3 = False
    c3 = {"wins": wins, "n": n, "required_wins": c3_req, "n_ratio": int(rr.size),
          "n_sole_certifier": int(np.isinf(rr).sum()), "median": med3, "ci_low": lo3, "ci_high": hi3, "min": mn,
          "threshold": f">= {C3_FRACTION[0]}/{C3_FRACTION[1]} of N wins, median > 1.10, CI lower > 1.00",
          "pass": bool(ok3)}

    not_ok = [m for m in material_ids if status.get(m) != "SUCCESS"]
    return {"n_planned": n,
            "n_success": n - len(not_ok),
            "not_analysed": {m: status.get(m, "MISSING") for m in not_ok},
            "r3_certified_by_tau": {f"{t:g}": int(cr(FOCUS, t).notna().sum()) for t in TAUS},
            "criterion_1": c1, "criterion_2": c2, "criterion_3": c3,
            "verdict": "PASS" if (c1["pass"] and c2["pass"] and c3["pass"]) else "FAIL"}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--results-dir", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--aeccar-sources", type=Path, default=None,
                   help="if given, also evaluate the pre-registered secondary population (aeccar_available == 1)")
    p.add_argument("--out", type=Path, default=None)
    a = p.parse_args(argv)
    ids = pd.read_csv(a.manifest, dtype={"material_id": str})["material_id"].tolist()
    res = {"primary": evaluate(a.results_dir, ids)}
    if a.aeccar_sources is not None:
        s = pd.read_csv(a.aeccar_sources, dtype={"material_id": str, "aeccar_available": str})
        avail = set(s.loc[s["aeccar_available"] == "1", "material_id"])
        res["secondary_aeccar_available"] = evaluate(a.results_dir, [m for m in ids if m in avail])
    text = json.dumps(res, indent=2)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
