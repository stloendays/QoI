"""Figure 5 -- topology-dependent basin migration explains irregular amplification of re-derived Bader error.

2x2 (four coordinate claims) + a render row, 183 x 204 mm:
  a  re-solving amplifies the fixed-basin error       mechanism/basin_error_decomposition_summary.csv
  b  per-atom: domain term dominates large deviations  mechanism/basin_error_decomposition_per_atom.csv
  c  three representative full ladders                 benchmark/master_benchmark_full.csv
  d  jump severity vs basin reassignment               benchmark/master_benchmark_full.csv
  e  where the jump happens: the Fig. 5c jump-case ladder rendered in 3D (KCN, ZFP), three rungs, one
     camera. Red = voxels whose Bader owner changes. OVITO renders from render3d/build_kcn.py; the
     voxels are the pinned-stack re-solve (render3d/prep_fields.py), the numbers the frozen rows.
  f  which input carries the instability: five-probe QSQ floors of the 50 analyzable all-electron-reference
     materials when only the charge field, both fields, or only the partition-defining field is approximate
     (WP-G probes.csv for the first two, WP-I checkpoints for the third), and the partition-only floor against
     the joint floor. One red: the partition-field contract.

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
import glob
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (CODEC, CODEC_DARK, CODECS, DARK_B, DARK_G, ELEM, GREEN, INK, MID, OTHER, PALE, PALE_G,  # noqa: E402
                   RED, Page, grid, log_ticks, note, open_frame, place_render)
import advanced as A  # noqa: E402

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

# ---- f data: floors under the three all-electron-reference contracts --------------------------------
WPG = D.csv("analysis", "extensions_20260930", "WP-G", "probes.csv")
fl = WPG.groupby("material_id").agg(g1=("g1_response_e", "max"), g2=("g2_response_e", "max"), n=("seed", "size"))
g3 = {}
for path in glob.glob(os.path.join(r"D:\Research\QoI-ext-cache\WP-I\extract\results\checkpoints", "*.json")):
    j = json.load(open(path, encoding="utf-8"))
    if j.get("status") == "SUCCESS":
        g3[j["material_id"]] = max(pq["g3_response_e"] for pq in j["probes"])
fl["g3"] = pd.Series(g3)
fl = fl.dropna(subset=["g1", "g2", "g3"])
assert len(fl) == 50 and (fl.n == 5).all()
ELIG_F = {k: int((fl[k] < 1e-3).sum()) for k in ("g1", "g2", "g3")}
assert ELIG_F == {"g1": 50, "g2": 3, "g3": 3}, ELIG_F
assert abs(np.median(fl.g3 / fl.g2) - 1.0) < 1e-6 and (fl.g3 >= 0.9 * fl.g2).all()

# ---- page --------------------------------------------------------------------------------
OFF = 54.0                                  # height of the render row e
FH = 50.0                                   # height of the contract row f, at the bottom
BASE = OFF + FH
pg = Page(183.0, 138.0 + BASE)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 46.0
TOP, BOT = 86.0 + BASE, 14.0 + BASE

# ---- a --------------------------------------------------------------------------------------
pg.letter("a", 2.0, TOP + PH + 5.0)
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
ax.text(hi * 0.12, hi * 0.5, "identity", ha="right", va="top", fontsize=5.4, color=MID)
ax.text(0.97, 0.30, "%d representative material \u00d7 codec\n\u00d7 tolerance cases" % len(a), transform=ax.transAxes,
        fontsize=5.4, color=MID, va="bottom", ha="right")

# ---- b --------------------------------------------------------------------------------------
pg.letter("b", 94.0, TOP + PH + 5.0)
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
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="center left",
              bbox_to_anchor=(0.0, 0.5))
# every corner holds points; the only empty region is the band around zero domain contribution
ax.text(0.98, 0.5,r"$\Delta q_{\rm total} = \Delta q_{\rm integrand} + \Delta q_{\rm domain}$", transform=ax.transAxes,
        ha="right", va="center", fontsize=5.6, color=INK, zorder=7,
        bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="none"))

# ---- c: three representative ladders, stacked with a shared x ------------------------------------------
pg.letter("c", 2.0, BOT + PH + 5.0)
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
    ax.set_title("%s case  (%s, %s; max consecutive jump %s\u00d7)" % (ch.case, ch.material_id, ch.codec,
                                                                        format(int(round(ch.max_jump)), ",")),
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
pg.letter("d", 94.0, BOT + PH + 5.0)
ax = pg.ax(RX, BOT, PW, PH)
A.density_scatter(ax, dd.frac_voxels_reassigned.to_numpy(), dd.jump.to_numpy(), logx=True, logy=True, s=2.2)
for c in CODECS:
    s = dd[dd.codec == c]
    k, b0 = np.polyfit(np.log10(s.frac_voxels_reassigned), np.log10(s.jump), 1)
    xs = np.logspace(np.log10(s.frac_voxels_reassigned.min()), np.log10(s.frac_voxels_reassigned.max()), 40)
    ax.plot(xs, 10 ** (k * np.log10(xs) + b0), color=CODEC_DARK[c], lw=1.0, zorder=4)
ax.set_xscale("log"); ax.set_yscale("log"); log_ticks(ax)
ax.set_xlabel("reassigned voxel fraction")
ax.set_ylabel("consecutive-rung Bader-error jump factor")
open_frame(ax); grid(ax)
note(ax, 0.03, 0.96, "Spearman \u03c1 = %.2f  (n = %s rung steps)" % (rho, format(len(dd), ",")))
handles = [Line2D([], [], color=CODEC_DARK[c], lw=1.0, label=c) for c in CODECS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper right", ncol=1)
# the cloud sits at jump < 10 along the bottom; the upper right is empty

# ---- e: the jump-case ladder in 3D ------------------------------------------------------------
def sci(v):
    m, e = ("%.1e" % v).split("e")
    return r"%s$\times10^{%d}$" % (m, int(e))



assert chosen.iloc[2].material_id == "mp-676693" and chosen.iloc[2].codec == "ZFP"
pg.letter("e", 2.0, FH + OFF - 0.5)
kcn = bench[(bench.material_id == "mp-676693") & (bench.codec == "ZFP")].set_index("nominal_tolerance_relative")
rungs = ((1e-7, "kcn_moved_zfp_1e-7.png"), (3e-7, "kcn_moved_zfp_3e-7.png"), (1e-2, "kcn_moved_zfp_1e-2.png"))
xs = (32.0, 91.5, 151.0)
for (rel, png), xc in zip(rungs, xs):
    r = kcn.loc[kcn.index[np.isclose(kcn.index, rel)][0]]
    place_render(pg, png, xc - 24.0, FH + 12.5, 48.0, OFF - 16.0, anchor="S")
    k = int(round(np.log10(rel / (3 if np.isclose(rel, 3e-7) else 1))))
    tol = (r"$3 \times 10^{%d}$" % k) if np.isclose(rel, 3e-7) else (r"$10^{%d}$" % k)
    pg.fig.text(xc / pg.W, (FH + 11.0) / pg.H, "ZFP nominal %s  (realized $L_\\infty$/range %s)"
                % (tol, sci(r.realized_Linf / r.value_ptp)), fontsize=5.8, fontweight="bold", ha="center", va="top")
    pct = 100 * r.frac_voxels_reassigned
    what = ("%d voxels change owner" % int(r.n_voxels_reassigned)) if r.n_voxels_reassigned < 100 else \
           ("%s voxels (%.1f %%) change owner" % (format(int(r.n_voxels_reassigned), ","), pct))
    pg.fig.text(xc / pg.W, (FH + 7.6) / pg.H, "%s;  Bader error %s e" % (what, sci(r.Bader_error_resolved_e)),
                fontsize=5.6, color=INK, ha="center", va="top")
j = kcn.Bader_error_resolved_e.loc[kcn.index[np.isclose(kcn.index, 3e-7)][0]] / \
    kcn.Bader_error_resolved_e.loc[kcn.index[np.isclose(kcn.index, 1e-7)][0]]
assert abs(j - chosen.iloc[2].max_jump) < 1e-6 * j
ca = pg.canvas(0, FH, 183.0, OFF)
ya = 12.5 + (OFF - 16.0) * 0.55
ca.annotate("", xy=(67.0, ya), xytext=(57.0, ya), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=RED,
                                                                  mutation_scale=7, shrinkA=0, shrinkB=0))
ca.text(62.0, ya + 1.5, "%s\u00d7" % format(int(round(j)), ","), fontsize=6.2, fontweight="bold", color=RED,
        ha="center", va="bottom")
ca.text(62.0, ya - 1.5, "Bader error", fontsize=5.4, color=RED, ha="center", va="top")
ca.annotate("", xy=(127.0, ya), xytext=(117.0, ya), arrowprops=dict(arrowstyle="-|>", lw=0.7, color=INK,
                                                                    mutation_scale=6, shrinkA=0, shrinkB=0))
ca.text(122.0, ya + 1.5, "coarser", fontsize=5.4, color=INK, ha="center", va="bottom")
for jx, (s, c) in enumerate(ELEM.items()):
    ca.scatter([12.0 + 7.0 * jx], [OFF - 3.0], s=9, color=c, lw=0)
    ca.text(13.4 + 7.0 * jx, OFF - 3.0, s, fontsize=5.4, va="center")
ca.scatter([36.0], [OFF - 3.0], s=9, color=RED, lw=0)
ca.text(37.4, OFF - 3.0, "voxel whose Bader owner changes (drawn enlarged in the first two renders)",
        fontsize=5.4, va="center")

# ---- f: which input carries the instability --------------------------------------------------------------
pg.letter("f", 2.0, FH - 0.5)
ZERO = 2e-8                                   # where an exactly zero floor is drawn (broken axis)
ax = pg.ax(30.0, 12.0, 94.0, FH - 22.0)
rows = (("g1", "charge field", DARK_B), ("g2", "both fields", OTHER), ("g3", "partition field", RED))
for yrow, (k, lab, col) in zip((2, 1, 0), rows):
    v = fl[k].to_numpy()
    xv = np.where(v > 0, v, ZERO)
    off = A.swarm(np.log10(xv), 0.07, 0.07, max_off=0.34)
    ax.scatter(xv, yrow + off, s=7, c=col, alpha=0.85, linewidths=0, zorder=4)
for t_, w_ in ((1e-4, 0.5), (1e-3, 0.9), (1e-2, 0.5)):
    ax.axvline(t_, color=INK, lw=w_, ls="dashed", zorder=2)
    ax.text(t_, 2.62, r"$10^{%d}$ e" % int(round(np.log10(t_))), fontsize=5.4, ha="center", va="bottom", color=INK)
ax.set_xscale("log"); ax.set_xlim(1e-8, 20.0)
ax.set_xticks([ZERO, 1e-6, 1e-4, 1e-2, 1e0])
ax.set_xticklabels(["0", r"$10^{-6}$", r"$10^{-4}$", r"$10^{-2}$", r"$10^{0}$"])
ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
for xb in (5.5e-8, 6.5e-8):                    # axis break between the zero bin and the decades
    ax.plot([xb / 1.12, xb * 1.12], [-0.62, -0.48], color=INK, lw=0.6, clip_on=False, zorder=6)
ax.set_ylim(-0.55, 2.55); ax.set_yticks([2, 1, 0]); ax.set_yticklabels([r[1] for r in rows])
ax.set_ylabel("approximate input", labelpad=3)
ax.set_xlabel("five-probe QSQ stability floor (e)")
open_frame(ax); grid(ax, "x")
z1 = int((fl.g1 == 0).sum())
ax.text(ZERO * 1.6, 2.36, "%d at 0" % z1, fontsize=5.4, color=DARK_B, ha="left", va="bottom")
for yrow, k, col in ((2, "g1", DARK_B), (1, "g2", INK), (0, "g3", RED)):
    xt = 1.6e-2 if k == "g1" else 2e-7
    ax.text(xt, yrow, "%d / 50 eligible at $10^{-3}$ e" % ELIG_F[k], fontsize=5.8, fontweight="bold", color=col,
            ha="left", va="center", zorder=6)
# the charge-field row is empty right of 1e-5 and the two perturbed-partition rows are empty left of 1e-4,
# so each count sits in its own row's empty stretch

ax = pg.ax(144.0, 12.0, FH - 22.0, FH - 22.0)
lo, hi = 3e-4, 10.0
ax.plot([lo, hi], [lo, hi], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=2)
ax.scatter(fl.g2, fl.g3, s=8, c=RED, alpha=0.8, linewidths=0, zorder=4)
ax.set_xscale("log"); ax.set_yscale("log"); log_ticks(ax)
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("floor, both fields (e)")
ax.set_ylabel("floor, partition field (e)")
open_frame(ax); grid(ax)
ax.text(0.04, 0.97, "median ratio %.3f\n50 / 50 within 0.9\u00d7" % np.median(fl.g3 / fl.g2), transform=ax.transAxes,
        fontsize=5.6, color=INK, ha="left", va="top")

layout.audit(pg.fig)
pg.save(HERE, "Fig5")
