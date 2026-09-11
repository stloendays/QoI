#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(rel):
    with (ROOT / rel).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {n}')
    return text.replace(old, new, 1)


def fmt1(x):
    return f'{float(x):.1f}'


def pct(x):
    return 100.0 * float(x)

# -----------------------------------------------------------------------------
# Recompute/verify the high-risk numbers from current machine-readable sources.
# -----------------------------------------------------------------------------
reclass = {float(r['threshold_e']): r for r in read_csv('analysis/certifiability_reclassification_pooled_20260911.csv')}
assert int(reclass[1e-4]['n_decisions']) == 762
assert (int(reclass[1e-4]['naive_fail']), int(reclass[1e-4]['naive_fail_reclassified_non_evaluable']), int(reclass[1e-4]['eligible_fail'])) == (533, 518, 15)
assert (int(reclass[1e-3]['naive_fail']), int(reclass[1e-3]['naive_fail_reclassified_non_evaluable']), int(reclass[1e-3]['eligible_fail'])) == (310, 296, 14)
assert (int(reclass[1e-2]['naive_fail']), int(reclass[1e-2]['naive_fail_reclassified_non_evaluable']), int(reclass[1e-2]['eligible_fail'])) == (108, 61, 47)
assert int(reclass[1e-4]['non_evaluable_naive_pass']) == 106
assert int(reclass[1e-4]['naive_pass']) == 229

elig = {(float(r['threshold_e']), r['stratum']): r for r in read_csv('stability/eligibility_summary_A1.csv')}
assert [(int(elig[t, 'overall']['n']), int(elig[t, 'overall']['eligible']), int(elig[t, 'overall']['non_evaluable'])) for t in (1e-4, 1e-3, 1e-2)] == [(319, 64, 255), (319, 187, 132), (319, 288, 31)]
assert abs(float(elig[1e-4, 'dev_bulk']['floor_a1_median']) - 6.729e-4) < 1e-12

floor_rel = {(float(r['threshold_e']), r['codec']): r for r in read_csv('supplement/S2_floor_relative.csv')}
assert 1.09 < float(floor_rel[1e-4, 'zfp']['dq_over_floor_median']) < 1.10
assert 1.32 < float(floor_rel[1e-4, 'sz3']['dq_over_floor_median']) < 1.34
assert 1.23 < float(floor_rel[1e-4, 'sperr']['dq_over_floor_median']) < 1.24

summary = {(float(r['threshold_e']), r['stratum'], r['codec']): r for r in read_csv('benchmark/summary_a1.csv')}
# Current frozen development 1e-2 values.
expected_dev = {
    ('bulk', 'sz3'): (51.77969414519157, 47.69493441485609, 60.30696879570302, 0.9523809523809523),
    ('bulk', 'zfp'): (30.01965330038169, 27.0530934019328, 31.861606784438848, 0.9880952380952381),
    ('bulk', 'sperr'): (11.510742267135877, 10.12826234875516, 13.241847341156024, 0.9583333333333334),
    ('slab', 'sz3'): (67.75170239138666, 59.57740808560928, 70.63602570162104, 0.7704918032786885),
    ('slab', 'zfp'): (40.451044529674256, 35.794635271270785, 44.89717328013177, 0.9672131147540983),
    ('slab', 'sperr'): (8.097571180519235, 7.684321018844518, 8.644115994475955, 0.7704918032786885),
}
for key, exp in expected_dev.items():
    r = summary[(1e-2, key[0], key[1])]
    got = tuple(float(r[c]) for c in ('ratio_median', 'ratio_median_ci_lo', 'ratio_median_ci_hi', 'frac_certified'))
    assert all(abs(a-b) < 1e-12 for a, b in zip(got, exp)), (key, got, exp)

external = {(float(r['threshold_e']), r['stratum'], r['codec']): r for r in read_csv('validation/final_external_confirmatory63_20260908/confirmatory63/external_summary_a1.csv')}
for t, admitted in ((1e-4, 16), (1e-3, 42), (1e-2, 57)):
    assert int(external[t, 'overall', 'zfp']['n_admitted']) == admitted
assert abs(float(external[1e-2, 'overall', 'sz3']['ratio_median']) - 65.89190594093266) < 1e-12

# Protocol A.1 calibration numbers.
cal = read_csv('stability/probe_calibration.csv')
f32 = [r for r in cal if r['seed'] == 'float32' and abs(float(r['amplitude_factor']) - 1.0) < 1e-12]
primary_noise = [r for r in cal if r['seed'] == '20260905' and abs(float(r['amplitude_factor']) - 1.0) < 1e-12]
assert len(f32) == 18 and len(primary_noise) == 18
median_ties = statistics.median(int(r['n_exact_neighbour_ties_created']) for r in f32)
f32_zero = sum(int(r['n_voxels_reassigned']) == 0 for r in f32)
noise_zero = sum(int(r['n_voxels_reassigned']) == 0 for r in primary_noise)
assert median_ties == 82
assert f32_zero == 9
assert noise_zero == 2
assert all(int(r['n_exact_neighbour_ties_created']) == 0 for r in primary_noise)

# Current formal Figure 4 comparison: A.1 five-seed maximum versus archived A,
# restricted to paired development materials.
a1_rows = {r['material_id']: r for r in read_csv('stability/stability_floor_A1.csv') if r['corpus'].startswith('dev_')}
a0_rows = {r['material_id']: r for r in read_csv('stability/stability_floor_A_archived_float32.csv') if r['corpus'].startswith('dev_')}
paired = sorted(set(a1_rows) & set(a0_rows))
assert len(paired) == 254
ratios = []
for mid in paired:
    a1 = float(a1_rows[mid]['stability_floor_A1_e'])
    a0 = float(a0_rows[mid]['floor_resolved_e'])
    if math.isfinite(a1) and math.isfinite(a0) and a1 > 0 and a0 > 0:
        ratios.append(a1 / a0)
median_shift = statistics.median(ratios)
assert 1.5e4 < median_shift < 1.7e4, median_shift

# -----------------------------------------------------------------------------
# Patch the reader-facing manuscript.
# -----------------------------------------------------------------------------
man_path = ROOT / 'paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md'
man = man_path.read_text(encoding='utf-8')

old = "We next asked whether the requested Bader tolerances are themselves numerically identifiable. Protocol A.1 applies five fixed-seed, non-order-preserving perturbations to each reference density at an amplitude equal to that material's float32 $L_\\infty$ scale. The maximum re-derived Bader deviation across the five probes defines a material-specific stability floor. A Bader contract $\\tau$ is eligible only when this independently measured floor is below $\\tau$."
new = old + " The frozen protocol definition and its pre-freeze seed/amplitude calibration are summarized in Supplementary Table S2 and Supplementary Fig. S2."
man = replace_once(man, old, new, 'manuscript Protocol A.1 SI reference')

old = "Eligibility decreases sharply as the requested precision becomes stricter. Across all 319 development and external systems, 79.9% are non-evaluable at $10^{-4}\\,e$, 41.4% at $10^{-3}\\,e$, and 9.7% at $10^{-2}\\,e$. These fractions are properties of the reference analysis under the frozen qualification protocol; they are not codec failure rates."
new = old + " The development/external stratum breakdown is given in Supplementary Table S3 and Supplementary Fig. S1."
man = replace_once(man, old, new, 'manuscript eligibility SI reference')

old = "Most apparent failures at the strictest thresholds are therefore not attributable to the compressor. Of the 533 naive failures at $10^{-4}\\,e$, 518 (97.2%) occur on non-evaluable material–threshold pairs. At $10^{-3}\\,e$, 296 of 310 naive failures (95.5%) are likewise non-evaluable. Even at $10^{-2}\\,e$, 61 of 108 apparent failures (56.5%) fall outside the eligible benchmark. Importantly, eligibility is not a permissive filter that only removes failures: at $10^{-4}\\,e$, 106 of 229 naive passes (46.3%) are also non-evaluable. Stability qualification therefore changes the label space itself. A material–threshold pair is either **eligible and certified**, **eligible but not certified**, or **non-evaluable**; the third state can be assigned neither success nor failure at the requested precision."
new = old + " The codec-resolved decomposition shows the same strict-threshold pattern for ZFP, SZ3 and SPERR (Supplementary Table S4 and Supplementary Fig. S7)."
man = replace_once(man, old, new, 'manuscript reclassification SI reference')

old = "This distinction is substantial rather than cosmetic. The float32 probe generates a median of 82 exact neighbouring ties and reassigns zero voxels in 62% of tested systems, whereas non-order-preserving noise at the same, or even 100-fold smaller, amplitude can reassign hundreds of voxels. Across the full stability corpus, the Protocol A.1 noise-based floor is a median of approximately $8.7\\times10^3$ times larger than the archived float32 floor. The effect is also heterogeneous across materials, ruling out a simple global rescaling."
new = f"This distinction is substantial rather than cosmetic. In the 18-material pre-freeze calibration, the archived float32 probe creates a median of {int(median_ties)} exact neighbouring ties and reassigns zero voxels in {f32_zero}/18 systems, whereas the same-amplitude primary noise probe creates no exact neighbouring ties and reassigns zero voxels in only {noise_zero}/18. In the paired 254-material development comparison used in Fig. 4, the operative five-seed Protocol A.1 floor is a median of approximately $1.6\\times10^4$ times the archived Protocol A floor. The shift is heterogeneous rather than a simple global rescaling (Supplementary Table S7 and Supplementary Fig. S2)."
man = replace_once(man, old, new, 'manuscript probe correction')

old = "This relation weakens as the contract is relaxed. At $10^{-3}\\,e$, median error-to-floor ratios rise to 2.78–3.55, and at $10^{-2}\\,e$ to 10.7–14.6. We therefore describe the strictest certified regime as **floor-scale and consistent with an emerging analysis-limited regime**. The present data do not establish a universal material-by-material equality between a tight-ladder plateau and the Protocol A.1 floor, and no such equality is assumed in the certification rule."
new = old + " Threshold- and codec-resolved error-to-floor distributions are reported in Supplementary Table S6."
man = replace_once(man, old, new, 'manuscript floor-scale SI reference')

old = "Among eligible material–threshold pairs, we select the highest compression ratio that satisfies the Bader contract on the frozen codec ladder. The resulting rate–fidelity frontier is strongly tolerance dependent. At $10^{-2}\\,e$ in the development set, SZ3 provides the largest median certified compression ratio in both bulk and slab strata (52.0× [48.0, 61.7] and 69.6× [65.9, 72.3], respectively), ahead of ZFP (30.0× [27.2, 31.7] and 40.5× [37.0, 44.9]) and SPERR (11.6× [10.1, 13.4] and 8.1× [7.7, 9.4]). At $10^{-3}\\,e$, ZFP and SZ3 become much closer, and at $10^{-4}\\,e$ ZFP has the advantage among the much smaller eligible cohort. Thus, no single codec dominates across scientific contracts."
new = "Among eligible material–threshold pairs, we select the highest compression ratio that satisfies the Bader contract on the frozen codec ladder. The resulting rate–fidelity frontier is strongly tolerance dependent. At $10^{-2}\\,e$ in the development set, SZ3 provides the largest median certified compression ratio in both bulk and slab strata (51.8× [47.7, 60.3] and 67.8× [59.6, 70.6], respectively), ahead of ZFP (30.0× [27.1, 31.9] and 40.5× [35.8, 44.9]) and SPERR (11.5× [10.1, 13.2] and 8.1× [7.7, 8.6]). At $10^{-3}\\,e$, ZFP and SZ3 become much closer, and at $10^{-4}\\,e$ ZFP has the advantage among the much smaller eligible cohort. Thus, no single codec dominates across scientific contracts. These values are regenerated from the current frozen `benchmark/summary_a1.csv`; historical prose summaries are not used as a numerical source."
man = replace_once(man, old, new, 'manuscript development rate-fidelity correction')

old = "We finally applied the complete qualification and certification procedure to 63 untouched external systems without changing thresholds, probe definitions or codec-scoring rules (Fig. 7). The external analysis produced 1,689 retained rows, with zero material-level pipeline failures and zero codec error-bound violations; three row-level Bader-solver failures remain explicitly recorded in the audit."
new = old + " This primary 63-system confirmatory cohort is distinct from the 65-system external descriptive/stability universe used in the 319-system stability summary (Supplementary Table S1)."
man = replace_once(man, old, new, 'manuscript external denominator SI reference')

old = "The development benchmark contains 6,343 frozen reconstruction rows from 254 electronic-density fields: 186 bulk systems and 68 slabs. ZFP, SZ3/SZ and SPERR were evaluated over a base tolerance ladder and an extended tight ladder using their respective error-bounded compression frameworks [2–4]. Each row records material identity, codec configuration, requested tolerance, realized distortion, compressed size, downstream QoI errors and stability-qualification status. Frozen outputs were used for all downstream analyses; earlier protocol versions were retained as provenance rather than overwritten."
new = old + " Cohort and denominator conventions are summarized in Supplementary Table S1."
man = replace_once(man, old, new, 'methods benchmark S1 reference')

old = "For material $m$, Protocol A.1 applies five pre-specified fixed-seed uniform perturbations at an amplitude equal to the material's float32 $L_\\infty$ scale. Bader basins and charges are re-derived after each perturbation. The stability floor $f_m$ is the maximum induced Bader deviation across the five probes."
new = old + " The exact seed set, archived Protocol A comparison and frozen reporting semantics are given in Supplementary Table S2."
man = replace_once(man, old, new, 'methods Protocol A1 S2 reference')

old = "The external cohort was kept separate from development analyses. All scientific tolerances, perturbation definitions, eligibility rules and codec-scoring semantics were frozen before external evaluation. The confirmatory analysis assessed pipeline completion, codec error-bound compliance, Protocol A.1 eligibility, tolerance-dependent certified compression ratios and realized-distortion asymmetry."
new = old + " Supplementary Table S1 records the distinct 63-system confirmatory and 65-system descriptive/stability external universes."
man = replace_once(man, old, new, 'methods external S1 reference')

man_path.write_text(man, encoding='utf-8')

# -----------------------------------------------------------------------------
# Patch claim-evidence registry where stale intermediate values remained.
# -----------------------------------------------------------------------------
claim_path = ROOT / 'paper/CLAIM_EVIDENCE_MATRIX.md'
claim = claim_path.read_text(encoding='utf-8')

claim = replace_once(
    claim,
    "**Correction of record (2026-09-05).** The Protocol A stability probe (float32\nround trip) is order-preserving and blind to the on-grid watershed's tie\nresolution; it understates the stability floor by a median factor of ~8 700.\nProtocol A is archived unchanged; **Protocol A.1** (`results/stability/PROTOCOL_A1.md`,\nfive pre-registered noise seeds, floor = max over seeds) replaces it. Every\nprobe-dependent number below is restated under A.1, with the archived A value\nkept in brackets and marked *archived*. Codec rows of the master table are\nprobe-independent and unaffected.",
    "**Correction of record (2026-09-05; submission audit refreshed 2026-09-11).** The Protocol A stability probe (float32\nround trip) is order-preserving and blind to the on-grid basin-assignment failure channel.\nProtocol A is archived unchanged; **Protocol A.1** (`protocol/PROTOCOL_A1.md`, five\npre-registered noise seeds, floor = max over seeds) replaces it. In the current\nformal paired comparison of all 254 development materials, the operative A.1\nfloor is a median of approximately **1.6×10^4** times the archived Protocol A\nfloor. The older ~8,700× intermediate summary is superseded for submission\nwording. Every probe-dependent number below is restated under A.1, with the\narchived A value kept in brackets and marked *archived*. Codec rows of the\nmaster table are probe-independent and unaffected.",
    'claim correction record')

claim = claim.replace('`results/stability/eligibility_summary_a1.csv`', '`stability/eligibility_summary_A1.csv`')
claim = claim.replace('`results/stability/stability_floor_noise_seeds.csv`', '`stability/stability_floor_A1_per_seed.csv`')
claim = claim.replace('`results/stability/PROTOCOL_A1.md`', '`protocol/PROTOCOL_A1.md`')
claim = claim.replace('`results/stability/probe_calibration.csv`', '`stability/probe_calibration.csv`')
claim = claim.replace('`results/honest_benchmark/summary_a1.csv`', '`benchmark/summary_a1.csv`')

claim = replace_once(claim, 'Under A.1 the bulk median floor is 3.3e-04 e', 'Under A.1 the development-bulk median floor is 6.729e-04 e', 'claim 5 floor median')

old = "Lossy, **Protocol A.1, τ = 1e-2 e, best certified ratio, median [95% CI]**: bulk SZ3 52.0x [48.0, 61.7], ZFP 30.0x [27.2, 31.7], SPERR 11.6x [10.1, 13.4]; slab SZ3 69.6x [65.9, 72.3], ZFP 40.5x [37.0, 44.9]; certified fraction 94-99% bulk, 70-97% slab; 18 bulk and 7 slab materials non-evaluable and reported as such"
new = "Lossy, **Protocol A.1, τ = 1e-2 e, best certified ratio, median [95% CI]** from the current frozen summary: bulk SZ3 51.8x [47.7, 60.3], ZFP 30.0x [27.1, 31.9], SPERR 11.5x [10.1, 13.2]; slab SZ3 67.8x [59.6, 70.6], ZFP 40.5x [35.8, 44.9], SPERR 8.1x [7.7, 8.6]; certified fractions 95.2%/98.8%/95.8% for bulk SZ3/ZFP/SPERR and 77.0%/96.7%/77.0% for slab SZ3/ZFP/SPERR; 18 bulk and 7 slab materials non-evaluable and reported as such"
claim = replace_once(claim, old, new, 'claim 8 rate-fidelity')

old = "float32 round trip creates a median 82 exact neighbour ties and reassigns zero voxels in 62% of systems; noise of the same or 100x smaller amplitude reassigns hundreds. Noise/f32 floor ratio median 8 700. Single-seed verdicts flip in 35/319 (1e-4), 17/319 (1e-3), 2/319 (1e-2) against the 5-seed maximum"
new = "in the 18-material pre-freeze calibration, the float32 round trip creates a median 82 exact neighbour ties and reassigns zero voxels in 9/18 systems, whereas same-amplitude primary-seed noise creates no exact ties and reassigns zero voxels in only 2/18. In the formal 254-material paired development comparison, the five-seed A.1/archived-floor median shift is ~1.6×10^4. Primary-seed verdicts differ from the five-seed maximum in 35/319 (1e-4), 17/319 (1e-3), 2/319 (1e-2)"
claim = replace_once(claim, old, new, 'claim 13 probe numbers')

old = 'Float32 probe is order-preserving; understates the floor ~8 700x. Archived, marked PROVISIONAL / archived; A.1 values replace them'
new = 'Float32 probe is order-preserving and understates the floor substantially. The older ~8,700x intermediate summary is superseded for submission wording by the formal five-seed A.1 paired-development median shift of ~1.6×10^4. Archived A remains PROVISIONAL / archived; A.1 values replace it'
claim = replace_once(claim, old, new, 'retracted floor ratio wording')

claim_path.write_text(claim, encoding='utf-8')

# -----------------------------------------------------------------------------
# Align figure map with the actual polished manuscript and current Figure 4.
# -----------------------------------------------------------------------------
fig_path = ROOT / 'paper/FIGURE_MAP.md'
fig = fig_path.read_text(encoding='utf-8')
fig = replace_once(fig, '**Working title:** *Stability-Qualified Certification of Lossy Compression for Electronic-Density QoIs*', '**Working title:** *Stability-qualified benchmarks for scientific compression of electronic densities*', 'figure map title')

old = "Across 319 systems, A.1 non-evaluable fractions are 79.9% at `1e-4 e`, 41.4% at `1e-3 e`, and 9.7% at `1e-2 e`.\n\n**Take-home:** the qualification probe itself must excite the numerical failure channel relevant to the downstream operator."
new = "Across 319 systems, A.1 non-evaluable fractions are 79.9% at `1e-4 e`, 41.4% at `1e-3 e`, and 9.7% at `1e-2 e`. In the 18-material pre-freeze calibration, archived float32 rounding creates a median of 82 exact neighbouring ties and zero voxel reassignment in 9/18 systems, versus 2/18 under the same-amplitude primary noise probe. In the formal paired comparison of all 254 development materials, the operative five-seed A.1 floor is a median of approximately **1.6×10^4** times the archived Protocol A floor.\n\n**Take-home:** the qualification probe itself must excite the numerical failure channel relevant to the downstream operator."
fig = replace_once(fig, old, new, 'figure 4 quantitative alignment')

old = "1. Define Protocol A.1 eligibility and the three-state state space.\n2. **Figure 3:** demonstrate that naive binary benchmarking is materially invalid at strict Bader thresholds.\n3. **Figure 2:** provide operator-level motivation/background evidence. In page layout Figure 2 may precede Figure 3, but the prose must keep Figure 3 as the novelty-bearing result.\n4. **Figure 4:** validate the stability probe and the A -> A.1 correction.\n5. Report the tight-ladder result conservatively: at `1e-4 e`, median resolved-Bader-error/A.1-floor is 1.09-1.33× across codecs; call this floor-scale and consistent with an emerging analysis-limited regime, not `plateau = floor`.\n6. **Figure 5:** explain Bader domain migration.\n7. **Figure 6:** control nominal-versus-realized distortion.\n8. Report rate-fidelity only among eligible material-threshold pairs.\n9. **Figure 7:** close with untouched external confirmation."
new = "1. **Figure 2:** establish the operator-level motivation/background on identical reconstructions; this is not the novelty claim.\n2. Define Protocol A.1 eligibility and the three-state state space.\n3. **Figure 3:** demonstrate that naive binary benchmarking is materially invalid at strict Bader thresholds; keep Figure 3 as the novelty-bearing result.\n4. **Figure 4:** validate the stability probe and the A -> A.1 correction.\n5. Report the tight-ladder result conservatively: at `1e-4 e`, median resolved-Bader-error/A.1-floor is 1.09-1.33× across codecs; call this floor-scale and consistent with an emerging analysis-limited regime, not `plateau = floor`.\n6. **Figure 5:** explain Bader domain migration.\n7. **Figure 6:** control nominal-versus-realized distortion.\n8. Report rate-fidelity only among eligible material-threshold pairs, using `benchmark/summary_a1.csv` rather than historical prose values.\n9. **Figure 7:** close with untouched external confirmation."
fig = replace_once(fig, old, new, 'figure map results order')
fig_path.write_text(fig, encoding='utf-8')

# -----------------------------------------------------------------------------
# Record which SI objects are currently safe to cite.
# -----------------------------------------------------------------------------
xref_path = ROOT / 'paper/SUPPLEMENTARY_CROSS_REFERENCE_PLAN_20260911.md'
xref = xref_path.read_text(encoding='utf-8')
anchor = "Updated 2026-09-11. This map specifies where each Supplementary object should be cited in the polished manuscript. It is a build plan rather than a second narrative: the main text keeps the central claims, while the SI carries detailed denominators, sensitivity analyses and robustness evidence."
addition = anchor + "\n\n**Current insertion state (submission audit 2026-09-11):** Tables S1–S7 exist as submission-facing drafts; Supplementary Figs. S1, S2 and S7 are formally locked. The polished manuscript now cites only built/locked SI objects (S1–S4, S6–S7; Figs. S1, S2, S7). References to Tables S8–S14 and Figs. S3–S6/S8 remain deferred until those objects are built and locked."
xref = replace_once(xref, anchor, addition, 'SI current insertion state')
xref_path.write_text(xref, encoding='utf-8')

# -----------------------------------------------------------------------------
# Deterministic audit report.
# -----------------------------------------------------------------------------
audit = f"""# Numeric and cross-reference audit — 2026-09-11

**Scope:** reader-facing polished manuscript, Figures 1–7, currently built Supplementary objects, claim–evidence registry, and machine-readable source-of-record tables.

**Overall status: PASS AFTER CORRECTIONS.** The headline benchmark-validity numbers were already consistent. Three stale intermediate values were found and corrected: the Protocol A calibration zero-reassignment percentage, the Protocol A.1/archived floor-shift factor used in prose, and the development `1e-2 e` rate–fidelity summary. A stale development-bulk A.1 median floor in the claim–evidence matrix was also corrected.

## High-risk numeric audit

| Claim / object | Source of record | Recomputed value | Submission status |
|---|---|---:|---|
| Development reconstruction corpus | `benchmark/master_benchmark_full.csv` / operator audits | 254 systems; 6,343 rows | PASS |
| Stability universe | `stability/eligibility_summary_A1.csv` | 319 systems | PASS |
| A.1 non-evaluable fraction | `stability/eligibility_summary_A1.csv` | 79.94% / 41.38% / 9.72% at 1e-4 / 1e-3 / 1e-2 e | PASS |
| Figure 3 naive failures reclassified | `analysis/certifiability_reclassification_pooled_20260911.csv` | 518/533 = 97.2%; 296/310 = 95.5%; 61/108 = 56.5% | PASS |
| Figure 3 naive passes non-evaluable | same | 106/229 = 46.3% at 1e-4 e | PASS |
| Protocol A calibration: exact neighbour ties | `stability/probe_calibration.csv` | median {int(median_ties)} under archived float32 | PASS |
| Protocol A calibration: zero voxel reassignment | same | archived float32 {f32_zero}/18; same-amplitude primary noise {noise_zero}/18 | **CORRECTED** (old prose said 62%) |
| Formal A.1/archived floor shift | `stability/stability_floor_A1.csv` + archived table; Figure 4 calculation | n={len(paired)} paired development materials; median {median_shift:.3g}x (~1.6e4x) | **CORRECTED** (old prose used ~8.7e3 and wrong population label) |
| Development-bulk A.1 floor median | `stability/eligibility_summary_A1.csv` | 6.729e-4 e | **CORRECTED** in claim–evidence matrix |
| Strict certified error/A.1 floor | `supplement/S2_floor_relative.csv` | ZFP 1.091; SZ3 1.329; SPERR 1.232 median at 1e-4 e | PASS |
| Matched realized-Linf Bader effects | `analysis/matched_realized_linf_v1/REPORT.md` | ZFP/SZ3 0.557; ZFP/SPERR 0.601; SZ3/SPERR 1.033 | PASS |
| External eligibility | `external_summary_a1.csv` | 16/63; 42/63; 57/63 | PASS |
| External median CCR | `external_summary_a1.csv` | 1e-2 e: ZFP 40.57x; SZ3 65.89x; SPERR 10.82x | PASS |

## Corrected development rate–fidelity values at 1e-2 e

The polished manuscript and claim–evidence registry now use `benchmark/summary_a1.csv` directly.

| Stratum | Codec | n admitted | Certified fraction | Median CCR [95% bootstrap CI] |
|---|---|---:|---:|---:|
| bulk | SZ3 | 168 | 95.2% | 51.8x [47.7, 60.3] |
| bulk | ZFP | 168 | 98.8% | 30.0x [27.1, 31.9] |
| bulk | SPERR | 168 | 95.8% | 11.5x [10.1, 13.2] |
| slab | SZ3 | 61 | 77.0% | 67.8x [59.6, 70.6] |
| slab | ZFP | 61 | 96.7% | 40.5x [35.8, 44.9] |
| slab | SPERR | 61 | 77.0% | 8.1x [7.7, 8.6] |

Historical prose values such as bulk SZ3 52.0x [48.0, 61.7] and slab SZ3 69.6x [65.9, 72.3] are intermediate summaries and must not be used in the final submission package.

## Figure-by-figure consistency

- **Figure 1:** conceptual measurement contract; no high-risk numerical statistic.
- **Figure 2:** electron-count 3,205/1,383 result and Hartree 6,270-row / slope 1.02 / material-R2 statistics agree with the dedicated operator audits.
- **Figure 3:** 762 decisions per threshold and all binary-to-three-state counts agree with the frozen pooled reclassification CSV and Supplementary Table S4.
- **Figure 4:** manuscript wording now matches the pre-freeze 18-material calibration and the current formal paired-development Figure 4 calculation. The historical ~8,700x statement is not used as the current five-seed A.1/archived comparison.
- **Figure 5:** mechanism statements remain qualitative/representative in the polished manuscript and do not overgeneralize basin migration to arbitrary QoIs.
- **Figure 6:** equal-nominal realized-Linf ratios and 0.10-dex matched effects agree with `analysis/matched_realized_linf_v1/REPORT.md`.
- **Figure 7:** 63 systems, 1,689 retained rows, 0 material failures, 0 bound violations, 3 row-level Bader solver failures, eligibility 16/42/57 and tolerance-dependent CCR values agree with the frozen external confirmatory files.

## Supplementary cross-reference state

Safe to cite now:
- Tables **S1–S7** are built as submission-facing drafts.
- Figures **S1, S2 and S7** are locked R-generated objects.
- The polished manuscript currently inserts references only to built/locked objects needed for its present claims: **S1–S4, S6–S7 and Figs. S1, S2, S7**.

Deferred until built/locked:
- Tables S8–S14.
- Figures S3–S6 and S8.

This prevents the final Word/PDF from containing dangling Supplementary references.

## Denominator lock

Do not interchange these analysis universes:
- **254** = development benchmark.
- **319** = 254 development + 65 external descriptive/stability records.
- **65** = external descriptive/stability set.
- **63** = primary untouched confirmatory cohort.

## Submission rules frozen by this audit

1. Machine-readable tables override historical prose summaries.
2. `non-evaluable` is neither pass nor fail.
3. Figure 3 fractions use naive failures as denominators (533/310/108), not all 762 decisions.
4. The 46.3% value is 106/229 naive passes at 1e-4 e that are non-evaluable.
5. The `1e-4 e` floor result is **floor-scale / consistent with an emerging analysis-limited regime**, not a universal `plateau = floor` law.
6. Protocol A remains archived; Protocol A.1 is operative.
7. Development rate–fidelity values must be regenerated from `benchmark/summary_a1.csv` at build time.
8. External rate–fidelity values must be regenerated from the frozen 63-system confirmatory tables, not the 65-system descriptive aggregate.
"""
(ROOT / 'paper/NUMERIC_CROSS_REFERENCE_AUDIT_20260911.md').write_text(audit, encoding='utf-8')

print('PASS: submission consistency patch applied')
print(f'calibration median ties={median_ties}; float32 zero={f32_zero}/18; noise zero={noise_zero}/18')
print(f'paired development A1/archived median shift={median_shift:.6g}x, n={len(paired)}')
