# Deviations from PROTOCOL.md

Infrastructure fixes and any departure from the frozen protocol, recorded before the affected step is rerun.

None at freezing (2026-10-08).

## D1 (infrastructure, 2026-10-08 00:33–00:35 SGT): bundle jobs b2 and b3 failed to start 10 and 9 times

Jobs `1439806` (b2) and `1439807` (b3), submitted at 00:33, were started by PBS on CN-117 and CN-112 and ended before
the job script ran (`Exit_status = -10`, no PBS output file, no file written in any run directory), then requeued by PBS
(`run_count` 11 and 10). At 00:34:24 a user hold (`qhold`) was placed on both to stop the cycling, while the 11th and
10th starts on CN-112 succeeded; the jobs were running VASP at 00:35:05 and the holds were released (`qrls`) at 00:35. No
job, input or run was changed, nothing was rerun, and no slab result is affected.

## Before the HB run (2026-10-08, recorded before the sentinel is pushed; no HB quantity exists yet)

The cohort (N = 32, `cohort.csv`, commit `ec19c91`) is fixed. Hosting, decided by the author on 2026-10-08 (PROTOCOL.md
section 9 left it open and classes it as infrastructure): GitHub release `data-hb-selfslab-20261008` of
`stloendays/QoI` (prerelease, tag on `ec19c91`), 96 assets `<material_id>__<CHGCAR|AECCAR0|AECCAR2>.gz`,
1,805,055,269 bytes, each asset's SHA-256 equal to the `*_gz_sha256` of `cohort.csv` (verified by the coordinator for all
96 before upload). Download URL `https://github.com/stloendays/QoI/releases/download/data-hb-selfslab-20261008/<asset>`.

D2. **Data-source adapter** `run_joint_selfslab.py` (this directory) in place of `run_joint_slab.py`, which serves NOMAD
AECCARs only. Modelled on `run_joint_slab.py`, whose `NomadVaspBytes` marker, `parse_vasp_total` (baderkit
`Grid.from_dynamic`) and `nomad_aware_dev` loader proxy it imports unchanged. For the 32 ids of `cohort.csv` it
- serves the manifest's CHGCAR URL and the two AECCAR bucket keys of `run_joint_v2.process`
  (`aeccar{0,2}s/<task_id>.json.gz`, `task_id = material_id`) from the release assets through HB v2's own `b1.fetch`;
- checks every download's gz byte count and SHA-256 against `cohort.csv` and raises on a mismatch (the material is
  then FAILED, as for any HB v2 download error); the CHGCAR blob is returned as downloaded, so HB v2's own
  `sha256 == manifest sha256` check also runs;
- builds the CHGCAR grid for the manifest source `QoI self-computed slab (VASP 6.3.2)` with `dev.decompress_nomad` and
  baderkit `Grid.from_dynamic`, the two functions `dev.build_grid` applies to a VASP CHGCAR (its NOMAD branch); the
  AECCARs are decompressed with `dev.decompress_nomad` and parsed with `parse_vasp_total`, as in the slab runs;
- passes every other call to the HB v2 objects unchanged, and logs each download (`release_downloads_shard_XX.csv`).

`analysis/qoac_hb_v2/run_joint_v2.py`, `aggregate_joint_v2.py` and `run_joint_slab.py` are not modified (SHA-256 of
committed bytes unchanged: `7527629d…`, `98adbf78…`, `eb3bb321…`). Tests: `test_run_joint_selfslab.py`, 11 tests
(routing of the CHGCAR URL and both AECCAR keys, byte-count and SHA-256 mismatches for each file, delegation of other
URLs and ids, installation, parser identity with `dev.build_grid`'s VASP route and with the slab adapter's AECCAR
parser, manifest = cohort order and checksums, cohort = first 32 converged and QC-passing in draw order, shard load);
11/11 pass locally (Python 3.12.14, baderkit 0.10.2). Download check before the run, on one cohort material
(`mp-aaaabjil`): the three assets download through `b1.fetch` with the `cohort.csv` byte counts and SHA-256, the CHGCAR
grid is 56x56x500 (= manifest), and AECCAR0 + AECCAR2 has that shape with all values finite. No HB quantity was computed.

D3. **Workflow** `.github/workflows/hb_selfslab_cohort.yml` = `hb_slab_aeccar_cohort.yml` (`bab69ec`) with:
- trigger branch `research/hb-selfslab-20261007`, also in the preflight `GITHUB_REF` check and in the aggregate pull and
  push;
- sentinel `analysis/hb_selfslab_20261007/RUN_MANIFEST` (content: the manifest path);
- output `analysis/hb_selfslab_20261007/results/<stem>`;
- concurrency group `hb-selfslab-20261007-...`, not shared with the earlier slab runs;
- workflow name `QOAC-HB self-computed slab cohort`; result commit message `HB self-computed slab cohort results`;
- preflight also compiles `analysis/hb_selfslab_20261007/*.py` and runs `test_run_joint_selfslab.py`; it no longer
  runs the N = 4 cohort's `test_cohort_tables.py` (that cohort's tables), and still runs the evaluator's test
  `test_evaluate_criteria.py`;
- the shard step calls `analysis/hb_selfslab_20261007/run_joint_selfslab.py --cohort .../cohort.csv` before HB v2's
  unchanged argument list (in place of `run_joint_slab.py --aeccar-sources ...`);
- the aggregate step collects `release_downloads_shard_*.csv` into `results/<stem>/release_downloads.csv` (in place of
  the NOMAD `aeccar_downloads.csv`).

  Unchanged: runner type, timeouts (360 min per shard), the 19-shard matrix and `shard_for` (largest load 4 materials,
  shard 7), the Python and package pins, the frozen checkout `893f931`, the Henkelman Bader build, the default mu
  (1e-4, 1e-2, 1) and tau_B (1e-3, 1e-4, 1e-5), the artifact names and the aggregator `aggregate_joint_v2.py`.

D4. **Manifest** `manifest.csv` (written by `write_manifest.py` from `cohort.csv`): the 32 cohort slabs in cohort order,
in the slab cohorts' schema: `corpus = fresh_hb_selfslab`, `system_type = slab`, `source = QoI self-computed slab
(VASP 6.3.2)`, `task_id = material_id`, `url` = the CHGCAR release asset, `sha256` and `source_bytes` = that gz asset's
SHA-256 and byte count (the bytes HB v2 downloads and checks), `ngrid`, `npoints` and `natoms` from the input QC,
`selection_stratum = formula:<reduced formula>`, `selection_hash = h(material_id)` of PROTOCOL.md section 4.

D5. **Evaluator (recorded before the run).** The criteria are evaluated with `analysis/hb_slab_aeccar_cohort_20261007/evaluate_criteria.py` in
place and unchanged (SHA-256 `0729424b48056faadea6bb90d91b27ca871e974c0eb337684de94139d85eefdf`), primary population
only, with this cohort's `manifest.csv` and `results/manifest/`.

## After the HB run

None. CI run 37723028989 (head `4f22046`) completed with 21/21 jobs successful and was not rerun; no infrastructure fix
was needed. The criteria were evaluated with the committed evaluator unchanged (2026-10-08).
