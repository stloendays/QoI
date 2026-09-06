from __future__ import annotations

import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'submission/JCTC_MANUSCRIPT_v0.2.3.md'
CAP=ROOT/'submission/JCTC_FIGURE_CAPTIONS_v0.3.md'
SI=ROOT/'submission/SUPPORTING_INFORMATION_TEXT_JCTC_v0.2.md'
OUT=ROOT/'submission/JCTC_CROSSDOC_LINT_v0.2.md'
man=MAN.read_text(encoding='utf-8')
cap=CAP.read_text(encoding='utf-8')
si=SI.read_text(encoding='utf-8')
checks=[]
def add(n,ok,d): checks.append((n,bool(ok),d))

cap_nums=[int(x) for x in re.findall(r'(?m)^## Figure (\d+)\.',cap)]
add('caption figures 1-6 exactly once',cap_nums==[1,2,3,4,5,6],f'captions={cap_nums}')

first=[]
for m in re.finditer(r'\b(?:Fig\.|Figure)\s*([1-6])',man.split('## References',1)[0]):
    n=int(m.group(1))
    if n not in first:first.append(n)
add('main first figure mentions ordered',first==[1,2,3,4,5,6],f'first={first}')

for n in range(1,7):
    # Allow either a whole-figure citation (Figure 6) or panel citations (Fig. 3a).
    pat=rf'\b(?:Fig\.|Figure)\s*{n}(?:[a-z])?(?!\d)'
    add(f'Figure {n} cited in main',bool(re.search(pat,man)),f'figure={n}')

# Expected panel definitions in captions.
expected_panels={1:[],2:['a','b','c'],3:['a','b','c'],4:['a','b','c','d'],5:['a','b','c','d'],6:[]}
for n,panels in expected_panels.items():
    block=cap.split(f'## Figure {n}.',1)[1]
    if n<6: block=block.split(f'## Figure {n+1}.',1)[0]
    for p in panels:
        add(f'Figure {n}{p} panel captioned',f'**{p},**' in block,f'Figure {n}{p}')

# Final captions should be publication prose, not repository operations.
for token in ['Data:', '.csv', 'will be upgraded', 'when the full table is released', 'formal causal mediation', 'reviewer']:
    add(f'caption clean: {token}',token.lower() not in cap.lower(),token)

# SI structural completeness and cleanliness.
sections=[int(x) for x in re.findall(r'(?m)^## S(\d+)\.',si)]
add('SI sections S1-S12 contiguous',sections==list(range(1,13)),f'S={sections}')
for token in ['reviewer-facing','Remaining SI assembly tasks','If the full per-atom table becomes available before submission']:
    add(f'SI clean: {token}',token.lower() not in si.lower(),token)
add('SI has bibliography','## References' in si,'references')

# Shared headline numbers should agree across main/captions/SI where applicable.
for label,token in [
    ('99.7 direction','99.7%'),
    ('domain share','0.995'),
    ('SZ3 complete case','1.82'),
    ('SPERR complete case','2.00'),
    ('central non-evaluable','41.4%'),
]:
    add(f'{label} in main',token in man,token)
    add(f'{label} in captions',token in cap,token)
    # SI sometimes carries more precision; allow 41.38 in place of 41.4.
    si_ok=token in si or (token=='41.4%' and '41.38%' in si) or (token=='99.7%' and '99.70%' in si)
    add(f'{label} in SI',si_ok,token)

failed=[x for x in checks if not x[1]]
lines=['# JCTC cross-document lint v0.2','',f'Checks: {len(checks)}; passed: {len(checks)-len(failed)}; failed: {len(failed)}.','']
for n,ok,d in checks: lines.append(f"- {'PASS' if ok else 'FAIL'} — **{n}**: {d}")
OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
if failed: raise SystemExit(f'crossdoc lint failures: {[x[0] for x in failed]}')
