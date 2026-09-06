# Pre-specified analysis plan for `mechanism/basin_error_decomposition_per_atom.csv`

Prepared before the full per-atom file is available on `main`. The purpose is to avoid choosing atom-level summaries after seeing the completed table.

## Scope and unit of inference

Expected structure: one row per atom for each successful `(material, codec, tolerance)` mechanism case, with row-wise identity

`dq_total = dq_integrand + dq_domain`.

Atoms are nested within codec/tolerance cases and materials. **Do not treat all atom rows as independent replicates.** Primary uncertainty and headline summaries will be computed at the case level and, where appropriate, bootstrapped at the material level.

The current summary table contains 106 successful cases from 12 representative materials. The per-atom file should reconcile exactly with those successful cases unless the producing script intentionally records additional cases.

## 1. Integrity checks — required before any scientific statistic

For every atom row:
1. Verify finite `dq_total`, `dq_integrand`, `dq_domain`.
2. Compute `closure_residual = dq_total - dq_integrand - dq_domain`.
3. Require max absolute closure residual to be at floating-point roundoff scale; flag any row >1e-12 e for inspection.
4. Verify unique atom identifiers within each `(material, codec, tolerance)` case.
5. Reconcile atom count per case with `natoms` in `materials_metadata.csv` / master benchmark where joinable.
6. Recompute the atom with maximum `|dq_total|` from the per-atom file and verify that its total/integrand/domain values match `mechanism/basin_error_decomposition_summary.csv`.
7. Verify that the case-level `frac_voxels_reassigned`, realized L∞ and compression ratio agree with the summary/master table.

No mechanism headline is updated until these checks pass.

## 2. Primary per-case mechanism statistics

For each successful case, compute:

### A. L1-weighted domain share across all atoms
`D_L1 = sum_a |dq_domain,a| / (sum_a |dq_domain,a| + sum_a |dq_integrand,a|)`

This is bounded in [0,1] and measures the relative magnitude of the two decomposition channels across the entire atomic charge vector.

### B. Maximum-error-atom bounded dominance
At `a* = argmax_a |dq_total,a|`:

`D_max = |dq_domain,a*| / (|dq_domain,a*| + |dq_integrand,a*|)`.

This should reproduce the current summary-level bounded-dominance statistic (median 0.995 before the full atom file lands).

### C. Fraction of atoms domain-dominant
`F_domain = mean_a( |dq_domain,a| > |dq_integrand,a| )`.

Report only after case-level aggregation; do not pool atoms across materials.

### D. Cancellation index
For each atom:

`C_a = 1 - |dq_total,a| / (|dq_domain,a| + |dq_integrand,a|)`

when the denominator is nonzero. `C_a` approaches 1 under strong cancellation and 0 when the two terms reinforce or one term dominates. Summarize per case using the median and value at the maximum-error atom.

This explicitly explains why `|domain|/|total|` can exceed 1 and should not be used as a dominance fraction.

### E. Charge-vector norms
Per case compute L∞ and L1 norms of the three atomic vectors:
- `||dq_total||∞`, `||dq_domain||∞`, `||dq_integrand||∞`
- `||dq_total||1`, `||dq_domain||1`, `||dq_integrand||1`

This prevents the mechanism conclusion from depending only on one selected atom.

## 3. Primary headline tests

The primary mechanism statement will be evaluated at the **case level**:

1. Distribution of `D_L1` across successful cases, with median/IQR and material-cluster bootstrap CI.
2. Distribution of `D_max`, for direct reconciliation with the existing summary analysis.
3. Fraction of cases with `D_L1 > 0.5`, `>0.9` and `D_max >0.9`.
4. Results stratified by codec, nominal tolerance and system type, but these are secondary unless sample sizes support them.
5. Leave-one-material-out sensitivity: recompute the headline median after dropping each of the 12 materials in turn. Report the range. This is essential because the mechanism set is small and deliberately representative.

## 4. Link to full-benchmark reassignment result

The per-atom table will be used to validate, not replace, the full-table attenuation result:

- Full-table result at A.1 tau=1e-3 e: codec-associated ~2x residual after controlling material and realized L∞ attenuates to ~1 after adding `frac_voxels_reassigned`.
- Per-atom mechanism test: relate case-level `D_L1` and `||dq_domain||∞` to `frac_voxels_reassigned` and realized L∞.

Because 106 cases are nested in 12 materials, use material-clustered or material-bootstrap uncertainty. Do not report a naive atom-level p-value.

Candidate secondary models:
- `log ||dq_domain||∞ ~ log realized_Linf + log(frac_voxels_reassigned + pseudocount) + codec + material FE`
- `log ||dq_total||∞ ~ log ||dq_domain||∞ + log ||dq_integrand||∞ + material FE`

These are descriptive/mechanism-consistency models, not causal mediation.

## 5. Symmetry / atom-label sensitivity

The known `aflow-Al8Cu4U1_ICSD_601801` symmetry-equivalent relabelling case demonstrates that position-indexed atomic charges can change by permutation even when the multiset of equivalent-atom charges is unchanged. If any of the 12 mechanism materials contain symmetry-equivalent atoms:

1. flag them using available symmetry metadata where possible;
2. compare position-indexed and within-equivalence-class sorted/multiset charge differences as a sensitivity analysis;
3. do not silently relabel the primary QoI—the protocol's position-indexed contract remains primary.

This prevents arbitrary equivalent-atom permutations from being misread as generic domain-migration chemistry.

## 6. Figure 3 update once the file lands

Preferred panels:
- **3a:** case-level paired/stacked `D_L1` and complementary integrand share, 12 materials × codecs/tolerances summarized without atom pseudoreplication.
- **3b:** `||dq_domain||∞` and `||dq_integrand||∞` versus realized L∞, connected within material.
- **3c:** illustrative atom-level decomposition for one pre-existing representative case, including signs to show cancellation.
- **3d:** full-benchmark reassignment attenuation (already computed), visually linking the representative direct decomposition to the 254-material pattern.

The figure caption must state that the 12-material set is representative and mechanism-focused, not a random sample from which full-corpus prevalence is inferred.

## 7. Decision rule for upgrading the general mechanism claim

- **CONFIRMED for representative mechanism set** if integrity checks pass and both `D_L1` and `D_max` show strong domain dominance robust to leave-one-material-out analysis.
- **Do not generalize to the full 254-material corpus** merely because the atom-level table contains many rows; there are still only 12 mechanism materials.
- Full-corpus language may say that the representative direct decomposition and the full-table reassignment attenuation are mutually consistent evidence for basin migration as the mechanism behind the codec-associated residual.
