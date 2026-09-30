"""Figure 7 -- frequency allocation of reconstruction error controls Hartree fidelity at matched realized L-inf.

2x2, 183 x 120 mm, from the versioned spectral-mechanism outputs (457 ZFP/SZ3 matched pairs, 214 materials):
  a  radial error-energy spectrum, ZFP vs SZ3, median + pairwise IQR    radial_spectrum_summary.csv
  b  Hartree-weighted (|G|^-4) fraction per radial bin
  c  the three decomposition factors, material-level centres + 95% CI   mechanism_ratio_summary.csv
  d  per-material share of |log effect| from spectral susceptibility    matched_pair_mechanism.csv
  e  one matched pair in 3D (pair 266, KCN mp-676693): decoded error and Hartree-potential error for ZFP and
     SZ3, one camera, one isolevel per quantity. OVITO renders from render3d/build_kcn.py; dV_H uses the
     audit's own Nyquist-safe Poisson operator and reproduces the pair's frozen ratio (0.1532).

The one red is the low-G band / the median share line.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig7.py   -> Fig7.{svg,pdf,png}
"""
import os
import sys

import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import (BLUE, CODEC, CODEC_DARK, DARK_B, DARK_G, ELEM, GREEN, INK, MID, NEG_C, OTHER, PALE_B,  # noqa: E402
                   POS_C, RED, TINT_R, Page, grid, log_ticks, note, open_frame, place_render)

R = D.spectral_radial()
M = D.spectral_ratio_summary().set_index("metric")
P = D.spectral_pairs()
S = D.spectral_summary()
assert len(P) == 457 and P.material_id.nunique() == 214 and S["status"] == "FREQUENCY_STRUCTURE_DOMINANT"
assert (R.n == 457).all()
R["q"] = (R.q_low + R.q_high) / 2
share = P.groupby("material_id").spectral_structure_abs_log_share.median()
med_share = float(share.median())
assert abs(med_share - S["mechanism_diagnostics"]["median_material_spectral_structure_abs_log_share"]) < 1e-12
diag = S["mechanism_diagnostics"]

OFF = 50.0                                  # height of the render row e under the original 2x2
pg = Page(183.0, 120.0 + OFF)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 40.0
TOP, BOT = 70.0 + OFF, 12.0 + OFF
TWO = {"ZFP": CODEC_DARK["ZFP"], "SZ3": CODEC_DARK["SZ3"]}


def spectrum(ax, med, lo, hi, ylabel):
    ax.axvspan(0, 0.25, color=TINT_R, alpha=0.6, zorder=0, lw=0)
    for c in ("ZFP", "SZ3"):
        r = R[R.codec == c].sort_values("q")
        ax.fill_between(r.q, r[lo], r[hi], color=TWO[c], alpha=0.18, lw=0, zorder=2)
        ax.plot(r.q, r[med], color=TWO[c], lw=1.1, zorder=3)
    ax.set_yscale("log")
    ax.set_xlim(0, 1); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel(r"$q = |G| / G_{\max}$")
    ax.set_ylabel(ylabel)
    open_frame(ax); grid(ax)
    ax.text(0.125, 0.97, "low G", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=5.6, color=RED,
            fontweight="bold")


# ---- a ---------------------------------------------------------------------------------------
pg.letter("a", 2.0, 119.0 + OFF)
ax = pg.ax(LX, TOP, PW, PH)
spectrum(ax, "median_error_energy_fraction", "p25_error_energy_fraction", "p75_error_energy_fraction",
         "error-energy fraction per radial bin")
ax.set_ylim(5e-6, 0.4)
log_ticks(ax, "y", subs=())
handles = [Line2D([], [], color=TWO[c], lw=1.1, label=c) for c in ("ZFP", "SZ3")]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="lower left",
              title="median; band = pairwise IQR")
# both spectra fall steeply toward q = 1 and start low at q = 0; the lower-left is clear below 1e-3

# ---- b ---------------------------------------------------------------------------------------
pg.letter("b", 94.0, 119.0 + OFF)
ax = pg.ax(RX, TOP, PW, PH)
spectrum(ax, "median_hartree_weighted_fraction", "p25_hartree_weighted_fraction", "p75_hartree_weighted_fraction",
         r"Hartree-weighted ($|G|^{-4}$) fraction per bin")
ax.set_ylim(1e-11, 3)
ax.set_yticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0])
ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
handles = [Line2D([], [], color=TWO[c], lw=1.1, label=c) for c in ("ZFP", "SZ3")]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper right")

# ---- c: decomposition factors ---------------------------------------------------------------------
pg.letter("c", 2.0, 63.0 + OFF)
ax = pg.ax(LX + 26.0, BOT, PW - 26.0, PH)
rows = (("sqrt_total_safe_error_energy_ratio", "total spectral-energy\nfactor", DARK_B),
        ("sqrt_spectral_hartree_susceptibility_ratio", "spectral Hartree-\nsusceptibility factor", DARK_G),
        ("nyquist_safe_hartree_ratio", "Hartree error ratio\n(Nyquist-safe)", INK))
ax.axvline(1, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=1)
for y, (key, lab, col) in zip((2, 1, 0), rows):
    r = M.loc[key]
    ax.plot([r.ci_low, r.ci_high], [y, y], color=col, lw=0.9, zorder=3)
    ax.scatter([r.material_level_center], [y], s=30, c=col, zorder=4, linewidths=0)
    ax.text(r.material_level_center, y + 0.22, "%.3f" % r.material_level_center, ha="center", va="bottom", fontsize=6.0)
ax.set_xscale("log"); ax.set_xlim(0.05, 1.3)
ax.set_xticks([0.05, 0.1, 0.2, 0.4, 0.8, 1.0]); ax.set_xticklabels(["0.05", "0.1", "0.2", "0.4", "0.8", "1"])
ax.xaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([r[1] for r in rows]); ax.set_ylim(-0.6, 2.8)
ax.set_xlabel("ZFP / SZ3 factor")
open_frame(ax); grid(ax, "x")
ax.text(0.0, 1.02, "material-level centres, 95%% material-bootstrap CI (n = %d materials)" % int(M.loc["nyquist_safe_hartree_ratio"].n_materials),
        transform=ax.transAxes, fontsize=5.4, color=MID, va="bottom")
# bottom-right is empty: the lowest row's point sits near 0.08 on the left
ax.text(0.97, 0.04, "$R_H = (E_{ZFP}/E_{SZ3})^{1/2}\\,(S_{H,ZFP}/S_{H,SZ3})^{1/2}$\nholds pairwise", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=5.4, color=INK, linespacing=1.3)

# ---- d: share histogram ---------------------------------------------------------------------------
pg.letter("d", 94.0, 63.0 + OFF)
ax = pg.ax(RX, BOT, PW, PH)
ax.hist(share.values, bins=np.arange(0, 1.0001, 0.05), color=PALE_B, edgecolor="white", lw=0.4, zorder=2)
ax.axvline(0.5, color=OTHER, lw=0.6, ls=(0, (4, 2)), zorder=3)
ax.axvline(med_share, color=RED, lw=1.0, zorder=4)
ax.set_xlim(0, 1); ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); ax.set_xticklabels(["0", "20", "40", "60", "80", "100%"])
ax.set_xlabel("share of |log codec effect| from spectral susceptibility")
ax.set_ylabel("materials")
open_frame(ax); grid(ax, "y")
note(ax, 0.03, 0.96,
     "median %.1f%%\nZFP lower susceptibility: %.1f%% of materials\nZFP higher centroid: %.1f%%\nZFP lower low-$G$ fraction: %.1f%%"
     % (100 * med_share, 100 * diag["materials_with_spectral_susceptibility_ZFP_lt_SZ3_fraction"],
        100 * diag["materials_with_ZFP_centroid_higher_than_SZ3_fraction"],
        100 * diag["materials_with_ZFP_low_G_fraction_lt_SZ3_fraction"]), size=5.4)

# ---- e: pair 266 in 3D ------------------------------------------------------------------------------------
import json  # noqa: E402
RP = json.load(open(os.path.join(os.path.dirname(HERE), "render3d", "renders", "kcn_render_params.json")))
pair = P.set_index("pair_id").loc[266]
assert pair.material_id == "mp-676693"
rms = RP["hartree_rms_eV"]
ratio = rms["zfp_1e-3"] / rms["sz3_1e-4"]
assert abs(ratio - pair.nyquist_safe_hartree_ratio) < 5e-4, (ratio, pair.nyquist_safe_hartree_ratio)
bench = D.master()
kb = bench[bench.material_id == "mp-676693"]
rz = kb[(kb.codec.str.upper() == "ZFP") & np.isclose(kb.nominal_tolerance_relative, 1e-3)].iloc[0]
rs = kb[(kb.codec.str.upper() == "SZ3") & np.isclose(kb.nominal_tolerance_relative, 1e-4)].iloc[0]
vol = 202.49009370721893                 # KCN cell volume, A^3 (render3d provenance); stored fields are rho x V
pg.letter("e", 2.0, OFF - 0.5)
RY, RH, RW = 10.0, OFF - 17.0, 40.0
slots = ((24.0, "kcn_drho_zfp_1e-3.png", "ZFP", r"$L_\infty$ = %.1f$\times10^{-4}$ e $\AA^{-3}$" % (1e4 * rz.realized_Linf / vol)),
         (67.0, "kcn_drho_sz3_1e-4.png", "SZ3", r"$L_\infty$ = %.1f$\times10^{-4}$ e $\AA^{-3}$" % (1e4 * rs.realized_Linf / vol)),
         (116.0, "kcn_dvh_zfp_1e-3.png", "ZFP", r"rms %.2f meV; max %.2f meV, below the level" % (1e3 * rms["zfp_1e-3"], 1e3 * RP["hartree_max_eV"]["zfp_1e-3"])),
         (159.0, "kcn_dvh_sz3_1e-4.png", "SZ3", r"rms %.2f meV" % (1e3 * rms["sz3_1e-4"])))
for xc, png, codec, line in slots:
    place_render(pg, png, xc - RW / 2, RY, RW, RH, anchor="S")
    pg.fig.text(xc / pg.W, (RY - 1.0) / pg.H, codec, fontsize=6.2, fontweight="bold", color=TWO[codec],
                ha="center", va="top")
    pg.fig.text(xc / pg.W, (RY - 4.0) / pg.H, line, fontsize=5.4, color=INK, ha="center", va="top")
ce = pg.canvas(0, 0, 183.0, OFF)
for (xa, xb, lab) in ((6.0, 88.0, r"decoded error $\Delta\rho$, isosurfaces $\pm$%.1f$\times10^{-4}$ e $\AA^{-3}$ (both codecs)"
                       % (1e4 * RP["drho_iso_e_per_A3"])),
                      (97.0, 179.0, r"Hartree-potential error $\Delta V_H$, isosurfaces $\pm$%.2f meV (both codecs)"
                       % (1e3 * RP["hartree_iso_eV"]))):
    ce.plot([xa, xa, xb, xb], [OFF - 5.2, OFF - 4.2, OFF - 4.2, OFF - 5.2], color=INK, lw=0.5)
    ce.text((xa + xb) / 2, OFF - 3.6, lab, fontsize=5.8, ha="center", va="bottom", fontweight="bold")
ce.text(91.5, RY + RH * 0.55, "ZFP / SZ3\nHartree error\n%.3f" % ratio, fontsize=5.6, ha="center", va="center",
        color=INK, linespacing=1.15)
ce.text(91.5, RY + RH * 0.18, "matched pair 266\n$L_\\infty$ %.2f dex apart" % pair.distance_dex, fontsize=5.2,
        ha="center", va="center", color=MID, linespacing=1.15)
ky = 2.0
for j, (s, cc) in enumerate(ELEM.items()):
    ce.scatter([8.0 + 7.0 * j], [ky], s=9, color=cc, lw=0)
    ce.text(9.4 + 7.0 * j, ky, s, fontsize=5.4, va="center")
for j, (lab, cc) in enumerate(((r"positive", POS_C), (r"negative", NEG_C))):
    x = 36.0 + 16.0 * j
    ce.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle((x, ky - 1.0), 2.4, 2.0, color=cc, lw=0))
    ce.text(x + 3.2, ky, lab, fontsize=5.4, va="center")

layout.audit(pg.fig)
pg.save(HERE, "Fig7")
