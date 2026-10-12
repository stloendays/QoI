# Deployment cost of certified Hartree compression — protocol (frozen 2026-10-12, before any cohort run)

## Question

Fig. 5 reports certified compression ratios. A deployment also pays for encoding, for the certified search,
for decoding, for working memory and for moving the bytes. This study measures those costs for the arms of Fig. 5
on the same materials, at the same certified operating points, under one harness.

## Materials and operating points

- Cohorts: P1 (60 fresh Materials Project bulk crystals) and P3b (32 fresh NOMAD slabs), manifests
  `analysis/fresh_population_20261006/P1_CONFIRMATORY_MANIFEST.csv` and `P3B_CONFIRMATORY_MANIFEST.csv`.
- Tolerances: Hartree relative error τ ∈ {1e-4, 1e-6, 1e-8}; **primary τ = 1e-6**.
- Operating points are not re-optimized. Each arm is regenerated from the parameter recorded in the committed runs:
  - A1, the closed-form law: `alpha_rel` from `analysis/general_qoac_law/results/run_*/part_a_rows.csv`.
  - A3, the operational optimum: `margin` from the same file.
  - A6, the best of ZFP, SZ3 and SPERR: codec and `abs_tol_rel` from the same file.
  - M2, MGARD with s = −2, and Q, the best of the nine QPET configurations: `tol_rel` and configuration from
    `analysis/hartree_baselines_mgard_qpet_20261007/results/run_*/rows.csv`.
- Lossless references: float64 + zlib level 6, float64 + zstd level 3, and the source file as archived
  (MP `json.gz`; NOMAD CHGCAR, compressed as served).

## Implementations

- A1 and A3 are timed with the production implementation `fast_codec.py`, which writes and reads the unchanged
  stream formats: the Hermitian-orbit table is built in one compiled pass (numba 0.65.1, on-disk JIT cache; the
  warm-up call absorbs loading), sorted by shell with a counting sort, and the decoder inverts the half spectrum
  with `irfftn`. The orbit table is bit-identical to the reference, A1 streams are byte-identical, and decoded
  fields agree with the reference decoder to rounding (`test_fast_codec.py`, numba and numpy paths). The reference
  implementation of the committed runs is timed alongside as `A1ref` and `A3ref`.
- ZFP (zfpy 1.0.1), SZ3 (pysz 1.0.3) and SPERR (hdf5plugin 7.0.0, HDF5 file, single chunk) use the calls of the
  frozen benchmark.
- MGARD (commit ac53ff9) and QPET (authors' artifact, commits 5d17cb1 and 1874108) are the command-line programs of
  the committed baseline run, built from source in the workflow. Their encode time includes writing the raw input
  file the program reads, and their decode time includes reading the raw output file it writes; the program-only
  times are reported alongside.

## Measurements

Each operation runs in a fresh Python process, single-threaded (`OMP_NUM_THREADS` and related variables set to 1;
MGARD's OpenMP build also runs single-threaded). One material is measured end to end on one runner, so every
paired ratio compares arms on the same machine.

1. **Encode**: from the float64 field in memory to the stream at the recorded parameter. One warm-up, then five
   timed repetitions; the median is reported.
2. **Decode**: from the stream to the float64 field. Same repetitions. Every decoded field is re-certified with the
   decoded Hartree certificate; the certificate is not part of the timing.
3. **Certified search** (τ = 1e-6): the arm's complete certified compression from the raw field, as in the committed
   runs: A1, law-step bisection with exact spectral distortion, one encode, decoded certificate; A3, shell
   rate–distortion analysis, Lagrangian selection, encode, decoded certificate; A6, tolerance bisection with a
   decoded certificate at every point for each of ZFP, SZ3 and SPERR (the arm's cost is the sum over the three);
   M2, the same bisection for MGARD s = −2; Q, the same bisection for each of the nine QPET configurations (the
   arm's cost is the sum over the nine). The search must return the recorded parameter; any difference is reported.
4. **Peak memory**: the high-water resident set of the operation's process above its resident set after the input
   is loaded and the codec libraries are imported, reported as a multiple of the raw field size (8N bytes). For the
   command-line codecs, the peak resident set of the codec process itself.
5. **Retrieval cost**: time to a usable float64 field from storage at link bandwidth B,
   T(B) = 8·bytes / B + decode time, for B = 0.1, 1 and 10 Gbit/s. For the source file, the decode time is the
   measured time of the project loader from the source bytes to the float64 array. Bytes moved per material and per
   cohort are reported with it.
6. **Runner calibration**: CPU model and a fixed FFT / zlib / memory-copy micro-benchmark per runner.

## Endpoints (all descriptive; none gates a manuscript claim)

At τ = 1e-6, per cohort, with medians and paired-bootstrap 95% intervals (10,000 resamples, seed 20261012):

- E1 decode time and decode throughput (raw field MB per second) of A1; paired ratio of decode time A6/A1, Q/A1,
  M2/A1, A3/A1.
- E2 encode time of each arm; paired ratios against A1.
- E3 certified-search time of each arm; paired ratios against A1.
- E4 peak memory of encode and decode as a multiple of the raw field size.
- E5 time to field T(B) for B = 0.1, 1, 10 Gbit/s; paired ratios of each arm, of the lossless references and of
  the source file against A1; number of materials for which A1 is fastest to a usable field; and the break-even
  bandwidth B* = 8·(bytes_arm − bytes_A1) / (decode_A1 − decode_arm), below which A1 delivers the field first
  (infinite when A1 is both smaller and faster to decode).

The same quantities are reported at τ = 1e-4 and 1e-8 for encode, decode, memory and retrieval.

## Reproduction checks

Every regenerated stream is decoded and must be certified at its τ. Regenerated bytes are compared with the
recorded bytes (A1 parameters are recorded to nine significant digits, so A1 may differ by a few bytes). Every
deviation is listed in `results/RESULTS.md`.

## Execution

GitHub Actions, `ubuntu-24.04` hosted runners, one material per job (`.github/workflows/deployment_cost.yml`).
Raw outputs: `results/shards/`; aggregation: `aggregate_cost.py` → `results/per_operation.csv`,
`results/SUMMARY.json`, `results/RESULTS.md`.
