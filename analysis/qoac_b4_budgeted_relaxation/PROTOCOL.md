# QOAC-B4: budgeted leaf relaxation of the partition-faithful correction

Date: 2026-10-21
Branch: `research/qoac-b4-budgeted-relaxation-20261021` (from `research/qoac-b3-design-20261006`)
Status: **working draft, revisable.** Synthetic study done; real-material engineering done (run 39630018118, `results/real_engineering/RESULTS.md`): bound validated on the compiled binary, byte effect small (median total ratio ≥ 0.989).
Nothing in this file is frozen. The parameter grid, the reading guides in section 5 and the scope can all be
changed by the study owner before or after the engineering run. A confirmatory protocol, if one is wanted
later, would be written separately.

## 1. Question

QOAC-B3 compresses the partition field (AECCAR0 + AECCAR2) and forbids every basin reassignment, so the
Henkelman on-grid partition is reproduced voxel for voxel. On the 12 P2 engineering materials the side
information of the strict correction (arm A2) was a median 0.057 / 0.33 / 1.63 of the base payload at
relative bounds 1e-3 / 1e-2 / 5e-2 (`analysis/qoac_b3_design/results/real_engineering/RESULTS.md`).

The Bader contract only asks for per-atom charge errors below tau_B. B4 asks how much of B3's side
information is spent on reassignments that the contract would tolerate, and whether those bytes can be
dropped while keeping an **a-priori** per-atom bound below tau_B, with no Bader run needed to know it.

## 2. Construction and guarantee

Notation follows `analysis/qoac_b3_design/DESIGN_STUDY.md` section 2. f is the regular reference field,
s_f its successor map, lab its labels, c_p = CHGCAR_p / npoints the charge in voxel p.

- **Eligible set.** Non-vacuum, non-maximum reference leaves: voxels that are no voxel's s_f.
- **Relaxed set R** (encoder-side only; the decoder never needs it).
- **Constraints on the decoded field g:**
  - (V) and (M) exactly as in B3, on every voxel.
  - (B') for p not in R: s_g(p) != p, lab(s_g(p)) = lab(p), and s_g(p) not in R.
  - (R) for p in R: s_g(p) != p, s_g(p) not in R, s_g(p) not vacuum.
  - Robust margins as in B3 (64 ulp) on every decision.

**Claim.** Under (V), (M), (B'), (R):

1. every voxel outside R keeps its reference basin, because its ascent chain never enters R (B3 Theorem 1
   restricted to such chains);
2. a voxel in R takes the basin of one of its 26 neighbours, since its successor lies outside R;
3. the basin set and maxima are unchanged.

Basin *numbers* may still be permuted, because Henkelman numbers basins in scan order; atom charges do not
depend on the numbering. Hence for every atom a,

    |dq_a| <= B_a = sum_{p in R, atom(p)=a, N(p) touches another atom} |c_p|
                  + sum_{p in R, atom(p)!=a, a in atoms(N(p))}      |c_p|.

R is grown greedily during B3's escalation loop: a violating eligible voxel is first offered to R, cheapest
|c_p| first, and accepted only while every B_a <= theta * tau_B. Otherwise it is escalated as in B3.

**Termination.** When g = f, nobody points into R (leaves), and each p in R steps to s_f(p), which is not a
leaf, not vacuum (R2) and not p. So the loop ends, as in B3.

## 3. Synthetic study (done)

`run_synthetic_study.py`, results in `results/synthetic_study.md`. It uses the B3 field set (20 fields,
5 lattice families, 32×30×34), the log-domain base quantizer, and tau = tau_rel · max|q| (synthetic units).

- **Guarantee.** In all 360 rows, labels change only inside R (after maximum-identity renumbering).
  Actual dq never exceeded the bound. The bound never exceeded theta · tau.
- **Bytes, B4 / B3.** Side information median 0.38–0.97. Total median 0.90–0.998.
  - The largest effect is at delta = 5e-2, tau_rel = 1e-3, theta = 1: side 0.60, total 0.90.
  - On these small grids the base payload dominates, so total gains are small.
- **Reading.** The idea works mechanically. Whether it matters depends on the side/base ratio on real
  materials, which B3 measured to be much larger at 1e-2 and 5e-2 than on the synthetic fields.

## 4. Real-material engineering (prepared)

- **Population.** The 12 P2 engineering materials (`analysis/fresh_population_20261006/P2_ENGINEERING_MANIFEST.csv`),
  the same ones B3 used. The 48 P2 confirmation materials are not touched by this run.
- **Pipeline.** `run_b4_engineering.py` reuses the B3 runner: download, sha256, decode, compiled Henkelman
  1.05 `-b ongrid -vac 0.001 -ref REFCAR`, Gate 0 and arm L. It replaces the correction arms.
- **Arms per material, at delta in {1e-3, 1e-2, 5e-2}:**
  - B3 strict correction on the same base stream (paired baseline);
  - B4 for tau_B in {1e-3, 1e-4} e × theta in {0.5, 0.9}.
- **Per arm.** The decoded field goes through the compiled binary. Rows record:
  - base / side / total bytes and bytes relative to the label map;
  - the a-priori bound and the actual per-atom Bader error from ACF.dat;
  - atom-map changes outside R, basin counts, L∞ / bound, and timings.
- **Cost.** 15 binary runs per material plus the reference, against 9 in B3.
- **Workflow.** `.github/workflows/qoac_b4_engineering.yml`. It is triggered manually, or by pushing
  `analysis/qoac_b4_budgeted_relaxation/RUN_ENGINEERING` to this branch. It runs one matrix job per material
  (≤ 6 h each), then an aggregate job that commits `results/real_engineering/` back to the branch.

## 5. How to read the engineering run (guides, not gates)

These are suggestions for interpreting the output; they can be changed.

- **Construction check.** `bound_violations` and `atom_changes_outside_R` should be 0 in every group. If they
  are not, the construction or the transcription is wrong, and that is the first thing to look at.
- **Byte effect.** Look at `median_total_ratio_B4_over_B3` per (delta, tau, theta). A ratio clearly below
  1 at delta = 1e-2 or 5e-2 would suggest relaxation is worth carrying forward. A ratio near 1 everywhere
  would suggest B3's side information is spent on reassignments that carry real charge, and B4 can be dropped.
- **Against the label map.** `median_total_over_label` puts B4 next to B3's recommendation that a label map
  is about 17× cheaper when only charges are needed. B4 is not expected to beat the label map. The question
  is how much of the gap it closes for users who need the partition field itself.

## 6. Scope and claim boundary (current view)

- B4 is a QOAC-B3 variant. It inherits the partition-field use case: users who keep the field for later
  analyses, such as a different Bader implementation, integrating other fields over basins, or topology.
  It is not a better way to deliver Bader charges alone; the label map remains that.
- The guarantee is about the Henkelman on-grid partition with the B3 regularity conditions. It does not
  transfer automatically to near-grid or weight methods.
- Prior art for budgeted/relaxed segmentation preservation has not been checked yet. The B3 prior-art
  table (MSz family, all unverified there) is the starting point.

## 7. Open knobs

- **theta grid.** 0.5 and 0.9 now. 1.0 is excluded only because certification uses strict `<`.
- **Greedy order.** Smallest |c_p| first. An alternative is to prefer voxels whose escalation would cost
  the most side bits.
- **Eligibility.** Leaves only, which is what makes termination trivial. Admitting voxels with small
  inflow trees would need an inflow-weighted bound.
- **Combination with QSQ.** Voxels already reassigned by the QSQ probes could be admitted to R at no
  budget cost, since the floor already covers them. Not implemented.
