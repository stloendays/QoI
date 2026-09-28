"""Figure 3 -- QSQ prospectively stratifies downstream numerical risk after equalizing search opportunity.

Strip of three, 183 x 62 mm:
  a  the frozen screen splits 254 materials into 143 eligible / 111 rejected, with the fresh-trial
     exceedance risk of each (P2, primary threshold)          p2_fresh_probe_cohort_summary.csv
  b  no-pass risk after completing the same tight ladder for every material (P1)
                                                              p1_common_tight_summary.csv
  c  fresh exceedance risk at all three thresholds with material-cluster CIs (P2)

The one red is the screen-rejected cohort. Frozen anchors are asserted before drawing.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig3.py   -> Fig3.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (ELIGIBLE, INK, LINE, MID, OTHER, REJECTED, TINT_B, TINT_R, Page, grid, open_frame,  # noqa: E402
                   thr_label)

p1 = D.p1_common_tight().sort_values("tau_e").reset_index(drop=True)
p2 = D.p2_fresh_probes()
assert list(p1.n_decisions) == [762, 762, 762]
assert p2.groupby("tau_e").planned_trials.sum().eq(14986).all()
pe = p2[(p2.tau_e == 1e-3) & (p2.gate_group == "eligible")].iloc[0]
pr = p2[(p2.tau_e == 1e-3) & (p2.gate_group == "screen_rejected")].iloc[0]
assert (pe.n_materials, pr.n_materials, pe.exceedance_events, pr.exceedance_events) == (143, 111, 135, 5326)
rr_primary = pr.valid_trial_exceedance_fraction / pe.valid_trial_exceedance_fraction
assert abs(rr_primary - 50.83) < 0.01, rr_primary

pg = Page(183.0, 62.0)

# ---- a: the split, drawn -------------------------------------------------------------------------
pg.letter("a", 2.0, 61.0)
cv = pg.canvas(3.0, 6.0, 56.0, 50.0)


def box(x, y, w, h, fill, edge):
    cv.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0",
                                facecolor=fill, edgecolor=edge, linewidth=0.7, zorder=2))


box(0.5, 18.0, 17.0, 14.0, "white", OTHER)
cv.text(9.0, 29.2, "QSQ screen", ha="center", va="center", fontsize=6.4, fontweight="bold")
cv.text(9.0, 25.0, "5 fixed seeds", ha="center", va="center", fontsize=5.6, color=MID)
cv.text(9.0, 21.4, r"$\tau = 10^{-3}$ e", ha="center", va="center", fontsize=5.8, color=MID)
cv.text(9.0, 34.0, "254 development\nmaterials", ha="center", va="bottom", fontsize=5.6, color=INK, linespacing=1.1)
for (y0, y1) in ((28.0, 40.0), (22.0, 10.0)):
    cv.plot([17.5, 22.5], [y0, y1], color=OTHER, lw=0.7, zorder=1)

for (y, fill, edge, head, row, risk) in (
        (33.5, TINT_B, ELIGIBLE, "eligible   %d materials" % pe.n_materials, pe, pe),
        (3.5, TINT_R, REJECTED, "screen-rejected   %d materials" % pr.n_materials, pr, pr)):
    box(23.0, y, 33.0, 14.0, fill, edge)
    cv.text(24.8, y + 11.2, head, ha="left", va="center", fontsize=6.2, fontweight="bold", color=edge)
    cv.text(24.8, y + 7.3, "%s / %s fresh trials exceed $\\tau$" % (format(int(row.exceedance_events), ","),
                                                                    format(int(row.valid_trials), ",")),
            ha="left", va="center", fontsize=5.6, color=INK)
    cv.text(24.8, y + 3.2, "%.2f%%   [%.2f\u2013%.2f%%]" % (100 * risk.valid_trial_exceedance_fraction,
                                                            100 * risk.material_cluster_ci_low,
                                                            100 * risk.material_cluster_ci_high),
            ha="left", va="center", fontsize=6.4, fontweight="bold", color=edge)
cv.text(39.5, 25.5, "risk ratio %.2f" % rr_primary, ha="center", va="center", fontsize=6.0, color=INK,
        bbox=dict(boxstyle="square,pad=0.3", facecolor="white", edgecolor=LINE, linewidth=0.5))
cv.text(0.5, 0.0, "59 fresh iid-uniform perturbations per material", ha="left", va="bottom", fontsize=5.2, color=MID)

# ---- b: equal-search no-pass risk ------------------------------------------------------------------
pg.letter("b", 63.0, 61.0)
ax = pg.ax(75.0, 14.0, 44.0, 38.0)
ys = [2, 1, 0]
for y, (_, r) in zip(ys, p1.iterrows()):
    ax.plot([r.no_pass_risk_eligible, r.no_pass_risk_non_evaluable], [y, y], color=OTHER, lw=1.6, zorder=2,
            solid_capstyle="round")
    ax.scatter([r.no_pass_risk_eligible], [y], s=26, c=ELIGIBLE, zorder=4, linewidths=0)
    ax.scatter([r.no_pass_risk_non_evaluable], [y], s=26, c=REJECTED, zorder=4, linewidths=0)
    rr = r.risk_ratio_non_evaluable_vs_eligible
    lab = "\u221e" if not np.isfinite(rr) else "%.2f\u00d7" % rr
    ax.text(r.no_pass_risk_non_evaluable + 0.04, y, lab, ha="left", va="center", fontsize=6.0, fontweight="bold")
ax.set_yticks(ys); ax.set_yticklabels([thr_label(t) for t in p1.tau_e])
ax.set_ylim(-0.6, 2.6); ax.set_xlim(0, 1.0)
ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); ax.set_xticklabels(["0", "20", "40", "60", "80", "100%"])
ax.set_xlabel("material\u2013codec pairs with no numerical pass")
ax.set_ylabel(r"Bader threshold $\tau$")
open_frame(ax); grid(ax, "x")
ax.text(0.0, 1.02, "equal search: 1,332 / 1,332 added rows;\n762 decisions per $\\tau$",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=5.4, color=MID)

# ---- c: fresh exceedance risk with CIs -----------------------------------------------------------------
pg.letter("c", 125.0, 61.0)
ax = pg.ax(137.0, 14.0, 44.0, 38.0)
for y, tau in zip(ys, (1e-4, 1e-3, 1e-2)):
    e = p2[(p2.tau_e == tau) & (p2.gate_group == "eligible")].iloc[0]
    r = p2[(p2.tau_e == tau) & (p2.gate_group == "screen_rejected")].iloc[0]
    for (row, col, dy) in ((e, ELIGIBLE, 0.16), (r, REJECTED, -0.16)):
        ax.plot([row.material_cluster_ci_low, row.material_cluster_ci_high], [y + dy, y + dy], color=col, lw=0.8,
                zorder=3)
        ax.scatter([row.valid_trial_exceedance_fraction], [y + dy], s=26, c=col, zorder=4, linewidths=0)
    rr = r.valid_trial_exceedance_fraction / e.valid_trial_exceedance_fraction
    ax.text(r.material_cluster_ci_low - 0.03, y - 0.16, "%.2f\u00d7" % rr, ha="right", va="center", fontsize=6.0,
            fontweight="bold")
ax.set_yticks(ys); ax.set_yticklabels([thr_label(t) for t in (1e-4, 1e-3, 1e-2)])
ax.set_ylim(-0.6, 2.6); ax.set_xlim(0, 1.0)
ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); ax.set_xticklabels(["0", "20", "40", "60", "80", "100%"])
ax.set_xlabel("fresh-trial exceedance risk")
open_frame(ax); grid(ax, "x")
ax.text(0.0, 1.02, "14,986 fresh trials;\nintervals resample materials",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=5.4, color=MID)
handles = [__import__("matplotlib").lines.Line2D([], [], marker="o", ls="none", color=c, ms=4, label=l)
           for c, l in ((ELIGIBLE, "eligible"), (REJECTED, "screen-rejected"))]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="center", ncol=1, bbox_to_anchor=(0.32, 0.5))
# the middle of the panel is empty: eligible points hug 0, rejected points sit near 80-90 %

layout.audit(pg.fig)
pg.save(HERE, "Fig3")
