"""NC Figure 3 -- under equal search, the closed-form operator law certifies an order of magnitude more than
pointwise codecs and beats spectral truncation, on fresh bulk crystals and fresh surface slabs.

183 x 66 mm:
  a  tau = 1e-6 Hartree certificate: per material, best equal-search ZFP/SZ3/SPERR CR (A6) vs closed-form law CR (A1);
     60 bulk (P1, circles) and 32 slab (P3b, triangles); iso-ratio lines 1x and 10x.
  b  the same against spectral truncation with equal search (A2); iso-ratio line 1x.
  c  median ratios A1/A6 and A1/A2 with bootstrap 95% CIs at tau = 1e-4, 1e-6, 1e-8, per cohort.
All medians are asserted against run_P1_CONFIRMATORY/SUMMARY.json and run_P3B_CONFIRMATORY/SUMMARY.json.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig3.py   -> Fig3.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common as C  # noqa: E402
import layout  # noqa: E402
from style import BLUE, DARK_B, DARK_G, GREEN, INK, MID, Page, grid, log_ticks, note  # noqa: E402

D = C.part_a()
S = C.summaries()
for coh in ("bulk", "slab"):
    for tau in C.TAUS:
        C.check_median(D, "A1", "A6", coh, tau, S, "A1_over_A6")
        C.check_median(D, "A1", "A2", coh, tau, S, "A1_over_A2")

pg = Page(183.0, 66.0)
MK = {"bulk": dict(marker="o", s=8), "slab": dict(marker="^", s=9)}


def pair(ax, den, col, lines):
    t = D[np.isclose(D.tau, 1e-6)]
    lo, hi = 5.0, 5000.0
    xs = np.array([lo, hi])
    for k in lines:
        ax.plot(xs, xs * k, color=MID if k != 1 else INK, lw=0.5, ls="-" if k == 1 else (0, (3, 2)), zorder=1)
        ax.text(hi / 1.15 / (k if k > 1 else 1) * (1 if k == 1 else 1), hi / 1.15 if k > 1 else hi / 1.6,
                "%g×" % k, fontsize=5.3, color=MID, ha="right", va="top")
    for coh in ("bulk", "slab"):
        s = t[t.cohort == coh]
        if coh == "bulk":
            ax.scatter(s[den], s.A1, color=col, edgecolor="white", lw=0.25, zorder=3, **MK[coh])
        else:
            ax.scatter(s[den], s.A1, facecolor="none", edgecolor=col, lw=0.55, zorder=3, **MK[coh])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    log_ticks(ax)
    grid(ax)
    ax.set_ylabel("Closed-form law CR (A1)")


pg.letter("a", 2.0, 65.0)
axa = pg.ax(13.0, 10.0, 48.0, 48.0)
pair(axa, "A6", DARK_B, (1, 10))
axa.set_xlabel("Best pointwise codec CR (A6)")
r1, r3 = S["bulk"]["part_A"]["tau_1e-06"]["A1_over_A6"], S["slab"]["part_A"]["tau_1e-06"]["A1_over_A6"]
note(axa, 0.04, 0.96, "$\\tau$ = 10$^{-6}$\nbulk: %.1f× (%d/%d)\nslab: %.1f× (%d/%d)" %
     (r1["median"], r1["wins"], r1["n"], r3["median"], r3["wins"], r3["n"]), size=5.3)

pg.letter("b", 64.0, 65.0)
axb = pg.ax(75.0, 10.0, 48.0, 48.0)
pair(axb, "A2", DARK_G, (1,))
axb.set_xlabel("Spectral truncation CR (A2)")
r1, r3 = S["bulk"]["part_A"]["tau_1e-06"]["A1_over_A2"], S["slab"]["part_A"]["tau_1e-06"]["A1_over_A2"]
note(axb, 0.04, 0.96, "$\\tau$ = 10$^{-6}$\nbulk: %.2f× (%d/%d)\nslab: %.2f× (%d/%d)" %
     (r1["median"], r1["wins"], r1["n"], r3["median"], r3["wins"], r3["n"]), size=5.3)

# ---- c: medians and CIs across tolerances ----------------------------------------------------------
pg.letter("c", 126.0, 65.0)
axc = pg.ax(137.0, 10.0, 43.0, 48.0)
X = {1e-4: 0, 1e-6: 1, 1e-8: 2}
for key, col, off in (("A1_over_A6", DARK_B, 0.0), ("A1_over_A2", DARK_G, 0.0)):
    for coh, dx, mk in (("bulk", -0.09, "o"), ("slab", 0.09, "^")):
        xs, ys, lo, hi = [], [], [], []
        for tau in C.TAUS:
            v = S[coh]["part_A"][C.TAU_KEY[tau]][key]
            xs.append(X[tau] + dx)
            ys.append(v["median"])
            lo.append(v["median"] - v["ci95"][0])
            hi.append(v["ci95"][1] - v["median"])
        axc.errorbar(xs, ys, yerr=[lo, hi], color=col, lw=0.6, elinewidth=0.6, capsize=1.2, marker=mk, ms=3.2,
                     mfc=col if coh == "bulk" else "white", mec=col, zorder=3)
axc.axhline(1.0, color=INK, lw=0.5, zorder=1)
axc.set_yscale("log")
axc.set_ylim(0.5, 200)
axc.set_xlim(-0.5, 2.5)
axc.set_xticks([0, 1, 2])
axc.set_xticklabels([C.TAU_LAB[t] for t in C.TAUS])
axc.set_xlabel("Hartree tolerance $\\tau$")
axc.set_ylabel("Median CR ratio")
log_ticks(axc, axis="y")
grid(axc, axis="y")
hand = [Line2D([], [], color=DARK_B, lw=0.8, label="law / pointwise (A1/A6)"),
        Line2D([], [], color=DARK_G, lw=0.8, label="law / truncation (A1/A2)"),
        Line2D([], [], ls="", marker="o", ms=3.2, color=MID, label="bulk (60)"),
        Line2D([], [], ls="", marker="^", ms=3.4, mfc="white", mec=MID, label="slab (32)")]
axc.legend(handles=hand, loc="upper center", fontsize=5.0, handletextpad=0.3, columnspacing=0.8, frameon=False, ncol=2)  # all data < 25, legend sits above

layout.audit(pg.fig)
pg.save(HERE, "Fig3")
