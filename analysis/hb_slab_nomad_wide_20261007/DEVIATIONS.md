# Deviations

Every departure from the N = 4 cohort (`analysis/hb_slab_aeccar_cohort_20261007/`, protocol `69f8fc2`, results
`bab69ec`), from the P3b selection rule (`analysis/fresh_population_20261006/P3B_SELECTION_RULE.md`) and from the
workflow `.github/workflows/hb_slab_aeccar_cohort.yml` is listed here, with its date and whether it was made before or
after any outcome of this cohort existed. None of them changes a codec, a post-processor, a certificate, a tolerance, a
statistic or a criterion threshold rule.

## Before the selection and the run (2026-10-07, recorded with the protocol freeze)

D1. **Population.** The P3b frame (820 rows) plus the re-listing of the 194 entries that the 2026-10-06 frame dropped
for "rawdir size unavailable" (`selection/relist_frame.py`). Resolved entries join the frame (PROTOCOL.md section 2).

D2. **Exclusions** (`selection/build_exclusion_sets.py`), replacing the strict project-wide set of the N = 4 cohort:
- ids: every NOMAD entry id and `nomad-` material id in any committed text data file on any origin branch, plus bare
  28-character `entry_id`/`task_id` values in CSV files; matching by exact id or by `nomad-` prefix;
- formulas: only reduced formulas of NOMAD or slab records. Formulas that occur only in Materials Project or AFLOW
  bulk rows are not excluded.

D3. **Size window.** 150,000 <= npoints <= 3,870,720, from the CHGCAR header (partial read). The P3b byte window
(1 MB <= CHGCAR bytes <= 80 MB) is not applied. The npoints lower bound 1.5e5 of P3b step 4 is kept.

D4. **Inclusion and input QC.** AECCAR0 and AECCAR2 in the CHGCAR's directory with header grids on the CHGCAR grid;
input QC on the full files: the P3b CHGCAR checks (plus parsed grid = header grid), and for each AECCAR file: header grid
= CHGCAR grid, zero Fortran exponent-less tokens, parse with the adapter's parser to the CHGCAR grid, all values finite.

D5. **Draw.** New salt `QOAC-HB-SLAB-NOMAD-WIDE-20261007|`; the hash-ordered draw runs over rows that passed the input
QC (every candidate row is evaluated first, so the number that qualify is known before the draw); one entry per reduced
formula, at most 6 per upload, N = min(32, qualified). P3b's fixed list of five excluded uploads is not applied (as in the
N = 4 cohort).

D6. **Workflow** `.github/workflows/hb_slab_nomad_wide.yml` = `hb_slab_aeccar_cohort.yml` (`bab69ec`) with:
- trigger branch `research/hb-slab-nomad-wide-20261007`, also in the preflight `GITHUB_REF` check and in the aggregate
  pull and push;
- sentinel `analysis/hb_slab_nomad_wide_20261007/RUN_MANIFEST` (content: the manifest path);
- concurrency group `hb-slab-nomad-wide-20261007-...`;
- preflight compiles `analysis/hb_slab_nomad_wide_20261007/*.py` and runs its `test_cohort_tables.py` and
  `test_evaluate_criteria.py` (in place of the N = 4 cohort's);
- shard step `--aeccar-sources repo/analysis/hb_slab_nomad_wide_20261007/aeccar_sources.csv`;
- output `analysis/hb_slab_nomad_wide_20261007/results/<stem>`;
- workflow name `QOAC-HB slab NOMAD-wide cohort`; result commit message `HB slab NOMAD-wide cohort results`; header
  comment.

  Unchanged: runner type, timeouts, the 19-shard matrix and `shard_for`, the Python and package pins, the frozen
  checkout `893f931`, the Henkelman Bader build, the default mu and tau_B, the artifact names (scoped to the run), the
  aggregator, the AECCAR download log and the unchanged adapter `analysis/qoac_hb_slab_20261007/run_joint_slab.py`.

D7. **Criteria evaluator** `evaluate_criteria.py` and `test_evaluate_criteria.py`: byte copies (SHA-256 `0729424b…` and
`81d77fcf…`), run on the primary population only.

D8. **Selection run location.** The selection (metadata and input QC) runs locally with the frozen stack (Python
3.12.14, numpy 2.4.6, baderkit 0.10.2, pymatgen 2025.10.7, pandas 2.3.3), because NOMAD is reachable from it. The HB
computation runs only on GitHub Actions.

## After the protocol freeze

None so far.
