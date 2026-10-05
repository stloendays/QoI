#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd

CALIPER=0.05
MIN_MATCHES=3

def read_many(root,pat):
    xs=[pd.read_csv(p) for p in sorted(root.glob(pat)) if p.stat().st_size]
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame()

def greedy_match(a,b):
    edges=[]
    for ia,ra in a.iterrows():
        if not ra.compression_ratio>0: continue
        la=math.log10(float(ra.compression_ratio))
        for ib,rb in b.iterrows():
            if not rb.compression_ratio>0: continue
            d=abs(la-math.log10(float(rb.compression_ratio)))
            if d<=CALIPER+1e-15: edges.append((d,int(ia),int(ib)))
    edges.sort(); ua=set(); ub=set(); out=[]
    for d,ia,ib in edges:
        if ia in ua or ib in ub: continue
        ua.add(ia); ub.add(ib); out.append((ia,ib,d))
    return out

def pair_summary(rows,beta_b,metric):
    out=[]
    for mid,g in rows.groupby("material_id"):
        a=g[g.beta==1.0].copy(); b=g[g.beta==beta_b].copy()
        pairs=greedy_match(a,b); ratios=[]
        for ia,ib,d in pairs:
            ea=float(a.loc[ia,metric]); eb=float(b.loc[ib,metric])
            if ea>=0 and eb>0 and np.isfinite(ea) and np.isfinite(eb):
                ratios.append(ea/eb)
        out.append({
          "material_id":mid,"beta_reference":beta_b,"metric":metric,
          "matched_pairs":len(ratios),"median_ratio_beta1_over_reference":float(np.median(ratios)) if ratios else np.nan,
          "evaluable":len(ratios)>=MIN_MATCHES,
          "beta1_better":bool(len(ratios)>=MIN_MATCHES and np.median(ratios)<1.0)
        })
    return pd.DataFrame(out)

def gate(frame,median_threshold):
    z=frame[frame.evaluable]
    frac=float(z.beta1_better.mean()) if len(z) else np.nan
    med=float(z.median_ratio_beta1_over_reference.median()) if len(z) else np.nan
    return {"evaluable_materials":int(len(z)),"wins":int(z.beta1_better.sum()),"fraction_beta1_better":frac,
            "median_material_ratio":med,"go":bool(len(z)==12 and z.beta1_better.sum()>=9 and med<median_threshold)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    rows=read_many(a.shards_root,"rows_shard_*.csv"); fails=read_many(a.shards_root,"failures_shard_*.csv"); planned=read_many(a.shards_root,"planned_shard_*.csv")
    manifest=pd.read_csv(a.manifest)
    if len(manifest)!=12 or manifest.material_id.nunique()!=12: raise RuntimeError("manifest cardinality failure")
    if set(planned.material_id)!=set(manifest.material_id): raise RuntimeError("planned population mismatch")
    if len(rows)!=12*3*25: raise RuntimeError(f"expected 900 rows, got {len(rows)}")
    if len(fails): raise RuntimeError(f"setting failures present: {len(fails)}")
    if not (rows.exact_modes==1).all(): raise RuntimeError("unexpected exact reciprocal modes")

    s10=pair_summary(rows,0.0,"electric_error_rel_RMSE_safe")
    s12=pair_summary(rows,2.0,"electric_error_rel_RMSE_safe")
    h10=pair_summary(rows,0.0,"electric_error_rel_RMSE_historical")
    A=gate(s10,0.70); B=gate(s12,0.95)

    merged=s10[["material_id","beta1_better"]].merge(
      h10[["material_id","beta1_better"]],on="material_id",suffixes=("_safe","_historical"))
    agree=int((merged.beta1_better_safe==merged.beta1_better_historical).sum())
    C={"direction_agreement_materials":agree,"go":bool(agree==12)}

    summary={
      "status":"COMPLETE","materials":12,"rows":int(len(rows)),"failures":int(len(fails)),
      "primary_metric":"Nyquist-safe vector electric-field relative RMSE",
      "gate_A_beta1_vs_beta0":A,
      "gate_B_beta1_vs_beta2":B,
      "gate_C_safe_historical_direction":C,
      "confirmatory_authorized":bool(A["go"] and B["go"] and C["go"])
    }
    rows.to_csv(out/"engineering_rows.csv",index=False)
    s10.to_csv(out/"beta1_vs_beta0_safe.csv",index=False)
    s12.to_csv(out/"beta1_vs_beta2_safe.csv",index=False)
    h10.to_csv(out/"beta1_vs_beta0_historical.csv",index=False)
    manifest.to_csv(out/"ENGINEERING_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# QOAC-E electric-field operator-generality engineering result\n\n"+
      f"- Gate A beta=1 vs beta=0: **{'GO' if A['go'] else 'NO-GO'}**; wins **{A['wins']}/12**; median error ratio **{A['median_material_ratio']:.4f}**.\n"+
      f"- Gate B beta=1 vs beta=2: **{'GO' if B['go'] else 'NO-GO'}**; wins **{B['wins']}/12**; median error ratio **{B['median_material_ratio']:.4f}**.\n"+
      f"- Gate C safe/historical direction agreement: **{'GO' if C['go'] else 'NO-GO'}**; **{agree}/12**.\n"+
      f"- Disjoint confirmation authorized: **{summary['confirmatory_authorized']}**.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
