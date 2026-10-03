"""Supplementary Figure S10 -- a certifying writer reproduces the stability-qualified frontier at a fraction of
the exhaustive cost.

Strip of three, 183 x 66 mm, from the frozen WP-E policy evaluation (no new computation) and the WP-H
sequential-QSQ cost integration:
  a  cost against retained archive compression for every writer policy at the three contracts; the
     adoption rule (>= 0.98 of the oracle, <= 2 % misses at 1e-3 e) is the shaded band, the adopted
     policy (BISECT at 1e-3 e) the one red point          WP-E/policy_summary.csv
  b  mean end-to-end Bader solves per material at 1e-3 e over all 254 materials, from exhaustive
     evaluation to bisection with exact sequential QSQ  WP-E/policy_summary.csv, WP-H/writer_cost_impact.csv
  c  per eligible material: compression ratio returned by the writer over the oracle ratio; every
     material below 1 is drawn, the materials at exactly 1 are counted   WP-E/policy_material.csv

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS10.py   -> FigS10.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import advanced as AD  # noqa: E402
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (CODEC_DARK, DARK_B, DARK_G, INK, MID, OTHER, RED, TINT_G, Page, grid, open_frame,  # noqa: E402
                   thr_label)

WPE = ("analysis", "extensions_20260930", "WP-E")
S = D.csv(*WPE, "policy_summary.csv")
M = D.csv(*WPE, "policy_material.csv")
H = D.csv("analysis", "extensions_20261001", "WP-H", "writer_cost_impact.csv")
TAU = (1e-4, 1e-3, 1e-2)


def row(tau, pol):
    r = S[np.isclose(S.tau_e, tau) & (S.policy == pol)]
    assert len(r) == 1, (tau, pol)
    return r.iloc[0]


b3 = row(1e-3, "BISECT")
assert abs(b3.fraction_of_oracle - 0.98476) < 1e-4 and b3.miss_count == 0 and abs(b3.mean_solves_eligible - 16.664) < 1e-3
assert abs(row(1e-3, "EXHAUSTIVE").mean_solves_eligible - 37.042) < 1e-3
h3 = H[np.isclose(H.tau_e, 1e-3)].iloc[0]
assert abs(h3.writer_mean_solves_all_original - 12.0039) < 1e-3 and abs(h3.writer_mean_solves_all_optimized - 10.3386) < 1e-3

pg = Page(183.0, 66.0)
MARK = {1e-4: "o", 1e-3: "s", 1e-2: "^"}

# ---- a: cost against retained archive compression -----------------------------------------------------
pg.letter("a", 2.0, 65.0)
ax = pg.ax(14.0, 12.0, 50.0, 44.0)
ax.axhspan(0.98, 1.02, color=TINT_G, zorder=0, lw=0)
ax.text(44.0, 0.968, "adoption: \u2265 0.98 of oracle", fontsize=5.4, color=DARK_G, ha="right", va="top")
fam = {"EXHAUSTIVE": OTHER, "SCAN": DARK_G, "BISECT": DARK_B}
for t in TAU:
    for pol, col in fam.items():
        r = row(t, pol)
        hl = (pol == "BISECT" and t == 1e-3)
        ax.scatter([r.mean_solves_eligible], [r.fraction_of_oracle], marker=MARK[t], s=26 if hl else 16,
                   c=RED if hl else col, edgecolors="white", linewidths=0.4, zorder=5 if hl else 4)
    for pol in ("BISECT-ZFP", "BISECT-SZ3", "BISECT-SPERR"):
        r = row(t, pol)
        cdc = pol.split("-")[1]
        ax.scatter([r.mean_solves_eligible], [r.fraction_of_oracle], marker=MARK[t], s=14, facecolors="white",
                   edgecolors=CODEC_DARK[cdc], linewidths=0.7, zorder=3)
ax.set_xlim(5, 42); ax.set_ylim(0.0, 1.06)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(["0", "25", "50", "75", "100%"])
ax.set_xlabel("Bader solves per eligible material")
ax.set_ylabel("archive compression, share of oracle")
open_frame(ax); grid(ax)
ax.annotate("", xy=(b3.mean_solves_eligible, b3.fraction_of_oracle), xytext=(21.0, 0.66),
            arrowprops=dict(arrowstyle="-", color=RED, lw=0.5, shrinkA=0, shrinkB=3))
ax.text(21.0, 0.62, "BISECT, $10^{-3}$ e\n98.5% at 16.7 solves", fontsize=5.6, color=RED, ha="left", va="center")
h = [Line2D([], [], ls="none", marker="o", color=c, ms=3.4, label=p.lower() if p != "BISECT" else "bisection")
     for p, c in fam.items()]
h += [Line2D([], [], ls="none", marker="o", mfc="white", mec=MID, ms=3.4, label="single codec")]
h += [Line2D([], [], ls="none", marker=MARK[t], color=INK, ms=3.0, label=thr_label(t)) for t in TAU]
layout.legend(ax, handles=h, labels=[x.get_label() for x in h], loc="lower right", ncol=2, fontsize=5.0)
# multi-codec policies sit in the top band and single-codec ones between 0.16 and 0.96 at 9-16 solves,
# so the lower-right quarter (few solves are never that low, shares never that small) is empty

# ---- b: end-to-end cost at the primary contract --------------------------------------------------------
pg.letter("b", 70.0, 65.0)
ax = pg.ax(82.0, 12.0, 44.0, 44.0)
ex, sc, bi = (row(1e-3, p).mean_solves_all for p in ("EXHAUSTIVE", "SCAN", "BISECT"))
assert abs(bi - h3.writer_mean_solves_all_original) < 1e-9
seq = h3.writer_mean_solves_all_optimized
AD.waterfall(ax, ["scan", "bisect", "sequential\nQSQ"], [sc - ex, bi - sc, seq - bi], start=ex,
             start_label="exhaustive", total_label="writer", fmt="%+.1f", highlight=None)
ax.set_ylabel(r"Bader solves per material at $10^{-3}$ e")
ax.set_ylim(0, 27)
ax.tick_params(axis="x", labelsize=5.8)
ax.text(0.0, 1.03, "mean over all 254 development materials", transform=ax.transAxes, fontsize=5.4, color=MID,
        ha="left", va="bottom")

# ---- c: per-material shortfall --------------------------------------------------------------------------
pg.letter("c", 132.0, 65.0)
ax = pg.ax(146.0, 12.0, 35.0, 44.0)
b = M[(M.policy == "BISECT") & D.truthy(M.eligible) & D.truthy(M.oracle_exists)].copy()
b["r"] = b.returned_cr / b.oracle_cr
for yrow, t in zip((2, 1, 0), TAU):
    x = b[np.isclose(b.tau_e, t)].r.to_numpy()
    at1 = x >= 1 - 1e-9
    low = x[~at1]
    off = AD.swarm(low, 0.03, 0.12, max_off=0.3)
    ax.scatter(low, yrow + off, s=10, c=RED if t == 1e-3 else DARK_B, linewidths=0, zorder=4)
    ax.scatter([1.0], [yrow], s=34, marker="s", c=DARK_G, linewidths=0, zorder=4)
    ax.text(0.97, yrow + 0.33, "%d / %d at 1" % (at1.sum(), len(x)), fontsize=5.4, ha="right", va="center")
ax.set_xlim(0.15, 1.06); ax.set_ylim(-0.6, 2.7)
ax.set_xticks([0.25, 0.5, 0.75, 1.0])
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([thr_label(t) for t in TAU])
ax.set_xlabel("writer / oracle ratio")
open_frame(ax); grid(ax, "x")

layout.audit(pg.fig)
pg.save(HERE, "FigS10")
