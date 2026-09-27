# Three-codec Hartree spectral generalization

Status: **secondary generalization after the frozen ZFP/SZ3 confirmatory mechanism audit**.

The parent branch `research/hartree-spectral-mechanism-20260927` is frozen at
commit `dc2b1675d3fc401ed7c72f4c21b609ba3e4a3a18`, where the 457-pair
ZFP/SZ3 mechanism audit closed with machine-precision operator identities.

This branch asks whether the same spectral mechanism generalizes to SPERR.

## Frozen matched populations

At the already frozen 0.10-dex realized-L-infinity matching rule:

- ZFP/SZ3: 457 pairs, 214 materials — inherited from the confirmatory audit;
- ZFP/SPERR: 465 pairs, 206 materials — newly audited here;
- SZ3/SPERR: 1847 pairs, 254 materials — newly audited here.

No new matching rule is introduced.

## Operator and spectral definitions

Exactly the same definitions as the confirmatory audit are reused:

- historical Hartree operator for exact reproduction of the previously reported
  matched-L-infinity observations;
- Nyquist-safe Hermitian Hartree operator for strict Parseval closure;
- safe spectral error energy;
- low-G and high-G fractions;
- spectral centroid;
- Hartree-weighted spectral energy;
- spectral Hartree susceptibility
  `S_H = W_H / E`.

For each pair A/B, the Nyquist-safe Hartree ratio factorizes pair by pair as

`R_H = sqrt(E_A/E_B) * sqrt(S_H,A/S_H,B)`.

## Generalization question

The strongest three-codec mechanism would be a consistent operator-susceptibility
ordering:

`ZFP < SPERR < SZ3`

where lower spectral Hartree susceptibility means that, per unit total spectral
error energy, less reconstruction error is placed in Fourier modes strongly
amplified by the Hartree kernel.

Spectral centroid and low-G fraction are supporting summaries; they are not used
as substitutes for the exact operator-weighted quantity.

## Population control

All reconstruction and radial-spectrum records carry an explicit `pair_label`.
Statistics are computed within each matched pair population, so differences in
which materials enter each pair comparison cannot masquerade as codec spectral
differences.

Bulk/slab stratification is reported as a robustness diagnostic.

The frozen manuscript and the frozen ZFP/SZ3 mechanism branch are not modified.
