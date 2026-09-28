"""Figure 7 -- frequency allocation of reconstruction error controls Hartree fidelity at matched realized L-inf.

2x2, 183 x 120 mm, from the versioned spectral-mechanism outputs (457 ZFP/SZ3 matched pairs, 214 materials):
  a  radial error-energy spectrum, ZFP vs SZ3, median + pairwise IQR    radial_spectrum_summary.csv
  b  Hartree-weighted (|G|^-4) fraction per radial bin
  c  the three decomposition factors, material-level centres + 95% CI   mechanism_ratio_summary.csv
  d  per-material share of |log effect| from spectral susceptibility    matched_pair_mechanism.csv

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
from style import (BLUE, CODEC, CODEC_DARK, DARK_B, DARK_G, GREEN, INK, MID, OTHER, PALE_B, RED, TINT_R,  # noqa: E402
                   Page, grid, log_ticks, note, open_frame)

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

pg = Page(183.0, 120.0)
LX, RX, PW, PH = 14.0, 106.0, 68.0, 40.0
TOP, BOT = 70.0, 12.0
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
pg.letter("a", 2.0, 119.0)
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
pg.letter("b", 94.0, 119.0)
ax = pg.ax(RX, TOP, PW, PH)
spectrum(ax, "median_hartree_weighted_fraction", "p25_hartree_weighted_fraction", "p75_hartree_weighted_fraction",
         r"Hartree-weighted ($|G|^{-4}$) fraction per bin")
ax.set_ylim(1e-11, 3)
ax.set_yticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0])
ax.yaxis.set_minor_locator(__import__("matplotlib").ticker.NullLocator())
handles = [Line2D([], [], color=TWO[c], lw=1.1, label=c) for c in ("ZFP", "SZ3")]
layout.legend(ax, handles=handles, labels=[h.get_label() for h in handles], loc="upper right")

# ---- c: decomposition factors ---------------------------------------------------------------------
pg.letter("c", 2.0, 63.0)
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
ax.text(0.98, 0.04, r"$R_H = (E_{ZFP}/E_{SZ3})^{1/2}\,(S_{H,ZFP}/S_{H,SZ3})^{1/2}$ holds pairwise", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=5.4, color=INK)

# ---- d: share histogram ---------------------------------------------------------------------------
pg.letter("d", 94.0, 63.0)
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

layout.audit(pg.fig)
pg.save(HERE, "Fig7")
