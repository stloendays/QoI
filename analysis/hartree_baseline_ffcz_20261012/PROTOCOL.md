# Hartree-contract baseline FFCz (frequency-domain correction), prospective cohorts P1 and P3b — frozen protocol

Freeze date: 2026-10-12. This protocol is committed and pushed before FFCz is evaluated on any P1 or P3b material.
It is a descriptive strongest-baseline record with no pass/fail gate, an extension of
`analysis/hartree_baselines_mgard_qpet_20261007/PROTOCOL.md` (protocol `16e8890`, called **BP** below). Where this
file is silent, BP applies unchanged.

Branch: `research/hartree-baseline-ffcz-20261012`, created from `paper/nc-rev4-20261012` at `16ca09e`. Nothing
under `paper/` or `figures/` changes. Execution is on the NUS Vanda cluster (author instruction "用超算做吧",
2026-10-12), not GitHub Actions.

## 1. Question

FFCz (Ren et al., arXiv:2601.01596, 2026; manuscript ref. 16) corrects the decoded output of an error-bounded
compressor in the Fourier domain until it meets a frequency-domain error bound, while keeping a spatial bound. It is
the published method closest to reciprocal-space error control. This study runs FFCz under the same Hartree contract
and equal search as A1/A6, M and Q, on the same 92 materials.

## 2. Population, contract, certificate and τ

As BP §2 and §3: P1 (60) and P3b (32) confirmatory manifests, the same loader, the decoded historical **and**
Nyquist-safe Hartree certificate, τ ∈ {1e-4, 1e-6, 1e-8}, primary τ = 1e-6. CR = 8N / total stored bytes (§4).
Shakedown (probe phase only): `mp-3148759` from `P1_ENGINEERING_MANIFEST.csv`; its results enter no statistic.

## 3. FFCz source and build

- Authors' repository `https://github.com/rcrcarissa/FFCz`, commit `96649b36b2a155075682d86fbabeb925e7d9e29a`
  (main, 2026-06-13). The CPU build (`CPU/`, executable `ffcz_cpu`) is used, as the README describes, with
  CMake 3.29.3, GCC 13.3.0, FFTW 3.3.10 and zstd 1.5.6 (Vanda modules of the GCCcore-13.3.0 family). The authors'
  code is not modified. The built commit, module list and binary SHA-256 are recorded.
- Defaults of the authors' `main.cpp` are kept: `max_iterations = 100`, convergence tolerance `1e-6`.
- Double precision (`-d`) throughout: the original and the base-decoded fields are float64.

## 4. Arm F and its configurations

A configuration is (base codec b, base tolerance ε_b, frequency-bound mode m):

- **b** ∈ {ZFP, SZ3, SPERR}, run through the same frozen codec path as A6 (`run_engineering`, i.e. the frozen
  `validation/external_end_to_end.py` round trip at `893f931`), at absolute tolerance ε_b.
- **ε_b / ptp(ρ)** ∈ {1e-2, 1e-3, 1e-4}.
- **m** ∈ {REL, PTW}:
  - REL: `-F REL r`, the authors' frequency bound |ΔF(k)| ≤ r · max_k |F(k)| for every frequency k;
  - PTW: `-F PTW r`, the authors' pointwise relative frequency bound |ΔF(k)| ≤ r · |F(k)|.
- Spatial bound passed to FFCz: `-M ABS ε_b`, the base codec's own bound, so the base's spatial guarantee is kept.

This gives 18 configurations. **F** = the highest certified CR over the 18 configurations, each with its own equal
search, by analogy with A6 and Q. Per-base, per-ε_b and per-mode results are reported descriptively.

**Encoding and decoding of one evaluated point (b, ε_b, m, r):**
1. Base stream: compress ρ with b at ε_b; decode it in a separate process to the base field ρ_b (float64 raw file).
   Cached per (material, b, ε_b), because the base does not depend on r or τ.
2. Correction: `ffcz_cpu -d -i ρ.raw -e ρ_b.raw -z edits.ffcz -M ABS ε_b -F m r -3 Nx Ny Nz`, with the grid axes in
   the order the authors' reader expects for a C-order array (checked by the probe, §7).
3. Decoding: a separate process runs `ffcz_cpu -d -e ρ_b.raw -z edits.ffcz -o ρ_dec.raw -M ABS ε_b -F m r -3 …`; the
   decoded ρ_dec is certified. Nothing else is passed to the decoder.
4. Stored bytes = base stream bytes + size of `edits.ffcz`. CR = 8N / stored bytes.

## 5. Search

As BP §4: `run_engineering.bisect_scale`, 60 log-space iterations, predicate "the decoded certificate passes at τ",
reported point = highest-CR passing point (ties to the larger r). The searched parameter is r:

| mode | interval for r | reason |
|---|---|---|
| REL | [1e-14, 1] | r = 1 bounds no frequency below the spectral maximum |
| PTW | [1e-14, 10] | r = 10 leaves every frequency effectively unconstrained |

Execution errors (non-zero exit, no output, wrong size, non-finite values, more than 1800 s) give a non-passing point
and are recorded in `failures_*.csv`, with BP's lower-bound rule. FFCz is deterministic, so evaluations are cached
per (material, configuration) across τ.

## 6. Comparison arms (recorded, not rerun)

A1, A2, A3 and A6 from `analysis/general_qoac_law/results/run_{P1,P3B}_CONFIRMATORY/part_a_material.csv`; M2,
M-best and Q from `analysis/hartree_baselines_mgard_qpet_20261007/results/run_{P1,P3B}_CONFIRMATORY/material.csv`
(SHA-256 in §9).

## 7. Probe phase (no cohort material)

- Build log, `ffcz_cpu` usage text, binary SHA-256.
- Round trip on a non-cubic smooth synthetic float64 array (48 × 56 × 72) for every (mode, r ∈ {1e-2, 1e-4}) on a
  SZ3 base at ε_b = 1e-3 · ptp. Recorded: success, edits bytes, spatial L∞ / ε_b, and the frequency-bound check
  computed in numpy (`numpy.fft.fftn` on the C-order array): max_k |ΔF(k)| / (r · max|F|) for REL and
  max_k |ΔF(k)| / (r |F(k)|) over |F(k)| > 0 for PTW. A ratio ≤ 1 + 1e-6 confirms the axis order and the bound
  semantics; any other value is reported with the evidence before the run phase.
- The shakedown material through the full pipeline.

## 8. Statistics and report

As BP §7, with arm F added: median certified CR of F per cohort and τ, with n; per-material A1/F and A3/F medians
with bootstrap 95% CI (`aggregate_law.boot`, 10,000 resamples, `default_rng(20261012)`), wins,
`baseline_never_certified`, failures and wall time. Also F/A6 and F/Q medians (descriptive). `RESULTS.md`: numbers
first, per cohort, τ = 1e-6 then 1e-4 and 1e-8.

## 9. Execution on Vanda and inputs

- Project `CFP04-CF-046`, route queue `auto`; scratch staging under `/scratch/junbotong/qoi-ffcz-20261012/`. Inputs are
  prefetched on the login node with `fetch_exact` (SHA-256 and byte count against the manifest); compute nodes read
  only staged files. A PBS array runs one (material, configuration) search set per task with `OMP_NUM_THREADS=1`.
- Phases: `probe` (§7), then `run` (92 materials). Between and after, only infrastructure may change (build flags,
  modules, paths, timeouts, PBS resources), each recorded in `DEVIATIONS.md` before any rerun. No configuration,
  interval, certificate, τ, statistic or population changes after this freeze; every failure is a counted result.
- Results are copied back, verified by SHA-256 against the server, committed under `results/`, and the staging
  directory is then deleted (Vanda cleanup rule).

| file | SHA-256 (committed bytes) |
|---|---|
| `analysis/fresh_population_20261006/P1_CONFIRMATORY_MANIFEST.csv` | `3297d6c17959c7a70bf157f7157283f45ddb046fdc460acaa8a8570ab4de7331` |
| `analysis/fresh_population_20261006/P3B_CONFIRMATORY_MANIFEST.csv` | `e7c447d5f8dc3b263c7b5b4b9d1f8344ad9c8ed41e5b72fa333c37ad14b70f97` |
| `analysis/fresh_population_20261006/P1_ENGINEERING_MANIFEST.csv` | `480bc38667544eb4023276ad9def91eff451b4f1dbccb7cde76fb707b66fd6a9` |
| `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_material.csv` | `5760ae206af28c4d916088ce4ab8061053975934ea38f58904e34aa12bfb715e` |
| `analysis/general_qoac_law/results/run_P3B_CONFIRMATORY/part_a_material.csv` | `cee4ec409461573f79716ef34279b6bab38416b9054b21620facb0837ecad2f1` |
| `analysis/hartree_baselines_mgard_qpet_20261007/results/run_P1_CONFIRMATORY/material.csv` | `ff5e1a030ca5a53720f2e8214821638ef1081ec1e970dd2a2d294ed618e2fea5` |
| `analysis/hartree_baselines_mgard_qpet_20261007/results/run_P3B_CONFIRMATORY/material.csv` | `f8ac369450119243e30bb27b8bde4eb6b8586a113394bb802181012fc01b15ba` |
| `analysis/hartree_baselines_mgard_qpet_20261007/run_mq.py` | `ff14686adfe584073705fd7f82f92b4623c49082d2b2c989b2dbdbb2f8d03467` |
| `analysis/qoac_v03_rdo/run_engineering.py` | `6cbdf8e31b4749cebb65a78582a8bec3032baf89073524b9c21065b65a7f3123` |
| `analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py` | `f78dd40aba7f2a25727d4df08d621f3456244bfb14f404423551900c3504ce1a` |
| `validation/qsq_prospective/development_compatibility_smoke.py` | `d51a31d7838d09175292e5024e7f969347c4de2e011446f6de863f2f3c0683bf` |
