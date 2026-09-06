from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.1.md"
OUT = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.1_LINT.md"
text = MAN.read_text(encoding="utf-8")
checks = []

def add(name, ok, detail):
    checks.append((name, bool(ok), detail))

for token in [
    "# 1. Introduction",
    "# 2. Scientific question and benchmark design",
    "# 3. Codec error structure",
    "# 4. QoI / Chemical fidelity",
    "# 5. Mechanism: why \\(L_\\infty\\) fails",
    "# 6. Robustness, failure regimes, and implications",
    "# 7. Conclusion",
]:
    add(f"section {token}", token in text, token)

for token in ["## Limitations", "## Results", "## Discussion", "## Methods"]:
    add(f"no old heading {token}", token not in text, token)

required = {
    "version": "JCTC Article submission draft v0.2.1",
    "BaderKit citation": "`baderkit` 0.10.2 [16]",
    "Materials Project citation": "Materials Project [17]",
    "AFLOW citation": "AFLOW bulk systems [18]",
    "NOMAD citation": "NOMAD two-dimensional or vacuum-containing systems [19]",
    "PVLDB year": "*Proc. VLDB Endow.* **2022**, *16* (4), 697–710",
    "BaderKit DOI": "10.21105/joss.09943",
    "Materials Project DOI": "10.1038/s41563-025-02272-0",
    "AFLOW DOI": "10.1016/j.commatsci.2012.02.002",
    "NOMAD DOI": "10.1088/2515-7639/ab13bb",
}
for name, token in required.items():
    add(name, token in text, token)

ref_text = text.split("## References", 1)[1]
nums = [int(x) for x in re.findall(r"(?m)^(\d+)\.\s", ref_text)]
add("references 1-19 contiguous", nums == list(range(1, 20)), f"refs={nums}")
dois = re.findall(r"DOI:\s*([^\s.]+(?:\.[^\s.]+)*)", ref_text)
add("no duplicate DOI", len(dois) == len(set(dois)), f"n={len(dois)}")

body = text.split("## References", 1)[0]
cited = set()
for b in re.findall(r"\[([0-9,–\- ]+)\]", body):
    for part in re.split(r",\s*", b):
        part = part.strip()
        m = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
        if m:
            a, z = map(int, m.groups())
            cited.update(range(min(a, z), max(a, z) + 1))
        elif part.isdigit():
            cited.add(int(part))
missing = sorted(n for n in cited if n not in set(nums))
add("all numerical citations resolve", not missing, f"missing={missing}")

failed = [x for x in checks if not x[1]]
lines = ["# JCTC manuscript v0.2.1 lint", "", f"Checks: {len(checks)}; passed: {len(checks)-len(failed)}; failed: {len(failed)}.", ""]
for name, ok, detail in checks:
    lines.append(f"- {'PASS' if ok else 'FAIL'} — **{name}**: {detail}")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
if failed:
    raise SystemExit([x[0] for x in failed])
