# Error-geometry permutation v0.1 — implementation notes

## 2026-09-07: smoke-run correction

The first implementation smoke (`Error Geometry Permutation Smoke`, run `34116572192`) failed before loading any density field. The failure was:

`mp-1038991: missing benchmark 1e-3 rows; got ['ZFP']`

This was an implementation/provenance lookup defect, not a scientific outcome. The preregistered representative set is defined from `mechanism/basin_error_decomposition_summary.csv`, where the selected materials have successful 1e-3 records for all three codecs. The current master table is an early-stopped benchmark table and therefore need not retain a 1e-3 row for every codec/material that was explicitly evaluated in the earlier mechanism matrix.

The correction is implemented in `mechanism/residual_spatial_permutation_v2.py`:

- selection remains exactly the preregistered selection from the released mechanism table;
- codec, relative tolerance (`1e-3`), codec implementation, five permutation seeds, 20 density-rank strata, norm-preserving permutation, Bader settings, estimands and bootstrap rules are unchanged;
- the absolute codec bound is reconstructed as preregistered from `1e-3 * source value_ptp`;
- the released mechanism row is used as the operating-point provenance authority for realized L-infinity, resolved-Bader error and compression ratio;
- source SHA256 and byte count remain independently verified from `materials_metadata.csv`.

No Protocol A.1 setting, codec setting, tolerance ladder, eligibility rule, early-stopping rule, failure semantic or external-confirmatory cohort was changed.
