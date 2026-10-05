#!/usr/bin/env python3
"""Aggregate the electric-field finite-rate diagnosis (diagnosis only; no gates)."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd

TARGETS=11
RATES={"zlib":"rate_zlib_bytes","h0_32":"rate_h0_32_bytes","h0_128":"rate_h0_128_bytes"}

def curve(g,col,target,ycol="ef_rel_rmse_safe"):
    x=np.log10(g.raw_bytes.to_numpy(float)/g[col].to_numpy(float)); y=np.log10(g[ycol].to_numpy(float))
    o=np.argsort(x); x=x[o]; y=y[o]
    ux=np.unique(x); uy=np.array([y[x==v].min() for v in ux])
    return np.interp(target,ux,uy)

def common_targets(g,col,betas):
    lo=max(np.log10(g[g.beta==b].raw_bytes/g[g.beta==b][col]).min() for b in betas)
    hi=min(np.log10(g[g.beta==b].raw_bytes/g[g.beta==b][col]).max() for b in betas)
    return np.linspace(lo+0.05*(hi-lo),hi-0.05*(hi-lo),TARGETS)

def ratio(g,col,b1,b2,targets,ycol="ef_rel_rmse_safe"):
    a=curve(g[g.beta==b1],col,targets,ycol); b=curve(g[g.beta==b2],col,targets,ycol)
    return float(10**np.median(a-b))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--work-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); repo=a.repo_root; w=a.work_dir; out=a.output_dir; out.mkdir(parents=True,exist_ok=True)
    S=pd.concat([pd.read_csv(f) for f in sorted(w.glob("settings_*.csv"))],ignore_index=True)
    H=pd.concat([pd.read_csv(f) for f in sorted(w.glob("shells_*.csv"))],ignore_index=True)
    T=pd.concat([pd.read_csv(f) for f in sorted(w.glob("theory_*.csv"))],ignore_index=True)
    mats=sorted(S.material_id.unique())
    if len(mats)!=12: raise RuntimeError(f"expected 12 materials, got {len(mats)}")
    mech=pd.read_csv(repo/"analysis/general_qoac_electric_field/results/mechanism_material.csv").set_index("material_id")
    bmap=pd.read_csv(repo/"analysis/general_qoac_electric_field_beta_map/results/beta_map_material.csv").set_index("material_id")

    closure={"max_rel_error_closure":float(S.closure_rel.max()),
             "max_abs_byte_difference":int((S.encoded_bytes-S.frozen_encoded_bytes).abs().max()),
             "settings":int(len(S))}

    rows=[]
    for mid in mats:
        g=S[S.material_id==mid]; th=T[(T.material_id==mid)]
        ef=th[th.operator=="electric_field"].set_index("beta"); ha=th[th.operator=="hartree"].set_index("beta")
        r={"material_id":mid,"system_type":g.system_type.iloc[0],
           "theory_ef_beta1_over_beta0":float(ef.loc[1.0,"pred_rmse_ratio_vs_beta0"]),
           "theory_ef_beta1_over_beta2":float(ef.loc[1.0,"pred_rmse_ratio_vs_beta2"]),
           "theory_ef_beta_opt":float(ef.pred_rmse_ratio_vs_beta1.idxmin()),
           "theory_ef_beta125_over_beta1":float(ef.loc[1.25,"pred_rmse_ratio_vs_beta1"]),
           "theory_hartree_beta2_over_beta0":float(ha.loc[2.0,"pred_rmse_ratio_vs_beta0"]),
           "frozen_pairmatched_beta1_over_beta0":float(mech.loc[mid,"median_error_ratio_beta1_over_beta0"]),
           "frozen_pairmatched_beta1_over_beta2":float(mech.loc[mid,"median_error_ratio_beta1_over_beta2"]),
           "frozen_betamap_beta_opt":float(bmap.loc[mid,"beta_opt"])}
        for name,col in RATES.items():
            t=common_targets(g,col,(0.0,1.0,1.25,2.0))
            r[f"{name}_beta1_over_beta0"]=ratio(g,col,1.0,0.0,t)
            r[f"{name}_beta1_over_beta2"]=ratio(g,col,1.0,2.0,t)
            r[f"{name}_beta125_over_beta1"]=ratio(g,col,1.25,1.0,t)
        t=common_targets(g,"rate_zlib_bytes",(0.0,1.0,2.0))
        for b in (0.0,1.0,2.0):
            gb=g[g.beta==b]
            r[f"dead_zone_fraction_beta{b:g}"]=float(np.median(np.interp(t,*_xy(gb,"dead_zone_fraction"))))
            r[f"zero_error_share_beta{b:g}"]=float(np.median(np.interp(t,*_xy(gb,"zero_share"))))
            r[f"actual_over_highrate_rmse_beta{b:g}"]=float(np.median(np.interp(t,*_xy(gb,"act_over_hr"))))
        # D4: implied exponent from per-shell marginal slopes at beta=1 (zlib bytes)
        h=H[(H.material_id==mid)&(H.beta==1.0)]
        lo,hi=t[0],t[-1]; implied=[]
        al=sorted(h.alpha_rel_ptp.unique())
        gb=g[g.beta==1.0].set_index("alpha_rel_ptp")
        for a1,a2 in zip(al[:-1],al[1:]):
            cr=np.log10(gb.loc[a1,"raw_bytes"]/gb.loc[a1,"encoded_bytes"])
            if not (lo<=cr<=hi): continue
            s1=h[h.alpha_rel_ptp==a1].set_index("shell"); s2=h[h.alpha_rel_ptp==a2].set_index("shell")
            dD=s2.err_weighted-s1.err_weighted; dR=s1.zlib_bytes-s2.zlib_bytes
            share=s2.err_weighted/s2.err_weighted.sum()
            ok=(dD>0)&(dR>0)&(share>=0.01)
            if ok.sum()<4: continue
            lam=np.log10(dD[ok]/dR[ok]); lq=np.log10(s2.q_mid[ok])
            slope=float(np.polyfit(lq,lam,1,w=np.sqrt(share[ok]))[0])
            implied.append(1.0-slope/2.0)
        r["d4_pairs"]=len(implied)
        r["d4_implied_beta_median"]=float(np.median(implied)) if implied else float("nan")
        rows.append(r)
    M=pd.DataFrame(rows); M.to_csv(out/"diagnosis_material.csv",index=False)

    # shell profile at the middle common target for beta=0,1,2 (zlib)
    prof=[]
    for mid in mats:
        g=S[S.material_id==mid]; t=common_targets(g,"rate_zlib_bytes",(0.0,1.0,2.0)); mid_t=t[len(t)//2]
        for b in (0.0,1.0,2.0):
            gb=g[g.beta==b].copy(); x=np.log10(gb.raw_bytes/gb.encoded_bytes)
            a_sel=gb.alpha_rel_ptp.iloc[int(np.argmin(np.abs(x-mid_t)))]
            h=H[(H.material_id==mid)&(H.beta==b)&(H.alpha_rel_ptp==a_sel)]
            for _,s in h.iterrows():
                prof.append({"material_id":mid,"beta":b,"alpha_rel_ptp":a_sel,"shell":int(s.shell),"q_mid":s.q_mid,
                    "byte_share":s.zlib_bytes/h.zlib_bytes.sum(),"error_share":s.err_weighted/max(h.err_weighted.sum(),1e-300),
                    "ref_share":s.ref_weighted_share,"dead_zone_fraction":s.dead_zone_fraction,
                    "actual_over_highrate":s.err_weighted/s.highrate_pred_weighted if s.highrate_pred_weighted>0 else np.nan})
    P=pd.DataFrame(prof); P.to_csv(out/"shell_profile_mid_rate.csv",index=False)

    med=lambda c:float(M[c].median())
    summary={"status":"COMPLETE","kind":"diagnosis_only_no_gates","materials":12,
        "frozen_results_unchanged":True,"confirmatory_authorized":False,"closure":closure,
        "D1_highrate_theory":{
            "ef_beta1_over_beta0_median":med("theory_ef_beta1_over_beta0"),
            "ef_beta1_over_beta0_range":[float(M.theory_ef_beta1_over_beta0.min()),float(M.theory_ef_beta1_over_beta0.max())],
            "ef_beta1_over_beta2_median":med("theory_ef_beta1_over_beta2"),
            "ef_beta1_over_beta2_range":[float(M.theory_ef_beta1_over_beta2.min()),float(M.theory_ef_beta1_over_beta2.max())],
            "ef_theory_optimum_beta_values":sorted(set(M.theory_ef_beta_opt.tolist())),
            "ef_beta125_over_beta1_median":med("theory_ef_beta125_over_beta1"),
            "hartree_beta2_over_beta0_median":med("theory_hartree_beta2_over_beta0"),
            "ball_limit":{"ef_beta1_over_beta0":math.sqrt(math.exp(2/3)/3),"ef_beta1_over_beta2":math.sqrt(5*math.exp(-2/3)/3)},
            "frozen_gate_thresholds":{"gate_A_beta1_over_beta0":0.70,"gate_B_beta1_over_beta2":0.90}},
        "observed_frozen":{"pairmatched_beta1_over_beta0_median":med("frozen_pairmatched_beta1_over_beta0"),
                           "pairmatched_beta1_over_beta2_median":med("frozen_pairmatched_beta1_over_beta2")},
        "D2_amplitudes":{f"dead_zone_fraction_beta{b}":med(f"dead_zone_fraction_beta{b}") for b in ("0","1","2")}
                       |{f"zero_error_share_beta{b}":med(f"zero_error_share_beta{b}") for b in ("0","1","2")}
                       |{f"actual_over_highrate_rmse_beta{b}":med(f"actual_over_highrate_rmse_beta{b}") for b in ("0","1","2")},
        "D3_rate_measures":{n:{"beta1_over_beta0":med(f"{n}_beta1_over_beta0"),"beta1_over_beta2":med(f"{n}_beta1_over_beta2"),
                               "beta125_over_beta1":med(f"{n}_beta125_over_beta1"),
                               "beta1_wins_vs_beta0":int((M[f"{n}_beta1_over_beta0"]<1).sum()),
                               "beta1_wins_vs_beta2":int((M[f"{n}_beta1_over_beta2"]<1).sum())} for n in RATES},
        "D4_marginal_slopes":{"implied_beta_median":med("d4_implied_beta_median"),
                              "implied_beta_range":[float(M.d4_implied_beta_median.min()),float(M.d4_implied_beta_median.max())]}}
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

def _xy(gb,kind):
    x=np.log10(gb.raw_bytes/gb.rate_zlib_bytes).to_numpy()
    if kind=="dead_zone_fraction": y=gb.dead_zone_fraction.to_numpy()
    elif kind=="zero_share": y=(gb.ef_rel_rmse_safe_zero_part**2/gb.ef_rel_rmse_safe**2).to_numpy()
    else: y=(gb.ef_rel_rmse_safe/gb.ef_rel_rmse_safe_highrate_pred).to_numpy()
    o=np.argsort(x); return x[o],y[o]

if __name__=="__main__": raise SystemExit(main())
