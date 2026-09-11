# P4 chemical-decision utility validation

Status: **FROZEN_SELECTION_PRINCIPLES**

This document is fixed before reading the prospective P2 aggregate or any P3A science outcome. Its purpose is to prevent post-hoc selection of a chemical case that happens to favor QoI Stability Qualification (QSQ).

## Scientific question

P4 asks whether a stability-qualified workflow improves an actual downstream chemical decision at useful coverage and cost, rather than merely changing benchmark labels.

The experiment must compare scientific decisions derived from compressed densities against a higher-confidence reference decision. QSQ is useful only if it reduces wrong retained decisions or targets expensive re-analysis more efficiently than reasonable alternatives. Rejecting every difficult case is not success.

## Dataset-selection rule

A P4 chemistry cohort must be selected without using codec outcome, QSQ eligibility, P2 fresh-seed outcome, or P3A implementation-transfer outcome.

Eligible sources are paired electronic-structure states for which the chemical comparison is intrinsically meaningful, for example adsorption before/after, hydrogenation before/after, redox-state pairs, or multiple adsorption/site configurations from the same chemical system. Each pair must have documented atom/fragment correspondence and compatible charge-density conventions.

Do not construct a cohort merely by selecting the largest historical Bader instabilities. If an existing external chemistry dataset is used, record the full candidate universe and all exclusions before computing its compression/QSQ outcomes.

The present 254-material compression benchmark does not by itself contain a documented paired-state chemistry endpoint. Therefore it cannot be re-labelled as a real chemical-decision validation without additional paired reference metadata.

## Primary decision endpoint

The primary endpoint is a **binary direction-of-charge-transfer decision** on a predeclared atom or chemically defined fragment:

`sign(Delta q)`, where `Delta q = q(state B) - q(state A)`.

The target atom/fragment must be chosen from chemical identity and the scientific question, not from whichever atom shows the largest compression-induced error.

A reference decision is considered intrinsically ambiguous if the higher-confidence reference magnitude is within a predeclared decision margin `delta_ref` of zero. Such cases are reported separately and are not forced into a positive/negative label.

`delta_ref` must be frozen from numerical reference uncertainty or an independently justified chemical resolution criterion before codec/QSQ outcomes are inspected. It must not be tuned to maximize QSQ performance.

## Secondary decision endpoints

Secondary endpoints may include:

1. rank ordering of predeclared sites/configurations by fragment charge change;
2. whether a predeclared charge-transfer magnitude exceeds an independently justified threshold;
3. preservation of a predeclared qualitative charge-localization pattern.

Formal oxidation state is not inferred from Bader charge alone. Bader-charge decisions must be described as charge partitioning / charge-transfer decisions unless an independent oxidation-state analysis is supplied.

## Higher-confidence reference

Each chemistry pair requires a reference-analysis record that includes, where available:

- exact density-file hashes and atom ordering;
- density-grid dimensions and integrated electron count;
- electronic-structure calculation provenance;
- BaderKit on-grid and Henkelman on-grid results;
- a finer-grid or otherwise demonstrably higher-confidence density analysis when genuinely recomputed data are available;
- an explicit rule for resolving atom/fragment correspondence between paired states.

If independent implementations disagree on the qualitative decision or the reference lies within `delta_ref`, label the reference **ambiguous**. Do not choose the solver that agrees with QSQ.

## Compression evaluation

For each non-ambiguous reference pair, evaluate the same codec family and prespecified compression settings on both state densities. Recompute the downstream Bader analysis after decompression. Do not derive one state's charge from the other's basins.

A compressed pair is a decision error if its downstream qualitative decision disagrees with the higher-confidence reference decision. Numerical Bader-error metrics remain secondary diagnostics; the primary P4 outcome is the chemical decision.

## Policies compared

At minimum compare four prespecified decision policies:

1. **No qualification:** use every available compressed result that meets the ordinary field/codec validity checks.
2. **Simple numerical proxy:** screen or rank cases using a cheap scalar proxy available before the chemical decision, such as realized field error or an independently frozen field-error threshold.
3. **Archived float32 probe:** use the historical order-preserving reference perturbation diagnostic as a legacy comparator.
4. **Frozen QSQ:** use the five-seed perturbation-based qualification rule exactly as deployed in the main benchmark.

If a post-P2 improved qualification rule is developed, it is a fifth, explicitly developmental policy and requires a separate calibration/validation split. It must not replace frozen QSQ retrospectively.

A random-rejection baseline matched to each policy's coverage must be included when feasible. This tests whether apparent reliability improvement is simply a consequence of discarding more cases.

## Escalation policy

In addition to pure accept/reject screening, test a selective escalation workflow:

- accept directly when the frozen qualification policy indicates low numerical risk;
- otherwise invoke a predeclared higher-cost analysis, such as an independent Bader implementation and/or genuinely finer electronic-structure density if available;
- if the higher-cost analyses remain inconsistent, return an explicit ambiguous/needs-review outcome rather than forcing a chemical label.

The escalation procedure and cost accounting must be frozen before its outcomes are inspected.

## Primary metrics

Report all of the following; no single favorable metric is sufficient:

- retained-decision error rate;
- coverage (fraction of non-ambiguous reference decisions retained without escalation);
- risk-coverage curve;
- fraction escalated;
- final unresolved/ambiguous fraction;
- total analysis runtime and additional storage/compute cost;
- error rate after escalation;
- bootstrap confidence intervals clustered by underlying chemical system, not by repeated codec setting.

When multiple codec settings exist for the same chemical system, they are repeated measurements, not independent chemical systems.

## Primary comparison

The main P4 comparison is whether frozen QSQ achieves lower decision error than the no-qualification policy **at non-trivial coverage**, and whether its risk-coverage behavior is better than simple-proxy and coverage-matched random rejection baselines.

The escalation analysis asks whether QSQ can target expensive re-analysis sufficiently well to improve final decision reliability at lower cost than escalating every case.

No universal performance threshold is promised in advance. Effect sizes, confidence intervals, coverage and cost are reported even if QSQ provides little or no benefit.

## Failure and ambiguity accounting

Source retrieval failure, decompression failure, Bader failure, missing atom correspondence and reference disagreement are distinct states. They must not be silently converted into scientific pass/fail labels.

For advertised reliability bounds, unresolved computational trials receive a conservative adverse accounting or the bound is withheld. Reference-ambiguous chemistry pairs remain outside binary decision-error denominators but are reported in cohort accounting.

## Completion criteria

P4 is not complete until:

1. the candidate chemistry universe and exclusions are frozen before compression/QSQ outcomes are computed;
2. each included pair has atom/fragment correspondence and a higher-confidence reference decision;
3. all compared qualification policies are defined before outcome inspection;
4. decision error, coverage, risk-coverage and cost are all reported;
5. selective escalation is evaluated or explicitly shown infeasible from available provenance;
6. all raw inputs, density hashes, analysis versions and exclusions are archived.

A small, honestly specified chemistry cohort with strong reference provenance is preferable to a large pseudo-validation assembled after seeing numerical outcomes.
