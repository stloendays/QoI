"""TOC / graphical abstract -- 83 x 44 mm (ACS TOC box), same renders and palette as Figs. 1, 5 and 7.

Left to right: the reference density, the decoded error, the voxels whose Bader owner changes (KCN,
mp-676693, ZFP nominal 1e-3), then the prospective result of Fig. 3a (fresh-trial exceedance at
tau = 1e-3 e, eligible vs screen-rejected). Numbers come from the frozen tables through figdata.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_toc.py   -> TOC.{svg,pdf,png}
"""
import os
import sys

from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import DARK_B, DARK_G, INK, MID, RED, TINT_B, TINT_R, Page, place_render  # noqa: E402

p2 = D.p2_fresh_probes()
pe = p2[(p2.tau_e == 1e-3) & (p2.gate_group == "eligible")].iloc[0]
pr = p2[(p2.tau_e == 1e-3) & (p2.gate_group == "screen_rejected")].iloc[0]
assert (pe.n_materials, pr.n_materials) == (143, 111)
fe, fr = 100 * pe.valid_trial_exceedance_fraction, 100 * pr.valid_trial_exceedance_fraction
assert abs(fe - 1.60) < 0.005 and abs(fr - 81.33) < 0.005, (fe, fr)

W, H = 83.0, 44.0
pg = Page(W, H)
cv = pg.canvas(0, 0, W, H)
cv.text(W / 2, H - 1.6, "Certify compression on the chemistry, after qualifying the reference",
        fontsize=7.0, fontweight="bold", ha="center", va="top")

RY, RH = 12.5, 24.0
for xc, png, lab in ((9.5, "kcn_rho.png", r"$\rho$"), (29.0, "kcn_drho_zfp_1e-3.png", r"$\tilde\rho-\rho$"),
                     (48.5, "kcn_moved_zfp_1e-3.png", r"$Q[\tilde\rho]$ basins")):
    place_render(pg, png, xc - 9.5, RY, 19.0, RH, anchor="S")
    cv.text(xc, RY - 0.8, lab, fontsize=7.0, ha="center", va="top")
for x0 in (18.6, 38.1):
    cv.annotate("", xy=(x0 + 2.2, RY + RH * 0.5), xytext=(x0, RY + RH * 0.5),
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=INK, mutation_scale=5, shrinkA=0, shrinkB=0))

# prospective result (Fig. 3a): two cohort cards
x, w = 60.5, 21.5
for y, h, fill, edge, head, val, col in ((22.0, 12.5, TINT_B, DARK_B, "QSQ-eligible", fe, DARK_B),
                                          (7.0, 12.5, TINT_R, RED, "screen-rejected", fr, RED)):
    cv.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0", facecolor=fill,
                                edgecolor=edge, linewidth=0.6))
    cv.text(x + w / 2, y + h - 1.6, head, fontsize=6.0, fontweight="bold", color=col, ha="center", va="top")
    cv.text(x + w / 2, y + 2.0, "%.1f %%" % val, fontsize=9.0, fontweight="bold", color=col, ha="center",
            va="bottom")
cv.text(x + w / 2, 5.6, r"fresh trials exceeding $\tau$", fontsize=6.0, color=INK, ha="center", va="top")
cv.text(1.0, 1.0, "KCN, ZFP: 0.42 % of voxels change Bader owner", fontsize=6.0, color=MID, ha="left",
        va="bottom")

layout.audit(pg.fig)
pg.save(HERE, "TOC")
