# QSQ research-strengthening plan

Opened 2026-09-11. Aim: a consequential, independently validated methods contribution suitable for a leading specialist journal, with broader-journal ambitions conditional on demonstrated transfer and scientific relevance. Scale, presentation and naming do not substitute for scientific validation.

## Current research status

The main research-strengthening sequence is now **P0–P4 resolved**, with P3B explicitly deferred and P5 optional. Frozen reconstruction data, the historical protocol and the deployed five-seed QSQ gate remain unchanged. All added validation is additive and provenance-tracked.

Authoritative concise snapshot: `analysis/research_upgrade/CURRENT_STATUS.md`.

- **P0 COMPLETE:** claims distinguish fixed-pipeline fidelity from robustness of the downstream reference analysis.
- **P1 COMPLETE:** 1,332/1,332 common-tight-ladder additions succeeded.
- **P2 COMPLETE:** 14,986/14,986 pre-registered fresh perturbation trials succeeded; original five-seed QSQ gate unchanged.
- **P3A COMPLETE:** resolved 24-system independent implementation-transfer panel; matched on-grid classification transfer is 24/24 at all three thresholds.
- **P3B DEFERRED_NO_NEW_DFT:** no claim of electronic-structure grid convergence is made in the current submission.
- **P4 COMPLETE_RESOLVED:** outcome-blind real-chemistry case study completed; 216/216 compressed solver cells valid. The frozen qualitative sign endpoint is a null utility result for correctness and a useful measurement-contract boundary case.
- **P5 OPTIONAL / NOT STARTED.**

## Why the original headline was revised

The historical full-record counts reproduce exactly, but their interpretation was too strong because extra tight-ladder access was targeted to 143 materials eligible at `1e-3 e`. At that threshold, the full record added 214 numerical passes, all in the eligible group. Therefore the historical >95% reclassification number is ladder-design-sensitive and is retained as provenance rather than used as the central causal claim.

The upgraded evidence chain asks progressively harder questions:

1. **P1:** does the separation survive equal compression-search opportunity?
2. **P2:** does the frozen QSQ gate predict risk on genuinely unseen perturbations?
3. **P3A:** does the qualification transfer across an independent implementation under matched analysis semantics?
4. **P4:** does exact QSQ qualification coincide with a coarser real chemical decision, or are these distinct contracts?

## P0 — Define the scientific target and correct the active claims

**Status: COMPLETE.**

The active manuscript separates:

- fixed-input/fixed-pipeline numerical reproduction;
- robustness of the reference QoI under a declared perturbation model;
- any stronger coupled robustness target.

QSQ is an operational qualification procedure. It does not imply that an exact numerical comparison is undefined, does not prove a worst-case theorem from five samples, and does not identify a unique causal source for every codec error.

**Gate outcome:** passed. Every principal result is tied to a declared target, perturbation family, ladder and population.

## P1 — Remove unequal search opportunity

**Status: COMPLETE.**

The 111 previously uncovered development materials received the same four tight relative settings for all three codecs, producing **1,332/1,332 successful additive reconstructions** after retrying 24 transient NOMAD source-download timeouts with unchanged scientific settings.

At `1e-3 e`, failure to find a numerical pass occurs in **3.3% of QSQ-eligible** versus **66.4% of QSQ-rejected** material–codec pairs, a **20.34x risk ratio**. Secondary results are 10.9% vs 79.3% at `1e-4 e` and 0.0% vs 68.0% at `1e-2 e`.

**Gate outcome:** passed for equalized candidate opportunity. The association is not described as a causal codec-failure fraction.

## P2 — Prospective validation on genuinely fresh perturbations

**Status: COMPLETE.**

The deployed five-seed QSQ gate was frozen before running **59 new iid-uniform perturbations per development material**, seeds 10000–10058, at the original material-specific float32-amplitude scale. All **14,986/14,986** trials returned valid Bader outcomes; unresolved = 0.

Primary `1e-3 e` result:

- acceptance coverage: **143/254 = 56.3%**;
- fresh exceedance risk in eligible materials: **1.600%** (135/8,437; material-cluster 95% CI 0.782–2.596%);
- risk in rejected materials: **81.325%** (5,326/6,549; CI 75.981–86.257%);
- rejected/eligible risk ratio: **50.83x**;
- at least one exceedance: **20/143** eligible vs **110/111** rejected materials.

Secondary thresholds preserve the direction: `1e-4 e`, 4.016% vs 86.938% (21.65x); `1e-2 e`, 0.148% vs 79.593% (537.69x).

**Gate outcome:** strong prospective risk stratification under the declared iid-uniform perturbation model on the development materials. This is not worst-case robustness, simultaneous per-material certification or new-material generalization.

## P3A — Independent implementation transfer

**Status: COMPLETE.**

The frozen 24-system panel crossed bulk/slab with four original QSQ-floor strata. Each material used the unperturbed field plus the original five perturbation fields, analyzed with BaderKit 0.10.2 on-grid, Henkelman Bader 1.05 on-grid and Henkelman near-grid.

The original run recorded 360 failures because a provenance gate compared decimal-serialized historical amplitudes at binary-ULP precision. All 360 were classified **before retry** as one pre-solver engineering/provenance family. An engineering-only retry preserved the panel, seeds, amplitudes, source identities, solvers and thresholds, and completed **360/360** blocked cells successfully.

Resolved results:

- **72/72** material–solver five-seed summaries complete;
- recreated BaderKit floors differ from frozen values by at most **8.71338e-11 e**;
- Henkelman on-grid: **24/24 classification agreement** at `1e-4`, `1e-3`, `1e-2 e`, agreement 100%, Cohen kappa 1.000 throughout, Spearman floor-rank **rho = 0.995**;
- Henkelman near-grid: 82.6%, 83.3%, 95.8% agreement across the three thresholds, floor-rank **rho = 0.754**.

**Gate outcome:** passed for targeted implementation transfer. QSQ is not an artifact of one software package under matched on-grid semantics, while near-grid differences demonstrate that numerical analysis semantics remain part of the measurement contract.

## P3B — Genuine electronic-structure grid convergence

**Status: DEFERRED_NO_NEW_DFT.**

The current submission will not add new DFT density-grid recomputation. This is a scope decision, not a positive convergence result. Existing provenance-audit assets remain available for future or reviewer-requested targeted calculations.

Consequent claim boundary:

- QSQ floor may be described as an **operational stability measure under the declared density representation and downstream-analysis contract**;
- it must not be called a grid-independent material constant;
- P3A must not be described as electronic-structure grid convergence or a unique physical Bader reference;
- interpolation/resampling must never be presented as a new DFT convergence calculation.

Source: `validation/qsq_prospective/P3B_SCOPE_DECISION.md`.

## P4 — Real chemical-decision case study

**Status: COMPLETE_RESOLVED.**

### Outcome-blind candidate construction

Before reading QSQ/codec/P2/P3A/Bader outcomes for candidate inclusion, a chemistry/provenance/geometry-only audit screened 68 NOMAD development slab states. It froze **five paired cases** across GaN electrochemical surfaces and RuO2 CO2RR chemistry. Pairing required same upload provenance, compatible lattice and density-grid shape, 1–4 added H/C/O atoms, persistent-host atom mapping and a geometry-selected local target atom.

This is a deliberately small case-study cohort, not prevalence evidence.

### Frozen reference gate

Before inspecting P4 charge outcomes, the reference rule was fixed: BaderKit on-grid and Henkelman on-grid must give the same non-zero `Delta q` sign, each `|Delta q| >= 0.02 e`, and inter-solver disagreement `<= 0.01 e`.

All **5/5** candidate pairs passed; the nine unique source states required **18/18 successful source solver calls**, with zero reference-ambiguous pairs.

### Frozen compression evaluation

Each pair used ZFP, SZ3 and SPERR at the common tight ladder `{1e-7, 3e-7, 1e-6, 3e-6}`. The first run produced 72 successes and 144 engineering-path failures. Before retry, all **144/144** failures were classified with zero unclassified: 72 SPERR work-directory creation failures and 72 Henkelman output-directory creation failures. An engineering-only retry executed exactly those failed keys without changing scientific settings.

Final accounting:

- **216/216 successful compressed solver cells**;
- **60/60** direct BaderKit qualitative charge-transfer-direction decisions preserved the frozen reference sign;
- adverse/zero-direction decisions: **0**.

### P4 interpretation

The prespecified qualitative sign endpoint is therefore a **null utility result for correctness**:

- no qualification retains 60/60 trials and has 0% direction error;
- frozen QSQ retains 36/60 trials (60% coverage; 3/5 pairs) and also has 0% direction error;
- coverage-matched realized-Linf selection and the archived float32 probe likewise have zero observed sign errors in their retained trials.

QSQ therefore does **not** improve correctness on this coarse endpoint because the unqualified common-tight baseline is already perfect. This result should not be converted post hoc into a positive chemical-utility claim.

The negative result is scientifically useful because it establishes a **measurement-contract boundary**: satisfying a strict `1e-3 e` numerical Bader contract and preserving a coarse sign-level chemical interpretation are distinct targets. QSQ is intentionally more conservative than the latter in this cohort.

Under the separately frozen optional second-solver audit workflow, QSQ-targeted escalation resolves all 60 decisions using **48 Henkelman reconstructed-state calls / 397.2 s**, versus **108 calls / 733.3 s** for escalating every trial. This is a reduction in audit burden relative to blanket independent checking, **not a correctness gain over the direct BaderKit decisions**, which already had zero errors.

**Gate outcome:** the P4 gate is satisfied through its prespecified alternative outcome: a useful negative result defining where screening does not improve a coarse chemical decision.

## P5 — Transfer beyond Bader

**Status: NO-GO FOR CURRENT SUBMISSION.**

A repository asset audit found no already-frozen, independently implemented second nonlinear/topology-sensitive QoI with a reference implementation, outcome-blind cohort and low marginal execution cost. Electron count and Hartree potential remain intentional controls rather than a second sensitive-task validation. Defining a new endpoint after observing the completed Bader evidence and the prespecified P4 null result would materially widen the scope and create avoidable outcome-driven-selection risk.

The current submission therefore stops at P4. P5 may be reconsidered only through an explicit scope-reopening addendum or a targeted reviewer request. The decision record is `paper/RESEARCH_SCOPE_FREEZE_20260911.md`.

## Execution order from the current checkpoint

1. Preserve the **FROZEN_FOR_SUBMISSION** scientific scope: P0–P4 resolved, P3B deferred, P5 no-go.
2. Maintain the PASS state of `paper/SUBMISSION_UPGRADE_CROSS_REFERENCE_AUDIT_20260911.md` while performing only non-scientific editorial changes.
3. Create a persistent archival release/DOI and record the submitted repository commit.
4. Apply target-journal figure-count, reference and formatting requirements without altering the locked estimands or primary evidence hierarchy.
5. Build the final Word/PDF submission package from the polished manuscript, locked real-data figures and current SI.

## Key provenance

- Authoritative status: `analysis/research_upgrade/CURRENT_STATUS.md`
- P1 report: `analysis/research_upgrade/P1_COMMON_TIGHT_REPORT.md`
- P2 report: `analysis/research_upgrade/P2_FRESH_PROBE_REPORT.md`
- P2 manifest: `validation/qsq_prospective/p2_fresh_probes/execution_manifest.json`
- P3A failure taxonomy: `analysis/research_upgrade/P3A_FAILURE_TAXONOMY.md`
- P3A resolved report: `validation/qsq_prospective/p3a_implementation_transfer_resolved/P3A_IMPLEMENTATION_TRANSFER_RESOLVED_REPORT.md`
- P3B scope decision: `validation/qsq_prospective/P3B_SCOPE_DECISION.md`
- P4 protocol: `validation/qsq_prospective/P4_CHEMICAL_DECISION_PROTOCOL.md`
- P4 reference/policy addendum: `validation/qsq_prospective/P4_REFERENCE_POLICY_ADDENDUM.md`
- P4 candidate audit: `validation/qsq_prospective/p4_candidate_audit/P4_CANDIDATE_AUDIT_REPORT.md`
- P4 reference report: `validation/qsq_prospective/p4_reference_adjudication/P4_REFERENCE_ADJUDICATION_REPORT.md`
- P4 failure taxonomy: `analysis/research_upgrade/p4_failure_taxonomy/P4_FAILURE_TAXONOMY.md`
- P4 resolved report: `validation/qsq_prospective/p4_chemical_decisions_resolved/P4_CHEMICAL_DECISION_REPORT.md`
- Active manuscript: `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`
