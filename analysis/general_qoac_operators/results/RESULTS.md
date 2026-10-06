# A-priori compression-gain predictors: retrospective calibration and operator prediction table

Status: **RETROSPECTIVE CALIBRATION.** The observed Hartree and electric-field ratios were known before the
predictors were written. Nothing here is a confirmation, and nothing changes a frozen gate or a frozen
number. The operator prediction table (section 3) covers operators without any compression run, and it is
not compared with one.

Population: the 12 engineering materials of `operator_aware_codec_hartree/results/PILOT_MANIFEST.csv`.
Predictions use only the orbit geometry (a), or the geometry plus the reference density spectrum (b). No
compression was run. Observations are the frozen per-material values:

- Hartree beta=2/beta=0: QOAC-H v0.1 pilot, historical metric (`mechanism_material.csv`, median 0.0767).
- E-field beta=1/beta=0 and beta=1/beta=2: v0.2, Nyquist-safe (`general_qoac_electric_field`).
- E-field optimal beta: beta map (`general_qoac_electric_field_beta_map`).

Predictor (b) is evaluated on the frozen alpha ladder (`logspace(-7, 1, 25) * ptp(rho)`) and summarized with
the same statistics as the observations. Ratios use greedy pairing within 0.05 dex of compression ratio and
the median over pairs. The optimal beta uses the beta-map common-rate interpolation with 11 targets. The
Hartree ladder mirrors the v0.1 container: Nyquist modes are stored exactly, and q is normalized over
non-Nyquist modes. Model compression ratio = raw bytes / (codec container bytes + ideal entropy bytes).
The container bytes (header, DC, zlib framing) depend only on the geometry. "(b) at tau = 1e-6" is the
single-target matched-rate ratio instead of the ladder median.

## 1. Calibration against the observed ratios

Log error = ln(predicted / observed) per material; rho = Spearman rank correlation across the 12 materials.

| quantity | observed median | predictor | predicted median | median \|log error\| | rho (p) | direction correct |
|---|---|---|---|---|---|---|
| Hartree beta2/beta0 | 0.0767 | (a) high-rate | 0.0496 | 0.362 | 0.94 (7e-6) | 12/12 |
| | | **(b) finite-rate, ladder** | **0.0832** | **0.148** | **0.96 (1e-6)** | 12/12 |
| | | (b) at tau = 1e-6 | 0.0825 | 0.169 | 0.95 (2e-6) | 12/12 |
| E-field beta1/beta0 | 0.806 | (a) high-rate | 0.783 | 0.037 | 0.71 (0.009) | 12/12 |
| | | **(b) finite-rate, ladder** | **0.790** | **0.021** | 0.58 (0.048) | 12/12 |
| | | (b) at tau = 1e-6 | 0.753 | 0.060 | 0.14 (0.66) | 12/12 |
| E-field beta1/beta2 | 0.928 | (a) high-rate | 0.913 | 0.021 | -0.49 (0.10) | 10/12 |
| | | **(b) finite-rate, ladder** | **0.922** | **0.018** | **0.52 (0.08)** | **12/12** |
| | | (b) at tau = 1e-6 | 0.992 | 0.068 | -0.42 (0.17) | — |

| E-field optimal beta (grid 0..2) | observed | (a) grid | (a) continuous | (b) beta-map mirror | (b) at tau = 1e-6 |
|---|---|---|---|---|---|
| median | 1.375 (range 1.0 – 2.0) | 1.0 | 1.03 | **1.5** | 1.5 |
| median \|error\| | — | 0.375 | 0.336 | **0.25** | 0.25 |
| within ±0.25 | — | 6/12 | 6/12 | **10/12** | — |
| rho | — | undefined (constant) | 0.15 | 0.45 (0.14) | -0.53 |

Closure: (a) for power laws reproduces the diagnosis D1 values in `diagnosis_material.csv` to 4e-15.

**The finite-rate predictor (b), applied on the frozen ladder, matches the observations. The high-rate
predictor (a) does not match them for the Hartree potential.**

- Hartree potential. (a) predicts a gain 1.4 times larger than observed in every material (median signed
  log error -0.36; worst mp-37207: 0.122 vs 0.256). (b) removes most of this bias: median 0.083 vs 0.077,
  median |log error| 0.15, and it ranks the materials almost perfectly (rho = 0.96). Slabs (0.02 – 0.05)
  and bulk (0.12 – 0.26) separate as observed. The largest remaining errors are 0.24 in log
  (nomad---3hBedCnC_e, predicted 0.046 vs 0.058) and 0.23 (mp-37207, 0.203 vs 0.256). In both, (b)
  predicts a larger gain than observed.
- E-field beta=1 vs beta=0. Both predictors are within 4% (median). (b) is closer in magnitude (2.1% vs
  3.7%). (a) ranks the materials better (rho 0.71 vs 0.58). For three NOMAD slabs observed at 0.864, both
  predict 0.79 (log error 0.09); this is the largest miss of (b).
- E-field beta=1 vs beta=2. (a) predicts beta=1 better in all 12 materials. The observed ratio exceeds 1 in
  mp-1188002 (1.010) and mp-22490 (1.054). (b) predicts exactly these two (1.033, 1.060), so it has the
  direction right in 12/12 and a positive rank correlation. (a) has a negative one.
- Optimal beta. (a) puts the optimum at 1.0 for every material. (b) moves it to 1.5 (11/12; 1.25 for
  nomad-19wSfSWChOSI), in line with the observed shift above 1 (median 1.375) and the diagnosis D4 slope
  estimate (1.56). (b) does not reproduce the per-material spread (observed 1.0 – 2.0; rho = 0.45, not
  significant).
- The single-target version of (b) at tau = 1e-6 is worse for the E-field than the ladder mirror. The
  observed statistics are medians over the whole frozen ladder, and the E-field gain depends on the rate
  regime: (b) gives beta1/beta0 = 0.78 at tau = 1e-8 and 0.75 at 1e-6. A predicted gain must therefore
  name the rate range it refers to.

Where the model itself is inaccurate:

- Absolute rate. Over the frozen E-field ladders (beta 0, 1, 2), the model compression ratio is off by a
  median of 0.068 dex (17%). The model overestimates the rate at the fine end (mp-1188002 at alpha_rel = 1e-7:
  CR 8.5 vs 17.9 observed). The variance-matched Laplacian has a higher entropy than the real,
  heavier-tailed coefficients within a radial bin. The errors partly cancel in ratios between policies,
  which is why the ratios are accurate while the absolute rates are not.
- Absolute error at a given alpha: median 0.010 dex, but about 0.11 dex for mp-1103974, mp-1188002,
  mp-22490 and nomad-19wSfSWChOSI.
- Dead-zone fraction at the matched points is 0.93 – 0.96 in the model vs 0.89 – 0.91 in the diagnosis.
  The two use different averaging (D2 averages over its own matched set), but the model's dead zone is
  probably somewhat too large. The cross-material correlation is weak (rho <= 0.4).

## 2. What each predictor is good for

- (a) needs only the grid and lattice. It gives the correct direction for beta > 0 vs beta = 0 and a
  reliable material ranking for the Hartree potential. For strongly weighted operators it overstates the
  magnitude of the gain, and it cannot say whether a steeper or a shallower exponent wins near the
  optimum.
- (b) adds the reference spectrum. It predicts the matched-rate ratios on the frozen ladders to a median
  of 2 – 15%, gets the direction right in 36/36 material-quantity cases, and places the optimum beta
  above the high-rate value. It is the predictor to use for setting per-material effect-size gates before
  a run.

## 3. Prediction table: operator-optimal u = w^{-1/2} vs blind u = 1 (no compression run exists)

Medians over the 12 materials (range of the rate ratio in brackets). "Rate ratio" = R_optimal / R_blind at
matched Nyquist-safe operator relative RMSE tau, so the predicted compression-ratio gain is its inverse.
"Matched-rate RMSE ratio" is evaluated at the rate the blind policy needs for tau. Full per-material rows
are in `prediction_table.csv`.

| operator | (a) matched-rate RMSE ratio | (a) saving, bits/pt | (b) rate ratio tau=1e-4 | tau=1e-6 | tau=1e-8 | (b) RMSE ratio tau=1e-6 | blind bits/pt tau=1e-6 |
|---|---|---|---|---|---|---|---|
| density | 1 | 0 | 1 | 1 | 1 | 1 | 6.42 |
| hartree_potential | 0.0496 | 4.40 | 0.364 [0.21–0.58] | 0.301 [0.15–0.38] | 0.282 [0.16–0.67] | 0.082 | 0.658 |
| hartree_field | 0.783 | 0.353 | 0.873 [0.84–0.90] | 0.839 [0.79–0.90] | 0.953 [0.92–0.97] | 0.753 | 1.489 |
| density_gradient | 0.913 | 0.131 | 0.971 [0.91–0.99] | 0.987 [0.97–0.99] | 0.992 [0.98–0.99] | 0.913 | 10.25 |
| density_laplacian | 0.731 | 0.453 | 0.939 [0.86–0.94] | 0.968 [0.93–0.97] | 0.978 [0.95–0.98] | 0.731 | 13.85 |
| gaussian_smoothed_density (sigma = 0.5 Å) | 10^-123 (outside high-rate validity) | 409 | 0.124 [0.11–0.17] | 0.030 [0.018–0.040] | 0.010 [0.003–0.011] | 4e-19 | 1.235 |

Reading the table:

- **Hartree potential and Gaussian smoothing give large gains**: the operator-optimal allocation needs
  about 30% (Hartree, tau = 1e-6) and about 3% (Gaussian, sigma = 0.5 Å) of the blind rate. For the Gaussian
  the optimal step grows as exp(sigma^2 |G|^2 / 2), so high-|G| modes are effectively dropped. The high-rate
  number (10^-123) is formally exact but meaningless there; (b) gives the usable prediction.
- **Derivative operators (gradient, Laplacian) give small relative rate gains.** They require a fine
  quantization of high-|G| modes, so both policies operate at 10 – 14 bits per point with essentially no
  dead zone. (b) then coincides with (a) for the RMSE ratio (0.913, 0.731), but the saving of 0.13 – 0.45
  bits per point is only 1 – 3% of the rate.
- **The Hartree field lies in between**: about a 16% rate saving at tau = 1e-6 and a smaller one at 1e-8.
- For the density itself, the optimal policy is the blind one by construction.

Files: `calibration_material.csv` (per material: all predictions, the frozen observations and model-curve
fidelity), `prediction_table.csv` (12 materials x 6 operators x 3 targets), `SUMMARY.json` (aggregate
statistics and the median prediction table). Regenerate with
`run_calibration.py compute` (about 40 min on this machine) and `run_calibration.py aggregate`.
