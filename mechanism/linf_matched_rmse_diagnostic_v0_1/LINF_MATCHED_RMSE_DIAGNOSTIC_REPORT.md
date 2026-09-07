# L-infinity-matched RMSE balance diagnostic v0.1

Frozen input: `benchmark/master_benchmark_full.csv` (blob `633c7b2ee1b9b800382a5d0d9cfbdc9e1dc793b7`).

A 95% CI for RMSE A/B that excludes 1 means the L-infinity-only matched comparison remains scalar-amplitude imbalanced.

| caliper | contrast | materials | pairs | Bader error A/B [95% CI] | matched L-inf A/B | matched RMSE A/B [95% CI] | shape-factor A/B | RMSE balanced? |
|---:|---|---:|---:|---|---:|---|---:|---|
| 0.05 | ZFP/SZ3 | 147 | 198 | 0.583 [0.549, 0.639] | 1.02 | 0.378 [0.361, 0.389] | 0.365 | no |
| 0.05 | ZFP/SPERR | 143 | 208 | 0.602 [0.508, 0.707] | 1.02 | 0.433 [0.418, 0.438] | 0.423 | no |
| 0.05 | SZ3/SPERR | 254 | 1848 | 1.03 [0.977, 1.07] | 1 | 1.29 [1.27, 1.3] | 1.29 | no |
| 0.10 | ZFP/SZ3 | 214 | 457 | 0.557 [0.523, 0.599] | 1.05 | 0.376 [0.365, 0.382] | 0.346 | no |
| 0.10 | ZFP/SPERR | 206 | 465 | 0.601 [0.534, 0.664] | 1.06 | 0.437 [0.426, 0.448] | 0.416 | no |
| 0.10 | SZ3/SPERR | 254 | 1848 | 1.03 [0.977, 1.07] | 1 | 1.29 [1.27, 1.3] | 1.29 | no |
| 0.20 | ZFP/SZ3 | 244 | 1089 | 0.591 [0.565, 0.621] | 1.16 | 0.372 [0.365, 0.379] | 0.304 | no |
| 0.20 | ZFP/SPERR | 245 | 1091 | 0.591 [0.558, 0.624] | 1.15 | 0.447 [0.433, 0.466] | 0.395 | no |
| 0.20 | SZ3/SPERR | 254 | 1848 | 1.03 [0.978, 1.07] | 1 | 1.29 [1.27, 1.3] | 1.29 | no |
| 0.30 | ZFP/SZ3 | 248 | 1621 | 0.599 [0.568, 0.625] | 1.22 | 0.378 [0.369, 0.388] | 0.292 | no |
| 0.30 | ZFP/SPERR | 248 | 1622 | 0.6 [0.574, 0.651] | 1.2 | 0.456 [0.434, 0.479] | 0.386 | no |
| 0.30 | SZ3/SPERR | 254 | 1848 | 1.03 [0.977, 1.07] | 1 | 1.29 [1.27, 1.3] | 1.29 | no |

## Primary 0.10-dex interpretation

- **ZFP/SZ3**: RMSE remains imbalanced after L-infinity matching (0.376, 95% CI 0.365–0.382); the residual Bader contrast cannot be uniquely assigned to spatial geometry.
- **ZFP/SPERR**: RMSE remains imbalanced after L-infinity matching (0.437, 95% CI 0.426–0.448); the residual Bader contrast cannot be uniquely assigned to spatial geometry.
- **SZ3/SPERR**: RMSE remains imbalanced after L-infinity matching (1.29, 95% CI 1.27–1.3); the residual Bader contrast cannot be uniquely assigned to spatial geometry.
