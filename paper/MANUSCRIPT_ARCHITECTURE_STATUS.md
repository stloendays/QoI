# Manuscript architecture status

Updated: 2026-09-07

## Executive status

The scientific architecture of the JCTC manuscript is substantially complete. The development evidence chain is closed through the benchmark, Protocol A.1 stability qualification, lossless/lossy comparison, sensitivity analyses, and the representative per-atom mechanism decomposition. The only remaining primary scientific gate is the frozen corpus-scale external rate–fidelity validation now running on the 65-system external corpus, with the pre-specified 63-system confirmatory cohort used for headline external rate–fidelity claims.

A submission-oriented working draft now exists at `paper/MANUSCRIPT_DRAFT.md`. It replaces the old chronological Stage-0/Stage-1 logic with the final methodological sequence: provenance → intrinsic QoI stability → eligibility → approximation → downstream re-analysis → topology audit → certification → rate–fidelity. `RESULTS.md` is retained as a historical research log rather than silently rewritten or treated as the final manuscript.

## Evidence backbone

### 1. Development benchmark — COMPLETE

- `benchmark/master_benchmark_full.csv`
- 6,343 retained rows across 254 materials.
- 4,627 base-ladder rows plus 1,716 tight-ladder rows.
- Three production codecs: ZFP, SZ3, SPERR.
- Both fixed-basin and re-derived/resolved Bader errors retained.
- Realized L-infinity error and requested/realized ratio retained for every successful row.
- Protocol A.1 eligibility and certification flags retained at 1e-4, 1e-3 and 1e-2 e.

The tight-rung data are therefore no longer pending; any manuscript/figure note that says otherwise is stale.

### 2. QoI stability qualification — COMPLETE

Protocol A.1 replaces the archived order-preserving float32 probe with the frozen five-seed equal-amplitude uniform-noise probe. The development and external stability tables support the central methodological requirement that a QoI must be shown to be intrinsically stable at the requested scientific tolerance before compression fidelity can be judged.

### 3. Fixed-basin versus re-derived evaluation — COMPLETE

The full benchmark directly supports the distinction between integrating over the original partition and re-deriving the Bader partition after reconstruction. The fixed-basin path is retained as a diagnostic only; certification uses the resolved/re-derived QoI.

### 4. Topological mechanism — COMPLETE FOR THE PRE-SPECIFIED REPRESENTATIVE SET

The previously thin mechanism layer is now materially stronger because the atom-level table is present:

- `mechanism/basin_error_decomposition_summary.csv`
- `mechanism/basin_error_decomposition_per_atom.csv`
- 1,665 per-atom rows.
- 12 representative materials spanning the pre-selected stability regimes.
- ZFP, SZ3 and SPERR across the three mechanism tolerances.
- 106 successful material/codec/tolerance points; two additional ZFP points failed in BaderKit and are explicitly registered in `failure_registry.csv`.
- Row identity: `dq_integrand + dq_domain = dq_total`, with reported residual no larger than 2e-16.
- At the atom carrying the largest absolute total error for each successful point, the reported median domain-term share is 0.9995.

This closes the earlier data-availability gap for a per-atom mechanism audit. The defensible manuscript claim should remain scoped to the representative mechanism set: the dominant error at the worst-affected atom is overwhelmingly associated with partition/domain migration, rather than asserting population-wide universality from 12 materials alone.

### 5. Rate–fidelity and lossless comparison — COMPLETE ON DEVELOPMENT DATA

- `benchmark/best_certified_a1.csv`
- `benchmark/summary_a1.csv`
- `benchmark/pairwise_a1.csv`
- `benchmark/lossless_baselines.jsonl`

These files close the development-side answer to whether lossy compression remains worthwhile after honest QoI qualification.

### 6. Sensitivity, negative results and failure semantics — COMPLETE

The supplementary sensitivity analyses, archived/null algorithmic tracks, explicit failure registry and Protocol A/A.1 record provide the audit trail needed to distinguish scientific non-replication, numerical instability, codec-row failure and material-level pipeline failure.

### 7. External generalization — STABILITY COMPLETE; RATE–FIDELITY IN PROGRESS

External stability qualification is complete on the frozen 65-system corpus. The formal rate–fidelity Full run is GitHub Actions run `34074537547` on trigger commit `893f931b3045b0b628329db81999c2f439d4e830`.

Reporting populations are frozen before corpus-scale execution:

- descriptive external corpus: 65 systems = 37 AFLOW bulk + 28 NOMAD 2D;
- primary confirmatory external rate–fidelity cohort: 63 systems = 36 AFLOW bulk + 27 NOMAD 2D;
- implementation sentinels excluded from the confirmatory rate–fidelity cohort only: `aflow-Ni1_ICSD_181716` and `nomad2d-0XHkHlmw3DQ_`.

No external outcome is permitted to change Protocol A.1, codec settings, tolerance ladders, eligibility rules, early stopping, failure accounting or the frozen confirmatory cohort.

## What the manuscript can already be built around

The current narrative spine is stable:

1. Pointwise error control is not a chemical-fidelity guarantee.
2. A fixed-domain/fixed-basin evaluation can materially understate the scientific error because the observable's domain changes after reconstruction.
3. Atom-level decomposition shows that, in the representative mechanism set, the worst-affected atom is dominated by the domain-migration term.
4. The downstream observable has its own numerical/topological stability floor; therefore a QoI contract must be stability-qualified before any codec is judged.
5. Under Protocol A.1, lossy compression still offers useful storage reduction, but the honest certified ratios are materially lower than naive fixed-basin estimates.
6. Requested pointwise error and realized perturbation differ systematically by codec, so nominal tolerance alone is not an equal-perturbation comparison.
7. Independent external validation tests which development conclusions transfer without retuning.

The new manuscript draft expresses this as a general scientific-data certification framework rather than as a narrow three-codec benchmark. Bader charge is presented as the topology-sensitive chemical case study, not as a claim of universal coverage of downstream QoIs.

## Remaining work before a submission-ready manuscript

### Scientific gate

Only one primary gate remains: finish and audit the frozen external Full run, then report all-65 descriptive results and the pre-specified confirmatory-63 rate–fidelity results.

### Documentation / writing work

These are not new experiments:

- refresh `paper/CLAIM_EVIDENCE_MATRIX.md` using the atom-level mechanism dataset and completed external run;
- update the external-status portions of `paper/FIGURE_MAP.md` after the Full run;
- fill the pending external-transfer Results subsection in `paper/MANUSCRIPT_DRAFT.md` only after aggregate audit;
- finalize figure scripts and captions against release paths, using R in GitHub Actions for submission figures;
- add and verify literature citations in the Introduction/Discussion without changing the frozen scientific claims;
- perform a final JCTC-style compression pass on wording, Methods redundancy, figure references and Supporting Information cross-references;
- keep limitations integrated into the relevant Results/Discussion sections rather than requiring a standalone limitations section.

## Release-builder warning

The local `build_release_package.py` was reported to regenerate `benchmark/`, `stability/`, `mechanism/`, `supplement/`, `paper/` and `protocol/`. The script itself is not currently present in this remote repository, so it cannot be patched here yet. Before the external branch is merged and the local release is rebuilt, the builder must be changed or guarded so that manually maintained cloud files in `protocol/` and `paper/` are not silently deleted. In particular, preserve:

- `protocol/EXTERNAL_RATE_FIDELITY_ANALYSIS_PLAN.md`
- `protocol/QOI_WORKFLOW_SPEC_V1.yaml`
- `paper/MANUSCRIPT_DRAFT.md`
- this manuscript status record and the final external-validation documentation.

## Bottom line

The project is no longer in a data-discovery phase. It is in the final evidence-lock and manuscript-integration phase. Development benchmark, QoI qualification, mechanism, rate–fidelity and supporting controls are available; the submission-oriented workflow prose is now drafted; external corpus-scale rate–fidelity validation remains the final primary scientific dependency.