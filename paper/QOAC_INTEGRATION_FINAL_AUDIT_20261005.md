# QOAC-H manuscript-integration final audit — 2026-10-05

Status: **scientific-story and canonical-source integration complete; final DOCX/PDF release QA remains.**

## Canonical branch

`paper/qoac-integration-20261005`

Active reader-facing title:

> **Numerical stability qualification and operator-aware compression of electronic densities**

## Scientific story

The active manuscript now uses the evidence chain:

`measurement-contract qualification -> matched-distortion diagnosis -> exact Hartree operator -> operator-derived error allocation -> QOAC-H -> decoded-field certification`.

QSQ remains logically prior to codec scoring. QOAC-H is a Hartree-specific diagnosis-to-design demonstration and does not transfer the $|G|^2$ law to Bader.

## Frozen QOAC-H evidence integrated into main text

- Operator-derived allocation: $\Delta_G\propto|G|^2$ from Hartree squared-error weighting $|G|^{-4}$.
- Frozen operator-blind ablation: 12/12 materials favor the operator-derived allocation; median Hartree-error ratio = **0.0767117**.
- Disjoint confirmatory cohort: **48/48 wins**, median certified CR ratio **15.016×**, bootstrap 95% CI **11.204–21.461**, bulk median **11.203×**, slab median **25.699×**, Nyquist-safe guardrail **48/48**.
- Full development-population census: **254 materials, 6,350/6,350 settings, 0 failures**.
- At $10^{-6}$ Hartree relative RMSE: **253/253 comparable wins**, median **12.463×**, P05 **4.459×**, minimum **2.444×**, bulk median **10.960×**, slab median **27.733×**.
- The direction remains favorable in every comparable material across the six frozen Hartree tolerances from $10^{-8}$ through $10^{-3}$.

## Prior-art boundary

The governing record is `paper/QOAC_PRIOR_ART_NOVELTY_AUDIT_20261005.md`.

Do not claim novelty for:
- QoI-aware compression in general;
- operator-aware compression in general;
- transform-domain bit allocation in general;
- electronic-structure compression in general.

The supported contribution is the **QSQ-qualified diagnosis-to-design loop** in which the exact downstream Hartree operator first explains codec-dependent error structure, then defines the compression distortion geometry, followed by direct downstream recertification of the decoded density.

## Main-text architecture

- Reader-facing main figures are continuous **Fig. 1–9**.
- **Fig. 8** is the new QOAC-H diagnosis-to-design figure.
- The historical external-confirmation render is reader-facing **Fig. 9** while retaining its internal provenance filename.
- Figure 8 source: `figures/R/figure8_qoac_h.R`.
- Figure 8 outputs: `figures/R/rendered/figure8_qoac_h_R.{png,pdf,svg}`.
- Successful render workflow: run **37280087154**; artifact **11331394795**.
- Visual QA: all four panels, global title/subtitle and caption are visible without clipping; denominator labels and primary contract remain legible.

## Canonical-source QA

Reader-facing files checked:
- `paper/MANUSCRIPT.md`;
- `paper/SUPPLEMENTARY_INFORMATION.md`;
- `paper/FIGURE_CAPTIONS.md`;
- `paper/CURRENT_PAPER_STORY.md`;
- Nature-style and ACS-style reference renderings.

Checks:
- title consistent between main text and SI;
- no reader-facing QOAC-H internal development labels;
- main figure captions continuous from 1 through 9;
- current bibliography contains **28 continuous references**;
- QOAC-H headline numbers agree among main text, SI, caption and frozen result tables;
- all standalone display math delimiters are `$$`;
- main abstract reduced to **213 words** without narrowing the scientific claims.

## Deterministic proof gates

Main-text proof:
- hardened workflow verifies canonical manuscript, captions, Fig. 1–9 inputs and absence of standalone single-dollar display delimiters;
- latest successful main proof-input package: workflow run **37281930474**, artifact **11332149113**;
- `junbo-scientific-writing/scripts/audit_manuscript.py --final` executed on the actual packaged `MANUSCRIPT.md`: **0 blockers, 0 warnings**.

Supplementary proof:
- hardened workflow verifies SI, tables, S1–S10 captions/assets and display delimiters;
- successful SI proof-input package: workflow run **37281731394**, artifact **11331923389**;
- the same final manuscript audit executed on the packaged `SUPPLEMENTARY_INFORMATION.md`: **0 blockers, 0 warnings**.

## Export mapping

The manuscript builders now expect **nine** main figures.

Reader-facing mapping:
- Figs. 1–7: existing locked composite renders;
- Fig. 8: `figures/R/rendered/figure8_qoac_h_R.png`;
- Fig. 9: `figures/R/rendered/figure8_external_confirmation_R.png`.

`figures/composite/make_sheet.py` accepts both Matplotlib double-quoted SVG attributes and R/svglite single-quoted attributes.

## Remaining release-stage work

These are not unresolved scientific claims:

1. generate the final submission DOCX from the current canonical Markdown;
2. render every DOCX page and inspect equations, page breaks, figure placement and bibliography;
3. export PDF from the audited DOCX and run PDF preflight;
4. insert final author/affiliation/corresponding-author metadata only from the author's verified record;
5. create and insert the archival release/DOI when the submission snapshot is frozen;
6. apply the selected journal's final reference and formatting style.

No additional scientific endpoint or primary cohort is required for the current QSQ/QOAC-H story.
