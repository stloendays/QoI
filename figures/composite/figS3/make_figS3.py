"""Supplementary Figure S3 -- extended operator controls: global, smooth nonlocal and topology-sensitive QoIs.

183 x 118 mm, 2x2:
  a  electron-count deviation vs re-derived Bader error, 2-D density     benchmark/master_benchmark_full.csv
  b  paired material-level R2, Hartree vs Bader, per codec               hartree_potential_expansion/material_smoothness.csv
  c  strictly monotone ladders, Bader vs Hartree, bulk and slab
  d  Bader P90/P10 within 0.5-decade Hartree bins vs bin centre          hartree_potential_expansion/matched_error_dispersion.csv

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS3.py   -> FigS3.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (BADER, CODEC, CODEC_DARK, CODECS, DARK_B, HARTREE, INK, MID, OTHER, RED, TINT_B, Page, grid,  # noqa: E402
                   log_ticks, note, open_frame)

bench = D.master()
assert len(bench) == 6343
e = bench[np.isfinite(bench.electron_count_abs_dev) & np.isfinite(bench.Bader_error_resolved_e)]
ngood = int((e.electron_count_abs_dev < 1e-4).sum())
ndec = int(((e.electron_count_abs_dev < 1e-4) & (e.Bader_error_resolved_e >= 1e-3)).sum())
assert (ngood, ndec) == (3205, 1383)
sm = D.hartree_smoothness()
assert len(sm) == 678
sm["hm"] = D.truthy(sm.hartree_monotone); sm["bm"] = D.truthy(sm.bader_monotone)
disp = D.hartree_dispersion()
d2 = disp[(disp.bader_p90_over_p10 > 0) & (disp.n >= 10)].copy()
d2["xc"] = d2.hartree_log10_bin_left + 0.25
wfrac = d2.loc[d2.bader_p90_over_p10 >= 10, "n"].sum() / d2.n.sum()

pg = Page(183.0, 118.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 40.0
TOP, BOT = 68.0, 12.0

# ---- a: 2-D histogram --------------------------------------------------------------------------------
pg.letter("a", 2.0, 117.0)
ax = pg.ax(LX, TOP, PW, PH)
x = np.log10(np.maximum(e.electron_count_abs_dev, 1e-12)); y = np.log10(np.maximum(e.Bader_error_resolved_e, 1e-12))
cmap = LinearSegmentedColormap.from_list("qoi_blue", ["#FFFFFF", TINT_B, DARK_B])
h = ax.hist2d(x, y, bins=48, cmap=cmap, norm=LogNorm(), zorder=2)
ax.axvline(-4, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=3); ax.axhline(-3, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=3)
ax.set_xticks([-12, -9, -6, -3, 0]); ax.set_xticklabels([r"$\leq10^{-12}$", r"$10^{-9}$", r"$10^{-6}$", r"$10^{-3}$", r"$10^{0}$"])
ax.set_yticks([-12, -9, -6, -3, 0]); ax.set_yticklabels([r"$\leq10^{-12}$", r"$10^{-9}$", r"$10^{-6}$", r"$10^{-3}$", r"$10^{0}$"])
ax.set_xlabel(r"electron-count deviation $|\Delta N|$ (e)")
ax.set_ylabel("re-derived Bader error (e)")
open_frame(ax); grid(ax)
note(ax, 0.03, 0.96, "$|\\Delta N| < 10^{-4}$ e but Bader $\\geq 10^{-3}$ e:\n%d / %d = %.2f%%" % (ndec, ngood, 100 * ndec / ngood), size=5.4)
cax = pg.ax(LX + PW - 24.0, TOP + 4.0, 20.0, 2.0)
cb = pg.fig.colorbar(h[3], cax=cax, orientation="horizontal")
cb.ax.tick_params(labelsize=5.0, length=1.5, pad=1); cb.outline.set_linewidth(0.4)
cax.set_title("rows per bin", fontsize=5.2, pad=1.5)

# ---- b: paired R2 ------------------------------------------------------------------------------------
pg.letter("b", 94.0, 117.0)
ax = pg.ax(RX + 14.0, TOP, PH, PH)
ax.plot([0, 1], [0, 1], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=2)
for c in CODECS:
    s = sm[sm.codec == c]
    ax.scatter(s.bader_R2, s.hartree_R2, s=6, c=CODEC_DARK[c], alpha=0.55, linewidths=0, zorder=3)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal")
ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
ax.set_xlabel(r"Bader log-log $R^2$"); ax.set_ylabel(r"Hartree log-log $R^2$")
open_frame(ax); grid(ax)
handles = [Line2D([], [], marker="o", ls="none", color=CODEC_DARK[c], ms=3.2, label=c) for c in CODECS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right")
ax.text(0.03, 0.12, "n = 678 material\u2013codec pairs", transform=ax.transAxes, fontsize=5.4, color=MID)

# ---- c: monotonicity ----------------------------------------------------------------------------------
pg.letter("c", 2.0, 61.0)
for k, st in enumerate(("bulk", "slab")):
    ax = pg.ax(LX + k * 36.0, BOT, 30.0, PH)
    for c in CODECS:
        s = sm[(sm.codec == c) & (sm.system_type == st)]
        ax.plot([0, 1], [s.bm.mean(), s.hm.mean()], color=CODEC_DARK[c], lw=0.9, marker="o", ms=3.2, zorder=3)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Bader", "Hartree"]); ax.set_xlim(-0.4, 1.4)
    ax.set_ylim(0, 1.02); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0", "20", "40", "60", "80", "100%"] if k == 0 else [])
    ax.set_title(st, loc="left", fontsize=6.0, fontweight="bold", pad=2)
    open_frame(ax); grid(ax, "y")
    if k == 0:
        ax.set_ylabel("strictly monotone ladders")
    if k == 1:
        handles = [Line2D([], [], marker="o", color=CODEC_DARK[c], ms=3.2, lw=0.9, label=c) for c in CODECS]
        layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right")

# ---- d: dispersion vs Hartree bin ----------------------------------------------------------------------
pg.letter("d", 94.0, 61.0)
ax = pg.ax(RX, BOT, PW, PH)
ax.axhline(10, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=2)
for c in CODECS:
    for st, mk in (("bulk", "o"), ("slab", "^")):
        s = d2[(d2.codec == c) & (d2.system_type == st)]
        ax.scatter(s.xc, s.bader_p90_over_p10, s=3 + 0.02 * s.n, c=CODEC_DARK[c], marker=mk, alpha=0.6, linewidths=0, zorder=3)
ax.set_yscale("log"); log_ticks(ax, "y", subs=())
ax.set_xlabel(r"$\log_{10}$ relative Hartree RMSE (bin centre)")
ax.set_ylabel("Bader P90 / P10 within bin")
open_frame(ax); grid(ax)
note(ax, 0.03, 0.96, "%.1f%% of rows lie in bins with P90/P10 \u2265 10\nmarker size = rows in bin (\u2265 10)" % (100 * wfrac), size=5.4)
handles = [Line2D([], [], marker="o", ls="none", color=MID, ms=3, label="bulk"),
           Line2D([], [], marker="^", ls="none", color=MID, ms=3, label="slab")]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right", ncol=2)

layout.audit(pg.fig)
pg.save(HERE, "FigS3")
