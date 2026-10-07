"""Word count of the Nature Communications manuscript and SI.

Counting rules (as stated in paper/nc_reopen/WORD_COUNT.md):
- running text only; section and subsection headings are excluded;
- display math ($$ ... $$) is excluded;
- superscript citation numbers (<sup>...</sup>) and [CITATION NEEDED: ...] placeholders are excluded;
- each inline math expression ($...$) counts as one word;
- numbers (e.g. "1.600%", "48/48") count as words;
- table cells are counted separately from running text (header row included, separator row excluded);
- a word is a whitespace-delimited token that contains at least one letter, digit or inline-math placeholder,
  so stand-alone punctuation such as "|" or "—" is not a word.
The abstract is also counted with plain `wc -w` semantics (every whitespace-delimited token).

Usage (stdlib only, any Python >= 3.8):
    python paper/nc_reopen/count_words.py [--manuscript paper/MANUSCRIPT.md] [--si paper/SUPPLEMENTARY_INFORMATION.md]
Prints a Markdown report to stdout.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SUP_RE = re.compile(r"<sup>.*?</sup>", re.S)
CITE_NEEDED_RE = re.compile(r"\[CITATION NEEDED:[^\]]*\]")
INLINE_MATH_RE = re.compile(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$")
MATH_TOKEN = "\u2063MATH\u2063"  # placeholder that cannot occur in the source
WORD_RE = re.compile(r"[0-9A-Za-z\u00C0-\u024F\u0370-\u03FF\u2063]")


def read(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")


def clean(text: str) -> str:
    text = SUP_RE.sub("", text)
    text = CITE_NEEDED_RE.sub("", text)
    text = INLINE_MATH_RE.sub(MATH_TOKEN, text)
    return text


def words(text: str) -> int:
    return sum(1 for tok in clean(text).split() if WORD_RE.search(tok))


def wc_w(text: str) -> int:
    return len(text.split())


def is_table_row(line: str) -> bool:
    return line.lstrip().startswith("|")


def is_separator_row(line: str) -> bool:
    return bool(re.fullmatch(r"\s*\|?(\s*:?-{3,}:?\s*\|)+\s*:?-*:?\s*\|?\s*", line))


def table_cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    # split on unescaped pipes outside inline code
    cells, cur, in_code = [], [], False
    for i, ch in enumerate(body):
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code and (i == 0 or body[i - 1] != "\\"):
            cells.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    cells.append("".join(cur))
    return cells


def sections(lines: list[str]) -> list[dict]:
    """Split a Markdown file into heading-delimited blocks.

    Each block records the heading path (h2, h3), its running-text lines and its table-cell lines.
    Display-math blocks are dropped.
    """
    blocks: list[dict] = []
    h2, h3 = "(front matter)", None
    cur = {"h2": h2, "h3": h3, "text": [], "cells": []}
    in_display = False
    for line in lines:
        stripped = line.strip()
        if stripped == "$$" or (stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4):
            if stripped == "$$":
                in_display = not in_display
            continue
        if in_display:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            if level == 1:
                continue  # title: a heading, excluded
            blocks.append(cur)
            if level == 2:
                h2, h3 = m.group(2).strip(), None
            else:
                h3 = m.group(2).strip()
            cur = {"h2": h2, "h3": h3, "text": [], "cells": []}
            continue
        if is_table_row(line):
            if not is_separator_row(line):
                cur["cells"].append(line)
            continue
        cur["text"].append(line)
    blocks.append(cur)
    return blocks


def block_counts(block: dict) -> tuple[int, int]:
    text = words("\n".join(block["text"]))
    cells = sum(words(c) for row in block["cells"] for c in table_cells(row))
    return text, cells


def last_commit(path: Path) -> str:
    """Short hash of the last commit that changed `path` (the counted source version)."""
    try:
        out = subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%h", "--", str(path)],
                             capture_output=True, text=True, check=True).stdout.strip()
        return out or "uncommitted"
    except Exception:
        return "unknown"


def manuscript_report(path: Path) -> tuple[list[str], dict]:
    lines = read(path)
    blocks = sections(lines)
    out: list[str] = []
    stats: dict = {}

    def get(h2, h3=None):
        return [b for b in blocks if b["h2"] == h2 and (h3 is None or b["h3"] == h3)]

    abstract_text = "\n".join(l for b in get("Abstract") for l in b["text"])
    abstract = words(abstract_text)
    abstract_wc = wc_w(abstract_text)
    intro = sum(block_counts(b)[0] for b in get("Introduction"))
    results = [(b["h3"], block_counts(b)[0]) for b in get("Results") if b["h3"]]
    results_lead = sum(block_counts(b)[0] for b in get("Results") if not b["h3"])
    results_total = sum(n for _, n in results) + results_lead
    discussion = sum(block_counts(b)[0] for b in get("Discussion"))
    methods_blocks = [b for b in get("Methods") if b["h3"]]
    methods_lead = sum(block_counts(b)[0] for b in get("Methods") if not b["h3"])
    methods = []
    table_cells_n = 0
    for b in methods_blocks:
        t, c = block_counts(b)
        methods.append((b["h3"], t))
        table_cells_n += c
    methods_total = sum(t for _, t in methods) + methods_lead
    data_av = sum(block_counts(b)[0] for b in get("Data availability"))
    code_av = sum(block_counts(b)[0] for b in get("Code availability"))

    ref_lines = [l for b in get("References") for l in b["text"] if re.match(r"^\s*\d+\.\s", l)]
    ref_words = sum(words(l) for l in ref_lines)
    legend_lines = [l for b in get("Figure legends") for l in b["text"] if l.strip().startswith("**Fig.")]
    fig_numbers = sorted({int(m.group(1)) for l in legend_lines for m in [re.match(r"\*\*Fig\.\s*(\d+)", l.strip())] if m})
    legend_words = sum(words(l) for l in legend_lines)
    per_legend = [(int(re.match(r"\*\*Fig\.\s*(\d+)", l.strip()).group(1)), words(l)) for l in legend_lines]

    irD = intro + results_total + discussion
    main_methods = irD + methods_total
    tables = sorted({int(m.group(1)) for l in lines for m in [re.match(r"^\*\*Table\s+(\d+)", l.strip())] if m})

    out.append("## Main text and Methods (limit: about 5,000 words including Methods)")
    out.append("")
    out.append("| section | words | budget |")
    out.append("|---|---:|---:|")
    out.append(f"| Abstract (not in the 5,000) | {abstract} (`wc -w`: {abstract_wc}) | ≤ 150 |")
    out.append(f"| Introduction | {intro:,} | |")
    for i, (h, n) in enumerate(results, 1):
        out.append(f"| Results {i} — {h} | {n:,} | |")
    out.append(f"| Results, total | {results_total:,} | |")
    out.append(f"| Discussion | {discussion:,} | |")
    out.append(f"| **Introduction + Results + Discussion** | **{irD:,}** | about 3,500 |")
    for h, t in methods:
        note = " (text, including the Table 1 caption)" if h.startswith("Populations") else ""
        out.append(f"| Methods — {h}{note} | {t:,} | |")
    out.append(f"| **Methods, running text** | **{methods_total:,}** | about 1,500 |")
    tbl_total = table_cells_n
    out.append(f"| Table 1 (pre-registration chronology), cell text | {tbl_total:,} | |")
    out.append(f"| **Main text + Methods** | **{main_methods:,}** ({main_methods + tbl_total:,} with Table 1) | about 5,000 |")
    out.append("")
    out.append("## Other parts (outside the 5,000-word count)")
    out.append("")
    out.append("| part | words |")
    out.append("|---|---:|")
    out.append(f"| Data availability | {data_av:,} |")
    out.append(f"| Code availability | {code_av:,} |")
    out.append(f"| References ({len(ref_lines)} entries) | {ref_words:,} |")
    fig_span = f"Figs {fig_numbers[0]}–{fig_numbers[-1]}" if fig_numbers else "none"
    out.append(f"| Figure legends ({fig_span}) | {legend_words:,} |")
    for n, w in per_legend:
        out.append(f"| — Fig. {n} legend | {w:,} |")
    out.append("")
    out.append("## Display items (limit: 10)")
    out.append("")
    n_display = len(fig_numbers) + len(tables)
    tbl_span = ", ".join(f"Table {t}" for t in tables)
    out.append(f"{fig_span.replace('Figs', 'Figures')} and {tbl_span}: {n_display} display items.")
    stats.update(abstract=abstract, abstract_wc=abstract_wc, irD=irD, methods=methods_total,
                 table=tbl_total, main_methods=main_methods, refs=len(ref_lines), figs=len(fig_numbers),
                 tables=len(tables), display=n_display)
    return out, stats


def si_report(path: Path) -> tuple[list[str], dict]:
    lines = read(path)
    blocks = sections(lines)
    groups: dict[str, list[int]] = {}
    order: list[str] = []
    for b in blocks:
        key = b["h2"]
        if key.startswith("The downstream operator") or key == "(front matter)":
            key = "Front matter and contents"
        else:
            key = re.sub(r"^Supplementary Note (\d+)\s*[—-]\s*", r"Note \1 — ", key)
        if key not in groups:
            groups[key] = [0, 0]
            order.append(key)
        t, c = block_counts(b)
        groups[key][0] += t
        groups[key][1] += c
    out = ["| part | running text | table cells |", "|---|---:|---:|"]
    tt = tc = 0
    for k in order:
        t, c = groups[k]
        tt += t
        tc += c
        out.append(f"| {k} | {t:,} | {c:,} |")
    out.append(f"| **Total** | **{tt:,}** | **{tc:,}** |")
    return out, {"si_text": tt, "si_cells": tc}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manuscript", default=str(REPO / "paper" / "MANUSCRIPT.md"))
    ap.add_argument("--si", default=str(REPO / "paper" / "SUPPLEMENTARY_INFORMATION.md"))
    args = ap.parse_args()
    ms_lines, _ = manuscript_report(Path(args.manuscript))
    si_lines, _ = si_report(Path(args.si))
    print(f"<!-- generated by paper/nc_reopen/count_words.py; manuscript last changed in "
          f"{last_commit(Path(args.manuscript))}, SI last changed in {last_commit(Path(args.si))} -->")
    print("\n".join(ms_lines))
    print("")
    print("## Supplementary Information (`paper/SUPPLEMENTARY_INFORMATION.md`; no limit)")
    print("")
    print("\n".join(si_lines))


if __name__ == "__main__":
    main()
