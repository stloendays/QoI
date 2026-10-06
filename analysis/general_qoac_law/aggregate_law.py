#!/usr/bin/env python3
"""Aggregate the General-QOAC law confirmation with the frozen criteria of DESIGN.md."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

SEED=20261006; NBOOT=10000

def many(root,pat):
    xs=[pd.read_csv(p) for p in sorted(Path(root).rglob(pat)) if p.stat().st_size>2]
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame()

def boot(x):
    x=np.asarray(x,float); rng=np.random.default_rng(SEED)
    m=np.median(x[rng.integers(0,x.size,(NBOOT,x.size))],axis=1)
    return [float(np.quantile(m,0.025)),float(np.quantile(m,0.975))]

def part_a(rows,ids):
    cert=rows[rows.certified.astype(str).str.lower()=="true"]
    b=cert.groupby(["material_id","tau","arm"]).cr.max().unstack("arm")
    out={}
    for tau in (1e-4,1e-6,1e-8):
        t=b.xs(tau,level="tau").reindex(ids)
        d={}
        for name,num,den in (("A3_over_A1","A3","A1"),("A3_over_A5","A3","A5"),("A1_over_A6","A1","A6"),("A1_over_A2","A1","A2"),
                             ("A3_over_A0","A3","A0"),("A1_over_A0","A1","A0")):
            r=(t[num]/t[den]).dropna()
            d[name]={"n":int(r.size),"wins":int((r>1).sum()),"median":float(r.median()),"ci95":boot(r) if r.size else None}
        d["A1_certified"]=int(t.A1.notna().sum()); d["A3_certified"]=int(t.A3.notna().sum())
        out[f"tau_{tau:g}"]=d
    p=out["tau_1e-06"]; n=len(ids)
    analyzable=int(min(p["A1_certified"],p["A3_certified"]))
    crit={"validity":analyzable>=n-2,
          "A_H1":p["A3_over_A1"]["median"]<=1.15 and p["A3_over_A1"]["ci95"][1]<=1.20,
          "A_H2":p["A3_over_A5"]["wins"]>=0.90*p["A3_over_A5"]["n"] and p["A3_over_A5"]["median"]>1.5 and p["A3_over_A5"]["ci95"][0]>1.35,
          "A_H3":p["A1_over_A6"]["wins"]>=0.95*p["A1_over_A6"]["n"] and p["A1_over_A6"]["median"]>4,
          "A_H4":p["A1_over_A2"]["wins"]>=0.75*p["A1_over_A2"]["n"] and p["A1_over_A2"]["median"]>1.15}
    return out,crit,b

def part_b(obs,pred,ids):
    c=obs[obs.certified.astype(str).str.lower()=="true"]
    g=c.pivot_table(index=["material_id","operator","tau"],columns="arm",values="bytes",aggfunc="min")
    g["G_obs"]=g["blind"]/g["opt"]
    m=g.reset_index().merge(pred[["material_id","operator","tau","G_pred","a_matched_rate_rmse_ratio"]],on=["material_id","operator","tau"],how="left")
    m=m[m.material_id.isin(ids)]
    out={}
    for tau in (1e-6,1e-4):
        t=m[(m.tau==tau)&(m.operator!="density")].dropna(subset=["G_obs","G_pred"])
        le=np.abs(np.log(t.G_pred/t.G_obs))
        rho=float(spearmanr(t.G_pred,t.G_obs).statistic) if len(t)>2 else float("nan")
        per={}
        for op,s in m[m.tau==tau].groupby("operator"):
            per[op]={"n":int(s.G_obs.notna().sum()),"median_G_obs":float(s.G_obs.median()),"median_G_pred":float(s.G_pred.median()),
                     "median_abs_log_err":float(np.median(np.abs(np.log(s.G_pred/s.G_obs)))) ,
                     "frac_G_obs_in_0.90_1.11":float(((s.G_obs>=0.90)&(s.G_obs<=1.11)).mean())}
        out[f"tau_{tau:g}"]={"pooled_n":int(len(t)),"median_abs_log_err":float(np.median(le)),"spearman":rho,"per_operator":per}
    p=out["tau_1e-06"]; per={k:v for k,v in p["per_operator"].items() if k!="density"}
    order_ok=True
    ks=list(per)
    for i in range(len(ks)):
        for j in range(i+1,len(ks)):
            a,b=per[ks[i]],per[ks[j]]
            if abs(math.log(a["median_G_pred"]/b["median_G_pred"]))>math.log(1.05):
                if np.sign(a["median_G_pred"]-b["median_G_pred"])!=np.sign(a["median_G_obs"]-b["median_G_obs"]): order_ok=False
    null_ok=all(v["frac_G_obs_in_0.90_1.11"]>=0.80 for v in per.values() if v["median_G_pred"]<1.05)
    dens=p["per_operator"].get("density",{})
    n_ok=int(m[(m.tau==1e-6)].groupby("material_id").G_obs.apply(lambda s:s.notna().all()).sum())
    crit={"validity":n_ok>=len(ids)-2,"B_H1":p["median_abs_log_err"]<=math.log(1.25),"B_H2":p["spearman"]>=0.85,
          "B_H3":order_ok,"B_H4":null_ok,"control_density_G_obs_is_1":bool(abs(dens.get("median_G_obs",float("nan"))-1)<1e-12)}
    return out,crit,m

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--manifest",type=Path,required=True); a.add_argument("--shards-root",type=Path,required=True)
    a.add_argument("--predictions-dir",type=Path,required=True); a.add_argument("--output-dir",type=Path,required=True)
    a=a.parse_args(); out=a.output_dir; out.mkdir(parents=True,exist_ok=True)
    ids=pd.read_csv(a.manifest).material_id.tolist()
    ra=many(a.shards_root,"rows_*.csv"); ob=many(a.shards_root,"partb_*.csv"); pr=many(a.predictions_dir,"pred_*.csv")
    fails=[p.name for p in Path(a.shards_root).rglob("failure*")]+[p.name for p in Path(a.shards_root).rglob("failures_*.csv")]
    ra.to_csv(out/"part_a_rows.csv",index=False); ob.to_csv(out/"part_b_rows.csv",index=False)
    A,critA,bA=part_a(ra,ids); B,critB,mB=part_b(ob,pr,ids)
    bA.reset_index().to_csv(out/"part_a_material.csv",index=False); mB.to_csv(out/"part_b_material.csv",index=False)
    s={"status":"COMPLETE","materials":len(ids),"failure_files":fails,"part_A":A,"part_A_criteria":critA,"part_A_pass":all(critA.values()),
       "part_B":B,"part_B_criteria":critB,"part_B_pass":all(v for k,v in critB.items())}
    (out/"SUMMARY.json").write_text(json.dumps(s,indent=2),encoding="utf-8"); print(json.dumps({k:s[k] for k in ("part_A_criteria","part_B_criteria","part_A_pass","part_B_pass")},indent=2))

if __name__=="__main__": raise SystemExit(main())
