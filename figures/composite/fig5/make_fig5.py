"""Figure 5 -- topology-dependent basin migration explains irregular amplification of re-derived Bader error.

2x2 (four coordinate claims), 183 x 150 mm:
  a  re-solving amplifies the fixed-basin error       mechanism/basin_error_decomposition_summary.csv
  b  per-atom: domain term dominates large deviations  mechanism/basin_error_decomposition_per_atom.csv
  c  three representative full ladders                 benchmark/master_benchmark_full.csv
  d  jump severity vs basin reassignment               benchmark/master_benchmark_full.csv

Representative ladders in c are chosen exactly as the frozen R script chose them: among ZFP
material ladders with >= 5 rungs, the smallest, median and largest maximum consecutive jump.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig5.py   -> Fig5.{svg,pdf,png}
"""
import os
import sys

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (CODEC, CODEC_DARK, CODECS, DARK_B, DARK_G, GREEN, INK, MID, OTHER, PALE, PALE_G, RED,  # noqa: E402
                   Page, grid, log_ticks, note, open_frame)

# ---- data ---------------------------------------------------------------------------------
ms = D.mechanism_summary()
ma = D.mechanism_per_atom()
bench = D.master()
bench["codec"] = bench.codec.str.upper()
bench["realized_rel"] = bench.realized_Linf / bench.value_ptp

a = pd.DataFrame(dict(total=ms.dq_total_max_e.abs(), integrand=ms.dq_integrand_max_e.abs(),
                      reassign=ms.frac_voxels_reassigned))
a = a[(a.total > 0) & (a.integrand > 0) & np.isfinite(a.reassign)]

b = ma[np.isfinite(ma.dq_integrand_e) & np.isfinite(ma.dq_domain_e) & np.isfinite(ma.dq_total_e)]
large = b.dq_total_e.abs() >= 1e-3

ok = (bench.codec.isin(CODECS) & (bench.realized_rel > 0) & (bench.Bader_error_resolved_e > 0)
      & np.isfinite(bench.frac_voxels_reassigned))
st = bench[ok].sort_values(["material_id", "codec", "realized_rel"]).copy()
g = st.groupby(["material_id", "codec"])
st["prev_err"] = g.Bader_error_resolved_e.shift(1)
st["jump"] = np.maximum(st.Bader_error_resolved_e / st.prev_err, st.prev_err / st.Bader_error_resolved_e)
pairs = st.groupby(["material_id", "codec"]).agg(n=("Bader_error_resolved_e", "size"), max_jump=("jump", "max")).reset_index()
pairs = pairs[(pairs.n >= 5) & np.isfinite(pairs.max_jump) & (pairs.max_jump >= 1)]
pool = pairs[pairs.codec == "ZFP"].sort_values("max_jump").reset_index(drop=True)
idx = [0, int(round((len(pool) + 1) / 2)) - 1, len(pool) - 1]
chosen = pool.iloc[idx].assign(case=["smooth", "intermediate", "jump"])

dd = st[np.isfinite(st.jump) & (st.jump >= 1) & (st.frac_voxels_reassigned > 0)]
rho = spearmanr(np.log10(dd.frac_voxels_reassigned), np.log10(dd.jump)).statistic
assert abs(rho - 0.18) < 0.01, rho

# ---- page --------------------------------------------------------------------------------
pg = Page(183.0, 150.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 52.0
TOP, BOT = 92.0, 14.0

# ---- a --------------------------------------------------------------------------------------
pg.letter("a", 2.0, 149.0)
ax = pg.ax(LX, TOP, PW, PH)
lo, hi = a.integrand.min() * 0.5, a.total.max() * 2
ax.plot([lo, hi], [lo, hi], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=2)
sc = ax.scatter(a.integrand, a.total, s=9, c=a.reassign, cmap="Greens", vmin=0, vmax=0.35, alpha=0.85,
                linewidths=0.3, edgecolors=DARK_G, zorder=3)
ax.set_xscale("log"); ax.set_yscale("log"); log_ticks(ax)
ax.set_xlim(lo, hi); ax.set_ylim(a.total.min() * 0.5, hi)
ax.set_xlabel("fixed-basin (integrand) error (e)")
ax.set_ylabel("re-derived Bader error (e)")
open_frame(ax); grid(ax)
cax = pg.ax(LX + 42.0, TOP + 5.0, 22.0, 2.2)
cb = pg.fig.colorbar(sc, cax=cax, orientation="horizontal")
cb.set_ticks([0, 0.1, 0.2, 0.3]); cb.ax.tick_params(labelsize=5.4, length=1.5, pad=1)
cb.outline.set_linewidth(0.4)
cax.set_title("reassigned voxel fraction", fontsize=5.4, pad=2)
ax.text(hi * 0.5, hi * 0.5, "identity ", ha="right", va="top", fontsize=5.4, color=MID)
ax.text(0.97, 0.30, "%d representative material \u00d7 codec\n\u00d7 tolerance cases" % len(a), transform=ax.transAxes,
        fontsize=5.4, color=MID, va="bottom", ha="right")

# ---- b --------------------------------------------------------------------------------------
pg.letter("b", 94.0, 149.0)
ax = pg.ax(RX, TOP, PW, PH)
LT = 1e-7
ax.axhline(0, color=OTHER, lw=0.5, zorder=1); ax.axvline(0, color=OTHER, lw=0.5, zorder=1)
ax.scatter(b.dq_integrand_e[~large], b.dq_domain_e[~large], s=2.5, c=DARK_B, alpha=0.45, linewidths=0, zorder=3,
           rasterized=True)
ax.scatter(b.dq_integrand_e[large], b.dq_domain_e[large], s=2.5, c=RED, alpha=0.55, linewidths=0, zorder=4,
           rasterized=True)
ax.set_xscale("symlog", linthresh=LT, linscale=0.4); ax.set_yscale("symlog", linthresh=LT, linscale=0.4)
tk = [-1, -1e-3, 0, 1e-3, 1]
ax.set_xticks(tk); ax.set_yticks(tk)
lab = [r"$-10^{0}$", r"$-10^{-3}$", "0", r"$10^{-3}$", r"$10^{0}$"]
ax.set_xticklabels(lab); ax.set_yticklabels(lab)
ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
ax.set_xlabel(r"integrand contribution $\Delta q_{\rm integrand}$ (e)")
ax.set_ylabel(r"domain-migration contribution $\Delta q_{\rm domain}$ (e)")
open_frame(ax); grid(ax)
handles = [Line2D([], [], marker="o", ls="none", color=RED, ms=3, label=r"$|\Delta q_{\rm total}| \geq 10^{-3}$ e (n = %d)" % large.sum()),
           Line2D([], [], marker="o", ls="none", color=DARK_B, ms=3, label="typical (n = %d)" % (~large).sum())]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper left")
# top-left is empty: large negative integrand with large positive domain is not populated at the corner
ax.text(0.97, 0.03, r"$\Delta q_{\rm total} = \Delta q_{\rm integrand} + \Delta q_{\rm domain}$", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=5.6, color=INK)

# ---- c: three representative ladders, stacked with a shared x ------------------------------------------
pg.letter("c", 2.0, 71.0)
GAP = 4.5
h3 = (PH - 2 * GAP) / 3
for i, (_, ch) in enumerate(chosen.iterrows()):
    ax = pg.ax(LX, BOT + (2 - i) * (h3 + GAP), PW, h3)
    r = bench[(bench.material_id == ch.material_id) & (bench.codec == ch.codec) & (bench.realized_rel > 0)
              & (bench.Bader_error_fixed_e > 0) & (bench.Bader_error_resolved_e > 0)].sort_values("realized_rel")
    sz = 4 + 40 * np.sqrt(r.frac_voxels_reassigned.clip(lower=0))
    ax.plot(r.realized_rel, r.Bader_error_fixed_e, color=PALE, lw=0.8, zorder=2)
    ax.scatter(r.realized_rel, r.Bader_error_fixed_e, s=sz, c=PALE, linewidths=0, zorder=3)
    ax.plot(r.realized_rel, r.Bader_error_resolved_e, color=DARK_B, lw=0.8, zorder=4)
    ax.scatter(r.realized_rel, r.Bader_error_resolved_e, s=sz, c=DARK_B, linewidths=0, zorder=5)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(2e-8, 3e-2)
    ax.set_ylim(r[["Bader_error_fixed_e", "Bader_error_resolved_e"]].values.min() * 0.3,
                r[["Bader_error_fixed_e", "Bader_error_resolved_e"]].values.max() * 6)
    log_ticks(ax, "x", subs=())
    ax.yaxis.set_major_locator(__import__("matplotlib").ticker.LogLocator(base=10, numticks=4))
    ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
    open_frame(ax); grid(ax)
    ax.set_title("%s case  (%s, %s; max consecutive jump %.0f\u00d7)" % (ch.case, ch.material_id, ch.codec, ch.max_jump),
                 loc="left", fontsize=5.8, fontweight="bold", pad=1.5)
    if i < 2:
        ax.set_xticklabels([])
    if i == 1:
        ax.set_ylabel("Bader error (e)")
    if i == 2:
        ax.set_xlabel(r"realized $L_\infty$ / density range")
    if i == 0:
        # the smooth case occupies only the middle decades; its lower-right is empty
        handles = [Line2D([], [], marker="o", color=DARK_B, ms=3, lw=0.8, label="re-derived basins"),
                   Line2D([], [], marker="o", color=PALE, ms=3, lw=0.8, label="fixed reference basins")]
        layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right",
                      title="marker size = reassigned voxels")

# ---- d --------------------------------------------------------------------------------------
pg.letter("d", 94.0, 71.0)
ax = pg.ax(RX, BOT, PW, PH)
rng = np.random.default_rng(20260909)
for c in CODECS:
    s = dd[dd.codec == c]
    show = s.sample(n=min(len(s), 1500), random_state=20260909)
    ax.scatter(show.frac_voxels_reassigned, show.jump, s=2.5, c=CODEC[c], alpha=0.3, linewidths=0, zorder=2,
               rasterized=True)
    k, b0 = np.polyfit(np.log10(s.frac_voxels_reassigned), np.log10(s.jump), 1)
    xs = np.logspace(np.log10(s.frac_voxels_reassigned.min()), np.log10(s.frac_voxels_reassigned.max()), 40)
    ax.plot(xs, 10 ** (k * np.log10(xs) + b0), color=CODEC_DARK[c], lw=1.0, zorder=4)
ax.set_xscale("log"); ax.set_yscale("log"); log_ticks(ax)
ax.set_xlabel("reassigned voxel fraction")
ax.set_ylabel("consecutive-rung Bader-error jump factor")
open_frame(ax); grid(ax)
note(ax, 0.03, 0.96, "Spearman \u03c1 = %.2f  (n = %s rung steps)\ndescriptive association only" % (rho, format(len(dd), ",")))
handles = [Line2D([], [], color=CODEC_DARK[c], lw=1.0, label=c) for c in CODECS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper right", ncol=3)
# the cloud sits at jump < 10 along the bottom; the upper right is empty

layout.audit(pg.fig)
pg.save(HERE, "Fig5")
