# Main-manuscript content-proof export

This directory records the deterministic export layer used for the anonymous/content proof. The canonical scientific sources remain:

- `paper/MANUSCRIPT.md`
- `paper/FIGURE_CAPTIONS.md`
- `figures/R/rendered/` main-figure sources, including QOAC-H as reader-facing Fig. 8 and the existing external-confirmation render as Fig. 9

The proof is not the authoritative scientific source and must be regenerated after any canonical-source change.

## Export rules

1. Use Pandoc so inline/display math becomes native Word OMML.
2. Insert Figures 1-9 only in a temporary export Markdown file; do not add export-only image links to the canonical manuscript.
3. Use the unified captions in `paper/FIGURE_CAPTIONS.md`; do not reconstruct captions from plot-internal subtitles.
4. Place main figures at the end of the corresponding Results subsection rather than mechanically after the first in-text citation when the latter produces large pagination gaps.
5. Use Times New Roman 11 pt for sustained prose, restrained black academic styling, centered figures and captions kept with their figure.
6. Run `postprocess_main_proof.py` after Pandoc to keep bibliography entries left-aligned and compact; this avoids the abnormal word spacing produced by fully justified reference paragraphs.
7. Run the manuscript-submission DOCX structural audit.
8. Render every DOCX page and inspect it visually.
9. Export PDF from the exact audited DOCX and run PDF preflight.

## Word-compatibility decisions encoded in canonical source

The following source-level fixes were made because they affected native Word math rendering:

- chemical text is written as `RuO₂` and `CO₂RR`, not empty-base math subscripts;
- semantic equation labels such as `eligible`, `certified`, `target`, `RMS`, `ZFP` and `SZ3` use `\\text{...}` rather than `\\mathrm{...}` where Word/LibreOffice otherwise separates letters;
- figure-caption LaTeX escapes are kept literal (`\\,e`, `\\times`, `L_\\infty`).

## Current proof gate

The 2026-09-27 anonymous/content proof has 18 pages, 8 embedded main figures and 134 native OMML equation elements. The structural DOCX audit and PDF preflight both pass. Author/affiliation metadata and archival DOI remain release-stage metadata rather than content-proof inputs.


## 2026-10-05 figure-number mapping

The reader-facing nine-figure manuscript uses:
- Figures 1–7: existing locked main renders;
- Figure 8: `figures/R/rendered/figure8_qoac_h_R.png`;
- Figure 9: `figures/R/rendered/figure8_external_confirmation_R.png`.

The external-confirmation filename retains its historical internal number for provenance; export code maps it to reader-facing Figure 9.
