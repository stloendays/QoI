# QSQ research upgrade — current status

Last synchronized: **2026-09-11 21:50 Asia/Singapore**.

This file is the concise status record for the active research-strengthening phase. Historical benchmark/protocol outputs remain frozen; all prospective work is additive.

## Overall

- **P0 — claim correction / target definition: COMPLETE.** The active manuscript distinguishes fixed-pipeline numerical fidelity from reference robustness and no longer treats the historical >95% full-record number as a design-independent causal misattribution rate.
- **P1 — equal search opportunity: COMPLETE.** 1,332/1,332 additive common-tight-ladder reconstructions were accounted successfully; no final failures remain.
- **P2 — prospective fresh-perturbation validation: COMPLETE.** 14,986/14,986 pre-registered fresh perturbation trials succeeded with the original five-seed QSQ gate unchanged.
- **P3A — implementation transfer: COMPLETE_WITH_RECORDED_FAILURES.** 432/432 planned solver cells are accounted, but only 72 succeeded and 360 are explicitly failed/unresolved. The current result is therefore a partial implementation-transfer diagnostic, not a passed 24-system validation.
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

## P3A result and current blocker

GitHub Actions run **34605557997** completed with an overall failure conclusion because the workflow intentionally surfaced recorded P3A failures. The aggregate itself was produced and committed in **99f5adcaf08f7556b5d05fdb16f75b465592f52b**.

Accounting:

- planned solver evaluations: **432/432 accounted**;
- successful rows: **72**;
- failed rows: **360**;
- 24-system panel, but only **4 materials** currently have complete five-seed results across the implementation comparison.

Complete-case signal:

- recreated BaderKit floor matches the frozen BaderKit floor to maximum absolute difference **1.54445e-11 e**;
- Henkelman on-grid classification agrees **100%** with frozen BaderKit on the four complete materials at `1e-4`, `1e-3`, and `1e-2 e` (Cohen kappa 1.0); floor-rank Spearman rho = 1.0;
- Henkelman near-grid is less stable across the same four complete materials (agreement 50% / 75% / 75%; floor-rank rho 0.4), defining an implementation-sensitive boundary rather than a universal reference.

However, **20/24 materials are unresolved**, so the complete-case agreement cannot be generalized to the full panel.

One inspected failed shard shows a concrete engineering/provenance gate issue: the source-derived float32 amplitude differed from the stored historical CSV decimal only at rounding-scale precision (example `0.00012195625004096655` vs stored `0.0001219562500409`), while the hard check used an approximately `5.42e-20` tolerance. This is not itself evidence of a Bader scientific failure. The remaining failures must be classified before any rerun; only provenance/engineering checks may be repaired, while the frozen scientific panel, perturbations, solver definitions, and thresholds must remain unchanged.

Source: `validation/qsq_prospective/p3a_implementation_transfer/P3A_IMPLEMENTATION_TRANSFER_REPORT.md` and execution manifest.

## Immediate next actions

1. Audit all 360 P3A failure rows by stage/error signature and determine how many are precision-gate/infrastructure failures versus genuine solver/source failures.
2. If the amplitude-text precision issue is systematic, replace only that provenance equality check with a predeclared numerically appropriate tolerance tied to serialized precision; retain the original failed run as provenance, then rerun only unresolved cells with unchanged science.
3. Recompute the 24-system P3A classification-transfer table only after full accounting; do not headline the current four-material complete-case statistics.
4. Execute P3B only where genuinely recomputed grids can be recovered/generated.
5. After P3 is scientifically closed, proceed to the already outcome-blind P4 chemistry-decision utility test.

## Key provenance

- P1 final report: `analysis/research_upgrade/P1_COMMON_TIGHT_REPORT.md`
- P2 final report: `analysis/research_upgrade/P2_FRESH_PROBE_REPORT.md`
- P2 execution manifest: `validation/qsq_prospective/p2_fresh_probes/execution_manifest.json`
- P3 protocol: `validation/qsq_prospective/P3_NUMERICAL_VALIDATION_PROTOCOL.md`
- P3A report: `validation/qsq_prospective/p3a_implementation_transfer/P3A_IMPLEMENTATION_TRANSFER_REPORT.md`
- Current manuscript: `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`
- Figure 3 R source: `figures/R/figure3_certification_landscape.R`
