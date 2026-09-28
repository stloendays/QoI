"""Supplementary Figure S4 -- the strictest certified Bader regime is floor-scale, not a universal plateau.

183 x 60 mm strip of three:
  a  best-certified error / QSQ floor per codec and tau, median + P10-P90   supplement/S2_floor_relative.csv (re-derived from master)
  b  floor vs best-certified error at 1e-4 e, n = 123                     benchmark/master_benchmark_full.csv
  c  error / floor along the common tight ladder, median + IQR             benchmark/master_benchmark_tight_ladder.csv

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS4.py   -> FigS4.{svg,pdf,png}
"""
import os
import sys

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import CODEC, CODEC_DARK, CODECS, INK, MID, OTHER, RED, Page, grid, log_ticks, open_frame, thr_label  # noqa: E402

master = D.master()
tight = D.tight_ladder()
s2 = D.supp("S2_floor_relative.csv")
s2["codec"] = s2.codec.str.upper()
assert len(master) == 6343 and len(tight) == 1716
TAU = ((1e-4, "0.0001"), (1e-3, "0.001"), (1e-2, "0.01"))

best = []
for tau, suf in TAU:
    m = master[D.truthy(master["certified_at_" + suf]) & np.isfinite(master.compression_ratio)
               & np.isfinite(master.Bader_error_resolved_e) & (master.stability_floor_A1_e > 0)]
    b = m.sort_values("compression_ratio", ascending=False).drop_duplicates(["material_id", "codec"])
    best.append(b.assign(tau=tau, r=b.Bader_error_resolved_e / b.stability_floor_A1_e))
best = pd.concat(best)
best["codec"] = best.codec.str.upper()
for _, r in s2.iterrows():
    v = best[(best.tau == r.threshold_e) & (best.codec == r.codec)].r
    assert len(v) == r.n and abs(v.median() - r.dq_over_floor_median) < 1e-9, (r.threshold_e, r.codec)

pg = Page(183.0, 60.0)
X = np.arange(3)

# ---- a ---------------------------------------------------------------------------------------
pg.letter("a", 2.0, 59.0)
ax = pg.ax(14.0, 12.0, 46.0, 40.0)
ax.axhline(1, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=1)
for j, c in enumerate(CODECS):
    r = s2[s2.codec == c].set_index("threshold_e").loc[[t for t, _ in TAU]]
    dx = (j - 1) * 0.18
    ax.errorbar(X + dx, r.dq_over_floor_median, yerr=[r.dq_over_floor_median - r.dq_over_floor_p10, r.dq_over_floor_p90 - r.dq_over_floor_median],
                fmt="o", color=CODEC_DARK[c], ms=3.2, lw=0.8, capsize=1.5, capthick=0.6, zorder=3)
ax.set_yscale("log"); ax.set_ylim(0.3, 300)
ax.set_yticks([0.5, 1, 2, 5, 10, 20, 50, 100, 200]); ax.set_yticklabels(["0.5", "1", "2", "5", "10", "20", "50", "100", "200"])
ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
ax.set_xticks(X); ax.set_xticklabels([thr_label(t) for t, _ in TAU]); ax.set_xlim(-0.5, 2.5)
ax.set_xlabel(r"certification threshold $\tau$"); ax.set_ylabel("best-certified Bader error / QSQ floor")
open_frame(ax); grid(ax, "y")
handles = [Line2D([], [], marker="o", ls="none", color=CODEC_DARK[c], ms=3.2, label=c) for c in CODECS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper left", ncol=1)
ax.text(0.98, 0.02, "median, P10\u2013P90;\none highest-rate certified\npoint per material\u2013codec", transform=ax.transAxes,
        fontsize=5.2, color=MID, ha="right", va="bottom")
ax.text(2.45, 1, "floor ", ha="right", va="bottom", fontsize=5.4, color=RED)

# ---- b ---------------------------------------------------------------------------------------
pg.letter("b", 64.0, 59.0)
ax = pg.ax(76.0, 12.0, 40.0, 40.0)
st = best[best.tau == 1e-4]
assert len(st) == 123
lo, hi = 1e-6, 1e-2
ax.plot([lo, hi], [lo, hi], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=2)
for c in CODECS:
    s = st[st.codec == c]
    ax.scatter(s.stability_floor_A1_e, s.Bader_error_resolved_e, s=8, c=CODEC_DARK[c], alpha=0.65, linewidths=0, zorder=3)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2]); ax.set_yticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2])
ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator()); ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
ax.set_xlabel("QSQ stability floor (e)"); ax.set_ylabel("best-certified Bader error (e)")
open_frame(ax); grid(ax)
ax.text(0.03, 0.97, r"$\tau = 10^{-4}$ e; n = 123 certified" "\nmaterial\u2013codec decisions", transform=ax.transAxes, fontsize=5.4,
        color=MID, va="top")

# ---- c ---------------------------------------------------------------------------------------
pg.letter("c", 120.0, 59.0)
ax = pg.ax(132.0, 12.0, 48.0, 40.0)
t2 = tight[np.isfinite(tight.Bader_error_resolved_e) & (tight.stability_floor_A1_e > 0)].copy()
t2["codec"] = t2.codec.str.upper()
t2["r"] = np.maximum(t2.Bader_error_resolved_e / t2.stability_floor_A1_e, 1e-6)
ax.axhline(1, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=1)
for c in CODECS:
    g = t2[t2.codec == c].groupby("nominal_tolerance_relative").r
    q = g.quantile([0.25, 0.5, 0.75]).unstack()
    ax.fill_between(q.index, q[0.25], q[0.75], color=CODEC[c], alpha=0.2, lw=0, zorder=2)
    ax.plot(q.index, q[0.5], color=CODEC_DARK[c], lw=0.9, marker="o", ms=2.8, zorder=3)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("nominal relative codec tolerance"); ax.set_ylabel("Bader error / QSQ floor")
open_frame(ax); grid(ax)
ax.text(0.03, 0.97, "common tight ladder, 143 eligible materials\nmedian and IQR", transform=ax.transAxes, fontsize=5.4,
        color=MID, va="top")

layout.audit(pg.fig)
pg.save(HERE, "FigS4")
