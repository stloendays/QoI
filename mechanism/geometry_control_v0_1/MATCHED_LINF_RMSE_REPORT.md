# Matched realized-L-infinity + RMSE control v0.1

This report implements the frozen analysis in `protocol/ERROR_GEOMETRY_CONTROL_V0_1_PREREGISTRATION.md`.
It is a development-corpus mechanistic sensitivity analysis and does not modify Protocol A.1 or the external confirmatory design.

**Primary decision rule:** NOT SUPPORTED.

Allowed interpretation if supported: the residual ZFP chemical-fidelity advantage is not explained by realized L-infinity or RMSE alone. This analysis is not, by itself, causal proof of spatial error geometry.

## Summary

| caliper | contrast A/B | materials | pairs | Bader error A/B [95% CI] | matched L-inf A/B | matched RMSE A/B | compression A/B | certification A-B at 0.01 e (pp) |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| 0.05 | ZFP/SZ3 | 0 | 0 | NA [NA, NA] | NA | NA | NA | NA [NA, NA] |
| 0.05 | ZFP/SPERR | 18 | 19 | 1.16 [0.768, 1.79] | 1.01 | 1.03 | 0.204 | 6.25 [0, 18.8] |
| 0.05 | SZ3/SPERR | 165 | 427 | 0.923 [0.873, 0.987] | 1 | 1.03 | 8.33 | 4.43 [0.819, 7.96] |
| 0.10 | ZFP/SZ3 | 0 | 0 | NA [NA, NA] | NA | NA | NA | NA [NA, NA] |
| 0.10 | ZFP/SPERR | 48 | 70 | 1.3 [1.09, 1.45] | 1.07 | 1 | 0.231 | -3.62 [-13, 4.71] |
| 0.10 | SZ3/SPERR | 185 | 822 | 0.91 [0.874, 0.94] | 1 | 1.12 | 6.07 | 3.71 [0.963, 6.27] |
| 0.20 | ZFP/SZ3 | 8 | 8 | 0.706 [0.471, 0.923] | 1.52 | 0.647 | 0.301 | 14.3 [0, 42.9] |
| 0.20 | ZFP/SPERR | 87 | 254 | 1.04 [0.888, 1.18] | 1.35 | 0.884 | 0.369 | -0.404 [-6.16, 5.2] |
| 0.20 | SZ3/SPERR | 214 | 1480 | 0.954 [0.921, 0.993] | 1 | 1.26 | 3.89 | 2.45 [0.819, 4.04] |
| 0.30 | ZFP/SZ3 | 185 | 335 | 0.738 [0.693, 0.803] | 1.66 | 0.545 | 0.513 | 6.14 [2.88, 9.8] |
| 0.30 | ZFP/SPERR | 219 | 945 | 0.798 [0.74, 0.849] | 1.56 | 0.606 | 2.27 | 3.73 [1.36, 6.09] |
| 0.30 | SZ3/SPERR | 251 | 1644 | 0.986 [0.949, 1.04] | 1 | 1.29 | 3.59 | 0.276 [-1.97, 2.29] |

## Scope guard

A residual after dual matching rules out two scalar summaries (max error and RMS error) as sufficient explanations. It does not uniquely identify spatial geometry because other distributional or spectral summaries are not fixed. The preregistered next mechanistic intervention is a within-residual spatial permutation that preserves the residual value multiset and therefore L-infinity, L1/L2, RMSE, mean and histogram while changing only spatial assignment (optionally within density strata).

## Provenance

- Frozen input Git blob: `633c7b2ee1b9b800382a5d0d9cfbdc9e1dc793b7`
- Primary caliper: `0.1` dex on both realized L-infinity and RMSE
- Bootstrap: `5000` material-level resamples
- Master seed label: `20260907`
