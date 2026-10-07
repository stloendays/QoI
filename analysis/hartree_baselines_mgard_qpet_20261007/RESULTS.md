# Hartree-contract strongest baselines (MGARD s = −2, QPET): results

**Status: COMPLETE.**

- **Run used:** 37620406802. The sentinel was at `28574c3` and the aggregate was committed in `027e69a`.
- **Coverage:** 92 of 92 cohort materials analysed (P1 60, P3b 32), with 0 material-level failures.
- **Searches:** 3,588 in total (P1 2,340, P3b 1,248). Every search certified a point.
- **Protocol:** `PROTOCOL.md`, frozen at `16e8890` and unchanged since.
- **Comparison arms:** A1/A2/A3/A6 are the recorded law-run values from `part_a_material.csv` and were not rerun.

How the statistics are computed:

- **Median certified CR:** over the materials where the arm certified.
- **Ratios:** per material. The median and CI are taken over the materials where both arms certified; the
  convention is that of `aggregate_law.py`.
- **CI:** percentile bootstrap, 10,000 resamples over materials, `default_rng(20261006)` fresh for each statistic.
- **Wins:** ratio > 1.
- **Baseline never certified:** the baseline's search ran but found no passing point. Such cases are added to the
  wins.

## 1. Median certified CR and ratios

### τ = 1e-6 (primary)


#### P1 (60 MP bulk)

| | A1 | A2 | A3 | A6 | M2 | M-best | Q |
|---|---|---|---|---|---|---|---|
| median certified CR | 195 | 152 | 224 | 16 | 10.2 | 10.9 | 29.4 |
| n certified | 60 | 60 | 60 | 60 | 60 | 60 | 60 |

| ratio | median | 95% CI | wins / n both certified | baseline never certified | wins incl. never certified | min | max |
|---|---|---|---|---|---|---|---|
| A1/M2 | 18.2 | 15.3–21.7 | 60 / 60 | 0 | 60 | 5.74 | 69.9 |
| A1/M-best | 16.6 | 14.3–19.5 | 60 / 60 | 0 | 60 | 5.28 | 63.3 |
| A1/Q | 6.31 | 5.53–6.95 | 60 / 60 | 0 | 60 | 2.62 | 30.4 |
| A3/M2 | 20.3 | 17.5–25 | 60 / 60 | 0 | 60 | 5.94 | 111 |
| A3/Q | 6.91 | 5.92–8.15 | 60 / 60 | 0 | 60 | 2.71 | 39.6 |

Sub-arms, median certified CR (n): M_s=inf 4.38 (60); M_s=0 9.15 (60); M_s=-1 10.9 (60); M_s=-2 10.2 (60); Q_hpez 13.4 (60); Q_sperr 29.4 (60); Q_sz3 12.8 (60).

QPET configurations, median certified CR (n): Q_hpez_b4 13.4 (60); Q_hpez_b8 13.4 (60); Q_hpez_b16 13.4 (60); Q_sperr_b4 29.2 (60); Q_sperr_b8 26.2 (60); Q_sperr_b16 25 (60); Q_sz3_b4 12.8 (60); Q_sz3_b8 12.8 (60); Q_sz3_b16 12.8 (60).

#### P3b (32 NOMAD slabs)

| | A1 | A2 | A3 | A6 | M2 | M-best | Q |
|---|---|---|---|---|---|---|---|
| median certified CR | 504 | 353 | 647 | 23.3 | 21 | 23.1 | 46 |
| n certified | 32 | 32 | 32 | 32 | 32 | 32 | 32 |

| ratio | median | 95% CI | wins / n both certified | baseline never certified | wins incl. never certified | min | max |
|---|---|---|---|---|---|---|---|
| A1/M2 | 21 | 17.5–27.9 | 32 / 32 | 0 | 32 | 9.11 | 71.6 |
| A1/M-best | 19.6 | 15.7–24.9 | 32 / 32 | 0 | 32 | 8.43 | 61.2 |
| A1/Q | 9.47 | 8.14–12.8 | 32 / 32 | 0 | 32 | 3.78 | 30 |
| A3/M2 | 27.3 | 20.1–35.6 | 32 / 32 | 0 | 32 | 9.94 | 113 |
| A3/Q | 11.3 | 9.62–16.5 | 32 / 32 | 0 | 32 | 4.06 | 47.1 |

Sub-arms, median certified CR (n): M_s=inf 6.75 (32); M_s=0 17.2 (32); M_s=-1 22.8 (32); M_s=-2 21 (32); Q_hpez 22.7 (32); Q_sperr 46 (32); Q_sz3 16 (32).

QPET configurations, median certified CR (n): Q_hpez_b4 21.9 (32); Q_hpez_b8 21.7 (32); Q_hpez_b16 21.2 (32); Q_sperr_b4 46 (32); Q_sperr_b8 39.8 (32); Q_sperr_b16 35.3 (32); Q_sz3_b4 16 (32); Q_sz3_b8 16 (32); Q_sz3_b16 16 (32).

### τ = 1e-4


#### P1 (60 MP bulk)

| | A1 | A2 | A3 | A6 | M2 | M-best | Q |
|---|---|---|---|---|---|---|---|
| median certified CR | 818 | 969 | 1303 | 79.2 | 59.2 | 73.4 | 158 |
| n certified | 60 | 60 | 60 | 60 | 60 | 60 | 60 |

| ratio | median | 95% CI | wins / n both certified | baseline never certified | wins incl. never certified | min | max |
|---|---|---|---|---|---|---|---|
| A1/M2 | 12.5 | 11.4–15.4 | 60 / 60 | 0 | 60 | 1.98 | 46.2 |
| A1/M-best | 9.75 | 9–13.1 | 60 / 60 | 0 | 60 | 1.86 | 36.2 |
| A1/Q | 5.22 | 4.6–5.93 | 60 / 60 | 0 | 60 | 1.16 | 9.79 |
| A3/M2 | 20.5 | 17.2–23.4 | 60 / 60 | 0 | 60 | 4.82 | 82.1 |
| A3/Q | 7.97 | 6.84–9.33 | 60 / 60 | 0 | 60 | 2.81 | 22.9 |

Sub-arms, median certified CR (n): M_s=inf 8.82 (60); M_s=0 50.9 (60); M_s=-1 73.1 (60); M_s=-2 59.2 (60); Q_hpez 103 (60); Q_sperr 154 (60); Q_sz3 57.9 (60).

QPET configurations, median certified CR (n): Q_hpez_b4 94.8 (60); Q_hpez_b8 102 (60); Q_hpez_b16 101 (60); Q_sperr_b4 151 (60); Q_sperr_b8 91.8 (60); Q_sperr_b16 71.8 (60); Q_sz3_b4 56.5 (60); Q_sz3_b8 57.9 (60); Q_sz3_b16 57.9 (60).

#### P3b (32 NOMAD slabs)

| | A1 | A2 | A3 | A6 | M2 | M-best | Q |
|---|---|---|---|---|---|---|---|
| median certified CR | 1771 | 2309 | 3552 | 108 | 196 | 244 | 257 |
| n certified | 32 | 32 | 32 | 32 | 32 | 32 | 32 |

| ratio | median | 95% CI | wins / n both certified | baseline never certified | wins incl. never certified | min | max |
|---|---|---|---|---|---|---|---|
| A1/M2 | 7.97 | 5.32–11.1 | 32 / 32 | 0 | 32 | 1.58 | 31 |
| A1/M-best | 6.63 | 4.17–9.04 | 32 / 32 | 0 | 32 | 1.32 | 23.9 |
| A1/Q | 7.56 | 5.07–9.13 | 32 / 32 | 0 | 32 | 2.11 | 15.3 |
| A3/M2 | 15 | 9.31–20.2 | 32 / 32 | 0 | 32 | 4.23 | 93.2 |
| A3/Q | 15.6 | 9.67–21.5 | 32 / 32 | 0 | 32 | 3.5 | 40.3 |

Sub-arms, median certified CR (n): M_s=inf 14.6 (32); M_s=0 130 (32); M_s=-1 228 (32); M_s=-2 196 (32); Q_hpez 144 (32); Q_sperr 248 (32); Q_sz3 73.1 (32).

QPET configurations, median certified CR (n): Q_hpez_b4 144 (32); Q_hpez_b8 126 (32); Q_hpez_b16 117 (32); Q_sperr_b4 248 (32); Q_sperr_b8 145 (32); Q_sperr_b16 89.5 (32); Q_sz3_b4 71.7 (32); Q_sz3_b8 73.1 (32); Q_sz3_b16 73.1 (32).

### τ = 1e-8


#### P1 (60 MP bulk)

| | A1 | A2 | A3 | A6 | M2 | M-best | Q |
|---|---|---|---|---|---|---|---|
| median certified CR | 24.6 | 14.9 | 25 | 7.12 | 5.06 | 5.28 | 9.99 |
| n certified | 60 | 60 | 60 | 60 | 60 | 60 | 60 |

| ratio | median | 95% CI | wins / n both certified | baseline never certified | wins incl. never certified | min | max |
|---|---|---|---|---|---|---|---|
| A1/M2 | 4.69 | 4.27–5.77 | 60 / 60 | 0 | 60 | 1.77 | 31.7 |
| A1/M-best | 4.55 | 4.11–5.67 | 60 / 60 | 0 | 60 | 1.72 | 31 |
| A1/Q | 2.33 | 2–2.85 | 60 / 60 | 0 | 60 | 1.03 | 15.2 |
| A3/M2 | 4.79 | 4.32–6.09 | 60 / 60 | 0 | 60 | 1.81 | 34.9 |
| A3/Q | 2.36 | 2.05–2.97 | 60 / 60 | 0 | 60 | 1.05 | 16.8 |

Sub-arms, median certified CR (n): M_s=inf 2.72 (60); M_s=0 4.53 (60); M_s=-1 5.26 (60); M_s=-2 5.06 (60); Q_hpez 6.16 (60); Q_sperr 9.79 (60); Q_sz3 3.56 (60).

QPET configurations, median certified CR (n): Q_hpez_b4 6 (60); Q_hpez_b8 5.59 (60); Q_hpez_b16 5.79 (60); Q_sperr_b4 9.59 (60); Q_sperr_b8 9.51 (60); Q_sperr_b16 9.56 (60); Q_sz3_b4 3.56 (60); Q_sz3_b8 3.56 (60); Q_sz3_b16 3.56 (60).

#### P3b (32 NOMAD slabs)

| | A1 | A2 | A3 | A6 | M2 | M-best | Q |
|---|---|---|---|---|---|---|---|
| median certified CR | 64.9 | 27.2 | 70.3 | 10 | 8.65 | 8.89 | 18.2 |
| n certified | 32 | 32 | 32 | 32 | 32 | 32 | 32 |

| ratio | median | 95% CI | wins / n both certified | baseline never certified | wins incl. never certified | min | max |
|---|---|---|---|---|---|---|---|
| A1/M2 | 7.99 | 5.2–11.8 | 32 / 32 | 0 | 32 | 3.1 | 35.9 |
| A1/M-best | 7.42 | 4.91–10.8 | 32 / 32 | 0 | 32 | 3 | 34.9 |
| A1/Q | 3.84 | 2.7–4.83 | 32 / 32 | 0 | 32 | 1.37 | 7.72 |
| A3/M2 | 8.43 | 5.42–13.3 | 32 / 32 | 0 | 32 | 3.16 | 41 |
| A3/Q | 4.09 | 2.88–5.28 | 32 / 32 | 0 | 32 | 1.43 | 8.52 |

Sub-arms, median certified CR (n): M_s=inf 4.04 (32); M_s=0 7.42 (32); M_s=-1 8.89 (32); M_s=-2 8.65 (32); Q_hpez 8.54 (32); Q_sperr 16 (32); Q_sz3 7.11 (32).

QPET configurations, median certified CR (n): Q_hpez_b4 7.98 (32); Q_hpez_b8 7.78 (32); Q_hpez_b16 8.05 (32); Q_sperr_b4 15.4 (32); Q_sperr_b8 15.1 (32); Q_sperr_b16 14.4 (32); Q_sz3_b4 7.11 (32); Q_sz3_b8 7.1 (32); Q_sz3_b16 7.1 (32).

## 2. Feasibility facts

### M2: MGARD with `--smoothness -2`

The build was upstream MGARD `ac53ff9cec8cf2dee08892f0400ae0ddb755b193` with TCLAP 1.4 headers (`61cfae16…`),
OpenMPI, the CLI and OpenMP. The build log is `results/toolchain/mgard_build.log`.

**The CLI accepted `--smoothness -2`.** Tiny-array probe (16³ standard normal, seed 0, `--tolerance 0.01`; from
`results/toolchain/probe.json`):

| s | compress rc | decompress rc | decoded size OK, finite | stream bytes | L∞ error |
|---|---|---|---|---|---|
| inf | 0 | 0 | yes | 11,401 | 2.18e-4 |
| 0 | 0 | 0 | yes | 5,103 | 0.0176 |
| −1 | 0 | 0 | yes | 2,814 | 0.324 |
| −2 | 0 | 0 | yes | 889 | 3.03 |

M2 was therefore run, and M-best is taken over s ∈ {∞, 0, −1, −2}. In the cohorts, s = −2 had 0 failed
evaluations: 0 of 6,298 in P1 and 0 of 3,347 in P3b.

### Q: QPET

**Source.** The authors' artifact `https://github.com/JLiu-1/QPET-Artifact`, at these commits:

- `szfamily_qpet_revision` @ `5d17cb1647caf001bd7355c617856c72c4b6475e`: CLI `hpez` (SZ3 and HPEZ hosts);
- `sperr_qpet_revision` @ `1874108fe7a38b5eb0c63874889af0a16a248ad4`: CLI `sperr3d`;
- dependency SymEngine `v0.14.0` (`fac9314c78f2809570494017efc6603befeb4eda`).

All builds reported OK (`results/toolchain/versions.txt`).

**Supported QoIs found in the source and paper.** The supported QoIs are all local:

- pointwise f(x);
- multivariate over co-located variables;
- regional QoIs: block average (`qoiRegionMode = 1`), difference Laplacian (`2`) and gradient length (`3`).

There is no Poisson or Hartree functional.

**Configuration used** (PROTOCOL §5.2). Each configuration had its own equal search, and Q is the highest certified
CR over all 9.

- QoI: regional average of f(x) = x over b³ blocks, with b ∈ {4, 8, 16}.
- QoI bound: absolute, value t (the searched parameter).
- Base pointwise bound: absolute, equal to ptp(ρ).
- Hosts:
  - SZ3-QPET: `hpez -q 0`;
  - HPEZ-QPET: `hpez -q 3`;
  - SPERR-QPET: `sperr3d --qoi_id 14 --qoi_string x --qoi_bs b --ftype 64`.
- The `hpez` hosts receive float32 input, which is the only path the authors' CLI compiles. The certificate is
  always evaluated on the decoded field cast to float64.

**Probe.** All 9 configurations round-tripped. The probe used a 48 × 56 × 72 smooth synthetic array at
t = 1e-3 × ptp:

| configuration | stream bytes | pointwise L∞ / t | max block-average error / t |
|---|---|---|---|
| Q_sz3_b4 | 57,328 | 2 | 0.531 |
| Q_sz3_b8 | 57,328 | 2 | 0.146 |
| Q_sz3_b16 | 57,328 | 2 | 0.0774 |
| Q_hpez_b4 | 59,524 | 2 | 0.5 |
| Q_hpez_b8 | 48,264 | 3 | 0.228 |
| Q_hpez_b16 | 37,802 | 4 | 0.108 |
| Q_sperr_b4 | 32,230 | 6.16 | 1 |
| Q_sperr_b8 | 18,204 | 17 | 1 |
| Q_sperr_b16 | 240,527 | 37.3 | 1 |

## 3. Failures

**Material level.** 0 in P1 and 0 in P3b.

**Memory (run 37620406802).** All 92 shards ended with cgroup `oom_kill 0`. The cgroup `memory.peak` was at most
9.65 GiB, with a median of 9.37 GiB, under the 13 GiB cap. No evaluation exited with rc −9. Source: the
`Run material` step log of each shard job.

**Execution errors (codec exit codes).** All are in the authors' `hpez` CLI:

- rc −6: glibc heap-corruption abort;
- rc −11: segmentation fault.

`sperr3d` and `mgard` had 0 execution errors. There were no timeouts and no other error types. Each failed
evaluation counts as a non-passing point (PROTOCOL §4).

#### P1 (60 MP bulk)

| configuration | failed evaluations | rc −6 | rc −11 | rc −9 | other | materials affected |
|---|---|---|---|---|---|---|
| Q_hpez_b16 | 352 | 341 | 11 | 0 | 0 | 22 |
| Q_hpez_b4 | 373 | 369 | 4 | 0 | 0 | 24 |
| Q_hpez_b8 | 397 | 390 | 7 | 0 | 0 | 25 |
| Q_sz3_b16 | 776 | 679 | 97 | 0 | 0 | 46 |
| Q_sz3_b4 | 776 | 673 | 103 | 0 | 0 | 46 |
| Q_sz3_b8 | 776 | 676 | 100 | 0 | 0 | 46 |

| arm | evaluations | failed evaluations | materials with failed evaluations | searches | searches, lower bound raised | searches, codec never executed | search wall time per material, median s (τ = 1e-6 / 1e-4 / 1e-8) | codec + certificate h |
|---|---|---|---|---|---|---|---|---|
| M2 | 6298 | 0 | 0 | 180 | 0 | 0 | 16 / 18 / 20 | 1.24 |
| M-best | 25351 | 0 | 0 | 720 | 0 | 0 | 64 / 66 / 78 | 4.86 |
| Q | 52839 | 3450 | 50 | 1620 | 0 | 0 | 60 / 89 / 78 | 5.09 |

Material-level failures: 0.

#### P3b (32 NOMAD slabs)

| configuration | failed evaluations | rc −6 | rc −11 | rc −9 | other | materials affected |
|---|---|---|---|---|---|---|
| Q_hpez_b16 | 46 | 44 | 2 | 0 | 0 | 4 |
| Q_hpez_b4 | 67 | 66 | 1 | 0 | 0 | 5 |
| Q_hpez_b8 | 75 | 75 | 0 | 0 | 0 | 6 |
| Q_sz3_b16 | 85 | 64 | 21 | 0 | 0 | 6 |
| Q_sz3_b4 | 85 | 64 | 21 | 0 | 0 | 6 |
| Q_sz3_b8 | 85 | 65 | 20 | 0 | 0 | 6 |

| arm | evaluations | failed evaluations | materials with failed evaluations | searches | searches, lower bound raised | searches, codec never executed | search wall time per material, median s (τ = 1e-6 / 1e-4 / 1e-8) | codec + certificate h |
|---|---|---|---|---|---|---|---|---|
| M2 | 3347 | 0 | 0 | 96 | 0 | 0 | 28 / 30 / 28 | 0.78 |
| M-best | 13504 | 0 | 0 | 384 | 0 | 0 | 107 / 112 / 118 | 3.03 |
| Q | 29468 | 443 | 10 | 864 | 9 | 0 | 109 / 123 / 139 | 3.46 |

Material-level failures: 0.

**Lower search bound raised** (PROTOCOL §4). This happened in 9 searches, all on `nomad-uxkQqRHBpSox` (P3b):
`Q_hpez_b4`, `Q_hpez_b8` and `Q_hpez_b16`, at each τ. In each case the bound rose by one decade, from 1e-14 × ptp
to 1e-13 × ptp.

**Searches that ended without a certified point.** 0 of 3,588. Searches in which the codec never executed: 0.

**Superseded run 37601828909** (sentinel `839cf5e`, aggregate `3823863`). 32 of 92 shards (25 P1, 7 P3b) were lost
when the runner VM shut down (exit 143), with four concurrent codec processes. Its 60 completed shards (P1 35, P3b
25) produced 2,340 searches. In the rerun, all 2,340 have byte-identical selected stream sizes and identical
certified flags (P1 1,365 of 1,365; P3b 975 of 975).

**Probe-phase shakedown** (run 37598888695; `mp-3148759`, P1 engineering, not in either cohort). There were 88
failed evaluations, all `hpez` with rc −6. The shakedown rows are in `results/probe/`.

## 4. Runs, commits and deviations

| step | run id | commit |
|---|---|---|
| protocol freeze (PROTOCOL.md, code, workflow) | — | `16e8890` |
| probe phase (toolchain, probes, shakedown) | 37598888695 | sentinel `a5e6835`, results `1544e0d` |
| run phase, superseded (32 of 92 shards lost) | 37601828909 | sentinel `839cf5e`, results `3823863` |
| infrastructure fix, DEVIATIONS §B.1 | — | `883fdfb` |
| run phase, used (95 of 95 jobs successful) | 37620406802 | sentinel `28574c3`, results `027e69a` |

The entries in `DEVIATIONS.md` are:

- **§A:** every change of the workflow from the copied `general_qoac_law.yml`, plus the MGARD build steps taken
  from `qoac_h_strong_baselines.yml`.
- **§B:** the probe phase made no infrastructure change. It records the shakedown's `hpez` aborts.
- **§B.1:** the run phase was rerun after the runner-VM loss. The changes were `--workers 1` and a cgroup with
  `memory.max = 13G` and swap 0, logging `memory.peak` and `oom_kill`. No arm, configuration, interval, certificate,
  τ, statistic or population changed.
- **§B.2:** reporting after the run phase started. `render_tables.py` was added; it formats `SUMMARY.json` and
  tabulates `failures.csv`. The statistics were independently recomputed with 0 mismatches.

The wall time per arm is in the failure tables above. The total codec + certificate time was:

| arm | P1 | P3b |
|---|---|---|
| M2 | 1.24 h | 0.78 h |
| M-best | 4.86 h | 3.03 h |
| Q | 5.09 h | 3.46 h |

## 5. Files

All paths are under `analysis/hartree_baselines_mgard_qpet_20261007/`.

- `PROTOCOL.md`, `DEVIATIONS.md`, `RESULTS.md`.
- Code:
  - `run_mq.py` (runner);
  - `codecs_mq.py` (MGARD/QPET invocations);
  - `aggregate_mq.py` (statistics);
  - `probe_toolchain.py`;
  - `test_mq.py`;
  - `render_tables.py` (table formatting).
- Per cohort, `results/run_{P1,P3B}_CONFIRMATORY/`:
  - `SUMMARY.json`;
  - `material.csv` (certified CR of every arm and configuration per material and τ);
  - `rows.csv` (selected point of every search);
  - `evals.csv.gz` (every evaluated point);
  - `failures.csv`.
- Run level:
  - `results/SUMMARY.json`;
  - `results/toolchain/`: probe record, build logs, CLI help, versions;
  - `results/run_id.txt`.
- Probe phase: `results/probe/`.
- Workflow: `.github/workflows/hartree_baselines_mgard_qpet.yml`.
