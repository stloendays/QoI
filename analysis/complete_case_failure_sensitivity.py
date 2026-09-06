from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_output"
OUT.mkdir(exist_ok=True)
SEED = 20260906


def eligible_mask(df, col):
    s = df[col]
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False)
    return s.astype(str).str.lower().eq("true")


def boot_median(x, n=5000):
    x = pd.Series(x).replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
    if len(x) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(SEED)
    b = np.median(rng.choice(x, size=(n, len(x)), replace=True), axis=1)
    lo, hi = np.quantile(b, [0.025, 0.975])
    return float(np.median(x)), float(lo), float(hi)


def mutual_nearest(df, a, b, caliper=0.10, max_nominal=0.01):
    out = []
    for mid, g in df.groupby("material_id", sort=False):
        ga = g[(g.codec == a) & (g.nominal_tolerance_relative <= max_nominal) & (g.realized_Linf > 0) & g.Bader_error_resolved_e.notna()].copy().reset_index(drop=True)
        gb = g[(g.codec == b) & (g.nominal_tolerance_relative <= max_nominal) & (g.realized_Linf > 0) & g.Bader_error_resolved_e.notna()].copy().reset_index(drop=True)
        if ga.empty or gb.empty:
            continue
        xa = np.log10(ga.realized_Linf.to_numpy(float)); xb = np.log10(gb.realized_Linf.to_numpy(float))
        d = np.abs(xa[:, None] - xb[None, :])
        nb = d.argmin(axis=1); na = d.argmin(axis=0)
        for ia, ib in enumerate(nb):
            if na[ib] != ia or d[ia, ib] > caliper:
                continue
            ra, rb = ga.iloc[ia], gb.iloc[ib]
            qa = max(float(ra.Bader_error_resolved_e), 1e-15)
            qb = max(float(rb.Bader_error_resolved_e), 1e-15)
            out.append({"material_id": mid, "qoi_ratio": qa/qb, "linf_ratio": float(ra.realized_Linf/rb.realized_Linf)})
    return pd.DataFrame(out)


def interpolate(df, a, b, max_nominal=0.01):
    out=[]
    for mid,g in df.groupby("material_id", sort=False):
        ga=g[(g.codec==a)&(g.nominal_tolerance_relative<=max_nominal)&(g.realized_Linf>0)&g.Bader_error_resolved_e.notna()].sort_values("realized_Linf")
        gb=g[(g.codec==b)&(g.nominal_tolerance_relative<=max_nominal)&(g.realized_Linf>0)&g.Bader_error_resolved_e.notna()].sort_values("realized_Linf")
        if len(ga)<2 or len(gb)<2: continue
        xa=np.log10(ga.realized_Linf.to_numpy(float)); xb=np.log10(gb.realized_Linf.to_numpy(float))
        ya=np.log10(np.clip(ga.Bader_error_resolved_e.to_numpy(float),1e-15,None)); yb=np.log10(np.clip(gb.Bader_error_resolved_e.to_numpy(float),1e-15,None))
        lo=max(xa.min(),xb.min()); hi=min(xa.max(),xb.max())
        if hi<=lo: continue
        xs=lo+np.array([.25,.5,.75])*(hi-lo)
        ratios=[10**np.interp(x,xa,ya)/10**np.interp(x,xb,yb) for x in xs]
        out.append({"material_id":mid,"qoi_ratio":float(np.median(ratios))})
    return pd.DataFrame(out)

master=pd.read_csv(ROOT/"benchmark/master_benchmark_full.csv")
master["codec"]=master.codec.astype(str).str.upper()
fails=pd.read_csv(ROOT/"failure_registry.csv")
fails["nominal_tolerance_relative"]=pd.to_numeric(fails.nominal_tolerance_relative,errors="coerce")
low=fails[fails.nominal_tolerance_relative<=0.01].copy()
excluded=set(low.material_id.dropna().astype(str))
cc=master[~master.material_id.astype(str).isin(excluded)].copy()

report=["# Complete-case sensitivity to registered downstream failures",""]
report.append("A conservative complete-case analysis removes an entire material if any registered compressor/Bader case for that material failed at nominal relative tolerance <=0.01, regardless of which codec failed. This prevents selective survival of successful rows from favouring a codec in matched-realized-Linf comparisons.")
report.append("")
report.append(f"- Low-tolerance failure rows: **{len(low)}** across **{len(excluded)} unique materials**.")
report.append(f"- Master materials before/after exclusion: {master.material_id.nunique()} -> **{cc.material_id.nunique()}**.")
report.append(f"- Low-tolerance failures by codec: {low.codec.astype(str).str.upper().value_counts().to_dict()}.")
report.append("")

rows=[]
for tau,col in [(1e-4,"eligible_A1_at_0.0001"),(1e-3,"eligible_A1_at_0.001"),(1e-2,"eligible_A1_at_0.01")]:
    elig=cc[eligible_mask(cc,col)].copy()
    for a,b in [("SZ3","ZFP"),("SPERR","ZFP")]:
        mm=mutual_nearest(elig,a,b,.10,.01)
        if not mm.empty:
            per=mm.groupby("material_id").agg(qoi_ratio=("qoi_ratio","median"),linf_ratio=("linf_ratio","median")).reset_index()
            est,lo,hi=boot_median(per.qoi_ratio)
            r={"method":"0.10dex_mutual_nearest","tau_e":tau,"codec_a":a,"codec_b":b,"n_pairs":len(mm),"n_materials":len(per),"median_qoi_ratio":est,"ci_lo":lo,"ci_hi":hi,"frac_a_worse":float((per.qoi_ratio>1).mean()),"median_linf_ratio":float(per.linf_ratio.median())}
            rows.append(r)
            report.append(f"- tau={tau:g} e, {a}/{b}, 0.10-dex matching: {len(per)} materials; **{est:.2f}x** [{lo:.2f}, {hi:.2f}], A worse {100*r['frac_a_worse']:.1f}%, median L∞ ratio {r['median_linf_ratio']:.3f}.")
        ip=interpolate(elig,a,b,.01)
        if not ip.empty:
            est,lo,hi=boot_median(ip.qoi_ratio)
            r={"method":"common_support_interpolation","tau_e":tau,"codec_a":a,"codec_b":b,"n_pairs":np.nan,"n_materials":len(ip),"median_qoi_ratio":est,"ci_lo":lo,"ci_hi":hi,"frac_a_worse":float((ip.qoi_ratio>1).mean()),"median_linf_ratio":np.nan}
            rows.append(r)
            report.append(f"- tau={tau:g} e, {a}/{b}, common-support interpolation: {len(ip)} materials; **{est:.2f}x** [{lo:.2f}, {hi:.2f}], A worse {100*r['frac_a_worse']:.1f}%.")

# Fixed-effects and attenuation at tau 1e-3 on complete-case materials.
report += ["", "## Mechanism attenuation on complete-case materials", ""]
try:
    import statsmodels.formula.api as smf
    g=cc[eligible_mask(cc,"eligible_A1_at_0.001") & (cc.nominal_tolerance_relative<=0.01) & (cc.realized_Linf>0) & cc.Bader_error_resolved_e.notna()].copy()
    ranges=g.groupby("codec").realized_Linf.agg(["min","max"]); clo=float(ranges["min"].max()); chi=float(ranges["max"].min())
    g=g[g.realized_Linf.between(clo,chi)].copy()
    g["logQ"]=np.log10(np.clip(g.Bader_error_resolved_e.astype(float),1e-15,None)); g["logL"]=np.log10(g.realized_Linf.astype(float)); g["logL_c"]=g.logL-g.logL.median()
    g["logReassign"]=np.log10(np.clip(g.frac_voxels_reassigned.astype(float),0,None)+0.5/np.clip(g.npoints.astype(float),1,None))
    forms={"M0":"logQ ~ logL_c + C(codec, Treatment(reference='ZFP')) + C(material_id)","M1":"logQ ~ logL_c + logReassign + C(codec, Treatment(reference='ZFP')) + C(material_id)"}
    atten=[]
    for name,form in forms.items():
        fit=smf.ols(form,g).fit(cov_type="cluster",cov_kwds={"groups":g.material_id})
        for codec in ["SZ3","SPERR"]:
            t=f"C(codec, Treatment(reference='ZFP'))[T.{codec}]"; beta=float(fit.params[t]); se=float(fit.bse[t])
            atten.append({"model":name,"codec":codec,"effect":10**beta,"ci_lo":10**(beta-1.96*se),"ci_hi":10**(beta+1.96*se),"p":float(fit.pvalues[t])})
        if name=="M1":
            beta=float(fit.params["logReassign"]); se=float(fit.bse["logReassign"]); p=float(fit.pvalues["logReassign"])
            report.append(f"- log reassignment coefficient: **{beta:.3f}** [95% {beta-1.96*se:.3f}, {beta+1.96*se:.3f}], p={p:.3g}.")
    adf=pd.DataFrame(atten)
    for codec in ["SZ3","SPERR"]:
        s=adf[adf.codec==codec].set_index("model")
        report.append(f"- {codec}/ZFP: realized-L∞ + material FE **{s.loc['M0','effect']:.2f}x** -> after adding reassignment **{s.loc['M1','effect']:.2f}x**.")
    adf.to_csv(OUT/"complete_case_mechanism_attenuation.csv",index=False)
except Exception as e:
    report.append(f"- Regression unavailable: {type(e).__name__}: {e}")

pd.DataFrame(rows).to_csv(OUT/"complete_case_failure_sensitivity.csv",index=False)
(OUT/"complete_case_failure_sensitivity.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print("\n".join(report))
