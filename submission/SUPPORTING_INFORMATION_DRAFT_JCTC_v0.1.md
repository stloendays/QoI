# Supporting Information

## Chemical Fidelity beyond Pointwise Error Bounds: Stability and Bader-Domain Migration in Lossy-Compressed Electron Densities

**JCTC Supporting Information draft v0.1 — 2026-09-06**

This file is the assembly plan and prose scaffold for the separate Supporting Information file required for ACS Fast Format submission. It is not yet the final SI PDF. All numerical claims must remain consistent with the frozen headline-number registry and the JCTC submission manuscript.

---

## S1. Benchmark construction, scope, and reporting semantics

### S1.1 Development benchmark

Describe the 254-material development corpus, bulk/slab composition, density-grid representation, codec/tolerance grid, base ladder, and tight ladder. State explicitly that `benchmark/master_benchmark_full.csv` contains successful rows only and that registered exceptions are retained separately in `failure_registry.csv`.

### S1.2 Success, certification, and non-evaluable semantics

Define:

- successful codec reconstruction;
- pointwise-bound compliance;
- Protocol-A.1 eligibility;
- certified-at-\(\tau\);
- `NON_EVALUABLE_BADER_UNSTABLE`;
- registered downstream solver failure.

Emphasize that non-evaluable systems are neither passes nor codec failures.

### S1.3 No-exclusion sensitivity

Report the no-exclusion sensitivity analysis corresponding to the existing S1 material in `supplement/S1_S3_sensitivity.csv`.

---

## S2. Fixed-basin versus re-derived Bader evaluation

### S2.1 Definitions

Give the equations for fixed-basin and re-derived Bader charge error and explain why the re-derived metric is the primary chemical-fidelity endpoint.

### S2.2 Denominator-robust ratio audit

Report that the directional result—re-derived error exceeds fixed-basin error in 99.7% of successful base-ladder cases—is the primary conclusion. Present denominator-floor sensitivity and material-balanced aggregation showing that the large pooled ratio is not an artifact of vanishing fixed-basin denominators, while also showing that the multiplicative factor varies strongly across codec and tolerance.

**Source outputs:**
- `analysis_output/fixed_basin_ratio_robustness.md`
- `paper_data_v03/HEADLINE_NUMBER_REGISTRY_v03.md`

---

## S3. Certification robustness to alternative reporting choices

### S3.1 No-exclusion analysis

Use the existing sensitivity table to show that the broad codec ordering is not created by the primary exclusion semantics.

### S3.2 Inflation-threshold sensitivity

Report the preregistered/archived inflation thresholds \(k=2,5,10\) and show whether the engineering ordering changes.

**Source:** `supplement/S1_S3_sensitivity.csv`.

---

## S4. Protocol A.1 probe validation and amplitude sensitivity

### S4.1 Why Protocol A was archived

Explain the order-preserving character of float32 round-trip perturbations, exact-tie creation, and the resulting blind spot for an on-grid watershed depending on local ascent relations.

### S4.2 Matched-amplitude probe calibration

Report the 18-material calibration comparing float32 and uniform-noise probes, including tie counts, zero-reassignment counts, and the ratio of stability responses at matched perturbation amplitude.

### S4.3 Amplitude sensitivity

Present the 0.1x / 1x / 10x perturbation-amplitude sensitivity and retain the terminology **Protocol-A.1 numerical stability floor at the stated perturbation amplitude**.

**Sources:**
- `stability/probe_calibration.csv`
- `supplement/S4_amplitude_sensitivity.csv`
- `paper/PROBE_VALIDATION.md`
- `paper/PROTOCOL_A1.md` or corresponding protocol record.

---

## S5. Seed dependence of the stability qualification

Report the five-seed Protocol A.1 distribution, the within-material log10 floor range, the maximum observed seed span, and the number of eligibility decisions that differ from a single-seed implementation. State that the final floor is the conservative maximum across the preregistered seeds.

**Sources:** `stability/` five-seed tables and A.1 summary files.

---

## S6. QoI resolvability across corpus strata

### S6.1 Overall non-evaluable fractions

Report the 319-system non-evaluable fractions at \(10^{-4}\), \(10^{-3}\), and \(10^{-2}\) e.

### S6.2 Development/external strata

Show development bulk, development slab, external bulk, and external vacuum strata without promoting a bulk/slab directional claim that fails external replication.

### S6.3 Metadata-predictability audit

Report development fitting and untouched-external AUROC. Use the narrow conclusion that conventional low-cost descriptors do not generalize adequately to replace direct stability qualification.

---

## S7. Realized-\(L_\infty\) matching robustness

### S7.1 Bound utilization

Show the codec distributions of `realized_Linf_over_nominal`, highlighting the approximately 0.158 ZFP median versus approximately 1.0 for SZ3/SPERR.

### S7.2 Caliper sensitivity

Present matched-realized-\(L_\infty\) results across multiple log-space calipers, with the 0.10-decade analysis as the reviewer-facing conservative setting.

### S7.3 Interpolation sensitivity

Replace nearest-neighbor matching with within-material log-log interpolation on common measured-\(L_\infty\) support and report the persistence of the approximately twofold residual.

**Sources:**
- `analysis_output/complete_case_failure_sensitivity.csv`
- `analysis_output/complete_case_failure_sensitivity.md`
- realized-error matching outputs on the analysis branches.

---

## S8. Failure registry and symmetry-equivalent relabeling

### S8.1 Failure taxonomy

Summarize all 77 registered exceptions, including 76 Bader-solver failures and the symmetry-equivalent relabeling class.

### S8.2 Selective-survival complete-case sensitivity

Delete each entire material if any codec has a registered failure at nominal relative tolerance <=0.01, reducing the development set from 254 to 234 materials, and show that the matched codec-associated residual remains approximately twofold.

### S8.3 Symmetry-aware sensitivity

Describe `aflow-Al8Cu4U1_ICSD_601801`, explain the permutation of symmetry-equivalent Al basins, and report that removing this one known labeling pathology negligibly changes the overall Protocol-A.1 non-evaluable fractions.

---

## S9. Direct mechanism decomposition

### S9.1 Algebraic decomposition

For atom \(a\), define

\[
\Delta Q_a = \Delta Q_{a,\mathrm{integrand}} + \Delta Q_{a,\mathrm{domain}}.
\]

Define the bounded domain share

\[
f_{\mathrm{domain}} = \frac{|\Delta Q_{\mathrm{domain}}|}{|\Delta Q_{\mathrm{domain}}|+|\Delta Q_{\mathrm{integrand}}|}.
\]

### S9.2 Representative 12-material set

Report the current 106 successful material-codec-tolerance cases, machine-precision closure, median bounded domain contribution 0.995, IQR 0.965–0.999, and fraction above 0.90.

### S9.3 Per-atom extension — conditional

If `mechanism/basin_error_decomposition_per_atom.csv` is available before submission, analyze it only under the preregistered case/material aggregation scheme; atoms must not be treated as independent replicates. Include material-level bootstrap and leave-one-material-out sensitivity. If the file is unavailable, omit this subsection from the final SI and retain the representative-set claim.

---

## S10. Full-benchmark mechanism attenuation

Report material-fixed-effect models on Protocol-A.1-eligible complete cases at the \(10^{-3}\) e contract and common measured-\(L_\infty\) support. Show the codec multipliers before and after adding `frac_voxels_reassigned`, and label this as **mechanism-consistent attenuation**, not formal causal mediation.

**Source:** `analysis_output/complete_case_mechanism_attenuation.csv` and associated report.

---

## S11. Global electron-count deviation negative control

Test the alternative explanation that global charge/integral deviation accounts for the codec-associated residual. Report:

- SZ3/ZFP: 2.34x in the base model and 2.58x after adding global electron-count deviation;
- SPERR/ZFP: 2.08x and 2.06x, respectively;
- addition of basin reassignment reduces the multipliers to approximately unity;
- in the joint model, the electron-count term is not significant while reassignment remains strongly associated with Bader error.

**Source:** `paper_data_v03/global_conservation_negative_control.md`.

---

## S12. Certified compression frontier and lossless baselines

Provide complete bulk/slab tables for the Protocol-A.1-qualified best-certified compression ratios and certification coverage at \(10^{-2}\), \(10^{-3}\), and \(10^{-4}\) e. Explicitly identify the strictest slab result as descriptive because only four slab materials are admitted at \(10^{-4}\) e. Include lossless baseline compression ratios.

**Sources:**
- `benchmark/best_certified_a1.csv`
- `benchmark/summary_a1.csv`
- lossless-baseline tables.

---

## S13. Reproducibility, provenance, and versioned protocol record

List:

- codec versions and settings;
- Bader implementation/version and execution settings;
- Protocol A archive and dated Protocol A.1 definition;
- material-source URLs, licenses, and SHA-256 values;
- benchmark and analysis script versions;
- frozen Git commit and archival DOI used for submission;
- software environment sufficient to reproduce the statistical post-processing.

State that the submission archive is the authoritative scientific snapshot and that subsequent development-branch changes do not alter the submitted record.

---

# SI assembly checklist

- [ ] Convert this scaffold into a single review-ready SI document.
- [ ] Insert final Supplementary Figures and Tables in numerical order.
- [ ] Give every SI figure/table a self-contained caption.
- [ ] Ensure all SI numbers match the frozen headline registry or state their denominator/aggregation explicitly.
- [ ] Remove all internal path/status language that is not useful to a reviewer.
- [ ] Omit conditional S9.3 if the per-atom table is not available at submission.
- [ ] Add archival DOI and frozen commit SHA to S13.
