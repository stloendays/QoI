# Protocol A.1 — stability probe amendment — FROZEN

**Frozen: 2026-09-05, after the probe calibration below and before any
eligibility table, benchmark summary or external-validation statistic was
recomputed under it.**

Protocol A (`FROZEN_PROTOCOL.md`, 2026-09-04) is not edited. It stays frozen
and archived in full; its results are retained and labelled
**PROVISIONAL / archived (Protocol A)**. A.1 changes exactly one thing — the
perturbation used to measure the stability floor — and nothing else.

---

## 1. What changes and what does not

| | Protocol A | Protocol A.1 |
|---|---|---|
| probe | float64 → float32 → float64 round trip | additive uniform noise `U(-ε, +ε)` |
| amplitude ε | implicit, ≈ 4e-8 · ptp | **ε = L∞ of that material's float32 round trip** (so the same amplitude as A) |
| seeds | n/a (deterministic) | **five pre-registered seeds {20260905, 1, 2, 3, 4}** |
| floor | one value | **max over the five seeds** |
| thresholds τ | {1e-4, 1e-3, 1e-2} e | unchanged |
| exclusion semantics | `floor ≥ τ` → `NON_EVALUABLE_BADER_UNSTABLE`, neither pass nor fail, exclusion reported | unchanged |
| stratification, reporting rules, sensitivity analyses S1–S3 | as in A §3–§7 | unchanged |
| basins | `baderkit`, `method="ongrid"` | unchanged |

```
floor_i = max_{s in SEEDS} max_a | Q_a( rho_i + U_s(-ε_i, ε_i), basins re-derived )
                                 - Q_a( rho_i, basins from rho_i ) |
ε_i     = max | f32(rho_i) - rho_i |
```

Computed by `scripts/stability_floor_noise.py` →
`results/stability/stability_floor_noise_seeds.csv` (one row per material per
seed); eligibility by `scripts/build_eligibility_a1.py` →
`results/stability/eligibility_by_threshold_a1.csv`.

## 2. Why the probe is replaced

The float32 round trip is **order-preserving**: rounding is monotone, so no two
voxels ever exchange rank. What it does do is quantise the field onto a coarser
value grid and thereby create exact ties between neighbouring voxels. The
on-grid watershed resolves exact ties deterministically, so the probe reports a
stability that no other perturbation of the same — or far smaller — amplitude
reproduces.

Discovered on `mp-1007755` (HfAu, 4 atoms) while extending the benchmark ladder
downward (`scripts/honest_benchmark_tight.py`): Protocol A floor 5.9e-10 e with
zero voxels reassigned, yet

| perturbation | L∞ / ptp | axis-neighbour order flips | voxels reassigned | ΔQ (e) |
|---|---:|---:|---:|---:|
| float32 round trip | 4.2e-8 | 0 | **0** | 5.9e-10 |
| uniform noise, same L∞ | 4.2e-8 | 8 | 364 | 1.6e-3 |
| uniform noise, L∞ / 10 | 4.2e-9 | 2 | 267 | 4.9e-4 |
| uniform noise, L∞ / 100 | 4.2e-10 | 0 | 361 | 1.2e-3 |
| ZFP, relative 1e-7 | 2.3e-8 | 2 | 446 | 4.3e-3 |
| SZ3, relative 1e-7 | 1.0e-7 | 21 | 309 | 3.3e-3 |

A probe that is the single most watershed-friendly perturbation available
measures a lower bound with a systematic blind spot, not the floor.

## 3. Probe calibration (run before freezing; `scripts/probe_calibration.py` → `results/stability/probe_calibration.csv`)

Eighteen materials, stratified by corpus (development bulk, development slab,
external 2D) and by noise floor (low / mid / high, two each). Five seeds at the
pre-registered amplitude; amplitude sweep ×0.1 / ×1 / ×10 on the primary seed.

**Q1 — does noise break the false stability?** Yes. The float32 probe creates a
median of 82 exact neighbour ties per material and reassigns zero voxels in
9/18 materials. The noise probe creates zero exact ties and reassigns zero
voxels in 2/18.

**Q2 — is a single seed enough?** No. Across five seeds the per-material
log10(floor) spans a median 0.47 decades and up to 2.4 decades. The
eligibility verdict changes with the seed in **3/18 materials at τ=1e-4, 2/18
at 1e-3, 1/18 at 1e-2**. Hence the pre-registered five-seed set, with the
floor taken as the **maximum** over seeds: a QoI that moves by ≥ τ under any
one of five generic perturbations of a chemically negligible amplitude is not
certifiable at τ. The maximum is the conservative choice; it errs toward
exclusion, never toward a pass.

**Q3 — is the amplitude load-bearing?** Partly. Over two decades of amplitude
(×0.1 → ×10) the floor moves by a median 0.76 decades (p10 0.00, p90 2.02):
about half the materials sit on a plateau, the other half scale sub-linearly.
The floor is therefore *defined at* the float32 L∞ amplitude and reported as
such; it is not an amplitude-free property. The amplitude sensitivity is
reported as **S4** in the Supplement alongside S1–S3.

## 4. One further failure mode the probe exposed

`aflow-Al8Cu4U1_ICSD_601801`: A.1 floor 2.15 e, 76 k voxels reassigned. The
per-atom charges are a **permutation** — two pairs of symmetry-equivalent Al
atoms exchange basins (0.88 ↔ 3.03 e) while the multiset of charges is
unchanged. The original partition already breaks the crystal symmetry (basin
sizes 14 037 vs 48 811 voxels for equivalent atoms), so the watershed's
assignment of the plateau between them is arbitrary and flips under noise.
Under A.1 this material is `NON_EVALUABLE` at every τ, which is the correct
verdict for a position-indexed QoI; it is flagged as category
`basin_relabelling_symmetry_equivalent` in the failure registry so it is not
mistaken for a 2-electron chemical error.

## 5. What is recomputed under A.1, and what is not

Recomputed (both versions kept; A results marked PROVISIONAL / archived):

- `eligibility_by_threshold.csv` → `eligibility_by_threshold_a1.csv`
- Protocol-A stability-qualified summaries of the honest benchmark
- external-validation stratum comparison (`VALIDATION_REPORT.md` §4)
- claims 6b and 7 in `paper/CLAIM_EVIDENCE_MATRIX.md`

Not affected: the master benchmark table itself (`rate_chemical_master.csv`,
codec rows are probe-independent and the run continues), the mechanism
decomposition, the fixed-basin understatement result, the external baseline
closure.

## 6. Amendments to A.1

None.
