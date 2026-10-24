"""Supplementary Fig. 1 -- the contract orders codecs at matched density error (185 development materials).

183 x 62 mm:
  a  SZ3/SPERR maximum Bader-error ratio with reference (fixed) basins against the ratio with basins re-derived
     from the decoded density; SPERR is better in 185/185 under fixed basins, the order reverses in 109/185.
  b  re-derived error ratio against the ratio of reassigned-voxel fractions (Spearman 0.607).
  c  Spearman correlation of the re-derived error ratio with four diagnostics, material bootstrap 95% CI.
Every ratio is SZ3/SPERR within one material; one pair per material, matched in realized density L_inf and RMSE
within 0.10 dex without Bader outcomes. Counts and correlations are asserted against the committed summaries.
Source: analysis/contract_codec_order_20261023/.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS_order.py   -> FigS_order.{svg,pdf,png}, FigS_order.tweak_keys.json
Editable in the browser figure editor (desktop shortcut 论文调图, figure-studio assets/figure_hub.py); edits are kept in
FigS_order.tweaks.json and re-applied on every render.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "figures", "composite"))
import layout  # noqa: E402
from style import BLUE, DARK_B, GREEN, INK, MID, OTHER, RED, TINT_R, Page, grid  # noqa: E402

A = os.path.join(ROOT, "analysis", "contract_codec_order_20261023")
P = pd.read_csv(os.path.join(A, "inputs", "matched_real_material_pairs.csv"))
RR = json.load(open(os.path.join(A, "results", "rank_reversal_summary.json"), encoding="utf-8"))
MC = json.load(open(os.path.join(A, "results", "migration_coupling_summary.json"), encoding="utf-8"))
assert len(P) == 185 and P.material_id.is_unique

fixed = np.log10(P.Bader_fixed_error_SZ3_e / P.Bader_fixed_error_SPERR_e)
rederived = np.log10(P.Bader_resolved_error_SZ3_e / P.Bader_resolved_error_SPERR_e)
reassign = np.log10(P.reassigned_fraction_SZ3 / P.reassigned_fraction_SPERR)
rev = (fixed > 0) & (rederived < 0)
assert int((fixed > 0).sum()) == RR["results_by_system"]["all"]["fixed_SPERR_better"] == 185
assert int(rev.sum()) == RR["results_by_system"]["all"]["ranking_reversals"] == 109
STATS = MC["statistics"]["all"]["predictors_vs_rederived_error_ratio"]
assert abs(spearmanr(reassign, rederived).statistic - STATS["reassignment_ratio"]["rho"]) < 1e-12
bulk = P.system_type.eq("bulk").to_numpy()
COL = {"bulk": BLUE, "slab": GREEN}

pg = Page(183.0, 62.0)


def scatter(ax, x, y):
    for kind, m in (("bulk", bulk), ("slab", ~bulk)):
        ax.scatter(x[m], y[m], s=6, color=COL[kind], edgecolor="white", lw=0.25, zorder=3,
                   label="%s (%d)" % ("bulk crystals" if kind == "bulk" else "slabs", int(m.sum())))


pg.letter("a", 2.0, 61.0)
axa = pg.ax(15.0, 11.0, 44.0, 45.0)
axa.axhspan(-1.6, 0.0, color=TINT_R, zorder=0, lw=0)
axa.axhline(0.0, color=MID, lw=0.6, ls="--", zorder=1)
scatter(axa, fixed.to_numpy(), rederived.to_numpy())
axa.set_xlim(0.0, 2.3)
axa.set_ylim(-1.6, 2.8)
axa.set_xlabel("log$_{10}$ SZ3/SPERR, reference basins")
axa.set_ylabel("log$_{10}$ SZ3/SPERR, re-derived basins")
axa.text(0.04, -1.45, "order reversed: %d/185" % int(rev.sum()), fontsize=5.6, color=RED, ha="left", va="bottom")
axa.text(0.04, 2.72, "SPERR better with reference basins: 185/185", fontsize=5.3, color=INK, ha="left", va="top")
grid(axa)

pg.letter("b", 63.0, 61.0)
axb = pg.ax(76.0, 11.0, 44.0, 45.0)
axb.axhline(0.0, color=MID, lw=0.6, ls="--", zorder=1)
axb.axvline(0.0, color=MID, lw=0.6, ls="--", zorder=1)
scatter(axb, reassign.to_numpy(), rederived.to_numpy())
axb.set_xlim(-0.75, 0.2)
axb.set_ylim(-1.6, 2.8)
axb.set_xlabel("log$_{10}$ SZ3/SPERR reassigned-voxel fraction")
axb.set_ylabel("log$_{10}$ SZ3/SPERR, re-derived basins")
r = STATS["reassignment_ratio"]
axb.text(-0.72, 2.72, "Spearman %.3f (%.3f–%.3f)" % (r["rho"], *r["bootstrap95CI"]), fontsize=5.6, ha="left",
         va="top")
axb.legend(loc="lower right", fontsize=5.3, handletextpad=0.2, borderaxespad=0.3)
grid(axb)

pg.letter("c", 124.0, 61.0)
axc = pg.ax(152.0, 11.0, 28.0, 45.0)
rows = (("reassignment_ratio", "reassigned voxels"), ("fixed_bader_ratio", "reference-basin\nBader error"),
        ("density_rmse_ratio", "density RMSE"), ("density_linf_ratio", "density max. error"))
for j, (k, lab) in enumerate(rows):
    o = STATS[k]
    col = RED if j == 0 else DARK_B
    axc.plot(o["bootstrap95CI"], [j, j], color=col, lw=1.2, solid_capstyle="round")
    axc.scatter([o["rho"]], [j], s=12, color=col, zorder=3)
axc.axvline(0.0, color=MID, lw=0.6, ls="--")
axc.set_yticks(range(len(rows)))
axc.set_yticklabels([lab for _, lab in rows], fontsize=5.6)
axc.set_ylim(len(rows) - 0.5, -0.5)
axc.set_xlim(-0.4, 0.8)
axc.set_xticks([-0.4, 0.0, 0.4, 0.8])
axc.set_xlabel("Spearman correlation with\nre-derived error ratio")
axc.tick_params(axis="y", length=0)
grid(axc, axis="x")

layout.audit(pg.fig)
pg.save(HERE, "FigS_order")                     # applies FigS_order.tweaks.json (figures/composite/tweak.py)
