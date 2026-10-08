# WP-F — What qualification buys: the Materials Project charge-density archive

Frame: 415,289 objects, 8.4976 TB (MP json.gz), without the 186 frozen development objects. Stratified sample n = 300; 243 succeeded, 57 failed (failed objects keep their current json.gz size: no saving credited).

## Primary endpoint

R(1e-3 e) = 1.636 [1.580, 1.698] against the current json.gz archive — **storage saving (lower 95% bound 1.58 > 1.5)** — an estimated saving of 3.30 TB [3.12, 3.49].

## All tolerances

| τ (e) | R vs json.gz [95% CI] | saving (TB) | R vs float64 | R vs lossless float64 | non-evaluable (objects) [95% CI] | non-evaluable (bytes) | certified ZFP / SZ3 / SPERR (objects) |
|---:|---|---:|---:|---:|---|---:|---|
| 0.0001 | 1.434 [1.398, 1.477] | 2.57 | 1.53 | 1.27 [1.19, 1.37] | 61.0% [56.7, 65.0] | 37.5% | 11.0% / 1.0% / 8.0% |
| 0.001 | 1.636 [1.580, 1.698] | 3.30 | 2.82 | 2.35 [2.02, 2.79] | 31.3% [26.0, 36.3] | 19.9% | 18.0% / 11.3% / 20.3% |
| 0.01 | 1.836 [1.770, 1.916] | 3.87 | 8.06 | 6.70 [5.06, 9.63] | 10.0% [6.7, 13.3] | 6.8% | 5.3% / 39.0% / 26.7% |

Format gain alone (json.gz → lossless float64 + zlib, no scientific approximation): 2.05×. R vs lossless isolates what certified lossy compression adds on top of it.

## Prospective check of the WP-E writer (D01–D09 full ladders)

| τ (e) | eligible objects with a certifiable rung | misses | archive fraction of oracle |
|---:|---:|---:|---:|
| 0.0001 | 60 | 0 | 0.9806 |
| 0.001 | 149 | 0 | 0.9530 |
| 0.01 | 213 | 0 | 0.9502 |

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
| D09       |     41529 |         30 |           3 |         27 |            34.6  |                 2 |               1.07 |                2 |              1.07 |               3 |             1.09 |
| D10a      |     33105 |         15 |           0 |         15 |            59.8  |                 0 |               1    |                0 |              1    |               0 |             1    |
| D10b      |      6741 |         10 |           0 |         10 |            87.6  |                 0 |               1    |                0 |              1    |               0 |             1    |
| D10c      |      1683 |          5 |           0 |          5 |           250    |                 0 |               1    |                0 |              1    |               0 |             1    |

## Failures

135 failure records in 118 objects (`failures.csv`).

Files: `objects.csv`, `rungs.csv`, `estimates.csv`, `strata_results.csv`, `writer_prospective.csv`, `failures.csv`, `fig_archive.{png,svg,pdf}`, `provenance.json`, `DEVIATIONS.md`.
