# Revised main-figure map after realized-Linf post-processing

Branch-only editorial proposal. The frozen main-branch figure map is not modified.

## Figure 1 — Why a pointwise bound is not a chemical contract
Schematic: original density -> error-bounded compression -> reconstruction -> Bader partition -> atomic charges. Show the two evaluation paths: fixed original basins (diagnostic) versus basins re-derived from the reconstructed field (chemical contract). Introduce

`Delta Q_total = Delta Q_integrand + Delta Q_domain`.

Purpose: define the distinction between reconstructing a field and preserving a downstream quantity of interest.

## Figure 2 — Reusing the original partition hides the dominant error
(a) Paired fixed-basin versus re-derived Bader errors across the benchmark, log-log, identity line. (b) Distribution of the understatement factor, stratified by codec. (c) Representative basin-label changes.

Headline: among 4,627 successful base-ladder rows, re-derived error exceeds fixed-basin error in 99.7%; median resolved/fixed ratio is 52.8x overall (SPERR 100.1x, SZ3 8.0x, ZFP 106.9x).

Purpose: establish that the downstream analysis must be rerun on reconstructed data; evaluating reconstructed values over the original domains is not a faithful QoI test.

Data: `benchmark/master_benchmark_base_ladder.csv`, `analysis_output/reviewer_stress_tests.md`.

## Figure 3 — Basin migration is the mechanism
(a) For 12 stability-stratified materials, stacked magnitude of within-basin integrand contribution and domain-migration contribution at the maximum-error atom. Use the bounded dominance fraction `|domain|/(|domain|+|integrand|)` rather than `|domain|/|total|`, because cancellation can make the latter exceed one. Current summary: median bounded domain dominance 0.995; 84.9% of cases exceed 0.90; numerical closure residual <=2.22e-16 e. (b) Fraction of voxels reassigned versus realized L∞. (c) One illustrative material showing basin-boundary migration. (d) Mechanism-consistency regression at the 1e-3 e A.1 contract: after controlling material and realized L∞, the codec-associated multipliers are ~2x; after adding `frac_voxels_reassigned`, they attenuate to ~1. In the conservative complete-case analysis (all 20 materials with any <=0.01 registered failure removed), SZ3/ZFP 2.34x -> 0.96x and SPERR/ZFP 2.08x -> 0.94x; the log-log reassignment coefficient is 0.880 [0.723,1.037], p=5.78e-28.

Interpretation: panel (d) is **mediation-consistent / attenuation evidence**, not a causal-mediation estimate. Reassignment is a post-compression variable. The direct decomposition in panel (a) is the primary mechanism evidence.

Purpose: provide direct and statistical evidence that the dominant downstream error enters through movement of field-derived integration domains rather than density perturbation inside a frozen domain.

Data: `mechanism/basin_error_decomposition_summary.csv`, `analysis_output/complete_case_failure_sensitivity.md`; replace/augment panel (a) with the full per-atom table when its main-branch commit lands.

## Figure 4 — A QoI must be resolvable before it can be certified
(a) Protocol A.1 stability-floor distributions for development bulk, development slab, external bulk and external vacuum-containing systems, with 1e-4/1e-3/1e-2 e contract lines. (b) Non-evaluable fraction by contract. (c) Probe validation: archived float32 round trip versus non-monotone noise at matched amplitude; exact ties and voxel-reassignment counts. (d) Generalization/predictability audit: development cross-validation versus untouched external AUROC for conventional descriptors.

Headline numbers: 41.4% of 319 systems non-evaluable at 1e-3 e and 79.9% at 1e-4 e under Protocol A.1. Conventional descriptors fail to transfer as useful predictors: external AUROC 0.409, 0.387 and 0.398 for 1e-4, 1e-3 and 1e-2 e eligibility, respectively.

Purpose: establish stability qualification, show why the probe itself must be validated, and demonstrate that the issue survives on untouched external systems.

Data: `stability/`, `materials_metadata.csv`, `external_test_MANIFEST.json`, `analysis_output/resolvability_predictability.csv`.

## Figure 5 — Nominal bound, realized magnitude, and residual codec-associated structure
This replaces the old Figure 6.

(a) Distribution of `realized_Linf / nominal_tolerance_absolute`: SZ3 median 1.000, SPERR 1.000, ZFP 0.1575. (b) Same-nominal codec comparisons, explicitly labelled as a mixture of bound-utilization and structure effects. (c) Mutual-nearest matched-realized-L∞ comparison at <=0.10 dex. On all successful rows: SZ3/ZFP 1.81x [1.70,1.95], SPERR/ZFP 1.72x [1.54,1.89]. (d) Stability-qualified sensitivity at A.1 eligibility tau=1e-3 e: SZ3/ZFP 1.90x [1.70,2.20], SPERR/ZFP 1.87x [1.63,2.08]. (e) Conservative complete-case reviewer stress test: remove every material with any registered failure at nominal relative tolerance <=0.01 (20 materials; 254 -> 234). The 0.10-dex matched ratios remain SZ3/ZFP 1.82x [1.68,2.01] and SPERR/ZFP 2.00x [1.79,2.25]; within-material common-support interpolation gives 2.07x [1.95,2.19] and 1.99x [1.83,2.21].

Purpose: establish two separable effects. ZFP benefits partly from under-utilizing its nominal pointwise budget; nevertheless a roughly twofold codec-associated residual remains after controlling realized magnitude and QoI resolvability, and survives conservative exclusion of materials with downstream failures. Do not describe the statistical adjustment itself as causal evidence; the mechanistic interpretation is supported separately by Figure 3.

Data: `benchmark/master_benchmark_full.csv`, `analysis_output/matched_realized_linf_*`, `analysis_output/stability_qualified_structure_effect.md`, `analysis_output/reviewer_stress_tests.md`, `analysis_output/complete_case_failure_sensitivity.md`.

## Figure 6 — The certified compression frontier is contract-dependent
Plot best certified compression ratio against Bader contract, with certification coverage as a second visual channel; facet bulk/slab. Highlight the crossover: SZ3 leads at 1e-2 e, SZ3 and ZFP are similar near 1e-3 e, and ZFP leads at 1e-4 e. Include lossless baselines as horizontal references. Explicitly distinguish NON_EVALUABLE from codec failure.

Purpose: translate the methodological findings into the practical compression decision. Avoid declaring one codec globally best.

Data: `benchmark/best_certified_a1.csv`, `benchmark/summary_a1.csv`, `benchmark/lossless_baselines.jsonl`.

## Supplementary figure allocation
- S1/S3: eligibility/exclusion sensitivity and inflated-threshold sensitivity.
- S2: Bader error relative to each material's own stability floor.
- S4/S5: probe amplitude and seed sensitivity.
- S6/S7: negative algorithm results (boundary-aware allocation and promolecule prior).
- S8: complete failure taxonomy and registry, including the symmetry-equivalent relabelling case.
- S9: external baseline unit conversions and excluded/non-comparable codecs.
- S10: extended matched-realized-L∞ calipers, common-support interpolation and complete-case failure sensitivity.

# Main-text claim hierarchy
1. A pointwise error bound alone does not specify downstream chemical fidelity.
2. Reusing the original downstream partition severely understates error because it suppresses domain migration by construction.
3. Basin-domain migration is the dominant measured contribution in the representative mechanism set; across the full benchmark, basin reassignment statistically accounts for most of the codec-associated residual after controlling realized L∞ and material identity.
4. A QoI must itself be numerically resolvable at the requested contract before compression fidelity can be certified; the stability probe must also perturb the mathematical structure on which the QoI algorithm depends.
5. Same-nominal codec differences contain a large bound-utilization component, but after stability qualification, control of realized L∞, and conservative exclusion of failure-affected materials, a codec-associated residual of roughly twofold remains before accounting for basin reassignment.
6. Once evaluated honestly, lossy compression remains valuable, but the preferred codec depends on the chemical accuracy contract and certification coverage.
