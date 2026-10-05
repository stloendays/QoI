# QOAC-H v0.2 — Hermitian-orbit engineering pilot

Date frozen: 2026-10-05

Status: engineering iteration after the preregistered v0.1 pilot. The v0.1 scientific result is frozen and unchanged.

## Motivation

QOAC-H v0.1 strongly validated the operator-derived allocation law

    Delta_G proportional to |G|^2

but failed the preregistered competitive gate because all even-grid Nyquist planes were stored exactly. In the three SPERR-leading failures, the exact special-plane fraction numerically matched the observed encoded rate floor.

v0.2 changes only the reciprocal-space representation. It does not retune beta=2.

## Representation

1. Compute a full orthonormal FFT of the real density.
2. Partition reciprocal indices into Hermitian orbits under

       k -> -k mod N.

3. Store one canonical coefficient per orbit and reconstruct its partner by exact conjugation.
4. Store only G=0 exactly.
5. For self-conjugate nonzero modes, quantize the real coefficient and force the imaginary part to zero.
6. For ordinary two-member orbits, quantize real and imaginary parts of the canonical coefficient and reconstruct the partner by conjugation.

This representation contains the same real degrees of freedom as the original field while avoiding an exact Nyquist-plane side channel.

## Conservative Nyquist alias metric

For an even grid, a Nyquist coordinate is alias-equivalent to both +N/2 and -N/2. On a non-orthogonal lattice these choices can change |G|.

For every reciprocal index, enumerate all sign choices only for coordinates that lie on Nyquist indices and define

    |G|_safe^2 = min_alias |G|^2.

The quantization law remains

    Delta_k = alpha * (|G|_safe / Gmax_safe)^2.

Using the minimum reciprocal magnitude is conservative: it never allocates a looser step because an arbitrary FFT Nyquist sign happened to make |G| larger.

## Engineering population

Reuse the exact 12-material frozen v0.1 pilot cohort only as an engineering set.

This reuse is not a new confirmatory scientific test. It is permitted because the goal is to repair the identified representation bottleneck.

Any confirmatory competitive claim after v0.2 must use a disjoint frozen cohort or the full eligible development population.

## Alpha ladder

For certified engineering comparisons, reuse the exact v0.1 ladder:

    alpha / ptp(rho) = logspace(1e-7, 1e1, 25).

Additionally run one representation-floor probe at

    alpha / ptp(rho) = 1e8.

The floor probe is not eligible for the scientific certificate comparison; it is used only to verify that the exact-Nyquist rate floor has been removed.

## Scientific certificate

Primary threshold remains

    tau_H = 1e-6 historical Hartree relative RMSE.

The actual decoded field is certified with the same downstream Hartree calculation used by v0.1. The Nyquist-safe metric is reported in parallel.

## Engineering success gates

Gate A — rate-floor removal:
- all three v0.1 SPERR-leading materials must have v0.2 floor-probe CR greater than 1.25 times their best v0.1 baseline CR.

Gate B — certified representation improvement:
- median over 12 materials of best-certified CR(v0.2) / best-certified CR(v0.1) must exceed 1.05.

Gate C — confirmatory-candidate competitive performance:
- at least 9/12 materials must beat their best existing ZFP/SZ3/SPERR certified baseline;
- median best-certified CR(v0.2) / CR(best baseline) must exceed 1.05.

Passing Gate C does not itself create a confirmatory claim because the 12 materials are an engineering set. It only authorizes freezing a disjoint confirmatory experiment.

## Non-negotiable invariants

- beta remains exactly 2;
- G=0 is the only exact reciprocal coefficient;
- decoded spectrum must satisfy Hermitian symmetry by construction;
- decoded real-space field must have negligible imaginary leakage;
- no Nyquist mode may receive a step derived from a non-conservative alias choice;
- actual serialized bytes, not entropy estimates, define compression ratio.
