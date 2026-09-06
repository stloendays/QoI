"""Figure 6 draft: Pointwise error is not chemical error.

Scientific-content draft. Final typography/layout will be redesigned after the
full manuscript figure set is assembled.
"""
import matplotlib.pyplot as plt
import numpy as np

TOL = np.array([1e-4, 1e-3, 1e-2])
SZ3_OVER_ZFP = np.array([6.4, 9.2, 12.4])

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.linewidth": .8, "pdf.fonttype": 42,
                     "svg.fonttype": "none"})

fig = plt.figure(figsize=(9.2, 4.0), facecolor="#FAFAF8")
gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1], wspace=.34)
ax = fig.add_subplot(gs[0, 0], facecolor="#FAFAF8")
ax2 = fig.add_subplot(gs[0, 1], facecolor="#FAFAF8")
x = np.arange(3)

bars = ax.bar(x, SZ3_OVER_ZFP, width=.58, color="#0072B2",
              edgecolor="#003366", linewidth=.8)
for b, r in zip(bars, SZ3_OVER_ZFP):
    ax.text(b.get_x()+b.get_width()/2, r+.35, f"{r:.1f}×",
            ha="center", fontsize=11, fontweight="bold", color="#003366")
ax.axhline(1, color="#B3B3B3", lw=1.1, ls="--")
ax.set_xticks(x, [r"$10^{-4}$", r"$10^{-3}$", r"$10^{-2}$"])
ax.set_xlabel("Matched nominal tolerance")
ax.set_ylabel("SZ3 / ZFP Bader-error ratio")
ax.set_ylim(0, 14.2)
ax.set_title("Pointwise-equivalent bounds do not imply\nchemical-equivalent errors",
             loc="left", fontsize=11.5, fontweight="bold")

# Only the frozen 98–100% range is a headline result at this stage.
ax2.fill_between([-.35, 2.35], 98, 100, color="#FDDBC7", alpha=.95)
ax2.text(1, 97.3, "98–100% across matched tolerances", ha="center",
         fontsize=9.5, fontweight="bold", color="#D55E00")
ax2.set_xticks(x, [r"$10^{-4}$", r"$10^{-3}$", r"$10^{-2}$"])
ax2.set_xlabel("Matched nominal tolerance")
ax2.set_ylabel("Materials where SZ3 error > ZFP error (%)")
ax2.set_ylim(90, 101)
ax2.set_title("The codec ordering is systematic", loc="left",
              fontsize=11.5, fontweight="bold")

for a in (ax, ax2):
    a.spines[["top", "right"]].set_visible(False)
    a.grid(axis="y", color="#B3B3B3", alpha=.22, lw=.6)
    a.set_axisbelow(True)

fig.suptitle("Figure 6 | Pointwise error is not chemical error",
             x=.07, y=1.04, ha="left", fontsize=13.5, fontweight="bold")
fig.savefig("figure6_pointwise_vs_chemical.svg", bbox_inches="tight")
fig.savefig("figure6_pointwise_vs_chemical.pdf", bbox_inches="tight")
fig.savefig("figure6_pointwise_vs_chemical.png", dpi=400, bbox_inches="tight")
