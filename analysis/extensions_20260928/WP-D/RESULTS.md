# WP-D — Predicting non-evaluability from reference-density descriptors

Question: can the QSQ stability floor f_m be anticipated from cheap properties of the reference density and grid?

## Population

- Systems with complete descriptors: **318 / 319** (dev 254: bulk 186, slab 68; ext 64: bulk 36, vacuum2d 28).
- Failures recorded in `failures.csv`: **1**.
- Eligible (f_m < 1e-4 e): 64 / 318 (dev 46 / 254, ext 18 / 64).
- Eligible (f_m < 1e-3 e): 187 / 318 (dev 143 / 254, ext 44 / 64).
- Eligible (f_m < 1e-2 e): 287 / 318 (dev 229 / 254, ext 58 / 64).
- Target range: log10 f_m from -8.07 to 0.46 (f_m in e).
- Feature preprocessing notes: systems without any basin boundary (gap percentiles imputed with column maximum, lt1 fraction = 0): 2; systems with rho_median clipped for eps/median: 1.

## (a) Univariate Spearman ρ with log10 f_m (material bootstrap, 2,000 resamples, seed 20260928)

| rank | descriptor | group | n | ρ | 95% CI |
|---:|---|---:|---:|---:|---|
| 1 | `boundary_gap_lt1_fraction` | 3 | 316 | 0.554 | [0.463, 0.639] |
| 2 | `boundary_gap_p05_over_eps` | 3 | 316 | -0.332 | [-0.440, -0.227] |
| 3 | `near_tie_fraction_lt_0p1eps` | 4 | 318 | 0.246 | [0.140, 0.347] |
| 4 | `near_tie_fraction_lt_eps` | 4 | 318 | 0.219 | [0.112, 0.325] |
| 5 | `boundary_gap_p95_over_eps` | 3 | 316 | -0.213 | [-0.314, -0.105] |
| 6 | `min_basin_voxels` | 5 | 318 | 0.175 | [0.059, 0.299] |
| 7 | `is_vacuum2d` | 1 | 318 | -0.165 | [-0.255, -0.066] |
| 8 | `max_axis_grid_spacing_A` | 1 | 318 | -0.158 | [-0.264, -0.049] |
| 9 | `mean_grid_spacing_A` | 1 | 318 | -0.148 | [-0.260, -0.038] |
| 10 | `npoints` | 1 | 318 | 0.146 | [0.041, 0.250] |
| 11 | `boundary_gap_p50_over_eps` | 3 | 316 | -0.128 | [-0.239, -0.017] |
| 12 | `is_slab` | 1 | 318 | 0.124 | [0.025, 0.217] |
| 13 | `n_basins_lt_100_voxels` | 5 | 318 | -0.124 | [-0.239, -0.010] |
| 14 | `cell_aspect_ratio` | 1 | 318 | -0.111 | [-0.216, -0.003] |
| 15 | `min_basin_charge_e` | 5 | 318 | 0.107 | [0.002, 0.222] |
| 16 | `n_axis_order_flips_noise_seed20260905` | 6 | 318 | 0.104 | [-0.006, 0.214] |
| 17 | `eps_m` | 2 | 318 | 0.083 | [-0.023, 0.196] |
| 18 | `eps_over_rho_max` | 2 | 318 | -0.074 | [-0.186, 0.037] |
| 19 | `eps_over_rho_median` | 2 | 317 | -0.057 | [-0.168, 0.061] |
| 20 | `boundary_fraction` | 3 | 318 | -0.027 | [-0.139, 0.081] |
| 21 | `natoms` | 1 | 318 | 0.027 | [-0.089, 0.139] |
| 22 | `vacuum_fraction` | 1 | 318 | 0.026 | [-0.084, 0.133] |

Top three (groups 1–5) by |ρ|: `boundary_gap_lt1_fraction`, `boundary_gap_p05_over_eps`, `near_tie_fraction_lt_0p1eps`.

## (b) Ridge regression of log10 f_m on standardized descriptors (groups 1–5), α by inner 5-fold CV, 10-fold outer CV over systems

| model | subset | n | R² | 95% CI | RMSE (decades) | 95% CI |
|---|---|---:|---:|---|---:|---|
| ridge_groups1-5_cv10 | all | 318 | 0.238 | [0.048, 0.368] | 0.932 | [0.809, 1.062] |
| ridge_groups1-5_cv10 | dev | 254 | 0.257 | [0.166, 0.341] | 0.851 | [0.723, 0.981] |
| ridge_groups1-5_cv10 | ext | 64 | 0.147 | [-0.625, 0.497] | 1.199 | [0.882, 1.528] |
| ridge_groups1-5_cv10 | bulk | 222 | 0.190 | [-0.036, 0.344] | 1.057 | [0.909, 1.215] |
| ridge_groups1-5_cv10 | slab | 68 | 0.626 | [0.468, 0.730] | 0.412 | [0.352, 0.473] |
| ridge_groups1-5_cv10 | vacuum2d | 28 | -0.079 | [-0.811, 0.345] | 0.764 | [0.520, 0.989] |
| ridge_groups1-5_cv10 | slab_or_vacuum2d | 96 | 0.501 | [0.235, 0.671] | 0.539 | [0.432, 0.649] |
| ridge_groups1-5_cv10 | dev_bulk | 186 | 0.197 | [0.091, 0.282] | 0.963 | [0.819, 1.116] |
| ridge_groups1-5_cv10 | dev_slab | 68 | 0.626 | [0.468, 0.730] | 0.412 | [0.352, 0.473] |
| ridge_groups1-5_cv10 | ext_bulk | 36 | 0.167 | [-0.872, 0.539] | 1.449 | [0.987, 1.880] |
| ridge_groups1-5_cv10 | ext_vacuum2d | 28 | -0.079 | [-0.811, 0.345] | 0.764 | [0.520, 0.989] |
| ridge_groups1-6_diagnostic_cv10 | all | 318 | 0.234 | [0.049, 0.363] | 0.934 | [0.811, 1.067] |
| ridge_groups1-6_diagnostic_cv10 | dev | 254 | 0.250 | [0.154, 0.336] | 0.855 | [0.726, 0.987] |
| ridge_groups1-6_diagnostic_cv10 | ext | 64 | 0.148 | [-0.604, 0.504] | 1.198 | [0.887, 1.516] |
| ridge_groups1-6_diagnostic_cv10 | bulk | 222 | 0.183 | [-0.042, 0.340] | 1.062 | [0.913, 1.220] |
| ridge_groups1-6_diagnostic_cv10 | slab | 68 | 0.643 | [0.503, 0.738] | 0.402 | [0.344, 0.462] |
| ridge_groups1-6_diagnostic_cv10 | vacuum2d | 28 | -0.075 | [-0.854, 0.351] | 0.762 | [0.510, 0.990] |
| ridge_groups1-6_diagnostic_cv10 | slab_or_vacuum2d | 96 | 0.511 | [0.239, 0.684] | 0.533 | [0.425, 0.645] |
| ridge_groups1-6_diagnostic_cv10 | dev_bulk | 186 | 0.186 | [0.080, 0.273] | 0.970 | [0.821, 1.126] |
| ridge_groups1-6_diagnostic_cv10 | dev_slab | 68 | 0.643 | [0.503, 0.738] | 0.402 | [0.344, 0.462] |
| ridge_groups1-6_diagnostic_cv10 | ext_bulk | 36 | 0.168 | [-0.823, 0.543] | 1.449 | [0.999, 1.870] |
| ridge_groups1-6_diagnostic_cv10 | ext_vacuum2d | 28 | -0.075 | [-0.854, 0.351] | 0.762 | [0.510, 0.990] |

Outer-fold α values (groups 1–5): 5.62341, 1.77828, 31.6228, 100, 10, 17.7828, 31.6228, 31.6228, 5.62341, 56.2341. Full-population fit α = 56.2341; development-only fit α = 31.6228.

Standardized ridge coefficients (full-population fit, 319 systems), ranked by |coef|:

| rank | feature | raw descriptor | coef (all 319) | coef (dev 254) | rank (dev 254) |
|---:|---|---|---:|---:|---:|
| 1 | `boundary_gap_lt1_fraction` | `boundary_gap_lt1_fraction` | +0.214 | +0.217 | 3 |
| 2 | `log10_boundary_gap_p05_over_eps` | `boundary_gap_p05_over_eps` | -0.208 | -0.171 | 4 |
| 3 | `boundary_fraction` | `boundary_fraction` | +0.194 | +0.084 | 10 |
| 4 | `log10_eps_over_rho_median` | `eps_over_rho_median` | -0.182 | -0.219 | 2 |
| 5 | `log10_boundary_gap_p95_over_eps` | `boundary_gap_p95_over_eps` | -0.176 | -0.233 | 1 |
| 6 | `n_basins_lt_100_voxels` | `n_basins_lt_100_voxels` | -0.143 | -0.168 | 5 |
| 7 | `log10_npoints` | `npoints` | +0.120 | +0.146 | 8 |
| 8 | `log10_natoms` | `natoms` | +0.118 | +0.146 | 7 |
| 9 | `vacuum_fraction` | `vacuum_fraction` | +0.101 | +0.046 | 17 |
| 10 | `log10_eps_over_rho_max` | `eps_over_rho_max` | -0.080 | -0.079 | 11 |
| 11 | `is_vacuum2d` | `is_vacuum2d` | +0.076 | +0.000 | 21 |
| 12 | `is_slab` | `is_slab` | -0.075 | -0.006 | 20 |
| 13 | `log10_cell_aspect_ratio` | `cell_aspect_ratio` | -0.071 | -0.145 | 9 |
| 14 | `near_tie_fraction_lt_eps` | `near_tie_fraction_lt_eps` | +0.048 | +0.058 | 14 |
| 15 | `near_tie_fraction_lt_0p1eps` | `near_tie_fraction_lt_0p1eps` | +0.037 | +0.057 | 15 |
| 16 | `log10_min_basin_voxels_p1` | `min_basin_voxels` | -0.024 | -0.149 | 6 |
| 17 | `mean_grid_spacing_A` | `mean_grid_spacing_A` | -0.023 | +0.021 | 19 |
| 18 | `min_basin_charge_e` | `min_basin_charge_e` | -0.020 | +0.064 | 12 |
| 19 | `log10_boundary_gap_p50_over_eps` | `boundary_gap_p50_over_eps` | +0.015 | +0.052 | 16 |
| 20 | `log10_eps_m` | `eps_m` | +0.005 | -0.064 | 13 |
| 21 | `max_axis_grid_spacing_A` | `max_axis_grid_spacing_A` | +0.001 | -0.029 | 18 |

Top three ridge descriptors by |standardized coefficient| (all 319): `boundary_gap_lt1_fraction`, `boundary_gap_p05_over_eps`, `boundary_fraction`.

## (c) Logistic classification of eligibility (groups 1–5), C by inner 5-fold CV, 10-fold outer CV

| τ (e) | subset | n | n eligible | AUC | 95% CI |
|---|---|---:|---:|---:|---|
| 0.0001 | all | 318 | 64 | 0.770 | [0.705, 0.829] |
| 0.0001 | dev | 254 | 46 | 0.779 | [0.701, 0.845] |
| 0.0001 | ext | 64 | 18 | 0.715 | [0.571, 0.852] |
| 0.0001 | bulk | 222 | 52 | 0.749 | [0.670, 0.821] |
| 0.0001 | slab_or_vacuum2d | 96 | 12 | 0.750 | [0.589, 0.899] |
| 0.001 | all | 318 | 187 | 0.775 | [0.718, 0.830] |
| 0.001 | dev | 254 | 143 | 0.800 | [0.744, 0.853] |
| 0.001 | ext | 64 | 44 | 0.617 | [0.426, 0.797] |
| 0.001 | bulk | 222 | 125 | 0.785 | [0.718, 0.843] |
| 0.001 | slab_or_vacuum2d | 96 | 62 | 0.729 | [0.605, 0.846] |
| 0.01 | all | 318 | 287 | 0.804 | [0.717, 0.882] |
| 0.01 | dev | 254 | 229 | 0.739 | [0.622, 0.840] |
| 0.01 | ext | 64 | 58 | 0.980 | [0.933, 1.000] |
| 0.01 | bulk | 222 | 198 | 0.719 | [0.603, 0.829] |
| 0.01 | slab_or_vacuum2d | 96 | 89 | 0.978 | [0.941, 1.000] |

Operating points on out-of-fold probabilities (highest recall subject to the false-eligible constraint; FPR = false eligible / truly non-eligible, FDR = false eligible / predicted eligible):

| τ (e) | rule | threshold | TP | FP | FN | TN | precision | recall | FPR | FDR |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0001 | false_eligible_rate_FPR_le_5pct | 0.442 | 18 | 12 | 46 | 242 | 0.600 | 0.281 | 0.047 | 0.400 |
| 0.0001 | false_eligible_rate_FDR_le_5pct | 0.937 | 1 | 0 | 63 | 254 | 1.000 | 0.016 | 0.000 | 0.000 |
| 0.001 | false_eligible_rate_FPR_le_5pct | 0.856 | 22 | 6 | 165 | 125 | 0.786 | 0.118 | 0.046 | 0.214 |
| 0.001 | false_eligible_rate_FDR_le_5pct | inf | 0 | 0 | 187 | 131 | nan | 0.000 | 0.000 | 0.000 |
| 0.01 | false_eligible_rate_FPR_le_5pct | 0.944 | 108 | 1 | 179 | 30 | 0.991 | 0.376 | 0.032 | 0.009 |
| 0.01 | false_eligible_rate_FDR_le_5pct | 0.881 | 250 | 13 | 37 | 18 | 0.951 | 0.871 | 0.419 | 0.049 |

## (d) Held-out check: fit on the 254 development systems, evaluate on the 65 external systems

| model | τ (e) | metric | value | 95% CI | n external | n eligible external |
|---|---|---|---:|---|---:|---:|
| ridge_groups1-5_fit_dev254 |  | R2 | 0.134 | [-0.410, 0.385] | 64 |  |
| ridge_groups1-5_fit_dev254 |  | RMSE_decades | 1.208 | [0.967, 1.442] | 64 |  |
| ridge_groups1-5_fit_dev254 |  | R2_ext_bulk | 0.400 | [nan, nan] | 36 |  |
| ridge_groups1-5_fit_dev254 |  | RMSE_decades_ext_bulk | 1.230 | [nan, nan] | 36 |  |
| ridge_groups1-5_fit_dev254 |  | R2_ext_vacuum2d | -1.566 | [nan, nan] | 28 |  |
| ridge_groups1-5_fit_dev254 |  | RMSE_decades_ext_vacuum2d | 1.178 | [nan, nan] | 28 |  |
| logistic_groups1-5_fit_dev254 | 0.0001 | AUC | 0.710 | [0.561, 0.851] | 64 | 18 |
| logistic_groups1-5_fit_dev254 | 0.001 | AUC | 0.701 | [0.536, 0.849] | 64 | 44 |
| logistic_groups1-5_fit_dev254 | 0.01 | AUC | 0.940 | [0.868, 0.991] | 64 | 58 |

## Acceptance (applied literally)

- Held-out R² on the external 65 = 0.134 (95% CI [-0.410, 0.385]); rule requires ≥ 0.5 → **not met**.
- Top three in (a): ['boundary_gap_lt1_fraction', 'boundary_gap_p05_over_eps', 'near_tie_fraction_lt_0p1eps']; top three in ridge coefficients: ['boundary_gap_lt1_fraction', 'boundary_gap_p05_over_eps', 'boundary_fraction']; identical as sets → **no**.
- Verdict: **measured, not yet predictable**.

## Files

`descriptors.csv` (one row per system), `univariate.csv`, `cv_metrics.csv`, `coefficients.csv`, `external_holdout.csv`, `operating_points.csv`, `predictions.csv` (out-of-fold and hold-out predictions), `fig_predictor.{png,svg}`, `failures.csv`, `provenance.json`, `DEVIATIONS.md`. Compute: `compute_descriptors.py` → `aggregate.py` → `model.py`.

