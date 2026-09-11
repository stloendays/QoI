# Supplementary Table S12 | Realized-L∞ matching sensitivity across pre-specified calipers

Generated 2026-09-11 directly from `analysis/matched_realized_linf_v1/matching_diagnostics.csv` and `matched_effects_summary.csv`. The primary analysis uses a 0.10-dex caliper; 0.05, 0.20 and 0.30 dex are pre-specified sensitivity analyses.

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

**Interpretation boundary.** Matching controls realized maximum perturbation, not the full geometry of the codec error field. A residual codec effect after matching is consistent with an error-structure contribution but does not identify a unique spatial invariant. Fixed-basin effects are diagnostic because fixed domains change the downstream operator.

**Machine-readable submission source:** `supplement/S12_matching_sensitivity.csv`.
