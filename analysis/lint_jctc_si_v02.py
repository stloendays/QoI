from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "submission/SUPPORTING_INFORMATION_TEXT_JCTC_v0.2.md"
OUT = ROOT / "submission/JCTC_SI_v0.2_LINT.md"
text = P.read_text(encoding="utf-8")

checks=[]
def add(n, ok, d): checks.append((n,bool(ok),d))

required={
    "version":"JCTC Supporting Information v0.2",
    "Materials Project":"Materials Project [1]",
    "AFLOW":"AFLOW [2]",
    "NOMAD":"NOMAD [3]",
    "BaderKit":"BaderKit [4]",
    "ZFP":"ZFP [5]",
    "SZ3":"SZ3 [6]",
    "SPERR":"SPERR [7]",
    "master rows":"6,343",
    "fixed-vs-resolved":"99.70%",
    "A1 central":"41.38%",
    "complete-case SZ3":"1.82× [1.68, 2.01]",
    "complete-case SPERR":"2.00× [1.79, 2.25]",
    "mechanism":"0.995",
    "mechanism diagnostic":"mechanism-consistency diagnostic",
    "references":"## References",
}
for n,t in required.items(): add(n,t in text,t)

forbidden=[
    "reviewer-facing",
    "Remaining SI assembly tasks",
    "If the full per-atom table becomes available before submission",
    "not formal causal mediation",
    "This direct decomposition claim remains restricted",
    "final SI should record",
]
for t in forbidden: add(f"clean prose: {t}", t.lower() not in text.lower(), t)

refsec=text.split("## References",1)[1]
refs=[int(x) for x in re.findall(r"(?m)^(\d+)\. ",refsec)]
add("SI references 1-7 contiguous",refs==list(range(1,8)),f"refs={refs}")
body=text.split("## References",1)[0]
cited=set(int(x) for x in re.findall(r"\[(\d+)\]",body))
add("SI citations resolve",cited.issubset(set(refs)),f"cited={sorted(cited)}")

dois=[]
for line in refsec.splitlines():
    if "DOI:" in line: dois.append(line.split("DOI:",1)[1].strip().rstrip("."))
add("SI DOI unique",len(dois)==len(set(dois)),f"n={len(dois)}")

failed=[x for x in checks if not x[1]]
lines=["# JCTC Supporting Information v0.2 lint","",f"Checks: {len(checks)}; passed: {len(checks)-len(failed)}; failed: {len(failed)}.",""]
for n,ok,d in checks: lines.append(f"- {'PASS' if ok else 'FAIL'} — **{n}**: {d}")
OUT.write_text("\n".join(lines)+"\n",encoding="utf-8")
print("\n".join(lines))
if failed: raise SystemExit(f"SI v0.2 lint failures: {[x[0] for x in failed]}")
