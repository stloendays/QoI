# Supplementary Information

## Stability-qualified benchmarks for scientific compression of electronic densities

This Supplementary Information (SI) is organized to support the main-text benchmark-validity claim without duplicating the primary narrative. The main manuscript establishes the three-state certification logic and its headline consequence. The SI documents denominator conventions, qualification provenance, sensitivity analyses, extended operator controls, mechanistic robustness, matching diagnostics, rate–fidelity tables, external confirmation, and failure semantics.

The SI uses frozen data assets already versioned in the repository. No supplementary result should be transcribed manually when a machine-readable source exists.

---

## Supplementary Note 1 — Cohorts, denominators and data provenance

The development benchmark contains **254 electronic-density fields**, comprising **186 bulk** and **68 slab** systems. Across ZFP, SZ3 and SPERR and the frozen base/tight tolerance ladders, the merged development master table contains **6,343 retained reconstruction rows** (`benchmark/master_benchmark_full.csv`).

The numerical-stability qualification has a broader frozen universe of **319 systems**. This total is composed of 186 development bulk systems, 68 development slabs, 37 external bulk systems and 28 external vacuum-containing 2D systems (`stability/eligibility_summary_A1.csv`). The external stability set therefore contains **65 records** and should not be conflated with the **63-system primary external rate–fidelity confirmatory cohort**. The latter was frozen separately for confirmatory scoring and contains 1,689 retained scientific rows. A final 65-system external descriptive aggregate also exists and contains 1,755 rows (`validation/EXTERNAL_CONFIRMATORY63_20260908.md`).

This distinction is important because different questions use different denominators:

- **254 development systems**: primary codec benchmark, binary-to-three-state reclassification, electron-count control, Hartree control, realized-distortion matching.
- **319 stability-tested systems**: QSQ stability-floor and eligibility summaries.
- **65 external descriptive systems**: descriptive external stability/robustness universe.
- **63 external confirmatory systems**: frozen primary external rate–fidelity confirmation.

The final submission should preserve these labels explicitly. A reader should never be forced to infer why a reported denominator is 254, 319, 65 or 63.

Primary provenance assets are `materials_metadata.csv`, `external_test_MANIFEST.json`, `benchmark/master_benchmark_full.csv`, `validation/final_external_confirmatory63_20260908/`, and the chronological audit in `RESULTS.md`.

---

## Supplementary Note 2 — QoI Stability Qualification and archived probe provenance

The archived float32 qualification probe is retained as a provenance record. It used a deterministic float64 → float32 → float64 round trip to probe numerical Bader stability. During tight-ladder extension, this perturbation was found to be strongly order-preserving and therefore unusually benign for an on-grid watershed partition.

QoI Stability Qualification (QSQ) uses a perturbation-based numerical identifiability test. For material \(m\), let

\[
\epsilon_m = \|\mathrm{float32}(\rho_m)-\rho_m\|_\infty.
\]

Five pre-registered uniform perturbations \(U(-\epsilon_m,+\epsilon_m)\) are applied with seeds \(\{20260905,1,2,3,4\}\). Bader basins are re-derived after each perturbation. The material-specific QSQ stability floor is

\[
f_m=\max_s\max_a |Q_a(\rho_m+\delta_{m,s})-Q_a(\rho_m)|.
\]

A Bader tolerance \(\tau\) is eligible only when \(f_m<\tau\). If \(f_m\ge\tau\), the material–threshold pair is assigned `NON_EVALUABLE_BADER_UNSTABLE` and is neither a codec pass nor a codec failure.

The 18-material calibration run showed why the probe had to change (`stability/probe_calibration.csv`; `protocol/PROTOCOL_A1.md`):

- the archived float32 probe produced a median of **82 exact neighbouring ties** and reassigned zero voxels in **9/18** calibration systems;
- the non-order-preserving QSQ perturbation probe produced no exact ties and reassigned zero voxels in only **2/18** systems;
- across five seeds, the per-material log10 floor span had a median of **0.47 decades** and reached **2.4 decades**;
- a single-seed eligibility verdict changed across seeds in 3/18 materials at \(10^{-4}\,e\), 2/18 at \(10^{-3}\,e\), and 1/18 at \(10^{-2}\,e\);
- over a two-decade amplitude sweep (×0.1 to ×10), the floor changed by a median of **0.76 decades** (P10 0.00; P90 2.02), demonstrating that the reported floor is qualification-defined rather than an amplitude-free material constant.

Across the complete 319-system stability corpus, the QSQ non-evaluable fractions are **79.9%** at \(10^{-4}\,e\), **41.4%** at \(10^{-3}\,e\), and **9.7%** at \(10^{-2}\,e\) (`stability/eligibility_summary_A1.csv`).

One extreme QSQ response, `aflow-Al8Cu4U1_ICSD_601801`, corresponds to a permutation of symmetry-equivalent Al basins rather than a literal multi-electron chemical transfer. It is retained as `basin_relabelling_symmetry_equivalent` in `failure_registry.csv` and remains non-evaluable for a position-indexed atomic-charge QoI.

Historical repository identifiers such as `Protocol A`, `Protocol A.1`, and filenames containing `_A1` are retained only to preserve the frozen development record and machine-readable provenance; they are not the preferred scientific names of the qualification method.

---

## Supplementary Note 3 — Sensitivity analyses for eligibility and certification

The principal benchmark uses QSQ eligibility exactly as frozen. Four sensitivity analyses test how the reported conclusions depend on alternative reporting choices.

### S1 — No-exclusion diagnostic

`S1_no_exclusion` applies the Bader threshold directly without stability qualification. This is intentionally a diagnostic rather than an acceptable scientific decision rule. It quantifies how conventional binary reporting changes when non-evaluable material–threshold pairs are allowed to masquerade as pass/fail outcomes. Machine-readable source: `supplement/S1_S3_sensitivity.csv`.

### S2 — Error relative to the independent stability floor

For certified reconstructions, `supplement/S2_floor_relative.csv` reports \(\Delta Q_\mathrm{Bader}/f_m\). At \(10^{-4}\,e\), median ratios are **1.23** for SPERR, **1.33** for SZ3 and **1.09** for ZFP, with P90 values **3.20**, **2.86** and **3.25**, respectively. The strictest certified regime is therefore floor-scale. At \(10^{-3}\,e\), median ratios broaden to 2.78–3.55, and at \(10^{-2}\,e\) to 10.7–14.6. These data support an emerging analysis-limited regime at the strictest contract but do **not** establish a universal material-level identity between a tight-ladder plateau and the QSQ floor.

### S3 — Inflated-threshold stress test

`S3_inflated_threshold` evaluates alternative thresholds multiplied by \(k=2,5,10\). This analysis tests whether qualitative codec conclusions arise only from a particular hard cutoff. It is a robustness analysis and must not replace the pre-specified chemical contracts. Machine-readable source: `supplement/S1_S3_sensitivity.csv`.

### S4 — Probe-amplitude sensitivity

The 18-material amplitude sweep in `supplement/S4_amplitude_sensitivity.csv` reports floors at ×0.1, ×1 and ×10 of the QSQ perturbation amplitude. The heterogeneity across materials is part of the result: some systems are plateau-like while others scale substantially. The purpose is to demonstrate qualification-procedure dependence transparently, not to tune the amplitude post hoc.

---

## Supplementary Note 4 — Extended operator controls

### Electron-count negative control

All **6,343** development reconstruction rows were examined for total-electron-count fidelity (`analysis/electron_count_qoi/`). Among **3,205** rows with \(|\Delta N_e|<10^{-4}\,e\) and a finite re-derived Bader result, **1,383 (43.15%)** still have Bader error \(\ge10^{-3}\,e\). Global electron-number conservation is therefore not a sufficient certificate of atom-resolved chemical fidelity.

### Hartree-potential control

The full Hartree expansion targets the same 6,343 reconstruction rows. A reproduction gate retains **6,270** rows for formal statistics (`analysis/hartree_potential_expansion/RESULTS_DETAIL.md`). The pooled relation between Hartree error and realized \(L_\infty\) has a log–log slope of **1.02**. Across 678 material–codec pairs with at least five gate-passing points, median material-level Hartree \(R^2\) is approximately **0.994–0.997** by codec, whereas Bader response is much less regular. Hartree is strictly monotone in 88.6% of such pairs versus 32.4% for Bader.

The 73 Hartree reproduction-gate failures are all SZ3 rows with reconstruction distortion reproduced to within approximately 2×10^-5 relative, but compressed byte counts differing across platforms. They are classified as infrastructure `reproduction_mismatch`, excluded from formal Hartree statistics, and should not be described as codec or numerical failures.

At matched Hartree error, Bader response remains dispersed: **55.4%** of gate-passing rows lie in 0.5-decade Hartree-error bins where the Bader P90/P10 ratio is at least 10. This supports the use of structurally distinct downstream operators in the main manuscript without claiming that Hartree is universally “better” than Bader.

---

## Supplementary Note 5 — Binary-to-three-state reclassification

The primary Figure 3 audit uses one material–codec decision per Bader threshold, giving **254 materials × 3 codecs = 762 decisions per threshold**. The pooled results are frozen in `analysis/certifiability_reclassification_pooled_20260911.csv`; codec-resolved counts are in `analysis/certifiability_reclassification_by_codec_20260911.csv`.

At \(10^{-4}\,e\), a naive binary benchmark reports 533 failures, of which **518 (97.2%)** occur on non-evaluable material–threshold pairs; only 15 remain genuine eligible failures. At \(10^{-3}\,e\), **296/310 (95.5%)** naive failures are non-evaluable, leaving 14 genuine failures. At \(10^{-2}\,e\), **61/108 (56.5%)** are non-evaluable, leaving 47 genuine failures.

The qualification is not a permissive rescue rule: at \(10^{-4}\,e\), **106/229 (46.3%)** naive passes also occur on non-evaluable pairs. Supplementary Table S4 should expose the codec-by-codec decomposition so that this conclusion is auditable beyond the pooled Figure 3 presentation.

---

## Supplementary Note 6 — Extended Bader mechanism and cross-implementation robustness

The scientific Bader metric re-derives atom-centred basins after every reconstruction. Fixed-basin scoring is retained only as a diagnostic because it suppresses the domain-migration component.

The machine-readable mechanism tables are `mechanism/basin_error_decomposition_per_atom.csv` and `mechanism/basin_error_decomposition_summary.csv`. Representative systems are evaluated across three codecs and three chemical tolerances, with the charge change separated into an integrand contribution on the reference domain and a residual domain-migration contribution. The supplementary presentation should show the full representative-case matrix rather than only the selected main-text examples.

A separate independent-Bader study in `mechanism/independent_bader_20260908/` provides an implementation-robustness check. It contains **1,560/1,560 expected outcome rows** across a stratified panel and three solver modes. Henkelman on-grid reproduces BaderKit on-grid codec response with a median ratio of **1.00** (IQR approximately 0.92–1.005), aside from systems whose unperturbed basin sets differ. Codec ordering at relative tolerance \(10^{-4}\) is preserved across BaderKit on-grid, Henkelman on-grid and Henkelman near-grid. These results should remain supplementary because they validate robustness rather than define the central benchmark claim.

---

## Supplementary Note 7 — Realized-distortion matching diagnostics

Equal nominal codec tolerance is not a common realized-distortion scale. At equal nominal settings, median realized-\(L_\infty\) ratios are approximately **0.170** for ZFP/SZ3, **0.170** for ZFP/SPERR and **1.00** for SZ3/SPERR (`analysis/matched_realized_linf_v1/REPORT.md`).

The primary within-material match uses a **0.10-dex** caliper in \(\log_{10}(L_\infty)\), without replacement, and bootstraps materials rather than rows. At this caliper, the matched datasets contain 457 ZFP–SZ3 pairs from 214 materials, 465 ZFP–SPERR pairs from 206 materials, and 1,848 SZ3–SPERR pairs from 254 materials. Median larger/smaller realized-\(L_\infty\) is approximately 1.14 for the ZFP comparisons and 1.00 for SZ3/SPERR.

After matching, re-derived Bader-error ratios are **0.557** for ZFP/SZ3 (95% material-bootstrap CI 0.525–0.598), **0.601** for ZFP/SPERR (0.534–0.662), and **1.033** for SZ3/SPERR (0.976–1.072). Supplementary Figure S6 should show the sensitivity across 0.05, 0.10, 0.20 and 0.30 dex together with common-support counts; the main text should continue to report only the primary 0.10-dex result and the statement that direction is robust across the pre-specified calipers.

---

## Supplementary Note 8 — Stability-qualified rate–fidelity tables

For each eligible material–threshold pair, the benchmark selects the highest compression ratio on the frozen codec ladder that satisfies the re-derived Bader contract. `benchmark/summary_a1.csv`, `benchmark/pairwise_a1.csv` and `benchmark/best_certified_a1.csv` are the machine-readable sources.

The supplementary presentation should report, for each \(\tau\), stratum and codec: admitted denominator, non-evaluable denominator, certified count/fraction, median best-certified compression ratio, bootstrap confidence interval and distributional quantiles. Pairwise win fractions should be reported separately rather than folded into a single ranking label.

**Submission audit flag:** the final SI table must be regenerated directly from the current frozen benchmark files rather than copied from older prose summaries. Some historical narrative files contain earlier rate–fidelity values from intermediate aggregation states. `benchmark/summary_a1.csv` / the final manuscript-generation pipeline must be treated as the numerical source of record when the submission package is built.

---

## Supplementary Note 9 — External confirmation

The primary external confirmatory cohort contains **63/63 completed systems**, **1,689 retained scientific rows**, **0 material-level pipeline failures**, **0 codec-bound violations** and **3 preserved row-level Bader solver failures** affecting two materials (`validation/EXTERNAL_CONFIRMATORY63_20260908.md`). The final frozen 65-system descriptive aggregate contains **65/65 systems** and **1,755 rows**, also with zero material-level failures and zero bound violations.

For the primary 63-system confirmatory cohort, QSQ eligibility counts are **16**, **42** and **57** systems at \(10^{-4}\), \(10^{-3}\) and \(10^{-2}\,e\), respectively. The three pre-specified rate–fidelity directions reproduce: ZFP > SZ3 > SPERR at \(10^{-4}\,e\), ZFP ≈ SZ3 > SPERR at \(10^{-3}\,e\), and SZ3 > ZFP > SPERR at \(10^{-2}\,e\). The ZFP–SZ3 separation at the strictest threshold is narrower than in development and should not be described as a strong external separation.

The supplementary external section should also retain the row-level solver failures, recovery provenance for `aflow-Cl1O12Pb5V3_ICSD_203074`, the descriptive 65-system aggregate, and the distinction between `vacuum-containing 2D` systems and development adsorbate slabs.

---

## Supplementary Note 10 — Failure taxonomy and negative results

`failure_registry.csv` is the canonical failure register. Scientific non-evaluability, Bader-solver failure, reproduction mismatch and symmetry-equivalent basin relabelling must remain distinct categories. None should be silently converted into missing data or codec failure.

Negative algorithmic results are valuable supplementary evidence because they delimit the paper's contribution. The claim–evidence matrix records that boundary-aware allocation did not improve compression, the promolecule prior was detrimental, and symmetry folding did not yield a robust advantage. These results should be summarized compactly in Supplementary Table S14 rather than developed into a competing algorithm narrative. The paper's contribution is the measurement/certification framework, not a new codec.

---

# Proposed Supplementary Tables

| Table | Content | Primary source | Status |
|---|---|---|---|
| **Table S1** | Cohort composition, denominator conventions and provenance | `materials_metadata.csv`; `external_test_MANIFEST.json`; `validation/EXTERNAL_CONFIRMATORY63_20260908.md` | **READY** |
| **Table S2** | QSQ definition, seeds, amplitudes, decision semantics and archived float32-probe provenance | `protocol/PROTOCOL_A1.md`; `protocol/PROTOCOL_A_archived.md` | **READY** |
| **Table S3** | QSQ eligibility by threshold and stratum; archived float32 probe shown only as provenance | `stability/eligibility_summary_A1.csv` | **READY** |
| **Table S4** | Binary-to-three-state reclassification by codec | `analysis/certifiability_reclassification_by_codec_20260911.csv` | **READY** |
| **Table S5** | No-exclusion and inflated-threshold sensitivity | `supplement/S1_S3_sensitivity.csv` | **READY** |
| **Table S6** | Certified Bader error relative to QSQ floor | `supplement/S2_floor_relative.csv` | **READY** |
| **Table S7** | QSQ probe seed and amplitude sensitivity | `stability/stability_floor_A1_per_seed.csv`; `supplement/S4_amplitude_sensitivity.csv` | **READY** |
| **Table S8** | Electron-count control by codec/tolerance | `analysis/electron_count_qoi/electron_bader_decoupling.csv` | **BUILT** — `paper/SUPPLEMENTARY_TABLES_S8_S9_20260911.md` |
| **Table S9** | Hartree pooled scaling, material smoothness and reproduction gate | `analysis/hartree_potential_expansion/group_summary.csv`; `material_smoothness.csv`; `matched_error_dispersion.csv` | **BUILT** — `paper/SUPPLEMENTARY_TABLES_S8_S9_20260911.md` |
| **Table S10** | Bader domain decomposition across representative systems | `mechanism/basin_error_decomposition_summary.csv`; `..._per_atom.csv` | **READY** |
| **Table S11** | Cross-implementation Bader robustness + resolved 24-system QSQ classification transfer | `mechanism/independent_bader_20260908/`; `validation/qsq_prospective/p3a_implementation_transfer_resolved/` | **BUILT** — `paper/SUPPLEMENTARY_TABLES_S10_S11_20260911.md` |
| **Table S12** | Realized-L∞ matching quality and caliper sensitivity | `analysis/matched_realized_linf_v1/` | **READY** |
| **Table S13** | Development and external stability-qualified rate–fidelity summaries | `benchmark/summary_a1.csv`; `validation/final_external_confirmatory63_20260908/confirmatory63/` | **READY, regenerate at final build** |
| **Table S14** | Failure taxonomy and negative algorithm results | `failure_registry.csv`; `paper/CLAIM_EVIDENCE_MATRIX.md` | **READY, needs compact aggregation** |

# Proposed Supplementary Figures

All final supplementary figures should be generated from R sources and exported as PNG/PDF/SVG, following the same reproducibility standard as Figures 1–7.

| Figure | Content | Source data | Status |
|---|---|---|---|
| **Fig. S1** | Archived float32-probe vs QSQ stability-floor distribution and threshold eligibility | `stability/stability_floor_A1.csv`; archived predecessor; `eligibility_summary_A1.csv` | **LOCKED** |
| **Fig. S2** | QSQ five-seed spread and ×0.1/×1/×10 amplitude sensitivity | `stability/stability_floor_A1_per_seed.csv`; `supplement/S4_amplitude_sensitivity.csv` | **LOCKED** |
| **Fig. S3** | Full electron-count and Hartree control distributions | `analysis/electron_count_qoi/`; `analysis/hartree_potential_expansion/` | **LOCKED** |
| **Fig. S4** | Tight-regime Bader error/QSQ-floor ratios and tight-ladder diagnostic | `supplement/S2_floor_relative.csv`; `benchmark/master_benchmark_tight_ladder.csv` | **LOCKED** |
| **Fig. S5** | Extended fixed-basin/re-derived decomposition plus cross-implementation check | `mechanism/basin_error_decomposition_*`; `mechanism/independent_bader_20260908/` | **PLANNED R** |
| **Fig. S6** | Realized-L∞ matching support and 0.05–0.30 dex caliper sensitivity | `analysis/matched_realized_linf_v1/` | **PLANNED R** |
| **Fig. S7** | Codec-resolved binary reclassification beyond pooled Figure 3 | `analysis/certifiability_reclassification_by_codec_20260911.csv` | **LOCKED** |
| **Fig. S8** | External confirmatory per-system/pairwise distributions and audit summary | `validation/final_external_confirmatory63_20260908/confirmatory63/` | **PLANNED R** |

# Submission boundaries

1. The SI must not reintroduce withdrawn claims from earlier qualification stages.
2. Archived float32-probe results are provenance only and must be visibly labelled archived/provisional.
3. `NON_EVALUABLE_BADER_UNSTABLE` is neither pass nor failure.
4. The 319-system stability universe and 63-system primary external confirmatory cohort use different denominators and must be labelled separately.
5. Tight-ladder data support “floor-scale, consistent with an emerging analysis-limited regime”, not universal `plateau = floor`.
6. The resolved 24-system P3A panel validates classification transfer across the tested independent on-grid implementation, while near-grid threshold switches demonstrate implementation dependence. It does not redefine the frozen primary metric and does not establish grid convergence.
7. Supplementary figures should be regenerated in R rather than using legacy exploratory plots as final publication graphics.
8. Negative algorithm results belong in the SI to show what was tested and falsified; they should not compete with the benchmark-validity narrative.

# Current completion assessment

- **Raw evidence coverage:** high; nearly all intended SI claims already have frozen machine-readable sources.
- **Submission-facing SI prose:** first structured draft completed here.
- **Supplementary tables:** S1–S9 are now built as submission-facing drafts/objects; S10–S12/S14 require compact aggregation and S13 requires deterministic final regeneration. No new core scientific experiment is required.
- **Supplementary figures:** S1–S4 and S7 are locked R figures; S5, S6 and S8 remain to be built/locked from existing frozen analyses.
- **Highest-priority remaining build:** complete S10–S14 and Figures S5/S6/S8, then rerun the final manuscript ↔ SI cross-reference audit.


<!-- P4_CONTRACT_BOUNDARY_SI -->
## Supplementary Note | Outcome-blind chemical-decision boundary case study

An outcome-blind chemistry/provenance/geometry audit of the 68 NOMAD development slabs froze five paired states before QSQ, codec or Bader outcomes were inspected for inclusion. All five passed the independently frozen two-implementation source-reference rule. Across ZFP, SZ3 and SPERR on the four common tight settings, all 60 direct qualitative target-atom charge-transfer directions were preserved after compression. QSQ at $10^{-3}\,e$ retained 36/60 trials from three pairs, while the unqualified baseline retained all 60; both had zero observed sign errors. This deliberately negative result shows that the strict numerical Bader contract and a coarse sign-level chemical interpretation are different fidelity targets. Full pair-level reference values and policy accounting are provided in Supplementary Tables S15-S16.

The resolved compressed analysis contains 216/216 successful solver cells. The first execution's 144 failures were classified before retry as missing-work-directory engineering errors, and the retry executed exactly those failed keys without changing the scientific design. P3B new-DFT grid convergence was not used; the source reference is a BaderKit/Henkelman on-grid consensus under the declared density representation.
