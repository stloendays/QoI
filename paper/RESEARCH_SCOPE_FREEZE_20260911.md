# Research scope freeze for the current submission

Status: **FROZEN_FOR_SUBMISSION**

Date: 2026-09-11

## Decision

The current submission research scope is frozen after completion of P0, P1, P2, P3A and P4. P3B new-DFT grid convergence remains explicitly deferred, and P5 transfer to a second topology-sensitive QoI is **NO-GO for the current submission**.

This decision is methodological rather than schedule-driven. The completed evidence chain already tests the central claim through progressively harder controls:

1. **P1 — equal search opportunity:** the QSQ separation survives completion of a common tight codec ladder across all 254 development materials.
2. **P2 — prospective validation:** the frozen five-seed QSQ gate strongly stratifies 14,986 genuinely fresh perturbation outcomes without retuning.
3. **P3A — independent implementation transfer:** the QSQ classification transfers exactly across the independent Henkelman on-grid implementation on the frozen 24-system panel, while near-grid differences expose an explicit analysis-definition boundary.
4. **P4 — outcome-blind real-chemistry boundary case:** five pre-frozen chemistry pairs yield 60/60 correct common-tight charge-transfer-direction decisions even without qualification, showing that a strict numerical Bader contract and a coarse qualitative chemical contract are not interchangeable.

## P5 go/no-go audit

The repository was checked for an already available, independently defined second nonlinear/topology-sensitive QoI that could be evaluated outcome-blind with modest additional scope. No reproducible second-task asset chain was found for candidates such as ELF basin analysis, QTAIM critical-point/connectivity analysis, independent topological segmentation, or another comparable nonlinear partitioning task. The existing additional QoIs are electron count and Hartree potential, which are intentionally controls and do not constitute independent transfer of the QSQ framework to a second sensitive task.

Creating a new P5 task now would require selecting a new scientific endpoint, reference implementation, failure model, perturbation semantics and evaluation cohort after observing the completed Bader results, including the prespecified P4 null endpoint. That would materially expand the paper and introduce avoidable outcome-driven-selection risk. It is therefore not justified for the current submission.

## Locked scientific interpretation

The submission may claim that:

- QSQ is a prospectively validated empirical risk-stratification procedure for Bader response under the declared iid-uniform perturbation model on the studied development materials;
- equalized codec-search opportunity does not remove the strong separation between QSQ-qualified and screen-rejected targets;
- the qualification classification transfers across an independent on-grid Bader implementation on the targeted 24-system panel;
- the numerical analysis definition is part of the measurement contract, as shown by the near-grid implementation boundary;
- a strict numerical Bader tolerance and a coarser qualitative chemical direction are different contracts, as demonstrated by the frozen P4 null result.

The submission must not claim that:

- five QSQ probes constitute a worst-case mathematical stability guarantee;
- the QSQ floor is a grid-independent material constant;
- P3A establishes electronic-structure grid convergence or a unique physical Bader reference;
- the 24-system P3A panel estimates population prevalence;
- P4 shows a correctness benefit of QSQ for the coarse sign endpoint;
- the Bader-specific mechanism has already been demonstrated for arbitrary QoIs or a second topology-sensitive task;
- the historical 97.2%/95.5% full-record fractions are design-independent causal codec-failure misattribution rates.

## What may still change before submission

The following are allowed after this freeze because they do not create new scientific outcomes:

- prose editing that preserves the locked claim/evidence relationships;
- figure layout, caption and typography changes that do not alter plotted data or statistical definitions;
- Supplementary Information organization and cross-reference repair;
- journal-specific formatting;
- reference/citation corrections;
- persistent archival release/DOI creation;
- final Word/PDF assembly from the locked manuscript and real data-driven figures;
- reproducibility/provenance fixes that do not change scientific definitions and are explicitly logged.

## What requires reopening the research scope

Any new scientific endpoint, new material cohort used for a primary claim, new perturbation family used to replace the frozen QSQ result, new DFT grid-convergence calculation, new P5 task, or change to a primary threshold/selection rule requires an explicit dated scope-reopening addendum. Reviewer-requested targeted calculations may be added later, but must remain traceable to the review request and must not silently redefine the frozen primary evidence.

## Submission-ready evidence lock

The final cross-reference audit is `paper/SUBMISSION_UPGRADE_CROSS_REFERENCE_AUDIT_20260911.md` and is required to remain PASS. The active submission draft is `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`. Figure 3 remains the central prospective-validation figure; P3A is supporting implementation-transfer evidence; P4 remains a secondary contract-boundary/null result in the main text and Supplementary Tables S15-S16.
