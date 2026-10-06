# Fresh-population selection rule (QOAC-FRESH-20261006)

Frozen before any candidate file was downloaded. Its SHA-256 is recorded in
`PROVENANCE.json` (`selection_rule_sha256`) and it was committed on
`research/fresh-population-20261006` before `scripts/select_population.py` ran.

Only metadata may be read: S3/NOMAD listing entries, file size, SHA-256, grid
shape, number of atoms, reduced formula, lattice, and the finiteness / sign of
the integrated density needed for the validity check below. No compression,
codec, Hartree, Bader or other QoI outcome is computed on any candidate.

## Definitions

- `MB` = 10^6 bytes. Sizes are the bytes listed by S3 (MP) or by NOMAD
  `rawdir` (slabs), i.e. the file exactly as served.
- `selection_hash(id) = SHA256_hex("QOAC-FRESH-20261006|" + id)`, where `id` is
  the MP task id (`mp-NNNN` as in the S3 key) or the full 28-character NOMAD
  entry id.
- Strata: sort the frame ascending by `(size, id)`, `N` = frame size, `K` =
  number of strata; stratum `k` (0-based) holds positions
  `floor(k*N/K) .. floor((k+1)*N/K) - 1`. Labels are `s01ofK` ... `sKofK`.
- Exclusion set: `exclusion_ids.csv` (every `mp-*` id, every task id in an MP S3
  URL, every NOMAD entry id and `nomad-*` material id on any `origin/*` branch;
  WP-F `frame.csv.gz` contributes only its `in_frozen_study=1` rows because the
  rest is a bucket listing, not a usage record) and `exclusion_formulas.csv`
  (pymatgen reduced formulas of every `formula*` value in CSV/JSON files on any
  `origin/*` branch).

## Candidate validity (applied in hash order within a stratum)

A candidate is rejected, and the next key in the same stratum's hash order is
tried, if any of the following holds:

1. its id is in the exclusion id set (checked before download);
2. (MP) the material id recovered from the CHGCAR JSON (`poscar.comment`,
   lower-cased, if it matches `mp-\d+`) is in the exclusion id set;
   (NOMAD) `nomad-` + first 12 characters of the entry id is in the exclusion
   id set, or the entry's upload id is one of the uploads that contain an
   excluded NOMAD entry;
3. download or parsing with the project's loader
   (`validation/qsq_prospective/development_compatibility_smoke.py::build_grid`,
   i.e. `decode_mp_chgcar` for MP and `Grid.from_dynamic` for NOMAD) fails;
4. the total density grid contains a non-finite value or its sum is not > 0;
5. `npoints = nx*ny*nz` is outside `[1.5e5, 6.0e6]`;
6. the reduced formula of the parsed structure is in the excluded reduced
   formulas, or equals the reduced formula of a material already accepted in
   any pool of this population (pools are processed in the order P2, P1, P3 and
   strata in ascending order; this keeps every material, and every pool,
   distinct);
7. (P2 only) either AECCAR0 or AECCAR2 fails to download/parse with
   `decode_mp_chgcar`, has a grid shape different from the CHGCAR's, or contains
   a non-finite value.

If a stratum's keys are exhausted without an accepted candidate, the stratum is
left empty and reported as a deviation (no backfill from other strata).

Downloaded files are deleted immediately after their metadata is extracted.

## Pools

### P2 — MP bulk with CHGCAR + AECCAR0 + AECCAR2 (built first)

- Frame: task ids that have `chgcars/<id>.json.gz`, `aeccar0s/<id>.json.gz` and
  `aeccar2s/<id>.json.gz` in the 2026-10-06 S3 listing, with CHGCAR size in
  `[1 MB, 80 MB]` and each AECCAR size `<= 150 MB`.
- K = 60 strata, one accepted material per stratum.

### P1 — MP bulk, CHGCAR only

- Frame: task ids with `chgcars/<id>.json.gz` of size `[1 MB, 80 MB]` that are
  not in the P2 frame.
- K = 72 strata, one accepted material per stratum.

### P3 — NOMAD surface/adsorbate slabs

- Frame: public NOMAD entries (API v1, no credentials) with
  `results.material.structural_type = "surface"` and
  `results.method.simulation.program_name = "VASP"`, listed on 2026-10-06 and
  frozen in `nomad_frame_surface_vasp.csv.gz`; the CHGCAR is the first (by
  name) file in the mainfile directory whose basename matches
  `^CHGCAR(\.(bz2|gz|xz))?$`; its served size must be in `[1 MB, 80 MB]`.
- URL: `https://nomad-lab.eu/prod/v1/api/v1/entries/<entry_id>/raw/<basename>`.
- K = 72 strata, one accepted material per stratum.

## Engineering / confirmatory split

Within each pool, sort accepted materials ascending by `(npoints, id)`; with
0-based position `i`:

- P1 and P3: engineering iff `i >= 2 and (i - 2) % 6 == 0` (positions 2, 8, ..., 68 → 12 of 72);
- P2: engineering iff `i >= 2 and (i - 2) % 5 == 0` (positions 2, 7, ..., 57 → 12 of 60).

All other accepted materials are confirmatory.

## Manifest fields

`material_id` (MP material id from `poscar.comment`, else the task id;
`nomad-` + first 12 characters of the entry id for NOMAD), `task_id` (MP task id
or NOMAD entry id), `corpus` (`fresh_p{1,2,3}_{engineering,confirmatory}`),
`system_type` (`bulk` / `slab`), `source` (`Materials Project` /
`NOMAD surfaces/adsorbates`), `formula` (pymatgen reduced formula of the parsed
structure), `ngrid` (`nx`x`ny`x`nz`), `sha256` / `source_bytes` (of the served
CHGCAR file), `url`, `npoints`, `natoms`, `selection_stratum`
(`P<k>_sNNofK`), `selection_hash`.
