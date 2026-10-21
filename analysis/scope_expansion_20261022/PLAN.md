# Scope expansion plan — 2026-10-22

Branch: `research/scope-expansion-20261022` (from `research/qoac-b4-budgeted-relaxation-20261021`).
Status: **living document, revisable at any time by the study owner.** Gates below are reading guides, not
frozen criteria.

## Starting point (rev5, `paper/nc-rev5-deployment-cost-20261012`)

- The paper's thesis: *the downstream operator qualifies (QSQ), predicts and shapes certified compression of
  electronic densities.*
- **Covered QoIs:**
  - Bader charges (valence contract and exact all-electron-partition contract);
  - Hartree potential;
  - slab work function;
  - gain prediction for five diagonal operators;
  - grid extrema and the electron count (SI).
- **Populations:** 254 development densities, P1 (60 bulk), P3b (32 slabs), P2 (48+12 bulk with AECCAR),
  the MP archive frame (415,289 objects; sample of 300), and 63 external systems.
- **Budget:** 4,992 / 5,000 words and 10 / 10 display items. Anything new goes to the SI or replaces content.
- **Already done elsewhere (not repeated):**
  - FFCz Hartree baseline (owner's Vanda work);
  - MGARD / QPET baselines;
  - deployment cost;
  - the Hartree archive estimate;
  - self-contained HB bytes;
  - turbulence WP-J (n19 MET, excluded by author decision).

## Direction

Move from "two QoIs of the charge density" to **a measurement-contract framework that covers the classes of
downstream analysis people actually run on stored densities**. One stream should carry certificates for a
*portfolio* of analyses, and the design pattern should follow from the operator class:

| operator class | example | design pattern | status |
|---|---|---|---|
| linear, diagonal in Fourier space | Hartree, E-field, smoothing | spectral allocation (QOAC-H) | done |
| linear on a partition | Bader integrals (fixed partition) | constraint projection (QOAC-B2) | done |
| partition itself | Henkelman labels | exact topology correction (QOAC-B3) | done |
| partition under a tolerance | Bader charges with tau_B | **budgeted relaxation (QOAC-B4)** | engineering running |
| a second physical field | **spin / magnetization density, per-atom moments** | QSQ + projection on m | **new, WS-S** |
| non-electronic fields | turbulence (JHTDB) | QSQ only | n19 MET, not in paper |

## Workstreams (ranked by payoff × feasibility in this session)

### WS-B4 — budgeted relaxation (running)
- **Engineering:** 12 P2 engineering materials (run 39630018118).
- **Next:** read the results. If the total-bytes ratio is clearly below 1 at delta ≥ 1e-2, try greedy-order and
  eligibility variants on the same 12. Otherwise record a negative result and stop.

### WS-S — spin-density QoIs (new class of downstream analysis)
Spin-polarized MP calculations store a magnetization block (`data.diff`) next to the total density. Nothing in
the program uses it yet, although per-atom magnetic moments (Bader-integrated m) are a routine analysis.

1. **S0 census** (no Bader). Over the MP part of the development panel (186) plus the P1/P2 engineering sets:
   - which objects carry a non-null `diff`;
   - total / absolute magnetization;
   - |m| range relative to the total density;
   - the byte share of the magnetization block.
2. **S1 engineering** (only if S0 finds enough magnetic objects):
   - QSQ floor for Bader moments, with the partition from the total density;
   - certification of per-atom moments under ZFP/SZ3/SPERR on m;
   - a B2-style per-basin projection on m;
   - joint certification with Bader charges from one stored pair (rho, m).

### WS-T — cross-domain generality packaging (no new compute)
- Draft an SI note from the turbulence n19 results that already MET, so the owner can decide whether to bring
  generality back.
- This changes nothing in the manuscript unless the owner says so.

### WS-H — consistency fixes found by the survey
- The Hartree archive result is in the main text but has no SI section and no `SOURCE_FILES.md` row.
- Prepare the patch on a side branch for review. Do not merge.

### Held for the owner
- B3 confirmatory and any other run on the 48 P2 confirmation materials (holdout use is irreversible).
- Any manuscript edit.

## Log (times are SGT, from commit timestamps)
- 2026-10-22 00:05 — plan written; survey of branches after 10-07 completed.
- 00:07 — WS-S0 census triggered. 00:10: results in — 210/210 MP objects carry a magnetization block, and 87
  have an atom with |mu| ≥ 0.1 mu_B.
- 00:11 — WS-T SI-note draft written. The finite-panel bound is already rev5 SI 1.5.
- ~00:12 — WS-H on side branch `paper/nc-rev5-hartree-archive-si-20261022`: SI Note 3.4 plus the
  SOURCE_FILES row. Audit: 0 failures, 0 warnings. Not merged.
- ~00:13 — WS-B4 engineering read: the bound holds on the compiled binary; the byte effect is small. Not
  carried forward.
- 00:19 — **S0b: the archive estimates omit the magnetization block** (300/300; 52% of the text). Read as
  covering the charge-density block only, the ratios are Bader 2.10× and Hartree 171×. See
  `FINDING_magnetization_block.md`.
- 00:23 — WS-S1 results: the moment contract qualifies in 16/16 at 1e-2 mu_B. Certified m costs a median
  0.3% of lossless rho.
- 00:27 — WS-S2 (whole-object archive, with the atom map) triggered as run 39635020731.
- 00:28 — scope v6 storyline draft.
- 00:52 — WS-S3 v1: without a stored map the two contracts compose in all pairs at tau_B = 1e-3 e and in 27/32
  at 1e-2 e; the misses are budget overruns from migration.
- 01:10 — WS-S3 v2: decoded-frame certification composes in 60/62 pairs at no byte cost. The 2 exceptions
  are a real limit (migration > tau_mu).
- 01:20 — WS-S2 measured: whole-object archive ratios are Bader 4.36× and Hartree law 317× (232× with the atom
  map), against 35× for pointwise codecs. The moment contract qualifies in 300/300 archive objects; m costs a
  median 0.05% of lossless rho.
