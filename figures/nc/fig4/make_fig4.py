"""NC Figure 4 -- the operator symbol fixes where the step, the error and the bytes go (KCN, Hartree potential).

183 x 104 mm. One development density (KCN, mp-676693, the material of Figs. 1a and 3e), descriptive only. Data from
compute_kcn_law.py (data/kcn_law.{json,npz}); every stream is decoded and its Hartree relative error recomputed under
both operators (historical and Nyquist-safe), the larger shown.
  a  quantization step Delta_G on the reciprocal plane through G = 0 spanned by b1 and b2, for the closed-form law
     (Delta proportional to |G|^2), uniform steps (operator-blind) and spectral truncation at its best cutoff, each at
     its certified point for tau = 1e-6.
  b  rate-distortion: compression ratio against decoded Hartree relative error; truncation is the lower envelope over
     the 32 cutoffs; open markers, certified point at tau = 1e-4, 1e-6, 1e-8.
  c  rms reference coefficient amplitude per radial bin against the step of each policy (tau = 1e-6): coefficients
     smaller than about half a step are quantized to zero.
  d  Hartree-weighted decoded error per mode, relative to its mean over all modes, per radial bin (tau = 1e-6).
  e  compressed bytes per radial shell (tau = 1e-6).

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig4.py   -> Fig4.{svg,pdf,png}
"""
import json
import os
import sys

import matplotlib.colors as mcolors
import numpy as np
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common as C  # noqa: E402
import layout  # noqa: E402
from style import INK, MID, Page, grid, log_ticks  # noqa: E402

J = json.load(open(os.path.join(HERE, "data", "kcn_law.json")))
Z = np.load(os.path.join(HERE, "data", "kcn_law.npz"))
RAW = J["raw_bytes"]
PTP = J["ptp"]
CERT = J["cert"]
for tau, c in CERT.items():                       # every certified point is below its tolerance
    assert all(v["hartree"] < float(tau) for v in c.values()), tau

COL = {"law": C.ARM["A1"], "uniform": C.ARM["A5"], "trunc": C.ARM["A2"], "zfp": "#7E848C", "sz3": "#9AA0A8",
       "sperr": "#B8BDC4"}
LS = {"law": "-", "uniform": "-", "trunc": "-", "zfp": "-", "sz3": (0, (3, 1.6)), "sperr": (0, (1, 1.2))}
NAME = {"law": "closed-form law", "uniform": "uniform steps", "trunc": "spectral truncation", "zfp": "ZFP",
        "sz3": "SZ3", "sperr": "SPERR"}
pg = Page(183.0, 104.0)

# ---- a: step maps -------------------------------------------------------------------------------------------------
pg.letter("a", 2.0, 103.0)
cmap = mcolors.LinearSegmentedColormap.from_list("steps", ["#F2F4EE", "#C9D6BE", "#89AA7B", "#5E7A52", "#2B3D26"])
gx, gy = Z["map_gx"], Z["map_gy"]
maps = {k: np.log10(Z["map_" + k]) for k in ("law", "uniform", "trunc")}
vmin = min(np.nanmin(m) for m in maps.values())
vmax = max(np.nanmax(m) for m in maps.values())
XL = (gx.min() * 1.03, gx.max() * 1.03)
YL = (gy.min() * 1.03, gy.max() * 1.03)
for j, k in enumerate(("law", "uniform", "trunc")):
    ax = pg.ax(7.0 + j * 32.0, 58.0, 27.0, 39.0)
    ax.set_facecolor("white")
    m = np.ma.masked_invalid(maps[k])
    ax.pcolormesh(gx, gy, m, cmap=cmap, vmin=vmin, vmax=vmax, shading="nearest", rasterized=True)
    if k == "trunc":
        hole = np.where(np.isnan(maps[k]), 1.0, np.nan)
        hole[gx.shape[0] // 2, gx.shape[1] // 2] = np.nan
        ax.pcolormesh(gx, gy, np.ma.masked_invalid(hole), cmap=mcolors.ListedColormap(["#E6E6E6"]),
                      shading="nearest", rasterized=True)
        ax.text(0.97, 0.03, "not stored", transform=ax.transAxes, fontsize=5.0, ha="right", va="bottom", color=MID)
    ax.plot(0, 0, marker="+", ms=3.5, mew=0.6, color=INK)
    ax.set_aspect("equal")
    ax.set_xlim(*XL)
    ax.set_ylim(*YL)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(NAME[k], fontsize=6.3, pad=2.5, color=COL[k] if k != "uniform" else COL[k])
    if j == 0:
        ax.plot([XL[0], XL[0] + 20.0], [YL[0] * 0.97] * 2, color=INK, lw=0.8, clip_on=False)
        ax.text(XL[0] + 10.0, YL[0] * 0.93, "20 Å$^{-1}$", fontsize=5.0, ha="center", va="bottom")
cax = pg.ax(14.0, 53.0, 80.0, 1.6)
sm = __import__("matplotlib.cm", fromlist=["ScalarMappable"]).ScalarMappable(
    norm=mcolors.Normalize(vmin, vmax), cmap=cmap)
cb = pg.fig.colorbar(sm, cax=cax, orientation="horizontal")
cb.outline.set_linewidth(0.4)
cb.ax.tick_params(labelsize=5.3, length=1.5, width=0.4)
ticks = np.arange(np.ceil(vmin), np.floor(vmax) + 1)
cb.set_ticks(ticks)
cb.set_ticklabels(["10$^{%d}$" % t for t in ticks])
cb.set_label("quantization step $\\Delta_G$ / ptp($\\rho$)   ($\\tau$ = 10$^{-6}$; plane $\\mathbf{b}_1$, $\\mathbf{b}_2$ through $G$ = 0)",
             fontsize=5.4, labelpad=1.5)

# ---- b: rate-distortion ---------------------------------------------------------------------------------------------
pg.letter("b", 104.0, 103.0)
axb = pg.ax(118.0, 59.0, 62.0, 41.0)
for tau in (1e-4, 1e-6, 1e-8):                     # the three tolerances fall on the decade ticks
    axb.axvline(tau, color="#D8D8D8", lw=0.6, zorder=0)


def front(pts):
    pts = sorted(pts, key=lambda p: p[1])
    out, best = [], np.inf
    for b, e, *_ in pts:
        if b < best:
            out.append((b, e))
            best = b
    return out


for k in ("sperr", "sz3", "zfp", "trunc", "uniform", "law"):
    pts = front(J["rd"]["trunc_all"]) if k == "trunc" else sorted(J["rd"][k], key=lambda p: p[1])
    b = np.array([p[0] for p in pts], float)
    e = np.array([p[1] for p in pts], float)
    ok = (e > 3e-10) & (e < 2e-2)
    axb.plot(e[ok], RAW / b[ok], color=COL[k], lw=1.2 if k in ("law", "uniform", "trunc") else 0.9, ls=LS[k],
             zorder=3 if k == "law" else 2, label=NAME[k])
    for tau in ("0.0001", "1e-06", "1e-08"):
        c = CERT[tau][k]
        axb.scatter([c["hartree"]], [c["cr"]], s=9, facecolor="white", edgecolor=COL[k], lw=0.7, zorder=4)
axb.set_xscale("log")
axb.set_yscale("log")
axb.set_xlim(3e-10, 1e-2)
axb.set_ylim(2, 3000)
log_ticks(axb)
axb.xaxis.set_major_locator(__import__("matplotlib.ticker", fromlist=["LogLocator"]).LogLocator(base=100))
grid(axb, axis="y")
axb.set_xlabel("Decoded Hartree relative error")
axb.set_ylabel("Compression ratio")
hh, ll = axb.get_legend_handles_labels()
order = [ll.index(NAME[k]) for k in ("law", "uniform", "trunc", "zfp", "sz3", "sperr")]
axb.legend([hh[i] for i in order], [ll[i] for i in order], loc="upper left", fontsize=5.0, ncol=2, handlelength=1.6,
           columnspacing=0.8, borderaxespad=0.3)  # top-left:
# low error and high CR cannot co-occur, so that corner is empty
g = CERT["1e-06"]
axb.text(0.98, 0.04, "at 10$^{-6}$: law %.0f, uniform %.1f, truncation %.0f,\nZFP %.1f, SZ3 %.1f, SPERR %.1f"
         % (g["law"]["cr"], g["uniform"]["cr"], g["trunc"]["cr"], g["zfp"]["cr"], g["sz3"]["cr"], g["sperr"]["cr"]),
         transform=axb.transAxes, fontsize=4.9, ha="right", va="bottom", color=INK)

# ---- c-e: radial diagnostics at tau = 1e-6 ------------------------------------------------------------------------------
edges = Z["bin_edges"]
qc = 0.5 * (edges[1:] + edges[:-1])
modes = Z["modes"]
amp = np.sqrt(Z["ref_power"] / np.maximum(modes, 1)) / PTP
pg.letter("c", 2.0, 47.0)
axc = pg.ax(14.0, 11.0, 44.0, 32.0)
keep = modes > 0
axc.plot(qc[keep], amp[keep], color=INK, lw=1.0, label="reference |c|, rms per mode", zorder=3)
q = np.linspace(0.005, 1.0, 400)
a6 = g["law"]["alpha_rel"]
axc.plot(q, a6 * q ** 2, color=COL["law"], lw=1.2, label="step, law")
axc.plot(q, np.full_like(q, g["uniform"]["alpha_rel"]), color=COL["uniform"], lw=1.2, label="step, uniform")
qq = q[q <= g["trunc"]["q_cut"]]
axc.plot(qq, np.full_like(qq, g["trunc"]["alpha_rel"]), color=COL["trunc"], lw=1.2, ls=(0, (3, 1.5)),
         label="step, truncation")
axc.axvline(g["trunc"]["q_cut"], color=COL["trunc"], lw=0.5, ls=(0, (1, 1.5)))
axc.set_yscale("log")
axc.set_xlim(0, 1)
log_ticks(axc, axis="y")
grid(axc, axis="y")
axc.set_xlabel("$q = |G| / G_\\mathrm{max}$")
axc.set_ylabel("Amplitude / ptp($\\rho$)")
axc.legend(loc="upper right", fontsize=4.8, handlelength=1.5, borderaxespad=0.3, labelspacing=0.25)

pg.letter("d", 64.0, 47.0)
axd = pg.ax(76.0, 11.0, 44.0, 32.0)
for k in ("sperr", "sz3", "zfp", "trunc", "uniform", "law"):
    w = Z["werr_" + k]
    dens = (w / np.maximum(modes, 1)) / (w.sum() / modes.sum())
    ok = keep & (dens > 0)
    axd.step(qc[ok], dens[ok], where="mid", color=COL[k], lw=1.2 if k in ("law", "uniform", "trunc") else 0.8,
             ls=LS[k], zorder=3 if k == "law" else 2)
axd.set_yscale("log")
axd.set_xlim(0, 0.6)
axd.set_ylim(1e-6, 1e5)
log_ticks(axd, axis="y")
grid(axd, axis="y")
axd.set_xlabel("$q = |G| / G_\\mathrm{max}$")
axd.set_ylabel("Hartree error per mode\n(relative to mean)")
axd.text(0.37, 150, "law: equal Hartree\nerror per mode", fontsize=5.0, color=C.ARM["A3"], ha="center", va="bottom")

pg.letter("e", 126.0, 47.0)
axe = pg.ax(138.0, 11.0, 42.0, 32.0)
qs = (np.arange(32) + 0.5) / 32
for k in ("trunc", "uniform", "law"):
    sb = Z["shell_bytes_" + k]
    axe.step(qs, sb / 1e3, where="mid", color=COL[k], lw=1.2, zorder=3 if k == "law" else 2,
             label="%s, %.1f kB" % (NAME[k].replace("spectral ", ""), J["cert"]["1e-06"][k]["bytes"] / 1e3))
axe.set_xlim(0, 1)
axe.set_ylim(0, None)
grid(axe, axis="y")
axe.set_xlabel("$q$ (radial shell)")
axe.set_ylabel("Compressed kB per shell")
axe.legend(loc="upper right", fontsize=4.8, handlelength=1.4, borderaxespad=0.3)

layout.audit(pg.fig)
pg.save(HERE, "Fig4")
