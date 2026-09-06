from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "submission/JCTC_MANUSCRIPT_v0.1.md"
OUT = ROOT / "submission/JCTC_MANUSCRIPT_LINT_v0.1.md"
text = MAN.read_text(encoding="utf-8")

checks: list[tuple[str, bool, str]] = []
def add(name: str, ok: bool, detail: str) -> None:
    checks.append((name, bool(ok), detail))

required = {
    "JCTC title": "Chemical Fidelity beyond Pointwise Error Bounds: Stability and Bader-Domain Migration in Lossy-Compressed Electron Densities",
    "submission marker": "JCTC Article submission draft v0.1",
    "master size": "6,343",
    "fixed-domain result": "99.7%",
    "mechanism result": "0.995",
    "matched SZ3 result": "1.82-fold",
    "matched SPERR result": "2.00-fold",
    "resolvability result": "41.4%",
    "MARGR DOI": "10.1021/acs.jctc.6c01124",
    "MARGR citation number": "[15]",
    "chemistry framing": "field-dependent analysis",
    "data/software heading": "## Data and Software Availability",
    "repository URL": "https://github.com/stloendays/QoI",
}
for name, token in required.items():
    add(name, token in text, f"required token: {token}")

forbidden = {
    "internal branch note": "branch-only draft",
    "pending-file note": "until `mechanism/basin_error_decomposition_per_atom.csv` is committed",
    "generic first claim": "first to show that pointwise",
    "causal mediation overclaim": "formal causal mediation demonstrates",
    "deprecated availability heading": "## Data and code availability",
}
for name, token in forbidden.items():
    add(name, token.lower() not in text.lower(), f"forbidden token: {token}")

# Universal-winner language is acceptable only inside explicit negation.
uw_hits = list(re.finditer(r"one codec is universally superior|universally best codec|universally superior codec", text, flags=re.I))
uw_safe = True
for hit in uw_hits:
    context = text[max(0, hit.start()-30):hit.end()+30].lower()
    if "not" not in context and "does not" not in context:
        uw_safe = False
add("no universal codec winner", uw_safe, f"hits={len(uw_hits)}; all must be explicitly negated")

m = re.search(r"## Abstract\n(.*?)\n## Introduction", text, flags=re.S)
abstract = m.group(1).strip() if m else ""
add("abstract found", bool(abstract), "Abstract section must be present")
add("abstract no numerical citations", re.search(r"\[[0-9]+(?:[-,][0-9]+)*\]", abstract) is None, "avoid reference citations in abstract")
word_count = len(re.findall(r"\b\w+[\w^-]*\b", abstract))
add("abstract concise", word_count <= 250, f"abstract word count={word_count}; internal target <=250")

# Existing direct mechanism claim must remain scoped to the representative set until the per-atom file lands.
add(
    "mechanism scope",
    "representative 12-material mechanism set" in text and "restrict this direct decomposition claim" in text,
    "direct decomposition remains representative-set scoped",
)

# Scientific semantics guardrails.
add("non-evaluable semantics", "NON_EVALUABLE_BADER_UNSTABLE" in text, "unstable reference is not codec failure")
add("protocol-defined floor", "Protocol-A.1 numerical stability floor" in text, "stability floor remains protocol-defined")
add("association not causation", "association rather than a causal codec effect" in text, "codec coefficient remains associative")

# Reference integrity: numbering must be unique and contiguous, and the MARGR paper must be number 15.
ref_match = re.search(r"## References\n(.*)$", text, flags=re.S)
ref_text = ref_match.group(1) if ref_match else ""
ref_numbers = [int(x) for x in re.findall(r"(?m)^(\d+)\.\s", ref_text)]
add("references section found", bool(ref_numbers), "numbered bibliography must be present")
if ref_numbers:
    expected = list(range(1, max(ref_numbers) + 1))
    add("reference numbers unique", len(ref_numbers) == len(set(ref_numbers)), f"numbers={ref_numbers}")
    add("reference numbers contiguous", ref_numbers == expected, f"expected={expected}; observed={ref_numbers}")
else:
    add("reference numbers unique", False, "no references parsed")
    add("reference numbers contiguous", False, "no references parsed")
add(
    "MARGR is reference 15",
    bool(re.search(r"(?m)^15\. .*Bridging Machine Learning and Electron Density Theory", ref_text)),
    "MARGR should follow existing reference 14 rather than duplicate it",
)

# All simple numerical bracket citations in the manuscript must refer to an existing reference number.
body = text.split("## References", 1)[0]
cited_nums: set[int] = set()
for bracket in re.findall(r"\[([0-9,–\- ]+)\]", body):
    # Expand comma-separated integers and simple ranges such as 1–3.
    for part in re.split(r",\s*", bracket):
        part = part.strip()
        mrange = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
        if mrange:
            a, b = map(int, mrange.groups())
            cited_nums.update(range(min(a,b), max(a,b)+1))
        elif part.isdigit():
            cited_nums.add(int(part))
missing_citations = sorted(n for n in cited_nums if n not in set(ref_numbers))
add("all numerical citations resolve", not missing_citations, f"unresolved={missing_citations}")

failed = [x for x in checks if not x[1]]
lines = [
    "# JCTC submission manuscript lint v0.1",
    "",
    f"Checks: {len(checks)}; passed: {len(checks)-len(failed)}; failed: {len(failed)}.",
    "",
]
for name, ok, detail in checks:
    lines.append(f"- {'PASS' if ok else 'FAIL'} — **{name}**: {detail}")
lines += ["", f"Abstract word count: **{word_count}**."]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))

if failed:
    raise SystemExit(f"JCTC lint failures: {[x[0] for x in failed]}")
