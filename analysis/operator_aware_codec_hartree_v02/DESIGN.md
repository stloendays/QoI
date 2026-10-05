# QOAC-H v0.2 — conservative Nyquist-aware Hermitian-orbit engineering

Date frozen: 2026-10-05

Status: **engineering/tuning extension** motivated by the completed QOAC-H v0.1 pilot. The v0.1 12-material cohort is reused only to improve the storage representation. It is not a confirmatory cohort for a new competitive claim.

## Parent evidence

QOAC-H v0.1 established:
- 12/12 materials completed, 600/600 settings, zero failures;
- operator-derived beta=2 allocation beat beta=0 on 12/12 materials;
- median matched-storage Hartree-error ratio beta=2/beta=0 = 0.0767117;
- competitive gate did not pass: median certified CR ratio versus the best ZFP/SZ3/SPERR baseline = 1.00394, bootstrap 95% CI [0.92102, 1.58564].

The postmortem showed that the three SPERR-leading failures were capped by the v0.1 decision to preserve every Nyquist plane exactly. Their encoded floor fractions were nearly identical to their exact-special-mode fractions.

## Engineering question

Can the v0.1 Nyquist-plane rate floor be removed without exploiting the alias ambiguity of continuum reciprocal vectors on even-grid Nyquist indices?

The successful beta=2 operator law is not retuned.

## Full-spectrum Hermitian-orbit representation

v0.2 uses the full orthonormal FFT.

For each discrete index k, define its Hermitian partner

    partner(k) = -k mod N.

Each pair is one Hermitian orbit. Exactly one canonical representative is stored. On decode, its partner is reconstructed by exact complex conjugation. Self-conjugate modes are stored as real values.

G=0 remains exact.

## Conservative alias-safe reciprocal magnitude

For an even FFT dimension, a Nyquist index is alias-equivalent to both +N/2 and -N/2. In a non-orthogonal lattice these sign choices can produce different continuum |G|^2 because of reciprocal-basis cross terms.

For every canonical orbit, v0.2 enumerates all alias-equivalent sign choices for coordinates lying on Nyquist indices and defines

    |G|^2_cons = min_alias |G_alias|^2.

This is deliberately conservative: the minimum |G|^2 corresponds to the maximum Hartree sensitivity 1/|G|^4.

The allocation remains

    Delta_G = alpha * (|G|_cons / Gmax_cons)^2.

Thus v0.2 removes the exact-plane exception without choosing a favorable alias.

## Serialization

- one exact DC coefficient;
- all other canonical Hermitian-orbit representatives are quantized;
- real components are stored for every orbit;
- imaginary components are stored only for non-self-conjugate orbits;
- reciprocal shells are used only for storage organization;
- each shell uses the smallest signed integer dtype required by its quantized coefficients;
- all-zero shells have no payload;
- non-zero shell payloads use zlib;
- shape, lattice, alpha, beta, shell layout and exact DC are stored in the stream.

Only actual serialized bytes count as the v0.2 rate.

## Scientific guard against Nyquist metric gaming

Every v0.2 setting reports three Hartree-related errors:

1. the historical real-space Hartree relative RMSE used by the completed Hartree-QSQ study;
2. the Nyquist-safe real-space Hartree relative RMSE used by the mechanism audit;
3. a conservative full-spectrum Hartree norm using |G|^2_cons on every non-zero Hermitian orbit.

For the engineering comparison at tau_H = 1e-6, a v0.2 row is accepted only when both

    historical Hartree relative RMSE < 1e-6

and

    conservative alias-safe Hartree relative norm < 1e-6.

This is stricter than relying on the historical metric alone.

## Engineering cohort and alpha ladder

Cohort: exactly the 12 materials frozen in

    analysis/operator_aware_codec_hartree/results/PILOT_MANIFEST.csv

from v0.1.

This cohort is now a tuning set.

For each material run beta=2 only at the same 25-setting ladder

    alpha / ptp(rho) = logspace(1e-7, 1e1, 25).

No v0.1 result is recomputed.

## Engineering promotion criteria

These criteria decide whether the architecture is worth freezing for a later held-out confirmatory experiment. They are not publication-level statistical claims.

Promotion-ready requires all of:
- 12/12 materials accounted for with no silent failure;
- all 12 have a dual-certified v0.2 row at tau_H=1e-6;
- median CR(v0.2) / CR(v0.1) > 1.05;
- median CR(v0.2) / CR(best existing baseline) > 1.05;
- v0.2 beats the best existing baseline on at least 9/12 materials;
- for each of the three v0.1 SPERR-leading rate-floor cases, the v0.2 maximum observed CR exceeds that material's best certified baseline CR.

If these engineering criteria pass, the next step is to freeze v0.2 and test a disjoint cohort or the full development population.

## Interpretation boundary

A positive result on these 12 materials is evidence that the engineering defect was repaired, not independent confirmation of competitive superiority.
