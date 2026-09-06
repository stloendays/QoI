# JCTC Submission Checklist

**Checked against current JCTC/ACS information on 2026-09-06.**

## A. Scientific package

- [x] Manuscript scientific content conditionally frozen as v0.3.1.
- [x] JCTC-targeted manuscript generated as `submission/JCTC_MANUSCRIPT_v0.1.md`.
- [x] Core headline numbers centralized in `paper_data_v03/HEADLINE_NUMBER_REGISTRY_v03.md`.
- [x] Realized-L∞ matching, complete-case sensitivity, mechanism attenuation, symmetry sensitivity, and global-conservation negative control completed.
- [x] Scientific-freeze lint: 32/32 passed, 0 failed.
- [x] JCTC-targeted lint includes title, abstract, scientific semantics, reference integrity, and citation-resolution checks.
- [ ] Pending optional/final mechanism extension: `mechanism/basin_error_decomposition_per_atom.csv`.
- [ ] If the per-atom table lands before submission, update only Figure 3 / direct-mechanism wording unless the preregistered check materially fails.

## B. JCTC positioning

- [x] Submit as an **Article**.
- [x] Lead with computational electronic-structure methodology, not a compressor bake-off.
- [x] Frame contribution as a stability-qualified fidelity contract for field-dependent chemical analysis.
- [x] Explicitly distinguish prior generic QoI-preserving / topology-preserving compression work.
- [x] Explicitly discuss the 2026 JCTC MARGR electron-density fidelity paper (DOI 10.1021/acs.jctc.6c01124).
- [x] Avoid claims of being first to show that pointwise error does not preserve a QoI.

## C. ACS Fast Format / initial manuscript

Current ACS initial-submission rules allow Fast Format. For the review-ready file:

- [x] Standard original-research sections are clearly identified.
- [ ] Embed all final figures/tables near their first discussion in the manuscript.
- [x] References include titles and complete bibliographic information; exact production typography is not required for initial Fast Format submission.
- [ ] Ensure author names and affiliations in the manuscript exactly match ACS Publishing Center metadata.
- [ ] Remove all internal drafting notes/placeholders from the upload version.
- [ ] Produce final Word or LaTeX/PDF review-ready manuscript.

## D. Files to submit

- [ ] Main manuscript in final ACS-compatible Word or LaTeX/PDF form.
- [ ] Supporting Information as a **separate file**; scaffold now exists at `submission/SUPPORTING_INFORMATION_DRAFT_JCTC_v0.1.md`.
- [ ] Table-of-Contents graphical summary — required by JCTC.
- [ ] Separate high-resolution/vector figure files retained for revision/production and uploaded if requested by the portal.
- [x] Cover-letter draft prepared.
- [x] Data and Software Availability draft prepared.
- [x] Submission metadata worksheet prepared.
- [ ] Funding statement confirmed.
- [ ] Author contribution / CRediT statement completed if requested/used.
- [ ] Competing-interest declaration confirmed.
- [ ] ORCID identifiers collected.

## E. TOC graphic

- [x] JCTC requires a graphical summary for the Table of Contents.
- [x] Working canvas fixed at **3.25 in × 1.75 in**.
- [x] Design brief prepared at `submission/TOC_GRAPHIC_BRIEF_JCTC_v0.1.md`.
- [ ] Create original final artwork.
- [ ] Mark/designate as **For Table of Contents Only** according to the live ACS portal instructions.
- [ ] Check legibility at final size and on a phone without zooming.
- [ ] Confirm accepted file format/resolution in the live submission portal on submission day.

## F. Data and software reproducibility

The 2026 JCTC/JCIM reproducibility policy is now a first-class submission requirement for this project.

- [x] Dedicated Data and Software Availability draft prepared: `submission/DATA_SOFTWARE_AVAILABILITY_JCTC_v0.1.md`.
- [x] Data/code package inventory defined.
- [ ] Decide exact public-release timing before formal submission.
- [ ] Freeze exact submission commit.
- [ ] Create immutable Git release/tag.
- [ ] Deposit the submitted scientific snapshot in Zenodo or equivalent persistent repository.
- [ ] Insert persistent DOI into manuscript and cover-letter/package metadata.
- [ ] Verify archive contains all data/code actually required for the submitted claims.
- [ ] Record manuscript, SI, figure, and TOC-graphic hashes in a submission manifest.

Preferred route:

`submission commit -> immutable release/tag -> persistent archive DOI -> formal ACS submission`

## G. Main manuscript QA before upload

- [x] Title foregrounds chemical fidelity and Bader-domain migration.
- [x] Abstract contains no literature citations and is currently ~209 words.
- [x] Same-nominal comparisons are not interpreted as pure spatial-structure effects.
- [x] Reassignment regression is described as attenuation / mechanism-consistent evidence, not causal mediation.
- [x] Stability floor is described as protocol-defined / probe-defined, not intrinsic.
- [x] `NON_EVALUABLE_BADER_UNSTABLE` is not counted as a codec failure.
- [x] Strictest slab result states that only four slab materials are admitted at 10^-4 e and remains descriptive.
- [ ] All acronyms defined at first occurrence in the formatted version.
- [ ] Every figure cited in numerical order after final figure assembly.
- [ ] Figure axes/units legible at final single/double-column size.
- [ ] Figure 3 wording matches the final available mechanism data.
- [ ] Final Data and Software Availability section contains active archive DOI rather than a future-release statement.

## H. Reference QA

- [x] ZFP primary method reference verified.
- [x] SZ3 primary method reference verified: DOI 10.1109/TBDATA.2022.3201176.
- [x] SPERR primary method reference verified: DOI 10.1109/IPDPS54959.2023.00104.
- [x] Recent JCTC MARGR reference verified: DOI 10.1021/acs.jctc.6c01124.
- [x] MARGR assigned a unique reference number after the existing Brehm & Thomas reference.
- [x] Automated lint checks bibliography numbering uniqueness/continuity and that numerical citations resolve.
- [ ] Verify every DOI against final published records before upload.
- [ ] Ensure year/volume/page/article information is final for 2026 in-press/accepted papers.
- [ ] Final ACS/JCTC production styling can be deferred until revision/acceptance if Fast Format is used.

## I. Cover letter

- [x] JCTC-specific scientific pitch prepared.
- [x] Public-release wording corrected so the letter does not claim the currently private repository is already released.
- [ ] Insert final corresponding-author name, affiliation, postal address, and email.
- [ ] Confirm all authors have approved submission.
- [ ] Confirm manuscript is not under consideration elsewhere.
- [ ] Confirm related manuscripts/preprints are disclosed if applicable.
- [ ] Confirm competing-interest statement.

## J. Administrative metadata

Worksheet: `submission/JCTC_SUBMISSION_METADATA_v0.1.md`.

- [ ] final author order
- [ ] affiliations
- [ ] corresponding author
- [ ] ORCIDs
- [ ] funding/grant numbers
- [ ] CRediT roles
- [ ] conflict statement
- [ ] preprint/related-work disclosure
- [ ] suggested reviewers after conflict screening
- [ ] reviewer exclusions only if justified

## K. Current JCTC/ACS procedural checks

- [x] Submission route: ACS Publishing Center.
- [x] JCTC requires a graphical summary for the Table of Contents.
- [x] ACS initial submission supports Fast Format.
- [x] Figures should be embedded in the manuscript when possible.
- [x] Supporting Information is submitted separately.
- [x] References may use any complete style at initial submission but must include titles.
- [x] Author names/affiliations must match ACS Publishing Center metadata.
- [x] 2026 JCTC/JCIM policy calls for Data and Software Availability and submission-time reproducibility materials whenever possible.
- [ ] Re-check live JCTC Author Guidelines and ACS Publishing Center immediately before formal upload.

## L. Final go/no-go

**GO for JCTC manuscript/SI/figure/TOC preparation now.**

The temporarily unavailable per-atom table is not a blocker for preparing or even scientifically supporting the current manuscript because the direct decomposition claim is explicitly restricted to the representative 12-material mechanism set. It becomes a submission blocker only if the final manuscript or Figure 3 is rewritten to make a claim that requires the missing atom-level table.

**Current true blockers to clicking Submit:**

1. final author/affiliation/funding/conflict metadata;
2. final TOC graphic;
3. assembled review-ready SI;
4. final manuscript file with embedded figures;
5. immutable public/persistent data-software archive and DOI;
6. final reference/figure/submission-day QA.
