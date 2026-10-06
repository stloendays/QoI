# QOAC-HB — one compressed stream certified for Hartree potential and Bader charge

Freeze date: 2026-10-06

Status: prospective engineering protocol with a frozen confirmatory continuation. Frozen before any arm
below is executed on any material. Does not modify the frozen manuscript, QOAC-H, QOAC-B2 or any frozen
result.

## Question

QOAC-H and QOAC-B2 were each validated for a single downstream QoI. A stored density is normally reused
for several analyses. Can one stream satisfy both contracts at once, and is the operator-designed stream
still the cheapest way to do it?

The two designs act on different geometries:
- QOAC-H allocates error in the Hartree eigenbasis (Delta_G ∝ |G|^2) and leaves large real-space density
  error (median Linf 1.89 on the QOAC-H confirmatory cohort).
- B2 restores every fixed Bader region sum with the uniform minimum-Linf / minimum-L2 correction
  c = Delta_i / N_i, a piecewise-constant field with sharp basin edges.

Composition is not guaranteed. The correction can add Hartree error, and a Hartree-designed stream can
carry large basin-sum errors that make the correction large. This study measures the composition.

## Joint contract C_HB

On the final reconstructed CHGCAR:
1. historical Hartree relative RMSE < 1e-6 **and** Nyquist-safe Hartree relative RMSE < 1e-6;
2. actual Henkelman Bader 1.05 (`-b ongrid -vac 0.001`, exact AECCAR0+AECCAR2 reference) maximum atomic
   charge error <= tau_B = 1e-3 e;
3. zero basin reassignment;
4. scaled discrete region-sum closure <= 1e-9 (construction invariant).

No auxiliary density-Linf budget (kappa) applies: the Hartree certificate is the second scientific
constraint that excludes degenerate fields. Density Linf and RMSE are reported for every selected stream.

AECCAR is exact and is part of the measurement contract (as in B1/B2); it is not charged to any arm.

## Arms (all followed by the identical B2 projection and side-channel accounting)

- **J — QOAC-H + projection.** Frozen QOAC-H v0.2 codec (beta = 2, 32 shells, zlib 6),
  alpha / ptp = logspace(1e-7, 1e1, 25).
- **T1P — spectral truncation + projection.** Frozen T1 codec of the strongest-baseline study,
  q_c in {0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.50, 0.75, 1.00} x the same 25-point alpha ladder.
- **GP — generic + projection.** Every frozen WP-G ZFP/SZ3/SPERR row with status OK
  (`analysis/extensions_20260930/WP-G/rows.csv`), reproduced on the CHGCAR.

Bytes = codec stream + serialized basin side channel. CR = 8 * npoints / bytes.

Descriptive control: for the J candidate, also run Bader on the unprojected QOAC-H stream to show
whether projection is necessary.

## Candidate selection (per arm, per material)

1. Evaluate every ladder point; project; compute Hartree errors and closure.
2. Order rows that pass items 1 and 4 by CR, descending.
3. Run actual Henkelman Bader on the highest row. If it fails item 2 or 3, move to the next row, up to 5
   attempts; every attempt is recorded.
4. The certified CR of the arm is that of the first row passing all four items. If none passes, the arm
   does not certify that material.

## Populations

The 50 WP-G materials with finite all-electron reference, already split by QOAC-B1 before any execution:
- engineering: the 12 materials of `operator_aware_bader_fixed_partition/results/ENGINEERING_MANIFEST.csv`;
- confirmatory: the 38 materials of `FROZEN_HOLDOUT_MANIFEST.csv`. These were the QOAC-B2 confirmatory
  population; no joint-contract arm has been run on them.

## Engineering gates (12 materials)

R_J = CR_J / max(CR_T1P, CR_GP) per material; a material where J certifies and neither competitor does
counts as a J win.

- **E1 — feasibility:** J certifies C_HB in >= 10/12.
- **E2 — utility:** R_J > 1 in >= 9/12 and median R_J > 1.25.

Confirmation is authorized only if E1 and E2 both pass. If E1 fails because projection breaks the Hartree
certificate, the next engineering iteration is a Hartree-aware projection (minimize the Hartree norm of the
correction subject to the region sums). That would be a new protocol, frozen before execution.

## Confirmatory criteria (38 materials, frozen now)

1. 38/38 analyzable, zero pipeline failures;
2. J certifies C_HB in >= 34/38;
3. R_J > 1 in >= 28/38;
4. median R_J > 1.25;
5. fixed-seed (20261006, 10,000 resamples) bootstrap 95% CI lower bound of median R_J > 1.10;
6. every certified J stream has zero reassignment and Bader error <= 1e-3 e (by construction of item 2).

## Reporting

Per arm: certification count, median and range of certified CR, Hartree errors before and after projection,
Bader error before and after projection (J), density Linf/RMSE, side-channel fraction, Bader attempts used.
