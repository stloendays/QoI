"""Figure 8 -- untouched external systems reproduce the stability-qualified decision frontier.

2x2, 183 x 118 mm, from the frozen 63-system external confirmatory outputs:
  a  median best-certified compression ratio vs tau per codec, 95% bootstrap CI   external_summary_a1.csv
  b  SZ3-over-ZFP win fraction vs tau                                            pairwise_external.csv
  c  realized / nominal L-inf at the best-certified point per codec              best_certified_external.csv
  d  QSQ-eligible systems vs tau                                                 external_summary_a1.csv, summary.json

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig8.py   -> Fig8.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (CODEC, CODEC_DARK, CODECS, DARK_B, DARK_G, INK, MID, OTHER, RED, TINT_G, Page, grid,  # noqa: E402
                   note, open_frame, thr_label)

S = D.external_summary()
P = D.external_pairwise()
B = D.external_best()
A = D.external_audit()
TAU = (1e-4, 1e-3, 1e-2)
S["codec"] = S.codec.str.upper()
B["codec"] = B.codec.str.upper()
ov = S[S.stratum == "overall"]
elig = ov[ov.codec == "ZFP"].set_index("threshold_e").n_admitted
assert list(elig.loc[list(TAU)]) == [16, 42, 57]
n_complete = A["n_materials_complete"]

pg = Page(183.0, 118.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 40.0
TOP, BOT = 68.0, 12.0
X = np.arange(3)


def tau_axis(ax):
    ax.set_xticks(X); ax.set_xticklabels([thr_label(t) for t in TAU]); ax.set_xlim(-0.5, 2.5)
    ax.set_xlabel(r"Bader contract $\tau$")


# ---- a: best-certified ratio ---------------------------------------------------------------------
pg.letter("a", 2.0, 117.0)
ax = pg.ax(LX, TOP, PW, PH)
for j, c in enumerate(CODECS):
    r = ov[ov.codec == c].set_index("threshold_e").loc[list(TAU)]
    dx = (j - 1) * 0.08
    ax.errorbar(X + dx, r.ratio_median, yerr=[r.ratio_median - r.ratio_median_ci_lo, r.ratio_median_ci_hi - r.ratio_median],
                color=CODEC_DARK[c], lw=0.9, marker="o", ms=3.2, capsize=1.6, capthick=0.6, elinewidth=0.6, zorder=3)
ax.set_yscale("log"); ax.set_ylim(3.5, 130)
ax.set_yticks([5, 10, 20, 40, 80]); ax.set_yticklabels(["5", "10", "20", "40", "80"])
ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
tau_axis(ax); ax.set_ylabel("best-certified compression ratio")
open_frame(ax); grid(ax, "y")
handles = [Line2D([], [], marker="o", color=CODEC_DARK[c], ms=3.2, lw=0.9, label=c) for c in CODECS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper left")
# series rise to the right; upper-left is clear
ax.text(0.0, 1.02, "median over eligible systems; 95% bootstrap CI", transform=ax.transAxes, fontsize=5.2, color=MID,
        ha="left", va="bottom")

# ---- b: SZ3 win fraction --------------------------------------------------------------------------
pg.letter("b", 94.0, 117.0)
ax = pg.ax(RX, TOP, PW, PH)
b = P[(P.stratum == "overall") & (P.codec_a == "sz3") & (P.codec_b == "zfp")].set_index("threshold_e").loc[list(TAU)]
ax.axhline(0.5, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
ax.errorbar(X, b.frac_a_wins, yerr=[b.frac_a_wins - b.a_wins_ci_lo, b.a_wins_ci_hi - b.frac_a_wins], color=DARK_G, lw=0.9,
            marker="o", ms=3.4, capsize=1.6, capthick=0.6, elinewidth=0.6, zorder=3)
for x, (t, r) in zip(X, b.iterrows()):
    ax.text(x + 0.08, r.frac_a_wins - 0.06, "%.0f%%  (n = %d)" % (100 * r.frac_a_wins, r.n), ha="left", va="top", fontsize=5.6)
ax.set_ylim(0, 1.05); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(["0", "25", "50", "75", "100%"])
tau_axis(ax); ax.set_ylabel("eligible systems where SZ3\nbeats ZFP on certified ratio")
open_frame(ax); grid(ax, "y")

# ---- c: realized / nominal at the best-certified point ------------------------------------------------
pg.letter("c", 2.0, 61.0)
ax = pg.ax(LX, BOT, PW, PH)
cb = B[(B.has_certified_point.astype(str).str.lower() == "true") & np.isfinite(B.realized_Linf_over_nominal_at_CCR)
       & (B.realized_Linf_over_nominal_at_CCR > 0)]
ax.axhline(1, color=RED, lw=0.7, ls=(0, (3, 2)), zorder=1)
ax.text(-0.45, 0.0, " nominal budget", ha="left", va="bottom", fontsize=5.4, color=RED)   # y axis is log10
rng = np.random.default_rng(20260908)
for j, c in enumerate(CODECS):
    v = cb[cb.codec == c].realized_Linf_over_nominal_at_CCR.values
    lv = np.log10(v)
    vp = ax.violinplot([lv], positions=[j], widths=0.7, showextrema=False, points=200)
    for body in vp["bodies"]:
        body.set_facecolor(CODEC[c]); body.set_edgecolor("none"); body.set_alpha(0.35)
    ax.scatter(j + rng.uniform(-0.12, 0.12, len(lv)), lv, s=3, c=CODEC_DARK[c], alpha=0.45, linewidths=0, zorder=3)
    med = np.median(v)
    ax.plot([j - 0.2, j + 0.2], [np.log10(med)] * 2, color=INK, lw=0.9, zorder=4)
    ax.text(j + 0.24, np.log10(med), "median %.2f" % med, ha="left", va="center", fontsize=5.6)
ax.set_xticks(X); ax.set_xticklabels(CODECS); ax.set_xlim(-0.5, 2.6)
ax.set_ylim(-1.4, 0.3); ax.set_yticks([-1, np.log10(0.2), np.log10(0.5), 0]); ax.set_yticklabels(["0.1", "0.2", "0.5", "1"])
ax.set_ylabel(r"realized $L_\infty$ / nominal budget")
open_frame(ax); grid(ax, "y")
ax.text(0.0, 1.02, "certified external rows, n = %d" % len(cb), transform=ax.transAxes, fontsize=5.4, color=MID, va="bottom")

# ---- d: eligible systems -----------------------------------------------------------------------------
pg.letter("d", 94.0, 61.0)
ax = pg.ax(RX, BOT, PW, PH)
ax.bar(X, elig.loc[list(TAU)], width=0.5, color=TINT_G, edgecolor=DARK_G, lw=0.6, zorder=2)
for x, t in zip(X, TAU):
    n = int(elig.loc[t])
    ax.text(x, n + 1.2, "%d / %d\n(%.0f%%)" % (n, n_complete, 100 * n / n_complete), ha="center", va="bottom", fontsize=5.8)
ax.set_ylim(0, 75); ax.set_yticks([0, 20, 40, 60])
tau_axis(ax); ax.set_ylabel("QSQ-eligible external systems")
open_frame(ax); grid(ax, "y")
note(ax, 0.03, 0.96, "%d / %d systems complete\n%d pipeline failures, %d bound violations\n%s retained rows"
     % (n_complete, A["n_materials_observed"], A["n_material_pipeline_failures"], A["n_bound_violations"],
        format(A["n_rows"], ",")), size=5.4)

layout.audit(pg.fig)
pg.save(HERE, "Fig8")
