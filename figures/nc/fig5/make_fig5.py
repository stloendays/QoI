"""NC Figure 5 -- under equal search, the closed-form operator law certifies an order of magnitude more than
pointwise codecs and beats spectral truncation, on fresh bulk crystals and fresh surface slabs.

183 x 155 mm:
  a  tau = 1e-6 Hartree certificate: per material, best equal-search ZFP/SZ3/SPERR CR (A6) vs closed-form law CR (A1);
     60 bulk (P1, circles) and 32 slab (P3b, triangles); iso-ratio lines 1x and 10x.
  b  the same against spectral truncation with equal search (A2); iso-ratio line 1x.
  c  median ratios A1/A6 and A1/A2 with bootstrap 95% CIs at tau = 1e-4, 1e-6, 1e-8, per cohort.
  d  certified CR against Hartree tolerance for the three equal-search arms: median (line) and interquartile range
     (band) over materials, bulk and slab.
  e  A1 vs QoI-preserving baselines QPET (Q) and MGARD s = -2 (M2), at tau = 1e-6.
  f  absolute slab work-function error for the five certified arms at tau = 1e-4 and 1e-6.
All medians are asserted against run_P1_CONFIRMATORY/SUMMARY.json and run_P3B_CONFIRMATORY/SUMMARY.json.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig5.py   -> Fig5.{svg,pdf,png}
"""
import os
import re
import sys

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common as C  # noqa: E402
from advanced import swarm  # noqa: E402
import layout  # noqa: E402
from style import BLUE, DARK_G, INK, MID, PALE, POS_C, Page, grid, log_ticks, note  # noqa: E402

D = C.part_a()
S = C.summaries()
B = C.baseline_materials()
V = C.slab_dphi()
for coh in ("bulk", "slab"):
    for tau in C.TAUS:
        C.check_median(D, "A1", "A6", coh, tau, S, "A1_over_A6")
        C.check_median(D, "A1", "A2", coh, tau, S, "A1_over_A2")


def _sig3(value):
    value = float(value)
    return round(value, 2 - int(np.floor(np.log10(abs(value)))))


def _baseline_doc_expectations():
    """Read the committed tau=1e-6 median/win rows from the baseline RESULTS.md."""
    path = os.path.join(os.path.dirname(C.BASELINE_RESULTS), "RESULTS.md")
    text = open(path, encoding="utf-8").read()
    m = re.search(r"### τ = 1e-6\s*(.*?)(?=\n### τ = 1e-4)", text, flags=re.S)
    assert m, "tau=1e-6 baseline section missing from RESULTS.md"
    block = m.group(1)
    out = {}
    for cohort, heading in (("bulk", "#### P1 (60 MP bulk)"), ("slab", "#### P3b (32 NOMAD slabs)")):
        start = block.index(heading) + len(heading)
        end = block.find("#### ", start)
        section = block[start:] if end < 0 else block[start:end]
        for baseline in ("Q", "M2"):
            key = "A1/%s" % baseline
            line = next(line for line in section.splitlines() if re.match(r"\|\s*%s\s*\|" % re.escape(key), line))
            fields = [field.strip() for field in line.split("|")]
            wins, total = [int(x.strip()) for x in fields[4].split("/")]
            out[(cohort, baseline)] = (float(fields[2]), wins, total)
    return out


BASELINE_DOC = _baseline_doc_expectations()
for cohort, n_expected in (("bulk", 60), ("slab", 32)):
    t = B[(B.cohort == cohort) & np.isclose(B.tau, 1e-6)]
    assert len(t) == n_expected
    for baseline in ("Q", "M2"):
        ratios = (t.A1 / t[baseline]).dropna().to_numpy()
        got_median = float(np.median(ratios))
        doc_median, doc_wins, doc_n = BASELINE_DOC[(cohort, baseline)]
        assert _sig3(got_median) == _sig3(doc_median), (cohort, baseline, got_median, doc_median)
        assert int(np.sum(ratios > 1.0)) == doc_wins == doc_n == n_expected


DPHI_SUMMARY = pd.read_csv(os.path.join(C.VACUUM_RESULTS, "summary.csv"))
F_ARMS = ("A1", "A3", "A5", "A2", "A6")
F_TAUS = (1e-4, 1e-6)
for tau in F_TAUS:
    for arm in F_ARMS:
        values = V[(V.arm == arm) & np.isclose(V.tau, tau) & V.evaluated].abs_dphi_meV.to_numpy()
        summary_row = DPHI_SUMMARY[(DPHI_SUMMARY.arm == arm) & np.isclose(DPHI_SUMMARY.tau, tau)]
        assert len(summary_row) == 1
        want = summary_row.iloc[0]
        assert len(values) == int(want.n_evaluated) == 27
        assert np.isclose(np.median(values), want.median_abs_dphi_meV, rtol=0, atol=1e-12)

DPHI_EXPECTED = {("A1", 1e-6): 0.00400, ("A1", 1e-4): 1.09,
                 ("A6", 1e-6): 0.340, ("A6", 1e-4): 35.5}
for (arm, tau), expected in DPHI_EXPECTED.items():
    values = V[(V.arm == arm) & np.isclose(V.tau, tau) & V.evaluated].abs_dphi_meV.to_numpy()
    assert np.isclose(np.median(values), expected, rtol=5e-3), (arm, tau, np.median(values), expected)

pg = Page(183.0, 155.0)
MK = {"bulk": dict(marker="o", s=8), "slab": dict(marker="^", s=9)}
LAW = C.ARM["A1"]


def pair(ax, den, lines):
    t = D[np.isclose(D.tau, 1e-6)]
    lo, hi = 5.0, 5000.0
    xs = np.array([lo, hi])
    for k in lines:
        ax.plot(xs, xs * k, color=MID if k != 1 else INK, lw=0.5, ls="-" if k == 1 else (0, (3, 2)), zorder=1)
        ax.text(hi / 1.15 / (k if k > 1 else 1), hi / 1.15 if k > 1 else hi / 1.6,
                "%g×" % k, fontsize=5.3, color=MID, ha="right", va="top")
    for coh in ("bulk", "slab"):
        s = t[t.cohort == coh]
        if coh == "bulk":
            ax.scatter(s[den], s.A1, color=LAW, edgecolor="white", lw=0.25, zorder=3, **MK[coh])
        else:
            ax.scatter(s[den], s.A1, facecolor="none", edgecolor=LAW, lw=0.6, zorder=3, **MK[coh])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    log_ticks(ax)
    grid(ax)
    ax.set_ylabel("Closed-form law CR (A1)")


TOP = 107.0
pg.letter("a", 2.0, 154.0)
axa = pg.ax(13.0, TOP, 44.0, 44.0)
pair(axa, "A6", (1, 10))
axa.set_xlabel("Best pointwise codec CR (A6)")
r1, r3 = S["bulk"]["part_A"]["tau_1e-06"]["A1_over_A6"], S["slab"]["part_A"]["tau_1e-06"]["A1_over_A6"]
note(axa, 0.96, 0.04, ha="right", va="bottom", text= "$\\tau$ = 10$^{-6}$\nbulk: %.1f× (%d/%d)\nslab: %.1f× (%d/%d)" %
     (r1["median"], r1["wins"], r1["n"], r3["median"], r3["wins"], r3["n"]), size=5.3)

pg.letter("b", 64.0, 154.0)
axb = pg.ax(75.0, TOP, 44.0, 44.0)
pair(axb, "A2", (1,))
axb.set_xlabel("Spectral truncation CR (A2)")
r1, r3 = S["bulk"]["part_A"]["tau_1e-06"]["A1_over_A2"], S["slab"]["part_A"]["tau_1e-06"]["A1_over_A2"]
note(axb, 0.96, 0.04, ha="right", va="bottom", text= "$\\tau$ = 10$^{-6}$\nbulk: %.2f× (%d/%d)\nslab: %.2f× (%d/%d)" %
     (r1["median"], r1["wins"], r1["n"], r3["median"], r3["wins"], r3["n"]), size=5.3)

# ---- c: medians and CIs across tolerances ----------------------------------------------------------
pg.letter("c", 126.0, 154.0)
axc = pg.ax(137.0, TOP, 43.0, 44.0)
X = {1e-4: 0, 1e-6: 1, 1e-8: 2}
for key, col in (("A1_over_A6", C.ARM["A6"]), ("A1_over_A2", C.ARM["A2"])):
    for coh, dx, mk in (("bulk", -0.09, "o"), ("slab", 0.09, "^")):
        xs, ys, lo, hi = [], [], [], []
        for tau in C.TAUS:
            v = S[coh]["part_A"][C.TAU_KEY[tau]][key]
            xs.append(X[tau] + dx)
            ys.append(v["median"])
            lo.append(v["median"] - v["ci95"][0])
            hi.append(v["ci95"][1] - v["median"])
        axc.errorbar(xs, ys, yerr=[lo, hi], color=col, lw=0.7, elinewidth=0.6, capsize=1.2, marker=mk, ms=3.2,
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
hand = [Line2D([], [], color=C.ARM["A6"], lw=0.8, label="law / pointwise (A1/A6)"),
        Line2D([], [], color=C.ARM["A2"], lw=0.8, label="law / truncation (A1/A2)")]
axc.legend(handles=hand, loc="upper center", fontsize=5.0, handletextpad=0.4, frameon=False, ncol=1)  # data < 25

# ---- d: certified CR against tolerance, three equal-search arms --------------------------------------------------
pg.letter("d", 2.0, 96.0)
for j, (coh, title, x0) in enumerate((("bulk", "bulk crystals (60)", 13.0), ("slab", "surface slabs (32)", 102.0))):
    ax = pg.ax(x0, 61.0, 78.0, 30.0)
    for arm in ("A6", "A2", "A1"):
        med, q1, q3 = [], [], []
        for tau in C.TAUS:
            v = D[(D.cohort == coh) & np.isclose(D.tau, tau)][arm].dropna()
            med.append(np.median(v))
            q1.append(np.quantile(v, 0.25))
            q3.append(np.quantile(v, 0.75))
        x = np.log10(C.TAUS)
        ax.fill_between(x, q1, q3, color=C.ARM[arm], alpha=0.22, lw=0, zorder=1)
        ax.plot(x, med, color=C.ARM[arm], lw=1.1, marker="o" if coh == "bulk" else "^", ms=3.4,
                mfc=C.ARM[arm] if coh == "bulk" else "white", mec=C.ARM[arm], zorder=3)
    ax.set_yscale("log")
    ax.set_ylim(2, 4000)
    ax.set_xlim(-3.6, -8.4)
    ax.set_xticks(np.log10(C.TAUS))
    ax.set_xticklabels([C.TAU_LAB[t] for t in C.TAUS])
    ax.set_xlabel("Hartree tolerance $\\tau$")
    log_ticks(ax, axis="y")
    grid(ax, axis="y")
    ax.text(0.98, 0.94, title, transform=ax.transAxes, fontsize=6.0, ha="right", va="top")
    if j == 0:
        ax.set_ylabel("Certified CR")
hand = [Line2D([], [], color=C.ARM[a], lw=1.1, label=lab) for a, lab in
        (("A1", "closed-form law (A1)"), ("A2", "spectral truncation (A2)"), ("A6", "best pointwise codec (A6)"))]
hand += [Patch(facecolor=MID, alpha=0.22, lw=0, label="interquartile range"),
         Line2D([], [], ls="", marker="o", ms=3.0, color=MID, label="bulk crystal (P1)"),
         Line2D([], [], ls="", marker="^", ms=3.2, mfc="none", mec=MID, mew=0.6, label="surface slab (P3b)")]

# ---- e: equal-search law versus QoI-preserving baselines --------------------------------------------------------
Q_COLOR, M2_COLOR = PALE, POS_C
pg.letter("e", 2.0, 49.0)
axe = pg.ax(13.0, 14.0, 78.0, 30.0)
lo, hi = 5.0, 5000.0
xs = np.array([lo, hi])
for k in (1, 10):
    axe.plot(xs, xs * k, color=MID if k != 1 else INK, lw=0.5,
             ls="-" if k == 1 else (0, (3, 2)), zorder=1)
    if k == 10:
        axe.text(hi / 10.0 * 1.08, hi / 1.15, "%g×" % k, fontsize=5.3, color=MID,
                 ha="left", va="top", bbox=dict(fc="white", ec="none", pad=0.3), zorder=7)
    else:
        axe.text(hi / 1.15, hi / 1.6, "%g×" % k, fontsize=5.3, color=MID,
                 ha="right", va="top")
for baseline, color in (("Q", Q_COLOR), ("M2", M2_COLOR)):
    t = B[np.isclose(B.tau, 1e-6)]
    for cohort in ("bulk", "slab"):
        s = t[t.cohort == cohort]
        if cohort == "bulk":
            axe.scatter(s[baseline], s.A1, color=color, edgecolor="white", lw=0.25, zorder=3, **MK[cohort])
        else:
            axe.scatter(s[baseline], s.A1, facecolor="none", edgecolor=color, lw=0.6, zorder=3, **MK[cohort])
axe.set_xscale("log")
axe.set_yscale("log")
axe.set_xlim(lo, hi)
axe.set_ylim(lo, hi)
axe.set_xlabel("Baseline certified CR ($\\tau = 10^{-6}$)")
axe.set_ylabel("Closed-form law CR (A1)")
log_ticks(axe)
grid(axe)
layout.legend(
    axe,
    handles=[Line2D([], [], ls="", marker="o", ms=3.4, color=Q_COLOR, mfc=Q_COLOR, mec="white"),
             Line2D([], [], ls="", marker="o", ms=3.4, color=M2_COLOR, mfc=M2_COLOR, mec="white")],
    labels=["QPET (Q): bulk 6.31× (60/60), slab 9.47× (32/32)",
            "MGARD $s=-2$ (M2): bulk 18.2× (60/60), slab 21.0× (32/32)"],
    loc="lower right", bbox_to_anchor=(0.97, 0.04), fontsize=4.35,
    handletextpad=0.35, labelspacing=0.25, title="$\\tau$ = 10$^{-6}$")

# ---- f: vacuum-level work-function error for certified slab streams ---------------------------------------------
F_COLOR = {"A1": C.ARM["A1"], "A3": DARK_G, "A5": BLUE, "A2": C.ARM["A2"], "A6": C.ARM["A6"]}
F_LABEL = {"A1": "law", "A3": "oper.", "A5": "blind", "A2": "trunc.", "A6": "ptwise"}
pg.letter("f", 91.0, 49.0)
axf = pg.ax(96.0, 14.0, 78.0, 30.0)
group_shift = {1e-4: 0.0, 1e-6: 6.0}
positions = []
labels = []
for tau in F_TAUS:
    for i, arm in enumerate(F_ARMS):
        p = i + group_shift[tau]
        positions.append(p)
        labels.append("%s\n%s" % (arm, F_LABEL[arm]))
        values = V[(V.arm == arm) & np.isclose(V.tau, tau) & V.evaluated].abs_dphi_meV.to_numpy()
        log_values = np.log10(values)
        off = swarm(log_values, d_val=0.07, d_off=0.045, max_off=0.30)
        axf.scatter(p + off, values, s=7.0, color=F_COLOR[arm], edgecolor="white", lw=0.25, zorder=3)
        median = float(np.median(values))
        axf.plot([p - 0.22, p + 0.22], [median, median], color=INK, lw=0.9, solid_capstyle="butt", zorder=5)
axf.set_yscale("log")
axf.set_ylim(1e-5, 1e3)
axf.set_xlim(-0.8, 10.8)
axf.set_xticks(positions)
axf.set_xticklabels(labels, fontsize=4.8)
for tick, arm in zip(axf.get_xticklabels(), F_ARMS * 2):
    tick.set_color(F_COLOR[arm])
axf.tick_params(axis="x", length=0, pad=1)
axf.set_ylabel("$|\\Delta \\Phi|$ (meV)")
log_ticks(axf, axis="y")
grid(axf, axis="y")
for y, label in ((1.0, "1 meV"), (10.0, "10 meV")):
    axf.axhline(y, color=MID, lw=0.45, ls=(0, (3, 2)), zorder=1)
    axf.text(1.015, y * 1.08, label, transform=axf.get_yaxis_transform(), color=MID,
             fontsize=4.8, ha="left", va="bottom", clip_on=False,
             bbox=dict(facecolor="white", edgecolor="none", pad=0.1), zorder=6)
axf.text(2.0, 1.02, r"$\tau = 10^{-4}$", transform=axf.get_xaxis_transform(),
         ha="center", va="bottom", fontsize=5.3, clip_on=False)
axf.text(8.0, 1.02, r"$\tau = 10^{-6}$", transform=axf.get_xaxis_transform(),
         ha="center", va="bottom", fontsize=5.3, clip_on=False)

leg = pg.ax(13.0, 0.2, 167.0, 3.6)
leg.axis("off")
leg.legend(handles=hand, loc="center", ncol=6, fontsize=5.3, frameon=False, columnspacing=1.4)

layout.audit(pg.fig)
pg.save(HERE, "Fig5")
