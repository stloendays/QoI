"""Supplementary Fig. 1 -- Bader storage contracts on real materials (12 fresh P2 engineering materials).

183 x 62 mm:
  a  total stored bytes of each partition-faithful AECCAR arm (A1, A2 at relative bounds 1e-3, 1e-2, 5e-2) divided by
     the bytes of the lossless atom label map, per material; bar, median (16.3-56.9).
  b  size of the lossless label maps per material: atom map and volnum map (medians 12.9 kB and 21.8 kB).
Every row has status OK, zero reassigned voxels and zero Bader error (asserted).
Source: analysis/qoac_b3_design/results/real_engineering/rows.csv.

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS1.py   -> FigS1.{svg,pdf,png}
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "figures", "composite"))
import layout  # noqa: E402
from style import BLUE, DARK_B, DARK_G, GREEN, INK, MID, Page, grid, log_ticks  # noqa: E402

R = pd.read_csv(os.path.join(ROOT, "analysis", "qoac_b3_design", "results", "real_engineering", "rows.csv"))
assert (R.status == "OK").all() and R.reassigned_volnum_frac.max() == 0.0 and R.bader_charge_err_max_e.max() == 0.0
assert R.material_id.nunique() == 12 and len(R) == 72
R["ratio"] = R.total_bytes / R.label_ctx_bytes_atom
WANT = {("A2", 1e-3): 17.3, ("A2", 1e-2): 16.3, ("A2", 5e-2): 27.1, ("A1", 1e-3): 21.1, ("A1", 1e-2): 29.5,
        ("A1", 5e-2): 56.9}
pg = Page(183.0, 62.0)
rng = np.random.default_rng(3)

pg.letter("a", 2.0, 61.0)
axa = pg.ax(16.0, 12.0, 104.0, 44.0)
x = 0
ticks, labs = [], []
for arm, col in (("A2", DARK_B), ("A1", BLUE)):
    for d in (1e-3, 1e-2, 5e-2):
        v = R[(R.arm == arm) & np.isclose(R.delta, d)].ratio
        m = float(np.median(v))
        assert abs(m - WANT[(arm, d)]) < 0.051, (arm, d, m)
        axa.scatter(x + rng.uniform(-0.14, 0.14, v.size), v, s=7, color=col, edgecolor="white", lw=0.25, zorder=3)
        axa.plot([x - 0.25, x + 0.25], [m, m], color=INK, lw=1.0, zorder=4)
        axa.text(x, 230, "%.1f" % m, fontsize=5.3, ha="center", va="center")
        ticks.append(x)
        labs.append("%s\n%s" % (arm, {1e-3: "10$^{-3}$", 1e-2: "10$^{-2}$", 5e-2: "5×10$^{-2}$"}[d]))
        x += 1
    x += 0.5
axa.set_yscale("log")
axa.set_ylim(4, 400)
axa.set_xlim(-0.6, x - 0.9)
axa.set_xticks(ticks)
axa.set_xticklabels(labs, fontsize=5.3)
axa.tick_params(axis="x", length=0, pad=2.5)
log_ticks(axa, axis="y")
grid(axa, axis="y")
axa.set_ylabel("Partition-faithful AECCAR bytes\n/ lossless label-map bytes")
axa.text(0.01, 0.04, "every stream: zero voxels reassigned, zero Bader error (72/72)", transform=axa.transAxes,
         fontsize=5.3, ha="left", va="bottom", color=MID)

pg.letter("b", 128.0, 61.0)
axb = pg.ax(142.0, 12.0, 38.0, 44.0)
u = R.drop_duplicates("material_id")
for i, (c, lab, col) in enumerate((("label_ctx_bytes_atom", "atom\nmap", DARK_G), ("label_ctx_bytes_volnum", "volnum\nmap", GREEN))):
    v = u[c] / 1e3
    axb.scatter(np.full(v.size, float(i)), v, s=7, color=col, edgecolor="white", lw=0.25, zorder=3)
    axb.plot([i - 0.22, i + 0.22], [v.median()] * 2, color=INK, lw=1.0, zorder=4)
    axb.text(i, 330, "%.1f kB" % v.median(), fontsize=5.3, ha="center", va="center")
for _, r in u.iterrows():
    axb.plot([0, 1], [r.label_ctx_bytes_atom / 1e3, r.label_ctx_bytes_volnum / 1e3], color="#D3D6DA", lw=0.4, zorder=1)
axb.set_xlim(-0.5, 1.5)
axb.set_yscale("log")
axb.set_ylim(2, 500)
log_ticks(axb, axis="y")
axb.set_xticks([0, 1])
axb.set_xticklabels(["atom\nmap", "volnum\nmap"], fontsize=5.3)
axb.tick_params(axis="x", length=0, pad=2.5)
grid(axb, axis="y")
axb.set_ylabel("Lossless label map (kB)")

layout.audit(pg.fig)
pg.save(HERE, "FigS1")
