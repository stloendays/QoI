# Supplementary figure captions

Updated 2026-09-11. Canonical submission-facing captions for the first formal supplementary figures. Figure numbering follows `paper/SUPPLEMENTARY_ASSET_MAP_20260911.md`.

## Supplementary Figure S1 | Protocol A.1 redefines the measurable Bader-fidelity landscape

**A,** Material-level Bader stability floors measured with the archived Protocol A float32 round-trip probe and the operative Protocol A.1 five-seed uniform-noise probe. The dashed line marks equality; points above it indicate a larger inferred instability under A.1. Protocol A is retained only as provenance and is not used for current eligibility or certification. **B,** Overall fraction of the 319-system stability universe classified as non-evaluable at the three Bader tolerances under archived Protocol A and operative Protocol A.1. **C,** Protocol A.1 non-evaluable fractions resolved by development bulk, development slab, external bulk, and external vacuum-containing 2D strata. Numerical eligibility depends strongly on the requested tolerance and cannot be inferred from a universal bulk-versus-slab rule. A non-evaluable material-threshold pair is neither a codec pass nor a codec failure.

**Sources:** `stability/stability_floor_A1.csv`; `stability/stability_floor_A_archived_float32.csv`; `stability/eligibility_summary_A1.csv`.

**R source:** `figures/R/supplement/figureS1_stability_floor_landscape.R`.

## Supplementary Figure S2 | Protocol A.1 probe validation, seed sensitivity and amplitude sensitivity

**A-B,** Eighteen-material pre-freeze calibration comparing the archived order-preserving float32 round trip with a non-order-preserving uniform-noise perturbation at the same material-specific amplitude. Float32 rounding creates exact neighbouring ties and leaves more systems with zero basin reassignment, whereas the noise probe more effectively excites the order-dependent Bader partition response. In the pre-freeze 18-material calibration, the five-seed log10 floor span had a median of approximately 0.47 decades and a maximum of approximately 2.4 decades. **C,** Deployment of the frozen five-seed procedure across the full 319-system stability corpus. The full-corpus within-material log10 span has a median of approximately **0.37 decades** and a maximum of approximately **3.82 decades**. Relative to the five-seed maximum, using only the primary seed changes the eligibility verdict for **35/319** systems at 10^-4 e, **17/319** at 10^-3 e, and **2/319** at 10^-2 e. The calibration and full-corpus statistics answer different questions and are therefore reported separately. **D,** Floor response across a two-decade perturbation-amplitude sweep on the 18 calibration materials. The median change from x0.1 to x10 is approximately 0.76 decades, with substantial between-material heterogeneity. The amplitude sweep is a sensitivity analysis and was not used to retune the frozen A.1 definition.

**Sources:** `stability/probe_calibration.csv`; `stability/stability_floor_A1_per_seed.csv`; `supplement/S4_amplitude_sensitivity.csv`; `protocol/PROTOCOL_A1.md`.

**R source:** `figures/R/supplement/figureS2_probe_seed_amplitude.R`.

## Supplementary Figure S7 | Codec-resolved consequences of stability qualification

**A,** Naive failures for ZFP, SZ3, and SPERR decomposed into genuine eligible failures and failures reclassified as non-evaluable after Protocol A.1 qualification. At 10^-4 and 10^-3 e, more than 93% of naive failures for every codec occur on material-threshold pairs for which the reference Bader QoI is not independently resolvable. Specifically, the reclassified fractions are 100.0%, 96.1%, and 96.4% for ZFP, SZ3, and SPERR at 10^-4 e, and 98.8%, 93.9%, and 94.5% at 10^-3 e. **B,** Fraction of naive passes that also occur on non-evaluable material-threshold pairs, demonstrating that eligibility qualification invalidates apparent successes as well as apparent failures. **C,** Genuine eligible-failure fraction after conditioning on numerical eligibility; exact counts are reported in Supplementary Table S4. Each codec contributes 254 development material-level decisions per threshold. Protocol A.1 therefore changes the benchmark label space rather than relaxing the criterion for a particular codec.

**Source:** `analysis/certifiability_reclassification_by_codec_20260911.csv`.

**R source:** `figures/R/supplement/figureS7_reclassification_by_codec.R`.

## Interpretation boundary

Figures S1, S2 and S7 support the benchmark-validity and probe-validation claims. They do not establish that Protocol A.1 is an amplitude-free intrinsic material property, do not convert non-evaluable cases into successful codec outcomes, and do not imply a universal codec ranking.
