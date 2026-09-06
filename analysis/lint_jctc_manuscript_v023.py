from __future__ import annotations

import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'submission/JCTC_MANUSCRIPT_v0.2.3.md'
OUT=ROOT/'submission/JCTC_MANUSCRIPT_v0.2.3_LINT.md'
text=P.read_text(encoding='utf-8')
checks=[]
def add(n,ok,d): checks.append((n,bool(ok),d))

for s in [
    '# 1. Introduction',
    '# 2. Scientific question and benchmark design',
    '# 3. Codec error structure',
    '# 4. QoI / Chemical fidelity',
    '# 5. Mechanism: why \\(L_\\infty\\) fails',
    '# 6. Robustness, failure regimes, and implications',
    '# 7. Conclusion',
]: add(f'section {s}',s in text,s)
add('version','JCTC Article submission draft v0.2.3' in text,'v0.2.3')

# Figure order based on first distinct mention in main text.
mentions=[]
for m in re.finditer(r'\b(?:Fig\.|Figure)\s*([1-6])',text.split('## References',1)[0]):
    n=int(m.group(1))
    if n not in mentions: mentions.append(n)
add('figures first cited 1-6 in numerical order',mentions==[1,2,3,4,5,6],f'first_distinct_mentions={mentions}')

required={
    'Fig1 design':'Figure 1 summarizes the resulting evaluation chain',
    'Fig2a bound utilization':'(Fig. 2a)',
    'Fig2b matching':'(Fig. 2b)',
    'Fig3a fixed vs rederived':'(Fig. 3a)',
    'Fig3b ratio':'(Fig. 3b)',
    'Fig3 long-form narrative':'Figure 3 therefore reports both the directional 99.7% result and stratified multiplicative ratios',
    'Fig4a resolvability':'(Fig. 4a)',
    'Fig4d predictability':'(Fig. 4d)',
    'Fig5a mechanism':'(Fig. 5a)',
    'Fig5d mechanism model':'(Fig. 5d and Fig. 2c)',
    'Fig6 frontier':'(Fig. 6)',
    'ChargeFlow':'10.1021/acs.jctc.6c00585',
    'fixed-vs-resolved':'99.7%',
    'domain dominance':'0.995',
}
for n,t in required.items(): add(n,t in text,t)

for t in [
    '## Limitations',
    'reviewer-facing',
    'we deliberately restrict',
    'a limitation of this work',
    'Figure 2 therefore reports both the directional 99.7% result',
]:
    add(f'clean/renumbered: {t}',t.lower() not in text.lower(),t)

refsec=text.split('## References',1)[1]
refs=[int(x) for x in re.findall(r'(?m)^(\d+)\. ',refsec)]
add('references 1-20 contiguous',refs==list(range(1,21)),f'refs={refs}')
line_dois=[]
for line in refsec.splitlines():
    if 'DOI:' in line: line_dois.append(line.split('DOI:',1)[1].strip().rstrip('.'))
add('DOIs unique',len(line_dois)==len(set(line_dois)),f'n={len(line_dois)}')

failed=[x for x in checks if not x[1]]
lines=['# JCTC manuscript v0.2.3 lint','',f'Checks: {len(checks)}; passed: {len(checks)-len(failed)}; failed: {len(failed)}.','']
for n,ok,d in checks: lines.append(f"- {'PASS' if ok else 'FAIL'} — **{n}**: {d}")
OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
if failed: raise SystemExit(f'v0.2.3 lint failures: {[x[0] for x in failed]}')
