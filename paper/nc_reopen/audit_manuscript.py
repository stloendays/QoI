"""Mechanical audit of the Nature Communications manuscript source.

Checks (FAIL items; requested for the 2026-10-07 audit record):
  C1 citations   - every <sup> citation parses; reference numbers are first cited in increasing order (each new number
                   is the previous maximum + 1); the reference list is numbered 1..N; every reference is cited and every
                   cited number exists; SI pointers of the form "main-text ref. N" exist.
  C2 cross-refs  - every cited main figure has a legend and every cited panel exists in that legend; legends are
                   numbered 1..K and every figure is cited in the main text; main figures (and tables) are first cited
                   in order; every cited table has a caption; every cited Supplementary Note / Fig. / Table exists in
                   the SI.
  C3 paths       - every repository path mentioned in the manuscript, the SI and the SI's source table
                   (paper/nc_reopen/SOURCE_FILES.md) exists in the tree of HEAD; a bare file name must match at least
                   one tracked file.
  C4 characters  - no TAB or other control character (Unicode category Cc, except the LF / CRLF line ending) in any
                   .md file under paper/.
  C5 math        - `$$` display delimiters are balanced in each file, and every paragraph or table row has an even
                   number of unescaped inline `$` delimiters (code spans excluded).
Additional checks (FAIL items):
  A1 commits     - every commit hash cited in the manuscript, the SI or SOURCE_FILES.md resolves to a commit that is an
                   ancestor of HEAD (i.e. is on this branch).
  A2 source map  - each single-file row of SOURCE_FILES.md lists the commit that last changed that file, as the table
                   states.
Warnings (reported, not counted as failures unless --final):
  W1 legend panels that the main text never cites (the figure is not cited as a whole either);
  W2 Supplementary Notes / Figs first cited out of order in the main text, or never cited from it;
  W3 SI contents entries whose title differs from the note heading;
  W4 inline math with whitespace just inside a `$` delimiter;
  W5 invisible format characters (Unicode category Cf) in .md files under paper/.
--final (submission QA) also fails on any warning and on placeholders ("[placeholder", "[CITATION NEEDED") and a
missing author block.

Usage (standard library + git on PATH):
    python paper/nc_reopen/audit_manuscript.py [--final] [--out paper/nc_reopen/AUDIT_<date>.md]
Exit status 1 when any FAIL item is found.
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MS = REPO / "paper" / "MANUSCRIPT.md"
SI = REPO / "paper" / "SUPPLEMENTARY_INFORMATION.md"
SRC = REPO / "paper" / "nc_reopen" / "SOURCE_FILES.md"

DASHES = "\u2013\u2014-"
FILE_EXT = ("md", "json", "csv", "py", "txt", "yml", "yaml", "pdf", "docx", "png", "svg", "tsv", "npz", "npy", "sh",
            "ps1", "toml", "cfg", "ini", "html", "tex", "bib", "jsonl")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True).stdout


def rel(p: Path) -> str:
    return p.relative_to(REPO).as_posix()


def read_lines(p: Path) -> list[str]:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")


class Report:
    def __init__(self) -> None:
        self.items: dict[str, list[str]] = {}
        self.titles: dict[str, str] = {}
        self.kind: dict[str, str] = {}
        self.info: dict[str, list[str]] = {}

    def check(self, key: str, title: str, kind: str) -> None:
        self.items[key] = []
        self.info[key] = []
        self.titles[key] = title
        self.kind[key] = kind

    def add(self, key: str, msg: str) -> None:
        self.items[key].append(msg)

    def note(self, key: str, msg: str) -> None:
        self.info[key].append(msg)


# ----------------------------------------------------------------------------------------------- manuscript parsing
def split_manuscript(lines: list[str]):
    """Return (body, references, legends) as lists of (line_no, text); body excludes References and Figure legends."""
    body, refs, legends = [], [], []
    section = "body"
    for i, line in enumerate(lines, 1):
        if re.match(r"^##\s+References\s*$", line):
            section = "refs"
            continue
        if re.match(r"^##\s+Figure legends\s*$", line):
            section = "legends"
            continue
        if section == "refs" and re.match(r"^##\s", line):
            section = "body"
        {"body": body, "refs": refs, "legends": legends}[section].append((i, line))
    return body, refs, legends


def expand_numbers(spec: str) -> list[int] | None:
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            return None
        m = re.fullmatch(rf"(\d+)\s*[{DASHES}]\s*(\d+)", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b <= a:
                return None
            out.extend(range(a, b + 1))
        elif part.isdigit():
            out.append(int(part))
        else:
            return None
    return out


def expand_panels(spec: str) -> list[str]:
    out: list[str] = []
    for part in re.split(r",\s*", spec):
        m = re.fullmatch(rf"([a-z])[{DASHES}]([a-z])", part)
        if m:
            out.extend(chr(c) for c in range(ord(m.group(1)), ord(m.group(2)) + 1))
        elif re.fullmatch(r"[a-z]", part):
            out.append(part)
    return out


FIG_RE = re.compile(rf"(?<!Supplementary )\bFig(?:ure)?s?\.?\s+(\d+(?:[a-z](?:\s*[,{DASHES}]\s*[a-z](?![a-z]))*)?"
                    rf"(?:\s*(?:[,{DASHES}]|and)\s*\d+(?:[a-z](?:\s*[,{DASHES}]\s*[a-z](?![a-z]))*)?)*)")
TABLE_RE = re.compile(r"(?<!Supplementary )\bTables?\s+(\d+)")
SUPP_RE = re.compile(rf"\bSupplementary\s+(Note|Fig\.|Figure|Table)s?\s+(\d+(?:\s*(?:[,{DASHES}]|and)\s*\d+)*)")


def fig_mentions(text: str) -> list[tuple[int, list[str]]]:
    """[(figure number, [panels]) ...] in order of appearance."""
    out = []
    for m in FIG_RE.finditer(text):
        for item in re.split(rf"\s*(?:,|and)\s*(?=\d)|\s*[{DASHES}]\s*(?=\d)", m.group(1)):
            mm = re.fullmatch(r"(\d+)([a-z].*)?", item.strip())
            if not mm:
                continue
            out.append((int(mm.group(1)), expand_panels(mm.group(2)) if mm.group(2) else []))
        # numeric ranges "Figs 2-4"
        r = re.fullmatch(rf"(\d+)\s*[{DASHES}]\s*(\d+)", m.group(1).strip())
        if r:
            out = out[:-2] + [(n, []) for n in range(int(r.group(1)), int(r.group(2)) + 1)]
    return out


def supp_mentions(text: str) -> list[tuple[str, int]]:
    out = []
    for m in SUPP_RE.finditer(text):
        kind = {"Note": "Note", "Fig.": "Fig.", "Figure": "Fig.", "Table": "Table"}[m.group(1)]
        nums = expand_numbers(re.sub(r"\band\b", ",", m.group(2))) or []
        out.extend((kind, n) for n in nums)
    return out


# ----------------------------------------------------------------------------------------------- checks
def check_citations(rep: Report, ms_lines: list[str], si_lines: list[str]) -> None:
    rep.check("C1", "Citations: first-cited order, every reference cited, numbering", "core")
    body, refs, legends = split_manuscript(ms_lines)
    ref_nums = []
    for i, line in refs:
        m = re.match(r"^\s*(\d+)\.\s", line)
        if m:
            ref_nums.append((i, int(m.group(1))))
    n_refs = len(ref_nums)
    for k, (i, n) in enumerate(ref_nums, 1):
        if n != k:
            rep.add("C1", f"MANUSCRIPT.md:{i}: reference list entry numbered {n}, expected {k}")
    defined = {n for _, n in ref_nums}
    cited: set[int] = set()
    order: list[int] = []
    for i, line in body + legends:
        for m in re.finditer(r"<sup>(.*?)</sup>", line):
            nums = expand_numbers(m.group(1))
            if nums is None:
                rep.add("C1", f"MANUSCRIPT.md:{i}: superscript '{m.group(1)}' is not a citation list")
                continue
            for n in nums:
                if n not in cited:
                    expected = len(order) + 1
                    if n != expected:
                        rep.add("C1", f"MANUSCRIPT.md:{i}: reference {n} is first cited in position {expected} "
                                      f"(expected reference {expected})")
                    cited.add(n)
                    order.append(n)
                if n not in defined:
                    rep.add("C1", f"MANUSCRIPT.md:{i}: cited reference {n} is not in the reference list")
    for n in sorted(defined - cited):
        rep.add("C1", f"MANUSCRIPT.md: reference {n} is never cited")
    for i, line in enumerate(si_lines, 1):
        for m in re.finditer(r"main-text refs?\.\s*([\d,\s\u2013-]+\d)", line):
            for n in expand_numbers(m.group(1)) or []:
                if n not in defined:
                    rep.add("C1", f"SUPPLEMENTARY_INFORMATION.md:{i}: 'main-text ref. {n}' does not exist")
    rep.note("C1", f"{n_refs} references; {len(cited)} distinct numbers cited; first-citation sequence "
                   f"{order[0] if order else '-'}..{order[-1] if order else '-'}")


def legend_table(legends: list[tuple[int, str]]):
    figs: dict[int, set[str]] = {}
    for i, line in legends:
        m = re.match(r"^\*\*Fig\.\s*(\d+)\s*\|", line.strip())
        if m:
            n = int(m.group(1))
            figs[n] = set(re.findall(r"\*\*([a-z])\*\*", line))
    return figs


def si_items(si_lines: list[str]):
    notes, figs, tables, titles = {}, set(), set(), {}
    for i, line in enumerate(si_lines, 1):
        m = re.match(rf"^##\s+Supplementary Note\s+(\d+)\s*[{DASHES}]?\s*(.*)$", line)
        if m:
            notes[int(m.group(1))] = i
            titles[int(m.group(1))] = m.group(2).strip()
        m = re.match(r"^\*\*Supplementary (?:Fig\.|Figure)\s*(\d+)\s*\|", line.strip())
        if m:
            figs.add(int(m.group(1)))
        m = re.match(r"^\*\*Supplementary Table\s*(\d+)\s*\|", line.strip())
        if m:
            tables.add(int(m.group(1)))
    return notes, figs, tables, titles


def check_crossrefs(rep: Report, ms_lines: list[str], si_lines: list[str]) -> None:
    rep.check("C2", "Figure, table and SI references exist; main figures first cited in order", "core")
    rep.check("W1", "Legend panels never cited in the main text", "warn")
    rep.check("W2", "Supplementary items: main-text citation order and coverage", "warn")
    rep.check("W3", "SI contents entries vs note headings", "warn")
    body, refs, legends = split_manuscript(ms_lines)
    figs = legend_table(legends)
    nums = sorted(figs)
    if nums != list(range(1, len(nums) + 1)):
        rep.add("C2", f"MANUSCRIPT.md: figure legends are numbered {nums}, expected 1..{len(nums)}")
    first, whole, panels_cited = [], set(), {}
    for i, line in body:
        if line.startswith("#"):
            continue
        for n, panels in fig_mentions(line):
            if n not in figs:
                rep.add("C2", f"MANUSCRIPT.md:{i}: Fig. {n} is cited but has no legend")
                continue
            for p in panels:
                if p not in figs[n]:
                    rep.add("C2", f"MANUSCRIPT.md:{i}: Fig. {n}{p} is cited but the Fig. {n} legend has no panel {p}")
            if not panels:
                whole.add(n)
            panels_cited.setdefault(n, set()).update(panels)
            if n not in first:
                expected = len(first) + 1
                if n != expected:
                    rep.add("C2", f"MANUSCRIPT.md:{i}: Fig. {n} is first cited in position {expected} "
                                  f"(expected Fig. {expected})")
                first.append(n)
    for n in nums:
        if n not in first:
            rep.add("C2", f"MANUSCRIPT.md: Fig. {n} has a legend but is never cited in the main text")
        elif n not in whole:
            for p in sorted(figs[n] - panels_cited.get(n, set())):
                rep.add("W1", f"Fig. {n}{p} (legend panel) is not cited in the main text")
    for i, line in legends:
        for n, panels in fig_mentions(re.sub(r"^\*\*Fig\.\s*\d+\s*\|", "", line.strip())):
            if n not in figs:
                rep.add("C2", f"MANUSCRIPT.md:{i}: legend cites Fig. {n}, which has no legend")
    # tables
    captions = {int(m.group(1)): i for i, line in body
                for m in [re.match(r"^\*\*Table\s+(\d+)\s*\|", line.strip())] if m}
    t_first = []
    for i, line in body:
        if line.strip().startswith("**Table") or line.startswith("#"):
            continue
        for m in TABLE_RE.finditer(line):
            n = int(m.group(1))
            if n not in captions:
                rep.add("C2", f"MANUSCRIPT.md:{i}: Table {n} is cited but has no caption")
            if n not in t_first:
                expected = len(t_first) + 1
                if n != expected:
                    rep.add("C2", f"MANUSCRIPT.md:{i}: Table {n} is first cited in position {expected} "
                                  f"(expected Table {expected})")
                t_first.append(n)
    for n in sorted(captions):
        if n not in t_first:
            rep.add("C2", f"MANUSCRIPT.md:{captions[n]}: Table {n} has a caption but is never cited")
    # supplementary items
    notes, sfigs, stables, titles = si_items(si_lines)
    have = {"Note": set(notes), "Fig.": sfigs, "Table": stables}
    ms_first: dict[str, list[int]] = {"Note": [], "Fig.": [], "Table": []}
    for src, lines in (("MANUSCRIPT.md", [l for _, l in body + legends]), ("SUPPLEMENTARY_INFORMATION.md", si_lines)):
        for i, line in enumerate(lines, 1):
            for kind, n in supp_mentions(line):
                if n not in have[kind]:
                    where = f"{src}:{i}" if src.startswith("SUPP") else src
                    rep.add("C2", f"{where}: Supplementary {kind} {n} is cited but does not exist in the SI")
                if src == "MANUSCRIPT.md" and n not in ms_first[kind]:
                    ms_first[kind].append(n)
        if src.startswith("SUPP"):
            for i, line in enumerate(lines, 1):
                if re.search(r"main-text Methods", line) and not any(re.match(r"^##\s+Methods\s*$", l) for l in ms_lines):
                    rep.add("C2", f"{src}:{i}: 'main-text Methods' but the manuscript has no Methods section")
    for kind, seq in ms_first.items():
        if seq and seq != sorted(seq):
            rep.add("W2", f"Supplementary {kind}s first cited in the main text in the order {seq}")
        missing = sorted(have[kind] - set(seq))
        if missing:
            rep.add("W2", f"Supplementary {kind} {', '.join(map(str, missing))} not cited from the main text")
    # SI contents list vs headings
    for i, line in enumerate(si_lines, 1):
        m = re.match(r"^-\s+Supplementary Note\s+(\d+)\.\s+(.*)$", line)
        if m:
            n, t = int(m.group(1)), m.group(2).strip().rstrip(".")
            if n not in notes:
                rep.add("C2", f"SUPPLEMENTARY_INFORMATION.md:{i}: contents lists Supplementary Note {n}, which does not exist")
            elif titles.get(n, "").rstrip(".") != t:
                rep.add("W3", f"SUPPLEMENTARY_INFORMATION.md:{i}: contents title of Note {n} '{t}' differs from heading "
                              f"'{titles.get(n, '')}' (line {notes[n]})")
    rep.note("C2", f"main figures with legends: {nums}; first-cited order {first}; tables {sorted(captions)}; "
                   f"SI notes {sorted(notes)}, SI figures {sorted(sfigs)}, SI tables {sorted(stables)}")


PATH_TOKEN = re.compile(r"`([^`\s]+)`")
BARE_FILE = re.compile(rf"(?<![\w/.`-])([A-Za-z0-9_][\w.-]*\.(?:{'|'.join(FILE_EXT)}))(?![\w/-])")


def expand_braces(tok: str) -> list[str]:
    m = re.search(r"\{([^{}]+)\}", tok)
    if not m:
        return [tok]
    return [x for alt in m.group(1).split(",") for x in expand_braces(tok[:m.start()] + alt + tok[m.end():])]


def check_paths(rep: Report, files: list[Path]) -> None:
    rep.check("C3", "Repository paths mentioned exist on this branch (HEAD tree)", "core")
    tree = set(git("ls-tree", "-r", "--name-only", "HEAD").splitlines())
    dirs = {"/".join(p.split("/")[:k]) for p in tree for k in range(1, p.count("/") + 1)}
    basenames: dict[str, int] = {}
    for p in tree:
        b = p.rsplit("/", 1)[-1]
        basenames[b] = basenames.get(b, 0) + 1
    checked = 0
    for f in files:
        for i, line in enumerate(read_lines(f), 1):
            toks = set()
            for m in PATH_TOKEN.finditer(line):
                tok = m.group(1).strip().rstrip(".,;:")
                if "://" in tok:
                    continue
                if "/" in tok and re.fullmatch(r"[\w.*{},/-]+", tok) and not tok.startswith("-"):
                    toks.add(tok)
                elif re.fullmatch(rf"[\w.-]+\.(?:{'|'.join(FILE_EXT)})", tok):
                    toks.add(tok)
            plain = re.sub(r"`[^`]*`", " ", line)
            plain = re.sub(r"https?://\S+", " ", plain)
            for m in BARE_FILE.finditer(plain):
                toks.add(m.group(1))
            for tok in sorted(toks):
                for t in expand_braces(tok):
                    checked += 1
                    t = t.strip("/")
                    if "/" in t:
                        ok = (t in tree or t in dirs or
                              ("*" in t and any(fnmatch.fnmatch(p, t) for p in tree)))
                        if not ok:
                            rep.add("C3", f"{rel(f)}:{i}: path `{t}` does not exist on this branch")
                    else:
                        if t not in basenames:
                            rep.add("C3", f"{rel(f)}:{i}: file name `{t}` matches no tracked file")
    rep.note("C3", f"{checked} path mentions checked in {', '.join(rel(f) for f in files)}")


def check_commits(rep: Report, files: list[Path]) -> None:
    rep.check("A1", "Cited commit hashes are on this branch (ancestors of HEAD)", "additional")
    rep.check("A2", "SOURCE_FILES.md lists the commit that last changed each file", "additional")
    hashes: dict[str, str] = {}
    for f in files:
        for i, line in enumerate(read_lines(f), 1):
            for m in re.finditer(r"`([0-9a-f]{7,40})`", line):
                if re.search(r"[a-f]", m.group(1)) and re.search(r"\d", m.group(1)):
                    hashes.setdefault(m.group(1), f"{rel(f)}:{i}")
    for h, where in sorted(hashes.items(), key=lambda kv: kv[1]):
        r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--verify", "--quiet", f"{h}^{{commit}}"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            rep.add("A1", f"{where}: commit `{h}` does not resolve in this repository")
            continue
        a = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", h, "HEAD"])
        if a.returncode != 0:
            rep.add("A1", f"{where}: commit `{h}` exists but is not an ancestor of HEAD")
    rep.note("A1", f"{len(hashes)} distinct commit hashes checked")
    for i, line in enumerate(read_lines(SRC), 1):
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if len(cells) < 3:
            continue
        paths = re.findall(r"`([^`]+/[^`]+)`", cells[1])
        commit = re.findall(r"`([0-9a-f]{7,40})`", cells[2])
        if len(paths) != 1 or len(commit) != 1:
            continue
        last = git("log", "-1", "--format=%h", "--abbrev=7", "--", paths[0]).strip()
        if last and not (last.startswith(commit[0]) or commit[0].startswith(last)):
            rep.add("A2", f"{rel(SRC)}:{i}: `{paths[0]}` listed at `{commit[0]}`, last changed in `{last}`")


def check_characters(rep: Report, skip: Path | None = None) -> None:
    """`skip` is the report file being regenerated (--out); its old content is not part of the audited source."""
    rep.check("C4", "No TAB or other control characters in .md files under paper/", "core")
    rep.check("W5", "Invisible format characters (Cf) in .md files under paper/", "warn")
    md_files = sorted(p for p in (REPO / "paper").rglob("*.md")
                      if p.is_file() and (skip is None or p.resolve() != skip.resolve()))
    for p in md_files:
        raw = p.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            rep.add("C4", f"{rel(p)}: not valid UTF-8 ({e})")
            continue
        for i, line in enumerate(text.split("\n"), 1):
            body = line[:-1] if line.endswith("\r") else line
            for col, ch in enumerate(body, 1):
                cat = unicodedata.category(ch)
                if cat == "Cc":
                    name = {"\t": "TAB", "\r": "CR"}.get(ch, f"U+{ord(ch):04X}")
                    ctx = "".join({"\t": "\\t", "\r": "\\r"}.get(c, f"\\x{ord(c):02x}")
                                  if unicodedata.category(c) == "Cc" else c
                                  for c in body[max(0, col - 15):col + 15])
                    rep.add("C4", f"{rel(p)}:{i}:{col}: {name} in '...{ctx}...'")
                elif cat == "Cf" and not (i == 1 and col == 1 and ch == "\ufeff"):
                    rep.add("W5", f"{rel(p)}:{i}:{col}: U+{ord(ch):04X} {unicodedata.name(ch, '?')}")
    rep.note("C4", f"{len(md_files)} .md files scanned under paper/")


def check_math(rep: Report, files: list[Path]) -> None:
    rep.check("C5", "Matched $ math delimiters", "core")
    rep.check("W4", "Inline math with whitespace inside a $ delimiter", "warn")
    spans = 0
    for f in files:
        lines = read_lines(f)
        display_open = None
        para: list[tuple[int, str]] = []

        def flush(chunk: list[tuple[int, str]]) -> None:
            nonlocal spans
            if not chunk:
                return
            text = " ".join(t for _, t in chunk)
            dollars = [m.start() for m in re.finditer(r"(?<!\\)\$", text)]
            if len(dollars) % 2:
                rep.add("C5", f"{rel(f)}:{chunk[0][0]}: odd number of inline $ delimiters ({len(dollars)})")
                return
            for a, b in zip(dollars[0::2], dollars[1::2]):
                spans += 1
                inner = text[a + 1:b]
                if not inner.strip():
                    rep.add("C5", f"{rel(f)}:{chunk[0][0]}: empty inline math '$$' inside running text")
                elif inner != inner.strip():
                    rep.add("W4", f"{rel(f)}:{chunk[0][0]}: whitespace inside delimiter in '${inner}$'")

        for i, line in enumerate(lines, 1):
            s = re.sub(r"`[^`]*`", "", line)
            st = s.strip()
            if st == "$$":
                flush(para)
                para = []
                display_open = None if display_open else i
                continue
            if display_open:
                if "$$" in st:
                    rep.add("C5", f"{rel(f)}:{i}: '$$' inside an open display block (opened line {display_open})")
                continue
            if st.startswith("$$") and st.endswith("$$") and len(st) > 4:
                flush(para)
                para = []
                continue
            if "$$" in st:
                rep.add("C5", f"{rel(f)}:{i}: '$$' inside a line of running text")
            if not st or st.startswith("|") or st.startswith("#"):
                flush(para)
                para = []
                if st.startswith("|") or st.startswith("#"):
                    flush([(i, s)])
                continue
            para.append((i, s))
        flush(para)
        if display_open:
            rep.add("C5", f"{rel(f)}:{display_open}: display math opened with '$$' is never closed")
    rep.note("C5", f"{spans} inline math spans checked in {', '.join(rel(f) for f in files)}")


def check_final(rep: Report, ms_lines: list[str]) -> None:
    rep.check("F1", "Submission readiness (--final): placeholders and author block", "final")
    for f in (MS, SI):
        for i, line in enumerate(read_lines(f), 1):
            for pat in (r"\[placeholder", r"\[CITATION NEEDED", r"\bTODO\b", r"\bTBD\b"):
                if re.search(pat, line, re.I):
                    rep.add("F1", f"{rel(f)}:{i}: placeholder matching '{pat}'")
    head = "\n".join(ms_lines[:6])
    if not re.search(r"(?i)affiliation|\bauthors?\b|ORCID|\d\s*Department", head):
        rep.add("F1", "MANUSCRIPT.md: no author list / affiliations between the title and the Abstract")


# ----------------------------------------------------------------------------------------------- driver
def main() -> int:
    ap = argparse.ArgumentParser(description="Mechanical audit of the NC manuscript source.")
    ap.add_argument("--final", action="store_true", help="submission QA: warnings and placeholders fail")
    ap.add_argument("--out", help="also write the Markdown report to this file")
    args = ap.parse_args()

    ms_lines, si_lines = read_lines(MS), read_lines(SI)
    rep = Report()
    check_citations(rep, ms_lines, si_lines)
    check_crossrefs(rep, ms_lines, si_lines)
    check_paths(rep, [MS, SI, SRC])
    check_characters(rep, Path(args.out) if args.out else None)
    check_math(rep, [MS, SI])
    check_commits(rep, [MS, SI, SRC])
    if args.final:
        check_final(rep, ms_lines)

    head = git("rev-parse", "--short", "HEAD").strip()
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    ms_c = git("log", "-1", "--format=%h", "--", rel(MS)).strip()
    si_c = git("log", "-1", "--format=%h", "--", rel(SI)).strip()
    dirty = git("status", "--porcelain", "--", rel(MS), rel(SI), rel(SRC)).strip()

    failing = {"core", "additional", "final"} | ({"warn"} if args.final else set())
    n_fail = sum(len(v) for k, v in rep.items.items() if rep.kind[k] in failing)
    n_warn = sum(len(v) for k, v in rep.items.items() if rep.kind[k] not in failing)
    out = [f"# Manuscript audit — {'final (submission QA)' if args.final else 'standard'}",
           "",
           f"Generated by `paper/nc_reopen/audit_manuscript.py{' --final' if args.final else ''}` on branch `{branch}` "
           f"at `{head}`. Audited source: `paper/MANUSCRIPT.md` (last changed in `{ms_c}`), "
           f"`paper/SUPPLEMENTARY_INFORMATION.md` (last changed in `{si_c}`), `paper/nc_reopen/SOURCE_FILES.md`; "
           f"character scan over every `.md` file under `paper/`."
           + (" Working-tree changes to the audited files were present." if dirty else ""),
           "",
           f"**Result: {n_fail} failure(s), {n_warn} warning(s).**",
           "",
           "| check | kind | result |",
           "|---|---|---|"]
    for k in rep.items:
        n = len(rep.items[k])
        res = "pass" if n == 0 else (f"{n} warning(s)" if rep.kind[k] == "warn" and not args.final else f"FAIL ({n})")
        out.append(f"| {k} {rep.titles[k]} | {rep.kind[k]} | {res} |")
    out.append("")
    for k in rep.items:
        out.append(f"## {k} — {rep.titles[k]}")
        out.append("")
        for msg in rep.info[k]:
            out.append(f"- scope: {msg}")
        if rep.items[k]:
            label = "WARN" if rep.kind[k] == "warn" and not args.final else "FAIL"
            for msg in rep.items[k]:
                out.append(f"- {label}: {msg}")
        else:
            out.append("- pass")
        out.append("")
    text = "\n".join(out).rstrip() + "\n"
    sys.stdout.reconfigure(encoding="utf-8")
    print(text, end="")
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
