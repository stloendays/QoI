# Fourier-spectrum mechanism audit

Status: **research extension; frozen manuscript untouched**.

## Question

At matched realised pointwise error, can the persistent codec dependence of the
Hartree-potential error be explained by the reciprocal-space structure of
reconstruction error rather than by scalar L-infinity magnitude alone?

For each reconstruction error field
`Delta rho(r) = rho_recon(r) - rho_ref(r)`, measure:

- radial error energy `|Delta rho(G)|^2`;
- low-G and high-G energy fractions;
- spectral centroid;
- the Hartree-weighted quantity
  `sum_{G != 0} |Delta rho(G)|^2 / |G|^4`.

The exact FFT/Poisson identity is checked numerically:

`RMS(Delta V_H)^2 = (4 pi)^2/N^2 * sum_{G != 0}|Delta rho(G)|^2/|G|^4`.

Therefore a Hartree RMSE ratio should equal the square root of the corresponding
Hartree-weighted spectral-energy ratio. The audit asks a stronger mechanism
question: after realised-Linf matching, does ZFP place a smaller fraction of
its error energy at low G / shift the spectral centroid to larger G than SZ3?

## Population and matching

- Frozen 12-material Hartree pilot cohort.
- ZFP, SZ3 and SPERR.
- Three-way common-support matching within each material.
- ZFP rows are anchors; nearest unused SZ3 and SPERR rows are admitted only
  within 0.10 dex in `log10(realized_Linf)`.
- Reconstruction is regenerated from the frozen nominal absolute tolerance and
  must reproduce the frozen realised L-infinity within [0.85, 1.15]x.

## Frequency definitions

Let `q = |G|/Gmax` on each material's reciprocal grid.

- low G: `q <= 0.25`
- high G: `q >= 0.75`
- centroid: error-energy-weighted mean q

The rFFT half-spectrum is converted to a full-spectrum-equivalent sum using the
Hermitian multiplicity along the final FFT axis.

## Interpretation

A mechanism result requires all of the following:

1. Parseval/Poisson identity passes numerically.
2. Direct Hartree RMSE ratio agrees with the square root of the
   Hartree-weighted spectral ratio.
3. ZFP/SZ3 differs in low-G fraction / centroid in the direction required by
   the Hartree operator.
4. Total unweighted spectral error energy does not by itself account for the
   Hartree advantage.

The previously observed approximately 0.078 ZFP/SZ3 Hartree ratio is treated as
an external consistency target, not as a fitted parameter.

Numerical outputs remain outside the frozen manuscript and are encrypted before
artifact upload.
