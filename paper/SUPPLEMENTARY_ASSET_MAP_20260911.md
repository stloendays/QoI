# Supplementary asset map

Updated 2026-09-11. This file is the canonical bridge between the submission-facing Supplementary Information and the frozen repository assets. It does **not** duplicate or relocate raw data; existing paths are preserved so analysis scripts remain reproducible.

## Status vocabulary

- **READY** — machine-readable source exists and can be used directly.
- **READY / AGGREGATE** — source exists; final publication table needs a compact aggregation step.
- **PLANNED R** — source data exist, but a formal R figure has not yet been rendered and locked.
- **ARCHIVED** — retained only for provenance; not a current scientific result.
- **DO NOT USE** — withdrawn or superseded evidence.

## SI section → asset registry

| SI item | Scientific role | Canonical source(s) | Publication object | Status |
|---|---|---|---|---|
| Note 1 | Cohort definitions and denominator conventions | `materials_metadata.csv`; `external_test_MANIFEST.json`; `benchmark/master_benchmark_full.csv`; `validation/EXTERNAL_CONFIRMATORY63_20260908.md` | Table S1 | READY |
| Note 2 | Protocol A.1 definition and archived A provenance | `protocol/PROTOCOL_A1.md`; `protocol/PROTOCOL_A_archived.md`; `stability/probe_calibration.csv` | Table S2; Figs. S1–S2 | READY / PLANNED R |
| Note 3 | Eligibility and certification sensitivity | `supplement/S1_S3_sensitivity.csv`; `supplement/S2_floor_relative.csv`; `supplement/S4_amplitude_sensitivity.csv`; `stability/stability_floor_A1_per_seed.csv` | Tables S5–S7; Figs. S2, S4 | READY / PLANNED R |
| Note 4 | Electron-count and Hartree controls | `analysis/electron_count_qoi/`; `analysis/hartree_potential_expansion/` | Tables S8–S9; Fig. S3 | READY / PLANNED R |
| Note 5 | Binary → three-state reclassification | `analysis/certifiability_reclassification_pooled_20260911.csv`; `analysis/certifiability_reclassification_by_codec_20260911.csv`; `analysis/CERTIFIABILITY_AUDIT_20260911.md` | Table S4; Fig. S7 | READY / PLANNED R |
| Note 6 | Basin migration and Bader implementation robustness | `mechanism/basin_error_decomposition_per_atom.csv`; `mechanism/basin_error_decomposition_summary.csv`; `mechanism/independent_bader_20260908/` | Tables S10–S11; Fig. S5 | READY / AGGREGATE / PLANNED R |
| Note 7 | Realized-L∞ matching and sensitivity | `analysis/matched_realized_linf_v1/` | Table S12; Fig. S6 | READY / PLANNED R |
| Note 8 | Development rate–fidelity | `benchmark/summary_a1.csv`; `benchmark/pairwise_a1.csv`; `benchmark/best_certified_a1.csv` | Table S13 | READY; regenerate final |
| Note 9 | External confirmation | `validation/final_external_confirmatory63_20260908/confirmatory63/`; `validation/final_external_confirmatory63_20260908/all65/`; `validation/EXTERNAL_CONFIRMATORY63_20260908.md` | Table S13; Fig. S8 | READY / PLANNED R |
| Note 10 | Failure taxonomy and negative results | `failure_registry.csv`; `paper/CLAIM_EVIDENCE_MATRIX.md` | Table S14 | READY / AGGREGATE |

## Denominator registry

This is a high-risk area for manuscript/SI consistency and is therefore frozen here explicitly.

| Universe | n | Use |
|---|---:|---|
| Development bulk | 186 | Development benchmark and stability qualification |
| Development slab | 68 | Development benchmark and stability qualification |
| Development total | **254** | 6,343-row codec benchmark and Figure 3 reclassification |
| External bulk stability records | 37 | Protocol A.1 external stability/descriptive analysis |
| External vacuum-containing 2D stability records | 28 | Protocol A.1 external stability/descriptive analysis |
| External descriptive total | **65** | Frozen external manifest / descriptive aggregate |
| Stability total | **319** | 254 development + 65 external stability records |
| Primary external confirmatory cohort | **63** | Pre-frozen rate–fidelity confirmation; 1,689 retained rows |

The final SI must state that the **65-system descriptive/stability external set and the 63-system primary confirmatory set are distinct analysis universes**. They must not be silently substituted for one another.

## Supplementary table build plan

### Table S1 — Cohorts and provenance

Columns: analysis universe, domain/stratum, n systems, n reconstruction rows where relevant, source database, use in study, freeze status.

### Table S2 — Protocol A vs A.1

Columns: perturbation, amplitude, seeds, floor definition, thresholds, basin algorithm, exclusion semantics, status. A must be labelled **ARCHIVED / PROVISIONAL**.

### Table S3 — Eligibility by threshold

Direct source: `stability/eligibility_summary_A1.csv`. Include `overall`, `dev_bulk`, `dev_slab`, `ext_bulk`, `ext_vacuum`; report n, eligible, non-evaluable, non-evaluable fraction, floor median/P90/max. Archived A fractions may be shown in a separate final column or footnote only.

### Table S4 — Reclassification by codec

Direct source: `analysis/certifiability_reclassification_by_codec_20260911.csv`. Required columns: threshold, codec, naive pass/fail, qualified pass, eligible fail, non-evaluable, non-evaluable naive pass, reclassified naive fail, reclassification fraction.

### Table S5 — Reporting-rule sensitivity

Direct source: `supplement/S1_S3_sensitivity.csv`. Keep `S1_no_exclusion` and `S3_inflated_threshold` visibly separated; do not present the inflated thresholds as alternative primary results.

### Table S6 — Error / floor

Direct source: `supplement/S2_floor_relative.csv`. Caption must say that the table includes certified points only and does not estimate a material-level plateau.

### Table S7 — Seed and amplitude sensitivity

Combine `stability/stability_floor_A1_per_seed.csv`, `stability/probe_calibration.csv` and `supplement/S4_amplitude_sensitivity.csv`. Report pre-registered seeds and the maximum-over-seeds decision rule.

### Table S8 — Electron-count control

Use `analysis/electron_count_qoi/summary_by_codec.csv` and `summary_by_tolerance.csv`; include the 3,205/1,383 decoupling result prominently.

### Table S9 — Hartree control

Use `analysis/hartree_potential_expansion/group_summary.csv` and `material_smoothness.csv`. A separate footnote should explain the 73 SZ3 reproduction-gate exclusions as platform byte-stream mismatches rather than field-reconstruction mismatches.

### Table S10 — Basin decomposition

Use `mechanism/basin_error_decomposition_summary.csv` for the compact table and retain `..._per_atom.csv` as the machine-readable extended data source.

### Table S11 — Cross-implementation robustness

Aggregate `mechanism/independent_bader_20260908/` into one compact table: solver mode, n outcomes, baseline comparability, median BaderKit/Henkelman response ratio, IQR, codec-order concordance.

### Table S12 — Realized-distortion matching

Use `analysis/matched_realized_linf_v1/REPORT.md`, `matched_effects_summary.csv`, `matched_pairs_primary_0p10dex.csv` and caliper sensitivity files. Report common support, match quality, effect ratios and material-bootstrap CIs.

### Table S13 — Development + external rate–fidelity

Generate from machine-readable sources at final build time. **Do not manually copy older prose values.** Development source: `benchmark/summary_a1.csv`; external source: `validation/final_external_confirmatory63_20260908/confirmatory63/external_codec_summary.csv` and `pairwise_external.csv`.

### Table S14 — Failure and negative-result register

Aggregate `failure_registry.csv` by corpus/stage/category. Add only manuscript-relevant negative algorithm results from `paper/CLAIM_EVIDENCE_MATRIX.md`: boundary-aware allocation, promolecule prior, slab symmetry folding, and closed/pending bulk symmetry track.

## Supplementary figure build plan

### Figure S1 — Stability-floor landscape

R source to create: `figures/R/supplement/figureS1_stability_floor_landscape.R`.

Panels: A vs A.1 floor distribution; threshold eligibility by stratum; optional reference lines at 1e-4/1e-3/1e-2 e. Avoid visually implying the archived Protocol A is a competing valid protocol.

### Figure S2 — Probe robustness

R source to create: `figures/R/supplement/figureS2_probe_seed_amplitude.R`.

Panels: per-seed floor spread; eligibility flips vs single seed; ×0.1/×1/×10 amplitude response. The figure should emphasize why five-seed max is a conservative protocol definition.

### Figure S3 — Linear-control expansion

R source to create: `figures/R/supplement/figureS3_linear_controls.R`.

Panels: electron-count/Bader decoupling; Hartree slope distributions; material-level R²; matched-Hartree Bader dispersion. Slab monotonicity caveat must be visible in the caption.

### Figure S4 — Tight regime and floor scale

R source to create: `figures/R/supplement/figureS4_tight_floor_scale.R`.

Panels: error/floor summary by codec and threshold; selected tight-ladder trajectories. Caption boundary: **floor-scale / emerging analysis-limited**, not `plateau = floor`.

### Figure S5 — Extended Bader mechanism

R source to create: `figures/R/supplement/figureS5_bader_robustness.R`.

Panels: full representative fixed-vs-resolved decomposition; domain-term fraction; BaderKit vs Henkelman cross-implementation comparison; near-grid sensitivity if legible.

### Figure S6 — Matching sensitivity

R source to create: `figures/R/supplement/figureS6_matching_sensitivity.R`.

Panels: common-support counts and Bader-error effect ratios across 0.05/0.10/0.20/0.30 dex. Primary 0.10-dex estimate should be visually distinguished without hiding sensitivity results.

### Figure S7 — Codec-resolved reclassification

R source to create: `figures/R/supplement/figureS7_reclassification_by_codec.R`.

Show how naive pass/fail decomposes within each codec. This should support, not duplicate, the pooled central Figure 3.

### Figure S8 — External confirmation details

R source to create: `figures/R/supplement/figureS8_external_details.R`.

Panels: per-system certified CCR distribution, pairwise codec wins, realized-L∞/nominal ratios, and explicit row-level failure accounting.

## Provenance-only / non-publication assets

These remain in the repository but should not be reproduced as SI figures unless needed for reviewer response:

- interim 62-system external confirmation files;
- archived Protocol A result tables beyond the limited comparison needed to justify A.1;
- exploratory mechanism PNG/PDF files in `mechanism/independent_bader_20260908/`;
- chronological debug logs and HPC accounting;
- withdrawn fixed-basin codec-ranking claims;
- retracted external-baseline unit conversions listed in `paper/CLAIM_EVIDENCE_MATRIX.md`.

## Current blocking items

1. **Formal R renderings S1–S8 do not yet exist.** Data are available; this is a presentation/build task, not a new experiment.
2. **Table S11 and S14 require compact aggregation.** No new scientific computation is required.
3. **Table S13 must be regenerated from final machine-readable sources.** Historical prose contains intermediate rate–fidelity values and should not be treated as canonical.
4. Before submission, explicitly document the membership relationship between the 65-system external descriptive set and the 63-system confirmatory set in Table S1 or its footnote.

## Definition of SI-ready

The supplement is ready for Word/PDF assembly only when:

- all S1–S14 tables have a deterministic build path;
- all S1–S8 figures have R source plus PNG/PDF/SVG outputs;
- every main-text Supplementary reference resolves to one numbered object;
- all denominators agree with this registry;
- Protocol A is clearly archived;
- failure categories remain disjoint;
- a final cross-reference audit finds no stale figure/table numbers.
