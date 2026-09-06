from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.2.md"
OUT = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.2_LINT.md"
text = P.read_text(encoding="utf-8")

checks: list[tuple[str, bool, str]] = []
def add(name: str, ok: bool, detail: str) -> None:
    checks.append((name, bool(ok), detail))

required = {
    "version": "JCTC Article submission draft v0.2.2",
    "lossless electron-density context": "volumetric trajectories, including electron-density grids",
    "Brehm citation in Introduction": "lossless representation is used [14]",
    "JCTC neighboring-work framing": "growing JCTC literature on the downstream use of approximate electron densities",
    "MARGR citation": "downstream evaluation [15]",
    "ChargeFlow citation": "Bader partitioning and electrostatic-potential analysis across a broad external benchmark [20]",
    "ChargeFlow DOI": "10.1021/acs.jctc.6c00585",
    "ChargeFlow pages": "8481–8492",
    "BaderKit citation": "`baderkit` 0.10.2 [16]",
    "Materials Project citation": "Materials Project [17]",
    "AFLOW citation": "AFLOW bulk systems [18]",
    "NOMAD citation": "NOMAD two-dimensional or vacuum-containing systems [19]",
    "fixed-vs-resolved": "99.7%",
    "domain dominance": "0.995",
    "complete-case SZ3": "1.82 [1.68, 2.01]",
    "complete-case SPERR": "2.00 [1.79, 2.25]",
}
for name, token in required.items():
    add(name, token in text, token)

forbidden = [
    "## Limitations",
    "# Limitations",
    "we acknowledge that",
    "a limitation of this work",
    "we deliberately restrict",
    "reviewer concern",
    "reviewer-facing",
]
for token in forbidden:
    add(f"non-defensive: {token}", token.lower() not in text.lower(), token)

ref_section = text.split("## References", 1)[1]
refs = [int(x) for x in re.findall(r"(?m)^(\d+)\. ", ref_section)]
add("references 1-20 contiguous", refs == list(range(1, 21)), f"refs={refs}")

dois = re.findall(r"DOI:\s*([^\s.]+(?:\.[^\s.]+)*)\.?", ref_section)
# robust duplicate check using literal DOI strings from lines
line_dois = []
for line in ref_section.splitlines():
    if "DOI:" in line:
        line_dois.append(line.split("DOI:", 1)[1].strip().rstrip("."))
add("no duplicate DOI", len(line_dois) == len(set(line_dois)), f"n={len(line_dois)}")

cited = set()
for m in re.findall(r"\[(\d+(?:\s*[–-]\s*\d+)?(?:\s*,\s*\d+)*)\]", text.split("## References",1)[0]):
    for part in re.split(r"\s*,\s*", m):
        if re.search(r"[–-]", part):
            a,b = map(int, re.split(r"\s*[–-]\s*", part))
            cited.update(range(a,b+1))
        else:
            cited.add(int(part))
missing = sorted(cited - set(refs))
add("all numerical citations resolve", not missing, f"missing={missing}")
add("ChargeFlow is cited in body", 20 in cited, f"cited={sorted(cited)}")
add("Brehm is cited in body", 14 in cited, f"cited={sorted(cited)}")

failed = [x for x in checks if not x[1]]
lines = ["# JCTC manuscript v0.2.2 lint", "", f"Checks: {len(checks)}; passed: {len(checks)-len(failed)}; failed: {len(failed)}.", ""]
for name, ok, detail in checks:
    lines.append(f"- {'PASS' if ok else 'FAIL'} — **{name}**: {detail}")
OUT.write_text("\n".join(lines)+"\n", encoding="utf-8")
print("\n".join(lines))
if failed:
    raise SystemExit(f"v0.2.2 lint failures: {[x[0] for x in failed]}")
