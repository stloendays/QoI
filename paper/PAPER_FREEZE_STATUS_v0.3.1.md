# Paper freeze status — v0.3.1

Date: 2026-09-06
Branch: `analysis/paper-freeze-v03-20260906`
Frozen data branch: `main` remains untouched by this editorial/statistical branch.

## Status

**Scientific manuscript state: conditionally frozen.**

The central evaluation, stability, statistical-robustness, mechanism-consistency and engineering claims are now fixed for manuscript v0.3.1. No additional full compression/Bader benchmark run is currently justified.

The only remaining scientific data dependency is the pending full per-atom mechanism file:

`mechanism/basin_error_decomposition_per_atom.csv`

As of this freeze, that file is not yet present on `main`. When it lands, it may update Figure 3 and the direct-mechanism paragraph only. It must not automatically reopen Protocol A.1, the master benchmark, the realized-Linf analysis or the overall manuscript story.

## Frozen manuscript identity

**Title:**

> Pointwise Error Bounds Do Not Define Chemical Fidelity: Stability and Domain Migration in Lossy-Compressed Electron Densities

**One-sentence thesis:**

> A pointwise reconstruction guarantee is not a chemical-fidelity contract when the downstream observable is defined on field-derived domains; the observable must be re-derived, shown to be numerically resolvable, and evaluated at the realized perturbation scale.

**Paper identity:** computational-science / chemical-informatics methodology and evaluation, demonstrated on Bader analysis of DFT electron-density fields; not a claim to introduce a new compressor.

## Frozen primary evidence

### Re-derived downstream analysis

- Successful master table: 6,343 reconstructions, 254 development materials.
- Base ladder: 4,627 successful rows.
- Re-derived Bader error exceeds fixed-basin error in 99.7% of base-ladder rows.
- Fixed-domain error remains a diagnostic, not the primary chemical-fidelity endpoint.

### Nominal versus realized error

- ZFP median realized/nominal Linf = 0.1575.
- SZ3 and SPERR medians are approximately 1.000.
- Same-nominal codec gaps must therefore be described as a mixture of bound-utilization and residual-structure effects.

### Realized-Linf-controlled residual

Primary Protocol-A.1-qualified result at tau=1e-3 e and 0.10-dex matching:

- SZ3/ZFP = 1.90x [1.70, 2.20].
- SPERR/ZFP = 1.87x [1.63, 2.08].

Conservative complete-case sensitivity after removing every material with any registered downstream failure at nominal relative tolerance <=0.01:

- 254 -> 234 materials.
- SZ3/ZFP = 1.82x [1.68, 2.01].
- SPERR/ZFP = 2.00x [1.79, 2.25].
- Common-support interpolation = 2.07x [1.95, 2.19] and 1.99x [1.83, 2.21].

Interpretation: codec identity remains associated with an approximately twofold downstream-error difference after measured pointwise magnitude and QoI resolvability are controlled. Do not call this a causal codec effect.

### Direct and statistical mechanism evidence

Representative 12-material direct mechanism set:

- 106 successful cases.
- max decomposition closure residual <=2.22e-16 e.
- median bounded domain dominance = 0.995.
- IQR = 0.965–0.999.
- 84.9% of cases >0.90.

Full-benchmark complete-case attenuation at tau=1e-3 e:

- SZ3/ZFP 2.34x -> 0.96x after adding basin reassignment.
- SPERR/ZFP 2.08x -> 0.94x.
- reassignment log-log coefficient = 0.880 [0.723,1.037], p=5.78e-28.

Interpretation: direct decomposition establishes domain dominance only in the representative mechanism set; full-table reassignment supplies mechanism-consistent attenuation, not formal causal mediation.

### Global-conservation negative control

Adding `electron_count_abs_dev` does not absorb the codec-associated residual:

- SZ3/ZFP 2.34x -> 2.58x.
- SPERR/ZFP 2.08x -> 2.06x.

With electron-count deviation and reassignment both included:

- SZ3/ZFP = 1.02x.
- SPERR/ZFP = 0.94x.
- electron-count coefficient = -0.017 [-0.040,0.006], p=0.139.
- reassignment coefficient = 0.879 [0.722,1.036], p=5.25e-28.

This rules against simple global integral/conservation error as the explanation of the residual and strengthens the domain-redistribution interpretation.

### Protocol-A.1 resolvability

Across 319 systems:

- non-evaluable at 1e-4 e: 79.9%.
- non-evaluable at 1e-3 e: 41.4%.
- non-evaluable at 1e-2 e: 9.7%.

These are QoI-eligibility states, not codec failures.

Use `Protocol-A.1 numerical stability floor at the stated perturbation amplitude`; never imply an intrinsic material constant.

### Probe validation

Calibration results supporting A.1:

- archived float32 probe median exact-neighbour ties: 82; matched-amplitude random noise: 0.
- zero voxel reassignment: 9/18 under float32 versus 2/18 under random noise.
- matched-probe stability-floor contrast: median 29x.
- five-seed floor span: median 0.47 decades, max 2.39.
- 0.1x-to-10x amplitude change shifts floor by median 0.76 decades.

### Symmetry sensitivity

Known symmetry-equivalent relabeling case: `aflow-Al8Cu4U1_ICSD_601801`.

Removing this one known case changes overall A.1 non-evaluable fractions only slightly:

- 1e-4 e: 79.94% -> 79.87%.
- 1e-3 e: 41.38% -> 41.19%.
- 1e-2 e: 9.72% -> 9.43%.

Retain frozen primary A.1; present symmetry-aware handling as sensitivity only.

### Certified compression frontier

No universal codec winner.

- At 1e-2 e, SZ3 maximizes compression ratio but ZFP generally offers higher certification coverage.
- Near 1e-3 e, SZ3 and ZFP are comparable in bulk; ZFP has higher slab coverage.
- At 1e-4 e, ZFP leads the bulk best-certified compression ratio.
- Only four slab materials are admitted at 1e-4 e; that strictest slab frontier is descriptive only.

## Manuscript and reproducibility assets

Primary manuscript:

- `paper/MANUSCRIPT_CHATGPT_v0.3.1.md`

Statistical/reporting freeze:

- `paper/STATISTICAL_ANALYSIS_PLAN_CHATGPT_v1.md`
- `paper_data_v03/HEADLINE_NUMBER_REGISTRY_v03.md`
- `paper_data_v03/HEADLINE_NUMBER_REGISTRY_v03.csv`

Reviewer and submission controls:

- `paper/REVIEWER_PREMORTEM_CHATGPT_v0.3.md`
- `paper/SUBMISSION_READINESS_GATE_v0.3.md`
- `paper_data_v03/manuscript_lint_v031.md`

Main-figure planning:

- `paper/FIGURE_CAPTIONS_CHATGPT_v0.3.md`
- `figures_v03/Figure2_fixed_vs_resolved_draft.{pdf,svg,png}`
- `figures_v03/Figure4_resolvability_probe_draft.{pdf,svg,png}`
- `figures_v03/Figure5_magnitude_structure_draft.{pdf,svg,png}`
- `figures_v03/Figure6_certified_frontier_draft.{pdf,svg,png}`

Supplement planning:

- `paper/SUPPLEMENTARY_FIGURE_MAP_CAPTIONS_v0.3.md`

Bibliography:

- `paper/REFERENCE_AUDIT_CHATGPT_v0.3.md`
- `paper/references_core_verified.bib`

Key analysis outputs:

- `analysis_output/complete_case_failure_sensitivity.md`
- `analysis_output/reviewer_stress_tests.md`
- `analysis_output/fixed_basin_ratio_robustness.md`
- `paper_data_v03/global_conservation_negative_control.md`

## Automated scientific-claim audit

Latest manuscript lint:

- checks: 32.
- passed: 32.
- failed: 0.

The lint verifies frozen headline numbers, representative-set mechanism scope, non-causal attenuation wording, Protocol-A.1 floor semantics, explicit n=4 strict-slab caveat, NON_EVALUABLE semantics, and core ZFP/SZ3/SPERR citation mapping.

## Rules after this freeze

Do not reopen the master story merely because:

- a new generic codec becomes available;
- another random probe seed gives a different individual floor;
- an average/RMS atom metric looks more favorable than the frozen max-atom contract;
- the per-atom table shows expected atom-level heterogeneity without reversing the preregistered case/material summaries;
- a topology-aware compressor appears promising.

Any such work is an optional extension or future study unless it reveals a genuine error in the frozen data or analysis.

## Remaining hard dependency

**One item:** the pending per-atom mechanism table.

When it lands:

1. verify per-atom closure;
2. aggregate to case/material before inference;
3. run material bootstrap and leave-one-material-out sensitivity;
4. compare all-atom mechanism summaries with the current maximum-error-atom summary;
5. update Figure 3 and the mechanism paragraph if required;
6. rerun manuscript lint;
7. then choose target journal and apply venue-specific formatting.

Until that file lands, no new full benchmark calculation is recommended.
