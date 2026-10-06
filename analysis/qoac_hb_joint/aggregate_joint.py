#!/usr/bin/env python3
"""Aggregate QOAC-HB with the frozen engineering gates or confirmatory criteria (DESIGN.md)."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

SEED=20261006; NBOOT=10000

def many(root,pat):
    xs=[]
    for p in sorted(root.rglob(pat)):
        d=pd.read_csv(p)
        if "material_id" in d and d.material_id.notna().any(): xs.append(d[d.material_id.notna()])
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame(columns=["material_id"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--phase",choices=["engineering","confirmatory"],required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir; out.mkdir(parents=True,exist_ok=True)
    man=pd.read_csv(a.manifest)
    rows=many(a.shards_root,"rows_shard_*.csv"); bad=many(a.shards_root,"bader_shard_*.csv")
    fails=many(a.shards_root,"failures_shard_*.csv"); mats=many(a.shards_root,"materials_shard_*.csv")
    if set(mats.material_id)!=set(man.material_id): raise RuntimeError("population mismatch")
    for name,d in (("rows",rows),("bader_attempts",bad),("failures",fails),("materials",mats)): d.to_csv(out/f"{name}.csv",index=False)
    cert=bad[bad.certified.astype(str).str.lower()=="true"] if len(bad) else bad
    M=man[["material_id","system_type"]].set_index("material_id")
    for arm in ("J","T1P","GP"):
        c=cert[cert.arm==arm].set_index("material_id")
        M[f"{arm}_cr"]=c.compression_ratio.reindex(M.index)
        M[f"{arm}_param"]=c.param.reindex(M.index)
        M[f"{arm}_attempt"]=c.attempt.reindex(M.index)
    jb=bad[bad.arm=="J"].sort_values("attempt").groupby("material_id").first() if len(bad) else pd.DataFrame()
    if len(jb):
        M["J_unprojected_bader_error_e"]=jb.unprojected_bader_error_e.reindex(M.index)
        M["J_unprojected_reassigned_frac"]=jb.unprojected_reassigned_frac.reindex(M.index)
    sel=rows.merge(cert[["material_id","arm","param"]],on=["material_id","arm","param"]) if len(cert) else rows.iloc[0:0]
    for arm in ("J","T1P","GP"):
        s=sel[sel.arm==arm].set_index("material_id")
        for col in ("density_Linf","density_RMSE","hartree_hist_pre","hartree_hist","side_channel_fraction"):
            M[f"{arm}_{col}"]=s[col].reindex(M.index)
    comp=M[["T1P_cr","GP_cr"]].max(axis=1)
    M["R_J"]=np.where(M.J_cr.notna()&comp.notna(),M.J_cr/comp,np.where(M.J_cr.notna(),np.inf,np.nan))
    M.reset_index().to_csv(out/"joint_material.csv",index=False)
    jc=int(M.J_cr.notna().sum()); R=M.R_J.dropna().to_numpy(float); Rf=np.where(np.isfinite(R),R,1e9)
    wins=int((R>1).sum()); med=float(np.median(Rf)) if R.size else None
    rng=np.random.default_rng(SEED)
    ci=[float(np.quantile(np.median(Rf[rng.integers(0,Rf.size,(NBOOT,Rf.size))],axis=1),q)) for q in (0.025,0.975)] if R.size else None
    n=len(man); failed=int((mats.status!="SUCCESS").sum())
    arms={arm:{"certified":int(M[f"{arm}_cr"].notna().sum()),"median_cr":float(M[f"{arm}_cr"].median()) if M[f"{arm}_cr"].notna().any() else None} for arm in ("J","T1P","GP")}
    s={"status":"COMPLETE","phase":a.phase,"materials":n,"material_failures":failed,"setting_failures":int(len(fails)),
       "arms":arms,"R_J":{"n":int(R.size),"wins":wins,"median":med,"bootstrap_ci95":ci,"min":float(np.min(R)) if R.size else None},
       "J_unprojected_bader_fail_count":int((M.get("J_unprojected_bader_error_e",pd.Series(dtype=float))>1e-3).sum())}
    if a.phase=="engineering":
        e1=jc>=10; e2=wins>=9 and med is not None and med>1.25
        s.update(gate_E1_feasibility={"go":e1,"J_certified":jc},gate_E2_utility={"go":e2,"wins":wins,"median_R_J":med},confirmatory_authorized=bool(e1 and e2))
    else:
        crit={"all_38_analyzable_zero_failures":failed==0 and n==38,"J_certified_ge_34":jc>=34,"wins_ge_28":wins>=28,
              "median_gt_1p25":med is not None and med>1.25,"bootstrap_lower_gt_1p10":ci is not None and ci[0]>1.10}
        s.update(criteria=crit,confirmatory_pass=all(crit.values()))
    (out/"SUMMARY.json").write_text(json.dumps(s,indent=2),encoding="utf-8"); print(json.dumps(s,indent=2))

if __name__=="__main__": raise SystemExit(main())
