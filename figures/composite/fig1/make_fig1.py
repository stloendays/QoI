"""Figure 1 -- the measurement contract: QSQ qualifies the reference QoI before codec fidelity is scored.

Schematic only, 183 x 62 mm. No data file. Drawn on a millimetre canvas so box and
arrow geometry is exact. One red: the NON-EVALUABLE branch, which is the thing this
figure introduces.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig1.py   -> Fig1.{svg,pdf,png}
"""
import os
import sys

from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from style import (DARK_B, DARK_G, GREEN, INK, LINE, MID, OTHER, RED, TINT_B, TINT_G, TINT_R,  # noqa: E402
                   Page)
import layout  # noqa: E402

W, H = 183.0, 62.0
pg = Page(W, H)
cv = pg.canvas(0, 0, W, H)


def box(x, y, w, h, fill, edge, lw=0.7, r=1.2):
    cv.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=%.2f" % r,
                                facecolor=fill, edgecolor=edge, linewidth=lw, zorder=2))


def text(x, y, s, size=6.0, weight="normal", color=INK, ha="center", va="center", **kw):
    cv.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha, va=va, zorder=4, **kw)


def arrow(x0, y0, x1, y1, color=INK, lw=0.7):
    cv.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=3,
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, mutation_scale=6,
                                shrinkA=0, shrinkB=0))


# ---- the main flow, left to right, box tops aligned at y = 52 ---------------------------
YT, BH = 52.0, 20.0           # top of the flow row and its box height
Y0 = YT - BH
DH = 13.0                     # decision-box height, vertically centred on the row
YD = Y0 + (BH - DH) / 2

# 1 scientific target
x, w = 3.0, 30.0
box(x, Y0, w, BH, TINT_B, DARK_B)
text(x + w / 2, YT - 3.6, "Scientific target", 6.6, "bold")
text(x + w / 2, YT - 8.3, r"reference density $\rho$", 5.8, color=DARK_B)
text(x + w / 2, YT - 12.2, r"downstream QoI $Q[\rho]$", 5.8)
text(x + w / 2, YT - 16.1, r"requested tolerance $\tau$", 5.8, color=DARK_G)
arrow(x + w, YT - BH / 2, x + w + 4.0, YT - BH / 2)

# 2 QSQ
x, w = 37.0, 34.0
box(x, Y0, w, BH, TINT_G, DARK_G)
text(x + w / 2, YT - 3.6, "QoI Stability Qualification", 6.6, "bold")
text(x + w / 2, YT - 8.3, "5 pre-specified perturbations", 5.8, color=MID)
text(x + w / 2, YT - 12.2, "re-derive the downstream QoI", 5.8, color=MID)
text(x + w / 2, YT - 16.1, r"stability floor  $f_m$ = max response", 5.8, color=DARK_G)
arrow(x + w, YT - BH / 2, x + w + 4.0, YT - BH / 2)

# 3 decision 1
x, w = 75.0, 20.0
box(x, YD, w, DH, "white", INK, lw=0.8)
text(x + w / 2, YD + DH - 4.2, r"$f_m < \tau$ ?", 6.8, "bold")
text(x + w / 2, YD + 3.6, "reference QoI eligible?", 5.3, color=MID)
arrow(x + w, YT - BH / 2, x + w + 4.0, YT - BH / 2, color=DARK_G)
text(x + w + 2.0, YT - BH / 2 + 1.6, "yes", 5.4, "bold", color=DARK_G)
# NO branch, down
arrow(x + w / 2, YD, x + w / 2, 21.0, color=RED)
text(x + w / 2 + 1.4, (YD + 21.0) / 2, "no", 5.4, "bold", color=RED, ha="left")

# 4 compression evaluation
x, w = 99.0, 32.0
box(x, Y0, w, BH, TINT_B, DARK_B)
text(x + w / 2, YT - 3.6, "Compression evaluation", 6.6, "bold")
text(x + w / 2, YT - 8.3, "ZFP  \u00b7  SZ3  \u00b7  SPERR", 5.8, color=DARK_B)
text(x + w / 2, YT - 12.2, r"decode $\tilde\rho$", 5.8, color=MID)
text(x + w / 2, YT - 16.1, r"re-derive $Q[\tilde\rho]$, same analysis", 5.8, color=MID)
arrow(x + w, YT - BH / 2, x + w + 4.0, YT - BH / 2)

# 5 decision 2
x, w = 135.0, 20.0
box(x, YD, w, DH, "white", INK, lw=0.8)
text(x + w / 2, YD + DH - 4.2, r"$|\Delta Q| < \tau$ ?", 6.8, "bold")
text(x + w / 2, YD + 3.6, "reconstruction agrees?", 5.3, color=MID)
arrow(x + w, YT - BH / 2, x + w + 4.0, YT - BH / 2, color=DARK_G)
text(x + w + 2.0, YT - BH / 2 + 1.6, "yes", 5.4, "bold", color=DARK_G)
arrow(x + w / 2, YD, x + w / 2, 21.0, color=OTHER)
text(x + w / 2 + 1.4, (YD + 21.0) / 2, "no", 5.4, "bold", color=MID, ha="left")

# 6 certified
x, w = 159.0, 21.0
box(x, YD, w, DH, TINT_G, GREEN)
text(x + w / 2, YD + DH - 4.2, "CERTIFIED", 6.6, "bold", color=DARK_G)
text(x + w / 2, YD + 3.6, "eligible and within $\\tau$", 5.3)

# ---- the two outcome boxes on the lower row ----------------------------------------------
OY, OH = 10.0, 11.0
x, w = 66.0, 38.0
box(x, OY, w, OH, TINT_R, RED)
text(x + w / 2, OY + OH - 3.6, "NON-EVALUABLE", 6.6, "bold", color=RED)
text(x + w / 2, OY + 3.4, "reference QoI cannot support $\\tau$;\nfixed-pipeline codec agreement may still be reported",
     5.0, color=INK, linespacing=1.15)

x, w = 126.0, 38.0
box(x, OY, w, OH, "white", OTHER)
text(x + w / 2, OY + OH - 3.6, "ELIGIBLE, NOT CERTIFIED", 6.6, "bold", color=MID)
text(x + w / 2, OY + 3.4, "reference is measurable;\nreconstruction misses $\\tau$", 5.0, color=INK, linespacing=1.15)

# ---- the two benchmark axes, as brackets under the flow ------------------------------------
BY = 4.2
for (xa, xb, lab, col) in ((37.0, 95.0, "axis 1   reference stability: can the QoI support $\\tau$?", DARK_G),
                           (99.0, 155.0, "axis 2   reconstruction fidelity: does the decoded field satisfy $\\tau$?", DARK_B)):
    cv.plot([xa, xa, xb, xb], [BY + 1.2, BY, BY, BY + 1.2], color=col, lw=0.6, zorder=3)
    text((xa + xb) / 2, BY - 1.2, lab, 5.4, color=col, va="top")

layout.audit(pg.fig)
pg.save(HERE, "Fig1")
