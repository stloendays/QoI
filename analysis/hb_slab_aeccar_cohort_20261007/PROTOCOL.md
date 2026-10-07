# QOAC-HB slab cohort selected on AECCAR availability — frozen protocol

Freeze date: 2026-10-07. Branch `research/hb-slab-aeccar-cohort-20261007`, created on origin at `f5c0ac1` as a copy of
`research/qoac-hb-slab-20261007`. This protocol is committed and pushed before the cohort is drawn, before any candidate
file is read beyond the metadata and input-validity checks declared in section 2, and before any HB computation.

Purpose: run the frozen QOAC-HB v2 method (`analysis/qoac_hb_v2/`, unchanged) and its confirmatory criteria on a
fresh NOMAD slab cohort in which every entry has a usable AECCAR0 + AECCAR2 reference. The completed slab run
(`analysis/qoac_hb_slab_20261007/`, confirmatory FAIL, 13/32 analysable) is not modified, rerun or re-evaluated; its
verdict stands.

## 1. Part A outcome (diagnosis of the slab run's four loading failures)

`diagnosis/DIAGNOSIS.md`, with evidence tables `diagnosis/aeccar_file_scan.csv` and
`diagnosis/aeccar_loader_results.csv`. All 8 files match the frozen listing in bytes and SHA-256; all headers are on
the CHGCAR grid; no augmentation or spin blocks. All four failures are data defects in the published AECCAR0:

| entry | AECCAR0 | class |
|---|---|---|
| `nomad-IZPVe_A6_quS` | 2,419,200 / 2,419,200 values `NaN` | data defect |
| `nomad-ViaCyatoI3FA` | 1,975,680 / 1,975,680 values `NaN` | data defect |
| `nomad-DcwYU1UzKNe8` | 1,658,880 / 1,658,880 values `NaN` | data defect |
| `nomad-hk3gUBk-5QN5` | 1,229,312 values written without `E` (exponents +171 to +197), magnitude 4.94e170–8.52e196, 612,201 negative; all other 1,580,544 values 0 | data defect |

No parser defect was found, so there is no adapter fix. Because data defects exist, section 2 declares an input-validity
check (step 4d).

## 2. Population and selection rule

### Inputs

- Frame: `analysis/fresh_population_20261006/nomad_frame_surface_vasp.csv.gz` (the P3b frame; 820 rows; SHA-256
  `a3e34968cf47ca2bf566d77bbd2d636d3a18abee47b24a9444a6b3e0422f74be`).
- Exclusion set (`selection/`, built by `selection/build_exclusion_set.py` on 2026-10-07 09:15 UTC, summary in
  `selection/exclusion_set.json` with the commit SHA of every branch scanned):
  - the union of the frozen 2026-10-06 set (`exclusion_ids_full.csv.gz`, 833 ids; `exclusion_formulas.csv`, 290 reduced
    formulas) and a new scan of every text-like data file on all 76 `origin/*` branches with the identifier regexes,
    formula columns and pymatgen reduction of `analysis/fresh_population_20261006/scripts/build_exclusion.py`
    (imported). The scan covers every manifest committed since 2026-10-06, including P1, P2 and P3b, the WP-F sample,
    the external cohorts and the QOAC-HB slab run.
  - Skipped as candidate-universe listings, not usage records (as the original rule skipped the WP-F bucket frame):
    `nomad_frame_surface_vasp.csv.gz`, `s3_index_{chgcars,aeccar0s,aeccar2s}.csv.gz`, the exclusion tables themselves
    and the listing logs (`nomad_frame_log.json`, `s3_index_log.json`, `frame_counts.json`). Draw records
    (`attempts.csv`, `p3b_attempts.csv`) are scanned.
  - `selection/exclusion_ids.csv`: 1,053 ids (128 NOMAD entry ids, 102 `nomad-` material ids, 510 `mp-` ids, 623 MP
    task ids in S3 URLs). SHA-256 `eae9d2d9856ae40303794e88830fca07d5304636cf5e57d90c389b03dc7a1a22`.
  - `selection/exclusion_formulas.csv`: 690 reduced formulas. SHA-256
    `61cee7230137407e23d8bf26a63698c92d36269b7c0267ce0dd9c9f81df0f775`.

### Rule

Salt `S = "QOAC-HB-SLAB-AECCAR-20261007|"`. `h(x) = SHA256_hex(S + x)`.

1. Keep frame rows with 1 MB <= `chgcar_bytes` <= 80 MB (P3b step 1).
2. Drop rows whose `entry_id`, or `nomad-` + its first 12 characters, is in `exclusion_ids.csv`, and rows whose
   frame `reduced_formula` is in `exclusion_formulas.csv`. P3b's fixed list of five excluded uploads is not applied
   (DEVIATIONS.md D1).
3. Group by reduced formula. Order the formulas by `h(reduced_formula)`; within a formula, order rows by
   `h(entry_id)`.
4. Visit the formulas in that order and try each formula's rows in order. A row whose upload already has 6 accepted
   entries is rejected (`upload_cap`). Otherwise accept the first row that passes all of:
   - a. **AECCAR availability (metadata).** The NOMAD listing `GET /entries/<entry_id>/rawdir` has, in the directory
     of the frame's `chgcar_path`, a file whose basename matches `^AECCAR0(\.(bz2|gz|xz))?$` and one matching
     `^AECCAR2(\.(bz2|gz|xz))?$` (first by path if several);
   - b. **P3b CHGCAR checks.** The CHGCAR from `.../entries/<entry_id>/raw/<basename(chgcar_path)>` parses with
     `development_compatibility_smoke.build_grid` (source `NOMAD surfaces/adsorbates`); its density is finite with a
     positive sum; 1.5e5 <= npoints <= 6.0e6; the parsed structure's reduced formula is not in the exclusion formulas;
   - c. **AECCAR header grid (metadata).** Each AECCAR file, downloaded from `.../raw/<basename>` (bytes and SHA-256 as
     served are recorded), has a header grid equal to the CHGCAR grid;
   - d. **Input-validity check (input QC, declared because Part A found data defects).** Each AECCAR file parses with
     baderkit `Grid.from_dynamic`, through the slab adapter's `run_joint_slab.parse_vasp_total` (the parser used in
     the HB run), to an array of the CHGCAR grid shape with all values finite.

   At most one entry per reduced formula. Stop when 32 entries are accepted. A download or parse error rejects that
   row (reason recorded), as in P3b.
5. **N.** N = 32 if 32 entries are accepted; otherwise N = all that qualify, which is the number accepted once every
   formula has been visited. N is fixed by this procedure (metadata and input QC only) before any HB computation. If
   N = 0, no HB run is started and the result is reported as N = 0.
6. Outputs: `manifest.csv` (P3b manifest schema; `corpus = fresh_hb_slab_aeccar`, `system_type = slab`,
   `source = NOMAD surfaces/adsorbates`, `material_id = nomad-<first 12 characters of entry_id>`,
   `task_id = entry_id`, `selection_stratum = formula:<reduced formula>`, `selection_hash = h(entry_id)`);
   `aeccar_sources.csv` (the slab run's schema, read by the adapter); `selection/attempts.csv` (every attempt with
   decision and reason); `selection/selection_log.json` (counts, N, SHA-256 of outputs and inputs, environment).
   Downloaded files are discarded after the values are extracted. No compression, codec, Hartree or Bader quantity is
   computed in the selection.

The selection runs once, with `selection/select_cohort.py` (SHA-256 of committed bytes
`847cb89cccbb8c923f28811a2127eb24a13187c53d100eb42384d69d23322321`) under Python 3.12.14 and the frozen stack of
`893f931` (numpy 2.4.6, baderkit 0.10.2, pymatgen 2025.10.7, pandas 2.3.3). Its outputs are committed and pushed
before the HB run is started.

Pool from metadata (frame and exclusion set only, computed with `select_cohort.py --pool-only`): 531 rows in the
size window; 435 after the id exclusion; **119 rows, 33 reduced formulas, 5 uploads** after the formula exclusion. All
119 rows are in the five uploads that P3b excluded. With at most 6 per upload, at most 26 entries can be accepted
(6 + 6 + 6 + 6 + 2), so N <= 26 < 32.

Checks before freezing, on already-used entries only (no candidate was read): `select_cohort.py --check-entries`
(formula exclusion off, so that every step runs) on five P3b entries. For the four with AECCARs it reproduced the
frozen slab listing (AECCAR bytes, SHA-256, grids) and the P3b manifest (CHGCAR SHA-256, grid, formula).
`nomad-gPlluuEHW2ND` and `nomad-O_yuQGDsVTCx` pass every step; `nomad-g7Z9ilV401H7` is rejected `no_aeccar`,
`nomad-IZPVe_A6_quS` `aeccar0_qc_nonfinite` and `nomad-hk3gUBk-5QN5` `aeccar0_qc_parse_error`.

## 3. Prior-result check

Every material id, NOMAD entry id and reduced formula on any origin branch is excluded (section 2), so no candidate
has a prior result of any kind in this repository. `test_cohort_tables.py` checks this for the drawn manifest.

## 4. Method — HB v2, unchanged

Scientific code: `analysis/qoac_hb_v2/run_joint_v2.py` (`process`, `main`) and `aggregate_joint_v2.py`, imported and
run without modification, through the slab adapter `analysis/qoac_hb_slab_20261007/run_joint_slab.py`, also
unchanged and invoked in place with `--aeccar-sources analysis/hb_slab_aeccar_cohort_20261007/aeccar_sources.csv`.
`git diff 7e2799c f5c0ac1` is empty for every scientific file listed in the slab protocol's section 3 table (same
SHA-256 values; e.g. `run_joint_v2.py` `7527629d56f41da21b88eb8f5967550619ab56a317c80ac622b53ad9c69b51aa`,
`aggregate_joint_v2.py` `98adbf78761570bfba67360d3e71d4b72513075d93c020766d760fa47082abab`,
`development_compatibility_smoke.py` `d51a31d7838d09175292e5024e7f969347c4de2e011446f6de863f2f3c0683bf`). The
adapter is `run_joint_slab.py` at `7e2799c`, SHA-256 of committed bytes
`eb3bb321643074e09c1744874c3b0c0936c5348dd6aa57752dc704ac8cb38760`.

Parameters: identical to the slab run (HB v2 defaults of the push-triggered run): base codecs `J`, `T1`, `GP`, `R3`,
`GF`; post-processors `none`, `uniform`, `hap:mu`, `ctp-uniform`, `ctp-hap:mu` for mu in {1e-4, 1e-2, 1}, plus
`hartree_only`; tau_B in {1e-3, 1e-4, 1e-5} e, primary 1e-4; TAU_H = 1e-6; closure 1e-9; at most 5 Bader attempts per
(base, post, tau_B); Henkelman Bader 1.05 from `mechanism/independent_bader_20260908/reference_source/`, `-ref` exact
AECCAR0 + AECCAR2, `-b ongrid -vac 0.001`; Python 3.12.14, `frozen/validation/requirements-external-e2e.txt` of
`893f931`, ubuntu-24.04; 19 hash shards (`shard_for`, prefix `QOAC-HB-V2|`), 360 min per shard.

## 5. Execution

`.github/workflows/hb_slab_aeccar_cohort.yml`, a copy of `qoac_hb_slab.yml` with the changes listed in
`DEVIATIONS.md` D2. The run is started by pushing the sentinel `analysis/hb_slab_aeccar_cohort_20261007/RUN_MANIFEST`
(content: `analysis/hb_slab_aeccar_cohort_20261007/manifest.csv`). The aggregate job commits
`analysis/hb_slab_aeccar_cohort_20261007/results/manifest/` to this branch. The criteria are then evaluated with
`evaluate_criteria.py` (a byte copy of the slab run's evaluator, SHA-256
`0729424b48056faadea6bb90d91b27ca871e974c0eb337684de94139d85eefdf`; its test `test_evaluate_criteria.py`, SHA-256
`81d77fcf5e2cdb8d0d8d2938127b2257c659da89e8e59ed192a82b99eb000ec9`) on the manifest, without the secondary
`--aeccar-sources` option. The output is `CRITERIA.json` and `RESULTS.md` in this directory.

## 6. Acceptance — criteria verbatim from `analysis/qoac_hb_slab_20261007/PROTOCOL.md` section 5

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
  >= ceil(N x 36/48) wins. For N = 32 these are **>= 31/32** and **>= 24/32**. For N <= 23, ceil(N x 46/48) = N.
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

**Verdict:** CONFIRMATORY PASS if and only if criteria 1, 2 and 3 all pass on the population of N entries. There is no
secondary analysis.

## 7. Fixed after freezing

- No criterion, threshold, statistic, parameter, selection step, salt, exclusion or population changes after this
  protocol is pushed.
- A failure of the selection run or of the workflow itself (script crash, preflight or aggregate error, a cancelled or
  timed-out shard job, a runner fault) is an infrastructure failure. Only infrastructure may be fixed, and the fix is
  recorded in `DEVIATIONS.md` before the whole step is rerun. A per-row rejection in the selection and a per-material
  failure inside a completed shard are results and are counted.
- `RESULTS.md` reports the numbers with denominators, the per-criterion verdicts against the thresholds above, and the
  failures, without interpretation beyond these criteria.
