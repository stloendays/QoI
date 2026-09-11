#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper' / 'SUPPLEMENTARY_TABLES_S8_S9_20260911.md'


def read_csv(rel: str):
    with (ROOT / rel).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def fpercent(x: float, digits: int = 1) -> str:
    return f'{100.0 * x:.{digits}f}%'


def fnum(x: float, digits: int = 3) -> str:
    return f'{x:.{digits}f}'


def truthy(x: str) -> bool:
    return str(x).strip().lower() in {'true', 't', '1', 'yes'}

# -----------------------------------------------------------------------------
# Table S8: electron-count negative control
# -----------------------------------------------------------------------------
dec = read_csv('analysis/electron_count_qoi/electron_bader_decoupling.csv')
# Headline audit assertion.
h = [r for r in dec if r['codec'] == 'ALL' and float(r['electron_threshold_e']) == 1e-4 and float(r['bader_threshold_e']) == 1e-3]
assert len(h) == 1
assert int(h[0]['n_with_electron_count_preserved']) == 3205
assert int(h[0]['n_bader_failed_despite_electron_preservation']) == 1383
assert abs(float(h[0]['fraction_bader_failed']) - 0.431513) < 1e-6

all_rows = [r for r in dec if r['codec'] == 'ALL']
all_rows.sort(key=lambda r: (float(r['electron_threshold_e']), float(r['bader_threshold_e'])))
headline_codec = [r for r in dec if r['codec'] != 'ALL' and float(r['electron_threshold_e']) == 1e-4 and float(r['bader_threshold_e']) == 1e-3]
headline_codec.sort(key=lambda r: {'ZFP': 0, 'SZ3': 1, 'SPERR': 2}[r['codec']])

# -----------------------------------------------------------------------------
# Table S9: Hartree operator-control audit
# -----------------------------------------------------------------------------
group = read_csv('analysis/hartree_potential_expansion/group_summary.csv')
all_codec_group = [r for r in group if r['system_type'] == 'ALL']
all_codec_group.sort(key=lambda r: {'ZFP': 0, 'SZ3': 1, 'SPERR': 2}[r['codec']])
assert sum(int(float(r['n_rows'])) for r in all_codec_group) == 6270

smooth = read_csv('analysis/hartree_potential_expansion/material_smoothness.csv')
smooth = [r for r in smooth if int(float(r['n_rows'])) >= 5]
assert len(smooth) == 678

summary_material = []
for codec in ('ZFP', 'SZ3', 'SPERR'):
    rr = [r for r in smooth if r['codec'] == codec]
    assert rr
    summary_material.append({
        'codec': codec,
        'pairs': len(rr),
        'hartree_monotone': sum(truthy(r['hartree_monotone']) for r in rr) / len(rr),
        'bader_monotone': sum(truthy(r['bader_monotone']) for r in rr) / len(rr),
        'hartree_R2_median': statistics.median(float(r['hartree_R2']) for r in rr),
        'bader_R2_median': statistics.median(float(r['bader_R2']) for r in rr),
        'hartree_slope_median': statistics.median(float(r['hartree_slope']) for r in rr),
        'bader_slope_median': statistics.median(float(r['bader_slope']) for r in rr),
    })

all_hmono = sum(truthy(r['hartree_monotone']) for r in smooth) / len(smooth)
all_bmono = sum(truthy(r['bader_monotone']) for r in smooth) / len(smooth)
all_h_r2_med = statistics.median(float(r['hartree_R2']) for r in smooth)
all_b_r2_med = statistics.median(float(r['bader_R2']) for r in smooth)
bader_el_min = min(float(r['bader_local_elasticity_min']) for r in smooth if r['bader_local_elasticity_min'] not in ('', 'nan', 'NaN'))
bader_el_max = max(float(r['bader_local_elasticity_max']) for r in smooth if r['bader_local_elasticity_max'] not in ('', 'nan', 'NaN'))
hartree_el_min = min(float(r['hartree_local_elasticity_min']) for r in smooth if r['hartree_local_elasticity_min'] not in ('', 'nan', 'NaN'))
hartree_el_max = max(float(r['hartree_local_elasticity_max']) for r in smooth if r['hartree_local_elasticity_max'] not in ('', 'nan', 'NaN'))
max_jump = max(float(r['bader_max_consecutive_jump']) for r in smooth if r['bader_max_consecutive_jump'] not in ('', 'nan', 'NaN'))
assert abs(all_hmono - 0.8864306784660767) < 0.002
assert abs(all_bmono - 0.3244837758112094) < 0.002
assert 22290 < max_jump < 22300

# Matched-Hartree bins. The frozen analysis report applies n >= 10; the table file
# already contains those retained bins. Use row weighting to reproduce the 55.4% claim.
disp = read_csv('analysis/hartree_potential_expansion/matched_error_dispersion.csv')
valid_disp = [r for r in disp if int(r['n']) >= 10]
row_total = sum(int(r['n']) for r in valid_disp)
row_decade = sum(int(r['n']) for r in valid_disp if float(r['bader_p90_over_p10']) >= 10)
row_decade_frac = row_decade / row_total
assert 0.553 < row_decade_frac < 0.555, row_decade_frac

# -----------------------------------------------------------------------------
# Render submission-facing Markdown.
# -----------------------------------------------------------------------------
lines = []
lines.append('# Supplementary Tables S8–S9')
lines.append('')
lines.append('Generated 2026-09-11 directly from frozen operator-control outputs. These tables support Supplementary Figure S3 and the main-text operator comparison. No values are transcribed from historical prose summaries.')
lines.append('')
lines.append('## Supplementary Table S8 | Electron-count preservation does not certify Bader-charge fidelity')
lines.append('')
lines.append('### S8a. Pooled negative-control matrix across all codecs')
lines.append('')
lines.append('| Electron-count threshold | Bader threshold | Rows preserving electron count | Rows failing Bader threshold despite preservation | Fraction |')
lines.append('|---:|---:|---:|---:|---:|')
for r in all_rows:
    lines.append(f"| {float(r['electron_threshold_e']):.0e} e | {float(r['bader_threshold_e']):.0e} e | {int(r['n_with_electron_count_preserved']):,} | {int(r['n_bader_failed_despite_electron_preservation']):,} | {fpercent(float(r['fraction_bader_failed']), 2)} |")
lines.append('')
lines.append('### S8b. Codec-resolved headline control at |ΔNe| < 1e-4 e and Bader error >= 1e-3 e')
lines.append('')
lines.append('| Codec | Rows preserving electron count | Rows still failing Bader threshold | Fraction |')
lines.append('|---|---:|---:|---:|')
for r in headline_codec:
    lines.append(f"| {r['codec']} | {int(r['n_with_electron_count_preserved']):,} | {int(r['n_bader_failed_despite_electron_preservation']):,} | {fpercent(float(r['fraction_bader_failed']), 2)} |")
lines.append(f"| **All codecs** | **{int(h[0]['n_with_electron_count_preserved']):,}** | **{int(h[0]['n_bader_failed_despite_electron_preservation']):,}** | **{fpercent(float(h[0]['fraction_bader_failed']), 2)}** |")
lines.append('')
lines.append('**Interpretation.** Global electron conservation is a negative control, not a sufficient certificate for atom-resolved Bader fidelity. The main-text 3,205 / 1,383 = 43.15% result is the pooled row highlighted above.')
lines.append('')
lines.append('**Source:** `analysis/electron_count_qoi/electron_bader_decoupling.csv`.')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## Supplementary Table S9 | Hartree-potential response is smoother than re-derived Bader response on the same reconstructions')
lines.append('')
lines.append('### S9a. Pooled codec-level scaling on the 6,270 reproduction-gate-passing rows')
lines.append('')
lines.append('| Codec | Gate-passing rows | Hartree slope | Hartree R² | Bader slope | Bader R² | Median Hartree relative RMSE | Median Bader error (e) |')
lines.append('|---|---:|---:|---:|---:|---:|---:|---:|')
for r in all_codec_group:
    lines.append(f"| {r['codec']} | {int(float(r['n_rows'])):,} | {float(r['hartree_slope']):.3f} | {float(r['hartree_R2']):.3f} | {float(r['bader_slope']):.3f} | {float(r['bader_R2']):.3f} | {float(r['median_potential_rel_RMSE']):.3e} | {float(r['median_Bader_error_e']):.3e} |")
lines.append('')
lines.append('The all-codec pooled Hartree log–log exponent reported by the frozen analysis is **1.02** on all 6,270 gate-passing rows; the per-codec values above show the same near-first-order pattern without collapsing codec-specific prefactors.')
lines.append('')
lines.append('### S9b. Material-level smoothness for 678 material–codec pairs with at least five gate-passing rows')
lines.append('')
lines.append('| Codec | Pairs | Hartree monotone | Bader monotone | Median Hartree R² | Median Bader R² | Median Hartree slope | Median Bader slope |')
lines.append('|---|---:|---:|---:|---:|---:|---:|---:|')
for r in summary_material:
    lines.append(f"| {r['codec']} | {r['pairs']} | {fpercent(r['hartree_monotone'])} | {fpercent(r['bader_monotone'])} | {r['hartree_R2_median']:.3f} | {r['bader_R2_median']:.3f} | {r['hartree_slope_median']:.2f} | {r['bader_slope_median']:.2f} |")
lines.append(f"| **All** | **678** | **{fpercent(all_hmono)}** | **{fpercent(all_bmono)}** | **{all_h_r2_med:.3f}** | **{all_b_r2_med:.3f}** | — | — |")
lines.append('')
lines.append('### S9c. Rung-level irregularity and matched-Hartree dispersion')
lines.append('')
lines.append('| Diagnostic | Hartree | Bader |')
lines.append('|---|---:|---:|')
lines.append(f'| Local log–log elasticity range | {hartree_el_min:.1f} to +{hartree_el_max:.1f} | {bader_el_min:.1f} to +{bader_el_max:.1f} |')
lines.append(f'| Largest consecutive Bader-error jump | — | {max_jump:,.0f}× |')
lines.append(f'| Gate-passing rows in matched-Hartree bins with Bader P90/P10 >= 10 | — | {row_decade:,}/{row_total:,} = {fpercent(row_decade_frac)} |')
lines.append('')
lines.append('**Interpretation.** The Hartree control is close to first-order at pooled and material levels, whereas the re-derived Bader response shows substantially more rung-level non-monotonicity and dispersion. The slab monotonicity caveat remains: strict Hartree monotonicity is weaker on slabs even though material-level Hartree R² remains high. The result should therefore be described as a smoother response, not as universal monotonicity.')
lines.append('')
lines.append('**Sources:** `analysis/hartree_potential_expansion/group_summary.csv`; `analysis/hartree_potential_expansion/material_smoothness.csv`; `analysis/hartree_potential_expansion/matched_error_dispersion.csv`; `analysis/hartree_potential_expansion/RESULTS_DETAIL.md`.')
lines.append('')
lines.append('## Submission boundary')
lines.append('')
lines.append('Tables S8–S9 are operator-control evidence. They motivate why downstream analyses must be evaluated explicitly, but they do not carry the central novelty claim. The central benchmark-validity result remains the stability-qualified binary-to-three-state reclassification in Figure 3 / Supplementary Table S4.')

OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Wrote {OUT.relative_to(ROOT)}')
print(f'S8 headline: {h[0]["n_bader_failed_despite_electron_preservation"]}/{h[0]["n_with_electron_count_preserved"]} = {100*float(h[0]["fraction_bader_failed"]):.2f}%')
print(f'S9: n_pairs={len(smooth)}, Hartree monotone={100*all_hmono:.1f}%, Bader monotone={100*all_bmono:.1f}%, matched-bin fraction={100*row_decade_frac:.1f}%')
