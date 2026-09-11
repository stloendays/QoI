# Supplementary Information workspace

This directory is the stable entry point for submission-facing supplementary assets.

The frozen raw evidence is intentionally **not** moved into this directory because many analysis and figure scripts depend on the existing repository paths. The submission-facing organization is therefore maintained through two canonical maps:

- `paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md` — reader-facing SI prose and proposed Supplementary Notes/Tables/Figures.
- `paper/SUPPLEMENTARY_ASSET_MAP_20260911.md` — exact mapping from each SI object to its frozen machine-readable source.

## Existing sensitivity files

- `S1_S3_sensitivity.csv` — no-exclusion diagnostic and inflated-threshold sensitivity.
- `S2_floor_relative.csv` — certified Bader error relative to the independently measured Protocol A.1 floor.
- `S4_amplitude_sensitivity.csv` — Protocol A.1 probe-amplitude sensitivity for the 18-material calibration panel.

These filenames are retained for provenance. Their publication labels will be assigned through the SI table/figure map rather than by renaming the raw files.

## Frozen SI structure

The current submission plan contains:

- **10 Supplementary Notes**;
- **14 Supplementary Tables (S1–S14)**;
- **8 Supplementary Figures (S1–S8)**.

Tables S1–S9 are now built as submission-facing drafts/objects, and Figures S1–S4 plus S7 are locked R-generated publication figures. The remaining work is primarily compact aggregation for S10–S14 and R rendering/locking for S5, S6 and S8 rather than new experiments.

## Critical denominator convention

Keep the following universes distinct:

- 254 development systems = 186 bulk + 68 slab;
- 65 external records = frozen external descriptive/stability set;
- 319 stability records = 254 development + 65 external;
- 63 systems = separately frozen primary external confirmatory rate–fidelity cohort.

The 65-record external descriptive set must not be silently substituted for the 63-system confirmatory cohort.

## Publication rules

1. Protocol A is archived/provisional; Protocol A.1 is operative.
2. Non-evaluable is neither pass nor failure.
3. Supplementary tables are generated from machine-readable sources, not transcribed from prose.
4. Final supplementary figures use R and export PNG/PDF/SVG from the same source.
5. Legacy exploratory plots may support provenance but are not final publication graphics.
6. Negative algorithm results remain in the SI because they delimit the contribution; they do not create a second algorithmic narrative.
7. Any discrepancy between historical prose and frozen tables must be resolved in favour of a regenerated, versioned numerical source before submission.

## Next build order

1. Build Tables S10–S11 and Figure S5 for Bader mechanism / independent-implementation robustness.
2. Build Table S12 and Figure S6 for realized-distortion matching sensitivity.
3. Regenerate Table S13 and Figure S8 from the final 63-system external confirmatory outputs and the current development `benchmark/summary_a1.csv`.
4. Aggregate failure/negative-result Table S14.
5. Run the final manuscript ↔ SI cross-reference audit, then assemble Word/PDF submission files.
