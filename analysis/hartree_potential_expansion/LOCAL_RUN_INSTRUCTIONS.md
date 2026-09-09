# Local execution contract

Run this expansion in the same local RhoCodec/CatalystForge environment that generated the frozen benchmark. Do not substitute new codec versions.

## Required environment

- original RhoCodec source tree (local path previously identified as `D:/Research/RhoCodec`)
- the codec wrappers/versions used by the frozen benchmark for ZFP, SZ3 and SPERR
- Python environment compatible with the frozen run (`zfpy 1.0.1` for ZFP)
- `analysis/mp_chgcar_loader.py` from this repository

## Required computation

Generate `analysis/hartree_potential_expansion/rows.csv` with one row for every regenerated frozen benchmark row included by the expansion protocol.

The minimum required columns are:

- `material_id`
- `formula`
- `system_type`
- `codec`
- `ladder`
- `nominal_tolerance_relative`
- `nominal_tolerance_absolute`
- `frozen_realized_Linf`
- `reproduced_realized_Linf`
- `Linf_reproduction_ratio`
- `reproduction_gate_pass`
- `frozen_compressed_bytes`
- `reproduced_compressed_bytes`
- `realized_Linf`
- `realized_Linf_over_ptp`
- `rmse_density`
- `potential_rel_RMSE`
- `potential_rel_Linf`
- `Bader_error_resolved_e`
- `Bader_error_fixed_e`
- `frac_voxels_reassigned`
- `compression_ratio_frozen`

Use the same reciprocal-space Hartree implementation validated in `analysis/hartree_potential_pilot/run_hartree_pilot.py`.

## Exact row matching

Each regenerated row must match a unique frozen master-table row on at least:

`(material_id, codec, nominal_tolerance_relative, nominal_tolerance_absolute, ladder)`.

Never attach a Bader error from a neighboring tolerance or interpolated row.

## Gate

`reproduction_gate_pass = (0.95 <= reproduced_realized_Linf / frozen_realized_Linf <= 1.05)`

When deterministic byte counts are available, also require exact equality of reproduced and frozen compressed byte counts. Record the mismatch rather than silently dropping it.

## After rows.csv is generated

Run:

```bash
python analysis/hartree_potential_expansion/summarize_expansion.py
```

This produces the pre-declared group, material-smoothness, matched-error-dispersion and gate-failure tables, plus `RESULTS.md` with the recommendation determined from the frozen criteria.

Commit all generated outputs plus provenance (Python/Numpy/codec versions, source-density hashes, RhoCodec commit/hash if available). Do not edit the criteria after seeing the results.
