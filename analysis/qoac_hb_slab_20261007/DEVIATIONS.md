# Deviations from the HB v2 code path and workflow

Every departure from `analysis/qoac_hb_v2/` and `.github/workflows/qoac_hb_v2.yml` (`77caf5d`) is listed here, with
its date and whether it was made before or after any slab outcome existed. None of them changes a codec, a
post-processor, a certificate, a tolerance, a criterion or the population.

## Before the run (2026-10-07, recorded with the protocol freeze)

D1. **NOMAD AECCAR source** (`run_joint_slab.py`). HB v2 reads the AECCAR reference from the Materials Project S3
bucket by task id, and the P3b slabs are NOMAD entries. The adapter serves those two downloads from the NOMAD entry's
raw directory. It checks byte count and SHA-256 against `aeccar_sources.csv`, and decompresses and parses with the
same functions HB v2's loader uses for a NOMAD CHGCAR. It also writes `aeccar_downloads_shard_XX.csv` (entry, file,
bytes, SHA-256) next to the shard outputs. `run_joint_v2.py` itself is imported unmodified. Details: PROTOCOL.md
section 3.

D2. **Workflow** `.github/workflows/qoac_hb_slab.yml` = `qoac_hb_v2.yml` with:
- the requested changes:
  - trigger branch `research/qoac-hb-slab-20261007`, also in the preflight `GITHUB_REF` check and in the
    aggregate pull/push;
  - sentinel and manifest `analysis/qoac_hb_slab_20261007/RUN_MANIFEST` -> `analysis/qoac_hb_slab_20261007/manifest.csv`;
  - output `analysis/qoac_hb_slab_20261007/results/<stem>`;
  - workflow name `QOAC-HB slab confirmation (P3b fresh slabs)`;
- infrastructure changes beyond those:
  - concurrency group renamed `qoac-hb-slab-20261007-...`, so it is not shared with HB v2;
  - preflight also compiles `analysis/qoac_hb_slab_20261007/*.py` and runs `test_run_joint_slab.py` and
    `test_evaluate_criteria.py`. Preflight has no baderkit, so the parser test is skipped there; it passed locally;
  - the shard step calls `run_joint_slab.py` (D1) with HB v2's unchanged argument list;
  - the aggregate step also concatenates `aeccar_downloads_shard_*.csv` into `results/<stem>/aeccar_downloads.csv`;
  - the result commit message reads `QOAC-HB slab results`.

  Unchanged: runner type, timeouts, the 19-shard matrix and `shard_for`, the Python and package pins, the frozen
  checkout `893f931`, the Henkelman Bader build, the default mu and tau_B, the artifact names and the aggregator.

D3. **Criteria evaluator** (`evaluate_criteria.py`). HB v2 has no committed criteria script: its aggregator applies
no gates, and the criteria were evaluated when its `RESULTS.md` was written. The evaluator implements the frozen
criteria. `test_evaluate_criteria.py` shows that it reproduces every number HB v2 reported for P2 from HB v2's
committed aggregate.

D4. **Count thresholds for N != 48.** HB v2 wrote its counts for N = 48. They are applied as the same fractions of the
planned N, rounded up: 31/32 and 24/32 here, and 17/17 and 13/17 for the secondary analysis.

D5. **No engineering phase.** HB v2 ran 12 engineering materials (gates E1/E2/E4) before its confirmation. Here the
method is HB v2's frozen method, applied without tuning, so only the confirmatory criteria are used.

D6. **Pre-registered secondary analysis** on the 17 entries with an AECCAR reference (PROTOCOL.md section 5). It is
added; it does not replace the primary analysis.

## After the run starts

None. The single run (CI 37579899219) completed with no infrastructure failure; nothing was fixed or rerun.
