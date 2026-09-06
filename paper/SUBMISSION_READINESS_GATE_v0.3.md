# Submission readiness gate — QoI manuscript v0.3

Date: 2026-09-06

This document defines what must be complete before submission and, equally importantly, what should **not** trigger further open-ended computation.

## Current scientific status

**Core evaluation claim: READY.**

- 6,343 successful reconstructions / 254 development materials.
- 4,627-row base-ladder fixed-versus-re-derived analysis.
- Re-derived Bader error exceeds fixed-basin error in 99.7% of successful base rows.
- Nominal error-budget utilization is measured explicitly; ZFP median utilization 0.1575 versus ~1 for SZ3/SPERR.
- A.1-qualified realized-L∞ matching retains an approximately twofold codec-associated residual.
- Matching-window, common-support interpolation and conservative complete-case sensitivity all retain the result.

**QoI resolvability claim: READY.**

- Protocol A.1 is frozen and fully recomputed over 319 systems.
- Non-evaluable fractions are fixed at 79.9%, 41.4% and 9.7% for 1e-4, 1e-3 and 1e-2 e contracts.
- Probe seed and amplitude sensitivities are documented.
- The archived float32 probe failure mode is documented rather than erased.
- Known symmetry-equivalent basin relabeling has an explicit sensitivity and does not drive the headline.

**Mechanism claim: READY at representative-set scope; pending final per-atom audit for presentation.**

- Direct 12-material decomposition: median bounded domain dominance 0.995; 84.9% >0.90; machine-precision closure.
- Full-table reassignment attenuation: codec multipliers ~2x -> ~1 after adding reassignment.
- Global electron-count deviation negative control does not reproduce the attenuation; with both covariates, electron-count deviation is non-significant while reassignment remains strongly associated with Bader error.
- The claim must remain scoped to direct dominance in the representative mechanism set plus full-benchmark mechanism-consistent attenuation.

**Engineering/utility claim: READY.**

- Certified compression–coverage frontier is quantified by domain and Bader contract.
- Codec ordering changes with the scientific contract.
- Strictest slab result is explicitly marked descriptive because only four materials are admitted.

## Hard requirements before submission

### Gate 1 — Per-atom mechanism file lands and passes the preregistered audit

Required file: `mechanism/basin_error_decomposition_per_atom.csv`.

Required checks:
- exact/near-machine closure of `dq_total = dq_integrand + dq_domain` for every atom;
- no atom-level pseudoreplication in uncertainty estimates;
- case-level and material-level summaries of bounded domain dominance;
- leave-one-material-out sensitivity;
- check whether maximum-error atoms are atypical relative to the rest of each material.

**Pass condition:** no systematic closure error and no qualitative reversal of the representative-set domain-dominance interpretation under case/material aggregation.

If this gate fails, revise the mechanism wording; do not alter frozen benchmark/protocol outcomes.

### Gate 2 — Bibliography is converted from provisional Markdown numbering to verified BibTeX/citation-manager entries

Core verified method references:
- ZFP: DOI 10.1137/18M1168832.
- SZ3: DOI 10.1109/TBDATA.2022.3201176.
- SPERR: DOI 10.1109/IPDPS54959.2023.00104.

All 2026 topology/QoI references must be checked against final venue metadata immediately before submission.

### Gate 3 — Main figures are visually publication-ready

Scientific/statistical content for Figures 2, 4, 5 and 6 is frozen in `figures_v03/` and `paper_data_v03/`.

Still needed:
- Figure 1 conceptual schematic;
- Figure 3 final spatial/mechanism illustration after per-atom file is available;
- typography, panel labels, axis units and journal sizing across all figures;
- color-blind-safe final palette and grayscale legibility;
- remove draft wording from filenames/captions for submission.

### Gate 4 — Manuscript numeric/citation QA

Before submission:
- every headline number must map to `paper_data_v03/HEADLINE_NUMBER_REGISTRY_v03.md` or a named stratified analysis table;
- every percentage must name or imply the correct denominator;
- primary A.1 result must be distinguished from complete-case reviewer sensitivity;
- `NON_EVALUABLE` must never be counted as codec failure;
- no “causal codec effect,” “intrinsic Bader floor,” “universally best codec,” or “first QoI-aware compression” wording;
- all placeholder references removed.

## Optional extensions — only if they fit the chosen venue

### One topology/local-order-aware compressor

Potential value: directly test whether a guarantee closer to the discovered Bader failure mode reduces basin migration.

Do this only if:
- a mature implementation can ingest the released volumetric fields without redesigning the study;
- the target venue is compression-algorithm-centric and reviewers are likely to demand a topology-aware comparator;
- it can be presented as a supplementary validation without changing Protocol A.1 or the primary general-purpose-codec benchmark.

Do **not** delay the paper solely to build a new compressor.

### Additional QoIs

Potential value: generality beyond Bader charge.

Do this only as a new study or clearly separated extension. The current paper is scientifically coherent with one demanding field-derived-domain QoI. Adding a weakly motivated second QoI late could dilute the mechanism story.

### More Protocol-A.1 seeds

Not required for the primary operational protocol. A small seed-saturation experiment could be useful only if a target reviewer explicitly expects empirical convergence of the maximum; do not replace the frozen five-seed primary results.

## Explicit stop rules

The following observations do **not** justify reopening the frozen protocol or full benchmark:

- a different seed produces a different individual stability floor;
- a topology-aware codec performs better than one general-purpose codec;
- a new descriptive material subgroup appears interesting;
- a reviewer-preferred average charge metric gives a friendlier result;
- the per-atom file reveals heterogeneity among atoms while the preregistered case/material summaries remain directionally consistent;
- a new codec or QoI is published while the paper is being prepared.

## Submission-ready definition

The manuscript is **scientifically submission-ready** when:

1. per-atom mechanism audit passes or the mechanism claim is transparently narrowed;
2. all references are verified and placeholder-free;
3. Figures 1–6 are publication-ready;
4. numerical QA passes against the headline registry;
5. target-venue formatting is applied.

No additional full benchmark run is currently required.
