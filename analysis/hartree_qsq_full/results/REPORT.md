# Full-population Hartree-QSQ generality study

Status: **GO_FULL_POPULATION_GENERALITY_SUPPORTED**

## Accounting

- Planned materials: **254**
- Reference-complete materials: **254**
- Five-seed Hartree-QSQ measurements: **1270**
- Reconstructed codec rows: **6343**
- Scientific reproduction-gate pass rows: **6342**
- Scientific reproduction-gate fail rows: **1**
- Materials with source/reference failure: **0**

## Primary Hartree-QSQ contract

At relative-RMSE tau = 1e-06, **254/254 = 100.0%** of the planned development cohort is reference-qualified (missing reference measurements counted conservatively as not eligible).

## Smoothness by codec

| Codec | series (>=4 points) | monotone | median R2 | median slope | GO checks |
|---|---:|---:|---:|---:|---|
| ZFP | 243 | 85.2% | 0.997 | 1.047 | PASS |
| SZ3 | 235 | 84.7% | 0.994 | 1.171 | PASS |
| SPERR | 227 | 95.6% | 0.996 | 1.012 | PASS |

## Matched realized L-infinity control

Primary caliper: 0.10 dex, within material, without replacement.

| Pair | matched pairs | materials | Hartree ratio A/B | Hartree median |log10 ratio| | Bader ratio A/B | Bader median |log10 ratio| |
|---|---:|---:|---:|---:|---:|---:|
| SZ3/SPERR | 1847 | 254 | 6.768 [6.162, 7.613] | 0.865 | 1.033 [0.978, 1.073] | 0.166 |
| ZFP/SPERR | 465 | 206 | 0.670 [0.639, 0.741] | 0.229 | 0.601 [0.534, 0.670] | 0.286 |
| ZFP/SZ3 | 457 | 214 | 0.078 [0.070, 0.084] | 1.108 | 0.557 [0.525, 0.597] | 0.258 |

## Interpretation boundary

The study is an additive operator-generality extension. It does not automatically alter the frozen manuscript, P1-P4 evidence hierarchy, or submission artifacts.

A GO means the pre-specified population-level numerical criteria were met; it does not make the Hartree relative-RMSE ladder a universal chemical tolerance.
