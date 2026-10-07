# QOAC-HB slab confirmation (fresh P3b slabs) — frozen protocol

Freeze date: 2026-10-07. This protocol is frozen before any HB (joint Hartree + Bader) computation on any slab.
Branch `research/qoac-hb-slab-20261007`, created from `origin/paper/nc-reopen-20261007` at `6d54d94`.

Purpose: repeat the QOAC-HB v2 confirmation (`analysis/qoac_hb_v2/`, 48/48 fresh P2 bulk materials, all frozen
criteria PASS) on fresh slabs, with HB v2's method and frozen criteria unchanged.

## 1. Prior-result check

All 71 `origin/*` branches and all local branches were searched with `git grep` for the 32 material ids and the 32
NOMAD entry ids of the population. Hits:
- `analysis/fresh_population_20261006/P3B_CONFIRMATORY_MANIFEST.csv` and `p3b_attempts.csv` (selection metadata);
- `analysis/general_qoac_law/results/predictions/pred_*.csv` and `results/run_P3B_CONFIRMATORY/part_{a,b}_*.csv`
  (General-QOAC law run: compression ratio and Hartree metrics, no Bader column).

No path containing `qoac_hb` and no file with a Bader result exists for any of these slabs. No HB result on this
population exists.

## 2. Population

- `manifest.csv` is a byte copy of `analysis/fresh_population_20261006/P3B_CONFIRMATORY_MANIFEST.csv` at `6d54d94`
  (last changed in `d1c1050`). SHA-256 of the committed bytes (LF):
  `e7c447d5f8dc3b263c7b5b4b9d1f8344ad9c8ed41e5b72fa333c37ad14b70f97`.
- 32 slabs, NOMAD `surfaces/adsorbates`, drawn under the frozen rule `P3B_SELECTION_RULE.md` (SHA-256
  `61ab4f1142e0ea13c0d21fefd289402f64d4183982cee8a5f7d6b861bfd3c157`, `39ba728`). npoints 677,376–3,870,720.
- Exclusions: none. The frozen P3b rule excludes nothing beyond its own draw, so all 32 are planned. N planned = 32.

### AECCAR availability (metadata only, recorded now)

HB v2's Bader reference is the exact AECCAR0 + AECCAR2 sum of the same VASP run. For every entry, the NOMAD
`entries/<entry_id>/rawdir` listing (2026-10-07) was read, and each AECCAR0/AECCAR2 file found next to the CHGCAR was
streamed once to record its byte count, SHA-256 (bytes as served) and header grid. Nothing else was read; no file was
kept. Result in `aeccar_sources.csv` (SHA-256 `aead24ef47ebbdd1a6e97055ba86113f68343494a8257c784cbb3b518fa4c98e`):

- 17/32 entries have AECCAR0 and AECCAR2 in the CHGCAR's directory, each on the CHGCAR grid:
  `nomad-slKw7W6vu-8S`, `nomad-wpVo8yTF7eRr`, `nomad-IZPVe_A6_quS`, `nomad-DfpU7vvNQ-Vo`, `nomad-3wOOZLfv7lb_`,
  `nomad--QPBOSBRk9z4`, `nomad-ZzgnSZOSnag2`, `nomad-TSS0Y8O9xp8A`, `nomad-deLeLsqokf9I`, `nomad-bEMTXRvdLPTu`,
  `nomad-ViaCyatoI3FA`, `nomad-gPlluuEHW2ND`, `nomad-DcwYU1UzKNe8`, `nomad-O_yuQGDsVTCx`, `nomad-hk3gUBk-5QN5`,
  `nomad-NOOih6wwVxT5`, `nomad-CVWFkEoST7FX`.
- 15/32 entries have no AECCAR file:
  `nomad-G-yDaY8qmw5_` (TiO2), `nomad-vbsqs8Js2fzW` (ZnSiN2), `nomad-uxkQqRHBpSox` (Ti4C3),
  `nomad-a3nHf0dBA8BK` (Cu44Ni), `nomad-uI3dGHZQPhUQ` (VCu44), `nomad-vGEh154443lz` (ZnGeN2),
  `nomad-C-8aMchGaf7P` (HfC), `nomad-OLo5BGMUENyW` (ZrC), `nomad-BLbUQWtMdS99` (ZnSnN2), `nomad-Lt4FFQvyPw8a` (NbC),
  `nomad-hYJ7QAq46DqB` (Cu44H3PtC), `nomad-BGv3HMr4F-YZ` (Ti3C2), `nomad-HCM86CvqrAFu` (MoC),
  `nomad-bUeGvZ6vwC_l` (TiC), `nomad-g7Z9ilV401H7` (TaC).

These 15 stay in the population. HB v2's method cannot run without the AECCAR reference, so each of them is a
per-material download failure, recorded and counted exactly as HB v2 counts failures (section 5).

## 3. Method — HB v2, unchanged

Scientific code: `analysis/qoac_hb_v2/run_joint_v2.py` (`process`, `main`) and `aggregate_joint_v2.py`, imported and
run without modification. This is the same code that produced the HB v2 P2 results: `git diff e095a0c 6d54d94` is
empty for every file below.

| file | last commit | SHA-256 (committed bytes) |
|---|---|---|
| `analysis/qoac_hb_v2/run_joint_v2.py` | `77caf5d` | `7527629d56f41da21b88eb8f5967550619ab56a317c80ac622b53ad9c69b51aa` |
| `analysis/qoac_hb_v2/projection_v2.py` | `a0067b7` | `2e5391d39a71f870e8345b4dd46bad2ebf8875c00b6966dad9ffb16ed783dc31` |
| `analysis/qoac_hb_v2/codec_qoac_v03.py` | `b8ac91b` | `385de4425d32d4ac3658a778d8fa17e7c7dceae28e67e101f587b961c2fac523` |
| `analysis/qoac_hb_v2/aggregate_joint_v2.py` | `77caf5d` | `98adbf78761570bfba67360d3e71d4b72513075d93c020766d760fa47082abab` |
| `analysis/qoac_hb_v2/test_projection_v2.py` | `a0067b7` | `d9c15764baa9847033c2f4e3663e81ad994c7e518623d96156d173c1cf59dbea` |
| `analysis/qoac_hb_v2/test_codec_qoac_v03.py` | `b8ac91b` | `df7c5be6d5f8251530dbc76a33181c7461a1d92e80ac292b2779a2563bc3b3b0` |
| `analysis/qoac_hb_v2/test_runner_v2.py` | `77caf5d` | `64f339ea3c3c067a7233453c8d9265b04cfa491b644ece28f15bbea5d1a9275b` |
| `analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py` | `5b36848` | `f78dd40aba7f2a25727d4df08d621f3456244bfb14f404423551900c3504ce1a` |
| `analysis/operator_aware_bader_fixed_partition/qoac_b_core.py` | `cb2a664` | `eb3fa3c0f4e3bf7f82f57989751e5f6e0082c8f1816a893ce355b54ee2d0ad19` |
| `analysis/operator_aware_bader_fixed_partition/run_engineering.py` | `3c11ccc` | `56004e8af05777bbf0bd44be3347c4bad5283d5c93aa30698e898896bd4e5d75` |
| `analysis/qoac_h_strong_baselines/truncation_codec.py` | `2fcddf8` | `4e6e1d623d6ab0ddf2dec4afd7c5309cf3fc6d040df0132f9462613d5f187d54` |
| `analysis/qoac_h_strong_baselines/test_truncation_codec.py` | `2fcddf8` | `b52289272edfc735f57b050113b1ae8e7198f6c27842a5865c78ee6082b98d98` |
| `validation/qsq_prospective/development_compatibility_smoke.py` | `427d70f` | `d51a31d7838d09175292e5024e7f969347c4de2e011446f6de863f2f3c0683bf` |
| `analysis/extensions_20260930/WP-G/rows.csv` (GP rows) | `4a95cfd` | `fabca4516fa67f671ae3eac9b5faf7850c5d7fca436ed189040ad7dd51180167` |
| `.github/workflows/qoac_hb_v2.yml` (template) | `77caf5d` | `2b71804a00378733905564e46a3af2c7b72a64620d78642672953815f3a3e196` |
| `analysis/qoac_hb_v2/DESIGN.md` (criteria) | `8a784a4` | `50220873675c5f5fffa7642e44b0188da04e47e1802ca5b6d3ed4b906b85511c` |
| `mechanism/independent_bader_20260908/reference_source/` (Henkelman Bader 1.05 source) | `af6ca3d` | tree `8f840f6413602eafd9c49c59be57654cb785c0ad` |
| frozen `validation/external_end_to_end.py` @ `893f931` (codec round trip) | `893f931` | `a4f791b7ab60b3a6300e49c9a857891a178099c5209354ecf6392310a47ec811` |
| frozen `validation/requirements-external-e2e.txt` @ `893f931` | `893f931` | `c6da91db628ff7f30c4b627d0a87660f5481f0a261cde5f608cefaffdfdf3656` |

Parameters (HB v2 defaults of the push-triggered run, identical to the P2 run):
- base codecs: all registered (`J`, `T1`, `GP`, `R3`, `GF`); GP has no candidates on fresh materials;
- post-processors: `none`, `uniform`, `hap:mu`, `ctp-uniform`, `ctp-hap:mu` for mu in {1e-4, 1e-2, 1}, plus the
  reference `hartree_only`;
- tau_B in {1e-3, 1e-4, 1e-5} e, primary 1e-4; Hartree certificate TAU_H = 1e-6 (historical and Nyquist-safe);
  closure 1e-9; at most 5 Bader attempts per (base, post, tau_B); R3 margins and floor, J/T1/GF ladders as in
  `run_joint_v2.py`;
- Henkelman Bader 1.05 built from the source above, `-ref` exact AECCAR0 + AECCAR2, `-b ongrid -vac 0.001`;
- environment: Python 3.12.14, `frozen/validation/requirements-external-e2e.txt` of `893f931`, ubuntu-24.04;
- 19 hash shards (`shard_for`, prefix `QOAC-HB-V2|`), 360 min per shard.

### Data-source adapter (infrastructure only)

`run_joint_v2.process` reads the AECCAR reference from the Materials Project S3 bucket by task id
(`b1.BUCKET + "aeccar{0,2}s/<task_id>.json.gz"`, decoded with `dev.decode_mp_chgcar`). The slabs are NOMAD entries, so
the unchanged code would fail every slab at that download. `run_joint_slab.py` serves exactly these two requests from
the NOMAD entry's raw directory and passes everything else to the HB v2 objects:
- `GET https://nomad-lab.eu/prod/v1/api/v1/entries/<entry_id>/raw/<basename>` through HB v2's `b1.fetch` (same
  retries), with byte count and SHA-256 checked against `aeccar_sources.csv`;
- decompression by extension with `dev.decompress_nomad`, and parsing with baderkit `Grid.from_dynamic`. These are
  the decompressor and parser that `dev.build_grid` uses for the NOMAD CHGCAR, so the reference is in the same units
  as rho;
- an entry without AECCAR raises `AECCAR0 unavailable ...` at that download; `run_joint_v2.main` records the
  material `FAILED`.

The CHGCAR path (`meta["url"]`, SHA-256 from the manifest, `dev.build_grid`) is HB v2's own. Checks done before
freezing, with no HB computation:
- `test_run_joint_slab.py` (routing, checksum, missing-AECCAR failure, frozen table vs manifest; parser and units
  identical to the NOMAD CHGCAR loader): 7/7 pass with baderkit 0.10.2;
- I/O smoke on `nomad-gPlluuEHW2ND`: CHGCAR and AECCAR0 + AECCAR2 load on the same 64x64x180 grid, finite;
  `nomad-g7Z9ilV401H7` raises `AECCAR0 unavailable`.

## 4. Execution

`.github/workflows/qoac_hb_slab.yml`, a copy of `qoac_hb_v2.yml` with the changes listed in `DEVIATIONS.md`. The run is
started by pushing the sentinel `analysis/qoac_hb_slab_20261007/RUN_MANIFEST` (content:
`analysis/qoac_hb_slab_20261007/manifest.csv`). The aggregate job commits
`analysis/qoac_hb_slab_20261007/results/manifest/` to this branch. The criteria are then evaluated with
`evaluate_criteria.py` (section 5), unchanged.

## 5. Acceptance — HB v2 confirmatory criteria, verbatim

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

Statistics and denominators, exactly as HB v2 computed them. `evaluate_criteria.py` implements them, and
`test_evaluate_criteria.py` reproduces HB v2's reported P2 values from its committed aggregate: 48/48; overhead
median 1.000, CI [1.000, 1.000]; 48/48 wins, median 1.317, CI [1.269, 1.360], min 1.096.
- Denominator of the counts in criteria 1 and 3: all planned materials. A FAILED or MISSING material is not
  analyzable and not certified, and is not a win.
- Count thresholds keep HB v2's fractions of the planned N: criterion 1 needs >= ceil(N x 46/48) and criterion 3
  >= ceil(N x 36/48) wins. For N = 32 these are **>= 31/32** and **>= 24/32**.
- Overhead: R3's `joint_overhead` in `joint_v2_best_post.csv` at tau_B = 1e-4, over materials where both
  `hartree_only` and the joint stream certify.
- Utility: ratio over materials where R3 certifies; win = ratio > 1. A sole certifier (no other of J, T1, GF
  certifies) is +inf, a win, and enters the median as 1e9 (the `aggregate_joint_v2.py` convention).
- Bootstrap: values in manifest order; `numpy.random.default_rng(20261007)` fresh for each statistic; 10,000
  resamples (`rng.integers(0, n, (10000, n))`); median of each; 2.5th and 97.5th percentiles. A statistic over an
  empty set fails its criterion.
- Failures (download, including a missing AECCAR; memory; solver) are recorded per material in `materials.csv`
  (`status`, `error`) and per setting in `failures.csv`. They are counted as above; failed materials are not
  retried.

**Verdict:** CONFIRMATORY PASS if and only if criteria 1, 2 and 3 all pass on the primary population (N = 32).

Known before any computation: 15/32 entries have no AECCAR, so criterion 1 on N = 32 can reach at most 17/32, below
the required 31/32. The primary verdict is therefore FAIL whatever the HB outcome on the other 17. This is recorded
here, before the run, so that it is not reported later as an observed result.

### Pre-registered secondary analysis (declared now, before any outcome)

The same three criteria, statistics and thresholds, applied to the 17 entries with an AECCAR reference
(`aeccar_available = 1`, fixed in section 2 from metadata only): N = 17, criterion 1 >= 17/17 (ceil(16.29)), criterion
3 >= 13/17 wins (ceil(12.75)). It is reported next to the primary analysis with its own pass/fail. It does not
replace the primary verdict.

## 6. Fixed after freezing

- No criterion, threshold, statistic, parameter, population or exclusion changes after any outcome is observed.
- A failure of the workflow itself (preflight or aggregate error, a cancelled or timed-out shard job, a runner fault)
  is an infrastructure failure. Only infrastructure may be fixed, and the fix is recorded in `DEVIATIONS.md` before
  the whole manifest is rerun. A per-material failure inside a completed shard is a result and is counted (section 5).
- `RESULTS.md` reports the numbers with denominators, the per-criterion verdicts against the thresholds above, and
  the failures, without interpretation beyond these criteria.
