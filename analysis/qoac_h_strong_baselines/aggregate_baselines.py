#!/usr/bin/env python3
"""Aggregate the QOAC-H strongest-baseline study using the frozen reading bands in DESIGN.md."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

TAU=1e-6; SEED=20261005; NBOOT=10000

def many(root,pat):
    xs=[pd.read_csv(p) for p in sorted(root.rglob(pat)) if p.stat().st_size>2]
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame()

def boot_ci(x):
    rng=np.random.default_rng(SEED); x=np.asarray(x,float)
    m=np.median(x[rng.integers(0,x.size,(NBOOT,x.size))],axis=1)
    return [float(np.quantile(m,0.025)),float(np.quantile(m,0.975))]

def best(rows,arm,safe):
    r=rows[rows.arm==arm].copy()
    ok=r.hartree_rel_rmse_historical.astype(float)<TAU
    if safe: ok&=pd.to_numeric(r.hartree_rel_rmse_safe,errors="coerce")<TAU
    r=r[ok]
    if r.empty: return rows.iloc[0:0]
    return r.loc[r.groupby("material_id").compression_ratio.idxmax()]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir; out.mkdir(parents=True,exist_ok=True)
    conf=pd.read_csv(a.repo_root/"analysis/operator_aware_codec_hartree_v02_confirmatory/results/confirmatory_material.csv")
    rows=many(a.shards_root,"rows_shard_*.csv"); fails=many(a.shards_root,"failures_shard_*.csv")
    planned=many(a.shards_root,"planned_shard_*.csv")
    if len(conf)!=48 or set(planned.material_id)!=set(conf.material_id): raise RuntimeError("population mismatch")
    rows.to_csv(out/"baseline_rows.csv",index=False)
    if len(fails): fails.to_csv(out/"baseline_failures.csv",index=False)
    arm_status={}
    for arm,param_count in (("T1",9),("M",3),("V",3)):
        f=fails[fails.arm==arm] if len(fails) else pd.DataFrame()
        arm_status[arm]={"rows":int((rows.arm==arm).sum()) if len(rows) else 0,"failures":int(len(f)),
                         "params_with_rows":sorted(rows[rows.arm==arm].param.unique().tolist()) if len(rows) else []}
    sel={arm:best(rows,arm,arm!="V").set_index("material_id") for arm in ("T1","M","V")}
    M=conf[["material_id","system_type","qoac_cr","baseline_cr","baseline_codec","density_Linf","density_RMSE"]].rename(
        columns={"baseline_cr":"zfp_sz3_sperr_cr","density_Linf":"qoac_density_Linf","density_RMSE":"qoac_density_RMSE"}).set_index("material_id")
    for arm,s in sel.items():
        M[f"{arm}_cr"]=s.compression_ratio.reindex(M.index)
        M[f"{arm}_param"]=s.param.reindex(M.index)
        if arm!="V":
            M[f"{arm}_density_Linf"]=pd.to_numeric(s.density_Linf,errors="coerce").reindex(M.index)
            M[f"{arm}_density_RMSE"]=pd.to_numeric(s.density_RMSE,errors="coerce").reindex(M.index)
    M["new_cr"]=M[["T1_cr","M_cr"]].max(axis=1)
    M["new_certified"]=M.new_cr.notna()
    M["R_new"]=np.where(M.new_certified,M.qoac_cr/M.new_cr,np.inf)
    M["R_T1"]=M.qoac_cr/M.T1_cr; M["R_M"]=M.qoac_cr/M.M_cr; M["R_V"]=M.qoac_cr/M.V_cr
    M.reset_index().to_csv(out/"baseline_material.csv",index=False)
    R=M.R_new.to_numpy(float); fin=np.where(np.isfinite(R),R,1e9)
    med=float(np.median(fin)); ci=boot_ci(fin); wins=int((R>1).sum())
    if wins>=36 and med>1.25 and ci[0]>1.10: band="advantage_retained"
    elif ci[0]<=1<=ci[1]: band="parity"
    elif med<0.90: band="advantage_lost"
    else: band="mixed"
    def stats(col):
        x=M[col].dropna().to_numpy(float)
        return {"n":int(x.size),"wins":int((x>1).sum()),"median":float(np.median(x)) if x.size else None,
                "min":float(np.min(x)) if x.size else None,"bootstrap_ci95":boot_ci(x) if x.size else None}
    summary={"status":"COMPLETE","materials":48,"tau_hartree":TAU,"arm_status":arm_status,
        "primary_R_new":{"wins":wins,"median":med,"bootstrap_ci95":ci,"min":float(np.min(fin)),
                         "materials_without_certified_new_baseline":int((~M.new_certified).sum()),"reading_band":band},
        "R_T1":stats("R_T1"),"R_M":stats("R_M"),"R_V_contract_changing_reference":stats("R_V"),
        "bulk_median_R_new":float(np.median(fin[(M.system_type=="bulk").to_numpy()])),
        "slab_median_R_new":float(np.median(fin[(M.system_type=="slab").to_numpy()]))}
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__": raise SystemExit(main())
