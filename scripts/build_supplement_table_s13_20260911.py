#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper' / 'SUPPLEMENTARY_TABLE_S13_20260911.md'
SUM_OUT = ROOT / 'supplement' / 'S13_rate_fidelity_summary.csv'
PAIR_OUT = ROOT / 'supplement' / 'S13_pairwise_sz3_zfp.csv'


def read_csv(rel):
    with (ROOT / rel).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def pct(x): return f'{100*float(x):.1f}%'

def rowfmt(r):
    return f"{float(r['ratio_median']):.1f}× [{float(r['ratio_median_ci_lo']):.1f}, {float(r['ratio_median_ci_hi']):.1f}]"

# Current frozen sources of record.
dev = read_csv('benchmark/summary_a1.csv')
ext = read_csv('validation/final_external_confirmatory63_20260908/confirmatory63/external_summary_a1.csv')
dev_pair = read_csv('benchmark/pairwise_a1.csv')
ext_pair = read_csv('validation/final_external_confirmatory63_20260908/confirmatory63/pairwise_external.csv')

# High-risk assertions.
D = {(float(r['threshold_e']), r['stratum'], r['codec']): r for r in dev}
E = {(float(r['threshold_e']), r['stratum'], r['codec']): r for r in ext}
assert abs(float(D[(1e-2,'bulk','sz3')]['ratio_median']) - 51.77969414519157) < 1e-12
assert abs(float(D[(1e-2,'slab','sz3')]['ratio_median']) - 67.75170239138666) < 1e-12
assert abs(float(E[(1e-4,'overall','zfp')]['ratio_median']) - 13.026955334522793) < 1e-12
assert abs(float(E[(1e-3,'overall','sz3')]['ratio_median']) - 18.758628450928306) < 1e-12
assert abs(float(E[(1e-2,'overall','sz3')]['ratio_median']) - 65.89190594093266) < 1e-12
assert [int(E[(t,'overall','zfp')]['n_admitted']) for t in (1e-4,1e-3,1e-2)] == [16,42,57]

# Long-form machine-readable summary with cohort labels and row-failure flags.
summary=[]
for cohort, rows in [('development',dev),('external_confirmatory63',ext)]:
    for r in rows:
        summary.append({
            'cohort':cohort,
            'threshold_e':float(r['threshold_e']),
            'stratum':r['stratum'],
            'codec':r['codec'].upper(),
            'n_admitted':int(r['n_admitted']),
            'n_non_evaluable':int(r['n_non_evaluable']),
            'n_certified':int(r['n_certified']),
            'frac_certified':float(r['frac_certified']),
            'ratio_median':float(r['ratio_median']),
            'ratio_median_ci_lo':float(r['ratio_median_ci_lo']),
            'ratio_median_ci_hi':float(r['ratio_median_ci_hi']),
            'ratio_p10':float(r['ratio_p10']),
            'ratio_q1':float(r['ratio_q1']),
            'ratio_q3':float(r['ratio_q3']),
            'ratio_p90':float(r['ratio_p90']),
            'n_row_failure_affected':int(r.get('n_row_failure_affected') or 0),
        })
write_csv(SUM_OUT, summary)

# Pairwise SZ3 vs ZFP only: this is the most decision-relevant ranking transition.
pairs=[]
for cohort, rows in [('development',dev_pair),('external_confirmatory63',ext_pair)]:
    for r in rows:
        if r['codec_a']=='sz3' and r['codec_b']=='zfp':
            pairs.append({
                'cohort':cohort,'threshold_e':float(r['threshold_e']),'stratum':r['stratum'],
                'n':int(r['n']),'sz3_win_fraction':float(r['frac_a_wins']),
                'tie_fraction':float(r['frac_ties']),'zfp_win_fraction':float(r['frac_b_wins']),
                'sz3_win_ci_lo':float(r['a_wins_ci_lo']),'sz3_win_ci_hi':float(r['a_wins_ci_hi']),
                'median_log2_ratio_sz3_over_zfp':float(r['median_log2_ratio_a_over_b']),
                'n_both_certified':int(r.get('n_both_certified') or 0),
                'n_row_failure_affected':int(r.get('n_row_failure_affected') or 0),
            })
write_csv(PAIR_OUT,pairs)
P={(r['cohort'],r['threshold_e'],r['stratum']):r for r in pairs}
assert abs(P[('development',1e-2,'overall')]['sz3_win_fraction']-0.8034934497816594)<1e-12
assert abs(P[('external_confirmatory63',1e-2,'overall')]['sz3_win_fraction']-0.8947368421052632)<1e-12
assert abs(P[('external_confirmatory63',1e-4,'overall')]['sz3_win_fraction']-0.3125)<1e-12

codec_order={'zfp':0,'sz3':1,'sperr':2}
thresholds=(1e-4,1e-3,1e-2)

lines=['# Supplementary Table S13 | Stability-qualified rate–fidelity in development and untouched external confirmation','',
       'Generated 2026-09-11 directly from the current frozen development and 63-system external confirmatory summaries. This table is the submission numerical source for rate–fidelity prose; historical intermediate summaries are not used.','',
       '## S13a. Development cohort — overall eligible material set','',
       '| Bader contract | Codec | Admitted | Non-evaluable | Certified | Certified fraction | Median best-certified compression ratio [95% bootstrap CI] | P10–P90 |',
       '|---:|---|---:|---:|---:|---:|---:|---:|']
for t in thresholds:
    rr=sorted([r for r in dev if r['stratum']=='overall' and abs(float(r['threshold_e'])-t)<1e-15], key=lambda x:codec_order[x['codec']])
    for r in rr:
        lines.append(f"| {t:.0e} e | {r['codec'].upper()} | {int(r['n_admitted'])} | {int(r['n_non_evaluable'])} | {int(r['n_certified'])} | {pct(r['frac_certified'])} | {rowfmt(r)} | {float(r['ratio_p10']):.1f}–{float(r['ratio_p90']):.1f}× |")

lines += ['', '## S13b. Development cohort — bulk/slab strata', '',
          '| Bader contract | Stratum | Codec | Admitted | Non-evaluable | Certified fraction | Median ratio [95% bootstrap CI] |',
          '|---:|---|---|---:|---:|---:|---:|']
for t in thresholds:
    for stratum in ('bulk','slab'):
        rr=sorted([r for r in dev if r['stratum']==stratum and abs(float(r['threshold_e'])-t)<1e-15], key=lambda x:codec_order[x['codec']])
        for r in rr:
            lines.append(f"| {t:.0e} e | {stratum} | {r['codec'].upper()} | {int(r['n_admitted'])} | {int(r['n_non_evaluable'])} | {pct(r['frac_certified'])} | {rowfmt(r)} |")

lines += ['', '## S13c. Untouched external confirmatory cohort — overall', '',
          '| Bader contract | Codec | Admitted (of 63) | Non-evaluable | Certified | Certified fraction | Median best-certified compression ratio [95% bootstrap CI] | Row-failure-affected materials |',
          '|---:|---|---:|---:|---:|---:|---:|---:|']
for t in thresholds:
    rr=sorted([r for r in ext if r['stratum']=='overall' and abs(float(r['threshold_e'])-t)<1e-15], key=lambda x:codec_order[x['codec']])
    for r in rr:
        lines.append(f"| {t:.0e} e | {r['codec'].upper()} | {int(r['n_admitted'])} | {int(r['n_non_evaluable'])} | {int(r['n_certified'])} | {pct(r['frac_certified'])} | {rowfmt(r)} | {int(r['n_row_failure_affected'])} |")

lines += ['', '## S13d. Untouched external cohort — bulk/vacuum-containing 2D strata', '',
          '| Bader contract | Stratum | Codec | Admitted | Non-evaluable | Certified fraction | Median ratio [95% bootstrap CI] |',
          '|---:|---|---|---:|---:|---:|---:|']
for t in thresholds:
    for stratum in ('bulk','vacuum2d'):
        rr=sorted([r for r in ext if r['stratum']==stratum and abs(float(r['threshold_e'])-t)<1e-15], key=lambda x:codec_order[x['codec']])
        for r in rr:
            lines.append(f"| {t:.0e} e | {stratum} | {r['codec'].upper()} | {int(r['n_admitted'])} | {int(r['n_non_evaluable'])} | {pct(r['frac_certified'])} | {rowfmt(r)} |")

lines += ['', '## S13e. Pairwise SZ3 versus ZFP transition', '',
          '| Cohort | Bader contract | Stratum | n eligible comparisons | SZ3 wins | Ties | ZFP wins | Median log2(SZ3/ZFP) |',
          '|---|---:|---|---:|---:|---:|---:|---:|']
for cohort in ('development','external_confirmatory63'):
    for t in thresholds:
        for stratum in ('overall','bulk','slab' if cohort=='development' else 'vacuum2d'):
            r=P.get((cohort,t,stratum))
            if not r: continue
            lines.append(f"| {cohort} | {t:.0e} e | {stratum} | {r['n']} | {pct(r['sz3_win_fraction'])} | {pct(r['tie_fraction'])} | {pct(r['zfp_win_fraction'])} | {r['median_log2_ratio_sz3_over_zfp']:.3f} |")

lines += ['',
          '**External confirmation summary.** The untouched cohort admits 16/63, 42/63 and 57/63 systems at 1e-4, 1e-3 and 1e-2 e. Median external best-certified compression ratios are approximately ZFP/SZ3/SPERR = 13.0/12.1/5.2× at 1e-4 e, 18.8/18.8/6.4× at 1e-3 e, and 40.6/65.9/10.8× at 1e-2 e. The SZ3-versus-ZFP win fraction correspondingly shifts from 31.3% to 35.7% to 89.5%.', '',
          '**Interpretation boundary.** The preferred codec depends on the scientific contract and the eligible cohort. These tables do not support a universal codec winner. The 63-system confirmatory cohort must not be replaced by the 65-system descriptive/stability aggregate when reporting external rate–fidelity.', '',
          '**Machine-readable submission sources:** `supplement/S13_rate_fidelity_summary.csv` and `supplement/S13_pairwise_sz3_zfp.csv`.']
OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Wrote {OUT.relative_to(ROOT)}, {SUM_OUT.relative_to(ROOT)}, {PAIR_OUT.relative_to(ROOT)}')
