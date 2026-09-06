from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis_output"; OUT.mkdir(exist_ok=True)
SEED=20260906


def boolmask(s):
    if pd.api.types.is_bool_dtype(s): return s.fillna(False)
    return s.astype(str).str.lower().eq("true")


def bootmed(x,n=5000):
    x=pd.Series(x).replace([np.inf,-np.inf],np.nan).dropna().to_numpy(float)
    if len(x)==0:return np.nan,np.nan,np.nan
    rng=np.random.default_rng(SEED); b=np.median(rng.choice(x,size=(n,len(x)),replace=True),axis=1)
    lo,hi=np.quantile(b,[.025,.975]);return float(np.median(x)),float(lo),float(hi)

m=pd.read_csv(ROOT/"benchmark/master_benchmark_full.csv")
base=m[m.ladder.eq("base") & m.Bader_error_fixed_e.notna() & m.Bader_error_resolved_e.notna()].copy()
report=["# Fixed-basin understatement: denominator-robust audit",""]
report.append(f"Base successful paired rows: **{len(base)}**. Resolved > fixed in **{100*(base.Bader_error_resolved_e>base.Bader_error_fixed_e).mean():.2f}%**.")
report.append("")

# Raw denominator distribution
f=base.Bader_error_fixed_e.astype(float); r=base.Bader_error_resolved_e.astype(float)
for cut in [1e-12,1e-10,1e-8,1e-6,1e-5,1e-4]:
    report.append(f"- fixed error <= {cut:g} e: {100*(f<=cut).mean():.1f}% of rows.")
report.append("")

# Floors on denominator only, to expose sensitivity of ratio magnitude
floor_rows=[]
report += ["## 1. Ratio sensitivity to denominator floor",""]
for floor in [1e-15,1e-12,1e-10,1e-8,1e-6,1e-5,1e-4]:
    ratio=np.clip(r,1e-15,None)/np.clip(f,floor,None)
    est,lo,hi=bootmed(ratio)
    floor_rows.append({"fixed_denominator_floor_e":floor,"median_ratio":est,"ci_lo":lo,"ci_hi":hi})
    report.append(f"- denominator floor {floor:g} e: median resolved/fixed* = **{est:.1f}x** [{lo:.1f},{hi:.1f}].")
pd.DataFrame(floor_rows).to_csv(OUT/"fixed_basin_ratio_floor_sensitivity.csv",index=False)
report.append("")

# Per material median log-ratio where both positive
report += ["## 2. Material-balanced log-ratio",""]
pos=base[(base.Bader_error_fixed_e>0)&(base.Bader_error_resolved_e>0)].copy()
pos["log_ratio"]=np.log10(pos.Bader_error_resolved_e.astype(float))-np.log10(pos.Bader_error_fixed_e.astype(float))
pm=pos.groupby("material_id").log_ratio.median()
est,lo,hi=bootmed(10**pm)
report.append(f"- Per-material median of the within-material median ratio: **{est:.1f}x** [{lo:.1f},{hi:.1f}], {len(pm)} materials.")
for codec,g in pos.groupby("codec"):
    p=g.groupby("material_id").log_ratio.median();est,lo,hi=bootmed(10**p)
    report.append(f"- {codec}: material-balanced ratio **{est:.1f}x** [{lo:.1f},{hi:.1f}], {len(p)} materials.")
report.append("")

# Core nominal tolerances, material-level paired ratio and ratio-of-medians
report += ["## 3. Core nominal tolerances",""]
core=[]
for rel in [1e-4,1e-3,1e-2]:
    for codec in sorted(base.codec.unique()):
        g=base[(base.codec==codec)&np.isclose(base.nominal_tolerance_relative,rel)].copy()
        if g.empty: continue
        # raw per-material row ratios at exact nominal rung
        ratio=np.clip(g.Bader_error_resolved_e.astype(float),1e-15,None)/np.clip(g.Bader_error_fixed_e.astype(float),1e-15,None)
        est,lo,hi=bootmed(ratio)
        rom=float(g.Bader_error_resolved_e.median()/max(g.Bader_error_fixed_e.median(),1e-15))
        core.append({"relative_tolerance":rel,"codec":codec,"n":len(g),"median_row_ratio":est,"ci_lo":lo,"ci_hi":hi,"ratio_of_median_errors":rom,"median_fixed_e":g.Bader_error_fixed_e.median(),"median_resolved_e":g.Bader_error_resolved_e.median(),"fraction_resolved_gt_fixed":float((g.Bader_error_resolved_e>g.Bader_error_fixed_e).mean())})
        report.append(f"- rel={rel:g}, {codec}, n={len(g)}: median paired ratio **{est:.1f}x** [{lo:.1f},{hi:.1f}]; ratio of median errors **{rom:.1f}x**; resolved>fixed {100*(g.Bader_error_resolved_e>g.Bader_error_fixed_e).mean():.1f}%.")
pd.DataFrame(core).to_csv(OUT/"fixed_basin_core_tolerance_summary.csv",index=False)
report.append("")

# A1 admitted by contract; within corresponding nominal rung and all <= contract-ish rungs
report += ["## 4. A.1-qualified core comparisons",""]
a1=[]
for tau,col in [(1e-4,"eligible_A1_at_0.0001"),(1e-3,"eligible_A1_at_0.001"),(1e-2,"eligible_A1_at_0.01")]:
    elig=base[boolmask(base[col])].copy()
    # exact same nominal relative rung for interpretability
    for codec in sorted(base.codec.unique()):
        g=elig[(elig.codec==codec)&np.isclose(elig.nominal_tolerance_relative,tau)].copy()
        if g.empty: continue
        ratio=np.clip(g.Bader_error_resolved_e.astype(float),1e-15,None)/np.clip(g.Bader_error_fixed_e.astype(float),1e-15,None)
        est,lo,hi=bootmed(ratio);rom=float(g.Bader_error_resolved_e.median()/max(g.Bader_error_fixed_e.median(),1e-15))
        a1.append({"tau_e":tau,"codec":codec,"n":len(g),"median_paired_ratio":est,"ci_lo":lo,"ci_hi":hi,"ratio_of_median_errors":rom,"fraction_resolved_gt_fixed":float((g.Bader_error_resolved_e>g.Bader_error_fixed_e).mean())})
        report.append(f"- A.1 tau={tau:g} e, nominal rel={tau:g}, {codec}, n={len(g)}: paired ratio **{est:.1f}x** [{lo:.1f},{hi:.1f}], ratio-of-medians **{rom:.1f}x**, resolved>fixed {100*(g.Bader_error_resolved_e>g.Bader_error_fixed_e).mean():.1f}%.")
pd.DataFrame(a1).to_csv(OUT/"fixed_basin_A1_qualified_summary.csv",index=False)
report.append("")

report += ["## Recommendation",""]
report.append("Use `resolved > fixed in 99.7% of successful base-ladder rows` as the denominator-robust directional headline. Report a multiplicative understatement only with an explicitly stated aggregation and denominator treatment. Avoid presenting the raw pooled 52.8x median as if it were invariant to near-zero fixed-basin errors.")

(OUT/"fixed_basin_ratio_robustness.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print("\n".join(report))
