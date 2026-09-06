from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_output"
OUT.mkdir(exist_ok=True)
SEED = 20260906


def bootstrap_median(values, n_boot=5000):
    x = pd.Series(values).replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
    if len(x) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(SEED)
    est = float(np.median(x))
    boots = np.median(rng.choice(x, size=(n_boot, len(x)), replace=True), axis=1)
    lo, hi = np.quantile(boots, [0.025, 0.975])
    return est, float(lo), float(hi)


def eligible_mask(df, col):
    s = df[col]
    if pd.api.types.is_bool_dtype(s):
        return s.fillna(False)
    return s.astype(str).str.lower().eq("true")


def mutual_nearest(df, codec_a, codec_b, caliper_dex, max_nominal=0.01):
    rows = []
    for material_id, g in df.groupby("material_id", sort=False):
        a = g[(g.codec == codec_a) & (g.nominal_tolerance_relative <= max_nominal)].copy()
        b = g[(g.codec == codec_b) & (g.nominal_tolerance_relative <= max_nominal)].copy()
        a = a[(a.realized_Linf > 0) & a.Bader_error_resolved_e.notna()].reset_index(drop=True)
        b = b[(b.realized_Linf > 0) & b.Bader_error_resolved_e.notna()].reset_index(drop=True)
        if a.empty or b.empty:
            continue
        la = np.log10(a.realized_Linf.to_numpy(float))
        lb = np.log10(b.realized_Linf.to_numpy(float))
        dist = np.abs(la[:, None] - lb[None, :])
        nearest_b = dist.argmin(axis=1)
        nearest_a = dist.argmin(axis=0)
        for ia, ib in enumerate(nearest_b):
            if nearest_a[ib] != ia or float(dist[ia, ib]) > caliper_dex:
                continue
            ra, rb = a.iloc[ia], b.iloc[ib]
            qa = max(float(ra.Bader_error_resolved_e), 1e-15)
            qb = max(float(rb.Bader_error_resolved_e), 1e-15)
            rows.append({
                "material_id": material_id,
                "codec_a": codec_a,
                "codec_b": codec_b,
                "caliper_dex": caliper_dex,
                "linf_ratio_a_over_b": float(ra.realized_Linf / rb.realized_Linf),
                "qoi_ratio_a_over_b": qa / qb,
            })
    return pd.DataFrame(rows)


def interpolate_pairwise(df, codec_a, codec_b, max_nominal=0.01):
    rows = []
    for material_id, g in df.groupby("material_id", sort=False):
        a = g[(g.codec == codec_a) & (g.nominal_tolerance_relative <= max_nominal) & (g.realized_Linf > 0)].copy()
        b = g[(g.codec == codec_b) & (g.nominal_tolerance_relative <= max_nominal) & (g.realized_Linf > 0)].copy()
        a = a[a.Bader_error_resolved_e.notna()].sort_values("realized_Linf")
        b = b[b.Bader_error_resolved_e.notna()].sort_values("realized_Linf")
        if len(a) < 2 or len(b) < 2:
            continue
        xa = np.log10(a.realized_Linf.to_numpy(float))
        xb = np.log10(b.realized_Linf.to_numpy(float))
        ya = np.log10(np.clip(a.Bader_error_resolved_e.to_numpy(float), 1e-15, None))
        yb = np.log10(np.clip(b.Bader_error_resolved_e.to_numpy(float), 1e-15, None))
        lo = max(float(xa.min()), float(xb.min()))
        hi = min(float(xa.max()), float(xb.max()))
        if hi <= lo:
            continue
        xs = lo + np.array([0.25, 0.50, 0.75]) * (hi - lo)
        ratios = []
        for x in xs:
            qa = 10 ** np.interp(x, xa, ya)
            qb = 10 ** np.interp(x, xb, yb)
            ratios.append(qa / qb)
        rows.append({
            "material_id": material_id,
            "codec_a": codec_a,
            "codec_b": codec_b,
            "overlap_lo_log10_linf": lo,
            "overlap_hi_log10_linf": hi,
            "qoi_ratio_a_over_b": float(np.median(ratios)),
        })
    return pd.DataFrame(rows)


master = pd.read_csv(ROOT / "benchmark/master_benchmark_full.csv")
master["codec"] = master.codec.astype(str).str.upper()
fails = pd.read_csv(ROOT / "failure_registry.csv")

report = ["# Reviewer stress tests", ""]
report.append("Primary stress tests restrict the compressor ladder to nominal relative tolerance <= 0.01. This removes the loose 0.03/0.1 region where registered Bader-solver failures concentrate and reduces sensitivity to codec-specific early stopping.")
report.append("")

# 1. Failure-registry audit
report += ["## 1. Failure-registry audit", ""]
f = fails.copy()
f["codec"] = f.codec.astype(str).str.upper()
f["nominal_tolerance_relative"] = pd.to_numeric(f.nominal_tolerance_relative, errors="coerce")
fail_tab = (
    f.groupby(["codec", "domain", "nominal_tolerance_relative"], dropna=False)
    .size().rename("n_failures").reset_index()
)
fail_tab.to_csv(OUT / "failure_registry_by_codec_domain_tolerance.csv", index=False)
low_fail = f[f.nominal_tolerance_relative <= 0.01]
report.append(f"- Total registry rows: {len(f)}; rows at nominal relative tolerance <=0.01: **{len(low_fail)}**.")
if len(low_fail):
    report.append(f"- Low-tolerance failures by codec: {low_fail.codec.value_counts().to_dict()}.")
else:
    report.append("- There are **no registered failures at or below nominal relative tolerance 0.01**.")
report.append(f"- Failure categories overall: {f.category.value_counts().to_dict()}.")
report.append("")

# 2. Stability-qualified matched realized-Linf sensitivity
report += ["## 2. Stability-qualified matched-realized-Linf sensitivity in the failure-free ladder", ""]
match_rows = []
for tau, ecol in [(1e-4, "eligible_A1_at_0.0001"), (1e-3, "eligible_A1_at_0.001"), (1e-2, "eligible_A1_at_0.01")]:
    elig = master[eligible_mask(master, ecol)].copy()
    for codec_a, codec_b in [("SZ3", "ZFP"), ("SPERR", "ZFP")]:
        for caliper in [0.05, 0.075, 0.10, 0.15]:
            mm = mutual_nearest(elig, codec_a, codec_b, caliper, max_nominal=0.01)
            if mm.empty:
                continue
            per = mm.groupby("material_id").agg(
                qoi_ratio=("qoi_ratio_a_over_b", "median"),
                linf_ratio=("linf_ratio_a_over_b", "median"),
            ).reset_index()
            est, lo, hi = bootstrap_median(per.qoi_ratio)
            row = {
                "tau_e": tau, "codec_a": codec_a, "codec_b": codec_b,
                "caliper_dex": caliper, "n_pairs": len(mm),
                "n_materials": per.material_id.nunique(),
                "median_qoi_ratio": est, "ci_lo": lo, "ci_hi": hi,
                "fraction_a_worse": float((per.qoi_ratio > 1).mean()),
                "median_linf_ratio": float(per.linf_ratio.median()),
            }
            match_rows.append(row)
            report.append(
                f"- tau={tau:g} e, {codec_a}/{codec_b}, <= {caliper:.3f} dex: "
                f"{len(mm)} pairs / {per.material_id.nunique()} materials; QoI ratio **{est:.2f}x** "
                f"[{lo:.2f}, {hi:.2f}], A worse in {100*row['fraction_a_worse']:.1f}%; "
                f"median L∞ ratio {row['median_linf_ratio']:.3f}."
            )
pd.DataFrame(match_rows).to_csv(OUT / "reviewer_matched_linf_sensitivity_failure_free.csv", index=False)
report.append("")

# 3. Interpolation on common within-material realized-Linf support
report += ["## 3. Within-material log-log interpolation on common realized-Linf support", ""]
interp_rows = []
for tau, ecol in [(1e-4, "eligible_A1_at_0.0001"), (1e-3, "eligible_A1_at_0.001"), (1e-2, "eligible_A1_at_0.01")]:
    elig = master[eligible_mask(master, ecol)].copy()
    for codec_a, codec_b in [("SZ3", "ZFP"), ("SPERR", "ZFP")]:
        ip = interpolate_pairwise(elig, codec_a, codec_b, max_nominal=0.01)
        if ip.empty:
            continue
        est, lo, hi = bootstrap_median(ip.qoi_ratio_a_over_b)
        row = {
            "tau_e": tau, "codec_a": codec_a, "codec_b": codec_b,
            "n_materials": len(ip), "median_qoi_ratio": est,
            "ci_lo": lo, "ci_hi": hi,
            "fraction_a_worse": float((ip.qoi_ratio_a_over_b > 1).mean()),
        }
        interp_rows.append(row)
        report.append(
            f"- tau={tau:g} e, {codec_a}/{codec_b}: {len(ip)} materials; "
            f"interpolated QoI ratio **{est:.2f}x** [{lo:.2f}, {hi:.2f}], "
            f"A worse in {100*row['fraction_a_worse']:.1f}%."
        )
pd.DataFrame(interp_rows).to_csv(OUT / "reviewer_common_support_interpolation.csv", index=False)
report.append("")

# 4. Mechanism attenuation
report += ["## 4. Mechanism attenuation after adding basin-reassignment and fixed-basin terms", ""]
try:
    import statsmodels.formula.api as smf

    g = master[
        eligible_mask(master, "eligible_A1_at_0.001")
        & (master.nominal_tolerance_relative <= 0.01)
        & (master.realized_Linf > 0)
        & master.Bader_error_resolved_e.notna()
    ].copy()
    ranges = g.groupby("codec")["realized_Linf"].agg(["min", "max"])
    common_lo = float(ranges["min"].max())
    common_hi = float(ranges["max"].min())
    g = g[g.realized_Linf.between(common_lo, common_hi)].copy()
    g["logQ"] = np.log10(np.clip(g.Bader_error_resolved_e.astype(float), 1e-15, None))
    g["logL"] = np.log10(g.realized_Linf.astype(float))
    g["logL_c"] = g.logL - g.logL.median()
    pseudo = 0.5 / np.clip(g.npoints.astype(float), 1, None)
    g["logReassign"] = np.log10(np.clip(g.frac_voxels_reassigned.astype(float), 0, None) + pseudo)
    g["logFixed"] = np.log10(np.clip(g.Bader_error_fixed_e.astype(float), 1e-15, None))

    formulas = {
        "M0_Linf_codec_material": "logQ ~ logL_c + C(codec, Treatment(reference='ZFP')) + C(material_id)",
        "M1_plus_reassignment": "logQ ~ logL_c + logReassign + C(codec, Treatment(reference='ZFP')) + C(material_id)",
        "M2_plus_reassignment_fixed": "logQ ~ logL_c + logReassign + logFixed + C(codec, Treatment(reference='ZFP')) + C(material_id)",
    }
    coef_rows = []
    for name, formula in formulas.items():
        fit = smf.ols(formula, data=g).fit(cov_type="cluster", cov_kwds={"groups": g.material_id})
        for codec in ["SZ3", "SPERR"]:
            term = f"C(codec, Treatment(reference='ZFP'))[T.{codec}]"
            beta = float(fit.params[term]); se = float(fit.bse[term]); p = float(fit.pvalues[term])
            coef_rows.append({
                "model": name, "codec": codec, "beta_log10": beta,
                "multiplicative": 10**beta,
                "ci_lo": 10**(beta - 1.96*se), "ci_hi": 10**(beta + 1.96*se),
                "p": p, "n_rows": len(g), "n_materials": g.material_id.nunique(),
                "common_linf_lo": common_lo, "common_linf_hi": common_hi,
            })
        if "logReassign" in fit.params:
            beta = float(fit.params["logReassign"]); se = float(fit.bse["logReassign"])
            report.append(
                f"- {name}: reassignment coefficient beta={beta:.3f} log10-Q per log10 reassigned-fraction "
                f"[95% {beta-1.96*se:.3f}, {beta+1.96*se:.3f}]."
            )
    cdf = pd.DataFrame(coef_rows)
    cdf.to_csv(OUT / "reviewer_codec_effect_mechanism_attenuation.csv", index=False)
    report.append(f"- Regression common realized-L∞ support: [{common_lo:.3g}, {common_hi:.3g}], {len(g)} rows / {g.material_id.nunique()} materials.")
    for codec in ["SZ3", "SPERR"]:
        sub = cdf[cdf.codec == codec].set_index("model")
        m0 = sub.loc["M0_Linf_codec_material", "multiplicative"]
        m1 = sub.loc["M1_plus_reassignment", "multiplicative"]
        m2 = sub.loc["M2_plus_reassignment_fixed", "multiplicative"]
        report.append(f"- {codec}/ZFP codec effect: M0 **{m0:.2f}x** -> +reassignment **{m1:.2f}x** -> +reassignment+fixed-basin **{m2:.2f}x**.")
except Exception as e:
    report.append(f"Mechanism regression unavailable: {type(e).__name__}: {e}")
report.append("")

# 5. Fixed-basin directionality
report += ["## 5. Fixed-basin metric directionality", ""]
base = master[master.ladder == "base"].copy()
valid = base[base.Bader_error_resolved_e.notna() & base.Bader_error_fixed_e.notna()].copy()
report.append(
    f"- Among {len(valid)} successful base-ladder rows, resolved error exceeds fixed-basin error in "
    f"**{100*(valid.Bader_error_resolved_e > valid.Bader_error_fixed_e).mean():.1f}%** of rows."
)
for codec, gg in valid.groupby("codec"):
    ratio = (
        np.clip(gg.Bader_error_resolved_e.astype(float), 1e-15, None)
        / np.clip(gg.Bader_error_fixed_e.astype(float), 1e-15, None)
    )
    est, lo, hi = bootstrap_median(ratio)
    report.append(
        f"- {codec}: median resolved/fixed ratio **{est:.1f}x** [{lo:.1f}, {hi:.1f}], "
        f"resolved > fixed in {100*(gg.Bader_error_resolved_e > gg.Bader_error_fixed_e).mean():.1f}%."
    )

(OUT / "reviewer_stress_tests.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
