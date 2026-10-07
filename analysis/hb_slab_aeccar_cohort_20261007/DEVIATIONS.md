# Deviations

Every departure from the P3b selection rule (`analysis/fresh_population_20261006/P3B_SELECTION_RULE.md`), from the
slab run (`analysis/qoac_hb_slab_20261007/`, `f5c0ac1`) and from its workflow `.github/workflows/qoac_hb_slab.yml` is
listed here, with its date and whether it was made before or after any outcome of this cohort existed. None of them
changes a codec, a post-processor, a certificate, a tolerance, a statistic or a criterion threshold rule.

## Before the selection and the run (2026-10-07, recorded with the protocol freeze)

D1. **Selection rule.** P3b's frame, size window, formula grouping, hash ordering, CHGCAR checks, one entry per
formula and 6-per-upload cap are kept. Changed:
- exclusions: the rebuilt project-wide set (`selection/exclusion_ids.csv`, `selection/exclusion_formulas.csv`;
  PROTOCOL.md section 2) replaces P3b's 2026-10-06 tables plus P1/P2 manifest formulas;
- P3b's fixed list of five excluded uploads (`p3_feasibility.json`, `excluded_uploads`) is not applied. After the
  size window and the id and formula exclusions, all 119 remaining frame rows (33 formulas) are in those five uploads,
  so applying the list leaves a pool of 0 rows. The exclusion requirement for this cohort is the id, entry and formula
  set above;
- new salt `QOAC-HB-SLAB-AECCAR-20261007|` (P3b: `QOAC-FRESH-SLAB-20261006|`);
- new inclusion steps 4a (AECCAR0 and AECCAR2 next to the CHGCAR), 4c (AECCAR header grids equal the CHGCAR grid) and
  4d (input QC: both AECCARs parse with the adapter's parser to the CHGCAR grid, all finite), the last declared because
  Part A found data defects;
- target N = 32, stop at 32 accepted; N = all that qualify if fewer.

D2. **Workflow** `.github/workflows/hb_slab_aeccar_cohort.yml` = `qoac_hb_slab.yml` (`f5c0ac1`) with:
- trigger branch `research/hb-slab-aeccar-cohort-20261007`, also in the preflight `GITHUB_REF` check and in the
  aggregate pull and push;
- sentinel `analysis/hb_slab_aeccar_cohort_20261007/RUN_MANIFEST` (content: the manifest path);
- output `analysis/hb_slab_aeccar_cohort_20261007/results/<stem>`;
- concurrency group renamed `hb-slab-aeccar-cohort-20261007-...`, so it is not shared with the slab run;
- workflow name `QOAC-HB slab AECCAR cohort`; result commit message `HB slab AECCAR cohort results`;
- preflight also compiles `analysis/hb_slab_aeccar_cohort_20261007/*.py` and runs its `test_cohort_tables.py` and
  `test_evaluate_criteria.py`;
- the shard step calls the unchanged adapter `analysis/qoac_hb_slab_20261007/run_joint_slab.py` with
  `--aeccar-sources repo/analysis/hb_slab_aeccar_cohort_20261007/aeccar_sources.csv` (the adapter's own option)
  before HB v2's unchanged argument list.

  Unchanged: runner type, timeouts, the 19-shard matrix and `shard_for`, the Python and package pins, the frozen
  checkout `893f931`, the Henkelman Bader build, the default mu and tau_B, the artifact names (scoped to the run), the
  aggregator and the AECCAR download log.

D3. **No adapter change.** Part A found no parser defect (`diagnosis/DIAGNOSIS.md`), so `run_joint_slab.py` is used as
committed at `7e2799c`, in place.

D4. **Criteria evaluator** `evaluate_criteria.py` and `test_evaluate_criteria.py` are byte copies of the slab run's
files. They are run on the primary population only; the slab run's secondary `--aeccar-sources` analysis does not
apply (every entry here has an AECCAR by construction).

D5. **Selection run location.** The selection (metadata and input QC) runs on a local machine with the frozen stack
(Python 3.12.14, numpy 2.4.6, baderkit 0.10.2, pymatgen 2025.10.7, pandas 2.3.3), because NOMAD is reachable from it.
The HB computation runs only on GitHub Actions.

## After the protocol freeze

None. No infrastructure deviation after the run started; the criteria were evaluated with the committed evaluator unchanged (2026-10-07).
