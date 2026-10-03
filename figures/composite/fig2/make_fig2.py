"""Figure 2 -- downstream operator structure controls how density error propagates.

Composite, 183 x 150 mm, four coordinate sub-claims (a 2x2 that is really 2x2):
  a  electron-count conservation does not imply Bader fidelity   master_benchmark_full.csv
  b  Hartree error is first-order in realized L-inf                hartree_potential_expansion/rows.csv
  c  Hartree is smoother than Bader at the material level          material_smoothness.csv
  d  matched Hartree error still leaves Bader dispersed            matched_error_dispersion.csv

2026-09-30 rebuild with figure-studio advanced.py: every point drawn and density-coloured (a, b);
per-codec x system slopes with material-cluster bootstrap CIs as an inset forest (b); raincloud of
1 - R^2 on a log axis with paired Wilcoxon tests (c); bubble matrix of Bader P90/P10 over matched
Hartree bins, colour centred on P90/P10 = 10 (d).

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig2.py   -> Fig2.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.colors import TwoSlopeNorm
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import advanced as A  # noqa: E402
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import BADER, CODECS, HARTREE, INK, MID, RED, Page, grid, log_ticks, note, open_frame  # noqa: E402

rng = np.random.default_rng(20260930)

# ---- data ---------------------------------------------------------------------------------
bench = D.master()
a = bench[np.isfinite(bench.electron_count_abs_dev) & np.isfinite(bench.Bader_error_resolved_e)
          & (bench.electron_count_abs_dev > 0) & (bench.Bader_error_resolved_e > 0)]
lo_n = a.electron_count_abs_dev <= 1e-4
hi_b = a.Bader_error_resolved_e >= 1e-3
quad = {"tl": int((lo_n & hi_b).sum()), "bl": int((lo_n & ~hi_b).sum()),
        "tr": int((~lo_n & hi_b).sum()), "br": int((~lo_n & ~hi_b).sum())}
n_pres, n_fail = int(lo_n.sum()), quad["tl"]
assert (n_pres, n_fail) == (3205, 1383), (n_pres, n_fail)          # frozen manuscript anchor
assert sum(quad.values()) == len(a) == 6343

gp = D.hartree_rows()
b = gp[np.isfinite(gp.realized_Linf) & np.isfinite(gp.potential_rel_RMSE)
       & (gp.realized_Linf > 0) & (gp.potential_rel_RMSE > 0)].reset_index(drop=True)
# the frozen pooled statistics (slope 1.02, r 0.89) regress on absolute realized L-inf, so plot that
lx, ly = np.log10(b.realized_Linf.values), np.log10(b.potential_rel_RMSE.values)
pooled_slope = np.polyfit(lx, ly, 1)[0]
pooled_r = np.corrcoef(lx, ly)[0, 1]
assert abs(pooled_slope - 1.02) < 0.01 and abs(pooled_r - 0.89) < 0.01, (pooled_slope, pooled_r)
assert len(b) == 6270 and b.material_id.nunique() == 254


def cluster_boot_slope(rows, n_boot=2000):
    """Log-log slope with a 95 % CI from resampling materials (rows of one material move together)."""
    x, y = np.log10(rows.realized_Linf.values), np.log10(rows.potential_rel_RMSE.values)
    ids = rows.material_id.values
    mats = np.unique(ids)
    where = {m: np.flatnonzero(ids == m) for m in mats}
    boots = []
    for _ in range(n_boot):
        ii = np.concatenate([where[m] for m in rng.choice(mats, len(mats))])
        boots.append(np.polyfit(x[ii], y[ii], 1)[0])
    return np.polyfit(x, y, 1)[0], *np.percentile(boots, [2.5, 97.5])


groups = [(c, st) for st in ("bulk", "slab") for c in CODECS]
slopes = {g: cluster_boot_slope(b[(b.codec == g[0]) & (b.system_type == g[1])]) for g in groups}
pooled = cluster_boot_slope(b)
assert abs(pooled[0] - pooled_slope) < 1e-12
assert 0.99 < pooled[1] < 1.02 and 1.02 < pooled[2] < 1.05, pooled

sm = D.hartree_smoothness()
assert len(sm) == 678
smooth = {}
for c in CODECS:
    s = sm[sm.codec == c]
    w = stats.wilcoxon(s.bader_R2, s.hartree_R2)
    smooth[c] = dict(h=np.log10(1 - s.hartree_R2.values), bd=np.log10(1 - s.bader_R2.values),
                     worse=int((s.bader_R2 < s.hartree_R2).sum()), n=len(s), p=w.pvalue)
assert [(smooth[c]["worse"], smooth[c]["n"]) for c in CODECS] == [(232, 241), (202, 219), (212, 218)]
assert max(smooth[c]["p"] for c in CODECS) < 1e-30

disp = D.hartree_dispersion()
disp = disp[np.isfinite(disp.bader_p90_over_p10) & (disp.bader_p90_over_p10 > 0)]
frac_ge10 = 100.0 * disp.loc[disp.bader_p90_over_p10 >= 10, "n"].sum() / disp.n.sum()
assert abs(frac_ge10 - 55.4) < 0.1, frac_ge10
bins = np.sort(disp.hartree_log10_bin_left.unique())
rows = [(c, st) for st in ("bulk", "slab") for c in CODECS]
S = np.full((len(rows), len(bins)), np.nan)
C = np.full_like(S, np.nan)
for i, (c, st) in enumerate(rows):
    for _, r in disp[(disp.codec == c) & (disp.system_type == st)].iterrows():
        j = int(np.searchsorted(bins, r.hartree_log10_bin_left))
        S[i, j], C[i, j] = r.n, np.log10(r.bader_p90_over_p10)
assert np.nansum(S) == disp.n.sum() == 6229

# ---- page --------------------------------------------------------------------------------
pg = Page(183.0, 150.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 52.0
TOP, BOT = 92.0, 16.0

# ---- a: electron count vs Bader, every point, quadrant counts ------------------------------
pg.letter("a", 2.0, 149.0)
ax = pg.ax(LX, TOP, PW, PH)
A.density_scatter(ax, a.electron_count_abs_dev.values, a.Bader_error_resolved_e.values, logx=True, logy=True,
                  s=2.0)
xmin, xmax = a.electron_count_abs_dev.min(), a.electron_count_abs_dev.max()
ymin, ymax = a.Bader_error_resolved_e.min(), a.Bader_error_resolved_e.max()
ax.axvline(1e-4, color=INK, lw=0.6, ls=(0, (3, 2)), zorder=3)
ax.axhline(1e-3, color=INK, lw=0.6, ls=(0, (3, 2)), zorder=3)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(xmin * 0.5, xmax * 3)
ax.set_ylim(ymin * 0.5, ymax * 30)
log_ticks(ax)
ax.set_xlabel(r"electron-count deviation $|\Delta N|$ (e)")
ax.set_ylabel("re-derived Bader error (e)")
open_frame(ax)
# the claim cell (|dN| < 1e-4 yet Bader >= 1e-3) is the one red element; the other three are context
note(ax, 0.03, 0.97, "%s / %s = %.2f%%\n$|\\Delta N| < 10^{-4}$ e, Bader $\\geq 10^{-3}$ e"
     % (format(n_fail, ","), format(n_pres, ","), 100.0 * n_fail / n_pres), size=5.4, color=RED)
note(ax, 0.97, 0.97, format(quad["tr"], ","), ha="right", size=5.4)
note(ax, 0.03, 0.04, format(quad["bl"], ","), va="bottom", size=5.4)
note(ax, 0.97, 0.04, format(quad["br"], ","), ha="right", va="bottom", size=5.4)

# ---- b: Hartree first-order response, every row; right strip: slopes with cluster CIs ---------
pg.letter("b", 94.0, 149.0)
ax = pg.ax(RX, TOP, 45, PH)
A.density_scatter(ax, b.realized_Linf.values, b.potential_rel_RMSE.values, logx=True, logy=True, s=2.0)
xs = np.logspace(lx.min(), lx.max(), 50)
k, b0 = np.polyfit(lx, ly, 1)
ax.plot(xs, 10 ** (k * np.log10(xs) + b0), color=INK, lw=0.8, ls=(0, (4, 2)), zorder=5)
ax.set_xscale("log")
ax.set_yscale("log")
log_ticks(ax)
ax.set_xticks([1e-6, 1e-4, 1e-2, 1e0, 1e2])
ax.set_yticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2])
ax.set_ylim(2e-11, 3e-1)
ax.set_xlabel(r"realized $L_\infty$ (field units)")
ax.set_ylabel("Hartree-potential relative RMSE")
open_frame(ax)
# the data run diagonally from bottom-left to top-right, so the upper-left corner is empty
note(ax, 0.03, 0.97, "pooled slope %.2f\nPearson $\\mathit{r}$ = %.2f\n%s rows\n%d materials"
     % (pooled_slope, pooled_r, format(len(b), ","), b.material_id.nunique()), size=5.4)
fx = pg.ax(RX + 59, TOP + 9, 14, PH - 9)
A.forest(fx, ["%s %s" % g for g in groups], [slopes[g][0] for g in groups], [slopes[g][1] for g in groups],
         [slopes[g][2] for g in groups], null=1.0, pooled=pooled, pooled_label="pooled", numbers=False,
         ms_range=(2.6, 0.0))
fx.set_xlim(0.85, 1.17)
fx.set_xticks([0.9, 1.0, 1.1])
fx.set_xticklabels(["0.9", "1", "1.1"])
fx.tick_params(axis="both", labelsize=5.6, pad=1.2)
fx.set_xlabel("log\u2013log slope\n(95% CI)", fontsize=6.0, labelpad=1.5)

# ---- c: material-level deviation from a power law, Hartree vs Bader, every pair ----------------
pg.letter("c", 2.0, 73.0)
ax = pg.ax(LX + 14, BOT, PW - 14, PH + 2)
data, labels, cols, pos = [], [], [], []
y0 = 0.0
for c in reversed(CODECS):
    for key, lab, col in (("bd", "Bader", BADER), ("h", "Hartree", HARTREE)):
        data.append(smooth[c][key])
        labels.append(lab)
        cols.append(col)
        pos.append(y0)
        y0 += 1.0
    y0 += 0.55
A.raincloud(ax, data, labels, colors=cols, positions=pos, cloud=0.5, rain=0.3, point_size=1.6, point_alpha=0.55,
            swarm_d=0.006, bounds=(-np.inf, 0.0), value_label="1 $-$ $\\mathit{R}^2$ of the material-level log\u2013log fit")
ax.set_xlim(-4.3, 0.25)
ax.set_xticks([-4, -3, -2, -1, 0])
ax.set_xticklabels([r"$10^{%d}$" % k if k else "1" for k in (-4, -3, -2, -1, 0)])
for i, c in enumerate(reversed(CODECS)):
    yb = pos[2 * i]
    s = smooth[c]
    pg.fig.text(4.0 / pg.W, (BOT + (PH + 2) * ((yb + 0.5) - ax.get_ylim()[0]) / np.ptp(ax.get_ylim())) / pg.H, c,
                ha="left", va="center", fontsize=6.5, fontweight="bold")
    ax.text(-4.22, yb - 0.02, "Bader > Hartree in\n%d / %d materials, $p$ < 10$^{-30}$" % (s["worse"], s["n"]),
            ha="left", va="center", fontsize=5.3, color=INK, linespacing=1.15)
grid(ax, "x")

# ---- d: Bader dispersion over matched Hartree bins ------------------------------------------------
pg.letter("d", 94.0, 73.0)
ax = pg.ax(RX + 6, BOT + 4, PW - 14, PH - 14)
norm = TwoSlopeNorm(vmin=0.0, vcenter=1.0, vmax=5.0)            # white at P90/P10 = 10
sc = A.bubble_matrix(ax, S, C, ["%s %s" % r for r in rows], ["" for _ in bins], norm=norm, smax=34, s_ref=188,
                     xrot=0)
ax.set_xticks(range(len(bins)))
ax.set_xticklabels([(r"$10^{%d}$" % v) if float(v).is_integer() and int(v) % 2 == 0 else "" for v in bins])
ax.tick_params(axis="x", pad=1.5)
ax.set_xlabel("Hartree relative RMSE bin (0.5 decade, lower edge)")
cb = A.cbar(pg.ax(RX + PW - 5.5, BOT + 5, 1.8, 28), sc, "Bader P90 / P10", ticks=[0, 1, 2, 3, 4, 5])
cb.ax.set_yticklabels([r"$10^{%d}$" % k for k in range(6)])
A.size_key(ax, [20, 80, 180], 188, smax=34, fmt="%d rows", loc="lower left", bbox_to_anchor=(-0.02, 1.0),
           ncol=3, frame=False, borderaxespad=0.2)
ax.text(0.0, 1.19, "%.1f%% of rows lie in bins with Bader P90/P10 \u2265 10 (white = 10)" % frac_ge10,
        transform=ax.transAxes, ha="left", va="bottom", fontsize=5.4, color=INK)

layout.audit(pg.fig)
pg.save(HERE, "Fig2")

print("slopes (95% material-cluster CI):")
for g in groups:
    print("  %-5s %-4s %.3f [%.3f, %.3f]" % (g[0], g[1], *slopes[g]))
print("  pooled     %.3f [%.3f, %.3f]" % pooled)
for c in CODECS:
    print("  %s: Bader R2 < Hartree R2 in %d/%d, Wilcoxon p = %.1e" % (c, smooth[c]["worse"], smooth[c]["n"],
                                                                    smooth[c]["p"]))
