# Reader-facing provenance index

This index maps stable scientific names used in the manuscript and Supplementary Information to exact repository artifacts. Internal schema/version identifiers are retained here for reproducibility but should not be used as scientific method names in reader-facing prose.

| Semantic manuscript name | Scientific role | Exact repository artifact |
|---|---|---|
| QSQ stability floors | Material-specific five-seed QoI Stability Qualification response | `stability/stability_floor_A1.csv` |
| QSQ per-seed responses | Seed-resolved responses underlying QSQ floors | `stability/stability_floor_A1_per_seed.csv` |
| QSQ eligibility summary | Threshold-specific evaluability by material and stratum | `stability/eligibility_summary_A1.csv` |
| QSQ eligibility table | Material-threshold eligibility decisions | `stability/eligibility_by_threshold_A1.csv` |
| QSQ-certified benchmark summary | Certified compression ratios and success fractions among eligible targets | `benchmark/summary_a1.csv` |
| QSQ pairwise codec summary | Pairwise codec comparisons under QSQ eligibility | `benchmark/pairwise_a1.csv` |
| Best certified operating points | Highest-rate certified operating point by material/codec/contract | `benchmark/best_certified_a1.csv` |
| Archived order-preserving control | Superseded float32 round-trip stability control retained only for method validation/provenance | `stability/stability_floor_A_archived_float32.csv` |
| Probe calibration panel | Comparison of QSQ perturbations with the order-preserving control | `stability/probe_calibration.csv` |
| Prospective QSQ validation | Fresh-perturbation validation of the pre-specified QSQ screen | `validation/qsq_prospective/p2_fresh_probes/` |
| Implementation-transfer panel | Independent Bader implementation transfer analysis | `validation/qsq_prospective/p3a_implementation_transfer_resolved/` |
| Chemical-decision boundary case | Outcome-blind qualitative charge-transfer case study | `validation/qsq_prospective/p4_chemical_decisions_resolved/` |
| Fourier-spectrum mechanism audit | Matched-distortion Hartree spectral mechanism tables and checks | `analysis/hartree_spectral_mechanism/results/` |
| QOAC-H operator-derived codec | Reader-facing Hartree-specific transform codec implementation | `analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py` |
| QOAC-H mechanism ablation | Frozen operator-derived versus operator-blind allocation experiment | `analysis/operator_aware_codec_hartree/results/` |
| QOAC-H implementation audit | Hermitian, Nyquist, rate-accounting and decoded-field sanity checks | `analysis/operator_aware_codec_hartree_v02/SANITY_AUDIT.md` |
| QOAC-H disjoint confirmation | Frozen 48-material confirmatory cohort, per-material results and summary | `analysis/operator_aware_codec_hartree_v02_confirmatory/results/` |
| QOAC-H full-population census | 254-material, 6,350-setting Hartree tolerance census | `analysis/operator_aware_codec_hartree_v02_census/results/` |
| Realized-distortion matching | Within-material codec matching on measured reconstruction distortion | `analysis/matched_realized_linf_v1/` |
| External confirmation | Untouched external cohort scored with the same QSQ/certification rules | `validation/final_external_confirmatory63_20260908/confirmatory63/` |

## Terminology mapping

- Reader-facing qualification method: **QoI Stability Qualification (QSQ)**.
- Reader-facing Hartree compression method: **QoI- and operator-aware Hartree compression (QOAC-H)**.
- Reader-facing quantities: **QSQ stability floor**, **QSQ eligibility**, **QSQ-certified operating point**.
- Historical identifiers such as `Protocol A`, `Protocol A.1`, `A1`, and filenames containing `_A1` are implementation/provenance identifiers only.
- The **archived order-preserving control** is not an active qualification method.

## Canonical manuscript artifacts

- Main manuscript: `paper/MANUSCRIPT.md`
- Supplementary Information: `paper/SUPPLEMENTARY_INFORMATION.md`
- Current scientific story: `paper/CURRENT_PAPER_STORY.md`
- Claim-evidence matrix: `paper/CLAIM_EVIDENCE_MATRIX.md`
- Figure map: `paper/FIGURE_MAP.md`


## QOAC-H provenance boundary

Reader-facing prose must use **QOAC-H** without internal development-version labels. Repository directories containing `v02` are provenance identifiers only. The scientific evidence hierarchy is:

`Hartree Fourier mechanism -> operator-derived allocation -> 12-material ablation -> 48-material disjoint confirmation -> 254-material census`.

The 48-material cohort is the independent confirmatory sample. The 254-material result is an exhaustive development-population census and must not be described as external confirmation.
