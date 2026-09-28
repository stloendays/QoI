"""Supplementary Figure S5 -- the Bader mechanism is robust to an independent implementation.

183 x 118 mm, 2x2:
  a  exact BaderKit decomposition, domain vs integrand term by perturbation kind   mechanism/independent_bader_20260908/mechanism_domain_decomposition.csv
  b  QSQ floor, BaderKit vs Henkelman on-grid / near-grid                        mechanism/independent_bader_20260908/stability_comparison.csv
  c  paired codec responses above the print-resolution region                    supplement/S11_cross_implementation_pairs.csv
  d  spatial-reorganization controls, median log2 ratio with IQR                 supplement/S11_spatial_control_summary.csv

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS5.py   -> FigS5.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (BLUE, CODEC_DARK, CODECS, DARK_B, DARK_G, GREEN, INK, MID, OTHER, PALE, RED, Page, grid,  # noqa: E402
                   log_ticks, note, open_frame)

dec = D.csv("mechanism", "independent_bader_20260908", "mechanism_domain_decomposition.csv")
stab = D.csv("mechanism", "independent_bader_20260908", "stability_comparison.csv")
pairs = D.supp("S11_cross_implementation_pairs.csv")
impl = D.supp("S11_independent_implementation_summary.csv")
spatial = D.supp("S11_spatial_control_summary.csv")
dec = dec[~D.truthy(dec.sentinel)]
stab = stab[~D.truthy(stab.sentinel)]
assert (dec.kind == "codec").sum() == 70 and (dec.kind == "noise").sum() == 60 and (dec.kind == "spatial_control").sum() == 324 and (dec.kind == "float32").sum() == 12
assert len(pairs) == 140 and len(spatial) == 9 and stab.material.nunique() == 12
above = pairs[D.truthy(pairs["above_2e-6_print_region"])]
stats = {s: impl[(impl.metric == "codec_response_ratio") & (impl.solver == s) & (impl["filter"] == "above_print_resolution")].iloc[0]
         for s in ("henkelman_ongrid", "henkelman_neargrid")}
assert abs(stats["henkelman_ongrid"]["median"] - 1.0) < 0.01

pg = Page(183.0, 118.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 40.0
TOP, BOT = 68.0, 12.0

# ---- a ---------------------------------------------------------------------------------------
pg.letter("a", 2.0, 117.0)
ax = pg.ax(LX, TOP, PW, PH)
KIND = (("codec", "codec", DARK_B, "o"), ("noise", "QSQ perturbation", DARK_G, "^"),
        ("spatial_control", "spatial control", PALE, "s"), ("float32", "float32 control", RED, "D"))
lo, hi = 1e-12, 10
ax.plot([lo, hi], [lo, hi], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=2)
handles = []
for key, lab, col, mk in KIND:
    s = dec[dec.kind == key]
    ax.scatter(np.maximum(s.integrand_max_e, lo), np.maximum(s.domain_max_e, lo), s=8, c=col, marker=mk, alpha=0.6, linewidths=0, zorder=3)
    handles.append(Line2D([], [], marker=mk, ls="none", color=col, ms=3.2, label="%s (n = %d)" % (lab, len(s))))
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xticks([1e-12, 1e-9, 1e-6, 1e-3, 1e0]); ax.set_yticks([1e-12, 1e-9, 1e-6, 1e-3, 1e0])
ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator()); ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
ax.set_xlabel(r"integrand contribution, max $|\Delta Q|$ (e)"); ax.set_ylabel(r"domain-migration contribution, max $|\Delta Q|$ (e)")
open_frame(ax); grid(ax)
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right")
ax.text(0.03, 0.97, "exact BaderKit decomposition; sentinel excluded", transform=ax.transAxes, fontsize=5.4, color=MID, va="top")

# ---- b: floors across implementations ------------------------------------------------------------------
pg.letter("b", 94.0, 117.0)
ref = stab[stab.solver == "baderkit_ongrid"].set_index("material").probe_response_max_e
dom = pairs.drop_duplicates("material").set_index("material").domain
for k, (sol, lab) in enumerate((("henkelman_ongrid", "Henkelman on-grid"), ("henkelman_neargrid", "Henkelman near-grid"))):
    ax = pg.ax(RX + k * 36.0, TOP, 30.0, PH)
    s = stab[stab.solver == sol].set_index("material")
    x = np.maximum(ref.loc[s.index], 1e-9); y = np.maximum(s.probe_response_max_e, 1e-9)
    assert len(s) == 12
    ax.plot([1e-9, 10], [1e-9, 10], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=2)
    for st, mk in (("bulk", "o"), ("slab", "^")):
        sel = dom.loc[s.index] == st
        ax.scatter(x[sel], y[sel], s=12, c=DARK_G, marker=mk, alpha=0.75, linewidths=0, zorder=3)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e-9, 10); ax.set_ylim(1e-9, 10)
    ax.set_xticks([1e-9, 1e-6, 1e-3, 1e0]); ax.set_yticks([1e-9, 1e-6, 1e-3, 1e0])
    ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator()); ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
    if k == 1:
        ax.set_yticklabels([])
    else:
        ax.set_ylabel("independent-implementation\nQSQ floor (e)")
    ax.set_xlabel("BaderKit on-grid QSQ floor (e)")
    ax.set_title(lab, loc="left", fontsize=6.0, fontweight="bold", pad=2)
    open_frame(ax); grid(ax)
    if k == 1:
        handles = [Line2D([], [], marker="o", ls="none", color=DARK_G, ms=3, label="bulk"),
                   Line2D([], [], marker="^", ls="none", color=DARK_G, ms=3, label="slab")]
        layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right")

# ---- c: paired codec responses -----------------------------------------------------------------------------
pg.letter("c", 2.0, 61.0)
for k, (sol, lab) in enumerate((("henkelman_ongrid", "Henkelman on-grid"), ("henkelman_neargrid", "Henkelman near-grid"))):
    ax = pg.ax(LX + k * 36.0, BOT, 30.0, PH)
    s = above[above.comparison_solver == sol]
    ax.plot([2e-6, 0.4], [2e-6, 0.4], color=INK, lw=0.6, ls=(0, (4, 2)), zorder=2)
    for c in CODECS:
        t = s[s.codec == c]
        ax.scatter(np.maximum(t.baderkit_error_e, 1e-8), np.maximum(t.comparison_error_e, 1e-8), s=8, c=CODEC_DARK[c], alpha=0.7,
                   linewidths=0, zorder=3)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(2e-6, 0.4); ax.set_ylim(2e-6, 0.4)
    ax.set_xticks([1e-5, 1e-3, 1e-1]); ax.set_yticks([1e-5, 1e-3, 1e-1])
    ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator()); ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
    if k == 1:
        ax.set_yticklabels([])
    else:
        ax.set_ylabel("independent-implementation\ncharge error (e)")
    ax.set_xlabel("BaderKit charge error (e)")
    ax.set_title(lab, loc="left", fontsize=6.0, fontweight="bold", pad=2)
    open_frame(ax); grid(ax)
    st = stats[sol]
    note(ax, 0.04, 0.96, "n = %d\nmedian ratio %.3f\nIQR %.3f\u2013%.3f" % (len(s), st["median"], st.q25, st.q75), size=5.2)
    if k == 1:
        handles = [Line2D([], [], marker="o", ls="none", color=CODEC_DARK[c], ms=3, label=c) for c in CODECS]
        layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower right")

# ---- d: spatial controls ----------------------------------------------------------------------------------
pg.letter("d", 94.0, 61.0)
ax = pg.ax(RX, BOT, PW, PH)
CTRL = (("global", "global shuffle"), ("shift", "periodic shift"), ("stratified", "stratified shuffle"))
SOLV = (("baderkit_ongrid", "BaderKit on-grid", DARK_B), ("henkelman_ongrid", "Henkelman on-grid", DARK_G),
        ("henkelman_neargrid", "Henkelman near-grid", PALE))
ax.axhline(0, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
for j, (sol, lab, col) in enumerate(SOLV):
    for i, (ck, cl) in enumerate(CTRL):
        r = spatial[(spatial.solver == sol) & (spatial.control == ck)].iloc[0]
        x = i + (j - 1) * 0.2
        ax.plot([x, x], [r.q25, r.q75], color=col, lw=0.9, zorder=3)
        ax.scatter([x], [r.median_log2_control_over_codec], s=18, c=col, zorder=4, linewidths=0)
ax.set_xticks(range(3)); ax.set_xticklabels([c[1] for c in CTRL]); ax.set_xlim(-0.6, 2.6)
ax.set_ylabel(r"$\log_2$(control error / codec error)")
open_frame(ax); grid(ax, "y")
handles = [Line2D([], [], marker="o", ls="none", color=c, ms=3.2, label=l) for _, l, c in SOLV]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper right")
ax.text(0.02, 0.03, "median with IQR; n = 36 pairs per point", transform=ax.transAxes, fontsize=5.4, color=MID)

layout.audit(pg.fig)
pg.save(HERE, "FigS5")
