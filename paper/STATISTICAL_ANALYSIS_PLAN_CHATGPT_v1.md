# Statistical analysis plan for manuscript freeze v1

Date: 2026-09-06

This document fixes the manuscript-level estimands and reporting hierarchy before the full per-atom mechanism table is available. It is editorial/statistical guidance for the analysis branch and does not modify frozen Protocol A or Protocol A.1.

## 1. Population and denominators

- Development benchmark: 254 materials.
- Successful master table: 6,343 reconstructions = 4,627 base-ladder + 1,716 tight-ladder rows.
- Registered exceptional rows are outside the successful master table and remain in `failure_registry.csv`.
- Protocol-A.1 eligibility is always defined at the material × charge-contract level before codec certification is evaluated.
- Any manuscript percentage must name its denominator: successful rows, eligible materials, all attempted cases, or complete-case materials.

## 2. Primary evaluation estimand: re-derived versus fixed Bader partition

Primary directional estimand:

`P(Bader_error_resolved_e > Bader_error_fixed_e)`

reported over successful base-ladder rows.

Current estimate: 99.70% of 4,627 rows.

The resolved/fixed ratio is secondary because it varies strongly by codec and tolerance. The pooled median (52.8x) may be reported only with its aggregation explicitly stated. Figure 2 should show codec/tolerance-resolved ratios rather than imply a universal multiplicative factor.

## 3. Primary magnitude-versus-structure estimand

Same-nominal codec comparisons are descriptive only. They mix:

1. nominal-bound utilization, and
2. residual codec-associated reconstruction structure.

Primary adjusted nonparametric comparison:

- restrict to Protocol-A.1-eligible materials at the stated charge contract;
- compare SZ3/ZFP and SPERR/ZFP within material;
- match mutual nearest neighbours in `log10(realized_Linf)`;
- primary caliper = 0.10 decades;
- summarize the Bader-error ratio first within material, then across materials;
- use material-level bootstrap confidence intervals.

Primary contract for the manuscript narrative: `tau = 1e-3 e`.

Current primary estimates:

- SZ3/ZFP = 1.90x [1.70, 2.20]; 128 materials; SZ3 worse in 91.4%.
- SPERR/ZFP = 1.87x [1.63, 2.08]; 124 materials; SPERR worse in 79.8%.

## 4. Prespecified sensitivity analyses for the ~2x residual

A result is considered robust only if direction and approximate magnitude survive:

- matching calipers 0.05, 0.075, 0.10, 0.15 decades;
- within-material log-log interpolation over common realized-Linf support;
- restriction to nominal relative tolerance <= 0.01;
- conservative complete-case exclusion: remove an entire material if any codec has any registered failure at nominal relative tolerance <= 0.01.

Current complete-case benchmark: 234 materials after removing 20 failure-affected materials.

At tau = 1e-3 e:

- complete-case 0.10-dex SZ3/ZFP = 1.82x [1.68, 2.01];
- complete-case 0.10-dex SPERR/ZFP = 2.00x [1.79, 2.25];
- common-support interpolation = 2.07x [1.95, 2.19] and 1.99x [1.83, 2.21].

## 5. Regression estimand

Material-fixed-effect regressions are supporting analyses, not the primary estimand.

Base model:

`log10(Bader_error_resolved_e) ~ log10(realized_Linf) + codec + material fixed effects`

At tau = 1e-3 e, current codec-associated multipliers versus ZFP are approximately:

- SZ3: 2.23x [2.09, 2.39]
- SPERR: 2.00x [1.86, 2.16]

Do not describe these coefficients as causal codec effects.

## 6. Mechanism-consistency attenuation

Expanded model adds `frac_voxels_reassigned` on the same A.1-qualified, common-realized-Linf support.

Interpretation is attenuation / mediation-consistent evidence, not formal causal mediation, because reassignment is measured after compression.

Complete-case current result:

- SZ3/ZFP: 2.34x -> 0.96x after adding reassignment;
- SPERR/ZFP: 2.08x -> 0.94x;
- log-log reassignment coefficient = 0.880 [0.723, 1.037], p = 5.78e-28.

The direct algebraic decomposition remains the stronger mechanistic evidence.

## 7. Direct mechanism decomposition

Until `mechanism/basin_error_decomposition_per_atom.csv` is committed, the primary mechanism evidence is restricted to the existing representative 12-material summary set.

Use bounded dominance:

`|dq_domain| / (|dq_domain| + |dq_integrand|)`

rather than `|dq_domain| / |dq_total|`, because cancellation can make the latter exceed one.

Current summary-level result:

- 106 successful cases / 12 materials;
- median bounded domain dominance = 0.995;
- IQR = 0.965–0.999;
- 84.9% of cases > 0.90;
- max closure residual <= 2.22e-16 e.

Do not generalize this direct decomposition to all 254 benchmark materials.

## 8. Per-atom analysis rule once the third commit lands

Atoms are nested observations, not independent replicates.

Primary per-atom summaries must therefore be aggregated at case/material level before across-material inference. Required checks:

- closure of `dq_total = dq_integrand + dq_domain` for every atom;
- distribution of bounded domain dominance by case;
- fraction of atoms with domain dominance > 0.5 and > 0.9, summarized per case then per material;
- contribution of the maximum-error atom relative to all atoms;
- leave-one-material-out sensitivity;
- material-level bootstrap, never atom-level bootstrap as the headline uncertainty.

No new atom-level headline metric should be selected after inspecting the final table unless labelled exploratory.

## 9. QoI resolvability estimand

Protocol A.1 defines a protocol/probe-dependent numerical stability floor, not an intrinsic material constant.

Headline non-evaluable fractions over 319 systems:

- tau = 1e-2 e: 9.7%
- tau = 1e-3 e: 41.4%
- tau = 1e-4 e: 79.9%

External predictability using conventional metadata is a generalization audit, not a proof of fundamental unpredictability. Current external AUROC is ~0.4 across the three contracts.

## 10. Probe-validation estimands

Use the calibration study to support the claim that a stability probe must perturb algorithmically relevant structure.

Headline quantities:

- matched float32 versus random-noise probe at amplitude factor 1: median floor ratio 29.0x;
- float32 median exact ties 82 versus noise 0;
- zero voxel reassignment 9/18 versus 2/18;
- five-seed log10-floor range median 0.47 decades, maximum 2.39;
- amplitude 0.1x -> 10x changes the floor by median 0.76 decades.

Therefore use `protocol-defined stability floor` or `probe-defined stability floor`, never `intrinsic Bader floor`.

## 11. Compression-certification decision estimand

The practical output is a contract-dependent frontier rather than a universal codec winner.

Primary quantities by system type and charge contract:

- best certified compression ratio;
- certification coverage among eligible materials;
- explicit NON_EVALUABLE count separated from codec failure.

Narrative crossover:

- 1e-2 e: SZ3 leads in compression ratio, ZFP often has higher certification coverage;
- ~1e-3 e: SZ3 and ZFP are similar;
- 1e-4 e: ZFP leads.

## 12. Claim wording hierarchy

Safe primary claims:

1. A pointwise error bound alone does not specify downstream Bader-charge fidelity.
2. Reusing the original Bader partition suppresses domain migration and severely understates re-derived error.
3. At comparable measured L-infinity error and among A.1-resolvable systems, codec identity remains associated with an approximately twofold difference in re-derived Bader error.
4. Direct decomposition in the representative mechanism set and full-table reassignment attenuation independently implicate basin migration.
5. The QoI must be numerically resolvable under a validated stability probe before it can define a compression contract.
6. The preferred compressor depends on the scientific accuracy contract and certification coverage.

Claims to avoid:

- first-ever observation that pointwise bounds do not preserve QoIs;
- attributing the 6–12x same-nominal gap entirely to spatial structure;
- calling codec coefficients causal;
- claiming domain migration dominates every material in the corpus;
- calling Bader resolvability intrinsically/fundamentally unpredictable;
- declaring ZFP, SZ3 or SPERR universally best.
