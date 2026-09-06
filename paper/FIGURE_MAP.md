# Figure map

Scientific logic first; no styling work until the evidence behind each panel is
frozen. Every figure names the data file it is generated from. A figure with no
data file is not yet a figure. Updated 2026-09-06: every data-bearing panel now
has its file; statuses are DATA-READY (file frozen, figure not drawn) or
PENDING (file still being produced).

**Working title:** *Chemical Fidelity Is Not a Pointwise Error: Topology-Induced
Failure Modes in Lossy Compression of Electronic Densities*

**Narrative spine.** Scientific compressors promise pointwise error control.
Chemistry cares about derived observables. The obvious way to test observable
preservation is itself wrong: re-partitioning after reconstruction changes the
answer by an order of magnitude, and the dominant error is topological. Worse,
the observable has its own stability floor — and the obvious probe of that
floor is wrong too, in a way that flatters it by four orders of magnitude.
Under a corrected, calibrated, stability-qualified protocol lossy compression
remains worthwhile, at honest and far more modest ratios, and only for the
materials on which the observable is defined at all.

---

## Figure 1 — Problem setup and the two evaluation paths

Schematic. DFT density → lossy compression → reconstruction → chemical
observable; wrong branch (basins from the original field) and correct branch
(basins re-derived from the reconstruction), annotated with
`ΔQ_total = ΔQ_integrand + ΔQ_domain`.

*Data:* none. *Status:* schematic, draw at layout time.

---

## Figure 2 — The fixed-basin metric fails

(a) Paired scatter `dQ_fixed` vs `dQ_resolved`, one point per (material, codec,
rung), faceted bulk / slab, identity line. Inset: understatement factor
`dQ_resolved / max(dQ_fixed, ε)` — full-table median 46x, p90 570x, 96 % of
points > 2x. (b) Ordering: the best codec at matched tolerance is ZFP under
both metrics in 96-98 % of materials; the order of the two worse codecs
differs in 44 % (1e-3) / 16 % (1e-2). Claim 3 as originally stated is
falsified and this panel shows why: the winner is robust, the rest is not.

*Data:* `results/honest_benchmark/rate_chemical_master.csv` (254 materials,
4627 rows). *Status:* DATA-READY.

---

## Figure 3 — Error decomposition: domain migration dominates

Per-atom decomposition at the atom of largest total error, 12 representative
materials chosen by stability floor (most / median / least stable per regime),
three codecs, three tolerances. Domain share ≈ 1.00 in every cell. Companion:
fraction of voxels reassigned vs tolerance.

*Data:* `results/mechanism/basin_error_decomposition.csv` (99 rows).
*Status:* DATA-READY.

---

## Figure 4 — The observable's own stability floor, and the probe that hid it

(a) Distribution of the Protocol A.1 floor (max over five noise seeds), four
strata: dev bulk, dev slab, ext bulk, ext vacuum; log axis; threshold lines at
1e-4 / 1e-3 / 1e-2 e. (b) Non-evaluable fraction per threshold per stratum.
**(c) New panel — probe validation:** the archived float32 floor against the
A.1 floor per material (median ratio 8 700x; 62 % of materials at zero
reassigned voxels under float32 vs 1.9 % under noise), with the mp-1007755
calibration table as an inset: float32 / noise at 1x, 0.1x, 0.01x / ZFP 1e-7 /
SZ3 1e-7 → reassigned voxels and ΔQ.

*Data:* `results/stability/stability_floor_noise_seeds.csv`,
`results/stability/eligibility_summary_a1.csv`,
`results/stability/probe_calibration.csv`, archived
`results/stability/stability_floor.csv`. *Status:* DATA-READY.

---

## Figure 5 — Honest rate–chemical-fidelity frontier

Compression ratio vs `dQ_resolved`, ZFP / SZ3 / SPERR, faceted bulk / slab,
A.1-admitted materials only, admitted-N and non-evaluable-N on each facet,
guides at the three thresholds. The tight rungs (1e-7..3e-6) extend the
frontier leftward and show the error plateau: `dQ_resolved` stops falling
while the ratio keeps dropping.

*Data:* `results/honest_benchmark/rate_chemical_master.csv` +
`results/honest_benchmark/rate_chemical_tight.csv`, filtered by
`results/stability/eligibility_by_threshold_a1.csv`.
*Status:* PENDING (tight rungs on Vanda job 1351857).

---

## Figure 6 — Pointwise error is not chemical error

Points binned by nominal tolerance; `dQ_resolved` spread across codecs within a
bin. Per-material SZ3/ZFP error ratio at matched tolerance: 6.4x (1e-4), 9.2x
(1e-3), 12.4x (1e-2); SZ3 worse on 98-100 %.

*Data:* `results/honest_benchmark/rate_chemical_master.csv`. *Status:* DATA-READY.

---

## Figure 7 — Lossless versus honest lossy

Grouped bars per stratum: f64+zstd, f64+xz, f32+zstd, and best certified lossy
at each threshold under A.1 (median with 95 % paired-bootstrap CI; certified
fraction printed above each bar; non-evaluable N in the facet title). At 1e-2:
bulk SZ3 52x / ZFP 30x / SPERR 12x; slab 70x / 40x / 8x. At 1e-3 the order
flips to ZFP.

*Data:* `results/baseline/lossless.jsonl`,
`results/honest_benchmark/summary_a1.csv`. *Status:* DATA-READY (1e-3 / 1e-4
bars to be refreshed once the tight rungs are merged).

---

## Figure 8 — Generality on untouched data

A.1 floor distributions of the external strata (AFLOW bulk, NOMAD 2D) overlaid
on the development strata; P(vacuum floor > bulk floor) dev 0.564, ext 0.382.
The bulk/slab split does not reproduce under either probe; the frequency and
unpredictability of instability does.

*Data:* `results/stability/stability_floor_noise_seeds.csv`,
`results/validation/VALIDATION_REPORT.md` §6, `data/external_test/MANIFEST.json`.
*Status:* DATA-READY.

---

## Supplementary

| Panel | Content | Data | Status |
|---|---|---|---|
| S1 | No exclusion | `results/supplement/S1_S3_sensitivity.csv` | DATA-READY |
| S2 | dQ / own floor at the best certified rung | `results/supplement/S2_floor_relative.csv` | DATA-READY |
| S3 | Inflated threshold τ_eff = max(τ, k·floor), k ∈ {2,5,10} | `results/supplement/S1_S3_sensitivity.csv` | DATA-READY |
| S4 | Probe amplitude sensitivity (x0.1 / x1 / x10) | `results/supplement/S4_amplitude_sensitivity.csv` | DATA-READY |
| S5 | Seed dependence of the floor; single-seed vs 5-seed verdicts (35 / 17 / 2 of 319) | `results/stability/stability_floor_noise_seeds.csv` | DATA-READY |
| S6 | Negative result: boundary-aware allocation | `results/negative/boundary_allocation/` | DATA-READY |
| S7 | Negative result: promolecule prior | `results/stage0/g0c_promolecule.jsonl` | DATA-READY |
| S8 | Failure taxonomy and registry (77 entries, incl. `basin_relabelling_symmetry_equivalent`) | `results/failures/failure_registry.csv` | DATA-READY |
| S9 | External baselines: BQB unit conversion, den2bin | `results/external_baselines/BASELINE_REPORT.md` | DATA-READY |

Dropped: the symmetry-folding bulk panel (claim 12) — never regenerated under
the corrected metric; not quoted.
