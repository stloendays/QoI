#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper' / 'SUPPLEMENTARY_TABLE_S14_20260911.md'
CSV_OUT = ROOT / 'supplement' / 'S14_failure_registry_summary.csv'


def read_csv(rel):
    with (ROOT / rel).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

rows = read_csv('failure_registry.csv')
assert rows

# Machine-readable aggregation of the explicit failure registry.
counts = Counter((r['category'], r['corpus'], r['domain'], r['codec'] or 'NA') for r in rows)
agg=[]
for (category,corpus,domain,codec), n in sorted(counts.items()):
    agg.append({'category':category,'corpus':corpus,'domain':domain,'codec':codec,'n_rows':n})
with CSV_OUT.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(agg[0].keys()),lineterminator='\n'); w.writeheader(); w.writerows(agg)

cat=Counter(r['category'] for r in rows)
corpus_cat=Counter((r['corpus'],r['category']) for r in rows)
solver=[r for r in rows if r['category']=='bader_solver_failure']
solver_codec=Counter((r['corpus'],r['codec']) for r in solver)

# Parse the canonical retracted-claim block rather than duplicating it by hand.
claim_text=(ROOT/'paper'/'CLAIM_EVIDENCE_MATRIX.md').read_text(encoding='utf-8')
start=claim_text.index('## Retracted numbers — must not be cited')
end=claim_text.index('## External baselines: closed',start)
block=claim_text[start:end]
retracted=[]
for line in block.splitlines():
    if line.startswith('| ') and not line.startswith('|---') and 'Retracted | Why' not in line:
        parts=[p.strip() for p in line.strip('|').split('|')]
        if len(parts)>=2:
            retracted.append((parts[0],parts[1]))
assert len(retracted)>=8

lines=['# Supplementary Table S14 | Failure taxonomy, exclusions and negative-result audit','',
       'Generated 2026-09-11 from the canonical `failure_registry.csv` and the retracted/closed-track records in `paper/CLAIM_EVIDENCE_MATRIX.md`. This table preserves the distinction between scientific non-evaluability, downstream solver failure, infrastructure mismatch and superseded exploratory claims.','',
       '## S14a. Failure and exclusion semantics used in the submission','',
       '| State / category | Meaning | Scored as codec pass/fail? | Canonical source |',
       '|---|---|---|---|',
       '| `NON_EVALUABLE_BADER_UNSTABLE` | Reference Bader QoI fails Protocol A.1 eligibility at the requested tolerance | **No** — neither pass nor fail | `stability/eligibility_summary_A1.csv`; Figure 3/S4 |',
       '| `bader_solver_failure` | Downstream Bader analysis did not return a valid row-level result | **No automatic codec attribution**; retained in audit | `failure_registry.csv` |',
       '| `reproduction_mismatch` | Reproduction/platform check failed despite reconstructed scientific field remaining consistent | **No**; infrastructure exclusion from the affected formal analysis | Hartree reproduction-gate records |',
       '| `basin_relabelling_symmetry_equivalent` | Apparent large atom-indexed charge change is a permutation among symmetry-equivalent basins | **Non-evaluable for position-indexed charge**, separately flagged | `failure_registry.csv` |',
       '| eligible + not certified | Reference QoI is numerically eligible but compressed reconstruction exceeds the requested Bader contract | **Yes: genuine failure** | `benchmark/master_benchmark_full.csv` |',
       '| eligible + certified | Reference QoI is eligible and the reconstruction satisfies the contract | **Yes: certified success** | `benchmark/master_benchmark_full.csv` |','',
       '## S14b. Explicit `failure_registry.csv` counts','',
       '| Registry category | Row records |', '|---|---:|']
for k,n in sorted(cat.items()): lines.append(f'| `{k}` | {n} |')
lines += ['', '### Bader-solver failures by corpus and codec', '', '| Corpus | Codec | Row failures |', '|---|---|---:|']
for (corpus,codec),n in sorted(solver_codec.items()): lines.append(f'| {corpus} | {codec or "NA"} | {n} |')
lines += ['', 'These counts describe explicit row-level failure records, not material-level non-evaluable counts. Protocol A.1 non-evaluability is stored in the stability/benchmark tables and must not be reconstructed from `failure_registry.csv`.', '',
          '## S14c. Superseded exploratory statements retained for provenance but prohibited from the submission','',
          '| Superseded statement | Why it is not submission-valid |', '|---|---|']
for a,b in retracted:
    lines.append(f'| {a} | {b} |')
lines += ['',
          '## S14d. Closed baseline / algorithm tracks', '',
          '- **External baselines:** BQB and den2bin remain related-work context rather than headline fair benchmarks because their task definitions and/or error-control contracts are not comparable to the frozen density-field L∞ benchmark. The measured denominator audit is retained in `results/external_baselines/BASELINE_REPORT.md`.',
          '- **Algorithm track:** closed under the corrected re-derived-Bader metric. No proposed codec modification survived with sufficient evidence to become a contribution; the paper therefore presents a measurement/certification framework rather than a new compressor.', '',
          '**Interpretation boundary.** A transparent SI should record failures and discarded exploratory claims, but these categories must not be pooled into a single “failure rate”. In particular, non-evaluable scientific targets are not codec failures, solver failures are not silently imputed as codec failures, and superseded pilot numbers are not reused in the manuscript.', '',
          '**Machine-readable registry summary:** `supplement/S14_failure_registry_summary.csv`.']
OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Wrote {OUT.relative_to(ROOT)} and {CSV_OUT.relative_to(ROOT)}')
print('categories',dict(cat))
print('solver failures',len(solver))
