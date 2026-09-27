# Submission source audit — 2026-09-27

Status: **SOURCE GATE PASS**

Branch: `paper/fourier-mechanism-integration-20260927`

Canonical sources:
- `paper/MANUSCRIPT.md`
- `paper/SUPPLEMENTARY_INFORMATION.md`
- `paper/CURRENT_PAPER_STORY.md`
- `paper/FIGURE_MAP.md`
- `paper/CLAIM_EVIDENCE_MATRIX.md`
- `paper/READER_FACING_PROVENANCE_INDEX.md`

## Deterministic manuscript gates

### Junbo scientific-writing audit

Command-equivalent gate:
`audit_manuscript.py MANUSCRIPT.md --final`

Result:
- blockers: **0**
- warnings: **0**

### Generic submission Markdown audit

Command-equivalent gate:
`markdown_submission_audit.py --main MANUSCRIPT.md --si SUPPLEMENTARY_INFORMATION.md`

Result:
- blockers: **0**
- warnings: **16**

All 16 warnings were manually inspected and are false-positive literal-LaTeX warnings caused by the audit script evaluating individual lines inside valid multi-line `$$ ... $$` display equations. No literal LaTeX command occurs in reader-facing prose outside math mode.

## Cross-document numbering and references

- Main Figure references: **1–8**, contiguous; all eight are cited in the manuscript.
- Main Figure assets: **Figures 1–8 each have PNG/PDF/SVG outputs**.
- Supplementary Figure inventory: **S1–S8**, contiguous.
- Supplementary Figure assets: **S1–S8 have rendered publication-format outputs**.
- Supplementary Table inventory: **S1–S17**, contiguous.
- Every Supplementary Figure/Table reference parsed from the manuscript/SI resolves to an existing inventory item.
- Numeric literature references: **1–21**, contiguous.
- Every literature reference 1–21 is cited at least once; there are no uncited reference entries and no cited-but-missing entries.
- Main/SI title match exactly:
  *Numerical stability qualification for downstream-fidelity benchmarks of compressed electronic densities*.

## Recent-reference verification

Current web/publisher verification was performed for the most time-sensitive recent references:

- Reference 1: *A Survey on Error-Bounded Lossy Compression for Scientific Datasets*, ACM Computing Surveys 57(11), Article 287, DOI **10.1145/3733104** — metadata verified.
- Reference 7: *An Algorithm for Atom-Centered Lossy Compression of the Atomic Orbital Basis in Density Functional Theory Calculations*, J. Chem. Theory Comput. 22(7), 3327–3340 (2026), DOI **10.1021/acs.jctc.5c01988** — publisher metadata verified.
- Reference 16: *TOPIQ: Statistical Error Propagation for Quantity-of-Interest Prediction under Lossy Compression*, arXiv:2608.26912 — current arXiv record verified; the arXiv record states **Accepted by SC'26**. The manuscript conservatively retains the arXiv citation because the conference proceedings record/DOI is not yet the stable published citation at the audit date.

## Scientific-content lock

The current submission story remains:

1. Reference-QoI stability is a separate benchmark axis.
2. QSQ prospectively stratifies numerical response risk under the declared perturbation model.
3. Classification transfers across an independent on-grid Bader implementation when assignment semantics are matched.
4. Realized reconstruction distortion, not nominal codec tolerance, is required for fair codec comparison.
5. The matched-distortion Hartree codec effect is mechanistically resolved by reciprocal-space error allocation and downstream operator weighting.
6. Strict numerical fidelity and coarse qualitative decision preservation are distinct contracts.

No additional scientific endpoint is required for the current submission scope.

## Remaining submission metadata, not scientific blockers

The repository does **not** currently contain authoritative reader-facing metadata for:
- author list/order;
- affiliations;
- corresponding-author designation/email;
- ORCID identifiers;
- funding/acknowledgement statement, if required by the target journal.

These fields must not be invented during export.

The repository also does not yet contain a final DOI-backed archival release for the exact submission commit. Data/Code Availability correctly describes this as a release-stage item rather than a completed DOI.

## Artifact/render gate

Anonymous/content proof input snapshot:
- proof packaging head SHA: `4124d3501c2ba870d4ae84b20471963ff214d60b`;
- canonical scientific inputs: current `paper/MANUSCRIPT.md`, `paper/FIGURE_CAPTIONS.md`, and rendered Figures 1-8;
- later repository commits in `paper/export/` document the deterministic export layer and do not change the scientific source used for the inspected proof.

Resolved export defects found by visual QA:
- Figure 1 was rebuilt to match its intended measurement-contract role rather than duplicating Figure 2's operator hierarchy;
- caption-registry escape defects were corrected for `\\times`, `\\,e` and `L_\\infty`;
- empty-base chemical subscripts were replaced by export-safe text forms `RuO₂` and `CO₂RR`;
- semantic math labels use Word-safe `\\text{...}` forms where OMML/LibreOffice split `\\mathrm{...}` into spaced letters;
- bibliography paragraphs are left-aligned and compact rather than fully justified.

Final anonymous/content proof checks:
- rendered page count: **18**;
- embedded main figures: **8**;
- native OMML equation elements: **134**;
- DOCX structural audit: **0 blockers, 0 warnings**;
- PDF preflight: **18 pages**, unencrypted, openable, not scan-like;
- every rendered page inspected visually;
- post-scrub render comparison: **18/18 pages pixel-identical (AE=0)** to the inspected pre-scrub proof.

The generic two-renderer PDF parity helper was also run. Its report is not used as a release blocker because its current filename ordering pairs `page-2` with `page-10` and so on. Same-page manual/primary-render inspection found no renderer-specific scientific or layout defect.

## Release decision

**Scientific/content source gate: PASS.**

**Anonymous/content artifact gate: PASS.**

The inspected DOCX/PDF proof is suitable for content review. A submission-ready author-identifiable release remains gated only by authoritative author/affiliation metadata and the final archival snapshot/DOI, not by unresolved scientific analysis.
