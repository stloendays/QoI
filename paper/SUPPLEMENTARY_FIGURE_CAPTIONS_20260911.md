# Supplementary figure captions

Updated 2026-09-11. Canonical submission-facing captions for the formal supplementary figures. Figure numbering follows `paper/SUPPLEMENTARY_ASSET_MAP_20260911.md`.

## Supplementary Figure S1 | QSQ defines the measurable Bader-fidelity landscape

**A,** Material-level Bader stability floors measured with the archived float32 probe and the operative five-seed QoI Stability Qualification (QSQ) perturbation probe. The dashed line marks equality; points above it indicate a larger inferred instability under QSQ. The archived probe is retained only as provenance and is not used for current eligibility or certification. **B,** Overall fraction of the 319-system stability universe classified as non-evaluable at the three Bader tolerances under the archived float32 probe and QSQ. **C,** QSQ non-evaluable fractions resolved by development bulk, development slab, external bulk, and external vacuum-containing 2D strata. Numerical eligibility depends strongly on the requested tolerance and cannot be inferred from a universal bulk-versus-slab rule. A non-evaluable material-threshold pair is neither a codec pass nor a codec failure.

**Sources:** `stability/stability_floor_A1.csv`; `stability/stability_floor_A_archived_float32.csv`; `stability/eligibility_summary_A1.csv`.

**R source:** `figures/R/supplement/figureS1_stability_floor_landscape.R`.

## Supplementary Figure S2 | QSQ probe validation, seed sensitivity and amplitude sensitivity

**A-B,** Eighteen-material pre-freeze calibration comparing the archived order-preserving float32 round trip with the non-order-preserving QSQ perturbation probe at the same material-specific amplitude. Float32 rounding creates exact neighbouring ties and leaves more systems with zero basin reassignment, whereas the QSQ probe more effectively excites the order-dependent Bader partition response. In the pre-freeze 18-material calibration, the five-seed log10 floor span had a median of approximately 0.47 decades and a maximum of approximately 2.4 decades. **C,** Deployment of the frozen five-seed QSQ procedure across the full 319-system stability corpus. The full-corpus within-material log10 span has a median of approximately **0.37 decades** and a maximum of approximately **3.82 decades**. Relative to the five-seed maximum, using only the primary seed changes the eligibility verdict for **35/319** systems at 10^-4 e, **17/319** at 10^-3 e, and **2/319** at 10^-2 e. The calibration and full-corpus statistics answer different questions and are therefore reported separately. **D,** Floor response across a two-decade perturbation-amplitude sweep on the 18 calibration materials. The median change from x0.1 to x10 is approximately 0.76 decades, with substantial between-material heterogeneity. The amplitude sweep is a sensitivity analysis and was not used to retune the frozen QSQ definition.

**Sources:** `stability/probe_calibration.csv`; `stability/stability_floor_A1_per_seed.csv`; `supplement/S4_amplitude_sensitivity.csv`; `protocol/PROTOCOL_A1.md`.

**R source:** `figures/R/supplement/figureS2_probe_seed_amplitude.R`.

## Supplementary Figure S7 | Codec-resolved consequences of stability qualification

**A,** Naive failures for ZFP, SZ3, and SPERR decomposed into genuine eligible failures and failures reclassified as non-evaluable after QSQ. At 10^-4 and 10^-3 e, more than 93% of naive failures for every codec occur on material-threshold pairs for which the reference Bader QoI is not independently resolvable. Specifically, the reclassified fractions are 100.0%, 96.1%, and 96.4% for ZFP, SZ3, and SPERR at 10^-4 e, and 98.8%, 93.9%, and 94.5% at 10^-3 e. **B,** Fraction of naive passes that also occur on non-evaluable material-threshold pairs, demonstrating that eligibility qualification invalidates apparent successes as well as apparent failures. **C,** Genuine eligible-failure fraction after conditioning on numerical eligibility; exact counts are reported in Supplementary Table S4. Each codec contributes 254 development material-level decisions per threshold. QSQ therefore changes the benchmark label space rather than relaxing the criterion for a particular codec.

**Source:** `analysis/certifiability_reclassification_by_codec_20260911.csv`.

**R source:** `figures/R/supplement/figureS7_reclassification_by_codec.R`.

## Supplementary Figure S3 | Extended operator controls separate global, smooth nonlocal and topology-sensitive QoIs

**A,** Electron-count error versus re-derived Bader-charge error across finite development reconstructions. The dashed thresholds mark |ΔNe| = 10^-4 e and Bader error = 10^-3 e; 1,383 of 3,205 reconstructions (43.15%) that satisfy the electron-count threshold still exceed the Bader threshold. **B,** Paired material-level goodness of fit for Hartree-potential and Bader response across 678 material–codec pairs with at least five reproduction-gate-passing rows. **C,** Strict monotonicity resolved by bulk/slab stratum and codec. Hartree response is substantially smoother overall, while the slab result is intentionally retained as a caveat against claiming universal monotonicity. **D,** Dispersion of re-derived Bader error within 0.5-decade Hartree-error bins containing at least 10 rows; 3,452 of 6,229 rows (55.4%) lie in bins with Bader P90/P10 ≥ 10. Together these controls show that similar global or smooth nonlocal fidelity does not uniquely determine the topology-sensitive Bader response.

**Sources:** `analysis/electron_count_qoi/electron_bader_decoupling.csv`; `analysis/hartree_potential_expansion/group_summary.csv`; `analysis/hartree_potential_expansion/material_smoothness.csv`; `analysis/hartree_potential_expansion/matched_error_dispersion.csv`.

**R source:** `figures/R/supplement/figureS3_operator_controls.R`.

## Supplementary Figure S4 | The strictest certified Bader regime is floor-scale, not a universal plateau

**A,** Re-derived Bader error normalized by the independently measured QSQ stability floor for one highest-rate certified reconstruction per material–codec pair. Points show the median and bars the P10–P90 range. At 10^-4 e, median error/floor is 1.09 for ZFP, 1.33 for SZ3 and 1.23 for SPERR. **B,** Material-level relation between the QSQ floor and the best-certified re-derived Bader error at the 10^-4 e contract (n = 123 certified material–codec decisions); the dashed diagonal denotes equal scales. **C,** Median and interquartile range of error/floor across the frozen tight ladder as a function of nominal relative codec tolerance. This panel is descriptive and is not used as a material-level plateau estimator. The strictest certified regime is therefore floor-scale and consistent with an emerging analysis-limited regime, but the data do not establish a universal identity between a compression plateau and the QSQ floor.

**Sources:** `supplement/S2_floor_relative.csv`; `benchmark/master_benchmark_full.csv`; `benchmark/master_benchmark_tight_ladder.csv`.

**R source:** `figures/R/supplement/figureS4_tight_floor_scale.R`.

## Interpretation boundary

Figures S1, S2 and S7 support the benchmark-validity and probe-validation claims. They do not establish that the QSQ stability floor is an amplitude-free intrinsic material property, do not convert non-evaluable cases into successful codec outcomes, and do not imply a universal codec ranking. Historical source filenames and protocol documents retain their frozen identifiers solely for provenance.
