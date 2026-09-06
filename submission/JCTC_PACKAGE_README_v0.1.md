# JCTC Submission Package v0.2.1

Branch: `submission/jctc-v0.1`  
Scientific source: frozen benchmark/statistical evidence from the v0.3.1 analysis line.

## Primary manuscript

**Current working manuscript:** `JCTC_MANUSCRIPT_v0.2.1.md`

The v0.2.1 manuscript uses the seven-part scientific narrative agreed for the JCTC submission:

1. Introduction
2. Scientific question and benchmark design
3. Codec error structure
4. QoI / Chemical fidelity
5. Mechanism: why L∞ fails
6. Robustness, failure regimes, and implications
7. Conclusion

Version v0.2.1 retains the v0.2 scientific narrative and strengthens bibliographic/provenance closure. The previous v0.2 and v0.1 manuscripts are retained as editorial snapshots.

Writing conventions are defined in `WRITING_README.md`. The main rule is to write forward from scientific question to evidence, mechanism, and implication rather than organizing the manuscript around anticipated objections.

## Current integrity status

- **v0.2.1 reference/provenance lint:** 24/24 passed, 0 failed.
- **v0.2 structure/writing lint:** 46/46 passed, 0 failed.
- **Supporting Information lint:** 34/34 passed, 0 failed.
- Reference numbering is unique and contiguous (1–19), all numerical citations resolve, and no duplicate DOI entries are present.
- BaderKit, Materials Project, AFLOW, and NOMAD now have explicit bibliography entries tied to their use in the benchmark/methodology text.

## Primary files

- `JCTC_MANUSCRIPT_v0.2.1.md` — current JCTC manuscript; seven-section narrative plus updated reference/provenance closure.
- `JCTC_MANUSCRIPT_v0.2.1_LINT.md` — automated section, citation, DOI, and reference-number integrity checks.
- `JCTC_MANUSCRIPT_v0.2.md` — previous seven-section manuscript retained as an editorial snapshot.
- `WRITING_README.md` — manuscript voice, evidence hierarchy, terminology, and non-defensive writing rules.
- `JCTC_MANUSCRIPT_v0.2_LINT.md` — v0.2 structure/language/headline-number checks.
- `SUPPORTING_INFORMATION_TEXT_JCTC_v0.1.md` — populated SI text containing robustness, probe validation, matching, mechanism, negative-control, and certified-frontier results.
- `JCTC_SI_LINT_v0.1.md` — automated SI number/semantics/scope checks.
- `COVER_LETTER_JCTC_v0.1.md` — JCTC cover-letter draft.
- `TOC_GRAPHIC_BRIEF_JCTC_v0.1.md` — design brief for the graphical summary.
- `JCTC_FIGURE_ASSEMBLY_PLAN_v0.1.md` — six-figure production map and data-source lock.
- `DATA_SOFTWARE_AVAILABILITY_JCTC_v0.1.md` — reproducibility-policy draft and archival plan.
- `REFERENCE_AUDIT_JCTC_v0.1.md` — reference audit record; update again immediately before formal submission for 2026 accepted/in-press work.
- `JCTC_SUBMISSION_METADATA_v0.1.md` — ACS Publishing Center metadata worksheet.
- `JCTC_SUBMISSION_CHECKLIST_v0.1.md` — scientific, administrative, figure, reference, reproducibility, and submission-day checklist.
- `JCTC_REQUIREMENTS_SNAPSHOT_20260906.md` — dated snapshot of the JCTC/ACS requirements used for preparation.
- `SUBMISSION_MANIFEST_TEMPLATE_v0.1.md` — template for exact submitted commit, archive DOI, file names, and hashes.

## Reference improvements in v0.2.1

- BaderKit is cited directly because the benchmark uses `baderkit` 0.10.2.
- Materials Project, AFLOW, and NOMAD are cited at first mention in the benchmark provenance section.
- The PVLDB QoI-compression record is normalized to its published 2022 volume/issue record.
- Issue information is added where verified for TopoSZ, discrete Morse–Smale preservation, and Brehm–Thomas.
- TOPIQ and FZ-VIS remain cited as accepted 2026 work plus their arXiv records until final proceedings/TVCG bibliographic metadata are public; these entries must be checked again on submission day.

## JCTC pitch

### One sentence

A pointwise error guarantee is not a sufficient chemical-fidelity contract for compressed electron densities when the downstream Bader integration domains are re-derived from the reconstructed field.

### Three-sentence editor pitch

We develop a stability-qualified methodology for validating lossy-compressed DFT electron densities against Bader charge analysis. Across 6,343 successful reconstructions, the study separates requested tolerance from realized field perturbation, re-derives the Bader partition to expose domain migration, and qualifies the numerical resolution of the reference Bader observable before certification. The resulting framework connects electronic-structure data representation to a downstream chemical accuracy contract and identifies local domain migration as the mechanism missing from pointwise error control.

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

## Current mechanism-data status

The manuscript already supports the direct mechanism argument with the representative 12-material decomposition and the full-benchmark reassignment analysis. If the full per-atom mechanism table becomes available before submission, it can refine Figure 3 and the atom-level summary using the preregistered material-level analysis plan. The frozen Protocol A.1, master benchmark, realized-L∞ matching, and complete-case estimands remain unchanged.

## Remaining production tasks

1. finalize author order, affiliations, corresponding author, ORCIDs, funding, CRediT, and disclosures;
2. produce the final original TOC graphic;
3. convert the populated SI text into a review-ready formatted SI with final supplementary figures/tables;
4. place the final Figures 1–6 into the ACS Fast Format manuscript near first discussion;
5. freeze an immutable data/software release with a persistent DOI and exact submission commit/tag;
6. run submission-day reference, figure, metadata, and file-integrity QA.
