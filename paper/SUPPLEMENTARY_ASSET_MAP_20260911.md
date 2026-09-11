# Supplementary asset map

Updated 2026-09-11. This file is the canonical bridge between the submission-facing Supplementary Information and the frozen repository assets. It does **not** duplicate or relocate raw data; existing paths and frozen schema names are preserved so analysis scripts remain reproducible.

## Reader-facing naming rule

Use **QoI Stability Qualification (QSQ)** for the operative framework, **QSQ stability floor**, **QSQ eligibility**, **QSQ perturbation probe**, and **archived float32 probe**. Historical identifiers such as `Protocol A`, `Protocol A.1`, `_A1`, and `summary_a1.csv` remain only where they identify frozen files, columns or development provenance.

## Status vocabulary

- **LOCKED** — formal R source and PNG/PDF/SVG publication outputs exist and the interpretation boundary is fixed.
- **SOURCE READY** — formal source exists but the latest publication render still requires final acceptance.
- **READY** — machine-readable source or submission-facing table exists and can be used directly.
- **ARCHIVED** — retained only for provenance; not a current scientific result.
- **DO NOT USE** — withdrawn or superseded evidence.

## SI section → asset registry

| SI item | Scientific role | Canonical source(s) | Publication object | Current state |
|---|---|---|---|---|
| Note 1 | Cohort definitions and denominator conventions | `materials_metadata.csv`; `external_test_MANIFEST.json`; `benchmark/master_benchmark_full.csv`; `validation/EXTERNAL_CONFIRMATORY63_20260908.md` | Table S1 | **READY** |
| Note 2 | QSQ definition and archived float32-probe provenance | `protocol/PROTOCOL_A1.md`; `protocol/PROTOCOL_A_archived.md`; `stability/probe_calibration.csv` | Table S2; Figs. S1–S2 | **READY / LOCKED** |
| Note 3 | QSQ eligibility, floor and sensitivity | `supplement/S1_S3_sensitivity.csv`; `supplement/S2_floor_relative.csv`; `supplement/S4_amplitude_sensitivity.csv`; `stability/stability_floor_A1_per_seed.csv` | Tables S5–S7; Figs. S2, S4 | **READY / LOCKED** |
| Note 4 | Electron-count and Hartree controls | `analysis/electron_count_qoi/`; `analysis/hartree_potential_expansion/` | Tables S8–S9; Fig. S3 | **READY / LOCKED** |
| Note 5 | Binary → three-state reclassification | `analysis/certifiability_reclassification_pooled_20260911.csv`; `analysis/certifiability_reclassification_by_codec_20260911.csv`; `analysis/CERTIFIABILITY_AUDIT_20260911.md` | Table S4; Fig. S7 | **READY / LOCKED** |
| Note 6 | Basin migration and Bader implementation robustness | `mechanism/basin_error_decomposition_per_atom.csv`; `mechanism/basin_error_decomposition_summary.csv`; `mechanism/independent_bader_20260908/` | Tables S10–S11; Fig. S5 | **TABLES READY; FIG. S5 SOURCE READY** |
| Note 7 | Realized-L∞ matching and sensitivity | `analysis/matched_realized_linf_v1/`; `supplement/S12_matching_sensitivity.csv` | Table S12; Fig. S6 | **READY / LOCKED** |
| Note 8 | Development rate–fidelity | `benchmark/summary_a1.csv`; `benchmark/pairwise_a1.csv`; `benchmark/best_certified_a1.csv` | Table S13 | **READY; regenerate at final build** |
| Note 9 | External confirmation | `validation/final_external_confirmatory63_20260908/confirmatory63/`; `validation/final_external_confirmatory63_20260908/all65/`; `validation/EXTERNAL_CONFIRMATORY63_20260908.md` | Table S13; Fig. S8 | **READY / publication outputs present** |
| Note 10 | Failure taxonomy and negative results | `failure_registry.csv`; `paper/CLAIM_EVIDENCE_MATRIX.md`; `supplement/S14_failure_registry_summary.csv` | Table S14 | **READY** |

## Supplementary figure registry

### Supplementary Figure S1 — QSQ stability-floor landscape

- **Role:** archived float32 probe versus operative QSQ; overall and stratum-level non-evaluable landscape.
- **R source:** `figures/R/supplement/figureS1_stability_floor_landscape.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS1_stability_floor_landscape_R.{png,pdf,svg}`.
- **Interpretation:** QSQ defines current eligibility; the archived float32 result is provenance only.
- **Status:** **LOCKED**.

### Supplementary Figure S2 — QSQ probe validation, seed and amplitude sensitivity

- **Role:** validates the non-order-preserving perturbation probe and documents seed/amplitude dependence.
- **R source:** `figures/R/supplement/figureS2_probe_seed_amplitude.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS2_probe_seed_amplitude_R.{png,pdf,svg}`.
- **Interpretation lock:** the 18-material pre-freeze calibration and the 319-system deployment statistics answer different questions and must not be substituted for each other.
- **Status:** **LOCKED**.

### Supplementary Figure S3 — extended operator controls

- **Role:** expands Figure 2 with electron-count, Hartree smoothness, monotonicity and matched-Hartree dispersion controls.
- **R source:** `figures/R/supplement/figureS3_operator_controls.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS3_operator_controls_R.{png,pdf,svg}`.
- **Interpretation:** supporting operator evidence; not the central novelty claim.
- **Status:** **LOCKED**.

### Supplementary Figure S4 — strict certified regime relative to the QSQ stability floor

- **Role:** places certified Bader reconstruction error relative to the independently measured QSQ floor.
- **R source:** `figures/R/supplement/figureS4_tight_floor_scale.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS4_tight_floor_scale_R.{png,pdf,svg}`.
- **Interpretation lock:** at 10^-4 e, certified error is floor-scale (median error/floor 1.09–1.33 across codecs), consistent with an emerging analysis-limited regime. Do not claim universal `plateau = floor`.
- **Status:** **LOCKED**.

### Supplementary Figure S5 — independent Bader implementation robustness

- **Role:** extended domain-migration decomposition and cross-implementation robustness.
- **R source:** `figures/R/supplement/figureS5_bader_implementation_robustness.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS5_bader_implementation_robustness_R.{png,pdf,svg}` once the current render is accepted.
- **Interpretation:** mechanism/implementation robustness only; it does not redefine QSQ.
- **Status:** **SOURCE READY**. A render-script lookup bug discovered during the naming refresh was corrected; publication render is being revalidated.

### Supplementary Figure S6 — realized-L∞ matching sensitivity

- **Role:** common support, match quality and effect stability across 0.05–0.30 dex.
- **R source:** `figures/R/supplement/figureS6_matching_sensitivity.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS6_matching_sensitivity_R.{png,pdf,svg}`.
- **Status:** **LOCKED**.

### Supplementary Figure S7 — codec-resolved stability-qualified reclassification

- **Role:** shows that Figure 3 reclassification is not driven by one codec and that QSQ invalidates unsupported successes as well as failures.
- **R source:** `figures/R/supplement/figureS7_reclassification_by_codec.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS7_reclassification_by_codec_R.{png,pdf,svg}`.
- **Status:** **LOCKED**.

### Supplementary Figure S8 — untouched external confirmation details

- **Role:** QSQ eligibility, certified rate–fidelity and pairwise codec behavior in the frozen 63-system confirmatory cohort.
- **R source:** `figures/R/supplement/figureS8_external_confirmation.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS8_external_confirmation_R.{png,pdf,svg}`.
- **Interpretation:** the 63-system confirmatory cohort is distinct from the 65-system descriptive/stability universe.
- **Status:** publication outputs present; include in the final visual acceptance pass.

Canonical supplementary captions are maintained in `paper/SUPPLEMENTARY_FIGURE_CAPTIONS_20260911.md`.

## Denominator registry

| Universe | n | Use |
|---|---:|---|
| Development bulk | 186 | Development benchmark and QSQ |
| Development slab | 68 | Development benchmark and QSQ |
| Development total | **254** | 6,343-row codec benchmark and Figure 3/S7 reclassification |
| External bulk stability records | 37 | QSQ external stability/descriptive analysis |
| External vacuum-containing 2D stability records | 28 | QSQ external stability/descriptive analysis |
| External descriptive total | **65** | Frozen external manifest / descriptive aggregate |
| Stability total | **319** | 254 development + 65 external stability records |
| Primary external confirmatory cohort | **63** | Pre-frozen rate–fidelity confirmation; 1,689 retained rows |

The **65-system descriptive/stability external set and the 63-system primary confirmatory set are distinct analysis universes** and must never be silently substituted for one another.

## Supplementary table registry

- **Tables S1–S4:** `paper/SUPPLEMENTARY_TABLES_S1_S4_20260911.md` — cohorts, QSQ definition, eligibility, reclassification.
- **Tables S5–S7:** `paper/SUPPLEMENTARY_TABLES_S5_S7_20260911.md` — no-exclusion/inflated-threshold diagnostics, error relative to QSQ floor, seed/amplitude sensitivity.
- **Tables S8–S9:** `paper/SUPPLEMENTARY_TABLES_S8_S9_20260911.md` — electron-count and Hartree operator controls.
- **Tables S10–S11:** `paper/SUPPLEMENTARY_TABLES_S10_S11_20260911.md` — basin decomposition and independent implementation robustness.
- **Table S12:** `paper/SUPPLEMENTARY_TABLE_S12_20260911.md` — realized-L∞ matching sensitivity.
- **Table S13:** `paper/SUPPLEMENTARY_TABLE_S13_20260911.md` — development/external rate–fidelity. Regenerate from frozen machine-readable sources at final build time rather than copying historical prose.
- **Table S14:** `paper/SUPPLEMENTARY_TABLE_S14_20260911.md` — failure taxonomy, exclusions and negative-result audit.

## Provenance-only / non-publication assets

These remain in the repository but should not be promoted into reader-facing method names or reproduced as primary SI evidence unless required for reviewer response:

- historical protocol files `protocol/PROTOCOL_A1.md` and `protocol/PROTOCOL_A_archived.md` as development provenance;
- interim 62-system external confirmation files;
- archived float32-probe result tables beyond the limited comparison required to justify the QSQ probe;
- exploratory mechanism outputs superseded by formal R figures;
- chronological debug logs and HPC accounting;
- withdrawn fixed-basin codec-ranking claims;
- retracted external-baseline unit conversions listed in `paper/CLAIM_EVIDENCE_MATRIX.md`.

## Current remaining build item

The scientific evidence and submission-facing tables are built. The remaining supplementary production item is to complete the final render/visual acceptance of **Figure S5** and include **Figure S8** in the final visual acceptance pass. This is a publication-build task from existing frozen analyses, not a new core experiment.

## Definition of SI-ready

The supplement is ready for Word/PDF assembly when:

- Tables S1–S14 resolve to deterministic frozen sources;
- Figures S1–S8 have R source plus accepted PNG/PDF/SVG outputs;
- every main-text Supplementary reference resolves to one numbered object;
- all denominators agree with this registry;
- reader-facing text consistently uses **QSQ** and **archived float32 probe** rather than internal version labels;
- non-evaluable, solver-failure and infrastructure-failure categories remain disjoint;
- a final cross-reference audit finds no stale figure/table numbers or terminology.
