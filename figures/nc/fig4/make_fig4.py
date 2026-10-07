"""NC Figure 4 -- the operator metric carries the gain; the optimizer's added share is set by the system class.

183 x 68 mm:
  a  per material, CR of the operational optimum in the operator metric (A3) over the operational optimum in the blind
     L2 metric (A5), both certified for the same Hartree contract; bulk (60) and slab (32) at tau = 1e-4, 1e-6, 1e-8.
  b  per material, operational optimum (A3) over the closed-form law with continuous search (A1); the dashed line is
     the pre-registered near-optimality threshold 1.15 (A-H1).
Medians (bars) and bootstrap 95% CIs (whiskers) are read from the committed SUMMARY.json files and asserted against the
per-material tables.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig4.py   -> Fig4.{svg,pdf,png}
"""
import os
import sys

import matplotlib.ticker
import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common as C  # noqa: E402
import layout  # noqa: E402
from style import DARK_B, GREEN, INK, MID, Page, grid, log_ticks  # noqa: E402

D = C.part_a()
S = C.summaries()
COL = {"bulk": DARK_B, "slab": GREEN}
pg = Page(183.0, 68.0)
rng = np.random.default_rng(7)


def strips(ax, num, den, key, ylim):
    for i, tau in enumerate(C.TAUS):
        for coh, dx in (("bulk", -0.18), ("slab", 0.18)):
            r, v = C.check_median(D, num, den, coh, tau, S, key)
            x = i + dx + rng.uniform(-0.07, 0.07, r.size)
            if coh == "bulk":
                ax.scatter(x, r, s=5, color=COL[coh], edgecolor="white", lw=0.2, alpha=0.85, zorder=2)
            else:
                ax.scatter(x, r, s=6, marker="^", facecolor="none", edgecolor=COL[coh], lw=0.45, zorder=2)
            ax.plot([i + dx - 0.12, i + dx + 0.12], [v["median"]] * 2, color=INK, lw=1.0, zorder=4)
            ax.plot([i + dx] * 2, v["ci95"], color=INK, lw=0.6, zorder=4)
    ax.set_yscale("log")
    ax.set_ylim(*ylim)
    ax.set_xlim(-0.5, 2.5)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([C.TAU_LAB[t] for t in C.TAUS])
    ax.set_xlabel("Hartree tolerance $\\tau$")
    ax.axhline(1.0, color=INK, lw=0.5, zorder=1)
    log_ticks(ax, axis="y")
    grid(ax, axis="y")


pg.letter("a", 2.0, 67.0)
axa = pg.ax(14.0, 15.0, 72.0, 46.0)
strips(axa, "A3", "A5", "A3_over_A5", (0.8, 12))
axa.set_ylabel("Operator metric / blind metric\n(both optimal; CR ratio A3/A5)")
axa.set_yticks([1, 2, 5, 10])
axa.set_yticklabels(["1", "2", "5", "10"])
axa.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
for i, tau in enumerate(C.TAUS):
    for coh, dx in (("bulk", -0.18), ("slab", 0.18)):
        m = S[coh]["part_A"][C.TAU_KEY[tau]]["A3_over_A5"]["median"]
        axa.text(i + dx, 9.2, "%.2f" % m, fontsize=5.3, ha="center", va="center", color=COL[coh])

pg.letter("b", 94.0, 67.0)
axb = pg.ax(106.0, 15.0, 72.0, 46.0)
strips(axb, "A3", "A1", "A3_over_A1", (0.9, 4.5))
axb.axhline(1.15, color=MID, lw=0.6, ls=(0, (3, 2)), zorder=1)
axb.text(2.45, 1.16, "1.15", fontsize=5.3, color=MID, ha="right", va="bottom")
axb.set_ylabel("Operational optimum / closed-form law\n(CR ratio A3/A1)")
axb.set_yticks([1, 1.5, 2, 3, 4])
axb.set_yticklabels(["1", "1.5", "2", "3", "4"])
axb.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
for i, tau in enumerate(C.TAUS):
    for coh, dx in (("bulk", -0.18), ("slab", 0.18)):
        m = S[coh]["part_A"][C.TAU_KEY[tau]]["A3_over_A1"]["median"]
        axb.text(i + dx, 3.9, "%.3f" % m, fontsize=5.3, ha="center", va="center", color=COL[coh])

hand = [Line2D([], [], ls="", marker="o", ms=3.0, color=COL["bulk"], label="bulk crystals (P1, 60)"),
        Line2D([], [], ls="", marker="^", ms=3.2, mfc="none", mec=COL["slab"], mew=0.6, label="surface slabs (P3b, 32)"),
        Line2D([], [], color=INK, lw=1.0, label="median, 95% CI")]
leg = pg.ax(14.0, 0.3, 164.0, 4.5)
leg.axis("off")
leg.legend(handles=hand, loc="center", ncol=3, fontsize=5.3, frameon=False, columnspacing=1.2)

layout.audit(pg.fig)
pg.save(HERE, "Fig4")
