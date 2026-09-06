# JCTC Submission Checklist

**Checked against current JCTC/ACS information on 2026-09-06.**

## A. Scientific package

- [x] Manuscript scientific content conditionally frozen as v0.3.1.
- [x] Core headline numbers centralized in `paper_data_v03/HEADLINE_NUMBER_REGISTRY_v03.md`.
- [x] Realized-L∞ matching, complete-case sensitivity, mechanism attenuation, symmetry sensitivity, and global-conservation negative control completed.
- [x] Scientific-claim lint: 32/32 passed, 0 failed.
- [ ] Pending per-atom mechanism table: `mechanism/basin_error_decomposition_per_atom.csv`.
- [ ] After the per-atom table lands, update only Figure 3 / direct-mechanism wording unless a preregistered check materially fails.

## B. JCTC positioning

- [x] Submit as an **Article**.
- [x] Lead with computational electronic-structure methodology, not a compressor bake-off.
- [x] Frame contribution as a stability-qualified fidelity contract for field-dependent chemical analysis.
- [x] Explicitly distinguish prior generic QoI-preserving / topology-preserving compression work.
- [x] Explicitly discuss the 2026 JCTC MARGR electron-density fidelity paper (DOI 10.1021/acs.jctc.6c01124).
- [x] Avoid claims of being first to show that pointwise error does not preserve a QoI.

## C. Files to submit

- [ ] Main manuscript in final ACS-compatible Word or LaTeX/PDF form.
- [ ] Supporting Information PDF with S1–S13 structure and all final supplementary captions/tables.
- [ ] Table-of-Contents graphical summary — required by JCTC.
- [ ] Separate high-resolution/vector figure files as requested by the submission system.
- [ ] Cover letter.
- [ ] Data/code availability statement checked against repository visibility and release plan.
- [ ] Funding statement.
- [ ] Author contribution / CRediT statement if requested in the submission workflow.
- [ ] Competing interests / conflict-of-interest declaration.
- [ ] ORCID identifiers for authors where available.

## D. Current JCTC/ACS procedural checks

- [x] Submission route: ACS Publishing Center.
- [x] JCTC currently requires a graphical summary for the Table of Contents.
- [x] Current peer-review model is single-anonymous; ACS also offers an optional transparent peer-review pathway.
- [x] If preparing the manuscript in Word, use U.S. Letter as the original page size per the current ACS author-information page.
- [ ] Re-check the live JCTC Author Guidelines on the actual submission day for file-format, TOC dimensions, and any changed metadata requirements.

## E. Main manuscript QA before upload

- [ ] Title contains no unnecessary jargon and foregrounds chemical fidelity / Bader-domain migration.
- [ ] Abstract contains no reference citations and reports quantitative results consistently with the frozen registry.
- [ ] All acronyms are defined at first occurrence.
- [ ] Every figure is cited in numerical order.
- [ ] Figure axes/units remain legible at final size.
- [ ] Figure 3 wording matches the final per-atom audit.
- [ ] Strictest slab result explicitly remains descriptive because only four slab materials are admitted at 10^-4 e.
- [ ] `NON_EVALUABLE_BADER_UNSTABLE` is never counted as codec failure.
- [ ] Stability floor is always described as protocol-defined / probe-defined, not intrinsic.
- [ ] Reassignment regression is described as attenuation / mechanism-consistent evidence, not causal mediation.
- [ ] Same-nominal comparisons are never interpreted as pure spatial-structure effects.

## F. Reference QA

- [x] ZFP primary method reference verified.
- [x] SZ3 primary method reference verified: DOI 10.1109/TBDATA.2022.3201176.
- [x] SPERR primary method reference verified: DOI 10.1109/IPDPS54959.2023.00104.
- [x] Recent JCTC MARGR reference verified: DOI 10.1021/acs.jctc.6c01124.
- [ ] Convert final bibliography to the JCTC/ACS numerical reference style used by the submission manuscript.
- [ ] Verify every DOI programmatically or manually before submission.
- [ ] Ensure cited titles and year/volume/page or article information match the final published records.

## G. Cover-letter checks

- [ ] Insert final corresponding-author name, affiliation, postal address, and email.
- [ ] Confirm all authors have approved submission.
- [ ] Confirm manuscript is not under consideration elsewhere.
- [ ] Confirm any related manuscripts/preprints are disclosed if applicable.
- [ ] Keep the pitch focused on electronic-structure methodology and field-derived chemical domains.

## H. Repository / reproducibility

- [x] Frozen `main` remains distinct from editorial/statistical submission branches.
- [x] JCTC submission work is isolated on `submission/jctc-v0.1`.
- [ ] Decide whether the repository will be public at submission, at acceptance, or linked through an archival release/DOI.
- [ ] Create an immutable release/tag for the exact submitted data/code state.
- [ ] Record submitted manuscript hash and figure hashes in a submission manifest.

## I. Final go/no-go

**GO for JCTC formatting and submission preparation now.**

The temporarily unavailable per-atom table is not a blocker for JCTC-specific writing, cover-letter preparation, TOC design, bibliography cleanup, SI assembly, or figure polishing. It is a blocker only for freezing the final Figure 3 atom-level mechanism panel and any wording that explicitly depends on that table.
