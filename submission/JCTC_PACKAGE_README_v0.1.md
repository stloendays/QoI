# JCTC Submission Package v0.1

Branch: `submission/jctc-v0.1`  
Scientific source: `paper/MANUSCRIPT_CHATGPT_v0.3.1.md` from the conditionally frozen analysis branch.

## Primary files

- `JCTC_MANUSCRIPT_v0.1.md` — JCTC-targeted full manuscript generated from the scientific freeze.
- `JCTC_MANUSCRIPT_LINT_v0.1.md` — automated journal-targeted scientific/editorial/reference checks.
- `COVER_LETTER_JCTC_v0.1.md` — cover-letter draft; author details and declarations remain to be confirmed.
- `TOC_GRAPHIC_BRIEF_JCTC_v0.1.md` — design brief for the required graphical summary.
- `SUPPORTING_INFORMATION_DRAFT_JCTC_v0.1.md` — review-ready SI assembly scaffold, including all robustness and mechanism sections.
- `DATA_SOFTWARE_AVAILABILITY_JCTC_v0.1.md` — JCTC/JCIM 2026 reproducibility-policy draft and archive plan.
- `JCTC_SUBMISSION_METADATA_v0.1.md` — ACS Publishing Center metadata worksheet for authors, affiliations, ORCIDs, funding, conflicts, and disclosures.
- `JCTC_SUBMISSION_CHECKLIST_v0.1.md` — scientific, administrative, figure, reference, reproducibility, and submission-day checklist.
- `JCTC_REQUIREMENTS_SNAPSHOT_20260906.md` — dated snapshot of the current JCTC/ACS author requirements used to prepare this package.
- `SUBMISSION_MANIFEST_TEMPLATE_v0.1.md` — template for the exact submitted commit, DOI, file names, and cryptographic hashes.

## JCTC pitch

### One sentence

A pointwise error guarantee is not a sufficient chemical-fidelity contract for compressed electron densities when the downstream Bader integration domains are themselves re-derived from the reconstructed field.

### Three-sentence editor pitch

We develop a stability-qualified methodology for validating lossy-compressed DFT electron densities against Bader charge analysis. Across 6,343 successful reconstructions, we separate requested tolerance from realized field perturbation, show that fixed-basin scoring suppresses a major field-derived-domain error channel, and require the Bader observable itself to be numerically resolvable before certification. The resulting framework connects electronic-structure data representation to a defensible downstream chemical accuracy contract rather than proposing a new compressor.

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

## Current scientific dependency

The full per-atom mechanism file has not yet landed on `main`. This does not block the current JCTC manuscript, cover letter, TOC design, SI assembly, or formatting because the direct algebraic mechanism claim remains explicitly scoped to the representative 12-material mechanism set.

If the file becomes available before submission, it should update only Figure 3 and the direct-mechanism section under the preregistered material-level analysis plan. It should not automatically reopen Protocol A.1, the master benchmark, the realized-\(L_\infty\) analysis, or the overall story.

## Current true submission blockers

1. final author order, affiliations, corresponding author, ORCIDs, funding, and conflict/disclosure information;
2. final original TOC graphic;
3. assembled review-ready Supporting Information file;
4. final manuscript format with figures embedded near first discussion;
5. immutable archived data/software release with a persistent DOI;
6. submission-day reference, figure, and metadata QA.

The unavailable per-atom file is not itself a blocker unless the final paper is broadened to make an atom-level claim that requires it.
