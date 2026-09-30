# WP-E — A certifying writer on the frozen development ladders

No new computation: 254 development materials, 6,343 frozen reconstruction rows; a policy pays 6 Bader solves
for QSQ (reference + 5 probes) and 1 solve per rung it evaluates. Certificates were re-checked mechanically:
every returned row is certified at its τ.

## Adopted policy

**BISECT** — fewest mean solves among multi-codec policies meeting >= 0.98 of oracle archive compression and <= 2% misses at 1e-3 e.

## Multi-codec policies

| τ (e) | policy | eligible | archive CR | oracle archive CR | fraction of oracle [95% CI] | misses | per-material ratio median / P05 | solves per eligible material |
|---:|---|---:|---:|---:|---|---:|---|---:|
| 0.0001 | EXHAUSTIVE | 46 | 8.47 | 8.47 | 1.0000 [1.0000, 1.0000] | 0 / 46 | 1.000 / 1.000 | 38.5 |
| 0.0001 | SCAN | 46 | 8.47 | 8.47 | 1.0000 [1.0000, 1.0000] | 0 / 46 | 1.000 / 1.000 | 34.3 |
| 0.0001 | BISECT | 46 | 8.45 | 8.47 | 0.9976 [0.9918, 1.0000] | 0 / 46 | 1.000 / 1.000 | 16.7 |
| 0.001 | EXHAUSTIVE | 143 | 15.13 | 15.13 | 1.0000 [1.0000, 1.0000] | 0 / 143 | 1.000 / 1.000 | 37.0 |
| 0.001 | SCAN | 143 | 15.13 | 15.13 | 1.0000 [1.0000, 1.0000] | 0 / 143 | 1.000 / 1.000 | 26.8 |
| 0.001 | BISECT | 143 | 14.90 | 15.13 | 0.9848 [0.9695, 0.9959] | 0 / 143 | 1.000 / 0.686 | 16.7 |
| 0.01 | EXHAUSTIVE | 229 | 24.79 | 24.79 | 1.0000 [1.0000, 1.0000] | 0 / 227 | 1.000 / 1.000 | 32.2 |
| 0.01 | SCAN | 229 | 24.79 | 24.79 | 1.0000 [1.0000, 1.0000] | 0 / 227 | 1.000 / 1.000 | 17.3 |
| 0.01 | BISECT | 229 | 24.55 | 24.79 | 0.9901 [0.9698, 0.9982] | 0 / 227 | 1.000 / 1.000 | 15.9 |

## Single-codec policies (no codec search)

| τ (e) | policy | archive CR | fraction of oracle | misses | solves per eligible material |
|---:|---|---:|---:|---:|---:|
| 0.0001 | BISECT-SPERR | 2.55 | 0.3006 | 7 | 9.5 |
| 0.0001 | BISECT-SZ3 | 3.24 | 0.3831 | 8 | 9.4 |
| 0.0001 | BISECT-ZFP | 8.08 | 0.9535 | 0 | 9.8 |
| 0.0001 | SCAN-SPERR | 2.55 | 0.3006 | 7 | 15.7 |
| 0.0001 | SCAN-SZ3 | 3.25 | 0.3836 | 8 | 15.6 |
| 0.0001 | SCAN-ZFP | 8.08 | 0.9535 | 0 | 15.1 |
| 0.001 | BISECT-SPERR | 4.10 | 0.2711 | 6 | 9.5 |
| 0.001 | BISECT-SZ3 | 5.31 | 0.3508 | 7 | 9.5 |
| 0.001 | BISECT-ZFP | 12.65 | 0.8359 | 1 | 9.6 |
| 0.001 | SCAN-SPERR | 4.14 | 0.2739 | 6 | 12.9 |
| 0.001 | SCAN-SZ3 | 5.34 | 0.3527 | 7 | 13.3 |
| 0.001 | SCAN-ZFP | 12.72 | 0.8405 | 1 | 12.7 |
| 0.01 | BISECT-SPERR | 3.99 | 0.1611 | 19 | 9.2 |
| 0.01 | BISECT-SZ3 | 5.07 | 0.2043 | 23 | 9.1 |
| 0.01 | BISECT-ZFP | 18.08 | 0.7291 | 2 | 9.6 |
| 0.01 | SCAN-SPERR | 4.00 | 0.1612 | 19 | 10.0 |
| 0.01 | SCAN-SZ3 | 5.21 | 0.2103 | 20 | 9.8 |
| 0.01 | SCAN-ZFP | 18.13 | 0.7313 | 2 | 9.5 |

## Reading

At τ = 1e-3 e the writer (QSQ, then per-codec bisection, best of three codecs) keeps 98.5% of the oracle archive compression (14.90 of 15.13) with no eligible material left uncompressed, at 16.7 instead of 37.0 Bader solves per eligible material (55% fewer). Codec search matters more than ladder search: the best single codec keeps at most 84.0% of the oracle at the same τ.

Files: `policy_material.csv`, `policy_summary.csv`, `adopted_policy.json`, `fig_writer.{png,svg,pdf}`, `provenance.json`.
