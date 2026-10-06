# General-QOAC electric-field — finite-rate diagnosis

Freeze date: 2026-10-05

Status: **diagnosis only.** This study adds no GO/NO-GO gate, changes no frozen result, and authorizes no
confirmatory cohort. The electric-field engineering result (`analysis/general_qoac_electric_field`) and the
beta-map result (`analysis/general_qoac_electric_field_beta_map`) both remain NO-GO with
`confirmatory_authorized = false`. No new beta value and no new alpha value is evaluated.

## Population and settings

Exactly the 12 QOAC-H / electric-field engineering materials
(`analysis/operator_aware_codec_hartree/results/PILOT_MANIFEST.csv`), the frozen codec
`codec_qoac_h_v02.py` (shell_count = 32, zlib_level = 6), the frozen alpha ladder
`alpha/ptp(rho) = logspace(1e-7, 1e1, 25)` and the already-evaluated grid
`beta in {0, 0.25, ..., 2}`. Primary metric: the frozen Nyquist-safe electric-field relative RMSE.

## Questions

1. **High-rate theory vs observation.** What effect size does the frozen high-rate model itself predict?
2. **Coefficient amplitudes.** What fraction of each spectral shell is quantized to zero (dead zone), and how
   much of the error comes from zeroed coefficients rather than from uniform rounding?
3. **Radial-shell rate/error contributions.** Where the bytes and the weighted field error sit in |G|.
4. **Empirical marginal rate-distortion slopes.** Whether the Lagrangian slope -dD_s/dR_s is equal across
   shells at beta = 1, as the high-rate optimality condition requires.
5. **Shell/entropy-coding masking.** Whether the 32-shell integer-width + zlib packing hides a beta = 1
   advantage that an ideal entropy coder would show.

## D1 — analytic high-rate prediction (stated before per-material computation)

Under the frozen model, each canonical Hermitian orbit k carries n_k real quantized components
(2, or 1 if self-conjugate) and multiplicity m_k on the full grid (2, or 1). With step Delta_k = alpha q_k^beta:

    D(beta)  = sum_{k in safe} m_k n_k w_k Delta_k^2 / 12,     w_k = 1/|G_k|^2 (electric field)
    R(beta)  = sum_k n_k [h_k - log2 Delta_k]                   (high-rate rate model)

At equal R, sum_k n_k log Delta_k is fixed, so log alpha = C - beta <log q>_n. Hence the predicted
matched-rate RMSE ratio between two exponents depends **only on the orbit set (grid and lattice)**, not on
the density:

    RMSE(b1)/RMSE(b2) = sqrt( exp(-2(b1-b2)<log q>_n) * S(b1)/S(b2) ),
    S(b) = sum_{k in safe} m_k n_k q_k^(2b) w_k.

For a uniform density of modes in a ball (q^2 dq on [0,1]) this gives, for the electric field,

    beta=1 / beta=0 :  sqrt(e^(2/3)/3)       = 0.806
    beta=1 / beta=2 :  sqrt(5 e^(-2/3)/3)    = 0.925

and a continuous optimum exactly at beta = 1 with a flat minimum. D1 evaluates the exact discrete
expression on every material's actual conservative orbit set, for the electric field and, as a calibration
check, for the Hartree potential (w_k = 1/|G_k|^4, beta = 2 vs 0).

## D2 — per-shell decomposition of the frozen settings

For every material, every frozen beta and every frozen alpha, quantize exactly as `encode_prepared` and
compute in orbit space, per shell:

- number of orbits, reference weighted energy;
- weighted electric-field error, split into zeroed-coefficient error and rounded-coefficient error;
- the high-rate prediction sum m n w Delta^2/12 for the same shell;
- dead-zone fraction (quantized integer = 0);
- actual zlib bytes (identical to the codec stream), zeroth-order entropy of the shell's integers
  (32 frozen shells) and of the same integers pooled in 128 finer q bins.

Closure check: the total Nyquist-safe weighted error must reproduce the frozen
`electric_field_error_rel_RMSE_safe` of the corresponding row in
`general_qoac_electric_field_beta_map/results/beta_map_rows.csv` to relative 1e-6. The stream byte count must
reproduce `encoded_bytes` exactly.

## D3 — matched-rate ratios under three rate measures

Using the beta-map common-rate interpolation (log10 error linear in log10 rate, per material, common
overlap), report beta=1/beta=0 and beta=1/beta=2 under: actual serialized bytes (closure with the frozen
result), H0 over 32 shells, H0 over 128 bins. A large shift between the three measures would indicate that
packing masks the beta effect.

## D4 — marginal slopes

For beta = 1, between adjacent alpha ladder points, lambda_s = -Delta D_s / Delta R_s per shell (zlib bytes).
Report the spread of log10 lambda_s across shells that carry >= 1% of the error, low-q vs high-q.

## Interpretation boundary

D1 can only state what effect size the frozen theory implies; it cannot convert the frozen NO-GO into a GO.
Any redesigned electric-field codec or any recalibrated gate requires a new prospective engineering protocol,
frozen before execution, and a new disjoint cohort that excludes the 12 engineering materials and the 48
QOAC-H confirmatory materials.
