#!/usr/bin/env python3
"""Aggregate frozen 38-material QOAC-B2 confirmation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

NBOOT=50000
SEED=20261005


def bootstrap_median_ci(x):
    x=np.asarray(x,dtype=float); n=len(x); rng=np.random.default_rng(SEED)
    vals=np.empty(NBOOT,dtype=float)
    for i in range(NBOOT):
        vals[i]=np.median(x[rng.integers(0,n,n)])
    return float(np.quantile(vals,0.025)),float(np.quantile(vals,0.975))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--holdout-manifest",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    hold=pd.read_csv(a.holdout_manifest)
    if len(hold)!=38 or hold.material_id.nunique()!=38:
        raise RuntimeError("frozen holdout must contain 38 unique materials")

    js=[]
    for pth in sorted(a.shards_root.glob("mp-*.json")):
        js.append(json.loads(pth.read_text()))
    if len(js)!=38:
        raise RuntimeError(f"expected 38 material JSONs, got {len(js)}")
    if set(x["material_id"] for x in js)!=set(hold.material_id):
        raise RuntimeError("holdout population mismatch")
    failed=[x for x in js if x.get("status")!="SUCCESS"]
    if failed:
        raise RuntimeError(f"holdout material failures: {[x['material_id'] for x in failed]}")

    rows=[]
    for x in js:
        c=dict(material_id=x["material_id"],**x["candidate"])
        c["npoints"]=x["npoints"]; c["natoms"]=x["natoms"]; c["nlabels"]=x["nlabels"]
        rows.append(c)
    df=pd.DataFrame(rows)
    ratios=df.cr_ratio_over_baseline.to_numpy(float)
    lo,hi=bootstrap_median_ci(ratios)
    wins=int(np.count_nonzero(ratios>1))
    median=float(np.median(ratios))
    crit={
      "all_38_analyzable_zero_failures":True,
      "all_38_bader_error_le_2e-6":bool((df.actual_bader_error_e<=2e-6).all()),
      "all_38_zero_reassignment":bool((df.actual_reassigned_frac==0).all()),
      "wins_at_least_30_of_38":bool(wins>=30),
      "median_ratio_gt_1p30":bool(median>1.30),
      "bootstrap_lower_gt_1p10":bool(lo>1.10),
      "all_side_channel_lt_1pct":bool((df.side_channel_fraction<0.01).all()),
    }
    passed=bool(all(crit.values()))
    summary={
      "status":"COMPLETE",
      "confirmatory_pass":passed,
      "materials":38,
      "kappa":4.0,
      "tau_bader_e":1e-3,
      "wins":wins,
      "win_fraction":wins/38,
      "median_cr_ratio":median,
      "bootstrap_median_95_ci":[lo,hi],
      "min_cr_ratio":float(np.min(ratios)),
      "p05_cr_ratio":float(np.quantile(ratios,0.05)),
      "p25_cr_ratio":float(np.quantile(ratios,0.25)),
      "p75_cr_ratio":float(np.quantile(ratios,0.75)),
      "p95_cr_ratio":float(np.quantile(ratios,0.95)),
      "max_cr_ratio":float(np.max(ratios)),
      "median_linf_ratio":float(np.median(df.linf_ratio_over_baseline)),
      "max_linf_ratio":float(np.max(df.linf_ratio_over_baseline)),
      "max_bader_error_e":float(np.max(df.actual_bader_error_e)),
      "max_reassigned_frac":float(np.max(df.actual_reassigned_frac)),
      "max_side_channel_fraction":float(np.max(df.side_channel_fraction)),
      "criteria":crit,
    }
    df.to_csv(out/"confirmatory_material.csv",index=False)
    hold.to_csv(out/"FROZEN_HOLDOUT_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# QOAC-B2 frozen 38-material confirmation\n\n"+
      f"Status: **{'PASS' if passed else 'FAIL'}**\n\n"+
      f"- Materials: **38/38 analyzable**; pipeline failures: **0**.\n"+
      f"- Actual Bader error <= 2e-6 e: **{int((df.actual_bader_error_e<=2e-6).sum())}/38**.\n"+
      f"- Zero basin reassignment: **{int((df.actual_reassigned_frac==0).sum())}/38**.\n"+
      f"- Wins over best frozen G1 baseline: **{wins}/38 ({wins/38:.1%})**.\n"+
      f"- Median CR ratio: **{median:.3f}x**; bootstrap 95% CI **[{lo:.3f}, {hi:.3f}]**.\n"+
      f"- P05 / minimum CR ratio: **{np.quantile(ratios,0.05):.3f}x / {np.min(ratios):.3f}x**.\n"+
      f"- Maximum side-channel fraction: **{df.side_channel_fraction.max():.3%}**.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
