"""Figure 2 -- downstream operator structure controls how density error propagates.

Composite, 183 x 150 mm, four coordinate sub-claims (a 2x2 that is really 2x2):
  a  electron-count conservation does not imply Bader fidelity   master_benchmark_full.csv
  b  Hartree error is first-order in realized L-inf                hartree_potential_expansion/rows.csv
  c  Hartree is smoother than Bader at the material level          material_smoothness.csv
  d  matched Hartree error still leaves Bader dispersed            matched_error_dispersion.csv

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig2.py   -> Fig2.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (BADER, CODEC, CODEC_DARK, CODECS, GRID, HARTREE, INK, MID, OTHER, RED, TINT_G,  # noqa: E402
                   Page, grid, log_ticks, note, open_frame)

rng = np.random.default_rng(20260909)

# ---- data ---------------------------------------------------------------------------------
bench = D.master()
a = bench[np.isfinite(bench.electron_count_abs_dev) & np.isfinite(bench.Bader_error_resolved_e)
          & (bench.electron_count_abs_dev > 0) & (bench.Bader_error_resolved_e > 0)]
pres = a.electron_count_abs_dev <= 1e-4
n_pres, n_fail = int(pres.sum()), int((a.Bader_error_resolved_e[pres] >= 1e-3).sum())
frac_fail = 100.0 * n_fail / n_pres
assert (n_pres, n_fail) == (3205, 1383), (n_pres, n_fail)          # frozen manuscript anchor

gp = D.hartree_rows()
b = gp[np.isfinite(gp.realized_Linf) & np.isfinite(gp.potential_rel_RMSE)
       & (gp.realized_Linf > 0) & (gp.potential_rel_RMSE > 0)]
# the frozen pooled statistics (slope 1.02, r 0.89) regress on absolute realized L-inf, so plot that
lx, ly = np.log10(b.realized_Linf.values), np.log10(b.potential_rel_RMSE.values)
pooled_slope = np.polyfit(lx, ly, 1)[0]
pooled_r = np.corrcoef(lx, ly)[0, 1]
assert abs(pooled_slope - 1.02) < 0.01 and abs(pooled_r - 0.89) < 0.01, (pooled_slope, pooled_r)

sm = D.hartree_smoothness()
disp = D.hartree_dispersion()
disp = disp[np.isfinite(disp.bader_p90_over_p10) & (disp.bader_p90_over_p10 > 0)]
frac_ge10 = 100.0 * disp.loc[disp.bader_p90_over_p10 >= 10, "n"].sum() / disp.n.sum()
assert abs(frac_ge10 - 55.4) < 0.1, frac_ge10

# ---- page --------------------------------------------------------------------------------
pg = Page(183.0, 150.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 52.0
TOP, BOT = 92.0, 14.0

# ---- a: electron count vs Bader --------------------------------------------------------------
pg.letter("a", 2.0, 149.0)
ax = pg.ax(LX, TOP, PW, PH)
xmin, xmax = a.electron_count_abs_dev.min(), a.electron_count_abs_dev.max()
ymin, ymax = a.Bader_error_resolved_e.min(), a.Bader_error_resolved_e.max()
ax.add_patch(__import__("matplotlib").patches.Rectangle((xmin * 0.5, 1e-3), 1e-4 - xmin * 0.5, ymax * 3 - 1e-3,
                                                       facecolor=TINT_G, edgecolor="none", zorder=0))
ax.scatter(a.electron_count_abs_dev, a.Bader_error_resolved_e, s=2.2, c=OTHER, alpha=0.35,
           linewidths=0, rasterized=True, zorder=2)
ax.axvline(1e-4, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=3)
ax.axhline(1e-3, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=3)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(xmin * 0.5, xmax * 3); ax.set_ylim(ymin * 0.5, ymax * 3)
log_ticks(ax)
ax.set_xlabel(r"electron-count deviation $|\Delta N|$ (e)")
ax.set_ylabel("re-derived Bader error (e)")
open_frame(ax); grid(ax)
note(ax, 0.03, 0.96, "%d / %d = %.2f%% of reconstructions with\n$|\\Delta N| < 10^{-4}$ e still exceed $10^{-3}$ e Bader error"
     % (n_fail, n_pres, frac_fail), size=5.4)
ax.text(1e-4, ymin * 0.7, r" $|\Delta N| = 10^{-4}$ e", fontsize=5.4, color=RED, ha="left", va="bottom")
ax.text(xmax * 2.6, 1e-3, r"$10^{-3}$ e ", fontsize=5.4, color=RED, ha="right", va="bottom")

# ---- b: Hartree first-order response -------------------------------------------------------------
pg.letter("b", 94.0, 149.0)
ax = pg.ax(RX, TOP, PW, PH)
for c in CODECS:
    sub = b[b.codec == c]
    show = sub.sample(n=min(len(sub), 1200), random_state=20260909)
    for st, mk in (("bulk", "o"), ("slab", "^")):
        s2 = show[show.system_type == st]
        ax.scatter(s2.realized_Linf, s2.potential_rel_RMSE, s=3.0, marker=mk, c=CODEC[c],
                   alpha=0.30, linewidths=0, rasterized=True, zorder=2)
    k, b0 = np.polyfit(np.log10(sub.realized_Linf), np.log10(sub.potential_rel_RMSE), 1)
    xs = np.logspace(np.log10(sub.realized_Linf.min()), np.log10(sub.realized_Linf.max()), 50)
    ax.plot(xs, 10 ** (k * np.log10(xs) + b0), color=CODEC_DARK[c], lw=1.0, zorder=4)
xs = np.logspace(lx.min(), lx.max(), 50)
k, b0 = np.polyfit(lx, ly, 1)
ax.plot(xs, 10 ** (k * np.log10(xs) + b0), color=INK, lw=0.8, ls=(0, (4, 2)), zorder=5)
ax.set_xscale("log"); ax.set_yscale("log")
log_ticks(ax)
ax.set_xlabel(r"realized $L_\infty$ (field units)")
ax.set_ylabel("Hartree-potential relative RMSE")
open_frame(ax); grid(ax)
note(ax, 0.97, 0.05, "pooled log-log slope %.2f\nPearson r = %.2f" % (pooled_slope, pooled_r), ha="right", va="bottom")
handles = [Line2D([], [], color=CODEC_DARK[c], lw=1.0, label=c) for c in CODECS]
handles += [Line2D([], [], color=INK, lw=0.8, ls=(0, (4, 2)), label="pooled fit"),
            Line2D([], [], marker="o", ls="none", color=MID, ms=3, label="bulk"),
            Line2D([], [], marker="^", ls="none", color=MID, ms=3, label="slab")]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper left", ncol=2)
# the data run diagonally from bottom-left to top-right, so the upper-left corner is empty

# ---- c: material-level R2, Hartree vs Bader, per codec -----------------------------------------------
pg.letter("c", 2.0, 71.0)
ax = pg.ax(LX, BOT, PW, PH)
pos, ticks, tlab = [], [], []
for i, c in enumerate(CODECS):
    sub = sm[sm.codec == c]
    for j, (col, colr, lab) in enumerate((("hartree_R2", HARTREE, "Hartree"), ("bader_R2", BADER, "Bader"))):
        v = sub[col].values
        v = v[np.isfinite(v)]
        x0 = i * 3.0 + j * 1.0
        vp = ax.violinplot([v], positions=[x0], widths=0.85, showextrema=False, points=200)
        for body in vp["bodies"]:
            body.set_facecolor(colr); body.set_edgecolor("none"); body.set_alpha(0.35)
        ax.boxplot([v], positions=[x0], widths=0.22, showfliers=False, patch_artist=True,
                   boxprops=dict(facecolor="white", edgecolor=colr, linewidth=0.7),
                   whiskerprops=dict(color=colr, linewidth=0.6), capprops=dict(color=colr, linewidth=0.6),
                   medianprops=dict(color=INK, linewidth=0.9), zorder=4)
        jitter = rng.uniform(-0.28, 0.28, len(v))
        ax.scatter(x0 + jitter, v, s=1.6, c=colr, alpha=0.30, linewidths=0, zorder=3, rasterized=True)
        ax.text(x0, -0.05, lab, ha="center", va="top", fontsize=6.0, color=colr)
    ax.text(i * 3.0 + 0.5, 1.055, c, ha="center", va="bottom", fontsize=6.5, fontweight="bold")
ax.set_xlim(-0.8, 7.8); ax.set_ylim(-0.02, 1.02)
ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
ax.set_ylabel(r"material-level log-log $R^2$")
open_frame(ax); grid(ax, "y")
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.text(0.99, 0.04, "n = %d material\u2013codec pairs" % len(sm), transform=ax.transAxes, ha="right",
        va="bottom", fontsize=5.4, color=MID)

# ---- d: Bader dispersion within matched Hartree bins -------------------------------------------------
pg.letter("d", 94.0, 71.0)
ax = pg.ax(RX, BOT, PW, PH)
ax.axhline(1.0, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=3)          # y is log10(P90/P10)
ax.text(5.55, 1.0, "P90/P10 = 10 ", fontsize=5.4, color=RED, ha="right", va="bottom")
i = 0
for st in ("bulk", "slab"):
    for c in CODECS:
        v = disp[(disp.codec == c) & (disp.system_type == st)].bader_p90_over_p10.values
        lv = np.log10(v)
        vp = ax.violinplot([lv], positions=[i], widths=0.85, showextrema=False, points=200)
        for body in vp["bodies"]:
            body.set_facecolor(CODEC[c]); body.set_edgecolor("none"); body.set_alpha(0.35)
        ax.boxplot([lv], positions=[i], widths=0.22, showfliers=False, patch_artist=True,
                   boxprops=dict(facecolor="white", edgecolor=CODEC_DARK[c], linewidth=0.7),
                   whiskerprops=dict(color=CODEC_DARK[c], linewidth=0.6),
                   capprops=dict(color=CODEC_DARK[c], linewidth=0.6),
                   medianprops=dict(color=INK, linewidth=0.9), zorder=4)
        ax.scatter(i + rng.uniform(-0.28, 0.28, len(lv)), lv, s=2.4, c=CODEC_DARK[c], alpha=0.5,
                   linewidths=0, zorder=3)
        ax.text(i, -0.55, "%s\n%s" % (c, st), ha="center", va="top", fontsize=5.6, color=INK, linespacing=1.1)
        i += 1
ax.set_xlim(-0.7, 5.7); ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
ax.set_ylim(-0.4, 5.6)
ax.set_yticks([0, 1, 2, 3, 4, 5]); ax.set_yticklabels([r"$10^{%d}$" % k for k in range(6)])
ax.set_ylabel("Bader error dispersion within\n0.5-decade Hartree bins (P90 / P10)")
open_frame(ax); grid(ax, "y")
note(ax, 0.03, 0.96, "%.1f%% of rows sit in bins with\nBader P90/P10 \u2265 10" % frac_ge10, size=5.4)

layout.audit(pg.fig)
pg.save(HERE, "Fig2")
