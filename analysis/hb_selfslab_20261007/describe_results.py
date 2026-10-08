#!/usr/bin/env python3
"""Descriptive block of RESULTS.md, from the aggregate of aggregate_joint_v2.py (no criterion; the criteria are in
CRITERIA.json from evaluate_criteria.py). Same quantities as the earlier slab cohorts' RESULTS.md:
certified R3 best-post streams (largest Bader error / tau_B, reassigned fraction), R3 best joint post-processor per
tau_B, median joint overhead and median R3 joint CR per tau_B, CTP decisions of R3 (projected among evaluated rows),
median joint CR per base at tau_B = 1e-4, uncertified non-hartree_only streams per base and tau_B, and per-material
runtimes. Usage: describe_results.py <results-dir> [--json out.json]"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

TAUS = (1e-3, 1e-4, 1e-5)
BASES = ("R3", "J", "T1", "GF", "GP")


def describe(d: Path) -> dict:
    M = pd.read_csv(d / "joint_v2_material.csv", dtype={"material_id": str})
    B = pd.read_csv(d / "joint_v2_best_post.csv", dtype={"material_id": str})
    mats = pd.read_csv(d / "materials.csv", dtype={"material_id": str})
    out: dict = {"by_tau": {}}
    r3b = B[B.base == "R3"]
    for t in TAUS:
        bt = r3b[(r3b.tau_bader - t).abs() < 1e-12]
        cert = bt[bt.best_joint_post.notna()]
        sel = cert.merge(M, left_on=["material_id", "base", "best_joint_post"], right_on=["material_id", "base", "post"])
        sel = sel[(sel.tau_bader_y - t).abs() < 1e-12]
        r3m = M[(M.base == "R3") & ((M.tau_bader - t).abs() < 1e-12)]
        ctp = r3m[r3m.ctp_decision.notna()]
        out["by_tau"][f"{t:g}"] = {
            "r3_best_post_certified": int(len(cert)),
            "r3_best_post_counts": dict(Counter(cert.best_joint_post)),
            "max_bader_error_over_tau": float((sel.bader_error_e / t).max()) if len(sel) else None,
            "max_reassigned_frac": float(sel.reassigned_frac.max()) if len(sel) else None,
            "median_joint_overhead": float(bt.joint_overhead.dropna().median()) if bt.joint_overhead.notna().any() else None,
            "n_joint_overhead": int(bt.joint_overhead.notna().sum()),
            "median_r3_joint_cr": float(cert.best_joint_cr.median()) if len(cert) else None,
            "ctp_projected": int((ctp.ctp_decision == "projected").sum()),
            "ctp_evaluated": int(len(ctp)),
            "median_joint_cr_by_base": {b: float(B[(B.base == b) & ((B.tau_bader - t).abs() < 1e-12)].best_joint_cr.dropna().median())
                                        for b in BASES},
            "n_certified_by_base": {b: int(B[(B.base == b) & ((B.tau_bader - t).abs() < 1e-12)].best_joint_post.notna().sum())
                                    for b in BASES},
        }
    nh = M[M.post != "hartree_only"]
    unc = nh[nh.certified == False]  # noqa: E712
    out["uncertified_streams"] = {"n": int(len(unc)), "of": int(len(nh)),
                                  "by_base_tau": {f"{b}|{t:g}": int(((unc.base == b) & ((unc.tau_bader - t).abs() < 1e-12)).sum())
                                                  for b in BASES for t in TAUS},
                                  "r3_at_best_post": int(len(unc[unc.base == "R3"].merge(
                                      r3b[["material_id", "tau_bader", "best_joint_post"]],
                                      left_on=["material_id", "tau_bader", "post"],
                                      right_on=["material_id", "tau_bader", "best_joint_post"])))}
    ok = mats[mats.status == "SUCCESS"]
    out["materials"] = {"success": int(len(ok)), "failed": mats.loc[mats.status != "SUCCESS", "material_id"].tolist(),
                        "seconds_min": float(ok.seconds.min()), "seconds_median": float(ok.seconds.median()),
                        "seconds_max": float(ok.seconds.max()), "seconds_sum": float(ok.seconds.sum())}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", type=Path)
    ap.add_argument("--json", type=Path, default=None)
    a = ap.parse_args(argv)
    res = describe(a.results_dir)
    text = json.dumps(res, indent=1)
    if a.json:
        a.json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
