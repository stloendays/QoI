"""Manuscript and Supplementary Information as DOCX + PDF, with the composite figures embedded.

Sources (read only):
    paper/MANUSCRIPT.md                    main text; Fig. N is inserted after the paragraph that first cites it
    paper/FIGURE_CAPTIONS.md               main captions (panel letters lowercased to match the figures)
    paper/SUPPLEMENTARY_INFORMATION.md     SI notes
    paper/SUPPLEMENTARY_FIGURE_CAPTIONS.md SI figure captions
    paper/SUPPLEMENTARY_TABLES_FINAL.md    SI tables (parsed by tables/build_si_tables.py)
    figures/composite/fig*/Fig*.png        600 dpi renders, embedded at 300 dpi

Outputs, in figures/composite/release/:
    QSQ_manuscript_<date>.{html,pdf,docx}
    QSQ_supplementary_information_<date>.{html,pdf,docx}
    MANIFEST_<date>.txt   sha256 of every deliverable

    D:/Research/CatalystForge/.venv/Scripts/python.exe build_manuscript.py
"""
import datetime as dt
import hashlib
import html
import os
import re
import subprocess
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tables"))
import build_si_tables as T  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PAPER = os.path.join(REPO, "paper")
OUT = os.path.join(HERE, "release")
EMBED = os.path.join(OUT, "_embed")
DATE = dt.date.today().strftime("%Y%m%d")
CHROME = T.CHROME
TEXT_W_CM = 17.8


# ---- markdown -> blocks ---------------------------------------------------------------------------------
def parse_md(md):
    blocks, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.startswith("# "):
            blocks.append(("h1", ln[2:].strip()))
        elif ln.startswith("## "):
            blocks.append(("h2", ln[3:].strip()))
        elif ln.startswith("### "):
            blocks.append(("h3", ln[4:].strip()))
        elif ln.startswith("$$"):
            eq, i = [], i + 1
            while i < len(lines) and not lines[i].startswith("$$"):
                eq.append(lines[i].strip()); i += 1
            blocks.append(("eq", " ".join(eq)))
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            align = ["r" if c.strip().endswith(":") and not c.strip().startswith(":") else "l" for c in rows[1]]
            blocks.append(("table", rows[0], align, rows[2:])); continue
        elif re.match(r"^\s*[-*] ", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*] ", lines[i]):
                items.append(re.sub(r"^\s*[-*] ", "", lines[i]).strip()); i += 1
            blocks.append(("ul", items)); continue
        elif re.match(r"^\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]).strip()); i += 1
            blocks.append(("ol", items)); continue
        elif ln.strip():
            blocks.append(("p", ln.strip()))
        i += 1
    return blocks


def runs(s):
    """bold/italic/code runs -> [(text, bold, italic)], TeX converted to Unicode."""
    s = T.tex(s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    out, pos = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*|\*(.+?)\*", s):
        if m.start() > pos:
            out.append((s[pos:m.start()], False, False))
        if m.group(1) is not None:
            out.append((m.group(1), True, False))
        else:
            out.append((m.group(2), False, True))
        pos = m.end()
    if pos < len(s):
        out.append((s[pos:], False, False))
    return out


def lower_panels(s):
    s = re.sub(r"\*\*\(([A-H])\)\*\*", lambda m: "**%s**," % m.group(1).lower(), s)      # **(A)** -> **a**,
    s = re.sub(r"\*\*([A-H])(-[A-H])?,\*\*", lambda m: "**%s%s**," % (m.group(1).lower(), (m.group(2) or "").lower()), s)
    s = re.sub(r"\bFig\. (\d)([A-H])\b", lambda m: "Fig. %s%s" % (m.group(1), m.group(2).lower()), s)
    return s


def captions(path, key):
    """{N: caption} from a captions file whose sections are '## Figure N' / '## Supplementary Figure SN | ...'."""
    out, cur = {}, None
    for ln in open(path, encoding="utf-8").read().split("\n"):
        m = re.match(r"^## (?:Supplementary )?Figure (S?\d+)", ln)
        if m:
            cur = m.group(1); out[cur] = []
            title = ln.split("|", 1)[1].strip() if "|" in ln else None
            if title:
                out[cur].append("**Supplementary Figure %s | %s**" % (cur, title))
        elif cur and ln.strip():
            out[cur].append(ln.strip())
    return {k: lower_panels(" ".join(v)) for k, v in out.items()}


def embed_png(src, stem):
    os.makedirs(EMBED, exist_ok=True)
    dst = os.path.join(EMBED, stem + ".png")
    im = Image.open(src)
    im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)          # 600 -> 300 dpi
    im.save(dst, dpi=(300, 300), optimize=True)
    return dst


# ---- HTML ----------------------------------------------------------------------------------------------
CSS = T.CSS + """
body { font-size: 10pt; line-height: 1.45; }
h1 { font-size: 15pt; margin-bottom: 6mm; }
h2 { font-size: 11.5pt; margin: 8mm 0 2mm 0; }
h3 { font-size: 10pt; margin: 5mm 0 1.5mm 0; }
p { margin: 0 0 2.4mm 0; text-align: justify; }
p.eq { font-size: 10.5pt; }
ul, ol { margin: 0 0 2.4mm 0; padding-left: 6mm; }
li { margin-bottom: 1mm; }
ol.refs { font-size: 8.5pt; }
figure { margin: 5mm 0 6mm 0; page-break-inside: avoid; }
figure img { width: 100%; display: block; }
figcaption { font-size: 8.3pt; line-height: 1.35; margin-top: 2.5mm; text-align: justify; }
"""


def html_runs(s):
    o = []
    for t, b, it in runs(s):
        t = html.escape(t)
        o.append(("<b>%s</b>" if b else "<i>%s</i>" if it else "%s") % t)
    return "".join(o)


def blocks_html(blocks, refs_start=None):
    out = []
    for b in blocks:
        k = b[0]
        if k in ("h1", "h2", "h3"):
            out.append("<%s>%s</%s>" % (k, html_runs(b[1]), k))
        elif k == "eq":
            out.append("<p class='eq'>%s</p>" % html.escape(T.tex("$" + b[1] + "$")))
        elif k == "p":
            out.append("<p>%s</p>" % html_runs(b[1]))
        elif k == "ul":
            out.append("<ul>" + "".join("<li>%s</li>" % html_runs(x) for x in b[1]) + "</ul>")
        elif k == "ol":
            out.append("<ol class='refs'>" + "".join("<li>%s</li>" % html_runs(x) for x in b[1]) + "</ol>")
        elif k == "fig":
            out.append("<figure><img src='%s'><figcaption>%s</figcaption></figure>" % (b[1].replace("\\", "/"), html_runs(b[2])))
        elif k == "table":
            _, header, align, rows = b
            out.append("<table><thead><tr>" + "".join("<th class='%s'>%s</th>" % (a, html_runs(h)) for h, a in zip(header, align))
                       + "</tr></thead><tbody>")
            for r in rows:
                r = r + [""] * (len(header) - len(r))
                out.append("<tr>" + "".join("<td class='%s'>%s</td>" % (a, html_runs(c)) for c, a in zip(r, align)) + "</tr>")
            out.append("</tbody></table>")
    return "\n".join(out)


def write_html_pdf(blocks, stem, title):
    h = "<!doctype html><meta charset='utf-8'><title>%s</title><style>%s</style><body>%s</body>" % (
        html.escape(title), CSS, blocks_html(blocks))
    hp = os.path.join(OUT, stem + ".html")
    open(hp, "w", encoding="utf-8").write(h)
    pdf = os.path.join(OUT, stem + ".pdf")
    if os.path.exists(pdf):
        os.remove(pdf)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=%s" % pdf,
                    "file:///" + hp.replace("\\", "/")], check=False, capture_output=True, timeout=600)
    return pdf


# ---- DOCX ----------------------------------------------------------------------------------------------
def add_runs(par, s, size, bold_all=False, color=None):
    for t, b, it in runs(s):
        r = par.add_run(t); r.font.size = Pt(size); r.font.name = "Arial"; r.bold = b or bold_all; r.italic = it
        if color:
            r.font.color.rgb = RGBColor.from_string(color)


def write_docx(blocks, stem):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.6); sec.top_margin = sec.bottom_margin = Cm(1.8)
    st = doc.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    for b in blocks:
        k = b[0]
        if k in ("h1", "h2", "h3"):
            p = doc.add_paragraph(); p.paragraph_format.space_before = Pt({"h1": 0, "h2": 16, "h3": 10}[k])
            p.paragraph_format.space_after = Pt(4); p.paragraph_format.keep_with_next = True
            add_runs(p, b[1], {"h1": 15, "h2": 11.5, "h3": 10}[k], bold_all=True)
        elif k == "eq":
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(T.tex("$" + b[1] + "$")); r.font.name = "Cambria Math"; r.font.size = Pt(10.5)
        elif k == "p":
            p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_runs(p, b[1], 10)
        elif k in ("ul", "ol"):
            for j, x in enumerate(b[1], start=1):
                p = doc.add_paragraph(style="List Bullet" if k == "ul" else "List Number")
                p.paragraph_format.space_after = Pt(2)
                add_runs(p, x, 10 if k == "ul" else 8.5)
        elif k == "fig":
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_before = Pt(10)
            p.add_run().add_picture(b[1], width=Cm(TEXT_W_CM))
            c = doc.add_paragraph(); c.paragraph_format.space_after = Pt(12); c.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_runs(c, b[2], 8.3)
        elif k == "table":
            T.to_docx_table(doc, b)
    path = os.path.join(OUT, stem + ".docx")
    doc.save(path)
    return path


# ---- assembly ------------------------------------------------------------------------------------------
def main_manuscript():
    md = open(os.path.join(PAPER, "MANUSCRIPT.md"), encoding="utf-8").read()
    caps = captions(os.path.join(PAPER, "FIGURE_CAPTIONS.md"), "Figure")
    blocks = [(b[0], lower_panels(b[1])) if b[0] == "p" else b for b in parse_md(md)]
    placed, out = set(), []
    for b in blocks:
        out.append(b)
        if b[0] == "p":
            for n in re.findall(r"Fig(?:\.|ure) (\d)", b[1]):
                if n not in placed:
                    placed.add(n)
                    png = embed_png(os.path.join(HERE, "fig%s" % n, "Fig%s.png" % n), "Fig%s" % n)
                    out.append(("fig", png, caps[n]))
    assert placed == {str(i) for i in range(1, 9)}, placed
    return out


def supplementary():
    md = open(os.path.join(PAPER, "SUPPLEMENTARY_INFORMATION.md"), encoding="utf-8").read()
    caps = captions(os.path.join(PAPER, "SUPPLEMENTARY_FIGURE_CAPTIONS.md"), "Supplementary Figure")
    blocks = parse_md(md)
    blocks.append(("h2", "Supplementary Figures"))
    for n in range(1, 9):
        png = embed_png(os.path.join(HERE, "figS%d" % n, "FigS%d.png" % n), "FigS%d" % n)
        blocks.append(("fig", png, caps["S%d" % n]))
    tmd = open(T.SRC, encoding="utf-8").read()
    tb = T.parse(tmd)
    tb = [("h2", "Supplementary Tables") if b[0] == "h1" else b for b in tb]
    return blocks + tb


def main():
    os.makedirs(OUT, exist_ok=True)
    # give the SI table builder a docx-table entry point
    if not hasattr(T, "to_docx_table"):
        def to_docx_table(doc, b):
            from docx.enum.table import WD_TABLE_ALIGNMENT
            _, header, align, rows = b
            t = doc.add_table(rows=1 + len(rows), cols=len(header)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
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

    deliverables = []
    for stem, blocks, title in (("QSQ_manuscript_%s" % DATE, main_manuscript(),
                                 "Numerical stability qualification for downstream-fidelity benchmarks of compressed electronic densities"),
                                ("QSQ_supplementary_information_%s" % DATE, supplementary(), "Supplementary Information")):
        pdf = write_html_pdf(blocks, stem, title)
        docx = write_docx(blocks, stem)
        deliverables += [pdf, docx]
        print("%s: %d blocks, pdf %s, docx %.1f MB" % (stem, len(blocks), "ok" if os.path.exists(pdf) else "FAILED",
                                                       os.path.getsize(docx) / 1e6))
    man = [("%s  %s  %d bytes" % (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.path.basename(p), os.path.getsize(p)))
           for p in deliverables]
    open(os.path.join(OUT, "MANIFEST_%s.txt" % DATE), "w", encoding="utf-8").write("\n".join(man) + "\n")
    print("\n".join(man))


if __name__ == "__main__":
    main()
