#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import numpy as np
import pandas as pd

TAUS=(1e-8,1e-7,1e-6,1e-5,1e-4,1e-3)

def many(root,pat):
    xs=[pd.read_csv(p) for p in sorted(root.glob(pat)) if p.stat().st_size]
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame()

def load_baseline(path,materials):
    out=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["material_id"] not in materials: continue
            try:
                gate=str(r.get("scientific_reproduction_gate_pass","")).lower() in {"true","1","yes"}
                err=float(r["hartree_error_rel_RMSE"])
                cr=float(r["reproduced_compression_ratio"])
                floor=float(r["hartree_qsq_response_scale_rel_RMSE"])
            except Exception:
                continue
            out.append({
              "material_id":r["material_id"],"codec":r["codec"],"gate":gate,
              "hartree_error":err,"compression_ratio":cr,"qsq_floor":floor
            })
    return pd.DataFrame(out)

def qtile(x,p):
    return float(np.quantile(np.asarray(x,dtype=float),p))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    repo=a.repo_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    rows=many(a.shards_root,"rows_shard_*.csv"); fails=many(a.shards_root,"failures_shard_*.csv"); planned=many(a.shards_root,"planned_shard_*.csv")
    manifest=pd.read_csv(a.manifest)
    if len(manifest)!=254 or manifest.material_id.nunique()!=254: raise RuntimeError("census manifest must contain 254 unique materials")
    if set(planned.material_id)!=set(manifest.material_id): raise RuntimeError("planned population mismatch")
    if len(rows)!=254*25: raise RuntimeError(f"expected 6350 rows, got {len(rows)}")
    if len(fails): raise RuntimeError(f"census failures present: {len(fails)}")
    if not (rows.exact_modes==1).all(): raise RuntimeError("non-DC exact mode detected")

    baseline=load_baseline(repo/"analysis"/"hartree_qsq_full"/"results"/"hartree_codec_rows.csv",set(manifest.material_id))
    records=[]
    summaries=[]
    for tau in TAUS:
        for _,m in manifest.iterrows():
            mid=m.material_id
            bb=baseline[baseline.material_id==mid]
            floors=bb.qsq_floor[np.isfinite(bb.qsq_floor)]
            floor=float(floors.iloc[0]) if len(floors) else np.nan
            eligible=bool(np.isfinite(floor) and floor<tau)
            qbest=None; bbest=None
            if eligible:
                q=rows[(rows.material_id==mid)&(rows.hartree_error_rel_RMSE_historical<tau)]
                b=bb[(bb.gate)&(bb.hartree_error<tau)]
                qbest=q.loc[q.compression_ratio.idxmax()] if len(q) else None
                bbest=b.loc[b.compression_ratio.idxmax()] if len(b) else None
            safe=bool(qbest is not None and float(qbest.hartree_error_rel_RMSE_safe)<tau)
            ratio=float(qbest.compression_ratio/bbest.compression_ratio) if qbest is not None and bbest is not None else np.nan
            records.append({
              "material_id":mid,"system_type":m.system_type,"tau":tau,"qsq_floor":floor,"eligible":eligible,
              "qoac_certified":bool(qbest is not None),"baseline_certified":bool(bbest is not None),
              "safe_guardrail":safe,
              "qoac_cr":float(qbest.compression_ratio) if qbest is not None else np.nan,
              "qoac_hist_error":float(qbest.hartree_error_rel_RMSE_historical) if qbest is not None else np.nan,
              "qoac_safe_error":float(qbest.hartree_error_rel_RMSE_safe) if qbest is not None else np.nan,
              "qoac_alpha_rel_ptp":float(qbest.alpha_rel_ptp) if qbest is not None else np.nan,
              "baseline_cr":float(bbest.compression_ratio) if bbest is not None else np.nan,
              "baseline_codec":str(bbest.codec) if bbest is not None else "",
              "baseline_hist_error":float(bbest.hartree_error) if bbest is not None else np.nan,
              "ratio_qoac_over_baseline":ratio
            })
        t=pd.DataFrame([r for r in records if r["tau"]==tau])
        e=t[t.eligible]
        c=e[np.isfinite(e.ratio_qoac_over_baseline)]
        ratios=c.ratio_qoac_over_baseline.to_numpy(dtype=float)
        bulk=c[c.system_type=="bulk"].ratio_qoac_over_baseline.to_numpy(dtype=float)
        slab=c[c.system_type=="slab"].ratio_qoac_over_baseline.to_numpy(dtype=float)
        summaries.append({
          "tau":tau,"eligible":int(len(e)),"comparable":int(len(c)),
          "safe_guardrail_pass":int(e.safe_guardrail.sum()),
          "wins":int(np.count_nonzero(ratios>1.0)) if len(ratios) else 0,
          "win_fraction":float(np.mean(ratios>1.0)) if len(ratios) else np.nan,
          "median_ratio":float(np.median(ratios)) if len(ratios) else np.nan,
          "p05_ratio":qtile(ratios,0.05) if len(ratios) else np.nan,
          "p25_ratio":qtile(ratios,0.25) if len(ratios) else np.nan,
          "p75_ratio":qtile(ratios,0.75) if len(ratios) else np.nan,
          "p95_ratio":qtile(ratios,0.95) if len(ratios) else np.nan,
          "min_ratio":float(np.min(ratios)) if len(ratios) else np.nan,
          "median_qoac_cr":float(np.median(c.qoac_cr)) if len(c) else np.nan,
          "median_baseline_cr":float(np.median(c.baseline_cr)) if len(c) else np.nan,
          "bulk_median_ratio":float(np.median(bulk)) if len(bulk) else np.nan,
          "slab_median_ratio":float(np.median(slab)) if len(slab) else np.nan
        })
    detail=pd.DataFrame(records); summary_df=pd.DataFrame(summaries)
    detail.to_csv(out/"census_material_tau.csv",index=False)
    rows.to_csv(out/"census_settings.csv",index=False)
    summary_df.to_csv(out/"census_tau_summary.csv",index=False)
    result={
      "status":"COMPLETE","materials":254,"settings":int(len(rows)),"failures":int(len(fails)),
      "bulk":int((manifest.system_type=="bulk").sum()),"slab":int((manifest.system_type=="slab").sum()),
      "tau_summary":summaries
    }
    (out/"SUMMARY.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    lines=["# QOAC-H v0.2 full development-population census","",
           "- Population: **254/254 materials** (186 bulk, 68 slab).",
           f"- QOAC-H settings: **{len(rows)}/6350**; failures: **{len(fails)}**.","",
           "| tau | eligible | wins/comparable | median ratio | p05 | bulk median | slab median |",
           "|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summaries:
        lines.append(f"| {s['tau']:.0e} | {s['eligible']} | {s['wins']}/{s['comparable']} | {s['median_ratio']:.3f}x | {s['p05_ratio']:.3f}x | {s['bulk_median_ratio']:.3f}x | {s['slab_median_ratio']:.3f}x |")
    (out/"RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
