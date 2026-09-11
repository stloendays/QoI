# Supplementary Tables S10–S11

Generated 2026-09-11 from the frozen Bader mechanism corpus and the independent Bader implementation study. These are robustness/mechanism tables; they do not alter the frozen benchmark or the central Figure 3 classification.

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

**Sources:** `mechanism/basin_error_decomposition_summary.csv`; extended per-atom values in `mechanism/basin_error_decomposition_per_atom.csv`. The stability-floor column in the historical mechanism table is not used for current Protocol A.1 claims.

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
| Separate probe-failure sentinel | 1 (`mp-1007755`; excluded from aggregates) |

### S11b. Cross-implementation stability and codec response

| Diagnostic | Comparison solver | n | Median / fraction | IQR |
|---|---|---:|---:|---:|
| Codec response comparison/BaderKit | henkelman_ongrid (above print resolution) | 70 | 1.000 | 0.920–1.005 |
| Codec response comparison/BaderKit | henkelman_ongrid (above print and baseline compatible) | 47 | 1.000 | 1.000–1.000 |
| Codec response comparison/BaderKit | henkelman_neargrid (above print resolution) | 70 | 0.768 | 0.310–1.218 |
| A.1 floor agrees with BaderKit within 1e-6 e | henkelman_ongrid | 12 materials | 75.0% | — |
| Eligibility concordance at 0.0001 e | henkelman_ongrid | 12 materials | 100.0% | — |
| Eligibility concordance at 0.001 e | henkelman_ongrid | 12 materials | 100.0% | — |
| Eligibility concordance at 0.01 e | henkelman_ongrid | 12 materials | 91.7% | — |
| A.1 floor agrees with BaderKit within 1e-6 e | henkelman_neargrid | 12 materials | 0.0% | — |
| Eligibility concordance at 0.0001 e | henkelman_neargrid | 12 materials | 83.3% | — |
| Eligibility concordance at 0.001 e | henkelman_neargrid | 12 materials | 91.7% | — |
| Eligibility concordance at 0.01 e | henkelman_neargrid | 12 materials | 91.7% | — |

Codec-response ratios above use successful paired outputs above the 2e-6 e Henkelman print-resolution region. The additional on-grid baseline-compatible row requires the unperturbed Henkelman/BaderKit atomic charges to agree within 1e-3 e. All paired points, including flagged baseline differences, remain in `supplement/S11_cross_implementation_pairs.csv`.

### S11c. Relative 1e-4 codec-response ordering by implementation

| Solver | Error ratio | n materials | Median ratio | IQR |
|---|---|---:|---:|---:|
| baderkit_ongrid | SZ3/ZFP | 12 | 6.18× | 3.35–12.81× |
| baderkit_ongrid | SPERR/ZFP | 12 | 6.69× | 2.65–13.36× |
| henkelman_ongrid | SZ3/ZFP | 12 | 4.83× | 2.54–6.97× |
| henkelman_ongrid | SPERR/ZFP | 12 | 5.45× | 1.32–6.95× |
| henkelman_neargrid | SZ3/ZFP | 12 | 3.17× | 1.23–10.62× |
| henkelman_neargrid | SPERR/ZFP | 12 | 2.87× | 0.92–8.52× |

### S11d. Exact BaderKit decomposition by perturbation kind

| Perturbation kind | n | Median bounded domain share | IQR | Domain > integrand | Max closure residual (e) |
|---|---:|---:|---:|---:|---:|
| codec | 70 | 0.9898 | 0.9573–0.9991 | 100.0% | 0.0e+00 |
| float32 | 12 | 0.0208 | 0.0096–0.9999 | 41.7% | 0.0e+00 |
| noise | 60 | 0.9999 | 0.9990–1.0000 | 83.3% | 0.0e+00 |
| spatial_control | 324 | 0.9961 | 0.9843–0.9995 | 100.0% | 0.0e+00 |

### S11e. Spatial reorganization controls

| Solver | Control | n pairs | Median log2(control/codec) | IQR | Fraction increased |
|---|---|---:|---:|---:|---:|
| baderkit_ongrid | global | 36 | 0.26 | -0.17–0.81 | 52.8% |
| baderkit_ongrid | shift | 36 | 0.02 | -0.29–0.63 | 50.0% |
| baderkit_ongrid | stratified | 36 | 0.26 | -0.07–0.72 | 63.9% |
| henkelman_ongrid | global | 36 | 0.24 | -0.14–0.79 | 61.1% |
| henkelman_ongrid | shift | 36 | 0.04 | -0.17–0.66 | 55.6% |
| henkelman_ongrid | stratified | 36 | 0.15 | -0.15–0.69 | 61.1% |
| henkelman_neargrid | global | 36 | 0.07 | -0.36–0.74 | 50.0% |
| henkelman_neargrid | shift | 36 | 0.00 | -0.27–0.46 | 50.0% |
| henkelman_neargrid | stratified | 36 | 0.07 | -0.24–0.47 | 55.6% |

**Interpretation boundary.** This deliberately stratified 12-system panel is a mechanism/implementation robustness study, not a prevalence estimate. Henkelman on-grid reproduces the BaderKit codec response essentially one-for-one above print resolution, and the strict SZ3/ZFP and SPERR/ZFP ordering remains qualitatively similar under on-grid and near-grid Henkelman analyses. The exact decomposition supports a Bader-specific domain-migration channel. Spatial permutations provide secondary evidence that error organization matters, while the near-null periodic-shift control argues against a simple alignment-only explanation. These results do not redefine Protocol A.1 or alter the primary benchmark.

**Sources:** `mechanism/independent_bader_20260908/outcomes/*.jsonl`; `stability_comparison.csv`; `mechanism_domain_decomposition.csv`; `mechanism_spatial_pairs.csv`; protocol/scope in `mechanism/independent_bader_20260908/README.md`.
