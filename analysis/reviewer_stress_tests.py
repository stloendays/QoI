from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_output"
OUT.mkdir(exist_ok=True)
RNG = np.random.default_rng(20260906)


def bootstrap_median(values, n_boot=5000):
    x = pd.Series(values).replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
    if len(x) == 0:
        return np.nan, np.nan, np.nan
    est = float(np.median(x))
    b = np.median(RNG.choice(x, size=(n_boot, len(x)), replace=True), axis=1)
    lo, hi = np.quantile(b, [0.025, 0.975])
    return est, float(lo), float(hi)


def mutual_nearest(g, a, b, caliper, max_nominal=0.01):
    rows = []
    for mid, m in g.groupby("material_id", sort=False):
        aa = m[(m.codec == a) & (m.nominal_tolerance_relative <= max_nominal)].copy()
        bb = m[(m.codec == b) & (m.nominal_tolerance_relative <= max_nominal)].copy()
        if aa.empty or bb.empty:
            continue
        aa = aa[(aa.realized_Linf > 0) & aa.Bader_error_resolved_e.notna()].reset_index(drop=True)
        bb = bb[(bb.realized_Linf > 0) & bb.Bader_error_resolved_e.notna()].reset_index(drop=True)
        if aa.empty or bb.empty:
            continue
        la = np.log10(aa.realized_Linf.to_numpy(float))
        lb = np.log10(bb.realized_Linf.to_numpy(float))
        d = np.abs(la[:, None] - lb[None, :])
        nb = d.argmin(axis=1)
        na = d.argmin(axis=0)
        for ia, ib in enumerate(nb):
            if na[ib] != ia or d[ia, ib] > caliper:
                continue
            ra, rb = aa.iloc[ia], bb.iloc[ib]
            qa = max(float(ra.Bader_error_resolved_e), 1e-15)
            qb = max(float(rb.Bader_error_resolved_e), 1e-15)
            rows.append({
                "material_id": mid,
                "codec_a": a,
                "codec_b": b,
                "caliper_dex": caliper,
                "linf_a": float(ra.realized_Linf),
                "linf_b": float(rb.realized_Linf),
                "linf_ratio_a_over_b": float(ra.realized_Linf / rb.realized_Linf),
                "qoi_ratio_a_over_b": qa / qb,
            })
    return pd.DataFrame(rows)


def interpolate_pairwise(g, a, b, max_nominal=0.01):
    rows = []
    for mid, m in g.groupby("material_id", sort=False):
        aa = m[(m.codec == a) & (m.nominal_tolerance_relative <= max_nominal) & (m.realized_Linf > 0)].copy()
        bb = m[(m.codec == b) & (m.nominal_tolerance_relative <= max_nominal) & (m.realized_Linf > 0)].copy()
        aa = aa[aa.Bader_error_resolved_e.notna()].sort_values("realized_Linf")
        bb = bb[bb.Bader_error_resolved_e.notna()].sort_values("realized_Linf")
        if len(aa) < 2 or len(bb) < 2:
            continue
        xa = np.log10(aa.realized_Linf.to_numpy(float)); xb = np.log10(bb.realized_Linf.to_numpy(float))
        ya = np.log10(np.clip(aa.Bader_error_resolved_e.to_numpy(float), 1e-15, None))
        yb = np.log10(np.clip(bb.Bader_error_resolved_e.to_numpy(float), 1e-15, None))
        lo = max(xa.min(), xb.min()); hi = min(xa.max(), xb.max())
        if hi <= lo:
            continue
        # Evaluate at three shared points inside the overlap, then take a per-material median.
        xs = np.quantile(np.array([lo, hi]), [0.25, 0.5, 0.75])
        ratios = []
        for x in xs:
            qa = 10 ** np.interp(x, xa, ya)
            qb = 10 ** np.interp(x, xb, yb)
            ratios.append(qa / qb)
        rows.append({
            "material_id": mid,
            "codec_a": a,
            "codec_b": b,
            "overlap_lo_log10_linf": float(lo),
            "overlap_hi_log10_linf": float(hi),
            "qoi_ratio_a_over_b": float(np.median(ratios)),
        })
    return pd.DataFrame(rows)


master = pd.read_csv(ROOT / "benchmark/master_benchmark_full.csv")
master["codec"] = master.codec.astype(str).str.upper()
fails = pd.read_csv(ROOT / "failure_registry.csv")

report = ["# Reviewer stress tests", ""]
report.append("All primary stress tests below restrict the compressor ladder to nominal relative tolerance <= 0.01. This excludes the loose 0.03/0.1 region where Bader-solver failures concentrate and reduces sensitivity to codec-specific early stopping.")
report.append("")

# 1. Failure registry audit
report += ["## 1. Failure-registry audit", ""]
f = fails.copy()
f["codec"] = f.codec.astype(str).str.upper()
f["nominal_tolerance_relative"] = pd.to_numeric(f.nominal_tolerance_relative, errors="coerce")
fail_tab = (f.groupby(["codec", "system_type", "nominal_tolerance_relative"], dropna=False).size().rename("n_failures").reset_index())
fail_tab.to_csv(OUT / "failure_registry_by_codec_system_tolerance.csv", index=False)
low_fail = f[f.nominal_tolerance_relative <= 0.01]
report.append(f"- Total registry rows: {len(f)}; rows at nominal relative tolerance <=0.01: **{len(low_fail)}**.")
if len(low_fail):
    report.append(f"- Low-tolerance failures by codec: {low_fail.codec.value_counts().to_dict()}.")
else:
    report.append("- There are **no registered failures at or below nominal relative tolerance 0.01**.")
report.append(f"- Failure categories overall: {f.category.value_counts().to_dict()}.")
report.append("")

# 2. Matched realized-Linf sensitivity with A.1 eligibility and failure-free ladder
report += ["## 2. Stability-qualified matched-realized-Linf sensitivity in the failure-free ladder", ""]
match_rows = []
for tau in [1e-4, 1e-3, 1e-2]:
    ecol = f"eligible_A1_at_{tau:g}"
    if ecol not in master.columns:
        # exact CSV column formatting uses decimals
        ecol = {1e-4:"eligible_A1_at_0.0001",1e-3:"eligible_A1_at_0.001",1e-2:"eligible_A1_at_0.01"}[tau]
    elig = master[master[ecol].fillna(False).astype(bool)].copy()
    for a, b in [("SZ3", "ZFP"), ("SPERR", "ZFP")]:
        for c in [0.05, 0.075, 0.10, 0.15]:
            mm = mutual_nearest(elig, a, b, c, max_nominal=0.01)
            if mm.empty:
                continue
            per = mm.groupby("material_id").agg(qoi_ratio=("qoi_ratio_a_over_b","median"), linf_ratio=("linf_ratio_a_over_b","median")).reset_index()
            est, lo, hi = bootstrap_median(per.qoi_ratio)
            row = {
                "tau_e":tau,"codec_a":a,"codec_b":b,"caliper_dex":c,
                "n_pairs":len(mm),"n_materials":per.material_id.nunique(),
                "median_qoi_ratio":est,"ci_lo":lo,"ci_hi":hi,
                "fraction_a_worse":float((per.qoi_ratio>1).mean()),
                "median_linf_ratio":float(per.linf_ratio.median()),
            }
            match_rows.append(row)
            report.append(f"- tau={tau:g} e, {a}/{b}, <= {c:.3f} dex: {len(mm)} pairs / {per.material_id.nunique()} materials; QoI ratio **{est:.2f}x** [{lo:.2f}, {hi:.2f}], A worse in {100*row['fraction_a_worse']:.1f}%; median L∞ ratio {row['median_linf_ratio']:.3f}.")
match_df = pd.DataFrame(match_rows)
match_df.to_csv(OUT / "reviewer_matched_linf_sensitivity_failure_free.csv", index=False)
report.append("")

# 3. Interpolation instead of caliper matching
report += ["## 3. Within-material log-log interpolation on common realized-Linf support", ""]
interp_rows = []
for tau in [1e-4, 1e-3, 1e-2]:
    ecol = {1e-4:"eligible_A1_at_0.0001",1e-3:"eligible_A1_at_0.001",1e-2:"eligible_A1_at_0.01"}[tau]
    elig = master[master[ecol].fillna(False).astype(bool)].copy()
    for a,b in [("SZ3","ZFP"),("SPERR","ZFP")]:
        ip = interpolate_pairwise(elig,a,b,max_nominal=0.01)
        if ip.empty:
            continue
        est,lo,hi=bootstrap_median(ip.qoi_ratio_a_over_b)
        row={"tau_e":tau,"codec_a":a,"codec_b":b,"n_materials":len(ip),"median_qoi_ratio":est,"ci_lo":lo,"ci_hi":hi,"fraction_a_worse":float((ip.qoi_ratio_a_over_b>1).mean())}
        interp_rows.append(row)
        report.append(f"- tau={tau:g} e, {a}/{b}: {len(ip)} materials; interpolated QoI ratio **{est:.2f}x** [{lo:.2f}, {hi:.2f}], A worse in {100*row['fraction_a_worse']:.1f}%.")
pd.DataFrame(interp_rows).to_csv(OUT / "reviewer_common_support_interpolation.csv", index=False)
report.append("")

# 4. Mechanism attenuation: does basin reassignment explain part of codec effect?
report += ["## 4. Mechanism attenuation after adding basin-reassignment and fixed-basin terms", ""]
try:
    import statsmodels.formula.api as smf
    tau=1e-3
    g = master[(master["eligible_A1_at_0.001"].fillna(False).astype(bool)) & (master.nominal_tolerance_relative <= 0.01) & (master.realized_Linf>0)].copy()
    g = g[g.Bader_error_resolved_e.notna()].copy()
    g["logQ"] = np.log10(np.clip(g.Bader_error_resolved_e.astype(float),1e-15,None))
    g["logL"] = np.log10(g.realized_Linf.astype(float))
    g["logL_c"] = g.logL - g.logL.median()
    pseudo = 0.5 / np.clip(g.npoints.astype(float),1,None)
    g["logReassign"] = np.log10(np.clip(g.frac_voxels_reassigned.astype(float),0,None) + pseudo)
    g["logFixed"] = np.log10(np.clip(g.Bader_error_fixed_e.astype(float),1e-15,None))
    formulas = {
        "M0_Linf_codec_material":"logQ ~ logL_c + C(codec, Treatment(reference='ZFP')) + C(material_id)",
        "M1_plus_reassignment":"logQ ~ logL_c + logReassign + C(codec, Treatment(reference='ZFP')) + C(material_id)",
        "M2_plus_reassignment_fixed":"logQ ~ logL_c + logReassign + logFixed + C(codec, Treatment(reference='ZFP')) + C(material_id)",
    }
    coef_rows=[]
    for name,form in formulas.items():
        fit=smf.ols(form,data=g).fit(cov_type="cluster",cov_kwds={"groups":g.material_id})
        for codec in ["SZ3","SPERR"]:
            term=f"C(codec, Treatment(reference='ZFP'))[T.{codec}]"
            beta=float(fit.params[term]); se=float(fit.bse[term]); p=float(fit.pvalues[term])
            coef_rows.append({"model":name,"codec":codec,"beta_log10":beta,"multiplicative":10**beta,"ci_lo":10**(beta-1.96*se),"ci_hi":10**(beta+1.96*se),"p":p,"n_rows":len(g),"n_materials":g.material_id.nunique()})
        if "logReassign" in fit.params:
            beta=float(fit.params["logReassign"]); se=float(fit.bse["logReassign"])
            report.append(f"- {name}: reassignment coefficient beta={beta:.3f} log10-Q per log10 reassigned-fraction [95% {beta-1.96*se:.3f}, {beta+1.96*se:.3f}].")
    cdf=pd.DataFrame(coef_rows)
    cdf.to_csv(OUT / "reviewer_codec_effect_mechanism_attenuation.csv", index=False)
    for codec in ["SZ3","SPERR"]:
        sub=cdf[cdf.codec==codec].set_index("model")
        m0=sub.loc["M0_Linf_codec_material","multiplicative"]
        m1=sub.loc["M1_plus_reassignment","multiplicative"]
        m2=sub.loc["M2_plus_reassignment_fixed","multiplicative"]
        report.append(f"- {codec}/ZFP codec effect: M0 **{m0:.2f}x** -> +reassignment **{m1:.2f}x** -> +reassignment+fixed-basin **{m2:.2f}x**.")
except Exception as e:
    report.append(f"Mechanism regression unavailable: {type(e).__name__}: {e}")
report.append("")

# 5. Fixed-basin understatement robust direction
report += ["## 5. Fixed-basin metric directionality", ""]
g=master[master.ladder=="base"].copy()
valid=g[(g.Bader_error_resolved_e.notna()) & (g.Bader_error_fixed_e.notna())]
report.append(f"- Among {len(valid)} successful base-ladder rows, resolved error exceeds fixed-basin error in **{100*(valid.Bader_error_resolved_e>valid.Bader_error_fixed_e).mean():.1f}%** of rows; equals it in {100*np.isclose(valid.Bader_error_resolved_e,valid.Bader_error_fixed_e).mean():.1f}%.")
for codec,gg in valid.groupby("codec"):
    ratio=np.clip(gg.Bader_error_resolved_e.astype(float),1e-15,None)/np.clip(gg.Bader_error_fixed_e.astype(float),1e-15,None)
    est,lo,hi=bootstrap_median(ratio)
    report.append(f"- {codec}: median resolved/fixed ratio **{est:.1f}x** [{lo:.1f}, {hi:.1f}], resolved > fixed in {100*(gg.Bader_error_resolved_e>gg.Bader_error_fixed_e).mean():.1f}%.")

(OUT / "reviewer_stress_tests.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print("\n".join(report))
