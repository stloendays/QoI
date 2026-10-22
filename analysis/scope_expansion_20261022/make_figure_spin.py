#!/usr/bin/env python3
"""Draft Supplementary Figure Y: the magnetization block as a second measurement contract.

a  share of each archive object's text taken by the magnetization block (S0b, 300 objects)
b  certified m stream / lossless rho vs moment tolerance (S1 engineering, magnetic; S2 archive medians)
c  moment error from partition migration alone vs tau_mu (S3: Bader-certified rho'; S4: Hartree-law rho')
d  archive reduction: published (rho block only) vs whole served object (S2 / S2b)

Palette and page conventions follow figures/composite/style.py of the manuscript branch (copied constants;
the style module itself is not on this branch). Reads only committed result tables.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
R = HERE / "results"
INK, MID, GRID = "#1B1B1B", "#6B6F76", "#E4E4E4"
GREEN, BLUE, PALE, OTHER, RED = "#89AA7B", "#7789B7", "#9DACCB", "#B3B8C0", "#EB6969"
DARK_G, DARK_B = "#5E7A52", "#5A6480"
plt.rcParams.update({"font.size": 7, "axes.linewidth": 0.6, "xtick.direction": "in", "ytick.direction": "in",
                     "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "axes.labelsize": 7, "legend.frameon": False,
                     "pdf.fonttype": 42, "svg.fonttype": "none", "axes.spines.top": False, "axes.spines.right": False})


def main():
    fig, axs = plt.subplots(1, 4, figsize=(183 / 25.4, 52 / 25.4), constrained_layout=True)

    # a
    sb = pd.read_csv(R / "s0b_archive_spin_bytes/objects_spin_bytes.csv")
    ax = axs[0]
    ax.hist(sb.diff_share_text, bins=np.linspace(0.45, 0.65, 21), color=PALE, edgecolor=DARK_B, linewidth=0.4)
    ax.axvline(sb.diff_share_text.median(), color=RED, lw=0.8)
    ax.set_xlabel("magnetization share of object text")
    ax.set_ylabel("archive objects (n = 300)")
    ax.text(0.98, 0.95, f"median {sb.diff_share_text.median():.2f}", transform=ax.transAxes, ha="right", va="top",
            fontsize=6, color=RED)

    # b
    s1 = pd.read_csv(R / "s1_spin_engineering/rows.csv")
    s1 = s1[(s1.status == "OK") & (s1.certified == True) & (s1.magnetic == True)]  # noqa: E712
    best = s1.sort_values("m_bytes").groupby(["material_id", "tau_muB"]).head(1)
    ax = axs[1]
    taus = [1e-1, 1e-2, 1e-3]
    for i, t in enumerate(taus):
        v = best[best.tau_muB == t].m_bytes_over_lossless_rho * 100
        x = np.full(len(v), i) + np.linspace(-0.12, 0.12, len(v))
        ax.scatter(x, v, s=6, color=GREEN, edgecolor="none", zorder=3, label="engineering (12)" if i == 0 else None)
        ax.hlines(v.median(), i - 0.25, i + 0.25, color=DARK_G, lw=0.9)
    s2 = pd.read_csv(R / "s2_archive_whole_object/objects_spin_store.csv")
    for i, t in [(1, "0.01"), (2, "0.001")]:
        ax.scatter([i + 0.35], [np.median(s2[f"m_store_{t}"] / s2.lossless_rho) * 100], marker="D", s=10,
                   color=DARK_B, zorder=4, label="archive median (300)" if i == 1 else None)
    ax.set_yscale("log")
    ax.set_xticks(range(3), ["0.1", "0.01", "0.001"])
    ax.set_xlabel(r"moment tolerance $\tau_\mu$ ($\mu_B$)")
    ax.set_ylabel("certified m / lossless ρ (%)")
    ax.legend(fontsize=5.5, loc="upper left")

    # c
    ax = axs[2]
    s3 = pd.read_csv(R / "s3_joint_contracts_v2/rows.csv")
    s3 = s3[s3.status == "OK"].drop_duplicates(["material_id", "tau_B_e"])
    s4 = pd.read_csv(R / "s4_hartree_decoded_frame/rows.csv")
    s4 = s4[s4.status == "OK"].drop_duplicates(["material_id", "tau_H"])
    for df, col, key, vals, cols, lab in [
        (s3, "mu_err_m_exact_muB", "tau_B_e", (1e-2, 1e-3), (PALE, DARK_B), r"Bader $\tau_B$ = {} e"),
        (s4, "mu_err_migration_muB", "tau_H", (1e-4, 1e-6), ("#CBD7C3", DARK_G), r"Hartree $\tau_H$ = {}")]:
        for v, c in zip(vals, cols):
            y = np.maximum(df[df[key] == v][col].values, 1e-7)
            ax.scatter(np.sort(y), np.arange(1, len(y) + 1) / len(y), s=5, color=c, label=lab.format(f"{v:g}"))
    for t in (1e-2, 1e-3):
        ax.axvline(t, color=RED if t == 1e-3 else OTHER, lw=0.7, ls="--")
    ax.set_xscale("log")
    ax.set_xlabel(r"moment shift from partition migration ($\mu_B$)")
    ax.set_ylabel("fraction of materials")
    ax.legend(fontsize=5, loc="upper left", handletextpad=0.2)

    # d
    ax = axs[3]
    tab = json.loads((R / "whole_object_estimates/estimates.json").read_text())
    pick = {"Bader archive R at 0.001 e": "Bader\n1e-3 e", "Hartree archive R_L (law) at 1e-06": "law\n1e-6",
            "Hartree archive R_P (pointwise) at 1e-06": "pointwise\n1e-6"}
    rows = [e for e in tab if e["quantity"] in pick]
    x = np.arange(len(rows))
    ax.bar(x - 0.2, [e["published"] for e in rows], 0.38, color=OTHER, label="published (ρ only)")
    ax.bar(x + 0.2, [e["whole_object"] for e in rows], 0.38, color=DARK_B, label="whole object (ρ + m)")
    for xi, e in zip(x, rows):
        lo, hi = e["whole_object_ci"]
        ax.vlines(xi + 0.2, lo, hi, color=INK, lw=0.6)
    ax.set_yscale("log")
    ax.set_xticks(x, [pick[e["quantity"]] for e in rows], fontsize=6)
    ax.set_ylabel("archive reduction factor")
    ax.set_ylim(1, 5e3)
    ax.legend(fontsize=5.5, loc="upper left")

    for a, ch in zip(axs, "abcd"):
        a.text(-0.22, 1.05, ch, transform=a.transAxes, fontsize=9, fontweight="bold", va="bottom")
    out = R / "figures"
    out.mkdir(exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(out / f"supp_fig_spin_channel_draft.{ext}", dpi=400)
    print("written", out)


if __name__ == "__main__":
    main()
