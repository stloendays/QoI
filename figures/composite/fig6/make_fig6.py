"""Figure 6 -- equal nominal codec tolerance conflates realized distortion magnitude with error structure.

2x2, 183 x 118 mm:
  a  equal nominal tolerance is not equal realized L-inf             equal_nominal_diagnostics.csv
  b  Bader-error ratio after within-material L-inf matching, by caliper   matched_effects_summary.csv
  c  compression-ratio effect on the same matches
  d  certification-rate difference at tau = 0.01 e among jointly eligible pairs

The one red is the primary 0.10-dex caliper marker. Pair colours: ZFP/SZ3 blue, ZFP/SPERR pale blue,
SZ3/SPERR green (the null comparison).

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig6.py   -> Fig6.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import BLUE, DARK_B, GREEN, INK, MID, OTHER, PALE, RED, Page, grid, open_frame  # noqa: E402

eff = D.matched_effects()
base = D.equal_nominal()
PAIRS = (("zfp_vs_sz3", "ZFP / SZ3", DARK_B), ("zfp_vs_sperr", "ZFP / SPERR", BLUE), ("sz3_vs_sperr", "SZ3 / SPERR", GREEN))
CAL = (0.05, 0.10, 0.20, 0.30)
res = eff[eff.metric == "Bader_error_resolved_e"]
comp = eff[eff.metric == "compression_ratio"]
cert = eff[eff.metric == "certified_at_0.01 | both eligible_A1_at_0.01=TRUE"]
r10 = res[res.caliper_dex == 0.10].set_index("pair").effect
assert abs(r10["zfp_vs_sz3"] - 0.557) < 0.001 and abs(r10["zfp_vs_sperr"] - 0.601) < 0.001 and abs(r10["sz3_vs_sperr"] - 1.033) < 0.001

pg = Page(183.0, 118.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 40.0
TOP, BOT = 68.0, 12.0


def caliper_panel(ax, tab, ylabel, ylog=False, ref=1.0, scale=1.0):
    ax.axhline(ref, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
    ax.axvline(0.10, color=RED, lw=0.6, ls=(0, (2, 2)), zorder=1)
    for key, lab, col in PAIRS:
        t = tab[tab.pair == key].sort_values("caliper_dex")
        ax.errorbar(t.caliper_dex, t.effect * scale, yerr=[(t.effect - t.ci_low) * scale, (t.ci_high - t.effect) * scale],
                    color=col, lw=0.9, capsize=1.6, capthick=0.6, elinewidth=0.6, marker="o", ms=3.2, zorder=3)
    ax.set_xticks(CAL); ax.set_xticklabels(["0.05", "0.10", "0.20", "0.30"])
    ax.set_xlim(0.02, 0.33)
    ax.set_xlabel(r"matching caliper (dex in $\log_{10}$ realized $L_\infty$)")
    ax.set_ylabel(ylabel)
    if ylog:
        ax.set_yscale("log")
    open_frame(ax); grid(ax, "y")
    ax.text(0.10, 1.0, " primary", transform=ax.get_xaxis_transform(), fontsize=5.2, color=RED, ha="left", va="top")


# ---- a: equal nominal -> unequal realized L-inf ---------------------------------------------------
pg.letter("a", 2.0, 117.0)
ax = pg.ax(LX + 10.0, TOP, PW - 10.0, PH)
ax.axvline(1, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
for y, (key, lab, col) in zip((2, 1, 0), PAIRS):
    r = base[base.pair == key].iloc[0]
    v = r.median_realized_Linf_ratio_A_over_B
    ax.plot([v, 1], [y, y], color=OTHER, lw=1.4, zorder=2, solid_capstyle="round")
    ax.scatter([v], [y], s=28, c=col, zorder=4, linewidths=0)
    ax.text(v, y + 0.28, "%.2f\u00d7  (n = %s pairs)" % (v, format(int(r.n_pairs), ",")), ha="left" if v < 0.5 else "right",
            va="bottom", fontsize=5.6, color=INK)
ax.set_xscale("log"); ax.set_xlim(0.12, 1.5)
ax.set_xticks([0.15, 0.2, 0.3, 0.5, 1.0]); ax.set_xticklabels(["0.15", "0.2", "0.3", "0.5", "1"])
ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([p[1] for p in PAIRS]); ax.set_ylim(-0.6, 2.8)
ax.set_xlabel(r"median realized $L_\infty$ ratio, A / B, at equal nominal tolerance")
open_frame(ax); grid(ax, "x")
ax.text(0.0, 1.02, "254 development materials, all shared nominal settings", transform=ax.transAxes, fontsize=5.4,
        color=MID, va="bottom")

# ---- b: Bader-error ratio after matching --------------------------------------------------------------
pg.letter("b", 94.0, 117.0)
ax = pg.ax(RX, TOP, PW, PH)
caliper_panel(ax, res, "re-derived Bader-error ratio, A / B")
ax.set_ylim(0.45, 1.15); ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1])
handles = [Line2D([], [], marker="o", color=c, ms=3.2, lw=0.9, label=l) for _, l, c in PAIRS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="center right")
# right-centre is empty: the three series sit at 0.56-0.60 and at 1.03, leaving 0.7-0.95 clear
ax.text(0.98, 0.02, "material-level ratios; 95% material-bootstrap CI", transform=ax.transAxes, fontsize=5.2,
        color=MID, ha="right", va="bottom")

# ---- c: compression-ratio effect --------------------------------------------------------------------
pg.letter("c", 2.0, 61.0)
ax = pg.ax(LX, BOT, PW, PH)
caliper_panel(ax, comp, "compression-ratio effect, A / B", ylog=True)
ax.set_ylim(0.22, 4.6); ax.set_yticks([0.25, 0.5, 1, 2, 4]); ax.set_yticklabels(["0.25", "0.5", "1", "2", "4"])
ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())

# ---- d: certification-rate difference at 0.01 e --------------------------------------------------------
pg.letter("d", 94.0, 61.0)
ax = pg.ax(RX, BOT, PW, PH)
caliper_panel(ax, cert, "certification-rate difference,\nA \u2212 B (percentage points)", ref=0.0, scale=100.0)
ax.set_ylim(-6, 34); ax.set_yticks([0, 10, 20, 30])
ax.text(0.98, 0.96, r"$\tau = 10^{-2}$ e; jointly QSQ-eligible pairs", transform=ax.transAxes, fontsize=5.4, color=MID,
        ha="right", va="top")

layout.audit(pg.fig)
pg.save(HERE, "Fig6")
