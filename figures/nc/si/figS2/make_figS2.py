"""Supplementary Figure 2 -- magnetic-moment contracts and the magnetization writer.

183 x 104 mm, house style (figures/composite/style.py); reads only committed result tables.
  a  share of each archive object's text taken by the magnetization block (S0b, 300 objects)
  b  certified magnetization stream / lossless density vs moment tolerance (S1 engineering, magnetic; S2 archive medians)
  c  moment shift from partition migration alone (S3: Bader-certified density; S4: Hartree-law density)
  d  archive reduction: published (density block only) vs whole served object (S2 / S2b)
  e  per archive object at tau_H = 1e-6: magnetization bytes of the magnetization writer (W2M) against the best
     pointwise codec on the same decoded partition (analysis/archive_w2_20261025/results/objects.csv)
  f  exponent of the basin-indicator spectrum of each decoded partition (shells 2-24); Porod's law gives -4

Redrawn on 2026-10-26 from analysis/scope_expansion_20261022/make_figure_spin.py (a-d, same data) with e and f added.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS2.py   -> FigS2.{svg,pdf,png}, FigS2.tweak_keys.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import common as C  # noqa: E402
import layout  # noqa: E402
from style import DARK_B, DARK_G, INK, MID, OTHER, PALE, PALE_G, RED, Page, grid, log_ticks  # noqa: E402

R = os.path.join(C.ROOT, "analysis", "scope_expansion_20261022", "results")
A = os.path.join(C.ROOT, "analysis", "archive_w2_20261025", "results")
W2M = C.WRITER["W2S"]
pg = Page(183.0, 104.0)
TOP, BOT, H = 60.0, 12.0, 36.0

# ---- a: magnetization share of the archive objects ---------------------------------------------------------------
sb = pd.read_csv(os.path.join(R, "s0b_archive_spin_bytes", "objects_spin_bytes.csv"))
assert len(sb) == 300
pg.letter("a", 2.0, 103.0)
ax = pg.ax(14.0, TOP, 40.0, H)
ax.hist(sb.diff_share_text, bins=np.linspace(0.45, 0.65, 21), color=PALE, edgecolor=DARK_B, linewidth=0.4)
med = float(sb.diff_share_text.median())
ax.axvline(med, color=RED, lw=0.8)
ax.text(med + 0.006, 0.97, "median %.2f" % med, transform=ax.get_xaxis_transform(), fontsize=5.3, color=RED,
        ha="left", va="top")
ax.set_xlabel("Magnetization share of object text")
ax.set_ylabel("Archive objects (n = 300)")
grid(ax, axis="y")

# ---- b: certified magnetization stream against moment tolerance --------------------------------------------------
s1 = pd.read_csv(os.path.join(R, "s1_spin_engineering", "rows.csv"))
s1 = s1[(s1.status == "OK") & (s1.certified == True) & (s1.magnetic == True)]  # noqa: E712
best = s1.sort_values("m_bytes").groupby(["material_id", "tau_muB"]).head(1)
s2 = pd.read_csv(os.path.join(R, "s2_archive_whole_object", "objects_spin_store.csv"))
pg.letter("b", 60.0, 103.0)
ax = pg.ax(72.0, TOP, 40.0, H)
rng = np.random.default_rng(5)
for i, t in enumerate((1e-1, 1e-2, 1e-3)):
    v = best[best.tau_muB == t].m_bytes_over_lossless_rho * 100
    ax.scatter(i + rng.uniform(-0.12, 0.12, len(v)), v, s=7, color=DARK_G, edgecolor="white", lw=0.25, zorder=3,
               label="engineering, magnetic (12)" if i == 0 else None)
    ax.plot([i - 0.25, i + 0.25], [v.median()] * 2, color=INK, lw=1.0, zorder=4)
for i, t in ((1, "0.01"), (2, "0.001")):
    ax.scatter([i + 0.38], [np.median(s2["m_store_%s" % t] / s2.lossless_rho) * 100], marker="D", s=12,
               color=DARK_B, zorder=4, label="archive median (300)" if i == 1 else None)
ax.set_yscale("log")
log_ticks(ax, axis="y")
ax.set_xticks(range(3))
ax.set_xticklabels(["0.1", "0.01", "0.001"])
ax.set_xlim(-0.5, 2.6)
ax.set_xlabel(r"Moment tolerance $\tau_\mu$ ($\mu_\mathrm{B}$)")
ax.set_ylabel(r"Certified $m$ / lossless $\rho$ (%)")
grid(ax, axis="y")
layout.legend(ax, loc="upper left", fontsize=5.3)

# ---- c: moment shift from partition migration alone --------------------------------------------------------------
s3 = pd.read_csv(os.path.join(R, "s3_joint_contracts_v2", "rows.csv"))
s3 = s3[s3.status == "OK"].drop_duplicates(["material_id", "tau_B_e"])
s4 = pd.read_csv(os.path.join(R, "s4_hartree_decoded_frame", "rows.csv"))
s4 = s4[s4.status == "OK"].drop_duplicates(["material_id", "tau_H"])
pg.letter("c", 118.0, 103.0)
ax = pg.ax(130.0, TOP, 48.0, H)
for df, col, key, vals, cols, lab in (
        (s3, "mu_err_m_exact_muB", "tau_B_e", (1e-2, 1e-3), (PALE, DARK_B), r"Bader $\tau_\mathrm{B}$ = 10$^{%d}$ e"),
        (s4, "mu_err_migration_muB", "tau_H", (1e-4, 1e-6), (PALE_G, DARK_G), r"Hartree $\tau_\mathrm{H}$ = 10$^{%d}$")):
    for v, c in zip(vals, cols):
        y = np.sort(np.maximum(df[df[key] == v][col].values, 1e-7))
        ax.step(y, np.arange(1, len(y) + 1) / len(y), where="post", color=c, lw=1.0,
                label=lab % int(round(np.log10(v))))
for t, c in ((1e-2, OTHER), (1e-3, RED)):
    ax.axvline(t, color=c, lw=0.7, ls=(0, (3, 2)))
ax.set_xscale("log")
log_ticks(ax, axis="x")
ax.set_ylim(0, 1.02)
ax.set_xlabel(r"Moment shift from partition migration ($\mu_\mathrm{B}$)")
ax.set_ylabel("Fraction of materials")
grid(ax)
layout.legend(ax, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=5.0, frame=False)
# above the frame: the four curves fill every corner of the plot

# ---- d: archive reduction, density block only vs whole object ----------------------------------------------------
tab = json.load(open(os.path.join(R, "whole_object_estimates", "estimates.json"), encoding="utf-8"))
pick = {"Bader archive R at 0.001 e": "Bader\n10$^{-3}$ e", "Hartree archive R_L (law) at 1e-06": "law\n10$^{-6}$",
        "Hartree archive R_P (pointwise) at 1e-06": "pointwise\n10$^{-6}$"}
rows = [e for e in tab if e["quantity"] in pick]
assert len(rows) == 3
pg.letter("d", 2.0, 50.0)
ax = pg.ax(14.0, BOT, 40.0, H)
x = np.arange(len(rows))
ax.bar(x - 0.2, [e["published"] for e in rows], 0.38, color=OTHER, lw=0, label=r"published ($\rho$ only)")
ax.bar(x + 0.2, [e["whole_object"] for e in rows], 0.38, color=DARK_B, lw=0, label=r"whole object ($\rho$ + $m$)")
for xi, e in zip(x, rows):
    ax.plot([xi + 0.2] * 2, e["whole_object_ci"], color=INK, lw=0.6)
ax.set_yscale("log")
log_ticks(ax, axis="y")
ax.set_ylim(1, 1e4)
ax.set_xticks(x)
ax.set_xticklabels([pick[e["quantity"]] for e in rows])
ax.tick_params(axis="x", length=0)
ax.set_ylabel("Archive reduction")
grid(ax, axis="y")
layout.legend(ax, loc="upper left", fontsize=5.3)

# ---- e: magnetization writer against the pointwise codecs, per archive object ------------------------------------
ob = pd.read_csv(os.path.join(A, "objects.csv"))
SUM = json.load(open(os.path.join(A, "SUMMARY.json"), encoding="utf-8"))
ms = SUM["moment_stream"]["1e-06"]
e = ob.dropna(subset=["V_1e-06_w2m_bytes", "V_1e-06_pw_bytes"])
ratio = e["V_1e-06_pw_bytes"] / e["V_1e-06_w2m_bytes"]
assert len(e) == ms["pw_over_w2m"]["n"] == 300
assert abs(float(np.median(ratio)) - ms["pw_over_w2m"]["median"]) < 1e-9 * float(np.median(ratio))
assert int((ratio > 1).sum()) == ms["pw_over_w2m"]["wins"] == 298
pg.letter("e", 60.0, 50.0)
ax = pg.ax(72.0, BOT, 40.0, H)
lo, hi = 10.0, 3e5
for k, ls, c in ((1, "-", INK), (10, (0, (3, 2)), MID), (100, (0, (1, 1.5)), MID)):
    ax.plot([lo, hi], [lo * k, hi * k], color=c, lw=0.5, ls=ls, zorder=1)
ax.text(hi / 1.3, hi / 1.3 / 1.6, "1×", fontsize=5.3, color=INK, ha="right", va="top")
ax.text(hi / 10 / 1.3, hi / 1.3, "10×", fontsize=5.3, color=INK, ha="right", va="top")
ax.text(hi / 100 / 1.3, hi / 1.3, "100×", fontsize=5.3, color=INK, ha="right", va="top")
ax.scatter(e["V_1e-06_w2m_bytes"], e["V_1e-06_pw_bytes"], s=7, color=W2M, edgecolor="white", lw=0.25, zorder=3)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)
log_ticks(ax)
ax.set_xlabel("Magnetization writer (bytes)")
ax.set_ylabel("Best pointwise codec (bytes)")
ax.text(0.97, 0.04, "median %.1f× smaller\nsmaller in %d/%d" % (ms["pw_over_w2m"]["median"], ms["pw_over_w2m"]["wins"],
                                                             ms["pw_over_w2m"]["n"]),
        transform=ax.transAxes, fontsize=5.3, ha="right", va="bottom", color=INK)
grid(ax)

# ---- f: spectrum of the basin indicators of the decoded partitions -----------------------------------------------
po = ob.porod_exponent.dropna()
assert len(po) == SUM["porod_exponent"]["n"] == 299
assert abs(float(np.median(po)) - SUM["porod_exponent"]["median"]) < 1e-12
pg.letter("f", 118.0, 50.0)
ax = pg.ax(130.0, BOT, 48.0, H)
ax.hist(po, bins=np.arange(-4.6, -1.4, 0.1), color=PALE, edgecolor=DARK_B, linewidth=0.4)
ax.axvline(float(np.median(po)), color=RED, lw=0.8)
ax.axvline(-4.0, color=INK, lw=0.7, ls=(0, (3, 2)))
ax.text(float(np.median(po)) + 0.05, 0.97, ("median %.2f" % float(np.median(po))).replace("-", "−"),
        transform=ax.get_xaxis_transform(), fontsize=5.3, color=RED, ha="left", va="top")
ax.text(-4.06, 0.97, "Porod's\nlaw, $-4$", transform=ax.get_xaxis_transform(), fontsize=5.3, color=INK,
        ha="right", va="top")                   # left of its line, clear of the bars
ax.set_xlim(-4.8, -1.4)
ax.set_xlabel("Exponent of the basin-indicator spectrum")
ax.set_ylabel("Archive objects (n = 299)")
grid(ax, axis="y")

layout.audit(pg.fig)
pg.save(HERE, "FigS2")                          # applies FigS2.tweaks.json (figures/composite/tweak.py)
