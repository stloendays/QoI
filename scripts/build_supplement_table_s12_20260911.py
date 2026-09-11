#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper' / 'SUPPLEMENTARY_TABLE_S12_20260911.md'
SUB = ROOT / 'supplement' / 'S12_matching_sensitivity.csv'


def read_csv(rel):
    with (ROOT / rel).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write_csv(rows):
    with SUB.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator='\n')
        w.writeheader(); w.writerows(rows)


diag = read_csv('analysis/matched_realized_linf_v1/matching_diagnostics.csv')
eff = read_csv('analysis/matched_realized_linf_v1/matched_effects_summary.csv')

pair_label = {
    'zfp_vs_sz3': 'ZFP/SZ3',
    'zfp_vs_sperr': 'ZFP/SPERR',
    'sz3_vs_sperr': 'SZ3/SPERR',
}
calipers = [0.05, 0.10, 0.20, 0.30]

# Normalize diagnostics lookup.
d = {(float(r['caliper_dex']), r['pair']): r for r in diag}
resolved = {(float(r['caliper_dex']), r['pair']): r for r in eff if r['metric'] == 'Bader_error_resolved_e'}
fixed = {(float(r['caliper_dex']), r['pair']): r for r in eff if r['metric'] == 'Bader_error_fixed_e'}
for c in calipers:
    for p in pair_label:
        assert (c,p) in d and (c,p) in resolved and (c,p) in fixed

# Frozen primary assertions.
r = resolved[(0.10,'zfp_vs_sz3')]
assert abs(float(r['effect']) - 0.5574478963397762) < 1e-12
r = resolved[(0.10,'zfp_vs_sperr')]
assert abs(float(r['effect']) - 0.6007474002367663) < 1e-12
r = resolved[(0.10,'sz3_vs_sperr')]
assert abs(float(r['effect']) - 1.0325070260736608) < 1e-12
assert int(d[(0.10,'zfp_vs_sz3')]['n_pairs']) == 457
assert int(d[(0.10,'zfp_vs_sz3')]['n_materials']) == 214
assert int(d[(0.10,'zfp_vs_sperr')]['n_pairs']) == 465
assert int(d[(0.10,'zfp_vs_sperr')]['n_materials']) == 206
assert int(d[(0.10,'sz3_vs_sperr')]['n_pairs']) == 1848
assert int(d[(0.10,'sz3_vs_sperr')]['n_materials']) == 254

machine=[]
for c in calipers:
    for p,label in pair_label.items():
        dg=d[(c,p)]; rr=resolved[(c,p)]; ff=fixed[(c,p)]
        machine.append({
            'caliper_dex':c,'pair':p,'pair_label':label,
            'n_pairs':int(dg['n_pairs']),'n_materials':int(dg['n_materials']),
            'median_linf_ratio_larger_over_smaller':float(dg['median_linf_ratio_larger_over_smaller']),
            'q90_linf_ratio_larger_over_smaller':float(dg['q90_linf_ratio_larger_over_smaller']),
            'resolved_bader_ratio':float(rr['effect']),'resolved_ci_low':float(rr['ci_low']),'resolved_ci_high':float(rr['ci_high']),
            'resolved_n_usable_pairs':int(rr['n_usable_pairs']),'resolved_n_usable_materials':int(rr['n_usable_materials']),
            'fixed_bader_ratio':float(ff['effect']),'fixed_ci_low':float(ff['ci_low']),'fixed_ci_high':float(ff['ci_high']),
        })
write_csv(machine)

lines=['# Supplementary Table S12 | Realized-L∞ matching sensitivity across pre-specified calipers','',
       'Generated 2026-09-11 directly from `analysis/matched_realized_linf_v1/matching_diagnostics.csv` and `matched_effects_summary.csv`. The primary analysis uses a 0.10-dex caliper; 0.05, 0.20 and 0.30 dex are pre-specified sensitivity analyses.','',
       '## S12a. Matched support and realized-L∞ balance','',
       '| Caliper (dex) | Codec pair | Matched row pairs | Materials represented | Median larger/smaller realized L∞ | Q90 larger/smaller realized L∞ |',
       '|---:|---|---:|---:|---:|---:|']
for r in machine:
    lines.append(f"| {r['caliper_dex']:.2f} | {r['pair_label']} | {r['n_pairs']:,} | {r['n_materials']} | {r['median_linf_ratio_larger_over_smaller']:.3f} | {r['q90_linf_ratio_larger_over_smaller']:.3f} |")
lines += ['', '## S12b. Re-derived Bader-error effect after matching', '',
          '| Caliper (dex) | Codec-error ratio | Usable matched pairs | Usable materials | Effect | 95% material-bootstrap CI |',
          '|---:|---|---:|---:|---:|---:|']
for r in machine:
    lines.append(f"| {r['caliper_dex']:.2f} | {r['pair_label']} | {r['resolved_n_usable_pairs']:,} | {r['resolved_n_usable_materials']} | {r['resolved_bader_ratio']:.3f} | {r['resolved_ci_low']:.3f}–{r['resolved_ci_high']:.3f} |")
lines += ['', '## S12c. Fixed-basin diagnostic after the same matching', '',
          '| Caliper (dex) | Codec-error ratio | Effect | 95% material-bootstrap CI |',
          '|---:|---|---:|---:|']
for r in machine:
    lines.append(f"| {r['caliper_dex']:.2f} | {r['pair_label']} | {r['fixed_bader_ratio']:.3f} | {r['fixed_ci_low']:.3f}–{r['fixed_ci_high']:.3f} |")
lines += ['',
          '**Primary 0.10-dex result.** Re-derived Bader-error ratios are ZFP/SZ3 = **0.557** (95% CI 0.525–0.598), ZFP/SPERR = **0.601** (0.534–0.662), and SZ3/SPERR = **1.033** (0.976–1.072). The direction of the ZFP comparisons remains below one across all pre-specified calipers, whereas SZ3/SPERR remains close to one.', '',
          '**Interpretation boundary.** Matching controls realized maximum perturbation, not the full geometry of the codec error field. A residual codec effect after matching is consistent with an error-structure contribution but does not identify a unique spatial invariant. Fixed-basin effects are diagnostic because fixed domains change the downstream operator.', '',
          '**Machine-readable submission source:** `supplement/S12_matching_sensitivity.csv`.']
OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Wrote {OUT.relative_to(ROOT)} and {SUB.relative_to(ROOT)}')
