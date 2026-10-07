"""Nature Communications manuscript as PDF + DOCX with the eight main figures embedded.

Reuses figures/composite/build_manuscript.py (parser, HTML/PDF and DOCX writers) and changes only:
  - the figure mapping (8 main figures: frozen Figs. 3 and 7 and the new figures/nc/fig1, fig4-fig8), and
  - the caption source (the '## Figure legends' section of paper/MANUSCRIPT.md, which is removed from the body because
    each figure is inserted with its legend after the paragraph that first cites it).

    D:/Research/CatalystForge/.venv/Scripts/python.exe build_nc_manuscript.py
Outputs: figures/nc/release/NC_manuscript_<date>.{html,pdf,docx} and MANIFEST_<date>.txt
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMP = os.path.join(os.path.dirname(HERE), "composite")
sys.path.insert(0, COMP)
import build_manuscript as B  # noqa: E402

REPO = B.REPO
B.OUT = os.path.join(HERE, "release")
B.EMBED = os.path.join(B.OUT, "_embed")

FIG = {
    "1": os.path.join(HERE, "fig1", "Fig1.png"),
    "2": os.path.join(COMP, "fig3", "Fig3.png"),
    "3": os.path.join(COMP, "fig7", "Fig7.png"),
    "4": os.path.join(HERE, "fig4", "Fig4.png"),
    "5": os.path.join(HERE, "fig5", "Fig5.png"),
    "6": os.path.join(HERE, "fig6", "Fig6.png"),
    "7": os.path.join(HERE, "fig7", "Fig7.png"),
    "8": os.path.join(HERE, "fig8", "Fig8.png"),
}


def split_legends(md):
    body, leg = md.split("## Figure legends", 1)
    caps = {}
    for para in [p.strip() for p in leg.strip().split("\n\n") if p.strip()]:
        m = re.match(r"\*\*Fig\. (\d+) \|", para)
        assert m, para[:60]
        caps[m.group(1)] = para
    return body, caps


SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def superscripts(text):
    """Nature-style citation markers <sup>1–4,7</sup> -> Unicode superscripts (works in both the PDF and the DOCX)."""
    return re.sub(r"<sup>([^<]*)</sup>", lambda m: m.group(1).translate(SUP), text)


# TeX macros the shared converter (build_si_tables.tex) does not know; mapped before it runs (proof rendering only).
MACROS = [(r"\lVert", "‖"), (r"\rVert", "‖"), (r"\equiv", " ≡ "), (r"\mapsto", " ↦ "), (r"\pmod", " mod "),
          (r"\alpha", "α"), (r"\ast", "*"), (r"\land", " ∧ "), (r"\max", "max"), (r"\le", "≤"), (r"\ge", "≥"),
          (r"\in", " ∈ "), (r"\mathbb{E}", "𝔼"), (r"\quad", " "), (r"\qquad", "  ")]


def macros(text):
    for k, v in MACROS:
        text = re.sub(re.escape(k) + r"(?![A-Za-z])", lambda m, v=v: v, text)
    return text


def main_manuscript():
    md = macros(superscripts(open(os.path.join(REPO, "paper", "MANUSCRIPT.md"), encoding="utf-8").read()))
    body, caps = split_legends(md)
    assert set(caps) == set(FIG), (sorted(caps), sorted(FIG))
    blocks = [(b[0], B.lower_panels(b[1])) if b[0] == "p" else b for b in B.parse_md(body)]
    placed, out = set(), []
    for b in blocks:
        out.append(b)
        if b[0] == "p":
            for n in re.findall(r"Fig(?:\.|ure)s?\.? (\d)", b[1]):
                if n in FIG and n not in placed:
                    placed.add(n)
                    png = B.embed_png(FIG[n], "NCFig%s" % n)
                    out.append(("fig", png, caps[n]))
    assert placed == set(FIG), placed
    return out


def _docx_table_patch():
    """Same table writer that build_manuscript.main() attaches to the SI table module."""
    T = B.T
    if hasattr(T, "to_docx_table"):
        return
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt

    def to_docx_table(doc, b):
        _, header, align, rows = b
        t = doc.add_table(rows=1 + len(rows), cols=len(header))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for j, (h, a) in enumerate(zip(header, align)):
            c = t.cell(0, j); c.text = ""; p = c.paragraphs[0]; T.add_runs(p, h, 7.6, bold_all=True)
            if a == "r":
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            T.cell_border(c, top=6, bottom=4)
        for i, r in enumerate(rows, start=1):
            r = r + [""] * (len(header) - len(r))
            for j, (v, a) in enumerate(zip(r, align)):
                c = t.cell(i, j); c.text = ""; p = c.paragraphs[0]; T.add_runs(p, v, 7.6)
                p.paragraph_format.space_after = Pt(0)
                if a == "r":
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                T.cell_border(c, bottom=6 if i == len(rows) else None)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
    T.to_docx_table = to_docx_table


def main():
    os.makedirs(B.OUT, exist_ok=True)
    _docx_table_patch()
    title = open(os.path.join(REPO, "paper", "MANUSCRIPT.md"), encoding="utf-8").readline().lstrip("# ").strip()
    stem = "NC_manuscript_%s" % B.DATE
    blocks = main_manuscript()
    pdf = B.write_html_pdf(blocks, stem, title)
    docx = B.write_docx(blocks, stem)
    man = ["%s  %s  %d bytes" % (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.path.basename(p), os.path.getsize(p))
           for p in (pdf, docx)]
    open(os.path.join(B.OUT, "MANIFEST_%s.txt" % B.DATE), "w", encoding="utf-8").write("\n".join(man) + "\n")
    print("\n".join(man))


if __name__ == "__main__":
    main()
