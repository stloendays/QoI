# WS-0 fresh populations (QOAC-FRESH-20261006) — report

Branch `research/fresh-population-20261006`, built 2026-10-06. Only metadata was
collected (listing entries, size, SHA-256, grid shape, natoms, reduced formula,
lattice, and the finite/positive density validity check). No compression,
codec, Hartree, Bader or other QoI outcome was computed on any candidate.

The selection rule (`SELECTION_RULE.md`, SHA-256 `25d6f04f…3f133778b`) was
committed in `10e7863` before any candidate file was downloaded and is unchanged
since.

## Outcome

| Pool | Source | Engineering | Confirmatory | Total | Attempts | Status |
|---|---|---:|---:|---:|---:|---|
| P1 | MP bulk, CHGCAR | 12 | 60 | 72 | 72 | complete |
| P2 | MP bulk, CHGCAR + AECCAR0 + AECCAR2 | 12 | 48 | 60 | 64 | complete |
| P3 | NOMAD slabs | — | — | — | 0 | not built (infeasible, see Step 5) |

All 132 accepted materials have distinct task ids, material ids and reduced
formulas, none is in the exclusion set, and P1 ∩ P2 = ∅.

## Step 1 — exclusion set

- 60 `origin/*` branches scanned (after `git fetch origin`); 1,688 unique text
  blobs (csv/tsv/json/jsonl/md/txt/yaml/py, plus `.gz`).
- Unique identifiers: 833 = 368 `mp-*` ids + 486 MP S3 task ids + 96 NOMAD entry
  ids + 70 `nomad-*` material ids (one id can appear under two kinds).
- Formulas: 297 distinct `formula*` strings → 291 distinct pymatgen reduced
  formulas; 0 unparsable after filtering.
- `analysis/extensions_20260930/WP-F/frame.csv.gz` (on
  `origin/ext/QSQ-optimization-20261001`, and others) is a full listing of the
  `chgcars/` bucket (415,475 task ids). Only its 186 `in_frozen_study=1` rows
  were taken as usage; taking the whole file would have excluded every
  candidate.
- `exclusion_ids.csv` has one row per (id, kind, file) with the first branch and
  the branch count; the full id × file × branch table is in
  `exclusion_ids_full.csv.gz`.

## Step 2 — Materials Project S3 index (listed 2026-10-06 14:16–14:38 UTC)

| Prefix | Keys | Task-id keys |
|---|---:|---:|
| `chgcars/` | 415,480 | 415,475 |
| `aeccar0s/` | 138,847 | 138,845 |
| `aeccar2s/` | 138,821 | 138,819 |

- Task ids with CHGCAR: **415,475**; with CHGCAR + AECCAR0 + AECCAR2:
  **138,804**.
- Of the 415,475 CHGCARs, 1,239 are < 1 MB and 8,424 are > 80 MB.

## Step 3 — frames, strata and draw

| | P2 | P1 |
|---|---:|---:|
| Frame size after pre-filter | 135,534 | 270,278 |
| Frame task ids in exclusion set | 136 | 338 |
| Strata (keys per stratum) | 60 (2,258–2,259) | 72 (3,753–3,754) |
| CHGCARs downloaded | 64 | 72 |
| Rejected: `npoints_out_of_range` | 2 (both stratum 1, 48³ grids) | 0 |
| Rejected: `excluded_formula` | 2 (strata 13, 34) | 0 |
| Highest hash rank used | 2 | 0 |
| Strata left empty | 0 | 0 |

Six triple-available keys passed the CHGCAR size filter but had an AECCAR above
150 MB; they went to the P1 frame under the "rest" rule.

## Step 4 — manifests

`P1_ENGINEERING_MANIFEST.csv` (12), `P1_CONFIRMATORY_MANIFEST.csv` (60),
`P2_ENGINEERING_MANIFEST.csv` (12), `P2_CONFIRMATORY_MANIFEST.csv` (48), with
the `ENGINEERING_MANIFEST.csv` column order
(`material_id,task_id,corpus,system_type,source,formula,ngrid,sha256,url,source_bytes,npoints,natoms,selection_stratum,selection_hash`).
`sha256` and `source_bytes` are of the CHGCAR `.json.gz` exactly as served.
Every attempt (accepted and rejected), with lattice parameters and AECCAR byte
counts, is in `attempts.csv`.

**material_id:** the MP material id was recovered from `poscar.comment` for only
5/72 (P1) and 10/60 (P2) materials. For the other 117, the comment carries no
`mp-` id, so `material_id = task_id`. The MP API (key required) was not used.
Excluding a material by its formula also catches any other task of an
already-used material.

### Distributions of accepted materials

| | P1 (72) | P2 (60) |
|---|---|---|
| CHGCAR gz bytes, min / median / max | 1.31 MB / 14.7 MB / 67.7 MB | 1.35 MB / 11.1 MB / 61.8 MB |
| npoints, min / Q1 / median / Q3 / max | 175,616 / 691,200 / 1,045,248 / 2,039,040 / 4,741,632 | 175,616 / 442,176 / 884,736 / 1,294,704 / 5,832,000 |
| natoms, min / median / max | 2 / 12 / 72 | 2 / 7 / 64 |
| Engineering npoints, min / median / max | 248,832 / 1,026,560 / 4,096,000 | 193,536 / 826,368 / 2,764,800 |
| Confirmatory npoints, min / median / max | 175,616 / 1,045,248 / 4,741,632 | 175,616 / 884,736 / 5,832,000 |
| AECCAR0 gz bytes, min / median / max | — | 0.82 MB / 6.27 MB / 31.5 MB |
| AECCAR2 gz bytes, min / median / max | — | 0.65 MB / 5.38 MB / 30.6 MB |

Full quartiles are in `selection_stats.json`.

## Step 5 — slabs (P3): not built

- **How the development slabs were chosen.** The 68 development slabs come from
  five hand-picked NOMAD uploads (`upload_id` / `upload_description` in
  `materials_metadata.csv`: GaN electrochemical surfaces, RuO₂ CO₂RR, clean and
  O-covered Co(0001), Cl on Ti, clean fcc metal surfaces). No query script for
  that corpus exists on any branch.
- **Public frame.** A credential-free public query is possible and was frozen in
  `nomad_frame_surface_vasp.csv.gz` (`scripts/nomad_frame.py`, listed
  2026-10-06 14:37–15:06 UTC). The query was
  `results.material.structural_type = surface` and `program_name = VASP`. It
  returned 16,275 entries; 1,014 have a CHGCAR in the mainfile directory, and
  820 of those have a retrievable size.
  - `entries/rawdir/query` fails server-side for this filter (HTTP 500,
    "both public and restricted files found"), so sizes came from per-entry
    `rawdir` calls.
  - 194 entries return the same HTTP 500 persistently and are absent from the
    frame.
- **Feasibility check (metadata only, `p3_feasibility.json`).**
  - 531 of the 820 rows are in the 1–80 MB window; 398 of these belong to the
    five already-used uploads.
  - Under the frozen rule, 97 rows remain eligible, covering only 32 distinct
    reduced formulas, and 49 of the 72 size strata have no eligible row. At most
    23 materials could be drawn.
  - Even without the upload exclusion, the upper bound is 63 (65 formulas, 9
    empty strata).
  - Either way the requested 12 + 60 = 72 is unreachable, so no slab file was
    downloaded and P3 was skipped. The frozen frame and the feasibility counts
    are kept for a future, smaller or broader slab design (e.g. adding other
    codes or `structural_type` values).

## Step 6 — deviations and additions

1. **WP-F sampling frame:** counted only through its `in_frozen_study=1` rows
   (Step 1).
2. **Rule additions, frozen before any download:**
   - a material is rejected if its reduced formula equals one already accepted
     in this population, which keeps materials and pools distinct; it rejected
     nothing in practice;
   - for NOMAD, whole uploads containing an excluded entry are excluded.
3. **"Finite positive density"** is defined as all grid values finite and the
   grid sum > 0.
4. **`material_id = task_id`** for 117/132 materials (Step 4).
5. **P3 not built** (Step 5).
6. **Low free RAM (~1.7 GB):** OpenBLAS was pinned to one thread
   (`OPENBLAS_NUM_THREADS=1`). This has no effect on the selection.

## Volume and provenance

- Candidate downloads: 3.206 GB in total (P1 1.426 GB; P2 1.780 GB including
  the AECCARs). All downloaded files were deleted after metadata extraction;
  only listings, CSV/JSON outputs and scripts are kept. One transient AECCAR2
  download error was retried successfully.
- `PROVENANCE.json` records:
  - listing timestamps;
  - SHA-256 of every index, frame, exclusion file, script and manifest;
  - the loader's SHA-256;
  - the rule-freeze commit and the script commit.
- Scripts (`scripts/`): `build_exclusion.py`, `s3_index.py`, `nomad_frame.py`,
  `select_population.py` (resumable through `attempts.csv`),
  `p3_feasibility.py`, `finalize.py`.
