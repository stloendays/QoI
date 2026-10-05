#!/usr/bin/env python3
"""Deterministic post-processing for the anonymous main-manuscript DOCX proof.

Input DOCX is expected to come from Pandoc after assembling the canonical
MANUSCRIPT.md, FIGURE_CAPTIONS.md and current Figure 1-9 PNG assets.

This script changes presentation only. It does not edit scientific content.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


def format_references(doc: Document) -> None:
    in_refs = False
    for p in doc.paragraphs:
        text = p.text.strip()
        if text == "References":
            in_refs = True
            continue
        if not in_refs:
            continue
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(1.5)
        pf.line_spacing = 1.0
        pf.keep_together = True
        pf.widow_control = True
        for run in p.runs:
            run.font.size = Pt(10)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_docx", type=Path)
    ap.add_argument("output_docx", type=Path)
    args = ap.parse_args()

    doc = Document(args.input_docx)
    format_references(doc)
    doc.save(args.output_docx)
    print(args.output_docx)


if __name__ == "__main__":
    main()
