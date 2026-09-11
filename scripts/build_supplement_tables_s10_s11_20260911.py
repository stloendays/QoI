#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUP = ROOT / 'supplement'
SUP.mkdir(exist_ok=True)
MECH = ROOT / 'mechanism' / 'independent_bader_20260908'


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        raise RuntimeError(f'No rows for {path}')
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def q(vals, p):
    vals = sorted(vals)
    if not vals:
        return math.nan
    pos = (len(vals)-1)*p
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    return vals[lo] + (vals[hi]-vals[lo])*(pos-lo)


def med(vals):
    vals = [v for v in vals if math.isfinite(v)]
    return statistics.median(vals) if vals else math.nan


def pct(x):
    return f'{100*x:.1f}%'


def sci(x):
    return f'{x:.3g}'

# -----------------------------------------------------------------------------
# S10 — representative main-mechanism decomposition.
# -----------------------------------------------------------------------------
main = read_csv(ROOT / 'mechanism' / 'basin_error_decomposition_summary.csv')
for r in main:
    r['relative_tolerance'] = float(r['relative_tolerance'])
    r['total_at_atom'] = abs(float(r['dq_total_at_that_atom']))
    r['integrand_at_atom'] = abs(float(r['dq_integrand_at_that_atom']))
    r['domain_at_atom'] = abs(float(r['dq_domain_at_that_atom']))
    r['reassign'] = float(r['frac_voxels_reassigned'])
    denom = r['domain_at_atom'] + r['integrand_at_atom']
    r['domain_abs_share'] = r['domain_at_atom']/denom if denom > 0 else math.nan
    r['total_over_integrand'] = r['total_at_atom']/r['integrand_at_atom'] if r['integrand_at_atom'] > 0 else math.nan
    r['domain_dominates'] = r['domain_at_atom'] > r['integrand_at_atom']

assert len({r['material_id'] for r in main}) >= 6
assert len(main) >= 50

s10 = []
for tau in (1e-4, 1e-3, 1e-2):
    for codec in ('zfp','sz3','sperr'):
        rr = [r for r in main if r['codec'].lower() == codec and abs(r['relative_tolerance']-tau) < 1e-15]
        if not rr: continue
        amps = [r['total_over_integrand'] for r in rr if math.isfinite(r['total_over_integrand'])]
        shares = [r['domain_abs_share'] for r in rr if math.isfinite(r['domain_abs_share'])]
        s10.append({
            'relative_tolerance': tau,
            'codec': codec.upper(),
            'n_cases': len(rr),
            'median_total_over_integrand': med(amps),
            'p10_total_over_integrand': q(amps,.10),
            'p90_total_over_integrand': q(amps,.90),
            'median_domain_abs_share': med(shares),
            'fraction_domain_dominates': sum(r['domain_dominates'] for r in rr)/len(rr),
            'median_reassigned_voxel_fraction': med([r['reassign'] for r in rr]),
        })
write_csv(SUP / 'S10_bader_decomposition_summary.csv', s10)

all_amp = [r['total_over_integrand'] for r in main if math.isfinite(r['total_over_integrand'])]
all_share = [r['domain_abs_share'] for r in main if math.isfinite(r['domain_abs_share'])]
all_dom = sum(r['domain_dominates'] for r in main)/len(main)

# -----------------------------------------------------------------------------
# S11 — independent implementation study directly from 1,560 outcomes.
# -----------------------------------------------------------------------------
panel = json.loads((MECH / 'panel.json').read_text(encoding='utf-8'))
panel_map = {r['material_id']: r for r in panel}
outcomes = []
for p in sorted((MECH / 'outcomes').glob('*.jsonl')):
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip(): outcomes.append(json.loads(line))
assert len(outcomes) == 1560, len(outcomes)
lookup = {(r['material_id'], r['variant'], r['solver']): r for r in outcomes}
failures = [r for r in outcomes if r.get('status') != 'SUCCESS']
assert len(failures) == 2

# Baseline compatibility: compare original per-atom charges to BaderKit on-grid.
baseline = []
for mid, meta in panel_map.items():
    if meta.get('sentinel'): continue
    ref = lookup[(mid,'original','baderkit_ongrid')]
    for solver in ('henkelman_ongrid','henkelman_neargrid'):
        other = lookup[(mid,'original',solver)]
        if ref['status']=='SUCCESS' and other['status']=='SUCCESS':
            n = min(len(ref['atom_charges']), len(other['atom_charges']))
            diff = max(abs(ref['atom_charges'][i]-other['atom_charges'][i]) for i in range(n)) if n else math.nan
            baseline.append({'material':mid,'solver':solver,'baseline_max_abs_charge_diff_e':diff})
base_lookup = {(r['material'],r['solver']):r['baseline_max_abs_charge_diff_e'] for r in baseline}

# Paired codec responses. Preserve all successful pairs; mark print-resolution and baseline compatibility.
codec_re = re.compile(r'^(zfp|sz3|sperr)_(0\.0001|0\.001)$')
pairs = []
for mid, meta in panel_map.items():
    if meta.get('sentinel'): continue
    for codec in ('zfp','sz3','sperr'):
        for rel in ('0.0001','0.001'):
            variant = f'{codec}_{rel}'
            a = lookup.get((mid,variant,'baderkit_ongrid'))
            if not a or a.get('status') != 'SUCCESS': continue
            for solver in ('henkelman_ongrid','henkelman_neargrid'):
                b = lookup.get((mid,variant,solver))
                if not b or b.get('status') != 'SUCCESS': continue
                x = float(a['max_charge_error_e']); y = float(b['max_charge_error_e'])
                ratio = y/x if x > 0 else math.nan
                pairs.append({
                    'material': mid,
                    'domain': meta['domain'],
                    'role': meta['selection_role'],
                    'codec': codec.upper(),
                    'relative_tolerance': float(rel),
                    'comparison_solver': solver,
                    'baderkit_error_e': x,
                    'comparison_error_e': y,
                    'comparison_over_baderkit': ratio,
                    'above_2e-6_print_region': min(x,y) > 2e-6,
                    'baseline_max_abs_charge_diff_e': base_lookup[(mid,solver)],
                    'baseline_compatible_1e-3': base_lookup[(mid,solver)] <= 1e-3,
                })
write_csv(SUP / 'S11_cross_implementation_pairs.csv', pairs)

# Summaries under transparent filters: all pairs above print-resolution, and stricter baseline-compatible subset.
impl_summary = []
for solver in ('henkelman_ongrid','henkelman_neargrid'):
    for filter_name, pred in (
        ('above_print_resolution', lambda r: r['above_2e-6_print_region']),
        ('above_print_and_baseline_compatible', lambda r: r['above_2e-6_print_region'] and r['baseline_compatible_1e-3']),
    ):
        rr = [r for r in pairs if r['comparison_solver']==solver and pred(r) and math.isfinite(r['comparison_over_baderkit'])]
        vals = [r['comparison_over_baderkit'] for r in rr]
        impl_summary.append({
            'metric':'codec_response_ratio',
            'solver':solver,
            'filter':filter_name,
            'n':len(vals),
            'median':med(vals),
            'q25':q(vals,.25),
            'q75':q(vals,.75),
        })

# Noise-floor agreement and eligibility concordance from compact stability table.
stab = read_csv(MECH / 'stability_comparison.csv')
stab = [r for r in stab if str(r['sentinel']).lower() == 'false']
stab_map = {(r['material'],r['solver']):r for r in stab}
for solver in ('henkelman_ongrid','henkelman_neargrid'):
    ratios=[]; diffs=[]
    concord={1e-4:0,1e-3:0,1e-2:0}; nmat=0
    for mid, meta in panel_map.items():
        if meta.get('sentinel'): continue
        a=stab_map[(mid,'baderkit_ongrid')]; b=stab_map[(mid,solver)]
        x=float(a['probe_response_max_e']); y=float(b['probe_response_max_e'])
        diffs.append(abs(y-x))
        if x>0 and y>0: ratios.append(y/x)
        for tau,col in ((1e-4,'eligible_0.0001'),(1e-3,'eligible_0.001'),(1e-2,'eligible_0.01')):
            concord[tau] += (str(a[col]).lower()==str(b[col]).lower())
        nmat += 1
    impl_summary.append({'metric':'noise_floor_ratio','solver':solver,'filter':'all_12_representatives','n':len(ratios),'median':med(ratios),'q25':q(ratios,.25),'q75':q(ratios,.75)})
    for tau in (1e-4,1e-3,1e-2):
        impl_summary.append({'metric':f'eligibility_concordance_{tau:g}','solver':solver,'filter':'all_12_representatives','n':nmat,'median':concord[tau]/nmat,'q25':'','q75':''})
write_csv(SUP / 'S11_independent_implementation_summary.csv', impl_summary)

# Strict 1e-4 codec ordering by solver: median per-material error ratios relative to ZFP.
order_rows=[]
for solver in ('baderkit_ongrid','henkelman_ongrid','henkelman_neargrid'):
    for numerator in ('sz3','sperr'):
        vals=[]
        for mid,meta in panel_map.items():
            if meta.get('sentinel'): continue
            z=lookup.get((mid,'zfp_0.0001',solver)); n=lookup.get((mid,f'{numerator}_0.0001',solver))
            if not z or not n or z.get('status')!='SUCCESS' or n.get('status')!='SUCCESS': continue
            ze=float(z['max_charge_error_e']); ne=float(n['max_charge_error_e'])
            if ze>0 and ne>0: vals.append(ne/ze)
        order_rows.append({'solver':solver,'ratio':f'{numerator.upper()}/ZFP','n':len(vals),'median_ratio':med(vals),'q25':q(vals,.25),'q75':q(vals,.75)})
write_csv(SUP / 'S11_codec_order_1e4.csv', order_rows)

# Exact independent decomposition by kind; use bounded absolute contribution share.
dec = read_csv(MECH / 'mechanism_domain_decomposition.csv')
dec = [r for r in dec if str(r['sentinel']).lower() == 'false']
dec_summary=[]
for kind in sorted({r['kind'] for r in dec}):
    rr=[r for r in dec if r['kind']==kind]
    shares=[]; dom_gt=[]; closure=[]
    for r in rr:
        d=float(r['domain_max_e']); i=float(r['integrand_max_e'])
        if d+i>0: shares.append(d/(d+i))
        dom_gt.append(d>i)
        closure.append(float(r['closure_max_e']))
    dec_summary.append({'kind':kind,'n':len(rr),'median_domain_abs_share':med(shares),'q25':q(shares,.25),'q75':q(shares,.75),'fraction_domain_gt_integrand':sum(dom_gt)/len(dom_gt),'max_closure_e':max(closure)})
write_csv(SUP / 'S11_independent_domain_summary.csv', dec_summary)

# Spatial organization controls.
sp = read_csv(MECH / 'mechanism_spatial_pairs.csv')
sp = [r for r in sp if str(r['sentinel']).lower() == 'false' and r['ratio'] not in ('','None','nan','NaN')]
sp_summary=[]
for solver in ('baderkit_ongrid','henkelman_ongrid','henkelman_neargrid'):
    for control in ('global','shift','stratified'):
        rr=[r for r in sp if r['solver']==solver and r['control']==control]
        logs=[math.log2(float(r['ratio'])) for r in rr if float(r['ratio'])>0]
        sp_summary.append({'solver':solver,'control':control,'n':len(logs),'median_log2_control_over_codec':med(logs),'q25':q(logs,.25),'q75':q(logs,.75),'fraction_increased':sum(float(r['difference_e'])>0 for r in rr)/len(rr)})
write_csv(SUP / 'S11_spatial_control_summary.csv', sp_summary)

# -----------------------------------------------------------------------------
# Submission-facing Markdown.
# -----------------------------------------------------------------------------
lines=[]
lines.append('# Supplementary Tables S10–S11')
lines.append('')
lines.append('Generated 2026-09-11 from the frozen Bader mechanism corpus and the independent Bader implementation study. These are robustness/mechanism tables; they do not alter the frozen benchmark or the central Figure 3 classification.')
lines.append('')
lines.append('## Supplementary Table S10 | Representative Bader decomposition confirms a dominant domain-migration channel')
lines.append('')
lines.append('| Relative codec tolerance | Codec | Cases | Median total/integrand at max-error atom | P10–P90 | Median bounded domain share | Domain term > integrand | Median reassigned voxel fraction |')
lines.append('|---:|---|---:|---:|---:|---:|---:|---:|')
for r in s10:
    lines.append(f"| {r['relative_tolerance']:.0e} | {r['codec']} | {r['n_cases']} | {r['median_total_over_integrand']:.2f}× | {r['p10_total_over_integrand']:.2f}–{r['p90_total_over_integrand']:.2f}× | {r['median_domain_abs_share']:.3f} | {pct(r['fraction_domain_dominates'])} | {r['median_reassigned_voxel_fraction']:.3e} |")
lines.append('')
lines.append(f"Across the full representative matrix (n={len(main)} material–codec–tolerance cases), the median total/integrand amplification at the atom of maximum total deviation is **{med(all_amp):.2f}×**, the median bounded absolute domain share is **{med(all_share):.3f}**, and the domain term exceeds the integrand term in **{pct(all_dom)}** of cases. Because signed cancellation can make |domain|/|total| exceed 1, Table S10 reports the bounded diagnostic |domain|/(|domain|+|integrand|) and the directly interpretable total/integrand amplification separately.")
lines.append('')
lines.append('**Sources:** `mechanism/basin_error_decomposition_summary.csv`; extended per-atom values in `mechanism/basin_error_decomposition_per_atom.csv`. The stability-floor column in the historical mechanism table is not used for current Protocol A.1 claims.')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## Supplementary Table S11 | Independent Bader implementations preserve the mechanism and codec-response ordering')
lines.append('')
lines.append('### S11a. Study completeness and solver failures')
lines.append('')
lines.append('| Quantity | Result |')
lines.append('|---|---:|')
lines.append('| Expected outcome rows | 1,560 |')
lines.append('| Completed outcome rows | 1,560 |')
lines.append('| BaderKit on-grid solver failures | 2 |')
lines.append('| Henkelman on-grid solver failures | 0 |')
lines.append('| Henkelman near-grid solver failures | 0 |')
lines.append('| Representative systems in aggregate | 12 development systems |')
lines.append('| Separate probe-failure sentinel | 1 (`mp-1007755`; excluded from aggregates) |')
lines.append('')
lines.append('### S11b. Paired codec-response ratios relative to BaderKit on-grid')
lines.append('')
lines.append('| Comparison solver | Filter | n paired codec responses | Median comparison/BaderKit | IQR |')
lines.append('|---|---|---:|---:|---:|')
for r in impl_summary:
    if r['metric']!='codec_response_ratio': continue
    lines.append(f"| {r['solver']} | {r['filter'].replace('_',' ')} | {r['n']} | {float(r['median']):.3f} | {float(r['q25']):.3f}–{float(r['q75']):.3f} |")
lines.append('')
lines.append('The baseline-compatible filter requires the unperturbed comparison-solver and BaderKit atomic charges to agree within 1e-3 e and both codec responses to exceed the 2e-6 e Henkelman print-resolution region. The unfiltered paired points remain available in `supplement/S11_cross_implementation_pairs.csv`.')
lines.append('')
lines.append('### S11c. Relative 1e-4 codec-response ordering by implementation')
lines.append('')
lines.append('| Solver | Error ratio | n materials | Median ratio | IQR |')
lines.append('|---|---|---:|---:|---:|')
for r in order_rows:
    lines.append(f"| {r['solver']} | {r['ratio']} | {r['n']} | {r['median_ratio']:.2f}× | {r['q25']:.2f}–{r['q75']:.2f}× |")
lines.append('')
lines.append('### S11d. Exact BaderKit decomposition by perturbation kind')
lines.append('')
lines.append('| Perturbation kind | n | Median bounded domain share | IQR | Domain > integrand | Max closure residual (e) |')
lines.append('|---|---:|---:|---:|---:|---:|')
for r in dec_summary:
    lines.append(f"| {r['kind']} | {r['n']} | {r['median_domain_abs_share']:.4f} | {r['q25']:.4f}–{r['q75']:.4f} | {pct(r['fraction_domain_gt_integrand'])} | {float(r['max_closure_e']):.1e} |")
lines.append('')
lines.append('### S11e. Spatial reorganization controls')
lines.append('')
lines.append('| Solver | Control | n pairs | Median log2(control/codec) | IQR | Fraction increased |')
lines.append('|---|---|---:|---:|---:|---:|')
for r in sp_summary:
    lines.append(f"| {r['solver']} | {r['control']} | {r['n']} | {r['median_log2_control_over_codec']:.2f} | {r['q25']:.2f}–{r['q75']:.2f} | {pct(r['fraction_increased'])} |")
lines.append('')
lines.append('**Interpretation boundary.** This deliberately stratified 12-system panel is a mechanism/implementation robustness study, not a prevalence estimate. The independent implementation results support the Bader-specific basin-migration mechanism and preserve the qualitative codec ordering at strict perturbation. Spatial permutations provide secondary evidence that error organization matters, while the near-null periodic-shift control argues against a simple alignment-only explanation. These results do not redefine Protocol A.1 or alter the primary benchmark.')
lines.append('')
lines.append('**Sources:** `mechanism/independent_bader_20260908/outcomes/*.jsonl`; `stability_comparison.csv`; `mechanism_domain_decomposition.csv`; `mechanism_spatial_pairs.csv`; protocol and scope in `mechanism/independent_bader_20260908/README.md`.')

(ROOT/'paper'/'SUPPLEMENTARY_TABLES_S10_S11_20260911.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Built S10/S11')
print('S10 overall amplification', med(all_amp), 'domain share', med(all_share), 'domain dominates', all_dom)
for r in impl_summary:
    if r['metric']=='codec_response_ratio': print('codec pair',r)
for r in order_rows: print('order',r)
for r in dec_summary: print('domain',r)
