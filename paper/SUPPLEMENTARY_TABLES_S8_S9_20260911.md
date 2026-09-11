# Supplementary Tables S8-S9

Updated 2026-09-11. Submission-facing extended operator-control tables. Machine-readable assets remain the numerical source of record.

## Supplementary Table S8 | Total-electron-count negative control

### S8a. Electron-count deviation and re-derived Bader error by codec

All 6,343 retained development reconstruction rows are included. The electron-count quantity is a global linear control, not a difficult target QoI.

| Codec | n rows | Median |Delta Ne| (e) | P95 (e) | P99 (e) | Maximum (e) | Median re-derived Bader error (e) |
|---|---:|---:|---:|---:|---:|---:|
| All codecs | 6,343 | 9.38e-5 | 6.43e-2 | 2.75e-1 | 3.98 | 4.00e-3 |
| SPERR | 1,956 | 3.27e-5 | 8.29e-3 | 2.96e-2 | 1.46e-1 | 5.63e-3 |
| SZ3 | 1,937 | 2.43e-3 | 2.08e-1 | 5.46e-1 | 3.98 | 5.71e-3 |
| ZFP | 2,450 | 2.68e-5 | 9.86e-3 | 2.50e-2 | 9.52e-2 | 2.45e-3 |

**Source:** `analysis/electron_count_qoi/summary_by_codec.csv`.

### S8b. Decoupling of global electron conservation from local Bader fidelity

Using the deliberately strict global-control condition `|Delta Ne| < 1e-4 e`, **3,205** reconstruction rows have both preserved total electron count and a finite re-derived Bader result. Among these, **1,383** have a re-derived Bader error `>= 1e-3 e`, corresponding to **43.15%**.

| Condition | Rows |
|---|---:|
| Finite re-derived Bader result and `|Delta Ne| < 1e-4 e` | **3,205** |
| Of these, re-derived Bader error `>= 1e-3 e` | **1,383** |
| Conditional fraction | **43.15%** |

This negative control supports only the statement that **global electron-number conservation is not a sufficient certificate of atom-resolved Bader fidelity**. It does not imply that total electron count itself is unstable or difficult to preserve.

### S8c. Log-scale correlations

| Codec | n | Pearson: log electron-count error vs log realized Linf | Pearson: log electron-count error vs log Bader error |
|---|---:|---:|---:|
| All codecs | 6,343 | 0.866 | 0.777 |
| SPERR | 1,956 | 0.936 | 0.807 |
| SZ3 | 1,937 | 0.955 | 0.851 |
| ZFP | 2,450 | 0.927 | 0.811 |

**Source:** `analysis/electron_count_qoi/correlations.csv`. Tolerance-resolved values remain in `analysis/electron_count_qoi/summary_by_tolerance.csv`.

---

## Supplementary Table S9 | Hartree-potential control on the frozen development reconstruction corpus

The periodic Hartree potential is used as a linear nonlocal comparator. The full expansion regenerated all 6,343 frozen development rows. The formal reproduction gate retained **6,270 rows**; the 73 excluded rows are infrastructure-level SZ3 byte-stream mismatches, not reconstruction-field mismatches or codec-bound failures.

### S9a. Pooled log-log response by codec and system type

`Hartree slope` is the pooled exponent in `Hartree error proportional to realized Linf^alpha`. Bader statistics are shown on the same gate-passing rows for comparison.

| Codec | Stratum | n rows | Hartree slope | Hartree R2 | Hartree Pearson | Bader slope | Bader R2 | Bader Pearson |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ZFP | Bulk | 1,839 | 1.00 | 0.930 | 0.964 | 0.67 | 0.685 | 0.828 |
| ZFP | Slab | 611 | 0.91 | 0.852 | 0.923 | 0.57 | 0.689 | 0.830 |
| SZ3 | Bulk | 1,403 | 1.12 | 0.936 | 0.968 | 0.60 | 0.760 | 0.872 |
| SZ3 | Slab | 461 | 0.94 | 0.925 | 0.962 | 0.53 | 0.743 | 0.862 |
| SPERR | Bulk | 1,530 | 0.97 | 0.936 | 0.967 | 0.58 | 0.755 | 0.869 |
| SPERR | Slab | 426 | 0.99 | 0.894 | 0.945 | 0.64 | 0.773 | 0.879 |
| All codecs | Bulk | 4,772 | 1.04 | 0.877 | 0.937 | — | — | — |
| All codecs | Slab | 1,498 | 1.00 | 0.709 | 0.842 | — | — | — |
| All codecs | All | **6,270** | **1.02** | **0.792** | **0.890** | **0.62** | **0.714** | **0.845** |

**Sources:** `analysis/hartree_potential_expansion/group_summary.csv`; `analysis/hartree_potential_expansion/RESULTS_DETAIL.md`.

### S9b. Material-level ladder smoothness

Material-level statistics use 678 material-codec pairs with at least five reproduction-gate-passing rungs.

| Codec | Material-codec pairs | Hartree strictly monotone | Bader strictly monotone | Hartree median R2 | Bader median R2 |
|---|---:|---:|---:|---:|---:|
| ZFP | 241 | 85.1% | 19.5% | 0.997 | 0.892 |
| SZ3 | 219 | 85.8% | 42.0% | 0.994 | 0.947 |
| SPERR | 218 | 95.4% | 37.2% | 0.996 | 0.936 |
| All | **678** | **88.6%** | **32.4%** | **0.996** | **0.930** |

The strict-monotonicity contrast has an important slab caveat. Hartree remains highly smooth by R2, but small local Hartree decreases make strict monotonicity less frequent on slabs than in bulk.

| Codec | Hartree monotone, bulk | Hartree monotone, slab | Bader monotone, bulk | Bader monotone, slab |
|---|---:|---:|---:|---:|
| ZFP | 96.6% | 52.4% | 17.4% | 25.4% |
| SZ3 | 98.8% | 47.3% | 42.7% | 40.0% |
| SPERR | 98.8% | 84.3% | 31.1% | 56.9% |

Therefore the manuscript/SI should characterize Hartree as a smoother linear-nonlocal response using the combined evidence from slope, R2, elasticity and jump size, not as perfectly monotone in every slab ladder.

### S9c. Matched-Hartree dispersion of Bader error

Using 0.5-decade Hartree-error bins with at least 10 rows, **55.4% of gate-passing rows** fall into bins in which the Bader-error `P90/P10 >= 10`. The condition occurs in all three codecs and both system strata.

| Codec | Stratum | Eligible Hartree bins | Bins with Bader P90/P10 >= 10 | Rows in such bins / rows in displayed bins | Median Bader P90/P10 | Maximum Bader P90/P10 |
|---|---|---:|---:|---:|---:|---:|
| ZFP | Bulk | 14 | 9 | 1,131 / 1,836 | 17.8 | 61,567 |
| ZFP | Slab | 12 | 10 | 511 / 599 | 15.1 | 445 |
| SZ3 | Bulk | 14 | 7 | 626 / 1,397 | 8.9 | 2,439 |
| SZ3 | Slab | 10 | 3 | 146 / 450 | 7.4 | 12.3 |
| SPERR | Bulk | 13 | 6 | 723 / 1,527 | 9.5 | 22.4 |
| SPERR | Slab | 10 | 7 | 315 / 420 | 12.0 | 22.1 |

**Sources:** `analysis/hartree_potential_expansion/material_smoothness.csv`; `analysis/hartree_potential_expansion/matched_error_dispersion.csv`; `analysis/hartree_potential_expansion/RESULTS_DETAIL.md`.

### Reproduction-gate footnote

ZFP: 2,450/2,450 rows pass. SPERR: 1,956/1,956 pass. SZ3: 1,864/1,937 pass. In all 73 SZ3 gate exclusions, reproduced realized Linf agrees with the frozen value to better than approximately `2e-5` relative, but the compressed byte count differs across platforms. The median byte difference is approximately one byte, although rare larger differences occur. Per the frozen rule these rows are excluded from Hartree statistics. This is an infrastructure/reproducibility issue and must not be described as a numerical failure of the reconstruction.

## Interpretation boundary

Tables S8-S9 expand the operator-control evidence supporting main-text Figure 2. They motivate an operator-aware downstream measurement contract, but **they are not the central novelty claim**. The central benchmark-validity result remains the stability-qualified binary-to-three-state reclassification in Figure 3 / Supplementary Figure S7.
