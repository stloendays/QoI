from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_output"
OUT.mkdir(exist_ok=True)
RNG_SEED = 20260906


def q(x, p):
    x = pd.to_numeric(pd.Series(x), errors="coerce").dropna().to_numpy(float)
    return float(np.quantile(x, p)) if len(x) else float("nan")


def fmt(x, digits=3):
    if x is None or not np.isfinite(float(x)):
        return "NA"
    x = float(x)
    if x == 0:
        return "0"
    if abs(x) < 1e-3 or abs(x) >= 1e4:
        return f"{x:.{digits}g}"
    return f"{x:.{digits}f}"


def bootstrap_material_median(df, value_col, n_boot=4000):
    d = df[["material_id", value_col]].dropna()
    mats = d["material_id"].unique()
    if len(mats) == 0:
        return (np.nan, np.nan, np.nan)
    material_vals = d.groupby("material_id")[value_col].median()
    est = float(material_vals.median())
    rng = np.random.default_rng(RNG_SEED)
    vals = material_vals.to_numpy(float)
    boots = np.median(rng.choice(vals, size=(n_boot, len(vals)), replace=True), axis=1)
    lo, hi = np.quantile(boots, [0.025, 0.975])
    return est, float(lo), float(hi)


def mutual_nearest_matches(df, codec_a, codec_b, max_dex):
    rows = []
    codec_a = codec_a.upper(); codec_b = codec_b.upper()
    for material_id, g in df.groupby("material_id", sort=False):
        a = g[g.codec == codec_a].copy()
        b = g[g.codec == codec_b].copy()
        if a.empty or b.empty:
            continue
        a = a[(a.realized_Linf > 0) & (a.Bader_error_resolved_e >= 0)].reset_index(drop=False)
        b = b[(b.realized_Linf > 0) & (b.Bader_error_resolved_e >= 0)].reset_index(drop=False)
        if a.empty or b.empty:
            continue
        la = np.log10(a.realized_Linf.to_numpy(float))
        lb = np.log10(b.realized_Linf.to_numpy(float))
        dist = np.abs(la[:, None] - lb[None, :])
        nb = dist.argmin(axis=1)
        na = dist.argmin(axis=0)
        for ia, ib in enumerate(nb):
            if na[ib] != ia:
                continue
            dex = float(dist[ia, ib])
            if dex > max_dex:
                continue
            ra, rb = a.iloc[ia], b.iloc[ib]
            qa = max(float(ra.Bader_error_resolved_e), 1e-15)
            qb = max(float(rb.Bader_error_resolved_e), 1e-15)
            rows.append({
                "material_id": material_id,
                "system_type": ra.system_type,
                "codec_a": codec_a,
                "codec_b": codec_b,
                "max_match_dex": max_dex,
                "ladder_a": ra.ladder,
                "ladder_b": rb.ladder,
                "nominal_rel_a": ra.nominal_tolerance_relative,
                "nominal_rel_b": rb.nominal_tolerance_relative,
                "linf_a": ra.realized_Linf,
                "linf_b": rb.realized_Linf,
                "linf_ratio_a_over_b": float(ra.realized_Linf / rb.realized_Linf),
                "abs_log10_linf_diff": dex,
                "qoi_a": qa,
                "qoi_b": qb,
                "qoi_ratio_a_over_b": qa / qb,
                "compression_a": ra.compression_ratio,
                "compression_b": rb.compression_ratio,
            })
    return pd.DataFrame(rows)


def matched_summary(matches):
    if matches.empty:
        return {}
    mat = matches.groupby("material_id").agg(
        qoi_ratio=("qoi_ratio_a_over_b", "median"),
        linf_ratio=("linf_ratio_a_over_b", "median"),
        abs_dex=("abs_log10_linf_diff", "median"),
        n_pairs=("qoi_ratio_a_over_b", "size"),
    ).reset_index()
    est, lo, hi = bootstrap_material_median(mat, "qoi_ratio")
    return {
        "n_pairs": int(len(matches)),
        "n_materials": int(mat.material_id.nunique()),
        "median_qoi_ratio_material": est,
        "qoi_ratio_ci_lo": lo,
        "qoi_ratio_ci_hi": hi,
        "median_linf_ratio_material": float(mat.linf_ratio.median()),
        "median_abs_match_dex": float(mat.abs_dex.median()),
        "fraction_materials_a_worse": float((mat.qoi_ratio > 1).mean()),
    }


def same_nominal_stats(base, codec_a, codec_b, rel):
    keys = ["material_id", "system_type", "nominal_tolerance_relative"]
    cols = keys + ["realized_Linf", "Bader_error_resolved_e"]
    a = base[(base.codec == codec_a) & np.isclose(base.nominal_tolerance_relative, rel)][cols].copy()
    b = base[(base.codec == codec_b) & np.isclose(base.nominal_tolerance_relative, rel)][cols].copy()
    m = a.merge(b, on=keys, suffixes=("_a", "_b"))
    if m.empty:
        return {}
    m["qoi_ratio"] = np.clip(m.Bader_error_resolved_e_a.astype(float), 1e-15, None) / np.clip(m.Bader_error_resolved_e_b.astype(float), 1e-15, None)
    m["linf_ratio"] = m.realized_Linf_a / m.realized_Linf_b
    m["material_id"] = m.material_id.astype(str)
    est, lo, hi = bootstrap_material_median(m, "qoi_ratio")
    return {
        "n": int(len(m)),
        "median_qoi_ratio": est,
        "qoi_ci_lo": lo,
        "qoi_ci_hi": hi,
        "fraction_a_worse": float((m.qoi_ratio > 1).mean()),
        "median_linf_ratio": float(m.linf_ratio.median()),
        "linf_q25": q(m.linf_ratio, .25),
        "linf_q75": q(m.linf_ratio, .75),
    }


def bootstrap_ratio_ci(values, n_boot=4000):
    v = pd.to_numeric(pd.Series(values), errors="coerce").dropna().to_numpy(float)
    if len(v) == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(RNG_SEED)
    est = float(np.median(v))
    boots = np.median(rng.choice(v, size=(n_boot, len(v)), replace=True), axis=1)
    lo, hi = np.quantile(boots, [0.025, .975])
    return est, float(lo), float(hi)


# ---------- Load ----------
master = pd.read_csv(ROOT / "benchmark/master_benchmark_full.csv")
master["codec"] = master.codec.astype(str).str.upper()
base = master[master.ladder == "base"].copy()
tight = master[master.ladder == "tight"].copy()
metadata = pd.read_csv(ROOT / "materials_metadata.csv")
floors = pd.read_csv(ROOT / "stability/stability_floor_A1.csv")
probe = pd.read_csv(ROOT / "stability/probe_calibration.csv")
mech = pd.read_csv(ROOT / "mechanism/basin_error_decomposition_summary.csv")
fails = pd.read_csv(ROOT / "failure_registry.csv")
best = pd.read_csv(ROOT / "benchmark/best_certified_a1.csv")
best["codec"] = best.codec.astype(str).str.upper()

report = []
report.append("# Statistical post-processing audit")
report.append("")
report.append("Generated from the frozen repository tables on branch `analysis/chatgpt-postprocess-20260906`.")
report.append("")

# ---------- Integrity ----------
report += ["## 1. Integrity and scope", ""]
report.append(f"- Master table: **{len(master):,} rows**, **{master.material_id.nunique()} materials**, codecs = {', '.join(sorted(master.codec.unique()))}.")
report.append(f"- Base ladder: **{len(base):,} rows**; tight ladder: **{len(tight):,} rows**.")
report.append(f"- `bound_respected` all true: **{bool(master.bound_respected.fillna(False).all())}**; maximum realized/nominal = **{master.realized_Linf_over_nominal.max():.9f}**.")
report.append(f"- Failure registry: **{len(fails)} rows**; categories: {fails.category.value_counts().to_dict()}.")
report.append("")

# ---------- Bound utilization ----------
util_rows = []
for (codec, ladder), g in master.groupby(["codec", "ladder"]):
    x = g.realized_Linf_over_nominal.astype(float)
    util_rows.append({"codec": codec, "ladder": ladder, "n": len(g), "median": x.median(), "q25": x.quantile(.25), "q75": x.quantile(.75), "p05": x.quantile(.05), "p95": x.quantile(.95)})
util = pd.DataFrame(util_rows)
util.to_csv(OUT / "bound_utilization_summary.csv", index=False)
report += ["## 2. Bound utilization: nominal is not realized", ""]
for codec in ["SZ3", "ZFP", "SPERR"]:
    x = master.loc[master.codec == codec, "realized_Linf_over_nominal"].astype(float)
    report.append(f"- **{codec}**: median {x.median():.4f}; IQR [{x.quantile(.25):.4f}, {x.quantile(.75):.4f}]; 5–95% [{x.quantile(.05):.4f}, {x.quantile(.95):.4f}].")
report.append("")
report.append("This directly separates a **bound-utilization effect** (how much of the requested pointwise budget a codec actually uses) from any **residual spatial-structure effect** at matched realized L∞.")
report.append("")

# Same nominal comparisons
report += ["### Same nominal compression tolerance", ""]
same_rows = []
for a, b in [("SZ3", "ZFP"), ("SPERR", "ZFP")]:
    for rel in [1e-4, 1e-3, 1e-2]:
        s = same_nominal_stats(base, a, b, rel)
        if not s:
            continue
        same_rows.append({"codec_a": a, "codec_b": b, "nominal_relative": rel, **s})
        report.append(f"- {a}/{b}, nominal {rel:g}: n={s['n']}, median resolved-QoI ratio **{s['median_qoi_ratio']:.2f}×** [{s['qoi_ci_lo']:.2f}, {s['qoi_ci_hi']:.2f}], A worse in {100*s['fraction_a_worse']:.1f}%; median realized-L∞ ratio **{s['median_linf_ratio']:.2f}×**.")
pd.DataFrame(same_rows).to_csv(OUT / "same_nominal_pairwise.csv", index=False)
report.append("")

# Matched realized-Linf
report += ["### Mutual-nearest matching on realized L∞", ""]
matched_summaries = []
for a, b in [("SZ3", "ZFP"), ("SPERR", "ZFP")]:
    for dex in [0.10, 0.15, 0.20, 0.25]:
        mm = mutual_nearest_matches(master, a, b, dex)
        s = matched_summary(mm)
        if not s:
            continue
        matched_summaries.append({"codec_a": a, "codec_b": b, "max_match_dex": dex, **s})
        report.append(f"- {a}/{b}, ≤{dex:.2f} dex: {s['n_pairs']} matched points from {s['n_materials']} materials; median material-level L∞ ratio {s['median_linf_ratio_material']:.3f}; median QoI-error ratio **{s['median_qoi_ratio_material']:.2f}×** [{s['qoi_ratio_ci_lo']:.2f}, {s['qoi_ratio_ci_hi']:.2f}]; A worse in {100*s['fraction_materials_a_worse']:.1f}% of materials.")
        if abs(dex - 0.20) < 1e-9:
            mm.to_csv(OUT / f"matched_realized_linf_{a.lower()}_vs_{b.lower()}_020dex.csv", index=False)
pd.DataFrame(matched_summaries).to_csv(OUT / "matched_realized_linf_summary.csv", index=False)
report.append("")
report.append("Interpretation rule: a large same-nominal ratio that collapses toward 1 after realized-L∞ matching is primarily a **bound-utilization** phenomenon; a ratio that remains materially above 1 after matching is evidence for a **codec-specific residual structure effect** beyond L∞ magnitude.")
report.append("")

# Fixed-effects regression controlling realized Linf
report += ["### Material-fixed-effect regression", ""]
try:
    import statsmodels.formula.api as smf
    reg = master[(master.realized_Linf > 0) & master.Bader_error_resolved_e.notna()].copy()
    # restrict to global common support across codecs
    ranges = reg.groupby("codec")["realized_Linf"].agg(["min", "max"])
    lo = ranges["min"].max(); hi = ranges["max"].min()
    reg = reg[(reg.realized_Linf >= lo) & (reg.realized_Linf <= hi)].copy()
    reg["logL"] = np.log10(reg.realized_Linf.astype(float))
    center = float(reg.logL.median())
    reg["logL_c"] = reg.logL - center
    reg["logQ"] = np.log10(np.clip(reg.Bader_error_resolved_e.astype(float), 1e-15, None))
    model = smf.ols("logQ ~ logL_c * C(codec, Treatment(reference='ZFP')) + C(material_id)", data=reg).fit(cov_type="cluster", cov_kwds={"groups": reg.material_id})
    coefs = []
    for term in ["C(codec, Treatment(reference='ZFP'))[T.SZ3]", "C(codec, Treatment(reference='ZFP'))[T.SPERR]", "logL_c:C(codec, Treatment(reference='ZFP'))[T.SZ3]", "logL_c:C(codec, Treatment(reference='ZFP'))[T.SPERR]"]:
        if term in model.params:
            beta = float(model.params[term]); se=float(model.bse[term]); p=float(model.pvalues[term]);
            coefs.append({"term": term, "beta_log10": beta, "multiplicative": 10**beta, "ci_low_mult": 10**(beta-1.96*se), "ci_high_mult": 10**(beta+1.96*se), "p": p})
    pd.DataFrame(coefs).to_csv(OUT / "realized_linf_fixed_effect_regression.csv", index=False)
    report.append(f"Common realized-L∞ support: [{lo:.3g}, {hi:.3g}], n={len(reg)}, centered at log10 L∞={center:.3f}.")
    for r in coefs:
        report.append(f"- {r['term']}: beta={r['beta_log10']:.3f} log10 units; multiplicative effect {r['multiplicative']:.2f}× [95% CI {r['ci_low_mult']:.2f}, {r['ci_high_mult']:.2f}], p={r['p']:.3g}.")
except Exception as e:
    report.append(f"Regression unavailable: `{type(e).__name__}: {e}`")
report.append("")

# ---------- Fixed vs resolved ----------
report += ["## 3. Fixed-basin versus resolved-basin error", ""]
r = pd.to_numeric(base.fixed_basin_understatement, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
report.append(f"Across the {len(base):,}-row base ladder, finite resolved/fixed understatement ratios have median **{r.median():.1f}×**, p90 **{r.quantile(.90):.1f}×**; {100*(r>2).mean():.1f}% exceed 2×, {100*(r>10).mean():.1f}% exceed 10×, and {100*(r>100).mean():.1f}% exceed 100×.")
fb_rows=[]
for codec, g in base.groupby("codec"):
    x=pd.to_numeric(g.fixed_basin_understatement,errors="coerce").replace([np.inf,-np.inf],np.nan).dropna()
    fb_rows.append({"codec":codec,"n":len(x),"median":x.median(),"p90":x.quantile(.9),"frac_gt2":(x>2).mean(),"frac_gt10":(x>10).mean()})
pd.DataFrame(fb_rows).to_csv(OUT / "fixed_vs_resolved_summary.csv", index=False)
for z in fb_rows:
    report.append(f"- {z['codec']}: median {z['median']:.1f}×; p90 {z['p90']:.1f}×; >2× in {100*z['frac_gt2']:.1f}%.")
report.append("")

# ---------- Pareto / certification ----------
report += ["## 4. Compression–certification frontier", ""]
pareto_rows=[]
for (domain, threshold, codec), g in best.groupby(["domain","threshold_e","codec"]):
    counts=g.status.value_counts().to_dict()
    cert=g[g.status=="CERTIFIED"].ratio.dropna().astype(float)
    est,lo,hi=bootstrap_ratio_ci(cert)
    pareto_rows.append({"domain":domain,"threshold_e":threshold,"codec":codec,"n_rows":len(g),"status_counts":json.dumps(counts,sort_keys=True),"n_certified":len(cert),"certified_share_of_rows":len(cert)/len(g) if len(g) else np.nan,"median_ratio_certified":est,"ci_lo":lo,"ci_hi":hi})
pareto=pd.DataFrame(pareto_rows)
pareto.to_csv(OUT / "pareto_certification_summary.csv",index=False)
for threshold in sorted(pareto.threshold_e.unique()):
    for domain in sorted(pareto.loc[pareto.threshold_e==threshold,"domain"].unique()):
        sub=pareto[(pareto.threshold_e==threshold)&(pareto.domain==domain)].sort_values("codec")
        bits=[]
        for _,z in sub.iterrows():
            bits.append(f"{z.codec}: {z.median_ratio_certified:.1f}×, status {z.status_counts}")
        report.append(f"- τ={threshold:g}, {domain}: " + "; ".join(bits))
report.append("")

# ---------- Resolvability predictability ----------
report += ["## 5. Can conventional descriptors predict A.1 resolvability?", ""]
try:
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, balanced_accuracy_score, brier_score_loss
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    d=floors.merge(metadata,on="material_id",how="left",suffixes=("_floor","_meta"))
    # use metadata conventional descriptors; domain from floor is always present
    d["log_npoints"]=np.log10(pd.to_numeric(d.npoints_floor,errors="coerce"))
    d["log_natoms"]=np.log10(pd.to_numeric(d.natoms_floor,errors="coerce"))
    d["log_points_per_atom"]=d.log_npoints-d.log_natoms
    d["vacuum_fraction_num"]=pd.to_numeric(d.get("vacuum_fraction"),errors="coerce")
    d["cell_c_num"]=pd.to_numeric(d.get("cell_c_angstrom"),errors="coerce")
    d["domain_cat"]=d.domain.astype(str)
    num=["log_npoints","log_natoms","log_points_per_atom","vacuum_fraction_num","cell_c_num"]
    cat=["domain_cat"]
    pre=ColumnTransformer([("num",Pipeline([("imp",SimpleImputer(strategy="median",add_indicator=True)),("sc",StandardScaler())]),num),("cat",OneHotEncoder(handle_unknown="ignore"),cat)])
    clf=Pipeline([("pre",pre),("lr",LogisticRegression(max_iter=5000,class_weight="balanced",random_state=RNG_SEED))])
    pred_rows=[]
    for tau in [1e-4,1e-3,1e-2]:
        for excl in [False,True]:
            dd=d.copy()
            label="all"
            if excl:
                dd=dd[dd.material_id!="aflow-Al8Cu4U1_ICSD_601801"].copy(); label="exclude_known_symmetry_relabel"
            dd["eligible"]=(dd.stability_floor_A1_e.astype(float) < tau).astype(int)
            dev=dd[dd.corpus_floor.astype(str).str.startswith("dev")].dropna(subset=["eligible"])
            ext=dd[dd.corpus_floor.astype(str).str.startswith("ext")].dropna(subset=["eligible"])
            Xd=dev[num+cat]; yd=dev.eligible
            cv_auc=np.nan; cv_sd=np.nan
            if yd.nunique()==2 and yd.value_counts().min()>=5:
                cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=RNG_SEED)
                scores=cross_val_score(clf,Xd,yd,cv=cv,scoring="roc_auc")
                cv_auc=float(scores.mean());cv_sd=float(scores.std(ddof=1))
            ext_auc=ext_bal=ext_brier=np.nan
            if yd.nunique()==2 and len(ext) and ext.eligible.nunique()==2:
                clf.fit(Xd,yd)
                p=clf.predict_proba(ext[num+cat])[:,1]
                yh=(p>=.5).astype(int)
                ext_auc=float(roc_auc_score(ext.eligible,p));ext_bal=float(balanced_accuracy_score(ext.eligible,yh));ext_brier=float(brier_score_loss(ext.eligible,p))
            pred_rows.append({"tau_e":tau,"sensitivity":label,"n_dev":len(dev),"n_ext":len(ext),"eligible_dev":yd.mean(),"eligible_ext":ext.eligible.mean() if len(ext) else np.nan,"cv_auc_mean":cv_auc,"cv_auc_sd":cv_sd,"external_auc":ext_auc,"external_balanced_accuracy":ext_bal,"external_brier":ext_brier})
    pred=pd.DataFrame(pred_rows);pred.to_csv(OUT/"resolvability_predictability.csv",index=False)
    for _,z in pred[pred.sensitivity=="all"].iterrows():
        report.append(f"- τ={z.tau_e:g}: dev 5-fold AUROC {fmt(z.cv_auc_mean)} ± {fmt(z.cv_auc_sd)}; external AUROC **{fmt(z.external_auc)}**, balanced accuracy {fmt(z.external_balanced_accuracy)}; eligibility prevalence dev/ext {100*z.eligible_dev:.1f}%/{100*z.eligible_ext:.1f}%.")
except Exception as e:
    report.append(f"Predictability audit unavailable: `{type(e).__name__}: {e}`")
report.append("")

# ---------- Probe validation ----------
report += ["## 6. Protocol A.1 probe validation", ""]
probe["seed_str"]=probe.seed.astype(str)
float32=probe[probe.seed_str=="float32"].copy()
noise1=probe[(probe.seed_str=="20260905") & np.isclose(probe.amplitude_factor.astype(float),1.0)].copy()
p=float32.merge(noise1,on="material_id",suffixes=("_f32","_noise"))
p["floor_ratio_noise_over_f32"]=np.clip(p.floor_e_noise.astype(float),1e-30,None)/np.clip(p.floor_e_f32.astype(float),1e-30,None)
report.append(f"- Matched float32 vs calibrated random-noise probe (amplitude factor 1): n={len(p)}, median floor ratio **{p.floor_ratio_noise_over_f32.median():.1f}×**; float32 median exact ties {p.n_exact_neighbour_ties_created_f32.median():.0f} vs noise {p.n_exact_neighbour_ties_created_noise.median():.0f}; zero voxel reassignment {int((p.n_voxels_reassigned_f32==0).sum())}/{len(p)} vs {int((p.n_voxels_reassigned_noise==0).sum())}/{len(p)}.")
# seed range at amplitude 1, non-float32
seedset=probe[(probe.seed_str!="float32") & np.isclose(probe.amplitude_factor.astype(float),1.0)].copy()
seed_ranges=[]
for mid,g in seedset.groupby("material_id"):
    vals=np.log10(np.clip(g.floor_e.astype(float).to_numpy(),1e-30,None))
    seed_ranges.append({"material_id":mid,"log10_floor_range":vals.max()-vals.min(),"n_seed":len(vals)})
seed_ranges=pd.DataFrame(seed_ranges)
report.append(f"- Across random seeds at amplitude 1: median log10-floor range **{seed_ranges.log10_floor_range.median():.2f} decades**; maximum **{seed_ranges.log10_floor_range.max():.2f} decades**.")
# amplitude factor 0.1,1,10 for calibration seed
amp=probe[probe.seed_str=="20260905"].copy()
amp_stats=[]
for mid,g in amp.groupby("material_id"):
    gg=g.sort_values("amplitude_factor")
    if set(np.round(gg.amplitude_factor.astype(float),10)) >= {0.1,1.0,10.0}:
        low=float(gg.loc[np.isclose(gg.amplitude_factor,0.1),"floor_e"].iloc[0]); high=float(gg.loc[np.isclose(gg.amplitude_factor,10.0),"floor_e"].iloc[0])
        amp_stats.append({"material_id":mid,"two_decade_floor_shift":math.log10(max(high,1e-30))-math.log10(max(low,1e-30))})
amp_stats=pd.DataFrame(amp_stats)
if len(amp_stats):
    report.append(f"- Amplitude sensitivity from 0.1× to 10×: median floor shift **{amp_stats.two_decade_floor_shift.median():.2f} decades** (IQR {amp_stats.two_decade_floor_shift.quantile(.25):.2f}–{amp_stats.two_decade_floor_shift.quantile(.75):.2f}).")
probe_stats=pd.DataFrame([{"metric":"noise_over_float32_floor_ratio_median","value":p.floor_ratio_noise_over_f32.median()},{"metric":"seed_log10_range_median","value":seed_ranges.log10_floor_range.median()},{"metric":"seed_log10_range_max","value":seed_ranges.log10_floor_range.max()},{"metric":"amplitude_two_decade_shift_median","value":amp_stats.two_decade_floor_shift.median() if len(amp_stats) else np.nan}])
probe_stats.to_csv(OUT/"probe_validation_stats.csv",index=False)
report.append("")

# ---------- Mechanism ----------
report += ["## 7. Basin-domain mechanism decomposition", ""]
mech["closure_residual"] = mech.dq_total_at_that_atom - mech.dq_integrand_at_that_atom - mech.dq_domain_at_that_atom
mech["domain_abs_fraction"] = np.abs(mech.dq_domain_at_that_atom)/(np.abs(mech.dq_domain_at_that_atom)+np.abs(mech.dq_integrand_at_that_atom)+1e-30)
mech["domain_over_total_abs"] = np.abs(mech.dq_domain_at_that_atom)/(np.abs(mech.dq_total_at_that_atom)+1e-30)
report.append(f"- Rows: {len(mech)} ({mech.material_id.nunique()} materials). Max absolute closure residual = **{np.abs(mech.closure_residual).max():.3e} e**.")
report.append(f"- Bounded dominance fraction |domain|/(|domain|+|integrand|): median **{mech.domain_abs_fraction.median():.3f}**, IQR [{mech.domain_abs_fraction.quantile(.25):.3f}, {mech.domain_abs_fraction.quantile(.75):.3f}]; >0.90 in {100*(mech.domain_abs_fraction>.9).mean():.1f}% of cases.")
report.append(f"- |domain|/|total| at the maximum-error atom: median **{mech.domain_over_total_abs.median():.3f}** (can exceed 1 under cancellation).")
mech.groupby(["codec","relative_tolerance"])[["domain_abs_fraction","domain_over_total_abs"]].median().reset_index().to_csv(OUT/"mechanism_domain_fraction_by_codec_tolerance.csv",index=False)
report.append("")

# ---------- Failure registry ----------
report += ["## 8. Failure registry", ""]
for cat,n in fails.category.value_counts().items():
    report.append(f"- {cat}: {n}")
report.append("- Failure rows remain outside the successful benchmark by design; manuscript denominators should therefore state whether they are successful-decode/Bader rows, eligible materials, or all attempted cases.")
report.append("")

# ---------- Editorial decision ----------
report += ["## 9. Claim wording decision rule", ""]
report.append("1. **Always safe:** A nominal pointwise error bound alone is insufficient to predict downstream Bader fidelity.")
report.append("2. **Stronger claim only if matched analysis survives:** At comparable realized L∞, codec identity remains associated with materially different resolved Bader errors, implicating spatial error structure beyond magnitude alone.")
report.append("3. If the matched ratio collapses to ~1, attribute the same-nominal difference mainly to **bound utilization**, not spatial structure.")
report.append("4. Describe the A.1 stability floor as a **protocol-defined / probe-defined numerical stability floor**, not an intrinsic material constant, because it is amplitude- and seed-dependent.")
report.append("")

text="\n".join(report)+"\n"
(OUT/"statistics_report.md").write_text(text,encoding="utf-8")
print(text)
