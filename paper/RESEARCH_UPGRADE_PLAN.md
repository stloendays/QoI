# QSQ research-strengthening plan

Opened 2026-09-11. Aim: a consequential, independently validated methods contribution suitable for a leading specialist journal, with broader-journal ambitions conditional on demonstrated scientific utility and transfer. Acceptance is not guaranteed by scale, presentation or naming.

## Current research status

The project is in **research strengthening**, not merely submission assembly. Frozen reconstruction data, the archived protocol and the five-seed QSQ implementation remain unchanged. New tests are additive and dated in provenance, while formal method names remain version-free.

The first executed audit is `analysis/research_upgrade/REPORT.md`, produced by `scripts/audit_qsq_research.py` in GitHub Actions run **34597116019** (SUCCESS).

| Bader tolerance | Full-record no-pass outcomes on non-evaluable materials | Base-only / common observed base rungs | Non-evaluable share of all decisions |
|---|---:|---:|---:|
| 1e-4 e | 518/533 = 97.2% | 616/740 = 83.2% | 624/762 = 81.9% |
| 1e-3 e | 296/310 = 95.5% | 296/524 = 56.5% | 333/762 = 43.7% |
| 1e-2 e | 61/108 = 56.5% | 61/119 = 51.3% | 75/762 = 9.8% |

The original counts reproduce exactly, but their interpretation was too strong. Tight-ladder access was targeted to 143 materials eligible at 1e-3 e. The full record adds 214 numerical passes at that threshold, all in the eligible group. Thus the >95% headline is ladder-design-sensitive and is not a design-independent estimate of causal misattribution. At 1e-4 e the base-only 83.2% must be interpreted against 81.9% non-evaluable prevalence, not advertised in isolation.

The second executed audit is retrospective four-seed screening with one held-out seed: 18/338 (5.33%), 12/947 (1.27%) and 1/1441 (0.0694%) held-out exceedances among admitted material-splits at 1e-4, 1e-3 and 1e-2 e. Material-cluster resampling is used. This is NOT prospective validation of the deployed five-seed rule.

## Work packages and acceptance gates

### P0 — Define the scientific target and correct the active claims

**Status:** mathematical groundwork written; active manuscript integration required in this batch.

Separate fixed-pipeline numerical agreement, reference perturbation robustness, and any coupled recompression robustness. Keep non-evaluable as an operational QSQ state; do not imply that an exact numerical comparison is undefined or that QSQ identifies which mechanism causally produced a particular codec error. Use `ROBUST_FIDELITY_FOUNDATIONS.md` for definitions, a lossless counterexample, and the separate-threshold versus combined-budget distinction.

**Deliverable:** revised Abstract/Results/Discussion/Methods and an explicit scope notice in active evidence summaries. Preserve old figures and numerical assertions as a labelled full-record analysis until their scientific update is rendered; no cosmetic relabelling of old numbers as common-ladder results.

**Gate:** every reported result names its target, perturbation family, ladder and population. No unqualified >95% causal attribution claim remains in the active manuscript.

### P1 — Remove unequal search opportunity

**Status:** base-only and shared-base-rung audits executed; uniform tight-ladder extension to prepare.

Build a work order for the 111 development materials without tight-ladder results, using the exact same four tight settings and all three codecs: **1,332 planned material-codec-setting jobs** before solver failures. Reuse the original density loader, codec configuration, atom mapping and Bader implementation. Log every requested job, including solver failures; never infer a pass from missing data.

Report full record, common base ladder and newly completed common extended ladder separately. Add realized-distortion support diagnostics, per-codec/stratum summaries, material-level bootstrap intervals, and paired changes. The extension removes one design confound but is not itself an independent cohort.

**Gate:** all scheduled cells accounted for; comparable candidate opportunities; honest treatment of missing results; scientific claims supported without selecting whichever ladder gives the largest percentage.

### P2 — Validate qualification on genuinely fresh perturbations

**Status:** retrospective fragility audit executed; prospective validation protocol and work order to prepare.

Freeze new seed streams, density/solver hashes, eligibility policy and analysis before new outcomes. Primary test: unchanged frozen five-seed QSQ decisions versus 59 fresh iid uniform-noise realizations per development material at the frozen amplitude. This is independent perturbation validation on previously studied materials, not new-material external validation. No tuning on these outcomes.

Add separately specified charge-neutral, nonnegative-density-preserving and spatially correlated perturbation controls; label unconstrained uniform noise as a numerical stress test, not an asserted physical uncertainty distribution. Study sample-budget effects using a separate calibration pool, with the same held-out panel for every budget.

Report useful coverage, conditional held-out exceedance risk, exact per-target binomial limits where the sampling assumptions hold, solver failures and cost. Five fixed probes are not a worst-case certificate. A development-calibrated risk-controlled extension must be frozen before a new test population and must not be called validated using reused data.

**Gate:** a stated risk target and confidence level are met on untouched outcomes, with multiplicity handled for simultaneous claims. If not met, report failure and revise on development data rather than relabel the test set as calibration.

### P3 — Separate algorithmic instability from continuum/representation error

**Status:** existing 12-system implementation comparison available; new convergence panel not run.

Prepare a deterministic 24-system panel stratified by bulk/slab and the four frozen QSQ floor bands, selecting three per stratum-band by a fixed hash order. This targeted panel is for mechanism, not population prevalence. Compare BaderKit on-grid, independent Henkelman on-grid/near-grid and an accurately implemented weighted-integration reference where available. Pin implementation versions and density conventions.

Use genuinely recomputed density grids where convergence is claimed; interpolation of an existing coarse grid is not a new DFT convergence result. Record native grid, cell/atom mapping, valence versus all-electron reference, periodicity and charge conservation. Quantify how floors, basin migration and scientific decisions change with representation and solver.

**Gate:** at least one validated grid-convergence/implementation comparison separates representation dependence from codec perturbation. A disappearing effect is reported as a boundary of the original claim, not hidden.

### P4 — Demonstrate a useful scientific decision and a remedy

**Status:** endpoint design pending; no new chemical outcome asserted.

Preselect a chemically meaningful matched-state task, such as adsorption-induced charge-transfer direction or site ordering. Freeze the atom/fragment correspondence, scientifically meaningful margins and reference-convergence requirements before inspecting compressed outcomes. Bader charge is not automatically a formal oxidation state.

Compare numerical-only scoring, archived float32 screening, frozen QSQ and a development-calibrated extension. Evaluate wrong-decision rate versus coverage and total compute/storage cost. Include matched-coverage random or cheap-proxy rejection controls. A reject-everything policy is not a successful method.

For uncertain cases, compare a fixed escalation rule (better numerical integration or a finer reference calculation) with blanket rejection. Establish whether QSQ can target costly reanalysis effectively rather than merely remove difficult cases. No agent component is necessary for this scientific test.

**Gate:** a preregistered task shows improved decision reliability at nontrivial coverage and a measured cost, or a useful negative result establishes where screening does not help.

### P5 — Transfer beyond Bader and compare with relevant prior methods

**Status:** protocol design pending; no second-task validation claimed.

Select one independent topology-sensitive task on non-DFT scalar-field data, for example isosurface connectivity or topology-based segmentation. Freeze its field set, invariants, perturbation model and decision threshold before evaluation. Electron count and Hartree potential remain controls, not evidence of transfer to a second sensitive task.

Compare with appropriate topology-preserving compression where its guarantees match the task. Do not assume contour-tree preservation guarantees Bader basins. Audit numerical-validation and selective-prediction prior art as well as QoI compression, so the novelty is not claimed solely from introducing an abstention state.

**Gate:** qualification predicts held-out decision fragility or a demonstrable utility gain on the independent task; otherwise limit the paper to density-derived chemical analysis.

## Execution order

P0 and the completed-data part of P1/P2 now; prepare immutable work orders next. Run the common tight-ladder extension and fresh-seed validation using the original compute pipeline. Convergence and scientific-decision tests follow, with second-task transfer only after the gate itself is validated. Do not spend the next iteration on more decorative figures, another acronym, an unrelated agent, or a larger cohort that leaves the same identification problem unresolved.

## Reproducibility and handoff

- Audit source: `scripts/audit_qsq_research.py`.
- Exact results and SHA-256 manifest: `analysis/research_upgrade/`.
- Mathematical target definitions: `paper/ROBUST_FIDELITY_FOUNDATIONS.md`.
- New-work specification: `validation/qsq_prospective/PROTOCOL.md`.
- Work orders are specifications, not executed measurements. New density/codec/Bader runs must be explicitly recorded before their tasks are marked complete.

## Primary background sources checked for this plan

NIST exact binomial confidence limits: https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm

Yu and Trinkle, Accurate and efficient algorithm for Bader charge integration: https://arxiv.org/abs/1010.4916

Yan et al., TopoSZ: Preserving Topology in Error-Bounded Lossy Compression: https://arxiv.org/abs/2304.11768

These sources establish relevant statistical/numerical/topological context; they do not establish the novelty or success of the proposed QSQ extension.
