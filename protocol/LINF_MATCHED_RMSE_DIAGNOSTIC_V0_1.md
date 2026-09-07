# L-infinity-matched RMSE balance diagnostic v0.1

Date frozen: 2026-09-07

## Question

The current Figure 6 matching analysis controls realized L-infinity within material. Before interpreting any residual codec effect as spatial error geometry, test whether those L-infinity-matched pairs are also balanced in a second scalar amplitude summary, RMSE.

This is a diagnostic on the frozen development master table. It does not modify Protocol A.1, codec settings, tolerance ladders, eligibility rules, early stopping, failure semantics, or the external confirmatory cohort.

## Frozen input

`benchmark/master_benchmark_full.csv`, Git blob `633c7b2ee1b9b800382a5d0d9cfbdc9e1dc793b7`.

Retain development rows (`dev_bulk`, `dev_slab`) with finite positive realized L-infinity, RMSE, resolved-Bader error and compression ratio, and `bound_respected == True`.

## Matching

Contrasts are oriented A/B:

1. ZFP / SZ3
2. ZFP / SPERR
3. SZ3 / SPERR

Within each material, match rows without replacement using only

`d_inf = |log10(realized_Linf_A) - log10(realized_Linf_B)|`.

A pair is admissible if `d_inf <= caliper`. Sort admissible pairs by `d_inf`, then by absolute log10 nominal-tolerance difference, then deterministic row keys, and greedily match without replacement.

Primary caliper: **0.10 dex**. Sensitivity calipers: **0.05, 0.20, 0.30 dex**.

## Material-level estimands

For each material with at least one pair, take the geometric median across its matched pairs of:

- resolved-Bader error A/B;
- RMSE A/B;
- realized-L-infinity A/B;
- compression ratio A/B;
- shape factor A/B, where `shape factor = RMSE / realized_Linf`.

## Population summaries

Ratio point estimates are geometric medians across materials. 95% percentile CIs use 5,000 bootstrap resamples over materials with deterministic SHA256-derived seeds and master label `20260907`.

## Diagnostic interpretation

- If the 95% CI for matched RMSE A/B excludes 1 at the primary 0.10-dex caliper, the L-infinity-only matched comparison remains measurably imbalanced in a scalar amplitude statistic and therefore cannot uniquely identify spatial error geometry.
- If matched RMSE is balanced but Bader error remains different, the result motivates (but still does not prove) a spatial/distributional mechanism.
- No outcome from this diagnostic may be used to alter the already-frozen dual-metric matching or residual-permutation protocols.
