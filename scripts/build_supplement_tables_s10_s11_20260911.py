#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
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


def quantile(vals, p):
    vals = sorted(v for v in vals if math.isfinite(v))
    if not vals:
        return math.nan
    pos = (len(vals) - 1) * p
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    return vals[lo] + (vals[hi] - vals[lo]) * (pos - lo)


def median(vals):
    vals = [v for v in vals if math.isfinite(v)]
    return statistics.median(vals) if vals else math.nan


def pct(x):
    return f'{100*x:.1f}%'


def as_bool(x):
    return str(x).strip().lower() in {'true', 't', '1', 'yes'}

# S10 — representative fixed-basin versus re-derived mechanism decomposition.
main = read_csv(ROOT / 'mechanism' / 'basin_error_decomposition_summary.csv')
for r in main:
    r['relative_tolerance'] = float(r['relative_tolerance'])
    r['total_max'] = abs(float(r['dq_total_max_e']))
    r['integrand_max'] = abs(float(r['dq_integrand_max_e']))
    r['total_at_atom'] = abs(float(r['dq_total_at_that_atom']))
    r['integrand_at_atom'] = abs(float(r['dq_integrand_at_that_atom']))
    r['domain_at_atom'] = abs(float(r['dq_domain_at_that_atom']))
    r['reassign'] = float(r['frac_voxels_reassigned'])
    denom = r['domain_at_atom'] + r['integrand_at_atom']
    r['domain_abs_share'] = r['domain_at_atom'] / denom if denom > 0 else math.nan
    r['fixed_basin_underestimation'] = r['total_max'] / r['integrand_max'] if r['integrand_max'] > 0 else math.nan
    r['domain_dominates'] = r['domain_at_atom'] > r['integrand_at_atom']

assert len(main) >= 50 and len({r['material_id'] for r in main}) >= 6
s10 = []
for tau in (1e-4, 1e-3, 1e-2):
    for codec in ('zfp', 'sz3', 'sperr'):
        rr = [r for r in main if r['codec'].lower() == codec and abs(r['relative_tolerance'] - tau) < 1e-15]
        if not rr: continue
        amps = [r['fixed_basin_underestimation'] for r in rr]
        shares = [r['domain_abs_share'] for r in rr]
        s10.append({
            'relative_tolerance': tau, 'codec': codec.upper(), 'n_cases': len(rr),
            'median_fixed_basin_underestimation': median(amps),
            'p10_fixed_basin_underestimation': quantile(amps, .10),
            'p90_fixed_basin_underestimation': quantile(amps, .90),
            'median_domain_abs_share_at_max_total_atom': median(shares),
            'fraction_domain_dominates_at_max_total_atom': sum(r['domain_dominates'] for r in rr) / len(rr),
            'median_reassigned_voxel_fraction': median([r['reassign'] for r in rr]),
        })
write_csv(SUP / 'S10_bader_decomposition_summary.csv', s10)
all_amp = [r['fixed_basin_underestimation'] for r in main]
all_share = [r['domain_abs_share'] for r in main]
all_dom = sum(r['domain_dominates'] for r in main) / len(main)
assert 40 < median(all_amp) < 80, median(all_amp)

# S11 — independent implementation study directly from all 1,560 outcomes.
panel = json.loads((MECH / 'panel.json').read_text(encoding='utf-8'))
panel_map = {r['material_id']: r for r in panel}
outcomes = []
for p in sorted((MECH / 'outcomes').glob('*.jsonl')):
    outcomes.extend(json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip())
assert len(outcomes) == 1560, len(outcomes)
lookup = {(r['material_id'], r['variant'], r['solver']): r for r in outcomes}
failures = [r for r in outcomes if r.get('status') != 'SUCCESS']
assert len(failures) == 2

baseline = {}
for mid, meta in panel_map.items():
    if meta.get('sentinel'): continue
    ref = lookup[(mid, 'original', 'baderkit_ongrid')]
    for solver in ('henkelman_ongrid', 'henkelman_neargrid'):
        other = lookup[(mid, 'original', solver)]
        n = min(len(ref['atom_charges']), len(other['atom_charges']))
        baseline[(mid, solver)] = max(abs(ref['atom_charges'][i] - other['atom_charges'][i]) for i in range(n))

pairs = []
for mid, meta in panel_map.items():
    if meta.get('sentinel'): continue
    for codec in ('zfp', 'sz3', 'sperr'):
        for rel in ('0.0001', '0.001'):
            variant = f'{codec}_{rel}'
            a = lookup.get((mid, variant, 'baderkit_ongrid'))
            if not a or a.get('status') != 'SUCCESS': continue
            for solver in ('henkelman_ongrid', 'henkelman_neargrid'):
                b = lookup.get((mid, variant, solver))
                if not b or b.get('status') != 'SUCCESS': continue
                x = float(a['max_charge_error_e']); y = float(b['max_charge_error_e'])
                pairs.append({
                    'material': mid, 'domain': meta['domain'], 'role': meta['selection_role'], 'codec': codec.upper(),
                    'relative_tolerance': float(rel), 'comparison_solver': solver,
                    'baderkit_error_e': x, 'comparison_error_e': y,
                    'comparison_over_baderkit': y / x if x > 0 else math.nan,
                    'above_2e-6_print_region': min(x, y) > 2e-6,
                    'baseline_max_abs_charge_diff_e': baseline[(mid, solver)],
                    'baseline_compatible_1e-3': baseline[(mid, solver)] <= 1e-3,
                })
write_csv(SUP / 'S11_cross_implementation_pairs.csv', pairs)

impl_summary = []
for solver in ('henkelman_ongrid', 'henkelman_neargrid'):
    filters = [('above_print_resolution', lambda r: r['above_2e-6_print_region'])]
    if solver == 'henkelman_ongrid':
        filters.append(('above_print_and_baseline_compatible', lambda r: r['above_2e-6_print_region'] and r['baseline_compatible_1e-3']))
    for filter_name, pred in filters:
        rr = [r for r in pairs if r['comparison_solver'] == solver and pred(r) and math.isfinite(r['comparison_over_baderkit'])]
        vals = [r['comparison_over_baderkit'] for r in rr]
        impl_summary.append({'metric': 'codec_response_ratio', 'solver': solver, 'filter': filter_name, 'n': len(vals), 'median': median(vals), 'q25': quantile(vals, .25), 'q75': quantile(vals, .75)})

stab = [r for r in read_csv(MECH / 'stability_comparison.csv') if not as_bool(r['sentinel'])]
stab_map = {(r['material'], r['solver']): r for r in stab}
for solver in ('henkelman_ongrid', 'henkelman_neargrid'):
    ratios = []; print_agree = 0; concord = {1e-4: 0, 1e-3: 0, 1e-2: 0}; nmat = 0
    for mid, meta in panel_map.items():
        if meta.get('sentinel'): continue
        a = stab_map[(mid, 'baderkit_ongrid')]; b = stab_map[(mid, solver)]
        x = float(a['probe_response_max_e']); y = float(b['probe_response_max_e'])
        if x > 0 and y > 0: ratios.append(y / x)
        if abs(y - x) <= 1e-6: print_agree += 1
        for tau, col in ((1e-4, 'eligible_0.0001'), (1e-3, 'eligible_0.001'), (1e-2, 'eligible_0.01')):
            concord[tau] += str(a[col]).lower() == str(b[col]).lower()
        nmat += 1
    impl_summary.append({'metric': 'noise_floor_ratio', 'solver': solver, 'filter': 'all_12_representatives', 'n': len(ratios), 'median': median(ratios), 'q25': quantile(ratios, .25), 'q75': quantile(ratios, .75)})
    impl_summary.append({'metric': 'noise_floor_print_agreement', 'solver': solver, 'filter': 'abs_difference_le_1e-6', 'n': nmat, 'median': print_agree / nmat, 'q25': '', 'q75': ''})
    for tau in (1e-4, 1e-3, 1e-2):
        impl_summary.append({'metric': f'eligibility_concordance_{tau:g}', 'solver': solver, 'filter': 'all_12_representatives', 'n': nmat, 'median': concord[tau] / nmat, 'q25': '', 'q75': ''})
write_csv(SUP / 'S11_independent_implementation_summary.csv', impl_summary)
ongrid_pair = next(r for r in impl_summary if r['metric']=='codec_response_ratio' and r['solver']=='henkelman_ongrid' and r['filter']=='above_print_resolution')
near_pair = next(r for r in impl_summary if r['metric']=='codec_response_ratio' and r['solver']=='henkelman_neargrid' and r['filter']=='above_print_resolution')
assert abs(float(ongrid_pair['median']) - 1.0) < 0.01 and 0.7 < float(near_pair['median']) < 0.85

order_rows = []
for solver in ('baderkit_ongrid', 'henkelman_ongrid', 'henkelman_neargrid'):
    for numerator in ('sz3', 'sperr'):
        vals = []
        for mid, meta in panel_map.items():
            if meta.get('sentinel'): continue
            z = lookup.get((mid, 'zfp_0.0001', solver)); n = lookup.get((mid, f'{numerator}_0.0001', solver))
            if not z or not n or z.get('status') != 'SUCCESS' or n.get('status') != 'SUCCESS': continue
            ze = float(z['max_charge_error_e']); ne = float(n['max_charge_error_e'])
            if ze > 0 and ne > 0: vals.append(ne / ze)
        order_rows.append({'solver': solver, 'ratio': f'{numerator.upper()}/ZFP', 'n': len(vals), 'median_ratio': median(vals), 'q25': quantile(vals, .25), 'q75': quantile(vals, .75)})
write_csv(SUP / 'S11_codec_order_1e4.csv', order_rows)

dec = [r for r in read_csv(MECH / 'mechanism_domain_decomposition.csv') if not as_bool(r['sentinel'])]
dec_summary = []
for kind in sorted({r['kind'] for r in dec}):
    rr = [r for r in dec if r['kind'] == kind]
    shares = []; dominates = []; closure = []
    for r in rr:
        d = float(r['domain_max_e']); i = float(r['integrand_max_e'])
        if d + i > 0: shares.append(d / (d + i))
        dominates.append(d > i); closure.append(float(r['closure_max_e']))
    dec_summary.append({'kind': kind, 'n': len(rr), 'median_domain_abs_share': median(shares), 'q25': quantile(shares, .25), 'q75': quantile(shares, .75), 'fraction_domain_gt_integrand': sum(dominates) / len(dominates), 'max_closure_e': max(closure)})
write_csv(SUP / 'S11_independent_domain_summary.csv', dec_summary)

sp = [r for r in read_csv(MECH / 'mechanism_spatial_pairs.csv') if not as_bool(r['sentinel']) and r['ratio'] not in ('', 'None', 'nan', 'NaN')]
sp_summary = []
for solver in ('baderkit_ongrid', 'henkelman_ongrid', 'henkelman_neargrid'):
    for control in ('global', 'shift', 'stratified'):
        rr = [r for r in sp if r['solver'] == solver and r['control'] == control]
        logs = [math.log2(float(r['ratio'])) for r in rr if float(r['ratio']) > 0]
        sp_summary.append({'solver': solver, 'control': control, 'n': len(logs), 'median_log2_control_over_codec': median(logs), 'q25': quantile(logs, .25), 'q75': quantile(logs, .75), 'fraction_increased': sum(float(r['difference_e']) > 0 for r in rr) / len(rr)})
write_csv(SUP / 'S11_spatial_control_summary.csv', sp_summary)

lines = ['# Supplementary Tables S10–S11', '', 'Generated 2026-09-11 from the frozen Bader mechanism corpus and the independent Bader implementation study. These are robustness/mechanism tables; they do not alter the frozen benchmark or the central Figure 3 classification.', '', '## Supplementary Table S10 | Representative Bader decomposition confirms a dominant domain-migration channel', '', '| Relative codec tolerance | Codec | Cases | Median fixed-basin underestimation | P10–P90 | Median bounded domain share at max-total atom | Domain term > integrand | Median reassigned voxel fraction |', '|---:|---|---:|---:|---:|---:|---:|---:|']
for r in s10:
    lines.append(f"| {r['relative_tolerance']:.0e} | {r['codec']} | {r['n_cases']} | {r['median_fixed_basin_underestimation']:.2f}× | {r['p10_fixed_basin_underestimation']:.2f}–{r['p90_fixed_basin_underestimation']:.2f}× | {r['median_domain_abs_share_at_max_total_atom']:.3f} | {pct(r['fraction_domain_dominates_at_max_total_atom'])} | {r['median_reassigned_voxel_fraction']:.3e} |")
lines += ['', f"Across the full representative matrix (n={len(main)} material–codec–tolerance cases), the median maximum-resolved / maximum-fixed-basin error ratio is **{median(all_amp):.2f}×**. At the atom of maximum total deviation, the median bounded absolute domain share |domain|/(|domain|+|integrand|) is **{median(all_share):.3f}**, and the domain term exceeds the integrand term in **{pct(all_dom)}** of cases. These two metrics are reported separately because signed cancellation can make |domain|/|total| exceed 1.", '', '**Sources:** `mechanism/basin_error_decomposition_summary.csv`; extended per-atom values in `mechanism/basin_error_decomposition_per_atom.csv`. The stability-floor column in the historical mechanism table is not used for current Protocol A.1 claims.', '', '---', '', '## Supplementary Table S11 | Independent Bader implementations preserve the mechanism and strict-response ordering', '', '### S11a. Study completeness and solver failures', '', '| Quantity | Result |', '|---|---:|', '| Expected outcome rows | 1,560 |', '| Completed outcome rows | 1,560 |', '| BaderKit on-grid solver failures | 2 |', '| Henkelman on-grid solver failures | 0 |', '| Henkelman near-grid solver failures | 0 |', '| Representative systems in aggregate | 12 development systems |', '| Separate probe-failure sentinel | 1 (`mp-1007755`; excluded from aggregates) |', '', '### S11b. Cross-implementation stability and codec response', '', '| Diagnostic | Comparison solver | n | Median / fraction | IQR |', '|---|---|---:|---:|---:|']
for r in impl_summary:
    if r['metric'] == 'codec_response_ratio':
        lines.append(f"| Codec response comparison/BaderKit | {r['solver']} ({r['filter'].replace('_',' ')}) | {r['n']} | {float(r['median']):.3f} | {float(r['q25']):.3f}–{float(r['q75']):.3f} |")
    elif r['metric'] == 'noise_floor_print_agreement':
        lines.append(f"| A.1 floor agrees with BaderKit within 1e-6 e | {r['solver']} | {r['n']} materials | {pct(float(r['median']))} | — |")
    elif r['metric'].startswith('eligibility_concordance_'):
        tau = r['metric'].split('_')[-1]
        lines.append(f"| Eligibility concordance at {tau} e | {r['solver']} | {r['n']} materials | {pct(float(r['median']))} | — |")
lines += ['', 'Codec-response ratios above use successful paired outputs above the 2e-6 e Henkelman print-resolution region. The additional on-grid baseline-compatible row requires the unperturbed Henkelman/BaderKit atomic charges to agree within 1e-3 e. All paired points, including flagged baseline differences, remain in `supplement/S11_cross_implementation_pairs.csv`.', '', '### S11c. Relative 1e-4 codec-response ordering by implementation', '', '| Solver | Error ratio | n materials | Median ratio | IQR |', '|---|---|---:|---:|---:|']
for r in order_rows:
    lines.append(f"| {r['solver']} | {r['ratio']} | {r['n']} | {r['median_ratio']:.2f}× | {r['q25']:.2f}–{r['q75']:.2f}× |")
lines += ['', '### S11d. Exact BaderKit decomposition by perturbation kind', '', '| Perturbation kind | n | Median bounded domain share | IQR | Domain > integrand | Max closure residual (e) |', '|---|---:|---:|---:|---:|---:|']
for r in dec_summary:
    lines.append(f"| {r['kind']} | {r['n']} | {r['median_domain_abs_share']:.4f} | {r['q25']:.4f}–{r['q75']:.4f} | {pct(r['fraction_domain_gt_integrand'])} | {float(r['max_closure_e']):.1e} |")
lines += ['', '### S11e. Spatial reorganization controls', '', '| Solver | Control | n pairs | Median log2(control/codec) | IQR | Fraction increased |', '|---|---|---:|---:|---:|---:|']
for r in sp_summary:
    lines.append(f"| {r['solver']} | {r['control']} | {r['n']} | {r['median_log2_control_over_codec']:.2f} | {r['q25']:.2f}–{r['q75']:.2f} | {pct(r['fraction_increased'])} |")
lines += ['', '**Interpretation boundary.** This deliberately stratified 12-system panel is a mechanism/implementation robustness study, not a prevalence estimate. Henkelman on-grid reproduces the BaderKit codec response essentially one-for-one above print resolution, and the strict SZ3/ZFP and SPERR/ZFP ordering remains qualitatively similar under on-grid and near-grid Henkelman analyses. The exact decomposition supports a Bader-specific domain-migration channel. Spatial permutations provide secondary evidence that error organization matters, while the near-null periodic-shift control argues against a simple alignment-only explanation. These results do not redefine Protocol A.1 or alter the primary benchmark.', '', '**Sources:** `mechanism/independent_bader_20260908/outcomes/*.jsonl`; `stability_comparison.csv`; `mechanism_domain_decomposition.csv`; `mechanism_spatial_pairs.csv`; protocol/scope in `mechanism/independent_bader_20260908/README.md`.']
(ROOT / 'paper' / 'SUPPLEMENTARY_TABLES_S10_S11_20260911.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

print('Built S10/S11')
print('S10 overall fixed-basin underestimation', median(all_amp), 'domain share', median(all_share), 'domain dominates', all_dom)
for r in impl_summary:
    if r['metric'] in {'codec_response_ratio', 'noise_floor_print_agreement'}: print('impl', r)
for r in order_rows: print('order', r)
for r in dec_summary: print('domain', r)
