# Supplementary figure map and captions — manuscript v0.3

The supplement is organized to keep the main text focused on the contract and mechanism while making every exclusion, sensitivity and negative result auditable.

## Supplementary Figure S1 | Protocol-A.1 eligibility and certification semantics

Flow diagram and counts separating (i) the full stability corpus, (ii) Protocol-A.1-eligible materials at each Bader-charge contract, (iii) successful codec/Bader reconstructions and (iv) certified operating points. NON_EVALUABLE_BADER_UNSTABLE is shown as a QoI-eligibility state rather than a codec failure. Failed Bader solves are shown separately using `failure_registry.csv`. Purpose: make denominators and exclusion semantics explicit.

## Supplementary Figure S2 | Bader error normalized by each material's Protocol-A.1 stability floor

For eligible and near-boundary materials, plot re-derived Bader error divided by `stability_floor_A1_e` across codec and requested tolerance. The figure distinguishes absolute charge contracts from each system's measured numerical resolvability scale. Purpose: show that the benchmark conclusions do not depend on treating the same absolute QoI threshold as equally distant from the numerical floor for every material.

## Supplementary Figure S3 | Eligibility-threshold sensitivity

Repeat key certification summaries under the prespecified inflated-threshold / alternative eligibility sensitivity already stored in `supplement/`. Purpose: show which engineering conclusions depend on the exact A.1 admission boundary without changing the frozen primary protocol.

## Supplementary Figure S4 | Seed sensitivity of the Protocol-A.1 stability probe

For the 18-material calibration set, display the distribution of `floor_e` over the five preregistered random seeds at amplitude factor 1. Report the within-material log10 range: median 0.47 decades, maximum 2.39 decades. Mark cases whose eligibility changes across individual seeds at the three charge contracts. Purpose: justify the conservative five-seed maximum rather than a single random realization.

## Supplementary Figure S5 | Probe-amplitude sensitivity

For the primary calibration seed, plot Bader stability floor at amplitude factors 0.1, 1 and 10 for each calibration material. The median floor shift between 0.1× and 10× is 0.76 decades. Purpose: make clear that the A.1 floor is protocol-defined at a stated perturbation amplitude, not an intrinsic material constant.

## Supplementary Figure S6 | Archived float32 probe versus calibrated non-monotone probe

Paired comparison of stability floor, exact-neighbour ties, local axis-order flips and voxel reassignment for matched perturbation amplitude. Purpose: document why the frozen Protocol A probe was archived rather than silently retained after validation exposed its order-preserving blind spot.

## Supplementary Figure S7 | Negative algorithmic result: boundary-aware error allocation

Report the prespecified boundary-aware codec modification / allocation experiment from the existing supplement, including the absence of a robust improvement if that remains the frozen result. Purpose: prevent selective reporting and show that identifying the failure mechanism does not imply that the first intuitive mitigation succeeds.

## Supplementary Figure S8 | Negative algorithmic result: promolecule or prior-based correction

Report the prespecified prior/promolecule experiment and its negative or mixed outcome according to the frozen records. Purpose: preserve methodological completeness and distinguish diagnosis from a claimed new compressor.

## Supplementary Figure S9 | Failure registry and symmetry-equivalent relabeling

**a,** Failure counts by codec, system type and nominal tolerance. Of 77 registered exceptional rows, 76 are Bader-solver failures and one is a symmetry-equivalent basin-relabeling event. **b,** Low-tolerance failures (nominal relative tolerance <=0.01), highlighting 20 ZFP and 4 SPERR cases across 20 materials. **c,** `aflow-Al8Cu4U1_ICSD_601801`: position-indexed apparent charge change versus preserved charge multiset under symmetry-equivalent basin permutation. **d,** Symmetry-aware sensitivity: after removing the single known relabeling case, Protocol-A.1 non-evaluable fractions change from 79.94% to 79.87%, 41.38% to 41.19%, and 9.72% to 9.43% at 1e-4, 1e-3 and 1e-2 e, respectively. Purpose: make pathological labels visible without retroactively modifying frozen A.1.

## Supplementary Figure S10 | Realized-L∞ matching robustness

**a,** Stability-qualified SZ3/ZFP and SPERR/ZFP Bader-error ratios across mutual-nearest matching calipers 0.05, 0.075, 0.10 and 0.15 decades. **b,** Within-material common-support log–log interpolation as a matching-free sensitivity. At the 1e-3 e contract, complete-case interpolation gives 2.07 [1.95,2.19] for SZ3/ZFP and 1.99 [1.83,2.21] for SPERR/ZFP. **c,** Number of retained material pairs as a function of caliper. Purpose: show that the approximately twofold residual is not a tuning artefact of the primary 0.10-decade window.

## Supplementary Figure S11 | Conservative complete-case exclusion of downstream failures

Repeat the primary matched-realized-L∞ comparison before and after removing an entire material whenever any codec has a registered failure at nominal relative tolerance <=0.01. Twenty materials are removed (254 -> 234). At the central 1e-3 e contract, complete-case ratios are 1.82 [1.68,2.01] for SZ3/ZFP and 2.00 [1.79,2.25] for SPERR/ZFP. Purpose: close the selective-survival concern created by codec-dependent downstream failures.

## Supplementary Figure S12 | Fixed-basin understatement is not a near-zero-denominator artefact

**a,** Pooled median resolved/fixed ratio as an imposed lower floor on the fixed-basin denominator is raised from 1e-15 to 1e-4 e. The pooled median remains 52.6× at a 1e-6 e floor and is 21.8× even at 1e-4 e. **b,** Material-balanced ratios by codec. **c,** Core-tolerance ratios stratified by codec. Purpose: support the 99.7% directional main-text headline while showing why a universal multiplicative factor is not used.

## Supplementary Figure S13 | Global electron-count deviation does not explain the codec-associated residual

Negative-control regression on Protocol-A.1-eligible, conservative complete-case materials at 1e-3 e and nominal relative tolerance <=0.01, restricted to common measured-L∞ support. Show codec multipliers under four models: (M0) material fixed effects + measured L∞; (M-electron) M0 + absolute total electron-count deviation; (M-reassign) M0 + reassigned-voxel fraction; and (M-both) both post-compression covariates. SZ3/ZFP changes 2.34× -> 2.58× after adding global electron-count deviation but 2.34× -> 0.96× after adding reassignment; SPERR/ZFP changes 2.08× -> 2.06× versus 0.94×. With both covariates, the electron-count coefficient is -0.017 [−0.040,0.006], p=0.139, while reassignment remains 0.879 [0.722,1.036], p=5.25×10^-28. Purpose: distinguish redistribution among field-derived atomic domains from simple global integral/conservation error. This is an observational negative control, not causal mediation.

## Supplementary Figure S14 | External generalization of resolvability

Development cross-validation and untouched external performance for conventional metadata-based eligibility models, with and without the known symmetry-equivalent relabeling case. External AUROC remains approximately 0.4 across contracts. Include prevalence and balanced accuracy to make distribution shift visible. Purpose: support the narrow conclusion that conventional metadata do not transfer as useful screening predictors.

## Supplementary Figure S15 | Tight-ladder necessity at strict chemical contracts

Compare best-certifiable operating points with and without the added 1e-7, 3e-7, 1e-6 and 3e-6 ladder. Purpose: demonstrate that strict-contract codec comparisons are not artifacts of a coarse original tolerance grid and document which materials would otherwise be left-censored.

## Supplementary Table S1 | Data provenance and licenses

One row per material with corpus, system type, formula, grid dimensions, atom count, source URL, SHA-256, byte size and license from `materials_metadata.csv`.

## Supplementary Table S2 | Protocol-A.1 stability results

One row per material with float32 amplitude, five-seed maximum stability floor, eligibility flags at all three contracts and archived Protocol-A values.

## Supplementary Table S3 | Codec benchmark summary

Codec × system type × tolerance summary with compression ratio, realized/nominal L∞ utilization, fixed and re-derived Bader errors, reassignment and certification coverage.

## Supplementary Table S4 | Complete failure registry

All 77 registered exceptional cases with category and detail. No failure row is silently treated as successful benchmark data.

## Supplementary Table S5 | Matched-realized-L∞ sensitivity estimates

All calipers, contracts and codec pairs, including number of pairs/materials, median matched L∞ ratio, Bader-error ratio, bootstrap interval and direction-consistency fraction.

## Supplementary Table S6 | Regression and negative-control coefficients

Material-fixed-effect models with measured L∞, codec, basin reassignment and global electron-count deviation; include clustered confidence intervals and the exact complete-case material count.

## Supplementary Table S7 | Direct mechanism decomposition

Current representative-case summary and, once released, preregistered case/material-level summaries from the full per-atom decomposition. Atom rows are not treated as independent replicates.
