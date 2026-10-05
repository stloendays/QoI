#!/usr/bin/env python3
"""Aggregate General-QOAC electric-field engineering mechanism gates."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd

TAU=1e-6
MATCH_CALIPER_DEX=0.05
MIN_MATCHES=3

def many(root,pat):
    xs=[pd.read_csv(p) for p in sorted(root.glob(pat)) if p.stat().st_size]
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame()

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

def one_pair_summary(g,bother):
    a=g[g.beta==1.0].copy()
    b=g[g.beta==float(bother)].copy()
    ratios=[]
    for ia,ib,d in greedy_match(a,b):
        ea=float(a.loc[ia,"electric_field_error_rel_RMSE_historical"])
        eb=float(b.loc[ib,"electric_field_error_rel_RMSE_historical"])
        if ea>=0 and eb>0 and np.isfinite(ea) and np.isfinite(eb):
            ratios.append(ea/eb)
    return len(ratios), (float(np.median(ratios)) if ratios else np.nan)

def mechanism(rows):
    out=[]
    for mid,g in rows.groupby("material_id"):
        n10,r10=one_pair_summary(g,0.0)
        n12,r12=one_pair_summary(g,2.0)
        out.append({
          "material_id":mid,
          "matched_pairs_beta1_vs_beta0":n10,
          "median_error_ratio_beta1_over_beta0":r10,
          "evaluable_beta1_vs_beta0":bool(n10>=MIN_MATCHES),
          "beta1_better_than_beta0":bool(n10>=MIN_MATCHES and r10<1.0),
          "matched_pairs_beta1_vs_beta2":n12,
          "median_error_ratio_beta1_over_beta2":r12,
          "evaluable_beta1_vs_beta2":bool(n12>=MIN_MATCHES),
          "beta1_better_than_beta2":bool(n12>=MIN_MATCHES and r12<1.0),
        })
    return pd.DataFrame(out)

def certified(rows):
    out=[]
    for mid,g in rows.groupby("material_id"):
        rec={"material_id":mid}
        best={}
        for beta in (0.0,1.0,2.0):
            z=g[(g.beta==beta)&(g.electric_field_error_rel_RMSE_historical<TAU)&(g.electric_field_error_rel_RMSE_safe<TAU)]
            if len(z):
                q=z.loc[z.compression_ratio.idxmax()]
                best[beta]=q
                rec[f"beta{int(beta)}_certified"]=True
                rec[f"beta{int(beta)}_cr"]=float(q.compression_ratio)
                rec[f"beta{int(beta)}_error"]=float(q.electric_field_error_rel_RMSE_historical)
            else:
                rec[f"beta{int(beta)}_certified"]=False
                rec[f"beta{int(beta)}_cr"]=np.nan
                rec[f"beta{int(beta)}_error"]=np.nan
        if all(x in best for x in (0.0,1.0,2.0)):
            wrong=max(float(best[0.0].compression_ratio),float(best[2.0].compression_ratio))
            rec["cr_ratio_beta1_over_best_wrong"]=float(best[1.0].compression_ratio)/wrong
            rec["beta1_wins_certified_rate"]=bool(rec["cr_ratio_beta1_over_best_wrong"]>1.0)
        else:
            rec["cr_ratio_beta1_over_best_wrong"]=np.nan
            rec["beta1_wins_certified_rate"]=False
        out.append(rec)
    return pd.DataFrame(out)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    rows=many(a.shards_root,"rows_shard_*.csv"); fails=many(a.shards_root,"failures_shard_*.csv"); planned=many(a.shards_root,"planned_shard_*.csv")
    manifest=pd.read_csv(a.manifest)
    if len(manifest)!=12 or manifest.material_id.nunique()!=12: raise RuntimeError("manifest must contain 12 unique materials")
    if set(planned.material_id)!=set(manifest.material_id): raise RuntimeError("planned population mismatch")
    if len(rows)!=12*3*25: raise RuntimeError(f"expected 900 rows, got {len(rows)}")
    if len(fails): raise RuntimeError(f"setting/material failures present: {len(fails)}")
    if not (rows.exact_modes==1).all(): raise RuntimeError("non-DC exact mode detected")

    mech=mechanism(rows)
    e10=mech[mech.evaluable_beta1_vs_beta0]
    e12=mech[mech.evaluable_beta1_vs_beta2]
    wins10=int(e10.beta1_better_than_beta0.sum())
    wins12=int(e12.beta1_better_than_beta2.sum())
    med10=float(np.median(e10.median_error_ratio_beta1_over_beta0)) if len(e10) else np.nan
    med12=float(np.median(e12.median_error_ratio_beta1_over_beta2)) if len(e12) else np.nan
    gateA=bool(wins10>=9 and med10<0.70)
    gateB=bool(wins12>=9 and med12<0.90)

    cert=certified(rows)
    cc=cert[np.isfinite(cert.cr_ratio_beta1_over_best_wrong)]
    winsC=int((cc.cr_ratio_beta1_over_best_wrong>1.0).sum())
    medC=float(np.median(cc.cr_ratio_beta1_over_best_wrong)) if len(cc) else np.nan
    gateC=bool(len(cc)>=9 and winsC>=9 and medC>1.05)

    summary={
      "status":"COMPLETE","materials":12,"settings":int(len(rows)),"failures":int(len(fails)),
      "prediction":{"operator":"Hartree electric field","weight_squared":"1/|G|^2","predicted_beta":1.0},
      "gate_A_operator_blind":{
        "go":gateA,"evaluable":int(len(e10)),"wins":wins10,
        "median_material_error_ratio_beta1_over_beta0":med10
      },
      "gate_B_operator_specific":{
        "go":gateB,"evaluable":int(len(e12)),"wins":wins12,
        "median_material_error_ratio_beta1_over_beta2":med12
      },
      "gate_C_certified_rate":{
        "go":gateC,"comparable":int(len(cc)),"wins":winsC,
        "median_cr_ratio_beta1_over_best_wrong":medC,
        "tau_electric_field_rel_RMSE":TAU
      },
      "confirmatory_authorized":bool(gateA and gateB),
    }
    rows.to_csv(out/"engineering_rows.csv",index=False)
    mech.to_csv(out/"mechanism_material.csv",index=False)
    cert.to_csv(out/"certified_rate_material.csv",index=False)
    manifest.to_csv(out/"ENGINEERING_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# General-QOAC electric-field engineering results\n\n"+
      f"- Gate A beta=1 vs beta=0: **{'GO' if gateA else 'NO-GO'}**; wins {wins10}/{len(e10)}; median error ratio **{med10:.4g}**.\n"+
      f"- Gate B beta=1 vs beta=2: **{'GO' if gateB else 'NO-GO'}**; wins {wins12}/{len(e12)}; median error ratio **{med12:.4g}**.\n"+
      f"- Gate C certified-rate ablation at tau={TAU:g}: **{'GO' if gateC else 'NO-GO'}**; wins {winsC}/{len(cc)}; median CR ratio **{medC:.4g}**.\n"+
      f"- New disjoint confirmatory cohort authorized: **{bool(gateA and gateB)}**.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
