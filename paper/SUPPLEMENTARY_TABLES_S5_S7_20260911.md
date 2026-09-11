# Supplementary Tables S5-S7

Updated 2026-09-11. Submission-facing robustness tables generated from frozen machine-readable assets. These tables are diagnostics and sensitivity analyses; they do not replace the pre-specified Protocol A.1 contracts.

## Supplementary Table S5 | Sensitivity to omission of eligibility and inflation of the Bader threshold

### S5a. Naive no-exclusion diagnostic

The table applies the requested Bader tolerance directly to all 254 development materials without Protocol A.1 eligibility qualification. `n certified` therefore means a naive binary pass and must not be interpreted as a stability-qualified scientific certification.

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

**Machine-readable source:** `supplement/S1_S3_sensitivity.csv`. The source also contains bulk/slab-resolved rows and P10/P90 distributions and remains the source of record for any additional subgroup statistic.

---

## Supplementary Table S6 | Re-derived Bader error relative to each material's independent Protocol A.1 floor

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

**Machine-readable source:** `supplement/S2_floor_relative.csv`.

---

## Supplementary Table S7 | Protocol A.1 seed and amplitude sensitivity

### S7a. Pre-freeze 18-material calibration

| Diagnostic | Archived float32 / calibration result | Protocol implication |
|---|---:|---|
| Exact neighbouring ties created | median 82 under archived float32; 0 under same-amplitude noise | An order-preserving round trip is unusually benign for an order-dependent watershed |
| Systems with zero voxel reassignment | 9/18 archived float32; 2/18 same-amplitude noise | Noise more effectively probes the relevant partition-instability channel |
| Five-seed log10 floor span | median 0.47 decades; maximum 2.4 decades | A single seed is insufficient for the frozen qualification rule |
| Seed-dependent eligibility at 1e-4 e | 3/18 materials | Five pre-registered seeds retained |
| Seed-dependent eligibility at 1e-3 e | 2/18 materials | Five pre-registered seeds retained |
| Seed-dependent eligibility at 1e-2 e | 1/18 materials | Five pre-registered seeds retained |
| Floor change from x0.1 to x10 amplitude | median 0.76 decades; P10 0.00; P90 2.02 | The floor is explicitly protocol-defined, not amplitude-free |

### S7b. Full 319-system deployment of the already-frozen five-seed rule

| Diagnostic | Full-corpus result |
|---|---:|
| Systems | 319 |
| Five-seed log10 floor span, median | **0.37 decades** |
| Five-seed log10 floor span, maximum | **3.82 decades** |
| Primary-seed verdict differs from five-seed maximum at 1e-4 e | **35/319** |
| Primary-seed verdict differs from five-seed maximum at 1e-3 e | **17/319** |
| Primary-seed verdict differs from five-seed maximum at 1e-2 e | **2/319** |

The 0.47-decade median / 2.4-decade maximum in S7a are calibration-panel statistics measured before Protocol A.1 was frozen. The 0.37-decade median / 3.82-decade maximum in S7b are full-corpus deployment statistics measured after applying the frozen rule to all 319 systems. They are not contradictory and must not be substituted for one another.

**Machine-readable sources:** `stability/probe_calibration.csv`; `stability/stability_floor_A1_per_seed.csv`; `supplement/S4_amplitude_sensitivity.csv`. Protocol definition: `protocol/PROTOCOL_A1.md`.

## Interpretation boundary

Tables S5-S7 are sensitivity and audit material. They support transparency of the measurement contract, but they do not redefine the primary chemical thresholds, change the frozen A.1 seed set or amplitude, or turn a non-evaluable material-threshold pair into a codec pass.
