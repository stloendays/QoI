"""Figure 4 -- a stability probe must excite the numerical failure mode of the downstream analysis.

2 + 1 layout, 183 x 118 mm:
  a  the two floor distributions as rainclouds (every material shown), order-preserving float32 control vs QSQ
                                                                  stability_floor_A_archived_float32.csv, stability_floor_A1.csv
  b  the same pairs as a scatter against the identity: heterogeneous, not a rescaling
  c  ECDF of the QSQ floor over all 319 systems; the three tolerances cut the eligible cohort
                                                                  stability_floor_A1.csv, eligibility_summary_A1.csv

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig4.py   -> Fig4.{svg,pdf,png}
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (DARK_B, ELIGIBLE, INK, MID, OTHER, RED, Page, grid, log_ticks, note, open_frame,  # noqa: E402
                   pow_label, thr_label)
import advanced as AD  # noqa: E402

m = D.paired_floors()
med_ratio = float(np.median(m.ratio))
assert 1.5e4 < med_ratio < 1.7e4, med_ratio                 # "approximately 1.6 x 10^4" in the caption
a1 = D.floor_a1()
a1 = a1[np.isfinite(a1.stability_floor_A1_e) & (a1.stability_floor_A1_e > 0)]
elig = D.eligibility_summary()
elig = elig[elig.stratum == "overall"].set_index("threshold_e")
assert len(a1) == 319

pg = Page(183.0, 118.0)

# ---- a: the two floor distributions -----------------------------------------------------------------
pg.letter("a", 2.0, 117.0)
ax = pg.ax(14.0, 66.0, 62.0, 46.0)
la, lq = np.log10(m.archived.values), np.log10(m.stability_floor_A1_e.values)
AD.raincloud(ax, [la, lq], ["order-preserving\nfloat32 control", "QSQ\n(5 seeds, max)"], colors=[OTHER, DARK_B],
             orient="v", point_size=3.0, swarm_d=0.012, cloud=0.36, rain=0.3)
k0, k1 = int(np.floor(min(la.min(), lq.min()))), int(np.ceil(max(la.max(), lq.max())))
ax.set_yticks(range(k0, k1 + 1, 2)); ax.set_yticklabels([pow_label(k) for k in range(k0, k1 + 1, 2)])
ax.set_ylim(k0 - 0.3, k1 + 0.3)
ax.set_ylabel("re-derived Bader stability floor (e)")
grid(ax, "y")
ax.annotate("", xy=(0.6, np.median(lq)), xytext=(0.47, np.median(la)), zorder=6,
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.9, mutation_scale=7, shrinkA=0, shrinkB=0))
ax.text(0.2, k1 - 0.6, "median ratio %.1f × 10$^{4}$" % (med_ratio / 1e4), ha="center", va="top", fontsize=5.8,
        color=RED, fontweight="bold")
# the space above the control cloud (floors > 1e-1 e) is empty; the arrow runs in the gap between the clouds
ax.text(0.5, 1.02, "%d paired development materials" % len(m), transform=ax.transAxes, ha="center", va="bottom",
        fontsize=5.4, color=MID)

# ---- b: scatter vs identity ---------------------------------------------------------------------
pg.letter("b", 94.0, 117.0)
ax = pg.ax(106.0, 66.0, 62.0, 46.0)
lo = min(m.archived.min(), m.stability_floor_A1_e.min()) * 0.5
hi = max(m.archived.max(), m.stability_floor_A1_e.max()) * 2
ax.plot([lo, hi], [lo, hi], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=2)
ax.scatter(m.archived, m.stability_floor_A1_e, s=6, c=DARK_B, alpha=0.5, linewidths=0, zorder=3)
ax.set_xscale("log"); ax.set_yscale("log"); log_ticks(ax)
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0]); ax.set_yticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0])
ax.set_xlabel("float32 control response (e)")
ax.set_ylabel("QSQ stability floor (e)")
open_frame(ax); grid(ax)
note(ax, 0.04, 0.96, "median QSQ / control = %.1f \u00d7 10$^{4}$\nabove the identity: larger under QSQ" % (med_ratio / 1e4),
     size=5.4)

# ---- c: ECDF of the QSQ floor with the three contracts --------------------------------------------------
pg.letter("c", 2.0, 55.0)
ax = pg.ax(14.0, 12.0, 154.0, 36.0)
v = np.sort(a1.stability_floor_A1_e.values)
ax.step(v, np.arange(1, len(v) + 1) / len(v), where="post", color=ELIGIBLE, lw=1.1, zorder=3)
for tau, col in ((1e-4, MID), (1e-3, RED), (1e-2, MID)):
    frac = float((a1.stability_floor_A1_e < tau).mean())
    assert abs(frac - (1 - elig.loc[tau, "frac_non_evaluable_a1"])) < 0.002, (tau, frac)
    ax.axvline(tau, color=col, lw=0.8, ls=(0, (3, 2)), zorder=2)
    ax.plot([v.min(), tau], [frac, frac], color=col, lw=0.5, ls=(0, (1, 1.5)), zorder=2)
    ax.text(tau, 0.03, " %s\n %.0f%% eligible" % (thr_label(tau), 100 * frac), fontsize=5.6, color=col,
            ha="left", va="bottom", linespacing=1.1)
ax.set_xscale("log"); log_ticks(ax, "x")
ax.set_xlim(v.min() * 0.7, v.max() * 1.5); ax.set_ylim(0, 1.02)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(["0", "25", "50", "75", "100%"])
ax.set_xlabel("QSQ stability floor (e)")
ax.set_ylabel("cumulative fraction\nof systems")
open_frame(ax); grid(ax)
ax.text(0.0, 1.02, "all %d development + external systems with a finite floor; the primary contract is $10^{-3}$ e"
        % len(a1), transform=ax.transAxes, ha="left", va="bottom", fontsize=5.4, color=MID)

layout.audit(pg.fig)
pg.save(HERE, "Fig4")
