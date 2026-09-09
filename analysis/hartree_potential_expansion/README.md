# Hartree-potential QoI full expansion

Status: **protocol defined; computation must use the frozen RhoCodec codec implementations**.

This extension follows the successful 12-material ZFP pilot in `analysis/hartree_potential_pilot/` and does not modify Protocol A/A.1 or `benchmark/master_benchmark_full.csv`.

## Scientific question

Does the contrast observed in the pilot generalize across the development corpus and all three frozen codecs?

- smooth, nonlocal QoI: periodic electronic Hartree potential, `V(G)=4*pi*rho(G)/|G|^2`, `G!=0`, `G=0 -> 0`;
- topology-dependent QoI: re-solved Bader charge error already stored in the frozen master table.

Primary hypothesis: Hartree-potential error should vary smoothly and approximately linearly with realized density perturbation, whereas Bader error should show substantially weaker monotonicity and larger local jumps because the integration domains depend on density topology.

## Frozen inputs

- `benchmark/master_benchmark_full.csv` (read only)
- `materials_metadata.csv`
- `analysis/mp_chgcar_loader.py` (extracted verbatim from the original RhoCodec loader, with validation checks)
- original RhoCodec implementations of ZFP 1.0.1, SZ3 and SPERR used to generate the frozen benchmark

## Population

Use every development-corpus material represented in the frozen benchmark, including both `bulk` and `slab`, subject only to successful source-density loading and a finite frozen re-solved Bader result for the corresponding row.

Run all three codecs: `ZFP`, `SZ3`, `SPERR`.

The preferred analysis uses the complete frozen tolerance ladder for each `(material_id, codec)` pair. If runtime is prohibitive, the pre-declared reduced ladder is 7 approximately log-spaced rows spanning each pair's available realized-Linf range; selection must be based only on realized-Linf rank, not Bader or Hartree results.

## Reproduction gate

A regenerated row may inherit the frozen Bader result only when both conditions hold:

1. `0.95 <= reproduced_realized_Linf / frozen_realized_Linf <= 1.05`;
2. reproduced compressed byte count equals the frozen byte count when the original codec wrapper exposes a deterministic byte stream/size.

Report gate failures explicitly. Do not silently substitute or interpolate Bader values.

## Hartree metric

For each original density and regenerated reconstruction:

`potential_rel_RMSE = RMS(V_recon - V_orig) / RMS(V_orig)`

Also retain:

- `potential_rel_Linf`
- `realized_Linf`
- `realized_Linf_over_ptp`
- `rmse_density`
- `Bader_error_resolved_e`
- `Bader_error_fixed_e`
- `frac_voxels_reassigned`
- `compression_ratio`
- `system_type`
- `codec`

## Pre-declared analyses

### 1. Pooled scaling

For each codec and system type, fit on log10 scale:

- Hartree error vs realized Linf;
- Bader error vs realized Linf.

Report slope, R2, Pearson and Spearman correlations.

### 2. Material-level smoothness

For every `(material_id, codec)` with at least 5 gate-passing rows, report:

- monotone nondecreasing flag;
- number of local decreases;
- log-log slope and R2;
- local elasticity range;
- maximum consecutive jump ratio;
- dynamic range.

Compare the distributions for Hartree and Bader.

### 3. Matched-error dispersion

Bin rows by `potential_rel_RMSE` in 0.5-decade bins. Within each bin, quantify the spread of Bader error as `P90/P10` and `max/min` (with a small reporting floor only for ratios). This tests whether similar smooth-field fidelity can coexist with widely different topological-QoI errors.

### 4. Bulk/slab robustness

Repeat the principal summaries separately for `bulk` and `slab`. A main-text mechanistic claim requires the qualitative hierarchy to reproduce in both system types.

### 5. Codec robustness

A main-text mechanistic claim requires the hierarchy to reproduce independently in ZFP, SZ3 and SPERR; pooled-only significance is insufficient.

## Main-text promotion criteria

Promote this result from SI/pilot to the manuscript body only if all are met:

1. >=95% of regenerated rows pass the reconstruction gate for each codec;
2. for every codec, median material-level Hartree log-log R2 >=0.95;
3. for every codec, Hartree monotonicity fraction exceeds Bader monotonicity fraction by >=30 percentage points;
4. Hartree-vs-Linf pooled R2 exceeds Bader-vs-Linf pooled R2 in both bulk and slab;
5. at least two codecs show >=1 decade of Bader-error spread within matched Hartree-error bins over a nontrivial fraction of the corpus.

If these criteria fail, retain the 12-material ZFP pilot in SI only and do not broaden the manuscript claim.

## Required outputs

`analysis/hartree_potential_expansion/`

- `rows.csv`
- `group_summary.csv`
- `material_smoothness.csv`
- `matched_error_dispersion.csv`
- `gate_failures.csv`
- `provenance.json`
- `RESULTS.md`

`RESULTS.md` must end with exactly one recommendation: `PROMOTE_TO_MAIN_TEXT`, `KEEP_IN_SI`, or `DROP_EXTENSION`.
