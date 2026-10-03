"""Figure 1 -- qualification, certification and diagnosis of a scientific measurement contract.

183 x 112 mm.
  a  the objects the contract acts on, for one real material and one frozen benchmark row
     (KCN, mp-676693; ZFP at nominal relative tolerance 1e-3): reference density, its Bader basins,
     the decoded error and the voxels whose basin owner changes. OVITO renders from
     render3d/build_kcn.py (fields regenerated and gated by render3d/prep_fields.py). One red: the
     reassigned voxels.
  b  the workflow as one track (metro-map style, no box-and-arrow flowchart): parameters are stations,
     qualification and certification are soft bands, and every decision ends on one of three lines that
     terminate in the diagnosis band (certified, not certified, non-evaluable). One red: the
     non-evaluable line.
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
HB = 54.0                   # panel b (the workflow as a track); panel a sits above it
HA = 52.0
pg = Page(W, HB + HA)
cv = pg.canvas(0, 0, W, HB)

# ---- panel b: qualification -> certification -> diagnosis as one track (metro-map style) ----------------
# One line carries a material-contract pair through the workflow; parameters are stations. Qualification and
# certification are soft bands; each decision is a small node with its passing condition. Every decision ends
# on one of three lines that terminate side by side in the diagnosis band: certified (the main line),
# not certified (leaves at the certification gate) and non-evaluable (leaves at the qualification gate).
# No boxes and no yes/no arrows. Text is Arial like the data panels; symbols are Arial italic.
Y0 = 34.0                                  # the main track
YN, YE = 23.0, 12.0                        # not-certified and non-evaluable lines
SYM, DESC, TITLE = 8.4, 5.8, 7.0           # pt
TXT = "#2E3440"


def t(x, y, s, size, color=INK, weight="normal", ha="center", va="center", **kw):
    return cv.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, zorder=6, **kw)


def seg(x0, x1, y, color, lw=2.2):
    cv.plot([x0, x1], [y, y], color=color, lw=lw, solid_capstyle="round", zorder=2)


def station(x, sym, desc, ring, r=1.35):
    cv.add_patch(Circle((x, Y0), r, facecolor="white", edgecolor=ring, lw=1.1, zorder=4))
    t(x, Y0 + 4.4, sym, SYM, "#1F2A44", va="bottom")
    t(x, Y0 - 3.3, desc, DESC, TXT, va="top", linespacing=1.15)


def gate(x, cond, color):
    """A decision on the track: a small solid node with the passing condition above it."""
    cv.add_patch(Circle((x, Y0), 0.95, facecolor=color, edgecolor="white", lw=0.6, zorder=5))
    t(x, Y0 + 4.4, cond, SYM - 0.8, color, va="bottom")


def leave(x0, x1, y1, color, cond, text_color):
    """A failing verdict leaves the main line as a smooth curve and runs on at y1."""
    p = Path([(x0, Y0), (x0 + 0.5 * (x1 - x0), Y0), (x1 - 0.5 * (x1 - x0), y1), (x1, y1)],
             [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])
    cv.add_patch(PathPatch(p, facecolor="none", edgecolor=color, lw=1.6, capstyle="round", zorder=1))
    t(x0 + 0.42 * (x1 - x0) - 1.2, (Y0 + y1) / 2 - 0.6, cond, SYM - 1.6, text_color, ha="right")


def band(x0, x1, y0, y1, fill, title, color):
    cv.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=5.0",
                                facecolor=fill, edgecolor="none", alpha=0.8, zorder=0))
    t((x0 + x1) / 2, Y0 + 14.2, title, TITLE, color, weight="bold", va="bottom")


def terminal(y, color, label, line1, line2, label_color, check=False):
    cv.add_patch(Circle((XE, y), 2.0 if check else 1.3, facecolor=color, edgecolor="white", lw=0.7, zorder=5))
    if check:
        cv.plot([XE - 0.95, XE - 0.2, XE + 1.0], [y + 0.05, y - 0.75, y + 0.85], color="white", lw=1.1,
                solid_capstyle="round", solid_joinstyle="round", zorder=6)
    t(XE + 3.6, y + 2.3, label, DESC + 0.6, label_color, weight="bold", ha="left")
    t(XE + 3.6, y - 0.1, line1, DESC - 0.4, TXT, ha="left")
    t(XE + 3.6, y - 2.4, line2, DESC - 0.4, TXT, ha="left")


# x positions (mm): contract, probes, floor, gate 1, decoded field, QoI error, gate 2, terminals
XT, XP, XF, XG1, XR, XQ, XG2, XE = 14.0, 42.0, 63.0, 82.0, 97.0, 117.0, 131.0, 143.0

band(31.0, 77.0, Y0 - 10.0, Y0 + 12.5, TINT_G, "Qualification", DARK_G)
band(91.0, 127.0, Y0 - 10.0, Y0 + 12.5, TINT_B, "Certification", DARK_B)
band(137.5, 182.0, YE - 6.0, Y0 + 12.5, "#F1EFEC", "Diagnosis", INK)
t(XT, Y0 + 14.2, "Measurement contract", TITLE, INK, weight="bold", va="bottom")

# the main line, coloured by what it is carrying, and the two lines that leave it
seg(XT, 34.0, Y0, "#5A7BA6")
seg(34.0, XG1, Y0, DARK_G)
seg(XG1, XG2, Y0, DARK_B)
seg(XG2, XE, Y0, GREEN)
leave(XG1, XG1 + 8.5, YE, RED, r"$\mathit{f}_\mathit{C} \geq \mathit{\tau}$", RED)
seg(XG1 + 8.5, XE, YE, RED, lw=1.6)
leave(XG2, XE - 0.5, YN, OTHER, r"$|\Delta\mathit{Q}| \geq \mathit{\tau}$", MID)
for xa, ya, col in ((25.0, Y0, "white"), (106.0, Y0, "white"), (120.0, YE, "white")):   # direction of travel
    cv.annotate("", xy=(xa + 1.6, ya), xytext=(xa, ya), zorder=3,
                arrowprops=dict(arrowstyle="-|>", lw=0, color=col, mutation_scale=6, shrinkA=0, shrinkB=0))

station(XT, r"$\mathit{\rho},\ \mathit{Q},\ \mathit{\tau}$",
        "QoI, algorithm, tolerance,\nexact or approximate inputs", "#5A7BA6")
station(XP, r"$\mathit{\rho} + \mathit{\delta}_\mathit{k}$", "probes on the\napproximate inputs", DARK_G)
station(XF, r"$\mathit{f}_\mathit{C} = \max_\mathit{k}\,|\Delta\mathit{Q}_\mathit{k}|$", "stability floor", DARK_G)
gate(XG1, r"$\mathit{f}_\mathit{C} < \mathit{\tau}$", DARK_G)
station(XR, r"$\tilde{\mathit{\rho}}$", "decoded field\nZFP · SZ3 · SPERR", DARK_B)
station(XQ, r"$\Delta\mathit{Q}$", "same analysis on\nthe decoded field", DARK_B)
gate(XG2, r"$|\Delta\mathit{Q}| < \mathit{\tau}$", DARK_B)

terminal(Y0, GREEN, "certified", "valid for this QoI, " + r"$\mathit{\tau}$" + " and contract",
         "certificate stored with the field", DARK_G, check=True)
terminal(YN, OTHER, "not certified", "error spectrum × downstream operator",
         "→ tighter setting or another codec", MID)
terminal(YE, RED, "non-evaluable", "Bader: the partition-defining field",
         "→ change the contract or " + r"$\mathit{\tau}$", RED)

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
     r"$\rightarrow$ not certified"),
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
