"""NC Figure 7 -- one operator-aware stream certifies the Hartree potential and Bader charges together.

183 x 100 mm; 48 fresh bulk crystals with all-electron references (P2 confirmatory); joint contract = Hartree relative
RMSE < 1e-6 (historical and Nyquist-safe) + Henkelman Bader charge error <= tau_B with zero basin reassignment.
  a  per material, joint CR of R3 against the best other base (J, T1, GF at their best post-processors) at
     tau_B = 1e-4; colour = which base was the best other.
  b  joint CR at tau_B = 1e-4 for each base codec at its best joint post-processor: R3 (operational Hartree optimum),
     J (frozen-ladder law), T1 (spectral truncation ladder), GF (ZFP/SZ3/SPERR ladder).
  c  maximum atomic-charge error of the certified R3 stream per material at each tau_B (red: the tolerance); errors of
     exactly zero are drawn on the floor line.
  d  joint overhead CR_hartree_only / CR_joint for R3 at each tau_B, with the number of certify-then-project decisions
     that projected.
  e  which post-processor gave each base its best joint stream, per tau_B (48 materials each).
Source: analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/{joint_v2_best_post.csv, joint_v2_material.csv};
anchors asserted against its RESULTS.md (48/48, 1.317x, overhead 1.000, 0/192, 0/192, 31/165, none 48/48/33).

    D:/Tools/pur_bridge_env/Scripts/python.exe make_fig7.py   -> Fig7.{svg,pdf,png}
"""
import os
import sys

import matplotlib.ticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import common as C  # noqa: E402
import layout  # noqa: E402
from style import INK, MID, PALE_B, RED, TINT_G, Page, grid, log_ticks, note  # noqa: E402

R = os.path.join(C.HB, "P2_CONFIRMATORY_MANIFEST")
B = pd.read_csv(os.path.join(R, "joint_v2_best_post.csv"))
M = pd.read_csv(os.path.join(R, "joint_v2_material.csv"), low_memory=False)
B["tau_bader"] = B.tau_bader.astype(float)
M["tau_bader"] = M.tau_bader.astype(float)
TB = (1e-3, 1e-4, 1e-5)
TB_LAB = ["10$^{-3}$", "10$^{-4}$", "10$^{-5}$"]
r3 = B[B.base == "R3"]
assert r3.material_id.nunique() == 48 and r3.best_joint_cr.notna().all()
t4 = r3[np.isclose(r3.tau_bader, 1e-4)].set_index("material_id")
o4 = B[B.base.isin(["J", "T1", "GF"]) & np.isclose(B.tau_bader, 1e-4)]
oth = o4.groupby("material_id").best_joint_cr.max()
oth_base = o4.loc[o4.groupby("material_id").best_joint_cr.idxmax()].set_index("material_id").base
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
none_r3 = [int(((r3.best_joint_post == "none") & np.isclose(r3.tau_bader, tb)).sum()) for tb in TB]
assert none_r3 == [48, 48, 33], none_r3

BASE_C = {"R3": C.ARM["A3"], "J": C.ARM["A1"], "T1": C.ARM["A2"], "GF": C.ARM["A6"]}
BASE_LAB = {"R3": "R3\noperational", "J": "J\nladder law", "T1": "T1\ntruncation", "GF": "GF\npointwise"}
pg = Page(183.0, 100.0)
rng = np.random.default_rng(11)
TOP = 55.0

# ---- a: R3 against the best other base, per material --------------------------------------------------------------
pg.letter("a", 2.0, 99.0)
axa = pg.ax(13.0, TOP, 40.0, 40.0)
lo, hi = 30.0, 3000.0
axa.plot([lo, hi], [lo, hi], color=INK, lw=0.5, zorder=1)
axa.plot([lo, hi], [1.5 * lo, 1.5 * hi], color=MID, lw=0.5, ls=(0, (3, 2)), zorder=1)
axa.text(hi / 1.12, hi / 1.25, "1×", fontsize=5.3, color=MID, ha="right", va="top")
axa.text(hi / 1.5 / 1.12, hi / 1.12, "1.5×", fontsize=5.3, color=MID, ha="right", va="top")
for b in ("J", "T1"):
    ids = oth_base.index[oth_base == b]
    axa.scatter(oth.reindex(ids), t4.best_joint_cr.reindex(ids), s=8, color=BASE_C[b], edgecolor="white", lw=0.25,
                zorder=3)
axa.set_xscale("log")
axa.set_yscale("log")
axa.set_xlim(lo, hi)
axa.set_ylim(lo, hi)
axa.set_aspect("equal")
log_ticks(axa)
grid(axa)
axa.set_xlabel("Best other base, joint CR")
axa.set_ylabel("R3 joint CR ($\\tau_\\mathrm{B}$ = 10$^{-4}$ e)")
note(axa, 0.96, 0.04, "R3 higher in %d/48\nmedian %.3f×" % ((ratio > 1).sum(), ratio.median()), ha="right",
     va="bottom", size=5.3)  # below the diagonal is empty by construction (48/48 above)
axa.legend(handles=[Line2D([], [], ls="", marker="o", ms=3.0, color=BASE_C[b], label="best other: %s (%d)" %
                           (b, int((oth_base == b).sum()))) for b in ("J", "T1")],
           loc="upper left", fontsize=5.0, handletextpad=0.2, borderaxespad=0.3)

# ---- b: joint CR per base -------------------------------------------------------------------------------------------
pg.letter("b", 62.0, 99.0)
axb = pg.ax(73.0, TOP, 58.0, 40.0)
for i, b in enumerate(("R3", "J", "T1", "GF")):
    v = B[(B.base == b) & np.isclose(B.tau_bader, 1e-4)].best_joint_cr.dropna()
    axb.scatter(i + rng.uniform(-0.16, 0.16, v.size), v, s=5, color=BASE_C[b], edgecolor="white", lw=0.2, zorder=2)
    axb.plot([i - 0.24, i + 0.24], [v.median()] * 2, color=INK, lw=1.0, zorder=3)
    axb.text(i, 2500, "%.0f" % v.median() if v.median() > 100 else "%.1f" % v.median(), fontsize=5.3, ha="center",
             va="center", color=INK)  # medians in the empty top band
axb.set_yscale("log")
axb.set_ylim(5, 4500)
axb.set_xlim(-0.6, 3.6)
axb.set_xticks(range(4))
axb.set_xticklabels([BASE_LAB[b] for b in ("R3", "J", "T1", "GF")], fontsize=5.3)
axb.tick_params(axis="x", length=0, pad=2.5)
axb.set_ylabel("Joint CR ($\\tau_\\mathrm{B}$ = 10$^{-4}$ e)")
log_ticks(axb, axis="y")
grid(axb, axis="y")

# ---- c: certified Bader error vs tau_B -------------------------------------------------------------------------------
pg.letter("c", 138.0, 99.0)
axc = pg.ax(150.0, TOP, 30.0, 40.0)
FLOOR = 1e-8
for i, tb in enumerate(TB):
    e = sel[np.isclose(sel.tau_bader, tb)].bader_error_e.to_numpy(float)
    e = np.where(e <= 0, FLOOR, e)
    axc.scatter(i + rng.uniform(-0.16, 0.16, e.size), e, s=4, color=BASE_C["R3"], edgecolor="white", lw=0.2, zorder=2)
    axc.plot([i - 0.32, i + 0.32], [tb, tb], color=RED, lw=1.0, zorder=3)
axc.axhline(FLOOR, color=MID, lw=0.4, ls=(0, (2, 2)), zorder=1)
axc.set_yscale("log")
axc.set_ylim(4e-9, 1e-2)
axc.set_xlim(-0.6, 2.6)
axc.set_xticks(range(3))
axc.set_xticklabels(TB_LAB)
axc.set_xlabel("$\\tau_\\mathrm{B}$ (e)")
axc.set_ylabel("Max atomic-charge error (e)")
axc.text(2.55, FLOOR * 1.4, "0", fontsize=5.3, color=MID, ha="right", va="bottom")
log_ticks(axc, axis="y")
grid(axc, axis="y")
axc.text(0.5, 0.97, "0 voxels reassigned", transform=axc.transAxes, fontsize=5.0, ha="center", va="top")

# ---- d: joint overhead and projection decisions ---------------------------------------------------------------------
pg.letter("d", 2.0, 44.0)
axd = pg.ax(16.0, 10.0, 46.0, 30.0)
for i, tb in enumerate(TB):
    v = r3[np.isclose(r3.tau_bader, tb)].joint_overhead.to_numpy(float)
    axd.scatter(i + rng.uniform(-0.16, 0.16, v.size), v, s=4, color=BASE_C["R3"], edgecolor="white", lw=0.2, zorder=2)
    axd.plot([i - 0.24, i + 0.24], [np.median(v)] * 2, color=INK, lw=1.0, zorder=3)
    p, n = proj[tb]
    axd.text(i, 1.042, "%d/%d" % (p, n), fontsize=5.3, ha="center", va="center", color=INK)
axd.text(1.0, 1.053, "certify-then-project: projected", fontsize=5.0, ha="center", va="center", color=MID)
axd.set_ylim(0.995, 1.06)
axd.set_xlim(-0.6, 2.6)
axd.set_xticks(range(3))
axd.set_xticklabels(TB_LAB)
axd.set_xlabel("Bader tolerance $\\tau_\\mathrm{B}$ (e)")
axd.set_ylabel("Joint overhead\n(CR$_\\mathrm{H}$ / CR$_\\mathrm{joint}$)")
axd.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.02))
grid(axd, axis="y")

# ---- e: best post-processor per base and tau_B ------------------------------------------------------------------------
pg.letter("e", 72.0, 44.0)
axe = pg.ax(93.0, 10.0, 87.0, 30.0)
CAT = (("none", "unprojected stream", TINT_G), ("uniform", "uniform basin projection", "#CFD1D8"),
       ("hap", "Hartree-aware projection", "#6F7380"))


def cat(p):
    return "hap" if p.startswith("hap") else ("uniform" if p.startswith("uniform") else "none")


counts = {b: {"%g" % tb: B[(B.base == b) & np.isclose(B.tau_bader, tb)].best_joint_post.map(cat).value_counts().to_dict()
               for tb in TB} for b in ("R3", "J", "T1", "GF")}
__import__("json").dump({"source": "analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/joint_v2_best_post.csv",
                         "materials": 48, "best_joint_post_counts": counts},
                        open(os.path.join(HERE, "POST_COUNTS.json"), "w"), indent=1)
ylab = []
y = 0
for b in ("R3", "J", "T1", "GF"):
    for tb, tl in zip(TB, ("10$^{-3}$", "10$^{-4}$", "10$^{-5}$")):
        s = B[(B.base == b) & np.isclose(B.tau_bader, tb)].best_joint_post.map(cat).value_counts()
        assert s.sum() == 48
        left = 0
        for k, _, col in CAT:
            n = int(s.get(k, 0))
            axe.barh(y, n, left=left, height=0.78, color=col, edgecolor="white", lw=0.3, zorder=2)
            if n >= 6:
                axe.text(left + n / 2, y, str(n), fontsize=4.8, ha="center", va="center",
                         color="white" if k == "hap" else INK, zorder=3)
            left += n
        ylab.append((y, tl))
        y += 1
    y += 0.6
axe.set_yticks([p for p, _ in ylab])
axe.set_yticklabels([t for _, t in ylab], fontsize=4.8)
axe.tick_params(axis="y", length=0, pad=1.5)
axe.invert_yaxis()
axe.set_xlim(0, 48)
axe.set_xticks([0, 12, 24, 36, 48])
axe.set_xlabel("Materials (of 48) by best joint post-processor")
for j, b in enumerate(("R3", "J", "T1", "GF")):
    axe.text(-5.0, j * 3.6 + 1.0, b, fontsize=5.6, fontweight="bold", ha="right", va="center", color=BASE_C[b],
             clip_on=False)
for sp in ("top", "right", "left"):
    axe.spines[sp].set_visible(False)
axe.legend(handles=[Patch(facecolor=col, edgecolor=MID if k == "none" else col, lw=0.3, label=lab) for k, lab, col in CAT],
           loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=5.0, handlelength=1.0, columnspacing=1.0,
           borderaxespad=0.2)

layout.audit(pg.fig)
pg.save(HERE, "Fig7")
