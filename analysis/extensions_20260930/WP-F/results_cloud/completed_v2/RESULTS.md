# WP-F — What qualification buys: the Materials Project charge-density archive

Frame: 415,289 objects, 8.4976 TB (MP json.gz), without the 186 frozen development objects. Stratified sample n = 300; 293 succeeded, 7 failed (failed objects keep their current json.gz size: no saving credited).

## Primary endpoint

R(1e-3 e) = 4.367 [3.637, 5.458] against the current json.gz archive — **storage saving (lower 95% bound 3.64 > 1.5)** — an estimated saving of 6.55 TB [6.16, 6.94].

## All tolerances

| τ (e) | R vs json.gz [95% CI] | saving (TB) | R vs float64 | R vs lossless float64 | non-evaluable (objects) [95% CI] | non-evaluable (bytes) | certified ZFP / SZ3 / SPERR (objects) |
|---:|---|---:|---:|---:|---|---:|---|
| 0.0001 | 2.362 [2.192, 2.577] | 4.90 | 1.45 | 1.27 [1.19, 1.38] | 74.0% [69.0, 78.7] | 72.2% | 12.6% / 1.7% / 9.2% |
| 0.001 | 4.367 [3.637, 5.458] | 6.55 | 3.04 | 2.66 [2.21, 3.27] | 35.9% [30.4, 41.6] | 32.8% | 22.4% / 14.6% / 24.5% |
| 0.01 | 8.989 [6.453, 13.418] | 7.55 | 8.97 | 7.87 [5.61, 12.10] | 11.7% [8.2, 15.5] | 11.0% | 5.3% / 48.8% / 31.6% |

Format gain alone (json.gz → lossless float64 + zlib, no scientific approximation): 2.00×. R vs lossless isolates what certified lossy compression adds on top of it.

## Prospective check of the WP-E writer (D01–D09 full ladders)

| τ (e) | eligible objects with a certifiable rung | misses | archive fraction of oracle |
|---:|---:|---:|---:|
| 0.0001 | 64 | 0 | 0.9817 |
| 0.001 | 166 | 0 | 0.9530 |
| 0.01 | 232 | 0 | 0.9310 |

## Strata

| stratum   |   N_frame |   n_sample |   n_success |   n_failed |   median_json_MB |   eligible_0.0001 |   R_vs_json_0.0001 |   eligible_0.001 |   R_vs_json_0.001 |   eligible_0.01 |   R_vs_json_0.01 |
|:----------|----------:|-----------:|------------:|-----------:|-----------------:|------------------:|-------------------:|-----------------:|------------------:|----------------:|-----------------:|
| D01       |     41527 |         30 |          30 |          0 |             3.14 |                11 |               3.35 |               20 |              6.89 |              27 |            19.2  |
| D02       |     41531 |         30 |          30 |          0 |             5.41 |                 2 |               2.49 |               14 |              4.22 |              26 |            15    |
| D03       |     41529 |         30 |          30 |          0 |             8.01 |                 8 |               2.78 |               20 |              5.97 |              27 |            17.3  |
| D04       |     41529 |         30 |          30 |          0 |            10.2  |                 7 |               2.62 |               20 |              5.64 |              28 |            25.3  |
| D05       |     41528 |         30 |          30 |          0 |            12.9  |                10 |               2.8  |               24 |              8.48 |              27 |            18.3  |
| D06       |     41529 |         30 |          30 |          0 |            14.7  |                10 |               2.92 |               17 |              4.48 |              27 |            18.9  |
| D07       |     41529 |         30 |          30 |          0 |            19.3  |                 7 |               2.6  |               17 |              4.44 |              23 |             8.41 |
| D08       |     41529 |         30 |          30 |          0 |            25.1  |                 3 |               2.19 |               15 |              3.84 |              25 |            11.4  |
| D09       |     41529 |         30 |          24 |          6 |            34.6  |                 6 |               1.89 |               19 |              3.14 |              22 |             3.96 |
| D10a      |     33105 |         15 |          14 |          1 |            59.8  |                 2 |               2.08 |                8 |              3.39 |              12 |             7.24 |
| D10b      |      6741 |         10 |          10 |          0 |            87.6  |                 6 |               4.39 |               10 |             40.4  |              10 |           146    |
| D10c      |      1683 |          5 |           5 |          0 |           250    |                 1 |               2.46 |                4 |              9.02 |               5 |           266    |

## Failures

95 failure records in 77 objects (`failures.csv`).

Files: `objects.csv`, `rungs.csv`, `estimates.csv`, `strata_results.csv`, `writer_prospective.csv`, `failures.csv`, `fig_archive.{png,svg,pdf}`, `provenance.json`, `DEVIATIONS.md`.
