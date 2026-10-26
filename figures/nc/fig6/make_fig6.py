"""NC Figure 6 -- the gain ladder: what the representation, the operator metric and the optimizer each contribute.

183 x 132 mm; fresh cohorts P1 (60 bulk crystals) and P3b (32 surface slabs); every stream decode-verified.
  a  per material (thin lines) and median (bold) certified CR at Hartree tolerance 1e-6 along the arm ladder
     A6 (best of ZFP/SZ3/SPERR) -> A5 (operational optimum, blind L2 metric) -> A1 (closed-form law) -> A3 (operational
     optimum, operator metric); the factor between rungs is the median per-material ratio (LADDER_STATS.json).
  b  A3/A5 (operator metric at equal optimization) per material at tau = 1e-4, 1e-6, 1e-8; median and bootstrap 95% CI.
  c  A3/A1 (the optimizer's share over the closed-form law); dashed line, pre-registered threshold 1.15.
  d  the writers: per material, certified CR at 1e-6 of A3 in the zlib container, the water-filling writer (W1S) and
     the predictive writer (W2S); factors are median per-material ratios (asserted against the two studies'
     SUMMARY.json). Right, whole-object reduction of the 8.50 TB Materials Project archive for every writer at 1e-6
     (filled) and 1e-4 (open) with paired-bootstrap 95% CIs (analysis/archive_w2_20261025/results/SUMMARY.json).
Medians and CIs are asserted against SUMMARY.json (b, c) or computed by ladder_stats.py with the aggregator bootstrap.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig6.py   -> Fig6.{svg,pdf,png}
"""
import json
import os
import sys

import matplotlib.ticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common as C  # noqa: E402
import layout  # noqa: E402
from style import INK, MID, Page, grid, log_ticks  # noqa: E402

D = C.part_a()
S = C.summaries()
L = json.load(open(os.path.join(HERE, "LADDER_STATS.json")))
RUNGS = ("A6", "A5", "A1", "A3")
TICK = {"A6": "pointwise\ncodecs", "A5": "blind\noptimum", "A1": "closed-\nform law", "A3": "operational\noptimum"}
STEP = ("transform\ncoding", "operator\nweight", "optimizer")
LINE_C = "#CDD0D5"
UP = 46.0                                   # rows a-c sit above the writer row d
pg = Page(183.0, 86.0 + UP)
rng = np.random.default_rng(7)

# ---- a: the ladder ------------------------------------------------------------------------------------------------
pg.letter("a", 2.0, 85.0 + UP)
for j, (coh, title, x0) in enumerate((("bulk", "Bulk crystals (60)", 14.0), ("slab", "Surface slabs (32)", 61.0))):
    ax = pg.ax(x0, 15.0 + UP, 42.0, 60.0)
    t = D[(D.cohort == coh) & np.isclose(D.tau, 1e-6)]
    xs = np.arange(4)
    for _, r in t.iterrows():
        ax.plot(xs, [r[a] for a in RUNGS], color=LINE_C, lw=0.3, zorder=1)
    for i, a in enumerate(RUNGS):
        jit = rng.uniform(-0.06, 0.06, len(t))
        if coh == "bulk":
            ax.scatter(i + jit, t[a], s=3.5, color=C.ARM[a], edgecolor="white", lw=0.15, zorder=2)
        else:
            ax.scatter(i + jit, t[a], s=4.5, marker="^", facecolor="none", edgecolor=C.ARM[a], lw=0.4, zorder=2)
    med = [L[coh]["tau_1e-06"]["median_cr"][a] for a in RUNGS]
    for i, a in enumerate(RUNGS):
        assert abs(med[i] - float(np.median(t[a]))) < 1e-9 * med[i]
    ax.plot(xs, med, color=INK, lw=1.0, zorder=4)
    ax.scatter(xs, med, s=16, color=[C.ARM[a] for a in RUNGS], edgecolor=INK, lw=0.6, zorder=5,
               marker="o" if coh == "bulk" else "^")
    for i, (num, den) in enumerate((("A5", "A6"), ("A1", "A5"), ("A3", "A1"))):
        f = L[coh]["tau_1e-06"]["%s_over_%s" % (num, den)]["median"]
        ax.text(i + 0.5, 4300, "×%.*f" % (3 if f < 1.5 else 2 if f < 5 else 1, f), fontsize=5.8, fontweight="bold",
                ha="center", va="center", color=INK, zorder=6)  # factor row above all data (max CR < 2,500)
        ax.text(i + 0.5, 2.9, STEP[i], fontsize=5.3, ha="center", va="bottom", color=INK)
    ax.set_yscale("log")
    ax.set_ylim(2.5, 7000)
    ax.set_xlim(-0.35, 3.35)
    ax.set_xticks(xs)
    ax.set_xticklabels([TICK[a] for a in RUNGS], fontsize=5.0)
    ax.tick_params(axis="x", length=0, pad=2.5)
    log_ticks(ax, axis="y")
    grid(ax, axis="y")
    ax.set_title(title, fontsize=6.3, pad=3)
    if j == 0:
        ax.set_ylabel("Certified compression ratio ($\\tau$ = 10$^{-6}$)")
    else:
        ax.set_yticklabels([])


def strips(ax, num, den, key, ylim, col):
    for i, tau in enumerate(C.TAUS):
        for coh, dx in (("bulk", -0.18), ("slab", 0.18)):
            r, v = C.check_median(D, num, den, coh, tau, S, key)
            x = i + dx + rng.uniform(-0.07, 0.07, r.size)
            if coh == "bulk":
                ax.scatter(x, r, s=3.5, color=col, edgecolor="white", lw=0.15, alpha=0.9, zorder=2)
            else:
                ax.scatter(x, r, s=4.5, marker="^", facecolor="none", edgecolor=col, lw=0.4, zorder=2)
            ax.plot([i + dx - 0.12, i + dx + 0.12], [v["median"]] * 2, color=INK, lw=1.0, zorder=4)
            ax.plot([i + dx] * 2, v["ci95"], color=INK, lw=0.6, zorder=4)
    ax.set_yscale("log")
    ax.set_ylim(*ylim)
    ax.set_xlim(-0.5, 2.5)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([C.TAU_LAB[t] for t in C.TAUS])
    ax.axhline(1.0, color=INK, lw=0.5, zorder=1)
    grid(ax, axis="y")
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())


# ---- b: operator metric at equal optimization ---------------------------------------------------------------------
pg.letter("b", 108.0, 85.0 + UP)
axb = pg.ax(124.0, 52.0 + UP, 56.0, 27.0)
strips(axb, "A3", "A5", "A3_over_A5", (0.8, 12), C.ARM["A3"])
axb.set_yticks([1, 2, 5, 10])
axb.set_yticklabels(["1", "2", "5", "10"])
axb.set_ylabel("Operator / blind\nmetric (A3/A5)")
axb.set_xticklabels([])
for i, tau in enumerate(C.TAUS):
    for coh, dx in (("bulk", -0.18), ("slab", 0.18)):
        m = S[coh]["part_A"][C.TAU_KEY[tau]]["A3_over_A5"]["median"]
        axb.text(i + dx, 9.6, "%.2f" % m, fontsize=5.0, ha="center", va="center", color=INK)

# ---- c: optimizer share -------------------------------------------------------------------------------------------
pg.letter("c", 108.0, 46.0 + UP)
axc = pg.ax(124.0, 15.0 + UP, 56.0, 27.0)
strips(axc, "A3", "A1", "A3_over_A1", (0.9, 4.6), C.ARM["A1"])
axc.axhline(1.15, color=MID, lw=0.6, ls=(0, (3, 2)), zorder=1)
axc.text(2.47, 1.17, "1.15", fontsize=5.3, color=INK, ha="right", va="bottom")
axc.set_yticks([1, 1.5, 2, 3, 4])
axc.set_yticklabels(["1", "1.5", "2", "3", "4"])
axc.set_ylabel("Optimizer share\n(A3/A1)")
axc.set_xlabel("Hartree tolerance $\\tau$")
for i, tau in enumerate(C.TAUS):
    for coh, dx in (("bulk", -0.18), ("slab", 0.18)):
        m = S[coh]["part_A"][C.TAU_KEY[tau]]["A3_over_A1"]["median"]
        axc.text(i + dx, 3.85, "%.3f" % m, fontsize=5.0, ha="center", va="center", color=INK)

# ---- d: the writers, per material and at archive scale ------------------------------------------------------------
AN = os.path.join(C.ROOT, "analysis")
SFP = json.load(open(os.path.join(AN, "sfp_spin_writer_20261025", "results", "SUMMARY.json")))
WF = json.load(open(os.path.join(AN, "waterfill_writer_20261025", "results", "SUMMARY.json")))
ARCH = json.load(open(os.path.join(AN, "archive_w2_20261025", "results", "SUMMARY.json")))["estimates"]
rows = pd.read_csv(os.path.join(AN, "sfp_spin_writer_20261025", "results", "rows.csv"))
rows = rows[rows.certified & np.isclose(rows.tau, 1e-6) & rows.arm.isin(["W1S", "W2S"])]
wr = rows.pivot(index="material_id", columns="arm", values="cr")
a3 = D[np.isclose(D.tau, 1e-6)].set_index("material_id")[["A3", "cohort"]]
WL = a3.join(wr, how="inner")
assert len(WL) == 92 and WL.W1S.notna().all() and WL.W2S.notna().all()
for key, num, den, src in (("W1S/A3_1e-06", "W1S", "A3", WF), ("W2S/W1S_1e-06", "W2S", "W1S", SFP)):
    for sel, tag in ((WL.cohort.notna(), "all"), (WL.cohort == "bulk", "P1"), (WL.cohort == "slab", "P3B")):
        got = float(np.median((WL[num] / WL[den])[sel]))
        assert abs(got - src["ratios"]["%s_%s" % (key, tag)]["median"]) < 1e-9 * got, (key, tag, got)
WRUNGS = ("A3", "W1S", "W2S")
WCOL = {"A3": C.ARM["A3"], "W1S": C.WRITER["W1S"], "W2S": C.WRITER["W2S"]}
WTICK = {"A3": "operational\noptimum (zlib)", "W1S": "water-filling\nwriter", "W2S": "predictive\nwriter"}
pg.letter("d", 2.0, 49.0)
for j, (coh, title, x0) in enumerate((("bulk", "Bulk crystals (60)", 14.0), ("slab", "Surface slabs (32)", 52.0))):
    ax = pg.ax(x0, 15.0, 34.0, 26.0)
    t = WL[WL.cohort == coh]
    xs = np.arange(3)
    for _, r in t.iterrows():
        ax.plot(xs, [r[a] for a in WRUNGS], color=LINE_C, lw=0.3, zorder=1)
    for i, a in enumerate(WRUNGS):
        jit = rng.uniform(-0.06, 0.06, len(t))
        if coh == "bulk":
            ax.scatter(i + jit, t[a], s=3.5, color=WCOL[a], edgecolor="white", lw=0.15, zorder=2)
        else:
            ax.scatter(i + jit, t[a], s=4.5, marker="^", facecolor="none", edgecolor=WCOL[a], lw=0.4, zorder=2)
    med = [float(np.median(t[a])) for a in WRUNGS]
    ax.plot(xs, med, color=INK, lw=1.0, zorder=4)
    ax.scatter(xs, med, s=16, color=[WCOL[a] for a in WRUNGS], edgecolor=INK, lw=0.6, zorder=5,
               marker="o" if coh == "bulk" else "^")
    for i, (num, den) in enumerate((("W1S", "A3"), ("W2S", "W1S"))):
        f = float(np.median(t[num] / t[den]))
        ax.text(i + 0.5, 30000, "×%.2f" % f, fontsize=5.8, fontweight="bold", ha="center", va="center", color=INK,
                zorder=6)                       # factor row above all data
    ax.set_yscale("log")
    ax.set_ylim(20, 60000)
    ax.set_xlim(-0.35, 2.35)
    ax.set_xticks(xs)
    ax.set_xticklabels([WTICK[a] for a in WRUNGS], fontsize=5.0)
    ax.tick_params(axis="x", length=0, pad=2.5)
    log_ticks(ax, axis="y")
    grid(ax, axis="y")
    ax.set_title(title, fontsize=6.3, pad=3)
    if j == 0:
        ax.set_ylabel("Certified CR ($\\tau$ = 10$^{-6}$)")
    else:
        ax.set_yticklabels([])

# right: the archive under every writer (whole objects, magnetization included)
AW = (("P", "best pointwise codec", C.ARM["A6"]), ("T", "spectral truncation", C.ARM["A2"]),
      ("L", "closed-form law", C.ARM["A1"]), ("O", "operational allocation (zlib)", C.ARM["A3"]),
      ("W", "water-filling writer", C.WRITER["W1S"]), ("V", "predictive + magnetization writers", C.WRITER["W2S"]))
WANT = {"P_1e-06": 34.6, "T_1e-06": 232, "L_1e-06": 316, "O_1e-06": 347, "W_1e-06": 555, "V_1e-06": 1401,
        "T_0.0001": 1115, "L_0.0001": 1036, "O_0.0001": 1325, "W_0.0001": 1735, "V_0.0001": 4719}
for k, v in WANT.items():                        # the manuscript's numbers
    assert abs(ARCH[k]["R"] - v) <= (0.05 if v < 100 else 0.5), (k, ARCH[k]["R"])
axr = pg.ax(130.0, 15.0, 50.0, 26.0)
for i, (w, lab, col) in enumerate(AW):
    for tk, face in (("1e-06", col), ("0.0001", "white")):
        e = ARCH.get("%s_%s" % (w, tk))
        if e is None:
            continue
        axr.plot(e["ci95"], [i, i], color=col, lw=0.8, zorder=2, solid_capstyle="butt")
        axr.scatter([e["R"]], [i], s=16, facecolor=face, edgecolor=col, lw=0.8, zorder=3)
    e = ARCH["%s_1e-06" % w]
    axr.text(e["ci95"][0] / 1.18, i, ("%.1f" % e["R"]) if e["R"] < 100 else "{:,.0f}".format(e["R"]),
             fontsize=5.0, ha="right", va="center", color=INK, fontweight="bold" if w == "V" else "normal")
e = ARCH["V_0.0001"]
axr.text(e["ci95"][1] * 1.15, len(AW) - 1, "{:,.0f}".format(e["R"]), fontsize=5.0, ha="left", va="center",
         color=INK, fontweight="bold")
axr.set_yticks(range(len(AW)))
axr.set_yticklabels([lab for _, lab, _ in AW], fontsize=5.3)
axr.tick_params(axis="y", length=0)
axr.set_ylim(-0.6, len(AW) - 0.4)
axr.set_xscale("log")
axr.set_xlim(8, 3e4)
log_ticks(axr, axis="x")
grid(axr, axis="x")
axr.set_xlabel("Archive reduction (8.50 TB, whole objects)")
axr.set_title("Materials Project archive", fontsize=6.3, pad=3)

hand = [Line2D([], [], ls="", marker="o", ms=3.0, color=MID, label="bulk crystal (P1)"),
        Line2D([], [], ls="", marker="^", ms=3.2, mfc="none", mec=MID, mew=0.6, label="surface slab (P3b)"),
        Line2D([], [], color=INK, lw=1.0, label="median (b, c: with 95% CI)"),
        Line2D([], [], ls="", marker="o", ms=3.4, mfc=MID, mec=MID, label=r"archive, $\tau$ = 10$^{-6}$"),
        Line2D([], [], ls="", marker="o", ms=3.4, mfc="white", mec=MID, mew=0.8, label=r"archive, $\tau$ = 10$^{-4}$")]
leg = pg.ax(14.0, 0.3, 166.0, 4.5)
leg.axis("off")
leg.legend(handles=hand, loc="center", ncol=5, fontsize=5.3, frameon=False, columnspacing=1.4)

layout.audit(pg.fig)
pg.save(HERE, "Fig6")
