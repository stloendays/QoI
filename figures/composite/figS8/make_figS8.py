"""Supplementary Figure S8 -- pre-specified rate-fidelity conclusions reproduce on the untouched external cohort.

183 x 118 mm, 2x2, from supplement/S13_rate_fidelity_summary.csv and S13_pairwise_sz3_zfp.csv:
  a  median best-certified ratio vs tau per codec, development and external side by side
  b  external QSQ-eligible fraction vs tau
  c  SZ3-vs-ZFP win fraction, development vs external
  d  certified fraction among admitted external systems

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS8.py   -> FigS8.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import CODEC_DARK, CODECS, DARK_B, DARK_G, INK, MID, OTHER, RED, TINT_G, Page, grid, open_frame, thr_label  # noqa: E402

S = D.supp("S13_rate_fidelity_summary.csv")
P = D.supp("S13_pairwise_sz3_zfp.csv")
assert len(S) == 54 and len(P) == 18
TAU = (1e-4, 1e-3, 1e-2)
X = np.arange(3)
ext = S[(S.cohort == "external_confirmatory63") & (S.stratum == "overall")]
assert sorted(ext[ext.codec == "ZFP"].n_admitted) == [16, 42, 57]
COH = (("development", "development (254)", DARK_B), ("external_confirmatory63", "external (63)", DARK_G))

pg = Page(183.0, 118.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 40.0
TOP, BOT = 68.0, 12.0


def tau_axis(ax):
    ax.set_xticks(X); ax.set_xticklabels([thr_label(t) for t in TAU]); ax.set_xlim(-0.5, 2.5)
    ax.set_xlabel(r"Bader contract $\tau$")


# ---- a: two small multiples -------------------------------------------------------------------------------
pg.letter("a", 2.0, 117.0)
for k, (coh, lab, _) in enumerate(COH):
    ax = pg.ax(LX + k * 36.0, TOP, 30.0, PH)
    s = S[(S.cohort == coh) & (S.stratum == "overall")]
    for j, c in enumerate(CODECS):
        r = s[s.codec == c].set_index("threshold_e").loc[list(TAU)]
        ax.errorbar(X + (j - 1) * 0.1, r.ratio_median, yerr=[r.ratio_median - r.ratio_median_ci_lo, r.ratio_median_ci_hi - r.ratio_median],
                    color=CODEC_DARK[c], lw=0.9, marker="o", ms=3, capsize=1.4, capthick=0.6, elinewidth=0.6, zorder=3)
    ax.set_yscale("log"); ax.set_ylim(3, 160)
    ax.set_yticks([4, 8, 16, 32, 64, 128]); ax.set_yticklabels(["4", "8", "16", "32", "64", "128"] if k == 0 else [])
    ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
    tau_axis(ax)
    if k == 0:
        ax.set_ylabel("best-certified compression ratio")
    ax.set_title(lab, loc="left", fontsize=6.0, fontweight="bold", pad=2)
    open_frame(ax); grid(ax, "y")
    if k == 0:
        handles = [Line2D([], [], marker="o", color=CODEC_DARK[c], ms=3, lw=0.9, label=c) for c in CODECS]
        layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper left")

# ---- b: eligible fraction ---------------------------------------------------------------------------------
pg.letter("b", 94.0, 117.0)
ax = pg.ax(RX, TOP, PW, PH)
e = ext[ext.codec == "ZFP"].set_index("threshold_e").loc[list(TAU)]
ax.bar(X, e.n_admitted / 63, width=0.5, color=TINT_G, edgecolor=DARK_G, lw=0.6, zorder=3)
for x, n in zip(X, e.n_admitted):
    ax.text(x, n / 63 + 0.02, "%d / 63" % n, ha="center", va="bottom", fontsize=5.8)
ax.set_ylim(0, 1.1); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(["0", "25", "50", "75", "100%"])
tau_axis(ax); ax.set_ylabel("QSQ-eligible external systems")
open_frame(ax); grid(ax, "y")

# ---- c: SZ3 win fraction ----------------------------------------------------------------------------------
pg.letter("c", 2.0, 61.0)
ax = pg.ax(LX, BOT, PW, PH)
ax.axhline(0.5, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
for k, (coh, lab, col) in enumerate(COH):
    r = P[(P.cohort == coh) & (P.stratum == "overall")].set_index("threshold_e").loc[list(TAU)]
    ax.errorbar(X + (k - 0.5) * 0.12, r.sz3_win_fraction, yerr=[r.sz3_win_fraction - r.sz3_win_ci_lo, r.sz3_win_ci_hi - r.sz3_win_fraction],
                color=col, lw=0.9, marker="o", ms=3.2, capsize=1.4, capthick=0.6, elinewidth=0.6, zorder=3)
ax.set_ylim(0, 1.05); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(["0", "25", "50", "75", "100%"])
tau_axis(ax); ax.set_ylabel("eligible systems where SZ3\nbeats ZFP on certified ratio")
open_frame(ax); grid(ax, "y")
handles = [Line2D([], [], marker="o", color=c, ms=3.2, lw=0.9, label=l) for _, l, c in COH]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper left")

# ---- d: certified among admitted (external) ------------------------------------------------------------------
pg.letter("d", 94.0, 61.0)
ax = pg.ax(RX, BOT, PW, PH)
ax.axhline(1, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
for j, c in enumerate(CODECS):
    r = ext[ext.codec == c].set_index("threshold_e").loc[list(TAU)]
    ax.plot(X + (j - 1) * 0.08, r.frac_certified, color=CODEC_DARK[c], lw=0.9, marker="o", ms=3.2, zorder=3)
    for x, (_, rr) in zip(X, r.iterrows()):
        if rr.frac_certified < 1:
            ax.text(x + (j - 1) * 0.08 + (0.03 if j == 2 else -0.03), rr.frac_certified - 0.012, "%d/%d" % (rr.n_certified, rr.n_admitted),
                    ha="left" if j == 2 else "right", va="top", fontsize=5.0, color=CODEC_DARK[c])
ax.set_ylim(0.74, 1.02); ax.set_yticks([0.75, 0.8, 0.85, 0.9, 0.95, 1.0]); ax.set_yticklabels(["75", "80", "85", "90", "95", "100%"])
tau_axis(ax); ax.set_ylabel("certified fraction among\nQSQ-eligible external systems")
open_frame(ax); grid(ax, "y")
handles = [Line2D([], [], marker="o", color=CODEC_DARK[c], ms=3.2, lw=0.9, label=c) for c in CODECS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right")

layout.audit(pg.fig)
pg.save(HERE, "FigS8")
