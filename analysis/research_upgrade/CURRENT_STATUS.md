# QSQ research upgrade — current status

Last synchronized: **2026-09-11 Asia/Singapore**.

This file is the concise authoritative status record for the active research-strengthening phase. Historical benchmark/protocol outputs remain frozen; all validation work below was additive and retained with provenance.

## Overall

- **P0 — claim correction / target definition: COMPLETE.** The active paper distinguishes fixed-pipeline numerical fidelity from robustness of the downstream reference analysis.
- **P1 — equal search opportunity: COMPLETE.** 1,332/1,332 additive common-tight-ladder reconstructions succeeded; final failures = 0.
- **P2 — prospective fresh-perturbation validation: COMPLETE.** 14,986/14,986 pre-registered fresh perturbation trials succeeded with the original five-seed QSQ gate unchanged.
- **P3A — independent implementation transfer: COMPLETE.** The resolved 24-system panel is complete across BaderKit on-grid, Henkelman on-grid and Henkelman near-grid. Henkelman on-grid reproduces QSQ classification for 24/24 systems at all three thresholds; near-grid exposes an analysis-definition boundary.
- **P3B — new-DFT grid convergence: DEFERRED_NO_NEW_DFT.** This is an explicit submission-scope decision, not a positive convergence result. The paper must not treat QSQ floors as grid-independent material constants.
- **P4 — real chemical-decision case study: COMPLETE_RESOLVED.** Five outcome-blind paired chemistry cases were frozen before outcome inspection; all five passed the two-implementation source-reference gate. Final compressed analysis contains 216/216 successful solver cells and 60/60 valid qualitative charge-transfer-direction decisions.
- **P5 — second sensitive task: OPTIONAL / NOT STARTED.** It should be added only if it materially strengthens transfer without diluting the electronic-density story.

## P1 result — common tight ladder

At the primary `1e-3 e` Bader tolerance, after equalizing tight-ladder search opportunity across all 254 development materials, failure to find a numerical pass occurs in **3.3% of eligible** versus **66.4% of QSQ screen-rejected** material–codec pairs, a **20.34x risk ratio**. Secondary results are 10.9% vs 79.3% at `1e-4 e` and 0.0% vs 68.0% at `1e-2 e`.

This removes unequal tight-search opportunity as an explanation for the observed separation. It is an association between qualification state and benchmark no-pass risk, not a causal codec-failure fraction.

## P2 result — prospective fresh perturbations

The original five-seed QSQ gate was frozen before each of the 254 development materials received 59 pre-registered fresh iid-uniform perturbations at its original float32-amplitude scale: **14,986/14,986 valid outcomes; unresolved = 0**.

Primary endpoint (`1e-3 e`):

- QSQ eligible: **143/254 materials (56.3% coverage)**; fresh exceedance risk **1.600%** (135/8,437; 95% material-cluster CI 0.782–2.596%).
- QSQ screen-rejected: **111/254 materials**; fresh exceedance risk **81.325%** (5,326/6,549; CI 75.981–86.257%).
- Rejected/eligible risk ratio: **50.83x**.
- Materials with at least one fresh exceedance: **20/143** eligible vs **110/111** rejected.

Secondary endpoints preserve the direction: `1e-4 e`, 4.016% vs 86.938% (21.65x); `1e-2 e`, 0.148% vs 79.593% (537.69x).

Interpretation boundary: P2 prospectively validates **risk stratification under the declared iid-uniform perturbation model on the development materials**. It is not a worst-case guarantee, simultaneous per-material certification, or new-material generalization.

## Figure 3 and active story

P1/P2 are the central validation evidence in `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`. Figure 3 is built around **equal-search validation + prospective fresh-risk stratification**, not the historical 97.2% / 95.5% full-record headline. Formal R PNG/PDF/SVG rendering passed in run **34605839019** and was committed in **f0693a35475f9b2a12af5ce9b1f12a4ef4c8429a**.

## P3A result — implementation transfer

The original run **34605557997** is retained with its 360 pre-solver recorded failures. Before retry, all 360 failures were classified as the same archived-amplitude serialization/provenance-gate family. The engineering-only retry **34608648393** changed no scientific panel, seed, perturbation amplitude, solver definition, threshold, QSQ gate, P1 or P2; it completed **360/360** retry cells successfully.

Resolved 24-system results:

- **72/72** material–solver five-seed summaries complete.
- Recreated BaderKit floors differ from frozen BaderKit floors by at most **8.71338e-11 e**.
- **Henkelman on-grid:** 24/24 classification agreement at `1e-4`, `1e-3` and `1e-2 e`; agreement 100%, Cohen kappa 1.000 at all three; floor-rank Spearman **rho = 0.995**.
- **Henkelman near-grid:** agreement 82.6%, 83.3% and 95.8% at the three thresholds; floor-rank Spearman **rho = 0.754**.

Interpretation: QSQ stratification is not an artifact of the original BaderKit package when the same on-grid assignment class is used. Near-grid disagreement shows that the downstream numerical definition remains part of the measurement contract. P3A is implementation-transfer evidence, not density-grid convergence or a unique physical Bader reference.

## P3B scope decision

P3B new electronic-structure grid recomputation is **deferred for the current submission**. Existing provenance-audit assets are retained for future or reviewer-requested targeted work.

Consequently, the manuscript may call the QSQ floor an **operational stability measure under the declared density representation and downstream-analysis contract**. It must not claim that the floor is grid independent, that Bader instability is independent of the electronic-structure grid, or that interpolation/resampling constitutes DFT convergence.

Source: `validation/qsq_prospective/P3B_SCOPE_DECISION.md`.

## P4 result — outcome-blind chemical decision case study

P4 was frozen before inspecting chemistry outcomes. A chemistry/provenance/geometry-only audit of 68 NOMAD development slab states yielded **5 primary paired cases** across GaN electrochemical surfaces and RuO2 CO2RR chemistry. Pair selection and target atoms did not use QSQ, codec, P2/P3A or Bader outcomes.

All **5/5** pairs passed the predeclared uncompressed reference gate based on BaderKit on-grid and Henkelman on-grid: same non-zero direction, minimum `|Delta q| >= 0.02 e`, inter-solver disagreement `<= 0.01 e`. The nine unique source states required **18/18 successful source solver calls** and produced zero reference-ambiguous pairs.

The compressed stage used the frozen common-tight ladder `{1e-7, 3e-7, 1e-6, 3e-6}` with ZFP, SZ3 and SPERR. The immutable first run **34617416199** produced 72 successful cells and 144 path-engineering failures. Before any retry, **144/144** failures were classified with zero unclassified: 72 SPERR work-directory creation failures and 72 Henkelman work-directory creation failures. The retry altered only directory creation and executed exactly the failed keys. Final resolved run **34618290375** yielded:

- **216/216 successful compressed solver cells; final failures = 0**.
- **60/60** direct BaderKit qualitative charge-transfer-direction decisions preserved the frozen reference direction; adverse/zero-direction decisions = **0**.
- Therefore **no qualification**, realized-Linf coverage matching, archived float32 screening and QSQ all have **0% direction-error rate** on their retained trials.
- Frozen QSQ retains **36/60 trials (60%)**, representing **3/5 chemistry pairs**, while no qualification retains 60/60. Thus QSQ is conservative relative to this deliberately coarse sign endpoint and **does not improve correctness here because the unqualified baseline is already perfect**.
- Under the predeclared optional second-solver audit workflow, QSQ-targeted escalation resolves all 60 decisions with **48 Henkelman reconstructed-state calls** and **397.2 s** measured Henkelman wall time, versus **108 calls** and **733.3 s** for escalating all. This is audit-cost reduction relative to blanket second-solver checking, not a correctness gain over direct BaderKit on this cohort.

Interpretation: P4 is a useful **null utility / contract-boundary result**, not a new headline. Strict `1e-3 e` Bader fidelity and preservation of a coarse chemical direction are distinct measurement contracts. P4 should be used in Discussion/Supplementary Information to make that distinction explicit, not to claim universal chemical-decision benefit.

Sources: `validation/qsq_prospective/p4_candidate_audit/`, `validation/qsq_prospective/p4_reference_adjudication/`, `analysis/research_upgrade/p4_failure_taxonomy/`, and `validation/qsq_prospective/p4_chemical_decisions_resolved/`.

## Immediate next actions

1. Integrate the **resolved P3A** result into the manuscript/SI as implementation-transfer evidence, maintaining the grid-convergence boundary.
2. Integrate **P4 as a negative/control-boundary case study** in Discussion/SI: no sign errors at common-tight settings, QSQ conservative for this coarse endpoint, optional audit-call reduction only.
3. Re-run the claim/evidence matrix and manuscript–Figure–SI numeric cross-reference audit after these additions.
4. Decide whether P5 is scientifically worth the scope expansion. Do not add a second task merely to obtain a positive result after P4's frozen null endpoint.
5. If no compelling P5 can be specified outcome-blind with low scope cost, freeze the research scope and move to submission assembly.

## Key provenance

- P1 final report: `analysis/research_upgrade/P1_COMMON_TIGHT_REPORT.md`
- P2 final report: `analysis/research_upgrade/P2_FRESH_PROBE_REPORT.md`
- P2 manifest: `validation/qsq_prospective/p2_fresh_probes/execution_manifest.json`
- P3A resolved report: `validation/qsq_prospective/p3a_implementation_transfer_resolved/P3A_IMPLEMENTATION_TRANSFER_RESOLVED_REPORT.md`
- P3B scope decision: `validation/qsq_prospective/P3B_SCOPE_DECISION.md`
- P4 primary protocol: `validation/qsq_prospective/P4_CHEMICAL_DECISION_PROTOCOL.md`
- P4 frozen reference/policy addendum: `validation/qsq_prospective/P4_REFERENCE_POLICY_ADDENDUM.md`
- P4 candidate audit: `validation/qsq_prospective/p4_candidate_audit/P4_CANDIDATE_AUDIT_REPORT.md`
- P4 reference report: `validation/qsq_prospective/p4_reference_adjudication/P4_REFERENCE_ADJUDICATION_REPORT.md`
- P4 failure taxonomy: `analysis/research_upgrade/p4_failure_taxonomy/P4_FAILURE_TAXONOMY.md`
- P4 resolved report: `validation/qsq_prospective/p4_chemical_decisions_resolved/P4_CHEMICAL_DECISION_REPORT.md`
- Current manuscript: `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`
- Figure 3 R source: `figures/R/figure3_certification_landscape.R`
