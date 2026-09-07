# Error-geometry control v0.1 — preregistration

Date frozen: 2026-09-07

## Purpose

Figure 6 currently establishes that matching **realized L-infinity** removes a large nominal-tolerance confounder but leaves a residual codec-dependent Bader-error difference. This follow-up asks a stricter question before using the phrase *error geometry*: **does the residual persist after simultaneously controlling realized L-infinity and RMSE within material?**

This is a development-corpus mechanistic sensitivity analysis. It does **not** modify Protocol A.1, codec settings, tolerance ladders, eligibility rules, early stopping, failure semantics, or any external confirmatory cohort.

## Frozen input

- `benchmark/master_benchmark_full.csv`
- Git blob SHA at preregistration: `633c7b2ee1b9b800382a5d0d9cfbdc9e1dc793b7`
- Development corpus only (`dev_bulk` and `dev_slab`).
- Retain rows only when `bound_respected == True` and realized L-infinity, RMSE, resolved Bader error, and compression ratio are finite and positive.

No external-rate-fidelity output is used.

## Codec contrasts

Orient every contrast as A / B:

1. ZFP / SZ3
2. ZFP / SPERR
3. SZ3 / SPERR

For Bader-error ratios, values below 1 mean codec A has lower resolved Bader error.

## Matching

Matching is performed **within material** and **without replacement**.

For every row pair from codecs A and B define

- `d_inf = |log10(realized_Linf_A) - log10(realized_Linf_B)|`
- `d_rmse = |log10(rmse_A) - log10(rmse_B)|`

A pair is admissible only if both distances are at or below the same caliper.

Primary caliper: **0.10 dex** on both realized L-infinity and RMSE.

Sensitivity calipers: **0.05, 0.20, 0.30 dex** on both axes.

Within a material, admissible pairs are sorted by normalized Euclidean distance

`sqrt((d_inf/caliper)^2 + (d_rmse/caliper)^2)`

with deterministic row-key tie breaking, then greedily selected without replacement. This algorithm is frozen before outcomes are computed.

## Material-level estimands

For each material with at least one matched pair:

- resolved-Bader error effect = geometric median of pairwise `error_A / error_B`;
- compression-ratio effect = geometric median of pairwise `CR_A / CR_B`;
- realized-L-infinity balance = geometric median of pairwise `Linf_A / Linf_B`;
- RMSE balance = geometric median of pairwise `RMSE_A / RMSE_B`.

For certification at `tau = 0.01 e`, use only matched row pairs where **both rows are Protocol-A.1 eligible at 0.01 e**. The material-level effect is the mean of `certified_A - certified_B` over those jointly eligible matched pairs, expressed in percentage points.

## Population summaries and uncertainty

- Ratio-type point estimates: geometric median across material-level effects.
- Certification difference: arithmetic mean across material-level effects.
- 95% CIs: percentile bootstrap over materials, 5,000 resamples.
- Bootstrap seeds are deterministic SHA256-derived integers with master seed label `20260907`.

Materials, not rows, are the resampling unit.

## Primary decision rule

The stricter amplitude-control result is considered **supported** if, at the 0.10-dex dual caliper:

- the upper 95% CI for ZFP/SZ3 resolved-Bader error ratio is below 1, and
- the upper 95% CI for ZFP/SPERR resolved-Bader error ratio is below 1.

If this criterion is met, the allowed manuscript claim is:

> The residual ZFP chemical-fidelity advantage is not explained by realized L-infinity or RMSE alone.

The result **must not by itself be called causal proof of spatial error geometry**. A separate residual-permutation intervention is required for that stronger claim.

## Failure / coverage reporting

Report, for every contrast and caliper:

- matched materials;
- matched row pairs;
- jointly A.1-eligible certification pairs;
- L-infinity and RMSE balance after matching;
- all point estimates and CIs.

No minimum-coverage threshold will be invented after seeing outcomes. Sparse sensitivity strata will be reported as sparse rather than discarded.
