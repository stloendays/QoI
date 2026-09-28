"""Supplementary Figure S6 -- realized-distortion matching conclusions are robust to the caliper choice.

183 x 58 mm strip of three, all from supplement/S12_matching_sensitivity.csv:
  a  re-derived Bader-error ratio vs caliper with 95% material-bootstrap band
  b  materials in common support vs caliper
  c  median and P95 larger/smaller realized L-inf ratio among matched pairs

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS6.py   -> FigS6.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import BLUE, DARK_B, GREEN, MID, OTHER, RED, Page, grid, open_frame  # noqa: E402

d = D.supp("S12_matching_sensitivity.csv")
assert len(d) == 12
PAIRS = (("ZFP/SZ3", "ZFP / SZ3", DARK_B), ("ZFP/SPERR", "ZFP / SPERR", BLUE), ("SZ3/SPERR", "SZ3 / SPERR", GREEN))
pri = d[d.caliper_dex == 0.10].set_index("pair_label")
assert abs(pri.loc["ZFP/SZ3", "resolved_bader_ratio"] - 0.5574478963397762) < 1e-10 and pri.loc["ZFP/SZ3", "n_pairs"] == 457
CAL = (0.05, 0.10, 0.20, 0.30)

pg = Page(183.0, 58.0)


def frame(ax, ylabel):
    ax.axvline(0.10, color=RED, lw=0.6, ls=(0, (2, 2)), zorder=1)
    ax.text(0.10, 1.0, " primary", transform=ax.get_xaxis_transform(), fontsize=5.2, color=RED, va="top")
    ax.set_xticks(CAL); ax.set_xticklabels(["0.05", "0.10", "0.20", "0.30"]); ax.set_xlim(0.02, 0.33)
    ax.set_xlabel("matching caliper (dex)")
    ax.set_ylabel(ylabel)
    open_frame(ax); grid(ax, "y")


# ---- a ---------------------------------------------------------------------------------------
pg.letter("a", 2.0, 57.0)
ax = pg.ax(14.0, 12.0, 46.0, 38.0)
ax.axhline(1, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
for key, lab, col in PAIRS:
    t = d[d.pair_label == key].sort_values("caliper_dex")
    ax.fill_between(t.caliper_dex, t.resolved_ci_low, t.resolved_ci_high, color=col, alpha=0.15, lw=0, zorder=2)
    ax.plot(t.caliper_dex, t.resolved_bader_ratio, color=col, lw=0.9, marker="o", ms=3, zorder=3)
frame(ax, "re-derived Bader-error ratio, A / B")
ax.set_ylim(0.45, 1.15)
handles = [Line2D([], [], marker="o", color=c, ms=3, lw=0.9, label=l) for _, l, c in PAIRS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="center right")

# ---- b ---------------------------------------------------------------------------------------
pg.letter("b", 64.0, 57.0)
ax = pg.ax(76.0, 12.0, 46.0, 38.0)
for key, lab, col in PAIRS:
    t = d[d.pair_label == key].sort_values("caliper_dex")
    ax.plot(t.caliper_dex, t.n_materials, color=col, lw=0.9, marker="o", ms=3, zorder=3)
frame(ax, "materials in common support")
ax.set_ylim(90, 270)
ax.text(0.97, 0.03, "SZ3 / SPERR: 254 throughout", transform=ax.transAxes, fontsize=5.2, color=MID, ha="right", va="bottom")

# ---- c ---------------------------------------------------------------------------------------
pg.letter("c", 126.0, 57.0)
ax = pg.ax(138.0, 12.0, 42.0, 38.0)
ax.axhline(1, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
for key, lab, col in PAIRS:
    t = d[d.pair_label == key].sort_values("caliper_dex")
    ax.fill_between(t.caliper_dex, t.median_linf_ratio_larger_over_smaller, t.p95_linf_ratio_larger_over_smaller, color=col,
                    alpha=0.15, lw=0, zorder=2)
    ax.plot(t.caliper_dex, t.median_linf_ratio_larger_over_smaller, color=col, lw=0.9, marker="o", ms=3, zorder=3)
frame(ax, r"larger / smaller realized $L_\infty$")
ax.set_ylim(0.95, 2.1)
ax.text(0.97, 0.97, "line = median,\nband to P95", transform=ax.transAxes, fontsize=5.2, color=MID, va="top", ha="right")

layout.audit(pg.fig)
pg.save(HERE, "FigS6")
