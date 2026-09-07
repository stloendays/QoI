# Error-geometry residual permutation v0.1 — preregistration

Date frozen: 2026-09-07

## Scientific question

After controlling scalar error magnitude, a residual codec effect can still reflect unmeasured distributional summaries. This intervention asks a stronger causal question: **holding the actual codec residual values fixed, does changing only where those residual values occur in the density field change resolved Bader error and the codec contrast?**

This is a development-corpus mechanism test. It is separate from, and does not modify, Protocol A.1 or the frozen external confirmatory analysis.

## Frozen representative set

Use the already released representative mechanism set in `mechanism/basin_error_decomposition_summary.csv`.

Primary population: every material in that set satisfying all of the following before this test is run:

1. `domain == bulk`;
2. the source in `materials_metadata.csv` is `Materials Project`;
3. successful released mechanism records exist at relative tolerance `1e-3` for all three generic codecs ZFP, SZ3 and SPERR.

No material is selected or removed based on the direction or magnitude of the permutation outcome.

Primary operating point: relative tolerance **1e-3** for each codec, using the same codec configuration and absolute-bound definition as the benchmark (`abs_bound = relative_tolerance * source value_ptp`).

## Provenance gate

For every selected material:

- fetch the exact source object recorded in `materials_metadata.csv`;
- verify compressed-source SHA256 against the released metadata;
- reconstruct the source CHGCAR/grid;
- reproduce the unshuffled codec round trip with the pinned benchmark implementations;
- verify realized L-infinity and resolved-Bader error against the released benchmark/mechanism record to numerical tolerance.

A failed provenance gate is a hard implementation/provenance failure and is reported rather than silently excluded.

## Intervention

For each material and codec, let the actual codec reconstruction residual be

`delta(r) = rho_codec(r) - rho_original(r)`.

The **primary intervention** is a density-stratified spatial permutation:

1. rank all voxels by the original density `rho_original`;
2. partition the ranked voxels into **20 equal-count strata** (last stratum may differ by at most one voxel);
3. within each stratum independently, permute the existing residual values without replacement;
4. form `rho_shuffle(r) = rho_original(r) + delta_permuted(r)`;
5. re-run the same resolved Bader analysis.

This preserves the residual value multiset exactly, hence preserves global L-infinity, L1, L2, RMSE, mean signed error, and the full residual histogram. Stratification additionally preserves the residual distribution conditional on coarse original-density rank while destroying its fine spatial organization.

Permutation seeds are frozen as **1701, 1702, 1703, 1704, 1705**.

## Required audits

For every shuffled field record:

- maximum absolute difference between original and shuffled residual L-infinity;
- RMSE difference;
- mean signed-error difference;
- mean absolute-error difference;
- resolved Bader error;
- fraction of voxels reassigned relative to the original Bader partition;
- Bader solver success/failure.

Norm-preservation differences must be at floating-point roundoff. Solver failures remain explicit outcomes and are never silently dropped.

## Estimands

### 1. Within-codec spatial sensitivity

For each material, codec and seed:

`S = log10(Bader_error_shuffled / Bader_error_observed)`.

Report the seed-median `S` per material/codec and the corresponding fold change. This directly quantifies how much chemical error changes when residual amplitudes are held fixed and only their spatial assignment is perturbed.

### 2. Codec-advantage attenuation

For each material and seed define, for ZFP versus comparator C:

`A_C = log10(error_ZFP_shuffled / error_C_shuffled) - log10(error_ZFP_observed / error_C_observed)`.

Positive `A_C` means the observed ZFP advantage is attenuated when codec-specific spatial organization is destroyed while each codec's residual amplitudes remain fixed.

Primary contrasts:

- ZFP vs SZ3;
- ZFP vs SPERR.

Material-level attenuation is the median across the five frozen seeds. Population summaries are the median across materials with 95% percentile CIs from 5,000 material-level bootstrap resamples using deterministic SHA256-derived seeds with master label `20260907`.

## Interpretation rules

- If the attenuation CI is entirely above zero for a ZFP contrast, we may state that codec-specific spatial organization contributes to the observed ZFP chemical-fidelity advantage in this representative bulk mechanism set.
- If both ZFP contrast CIs are entirely above zero, the stronger two-comparator statement is allowed.
- Regardless of direction, reproducible changes in resolved Bader error under the norm- and histogram-preserving intervention demonstrate that Bader fidelity depends on the spatial assignment of error, not only on scalar amplitude summaries.
- Population-wide universality must not be claimed from this representative mechanism set.

No outcome from this test may be used to alter codec parameters, tolerance ladders, Protocol A.1 eligibility, or the frozen external confirmatory design.
