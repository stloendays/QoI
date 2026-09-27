# Supplementary Tables S1–S17

The tables below report the reader-facing supplementary analyses for the current submission scope. Exact machine-readable files and implementation identifiers are mapped in the repository reader-facing provenance index.

## Supplementary Table S1 | Analysis cohorts and denominator conventions

| Analysis universe | Domain / stratum | Systems, n | Reconstruction rows | Primary use |
|---|---|---:|---:|---|
| Development benchmark | bulk | 186 | included in 6,343 total | codec benchmark, controls, reclassification, matching |
| Development benchmark | slab | 68 | included in 6,343 total | codec benchmark, controls, reclassification, matching |
| **Development benchmark total** | — | **254** | **6,343** | primary development analysis |
| External stability/descriptive set | bulk | 37 | included in 1,755 descriptive total | QSQ external stability/descriptive analysis |
| External stability/descriptive set | vacuum-containing 2D | 28 | included in 1,755 descriptive total | QSQ external stability/descriptive analysis |
| **External descriptive total** | — | **65** | **1,755** | external descriptive aggregate |
| **Combined stability universe** | development + external descriptive | **319** | not a codec-row denominator | QSQ stability-floor / eligibility summaries |
| **Primary external confirmatory cohort** | pre-specified confirmatory subset | **63** | **1,689 retained scientific rows** | untouched rate–fidelity confirmation |

**Caption.** The study uses several deliberately distinct analysis universes. The 254-system development benchmark underlies the 6,343-row compression table and the central binary-to-three-state reclassification. QoI Stability Qualification (QSQ) summaries use 319 systems, comprising the 254 development systems plus all 65 records in the external descriptive/stability set. The primary external rate–fidelity confirmation is a pre-specified 63-system cohort with 1,689 retained scientific rows. The 65-system external descriptive aggregate contains 1,755 rows. Denominators are therefore analysis-specific and are not interchangeable.

**Evidence provenance:** cohort metadata, QSQ eligibility summary, external manifest and confirmatory summary; exact repository paths are mapped in the reader-facing provenance index.

---

## Supplementary Table S2 | QSQ definition and order-preserving control

| Property | Order-preserving round-trip control | QSQ perturbation |
|---|---|---|
| Role | **Method-validation control** | **Active qualification procedure** |
| Stability perturbation | float64 → float32 → float64 round trip | additive uniform noise \(U(-\epsilon,+\epsilon)\) |
| Perturbation amplitude | implicit float32 round-trip amplitude | \(\epsilon\) equals that material's measured float32 \(L_\infty\) round-trip error |
| Seeds | deterministic; not applicable | five pre-specified seeds: 20260905, 1, 2, 3, 4 |
| Stability floor | one deterministic response | maximum Bader response across five seeds |
| Bader basins | BaderKit, on-grid, re-derived | unchanged |
| Scientific thresholds | \(10^{-4}\), \(10^{-3}\), \(10^{-2}\,e\) | unchanged |
| Non-evaluable rule | floor \(\ge\tau\) | unchanged |
| Non-evaluable semantics | neither pass nor failure | unchanged |
| Reason for replacement | round trip is order-preserving and unusually benign to on-grid watershed ordering | non-order-preserving perturbation can excite the relevant partition instability |
| Benchmark role | method-validation control only | defines eligibility and certification statistics |

**Calibration evidence supporting QSQ.** In the 18-material calibration panel, the order-preserving round-trip control created a median of 82 exact neighbouring ties and reassigned zero voxels in 9/18 systems. The QSQ perturbation created no exact ties and reassigned zero voxels in only 2/18 systems. Across five seeds, the material-wise log10 floor span had a median of 0.47 decades and reached 2.4 decades. Over the ×0.1 to ×10 amplitude sweep, the floor changed by a median of 0.76 decades (P10 0.00; P90 2.02).

**Evidence provenance:** QSQ method record, order-preserving control record and probe-calibration panel.

---

## Supplementary Table S3 | QSQ eligibility by threshold and stratum

| Bader tolerance, \(\tau\) | Stratum | n | Eligible | Non-evaluable | Non-evaluable fraction | QSQ floor median (e) | QSQ floor P90 (e) | QSQ floor max (e) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1e-4 | overall | 319 | 64 | 255 | **79.94%** | 6.525e-4 | 9.378e-3 | 2.913 |
| 1e-4 | development bulk | 186 | 42 | 144 | 77.42% | 6.729e-4 | 8.302e-3 | 2.913 |
| 1e-4 | development slab | 68 | 4 | 64 | 94.12% | 8.014e-4 | 9.929e-3 | 2.275e-2 |
| 1e-4 | external bulk | 37 | 10 | 27 | 72.97% | 4.953e-4 | 3.708e-2 | 2.146 |
| 1e-4 | external vacuum-containing 2D | 28 | 8 | 20 | 71.43% | 1.845e-4 | 1.462e-3 | 3.979e-3 |
| 1e-3 | overall | 319 | 187 | 132 | **41.38%** | 6.525e-4 | 9.378e-3 | 2.913 |
| 1e-3 | development bulk | 186 | 103 | 83 | 44.62% | 6.729e-4 | 8.302e-3 | 2.913 |
| 1e-3 | development slab | 68 | 40 | 28 | 41.18% | 8.014e-4 | 9.929e-3 | 2.275e-2 |
| 1e-3 | external bulk | 37 | 22 | 15 | 40.54% | 4.953e-4 | 3.708e-2 | 2.146 |
| 1e-3 | external vacuum-containing 2D | 28 | 22 | 6 | 21.43% | 1.845e-4 | 1.462e-3 | 3.979e-3 |
| 1e-2 | overall | 319 | 288 | 31 | **9.72%** | 6.525e-4 | 9.378e-3 | 2.913 |
| 1e-2 | development bulk | 186 | 168 | 18 | 9.68% | 6.729e-4 | 8.302e-3 | 2.913 |
| 1e-2 | development slab | 68 | 61 | 7 | 10.29% | 8.014e-4 | 9.929e-3 | 2.275e-2 |
| 1e-2 | external bulk | 37 | 31 | 6 | 16.22% | 4.953e-4 | 3.708e-2 | 2.146 |
| 1e-2 | external vacuum-containing 2D | 28 | 28 | 0 | 0.00% | 1.845e-4 | 1.462e-3 | 3.979e-3 |

**Caption.** QSQ determines whether the uncompressed Bader analysis is numerically identifiable at the requested tolerance before codec scoring. The non-evaluable fraction rises sharply at stricter tolerances. The development slab versus bulk contrast is not stable across thresholds and does not reproduce as a universal external structural-class effect; numerical eligibility is therefore measured per material rather than inferred from coarse system type.

**Evidence provenance:** QSQ eligibility summary.

---

## Supplementary Table S4 | Codec-resolved binary-to-three-state reclassification in the 254-system development cohort

| \(\tau\) | Codec | Eligible | Non-evaluable | Naive pass | Naive fail | Qualified pass | Genuine eligible fail | Non-evaluable naive pass | Naive fail → non-evaluable | Fraction of naive failures reclassified |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1e-4 | SPERR | 46 | 208 | 61 | 193 | 39 | 7 | 22 | 186 | **96.37%** |
| 1e-4 | SZ3 | 46 | 208 | 49 | 205 | 38 | 8 | 11 | 197 | **96.10%** |
| 1e-4 | ZFP | 46 | 208 | 119 | 135 | 46 | 0 | 73 | 135 | **100.00%** |
| 1e-3 | SPERR | 143 | 111 | 144 | 110 | 137 | 6 | 7 | 104 | **94.55%** |
| 1e-3 | SZ3 | 143 | 111 | 140 | 114 | 136 | 7 | 4 | 107 | **93.86%** |
| 1e-3 | ZFP | 143 | 111 | 168 | 86 | 142 | 1 | 26 | 85 | **98.84%** |
| 1e-2 | SPERR | 229 | 25 | 212 | 42 | 208 | 21 | 4 | 21 | 50.00% |
| 1e-2 | SZ3 | 229 | 25 | 209 | 45 | 207 | 22 | 2 | 23 | 51.11% |
| 1e-2 | ZFP | 229 | 25 | 233 | 21 | 225 | 4 | 8 | 17 | 80.95% |

**Caption.** Each row summarizes 254 material–codec decisions at one Bader tolerance. The same material-level eligibility denominator applies to all three codecs because eligibility is measured on the uncompressed reference analysis. At \(10^{-4}\) and \(10^{-3}\,e\), more than 93% of naive failures for every codec are reclassified as non-evaluable rather than genuine eligible failures. The presence of non-evaluable naive passes, particularly 73 ZFP cases at \(10^{-4}\,e\), shows that QSQ does not merely remove unfavorable codec outcomes; it invalidates both success and failure labels when the reference QoI is not independently resolvable.

**Evidence provenance:** codec-resolved reclassification summary.

---

## Supplementary Table S5 | Sensitivity to omission of eligibility and inflation of the Bader threshold

### S5a. Naive no-exclusion diagnostic

The table applies the requested Bader tolerance directly to all 254 development materials without QSQ eligibility qualification. `n certified` therefore means a naive binary pass and must not be interpreted as a stability-qualified scientific certification.

| Bader threshold | Codec | n | Naive certified, n | Naive certified (%) | Median best ratio (x) | P10 (x) | P90 (x) |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1e-4 e | SPERR | 254 | 61 | 24.0 | 4.19 | 3.81 | 13.13 |
| 1e-4 e | SZ3 | 254 | 49 | 19.3 | 6.95 | 5.10 | 9.86 |
| 1e-4 e | ZFP | 254 | 119 | 46.9 | 7.55 | 5.74 | 10.86 |
| 1e-3 e | SPERR | 254 | 144 | 56.7 | 5.88 | 4.55 | 29.05 |
| 1e-3 e | SZ3 | 254 | 140 | 55.1 | 13.23 | 8.21 | 20.64 |
| 1e-3 e | ZFP | 254 | 168 | 66.1 | 13.59 | 9.69 | 21.24 |
| 1e-2 e | SPERR | 254 | 212 | 83.5 | 10.32 | 7.13 | 103.25 |
| 1e-2 e | SZ3 | 254 | 209 | 82.3 | 57.65 | 25.88 | 109.56 |
| 1e-2 e | ZFP | 254 | 233 | 91.7 | 31.57 | 19.73 | 52.02 |

The corresponding pooled benchmark-validity audit is reported in main-text Figure 3 and Supplementary Table S4. In particular, apparent pass/fail labels in this no-exclusion analysis can be invalid whenever the reference Bader QoI is itself non-evaluable at the requested threshold.

### S5b. Inflated-threshold stress test

Here the analysis threshold is multiplied by `k = 2, 5, 10` as a post hoc robustness diagnostic. Values are pooled over the 254 development materials. The original chemical tolerance remains the pre-specified contract of record.

| Original threshold | k | Codec | Certified, n/254 | Certified (%) | Median best ratio (x) |
|---:|---:|---|---:|---:|---:|
| 1e-4 e | 2 | SPERR | 214/254 | 84.3 | 6.08 |
| 1e-4 e | 2 | SZ3 | 209/254 | 82.3 | 13.04 |
| 1e-4 e | 2 | ZFP | 244/254 | 96.1 | 13.86 |
| 1e-4 e | 5 | SPERR | 241/254 | 94.9 | 7.47 |
| 1e-4 e | 5 | SZ3 | 236/254 | 92.9 | 23.78 |
| 1e-4 e | 5 | ZFP | 253/254 | 99.6 | 20.02 |
| 1e-4 e | 10 | SPERR | 248/254 | 97.6 | 8.71 |
| 1e-4 e | 10 | SZ3 | 246/254 | 96.9 | 35.19 |
| 1e-4 e | 10 | ZFP | 254/254 | 100.0 | 24.70 |
| 1e-3 e | 2 | SPERR | 219/254 | 86.2 | 6.70 |
| 1e-3 e | 2 | SZ3 | 217/254 | 85.4 | 16.78 |
| 1e-3 e | 2 | ZFP | 244/254 | 96.1 | 16.13 |
| 1e-3 e | 5 | SPERR | 242/254 | 95.3 | 7.77 |
| 1e-3 e | 5 | SZ3 | 236/254 | 92.9 | 24.63 |
| 1e-3 e | 5 | ZFP | 253/254 | 99.6 | 21.08 |
| 1e-3 e | 10 | SPERR | 248/254 | 97.6 | 8.83 |
| 1e-3 e | 10 | SZ3 | 246/254 | 96.9 | 35.67 |
| 1e-3 e | 10 | ZFP | 254/254 | 100.0 | 25.01 |
| 1e-2 e | 2 | SPERR | 236/254 | 92.9 | 10.43 |
| 1e-2 e | 2 | SZ3 | 234/254 | 92.1 | 60.81 |
| 1e-2 e | 2 | ZFP | 253/254 | 99.6 | 32.30 |
| 1e-2 e | 5 | SPERR | 244/254 | 96.1 | 10.58 |
| 1e-2 e | 5 | SZ3 | 241/254 | 94.9 | 65.24 |
| 1e-2 e | 5 | ZFP | 253/254 | 99.6 | 34.60 |
| 1e-2 e | 10 | SPERR | 248/254 | 97.6 | 11.10 |
| 1e-2 e | 10 | SZ3 | 246/254 | 96.9 | 70.92 |
| 1e-2 e | 10 | ZFP | 254/254 | 100.0 | 37.83 |

**Evidence provenance:** threshold-sensitivity analysis, including bulk/slab-resolved rows and distributional quantiles.

---

## Supplementary Table S6 | Re-derived Bader error relative to each material's independent QSQ stability floor

Only certified reconstruction points are included. Ratios near unity indicate that the observed reconstruction error is on the same numerical scale as the independent stability floor. This table does not estimate a material-level compression-error plateau and cannot establish `plateau = floor`.

| Bader threshold | Codec | n | Median DeltaQ/floor | P10 | P90 |
|---:|---|---:|---:|---:|---:|
| 1e-4 e | SPERR | 39 | 1.232 | 0.543 | 3.203 |
| 1e-4 e | SZ3 | 38 | 1.329 | 0.753 | 2.860 |
| 1e-4 e | ZFP | 46 | 1.091 | 0.338 | 3.247 |
| 1e-3 e | SPERR | 137 | 3.546 | 0.915 | 19.915 |
| 1e-3 e | SZ3 | 136 | 2.783 | 0.902 | 16.587 |
| 1e-3 e | ZFP | 142 | 3.386 | 0.822 | 17.825 |
| 1e-2 e | SPERR | 208 | 14.221 | 1.531 | 127.075 |
| 1e-2 e | SZ3 | 207 | 14.613 | 1.733 | 128.381 |
| 1e-2 e | ZFP | 225 | 10.698 | 1.308 | 129.864 |

At the strictest certified contract, median `DeltaQ/floor` is only 1.09-1.33 across the three codecs, consistent with an emerging analysis-limited regime. The much broader ratios at 1e-3 and 1e-2 e show that this floor-scale interpretation should not be generalized across the full tolerance range.

**Evidence provenance:** certified-error-to-QSQ-floor summary.

---

## Supplementary Table S7 | QSQ seed and amplitude sensitivity

### S7a. Eighteen-material probe calibration

| Diagnostic | Calibration result | Qualification implication |
|---|---:|---|
| Exact neighbouring ties created | median 82 under order-preserving control; 0 under same-amplitude QSQ perturbation | An order-preserving round trip is unusually benign for an order-dependent watershed |
| Systems with zero voxel reassignment | 9/18 order-preserving control; 2/18 same-amplitude QSQ perturbation | QSQ noise more effectively probes the relevant partition-instability channel |
| Five-seed log10 floor span | median 0.47 decades; maximum 2.4 decades | A single seed is insufficient for the five-seed qualification rule |
| Seed-dependent eligibility at 1e-4 e | 3/18 materials | Five pre-specified seeds retained |
| Seed-dependent eligibility at 1e-3 e | 2/18 materials | Five pre-specified seeds retained |
| Seed-dependent eligibility at 1e-2 e | 1/18 materials | Five pre-specified seeds retained |
| Floor change from x0.1 to x10 amplitude | median 0.76 decades; P10 0.00; P90 2.02 | The floor is explicitly qualification-defined, not amplitude-free |

### S7b. Full 319-system application of the five-seed QSQ rule

| Diagnostic | Full-corpus result |
|---|---:|
| Systems | 319 |
| Five-seed log10 floor span, median | **0.37 decades** |
| Five-seed log10 floor span, maximum | **3.82 decades** |
| Primary-seed verdict differs from five-seed maximum at 1e-4 e | **35/319** |
| Primary-seed verdict differs from five-seed maximum at 1e-3 e | **17/319** |
| Primary-seed verdict differs from five-seed maximum at 1e-2 e | **2/319** |

The 0.47-decade median / 2.4-decade maximum in S7a describe the calibration panel, whereas the 0.37-decade median / 3.82-decade maximum in S7b describe application of the five-seed rule to the full 319-system corpus. They answer different questions and are not interchangeable.

**Evidence provenance:** probe-calibration panel, per-seed QSQ responses and amplitude-sensitivity analysis.

**Interpretation.**

Tables S5-S7 are sensitivity and audit material. They support transparency of the measurement contract, but they do not redefine the primary chemical thresholds, change the pre-specified QSQ seed set or amplitude, or turn a non-evaluable material-threshold pair into a codec pass.

---

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

**Evidence provenance:** electron-count/Bader decoupling analysis.

---

## Supplementary Table S9 | Hartree-potential response is smoother than re-derived Bader response on the same reconstructions

### S9a. Pooled codec-level scaling on the 6,270 reproduction-gate-passing rows

| Codec | Gate-passing rows | Hartree slope | Hartree R² | Bader slope | Bader R² | Median Hartree relative RMSE | Median Bader error (e) |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZFP | 2,450 | 0.968 | 0.863 | 0.646 | 0.684 | 9.405e-07 | 2.453e-03 |
| SZ3 | 1,864 | 1.069 | 0.910 | 0.584 | 0.757 | 2.591e-05 | 5.890e-03 |
| SPERR | 1,956 | 0.988 | 0.786 | 0.587 | 0.750 | 2.643e-06 | 5.631e-03 |

The all-codec pooled Hartree log–log exponent in the pooled analysis is **1.02** on all 6,270 gate-passing rows; the per-codec values above show the same near-first-order pattern without collapsing codec-specific prefactors.

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

**Evidence provenance:** Hartree pooled-scaling, material-smoothness and matched-error-dispersion analyses.

**Interpretation.** Tables S8–S9 are operator-control analyses. They show why downstream observables must be evaluated explicitly; the prospective QSQ validation remains a separate endpoint.

---

## Supplementary Table S10 | Representative Bader decomposition confirms a dominant domain-migration channel

| Relative codec tolerance | Codec | Cases | Median fixed-basin underestimation | P10–P90 | Median bounded domain share at max-total atom | Domain term > integrand | Median reassigned voxel fraction |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1e-04 | ZFP | 12 | 1011.31× | 87.56–11538.89× | 0.999 | 100.0% | 1.610e-03 |
| 1e-04 | SZ3 | 12 | 20.11× | 3.83–30.07× | 0.985 | 100.0% | 1.216e-02 |
| 1e-04 | SPERR | 12 | 585.30× | 118.26–1147.15× | 0.999 | 100.0% | 1.945e-02 |
| 1e-03 | ZFP | 12 | 171.84× | 27.16–1122.03× | 0.997 | 100.0% | 5.695e-03 |
| 1e-03 | SZ3 | 12 | 4.00× | 2.38–28.80× | 0.942 | 91.7% | 5.119e-02 |
| 1e-03 | SPERR | 12 | 158.98× | 46.34–466.47× | 0.998 | 100.0% | 1.182e-01 |
| 1e-02 | ZFP | 10 | 43.67× | 13.15–327.91× | 0.996 | 100.0% | 3.758e-02 |
| 1e-02 | SZ3 | 12 | 3.07× | 1.26–6.83× | 0.847 | 91.7% | 1.376e-01 |
| 1e-02 | SPERR | 12 | 40.29× | 10.15–229.09× | 0.993 | 100.0% | 2.365e-01 |

Across the full representative matrix (n=106 material–codec–tolerance cases), the median maximum-resolved / maximum-fixed-basin error ratio is **52.59×**. At the atom of maximum total deviation, the median bounded absolute domain share |domain|/(|domain|+|integrand|) is **0.995**, and the domain term exceeds the integrand term in **98.1%** of cases. These two metrics are reported separately because signed cancellation can make |domain|/|total| exceed 1.

**Evidence provenance:** representative Bader mechanism decomposition and per-atom decomposition tables.

---

## Supplementary Table S11 | Independent Bader implementations preserve the mechanism and strict-response ordering

### S11a. Study completeness and solver failures

| Quantity | Result |
|---|---:|
| Expected outcome rows | 1,560 |
| Completed outcome rows | 1,560 |
| BaderKit on-grid solver failures | 2 |
| Henkelman on-grid solver failures | 0 |
| Henkelman near-grid solver failures | 0 |
| Representative systems in aggregate | 12 development systems |
| Separate probe-failure sentinel | 1 system; excluded from aggregates |

### S11b. Cross-implementation stability and codec response

| Diagnostic | Comparison solver | n | Median / fraction | IQR |
|---|---|---:|---:|---:|
| Codec response comparison/BaderKit | Henkelman on-grid (above print resolution) | 70 | 1.000 | 0.920–1.005 |
| Codec response comparison/BaderKit | Henkelman on-grid (above print and baseline compatible) | 47 | 1.000 | 1.000–1.000 |
| Codec response comparison/BaderKit | Henkelman near-grid (above print resolution) | 70 | 0.768 | 0.310–1.218 |
| QSQ floor agrees with BaderKit within 1e-6 e | Henkelman on-grid | 12 materials | 75.0% | — |
| Eligibility concordance at 0.0001 e | Henkelman on-grid | 12 materials | 100.0% | — |
| Eligibility concordance at 0.001 e | Henkelman on-grid | 12 materials | 100.0% | — |
| Eligibility concordance at 0.01 e | Henkelman on-grid | 12 materials | 91.7% | — |
| QSQ floor agrees with BaderKit within 1e-6 e | Henkelman near-grid | 12 materials | 0.0% | — |
| Eligibility concordance at 0.0001 e | Henkelman near-grid | 12 materials | 83.3% | — |
| Eligibility concordance at 0.001 e | Henkelman near-grid | 12 materials | 91.7% | — |
| Eligibility concordance at 0.01 e | Henkelman near-grid | 12 materials | 91.7% | — |

Codec-response ratios above use successful paired outputs above the 2e-6 e Henkelman print-resolution region. The additional on-grid baseline-compatible row requires the unperturbed Henkelman/BaderKit atomic charges to agree within 1e-3 e. All paired points, including flagged baseline differences, remain in `supplement/S11_cross_implementation_pairs.csv`.

### S11c. Relative 1e-4 codec-response ordering by implementation

| Solver | Error ratio | n materials | Median ratio | IQR |
|---|---|---:|---:|---:|
| BaderKit on-grid | SZ3/ZFP | 12 | 6.18× | 3.35–12.81× |
| BaderKit on-grid | SPERR/ZFP | 12 | 6.69× | 2.65–13.36× |
| Henkelman on-grid | SZ3/ZFP | 12 | 4.83× | 2.54–6.97× |
| Henkelman on-grid | SPERR/ZFP | 12 | 5.45× | 1.32–6.95× |
| Henkelman near-grid | SZ3/ZFP | 12 | 3.17× | 1.23–10.62× |
| Henkelman near-grid | SPERR/ZFP | 12 | 2.87× | 0.92–8.52× |

### S11d. Exact BaderKit decomposition by perturbation kind

| Perturbation kind | n | Median bounded domain share | IQR | Domain > integrand | Max closure residual (e) |
|---|---:|---:|---:|---:|---:|
| codec | 70 | 0.9898 | 0.9573–0.9991 | 100.0% | 0.0e+00 |
| order-preserving control | 12 | 0.0208 | 0.0096–0.9999 | 41.7% | 0.0e+00 |
| QSQ perturbation | 60 | 0.9999 | 0.9990–1.0000 | 83.3% | 0.0e+00 |
| spatial control | 324 | 0.9961 | 0.9843–0.9995 | 100.0% | 0.0e+00 |

### S11e. Spatial reorganization controls

| Solver | Control | n pairs | Median log2(control/codec) | IQR | Fraction increased |
|---|---|---:|---:|---:|---:|
| BaderKit on-grid | global | 36 | 0.26 | -0.17–0.81 | 52.8% |
| BaderKit on-grid | shift | 36 | 0.02 | -0.29–0.63 | 50.0% |
| BaderKit on-grid | stratified | 36 | 0.26 | -0.07–0.72 | 63.9% |
| Henkelman on-grid | global | 36 | 0.24 | -0.14–0.79 | 61.1% |
| Henkelman on-grid | shift | 36 | 0.04 | -0.17–0.66 | 55.6% |
| Henkelman on-grid | stratified | 36 | 0.15 | -0.15–0.69 | 61.1% |
| Henkelman near-grid | global | 36 | 0.07 | -0.36–0.74 | 50.0% |
| Henkelman near-grid | shift | 36 | 0.00 | -0.27–0.46 | 50.0% |
| Henkelman near-grid | stratified | 36 | 0.07 | -0.24–0.47 | 55.6% |

### S11f. Resolved 24-system QSQ classification transfer

This second, deterministic panel is distinct from the 12-system mechanism matrix above. It contains 24 development systems stratified by bulk/slab and four QSQ stability-floor bands. The same five pre-specified perturbation fields were analyzed with independent Bader implementations.

| Bader threshold | Independent solver | Comparable systems | Ambiguous | Agreement with primary QSQ classification | Cohen kappa | Eligible -> rejected | Rejected -> eligible |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1e-4 e | Henkelman on-grid | 24 | 0 | **100.0%** | **1.000** | 0 | 0 |
| 1e-4 e | Henkelman near-grid | 23 | 1 | 82.6% | 0.593 | 1 | 3 |
| 1e-3 e | Henkelman on-grid | 24 | 0 | **100.0%** | **1.000** | 0 | 0 |
| 1e-3 e | Henkelman near-grid | 24 | 0 | 83.3% | 0.667 | 0 | 4 |
| 1e-2 e | Henkelman on-grid | 24 | 0 | **100.0%** | **1.000** | 0 | 0 |
| 1e-2 e | Henkelman near-grid | 24 | 0 | 95.8% | 0.882 | 0 | 1 |

Floor-rank Spearman correlation with primary BaderKit is **0.995** for Henkelman on-grid and **0.754** for Henkelman near-grid. Recreated BaderKit floors agree with their reference values to a maximum absolute difference of **8.71338e-11 e**.


**Evidence provenance:** resolved 24-system implementation-transfer classification and floor-rank summaries.

---

**Interpretation.** This deliberately stratified 12-system panel is a mechanism/implementation robustness study, not a prevalence estimate. Henkelman on-grid reproduces the BaderKit codec response essentially one-for-one above print resolution, and the strict SZ3/ZFP and SPERR/ZFP ordering remains qualitatively similar under on-grid and near-grid Henkelman analyses. The exact decomposition supports a Bader-specific domain-migration channel. Spatial permutations provide secondary evidence that error organization matters, while the near-null periodic-shift control argues against a simple alignment-only explanation. These results do not redefine QSQ or alter the primary benchmark.

**Evidence provenance:** independent-Bader outcome, stability-comparison, mechanism-decomposition and spatial-control summaries.

---

## Supplementary Table S12 | Realized-L∞ matching sensitivity across pre-specified calipers

The primary analysis uses a 0.10-dex caliper; 0.05, 0.20 and 0.30 dex are pre-specified sensitivity analyses.

## S12a. Matched support and realized-L∞ balance

| Caliper (dex) | Codec pair | Matched row pairs | Materials represented | Median |Δlog10 L∞| (dex) | P95 |Δlog10 L∞| (dex) | Median larger/smaller L∞ | P95 larger/smaller L∞ |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0.05 | ZFP/SZ3 | 198 | 147 | 0.0234 | 0.0466 | 1.055 | 1.113 |
| 0.05 | ZFP/SPERR | 208 | 143 | 0.0256 | 0.0467 | 1.061 | 1.113 |
| 0.05 | SZ3/SPERR | 1,848 | 254 | 0.0000 | 0.0005 | 1.000 | 1.001 |
| 0.10 | ZFP/SZ3 | 457 | 214 | 0.0560 | 0.0964 | 1.138 | 1.249 |
| 0.10 | ZFP/SPERR | 465 | 206 | 0.0553 | 0.0967 | 1.136 | 1.249 |
| 0.10 | SZ3/SPERR | 1,848 | 254 | 0.0000 | 0.0005 | 1.000 | 1.001 |
| 0.20 | ZFP/SZ3 | 1,089 | 244 | 0.1130 | 0.1904 | 1.297 | 1.550 |
| 0.20 | ZFP/SPERR | 1,091 | 245 | 0.1124 | 0.1903 | 1.296 | 1.550 |
| 0.20 | SZ3/SPERR | 1,848 | 254 | 0.0000 | 0.0005 | 1.000 | 1.001 |
| 0.30 | ZFP/SZ3 | 1,621 | 248 | 0.1464 | 0.2707 | 1.401 | 1.865 |
| 0.30 | ZFP/SPERR | 1,622 | 248 | 0.1452 | 0.2709 | 1.397 | 1.866 |
| 0.30 | SZ3/SPERR | 1,848 | 254 | 0.0000 | 0.0005 | 1.000 | 1.001 |

## S12b. Re-derived Bader-error effect after matching

| Caliper (dex) | Codec-error ratio | Usable matched pairs | Usable materials | Effect | 95% material-bootstrap CI |
|---:|---|---:|---:|---:|---:|
| 0.05 | ZFP/SZ3 | 198 | 147 | 0.583 | 0.549–0.650 |
| 0.05 | ZFP/SPERR | 208 | 143 | 0.602 | 0.508–0.707 |
| 0.05 | SZ3/SPERR | 1,848 | 254 | 1.033 | 0.976–1.072 |
| 0.10 | ZFP/SZ3 | 457 | 214 | 0.557 | 0.525–0.598 |
| 0.10 | ZFP/SPERR | 465 | 206 | 0.601 | 0.534–0.662 |
| 0.10 | SZ3/SPERR | 1,848 | 254 | 1.033 | 0.976–1.072 |
| 0.20 | ZFP/SZ3 | 1,089 | 244 | 0.591 | 0.565–0.620 |
| 0.20 | ZFP/SPERR | 1,091 | 245 | 0.591 | 0.558–0.624 |
| 0.20 | SZ3/SPERR | 1,848 | 254 | 1.033 | 0.976–1.072 |
| 0.30 | ZFP/SZ3 | 1,621 | 248 | 0.599 | 0.568–0.624 |
| 0.30 | ZFP/SPERR | 1,622 | 248 | 0.600 | 0.574–0.651 |
| 0.30 | SZ3/SPERR | 1,848 | 254 | 1.033 | 0.976–1.072 |

## S12c. Fixed-basin diagnostic after the same matching

| Caliper (dex) | Codec-error ratio | Effect | 95% material-bootstrap CI |
|---:|---|---:|---:|
| 0.05 | ZFP/SZ3 | 0.055 | 0.049–0.063 |
| 0.05 | ZFP/SPERR | 0.699 | 0.628–0.817 |
| 0.05 | SZ3/SPERR | 10.775 | 10.115–11.418 |
| 0.10 | ZFP/SZ3 | 0.057 | 0.052–0.061 |
| 0.10 | ZFP/SPERR | 0.709 | 0.665–0.801 |
| 0.10 | SZ3/SPERR | 10.775 | 10.115–11.418 |
| 0.20 | ZFP/SZ3 | 0.064 | 0.059–0.070 |
| 0.20 | ZFP/SPERR | 0.727 | 0.667–0.819 |
| 0.20 | SZ3/SPERR | 10.775 | 10.115–11.418 |
| 0.30 | ZFP/SZ3 | 0.068 | 0.061–0.075 |
| 0.30 | ZFP/SPERR | 0.726 | 0.660–0.794 |
| 0.30 | SZ3/SPERR | 10.775 | 10.115–11.418 |

**Primary 0.10-dex result.** Re-derived Bader-error ratios are ZFP/SZ3 = **0.557** (95% CI 0.525–0.598), ZFP/SPERR = **0.601** (0.534–0.662), and SZ3/SPERR = **1.033** (0.976–1.072). The direction of the ZFP comparisons remains below one across all pre-specified calipers, whereas SZ3/SPERR remains close to one.

**Interpretation.** Matching controls realized maximum perturbation, not the full geometry of the codec error field. A residual codec effect after matching is consistent with an error-structure contribution but does not identify a unique spatial invariant. Fixed-basin effects are diagnostic because fixed domains change the downstream operator.

**Evidence provenance:** realized-distortion matching diagnostics and caliper-sensitivity summary.

---

## Supplementary Table S13 | Stability-qualified rate–fidelity in development and untouched external confirmation

Development and external summaries use the same pre-specified QSQ eligibility and codec-scoring rules.

## S13a. Development cohort — overall eligible material set

| Bader contract | Codec | Admitted | Non-evaluable | Certified | Certified fraction | Median best-certified compression ratio [95% bootstrap CI] | P10–P90 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1e-04 e | ZFP | 46 | 208 | 46 | 100.0% | 7.8× [7.2, 8.1] | 5.9–10.6× |
| 1e-04 e | SZ3 | 46 | 208 | 38 | 82.6% | 6.4× [6.0, 7.3] | 4.8–8.4× |
| 1e-04 e | SPERR | 46 | 208 | 39 | 84.8% | 4.2× [4.1, 4.6] | 3.8–13.4× |
| 1e-03 e | ZFP | 143 | 111 | 142 | 99.3% | 13.8× [13.1, 14.8] | 9.8–21.6× |
| 1e-03 e | SZ3 | 143 | 111 | 136 | 95.1% | 13.2× [12.2, 14.3] | 8.2–20.2× |
| 1e-03 e | SPERR | 143 | 111 | 137 | 95.8% | 5.8× [5.6, 6.0] | 4.5–27.6× |
| 1e-02 e | ZFP | 229 | 25 | 225 | 98.3% | 31.9× [29.9, 34.0] | 19.8–52.6× |
| 1e-02 e | SZ3 | 229 | 25 | 207 | 90.4% | 57.7× [49.7, 66.5] | 26.2–109.8× |
| 1e-02 e | SPERR | 229 | 25 | 208 | 90.8% | 10.3× [9.4, 10.7] | 7.1–103.1× |

## S13b. Development cohort — bulk/slab strata

| Bader contract | Stratum | Codec | Admitted | Non-evaluable | Certified fraction | Median ratio [95% bootstrap CI] |
|---:|---|---|---:|---:|---:|---:|
| 1e-04 e | bulk | ZFP | 42 | 144 | 100.0% | 7.6× [6.9, 8.0] |
| 1e-04 e | bulk | SZ3 | 42 | 144 | 85.7% | 6.3× [5.8, 7.2] |
| 1e-04 e | bulk | SPERR | 42 | 144 | 90.5% | 4.2× [4.1, 4.6] |
| 1e-04 e | slab | ZFP | 4 | 64 | 100.0% | 10.5× [9.1, 11.6] |
| 1e-04 e | slab | SZ3 | 4 | 64 | 50.0% | 8.4× [8.3, 8.5] |
| 1e-04 e | slab | SPERR | 4 | 64 | 25.0% | 3.9× [3.9, 3.9] |
| 1e-03 e | bulk | ZFP | 103 | 83 | 99.0% | 13.5× [12.8, 14.5] |
| 1e-03 e | bulk | SZ3 | 103 | 83 | 99.0% | 12.9× [12.0, 14.3] |
| 1e-03 e | bulk | SPERR | 103 | 83 | 99.0% | 6.2× [6.0, 6.5] |
| 1e-03 e | slab | ZFP | 40 | 28 | 100.0% | 15.3× [13.0, 18.4] |
| 1e-03 e | slab | SZ3 | 40 | 28 | 85.0% | 14.1× [10.8, 15.4] |
| 1e-03 e | slab | SPERR | 40 | 28 | 87.5% | 5.1× [4.9, 5.4] |
| 1e-02 e | bulk | ZFP | 168 | 18 | 98.8% | 30.0× [27.1, 31.9] |
| 1e-02 e | bulk | SZ3 | 168 | 18 | 95.2% | 51.8× [47.7, 60.3] |
| 1e-02 e | bulk | SPERR | 168 | 18 | 95.8% | 11.5× [10.1, 13.2] |
| 1e-02 e | slab | ZFP | 61 | 7 | 96.7% | 40.5× [35.8, 44.9] |
| 1e-02 e | slab | SZ3 | 61 | 7 | 77.0% | 67.8× [59.6, 70.6] |
| 1e-02 e | slab | SPERR | 61 | 7 | 77.0% | 8.1× [7.7, 8.6] |

## S13c. Untouched external confirmatory cohort — overall

| Bader contract | Codec | Admitted (of 63) | Non-evaluable | Certified | Certified fraction | Median best-certified compression ratio [95% bootstrap CI] | Row-failure-affected materials |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1e-04 e | ZFP | 16 | 47 | 16 | 100.0% | 13.0× [7.1, 20.4] | 0 |
| 1e-04 e | SZ3 | 16 | 47 | 14 | 87.5% | 12.1× [7.3, 17.7] | 0 |
| 1e-04 e | SPERR | 16 | 47 | 14 | 87.5% | 5.2× [4.2, 6.2] | 0 |
| 1e-03 e | ZFP | 42 | 21 | 42 | 100.0% | 18.8× [14.3, 25.0] | 0 |
| 1e-03 e | SZ3 | 42 | 21 | 42 | 100.0% | 18.8× [12.1, 24.6] | 0 |
| 1e-03 e | SPERR | 42 | 21 | 41 | 97.6% | 6.4× [5.9, 6.9] | 0 |
| 1e-02 e | ZFP | 57 | 6 | 57 | 100.0% | 40.6× [35.4, 46.0] | 2 |
| 1e-02 e | SZ3 | 57 | 6 | 57 | 100.0% | 65.9× [40.7, 101.8] | 0 |
| 1e-02 e | SPERR | 57 | 6 | 57 | 100.0% | 10.8× [10.2, 12.4] | 0 |

## S13d. Untouched external cohort — bulk/vacuum-containing 2D strata

| Bader contract | Stratum | Codec | Admitted | Non-evaluable | Certified fraction | Median ratio [95% bootstrap CI] |
|---:|---|---|---:|---:|---:|---:|
| 1e-04 e | bulk | ZFP | 9 | 27 | 100.0% | 7.1× [6.3, 20.2] |
| 1e-04 e | bulk | SZ3 | 9 | 27 | 77.8% | 7.3× [4.5, 17.4] |
| 1e-04 e | bulk | SPERR | 9 | 27 | 88.9% | 4.3× [3.9, 11.1] |
| 1e-04 e | vacuum-containing 2D | ZFP | 7 | 20 | 100.0% | 19.7× [14.9, 27.8] |
| 1e-04 e | vacuum-containing 2D | SZ3 | 7 | 20 | 100.0% | 17.1× [9.9, 21.5] |
| 1e-04 e | vacuum-containing 2D | SPERR | 7 | 20 | 85.7% | 5.5× [4.7, 6.0] |
| 1e-03 e | bulk | ZFP | 21 | 15 | 100.0% | 11.2× [9.7, 13.9] |
| 1e-03 e | bulk | SZ3 | 21 | 15 | 100.0% | 9.8× [8.2, 16.8] |
| 1e-03 e | bulk | SPERR | 21 | 15 | 100.0% | 6.2× [5.0, 7.0] |
| 1e-03 e | vacuum-containing 2D | ZFP | 21 | 6 | 100.0% | 25.6× [24.8, 30.2] |
| 1e-03 e | vacuum-containing 2D | SZ3 | 21 | 6 | 100.0% | 24.6× [22.9, 39.1] |
| 1e-03 e | vacuum-containing 2D | SPERR | 21 | 6 | 95.2% | 6.6× [6.0, 7.0] |
| 1e-02 e | bulk | ZFP | 30 | 6 | 100.0% | 28.5× [23.1, 33.5] |
| 1e-02 e | bulk | SZ3 | 30 | 6 | 100.0% | 33.0× [26.5, 39.6] |
| 1e-02 e | bulk | SPERR | 30 | 6 | 100.0% | 13.1× [9.8, 22.8] |
| 1e-02 e | vacuum-containing 2D | ZFP | 27 | 0 | 100.0% | 49.1× [42.4, 61.1] |
| 1e-02 e | vacuum-containing 2D | SZ3 | 27 | 0 | 100.0% | 115.2× [101.8, 158.4] |
| 1e-02 e | vacuum-containing 2D | SPERR | 27 | 0 | 100.0% | 10.2× [9.6, 11.6] |

## S13e. Pairwise SZ3 versus ZFP transition

| Cohort | Bader contract | Stratum | n eligible comparisons | SZ3 wins | Ties | ZFP wins | Median log2(SZ3/ZFP) |
|---|---:|---|---:|---:|---:|---:|---:|
| development | 1e-04 e | overall | 46 | 10.9% | 0.0% | 89.1% | -0.199 |
| development | 1e-04 e | bulk | 42 | 11.9% | 0.0% | 88.1% | -0.187 |
| development | 1e-04 e | slab | 4 | 0.0% | 0.0% | 100.0% | -0.392 |
| development | 1e-03 e | overall | 143 | 32.9% | 0.0% | 67.1% | -0.106 |
| development | 1e-03 e | bulk | 103 | 40.8% | 0.0% | 59.2% | -0.095 |
| development | 1e-03 e | slab | 40 | 12.5% | 0.0% | 87.5% | -0.290 |
| development | 1e-02 e | overall | 229 | 80.3% | 1.3% | 18.3% | 0.746 |
| development | 1e-02 e | bulk | 168 | 86.9% | 0.6% | 12.5% | 0.869 |
| development | 1e-02 e | slab | 61 | 62.3% | 3.3% | 34.4% | 0.571 |
| external confirmatory | 1e-04 e | overall | 16 | 31.2% | 0.0% | 68.8% | -0.148 |
| external confirmatory | 1e-04 e | bulk | 9 | 22.2% | 0.0% | 77.8% | -0.122 |
| external confirmatory | 1e-04 e | vacuum-containing 2D | 7 | 42.9% | 0.0% | 57.1% | -0.173 |
| external confirmatory | 1e-03 e | overall | 42 | 35.7% | 0.0% | 64.3% | -0.116 |
| external confirmatory | 1e-03 e | bulk | 21 | 33.3% | 0.0% | 66.7% | -0.173 |
| external confirmatory | 1e-03 e | vacuum-containing 2D | 21 | 38.1% | 0.0% | 61.9% | -0.081 |
| external confirmatory | 1e-02 e | overall | 57 | 89.5% | 0.0% | 10.5% | 0.646 |
| external confirmatory | 1e-02 e | bulk | 30 | 83.3% | 0.0% | 16.7% | 0.299 |
| external confirmatory | 1e-02 e | vacuum-containing 2D | 27 | 96.3% | 0.0% | 3.7% | 1.316 |

**External confirmation summary.** The untouched cohort admits 16/63, 42/63 and 57/63 systems at 1e-4, 1e-3 and 1e-2 e. Median external best-certified compression ratios are approximately ZFP/SZ3/SPERR = 13.0/12.1/5.2× at 1e-4 e, 18.8/18.8/6.4× at 1e-3 e, and 40.6/65.9/10.8× at 1e-2 e. The SZ3-versus-ZFP win fraction correspondingly shifts from 31.3% to 35.7% to 89.5%.

**Interpretation.** The preferred codec depends on the scientific contract and the eligible cohort. These tables do not support a universal codec winner. The 63-system confirmatory cohort must not be replaced by the 65-system descriptive/stability aggregate when reporting external rate–fidelity.

**Evidence provenance:** development/external rate–fidelity summary and SZ3/ZFP pairwise comparison table.

---

## Supplementary Table S14 | Failure taxonomy, exclusions and negative-result audit


## S14a. Failure and exclusion semantics used in the submission

| State / category | Meaning | Scored as codec pass/fail? | Evidence class |
|---|---|---|---|
| `NON_EVALUABLE_BADER_UNSTABLE` | Reference Bader QoI fails **QSQ eligibility** at the requested tolerance | **No** — neither pass nor fail | QSQ eligibility summary |
| `bader_solver_failure` | Downstream Bader analysis did not return a valid row-level result | **No automatic codec attribution**; retained in audit | failure registry |
| `reproduction_mismatch` | Reproduction/platform check failed despite reconstructed scientific field remaining consistent | **No**; infrastructure exclusion from the affected formal analysis | Hartree reproduction records |
| `basin_relabelling_symmetry_equivalent` | Apparent large atom-indexed charge change is a permutation among symmetry-equivalent basins | **Non-evaluable for position-indexed charge**, separately flagged | failure registry |
| eligible + not certified | Reference QoI is numerically eligible but compressed reconstruction exceeds the requested Bader contract | **Yes: genuine failure** | development benchmark |
| eligible + certified | Reference QoI is eligible and the reconstruction satisfies the contract | **Yes: certified success** | development benchmark |

## S14b. Explicit failure registry counts

| Registry category | Row records |
|---|---:|
| `bader_solver_failure` | 78 |
| `basin_relabelling_symmetry_equivalent` | 1 |

### Bader-solver failures by corpus and codec

| Corpus | Codec | Row failures |
|---|---|---:|
| development bulk | ZFP | 37 |
| development slab | SPERR | 4 |
| development slab | ZFP | 37 |

These counts describe explicit row-level failure records, not material-level non-evaluable counts. QSQ non-evaluability is reported separately through the eligibility analysis and should not be reconstructed from the failure registry.

## S14c. Exploratory algorithm checks not retained as benchmark claims

| Check | Result / reason not promoted |
|---|---|
| External baselines (BQB, den2bin) | Retained as related-work context rather than headline fair benchmarks because task definitions and error-control contracts are not directly comparable to the density-field benchmark. |
| Candidate codec modifications | No proposed modification showed sufficiently robust improvement under the re-derived-Bader metric to support a new-compressor claim; the contribution therefore remains the measurement/certification framework. |

**Interpretation.** Scientific non-evaluability, downstream solver failure, infrastructure mismatch and codec fidelity are reported as distinct states. Non-evaluable targets are not codec failures, and solver failures are not silently imputed as codec failures.

**Evidence provenance:** failure-registry summary and claim–evidence audit.

---

## Supplementary Table S15 | Outcome-blind chemistry pairs and two-implementation source references

| Pair | Source chemistry | State A → State B | Added atoms | Target | Δq BaderKit (e) | Δq Henkelman (e) | Pair QSQ eligible at 1e-3 e |
|---|---|---|---|---|---:|---:|---:|
| Pair 1 | GaN electrochemical surfaces, with AECCARs | Ga22N22 → Ga22N22H2H2 | H:4 | N | 0.528936 | 0.528936 | Yes |
| Pair 2 | GaN electrochemical surfaces, with AECCARs | Ga15N15H2H1 → Ga15N15H3H3 | H:3 | N | 0.522669 | 0.522669 | Yes |
| Pair 3 | GaN electrochemical surfaces, with AECCARs | Ga15N15 → Ga15N15H2H1 | H:3 | N | 0.610388 | 0.610388 | Yes |
| Pair 4 | RuO₂ CO₂RR, adsorbate and spectator variations | O31Ru16 → H3C1O31Ru16 | C:1;H:3 | O | 0.421202 | 0.421201 | No |
| Pair 5 | RuO₂ CO₂RR, adsorbate and spectator variations | Ru16C3O33 → Ru16C3O34H1 | H:1;O:1 | Ru | -0.131815 | -0.131814 | No |

Reference acceptance was pre-specified before compression outcomes: identical non-zero sign in BaderKit and Henkelman on-grid, minimum |Δq| ≥ 0.02 e, and inter-solver |Δq| disagreement ≤ 0.01 e. All five pairs passed.

## Supplementary Table S16 | Direct-selection and optional independent-solver escalation policies

### Direct decision policies, pooled across codecs

| Policy | Retained / valid | Coverage | Adverse or zero-direction decisions | Error rate | Unique retained pairs |
|---|---:|---:|---:|---:|---:|
| Unqualified baseline | 60 / 60 | 100.0% | 0 | 0.0% | 5 |
| Realized-L∞ coverage-matched | 36 / 60 | 60.0% | 0 | 0.0% | 5 |
| Order-preserving control | 60 / 60 | 100.0% | 0 | 0.0% | 5 |
| QSQ | 36 / 60 | 60.0% | 0 | 0.0% | 3 |

### Optional independent-solver escalation

| Policy | Resolved / valid | Needs review | Errors among resolved | Henkelman state calls | Henkelman wall time (s) |
|---|---:|---:|---:|---:|---:|
| QSQ-targeted escalation | 60 / 60 | 0 | 0 | 48 | 397.2 |
| Escalate all | 60 / 60 | 0 | 0 | 108 | 733.3 |

Interpretation: no policy improves sign correctness because the unqualified common-tight baseline already has zero adverse decisions. QSQ is more conservative than this coarse sign contract. The lower independent-solver call count for targeted escalation is an audit-cost comparison only.

---

## Supplementary Table S17 | Operator-resolved Fourier diagnostics for realized-$L_\infty$-matched ZFP/SZ3 reconstructions.

The mechanism population contains 457 matched pairs from 214 materials (914 reconstructions). Material-level centers are computed after within-material aggregation on the log scale unless otherwise stated. The exact multiplicative Hartree decomposition is evaluated pairwise; separately aggregated centers are descriptive and are not expected to multiply exactly.

| Diagnostic | Value | Interpretation |
|---|---:|---|
| Reference-implementation Hartree error ratio, ZFP/SZ3 | 0.0776221 | Reproduces the matched-pair Hartree effect used as the mechanism target |
| Nyquist-safe Hartree error ratio, ZFP/SZ3 | 0.0776219 | Shows that the codec effect is unchanged after restoring exact Hermitian parity |
| Total spectral-error-energy factor, $\sqrt{E_{\text{ZFP}}/E_{\text{SZ3}}}$ | 0.376 | Contribution from overall spectral error magnitude |
| Spectral Hartree-susceptibility factor, $\sqrt{S_{H,\text{ZFP}}/S_{H,\text{SZ3}}}$ | 0.203 | Contribution from frequency allocation under Hartree weighting |
| Material-median spectral-structure share of absolute log effect | 62.0% | Frequency allocation is the larger component of the matched-distortion Hartree effect |
| Low-$G$ error-energy fraction ratio, ZFP/SZ3 | 0.416 | ZFP places less reconstruction-error energy in long-wavelength modes |
| High-$G$ error-energy fraction ratio, ZFP/SZ3 | 0.626 | ZFP also differs at high $G$, but these modes are weakly weighted by the Hartree operator |
| Materials with lower ZFP spectral Hartree susceptibility | 99.5% | Direction of the susceptibility effect is nearly universal in the mechanism cohort |
| Materials with higher ZFP spectral centroid | 98.1% | ZFP error is shifted toward higher reciprocal-space frequencies |
| Materials with lower ZFP low-$G$ error-energy fraction | 99.1% | Long-wavelength suppression is consistent across materials |
| Maximum real-space/Fourier-space Parseval relative discrepancy | $1.30\times10^{-15}$ | Confirms numerical identity of the Nyquist-safe operator and spectral expression |

For the Nyquist-safe reciprocal-space set $\mathcal{G}_s$,

$$
E=\sum_{G\in\mathcal{G}_s}|\Delta\rho(G)|^2,
\qquad
W_H=\sum_{G\in\mathcal{G}_s}\frac{|\Delta\rho(G)|^2}{|G|^4},
\qquad
S_H=\frac{W_H}{E}.
$$

For every matched pair,

$$
R_H=
\sqrt{\frac{E_{\text{ZFP}}}{E_{\text{SZ3}}}}
\sqrt{\frac{S_{H,\text{ZFP}}}{S_{H,\text{SZ3}}}}.
$$

**Machine-readable evidence:** Fourier-spectrum mechanism audit in the repository reader-facing provenance index, including the matched-pair mechanism table, reconstruction spectral metrics, radial-spectrum summary, mechanism-ratio summary and audit summary.
