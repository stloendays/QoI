# Supplementary Tables S1–S4

Submission-facing first-pass tables for the certifiability manuscript. Numerical values are copied only from frozen repository sources listed beneath each table. These tables are intended to be consumed by the final Word/PDF build; machine-readable files remain the source of record.

---

## Supplementary Table S1 | Analysis cohorts and denominator conventions

| Analysis universe | Domain / stratum | Systems, n | Reconstruction rows | Primary use |
|---|---|---:|---:|---|
| Development benchmark | bulk | 186 | included in 6,343 total | codec benchmark, controls, reclassification, matching |
| Development benchmark | slab | 68 | included in 6,343 total | codec benchmark, controls, reclassification, matching |
| **Development benchmark total** | — | **254** | **6,343** | primary development analysis |
| External stability/descriptive set | bulk | 37 | included in 1,755 descriptive total | QSQ external stability/descriptive analysis |
| External stability/descriptive set | vacuum-containing 2D | 28 | included in 1,755 descriptive total | QSQ external stability/descriptive analysis |
| **External descriptive total** | — | **65** | **1,755** | frozen external descriptive aggregate |
| **Combined stability universe** | development + external descriptive | **319** | not a codec-row denominator | QSQ stability-floor / eligibility summaries |
| **Primary external confirmatory cohort** | frozen confirmatory subset | **63** | **1,689 retained scientific rows** | untouched rate–fidelity confirmation |

**Caption.** The study uses several deliberately distinct analysis universes. The 254-system development benchmark underlies the 6,343-row compression table and the central binary-to-three-state reclassification. QoI Stability Qualification (QSQ) summaries use 319 systems, comprising the 254 development systems plus all 65 records in the frozen external descriptive/stability set. The primary external rate–fidelity confirmation is a separately frozen 63-system cohort with 1,689 retained scientific rows. The 65-system external descriptive aggregate contains 1,755 rows. Denominators are therefore analysis-specific and are not interchangeable.

**Sources:** `benchmark/master_benchmark_full.csv`; `stability/eligibility_summary_A1.csv`; `external_test_MANIFEST.json`; `validation/EXTERNAL_CONFIRMATORY63_20260908.md`.

---

## Supplementary Table S2 | Frozen stability-qualification definition and archived probe

| Property | Archived float32 probe | QSQ perturbation probe |
|---|---|---|
| Status | **ARCHIVED / PROVENANCE ONLY** | **FROZEN / CURRENT** |
| Stability perturbation | float64 → float32 → float64 round trip | additive uniform noise \(U(-\epsilon,+\epsilon)\) |
| Perturbation amplitude | implicit float32 round-trip amplitude | \(\epsilon\) equals that material's measured float32 \(L_\infty\) round-trip error |
| Seeds | deterministic; not applicable | five pre-registered seeds: 20260905, 1, 2, 3, 4 |
| Stability floor | one deterministic response | maximum Bader response across five seeds |
| Bader basins | BaderKit, on-grid, re-derived | unchanged |
| Scientific thresholds | \(10^{-4}\), \(10^{-3}\), \(10^{-2}\,e\) | unchanged |
| Non-evaluable rule | floor \(\ge\tau\) | unchanged |
| Non-evaluable semantics | neither pass nor failure | unchanged |
| Reason for replacement | round trip is order-preserving and unusually benign to on-grid watershed ordering | non-order-preserving perturbation can excite the relevant partition instability |
| Post-freeze role | provenance only | defines all current eligibility and certification statistics |

**Calibration evidence supporting QSQ.** In the 18-material calibration panel, the archived float32 perturbation created a median of 82 exact neighbouring ties and reassigned zero voxels in 9/18 systems. The QSQ noise probe created no exact ties and reassigned zero voxels in only 2/18 systems. Across five seeds, the material-wise log10 floor span had a median of 0.47 decades and reached 2.4 decades. Over the ×0.1 to ×10 amplitude sweep, the floor changed by a median of 0.76 decades (P10 0.00; P90 2.02).

**Sources:** `protocol/PROTOCOL_A1.md`; `protocol/PROTOCOL_A_archived.md`; `stability/probe_calibration.csv`.

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

**Source:** `stability/eligibility_summary_A1.csv`.

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

**Source:** `analysis/certifiability_reclassification_by_codec_20260911.csv`.

---

## Build note

Tables S1–S4 are structurally ready for inclusion in the final Supplementary Information. Before Word/PDF assembly, they should be regenerated programmatically from the same sources so the formatted publication tables cannot drift from the machine-readable data. Historical protocol identifiers in source paths remain unchanged solely for provenance and reproducibility. No scientific interpretation in these tables depends on historical intermediate summaries.
