# General-QOAC operators: diagonal-Fourier operator library and a-priori gain predictors

Workstream WS-B. Three pieces:

| file | content |
|---|---|
| `operators.py` | registry of linear, diagonal-in-Fourier operators on the density, with exact spectral error metrics and an explicit real-space implementation |
| `gain_predictors.py` | (a) high-rate orbit-only predictor and (b) finite-rate Laplacian/ECSQ predictor of the matched-rate operator-error ratio between two step-allocation policies |
| `run_calibration.py` | retrospective calibration on the 12 engineering materials plus a prediction table for six operators (`results/`) |

Frozen code (`operator_aware_codec_hartree_v02/`, `general_qoac_electric_field*/`) is imported, never modified.

## 1. Operator library

```python
import operators as ops
op = ops.get_operator("hartree_field")                    # or ops.hartree_field()
ref = ops.reference_energies(rho, lattice, op)            # {"historical", "safe", "historical_spectral"}
err = ops.relative_error(rho_hat - rho, lattice, op, ref) # relative RMSE per variant
w   = op.weight(g2)                                       # squared spectral weight for allocation
lw  = op.log_weight(g2)                                   # same, in log space (no underflow)
y   = ops.apply_realspace(rho, lattice, op, safe=True)    # explicit real-space output (n_components, *shape)
```

| name | (L rho)(G) | w(\|G\|^2) | components |
|---|---|---|---|
| `density` | rho(G) | 1 | 1 |
| `hartree_potential` | 4 pi rho / \|G\|^2 (G != 0) | \|G\|^-4 | 1 |
| `hartree_field` | -i 4 pi G rho / \|G\|^2 (G != 0) | \|G\|^-2 | 3 |
| `density_gradient` | i G rho | \|G\|^2 | 3 |
| `density_laplacian` | -\|G\|^2 rho | \|G\|^4 | 1 |
| `gaussian_smoothed_density(sigma_angstrom)` | exp(-sigma^2 \|G\|^2 / 2) rho | exp(-sigma^2 \|G\|^2) | 1 |

Metric variants (all are relative RMSE ||L e|| / ||L rho||):

- `safe`: every mode except the even-grid Nyquist planes (and G = 0 for the two Hartree operators).
- `historical`: all modes, exactly as realized in real space by `numpy.fft.irfftn`. On even grids, the
  fftfreq reciprocal vector of a Nyquist index is not Hermitian-consistent, so irfftn keeps only the
  Hermitian part of the kz = 0 and kz = Nyquist planes. The spectral metric applies the same projection.
- `historical_spectral`: all modes, plain spectral sum without that projection (the definition in
  `electric_field_operator.py`).

`legacy_relative_error` returns (historical, safe) under each frozen code's convention: `historical` for
`hartree_potential` (as in `codec_qoac_h_v02.hartree_error_metrics`) and `historical_spectral` for
`hartree_field` (as in `electric_field_operator.relative_error`).

## 2. Gain predictors

A policy is a step profile Delta_k = alpha u_k over the QOAC-H v0.2 Hermitian orbits, passed as log u:
`gp.power_law(beta)` (u = q^beta), `gp.blind()` (u = 1), `gp.operator_optimal(op)` (u = w^{-1/2}).

```python
import gain_predictors as gp, operators as ops
op = ops.hartree_field()

# (a) high-rate, orbit set only (no density needed)
orb = gp.orbit_model(shape, lattice)
lw = gp.log_weight(op, orb)
gp.highrate_rmse_ratio(orb, lw, gp.power_law(1.0)(orb), gp.power_law(0.0)(orb))   # matched-rate RMSE ratio
gp.highrate_optimal_beta(orb, lw)            # grid argmin on {0, .25, ..., 2} and continuous optimum
gp.highrate_rate_saving_bits_per_point(orb, lw, ua, ub)

# (b) finite-rate, Laplacian components with variances from the reference spectrum (256 radial q bins)
mod = gp.spectrum_model(rho, lattice)
lw = gp.log_weight(op, mod)
g = gp.finite_rate_gain(mod, lw, gp.operator_optimal(op)(mod), gp.blind()(mod), target_rel_rmse=1e-6)
g["rate_ratio"]                # R_optimal / R_blind at matched Nyquist-safe operator RMSE
g["matched_rate_rmse_ratio"]   # RMSE_optimal / RMSE_blind at the rate the blind policy needs
gp.finite_rate_point(mod, lw, log_u, log_alpha)   # rate (bits), distortion, dead-zone fraction
```

(a) D(u) ∝ exp(-2 <log u>_n) sum_{safe} m n w u^2. For power laws it equals diagnosis D1 exactly.

(b) Plain-rounding quantizer on a unit-variance Laplacian, r = Delta / sigma, b = 1/sqrt(2), d = r sqrt(2),
h = d/2: P(0) = 1 - e^{-h}, P(±k) = e^{-h}(1 - e^{-d}) e^{-(k-1)d} / 2. Output entropy and MSE are closed
forms (`laplace_ecsq_exact`):

    H   = -P0 ln P0 - e^{-h} ln(e^{-h}(1 - e^{-d})/2) + e^{-h} d / (e^d - 1)          [nats]
    MSE = b^2 [ gamma(3, h) + K(h) / (e^{2h} - 1) ],   K(h) = ∫_{-h}^{h} s^2 cosh s ds

A 24,001-point log-r table (`ecsq`) reproduces them to < 1e-6. Rate = sum n H over all orbits, distortion =
sum_{safe} m n w sigma^2 MSE. alpha is found by Brent root finding for a target distortion or rate.

## 3. Retrospective calibration

```bash
python run_calibration.py compute  --cache-dir <scratch>/cache --work-dir <scratch>/pred
python run_calibration.py aggregate --work-dir <scratch>/pred           # writes results/
```

`compute` downloads the 12 engineering materials of `PILOT_MANIFEST.csv` (SHA-256 checked) and writes one
prediction JSON per material. No compression is run. `aggregate` joins the predictions with the frozen
observations, using the same statistics on model curves: the frozen alpha ladder, greedy pair matching
within 0.05 dex of compression ratio, and the beta-map common-rate interpolation. Results and their
interpretation are in `results/RESULTS.md`.

## 4. Tests

```bash
python -m unittest test_operators test_gain_predictors
```

Result on 2026-10-06 (Windows, numpy 2 / scipy 1.18): **16 tests, all pass.**

| test | checks |
|---|---|
| `test_spectral_metrics_match_explicit_realspace` | safe and historical metrics of all six operators (two Gaussian widths) equal the explicit irfftn real-space RMS ratio to rel. 1e-10 on 8 random small grids (even/odd sizes, two non-orthogonal cells) |
| `test_energy_is_parseval_of_realspace` | spectral energy = N x real-space sum of squares, rel. 1e-10 |
| `test_hartree_potential_reproduces_frozen_v02` | equals `codec_qoac_h_v02.hartree_error_metrics` (historical, safe) to rel. 1e-12 |
| `test_hartree_field_reproduces_frozen_electric_field` | equals `electric_field_operator.relative_error` (historical, safe) to rel. 1e-12 |
| `test_historical_variants_agree_on_orthogonal_or_odd_grids` | `historical` = `historical_spectral` where the Nyquist convention is unambiguous |
| `test_weight_matches_amplitudes`, `test_constant_field` | w ∝ sum_c \|a_c\|^2; derivative/Hartree operators annihilate constants |
| `test_matches_monte_carlo` | Laplacian ECSQ entropy (abs. 3e-3 bits) and MSE (5 s.e.) vs 4e6-sample Monte Carlo at Delta/sigma = 0.05 – 8 |
| `test_limits`, `test_series_and_closed_form_agree`, `test_table_matches_exact` | high-rate limits H + log2 r -> log2(sqrt(2) e), MSE -> r^2/12; continuity of the series/closed-form switch; table error < 1e-6 |
| `test_finite_rate_approaches_highrate` | (b) -> (a) as Delta/sigma -> 0 (rel. < 1e-4 at tau = 1e-7, monotone) for E-field, Hartree, gradient |
| `test_highrate_matches_diagnosis_formula` | (a) equals the diagnosis D1 expression |
| `test_grouping_preserves_orbits`, `test_dead_zone_increases_with_alpha`, `test_operator_optimal_equals_power_law` | bookkeeping and consistency |

Headline calibration (retrospective; `results/RESULTS.md`): finite-rate predictor (b) gives Hartree
beta2/beta0 median 0.083 vs observed 0.077 (median |log error| 0.15, Spearman 0.96); the high-rate predictor
(a) gives 0.050 (|log error| 0.36). E-field beta1/beta0: (b) 0.790 vs 0.806 (|log error| 0.021); beta1/beta2:
(b) 0.922 vs 0.928 with the direction right in 12/12 (a: 10/12); optimal beta: (b) 1.5 vs observed median
1.375 (within ±0.25 in 10/12; a: 1.0, 6/12).
