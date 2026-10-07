"""NC Figure 6 -- the gain of operator-aware allocation is predicted before compression.

183 x 72 mm, three panels:
  a  tau = 1e-6: predicted gain G_pred against measured gain G_obs for five operators on 60 fresh bulk crystals (P1)
     and 32 fresh surface slabs (P3b); identity line with a +/-25 % band. Predictions were committed before any
     compression run (P1 d5fc30b, P3b c1e6564).
  b  the same at tau = 1e-4.
  c  per-operator medians at tau = 1e-6, ordered by predicted gain; predicted (open) and measured (filled), bulk and
     slab; the shaded band is the pre-registered null-gain window [0.90, 1.11]. The density control sits at 1.
Statistics are read from committed files and asserted before drawing:
  run_P1_CONFIRMATORY/SUMMARY.json, run_P3B_CONFIRMATORY/SUMMARY.json, POOLED_P1_P3B.json.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig6.py   -> Fig6.{svg,pdf,png}
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "figures", "composite"))
import layout  # noqa: E402
from style import (BLUE, DARK_B, DARK_G, GREEN, INK, MID, OTHER, PALE, PAPER, Page, grid, log_ticks,  # noqa: E402
                   note)

R = os.path.join(ROOT, "analysis", "general_qoac_law", "results")
P1 = pd.read_csv(os.path.join(R, "run_P1_CONFIRMATORY", "part_b_material.csv")).assign(cohort="bulk")
P3 = pd.read_csv(os.path.join(R, "run_P3B_CONFIRMATORY", "part_b_material.csv")).assign(cohort="slab")
S1 = json.load(open(os.path.join(R, "run_P1_CONFIRMATORY", "SUMMARY.json")))
S3 = json.load(open(os.path.join(R, "run_P3B_CONFIRMATORY", "SUMMARY.json")))
SP = json.load(open(os.path.join(R, "POOLED_P1_P3B.json")))
assert P1.material_id.nunique() == 60 and P3.material_id.nunique() == 32
assert abs(S1["part_B"]["tau_1e-06"]["spearman"] - 0.9776) < 1e-3
assert abs(S3["part_B"]["tau_1e-06"]["spearman"] - 0.9789) < 1e-3
assert SP["tau_1e-06"]["pairs"] == 460 and SP["tau_1e-06"]["materials"] == 92

GAUSS = "gaussian_smoothed_density(sigma_angstrom=0.5)"
OPS = [  # key, label, colour   (ordered by predicted gain, low to high)
    ("density_gradient", "Density gradient", PALE),
    ("density_laplacian", "Density Laplacian", BLUE),
    ("hartree_field", "Hartree field", DARK_G),
    ("hartree_potential", "Hartree potential", GREEN),
    (GAUSS, "Gaussian-smoothed density (σ = 0.5 Å)", DARK_B),
]
SHORT = {"density": "Density (control)", "density_gradient": "Gradient", "density_laplacian": "Laplacian",
         "hartree_field": "Hartree field", "hartree_potential": "Hartree potential", GAUSS: "Gaussian, σ 0.5 Å"}
COL = {k: c for k, _, c in OPS}
LAB = {k: lab for k, lab, _ in OPS}
MARK = {"bulk": "o", "slab": "^"}
D = pd.concat([P1, P3])
D = D[D.operator != "density"]

pg = Page(183.0, 72.0)
LIM = (0.85, 50.0)


def scatter(ax, tau, show_y):
    t = D[np.isclose(D.tau, tau)]
    xs = np.geomspace(*LIM, 50)
    ax.fill_between(xs, xs / 1.25, xs * 1.25, color=PAPER, lw=0, zorder=0)
    ax.plot(LIM, LIM, color=INK, lw=0.6, zorder=1)
    for key, _, c in OPS:
        for coh in ("bulk", "slab"):
            s = t[(t.operator == key) & (t.cohort == coh)]
            if coh == "bulk":
                ax.scatter(s.G_pred, s.G_obs, s=7, marker="o", color=c, edgecolor="white", lw=0.25, zorder=3)
            else:
                ax.scatter(s.G_pred, s.G_obs, s=8, marker="^", facecolor="none", edgecolor=c, lw=0.55, zorder=3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*LIM)
    ax.set_ylim(*LIM)
    ax.set_aspect("equal")
    log_ticks(ax)
    grid(ax)
    ax.set_xlabel("Predicted gain, $G_\\mathrm{pred}$")
    if show_y:
        ax.set_ylabel("Measured gain, $G_\\mathrm{obs}$")
    key = "tau_1e-06" if tau == 1e-6 else "tau_0.0001"
    b1, b3, pp = S1["part_B"][key], S3["part_B"][key], SP[key]
    txt = ("$\\tau$ = %s\nbulk (60): |ln err| %.3f, ρ %.3f\nslab (32): |ln err| %.3f, ρ %.3f\nall (92): |ln err| %.3f, ρ %.3f"
           % ("10$^{-6}$" if tau == 1e-6 else "10$^{-4}$", b1["median_abs_log_err"], b1["spearman"],
              b3["median_abs_log_err"], b3["spearman"], pp["median_abs_log_err"], pp["spearman_pooled"]))
    note(ax, 0.04, 0.96, txt, size=5.3, box=True)


pg.letter("a", 2.0, 71.0)
axa = pg.ax(12.0, 17.0, 50.0, 50.0)
scatter(axa, 1e-6, True)
pg.letter("b", 65.0, 71.0)
axb = pg.ax(70.0, 17.0, 50.0, 50.0)
scatter(axb, 1e-4, False)

# legend under a/b
hand = [Line2D([], [], ls="", marker="s", ms=3.6, color=c, label=lab) for _, lab, c in OPS]
hand += [Line2D([], [], ls="", marker="o", ms=3.2, color=MID, label="bulk crystals (P1)"),
         Line2D([], [], ls="", marker="^", ms=3.4, mfc="none", mec=MID, mew=0.6, label="surface slabs (P3b)")]
leg_ax = pg.ax(10.0, 0.5, 112.0, 6.0)
leg_ax.axis("off")
leg_ax.legend(handles=hand, loc="center", ncol=4, fontsize=5.3, handletextpad=0.3, columnspacing=0.9,
              frameon=False)

# ---- c: per-operator medians ----------------------------------------------------------------------
pg.letter("c", 123.0, 71.0)
axc = pg.ax(148.0, 17.0, 32.0, 50.0)
t6 = pd.concat([P1, P3])
t6 = t6[np.isclose(t6.tau, 1e-6)]
order = [("density", "Density (control)", OTHER)] + OPS
axc.axvspan(0.90, 1.11, color=PAPER, lw=0, zorder=0)
for i, (key, lab, c) in enumerate(order):
    y = len(order) - 1 - i
    for coh, dy in (("bulk", 0.17), ("slab", -0.17)):
        s = t6[(t6.operator == key) & (t6.cohort == coh)]
        gp, go = s.G_pred.median(), s.G_obs.median()
        axc.plot([gp, go], [y + dy, y + dy], color=c, lw=0.6, zorder=2)
        axc.scatter([gp], [y + dy], s=11, marker=MARK[coh], facecolor="white", edgecolor=c, lw=0.6, zorder=3)
        axc.scatter([go], [y + dy], s=11, marker=MARK[coh], color=c, edgecolor=c, lw=0.6, zorder=4)
axc.set_xscale("log")
axc.set_xlim(0.8, 40)
axc.set_ylim(-0.6, len(order) - 0.4)
axc.set_yticks(range(len(order)))
axc.set_yticklabels([SHORT[k] for k, _, _ in order][::-1], fontsize=5.3)
axc.tick_params(axis="y", length=0, pad=1.5)
log_ticks(axc, axis="x")
grid(axc, axis="x")
axc.set_xlabel("Median gain ($\\tau$ = 10$^{-6}$)")
hand_c = [Line2D([], [], ls="", marker="o", ms=3.2, mfc="white", mec=MID, mew=0.6, label="predicted"),
          Line2D([], [], ls="", marker="o", ms=3.2, color=MID, label="measured")]
axc.legend(handles=hand_c, loc="upper right", fontsize=5.3, handletextpad=0.2, frameon=False)  # top rows sit at G ~ 1

layout.audit(pg.fig)
pg.save(HERE, "Fig6")
