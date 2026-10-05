#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np
import pandas as pd

TAU=1e-6
BOOTSTRAP_SEED=20261005
BOOTSTRAP_N=50000

def many(root,pat):
    xs=[pd.read_csv(p) for p in sorted(root.glob(pat)) if p.stat().st_size]
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame()

def bootstrap_median_ci(x):
    x=np.asarray(x,dtype=float); n=len(x); rng=np.random.default_rng(BOOTSTRAP_SEED)
    sims=np.empty(BOOTSTRAP_N,dtype=float)
    for i in range(BOOTSTRAP_N):
        sims[i]=np.median(x[rng.integers(0,n,n)])
    return float(np.quantile(sims,0.025)),float(np.quantile(sims,0.975))

def wilson(k,n,z=1.959963984540054):
    p=k/n
    den=1+z*z/n
    center=(p+z*z/(2*n))/den
    half=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/den
    return center-half,center+half

def load_baseline(path,materials):
    out=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["material_id"] not in materials: continue
            if str(r.get("scientific_reproduction_gate_pass","")).lower() not in {"true","1","yes"}: continue
            try:
                err=float(r["hartree_error_rel_RMSE"]); cr=float(r["reproduced_compression_ratio"])
            except Exception: continue
            if np.isfinite(err) and np.isfinite(cr) and cr>0:
                out.append({"material_id":r["material_id"],"codec":r["codec"],"hartree_error":err,"compression_ratio":cr})
    return pd.DataFrame(out)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--engineering-manifest",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    repo=a.repo_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    rows=many(a.shards_root,"rows_shard_*.csv"); fails=many(a.shards_root,"failures_shard_*.csv"); planned=many(a.shards_root,"planned_shard_*.csv")
    manifest=pd.read_csv(a.manifest); eng=pd.read_csv(a.engineering_manifest)
    if len(manifest)!=48 or manifest.material_id.nunique()!=48: raise RuntimeError("confirmatory manifest must contain 48 unique materials")
    if set(manifest.material_id)&set(eng.material_id): raise RuntimeError("confirmatory cohort overlaps engineering cohort")
    if set(planned.material_id)!=set(manifest.material_id): raise RuntimeError("planned population mismatch")
    if len(rows)!=48*25: raise RuntimeError(f"expected 1200 rows, got {len(rows)}")
    if len(fails): raise RuntimeError(f"confirmatory failures present: {len(fails)}")
    if not (rows.exact_modes==1).all(): raise RuntimeError("non-DC exact mode detected")

    baseline=load_baseline(repo/"analysis"/"hartree_qsq_full"/"results"/"hartree_codec_rows.csv",set(manifest.material_id))
    rec=[]
    for _,m in manifest.iterrows():
        mid=m.material_id
        q=rows[(rows.material_id==mid)&(rows.hartree_error_rel_RMSE_historical<TAU)]
        b=baseline[(baseline.material_id==mid)&(baseline.hartree_error<TAU)]
        qbest=q.loc[q.compression_ratio.idxmax()] if len(q) else None
        bbest=b.loc[b.compression_ratio.idxmax()] if len(b) else None
        rec.append({
          "material_id":mid,"system_type":m.system_type,
          "qoac_certified":bool(qbest is not None),"baseline_certified":bool(bbest is not None),
          "qoac_cr":float(qbest.compression_ratio) if qbest is not None else np.nan,
          "qoac_historical_error":float(qbest.hartree_error_rel_RMSE_historical) if qbest is not None else np.nan,
          "qoac_safe_error":float(qbest.hartree_error_rel_RMSE_safe) if qbest is not None else np.nan,
          "safe_guardrail":bool(qbest is not None and float(qbest.hartree_error_rel_RMSE_safe)<TAU),
          "density_Linf":float(qbest.density_Linf) if qbest is not None else np.nan,
          "density_RMSE":float(qbest.density_RMSE) if qbest is not None else np.nan,
          "alpha_rel_ptp":float(qbest.alpha_rel_ptp) if qbest is not None else np.nan,
          "baseline_cr":float(bbest.compression_ratio) if bbest is not None else np.nan,
          "baseline_codec":str(bbest.codec) if bbest is not None else "",
          "baseline_hartree_error":float(bbest.hartree_error) if bbest is not None else np.nan,
          "ratio_qoac_over_baseline":float(qbest.compression_ratio/bbest.compression_ratio) if qbest is not None and bbest is not None else np.nan
        })
    mat=pd.DataFrame(rec)
    analyzable=mat[np.isfinite(mat.ratio_qoac_over_baseline)]
    if len(analyzable)!=48: raise RuntimeError(f"expected 48 analyzable materials, got {len(analyzable)}")
    ratios=analyzable.ratio_qoac_over_baseline.to_numpy(dtype=float)
    wins=int(np.count_nonzero(ratios>1.0))
    median=float(np.median(ratios)); ci_lo,ci_hi=bootstrap_median_ci(ratios)
    wlo,whi=wilson(wins,len(ratios))
    bulk=float(np.median(analyzable[analyzable.system_type=="bulk"].ratio_qoac_over_baseline))
    slab=float(np.median(analyzable[analyzable.system_type=="slab"].ratio_qoac_over_baseline))
    safe_all=bool(mat.safe_guardrail.all())
    criteria={
      "all_48_analyzable_zero_failures":bool(len(analyzable)==48 and len(fails)==0),
      "all_48_safe_guardrail":safe_all,
      "wins_at_least_36_of_48":bool(wins>=36),
      "median_ratio_gt_1p50":bool(median>1.50),
      "bootstrap_lower_gt_1p25":bool(ci_lo>1.25),
      "bulk_and_slab_medians_gt_1p25":bool(bulk>1.25 and slab>1.25),
      "wilson_win_lower_gt_0p50":bool(wlo>0.50)
    }
    passed=bool(all(criteria.values()))
    summary={
      "status":"COMPLETE","confirmatory_pass":passed,"materials":48,"rows_success":int(len(rows)),"failures":int(len(fails)),
      "wins":wins,"win_fraction":wins/48,"win_fraction_wilson_95_ci":[wlo,whi],
      "median_ratio_qoac_over_best_baseline":median,"bootstrap_median_95_ci":[ci_lo,ci_hi],
      "bulk_median_ratio":bulk,"slab_median_ratio":slab,"safe_guardrail_pass_count":int(mat.safe_guardrail.sum()),
      "criteria":criteria
    }
    rows.to_csv(out/"confirmatory_rows.csv",index=False)
    mat.to_csv(out/"confirmatory_material.csv",index=False)
    manifest.to_csv(out/"CONFIRMATORY_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# QOAC-H v0.2 disjoint confirmatory results\n\n"+
      f"Status: **{'PASS' if passed else 'FAIL'}**\n\n"+
      f"- Materials: **48/48 analyzable**; setting failures: **{len(fails)}**.\n"+
      f"- QOAC-H wins: **{wins}/48 ({wins/48:.1%})**; Wilson 95% CI **[{wlo:.3f}, {whi:.3f}]**.\n"+
      f"- Median CR ratio QOAC-H / best baseline: **{median:.3f}x**; bootstrap 95% CI **[{ci_lo:.3f}, {ci_hi:.3f}]**.\n"+
      f"- Bulk median: **{bulk:.3f}x**; slab median: **{slab:.3f}x**.\n"+
      f"- Nyquist-safe guardrail: **{int(mat.safe_guardrail.sum())}/48 passed**.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
