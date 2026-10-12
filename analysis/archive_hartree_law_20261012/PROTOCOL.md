# The closed-form operator law on the Materials Project charge-density archive (Hartree contract) — frozen protocol

Freeze date: 2026-10-12. This protocol is committed and pushed before any writer of this item is evaluated on any
object of the WP-F sample. Branch `research/archive-hartree-law-20261012`, created from `paper/nc-rev4-20261012` at
`16ca09e`. Nothing under `paper/` or `figures/` changes. Execution is on the NUS Vanda cluster (author instruction
"用hpc算吧", 2026-10-12).

## 1. Question

WP-F (`analysis/extensions_20260930/PROTOCOL.md`, section WP-F, frozen `cb6438c`) estimated how much a QSQ-gated,
Bader-certified ZFP/SZ3/SPERR writer shrinks the public Materials Project charge-density archive. This item asks the
same question for the manuscript's linear-operator result: on the **same frame, sample, storage rule and
estimators**, how much does a QSQ-gated, **Hartree-certified** archive shrink when its writer is the closed-form
operator law (A1), and how much when it is the best pointwise codec (A6)?

## 2. Frame, sample and per-object loading (unchanged from WP-F)

- Frame and strata: `analysis/extensions_20260930/WP-F/frame.csv.gz`, `strata.csv` (415,289 objects, 8.4976 TB after
  removing the development set).
- Sample: the 300 objects of `analysis/extensions_20260930/WP-F/sample.csv` (SHA-256 in §8), all of them, including
  the 7 that failed in WP-F. Each object is downloaded exactly; bytes and SHA-256 are recorded and the size must match
  the frame.
- Loading: the WP-F loader of `run_wpf.py` (frozen MP loader), the same `field` array (total charge density in CHGCAR
  units, float64), `lattice`, `npoints`, `json_bytes`, `raw64_bytes` (8 × npoints) and `lossless_bytes` (zlib level 6
  on the float64 array in stored order).

## 3. Contract, qualification and certificate

- **Contract:** the Hartree potential of the stored density, certified by the decoded certificate of the law
  protocol (`analysis/general_qoac_law/DESIGN.md`, arms A1/A6): historical **and** Nyquist-safe Hartree relative RMS
  error both < τ_H, computed by `codec_qoac_h_v02.hartree_error_metrics` exactly as `run_engineering.certify` does.
- **τ_H** ∈ {1e-4, 1e-6, 1e-8}; primary τ_H = 1e-6.
- **QSQ for this contract:** ε = ‖float32(field) − field‖_∞ and the five probes of WP-F, noise
  `Generator(PCG64(s)).uniform(-ε, ε, size=field.shape)` for s ∈ (20260905, 1, 2, 3, 4). The response of probe k is
  max(historical, Nyquist-safe) Hartree relative RMS error of (field + noise_k) against field. Floor f = max_k response;
  eligible at τ_H iff f < τ_H.

## 4. Writers

Both writers use the law protocol's code path unchanged (`analysis/qoac_v03_rdo/run_engineering.py`, as called by
`analysis/general_qoac_law/run_part_a.py`), with the same equal search: continuous bisection, 60 iterations in log
space, decoded certificate as predicate, highest-CR passing point reported. Stream bytes are counted as in the law run.

- **L (law):** arm A1, the closed-form law ΔG ∝ |G|² with continuous α bisection.
- **P (pointwise):** arm A6, the best of ZFP, SZ3 and SPERR by absolute-tolerance bisection.

A writer whose search finds no passing point at τ_H leaves the object uncertified for that writer.

## 5. Storage rule (WP-F's, applied to each writer separately)

At each τ_H and for each writer W ∈ {L, P}:
- eligible and W certified → W's certified stream bytes;
- eligible but W certified nothing, or non-evaluable → lossless bytes;
- failed object (download, parse, memory, solver, walltime) → its current MP json.gz bytes; no saving is credited.

Objects that exceed a node's memory are attempted once at the largest memory request of §7 and then count as
failed under this rule.

## 6. Estimators and reporting

- Stratified expansion estimators T̂_x = Σ_h (N_h / n_h) Σ_{i∈s_h} x_i for json bytes, float64 bytes, lossless
  bytes, and stored bytes of L and of P at each τ_H (WP-F's estimator, N_h and n_h from `strata.csv` and the sample).
- **Primary endpoint:** R_L(1e-6) = T̂_json / T̂_stored,L(1e-6) and the implied saving 8.4976 TB × (1 − 1/R_L).
- Also, at every τ_H:
  - R_P;
  - the ratio R_L / R_P;
  - R against float64 and against lossless;
  - the eligible fraction, by count and by bytes;
  - the per-object median of the certified-stream ratio L/P over objects where both writers certified.
- **Uncertainty:** stratified bootstrap. Objects are resampled with replacement within each stratum, 2,000 resamples,
  `numpy.random.default_rng(20261012)`. The intervals are 95% percentile intervals. R_L, R_P and R_L / R_P are
  computed on the same resample (paired).
- The design weights and the failure rule apply exactly as written. No object is dropped or reweighted after its
  outcome is known. There is no pass/fail gate.
- **`RESULTS.md`:**
  - numbers first: R_L, R_P and R_L / R_P at τ_H = 1e-6, then 1e-4 and 1e-8;
  - the saving in TB;
  - eligibility;
  - failures;
  - per-stratum tables;
  - wall time and memory per stratum.

## 7. Execution on Vanda

- **Allocation and staging:**
  - project `CFP04-CF-046`, route queue `auto`;
  - staging under `/scratch/junbotong/qoi-archive-law-20261012/`;
  - objects are prefetched on the login node and verified (size and SHA-256 recorded); compute nodes read only
    staged files.
- **Jobs:**
  - one PBS array task per object, `OMP_NUM_THREADS=1`;
  - memory by stratum: D01–D08 16 GB, D09 64 GB, D10a–D10c 120 GB;
  - one retry at 240 GB for an object that fails for memory.
- **Phases:**
  1. `probe`: one D01 object and one D10c object, end to end. Their outcomes are kept and counted in the run, because
     the protocol is frozen before them.
  2. `run`: all 300 objects.
- **Changes after freezing:** between and after the phases, only infrastructure may change (modules, paths, PBS
  resources, timeouts), each recorded in `DEVIATIONS.md` before any rerun.
- **Afterwards:**
  - results are copied back, verified by SHA-256 against the server, and committed under `results/`;
  - the staging directory is then deleted (Vanda cleanup rule).

## 8. Inputs (SHA-256 of the committed bytes)

| file | last commit | SHA-256 |
|---|---|---|
| `analysis/extensions_20260930/WP-F/sample.csv` | `cb6438c` | `b4382aeb9e46b772bd8b82c7af28659388fcee1c514c92654f9a627d03a250b5` |
| `analysis/extensions_20260930/WP-F/strata.csv` | `cb6438c` | `3b3ab5837f69716a1b1085e63549b8c1e339132ee5ef50dc5577669a752a57af` |
| `analysis/extensions_20260930/WP-F/run_wpf.py` | `a9e7c1b` | `ec093c506b88eb9586adfef03786858cad2dc72ad60364aa71981538015fb245` |
| `analysis/extensions_20260930/WP-F/analyze_wpf.py` | `a9e7c1b` | `e54c014ab64a306be41ec0712616d431d4fef4513359fcd03a7fafdc5317349d` |
| `analysis/general_qoac_law/DESIGN.md` | `39ba728` | `83f5a8098a877be162f3f110dbffafbfc520ab0a9bb34345af619b8937049608` |
| `analysis/qoac_v03_rdo/run_engineering.py` | `7ca412e` | `6cbdf8e31b4749cebb65a78582a8bec3032baf89073524b9c21065b65a7f3123` |
| `analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py` | `5b36848` | `f78dd40aba7f2a25727d4df08d621f3456244bfb14f404423551900c3504ce1a` |

The WP-F Bader result (`results_cloud/completed_v2/`) is not an input. It is cited only for comparison.
