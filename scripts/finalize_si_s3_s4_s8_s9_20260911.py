#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new, label):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'{label}: expected 1 match in {path}, found {n}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


def append_once(path, marker, addition, label):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if addition.strip() in text:
        return
    if marker not in text:
        raise RuntimeError(f'{label}: marker not found in {path}')
    p.write_text(text.replace(marker, addition + '\n\n' + marker, 1), encoding='utf-8')

# 1) Claim registry stale path.
replace_once(
    'paper/CLAIM_EVIDENCE_MATRIX.md',
    '`results/stability/eligibility_by_threshold_a1.csv`',
    '`stability/eligibility_by_threshold_A1.csv`',
    'Claim 7 eligibility path')

# 2) Polished manuscript: now-safe Supplementary references.
replace_once(
    'paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md',
    'Tight conservation of a global integral therefore does not certify atom-resolved charge fidelity.',
    'Tight conservation of a global integral therefore does not certify atom-resolved charge fidelity. The full codec- and tolerance-resolved negative-control matrix is reported in Supplementary Table S8 and Supplementary Fig. S3.',
    'manuscript S8/S3 electron reference')
replace_once(
    'paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md',
    'The response is therefore close to first order over the measured range.',
    'The response is therefore close to first order over the measured range. Full codec-level scaling, material-level smoothness and reproduction-gate diagnostics are provided in Supplementary Table S9 and Supplementary Fig. S3.',
    'manuscript S9/S3 Hartree reference')
replace_once(
    'paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md',
    'Threshold- and codec-resolved error-to-floor distributions are reported in Supplementary Table S6.',
    'Threshold- and codec-resolved error-to-floor distributions and the frozen tight-ladder diagnostic are reported in Supplementary Table S6 and Supplementary Fig. S4.',
    'manuscript S4 reference')

# 3) Supplementary captions: add S3/S4 before interpretation boundary.
caption_block = '''## Supplementary Figure S3 | Extended operator controls separate global, smooth nonlocal and topology-sensitive QoIs

**A,** Electron-count error versus re-derived Bader-charge error across finite development reconstructions. The dashed thresholds mark |ΔNe| = 10^-4 e and Bader error = 10^-3 e; 1,383 of 3,205 reconstructions (43.15%) that satisfy the electron-count threshold still exceed the Bader threshold. **B,** Paired material-level goodness of fit for Hartree-potential and Bader response across 678 material–codec pairs with at least five reproduction-gate-passing rows. **C,** Strict monotonicity resolved by bulk/slab stratum and codec. Hartree response is substantially smoother overall, while the slab result is intentionally retained as a caveat against claiming universal monotonicity. **D,** Dispersion of re-derived Bader error within 0.5-decade Hartree-error bins containing at least 10 rows; 3,452 of 6,229 rows (55.4%) lie in bins with Bader P90/P10 ≥ 10. Together these controls show that similar global or smooth nonlocal fidelity does not uniquely determine the topology-sensitive Bader response.

**Sources:** `analysis/electron_count_qoi/electron_bader_decoupling.csv`; `analysis/hartree_potential_expansion/group_summary.csv`; `analysis/hartree_potential_expansion/material_smoothness.csv`; `analysis/hartree_potential_expansion/matched_error_dispersion.csv`.

**R source:** `figures/R/supplement/figureS3_operator_controls.R`.

## Supplementary Figure S4 | The strictest certified Bader regime is floor-scale, not a universal plateau

**A,** Re-derived Bader error normalized by the independently measured Protocol A.1 stability floor for one highest-rate certified reconstruction per material–codec pair. Points show the median and bars the P10–P90 range. At 10^-4 e, median error/floor is 1.09 for ZFP, 1.33 for SZ3 and 1.23 for SPERR. **B,** Material-level relation between the Protocol A.1 floor and the best-certified re-derived Bader error at the 10^-4 e contract (n = 123 certified material–codec decisions); the dashed diagonal denotes equal scales. **C,** Median and interquartile range of error/floor across the frozen tight ladder as a function of nominal relative codec tolerance. This panel is descriptive and is not used as a material-level plateau estimator. The strictest certified regime is therefore floor-scale and consistent with an emerging analysis-limited regime, but the data do not establish a universal identity between a compression plateau and the Protocol A.1 floor.

**Sources:** `supplement/S2_floor_relative.csv`; `benchmark/master_benchmark_full.csv`; `benchmark/master_benchmark_tight_ladder.csv`.

**R source:** `figures/R/supplement/figureS4_tight_floor_scale.R`.'''
append_once(
    'paper/SUPPLEMENTARY_FIGURE_CAPTIONS_20260911.md',
    '## Interpretation boundary',
    caption_block,
    'S3/S4 captions')

# 4) Asset registry statuses.
replace_once(
    'paper/SUPPLEMENTARY_ASSET_MAP_20260911.md',
    '| Note 3 | Eligibility and certification sensitivity | `supplement/S1_S3_sensitivity.csv`; `supplement/S2_floor_relative.csv`; `supplement/S4_amplitude_sensitivity.csv`; `stability/stability_floor_A1_per_seed.csv` | Tables S5-S7; Figs. S2, S4 | **TABLES S5-S7 READY; S2 LOCKED; S4 PLANNED R** |',
    '| Note 3 | Eligibility and certification sensitivity | `supplement/S1_S3_sensitivity.csv`; `supplement/S2_floor_relative.csv`; `supplement/S4_amplitude_sensitivity.csv`; `stability/stability_floor_A1_per_seed.csv` | Tables S5-S7; Figs. S2, S4 | **TABLES S5-S7 READY; FIGS. S2/S4 LOCKED** |',
    'asset map Note 3')
replace_once(
    'paper/SUPPLEMENTARY_ASSET_MAP_20260911.md',
    '| Note 4 | Electron-count and Hartree controls | `analysis/electron_count_qoi/`; `analysis/hartree_potential_expansion/` | Tables S8-S9; Fig. S3 | **READY; S3 SOURCE READY** |',
    '| Note 4 | Electron-count and Hartree controls | `analysis/electron_count_qoi/`; `analysis/hartree_potential_expansion/` | Tables S8-S9; Fig. S3 | **TABLES S8-S9 READY; FIG. S3 LOCKED** |',
    'asset map Note 4')

s3s4_registry = '''### Supplementary Figure S3 — extended operator controls

- **Role:** expands Figure 2 with the full electron-count negative control, material-level Hartree/Bader smoothness comparison, bulk/slab monotonicity nuance and matched-Hartree Bader dispersion.
- **R source:** `figures/R/supplement/figureS3_operator_controls.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS3_operator_controls_R.{png,pdf,svg}`.
- **Final CI:** GitHub Actions run `34574517842`; artifact `10189104659`; source commit `4b98758b997ae03c57e62441e3a9500dfaf82e26`.
- **Visual inspection:** PASS. Four panels are legible with no clipping/collision; the slab monotonicity caveat remains visible rather than being averaged away.
- **Repository outputs:** PNG 683,983 B; PDF 58,131 B; SVG 235,326 B.
- **Blob SHAs:** PNG `c38446463ab62064029d6088fa904ec424f7dbbf`; PDF `780b4ab3b15e6a18bdca9039b2081b7c666c1575`; SVG `95a108e8e70fb6d657b51f9be8a68c7810efd4b7`.
- **Interpretation lock:** operator-control evidence only; it motivates explicit downstream evaluation but does not replace the Figure 3 benchmark-validity claim.
- **Status:** **LOCKED 2026-09-11**.

### Supplementary Figure S4 — strict certified regime relative to the A.1 floor

- **Role:** tests where certified Bader reconstruction error sits relative to the independently measured Protocol A.1 numerical floor.
- **R source:** `figures/R/supplement/figureS4_tight_floor_scale.R`.
- **Outputs:** `figures/R/rendered/supplementary_figureS4_tight_floor_scale_R.{png,pdf,svg}`.
- **Final CI:** GitHub Actions run `34584885979`; artifact `10193221595`; source commit `cafc9767a2060a85a7268fe02907fef5000569b0`.
- **Visual inspection:** PASS after title-layout refinement. No panel-title clipping, axis collision or legend collision remains.
- **Repository outputs:** PNG 550,537 B; PDF 16,413 B; SVG 41,996 B.
- **Blob SHAs:** PNG `f01594994769d21bbf90449c2421c5058cf03859`; PDF `189158ae2b3251a733741674e98e7c5c1b341a80`; SVG `5f6dea59561b860d03d4cafcd137d792ba6ef97a`.
- **Interpretation lock:** at 10^-4 e the certified error is floor-scale (median error/floor 1.09–1.33 across codecs), consistent with an emerging analysis-limited regime. This figure does **not** establish `plateau = floor` as a universal law.
- **Status:** **LOCKED 2026-09-11**.'''
append_once(
    'paper/SUPPLEMENTARY_ASSET_MAP_20260911.md',
    '### Supplementary Figure S7 — codec-resolved reclassification',
    s3s4_registry,
    'asset map S3/S4 registry')

replace_once(
    'paper/SUPPLEMENTARY_ASSET_MAP_20260911.md',
    '### Table S8 — electron-count control\n\nUse `analysis/electron_count_qoi/summary_by_codec.csv` and `summary_by_tolerance.csv`; include the 3,205/1,383 decoupling result prominently.\n\n### Table S9 — Hartree control\n\nUse `analysis/hartree_potential_expansion/group_summary.csv` and `material_smoothness.csv`. A separate footnote should explain the 73 SZ3 reproduction-gate exclusions as platform byte-stream mismatches rather than field-reconstruction mismatches.',
    '### Tables S8–S9 — operator controls — **BUILT**\n\nSubmission-facing tables are generated deterministically in `paper/SUPPLEMENTARY_TABLES_S8_S9_20260911.md` by `scripts/build_supplement_tables_s8_s9_20260911.py` (CI run `34584427019`). Table S8 contains the pooled and codec-resolved electron-count/Bader decoupling matrix, including 1,383/3,205 = 43.15%. Table S9 contains the 6,270-row Hartree scaling summary, the 678-pair material-level smoothness audit, local elasticity ranges, the 22,296× Bader jump and the matched-Hartree 55.4% dispersion result. The reproduction-gate exclusion remains an infrastructure/platform caveat rather than a codec-fidelity failure.',
    'asset map S8/S9 table section')

replace_once(
    'paper/SUPPLEMENTARY_ASSET_MAP_20260911.md',
    '### Figure S3 — extended operator controls — **SOURCE READY**\n\nR source: `figures/R/supplement/figureS3_operator_controls.R`.\n\nPanels: electron-count/Bader decoupling; paired material-level Hartree/Bader R2; bulk/slab strict-monotonicity nuance; matched-Hartree Bader dispersion. Slab monotonicity caveat must remain visible in the caption.\n\n### Figure S4 — tight regime and floor scale — **PLANNED R**\n\nPlanned R source: `figures/R/supplement/figureS4_tight_floor_scale.R`.\n\nPanels: error/floor summary by codec and threshold; selected tight-ladder trajectories. Caption boundary: **floor-scale / emerging analysis-limited**, not `plateau = floor`.',
    '### Figure S3 — extended operator controls — **LOCKED**\n\nSee locked-figure registry above.\n\n### Figure S4 — tight regime and floor scale — **LOCKED**\n\nSee locked-figure registry above.',
    'asset map S3/S4 build plan')
replace_once(
    'paper/SUPPLEMENTARY_ASSET_MAP_20260911.md',
    '1. **Figures S3-S6 and S8 remain to be formally rendered/locked.** S3 already has formal R source; S4-S6/S8 are presentation/build tasks, not new experiments.\n2. **Tables S8-S14 remain to be finalized.** S10-S12/S14 require compact aggregation; no new core scientific experiment is required.\n3. **Table S13 must be regenerated from final machine-readable sources.** Historical prose contains intermediate rate-fidelity values and should not be treated as canonical.\n4. Before submission, explicitly document the membership relationship between the 65-system external descriptive set and the 63-system confirmatory set in Table S1 or its footnote.',
    '1. **Figures S5, S6 and S8 remain to be formally rendered/locked.** These are presentation/build tasks from existing frozen analyses, not new core experiments.\n2. **Tables S10-S14 remain to be finalized.** S10-S12/S14 require compact aggregation; Table S13 requires deterministic regeneration from frozen development/external summaries.\n3. **Table S13 must be regenerated from final machine-readable sources.** Historical prose contains intermediate rate-fidelity values and should not be treated as canonical.\n4. Before submission, explicitly document the membership relationship between the 65-system external descriptive set and the 63-system confirmatory set in Table S1 or its footnote.',
    'asset map blockers')
replace_once(
    'paper/SUPPLEMENTARY_ASSET_MAP_20260911.md',
    'Canonical captions for S1/S2/S7 are in `paper/SUPPLEMENTARY_FIGURE_CAPTIONS_20260911.md`.',
    'Canonical captions for S1–S4 and S7 are in `paper/SUPPLEMENTARY_FIGURE_CAPTIONS_20260911.md`.',
    'asset map caption registry')

# 5) Cross-reference plan safe set.
replace_once(
    'paper/SUPPLEMENTARY_CROSS_REFERENCE_PLAN_20260911.md',
    '**Current insertion state (submission audit 2026-09-11):** Tables S1–S7 exist as submission-facing drafts; Supplementary Figs. S1, S2 and S7 are formally locked. The polished manuscript now cites only built/locked SI objects (S1–S4, S6–S7; Figs. S1, S2, S7). References to Tables S8–S14 and Figs. S3–S6/S8 remain deferred until those objects are built and locked.',
    '**Current insertion state (submission audit 2026-09-11):** Tables S1–S9 now exist as submission-facing objects; Supplementary Figs. S1–S4 and S7 are formally locked. The polished manuscript cites the built/locked objects needed for its current claims, including the operator-control Tables S8–S9/Fig. S3 and floor-scale Fig. S4. References to Tables S10–S14 and Figs. S5–S6/S8 remain deferred until those objects are built and locked.',
    'crossref insertion state')

# 6) SI draft status table/figure table and prose state.
replace_once(
    'paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md',
    '| **Table S8** | Electron-count control by codec/tolerance | `analysis/electron_count_qoi/summary_by_codec.csv`; `summary_by_tolerance.csv` | **READY** |',
    '| **Table S8** | Electron-count control by codec/tolerance | `analysis/electron_count_qoi/electron_bader_decoupling.csv` | **BUILT** — `paper/SUPPLEMENTARY_TABLES_S8_S9_20260911.md` |',
    'SI draft S8 status')
replace_once(
    'paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md',
    '| **Table S9** | Hartree pooled scaling, material smoothness and reproduction gate | `analysis/hartree_potential_expansion/group_summary.csv`; `material_smoothness.csv`; `gate_failures.csv` | **READY** |',
    '| **Table S9** | Hartree pooled scaling, material smoothness and reproduction gate | `analysis/hartree_potential_expansion/group_summary.csv`; `material_smoothness.csv`; `matched_error_dispersion.csv` | **BUILT** — `paper/SUPPLEMENTARY_TABLES_S8_S9_20260911.md` |',
    'SI draft S9 status')
for num, oldsrc in [
    ('S1', '`stability/stability_floor_A1.csv`; archived A; `eligibility_summary_A1.csv`'),
    ('S2', '`stability/stability_floor_A1_per_seed.csv`; `supplement/S4_amplitude_sensitivity.csv`'),
    ('S3', '`analysis/electron_count_qoi/`; `analysis/hartree_potential_expansion/`'),
    ('S4', '`supplement/S2_floor_relative.csv`; `benchmark/master_benchmark_tight_ladder.csv`'),
    ('S7', '`analysis/certifiability_reclassification_by_codec_20260911.csv`')]:
    old = f'| **Fig. {num}** |'
# exact row replacements below
replace_once('paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md', '| **Fig. S1** | Protocol A vs A.1 stability-floor distribution and threshold eligibility | `stability/stability_floor_A1.csv`; archived A; `eligibility_summary_A1.csv` | **PLANNED R** |', '| **Fig. S1** | Protocol A vs A.1 stability-floor distribution and threshold eligibility | `stability/stability_floor_A1.csv`; archived A; `eligibility_summary_A1.csv` | **LOCKED** |', 'SI draft S1 figure status')
replace_once('paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md', '| **Fig. S2** | Five-seed spread and ×0.1/×1/×10 amplitude sensitivity | `stability/stability_floor_A1_per_seed.csv`; `supplement/S4_amplitude_sensitivity.csv` | **PLANNED R** |', '| **Fig. S2** | Five-seed spread and ×0.1/×1/×10 amplitude sensitivity | `stability/stability_floor_A1_per_seed.csv`; `supplement/S4_amplitude_sensitivity.csv` | **LOCKED** |', 'SI draft S2 figure status')
replace_once('paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md', '| **Fig. S3** | Full electron-count and Hartree control distributions | `analysis/electron_count_qoi/`; `analysis/hartree_potential_expansion/` | **PLANNED R** |', '| **Fig. S3** | Full electron-count and Hartree control distributions | `analysis/electron_count_qoi/`; `analysis/hartree_potential_expansion/` | **LOCKED** |', 'SI draft S3 figure status')
replace_once('paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md', '| **Fig. S4** | Tight-regime Bader error/floor ratios and selected ladder trajectories | `supplement/S2_floor_relative.csv`; `benchmark/master_benchmark_tight_ladder.csv` | **PLANNED R** |', '| **Fig. S4** | Tight-regime Bader error/floor ratios and tight-ladder diagnostic | `supplement/S2_floor_relative.csv`; `benchmark/master_benchmark_tight_ladder.csv` | **LOCKED** |', 'SI draft S4 figure status')
replace_once('paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md', '| **Fig. S7** | Codec-resolved binary reclassification beyond pooled Figure 3 | `analysis/certifiability_reclassification_by_codec_20260911.csv` | **PLANNED R** |', '| **Fig. S7** | Codec-resolved binary reclassification beyond pooled Figure 3 | `analysis/certifiability_reclassification_by_codec_20260911.csv` | **LOCKED** |', 'SI draft S7 figure status')
replace_once(
    'paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md',
    '- **Supplementary tables:** 12/14 can be generated directly from existing tables; S11 and S14 require compact aggregation but no new scientific experiment.\n- **Supplementary figures:** source data are present, but final R renderings still need to be produced and locked.\n- **Highest-priority audit before final submission:** regenerate Table S13 from the final numerical source of record and explicitly document the 65-descriptive versus 63-confirmatory external-cohort relationship in the final SI build.',
    '- **Supplementary tables:** S1–S9 are now built as submission-facing drafts/objects; S10–S12/S14 require compact aggregation and S13 requires deterministic final regeneration. No new core scientific experiment is required.\n- **Supplementary figures:** S1–S4 and S7 are locked R figures; S5, S6 and S8 remain to be built/locked from existing frozen analyses.\n- **Highest-priority remaining build:** complete S10–S14 and Figures S5/S6/S8, then rerun the final manuscript ↔ SI cross-reference audit.',
    'SI completion assessment')

# 7) Supplement workspace README.
replace_once(
    'supplement/README.md',
    'Most tables are already backed by frozen CSV/JSON/Markdown evidence. The remaining work is primarily aggregation, R rendering, caption polishing and cross-reference validation rather than new experiments.',
    'Tables S1–S9 are now built as submission-facing drafts/objects, and Figures S1–S4 plus S7 are locked R-generated publication figures. The remaining work is primarily compact aggregation for S10–S14 and R rendering/locking for S5, S6 and S8 rather than new experiments.',
    'supplement README status')
replace_once(
    'supplement/README.md',
    '1. Build Tables S1–S4 and S6 directly from existing frozen tables.\n2. Render Figures S1–S2 (Protocol A.1 / seed / amplitude) because they are the most directly tied to benchmark validity.\n3. Render Figure S7 (codec-resolved reclassification) as the natural supplement to central Figure 3.\n4. Build the controls/mechanism/matching figures S3–S6.\n5. Regenerate Table S13 and Figure S8 from the final 63-system external confirmatory outputs.\n6. Aggregate failure/negative-result Table S14.\n7. Run final manuscript ↔ SI cross-reference audit before Word/PDF assembly.',
    '1. Build Tables S10–S11 and Figure S5 for Bader mechanism / independent-implementation robustness.\n2. Build Table S12 and Figure S6 for realized-distortion matching sensitivity.\n3. Regenerate Table S13 and Figure S8 from the final 63-system external confirmatory outputs and the current development `benchmark/summary_a1.csv`.\n4. Aggregate failure/negative-result Table S14.\n5. Run the final manuscript ↔ SI cross-reference audit, then assemble Word/PDF submission files.',
    'supplement README build order')

# 8) Numeric/cross-reference audit safe set.
replace_once(
    'paper/NUMERIC_CROSS_REFERENCE_AUDIT_20260911.md',
    'Safe to cite now:\n- Tables **S1–S7** are built as submission-facing drafts.\n- Figures **S1, S2 and S7** are locked R-generated objects.\n- The polished manuscript currently inserts references only to built/locked objects needed for its present claims: **S1–S4, S6–S7 and Figs. S1, S2, S7**.\n\nDeferred until built/locked:\n- Tables S8–S14.\n- Figures S3–S6 and S8.',
    'Safe to cite now:\n- Tables **S1–S9** are built as submission-facing drafts/objects.\n- Figures **S1–S4 and S7** are locked R-generated objects.\n- The polished manuscript currently cites built/locked operator-control, stability, reclassification and floor-scale SI objects as appropriate.\n\nDeferred until built/locked:\n- Tables S10–S14.\n- Figures S5, S6 and S8.',
    'numeric audit safe SI set')

print('PASS: finalized SI S3/S4 and Tables S8/S9 across manuscript and registries')
