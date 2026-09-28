"""Supplementary Figure S7 -- codec-resolved consequences of stability qualification.

183 x 100 mm, strip on top + two below, from analysis/certifiability_reclassification_by_codec_20260911.csv:
  a  naive failures per codec and tau, split into genuine eligible failures and non-evaluable pairs
  b  fraction of naive passes that lie on non-evaluable pairs
  c  genuine failure fraction among eligible decisions

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS7.py   -> FigS7.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import CODEC_DARK, CODECS, INK, MID, OTHER, PALE_B, RED, Page, grid, open_frame, thr_label  # noqa: E402

d = D.csv("analysis", "certifiability_reclassification_by_codec_20260911.csv")
d["codec"] = d.codec.str.upper()
assert len(d) == 9
expected = {"ZFP": [135, 86, 21], "SZ3": [205, 114, 45], "SPERR": [193, 110, 42]}   # frozen audit counts per codec
for c, v in expected.items():
    assert list(d[d.codec == c].sort_values("threshold_e").naive_fail) == v, c
TAU = (1e-4, 1e-3, 1e-2)
X = np.arange(3)

pg = Page(183.0, 100.0)

# ---- a: stacked bars, one small multiple per codec ------------------------------------------------------------
pg.letter("a", 2.0, 99.0)
for k, c in enumerate(CODECS):
    ax = pg.ax(14.0 + k * 57.0, 58.0, 48.0, 34.0)
    s = d[d.codec == c].set_index("threshold_e").loc[list(TAU)]
    ax.bar(X, s.eligible_fail, width=0.6, color=RED, edgecolor="white", lw=0.4, zorder=3)
    ax.bar(X, s.naive_fail_reclassified_non_evaluable, bottom=s.eligible_fail, width=0.6, color=PALE_B, edgecolor="white", lw=0.4, zorder=3)
    for x, (_, r) in zip(X, s.iterrows()):
        ax.text(x, r.naive_fail + 4, "%.1f%%\nn = %d" % (100 * r.reclassified_fraction_of_naive_fail, r.naive_fail), ha="center",
                va="bottom", fontsize=5.4, linespacing=1.1)
    ax.set_xticks(X); ax.set_xticklabels([thr_label(t) for t in TAU]); ax.set_xlim(-0.6, 2.6)
    ax.set_ylim(0, 260); ax.set_yticks([0, 50, 100, 150, 200])
    if k == 0:
        ax.set_ylabel("naive failures (of 254 decisions)")
    else:
        ax.set_yticklabels([])
    ax.set_title(c, loc="left", fontsize=6.2, fontweight="bold", pad=2)
    open_frame(ax); grid(ax, "y")
    if k == 2:
        handles = [Patch(facecolor=RED, label="genuine eligible failure"), Patch(facecolor=PALE_B, label="on a non-evaluable pair")]
        layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper right")
        # SPERR at 1e-2 e has 42 failures; the upper right above 1e-3/1e-2 bars is clear
pg.fig.text(14.0 / pg.W, 52.0 / pg.H, "percent label = share of naive failures that fall on non-evaluable material\u2013threshold pairs",
            fontsize=5.4, color=MID, va="top")

# ---- b ---------------------------------------------------------------------------------------
pg.letter("b", 2.0, 49.0)
ax = pg.ax(14.0, 10.0, 68.0, 32.0)
for c in CODECS:
    s = d[d.codec == c].set_index("threshold_e").loc[list(TAU)]
    f = s.non_evaluable_naive_pass / s.naive_pass
    ax.plot(X, f, color=CODEC_DARK[c], lw=0.9, marker="o", ms=3.2, zorder=3)
    r = s.iloc[0]
    ax.text(0.08, f.iloc[0], "%d / %d" % (r.non_evaluable_naive_pass, r.naive_pass), fontsize=5.4, va="center", color=CODEC_DARK[c])
ax.set_xticks(X); ax.set_xticklabels([thr_label(t) for t in TAU]); ax.set_xlim(-0.4, 2.4)
ax.set_ylim(0, 0.7); ax.set_yticks([0, 0.2, 0.4, 0.6]); ax.set_yticklabels(["0", "20", "40", "60%"])
ax.set_xlabel(r"Bader tolerance $\tau$"); ax.set_ylabel("naive passes on\nnon-evaluable pairs")
open_frame(ax); grid(ax, "y")
handles = [Line2D([], [], marker="o", color=CODEC_DARK[c], ms=3.2, lw=0.9, label=c) for c in CODECS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper right")

# ---- c ---------------------------------------------------------------------------------------
pg.letter("c", 94.0, 49.0)
ax = pg.ax(106.0, 10.0, 68.0, 32.0)
for c in CODECS:
    s = d[d.codec == c].set_index("threshold_e").loc[list(TAU)]
    ax.plot(X, s.eligible_fail / s.n_eligible, color=CODEC_DARK[c], lw=0.9, marker="o", ms=3.2, zorder=3)
ax.set_xticks(X); ax.set_xticklabels([thr_label(t) for t in TAU]); ax.set_xlim(-0.4, 2.4)
ax.set_ylim(0, 0.2); ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20]); ax.set_yticklabels(["0", "5", "10", "15", "20%"])
ax.set_xlabel(r"Bader tolerance $\tau$"); ax.set_ylabel("genuine failures among\neligible decisions")
open_frame(ax); grid(ax, "y")
ax.text(0.98, 0.96, "denominators: eligible decisions per codec\n(46 / 103+ / 168+, see Table S4)", transform=ax.transAxes, fontsize=5.2,
        color=MID, ha="right", va="top")

layout.audit(pg.fig)
pg.save(HERE, "FigS7")
