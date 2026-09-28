"""Supplementary Figure S2 -- QSQ probe validation, seed sensitivity and amplitude sensitivity.

183 x 118 mm, 2x2:
  a  exact neighbour ties created, float32 control vs QSQ (18-material calibration)   stability/probe_calibration.csv
  b  voxels reassigned, same comparison
  c  five-seed log10 floor span across all 319 systems                                  stability/stability_floor_A1_per_seed.csv
  d  amplitude sweep x0.1 / x1 / x10 on the 18 calibration materials                    supplement/S4_amplitude_sensitivity.csv

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS2.py   -> FigS2.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import DARK_B, DARK_G, INK, MID, OTHER, PALE, PALE_B, RED, Page, grid, note, open_frame  # noqa: E402

rng = np.random.default_rng(20260905)
cal = D.csv("stability", "probe_calibration.csv")
seed = D.csv("stability", "stability_floor_A1_per_seed.csv")
amp = D.supp("S4_amplitude_sensitivity.csv")
assert cal.material_id.nunique() == 18

cal["seed"] = cal.seed.astype(str)
cp = cal[(cal.amplitude_factor == 1) & cal.seed.isin(["float32", "20260905"])].copy()
assert len(cp) == 36
cp["probe"] = np.where(cp.seed == "float32", "control", "QSQ")

s2 = seed[(seed.floor_noise_resolved_e > 0)].copy()
span = s2.groupby("material_id").floor_noise_resolved_e.agg(lambda v: np.log10(v.max()) - np.log10(v.min()))
assert len(span) == 319
med_span, max_span = float(span.median()), float(span.max())
prim = s2[s2.seed.astype(str) == "20260905"].set_index("material_id").floor_noise_resolved_e
mx = s2.groupby("material_id").floor_noise_resolved_e.max()
flips = [int(((prim < t) != (mx.loc[prim.index] < t)).sum()) for t in (1e-4, 1e-3, 1e-2)]
assert flips == [35, 17, 2], flips

dom = cal.drop_duplicates("material_id").set_index("material_id").domain
amp = amp.assign(domain=amp.material_id.map(dom))
assert amp.domain.notna().all()
shift = amp["log10_floor_x10_over_x0.1"]

pg = Page(183.0, 118.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 40.0
TOP, BOT = 68.0, 12.0
PC = {"control": MID, "QSQ": DARK_B}


def paired_box(ax, col, ylabel, ylabels):
    for j, pr in enumerate(("control", "QSQ")):
        v = np.log10(1 + cp[cp.probe == pr][col].values)
        ax.boxplot([v], positions=[j], widths=0.4, showfliers=False, patch_artist=True,
                   boxprops=dict(facecolor="white", edgecolor=PC[pr], linewidth=0.7),
                   whiskerprops=dict(color=PC[pr], linewidth=0.6), capprops=dict(color=PC[pr], linewidth=0.6),
                   medianprops=dict(color=INK, linewidth=0.9), zorder=3)
        ax.scatter(j + rng.uniform(-0.12, 0.12, len(v)), v, s=7, c=PC[pr], alpha=0.6, linewidths=0, zorder=4)
        ax.text(j, -0.35, "median %.0f" % np.median(cp[cp.probe == pr][col]), ha="center", va="top", fontsize=5.4, color=MID)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["order-preserving\nfloat32 control", "QSQ perturbation"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_yticks(range(len(ylabels))); ax.set_yticklabels(ylabels)
    ax.set_ylabel(ylabel)
    open_frame(ax); grid(ax, "y")


# ---- a ---------------------------------------------------------------------------------------
pg.letter("a", 2.0, 117.0)
ax = pg.ax(LX, TOP, PW, PH)
paired_box(ax, "n_exact_neighbour_ties_created", "exact neighbour ties created", ["0", "9", "99", "999", "9,999"])
ax.set_ylim(-0.9, 4.6)
ax.text(0.0, 1.02, "18 calibration materials, matched perturbation amplitude", transform=ax.transAxes, fontsize=5.4,
        color=MID, va="bottom")

# ---- b ---------------------------------------------------------------------------------------
pg.letter("b", 94.0, 117.0)
ax = pg.ax(RX, TOP, PW, PH)
paired_box(ax, "n_voxels_reassigned", "voxels reassigned", ["0", "9", "99", "999", "9,999", "99,999"])
ax.set_ylim(-1.6, 5.6)
for j, pr in enumerate(("control", "QSQ")):
    z = int((cp[cp.probe == pr].n_voxels_reassigned == 0).sum())
    ax.text(j, -0.95, "zero reassignment %d / 18" % z, ha="center", va="top", fontsize=5.4, color=PC[pr])

# ---- c ---------------------------------------------------------------------------------------
pg.letter("c", 2.0, 61.0)
ax = pg.ax(LX, BOT, PW, PH)
ax.hist(span.values, bins=np.arange(0, max_span + 0.15, 0.15), color=PALE_B, edgecolor="white", lw=0.4, zorder=2)
ax.axvline(med_span, color=RED, lw=0.9, zorder=4)
ax.set_xlabel("within-material five-seed floor span (decades)")
ax.set_ylabel("materials")
open_frame(ax); grid(ax, "y")
note(ax, 0.97, 0.96, "all 319 systems\nmedian %.2f, max %.2f decades\n\nprimary seed vs five-seed max\nchanges the verdict for\n"
     "%d / 319 at $10^{-4}$ e, %d / 319 at $10^{-3}$ e, %d / 319 at $10^{-2}$ e" % (med_span, max_span, *flips),
     ha="right", size=5.4)

# ---- d ---------------------------------------------------------------------------------------
pg.letter("d", 94.0, 61.0)
ax = pg.ax(RX, BOT, PW, PH)
DC = {"bulk": DARK_B, "slab": DARK_G, "vacuum2d": PALE}
DL = {"bulk": "bulk", "slab": "slab", "vacuum2d": "external vacuum-2D"}
for _, r in amp.iterrows():
    ax.plot([0.1, 1, 10], [r["floor_x0.1"], r.floor_x1, r.floor_x10], color=DC[r.domain], lw=0.7, alpha=0.7, marker="o", ms=2.5,
            zorder=3)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xticks([0.1, 1, 10]); ax.set_xticklabels(["\u00d70.1", "\u00d71 (QSQ)", "\u00d710"])
ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
ax.set_xlim(0.05, 20)
ax.set_xlabel("perturbation amplitude relative to the QSQ definition")
ax.set_ylabel("re-derived Bader floor (e)")
open_frame(ax); grid(ax, "y")
handles = [Line2D([], [], color=DC[k], lw=0.9, marker="o", ms=2.5, label="%s (n = %d)" % (DL[k], (amp.domain == k).sum()))
           for k in ("bulk", "slab", "vacuum2d") if (amp.domain == k).any()]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="center", bbox_to_anchor=(0.5, 0.27))
# between 1e-5 and 1e-8 only the two lowest bulk lines pass, and they sit at the edges
note(ax, 0.03, 0.96, "\u00d70.1 \u2192 \u00d710 floor shift\nmedian %.2f decades\nP10 %.2f, P90 %.2f" % (
    shift.median(), shift.quantile(0.10), shift.quantile(0.90)), size=5.4)

layout.audit(pg.fig)
pg.save(HERE, "FigS2")
