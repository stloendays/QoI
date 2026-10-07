# Deviations from the P3b law code path and workflow

This file lists every departure from `.github/workflows/general_qoac_law_p3b.yml` (`39ba728`) and from the frozen
Part A code (`analysis/qoac_v03_rdo/run_engineering.py`, `7ca412e`). For each one it gives the date and whether it was
made before or after any outcome on a decoded P3b stream existed. None of them changes a codec, a parameter, a
certificate, a tolerance or the population.

## Before the run (2026-10-07, recorded with the protocol freeze)

D1. **Workflow** `.github/workflows/p3b_vacuum_level.yml` = `general_qoac_law_p3b.yml` with these changes.

The requested changes:
- `name`: `P3b vacuum-level (work-function) error`;
- trigger `on.push.branches`: `research/p3b-vacuum-level-20261007`; the aggregate pull and push target the same
  branch;
- `on.push.paths`: only the new sentinel `analysis/p3b_vacuum_level_20261007/RUN_SENTINEL`. The template listed
  `analysis/general_qoac_law/P3B_PHASE` and `.github/workflows/general_qoac_law.yml`; the workflow file is no longer
  listed, so committing it does not start a run;
- concurrency group `p3b-vacuum-level-20261007`, replacing `general-qoac-law-p3b-20261006`;
- outputs: shard directory `$RUNNER_TEMP/vac_<id>`, artifacts `p3bvac-<id>` (were `law_<id>`, `lawp3b-<phase>-<id>`),
  committed results `analysis/p3b_vacuum_level_20261007/results/` (was `analysis/general_qoac_law/results/run_P3B_*`).

Infrastructure changes beyond those:
- the select / predict / run phase machinery is removed: there is no `P3B_PHASE` read, no `select` job and no
  prediction check. This item has one phase, and it reads the already committed run;
- preflight also runs `test_vacuum_level.py` and checks the SHA-256 of the manifest and of the recorded
  `part_a_rows.csv`; its matrix list is the same 32 manifest ids;
- the shard step calls `run_vacuum_level.py` (with `--rows` pointing at the recorded `part_a_rows.csv`), not
  `run_part_b.py` + `run_part_a.py`; it also writes `pip freeze` to the shard output;
- the aggregate step calls `aggregate_vacuum_level.py`, not `aggregate_law.py`. It also writes `results/RUN_ID` and
  `results/pip_freeze_shard.txt`, and its commit message carries the run id and the `Co-Authored-By` line;
- the aggregate `if:` no longer tests the phase.

Unchanged: `workflow_dispatch` (kept, though unusable here), `permissions`, runner type, the Python version, the
package pins of every job, the frozen checkout `893f931`, `max-parallel: 20`, `fail-fast: false`, the 360-min shard
timeout, pip caching and the upload / download actions.

D2. **Route S instrumentation.** `run_engineering.material` is called unchanged. For the duration of the call, its
module-level `certify` is replaced by a wrapper that calls the original and returns its result unchanged. The wrapper
also keeps the planar average of (decoded - reference) along the normal axis, and mean(decoded - reference). Surviving
rows are matched to wrapper calls in order by their (hartree_hist, hartree_safe, density_Linf, density_RMSE) tuple.

D3. **Download retries.** `run_vacuum_level.fetch` calls the frozen `dev.fetch_exact` up to 3 times, with 30 s and 60 s
pauses, where `material` makes a single attempt. The SHA-256 and byte-count checks are those of `dev.fetch_exact`. It
writes the same cache file (`<cache>/<material_id>.src`) that `material` reads and SHA-checks, so route S does not
download again.

D4. **Route R** regenerates streams from recorded parameter strings with the frozen functions (PROTOCOL.md section 3).
This is new code, but it calls only frozen functions, with the same arguments as `material`.

## After the run starts

None so far.
