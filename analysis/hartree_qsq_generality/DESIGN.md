# Hartree-QSQ generality pilot

Status: **research extension, separate from the frozen submission scope**.

This branch tests whether the stability-qualification logic used for Bader charge also behaves coherently for a qualitatively different downstream observable: the periodic electronic Hartree potential.

## Scientific question

Does reference-side numerical qualification remain meaningful for a smooth, nonlocal density functional, or is the observed QSQ behavior specific to topology-sensitive Bader partitioning?

## Frozen inputs reused

- The 12-material Hartree pilot cohort already present on the parent branch.
- The existing ZFP reconstruction ladder and its verified Hartree-potential errors.
- The five QSQ seed labels `{20260905, 1, 2, 3, 4}`.
- The material-specific perturbation amplitude defined by the float32 round-trip L-infinity error.

No DFT is added and the current manuscript P1-P4 scope is not modified.

## New measurement

For each reference density, apply five iid-uniform perturbations at the frozen material-specific amplitude and recompute

`V(G) = 4 pi rho(G) / |G|^2`, with `V(G=0)=0`.

The primary reference-response metric is relative RMSE of the Hartree potential. The material-level Hartree QSQ response scale is the maximum over the five seed responses, mirroring the conservative aggregation used by the existing QSQ gate.

The existing ZFP Hartree reconstruction errors are then evaluated against a pre-specified relative-potential tolerance ladder. This is a pilot measurement contract, not a claim that any single ladder value is a universal chemistry threshold.

## Decision rule

The pilot is allowed to motivate a full bulk/slab, three-codec extension only if:

1. source/provenance and amplitude checks pass for every pilot material;
2. Hartree reference responses are finite and numerically small on the pre-specified contract scale;
3. the existing Hartree ladder remains predominantly monotone and near-linear;
4. at least one contract produces a non-trivial certification problem rather than an all-pass/all-fail result.

A scientific NO-GO is a valid outcome. Pipeline integrity failures are not interpreted scientifically.

## Privacy

The branch contains code and design only. Numerical outputs are encrypted before GitHub artifact upload and are not printed to the public Actions log.
