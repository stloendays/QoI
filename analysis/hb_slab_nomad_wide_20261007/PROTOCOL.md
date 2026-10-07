# QOAC-HB wide NOMAD slab cohort — frozen protocol

Freeze date: 2026-10-07. Branch `research/hb-slab-nomad-wide-20261007`, created on origin at `bab69ec`. This protocol is
committed before the input checks of section 2 step 6 are run on any candidate and before any HB computation. Up to this
commit, only metadata has been read: NOMAD listings (`entries/query`, `rawdir`) and the header lines (lattice, atoms,
grid) of CHGCAR and AECCAR files, read with partial raw requests.

Purpose: run the frozen QOAC-HB v2 method (`analysis/qoac_hb_v2/`, unchanged) and its confirmatory criteria on a wider
fresh NOMAD slab cohort than the N = 4 cohort (`analysis/hb_slab_aeccar_cohort_20261007/`, confirmatory PASS 4/4,
`bab69ec`). That cohort and the slab run (`analysis/qoac_hb_slab_20261007/`) are not modified or re-evaluated.

## 1. Population

Public NOMAD entries with `results.material.structural_type = surface` and
`results.method.simulation.program_name = VASP`, with a CHGCAR (`^CHGCAR(\.(bz2|gz|xz))?$`, first by name) in the
mainfile directory.
- The P3b frame `analysis/fresh_population_20261006/nomad_frame_surface_vasp.csv.gz` (SHA-256
  `a3e34968cf47ca2bf566d77bbd2d636d3a18abee47b24a9444a6b3e0422f74be`) lists 820 such entries, out of 16,275 entries and
  1,014 with a CHGCAR in the mainfile directory on 2026-10-06; 194 were dropped because `GET /entries/<id>/rawdir` did not
  return the CHGCAR size.
- Re-listing (`selection/relist_frame.py`, 2026-10-07 14:04–14:27 UTC; `selection/relist_log.json`,
  `selection/relisted_entries.csv`): the same query returns 16,275 entries, 1,014 with a CHGCAR in the mainfile
  directory, all 820 frame entries, and 194 entries not in the frame, all created before the frame listing started
  (2026-10-06 14:37:34 UTC) and none after. Those 194 are the dropped entries. An entry resolves when `rawdir` now
  returns the CHGCAR size. **Resolved: 0 of 194** (rawdir answers HTTP 500 for each, with the message "Inconsistency:
  both public and restricted files found"). No row is added.
- Population: the 820 frame rows.

## 2. Selection rule

Salt `S = "QOAC-HB-SLAB-NOMAD-WIDE-20261007|"`; `h(x) = SHA256_hex(S + x)`.

1. **CHGCAR header.** For every population row, the CHGCAR header is read with a partial raw request
   (`?offset=0&length=...`, decompressed; at least one complete 900 kB block for bz2): grid `nx x ny x nz`,
   `npoints = nx*ny*nz`. A row whose header cannot be read is excluded at this step.
2. **Size window.** 150,000 <= npoints <= 3,870,720.
   - Upper bound: 3,870,720 as directed, the largest slab grid HB v2 has completed on a GitHub runner (slab run and
     N = 4 cohort). The largest grid HB v2 has completed overall is 5,832,000 (P2 bulk,
     `analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/materials.csv`).
   - Lower bound: P3b's npoints lower bound 1.5e5 is kept. HB v2 has completed grids from 175,616 points upward
     (P2), so the bound does not exclude a grid size HB v2 has been shown to handle. (The predecessor QOAC-HB joint run
     completed a 110,592-point grid.)
   - P3b's byte window (1 MB <= CHGCAR bytes <= 80 MB) is not applied: it is a proxy for grid size and can exclude
     grids inside the npoints window.
3. **NOMAD id exclusion.** Drop a row if its `entry_id` is in `selection/exclusion_nomad_ids.csv`, or starts with the
   suffix of any `nomad-<prefix>` id in it.
4. **Formula exclusion.** Drop a row if its frame `reduced_formula` is in `selection/exclusion_slab_formulas.csv`.
5. **AECCAR present (metadata).** `GET /entries/<entry_id>/rawdir` lists, in the directory of the CHGCAR, a file
   matching `^AECCAR0(\.(bz2|gz|xz))?$` and one matching `^AECCAR2(\.(bz2|gz|xz))?$` (first by path if several), and the
   header grid of each (partial read) equals the CHGCAR header grid.
6. **Input checks (declared now), on the full files, for every row that passes step 5:**
   - CHGCAR (P3b step 4): downloads from `.../entries/<entry_id>/raw/<basename>` (bytes and SHA-256 recorded); parses
     with `development_compatibility_smoke.build_grid` (source `NOMAD surfaces/adsorbates`); finite density with
     positive sum; parsed grid equals the header grid and lies in the window; parsed reduced formula not in the
     formula exclusion set;
   - each of AECCAR0 and AECCAR2: downloads (bytes and SHA-256 recorded); header grid equals the CHGCAR grid; **no
     Fortran exponent-less token** in the data (`\d[+-]\d{2,3}` ending a token, e.g. `0.65466110724+193`; count must
     be 0); parses with baderkit `Grid.from_dynamic` through the slab adapter's `run_joint_slab.parse_vasp_total` (the
     parser of the HB run) to an array of the CHGCAR grid shape with **all values finite**.
   A row passing all of them is *qualified*. A download or parse error fails the row (reason recorded).
7. **Draw.** Order the reduced formulas of the qualified rows by `h(reduced_formula)`; within a formula, order its
   qualified rows by `h(entry_id)`. Visit the formulas in order and accept the first row whose upload has fewer than 6
   accepted entries. One entry per reduced formula. Stop at 32.
8. **N = min(32, number accepted)**; all qualified formulas are visited when fewer than 32 qualify. N is fixed by steps
   1–7 before any HB computation. If N = 0, no HB run is started and the result is reported as N = 0.
9. Outputs: `manifest.csv` (P3b manifest schema; `corpus = fresh_hb_slab_nomad_wide`, `system_type = slab`,
   `source = NOMAD surfaces/adsorbates`, `material_id = nomad-<first 12 characters>`, `task_id = entry_id`,
   `selection_stratum = formula:<reduced formula>`, `selection_hash = h(entry_id)`); `aeccar_sources.csv` (the slab
   adapter's schema); `selection/candidates.csv` (every population row with its step results), `selection/qc.csv`,
   `selection/draw.csv`, `selection/selection_log.json`. Downloaded files are discarded after the values are extracted.

Implementation: `selection/select_wide.py` (phases `meta` for steps 1–5, `qc` for step 6, `draw` for steps 7–9;
SHA-256 of committed bytes `2c950a073e77c7682d34d1ddcb60c73442d85cdd421c0e7d9ae2a4bb188d9538`), Python 3.12.14 with the
frozen stack of `893f931` (numpy 2.4.6, baderkit 0.10.2, pymatgen 2025.10.7, pandas 2.3.3).

### Exclusion sets (built 2026-10-07 14:34 UTC by `selection/build_exclusion_sets.py` over all 77 origin branches;
commit SHA of each branch in `selection/exclusion_sets.json`)

- `selection/exclusion_nomad_ids.csv` (SHA-256 `4d6dca4b4b63c324ef6a45fa9ecff52a6f670e17e33998f4d51fb277afaa8894`):
  **352 NOMAD ids** (246 28-character entry ids, 106 `nomad-` material ids), each with the list of files it appears
  in. Sources: every NOMAD entry id (`entries/<id>`) and `nomad-` id in any committed text data file on any branch, and
  bare 28-character `entry_id`/`task_id` values in CSV files. This includes the 96 NOMAD development materials
  (`materials_metadata.csv`: 68 surfaces, 28 2D), P3b (32), the external cohorts with NOMAD entries
  (`external_test_MANIFEST.json`), the slab run, the N = 4 cohort's manifest (4) and its draw record (118 entries
  attempted). Candidate-universe listings (the NOMAD frame, the S3 indices, frame and listing logs, this cohort's
  re-listing) and the exclusion tables themselves are not scanned.
- `selection/exclusion_slab_formulas.csv` (SHA-256 `6c18eb00e7d11b22957878064ce9a4fc3d7fe5dd1816ac245d94d0600fbe8b96`):
  **105 reduced formulas** of NOMAD or slab records (a CSV row or JSON object with a `nomad-` id, a `nomad-lab.eu` URL,
  a `source`/`corpus` value containing `NOMAD`, a bare 28-character `entry_id`/`task_id`, or `system_type = slab`),
  each with its source files: 69 from the NOMAD development materials, 32 from P3b, 25 from
  `external_test_MANIFEST.json`, 4 from the N = 4 cohort (overlapping). One of them is `X`, from a NOMAD 2D record whose
  formula string is `X01X11` (dummy species). Formulas found only in Materials Project or AFLOW bulk rows are not
  included. Draw records (attempts tables) are not used for formulas.
- Against the strict rule of the N = 4 cohort (`analysis/hb_slab_aeccar_cohort_20261007/selection/exclusion_set.json`):
  1,053 ids of all kinds (230 of them NOMAD: 128 entry ids, 102 `nomad-` ids) and 690 reduced formulas from any set.
  Here: 352 NOMAD ids and 105 formulas.

### Funnel from metadata (steps 1–5, `selection/funnel_meta.json`, `selection/candidates.csv`)

| step | rows | note |
|---|---:|---|
| frame (P3b) | 820 | |
| re-listed dropped entries | +0 | 194 identified, 0 resolved |
| CHGCAR header readable | 556 | 264 CHGCAR files are served with 0 bytes (listed size 0) |
| size window | 303 | 4 below 150,000; 249 above 3,870,720 |
| after NOMAD id exclusion | 188 | |
| after formula exclusion | 20 | 10 formulas, 13 uploads |
| AECCAR0 and AECCAR2 present, headers on the CHGCAR grid | 6 | 1 formula (`Ni`), 6 uploads; 14 rows have no AECCAR |

All six rows that reach step 6 have reduced formula `Ni`, so N <= 1.

Checks before freezing, on already-used entries only: `qc_row` of `select_wide.py` on the slab-run entries
`nomad-gPlluuEHW2ND` (qualified), `nomad-IZPVe_A6_quS` (rejected `aeccar0_nonfinite`, 2,419,200 non-finite) and
`nomad-hk3gUBk-5QN5` (rejected `aeccar0_no_E_tokens`, 1,229,312 tokens, the count of `diagnosis/aeccar_file_scan.csv`
of the N = 4 cohort).

## 3. Method — HB v2, unchanged

As in the N = 4 cohort (its PROTOCOL.md section 4): `analysis/qoac_hb_v2/run_joint_v2.py` and `aggregate_joint_v2.py`,
unchanged, through the unchanged slab adapter `analysis/qoac_hb_slab_20261007/run_joint_slab.py` (SHA-256 of committed
bytes `eb3bb321643074e09c1744874c3b0c0936c5348dd6aa57752dc704ac8cb38760`), invoked in place with
`--aeccar-sources analysis/hb_slab_nomad_wide_20261007/aeccar_sources.csv`. Parameters: base codecs `J`, `T1`, `GP`,
`R3`, `GF`; post-processors `none`, `uniform`, `hap:mu`, `ctp-uniform`, `ctp-hap:mu` for mu in {1e-4, 1e-2, 1}, plus
`hartree_only`; tau_B in {1e-3, 1e-4, 1e-5} e, primary 1e-4; TAU_H = 1e-6; closure 1e-9; at most 5 Bader attempts per
(base, post, tau_B); Henkelman Bader 1.05 from `mechanism/independent_bader_20260908/reference_source/`, `-ref` exact
AECCAR0 + AECCAR2, `-b ongrid -vac 0.001`; Python 3.12.14, `frozen/validation/requirements-external-e2e.txt` of
`893f931`, ubuntu-24.04; 19 hash shards, 360 min per shard.

## 4. Execution

`.github/workflows/hb_slab_nomad_wide.yml`, a copy of `hb_slab_aeccar_cohort.yml` with the changes listed in
`DEVIATIONS.md` D6. Started by pushing the sentinel `analysis/hb_slab_nomad_wide_20261007/RUN_MANIFEST` (content:
`analysis/hb_slab_nomad_wide_20261007/manifest.csv`), after the manifest is committed. The aggregate job commits
`results/manifest/`. The criteria are evaluated with `evaluate_criteria.py` (byte copy, SHA-256
`0729424b48056faadea6bb90d91b27ca871e974c0eb337684de94139d85eefdf`; test `test_evaluate_criteria.py`, SHA-256
`81d77fcf5e2cdb8d0d8d2938127b2257c659da89e8e59ed192a82b99eb000ec9`) on the manifest, primary population only. Outputs:
`CRITERIA.json` and `RESULTS.md` in this directory.

## 5. Acceptance — criteria verbatim from `analysis/qoac_hb_slab_20261007/PROTOCOL.md` section 5

From `analysis/qoac_hb_v2/DESIGN.md` (`8a784a4`), "Confirmatory criteria (48 materials; frozen now)":

> 1. >= 46/48 analyzable and certified (E1 definition).
> 2. Joint overhead at tau_B = 1e-4: median <= 1.10 and fixed-seed (20261007, 10,000 resamples) bootstrap CI upper
>    bound <= 1.15.
> 3. Utility at tau_B = 1e-4: >= 36/48 wins, median > 1.10, and bootstrap CI lower bound > 1.00.

with the definitions from the same file:

> **E1 feasibility:** R3 at its best joint post-processor is certified at all three tau_B
>
> **E4 utility:** at tau_B = 1e-4, CR_R3,joint(best post) / max over {J, T1, GF} of the joint CR at each base's best
> post-processor

and the joint overhead CR_R3,hartree_only / CR_R3,joint(best post) (E2). The joint contract is HB v2's: Hartree
relative RMSE < 1e-6 (historical and Nyquist-safe) on the final stream, and Henkelman Bader maximum atomic-charge error
<= tau_B with zero basin reassignment.

Statistics and denominators, exactly as HB v2 computed them (slab protocol section 5, unchanged):
- Denominator of the counts in criteria 1 and 3: all planned materials (N). A FAILED or MISSING material is not
  analyzable and not certified, and is not a win.
- Count thresholds keep HB v2's fractions of the planned N: criterion 1 needs >= ceil(N x 46/48) and criterion 3
  >= ceil(N x 36/48) wins. For N = 32: >= 31/32 and >= 24/32; for N = 1: >= 1/1 and >= 1/1.
- Overhead: R3's `joint_overhead` in `joint_v2_best_post.csv` at tau_B = 1e-4, over materials where both
  `hartree_only` and the joint stream certify; median <= 1.10 and CI upper bound <= 1.15.
- Utility: ratio over materials where R3 certifies; win = ratio > 1. A sole certifier (no other of J, T1, GF
  certifies) is +inf, a win, and enters the median as 1e9 (the `aggregate_joint_v2.py` convention); median > 1.10 and
  CI lower bound > 1.00.
- Bootstrap: values in manifest order; `numpy.random.default_rng(20261007)` fresh for each statistic; 10,000
  resamples (`rng.integers(0, n, (10000, n))`); median of each; 2.5th and 97.5th percentiles. A statistic over an
  empty set fails its criterion.
- Failures (download; memory; solver) are recorded per material in `materials.csv` (`status`, `error`) and per setting
  in `failures.csv`. They are counted as above; failed materials are not retried.

**Verdict:** CONFIRMATORY PASS if and only if criteria 1, 2 and 3 all pass on the population of N entries.

## 6. Fixed after freezing

- No criterion, threshold, statistic, parameter, selection step, salt, exclusion or population changes after this
  protocol is committed.
- A failure of the selection run or of the workflow itself (script crash, preflight or aggregate error, a cancelled or
  timed-out shard job, a runner fault) is an infrastructure failure. Only infrastructure may be fixed, and the fix is
  recorded in `DEVIATIONS.md` before the whole step is rerun. A per-row rejection in the selection and a per-material
  failure inside a completed shard are results and are counted.
- `RESULTS.md` reports the numbers with denominators, the per-criterion verdicts against the thresholds above, and the
  failures, without interpretation beyond these criteria.
