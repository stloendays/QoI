#!/usr/bin/env python3
"""Aggregate the finite-rate beta map for General-QOAC electric-field fidelity."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd

BETAS=np.array([0.0,0.25,0.50,0.75,1.0,1.25,1.50,1.75,2.0],dtype=float)
TARGETS=11

def many(root,pat):
    xs=[pd.read_csv(p) for p in sorted(root.glob(pat)) if p.stat().st_size]
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame()

def interp_curve(g,target):
    x=np.log10(g.compression_ratio.to_numpy(float))
    y=np.log10(g.electric_field_error_rel_RMSE_safe.to_numpy(float))
    ok=np.isfinite(x)&np.isfinite(y)&(g.compression_ratio.to_numpy(float)>0)&(g.electric_field_error_rel_RMSE_safe.to_numpy(float)>0)
    x=x[ok]; y=y[ok]
    order=np.argsort(x); x=x[order]; y=y[order]
    ux=[]; uy=[]
    for xx in np.unique(x):
        ux.append(xx); uy.append(float(np.min(y[x==xx])))
    ux=np.asarray(ux); uy=np.asarray(uy)
    if len(ux)<2 or target<ux[0]-1e-14 or target>ux[-1]+1e-14:
        raise RuntimeError("interpolation target outside support")
    return float(np.interp(target,ux,uy)),float(ux[0]),float(ux[-1])

def tie_argmin(beta_scores):
    best=min(beta_scores.values())
    cand=[b for b,s in beta_scores.items() if abs(s-best)<=1e-12]
    cand.sort(key=lambda b:(abs(b-1.0),b))
    return float(cand[0])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base-rows",type=Path,required=True)
    p.add_argument("--new-shards-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)

    base=pd.read_csv(a.base_rows)
    new=many(a.new_shards_root,"rows_shard_*.csv")
    fails=many(a.new_shards_root,"failures_shard_*.csv")
    planned=many(a.new_shards_root,"planned_shard_*.csv")
    manifest=pd.read_csv(a.manifest)

    if len(manifest)!=12 or manifest.material_id.nunique()!=12: raise RuntimeError("manifest must have 12 unique materials")
    if set(planned.material_id)!=set(manifest.material_id): raise RuntimeError("planned population mismatch")
    if len(base)!=900: raise RuntimeError(f"expected 900 frozen base rows, got {len(base)}")
    if len(new)!=1800: raise RuntimeError(f"expected 1800 new rows, got {len(new)}")
    if len(fails): raise RuntimeError(f"beta-map failures present: {len(fails)}")

    rows=pd.concat([base,new],ignore_index=True)
    if len(rows)!=2700: raise RuntimeError("combined beta-map row count mismatch")
    got=sorted(set(round(float(x),8) for x in rows.beta))
    exp=sorted(set(round(float(x),8) for x in BETAS))
    if got!=exp: raise RuntimeError(f"beta grid mismatch {got}")
    if not (rows.exact_modes==1).all(): raise RuntimeError("non-DC exact mode detected")

    material_rows=[]; target_rows=[]
    for mid,g in rows.groupby("material_id"):
        supports={}
        for beta in BETAS:
            z=g[np.isclose(g.beta,beta)].copy()
            if len(z)!=25: raise RuntimeError(f"{mid} beta={beta} has {len(z)} rows")
            lx=np.log10(z.compression_ratio.to_numpy(float))
            supports[float(beta)]=(float(np.min(lx)),float(np.max(lx)))
        L=max(v[0] for v in supports.values()); U=min(v[1] for v in supports.values())
        if not U>L: raise RuntimeError(f"no common rate overlap for {mid}")
        lo=L+0.05*(U-L); hi=U-0.05*(U-L)
        targets=np.linspace(lo,hi,TARGETS)

        vals={float(beta):[] for beta in BETAS}
        for t in targets:
            per={}
            for beta in BETAS:
                z=g[np.isclose(g.beta,beta)]
                y,_,_=interp_curve(z,float(t))
                vals[float(beta)].append(y); per[float(beta)]=y
            opt=tie_argmin(per)
            target_rows.append({"material_id":mid,"log10_cr_target":float(t),"cr_target":10**float(t),"beta_opt_at_target":opt,
                                **{f"log10_error_beta_{beta:g}":per[float(beta)] for beta in BETAS}})

        b1=np.asarray(vals[1.0])
        scores={beta:float(np.median(np.asarray(v)-b1)) for beta,v in vals.items()}
        opt=tie_argmin(scores)
        ratios0=10**(np.asarray(vals[opt])-np.asarray(vals[0.0]))
        ratios2=10**(np.asarray(vals[opt])-np.asarray(vals[2.0]))
        ratios1star=10**(np.asarray(vals[1.0])-np.asarray(vals[opt]))
        material_rows.append({
            "material_id":mid,"beta_opt":opt,"common_log10_cr_min":lo,"common_log10_cr_max":hi,
            "median_ratio_opt_over_beta0":float(np.median(ratios0)),
            "median_ratio_opt_over_beta2":float(np.median(ratios2)),
            "median_ratio_beta1_over_opt":float(np.median(ratios1star)),
            **{f"score_beta_{beta:g}":scores[float(beta)] for beta in BETAS},
        })

    mat=pd.DataFrame(material_rows)
    trg=pd.DataFrame(target_rows)
    global_scores={float(beta):float(np.median(mat[f"score_beta_{beta:g}"])) for beta in BETAS}
    beta_star=tie_argmin(global_scores)

    # Recompute per-material ratios specifically for the globally selected beta_star.
    star0=[]; star2=[]; oneStar=[]
    for mid,g in trg.groupby("material_id"):
        ys=g[f"log10_error_beta_{beta_star:g}"].to_numpy(float)
        y0=g["log10_error_beta_0"].to_numpy(float)
        y1=g["log10_error_beta_1"].to_numpy(float)
        y2=g["log10_error_beta_2"].to_numpy(float)
        star0.append(float(np.median(10**(ys-y0))))
        star2.append(float(np.median(10**(ys-y2))))
        oneStar.append(float(np.median(10**(y1-ys))))
    mat["median_ratio_beta_star_over_beta0"]=star0
    mat["median_ratio_beta_star_over_beta2"]=star2
    mat["median_ratio_beta1_over_beta_star"]=oneStar

    wins0=int((mat.median_ratio_beta_star_over_beta0<1).sum())
    wins2=int((mat.median_ratio_beta_star_over_beta2<1).sum())
    med0=float(np.median(mat.median_ratio_beta_star_over_beta0))
    med2=float(np.median(mat.median_ratio_beta_star_over_beta2))
    med1s=float(np.median(mat.median_ratio_beta1_over_beta_star))

    gate1=bool(0.75<=beta_star<=1.50)
    gate2=bool(wins0>=9 and wins2>=9 and med0<0.80 and med2<0.95)
    gate3=bool(med1s<1.10)

    summary={
      "status":"COMPLETE","materials":12,"combined_settings":int(len(rows)),"new_settings":int(len(new)),"failures":int(len(fails)),
      "beta_grid":[float(x) for x in BETAS],
      "common_rate_targets_per_material":TARGETS,
      "beta_star":beta_star,
      "global_scores_log10_error_relative_to_beta1":{f"{k:g}":v for k,v in global_scores.items()},
      "gate_M1_near_operator_prediction":{"go":gate1,"beta_star":beta_star},
      "gate_M2_beats_wrong_geometries":{"go":gate2,"wins_vs_beta0":wins0,"wins_vs_beta2":wins2,
                                        "median_error_ratio_star_over_beta0":med0,"median_error_ratio_star_over_beta2":med2},
      "gate_M3_beta1_near_star":{"go":gate3,"median_error_ratio_beta1_over_star":med1s},
      "confirmatory_authorized":bool(gate1 and gate2 and gate3)
    }
    rows.to_csv(out/"beta_map_rows.csv",index=False)
    mat.to_csv(out/"beta_map_material.csv",index=False)
    trg.to_csv(out/"beta_map_targets.csv",index=False)
    manifest.to_csv(out/"ENGINEERING_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# General-QOAC electric-field finite-rate beta map\n\n"+
      f"- Development-selected beta_star: **{beta_star:g}**.\n"+
      f"- M1 near operator prediction: **{'GO' if gate1 else 'NO-GO'}**.\n"+
      f"- M2 versus beta=0/beta=2: **{'GO' if gate2 else 'NO-GO'}**; wins **{wins0}/12** and **{wins2}/12**; median ratios **{med0:.3f}** and **{med2:.3f}**.\n"+
      f"- M3 analytic beta=1 near beta_star: **{'GO' if gate3 else 'NO-GO'}**; median beta1/star error ratio **{med1s:.3f}**.\n"+
      f"- Disjoint confirmation authorized: **{bool(gate1 and gate2 and gate3)}**.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
