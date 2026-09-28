"""Supplementary Figure S1 -- QSQ defines the measurable Bader-fidelity landscape.

183 x 90 mm, L-shape:
  a  paired float32-control vs QSQ floor, by stratum          stability_floor_A_archived_float32.csv, stability_floor_A1.csv
  b  overall non-evaluable fraction, control vs QSQ, per tau  eligibility_summary_A1.csv
  c  QSQ non-evaluable fraction by stratum x tau (heatmap)    eligibility_summary_A1.csv

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS1.py   -> FigS1.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (DARK_B, DARK_G, INK, MID, OTHER, PALE, RED, TINT_R, Page, grid, log_ticks, open_frame,  # noqa: E402
                   thr_label)

a1 = D.floor_a1()[["material_id", "corpus", "stability_floor_A1_e"]]
a0 = D.floor_archived()[["material_id", "floor_resolved_e"]]
m = a1.merge(a0, on="material_id")
m = m[(m.stability_floor_A1_e > 0) & (m.floor_resolved_e > 0)]
assert len(m) >= 250
elig = D.eligibility_summary()
STRATA = (("dev_bulk", "development bulk", DARK_B, "o"), ("dev_slab", "development slab", DARK_G, "^"),
          ("ext_bulk", "external bulk", PALE, "s"), ("ext_vacuum", "external vacuum-2D", OTHER, "D"))
TAU = (1e-4, 1e-3, 1e-2)

pg = Page(183.0, 90.0)

# ---- a ---------------------------------------------------------------------------------------
pg.letter("a", 2.0, 89.0)
ax = pg.ax(14.0, 12.0, 70.0, 70.0)
lo, hi = min(m.floor_resolved_e.min(), m.stability_floor_A1_e.min()) * 0.5, max(m.floor_resolved_e.max(), m.stability_floor_A1_e.max()) * 2
ax.plot([lo, hi], [lo, hi], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=2)
handles = []
for key, lab, col, mk in STRATA:
    s = m[m.corpus == key]
    if len(s) == 0:
        continue
    ax.scatter(s.floor_resolved_e, s.stability_floor_A1_e, s=9, c=col, marker=mk, alpha=0.6, linewidths=0, zorder=3)
    handles.append(Line2D([], [], marker=mk, ls="none", color=col, ms=3.5, label="%s (n = %d)" % (lab, len(s))))
ax.set_xscale("log"); ax.set_yscale("log"); log_ticks(ax)
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0]); ax.set_yticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0])
ax.set_xlabel("order-preserving float32 control response (e)")
ax.set_ylabel("QSQ stability floor (e)")
open_frame(ax); grid(ax)
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right")
# everything lies above the identity, so the lower-right triangle is empty
ax.text(0.03, 0.97, "n = %d paired systems; dashed line = equality" % len(m), transform=ax.transAxes, fontsize=5.4,
        color=MID, va="top")

# ---- b ---------------------------------------------------------------------------------------
pg.letter("b", 92.0, 89.0)
ax = pg.ax(112.0, 54.0, 66.0, 28.0)
ov = elig[elig.stratum == "overall"].set_index("threshold_e")
ys = (2, 1, 0)
for y, t in zip(ys, TAU):
    r = ov.loc[t]
    ax.plot([r.frac_non_evaluable_a_archived, r.frac_non_evaluable_a1], [y, y], color=OTHER, lw=1.4, zorder=2,
            solid_capstyle="round")
    ax.scatter([r.frac_non_evaluable_a_archived], [y], s=24, c=MID, zorder=4, linewidths=0)
    ax.scatter([r.frac_non_evaluable_a1], [y], s=24, c=RED, zorder=4, linewidths=0)
    ax.text(r.frac_non_evaluable_a1 + 0.03, y, "%.1f%%" % (100 * r.frac_non_evaluable_a1), ha="left", va="center", fontsize=5.8)
ax.set_yticks(ys); ax.set_yticklabels([thr_label(t) for t in TAU]); ax.set_ylim(-0.6, 2.6)
ax.set_xlim(0, 1.0); ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); ax.set_xticklabels(["0", "20", "40", "60", "80", "100%"])
ax.set_xlabel("non-evaluable fraction of 319 systems")
open_frame(ax); grid(ax, "x")
handles = [Line2D([], [], marker="o", ls="none", color=MID, ms=3.5, label="float32 control"),
           Line2D([], [], marker="o", ls="none", color=RED, ms=3.5, label="QSQ")]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right")

# ---- c: heatmap -------------------------------------------------------------------------------------
pg.letter("c", 92.0, 44.0)
ax = pg.ax(112.0, 12.0, 66.0, 24.0)
cmap = LinearSegmentedColormap.from_list("qoi_red", ["#FFFFFF", TINT_R, RED])
M = np.zeros((4, 3))
for i, (key, lab, _, _) in enumerate(STRATA):
    for j, t in enumerate(TAU):
        r = elig[(elig.stratum == key) & (elig.threshold_e == t)].iloc[0]
        M[i, j] = r.frac_non_evaluable_a1
        ax.text(j, i, "%.1f%%\n(%d / %d)" % (100 * r.frac_non_evaluable_a1, r.non_evaluable, r.n), ha="center", va="center",
                fontsize=5.4, color=INK, linespacing=1.1)
ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="auto", zorder=0)
ax.set_xticks(range(3)); ax.set_xticklabels([thr_label(t) for t in TAU])
ax.set_yticks(range(4)); ax.set_yticklabels([s[1] for s in STRATA])
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xlabel(r"Bader tolerance $\tau$")
ax.set_title("QSQ non-evaluable fraction by stratum", loc="left", fontsize=5.8, pad=2)

layout.audit(pg.fig)
pg.save(HERE, "FigS1")
