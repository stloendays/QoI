# P3b fresh slab cohort — selection rule (frozen before any candidate download)

Date: 2026-10-06. Purpose: a second prospective cohort for the General-QOAC law protocol
(`analysis/general_qoac_law/DESIGN.md`), covering surfaces from a second database. The WS-0 rule (72 size strata) was
infeasible for slabs (`p3_feasibility.json`), so this rule draws one material per distinct reduced formula.

Frame: the frozen NOMAD listing `nomad_frame_surface_vasp.csv.gz` (query `results.material.structural_type = surface`,
`program_name = VASP`, listed 2026-10-06; 820 rows with a retrievable CHGCAR size). Only metadata may be read: size,
SHA-256, grid shape, atom count, reduced formula, lattice, finiteness and positivity of the density.

1. Keep rows with 1 MB <= chgcar_bytes <= 80 MB.
2. Drop rows whose upload is one of the five uploads that contain an already-used NOMAD entry (`p3_feasibility.json`,
   `excluded_uploads`), rows whose entry id or `nomad-` + first 12 characters is in `exclusion_ids.csv`, and rows whose
   reduced formula is in `exclusion_formulas.csv` or equals the reduced formula of any P1 or P2 manifest material.
3. Group the remaining rows by reduced formula. Order the formulas by SHA-256 of
   `"QOAC-FRESH-SLAB-20261006|" + reduced_formula`; within a formula, order rows by SHA-256 of
   `"QOAC-FRESH-SLAB-20261006|" + entry_id`.
4. Visit the formulas in that order. For each, try its rows in order. Download the CHGCAR from
   `https://nomad-lab.eu/prod/v1/api/v1/entries/<entry_id>/raw/<basename(chgcar_path)>` and parse it with
   `development_compatibility_smoke.build_grid` (source `NOMAD surfaces/adsorbates`). Accept the first row that
   - parses,
   - has a finite density with positive sum,
   - has 1.5e5 <= npoints <= 6.0e6, and
   - belongs to an upload that has fewer than 6 accepted materials so far.
   At most one material is accepted per formula.
5. Every accepted material enters `P3B_CONFIRMATORY_MANIFEST.csv`, which has the P1 manifest schema with
   `system_type = slab`, `source = NOMAD surfaces/adsorbates`, `material_id = nomad-<first 12 characters of entry_id>`,
   `task_id = entry_id`. There is no engineering split: the law protocol has no tunable part, and the P1 shakedown already
   exercised the pipeline.
6. Every attempt is recorded in `p3b_attempts.csv`. Downloaded files are deleted after metadata extraction.

The cohort is analysed with the frozen law protocol and its criteria unchanged. The validity criteria scale as
"at least n - 2 of n materials".
