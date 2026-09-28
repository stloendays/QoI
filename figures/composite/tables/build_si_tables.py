"""Supplementary Tables S1-S17 in journal form, from the frozen reader-facing markdown.

Reads paper/SUPPLEMENTARY_TABLES_FINAL.md (never edited here), and writes

    SI_tables.html   journal table style (hairline top/bottom rules, header rule,
                     no vertical rules, no banded rows, Arial 8 pt), one table per block
    SI_tables.pdf    the same page printed by headless Chrome, A4 portrait
    SI_tables.docx   the same content through python-docx with identical rules

Numbers are copied cell for cell; nothing is retyped. TeX fragments in the
markdown (\\(10^{-3}\\,e\\), $L_\\infty$, ...) are converted to Unicode so the
tables read without a TeX engine.

    D:/Research/CatalystForge/.venv/Scripts/python.exe build_si_tables.py
"""
import html
import os
import re
import subprocess

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "paper", "SUPPLEMENTARY_TABLES_FINAL.md")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
INK, MID, LINE = "#1B1B1B", "#6B6F76", "#1B1B1B"

SUP = str.maketrans("0123456789-+", "\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079\u207b\u207a")
SUB = str.maketrans("0123456789", "\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089")
GREEK = {r"\tau": "\u03c4", r"\epsilon": "\u03b5", r"\rho": "\u03c1", r"\Delta": "\u0394", r"\infty": "\u221e",
         r"\times": "\u00d7", r"\ge": "\u2265", r"\geq": "\u2265", r"\le": "\u2264", r"\leq": "\u2264",
         r"\pm": "\u00b1", r"\sum": "\u03a3", r"\in": "\u2208", r"\mathcal{G}_s": "G\u209b", r"\qquad": "   ",
         r"\,": "\u2009", r"\;": " ", r"\to": "\u2192", r"\rightarrow": "\u2192", r"\ldots": "\u2026"}


def tex(s):
    """Convert the small TeX vocabulary used in the tables to Unicode."""
    def frag(m):
        t = m.group(1)
        t = re.sub(r"\\text\{([^}]*)\}", r"\1", t)
        t = re.sub(r"\\sqrt\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", lambda k: "\u221a(" + k.group(1) + ")", t)
        t = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", t)
        for k, v in sorted(GREEK.items(), key=lambda kv: -len(kv[0])):
            t = t.replace(k, v)
        t = re.sub(r"\^\{([^}]*)\}", lambda k: k.group(1).translate(SUP), t)
        t = re.sub(r"\^([0-9\-+])", lambda k: k.group(1).translate(SUP), t)
        t = re.sub(r"_\{([^}]*)\}", lambda k: k.group(1).translate(SUB) if k.group(1).isdigit() else "\u2009" + k.group(1), t)
        t = re.sub(r"_([0-9])", lambda k: k.group(1).translate(SUB), t)
        t = re.sub(r"_([A-Za-z])", r"\1", t)
        return t.replace("{", "").replace("}", "").replace("\\", "")
    s = re.sub(r"\\\((.*?)\\\)", frag, s)
    s = re.sub(r"\$\$(.*?)\$\$", frag, s, flags=re.S)
    s = re.sub(r"\$(.*?)\$", frag, s)
    s = re.sub(r"(?<![\w\d])(10|e)\^-(\d)", lambda m: m.group(1) + ("-" + m.group(2)).translate(SUP), s)   # bare 10^-4
    s = re.sub(r"\b1e-0?(\d)\b", lambda m: "10" + ("-" + m.group(1)).translate(SUP), s)                    # 1e-4 -> 10^-4
    s = s.replace("`", "")
    return s


def inline(s):
    """Markdown bold/italic -> list of (text, bold) runs."""
    out, pos = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*", s):
        if m.start() > pos:
            out.append((s[pos:m.start()], False))
        out.append((m.group(1), True))
        pos = m.end()
    if pos < len(s):
        out.append((s[pos:], False))
    return out


def parse(md):
    """Return a list of blocks: ('h2', text) ('h3', text) ('p', text) ('table', header, align, rows)."""
    blocks, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.startswith("# "):
            blocks.append(("h1", ln[2:].strip()))
        elif ln.startswith("## "):
            blocks.append(("h2", ln[3:].strip()))
        elif ln.startswith("### "):
            blocks.append(("h3", ln[4:].strip()))
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            header, sep, body = rows[0], rows[1], rows[2:]
            align = ["r" if c.strip().endswith(":") and not c.strip().startswith(":") else "l" for c in sep]
            blocks.append(("table", header, align, body))
            continue
        elif ln.startswith("$$"):
            eq = []
            i += 1
            while i < len(lines) and not lines[i].startswith("$$"):
                eq.append(lines[i].strip())
                i += 1
            blocks.append(("eq", " ".join(eq)))
        elif ln.strip():
            blocks.append(("p", ln.strip()))
        i += 1
    return blocks


# ---- HTML ----------------------------------------------------------------------------------------
CSS = """
@page { size: A4 portrait; margin: 18mm 16mm 18mm 16mm; }
body { font-family: Arial, Helvetica, sans-serif; color: %(ink)s; font-size: 8.5pt; line-height: 1.3; margin: 0; }
h1 { font-size: 13pt; font-weight: 700; margin: 0 0 4mm 0; }
h2 { font-size: 9.5pt; font-weight: 700; margin: 7mm 0 1.5mm 0; page-break-after: avoid; }
h3 { font-size: 8.5pt; font-weight: 700; margin: 3.5mm 0 1mm 0; page-break-after: avoid; }
p  { margin: 0 0 1.6mm 0; }
p.caption { font-size: 7.8pt; }
p.prov { font-size: 7.4pt; color: %(mid)s; }
p.eq { font-family: 'Cambria Math', 'Times New Roman', serif; font-size: 9pt; text-align: center; margin: 1.5mm 0; }
table { border-collapse: collapse; width: 100%%; margin: 1.5mm 0 2.5mm 0; font-size: 7.6pt; page-break-inside: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { font-weight: 700; text-align: left; vertical-align: bottom; padding: 1.2mm 1.6mm 1mm 0; border-top: 0.6pt solid %(line)s; border-bottom: 0.5pt solid %(line)s; }
td { vertical-align: top; padding: 0.9mm 1.6mm 0.7mm 0; border-bottom: none; }
tbody tr:last-child td { border-bottom: 0.6pt solid %(line)s; }
th.r, td.r { text-align: right; font-variant-numeric: tabular-nums; }
th:last-child, td:last-child { padding-right: 0; }
""" % dict(ink=INK, mid=MID, line=LINE)


def runs_html(s):
    return "".join(("<b>%s</b>" % html.escape(t)) if b else html.escape(t) for t, b in inline(tex(s)))


def to_html(blocks):
    out = ["<!doctype html><meta charset='utf-8'><title>Supplementary Tables S1-S17</title><style>%s</style><body>" % CSS]
    for b in blocks:
        if b[0] == "h1":
            out.append("<h1>%s</h1>" % runs_html(b[1]))
        elif b[0] == "h2":
            out.append("<h2>%s</h2>" % runs_html(b[1]))
        elif b[0] == "h3":
            out.append("<h3>%s</h3>" % runs_html(b[1]))
        elif b[0] == "eq":
            out.append("<p class='eq'>%s</p>" % html.escape(tex("$" + b[1] + "$")))
        elif b[0] == "p":
            cls = "prov" if b[1].startswith("**Evidence provenance") or b[1].startswith("**Machine-readable") else \
                  "caption" if b[1].startswith("**") else ""
            out.append("<p class='%s'>%s</p>" % (cls, runs_html(b[1])))
        else:
            _, header, align, rows = b
            out.append("<table><thead><tr>" + "".join("<th class='%s'>%s</th>" % (a, runs_html(h)) for h, a in zip(header, align))
                       + "</tr></thead><tbody>")
            for r in rows:
                r = r + [""] * (len(header) - len(r))
                out.append("<tr>" + "".join("<td class='%s'>%s</td>" % (a, runs_html(c)) for c, a in zip(r, align)) + "</tr>")
            out.append("</tbody></table>")
    out.append("</body>")
    return "\n".join(out)


# ---- DOCX ----------------------------------------------------------------------------------------
def cell_border(cell, top=None, bottom=None):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for side, val in (("top", top), ("bottom", bottom), ("left", None), ("right", None)):
        el = OxmlElement("w:%s" % side)
        if val:
            el.set(qn("w:val"), "single"); el.set(qn("w:sz"), str(val)); el.set(qn("w:color"), "1B1B1B")
        else:
            el.set(qn("w:val"), "nil")
        borders.append(el)
    tcPr.append(borders)


def add_runs(par, s, size, bold_all=False, color=None):
    for t, b in inline(tex(s)):
        r = par.add_run(t)
        r.font.size = Pt(size); r.font.name = "Arial"; r.bold = b or bold_all
        if color:
            r.font.color.rgb = RGBColor.from_string(color)


def to_docx(blocks, path):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.6); sec.top_margin = sec.bottom_margin = Cm(1.8)
    st = doc.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(8.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    for b in blocks:
        if b[0] in ("h1", "h2", "h3"):
            p = doc.add_paragraph(); p.paragraph_format.space_before = Pt({"h1": 0, "h2": 14, "h3": 8}[b[0]])
            p.paragraph_format.space_after = Pt(3); p.paragraph_format.keep_with_next = True
            add_runs(p, b[1], {"h1": 13, "h2": 9.5, "h3": 8.5}[b[0]], bold_all=True)
        elif b[0] == "eq":
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(tex("$" + b[1] + "$")); r.font.name = "Cambria Math"; r.font.size = Pt(9)
        elif b[0] == "p":
            p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
            prov = b[1].startswith("**Evidence provenance") or b[1].startswith("**Machine-readable")
            add_runs(p, b[1], 7.4 if prov else 7.8, color="6B6F76" if prov else None)
        else:
            _, header, align, rows = b
            t = doc.add_table(rows=1 + len(rows), cols=len(header)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.autofit = True
            for j, (h, a) in enumerate(zip(header, align)):
                c = t.cell(0, j); c.text = ""
                p = c.paragraphs[0]; add_runs(p, h, 7.6, bold_all=True)
                if a == "r":
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                cell_border(c, top=6, bottom=4)
            for i, r in enumerate(rows, start=1):
                r = r + [""] * (len(header) - len(r))
                for j, (v, a) in enumerate(zip(r, align)):
                    c = t.cell(i, j); c.text = ""
                    p = c.paragraphs[0]; add_runs(p, v, 7.6)
                    p.paragraph_format.space_after = Pt(0)
                    if a == "r":
                        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    cell_border(c, bottom=6 if i == len(rows) else None)
            # repeat header row on page breaks
            trPr = t.rows[0]._tr.get_or_add_trPr(); el = OxmlElement("w:tblHeader"); el.set(qn("w:val"), "true"); trPr.append(el)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
    doc.save(path)


def main():
    md = open(SRC, encoding="utf-8").read()
    blocks = parse(md)
    # the file's own H1 becomes the document title; drop its one-line preamble paragraph? keep it.
    blocks = [("h1", b[1]) if b[0] == "h2" and b[1].startswith("Supplementary Tables") else b for b in blocks]
    if md.startswith("# "):
        blocks.insert(0, ("h1", md.split("\n", 1)[0][2:].strip()))
    n_tables = sum(1 for b in blocks if b[0] == "table")
    h = to_html(blocks)
    hp = os.path.join(HERE, "SI_tables.html")
    open(hp, "w", encoding="utf-8").write(h)
    pdf = os.path.join(HERE, "SI_tables.pdf")
    if os.path.exists(pdf):
        os.remove(pdf)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=%s" % pdf,
                    "file:///" + hp.replace("\\", "/")], check=False, capture_output=True, timeout=300)
    to_docx(blocks, os.path.join(HERE, "SI_tables.docx"))
    print("blocks %d, tables %d; html/pdf(%s)/docx written" % (len(blocks), n_tables, "ok" if os.path.exists(pdf) else "FAILED"))


if __name__ == "__main__":
    main()
