# P4 reference-decision and policy addendum

Status: **FROZEN_BEFORE_P4_OUTCOMES**

This addendum is frozen after the chemistry-only candidate-pair audit was launched and before any P4 reference Bader charge, compressed-pair decision, QSQ eligibility, codec result, or risk-coverage result is inspected for the candidate pairs. It does not modify `P4_CHEMICAL_DECISION_PROTOCOL.md`.

## Scope decision

P3B electronic-structure grid recomputation is not part of the current P4 execution. P4 therefore tests whether QSQ can improve a practical Bader-based chemical decision and target an **independent Bader implementation** for selective escalation. It does not claim a grid-converged physical Bader reference.

## Primary chemistry endpoint

For every frozen candidate pair, state A is the lower-atom-count state and state B is the addition state selected by the chemistry-only pairing audit. The target is the persistent host atom selected by the audit from structure/provenance geometry only.

For solver `s`, define

`Delta q_s = q_s(state B, target_B) - q_s(state A, target_A)`.

The primary qualitative chemical decision is `sign(Delta q)` on that predeclared persistent host atom. This is described as a local charge-partitioning / charge-transfer direction; it is not interpreted as a formal oxidation-state assignment.

## Frozen higher-confidence reference gate

The uncompressed source densities are analyzed independently with:

1. BaderKit 0.10.2 on-grid, using the frozen benchmark semantics;
2. Henkelman Bader 1.05 on-grid, using the validated adapter and its own unperturbed state baselines.

A pair receives a binary reference decision only if **all** of the following hold:

- BaderKit and Henkelman on-grid give the same non-zero sign of `Delta q`;
- `min(|Delta q_BaderKit|, |Delta q_Henkelman|) >= 0.02 e`;
- `|Delta q_BaderKit - Delta q_Henkelman| <= 0.01 e`;
- atom species/order checks for the target mapping pass against the frozen CHGCAR structures;
- both source densities and both solver evaluations pass explicit accounting.

Otherwise the pair is `REFERENCE_AMBIGUOUS` or a named provenance/computational failure. Ambiguous reference pairs remain visible in cohort accounting and are excluded from binary decision-error denominators.

The numerical constants `0.02 e` and `0.01 e` are frozen here before P4 charge outcomes are inspected and will not be tuned after observing P4 performance.

## Frozen compression settings

For every non-ambiguous reference pair, run the same setting on both state densities for each of the three frozen codecs:

- ZFP;
- SZ3;
- SPERR.

Use exactly the common tight relative-tolerance ladder already used in P1:

`{1e-7, 3e-7, 1e-6, 3e-6}`.

This yields 12 codec-setting conditions per pair. No setting is added or removed according to QSQ status or whether the chemical decision is easy or difficult.

The ordinary compressed decision is obtained from BaderKit on-grid charges after decompression. A trial is a decision error when the compressed-pair sign disagrees with the frozen reference sign. If the compressed `Delta q` is exactly zero at machine representation, record `ZERO/UNRESOLVED` rather than forcing a sign.

## Frozen qualification policies

All policies operate at the main QSQ tolerance `tau = 1e-3 e`.

1. **No qualification**: retain every computationally valid compressed trial.
2. **Realized-Linf proxy**: rank valid compressed-pair trials by `max(realized_Linf_A, realized_Linf_B)` from low to high. For a coverage-matched comparison, retain exactly the same number of trials as frozen QSQ within each codec; ties at the cutoff are resolved by deterministic SHA-256 ordering of `pair_id|codec|relative_tolerance`.
3. **Archived float32 probe**: retain a pair only if both state-level archived float32-probe floors are below `1e-3 e`.
4. **Frozen QSQ**: retain a pair only if both state-level frozen five-seed QSQ floors are below `1e-3 e` using the original strict rule.
5. **Coverage-matched random rejection**: for each codec, draw 10,000 deterministic SHA-256 pseudo-random rankings and retain the same number of trials as frozen QSQ. Report the distribution of retained-decision error rates; random rejection is a negative-control baseline, not an alternative fitted model.

No policy threshold may use P4 decision correctness.

## Frozen selective-escalation workflow

The practical escalation policy intentionally avoids new DFT calculations:

- if both states pass frozen QSQ at `1e-3 e`, accept the compressed BaderKit decision directly;
- otherwise analyze the same two decompressed densities with Henkelman Bader 1.05 on-grid;
- accept the escalated decision only when BaderKit and Henkelman give the same non-zero sign and both compressed `|Delta q| >= 0.02 e`;
- otherwise return `NEEDS_REVIEW` rather than forcing a chemical direction.

Comparator: **escalate all** valid compressed trials with the same Henkelman rule. This gives a direct compute-cost comparison between targeted and indiscriminate second-solver analysis.

## Cost accounting

Record separately:

- compression encode/decode wall time where available;
- BaderKit wall time for source and reconstructed fields;
- Henkelman wall time for reference and escalation;
- number of second-solver calls invoked by each policy;
- source bytes and compressed bytes where available.

QSQ qualification itself is an upstream reference-analysis cost and is reported separately from per-compressed-trial escalation cost. Existing frozen QSQ measurements are reused; they are not rerun for P4.

## Primary reporting

For each policy report:

- reference-cohort accounting;
- direct retained coverage;
- retained-decision error rate;
- error count and denominator;
- risk-coverage curve where ranking is defined;
- escalation fraction;
- post-escalation error rate among resolved decisions;
- final `NEEDS_REVIEW` fraction;
- second-solver call count and measured wall time;
- results by codec and pooled descriptively.

Repeated codec settings for one pair are not independent chemistry systems. Bootstrap confidence intervals are clustered by `pair_id`. If the frozen candidate universe spans enough independent NOMAD uploads, an upload-clustered sensitivity analysis is also reported; otherwise no pseudo-precise upload-cluster CI is manufactured.

## No-retuning rule

After this file is committed, the candidate-pair inclusion rule, target atom, reference margins, codec ladder, QSQ threshold, proxy ranking, random baseline, and escalation rule are immutable for the primary P4 analysis. Any later exploratory alternative must be explicitly labeled exploratory and cannot replace the frozen primary result.
