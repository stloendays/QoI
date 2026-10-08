# WP-F — What qualification buys: the Materials Project charge-density archive

Frame: 415,289 objects, 8.4976 TB (MP json.gz), without the 186 frozen development objects. Stratified sample n = 300; 288 succeeded, 12 failed (failed objects keep their current json.gz size: no saving credited).

## Primary endpoint

R(1e-3 e) = 3.815 [3.203, 4.701] against the current json.gz archive — **storage saving (lower 95% bound 3.20 > 1.5)** — an estimated saving of 6.27 TB [5.84, 6.69].

## All tolerances

| τ (e) | R vs json.gz [95% CI] | saving (TB) | R vs float64 | R vs lossless float64 | non-evaluable (objects) [95% CI] | non-evaluable (bytes) | certified ZFP / SZ3 / SPERR (objects) |
|---:|---|---:|---:|---:|---|---:|---|
| 0.0001 | 2.245 [2.074, 2.464] | 4.71 | 1.45 | 1.27 [1.19, 1.38] | 72.5% [67.5, 77.3] | 69.3% | 12.6% / 1.7% / 9.0% |
| 0.001 | 3.815 [3.203, 4.701] | 6.27 | 2.97 | 2.61 [2.18, 3.22] | 35.6% [30.1, 41.3] | 32.3% | 21.8% / 14.1% / 24.3% |
| 0.01 | 6.880 [5.053, 10.180] | 7.26 | 8.88 | 7.79 [5.53, 12.22] | 11.4% [7.9, 15.1] | 10.5% | 5.3% / 47.6% / 31.4% |

Format gain alone (json.gz → lossless float64 + zlib, no scientific approximation): 2.00×. R vs lossless isolates what certified lossy compression adds on top of it.

## Prospective check of the WP-E writer (D01–D09 full ladders)

| τ (e) | eligible objects with a certifiable rung | misses | archive fraction of oracle |
|---:|---:|---:|---:|
| 0.0001 | 64 | 0 | 0.9817 |
| 0.001 | 164 | 0 | 0.9599 |
| 0.01 | 230 | 0 | 0.9299 |

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
| D09       |     41529 |         30 |          21 |          9 |            34.6  |                 6 |               1.72 |               17 |              2.51 |              20 |             2.99 |
| D10a      |     33105 |         15 |          13 |          2 |            59.8  |                 2 |               1.97 |                7 |              2.86 |              11 |             5.1  |
| D10b      |      6741 |         10 |           9 |          1 |            87.6  |                 5 |               3.15 |                9 |              8.56 |               9 |            10    |
| D10c      |      1683 |          5 |           5 |          0 |           250    |                 1 |               2.46 |                4 |              9.02 |               5 |           266    |

## Failures

97 failure records in 80 objects (`failures.csv`).

Files: `objects.csv`, `rungs.csv`, `estimates.csv`, `strata_results.csv`, `writer_prospective.csv`, `failures.csv`, `fig_archive.{png,svg,pdf}`, `provenance.json`, `DEVIATIONS.md`.
