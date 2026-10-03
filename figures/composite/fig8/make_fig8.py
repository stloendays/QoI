"""Figure 8 -- untouched external systems reproduce the stability-qualified decision frontier.

2x2, 183 x 118 mm, from the frozen 63-system external confirmatory outputs:
  a  median best-certified compression ratio at each tau per codec, 95% bootstrap CI   external_summary_a1.csv
  b  SZ3-over-ZFP win fraction at each tau                                         pairwise_external.csv
  c  realized / nominal L-inf at the best-certified point, every certified row     best_certified_external.csv
  d  the 63 systems at each tau: QSQ-eligible versus non-evaluable                 external_summary_a1.csv, summary.json
The three thresholds are discrete contracts, so values at different tau are never joined by a line.

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
import advanced as AD  # noqa: E402

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
                color=CODEC_DARK[c], ls="none", marker="o", ms=3.4, capsize=1.6, capthick=0.6, elinewidth=0.7, zorder=3)
ax.set_yscale("log"); ax.set_ylim(3.5, 130)
ax.set_yticks([5, 10, 20, 40, 80]); ax.set_yticklabels(["5", "10", "20", "40", "80"])
ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
tau_axis(ax); ax.set_ylabel("best-certified compression ratio")
open_frame(ax); grid(ax, "y")
handles = [Line2D([], [], marker="o", color=CODEC_DARK[c], ms=3.2, ls="none", label=c) for c in CODECS]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper left")
# series rise to the right; upper-left is clear
ax.text(0.0, 1.02, "median over eligible systems; 95% bootstrap CI", transform=ax.transAxes, fontsize=5.2, color=MID,
        ha="left", va="bottom")

# ---- b: SZ3 win fraction --------------------------------------------------------------------------
pg.letter("b", 94.0, 117.0)
ax = pg.ax(RX, TOP, PW, PH)
b = P[(P.stratum == "overall") & (P.codec_a == "sz3") & (P.codec_b == "zfp")].set_index("threshold_e").loc[list(TAU)]
ax.axhline(0.5, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
ax.errorbar(X, b.frac_a_wins, yerr=[b.frac_a_wins - b.a_wins_ci_lo, b.a_wins_ci_hi - b.frac_a_wins], color=DARK_G, ls="none",
            marker="o", ms=3.6, capsize=1.6, capthick=0.6, elinewidth=0.7, zorder=3)
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
ax.axvline(1, color=RED, lw=0.8, ls=(0, (3, 2)), zorder=1)
ax.text(1.0, 2.62, "nominal budget", ha="center", va="bottom", fontsize=5.4, color=RED)
for yrow, c in zip((2, 1, 0), CODECS):
    v = cb[cb.codec == c].realized_Linf_over_nominal_at_CCR.values
    lv = np.log10(v)
    off = AD.swarm(lv, 0.012, 0.045, max_off=0.36)
    ax.scatter(v, yrow + off, s=3.2, c=CODEC_DARK[c], alpha=0.75, linewidths=0, zorder=3)
    med = np.median(v)
    ax.plot([med, med], [yrow - 0.4, yrow + 0.4], color=INK, lw=0.9, zorder=4)
    lab = "median %.2f  (n = %d)" % (med, len(v))
    if med < 0.5:
        ax.text(med * 1.45, yrow + 0.18, lab, ha="left", va="center", fontsize=5.6)
    else:
        ax.text(med / 1.12, yrow, lab, ha="right", va="center", fontsize=5.6)
ax.set_xscale("log"); ax.set_xlim(0.06, 1.6)
ax.set_xticks([0.1, 0.2, 0.5, 1.0]); ax.set_xticklabels(["0.1", "0.2", "0.5", "1"])
ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
ax.set_yticks([2, 1, 0]); ax.set_yticklabels(CODECS); ax.set_ylim(-0.6, 2.6)
ax.set_xlabel(r"realized $L_\infty$ / nominal budget at the best-certified point")
open_frame(ax); grid(ax, "x")
ax.text(0.0, 1.02, "certified external rows, n = %d" % len(cb), transform=ax.transAxes, fontsize=5.4, color=MID, va="bottom")

# ---- d: eligible systems -----------------------------------------------------------------------------
pg.letter("d", 94.0, 61.0)
ax = pg.ax(RX, BOT, PW, PH)
for yrow, t in zip((2, 1, 0), TAU):
    n = int(elig.loc[t])
    ax.barh(yrow, n, height=0.52, color=DARK_B, lw=0, zorder=2)
    ax.barh(yrow, n_complete - n, left=n, height=0.52, color=RED, alpha=0.85, lw=0, zorder=2)
    ax.text(n / 2, yrow, "%d eligible" % n, ha="center", va="center", fontsize=5.8, color="white", fontweight="bold")
    ax.text(n + (n_complete - n) / 2, yrow, ("%d non-evaluable" if t == TAU[0] else "%d") % (n_complete - n),
            ha="center", va="center", fontsize=5.8,
            color="white", fontweight="bold")
ax.set_xlim(0, n_complete); ax.set_ylim(-0.6, 2.6)
ax.set_xticks([0, 16, 32, 48, 63])
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([thr_label(t) for t in TAU])
ax.set_xlabel("external systems (eligible | non-evaluable)")
ax.set_ylabel(r"Bader contract $\tau$")
open_frame(ax)
ax.text(0.0, 1.03, "%d / %d systems complete; %d pipeline failures; %d bound violations; %s retained rows"
        % (n_complete, A["n_materials_observed"], A["n_material_pipeline_failures"], A["n_bound_violations"],
           format(A["n_rows"], ",")), transform=ax.transAxes, fontsize=5.2, color=MID, ha="left", va="bottom")
layout.audit(pg.fig)
pg.save(HERE, "Fig8")
