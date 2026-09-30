"""Figure 1 -- the measurement contract: QSQ qualifies the reference QoI before codec fidelity is scored.

183 x 112 mm.
  a  the objects the contract acts on, for one real material and one frozen benchmark row
     (KCN, mp-676693; ZFP at nominal relative tolerance 1e-3): reference density, its Bader basins,
     the decoded error and the voxels whose basin owner changes. OVITO renders from
     render3d/build_kcn.py (fields regenerated and gated by render3d/prep_fields.py). One red: the
     reassigned voxels.
  b  the contract as one track (metro-map style, no box-and-arrow flowchart): parameters are stations,
     the two qualification axes are soft bands, failing verdicts leave the track as curved branches
     that carry their condition. One red: the non-evaluable branch.
Numbers quoted in a are the frozen benchmark row (benchmark/master_benchmark_full.csv).

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig1.py   -> Fig1.{svg,pdf,png}
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np  # noqa: E402
import figdata as D  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, PathPatch  # noqa: E402
from matplotlib.path import Path  # noqa: E402
from style import (DARK_B, DARK_G, ELEM, GREEN, INK, MID, NEG_C, OTHER, POS_C, RED, TINT_B, TINT_G,  # noqa: E402
                   Page, place_render)
import layout  # noqa: E402

W = 183.0
HB = 50.0                   # panel b (the contract as a track); panel a sits above it
HA = 52.0
H = HB
pg = Page(W, HB + HA)
cv = pg.canvas(0, 0, W, HB)

# ---- panel b: the contract as one track (metro-map style) --------------------------------------------
# One line carries a material through the contract; each parameter is a station on it. The two
# qualification axes are soft bands behind the line, and the two failing verdicts leave the line as
# curved branches. No boxes, no yes/no arrows: the branch carries its failing condition.
SERIF, MATHF = "Times New Roman", "stix"
Y0 = 27.0                                  # the track
SYM, DESC, TITLE = 9.0, 6.0, 7.2           # pt


def t(x, y, s, size, color=INK, weight="normal", ha="center", va="center", style="normal", **kw):
    return cv.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, family=SERIF,
                   math_fontfamily=MATHF, fontstyle=style, zorder=6, **kw)


def seg(x0, x1, color, lw=2.2):
    cv.plot([x0, x1], [Y0, Y0], color=color, lw=lw, solid_capstyle="round", zorder=2)


def station(x, sym, desc, ring, r=1.35, fill="white", sym_color="#1F2A44"):
    cv.add_patch(Circle((x, Y0), r, facecolor=fill, edgecolor=ring, lw=1.1, zorder=4))
    t(x, Y0 + 4.6, sym, SYM, sym_color, va="bottom")
    if desc:
        t(x, Y0 - 3.4, desc, DESC, "#2E3440", va="top", linespacing=1.15)


def gate(x, cond, color=INK):
    """A decision on the track: a small solid node with the passing condition above it."""
    cv.add_patch(Circle((x, Y0), 0.95, facecolor=color, edgecolor="white", lw=0.6, zorder=5))
    t(x, Y0 + 4.6, cond, SYM - 0.8, color, va="bottom")


def branch(x0, x1, y1, color, cond, verdict, note, text_color=None):
    """Failing verdict: a smooth curve leaving the track, a terminal node and its label."""
    tc = text_color or color                           # a light line may carry dark text (no light-grey text)
    p = Path([(x0, Y0), (x0 + 0.55 * (x1 - x0), Y0), (x1 - 0.2 * (x1 - x0), y1), (x1, y1)],
             [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])
    cv.add_patch(PathPatch(p, facecolor="none", edgecolor=color, lw=1.5, capstyle="round", zorder=1))
    cv.add_patch(Circle((x1, y1), 1.25, facecolor=color, edgecolor="white", lw=0.6, zorder=5))
    t(x0 + 0.62 * (x1 - x0) - 1.0, (Y0 + y1) / 2 - 0.4, cond, SYM - 1.4, tc, ha="right")
    t(x1 + 2.4, y1 + 0.9, verdict, DESC + 0.6, tc, weight="bold", ha="left", va="bottom")
    t(x1 + 2.4, y1 - 0.4, note, DESC - 0.4, "#2E3440", ha="left", va="top")


def band(x0, x1, fill, title, color):
    cv.add_patch(FancyBboxPatch((x0, Y0 - 12.5), x1 - x0, 25.5, boxstyle="round,pad=0,rounding_size=6.0",
                                facecolor=fill, edgecolor="none", alpha=0.75, zorder=0))
    t((x0 + x1) / 2, Y0 + 16.8, title, TITLE, color, weight="bold", va="bottom")


# x positions (mm) of stations, gates and terminals along the track
XT, XP, XF, XG1, XR, XQ, XG2, XC = 15.0, 45.0, 66.0, 86.0, 104.0, 124.0, 145.0, 170.0

band(33.0, 78.0, TINT_G, "Axis 1  \u00b7  QoI Stability Qualification", DARK_G)
band(94.0, 136.0, TINT_B, "Axis 2  \u00b7  Compression evaluation", DARK_B)
t(XT, Y0 + 16.8, "Scientific target", TITLE, INK, weight="bold", va="bottom")
t(XC, Y0 + 16.8, "Certified", TITLE, DARK_G, weight="bold", va="bottom")

# the track, coloured by what it is carrying
seg(XT, 36.0, "#5A7BA6")
seg(36.0, XG1, DARK_G)
seg(XG1, XG2, DARK_B)
seg(XG2, XC, GREEN)
for xa in (27.0, 96.0, 157.0):                         # direction of travel
    cv.annotate("", xy=(xa + 1.6, Y0), xytext=(xa, Y0), zorder=3,
                arrowprops=dict(arrowstyle="-|>", lw=0, color="white", mutation_scale=6, shrinkA=0, shrinkB=0))

station(XT, r"$\mathit{\rho}\,,\ \mathit{Q}[\mathit{\rho}]\,,\ \mathit{\tau}$",
        "reference density, downstream\nQoI, requested tolerance", "#5A7BA6")
station(XP, r"$\mathit{\rho} + \mathit{\delta}_\mathit{k}$", "5 pre-specified\nperturbations", DARK_G)
station(XF, r"$\mathit{f}_\mathrm{m} = \max_\mathit{k}\,|\Delta\mathit{Q}_\mathit{k}|$", "stability floor", DARK_G)
gate(XG1, r"$\mathit{f}_\mathrm{m} < \mathit{\tau}$", DARK_G)
station(XR, r"$\tilde{\mathit{\rho}}$", "decoded density\nZFP \u00b7 SZ3 \u00b7 SPERR", DARK_B)
station(XQ, r"$\Delta\mathit{Q} = \mathit{Q}[\tilde{\mathit{\rho}}] - \mathit{Q}[\mathit{\rho}]$", "same analysis,\nreconstructed field",
        DARK_B)
gate(XG2, r"$|\Delta\mathit{Q}| < \mathit{\tau}$", DARK_B)
cv.add_patch(Circle((XC, Y0), 2.1, facecolor=GREEN, edgecolor="white", lw=0.8, zorder=5))
cv.plot([XC - 0.95, XC - 0.2, XC + 1.0], [Y0 + 0.05, Y0 - 0.75, Y0 + 0.85], color="white", lw=1.1,
        solid_capstyle="round", solid_joinstyle="round", zorder=6)        # check mark
t(XC, Y0 - 3.6, "eligible and\nwithin " + r"$\mathit{\tau}$", DESC, "#2E3440", va="top", linespacing=1.15)

branch(XG1, XG1 + 11.0, 7.0, RED, r"$\mathit{f}_\mathrm{m} \geq \mathit{\tau}$", "non-evaluable",
       "the reference QoI cannot support " + r"$\mathit{\tau}$")
branch(XG2, XG2 + 10.0, 7.0, OTHER, r"$|\Delta\mathit{Q}| \geq \mathit{\tau}$", "eligible, not certified",
       "the KCN row in a", text_color=MID)
# ==== panel a: the objects, one material, one frozen row ===================================================
bench = D.master()
row = bench[(bench.material_id == "mp-676693") & (bench.codec.str.upper() == "ZFP")
            & np.isclose(bench.nominal_tolerance_relative, 1e-3)].iloc[0]
assert abs(row.realized_Linf - 0.1032119735) < 1e-9 and abs(row.Bader_error_resolved_e - 4.444881e-3) < 1e-9
assert bool(row["eligible_A1_at_0.001"]) and not bool(row["certified_at_0.001"])
import json  # noqa: E402
RP = json.load(open(os.path.join(os.path.dirname(HERE), "render3d", "renders", "kcn_render_params.json")))

pg.letter("a", 2.0, HB + HA - 0.5)
pg.letter("b", 2.0, HB - 0.5)
RY, RH = HB + 12.5, 35.0                                          # render row: bottom, height (mm)
slots = (  # centre x, render, title, two detail lines
    (22.0, "kcn_rho.png", r"reference density $\rho$", "KCN (mp-676693)", r"isosurface 0.60 e $\AA^{-3}$", ""),
    (67.0, "kcn_basins.png", r"$Q[\rho]$: Bader basins", "surface coloured by", "the owning atom", ""),
    (116.0, "kcn_drho_zfp_1e-3.png", r"$\Delta\rho = \tilde\rho - \rho$",
     r"ZFP, nominal $10^{-3}$, CR %.1f$\times$" % row.compression_ratio,
     r"isosurfaces $\pm$%.1f $\times 10^{-4}$ e $\AA^{-3}$" % (1e4 * RP["drho_iso_e_per_A3"]), ""),
    (161.0, "kcn_moved_zfp_1e-3.png", r"$Q[\tilde\rho]$: basins re-derived",
     "%.2f %% of voxels change owner" % (100 * row.frac_voxels_reassigned),
     r"$|\Delta Q|$ = %.1f $\times 10^{-3}$ e $> \tau = 10^{-3}$ e" % (1e3 * row.Bader_error_resolved_e),
     r"$\rightarrow$ eligible, not certified"),
)
for i, (xc, name, title, l1, l2, l3) in enumerate(slots):
    place_render(pg, name, xc - 20.0, RY, 40.0, RH, anchor="S")
    fy = RY - 1.2
    pg.fig.text(xc / W, fy / (HB + HA), title, fontsize=6.2, fontweight="bold", ha="center", va="top")
    pg.fig.text(xc / W, (fy - 3.1) / (HB + HA), l1, fontsize=5.4, color=MID, ha="center", va="top")
    pg.fig.text(xc / W, (fy - 5.7) / (HB + HA), l2, fontsize=5.4, color=MID, ha="center", va="top")
    pg.fig.text(xc / W, (fy - 8.3) / (HB + HA), l3, fontsize=5.4, color=INK, ha="center", va="top")
ta = pg.canvas(0, HB, W, HA)
for (x0, x1, lab) in ((40.0, 48.0, "Bader"), (86.0, 96.0, "compress,\ndecode"), (135.0, 142.0, "re-derive\nQ")):
    ya = RY - HB + RH * 0.55
    ta.annotate("", xy=(x1, ya), xytext=(x0, ya), arrowprops=dict(arrowstyle="-|>", lw=0.7, color=INK,
                                                                     mutation_scale=6, shrinkA=0, shrinkB=0))
    ta.text((x0 + x1) / 2, ya + 1.6, lab, fontsize=5.2, ha="center", va="bottom", color=INK, linespacing=1.05)
# keys: elements (renders 1-4), sign of the decoded error (render 3), reassigned voxel (render 4)
kx, ky = 9.0, HA - 2.6
for j, (s, c) in enumerate(ELEM.items()):
    ta.scatter([kx + 1 + 7.0 * j], [ky], s=9, color=c, lw=0)
    ta.text(kx + 2.4 + 7.0 * j, ky, s, fontsize=5.4, va="center")
for j, (lab, c) in enumerate(((r"$\Delta\rho > 0$", POS_C), (r"$\Delta\rho < 0$", NEG_C))):
    x = 99.0 + 15.0 * j
    ta.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle((x, ky - 1.0), 2.4, 2.0, color=c, lw=0))
    ta.text(x + 3.2, ky, lab, fontsize=5.4, va="center")
ta.scatter([146.0], [ky], s=9, color=RED, lw=0)
ta.text(147.4, ky, "voxel whose Bader owner changed", fontsize=5.4, va="center")

layout.audit(pg.fig)
pg.save(HERE, "Fig1")
