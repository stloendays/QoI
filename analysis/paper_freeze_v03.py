from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_data_v03"
OUT.mkdir(exist_ok=True)

master = pd.read_csv(ROOT / "benchmark/master_benchmark_full.csv")
base = master[master["ladder"].astype(str).str.lower() == "base"].copy()
elig = pd.read_csv(ROOT / "stability/eligibility_summary_A1.csv")
best = pd.read_csv(ROOT / "benchmark/best_certified_a1.csv")
fails = pd.read_csv(ROOT / "failure_registry.csv")
complete = pd.read_csv(ROOT / "analysis_output/complete_case_failure_sensitivity.csv")
atten = pd.read_csv(ROOT / "analysis_output/complete_case_mechanism_attenuation.csv")
fixed_core = pd.read_csv(ROOT / "analysis_output/fixed_basin_core_tolerance_summary.csv")
fixed_a1 = pd.read_csv(ROOT / "analysis_output/fixed_basin_A1_qualified_summary.csv")

rows: list[dict] = []

def add(section, metric, value, unit="", lo=np.nan, hi=np.nan, n=np.nan, denominator="", source=""):
    rows.append({
        "section": section,
        "metric": metric,
        "value": value,
        "unit": unit,
        "ci_lo": lo,
        "ci_hi": hi,
        "n": n,
        "denominator": denominator,
        "source": source,
    })

# Scope and integrity.
add("scope", "successful_master_rows", len(master), " rows", n=len(master), denominator="successful reconstructions", source="benchmark/master_benchmark_full.csv")
add("scope", "development_materials", master.material_id.nunique(), " materials", n=master.material_id.nunique(), denominator="development benchmark", source="benchmark/master_benchmark_full.csv")
add("scope", "base_ladder_rows", len(base), " rows", n=len(base), denominator="successful base-ladder reconstructions", source="benchmark/master_benchmark_full.csv")
add("scope", "registered_exceptions", len(fails), " rows", n=len(fails), denominator="failure registry", source="failure_registry.csv")

# Fixed versus re-derived Bader metric.
valid = base[base.Bader_error_resolved_e.notna() & base.Bader_error_fixed_e.notna()].copy()
frac_gt = float((valid.Bader_error_resolved_e > valid.Bader_error_fixed_e).mean())
ratio = valid.Bader_error_resolved_e.astype(float) / valid.Bader_error_fixed_e.astype(float)
add("fixed_vs_resolved", "resolved_greater_than_fixed_fraction", frac_gt, " fraction", n=len(valid), denominator="successful base-ladder rows", source="benchmark/master_benchmark_full.csv")
add("fixed_vs_resolved", "pooled_median_resolved_over_fixed", float(np.median(ratio)), "x", n=len(valid), denominator="successful base-ladder rows; paired row ratio", source="benchmark/master_benchmark_full.csv")
fixed_core.to_csv(OUT / "fig2_fixed_vs_resolved_core_tolerances.csv", index=False)
fixed_a1.to_csv(OUT / "fig2_fixed_vs_resolved_A1_qualified.csv", index=False)

# Bound utilization.
bu = (
    master.groupby("codec", as_index=False)["realized_Linf_over_nominal"]
    .agg(median="median", q25=lambda s: s.quantile(.25), q75=lambda s: s.quantile(.75), q05=lambda s: s.quantile(.05), q95=lambda s: s.quantile(.95), n="count")
)
bu.to_csv(OUT / "fig5_bound_utilization.csv", index=False)
for _, r in bu.iterrows():
    add("bound_utilization", f"{str(r.codec).upper()}_median_realized_over_nominal", float(r["median"]), " ratio", n=int(r.n), denominator="all successful master rows for codec", source="benchmark/master_benchmark_full.csv")

# Conservative complete-case matched result at the central 1e-3 e contract.
cc_primary = complete[(complete.method == "0.10dex_mutual_nearest") & np.isclose(complete.tau_e, 1e-3)].copy()
cc_primary.to_csv(OUT / "fig5_complete_case_primary_tau1e-3.csv", index=False)
for _, r in cc_primary.iterrows():
    add(
        "matched_realized_linf_complete_case",
        f"{r.codec_a}_over_{r.codec_b}_tau1e-3_0.10dex",
        float(r.median_qoi_ratio), "x", float(r.ci_lo), float(r.ci_hi), int(r.n_materials),
        "A1-eligible complete-case materials; nominal relative tolerance <=0.01",
        "analysis_output/complete_case_failure_sensitivity.csv",
    )

# Complete-case mechanism attenuation.
atten.to_csv(OUT / "fig3_complete_case_mechanism_attenuation.csv", index=False)
for _, r in atten.iterrows():
    add(
        "mechanism_attenuation",
        f"{str(r.codec)}_{str(r.model)}_codec_multiplier",
        float(r.effect), "x", float(r.ci_lo), float(r.ci_hi),
        denominator="complete-case A1 tau=1e-3 model",
        source="analysis_output/complete_case_mechanism_attenuation.csv",
    )
# Reassignment slope is recorded in the complete-case report, generated from the same model set.
add("mechanism_attenuation", "reassignment_loglog_slope", 0.880, " beta", 0.723, 1.037, denominator="complete-case A1 tau=1e-3 model", source="analysis_output/complete_case_failure_sensitivity.md")
add("mechanism_attenuation", "reassignment_p_value", 5.78e-28, " p", denominator="complete-case A1 tau=1e-3 model", source="analysis_output/complete_case_failure_sensitivity.md")

# QoI resolvability.
elig.to_csv(OUT / "fig4_resolvability_summary.csv", index=False)
for tau in [1e-4, 1e-3, 1e-2]:
    r = elig[(np.isclose(elig.threshold_e, tau)) & (elig.stratum == "overall")].iloc[0]
    add("resolvability", f"non_evaluable_fraction_tau_{tau:g}", float(r.frac_non_evaluable_a1), " fraction", n=int(r.n), denominator="319-system stability corpus", source="stability/eligibility_summary_A1.csv")

# Symmetry-aware sensitivity: one known external-bulk case is a symmetry-equivalent basin permutation.
sym_mid = "aflow-Al8Cu4U1_ICSD_601801"
sym_mask = fails.material_id.astype(str).eq(sym_mid) & fails.category.astype(str).eq("basin_relabelling_symmetry_equivalent")
assert sym_mask.any(), "Known symmetry-equivalent relabelling registry row not found"
sa = []
for tau in [1e-4, 1e-3, 1e-2]:
    r = elig[(np.isclose(elig.threshold_e, tau)) & (elig.stratum == "overall")].iloc[0]
    n2 = int(r.n) - 1
    ne2 = int(r.non_evaluable) - 1
    f2 = ne2 / n2
    sa.append({
        "threshold_e": tau,
        "primary_n": int(r.n),
        "primary_non_evaluable": int(r.non_evaluable),
        "primary_frac_non_evaluable": float(r.frac_non_evaluable_a1),
        "symmetry_aware_n": n2,
        "symmetry_aware_non_evaluable": ne2,
        "symmetry_aware_frac_non_evaluable": f2,
        "absolute_fraction_change": f2 - float(r.frac_non_evaluable_a1),
    })
    add("symmetry_sensitivity", f"symmetry_aware_non_evaluable_fraction_tau_{tau:g}", f2, " fraction", n=n2, denominator="stability corpus after removing known symmetry-equivalent relabelling case", source="paper_data_v03/fig4_symmetry_aware_resolvability_sensitivity.csv")
pd.DataFrame(sa).to_csv(OUT / "fig4_symmetry_aware_resolvability_sensitivity.csv", index=False)

# Certified compression frontier.
best["codec"] = best.codec.astype(str).str.upper()
front = []
for (tau, domain, codec), g in best.groupby(["threshold_e", "domain", "codec"], dropna=False):
    cert = g[g.status.astype(str).eq("CERTIFIED")]
    noncert = g[~g.status.astype(str).eq("CERTIFIED")]
    ratios = cert.ratio.dropna().astype(float)
    row = {
        "threshold_e": tau,
        "domain": domain,
        "codec": codec,
        "n_rows": len(g),
        "n_certified": len(cert),
        "n_not_certified": len(noncert),
        "certification_fraction_among_rows": len(cert) / len(g) if len(g) else np.nan,
        "median_best_certified_ratio": float(ratios.median()) if len(ratios) else np.nan,
        "q25_best_certified_ratio": float(ratios.quantile(.25)) if len(ratios) else np.nan,
        "q75_best_certified_ratio": float(ratios.quantile(.75)) if len(ratios) else np.nan,
    }
    front.append(row)
    add("certified_frontier", f"{codec}_{domain}_tau_{tau:g}_median_best_ratio", row["median_best_certified_ratio"], "x", n=len(g), denominator="Protocol-A1 admitted best-certified table", source="benchmark/best_certified_a1.csv")
    add("certified_frontier", f"{codec}_{domain}_tau_{tau:g}_coverage", row["certification_fraction_among_rows"], " fraction", n=len(g), denominator="Protocol-A1 admitted best-certified table", source="benchmark/best_certified_a1.csv")
front = pd.DataFrame(front).sort_values(["threshold_e", "domain", "codec"])
front.to_csv(OUT / "fig6_certified_compression_frontier.csv", index=False)

# Headline registry.
reg = pd.DataFrame(rows)
reg.to_csv(OUT / "HEADLINE_NUMBER_REGISTRY_v03.csv", index=False)

lines = [
    "# Headline number registry v0.3",
    "",
    "Machine-generated by `analysis/paper_freeze_v03.py`. Use this file as the single source for manuscript headline numbers. Values outside this registry may be used only when their aggregation is explicitly stated.",
    "",
]
for section, g in reg.groupby("section", sort=False):
    lines += [f"## {section}", ""]
    for _, r in g.iterrows():
        ci = ""
        if pd.notna(r.ci_lo) and pd.notna(r.ci_hi):
            ci = f" [{r.ci_lo:.4g}, {r.ci_hi:.4g}]"
        n = f"; n={int(r.n)}" if pd.notna(r.n) else ""
        lines.append(f"- `{r.metric}` = **{r.value:.6g}{r.unit}**{ci}{n}. Denominator: {r.denominator}. Source: `{r.source}`.")
    lines.append("")

lines += [
    "## editorial rules",
    "",
    "- Treat same-nominal codec gaps as a mixture of bound utilization and residual structure.",
    "- Use the complete-case matched analysis as the most conservative reviewer-facing sensitivity, while retaining the preregistered A.1-qualified all-successful analysis as the primary protocol result.",
    "- Describe reassignment regression as attenuation/mediation-consistent evidence, not causal mediation.",
    "- Describe the stability floor as protocol-defined/probe-defined.",
    "- Keep the symmetry-equivalent relabelling sensitivity separate from the frozen Protocol A.1 primary numbers.",
]
(OUT / "HEADLINE_NUMBER_REGISTRY_v03.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Wrote", len(reg), "headline registry rows to", OUT)
print(front.to_string(index=False))
