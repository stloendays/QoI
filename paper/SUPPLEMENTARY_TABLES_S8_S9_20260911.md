# Supplementary Tables S8–S9

Generated 2026-09-11 directly from frozen operator-control outputs. These tables support Supplementary Figure S3 and the main-text operator comparison. No values are transcribed from historical prose summaries.

## Supplementary Table S8 | Electron-count preservation does not certify Bader-charge fidelity

### S8a. Pooled negative-control matrix across all codecs

| Electron-count threshold | Bader threshold | Rows preserving electron count | Rows failing Bader threshold despite preservation | Fraction |
|---:|---:|---:|---:|---:|
| 1e-06 e | 1e-04 e | 1,108 | 652 | 58.84% |
| 1e-06 e | 1e-03 e | 1,108 | 108 | 9.75% |
| 1e-06 e | 1e-02 e | 1,108 | 10 | 0.90% |
| 1e-05 e | 1e-04 e | 1,993 | 1,486 | 74.56% |
| 1e-05 e | 1e-03 e | 1,993 | 482 | 24.18% |
| 1e-05 e | 1e-02 e | 1,993 | 73 | 3.66% |
| 1e-04 e | 1e-04 e | 3,205 | 2,691 | 83.96% |
| 1e-04 e | 1e-03 e | 3,205 | 1,383 | 43.15% |
| 1e-04 e | 1e-02 e | 3,205 | 306 | 9.55% |
| 1e-03 e | 1e-04 e | 4,380 | 3,866 | 88.26% |
| 1e-03 e | 1e-03 e | 4,380 | 2,477 | 56.55% |
| 1e-03 e | 1e-02 e | 4,380 | 801 | 18.29% |

### S8b. Codec-resolved headline control at |ΔNe| < 1e-4 e and Bader error >= 1e-3 e

| Codec | Rows preserving electron count | Rows still failing Bader threshold | Fraction |
|---|---:|---:|---:|
| ZFP | 1,509 | 607 | 40.23% |
| SZ3 | 466 | 79 | 16.95% |
| SPERR | 1,230 | 697 | 56.67% |
| **All codecs** | **3,205** | **1,383** | **43.15%** |

**Interpretation.** Global electron conservation is a negative control, not a sufficient certificate for atom-resolved Bader fidelity. The main-text 3,205 / 1,383 = 43.15% result is the pooled row highlighted above.

**Source:** `analysis/electron_count_qoi/electron_bader_decoupling.csv`.

---

## Supplementary Table S9 | Hartree-potential response is smoother than re-derived Bader response on the same reconstructions

### S9a. Pooled codec-level scaling on the 6,270 reproduction-gate-passing rows

| Codec | Gate-passing rows | Hartree slope | Hartree R² | Bader slope | Bader R² | Median Hartree relative RMSE | Median Bader error (e) |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZFP | 2,450 | 0.968 | 0.863 | 0.646 | 0.684 | 9.405e-07 | 2.453e-03 |
| SZ3 | 1,864 | 1.069 | 0.910 | 0.584 | 0.757 | 2.591e-05 | 5.890e-03 |
| SPERR | 1,956 | 0.988 | 0.786 | 0.587 | 0.750 | 2.643e-06 | 5.631e-03 |

The all-codec pooled Hartree log–log exponent reported by the frozen analysis is **1.02** on all 6,270 gate-passing rows; the per-codec values above show the same near-first-order pattern without collapsing codec-specific prefactors.

### S9b. Material-level smoothness for 678 material–codec pairs with at least five gate-passing rows

| Codec | Pairs | Hartree monotone | Bader monotone | Median Hartree R² | Median Bader R² | Median Hartree slope | Median Bader slope |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZFP | 241 | 85.1% | 19.5% | 0.997 | 0.892 | 1.05 | 0.58 |
| SZ3 | 219 | 85.8% | 42.0% | 0.994 | 0.947 | 1.17 | 0.60 |
| SPERR | 218 | 95.4% | 37.2% | 0.996 | 0.936 | 1.01 | 0.59 |
| **All** | **678** | **88.6%** | **32.4%** | **0.996** | **0.928** | — | — |

### S9c. Rung-level irregularity and matched-Hartree dispersion

| Diagnostic | Hartree | Bader |
|---|---:|---:|
| Local log–log elasticity range | -2.0 to +4.4 | -9.3 to +14.1 |
| Largest consecutive Bader-error jump | — | 22,296× |
| Gate-passing rows in matched-Hartree bins with Bader P90/P10 >= 10 | — | 3,452/6,229 = 55.4% |

**Interpretation.** The Hartree control is close to first-order at pooled and material levels, whereas the re-derived Bader response shows substantially more rung-level non-monotonicity and dispersion. The slab monotonicity caveat remains: strict Hartree monotonicity is weaker on slabs even though material-level Hartree R² remains high. The result should therefore be described as a smoother response, not as universal monotonicity.

**Sources:** `analysis/hartree_potential_expansion/group_summary.csv`; `analysis/hartree_potential_expansion/material_smoothness.csv`; `analysis/hartree_potential_expansion/matched_error_dispersion.csv`; `analysis/hartree_potential_expansion/RESULTS_DETAIL.md`.

## Submission boundary

Tables S8–S9 are operator-control evidence. They motivate why downstream analyses must be evaluated explicitly, but they do not carry the central novelty claim. The central benchmark-validity result remains the stability-qualified binary-to-three-state reclassification in Figure 3 / Supplementary Table S4.
