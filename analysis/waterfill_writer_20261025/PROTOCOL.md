# Water-filling law and the W1 writer on the law-protocol cohort — protocol

Fixed 2026-10-25, before any material of the cohort is run with this code. Branch `research/algo-upgrade-20261025`,
created from revision 10 (`0d74c39`). Plan: `paper/nc_reopen/ALGORITHM_UPGRADE_PLAN_20261025.md`. Nothing under
`paper/` (other than the plan) or `figures/` changes in this study. Execution on the NUS Vanda cluster (author
instruction, 2026-10-23: 「之后都用服务器来算」).

## 1. Questions

Under the Hartree contract (historical and Nyquist-safe relative RMS error of the Hartree potential < tau_H, decoded
certificate):

- **Q1 (allocation).** With the same container and entropy coder, does the closed-form water-filling law (one scalar,
  no per-shell search) store a material within a few percent of the operational optimum (per-shell Lagrangian search on
  the writer's exact curves), at the tight and the loose tolerance alike, and does it beat spectral truncation?
- **Q2 (writer).** By how much does the upgraded writer (water-filling law, binary container, adaptive arithmetic
  coding, symmetry-predictive coding) reduce the bytes of the revision-10 arms: the law A1, truncation A2, the
  operational allocation A3 and the best pointwise codec A6?
- **Q3 (attribution).** Which component produces the gain: container and coder (L1 vs A1), water-filling (W1 vs L1),
  symmetry (W1S vs W1)?

## 2. Cohort and loading

The 92 law-protocol materials: 60 P1 bulk (`analysis/fresh_population_20261006/P1_CONFIRMATORY_MANIFEST.csv`) and 32
P3b slabs (`P3B_CONFIRMATORY_MANIFEST.csv`), loaded with `development_compatibility_smoke.build_grid` from the
validation tree at `893f931` (as the law, XC and linearized-XC studies). Sources are downloaded on the login node; size
and SHA-256 must equal the manifest. Development exposure before this protocol: the P1 engineering materials
mp-3148759, mp-2521964, mp-1870388 and mp-2348544 only (plan §2); none is in the cohort.

## 3. Writer W1 (`w1.py`, `qac.py`, `symmetry.py`)

- Topology: the v0.2 Hermitian-orbit topology with 32 radial shells and the conservative Nyquist metric; G = 0 exact.
- Allocations: `law` (Delta_k = alpha q_k^2), `wf` (the law; shell s written iff E_s > alpha^2 H_s with
  E_s its operator-weighted energy and H_s = sum m_k p_k / 12 its operator-weighted high-rate noise; kappa = 1),
  `trunc` (uniform alpha below q_c), `rdo` (v0.3 ladder multipliers per shell, v0.3 Lagrangian selection and polish on
  this writer's exact per-shell curves; distortion floor from tau = 1e-8 as v0.3).
- Quantization: rounding to the nearest integer multiple of the step.
- Symmetry: space-group operations from spglib (pymatgen `SpacegroupAnalyzer`, symprec 1e-3) on the structure, kept if
  they map the grid onto itself and hold on the density to 1e-5 of its range in real space; their closure must hold as
  well, otherwise no symmetry is used. Within each shell, the first member of a star is coded and every other member is
  coded as the quantized residual from its predicted value at its own step. The stream stores a greedy generating set.
- Entropy coding: one segment per shell, the smaller of the adaptive binary arithmetic coder (`qac.py`) and zlib level
  6 on interleaved smallest-width integers; binary header (shape, lattice, DC, allocation parameters, generators,
  32 varint shell fields).
- Every reported stream is decoded by `w1.decode` from its bytes alone and certified on the decoded field with
  `codec_qoac_h_v02.hartree_error_metrics` (the law protocol's certificate).

## 4. Arms and searches

| arm | allocation | symmetry | search (as the law protocol's arm) |
|---|---|---|---|
| L1 | law | no | A1: 60-step log bisection of alpha on the exact spectral distortion (margin 0.995), then decode and certify, alpha × 0.99 until certified (≤ 40) |
| W1 | water-filling | no | as L1 |
| W1S | water-filling | yes | as L1 |
| T1S | truncation | yes | A2: every q_c = k/32, bisection of a uniform step, the three smallest candidates decoded and certified |
| O1 | operational | no | A3: Lagrangian + polish at margin 0.995, × 0.995 until certified (≤ 20) |
| O1S | operational | yes | as O1 |

Recorded comparison arms (law protocol, `analysis/general_qoac_law/results/run_{P1,P3B}_CONFIRMATORY/part_a_rows.csv`,
smallest certified stream per arm): A1, A2, A3, A6. Tolerances tau_H = 1e-6 (primary), 1e-4 (co-primary for Q1),
1e-8 (descriptive). CR = 8 × npoints / stream bytes, headers included.

## 5. Criteria

Medians over materials of per-material CR ratios; 95% intervals from a fixed-seed bootstrap of the median
(`numpy.random.default_rng(20261025)`, 10,000 resamples), over the 92 materials and per cohort.

- **H1 closed form at the optimum.** Median CR_O1S / CR_W1S <= 1.05 with interval upper bound <= 1.08, at 1e-6 and at
  1e-4.
- **H2 water-filling over truncation.** CR_W1S > CR_T1S in >= 90% of materials at 1e-6 and at 1e-4.
- **H3 the writer over the revision-10 operational allocation.** Median CR_W1S / CR_A3 > 1.3 with interval lower bound
  > 1.2 at 1e-6.
- **Validity.** >= 90 of 92 materials analyzable; every W1-family arm certified on every analyzable material at 1e-6
  and 1e-4.

Descriptive: CR_W1S / CR_A1, / CR_A2, / CR_A6; the attribution ladder L1/A1, W1/L1, W1S/W1, O1/W1; the same by cohort
and by the number of symmetry operations; 1e-8; shells written; encode/decode seconds. Each criterion is reported as met
or not met, with its number; a failed criterion is reported as such and stays in RESULTS.md.

## 6. Execution

- Vanda, project CFP04-CF-046, route queue `auto`; staging `/scratch/junbotong/qoi-algo-20261025/`; scripts
  `analysis/server_runs_20261025b/vanda/`; inputs prefetched on the login node; compute nodes read staged files only.
- `probe.pbs`: the test suite (`test_w1.py`), one development material end to end with the bytes of the local
  development run (`results/DEV_KNOWN_ANSWER.json`, within max(3 bytes, 0.5%)), and the two smallest cohort materials;
  their checkpoints count in the run.
- Production after a passing probe: one single-threaded worker per material, checkpoints per material, resumable.
- After the protocol is fixed, only infrastructure may change (modules, paths, resources, timeouts), each recorded in
  `DEVIATIONS.md` before any rerun.
- Results are copied back with SHA-256 verification, aggregated by `aggregate_w1.py` into `results/` and committed;
  the staging directory is then removed (Vanda cleanup rule).
