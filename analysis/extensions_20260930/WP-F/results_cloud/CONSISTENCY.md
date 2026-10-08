# WP-F platform consistency: laptop vs GitHub-hosted ubuntu-24.04

Rule: `DEVIATIONS.md` 7 (definitions in 8). Objects: mp-2488566, mp-2285510, mp-2050393, mp-2367698, mp-2682232. Laptop checkpoints: `results_laptop/checkpoints/` (as recorded); cloud checkpoints: `results_cloud/consistency/checkpoints/`. Every compared field: `consistency/consistency_fields.csv`.

**Verdict: DISAGREE** — 1405 of 1409 agreement checks pass.

## Per object

| object | stratum | laptop / cloud status | checks | failed | max abs Δ floor (e) | max abs Δ probe (e) | max abs Δ rung Bader error (e) | max rel Δ rung bytes | wall laptop / cloud (min) |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| mp-2488566 | D03 | SUCCESS / SUCCESS | 281 | 2 | 0 | 0 | 0.0002998648 | 0 | 10.9 / 22.5 |
| mp-2285510 | D06 | SUCCESS / SUCCESS | 281 | 0 | 0 | 0 | 0 | 0 | 44.8 / 22.0 |
| mp-2050393 | D03 | SUCCESS / SUCCESS | 282 | 1 | 0 | 0 | 0.0017768586 | 0 | 3.0 / 3.4 |
| mp-2367698 | D07 | SUCCESS / SUCCESS | 282 | 0 | 0 | 0 | 0 | 0 | 58.6 / 92.7 |
| mp-2682232 | D05 | SUCCESS / SUCCESS | 283 | 1 | 0 | 0 | 3.61689e-05 | 0 | 41.8 / 39.7 |

## Exact-match fields

| field | checks | identical |
|---|---:|---:|
| eligibility at 1e-4, 1e-3, 1e-2 e | 15 | 15 |
| evaluated rung set | 5 | 5 |
| rung status | 190 | 190 |
| rung certifiable_error flag | 190 | 190 |
| rung certified at each tau | 570 | 570 |
| writer choice (codec, rung) at each tau | 15 | 15 |

## Largest differences

| field | criterion | values compared | largest difference | where | laptop | cloud |
|---|---|---:|---:|---|---|---|
| floor f_m (e) | <= 1e-6 e | 5 | 0 | mp-2488566 floor_e | 0.0004710537 | 0.0004710537 |
| probe response (e) | <= 1e-6 e | 25 | 0 | mp-2488566 probe_response_e[seed=1] | 0.0004647752 | 0.0004647752 |
| rung Bader error (e) | <= 1e-6 e | 190 | 0.0017768586 | mp-2050393 rung[SPERR 0.03] bader_error_e | 0.4231005524 | 0.4213236938 |
| rung compressed bytes (relative) | <= 0.1 % | 185 | 0 | mp-2488566 rung[SPERR 1e-07] compressed_bytes | 1196660 | 1196660 |
| writer-choice compressed bytes (relative) | <= 0.1 % | 9 | 0 | mp-2488566 writer_choice@0.001 compressed_bytes | 206911 | 206911 |
| epsilon (field units) | informational | 5 | 0 | mp-2488566 epsilon | 6.091406249e-05 | 6.091406249e-05 |
| value range ptp | informational | 5 | 0 | mp-2488566 value_ptp | 1412.15202 | 1412.15202 |
| lossless bytes (relative) | informational | 5 | 0 | mp-2488566 lossless_bytes | 4358080 | 4358080 |
| rung realized L-inf | informational | 185 | 0 | mp-2488566 rung[SPERR 1e-07] realized_Linf | 0.0001412120645 | 0.0001412120645 |
| probe basin reassignments (voxels) | informational | 25 | 0 | mp-2488566 probe_n_reassigned[seed=1] | 228 | 228 |
| rung basin reassignments (voxels) | informational | 185 | 48 | mp-2488566 rung[SPERR 0.03] n_reassigned | 161916 | 161964 |

## Failed checks

| object | field | laptop | cloud | difference | criterion |
|---|---|---|---|---:|---|
| mp-2488566 | rung[SPERR 0.003] bader_error_e | 0.0669752537 | 0.0666753889 | 0.0002998648 | <= 1e-6 e |
| mp-2488566 | rung[SPERR 0.03] bader_error_e | 0.9304831415 | 0.9305542936 | 7.11521e-05 | <= 1e-6 e |
| mp-2050393 | rung[SPERR 0.03] bader_error_e | 0.4231005524 | 0.4213236938 | 0.0017768586 | <= 1e-6 e |
| mp-2682232 | rung[ZFP 0.1] bader_error_e | 0.7973621145 | 0.7973982834 | 3.61689e-05 | <= 1e-6 e |

Informational fields that differ (not part of the rule): none.
