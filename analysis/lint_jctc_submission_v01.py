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
    "chemistry framing": "field-dependent analysis",
}
for name, token in required.items():
    add(name, token in text, f"required token: {token}")

forbidden = {
    "internal branch note": "branch-only draft",
    "pending-file note": "until `mechanism/basin_error_decomposition_per_atom.csv` is committed",
    "generic first claim": "first to show that pointwise",
    "causal mediation overclaim": "formal causal mediation demonstrates",
}
for name, token in forbidden.items():
    add(name, token.lower() not in text.lower(), f"forbidden token: {token}")

# Universal-winner wording is acceptable only as an explicit negation/caveat.
winner_hits = [m.start() for m in re.finditer(r"one codec is universally superior", text, flags=re.I)]
winner_ok = True
for pos in winner_hits:
    context = text[max(0, pos-45):pos+60].lower()
    if "not that one codec is universally superior" not in context and "not one codec is universally superior" not in context:
        winner_ok = False
add("no universal codec winner", winner_ok, f"hits={len(winner_hits)}; all must be explicitly negated")

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
