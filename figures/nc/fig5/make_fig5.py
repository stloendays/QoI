"""NC Figure 5 -- one operator-aware stream certifies the Hartree potential and Bader charges together.

183 x 64 mm; 48 fresh bulk crystals with all-electron references (P2 confirmatory); joint contract = Hartree relative
RMSE < 1e-6 (historical and Nyquist-safe) + Henkelman Bader charge error <= tau_B with zero basin reassignment.
  a  joint CR at tau_B = 1e-4 for each base codec at its best joint post-processor: R3 (operational Hartree optimum),
     J (QOAC-H v0.2 ladder), T1 (spectral truncation ladder), GF (ZFP/SZ3/SPERR ladder).
  b  maximum atomic-charge error of the certified R3 stream per material at each tau_B (red: the tolerance); errors of
     exactly zero are drawn on the floor line.
  c  joint overhead CR_hartree_only / CR_joint for R3 at each tau_B, with the number of certify-then-project decisions
     that projected.
Source: analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/{joint_v2_best_post.csv, joint_v2_material.csv};
anchors asserted against its RESULTS.md (48/48, 1.317x, overhead 1.000, 0/192, 0/192, 31/165).

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig5.py   -> Fig5.{svg,pdf,png}
"""
import os
import sys

import matplotlib.ticker
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common as C  # noqa: E402
import layout  # noqa: E402
from style import BLUE, DARK_G, GREEN, INK, MID, OTHER, RED, Page, grid, log_ticks, note  # noqa: E402

R = os.path.join(C.HB, "P2_CONFIRMATORY_MANIFEST")
B = pd.read_csv(os.path.join(R, "joint_v2_best_post.csv"))
M = pd.read_csv(os.path.join(R, "joint_v2_material.csv"), low_memory=False)
B["tau_bader"] = B.tau_bader.astype(float)
M["tau_bader"] = M.tau_bader.astype(float)
TB = (1e-3, 1e-4, 1e-5)
r3 = B[B.base == "R3"]
assert r3.material_id.nunique() == 48 and r3.best_joint_cr.notna().all()
t4 = r3[np.isclose(r3.tau_bader, 1e-4)].set_index("material_id")
oth = B[B.base.isin(["J", "T1", "GF"]) & np.isclose(B.tau_bader, 1e-4)].groupby("material_id").best_joint_cr.max()
ratio = t4.best_joint_cr / oth.reindex(t4.index)
assert (ratio > 1).sum() == 48 and abs(ratio.median() - 1.3165) < 5e-4, ratio.median()
assert np.allclose(t4.joint_overhead.median(), 1.0)
ctp = M[(M.base == "R3") & M.post.str.startswith("ctp")]
ctp = ctp[ctp.ctp_decision.notna()]  # decisions recorded (as counted in RESULTS.md)
proj = {tb: (int((np.isclose(ctp.tau_bader, tb) & (ctp.ctp_decision == "projected")).sum()),
             int(np.isclose(ctp.tau_bader, tb).sum())) for tb in TB}
assert proj == {1e-3: (0, 192), 1e-4: (0, 192), 1e-5: (31, 165)}, proj
sel = r3.merge(M[M.base == "R3"][["material_id", "tau_bader", "post", "bader_error_e", "reassigned_frac"]],
               left_on=["material_id", "tau_bader", "best_joint_post"], right_on=["material_id", "tau_bader", "post"])
assert len(sel) == 144 and sel.reassigned_frac.max() == 0.0

pg = Page(183.0, 64.0)
rng = np.random.default_rng(11)

# ---- a: joint CR per base -------------------------------------------------------------------------------
pg.letter("a", 2.0, 63.0)
axa = pg.ax(14.0, 10.0, 52.0, 46.0)
BASES = [("R3", "R3\noperational", GREEN), ("J", "J\nv0.2 ladder", BLUE), ("T1", "T1\ntruncation", DARK_G),
         ("GF", "GF\npointwise", OTHER)]
for i, (b, lab, c) in enumerate(BASES):
    v = B[(B.base == b) & np.isclose(B.tau_bader, 1e-4)].best_joint_cr.dropna()
    axa.scatter(i + rng.uniform(-0.16, 0.16, v.size), v, s=5, color=c, edgecolor="white", lw=0.2, zorder=2)
    axa.plot([i - 0.24, i + 0.24], [v.median()] * 2, color=INK, lw=1.0, zorder=3)
    axa.text(i, 2200, "%.0f" % v.median(), fontsize=5.3, ha="center", va="center", color=INK)  # medians in the empty top band
axa.set_yscale("log")
axa.set_ylim(5, 4000)
axa.set_xlim(-0.6, 3.6)
axa.set_xticks(range(4))
axa.set_xticklabels([lab for _, lab, _ in BASES], fontsize=5.3)
axa.set_ylabel("Joint CR ($\\tau_\\mathrm{B}$ = 10$^{-4}$ e)")
log_ticks(axa, axis="y")
grid(axa, axis="y")
note(axa, 0.03, 0.04, "R3 / best other:\n%d/48, %.2f×" % ((ratio > 1).sum(), ratio.median()), va="bottom", size=5.3)  # bottom-left: no base reaches CR < 50 at x <= 1

# ---- b: certified Bader error vs tau_B ------------------------------------------------------------------
pg.letter("b", 70.0, 63.0)
axb = pg.ax(82.0, 10.0, 46.0, 46.0)
FLOOR = 1e-8
for i, tb in enumerate(TB):
    e = sel[np.isclose(sel.tau_bader, tb)].bader_error_e.to_numpy(float)
    e = np.where(e <= 0, FLOOR, e)
    axb.scatter(i + rng.uniform(-0.16, 0.16, e.size), e, s=5, color=GREEN, edgecolor="white", lw=0.2, zorder=2)
    axb.plot([i - 0.3, i + 0.3], [tb, tb], color=RED, lw=1.0, zorder=3)
axb.axhline(FLOOR, color=MID, lw=0.4, ls=(0, (2, 2)), zorder=1)
axb.set_yscale("log")
axb.set_ylim(4e-9, 5e-3)
axb.set_xlim(-0.6, 2.6)
axb.set_xticks(range(3))
axb.set_xticklabels(["10$^{-3}$", "10$^{-4}$", "10$^{-5}$"])
axb.set_xlabel("Bader tolerance $\\tau_\\mathrm{B}$ (e)")
axb.set_ylabel("Max atomic-charge error (e)")
axb.text(2.55, FLOOR * 1.4, "0", fontsize=5.3, color=MID, ha="right", va="bottom")
log_ticks(axb, axis="y")
grid(axb, axis="y")
note(axb, 0.03, 0.96, "reassigned voxels: 0 (144/144)", size=5.3)

# ---- c: joint overhead and projection decisions ---------------------------------------------------------
pg.letter("c", 132.0, 63.0)
axc = pg.ax(144.0, 10.0, 36.0, 46.0)
for i, tb in enumerate(TB):
    v = r3[np.isclose(r3.tau_bader, tb)].joint_overhead.to_numpy(float)
    axc.scatter(i + rng.uniform(-0.16, 0.16, v.size), v, s=5, color=GREEN, edgecolor="white", lw=0.2, zorder=2)
    axc.plot([i - 0.24, i + 0.24], [np.median(v)] * 2, color=INK, lw=1.0, zorder=3)
    p, n = proj[tb]
    axc.text(i, 1.047, "%d/%d" % (p, n), fontsize=5.3, ha="center", va="center", color=MID)
axc.text(1.0, 1.056, "projected", fontsize=5.3, ha="center", va="center", color=MID)
axc.set_ylim(0.995, 1.06)
axc.set_xlim(-0.6, 2.6)
axc.set_xticks(range(3))
axc.set_xticklabels(["10$^{-3}$", "10$^{-4}$", "10$^{-5}$"])
axc.set_xlabel("$\\tau_\\mathrm{B}$ (e)")
axc.set_ylabel("Joint overhead (CR$_\\mathrm{H}$ / CR$_\\mathrm{joint}$)")
axc.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.02))
grid(axc, axis="y")

layout.audit(pg.fig)
pg.save(HERE, "Fig5")
