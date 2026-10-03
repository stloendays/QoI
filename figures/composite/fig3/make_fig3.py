"""Figure 3 -- the frozen QSQ screen prospectively stratifies downstream numerical risk.

183 x 120 mm, two rows:
  a  every development material: its frozen five-probe QSQ floor against the fraction of its 59 fresh
     perturbations whose Bader response reaches tau = 1e-3 e (P2). The risk steps up at the floor = tau
     line that defines eligibility.                     p2_fresh_probe_material_summary.csv
  b  the finite-panel admission bound: the joint probability p(1 - p)^5 that a contract is admitted and
     a later probe still exceeds tau, with every material placed at its fresh exceedance fraction;
     below, how many materials sit at each fraction. The ceiling 6.70 % is reached only at p = 1/6.
  c  equal-search control (P1): no-pass risk after completing the same tight ladder for every material
                                                        p1_common_tight_summary.csv
  d  fresh exceedance risk at the three pre-specified thresholds with material-cluster CIs (P2)
                                                        p2_fresh_probe_cohort_summary.csv
Eligible navy, screen-rejected red (one red per panel). Frozen anchors are asserted before drawing.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig3.py   -> Fig3.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (ELIGIBLE, INK, MID, OTHER, REJECTED, Page, grid, log_ticks, note, open_frame,  # noqa: E402
                   thr_label)

# ---- data and frozen anchors --------------------------------------------------------------------
p1 = D.p1_common_tight().sort_values("tau_e").reset_index(drop=True)
p2 = D.p2_fresh_probes()
mat = D.csv("analysis", "research_upgrade", "p2_fresh_probe_material_summary.csv")
assert list(p1.n_decisions) == [762, 762, 762]
assert p2.groupby("tau_e").planned_trials.sum().eq(14986).all()
pe = p2[(p2.tau_e == 1e-3) & (p2.gate_group == "eligible")].iloc[0]
pr = p2[(p2.tau_e == 1e-3) & (p2.gate_group == "screen_rejected")].iloc[0]
assert (pe.n_materials, pr.n_materials, pe.exceedance_events, pr.exceedance_events) == (143, 111, 135, 5326)
rr_primary = pr.valid_trial_exceedance_fraction / pe.valid_trial_exceedance_fraction
assert abs(rr_primary - 50.83) < 0.01, rr_primary

m3 = mat[np.isclose(mat.tau_e, 1e-3)].copy()
m3["elig"] = D.truthy(m3.original_qsq_eligible)
assert len(m3) == 254 and m3.elig.sum() == 143
assert ((m3.original_qsq_floor_e < 1e-3) == m3.elig).all()
assert m3.n_exceed.sum() == 135 + 5326 and m3.n_valid.sum() == 14986
phat = m3.valid_exceedance_fraction.to_numpy()
joint = (m3.n_exceed[m3.elig].sum()) / m3.n_valid.sum()
assert abs(joint - 0.00901) < 5e-5, joint
N = 5
CEIL = N ** N / (N + 1) ** (N + 1)
assert abs(CEIL - 0.0670) < 5e-5

pg = Page(183.0, 120.0)

# ---- a: floor versus fresh risk, one point per material ---------------------------------------------
pg.letter("a", 2.0, 119.0)
ax = pg.ax(14.0, 68.0, 84.0, 44.0)
x = m3.original_qsq_floor_e.to_numpy()
for sel, col, z in ((m3.elig.to_numpy(), ELIGIBLE, 4), (~m3.elig.to_numpy(), REJECTED, 3)):
    ax.scatter(x[sel], phat[sel], s=9, c=col, alpha=0.7, linewidths=0, zorder=z)
ax.axvline(1e-3, color=INK, lw=0.7, ls="dashed", zorder=2)
ax.set_xscale("log"); log_ticks(ax, "x")
ax.set_xlim(1e-8, 10.0); ax.set_ylim(-0.05, 1.05)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(["0", "25", "50", "75", "100%"])
ax.set_xlabel("frozen five-probe QSQ stability floor (e)")
ax.set_ylabel(r"fresh perturbations reaching $\tau$")
open_frame(ax); grid(ax)
ax.text(1e-3 / 1.3, 1.035, r"$\tau = 10^{-3}$ e", fontsize=5.6, color=INK, ha="right", va="top")
note(ax, 0.02, 0.86, "eligible  %d materials\n%s / %s fresh trials  (%.2f%%)"
     % (pe.n_materials, format(int(pe.exceedance_events), ","), format(int(pe.valid_trials), ","),
        100 * pe.valid_trial_exceedance_fraction), color=ELIGIBLE)
note(ax, 0.985, 0.34, "screen-rejected  %d materials\n%s / %s fresh trials  (%.2f%%)"
     % (pr.n_materials, format(int(pr.exceedance_events), ","), format(int(pr.valid_trials), ","),
        100 * pr.valid_trial_exceedance_fraction), color=REJECTED, ha="right")
ax.text(1e-3 / 1.25, 0.52, "risk ratio\n%.2f\u00d7" % rr_primary, fontsize=5.8, fontweight="bold", color=INK,
        ha="right", va="center")
# eligible points hug p = 0 left of the line and rejected points p = 1 right of it; the two notes sit in
# the upper-left and lower-right quadrants, which only the transition region reaches

# ---- b: the finite-panel admission bound -----------------------------------------------------------
pg.letter("b", 106.0, 119.0)
axb = pg.ax(118.0, 86.0, 63.0, 26.0)
pp = np.linspace(0, 1, 400)
axb.plot(pp, 100 * pp * (1 - pp) ** N, color=INK, lw=1.0, zorder=3)
axb.scatter(phat[m3.elig.to_numpy()], 100 * (phat * (1 - phat) ** N)[m3.elig.to_numpy()], s=8, c=ELIGIBLE,
            linewidths=0, alpha=0.8, zorder=5)
axb.scatter(phat[~m3.elig.to_numpy()], 100 * (phat * (1 - phat) ** N)[~m3.elig.to_numpy()], s=8, c=REJECTED,
            linewidths=0, alpha=0.8, zorder=4)
axb.plot([1 / (N + 1)] * 2, [0, 100 * CEIL], color=MID, lw=0.5, ls="dotted", zorder=2)
axb.text(1 / (N + 1) + 0.035, 100 * CEIL + 0.9, "ceiling %.2f%% at $p = 1/6$" % (100 * CEIL), fontsize=5.6, color=INK,
         ha="left", va="center")
axb.text(0.98, 0.42, "observed joint rate\n%.2f%% (135 / 14,986)" % (100 * joint), transform=axb.transAxes,
         fontsize=5.6, color=INK, ha="right", va="center")
axb.set_xlim(-0.02, 1.02); axb.set_ylim(0, 8.0)
axb.set_yticks([0, 2, 4, 6, 8]); axb.set_xticklabels([])
axb.set_ylabel(r"$p(1-p)^5$ (%)")
open_frame(axb); grid(axb)

axh = pg.ax(118.0, 68.0, 63.0, 15.0)
bins = np.linspace(0, 1, 21)
ce, _ = np.histogram(phat[m3.elig.to_numpy()], bins=bins)
cr, _ = np.histogram(phat[~m3.elig.to_numpy()], bins=bins)
mid, wid = (bins[:-1] + bins[1:]) / 2, 0.043
axh.bar(mid, ce, width=wid, color=ELIGIBLE, lw=0, zorder=3)
axh.bar(mid, cr, width=wid, bottom=ce, color=REJECTED, lw=0, zorder=3)
axh.set_yscale("log"); axh.set_ylim(0.8, 300)
axh.set_yticks([1, 10, 100]); axh.set_yticklabels(["1", "10", "100"])
axh.set_xlim(-0.02, 1.02)
axh.set_xticks([0, 0.25, 0.5, 0.75, 1.0]); axh.set_xticklabels(["0", "25", "50", "75", "100%"])
axh.set_xlabel(r"material fresh exceedance fraction $p$ at $10^{-3}$ e")
axh.set_ylabel("materials", labelpad=4.5)
open_frame(axh); grid(axh, "y")
n0, n1 = int((phat == 0).sum()), int((phat == 1).sum())
axh.text(0.035, 1.0, "%d at 0" % n0, transform=axh.transAxes, fontsize=5.4, ha="left", va="top", color=INK)
axh.text(0.965, 1.0, "%d at 1" % n1, transform=axh.transAxes, fontsize=5.4, ha="right", va="top", color=INK)

# ---- c: equal-search no-pass risk ------------------------------------------------------------------------
ys = [2, 1, 0]
pg.letter("c", 2.0, 57.0)
ax = pg.ax(26.0, 12.0, 62.0, 36.0)
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
ax.text(0.0, 1.03, "equal search: 1,332 / 1,332 added reconstructions; 762 decisions per $\\tau$",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=5.4, color=MID)

# ---- d: fresh exceedance risk with CIs -------------------------------------------------------------------
pg.letter("d", 106.0, 57.0)
ax = pg.ax(118.0, 12.0, 63.0, 36.0)
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
ax.text(0.0, 1.03, "14,986 fresh trials; intervals resample materials",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=5.4, color=MID)
handles = [Line2D([], [], marker="o", ls="none", color=c, ms=4, label=l)
           for c, l in ((ELIGIBLE, "eligible"), (REJECTED, "screen-rejected"))]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="center",
              bbox_to_anchor=(0.36, 0.5))
# the middle of the panel is empty: eligible points hug 0, rejected points sit near 80-90 %

layout.audit(pg.fig)
pg.save(HERE, "Fig3")
