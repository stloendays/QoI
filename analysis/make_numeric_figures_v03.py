from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures_v03"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 10,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def save(fig, stem):
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.png", dpi=400, bbox_inches="tight")
    plt.close(fig)


# ---------------- Figure 2 ----------------
master = pd.read_csv(ROOT / "benchmark/master_benchmark_full.csv")
base = master[master.ladder.astype(str).eq("base")].copy()
core = pd.read_csv(ROOT / "paper_data_v03/fig2_fixed_vs_resolved_core_tolerances.csv")

fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.35))
ax = axes[0]
for codec, g in base.groupby("codec"):
    x = g.Bader_error_fixed_e.astype(float)
    y = g.Bader_error_resolved_e.astype(float)
    keep = (x > 0) & (y > 0) & np.isfinite(x) & np.isfinite(y)
    ax.scatter(x[keep], y[keep], s=7, alpha=0.25, label=str(codec))
lo = min(base.Bader_error_fixed_e[base.Bader_error_fixed_e > 0].min(), base.Bader_error_resolved_e[base.Bader_error_resolved_e > 0].min())
hi = max(base.Bader_error_fixed_e.max(), base.Bader_error_resolved_e.max())
ax.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Fixed-basin Bader error (e)")
ax.set_ylabel("Re-derived Bader error (e)")
ax.set_title("a  Re-deriving the partition exposes error", loc="left")
ax.legend(frameon=False)

ax = axes[1]
for codec, g in core.groupby("codec"):
    g = g.sort_values("relative_tolerance")
    yerr = np.vstack([g.median_row_ratio - g.ci_lo, g.ci_hi - g.median_row_ratio])
    ax.errorbar(g.relative_tolerance, g.median_row_ratio, yerr=yerr, marker="o", capsize=2, label=str(codec))
ax.axhline(1, linestyle="--", linewidth=1)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Nominal relative tolerance")
ax.set_ylabel("Median resolved / fixed error")
ax.set_title("b  Understatement varies by codec and tolerance", loc="left")
ax.legend(frameon=False)

ax = axes[2]
for codec, g in core.groupby("codec"):
    g = g.sort_values("relative_tolerance")
    ax.plot(g.relative_tolerance, 100 * g.fraction_resolved_gt_fixed, marker="o", label=str(codec))
ax.set_xscale("log")
ax.set_ylim(85, 100.5)
ax.set_xlabel("Nominal relative tolerance")
ax.set_ylabel("Cases with resolved > fixed (%)")
ax.set_title("c  Direction is overwhelmingly consistent", loc="left")
ax.legend(frameon=False)
fig.tight_layout()
save(fig, "Figure2_fixed_vs_resolved_draft")


# ---------------- Figure 4 ----------------
elig = pd.read_csv(ROOT / "stability/eligibility_summary_A1.csv")
cal = pd.read_csv(ROOT / "stability/probe_calibration.csv")
pred = pd.read_csv(ROOT / "analysis_output/resolvability_predictability.csv")

fig, axes = plt.subplots(2, 2, figsize=(8.3, 6.6))
ax = axes[0, 0]
for stratum, g in elig.groupby("stratum"):
    g = g.sort_values("threshold_e")
    ax.plot(g.threshold_e, 100 * g.frac_non_evaluable_a1, marker="o", label=stratum)
ax.set_xscale("log")
ax.set_xlabel("Bader contract, tau (e)")
ax.set_ylabel("Non-evaluable systems (%)")
ax.set_title("a  QoI resolvability is contract-dependent", loc="left")
ax.legend(frameon=False, ncol=2)

# Paired floor comparison: archived float32 vs maximum five-seed random-noise at matched amplitude.
f32 = cal[(cal.seed.astype(str) == "float32") & np.isclose(cal.amplitude_factor, 1.0)][["material_id", "floor_e"]].rename(columns={"floor_e":"floor_float32"})
noise = cal[(cal.seed.astype(str) != "float32") & np.isclose(cal.amplitude_factor, 1.0)].groupby("material_id", as_index=False).floor_e.max().rename(columns={"floor_e":"floor_noise_max"})
pair = f32.merge(noise, on="material_id", how="inner")
ax = axes[0, 1]
ax.scatter(pair.floor_float32, pair.floor_noise_max, s=24)
lo = min(pair.floor_float32[pair.floor_float32 > 0].min(), pair.floor_noise_max[pair.floor_noise_max > 0].min())
hi = max(pair.floor_float32.max(), pair.floor_noise_max.max())
ax.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Float32-probe floor (e)")
ax.set_ylabel("Five-seed noise floor (e)")
ax.set_title("b  A monotone probe can look falsely benign", loc="left")

# Algorithmic structure: exact ties and reassigned voxels for float32 versus primary random seed.
float_rows = cal[(cal.seed.astype(str) == "float32") & np.isclose(cal.amplitude_factor, 1.0)].copy()
noise_rows = cal[(cal.seed.astype(str) == "20260905") & np.isclose(cal.amplitude_factor, 1.0)].copy()
ax = axes[1, 0]
x = np.arange(2)
tie_meds = [float_rows.n_exact_neighbour_ties_created.median(), noise_rows.n_exact_neighbour_ties_created.median()]
re_meds = [float_rows.n_voxels_reassigned.median(), noise_rows.n_voxels_reassigned.median()]
width = 0.34
ax.bar(x - width/2, tie_meds, width, label="Exact neighbour ties")
ax.bar(x + width/2, re_meds, width, label="Reassigned voxels")
ax.set_xticks(x, ["float32", "random noise"])
ax.set_ylabel("Median count in 18-material calibration")
ax.set_title("c  The probes perturb different structures", loc="left")
ax.legend(frameon=False)

ax = axes[1, 1]
p = pred[pred.sensitivity == "all"].sort_values("tau_e")
ax.errorbar(p.tau_e, p.cv_auc_mean, yerr=p.cv_auc_sd, marker="o", capsize=2, label="Development 5-fold CV")
ax.plot(p.tau_e, p.external_auc, marker="o", label="Untouched external")
ax.axhline(0.5, linestyle="--", linewidth=1)
ax.set_xscale("log")
ax.set_ylim(0.25, 0.8)
ax.set_xlabel("Bader contract, tau (e)")
ax.set_ylabel("AUROC")
ax.set_title("d  Cheap descriptors do not transfer", loc="left")
ax.legend(frameon=False)
fig.tight_layout()
save(fig, "Figure4_resolvability_probe_draft")


# ---------------- Figure 5 ----------------
bu = pd.read_csv(ROOT / "paper_data_v03/fig5_bound_utilization.csv")
cc = pd.read_csv(ROOT / "analysis_output/complete_case_failure_sensitivity.csv")
atten = pd.read_csv(ROOT / "paper_data_v03/fig3_complete_case_mechanism_attenuation.csv")

fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.45))
ax = axes[0]
order = ["ZFP", "SZ3", "SPERR"]
for i, codec in enumerate(order):
    g = master[master.codec.astype(str).str.upper() == codec]
    vals = g.realized_Linf_over_nominal.to_numpy(float)
    ax.boxplot(vals, positions=[i], widths=0.55, showfliers=False)
ax.set_xticks(range(len(order)), order)
ax.set_yscale("log")
ax.set_ylabel("Realized L-inf / nominal bound")
ax.set_title("a  Codecs use the nominal budget differently", loc="left")

ax = axes[1]
primary = cc[(cc.method == "0.10dex_mutual_nearest") & np.isclose(cc.tau_e, 1e-3)].copy()
labels = [f"{a}/{b}" for a,b in zip(primary.codec_a, primary.codec_b)]
x = np.arange(len(primary))
y = primary.median_qoi_ratio.to_numpy(float)
yerr = np.vstack([y - primary.ci_lo.to_numpy(float), primary.ci_hi.to_numpy(float) - y])
ax.errorbar(x, y, yerr=yerr, fmt="o", capsize=3)
ax.axhline(1, linestyle="--", linewidth=1)
ax.set_xticks(x, labels)
ax.set_ylabel("Matched Bader-error ratio")
ax.set_title("b  ~2x residual at matched realized L-inf", loc="left")
ax.text(0.02, 0.03, "A.1 tau=1e-3 e\ncomplete-case; 0.10 dex", transform=ax.transAxes, va="bottom")

ax = axes[2]
for i, codec in enumerate(["SZ3", "SPERR"]):
    g = atten[atten.codec == codec].set_index("model")
    vals = [g.loc["M0", "effect"], g.loc["M1", "effect"]]
    errs_lo = [vals[0] - g.loc["M0", "ci_lo"], vals[1] - g.loc["M1", "ci_lo"]]
    errs_hi = [g.loc["M0", "ci_hi"] - vals[0], g.loc["M1", "ci_hi"] - vals[1]]
    pos = np.array([0, 1]) + (i - 0.5) * 0.12
    ax.errorbar(pos, vals, yerr=np.vstack([errs_lo, errs_hi]), marker="o", capsize=2, label=f"{codec}/ZFP")
ax.axhline(1, linestyle="--", linewidth=1)
ax.set_xticks([0,1], ["L-inf + material FE", "+ basin reassignment"])
ax.set_ylabel("Codec multiplier")
ax.set_title("c  Reassignment absorbs the residual", loc="left")
ax.legend(frameon=False)
fig.tight_layout()
save(fig, "Figure5_magnitude_structure_draft")


# ---------------- Figure 6 ----------------
front = pd.read_csv(ROOT / "paper_data_v03/fig6_certified_compression_frontier.csv")
fig, axes = plt.subplots(1, 2, figsize=(8.3, 3.6), sharey=True)
for ax, domain in zip(axes, ["bulk", "slab"]):
    d = front[front.domain == domain].copy()
    for codec, g in d.groupby("codec"):
        g = g.sort_values("threshold_e")
        ax.plot(100 * g.certification_fraction_among_rows, g.median_best_certified_ratio, marker="o", label=codec)
        for _, r in g.iterrows():
            ax.annotate(f"{r.threshold_e:g}", (100*r.certification_fraction_among_rows, r.median_best_certified_ratio), xytext=(3,3), textcoords="offset points", fontsize=7)
    ax.set_xlabel("Certification coverage among admitted rows (%)")
    ax.set_title(f"{domain.capitalize()} systems", loc="left")
    ax.grid(False)
axes[0].set_ylabel("Median best certified compression ratio")
axes[1].legend(frameon=False)
fig.suptitle("Certified compression is a contract-dependent Pareto problem", y=1.02, fontsize=11)
fig.tight_layout()
save(fig, "Figure6_certified_frontier_draft")

print("Wrote numeric figure drafts to", OUT)
