from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.md"
OUT = ROOT / "submission/JCTC_MANUSCRIPT_v0.2_LINT.md"
text = MAN.read_text(encoding="utf-8")

checks: list[tuple[str, bool, str]] = []
def add(name: str, ok: bool, detail: str) -> None:
    checks.append((name, bool(ok), detail))

required_sections = [
    "# 1. Introduction",
    "# 2. Scientific question and benchmark design",
    "# 3. Codec error structure",
    "# 4. QoI / Chemical fidelity",
    "# 5. Mechanism: why \\(L_\\infty\\) fails",
    "# 6. Robustness, failure regimes, and implications",
    "# 7. Conclusion",
]
positions = []
for sec in required_sections:
    pos = text.find(sec)
    positions.append(pos)
    add(f"section present: {sec}", pos >= 0, sec)
add("sections ordered 1-7", all(a < b for a, b in zip(positions, positions[1:])) and all(p >= 0 for p in positions), f"positions={positions}")

forbidden_headings = [
    "## Limitations",
    "# Limitations",
    "## Results",
    "# Results",
    "## Discussion",
    "# Discussion",
    "## Methods",
    "# Methods",
]
for token in forbidden_headings:
    add(f"no old heading: {token}", token not in text, token)

# Reviewer-response/development-history language should not appear in the scientific manuscript.
defensive_tokens = [
    "we acknowledge that",
    "a limitation of this work",
    "we deliberately restrict",
    "we cannot establish",
    "reviewer concern",
    "reviewer-facing",
    "pilot interpretation",
    "falsifies that ranking",
    "branch-only",
    "not a blocker",
    "internal draft",
]
for token in defensive_tokens:
    add(f"non-defensive language: {token}", token.lower() not in text.lower(), token)

required_numbers = {
    "master rows": "6,343",
    "development materials": "254",
    "base rows": "4,627",
    "fixed-vs-resolved": "99.7%",
    "domain dominance": "0.995",
    "ZFP utilization": "0.1575",
    "SZ3 complete-case": "1.82 [1.68, 2.01]",
    "SPERR complete-case": "2.00 [1.79, 2.25]",
    "A1 central non-evaluable": "41.4%",
    "reassignment attenuation SZ3": "0.96",
    "reassignment attenuation SPERR": "0.94",
}
for name, token in required_numbers.items():
    add(name, token in text, token)

# Abstract should remain concise and citation-free.
m = re.search(r"## Abstract\n(.*?)\n# 1\. Introduction", text, flags=re.S)
abstract = m.group(1).strip() if m else ""
wc = len(re.findall(r"\b\w+[\w^-]*\b", abstract))
add("abstract found", bool(abstract), "Abstract before Section 1")
add("abstract <= 250 words", wc <= 250, f"word_count={wc}")
add("abstract has no numbered citations", re.search(r"\[[0-9]+(?:[-,–][0-9]+)*\]", abstract) is None, "no numerical references in abstract")

# Bibliography integrity.
ref_match = re.search(r"## References\n(.*)$", text, flags=re.S)
ref_text = ref_match.group(1) if ref_match else ""
refs = [int(x) for x in re.findall(r"(?m)^(\d+)\.\s", ref_text)]
add("references 1-15 contiguous", refs == list(range(1, 16)), f"refs={refs}")

dois = re.findall(r"DOI:\s*([^\s]+)", ref_text, flags=re.I)
add("no duplicate DOI", len(dois) == len(set(d.lower().rstrip('.') for d in dois)), f"n={len(dois)}")

# Scope should be positive rather than a standalone limitations section.
add("representative mechanism scope stated", "representative mechanism set of 12 materials" in text, "12-material mechanism scope")
add("small strict-slab sample stated positively", "Four slab materials are admitted" in text, "positive small-sample statement")
add("Protocol A1 amplitude-defined", "numerical stability floor at a stated perturbation amplitude" in text, "protocol-defined stability language")

failed = [x for x in checks if not x[1]]
lines = [
    "# JCTC manuscript v0.2 lint",
    "",
    f"Checks: {len(checks)}; passed: {len(checks)-len(failed)}; failed: {len(failed)}.",
    "",
]
for name, ok, detail in checks:
    lines.append(f"- {'PASS' if ok else 'FAIL'} — **{name}**: {detail}")
lines += ["", f"Abstract word count: **{wc}**."]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
if failed:
    raise SystemExit(f"v0.2 lint failures: {[x[0] for x in failed]}")
