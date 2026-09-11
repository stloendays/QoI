# QSQ research upgrade — current status

Last synchronized: **2026-09-11 22:27 Asia/Singapore**.

This file is the concise status record for the active research-strengthening phase. Historical benchmark/protocol outputs remain frozen; all prospective work is additive.

## Overall

- **P0 — claim correction / target definition: COMPLETE.** The active manuscript distinguishes fixed-pipeline numerical fidelity from reference robustness and no longer treats the historical >95% full-record number as a design-independent causal misattribution rate.
- **P1 — equal search opportunity: COMPLETE.** 1,332/1,332 additive common-tight-ladder reconstructions were accounted successfully; no final failures remain.
- **P2 — prospective fresh-perturbation validation: COMPLETE.** 14,986/14,986 pre-registered fresh perturbation trials succeeded with the original five-seed QSQ gate unchanged.
- **P3A — implementation transfer: COMPLETE.** The original first run is retained with its recorded pre-solver failures; a failure taxonomy was frozen before an engineering-only retry. The 20 blocked materials were then rerun with unchanged scientific definitions. Retry accounting is 360/360 success, giving complete five-seed summaries for all 24 materials and all three solvers.
- **P3B — true grid convergence: NOT EXECUTED.** Requires genuinely recomputed electronic-density grids or recoverable original electronic-structure inputs; interpolation is not accepted as convergence evidence.
- **P4 — chemistry decision utility: protocol frozen; outcome not executed.** Case selection/evaluation rules were frozen before viewing P3A outcomes.
- **P5 — second-task transfer: not started.**

## P1 result: common tight ladder

At the primary `1e-3 e` Bader tolerance, after equalizing tight-ladder search opportunity across all 254 development materials, failure to find a numerical pass occurs in **3.3% of eligible** versus **66.4% of QSQ screen-rejected** material–codec pairs, a **20.34x risk ratio**. Secondary results are 10.9% vs 79.3% at `1e-4 e` and 0.0% vs 68.0% at `1e-2 e`.

Source: `analysis/research_upgrade/P1_COMMON_TIGHT_REPORT.md`.

## P2 result: prospective fresh perturbations

The original five-seed QSQ gate was frozen. Each of the 254 development materials then received 59 pre-registered fresh iid-uniform perturbations at its original float32-amplitude scale: **14,986/14,986 valid outcomes; unresolved = 0**.

Primary endpoint (`1e-3 e`):

- QSQ eligible: **143/254 materials (56.3% coverage)**; 135/8,437 fresh trials exceeded threshold = **1.600%**, 95% material-cluster CI **0.782–2.596%**.
- QSQ screen-rejected: **111/254 materials**; 5,326/6,549 fresh trials exceeded threshold = **81.325%**, 95% material-cluster CI **75.981–86.257%**.
- Rejected/eligible risk ratio: **50.83x**.
- Materials with >=1 exceedance: **20/143** eligible vs **110/111** rejected.

Secondary endpoints preserve the same direction: `1e-4 e`, 4.016% vs 86.938% (21.65x); `1e-2 e`, 0.148% vs 79.593% (537.69x).

Interpretation boundary: this prospectively validates **risk stratification under the declared iid-uniform perturbation model** on the development materials. It is not a worst-case stability guarantee, not simultaneous per-material certification, and not new-material generalization.

Source: `analysis/research_upgrade/P2_FRESH_PROBE_REPORT.md` and `validation/qsq_prospective/p2_fresh_probes/execution_manifest.json`.

## Manuscript and Figure 3

P1/P2 evidence has been integrated into `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`. The new central result is no longer the historical 97.2% / 95.5% reclassification headline; it is the combination of **equal-search risk separation (P1)** and **prospective fresh-perturbation discrimination (P2)**.

Figure 3 has been redesigned around these two prospective tests and rendered from the formal R source. GitHub Actions run **34605839019** completed successfully, and formal PNG/PDF/SVG outputs were committed in **f0693a35475f9b2a12af5ce9b1f12a4ef4c8429a**.

## P3A result: implementation transfer

The first P3A run, GitHub Actions **34605557997**, is retained unchanged. It accounted 432/432 conceptual solver cells but blocked 20/24 materials before solver execution because an archive-amplitude provenance comparison used binary-ULP precision against decimal-serialized historical CSV values. Before any retry, all 360 recorded failures were classified and frozen in `analysis/research_upgrade/P3A_FAILURE_TAXONOMY.md`; all 360 shared this single pre-solver error family, with no recorded Bader-solver, atom-mapping, vacuum, grid-shape, or source-download failure.

A predeclared engineering-only retry, GitHub Actions **34608648393**, changed only the archive-compatibility comparison and reliable shell exit-code capture. It did **not** change the 24-system panel, historical five perturbation seeds/amplitudes, solver definitions, density source identity, atom mapping, thresholds, original QSQ gate, P1, or P2. The retry completed **360/360 cells successfully with 0 recorded failures**. The resolved 24-system analysis contains **72/72 complete material–solver five-seed summaries**.

Resolved implementation-transfer results:

- Recreated BaderKit five-seed floors agree with the frozen BaderKit values to a maximum absolute difference of **8.71338e-11 e**.
- **Henkelman on-grid** reproduces the frozen QSQ eligibility classification for **24/24 materials at all three thresholds** (`1e-4`, `1e-3`, `1e-2 e`): **100% agreement, Cohen kappa = 1.000**, with no eligible→rejected or rejected→eligible switches.
- The on-grid floor ordering also transfers strongly: Spearman **rho = 0.995** across 24 materials.
- **Henkelman near-grid** is not equivalent: agreement is **82.6%** at `1e-4 e` (23 comparable, 1 threshold-ambiguous), **83.3%** at `1e-3 e`, and **95.8%** at `1e-2 e`; floor-rank Spearman **rho = 0.754**. The direction of threshold switches is reported explicitly in the resolved table.

Interpretation: the QSQ low-risk/high-risk classification is robust to an independent **on-grid implementation** on this deterministically stratified 24-system panel, while changing the basin-assignment numerical algorithm to the near-grid variant produces a measurable implementation-sensitive boundary. This is a mechanism/implementation-transfer result, not a population-prevalence estimate. P3A does **not** establish electronic-structure grid convergence or a unique physical Bader reference.

Sources: `analysis/research_upgrade/P3A_FAILURE_TAXONOMY.md`, `validation/qsq_prospective/p3a_implementation_transfer_resolved/P3A_IMPLEMENTATION_TRANSFER_RESOLVED_REPORT.md`, and the resolved execution manifest. Resolved aggregate commit: **428272ce397255b34839bfb11d8deb46777067f9**.

## Immediate next actions

1. Integrate the resolved P3A result into the active manuscript and supporting mechanism material without turning implementation transfer into a grid-convergence claim.
2. Audit recoverability of original electronic-structure inputs for the frozen 24-system panel. P3B may proceed only on systems for which genuinely recomputed density grids can be produced under a documented calculation protocol.
3. Freeze a P3B grid-convergence work order before inspecting new grid-convergence outcomes. Report non-recoverable systems rather than silently replacing them.
4. After P3B is scientifically resolved, execute the already outcome-blind P4 chemistry-decision utility protocol.
5. P5 remains optional and should be undertaken only if a second topology-sensitive task can be specified without weakening the central electronic-density story.

## Key provenance

- P1 final report: `analysis/research_upgrade/P1_COMMON_TIGHT_REPORT.md`
- P2 final report: `analysis/research_upgrade/P2_FRESH_PROBE_REPORT.md`
- P2 execution manifest: `validation/qsq_prospective/p2_fresh_probes/execution_manifest.json`
- P3 protocol: `validation/qsq_prospective/P3_NUMERICAL_VALIDATION_PROTOCOL.md`
- P3A first-run report: `validation/qsq_prospective/p3a_implementation_transfer/P3A_IMPLEMENTATION_TRANSFER_REPORT.md`
- P3A failure taxonomy: `analysis/research_upgrade/P3A_FAILURE_TAXONOMY.md`
- P3A resolved report: `validation/qsq_prospective/p3a_implementation_transfer_resolved/P3A_IMPLEMENTATION_TRANSFER_RESOLVED_REPORT.md`
- Current manuscript: `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`
- Figure 3 R source: `figures/R/figure3_certification_landscape.R`
