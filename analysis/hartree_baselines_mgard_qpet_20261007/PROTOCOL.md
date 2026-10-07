# Hartree-contract strongest baselines: MGARD with s = −2 and QPET, prospective cohorts P1 and P3b

Freeze date: 2026-10-07. This protocol is committed and pushed before any M or Q arm is evaluated on any P1 or P3b
material. It is a descriptive strongest-baseline record: there is no pass/fail gate.

Branch: `research/hartree-baselines-mgard-qpet-20261007`, created from the manuscript authority
`paper/nc-reopen-20261007` at `87b3a65`. Nothing under `paper/` or `figures/` is changed.

## 1. Question

The manuscript compares the closed-form operator law (A1) with ZFP/SZ3/SPERR (A6). This study adds two QoI-aware
baselines under the same Hartree contract and the same equal search:

- **M2**: MGARD with smoothness s = −2. Its squared s-norm weights the error spectrum by |G|^(2s) = |G|^-4, which is
  the error weight of the Hartree potential. The SI Note 2.4 study (`analysis/qoac_h_strong_baselines/`) ran only
  s ∈ {∞, 0, −1}.
- **Q**: QPET (Liu et al., PVLDB 18, 2440–2453, 2025; arXiv 2412.02799), configured with its closest supported
  linear low-pass QoI.

## 2. Population

Both cohorts are unchanged. Each manifest is verified by SHA-256 in CI before any job starts
(`run_mq.py --check-inputs`, table in §10). Each source file is verified against the manifest's `sha256` and
`source_bytes` by `development_compatibility_smoke.fetch_exact`, and each grid is checked against `npoints`. A
mismatch is a material-level failure.

| cohort | manifest | n |
|---|---|---|
| P1 | `analysis/fresh_population_20261006/P1_CONFIRMATORY_MANIFEST.csv` (Materials Project bulk) | 60 |
| P3b | `analysis/fresh_population_20261006/P3B_CONFIRMATORY_MANIFEST.csv` (NOMAD surface slabs) | 32 |

Shakedown (probe phase only, §8): `mp-3148759` from `P1_ENGINEERING_MANIFEST.csv`. It is the smallest engineering
grid and is not a member of either cohort. Its results enter no statistic.

## 3. Contract and certificate (identical to arms A1/A6 of `analysis/general_qoac_law/DESIGN.md`)

- Loader: the code path of `run_engineering.material`, which `run_part_a.py` calls. It uses `fetch_exact`,
  `build_grid` and `x = grid.total` as float64.
- Certificate: `run_engineering.certify`, which calls `codec_qoac_h_v02.hartree_error_metrics(rec − x, lattice,
  rh, rs)`. A stream is certified at τ iff the historical **and** the Nyquist-safe Hartree relative RMS errors are
  both < τ.
- τ ∈ {1e-4, 1e-6, 1e-8}. Primary τ = 1e-6.
- Decoding: every evaluated stream is written to a file by the codec's compression command. A separate process runs
  the codec's own decompression command on that file alone, and the decoded field is certified. Nothing else is
  passed to the decoder.
- CR = 8N / size of the complete compressed file, including all headers and containers. The numerator is 8N for
  every arm, including the float32-input QPET hosts (§5.2).

## 4. Search: the equal search of A1/A6

- One search per (material, arm configuration, τ).
- The search is `run_engineering.bisect_scale`, unchanged: 60 bisection iterations in log space, stopping when the
  log-interval falls below 1e-9. It bisects over the configuration's single tolerance parameter. The predicate is
  "the decoded certificate passes at τ", as in A6.
- Reported point: the highest-CR evaluated point that passes the decoded certificate (the A6 rule). Ties go to the
  larger tolerance.
- Intervals:

  | arm | interval | reason |
  |---|---|---|
  | M | [1e-14, 1e3] × ptp(ρ) | A1's interval; MGARD's s-norm tolerance is not bounded by ptp |
  | Q | [1e-14, 1] × ptp(ρ) | A6's interval; QPET's tolerance is a block-average error in density units |

- Execution errors: a codec process that exits non-zero, writes no stream, decodes to the wrong size or to non-finite
  values, or exceeds 1800 s, gives a non-passing point. The error is recorded in `failures_*.csv`.
  - If such an error occurs at the lower bound, the lower bound is raised by one decade at a time. This continues
    until the codec executes, up to 1e-2 × ptp. Each raised decade is recorded (`lo_decades_skipped`).
  - The lower bound is never raised after a certificate failure.
  - If the codec never executes, the search reports nothing and records `lo_decades_skipped = −1`.
- The codecs are deterministic, so evaluations are cached per (material, configuration) across τ: an identical
  tolerance gives an identical stream.

## 5. Arms

### 5.1 M: MGARD

- Build exactly as in `.github/workflows/qoac_h_strong_baselines.yml`: upstream `github.com/CODARcode/MGARD`,
  `-DMGARD_ENABLE_CLI=ON -DMGARD_ENABLE_OPENMP=ON`, Release, OpenMPI, TCLAP 1.4 headers (`mirror/tclap` branch 1.4).
- MGARD is pinned at `ac53ff9cec8cf2dee08892f0400ae0ddb755b193`. This is the default-branch HEAD on 2026-10-07 and
  the commit of the SI Note 2.4 study. The commit actually built is recorded.
- Invocation: `run_baselines.mgard_roundtrip`, reused verbatim:
  - `mgard compress --datatype double --shape n0xn1xn2 --smoothness s --tolerance τ_M`;
  - `mgard decompress`.
- MGARD is non-periodic. No padding is applied, as in SI Note 2.4.
- The single parameter is MGARD's absolute tolerance τ_M in the s-norm. MGARD-QOI's operator-norm rescaling
  (τ/R_s) is a constant factor on τ_M, so the search absorbs it.
- **M2** = s = −2.
- **M-best** = the highest certified CR over s ∈ {∞, 0, −1, −2}. Each s has its own equal search.
- **Feasibility of M2** (probe, §8): the SI Note 2.4 tiny-array probe (16³ standard normal, seed 0, tolerance 0.01)
  is extended to s = −2.
  - M2 is feasible iff compression and decompression both return 0 and the decoded array has the right size and is
    finite.
  - If not, the CLI's output is recorded verbatim, M2 is reported as infeasible, and M-best is taken over
    s ∈ {∞, 0, −1}.

### 5.2 Q: QPET

**Source.** The authors' public artifact `https://github.com/JLiu-1/QPET-Artifact`. Its main branch README says the
code is in the other branches, frozen at submission and revision. The revision branches are used, at these commits:

| branch | commit | contents |
|---|---|---|
| `szfamily_qpet_revision` | `5d17cb1647caf001bd7355c617856c72c4b6475e` | SZ3-QPET and HPEZ-QPET; CLI `hpez` |
| `sperr_qpet_revision` | `1874108fe7a38b5eb0c63874889af0a16a248ad4` | SPERR-QPET; CLI `sperr3d` |

The required dependency SymEngine is built at tag `v0.14.0` (GMP integer class).

**Supported QoIs, established from the source and the paper before any run.** QPET preserves QoIs that are local
in the data:

- pointwise univariate f(x), given as a symbolic expression (`qoi = 14`), plus piecewise (`15`) and |·|-type (`17`)
  forms;
- multivariate QoIs over co-located variables (the `*_vec` branches, cross-snapshot);
- regional QoIs (`qoiRegionMode` in `include/QoZ/api/impl/SZInterp.hpp`):
  - 1 = average of f(x) over b³ blocks,
  - 2 = difference Laplacian,
  - 3 = gradient length.

The paper (§5) lists univariate, multivariate and regional (block-average) QoIs; its blocked-QoI evaluation uses
b = 4. QPET has no global or nonlocal functional such as a Poisson solve, so it cannot express V_H directly.

**Configuration.** Of the supported QoIs, only the regional average is a linear low-pass functional. The Laplacian
and the gradient weight |G|² and |G|, opposite to the Hartree |G|^-2. The declared configurations are:

- QoI: regional average of f(x) = x over b³ cubes aligned at index 0, with b ∈ {4, 8, 16}.
- QoI bound: absolute, value t. This is the single searched parameter.
- Base pointwise bound: absolute, equal to ptp(ρ). It never binds, so the QoI bound alone drives the codec.
- All other parameters are the authors' defaults. QPET sets confidence, the std-rate and the pointwise rate itself.
- Hosts (the three into which the paper integrates QPET):
  - **SZ3-QPET**: `hpez -q 0 -f -i in -z stream -3 n2 n1 n0 -M ABS ptp -c cfg -m ABS -e t`, then
    `hpez -f -z stream -o out -3 n2 n1 n0`.
  - **HPEZ-QPET**: as SZ3-QPET with `-q 3`, the authors' recommended default level.
  - In both, `cfg` = `[QoISettings] qoi = 14, qoi_string = x, qoiRegionMode = 1, qoiRegionSize = b`.
  - The `-m ABS -e t` form is used because the CLI's `-m <mode> <value>` form does not read its value
    (`test/hpez.cpp`, case `'m'`).
  - **SPERR-QPET**: `sperr3d -c in --ftype 64 --dims n2 n1 n0 --bitstream stream --pwe ptp --qoi_id 14 --qoi_string x
    --qoi_bs b --qoi_tol t`, then `sperr3d -d stream --decomp_d out`.
- This gives 9 configurations (3 hosts × 3 block sizes). **Q** = the highest certified CR over the 9 configurations,
  each with its own equal search, by analogy with A6.
- Per-host and per-block results are reported descriptively.

**Precision.** The authors' `hpez` CLI compiles only its float32 path; the double branch is commented out in
`test/hpez.cpp`. The SZ3 and HPEZ hosts therefore receive ρ cast to float32. Their decoded float32 field is cast to
float64 and certified against the original float64 ρ. SPERR-QPET runs on float64. The authors' code is not
modified.

**Feasibility** (probe, §8): every configuration is round-tripped at t = 1e-3 × ptp on a non-cubic smooth synthetic
array (48 × 56 × 72). The probe records:

- whether the roundtrip succeeds;
- the stream size;
- the pointwise L∞ error / t;
- the maximum block-average error / t, computed in numpy on the C-order axes. This checks the axis order and that
  the regional QoI is active.

A configuration that cannot be built or round-tripped is reported as infeasible with the evidence. Q is infeasible
as a whole only if no configuration is feasible. No other compressor is ever run under the QPET name.

## 6. Comparison arms (recorded, not rerun)

A1 (closed-form law), A2 (spectral truncation), A3 (operational optimum) and A6 (best of ZFP/SZ3/SPERR) are read from
`analysis/general_qoac_law/results/run_{P1,P3B}_CONFIRMATORY/part_a_material.csv`, restricted to the manifest ids.
The SHA-256 of these files is in §10.

## 7. Statistics (per cohort and τ; reported at 1e-6, then 1e-4 and 1e-8)

- **Median certified CR** of each arm (A1, A2, A3, A6, M2, M-best, Q), over the materials where that arm certified,
  with that n. The per-s MGARD medians and the per-host and per-configuration QPET medians are reported alongside.
- **Per-material ratios**: A1/M2, A1/M-best, A1/Q, A3/M2 and A3/Q.
  - **Wins**: ratio > 1.
  - **Median** with a percentile bootstrap 95% CI. The bootstrap is `aggregate_law.boot`, reused unchanged: 10,000
    resamples over materials, with `numpy.random.default_rng(20261006)` created fresh for each statistic.
- **Baseline never certified.** The numerator arm certified, and the baseline's search ran without finding a
  passing point. These cases are counted separately as `baseline_never_certified` and are added to the wins
  (`wins_incl_never_certified`).
  - Following `aggregate_law.py`, where an undefined ratio is dropped (`.dropna()`), such materials do **not** enter
    the median or its CI. The median is over the materials where both arms certified, and that n is reported.
  - A material whose search did not run (a material-level failure) is counted as `baseline_not_run`. It is not a win.
  - For M-best and Q, "never certified" means that no configuration of the arm certified.
- **Failures per arm**: failed evaluations (execution errors) and the materials affected, material-level failures,
  searches whose lower bound was raised, and searches in which the codec never executed.
- **Wall time per arm**: per-material search time summed over the arm's configurations (median and total), and the
  total codec + certificate time.
- There is no pass/fail gate. Outcomes are reported without interpretation.

## 8. Execution (GitHub Actions only)

Workflow: `.github/workflows/hartree_baselines_mgard_qpet.yml`. It fires on pushes to this branch that change the
sentinel `analysis/hartree_baselines_mgard_qpet_20261007/PHASE`.

- **Preflight**:
  - runs the unit tests (`test_mq.py`, `test_codec_qoac_v03.py`);
  - checks the input SHA-256 table (§10) and refuses to continue on a mismatch;
  - builds the matrix.
- **Toolchain**:
  - builds MGARD, SymEngine and both QPET branches from upstream source at the pinned commits;
  - runs `probe_toolchain.py` on tiny synthetic arrays;
  - uploads the toolchain and the probe record.
- **Shard**: one job per material (max-parallel 20, timeout 360 min).
  - Four worker processes, `OMP_NUM_THREADS=1`.
  - Runs the 13 configurations (4 MGARD s values and 9 QPET configurations) through `run_mq.py`.
  - Uses the frozen Python stack: commit `893f931`, `validation/requirements-external-e2e.txt`, Python 3.12.14.
- **Aggregate**: runs `aggregate_mq.py` and commits `analysis/hartree_baselines_mgard_qpet_20261007/results/`.

The phases run in this order:

1. `PHASE=probe`: toolchain, probes, and the shakedown material. No cohort material is touched.
2. `PHASE=run`: the 92 cohort materials.

Between the phases, and after the run has started, only infrastructure may change: build flags, runtime libraries,
paths and timeouts. Each such change is recorded in `DEVIATIONS.md` before any rerun.

No arm, configuration, block size, interval, certificate, τ, statistic or population may change after this freeze.
Every failure is kept as a counted result.

## 9. Report format (`RESULTS.md`)

Numbers first, per cohort, at τ = 1e-6 and then 1e-4 and 1e-8:

1. median CR per arm, with n;
2. A1/arm and A3/arm medians, with CI, wins and never-certified counts;
3. the M2 and Q feasibility facts (probe record, build log tails);
4. run ids, commits and file paths;
5. failures and wall time.

## 10. Input SHA-256 (LF bytes as committed; verified in CI preflight)

| file | SHA-256 |
|---|---|
| `analysis/fresh_population_20261006/P1_CONFIRMATORY_MANIFEST.csv` | `3297d6c17959c7a70bf157f7157283f45ddb046fdc460acaa8a8570ab4de7331` |
| `analysis/fresh_population_20261006/P3B_CONFIRMATORY_MANIFEST.csv` | `e7c447d5f8dc3b263c7b5b4b9d1f8344ad9c8ed41e5b72fa333c37ad14b70f97` |
| `analysis/fresh_population_20261006/P1_ENGINEERING_MANIFEST.csv` | `480bc38667544eb4023276ad9def91eff451b4f1dbccb7cde76fb707b66fd6a9` |
| `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_material.csv` | `5760ae206af28c4d916088ce4ab8061053975934ea38f58904e34aa12bfb715e` |
| `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_rows.csv` | `3ebb5c0d7221b1186a1d16030c96100b7b34fd19a5079586cf33511feb433b60` |
| `analysis/general_qoac_law/results/run_P3B_CONFIRMATORY/part_a_material.csv` | `cee4ec409461573f79716ef34279b6bab38416b9054b21620facb0837ecad2f1` |
| `analysis/general_qoac_law/results/run_P3B_CONFIRMATORY/part_a_rows.csv` | `45553d6d973fad3b87ee0fb41549c2a838472fba439b8c65f072ae4fed74575a` |
| `analysis/general_qoac_law/run_part_a.py` | `fbfd13febf5911ae342f407cf4b3e946a86bd6e20e386de1bbfbdf15beb7f2af` |
| `analysis/general_qoac_law/aggregate_law.py` | `18304421790504c62af5d3a69d779821aade014d037f866f71f6ee4588703ada` |
| `analysis/qoac_v03_rdo/run_engineering.py` | `6cbdf8e31b4749cebb65a78582a8bec3032baf89073524b9c21065b65a7f3123` |
| `analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py` | `f78dd40aba7f2a25727d4df08d621f3456244bfb14f404423551900c3504ce1a` |
| `analysis/qoac_h_strong_baselines/run_baselines.py` | `ad09c4a53c2f44ea47669e941e123669ddf5fbeb5a53c4a35b799596d3d2a8c6` |
| `validation/qsq_prospective/development_compatibility_smoke.py` | `d51a31d7838d09175292e5024e7f969347c4de2e011446f6de863f2f3c0683bf` |

The two cohort manifests and both `part_a_material.csv` files are byte-identical (same git blob) to those on
`research/general-qoac-law-confirm-20261006`. Their blobs are:

- P1 manifest: `ef4f22c`;
- P3b manifest: `8cc63db`;
- P1 `part_a_material.csv`: `5f80aae`;
- P3b `part_a_material.csv`: `e4b4bfe`.

The upstream sources are pinned in §5:

- MGARD `ac53ff9`;
- TCLAP branch 1.4 (`61cfae1` in SI Note 2.4; the built commit is recorded);
- SymEngine `v0.14.0`;
- QPET `5d17cb1` and `1874108`.
