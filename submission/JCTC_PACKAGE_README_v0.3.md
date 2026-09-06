# JCTC Submission Package v0.3

**Branch:** `submission/jctc-v0.1`  
**Current manuscript:** `JCTC_MANUSCRIPT_v0.2.3.md`

## Scientific narrative

1. Introduction
2. Scientific question and benchmark design
3. Codec error structure
4. QoI / Chemical fidelity
5. Mechanism: why L∞ fails
6. Robustness, failure regimes, and implications
7. Conclusion

The manuscript uses a forward scientific narrative: question -> evidence -> mechanism -> implication. There is no standalone Limitations section.

## Current integrity status

- **Main manuscript v0.2.3 lint:** 30/30 passed.
- **Supporting Information v0.2 lint:** 25/25 passed.
- **Manuscript–caption–SI cross-document lint:** 48/48 passed.
- References are numbered 1–20, numerical citations resolve, and DOI entries are unique.
- Main figures are cited in numerical order 1 -> 2 -> 3 -> 4 -> 5 -> 6.
- Shared headline numbers agree across manuscript, captions, and SI.

## Primary files

- `JCTC_MANUSCRIPT_v0.2.3.md` — current main manuscript.
- `JCTC_MANUSCRIPT_v0.2.3_LINT.md` — main-manuscript structure/reference/figure-order audit.
- `SUPPORTING_INFORMATION_TEXT_JCTC_v0.2.md` — clean SI scientific text, S1–S12 plus self-contained references.
- `JCTC_SI_v0.2_LINT.md` — SI scope/number/reference audit.
- `JCTC_FIGURE_CAPTIONS_v0.3.md` — publication-style main Figure 1–6 captions.
- `JCTC_FIGURE_ASSEMBLY_PLAN_v0.2.md` — production map using new narrative-order figure numbering.
- `JCTC_CROSSDOC_LINT_v0.2.md` — manuscript/caption/SI consistency audit.
- `REFERENCE_AUDIT_JCTC_v0.3.md` — current bibliography audit and submission-day 2026 update list.
- `WRITING_README.md` — manuscript voice and evidence hierarchy.
- `COVER_LETTER_JCTC_v0.1.md` — cover-letter draft.
- `TOC_GRAPHIC_BRIEF_JCTC_v0.1.md` — TOC graphic design brief.
- `DATA_SOFTWARE_AVAILABILITY_JCTC_v0.1.md` — reproducibility/archive plan.
- `JCTC_SUBMISSION_METADATA_v0.1.md` — author/affiliation/ORCID/funding/CRediT worksheet.
- `JCTC_SUBMISSION_CHECKLIST_v0.1.md` — submission checklist.
- `SUBMISSION_MANIFEST_TEMPLATE_v0.1.md` — final commit/archive/hash manifest template.

## Figure numbering after narrative reorganization

| Submission figure | Scientific role | Historical draft source |
|---|---|---|
| Figure 1 | evaluation contract schematic | new artwork |
| Figure 2 | bound utilization + matched realized-L∞ residual | old Figure 5 |
| Figure 3 | fixed-basin vs re-derived chemical fidelity | old Figure 2 |
| Figure 4 | QoI resolvability + probe validation | old Figure 4 |
| Figure 5 | basin-migration mechanism | old Figure 3 |
| Figure 6 | certified compression–coverage frontier | old Figure 6 |

Historical filenames are retained for provenance only; final exports should use the submission numbering above.

## Literature-positioning additions in current manuscript

The Introduction now links the paper to three chemistry/electron-density strands:

- Brehm–Thomas (2018): lossless compression of volumetric chemistry data, including electron-density grids;
- MARGR (JCTC 2026): downstream property fidelity of machine-learned electron densities under real-space integration;
- ChargeFlow (JCTC 2026, 22(16), 8481–8492): downstream Bader/ESP use of learned charge-conditioned electron densities.

This positions the manuscript positively as a controlled-lossy-reconstruction fidelity framework rather than defining novelty through absence claims.

## Remaining production tasks

1. finalize author order, affiliations, corresponding author, ORCIDs, funding, CRediT, and disclosures;
2. produce final Figure 1 schematic and Figure 5 spatial basin-migration panel;
3. visually redesign/finalize Figures 2–6 using the new submission numbering;
4. assemble the clean SI with final supplementary figures and tables;
5. embed final figures into the ACS Fast Format manuscript near first discussion;
6. freeze an immutable data/software archive with a persistent identifier and exact commit/tag;
7. rerun submission-day reference, figure, metadata, and file-integrity QA.

The representative 12-material direct decomposition and full-benchmark reassignment analysis already support the current mechanism narrative. Additional per-atom mechanism data may refine Figure 5 but do not reopen the frozen benchmark or core estimands.
