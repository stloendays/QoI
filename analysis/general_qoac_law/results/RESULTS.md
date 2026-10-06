# General-QOAC law — prospective confirmation results

Protocol `DESIGN.md`, frozen in `fe2e08a`. Predictions for all 72 P1 materials were committed in `d5fc30b` before the
compression run (CI run 37488577302) started. Population: 60 fresh Materials Project bulk materials never used in
the project (`P1_CONFIRMATORY_MANIFEST.csv`); 12 shakedown materials reported separately. **0 pipeline failures.** Every
stream is decode-verified.

## Verdict: every pre-registered criterion passes

| criterion | result (60 materials, tau = 1e-6) | threshold | pass |
|---|---|---|---|
| A validity | A1 and A3 certified 60/60 | >= 58 | yes |
| A-H1 closed-form law near the operational optimum | median CR_A3/CR_A1 **1.105**, 95% CI [1.090, 1.146] | <= 1.15, CI upper <= 1.20 | yes |
| A-H2 operator metric essential | CR_A3/CR_A5 **2.12**, CI [1.92, 2.46], 60/60 | > 1.5, CI lower > 1.35, >= 90% | yes |
| A-H3 law vs pointwise codecs (equal search) | CR_A1/CR_A6 **10.2**, CI [9.13, 12.09], 60/60 | > 4, >= 95% | yes |
| A-H4 law vs spectral truncation (equal search) | CR_A1/CR_A2 **1.32**, CI [1.27, 1.35], 52/60 | > 1.15, >= 75% | yes |
| B validity | all opt and blind arms certified, 60/60 | >= 58 | yes |
| B-H1 calibration | median abs ln(G_pred/G_obs) **0.024** over 300 pairs | <= ln 1.25 = 0.223 | yes |
| B-H2 ranking | Spearman **0.978** | >= 0.85 | yes |
| B-H3 operator ordering | all pairs ordered as predicted | — | yes |
| B-H4 null-gain operators | gradient 100%, Laplacian 98.3% within [0.90, 1.11] | >= 80% | yes |
| control | density G_obs = 1 | = 1 | yes |

## Part B — predicted vs measured gain (medians, tau = 1e-6)

| operator | G_pred | G_obs | median abs log error |
|---|---|---|---|
| density (control) | 1 | 1 | 0 |
| density gradient | 1.014 | 1.011 | 0.006 |
| density Laplacian | 1.040 | 1.042 | 0.012 |
| Hartree field | 1.151 | 1.149 | 0.014 |
| Hartree potential | 2.72 | 2.61 | 0.078 |
| Gaussian-smoothed density, sigma = 0.5 A | 17.6 | 12.1 | 0.431 |

At tau = 1e-4 the predictor remains calibrated (pooled median abs log error 0.034, Spearman 0.944; Hartree potential
1.56 predicted vs 1.44 measured; Gaussian 2.68 vs 2.02). The largest miss in both regimes is the Gaussian operator,
whose gain the predictor overstates by 1.3–1.5x.

## Part A across tolerances (medians, descriptive)

| ratio | tau 1e-4 | tau 1e-6 | tau 1e-8 |
|---|---|---|---|
| A3/A1 (operational optimum / closed-form law) | 1.58 | 1.10 | 1.03 |
| A3/A5 (operator metric / blind metric, both optimal) | 1.33 | 2.12 | 1.60 |
| A1/A6 (law / pointwise codecs, equal search) | 9.10 | 10.2 | 3.30 |
| A1/A2 (law / truncation, equal search) | 0.79 | 1.32 | 1.59 |
| A3/A0 (optimum / frozen-ladder v0.2) | 1.71 | 1.33 | 1.16 |

The closed-form law is near-optimal at tight tolerances. At the loose tolerance (1e-4) finite-rate allocation is worth
1.58x, and spectral truncation beats the pure power law.

## Shakedown cohort (12 P1 engineering materials; not part of any criterion)

All Part B criteria hold (median abs log error 0.024, Spearman 0.979). Part A: A3/A1 = 1.156, just above the H1 line;
A3/A5 = 2.26, A1/A6 = 9.80, A1/A2 = 1.24.

## Scope

60 bulk materials from one database (Materials Project). Slabs were not part of this cohort (no fresh slab pool was
feasible under the frozen WS-0 rule).
