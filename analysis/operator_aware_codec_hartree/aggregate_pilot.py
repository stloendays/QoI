#!/usr/bin/env python3
"""Aggregate QOAC-H v0.1 pilot rows and apply frozen GO/NO-GO gates."""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np
import pandas as pd
TAU=1e-6
MATCH_CALIPER_DEX=0.05
MIN_MATCHES=3
BOOTSTRAP_SEED=20261005
BOOTSTRAP_N=20000

def read_many(root,pattern):
    parts=[]
    for p in sorted(root.glob(pattern)):
        if p.stat().st_size: parts.append(pd.read_csv(p))
    return pd.concat(parts,ignore_index=True) if parts else pd.DataFrame()

def greedy_match(a,b):
    edges=[]
    for ia,ra in a.iterrows():
        if not (ra.compression_ratio>0): continue
        la=math.log10(float(ra.compression_ratio))
        for ib,rb in b.iterrows():
            if not (rb.compression_ratio>0): continue
            d=abs(la-math.log10(float(rb.compression_ratio)))
            if d<=MATCH_CALIPER_DEX+1e-15: edges.append((d,int(ia),int(ib)))
    edges.sort(); ua=set(); ub=set(); out=[]
    for d,ia,ib in edges:
        if ia in ua or ib in ub: continue
        ua.add(ia); ub.add(ib); out.append((ia,ib,d))
    return out

def mechanism_summary(rows):
    out=[]
    for mid,g in rows.groupby("material_id"):
        a=g[g.beta==2.0].copy(); b=g[g.beta==0.0].copy()
        pairs=greedy_match(a,b); ratios=[]
        for ia,ib,d in pairs:
            ea=float(a.loc[ia,"hartree_error_rel_RMSE_historical"]); eb=float(b.loc[ib,"hartree_error_rel_RMSE_historical"])
            if ea>=0 and eb>0 and np.isfinite(ea) and np.isfinite(eb): ratios.append(ea/eb)
        med=float(np.median(ratios)) if ratios else np.nan
        out.append({"material_id":mid,"matched_pairs":len(ratios),"median_hartree_ratio_beta2_over_beta0":med,
                    "evaluable":len(ratios)>=MIN_MATCHES,"beta2_better":bool(len(ratios)>=MIN_MATCHES and med<1.0)})
    return pd.DataFrame(out)

def load_baseline(path,materials):
    use=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["material_id"] not in materials: continue
            if str(r.get("scientific_reproduction_gate_pass","")).strip().lower() not in {"true","1","yes"}: continue
            try: err=float(r["hartree_error_rel_RMSE"]); cr=float(r["reproduced_compression_ratio"])
            except Exception: continue
            if np.isfinite(err) and np.isfinite(cr) and cr>0:
                use.append({"material_id":r["material_id"],"codec":r["codec"],"hartree_error":err,"compression_ratio":cr})
    return pd.DataFrame(use)

def bootstrap_median_ci(x):
    rng=np.random.default_rng(BOOTSTRAP_SEED); vals=np.asarray(x,dtype=float); n=len(vals)
    sims=np.empty(BOOTSTRAP_N,dtype=float)
    for i in range(BOOTSTRAP_N): sims[i]=np.median(vals[rng.integers(0,n,n)])
    return float(np.quantile(sims,0.025)),float(np.quantile(sims,0.975))

def competitive_summary(rows,baseline):
    out=[]
    for mid in sorted(set(rows.material_id)):
        q=rows[(rows.material_id==mid)&(rows.beta==2.0)]
        q=q[q.hartree_error_rel_RMSE_historical<TAU]
        b=baseline[(baseline.material_id==mid)&(baseline.hartree_error<TAU)]
        qbest=q.loc[q.compression_ratio.idxmax()] if len(q) else None
        bbest=b.loc[b.compression_ratio.idxmax()] if len(b) else None
        out.append({
            "material_id":mid,"qoac_certified":bool(qbest is not None),"baseline_certified":bool(bbest is not None),
            "qoac_best_cr":float(qbest.compression_ratio) if qbest is not None else np.nan,
            "qoac_alpha_rel_ptp":float(qbest.alpha_rel_ptp) if qbest is not None else np.nan,
            "qoac_hartree_error":float(qbest.hartree_error_rel_RMSE_historical) if qbest is not None else np.nan,
            "baseline_best_cr":float(bbest.compression_ratio) if bbest is not None else np.nan,
            "baseline_codec":str(bbest.codec) if bbest is not None else "",
            "baseline_hartree_error":float(bbest.hartree_error) if bbest is not None else np.nan,
            "cr_ratio_qoac_over_baseline":float(qbest.compression_ratio/bbest.compression_ratio) if qbest is not None and bbest is not None else np.nan
        })
    return pd.DataFrame(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo-root",type=Path,required=True)
    ap.add_argument("--shards-root",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    repo=args.repo_root.resolve(); out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    rows=read_many(args.shards_root,"rows_shard_*.csv"); failures=read_many(args.shards_root,"failures_shard_*.csv")
    planned=read_many(args.shards_root,"planned_shard_*.csv"); manifest=pd.read_csv(args.manifest)
    if len(manifest)!=12 or manifest.material_id.nunique()!=12: raise RuntimeError("manifest must contain exactly 12 unique materials")
    if set(planned.material_id)!=set(manifest.material_id): raise RuntimeError("planned shard population does not equal frozen manifest")
    mech=mechanism_summary(rows); eval_mech=mech[mech.evaluable]
    frac=float(eval_mech.beta2_better.mean()) if len(eval_mech) else np.nan
    med=float(eval_mech.median_hartree_ratio_beta2_over_beta0.median()) if len(eval_mech) else np.nan
    mechanism_go=bool(len(eval_mech)>0 and frac>=0.75 and med<0.70)
    baseline=load_baseline(repo/"analysis"/"hartree_qsq_full"/"results"/"hartree_codec_rows.csv",set(manifest.material_id))
    comp=competitive_summary(rows,baseline); comparable=comp[np.isfinite(comp.cr_ratio_qoac_over_baseline)]
    if len(comparable):
        ratios=comparable.cr_ratio_qoac_over_baseline.to_numpy(dtype=float); comp_med=float(np.median(ratios)); ci_lo,ci_hi=bootstrap_median_ci(ratios)
    else: comp_med=ci_lo=ci_hi=np.nan
    competitive_go=bool(len(comparable)>=9 and comp_med>1.05 and ci_lo>1.0)
    summary={"status":"COMPLETE","pilot_materials":int(len(manifest)),"rows_success":int(len(rows)),"failures":int(len(failures)),
             "primary_tau_historical_rel_RMSE":TAU,
             "mechanism_gate":{"evaluable_materials":int(len(eval_mech)),"fraction_materials_beta2_better":frac,
                               "median_material_hartree_ratio_beta2_over_beta0":med,"go":mechanism_go},
             "competitive_gate":{"comparable_materials":int(len(comparable)),
                                 "median_cr_ratio_qoac_over_best_baseline":comp_med,
                                 "bootstrap_95_ci":[ci_lo,ci_hi],"go":competitive_go},
             "interpretation":"MECHANISM_AND_COMPETITIVE_GO" if mechanism_go and competitive_go else ("MECHANISM_GO_ENGINEERING_CONTINUES" if mechanism_go else "MECHANISM_NO_GO")}
    rows.to_csv(out/"pilot_rows.csv",index=False); failures.to_csv(out/"failures.csv",index=False)
    mech.to_csv(out/"mechanism_material.csv",index=False); comp.to_csv(out/"competitive_material.csv",index=False)
    manifest.to_csv(out/"PILOT_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
        "# QOAC-H v0.1 pilot results\n\n"
        f"Status: **{summary['interpretation']}**\n\n"
        f"- Frozen pilot: **{len(manifest)} materials**.\n"
        f"- Successful setting rows: **{len(rows)}**; failure records: **{len(failures)}**.\n"
        f"- Mechanism-evaluable materials: **{len(eval_mech)}**.\n"
        f"- beta=2 better fraction: **{frac:.1%}**.\n"
        f"- Median material-level Hartree ratio beta=2/beta=0: **{med:.4g}**.\n"
        f"- Mechanism gate: **{'GO' if mechanism_go else 'NO-GO'}**.\n"
        f"- Competitive comparable materials at tau_H={TAU:g}: **{len(comparable)}**.\n"
        f"- Median certified CR ratio QOAC-H / best baseline: **{comp_med:.4g}**.\n"
        f"- Bootstrap 95% CI: **[{ci_lo:.4g}, {ci_hi:.4g}]**.\n"
        f"- Competitive gate: **{'GO' if competitive_go else 'NO-GO'}**.\n",
        encoding="utf-8")
    print(json.dumps(summary,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
