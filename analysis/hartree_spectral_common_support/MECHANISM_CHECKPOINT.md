# Mechanism interpretation checkpoint — 2026-09-27

Status: **research note only; not manuscript text**.

## Exact operator decomposition

For the Nyquist-safe Hartree operator, every matched reconstruction pair obeys

`R_H(A/B) = sqrt(E_A/E_B) * sqrt(S_H,A/S_H,B)`

where:

- `E` is total non-Nyquist, nonzero-G spectral reconstruction-error energy;
- `S_H = [sum |Delta rho(G)|^2/|G|^4] / E` is the Hartree spectral susceptibility.

The equality is a discrete operator identity, not a regression.

## Pairwise full-population findings

### ZFP / SZ3

- safe Hartree ratio: 0.0776219
- sqrt(total spectral-energy ratio): 0.375963
- sqrt(spectral Hartree-susceptibility ratio): 0.202683
- median material absolute-log contribution from susceptibility: 62.0%
- 99.5% of materials have lower ZFP susceptibility than SZ3
- 99.1% have lower ZFP low-G error fraction
- 98.1% have higher ZFP spectral centroid

Interpretation: both smaller total spectral error and a less Hartree-sensitive
frequency allocation favor ZFP. Frequency allocation is the larger of the two
log-scale contributions.

### SZ3 / SPERR

- safe Hartree ratio: 6.76894
- sqrt(total spectral-energy ratio): 1.29010
- sqrt(spectral Hartree-susceptibility ratio): 4.97678
- median material absolute-log contribution from susceptibility: 87.2%
- 100% of materials have susceptibility in the direction of the historical
  Hartree effect

Interpretation: both factors favor SPERR, but operator susceptibility is the
dominant mechanism.

### ZFP / SPERR

- safe Hartree ratio: 0.670213
- sqrt(total spectral-energy ratio): 0.440074
- sqrt(spectral Hartree-susceptibility ratio): 1.44468
- susceptibility contribution opposes the total-error contribution

Interpretation: ZFP has much smaller total spectral error energy, but its error
is more Hartree-sensitive than SPERR's. The net ratio is therefore a
competition between error magnitude and frequency allocation rather than a
single monotone codec ranking.

## System-type reversal

The ZFP/SPERR decomposition is especially diagnostic:

### Bulk

- safe Hartree ratio: 0.643509
- sqrt(total energy ratio): 0.460700
- sqrt(susceptibility ratio): 1.32269

Total-error magnitude wins; ZFP has lower Hartree error.

### Slab

- safe Hartree ratio: 3.07171
- sqrt(total energy ratio): 0.340002
- sqrt(susceptibility ratio): 9.68375

Despite substantially smaller total spectral error for ZFP, the operator
susceptibility term reverses the Hartree ranking and makes SPERR better for this
population.

This is direct evidence that a codec ranking based on scalar pointwise error or
even total L2 error does not determine downstream scientific fidelity.

## Current general statement

The data support a stronger mechanism than a universal codec ordering:

> At matched pointwise distortion, a downstream operator responds to both the
> total magnitude of reconstruction error and how that error is distributed
> over the operator's sensitive modes. Codec-dependent spectral allocation can
> reinforce, attenuate, or reverse the ranking suggested by scalar or L2 error
> alone.

The ongoing three-way common-support audit tests whether the pairwise
susceptibility pattern survives when ZFP, SZ3 and SPERR are compared on exactly
the same material/tolerance-support population.

No frozen manuscript text is modified by this note.
