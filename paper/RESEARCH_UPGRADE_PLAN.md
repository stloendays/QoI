# QSQ research-strengthening plan

Opened 2026-09-11. Aim: a consequential, independently validated methods contribution suitable for a leading specialist journal, with broader-journal ambitions conditional on demonstrated scientific utility and transfer. Acceptance is not guaranteed by scale, presentation or naming.

## Current research status

The project remains in **research strengthening**, not merely submission assembly. Frozen reconstruction data, the archived protocol and the deployed five-seed QSQ gate remain unchanged. New tests are additive and dated in provenance, while reader-facing method names remain version-free.

The concise authoritative execution snapshot is maintained in `analysis/research_upgrade/CURRENT_STATUS.md`.

Current package state:

- **P0 COMPLETE:** active manuscript claims distinguish fixed-pipeline numerical fidelity from reference robustness.
- **P1 COMPLETE:** 1,332/1,332 common-tight-ladder reconstructions are accounted successfully.
- **P2 COMPLETE:** 14,986/14,986 pre-registered fresh perturbation trials are valid; the frozen gate was not retuned.
- **P3A COMPLETE_WITH_RECORDED_FAILURES:** 432/432 planned implementation-transfer solver cells are accounted, but only 72 rows succeeded and 360 are recorded failed/unresolved; only 4/24 materials are complete across the comparison. This is not a passed 24-system validation.
- **P3B NOT EXECUTED:** true grid convergence still requires genuinely recomputed density grids or recoverable electronic-structure inputs.
- **P4 OUTCOME-BLIND PROTOCOL FROZEN:** no new chemistry-decision outcome has been evaluated yet.
- **P5 NOT STARTED.**

### Corrected historical audit

The original full-record counts reproduce exactly, but their interpretation was too strong. Tight-ladder access was targeted to 143 materials eligible at 1e-3 e; the full record adds 214 numerical passes at that threshold, all in the eligible group. Thus the historical >95% headline is ladder-design-sensitive and is not a design-independent estimate of causal misattribution.

| Bader tolerance | Full-record no-pass outcomes on non-evaluable materials | Base-only / common observed base rungs | Non-evaluable share of all decisions |
|---|---:|---:|---:|
| 1e-4 e | 518/533 = 97.2% | 616/740 = 83.2% | 624/762 = 81.9% |
| 1e-3 e | 296/310 = 95.5% | 296/524 = 56.5% | 333/762 = 43.7% |
| 1e-2 e | 61/108 = 56.5% | 61/119 = 51.3% | 75/762 = 9.8% |

The retrospective four-seed/one-held-out-seed diagnostic gives 18/338 (5.33%), 12/947 (1.27%) and 1/1441 (0.0694%) held-out exceedances among admitted material-splits at 1e-4, 1e-3 and 1e-2 e. These correlated reused-seed splits are not prospective validation of the deployed five-seed rule.

### P1 prospective equal-search result

Completing the same four tight settings for the 111 previously uncovered materials adds **1,332/1,332 successful reconstructions**. At the primary `1e-3 e` threshold, failure to find a numerical pass occurs in **3.3% of eligible** versus **66.4% of QSQ screen-rejected** material–codec pairs, a **20.34x risk ratio**. Secondary risks are 10.9% versus 79.3% at `1e-4 e` and 0.0% versus 68.0% at `1e-2 e`.

This removes unequal tight-search opportunity as the explanation for the observed separation, but does not by itself validate unseen reference perturbations or establish codec causality.

### P2 prospective fresh-perturbation result

The deployed five-seed QSQ gate was frozen before running **59 pre-registered fresh iid-uniform perturbations per development material**, for **14,986/14,986 valid outcomes and zero unresolved trials**.

At the pre-specified primary threshold `1e-3 e`, QSQ admits **143/254 materials (56.3% coverage)**. Fresh-threshold exceedance risk is **1.600%** in admitted materials (135/8,437; 95% material-cluster CI 0.782–2.596%) versus **81.325%** in the 111 screen-rejected materials (5,326/6,549; CI 75.981–86.257%), giving a **50.83x rejected/eligible risk ratio**. At least one fresh exceedance occurs in 20/143 admitted versus 110/111 rejected materials.

The prespecified secondary thresholds preserve the same direction: `1e-4 e`, 4.016% versus 86.938% (21.65x); `1e-2 e`, 0.148% versus 79.593% (537.69x).

This prospectively validates **risk stratification conditional on the development materials and declared iid-uniform perturbation model**. It is not a worst-case stability guarantee, not a simultaneous per-material certificate and not new-material generalization.

P1/P2 have been integrated into `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`. Figure 3 has been redesigned around equal-search and prospective-risk evidence; formal PNG/PDF/SVG outputs were rendered successfully in run **34605839019** and committed in **f0693a35475f9b2a12af5ce9b1f12a4ef4c8429a**.

## Work packages and acceptance gates

### P0 — Define the scientific target and correct the active claims

**Status: COMPLETE.** Active Abstract/Results/Discussion/Methods distinguish fixed-pipeline numerical agreement, reference perturbation robustness and any stronger coupled robustness target. No unqualified historical >95% causal-attribution claim remains as the central result.

Separate fixed-pipeline numerical agreement, reference perturbation robustness, and any coupled recompression robustness. Keep non-evaluable as an operational QSQ state; do not imply that an exact numerical comparison is undefined or that QSQ identifies which mechanism causally produced a particular codec error. Use `ROBUST_FIDELITY_FOUNDATIONS.md` for definitions, a lossless counterexample, and the separate-threshold versus combined-budget distinction.

**Gate:** every reported result names its target, perturbation family, ladder and population.

### P1 — Remove unequal search opportunity

**Status: COMPLETE. 1,332/1,332 scheduled common-tight-ladder measurements succeeded; final failure count = 0.** The first pass contained 24 source-download timeouts from two NOMAD materials; those exact keys were retried without changing codec, Bader, tolerance or source-identity semantics and all completed.

The historical full record, common base ladder and newly completed common extended ladder remain separate analyses. No pass is inferred from missing data.

**Gate outcome:** PASSED for accounting and equalized candidate opportunity. The resulting association is reported with eligible and screen-rejected denominators rather than as a causal codec-failure fraction.

### P2 — Validate qualification on genuinely fresh perturbations

**Status: COMPLETE. 14,986/14,986 fresh perturbation outcomes valid; unresolved = 0; original five-seed QSQ gate unchanged.** Primary `1e-3 e` result: 56.3% acceptance coverage with 1.600% fresh exceedance risk in eligible materials versus 81.325% in screen-rejected materials (50.83x risk ratio).

The primary test used 59 frozen fresh iid-uniform PRNG streams per development material at the original material-specific amplitude. New outcomes were not used to retune eligibility. The `1e-4` and `1e-2 e` rows are prespecified secondary endpoints evaluated on the same fresh response vectors rather than independent experiments.

Charge-neutral, nonnegative-density-preserving and spatially correlated perturbation controls remain distinct future model extensions; they are not pooled into the iid-uniform validation sample. Uniform noise is a numerical stress-test model, not an asserted physical uncertainty distribution.

**Gate outcome:** strong prospective discrimination is established for the stated perturbation model on the development materials. Finite panels do not establish worst-case robustness or new-material transfer.

### P3 — Separate algorithmic instability from continuum/representation error

**Status: P3A COMPLETE_WITH_RECORDED_FAILURES; P3B NOT EXECUTED.** P3A run **34605557997** accounted all **432/432** planned solver cells on the frozen 24-system panel, but only **72** rows succeeded and **360** are recorded failed/unresolved. Aggregate results were retained and committed in **99f5adcaf08f7556b5d05fdb16f75b465592f52b**. Only **4/24 materials** currently have complete five-seed implementation-transfer results, so P3A has not passed the full-panel gate.

Among those four complete materials, recreated BaderKit floors match the frozen floors to a maximum absolute difference of **1.54445e-11 e**. Henkelman on-grid classifications agree 100% with frozen BaderKit at `1e-4`, `1e-3` and `1e-2 e` (Cohen kappa 1.0; floor-rank Spearman rho 1.0). Henkelman near-grid is less consistent (agreement 50% / 75% / 75%; floor-rank rho 0.4), which currently defines an implementation-sensitive boundary rather than a universal reference.

One inspected failed shard shows a provenance-gate issue rather than a Bader-solver failure: the source-rederived float32 amplitude and the historical CSV value differ only at serialized decimal precision, while the hard ULP-based equality check was far tighter than the stored text precision. This finding cannot yet be extrapolated to all 360 failures. Every failed row must be classified by stage/signature before deciding which cells are eligible for an engineering-only rerun.

The deterministic 24-system panel remains frozen. Any rerun may repair only infrastructure/provenance validation logic; material selection, perturbation fields, solver definitions and scientific thresholds must not be changed because of observed outcomes. The original failed run remains provenance.

P3B grid convergence requires genuinely recomputed electronic-density grids where convergence is claimed; interpolation of an existing coarse grid is not accepted as a new DFT convergence result.

**Gate:** full-panel implementation-transfer evidence remains open until unresolved P3A rows are correctly classified/recovered. At least one genuine grid-convergence comparison is still required for P3B.

### P4 — Demonstrate a useful scientific decision and a remedy

**Status: OUTCOME-BLIND PROTOCOL FROZEN; no new chemistry-decision outcome executed.** Case-selection and evaluation rules were frozen before inspecting P3A outcomes so that the chemistry demonstration cannot be selected post hoc for a favorable Bader anomaly.

Use a chemically meaningful matched-state task, such as adsorption-induced charge-transfer direction or site ordering. Keep atom/fragment correspondence, scientific margins and reference-convergence requirements fixed. Bader charge is not automatically a formal oxidation state.

Compare numerical-only scoring, archived float32 screening, frozen QSQ and any legitimately development-calibrated extension. Evaluate wrong-decision rate versus coverage and total compute/storage cost, with matched-coverage random or cheap-proxy rejection controls. A reject-everything policy is not a successful method.

For uncertain cases, compare a fixed escalation rule (better numerical integration or a finer reference calculation) with blanket rejection. Establish whether QSQ can target costly reanalysis effectively rather than merely remove difficult cases.

**Gate:** a preregistered task shows improved decision reliability at nontrivial coverage and measured cost, or a useful negative result establishes where screening does not help.

### P5 — Transfer beyond Bader and compare with relevant prior methods

**Status: NOT STARTED; protocol design pending and no second-task validation claimed.**

Select one independent topology-sensitive task on non-DFT scalar-field data, for example isosurface connectivity or topology-based segmentation. Freeze its field set, invariants, perturbation model and decision threshold before evaluation. Electron count and Hartree potential remain controls, not evidence of transfer to a second sensitive task.

Compare with appropriate topology-preserving compression where its guarantees match the task. Do not assume contour-tree preservation guarantees Bader basins. Audit numerical-validation and selective-prediction prior art as well as QoI compression, so the novelty is not claimed solely from introducing an abstention state.

**Gate:** qualification predicts held-out decision fragility or a demonstrable utility gain on the independent task; otherwise limit the paper to density-derived chemical analysis.

## Execution order from the current checkpoint

1. Audit all 360 P3A failed rows by stage/error signature.
2. If the over-strict amplitude serialization check is systematic, correct only that provenance/engineering gate with a predeclared tolerance appropriate to stored decimal precision, preserve the failed run, and rerun only unresolved cells with unchanged science.
3. Recompute the full 24-system P3A transfer table only after complete accounting; do not headline the current four-material complete-case statistics.
4. Execute P3B only where genuinely recomputed density grids can be recovered/generated.
5. Then execute the already outcome-blind P4 chemistry-decision test.
6. Consider P5 only after P3/P4 establish a sufficiently strong scientific utility/transfer case.

Do not spend the next iteration on decorative figures, another acronym, an unrelated agent or a larger cohort that leaves the same identification problem unresolved.

## Reproducibility and handoff

- Authoritative current status: `analysis/research_upgrade/CURRENT_STATUS.md`.
- Historical audit source: `scripts/audit_qsq_research.py`.
- P1 final report: `analysis/research_upgrade/P1_COMMON_TIGHT_REPORT.md`.
- P2 final report: `analysis/research_upgrade/P2_FRESH_PROBE_REPORT.md`.
- P2 manifest: `validation/qsq_prospective/p2_fresh_probes/execution_manifest.json`.
- Mathematical target definitions: `paper/ROBUST_FIDELITY_FOUNDATIONS.md`.
- P3 protocol: `validation/qsq_prospective/P3_NUMERICAL_VALIDATION_PROTOCOL.md`.
- P3A report: `validation/qsq_prospective/p3a_implementation_transfer/P3A_IMPLEMENTATION_TRANSFER_REPORT.md`.
- Current manuscript: `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`.

## Primary background sources checked for this plan

NIST exact binomial confidence limits: https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm

Yu and Trinkle, Accurate and efficient algorithm for Bader charge integration: https://arxiv.org/abs/1010.4916

Yan et al., TopoSZ: Preserving Topology in Error-Bounded Lossy Compression: https://arxiv.org/abs/2304.11768

These sources establish relevant statistical/numerical/topological context; they do not establish the novelty or success of the proposed QSQ extension.
