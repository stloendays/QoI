# Hartree spectral mechanism audit

Status: **confirmatory research extension; frozen manuscript and frozen Hartree-QSQ results remain unchanged**.

## Scientific question

The full-population Hartree-QSQ study found that, after within-material matching
at 0.10 dex in realized L-infinity, the material-level ZFP/SZ3 Hartree-error
ratio is approximately 0.078. This audit asks what property of the
reconstruction error produces that codec dependence.

The confirmatory population is **exactly the 457 ZFP/SZ3 matched pairs across
214 materials already stored in
`analysis/hartree_qsq_full/results/matched_realized_linf_pairs_0p10dex.csv`**.
No rematching or cohort substitution is allowed for the primary audit.

For each selected reconstruction,
`Delta rho(r) = rho_recon(r) - rho_ref(r)`, measure the reciprocal-space
error distribution and the Poisson-operator-weighted energy.

## Primary quantities

Using the full-spectrum-equivalent rFFT energy,

`E(G) = |Delta rho(G)|^2`,

report:

- low-G error-energy fraction;
- high-G error-energy fraction;
- spectral centroid;
- radial error-energy profile;
- Hartree-weighted error
  `W_H = sum |Delta rho(G)|^2 / |G|^4`;
- spectral Hartree susceptibility
  `S_H = W_H / sum |Delta rho(G)|^2`.

For a fixed material, the safe-operator Hartree error ratio decomposes exactly as

`ZFP/SZ3 Hartree RMS ratio = sqrt(E_ZFP/E_SZ3) * sqrt(S_H,ZFP/S_H,SZ3)`.

This separates total L2 spectral error magnitude from frequency allocation.

## Nyquist-plane correction

The historical Hartree implementation is preserved and recomputed as a
reproduction diagnostic because it defines the published 0.078 observation.

For non-orthogonal cells with an even FFT dimension, Nyquist modes are
alias-equivalent under sign reversal while the continuum `|G|^2` expression
contains cross terms. Applying `1/|G|^2` directly on those discrete planes can
therefore break exact Hermitian symmetry before `irfftn`. The historical
implementation remains scientifically useful, but a direct Parseval audit of
`sum |Delta rho(G)|^2/|G|^4` is not mathematically exact on those ambiguous
planes.

The mechanism audit therefore also defines a **Nyquist-safe discrete Hartree
operator**:

- `G=0` is zero, as before;
- modes on any even-grid Nyquist plane are set to zero;
- all remaining modes use `4 pi Delta rho(G)/|G|^2`.

This makes the discrete operator Hermitian and restores the exact identity

`RMS(Delta V_H)^2 = (4 pi)^2 / N^2 * W_H`.

Because Nyquist planes are the highest-frequency modes and the Hartree kernel
suppresses them strongly, the historical and Nyquist-safe codec ratios are
reported side by side as a robustness check rather than silently replacing the
historical result.

## Reproduction gates

For every selected pair:

1. the matched-pair target row must map uniquely to a frozen benchmark row;
2. regenerated realized L-infinity must reproduce the value stored in the
   full-population matched-pair file;
3. the historical Hartree relative RMSE must reproduce the stored matched-pair
   Hartree error;
4. source SHA-256 and grid metadata must pass the frozen development loader
   checks.

A mapping or reproduction failure is a pipeline failure, not a scientific
negative result.

## Interpretation

The frequency-structure hypothesis is supported only if the full-population
0.078 effect is reproduced and the Nyquist-safe audit shows that the
operator-weighted spectral difference persists. The relative contribution of
total spectral energy and spectral Hartree susceptibility is reported rather
than assumed.

No manuscript text is modified automatically.
