from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "paper/MANUSCRIPT_CHATGPT_v0.3.1.md"
OUT = ROOT / "paper_data_v03/manuscript_lint_v031.md"

text = MAN.read_text(encoding="utf-8")
checks = []

def check(name, ok, detail):
    checks.append((name, bool(ok), detail))

# Required scientific scope/numbers.
required = {
    "version marker": "Integrated manuscript draft v0.3.1",
    "master size": "6,343",
    "development materials": "254",
    "base ladder": "4,627",
    "fixed-v-resolved direction": "99.7%",
    "representative mechanism dominance": "0.995",
    "ZFP utilization": "0.1575",
    "complete-case SZ3/ZFP": "1.82 [1.68, 2.01]",
    "complete-case SPERR/ZFP": "2.00 [1.79, 2.25]",
    "A1 1e-3 non-evaluable": "41.4%",
    "A1 1e-4 non-evaluable": "79.9%",
    "negative-control SZ3 electron model": "2.34 to 2.58",
    "negative-control reassignment p": "p=5.25×10^-28",
    "symmetry pathology id": "aflow-Al8Cu4U1_ICSD_601801",
    "NON_EVALUABLE semantics": "NON_EVALUABLE_BADER_UNSTABLE",
    "SZ3 DOI": "10.1109/TBDATA.2022.3201176",
    "SPERR DOI": "10.1109/IPDPS54959.2023.00104",
    "predictability caveat": "do not establish that Bader resolvability is fundamentally unpredictable",
}
for name, token in required.items():
    check(name, token in text, f"required token: {token}")

# Provisional/positive-overclaim text must be gone.
forbidden = {
    "placeholder reference": "reference to be replaced",
    "software placeholder": "[software/method reference",
    "generic first-to-show claim": "first to show that pointwise",
    "intrinsic Bader floor claim": "intrinsic Bader floor",
}
for name, token in forbidden.items():
    check(name, token.lower() not in text.lower(), f"forbidden token: {token}")

# Scope guardrails: the manuscript must explicitly narrow representative-set direct mechanism.
check(
    "representative-set scope explicit",
    "representative mechanism set" in text and "restrict this direct decomposition claim" in text,
    "direct decomposition must not be generalized to all 254 materials",
)
check(
    "attenuation is non-causal",
    "not as formal causal mediation" in text or "not as a causal mediation estimate" in text,
    "reassignment is a post-compression variable",
)
check(
    "probe floor is protocol-defined",
    "Protocol-A.1 numerical stability floor at the stated perturbation amplitude" in text,
    "avoid intrinsic-floor wording",
)
check(
    "strict slab caveat",
    "Only four slab materials are admitted" in text or "only four slab materials are admitted" in text,
    "1e-4 slab frontier must be descriptive",
)

# Detect common dangerous prose patterns. These are human-review flags only because a phrase
# can appear safely inside an explicit negation (e.g. 'not universally superior').
danger_patterns = [
    (r"\bcausal codec effect\b", "causal codec effect"),
    (r"\buniversally (?:best|superior)\b", "universal codec winner"),
    (r"\bdomain migration dominates (?:all|every)\b", "full-corpus mechanism overclaim"),
]
for pattern, label in danger_patterns:
    hits = [m.group(0) for m in re.finditer(pattern, text, flags=re.IGNORECASE)]
    check(f"danger phrase review: {label}", len(hits) == 0, f"hits={hits}")

# Basic reference ordering check for the opening [1-3] names.
ref1 = re.search(r"^1\. .*ZFP.*$", text, flags=re.MULTILINE | re.IGNORECASE)
ref2 = re.search(r"^2\. .*SZ3.*$", text, flags=re.MULTILINE | re.IGNORECASE)
ref3 = re.search(r"^3\. .*SPERR.*$", text, flags=re.MULTILINE | re.IGNORECASE)
check("reference 1 maps to ZFP", ref1 is not None, "opening [1–3] mapping")
check("reference 2 maps to SZ3", ref2 is not None, "opening [1–3] mapping")
check("reference 3 maps to SPERR", ref3 is not None, "opening [1–3] mapping")

# Summarize.
failed = [c for c in checks if not c[1]]
lines = [
    "# Manuscript v0.3.1 scientific-claim lint",
    "",
    f"Checks: {len(checks)}; passed: {len(checks)-len(failed)}; flagged/failed: {len(failed)}.",
    "",
]
for name, ok, detail in checks:
    lines.append(f"- {'PASS' if ok else 'FLAG'} — **{name}**: {detail}")

lines += [
    "",
    "## Interpretation",
    "",
    "This lint is a guardrail, not a substitute for editorial review. A flagged danger phrase can be harmless when used inside an explicit negation; such cases should be inspected manually rather than automatically deleted.",
]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))

# Fail only on hard requirements/provisional text/reference mapping, not on danger-phrase review labels.
hard_fail_names = set(required) | set(forbidden) | {
    "representative-set scope explicit",
    "attenuation is non-causal",
    "probe floor is protocol-defined",
    "strict slab caveat",
    "reference 1 maps to ZFP",
    "reference 2 maps to SZ3",
    "reference 3 maps to SPERR",
}
hard_failed = [c for c in checks if (c[0] in hard_fail_names and not c[1])]
if hard_failed:
    raise SystemExit(f"Hard manuscript lint failures: {[c[0] for c in hard_failed]}")
