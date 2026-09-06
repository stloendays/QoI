# JCTC Submission Package v0.1

Branch: `submission/jctc-v0.1`  
Scientific source: `paper/MANUSCRIPT_CHATGPT_v0.3.1.md` from the conditionally frozen analysis branch.

## Primary files

- `JCTC_MANUSCRIPT_v0.1.md` — JCTC-targeted full manuscript, generated from the scientific freeze.
- `COVER_LETTER_JCTC_v0.1.md` — cover-letter draft addressed to the current JCTC Editor-in-Chief; author details and standard declarations remain to be confirmed.
- `TOC_GRAPHIC_BRIEF_JCTC_v0.1.md` — design brief for the required graphical summary.
- `JCTC_SUBMISSION_CHECKLIST_v0.1.md` — scientific, administrative, figure, reference, and reproducibility checklist.
- `JCTC_MANUSCRIPT_LINT_v0.1.md` — automated journal-targeted scientific/editorial checks.

## JCTC pitch

### One sentence

A pointwise error guarantee is not a sufficient chemical-fidelity contract for compressed electron densities when the downstream Bader integration domains are themselves re-derived from the reconstructed field.

### Three-sentence editor pitch

We develop a stability-qualified methodology for validating lossy-compressed DFT electron densities against Bader charge analysis. Across 6,343 successful reconstructions, we separate requested tolerance from realized field perturbation, show that fixed-basin scoring suppresses the dominant field-derived-domain error channel, and require the Bader observable itself to be numerically resolvable before certification. The resulting framework connects electronic-structure data representation to a defensible downstream chemical accuracy contract rather than proposing a new compressor.

## Suggested manuscript type

**Article**

## Suggested keywords

- electron density
- density functional theory
- Bader charge
- lossy compression
- error-bounded compression
- numerical stability
- quantity of interest
- real-space analysis
- scientific data
- computational methodology

## Current scientific blocker

The full per-atom mechanism file has not yet landed on `main`. This does not block the JCTC manuscript, cover letter, TOC design, SI assembly, or formatting. Until the file is available, the direct algebraic mechanism claim remains explicitly scoped to the representative 12-material mechanism set.
