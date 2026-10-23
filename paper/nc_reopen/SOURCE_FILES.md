# Source files for every number in the main text and SI

Every number in the main text and this SI comes from the files below (commit that last changed each file). Protocols, manifests, per-material tables and the register of every protocol with its outcome are in the same repository.

| content | file | commit |
|---|---|---|
| QSQ fresh-perturbation test | `analysis/research_upgrade/p2_fresh_probe_cohort_summary.csv` | `b75a493` |
| QSQ equal-search control | `analysis/research_upgrade/p1_common_tight_summary.csv` | `f3a10ab` |
| QSQ validations (Supplementary Note 1) | frozen manuscript and SI, `paper/MANUSCRIPT.md` and `paper/SUPPLEMENTARY_INFORMATION.md` | `efd1e2c` |
| Hartree spectral audit | `analysis/hartree_spectral_mechanism/results/REPORT.md` | `dc2b167` |
| QOAC-H mechanism ablation | `analysis/operator_aware_codec_hartree/results/SUMMARY.json` | `a1351d1` |
| QOAC-H disjoint confirmation | `analysis/operator_aware_codec_hartree_v02_confirmatory/results/RESULTS.md` | `31def38` |
| QOAC-H census | `analysis/operator_aware_codec_hartree_v02_census/results/RESULTS.md` | `cc5d7a1` |
| strongest baselines | `analysis/qoac_h_strong_baselines/results/RESULTS.md` | `0c8b550` |
| basin projection holdout | `analysis/operator_aware_bader_projection_confirmatory/results/SUMMARY.json` | `8e4b5e8` |
| basin projection engineering | `analysis/operator_aware_bader_projection/results/RESULTS.md` | `892bedb` |
| partition transcription and storage | `analysis/qoac_b3_design/results/real_engineering/RESULTS.md` | `01a3d54` |
| law protocol, P1 | `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/SUMMARY.json` | `4164519` |
| law protocol, P3b | `analysis/general_qoac_law/results/run_P3B_CONFIRMATORY/SUMMARY.json` | `eaa3267` |
| law protocol, summary | `analysis/general_qoac_law/results/RESULTS.md` | `b9fd735` |
| QoI-preserving baselines QPET and MGARD, P1 and P3b | `analysis/hartree_baselines_mgard_qpet_20261007/RESULTS.md`; per material `analysis/hartree_baselines_mgard_qpet_20261007/results/run_P1_CONFIRMATORY/material.csv`, `analysis/hartree_baselines_mgard_qpet_20261007/results/run_P3B_CONFIRMATORY/material.csv` | `a86be8b` |
| Materials Project archive estimate | `analysis/extensions_20260930/WP-F/results_cloud/completed_v2/RESULTS.md`; estimates `analysis/extensions_20260930/WP-F/results_cloud/completed_v2/estimates.csv`; protocol `analysis/extensions_20260930/PROTOCOL.md` (WP-F) | `805747f` |
| Materials Project archive estimate, Hartree contract (main text, Table 1, Supplementary Note 3.4) | `analysis/archive_hartree_law_20261012/results/RESULTS.md`; estimates `analysis/archive_hartree_law_20261012/results/estimates.csv`, per stratum `analysis/archive_hartree_law_20261012/results/strata_results.csv`, per object `analysis/archive_hartree_law_20261012/results/objects.csv`; protocol `analysis/archive_hartree_law_20261012/PROTOCOL.md` | `81ba218` |
| work-function error on P3b slabs | `analysis/p3b_vacuum_level_20261007/RESULTS.md`; per stream `analysis/p3b_vacuum_level_20261007/results/per_slab_dphi.csv`, summary `analysis/p3b_vacuum_level_20261007/results/summary.csv` | `6f03249` |
| best QPET host and input precision | `paper/nc_reopen/derived/qpet_best_host.csv` (from `paper/nc_reopen/derive_qpet_best_host.py`) | `9557d1f` |
| self-contained joint storage, confirmation | `analysis/hb_selfcontained_bytes_20261012/RESULTS.md`; per material `analysis/hb_selfcontained_bytes_20261012/results/materials.csv` | `904fdc9` |
| deployment cost, run (Table 2, Supplementary Note 3.3) | `analysis/deployment_cost_20261012/results/RESULTS.md`, `analysis/deployment_cost_20261012/results/SUMMARY.json`; per material `analysis/deployment_cost_20261012/results/per_material.csv`; protocol `analysis/deployment_cost_20261012/PROTOCOL.md` | `2ee1dab` |
| deployment cost, Table 2 and Supplementary Note 3.3 tables | `paper/nc_reopen/derived/deployment_cost_table.csv`, `paper/nc_reopen/derived/deployment_cost_si.md` (from `paper/nc_reopen/derive_deployment_table.py`, `paper/nc_reopen/derive_deployment_si.py`) | `0c1e339` |
| pooled prediction statistics | `analysis/general_qoac_law/results/POOLED_P1_P3B.json` | `062d782` |
| predictor calibration | `analysis/general_qoac_operators/results/RESULTS.md` | `f4baa7a` |
| joint contract, engineering | `analysis/qoac_hb_v2/results/P2_ENGINEERING_MANIFEST/RESULTS.md` | `e095a0c` |
| joint contract, confirmation | `analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/RESULTS.md` | `56add26` |
| fresh populations | `analysis/fresh_population_20261006/REPORT.md` | `708dd37` |
| P3b rule | `analysis/fresh_population_20261006/P3B_SELECTION_RULE.md` | `39ba728` |

| FFCz Hartree comparator (P1/P3b, all three tolerances) | `analysis/hartree_baseline_ffcz_20261012/results/RESULTS.md`; `analysis/hartree_baseline_ffcz_20261012/results/summary.csv`; `analysis/hartree_baseline_ffcz_20261012/DEVIATIONS.md` | `eaf7427` |
| Whole-object Hartree archive and decoded magnetic-moment certification | `analysis/scope_expansion_20261022/results/s2b_archive_hartree_decframe/SUMMARY.json`; `analysis/scope_expansion_20261022/results/s2d_archive_pointwise_decframe_1e-6/READING.md`; `analysis/scope_expansion_20261022/results/whole_object_estimates/TABLE.md` | `045d917` |
| Magnetic-moment contract and partition migration | `analysis/scope_expansion_20261022/results/s3_joint_contracts_v2/RESULTS.md`; `analysis/scope_expansion_20261022/results/s1_spin_engineering/RESULTS.md` | `045d917` |
| Codec order at matched density error (Supplementary Note 1.13, Supplementary Fig. 1) | `analysis/contract_codec_order_20261023/RESULTS.md`; `analysis/contract_codec_order_20261023/results/rank_reversal_summary.json`; `analysis/contract_codec_order_20261023/results/migration_coupling_summary.json`; per material `analysis/contract_codec_order_20261023/results/migration_coupling_per_material.csv`; figure `figures/nc/si/figS_order/make_figS_order.py` | `0a6ebf6` |
| Operational optimum and law against spectral truncation (Results; Supplementary Note 3, A3/A2 rows) | `paper/nc_reopen/derived/operational_vs_truncation.csv` (from `paper/nc_reopen/derive_operational_vs_truncation.py`, reading `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_material.csv` and `run_P3B_CONFIRMATORY/part_a_material.csv`) | `02da306` |
