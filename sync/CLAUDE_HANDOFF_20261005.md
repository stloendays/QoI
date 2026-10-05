# Claude handoff — QSQ / QOAC project — 2026-10-05

You are taking over the scientific-compression project in repository `stloendays/QoI`.

## Read first

Use GitHub as the only authority for code and machine-readable evidence. Do not infer results from chat summaries when a frozen result file exists.

Start from branch:

`research/general-qoac-electric-field-20261005`

Then read, in this order:

1. `sync/QOI_QOAC_STATE_20261005.md`
2. `paper/QOAC_INTEGRATION_FINAL_AUDIT_20261005.md`
3. `paper/QOAC_PRIOR_ART_NOVELTY_AUDIT_20261005.md`
4. `analysis/operator_aware_bader_fixed_partition/DESIGN.md`
5. `analysis/operator_aware_bader_fixed_partition/results/SUMMARY.json`
6. `analysis/operator_aware_bader_projection/DESIGN.md`
7. `analysis/operator_aware_bader_projection/results/SUMMARY.json`
8. `analysis/operator_aware_bader_projection_confirmatory/results/SUMMARY.json`
9. `analysis/general_qoac_electric_field/DESIGN.md`
10. `analysis/general_qoac_electric_field/results/SUMMARY.json`

## Current scientific model

The project is no longer merely a codec benchmark. The working structure is:

`QSQ qualification -> diagnosis -> QoI-specific compression design -> actual downstream certification`.

QSQ asks whether the declared reference QoI/tolerance is numerically resolvable before using it to score a codec.

Two compression-design patterns are currently validated:

### QOAC-H

Hartree is linear and diagonal in reciprocal space. Squared Hartree error weights density-error modes by `|G|^-4`. Under the frozen high-rate model this gives `Delta_G propto |G|^2`.

Evidence:
- 12/12 mechanism wins against beta=0; median error ratio 0.0767117.
- 48/48 disjoint confirmatory wins vs best certified ZFP/SZ3/SPERR; median CR ratio 15.016x, bootstrap 95% CI [11.204,21.461].
- 254-material census; at tau_H=1e-6, 253/253 comparable wins, median 12.463x.

Do not claim this law applies to Bader.

### QOAC-B2

Bader is partition/topology dependent. With exact AECCAR, the partition is fixed and the CHGCAR basin-integral constraints can be restored after generic compression.

The successful method is:

`generic CHGCAR compression -> decode -> uniform per-basin sum projection -> actual Henkelman Bader certification`.

The uniform correction is minimum-Linf and minimum-L2 among unconstrained corrections restoring a fixed basin sum.

B1 negative result matters:
- the explicit basin-mean + zero-sum residual transform was scientifically valid but compression-hostile;
- median CR ratio residual/G1 = 0.401; it was rejected.

B2 engineering:
- kappa=4 auxiliary density budget;
- 11/12 wins;
- median CR ratio 1.782x;
- Bader error 0 and reassignment 0.

B2 disjoint holdout:
- 38/38 analyzable;
- 34/38 wins;
- median CR ratio 1.86462x;
- bootstrap 95% CI [1.75916,1.98549];
- actual Bader error 0 and reassignment 0 in 38/38;
- max side-channel fraction 0.999%.

### Electric-field General-QOAC engineering

Theory predicted beta=1 because electric-field squared error weights density error by `1/|G|^2`.

Important: this is currently a **NO-GO**, not a confirmed generalization.

Execution:
- 12 materials;
- 900 settings;
- 0 failures.

Results:
- beta1 vs beta0: beta1 better in 12/12, but median error ratio 0.8064 failed the frozen <0.70 gate.
- beta1 vs beta2: beta1 better in 10/12, median 0.9280 failed the frozen <0.90 gate.
- certified-rate: 7/12 wins, median CR ratio 1.0313, failed.
- confirmatory_authorized = false.

Do not run a new electric-field holdout under the failed protocol.

## Manuscript boundary

The current frozen manuscript is the QSQ + QOAC-H story on branch `paper/qoac-integration-20261005`.

It has:
- Fig. 1–9;
- main manuscript final audit 0 blockers / 0 warnings;
- SI final audit 0 blockers / 0 warnings.

QOAC-B2 and electric-field work are post-freeze research. Do not silently insert them into the manuscript. Any scope reopening requires explicit author authorization, a prior-art audit, claim/evidence mapping and figure-architecture update.

## What to do next

Work only on development data for the electric-field NO-GO diagnosis.

Recommended next investigation:
1. determine whether the high-rate derivation beta=1 is weakened by finite-rate entropy coding and actual Fourier coefficient distributions;
2. inspect rate and error by radial shell;
3. compare theoretical sensitivity `1/|G|` with empirical marginal rate-distortion slopes;
4. if testing beta more finely, define a new engineering protocol first and state clearly that it is a new iteration;
5. do not touch a future confirmatory cohort until the new engineering protocol passes its frozen GO criteria.

For Bader, the next unsolved problem is compression of the partition-defining AECCAR/topology (QOAC-B3). Keep that separate from the already confirmed QOAC-B2 exact-reference claim.

## Non-negotiable provenance rules

- Never fabricate results.
- Never overwrite or reinterpret a frozen negative result as a success.
- Keep engineering and confirmatory cohorts separate.
- Do not change frozen thresholds after looking at holdout results.
- Distinguish development-population census from external/disjoint confirmation.
- Use reader-facing names QSQ, QOAC-H and QOAC-B2; internal version labels stay in provenance paths only.
- GitHub branch + commit + machine-readable result file are authoritative.
