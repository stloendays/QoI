from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_data_v03"
OUT.mkdir(exist_ok=True)

master = pd.read_csv(ROOT / "benchmark/master_benchmark_full.csv")
fails = pd.read_csv(ROOT / "failure_registry.csv")
master["codec"] = master.codec.astype(str).str.upper()
fails["codec"] = fails.codec.astype(str).str.upper()
fails["nominal_tolerance_relative"] = pd.to_numeric(fails.nominal_tolerance_relative, errors="coerce")

# Exact same conservative complete-case material set used in the reviewer stress test.
bad_materials = set(
    fails.loc[
        fails.nominal_tolerance_relative.notna()
        & (fails.nominal_tolerance_relative <= 0.01),
        "material_id",
    ].astype(str)
)

g = master[
    ~master.material_id.astype(str).isin(bad_materials)
    & master["eligible_A1_at_0.001"].fillna(False).astype(bool)
    & (master.nominal_tolerance_relative <= 0.01)
    & (master.realized_Linf > 0)
    & master.Bader_error_resolved_e.notna()
].copy()

# Restrict to common realized-Linf support across all three codecs.
support = []
for codec in ["ZFP", "SZ3", "SPERR"]:
    x = g.loc[g.codec == codec, "realized_Linf"].astype(float)
    support.append((x.min(), x.max()))
lo = max(x[0] for x in support)
hi = min(x[1] for x in support)
g = g[(g.realized_Linf >= lo) & (g.realized_Linf <= hi)].copy()

# Transformations. The primary outcome and L-inf transformation match the existing attenuation analysis.
g["logQ"] = np.log10(np.clip(g.Bader_error_resolved_e.astype(float), 1e-15, None))
g["logL"] = np.log10(g.realized_Linf.astype(float))
g["logL_c"] = g.logL - g.logL.median()

# Global electron-count deviation can be exactly zero for some rows, so use a data-defined
# half-minimum-positive pseudocount rather than an arbitrary scientific threshold.
epos = g.loc[g.electron_count_abs_dev.astype(float) > 0, "electron_count_abs_dev"].astype(float)
e_pseudo = 0.5 * float(epos.min()) if len(epos) else 1e-18
g["logElectronDev"] = np.log10(g.electron_count_abs_dev.astype(float) + e_pseudo)

# Keep reassignment transform identical in spirit to the prior mechanism model: half a voxel
# divided by grid size prevents zero reassignment from becoming -inf.
re_pseudo = 0.5 / np.clip(g.npoints.astype(float), 1, None)
g["logReassign"] = np.log10(np.clip(g.frac_voxels_reassigned.astype(float), 0, None) + re_pseudo)

formulas = {
    "M0_Linf_codec_material": "logQ ~ logL_c + C(codec, Treatment(reference='ZFP')) + C(material_id)",
    "M_electron": "logQ ~ logL_c + logElectronDev + C(codec, Treatment(reference='ZFP')) + C(material_id)",
    "M_reassign": "logQ ~ logL_c + logReassign + C(codec, Treatment(reference='ZFP')) + C(material_id)",
    "M_both": "logQ ~ logL_c + logElectronDev + logReassign + C(codec, Treatment(reference='ZFP')) + C(material_id)",
}

coef_rows = []
model_rows = []
for name, formula in formulas.items():
    fit = smf.ols(formula, data=g).fit(cov_type="cluster", cov_kwds={"groups": g.material_id})
    for codec in ["SZ3", "SPERR"]:
        term = f"C(codec, Treatment(reference='ZFP'))[T.{codec}]"
        beta = float(fit.params[term]); se = float(fit.bse[term]); p = float(fit.pvalues[term])
        coef_rows.append({
            "model": name,
            "term": f"{codec}/ZFP",
            "beta_log10": beta,
            "effect": 10**beta,
            "ci_lo": 10**(beta - 1.96*se),
            "ci_hi": 10**(beta + 1.96*se),
            "p": p,
        })
    for term in ["logElectronDev", "logReassign"]:
        if term in fit.params:
            beta = float(fit.params[term]); se = float(fit.bse[term]); p = float(fit.pvalues[term])
            coef_rows.append({
                "model": name,
                "term": term,
                "beta_log10": beta,
                "effect": np.nan,
                "ci_lo": beta - 1.96*se,
                "ci_hi": beta + 1.96*se,
                "p": p,
            })
    model_rows.append({
        "model": name,
        "n_rows": len(g),
        "n_materials": g.material_id.nunique(),
        "r2": float(fit.rsquared),
        "adj_r2": float(fit.rsquared_adj),
    })

coef = pd.DataFrame(coef_rows)
models = pd.DataFrame(model_rows)
coef.to_csv(OUT / "global_conservation_negative_control_coefficients.csv", index=False)
models.to_csv(OUT / "global_conservation_negative_control_models.csv", index=False)

# Descriptive rank correlations after material centering, to avoid simple between-material scale confounding.
for col in ["logQ", "logL", "logElectronDev", "logReassign"]:
    g[f"within_{col}"] = g[col] - g.groupby("material_id")[col].transform("mean")
corr = g[["within_logQ", "within_logL", "within_logElectronDev", "within_logReassign"]].corr(method="spearman")
corr.to_csv(OUT / "global_conservation_negative_control_within_material_spearman.csv")

# Human-readable report.
def codec_effect(model, codec):
    return coef[(coef.model == model) & (coef.term == f"{codec}/ZFP")].iloc[0]

def scalar(model, term):
    return coef[(coef.model == model) & (coef.term == term)].iloc[0]

lines = [
    "# Global electron-count deviation negative control",
    "",
    "Question: can the approximately twofold codec-associated Bader-error residual be explained by global electron-count/integral deviation rather than Bader-domain migration?",
    "",
    f"Analysis set: Protocol-A.1 eligible at 1e-3 e; nominal relative tolerance <=0.01; conservative complete-case exclusion of {len(bad_materials)} failure-affected materials; common realized-Linf support [{lo:.6g}, {hi:.6g}].",
    f"Rows/materials: {len(g)} / {g.material_id.nunique()}. Electron-deviation pseudocount = half the minimum positive observed value = {e_pseudo:.3e}.",
    "",
    "## Codec coefficients",
    "",
]
for codec in ["SZ3", "SPERR"]:
    for model in formulas:
        r = codec_effect(model, codec)
        lines.append(f"- {codec}/ZFP, {model}: **{r.effect:.2f}x** [{r.ci_lo:.2f},{r.ci_hi:.2f}], p={r.p:.3g}.")
    lines.append("")

lines += ["## Covariate coefficients", ""]
for model, term in [("M_electron", "logElectronDev"), ("M_reassign", "logReassign"), ("M_both", "logElectronDev"), ("M_both", "logReassign")]:
    r = scalar(model, term)
    lines.append(f"- {model}, {term}: beta={r.beta_log10:.3f} [{r.ci_lo:.3f},{r.ci_hi:.3f}], p={r.p:.3g}.")

lines += [
    "",
    "## Interpretation rule",
    "",
    "- If adding global electron-count deviation leaves codec multipliers near the M0 values while reassignment collapses them toward 1, global conservation error is not a plausible explanation of the codec-associated residual.",
    "- If electron-count deviation itself strongly attenuates the codec coefficient, the manuscript must describe global integral bias as an additional mechanism and avoid attributing the residual mainly to basin migration.",
    "- The model is an observational negative control and must not be described as causal mediation.",
    "",
    "## Within-material Spearman matrix",
    "",
    corr.to_markdown(),
]
(OUT / "global_conservation_negative_control.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
