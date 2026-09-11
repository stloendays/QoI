# Supplementary asset map

Updated 2026-09-11. This file is the canonical bridge between the submission-facing Supplementary Information and the frozen repository assets. It does **not** duplicate or relocate raw data; existing paths are preserved so analysis scripts remain reproducible.

## Status vocabulary

- **LOCKED** — formal R source exists; PNG/PDF/SVG passed CI and visual inspection; interpretation/caption boundary fixed.
- **SOURCE READY** — formal R source exists but final CI render/visual lock is not yet complete.
- **READY** — machine-readable source exists and can be used directly.
- **READY / AGGREGATE** — source exists; final publication table needs a compact aggregation step.
- **PLANNED R** — source data exist, but a formal R figure has not yet been created.
- **ARCHIVED** — retained only for provenance; not a current scientific result.
- **DO NOT USE** — withdrawn or superseded evidence.

## SI section -> asset registry

| SI item | Scientific role | Canonical source(s) | Publication object | Status |
|---|---|---|---|---|
| Note 1 | Cohort definitions and denominator conventions | `materials_metadata.csv`; `external_test_MANIFEST.json`; `benchmark/master_benchmark_full.csv`; `validation/EXTERNAL_CONFIRMATORY63_20260908.md` | Table S1 | **READY** |
| Note 2 | Protocol A.1 definition and archived A provenance | `protocol/PROTOCOL_A1.md`; `protocol/PROTOCOL_A_archived.md`; `stability/probe_calibration.csv` | Table S2; Figs. S1-S2 | **TABLE READY; FIGS. S1-S2 LOCKED** |
| Note 3 | Eligibility and certification sensitivity | `supplement/S1_S3_sensitivity.csv`; `supplement/S2_floor_relative.csv`; `supplement/S4_amplitude_sensitivity.csv`; `stability/stability_floor_A1_per_seed.csv` | Tables S5-S7; Figs. S2, S4 | **TABLES S5-S7 READY; FIGS. S2/S4 LOCKED** |
| Note 4 | Electron-count and Hartree controls | `analysis/electron_count_qoi/`; `analysis/hartree_potential_expansion/` | Tables S8-S9; Fig. S3 | **TABLES S8-S9 READY; FIG. S3 LOCKED** |
| Note 5 | Binary -> three-state reclassification | `analysis/certifiability_reclassification_pooled_20260911.csv`; `analysis/certifiability_reclassification_by_codec_20260911.csv`; `analysis/CERTIFIABILITY_AUDIT_20260911.md` | Table S4; Fig. S7 | **TABLE S4 READY; FIG. S7 LOCKED** |
| Note 6 | Basin migration and Bader implementation robustness | `mechanism/basin_error_decomposition_per_atom.csv`; `mechanism/basin_error_decomposition_summary.csv`; `mechanism/independent_bader_20260908/` | Tables S10-S11; Fig. S5 | **READY / AGGREGATE / PLANNED R** |
| Note 7 | Realized-Linf matching and sensitivity | `analysis/matched_realized_linf_v1/` | Table S12; Fig. S6 | **READY / PLANNED R** |
| Note 8 | Development rate-fidelity | `benchmark/summary_a1.csv`; `benchmark/pairwise_a1.csv`; `benchmark/best_certified_a1.csv` | Table S13 | **READY; regenerate final** |
| Note 9 | External confirmation | `validation/final_external_confirmatory63_20260908/confirmatory63/`; `validation/final_external_confirmatory63_20260908/all65/`; `validation/EXTERNAL_CONFIRMATORY63_20260908.md` | Table S13; Fig. S8 | **READY / PLANNED R** |
| Note 10 | Failure taxonomy and negative results | `failure_registry.csv`; `paper/CLAIM_EVIDENCE_MATRIX.md` | Table S14 | **READY / AGGREGATE** |

## Locked supplementary figures

### Supplementary Figure S1 — stability-floor landscape

- **Role:** archived Protocol A versus operative Protocol A.1; overall and stratum-level non-evaluable landscape.
- **R source:** `figures/R/supplement/figureS1_stability_floor_landscape.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS1_stability_floor_landscape_R.{png,pdf,svg}`.
- **Final CI:** GitHub Actions run `34573541361`; artifact `10188756929`.
- **Visual inspection:** PASS. No clipping/collision; auxiliary paired-floor ratio label removed to avoid conflating different calibration/deployment summaries.
- **Repository outputs:** PNG 616,502 B; PDF 23,828 B; SVG 60,288 B.
- **Blob SHAs:** PNG `40bbe2a640c32bb5060503ce3933982cfb1125a8`; PDF `f09e9d58f01443091894f16fe61928855fd4890f`; SVG `0087ab89b34ccfe5f522aefc1ff9dc3148ce7d23`.
- **Status:** **LOCKED 2026-09-11**.

### Supplementary Figure S2 — probe validation, seed and amplitude sensitivity

- **Role:** validates the non-order-preserving A.1 probe and documents seed/amplitude dependence.
- **R source:** `figures/R/supplement/figureS2_probe_seed_amplitude.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS2_probe_seed_amplitude_R.{png,pdf,svg}`.
- **Final CI:** GitHub Actions run `34573541361`; artifact `10188756929`.
- **Visual inspection:** PASS. Calibration and full-corpus statistics are explicitly separated; external vacuum-2D calibration cases are labelled; axes/legends are legible.
- **Repository outputs:** PNG 668,503 B; PDF 16,864 B; SVG 53,945 B.
- **Blob SHAs:** PNG `7709324fda0d08ec63afd3dc15e6adbc533b86e5`; PDF `131e3f460ce7cd7bbab1b285392f00001cc2fc45`; SVG `b415caee6d70b04aedef0c85787a9313c08497a3`.
- **Interpretation lock:** 18-material pre-freeze calibration has five-seed span median ~0.47 decades, max ~2.4; the already-frozen five-seed rule deployed on all 319 systems gives median ~0.37, max ~3.82, with primary-seed-vs-max eligibility flips 35/17/2 at 1e-4/1e-3/1e-2 e. These populations must not be substituted for each other.
- **Status:** **LOCKED 2026-09-11**.

### Supplementary Figure S3 — extended operator controls

- **Role:** expands Figure 2 with the full electron-count negative control, material-level Hartree/Bader smoothness comparison, bulk/slab monotonicity nuance and matched-Hartree Bader dispersion.
- **R source:** `figures/R/supplement/figureS3_operator_controls.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS3_operator_controls_R.{png,pdf,svg}`.
- **Final CI:** GitHub Actions run `34574517842`; artifact `10189104659`; source commit `4b98758b997ae03c57e62441e3a9500dfaf82e26`.
- **Visual inspection:** PASS. Four panels are legible with no clipping/collision; the slab monotonicity caveat remains visible rather than being averaged away.
- **Repository outputs:** PNG 683,983 B; PDF 58,131 B; SVG 235,326 B.
- **Blob SHAs:** PNG `c38446463ab62064029d6088fa904ec424f7dbbf`; PDF `780b4ab3b15e6a18bdca9039b2081b7c666c1575`; SVG `95a108e8e70fb6d657b51f9be8a68c7810efd4b7`.
- **Interpretation lock:** operator-control evidence only; it motivates explicit downstream evaluation but does not replace the Figure 3 benchmark-validity claim.
- **Status:** **LOCKED 2026-09-11**.

### Supplementary Figure S4 — strict certified regime relative to the A.1 floor

- **Role:** tests where certified Bader reconstruction error sits relative to the independently measured Protocol A.1 numerical floor.
- **R source:** `figures/R/supplement/figureS4_tight_floor_scale.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS4_tight_floor_scale_R.{png,pdf,svg}`.
- **Final CI:** GitHub Actions run `34584885979`; artifact `10193221595`; source commit `cafc9767a2060a85a7268fe02907fef5000569b0`.
- **Visual inspection:** PASS after title-layout refinement. No panel-title clipping, axis collision or legend collision remains.
- **Repository outputs:** PNG 550,537 B; PDF 16,413 B; SVG 41,996 B.
- **Blob SHAs:** PNG `f01594994769d21bbf90449c2421c5058cf03859`; PDF `189158ae2b3251a733741674e98e7c5c1b341a80`; SVG `5f6dea59561b860d03d4cafcd137d792ba6ef97a`.
- **Interpretation lock:** at 10^-4 e the certified error is floor-scale (median error/floor 1.09–1.33 across codecs), consistent with an emerging analysis-limited regime. This figure does **not** establish `plateau = floor` as a universal law.
- **Status:** **LOCKED 2026-09-11**.

### Supplementary Figure S7 — codec-resolved reclassification

- **Role:** demonstrates that the pooled binary-to-three-state result is not driven by a single codec and that qualification invalidates apparent successes as well as failures.
- **R source:** `figures/R/supplement/figureS7_reclassification_by_codec.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS7_reclassification_by_codec_R.{png,pdf,svg}`.
- **Final CI:** GitHub Actions run `34573541361`; artifact `10188756929`.
- **Visual inspection:** PASS. Strict-contract pass labels retained; lower-value redundant labels moved to Table S4.
- **Repository outputs:** PNG 570,897 B; PDF 8,190 B; SVG 32,318 B.
- **Blob SHAs:** PNG `3fd7af7a5e57561aab7bbd4f3f81fee58a154ea6`; PDF `40633062ecf17028cc071e29ef4bf0ecf013b95a`; SVG `dd90d474770119f7ba48d50dd43ed28409e38f63`.
- **Status:** **LOCKED 2026-09-11**.

Canonical captions for S1–S4 and S7 are in `paper/SUPPLEMENTARY_FIGURE_CAPTIONS_20260911.md`.

## Denominator registry

This is a high-risk area for manuscript/SI consistency and is therefore frozen here explicitly.

| Universe | n | Use |
|---|---:|---|
| Development bulk | 186 | Development benchmark and stability qualification |
| Development slab | 68 | Development benchmark and stability qualification |
| Development total | **254** | 6,343-row codec benchmark and Figure 3/S7 reclassification |
| External bulk stability records | 37 | Protocol A.1 external stability/descriptive analysis |
| External vacuum-containing 2D stability records | 28 | Protocol A.1 external stability/descriptive analysis |
| External descriptive total | **65** | Frozen external manifest / descriptive aggregate |
| Stability total | **319** | 254 development + 65 external stability records |
| Primary external confirmatory cohort | **63** | Pre-frozen rate-fidelity confirmation; 1,689 retained rows |

The final SI must state that the **65-system descriptive/stability external set and the 63-system primary confirmatory set are distinct analysis universes**. They must not be silently substituted for one another.

## Supplementary table build plan

### Tables S1-S4 — core denominators, protocol and reclassification

Submission-facing first drafts are in `paper/SUPPLEMENTARY_TABLES_S1_S4_20260911.md`. Machine-readable sources remain the source of record.

### Tables S5-S7 — reporting sensitivity and Protocol A.1 robustness

Submission-facing first drafts are in `paper/SUPPLEMENTARY_TABLES_S5_S7_20260911.md`.

- **S5:** `supplement/S1_S3_sensitivity.csv`; separate no-exclusion and inflated-threshold diagnostics from the primary contracts.
- **S6:** `supplement/S2_floor_relative.csv`; certified points only; does not estimate a material-level plateau.
- **S7:** `stability/probe_calibration.csv`, `stability/stability_floor_A1_per_seed.csv`, `supplement/S4_amplitude_sensitivity.csv`; calibration and full-corpus deployment statistics remain separately labelled.

### Tables S8–S9 — operator controls — **BUILT**

Submission-facing tables are generated deterministically in `paper/SUPPLEMENTARY_TABLES_S8_S9_20260911.md` by `scripts/build_supplement_tables_s8_s9_20260911.py` (CI run `34584427019`). Table S8 contains the pooled and codec-resolved electron-count/Bader decoupling matrix, including 1,383/3,205 = 43.15%. Table S9 contains the 6,270-row Hartree scaling summary, the 678-pair material-level smoothness audit, local elasticity ranges, the 22,296× Bader jump and the matched-Hartree 55.4% dispersion result. The reproduction-gate exclusion remains an infrastructure/platform caveat rather than a codec-fidelity failure.

### Table S10 — basin decomposition

Use `mechanism/basin_error_decomposition_summary.csv` for the compact table and retain `..._per_atom.csv` as the machine-readable extended data source.

### Table S11 — cross-implementation robustness

Aggregate `mechanism/independent_bader_20260908/` into one compact table: solver mode, n outcomes, baseline comparability, median BaderKit/Henkelman response ratio, IQR, codec-order concordance.

### Table S12 — realized-distortion matching

Use `analysis/matched_realized_linf_v1/REPORT.md`, `matched_effects_summary.csv`, `matched_pairs_primary_0p10dex.csv` and caliper sensitivity files. Report common support, match quality, effect ratios and material-bootstrap CIs.

### Table S13 — development + external rate-fidelity

Generate from machine-readable sources at final build time. **Do not manually copy older prose values.** Development source: `benchmark/summary_a1.csv`; external source: `validation/final_external_confirmatory63_20260908/confirmatory63/external_codec_summary.csv` and `pairwise_external.csv`.

### Table S14 — failure and negative-result register

Aggregate `failure_registry.csv` by corpus/stage/category. Add only manuscript-relevant negative algorithm results from `paper/CLAIM_EVIDENCE_MATRIX.md`: boundary-aware allocation, promolecule prior, slab symmetry folding, and closed/pending bulk symmetry track.

## Supplementary figure build plan

### Figure S1 — stability-floor landscape — **LOCKED**

See locked-figure registry above.

### Figure S2 — probe robustness — **LOCKED**

See locked-figure registry above.

### Figure S3 — extended operator controls — **LOCKED**

See locked-figure registry above.

### Figure S4 — tight regime and floor scale — **LOCKED**

See locked-figure registry above.

### Figure S5 — extended Bader mechanism — **PLANNED R**

Planned R source: `figures/R/supplement/figureS5_bader_robustness.R`.

Panels: full representative fixed-vs-resolved decomposition; domain-term fraction; BaderKit vs Henkelman cross-implementation comparison; near-grid sensitivity if legible.

### Figure S6 — matching sensitivity — **PLANNED R**

Planned R source: `figures/R/supplement/figureS6_matching_sensitivity.R`.

Panels: common-support counts and Bader-error effect ratios across 0.05/0.10/0.20/0.30 dex. Primary 0.10-dex estimate should be visually distinguished without hiding sensitivity results.

### Figure S7 — codec-resolved reclassification — **LOCKED**

See locked-figure registry above.

### Figure S8 — external confirmation details — **PLANNED R**

Planned R source: `figures/R/supplement/figureS8_external_details.R`.

Panels: per-system certified CCR distribution, pairwise codec wins, realized-Linf/nominal ratios, and explicit row-level failure accounting.

## Provenance-only / non-publication assets

These remain in the repository but should not be reproduced as SI figures unless needed for reviewer response:

- interim 62-system external confirmation files;
- archived Protocol A result tables beyond the limited comparison needed to justify A.1;
- exploratory mechanism PNG/PDF files in `mechanism/independent_bader_20260908/`;
- chronological debug logs and HPC accounting;
- withdrawn fixed-basin codec-ranking claims;
- retracted external-baseline unit conversions listed in `paper/CLAIM_EVIDENCE_MATRIX.md`.

## Current blocking items

1. **Figures S5, S6 and S8 remain to be formally rendered/locked.** These are presentation/build tasks from existing frozen analyses, not new core experiments.
2. **Tables S10-S14 remain to be finalized.** S10-S12/S14 require compact aggregation; Table S13 requires deterministic regeneration from frozen development/external summaries.
3. **Table S13 must be regenerated from final machine-readable sources.** Historical prose contains intermediate rate-fidelity values and should not be treated as canonical.
4. Before submission, explicitly document the membership relationship between the 65-system external descriptive set and the 63-system confirmatory set in Table S1 or its footnote.

## Definition of SI-ready

The supplement is ready for Word/PDF assembly only when:

- all S1-S14 tables have a deterministic build path;
- all S1-S8 figures have R source plus validated PNG/PDF/SVG outputs;
- every main-text Supplementary reference resolves to one numbered object;
- all denominators agree with this registry;
- Protocol A is clearly archived;
- failure categories remain disjoint;
- a final cross-reference audit finds no stale figure/table numbers.
