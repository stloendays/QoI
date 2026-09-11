# Research-strengthening execution status

Updated 2026-09-11 after the initial work-package plan was written. This status note supersedes the plan's initial in-batch preparation/integration status lines; the scientific aims and acceptance gates are unchanged.

## Completed and checked

1. Common-ladder and retrospective seed-holdout analyses executed on frozen inputs. GitHub Actions run `34597116019`: SUCCESS. The original Figure 3 counts reproduce exactly. See `REPORT.md`, `ladder_summary.csv`, `ladder_transitions.csv`, `seed_holdout_summary.csv` and `manifest.json` in this directory.
2. Confirmation work orders generated and committed. GitHub Actions run `34597860220`: SUCCESS. See `validation/qsq_prospective/execution_manifest.json`: 1,332 missing tight-ladder jobs on 111 materials, 14,986 fresh-seed probe jobs on 254 previously studied materials, and a deterministically stratified 24-system convergence panel.
3. The active manuscript, README, Current Paper Story and Claim-Evidence Matrix were edited to distinguish numerical fidelity from reference robustness and to qualify the ladder-dependent headline. Before/after SHA-256 values are in `integration_manifest.json`. Existing numerical figures retain their historical full-record counts; they were not relabelled as common-ladder results.
4. Mathematical target definitions and an evidence-gated research plan are in `paper/ROBUST_FIDELITY_FOUNDATIONS.md` and `paper/RESEARCH_UPGRADE_PLAN.md`.
5. Notion project page was updated and a linked plan created: https://app.notion.com/p/3d8c0ee7c03e8183a582ecc758eb30bc . The parent project page now foregrounds the new audit and labels earlier broad completeness/headline statements as historical.

## Critical findings

The full-record reclassification fractions 97.2% / 95.5% / 56.5% become 83.2% / 56.5% / 51.3% under the common base ladder. At 1e-3 e all 214 extra passes contributed by the tight extension belong to the eligible group. At 1e-4 e the common-base 83.2% must be interpreted together with 81.9% non-evaluable prevalence. These are conditional descriptive counts, not causal attribution probabilities.

Retrospective four-to-one seed holdout produces 18/338, 12/947 and 1/1441 exceedances among admitted material-splits. This diagnoses finite-panel fragility, not the independently measured error rate of the deployed five-seed rule. Repeated splits are clustered by material.

## Prepared, not executed

All new tight-ladder, fresh-probe and convergence work orders remain `PREPARED_NOT_EXECUTED`. No new density, codec reconstruction or Bader charge measurement was produced in these preparation workflows. No new material-level external validation was performed.

The immediate next dependency is to bind the work orders to the original density-loader and compute-runner commit, validate baseline-density/atom correspondence and pin solver/environment fingerprints before scientific execution. The work-order manifest records these dependencies explicitly. Chemical-decision utility, an independently calibrated extension and second-task transfer remain unmeasured research work packages.

Frozen benchmark, stability and archived protocol inputs were not altered. Method names remain version-free in reader-facing text; historical file names and schemas are preserved.
