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

## Log
- 2026-10-22 00:20 SGT — plan written; survey of branches after 10-07 completed.
