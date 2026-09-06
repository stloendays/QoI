from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SI = ROOT / "submission/SUPPORTING_INFORMATION_TEXT_JCTC_v0.1.md"
OUT = ROOT / "submission/JCTC_SI_LINT_v0.1.md"
text = SI.read_text(encoding="utf-8")

checks: list[tuple[str, bool, str]] = []
def add(name: str, ok: bool, detail: str) -> None:
    checks.append((name, bool(ok), detail))

required = {
    "base ladder denominator": "4,627",
    "fixed greater fraction": "99.70%",
    "pooled fixed ratio": "52.8×",
    "1e-6 denominator sensitivity": "52.6×",
    "material-balanced ratio": "59.5× [50.8, 70.3]",
    "probe correction magnitude": "8,700",
    "A1 1e-4 non-evaluable": "79.9%",
    "A1 1e-3 non-evaluable": "41.4%",
    "A1 1e-2 non-evaluable": "9.7%",
    "seed decisions 1e-4": "35",
    "amplitude sensitivity": "0.76 decades",
    "ZFP utilization": "0.157521",
    "failure affected materials": "20",
    "complete-case materials": "234",
    "matched SZ3": "1.82× [1.68, 2.01]",
    "matched SPERR": "2.00× [1.79, 2.25]",
    "base attenuation SZ3": "2.34×",
    "reassigned SZ3": "0.96×",
    "base attenuation SPERR": "2.08×",
    "reassigned SPERR": "0.94×",
    "reassignment p": "5.78\\times10^{-28}",
    "joint reassignment p": "5.25\\times10^{-28}",
    "domain share": "0.995",
    "mechanism closure": "2.22\\times10^{-16}",
    "strict slab n": "n=4",
    "protocol-defined language": "Protocol-A.1 numerical stability floor at the stated perturbation amplitude",
    "non-evaluable semantics": "neither a codec pass nor a codec failure",
    "non-causal language": "not formal causal mediation",
}
for name, token in required.items():
    add(name, token in text, f"required token: {token}")

forbidden = {
    "intrinsic floor": "intrinsic material noise floor",
    "all-material direct mechanism": "all 254 materials are directly decomposed",
    "per-atom availability overclaim": "the full per-atom table is available",
    "universal codec winner": "universally superior codec",
}
for name, token in forbidden.items():
    add(name, token.lower() not in text.lower(), f"forbidden token: {token}")

# Per-atom section must be explicitly conditional while the file is unavailable.
add(
    "per-atom conditional scope",
    "If the full per-atom table becomes available before submission" in text,
    "SI must not imply the unavailable table is already part of the evidence package",
)

# Strictest slab row must be described as descriptive, not a population ranking.
add(
    "strict slab descriptive",
    "Only four slab materials are admitted" in text and "descriptive" in text,
    "strict 1e-4 slab frontier must remain descriptive",
)

failed = [x for x in checks if not x[1]]
lines = [
    "# JCTC Supporting Information lint v0.1",
    "",
    f"Checks: {len(checks)}; passed: {len(checks)-len(failed)}; failed: {len(failed)}.",
    "",
]
for name, ok, detail in checks:
    lines.append(f"- {'PASS' if ok else 'FAIL'} — **{name}**: {detail}")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))

if failed:
    raise SystemExit(f"JCTC SI lint failures: {[x[0] for x in failed]}")
