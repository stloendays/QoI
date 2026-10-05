# QOAC-H strongest-baseline study

Freeze date: 2026-10-05

Status: prospective protocol, frozen before any baseline arm below is executed on any material.
This study does not modify the frozen manuscript branch `paper/qoac-integration-20261005`, the frozen QOAC-H
codec, or any frozen QOAC-H result. Whether its outcome enters a manuscript is a separate scope-reopening
decision.

## Why

QOAC-H is compared in the frozen manuscript against the best certified ZFP/SZ3/SPERR row. Those codecs bound
pointwise density error and are not designed for a nonlocal linear QoI. At the primary Hartree certificate
the selected QOAC-H rows of the 48 confirmatory materials have median density Linf 1.89 and median density
RMSE 0.096 (frozen `confirmatory_material.csv`): the certified QOAC-H stream is effectively a low-pass
density. The scientifically relevant question is therefore whether QOAC-H still wins against baselines that
can also exploit Hartree smoothing:

- **T1 — spectral truncation.** The simplest operator-aware representation: keep only reciprocal modes with
  q = |G|/|G|max <= q_c, quantize them uniformly, drop the rest.
- **M — MGARD with negative smoothness.** Multilevel compression whose error is controlled in a Sobolev
  norm; s < 0 weakens high-frequency error, the established multilevel route to linear-QoI control
  (Ainsworth et al., SISC 2019).
- **V — store the QoI.** Compress the Hartree potential itself with ZFP/SZ3/SPERR. This changes the
  storage contract (the density is no longer recoverable) and is reported as a reference point, not as a
  same-contract competitor.

## Population

Exactly the 48 frozen QOAC-H confirmatory materials
(`analysis/operator_aware_codec_hartree_v02_confirmatory/results/CONFIRMATORY_MANIFEST.csv`).
QOAC-H rows and baseline rows are reused unchanged from the frozen confirmatory result; QOAC-H is not
re-tuned. No baseline arm has been run on these materials before this freeze.

Preflight smoke (correctness and toolchain only, no outcome inspection beyond pass/fail):
`mp-1188002` from the engineering manifest.

## Certificate (identical to the frozen QOAC-H confirmatory)

- historical Hartree relative RMSE < 1e-6 (primary);
- Nyquist-safe Hartree relative RMSE < 1e-6 (guardrail; a row failing it is not certified);
- compression ratio = 8 * npoints / total serialized bytes, including every header.

## Arms and frozen ladders

### T1 — spectral truncation

Reuses the frozen Hermitian-orbit representation of `codec_qoac_h_v02.py` (conservative Nyquist metric,
G = 0 exact, 32 shells, zlib level 6) with:

- Delta_G = alpha for q <= q_c (beta = 0);
- modes with q > q_c are not stored (their shells are empty; decoded as zero).

Ladders:

    q_c in {0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.50, 0.75, 1.00}
    alpha / ptp(rho) = logspace(1e-7, 1e1, 25)

225 settings per material. T1 receives 9x the search opportunity of QOAC-H (25 settings); this favours the
baseline and is therefore conservative for any QOAC-H advantage.

### M — MGARD

MGARD from conda-forge on ubuntu-24.04, version recorded at install. Uniform-grid 3-D float64 input,
absolute error tolerance mode.

    s in {inf, 0, -1}
    tol / ptp(rho) = logspace(1e-7, 1e1, 25)

75 settings per material. The preflight records which s values the installed build accepts. An s value
that the build rejects is recorded as `unsupported` with the error text and excluded from M; it is never
silently dropped. If MGARD cannot be installed at all, arm M is reported as `infeasible` with the install
log, and the study proceeds with T1 and V.

Periodicity: MGARD treats the grid as non-periodic. No padding or wrapping is applied; this is the
standard usage.

### V — Hartree potential stored directly

Compute V_H from the exact density with the frozen historical Hartree operator, compress V_H with ZFP,
SZ3 and SPERR (frozen external-E2E environment, `validation/requirements-external-e2e.txt` at commit
893f931) over

    abs_tol / ptp(V_H) = logspace(1e-9, 1e-1, 25)

and certify the relative RMSE of the decoded V_H directly against the reference V_H. The safe guardrail
is not applicable (no density is decoded); this is stated with the result.

## Primary comparison (same storage contract)

For each material, CR_new = best certified CR over T1 and M (all s, all q_c, all ladder points).

    R_new = CR_QOAC-H / CR_new

using the frozen certified QOAC-H CR. If neither T1 nor M certifies a material, it counts as a QOAC-H win
and is reported separately.

## Pre-declared reading of the outcome

These are interpretation bands frozen in advance, not new manuscript gates.

- **Advantage retained:** at least 36/48 materials with R_new > 1 and median R_new > 1.25, with a
  fixed-seed (seed = 20261005, 10,000 resamples) bootstrap 95% CI lower bound > 1.10.
- **Parity:** the median R_new bootstrap 95% CI contains 1.
- **Advantage lost:** median R_new < 0.90.
- Anything else is reported as **mixed**, with the per-material table.

Also reported: R_T1 and R_M separately; R_V = CR_QOAC-H / CR_V (contract-changing reference); bulk/slab
medians; density Linf and RMSE of every selected row so that the fidelity cost of each certified stream is
visible; encode/decode wall time.

## Execution

GitHub Actions, ubuntu-24.04, shards by SHA-256 of "QOAC-H-STRONG-BASELINES|" + material_id. Results
committed with the frozen-commit hash. No alpha, q_c, s or tolerance value may be added after the first
material result exists.
