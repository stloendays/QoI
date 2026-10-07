# Deviations log

## A. The new workflow compared with the copied workflow

`.github/workflows/hartree_baselines_mgard_qpet.yml` is a copy of `.github/workflows/general_qoac_law.yml`, which
drives P1 Part A. Its P3b twin, `general_qoac_law_p3b.yml`, has the same job structure. The MGARD build steps come
from the `mgard` job of `.github/workflows/qoac_h_strong_baselines.yml`. Every change from the copied files is
listed below.

### Trigger, concurrency and globals

1. `name` is now `Hartree strongest baselines MGARD s=-2 and QPET`.
2. `on.push.branches` is `research/hartree-baselines-mgard-qpet-20261007`.
   - Was: `research/general-qoac-law-confirm-20261006`.
3. `on.push.paths` is only the sentinel `analysis/hartree_baselines_mgard_qpet_20261007/PHASE`.
   - Was: `analysis/general_qoac_law/PHASE` and the workflow file itself.
   - Committing the workflow therefore starts no run.
4. `workflow_dispatch` is removed. It is unusable because the default branch `main` is a placeholder.
5. The concurrency group is `hartree-baselines-mgard-qpet-20261007`.
   - Was: `general-qoac-law-20261006`.
   - `cancel-in-progress: false` is unchanged.
6. A workflow-level `env` block is added:
   - `D`, the analysis directory;
   - the pinned upstream commits: MGARD, SymEngine tag, and the two QPET commits.

### `preflight`

7. Phases are `probe | run`. Was: `predict | run`.
8. The unit tests are now `test_mq.py`, plus the unchanged `test_codec_qoac_v03.py`.
   - Removed: `test_policy_codec.py`, `test_operators.py` and `test_gain_predictors.py`. They test code that this
     study does not use.
9. Added: `run_mq.py --check-inputs`, which verifies the PROTOCOL §10 SHA-256 table.
10. The material matrix now comes from `run_mq.py --list-matrix`:
    - `probe`: one P1-engineering shakedown material;
    - `run`: P1 confirmatory plus P3b confirmatory, 92 items.
    - The copied workflow listed P1 engineering plus P1 confirmatory.
11. Removed: the missing-predictions check, which belongs to law Part B.

### `toolchain` (new job, not in `general_qoac_law.yml`)

12. Builds MGARD with the commands of the `mgard` job of `qoac_h_strong_baselines.yml`: the same apt packages,
    TCLAP 1.4 headers, and the CMake flags `-DCMAKE_BUILD_TYPE=Release -DMGARD_ENABLE_CLI=ON -DMGARD_ENABLE_OPENMP=ON`.
    It differs from that job in four ways:
    1. The MGARD clone is checked out at the pinned commit `ac53ff9…`.
       - That job built the default-branch HEAD.
       - HEAD was `ac53ff9…` on 2026-10-07 and was also the SI Note 2.4 commit.
    2. `libgmp-dev` is added to the apt list. QPET needs it.
    3. The install prefix is `$GITHUB_WORKSPACE/tc/mgard`.
    4. The tarball contains the whole `tc/` tree.
13. Builds SymEngine `v0.14.0`, QPET `szfamily_qpet_revision@5d17cb1…` and QPET `sperr_qpet_revision@1874108…`
    from upstream source. Both QPET builds get `-I$TC/symengine/include -include cstdint`; the forced `<cstdint>` include is for GCC 13 on
    ubuntu-24.04. The SPERR build also gets `-DBUILD_UNIT_TESTS=OFF`, which avoids the GoogleTest download.
14. Runs `probe_toolchain.py` (PROTOCOL §5, §8) and captures the `--help` output of the three CLIs.
15. Uploads two artifacts:
    - `hbmq-probe`: the probe record and the build logs;
    - `toolchain-hbmq`: the toolchain tarball.

### `shard`

16. `needs: [preflight, toolchain]`. It runs only if both succeeded.
    - Was: `needs: preflight`.
17. `actions/checkout` of `repo`, `frozen@893f931`, Python 3.12.14 and the frozen pip stack are unchanged.
18. Added: download `toolchain-hbmq`, install the runtime libraries (`libzstd1 libprotobuf32t64 libopenmpi3t64
    libgmp10 libgomp1`), and set `PATH`/`LD_LIBRARY_PATH`. The runtime libraries are adapted from
    `qoac_h_strong_baselines.yml`.
19. The command is `run_mq.py --workers 4` with `OMP_NUM_THREADS=1`.
    - Was: `run_part_b.py` and `run_part_a.py`.
20. Output paths:
    - Output dir: `$RUNNER_TEMP/hbmq_<id>`. Was: `law_<id>`.
    - Artifact name: `hbmq-shard-<phase>-<id>`. Was: `law-<phase>-<id>`.
21. Unchanged: `max-parallel 20`, `timeout-minutes 360`, `fail-fast: false`.

### `aggregate`

22. `needs: [preflight, toolchain, shard]`. Was: `[preflight, shard]`.
23. The download pattern is `hbmq-*`. Was: `law-<phase>-*`.
24. Runs `aggregate_mq.py`. Was: `aggregate_law.py`.
25. Commits `analysis/hartree_baselines_mgard_qpet_20261007/results/`: `results/probe/` for the probe phase, and
    `results/` for the run phase. It also records the run id.
26. The pull/push target is `research/hartree-baselines-mgard-qpet-20261007`.
27. Unchanged: the aggregation pins `numpy==2.3.5 pandas==2.3.3 scipy==1.18.1` and the bot identity.

## B. Infrastructure deviations after the protocol freeze

None so far. Each one is recorded here before any rerun.

The probe phase was run 37598888695, at commit `a5e6835`; its results were committed in `1544e0d`. Every build
succeeded and every probe was feasible. In the shakedown material, the authors' `hpez` CLI aborted (rc −6, glibc
heap-corruption message) at some tolerances:

- SZ3 host (`-q 0`): 19 evaluations per block size.
- HPEZ host (`-q 3`): 1, 12 and 18 evaluations for b = 4, 8 and 16.

Under PROTOCOL §4 these are counted non-passing points, and the protocol is unchanged. No infrastructure change was
made before the run phase.
