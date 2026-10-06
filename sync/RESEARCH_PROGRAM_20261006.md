# QSQ / General-QOAC research program toward a top-journal manuscript — 2026-10-06

Base branch: `research/qoac-program-base-20261006` (QOAC-HB joint head merged with the E-field diagnosis
branch). The frozen manuscript `paper/qoac-integration-20261005` (QSQ + QOAC-H) is not modified by this
program. Any manuscript change requires scope reopening (prior-art audit, claim–evidence map, figure
architecture, story review, submission QA).

## Target scientific claim

The downstream measurement operator determines (i) whether the reference analysis is resolvable (QSQ),
(ii) the distortion geometry that compression should respect, and (iii) a gain that is predictable
**before compression** from the operator symbol and the reference spectrum. Non-spectral QoIs (Bader)
enter through minimum-disturbance constraint projection. One stored stream can be certified for several
QoIs.

## Evidence status entering the program

- QOAC-H v0.2: 48/48, 15.0x over ZFP/SZ3/SPERR; 1.56x over spectral truncation (45/48).
- QOAC-B2: 38/38 Bader-exact, 1.86x.
- E-field (beta = 1): directional 12/12, effect 0.81 (NO-GO); predicted 0.78 by high-rate theory.
- QOAC-HB joint: 50/50 jointly certified; confirmatory median 1.224 < 1.25 (FAIL); projection costs
  Hartree budget.

## Workstreams

| id | owner | branch | goal |
|---|---|---|---|
| WS-0 | CLI Claude | research/fresh-population-20261006 | fresh never-used populations: P1 CHGCAR bulk 12+60, P2 CHGCAR+AECCAR bulk 12+48, P3 slab 12+60 if reproducible |
| WS-A | main session | research/qoac-v03-rdo-20261006 | QOAC v0.3: exact per-shell Lagrangian RD allocation in the operator metric with direct certificate targeting |
| WS-B | CLI Claude | research/general-qoac-operators-20261006 | operator library (6 diagonal operators) + a-priori gain predictors (high-rate, finite-rate Laplacian ECSQ) |
| WS-C | CLI Claude | research/qoac-hb-v2-20261006 | Hartree-aware projection + certify-then-project for the joint contract |
| WS-D | later | — | QOAC-B3: AECCAR (partition-field) compression with topology preservation |

## Sequencing and gates

1. WS-A engineering on the 12 QOAC-H engineering materials, with gates frozen before execution.
2. WS-B predictions for the fresh populations are computed and frozen **before** any compression run on
   them.
3. Fresh confirmations: v0.3 (P1 + P3), multi-operator prediction test (P1 subset), HB v2 (P2). Each
   protocol is frozen before execution. Every baseline receives the same search opportunity
   (tolerance bisection), consistent with the QSQ principle of equalized codec search.
4. Manuscript scope reopening after the confirmations.

## Fairness rule for all new comparisons

Every arm, including ZFP/SZ3/SPERR, T1 and v0.2, is given continuous tolerance search (bisection) to the
same certificate whenever the new codec uses direct certificate targeting. Ladder-granularity gains are
reported separately from allocation gains.
