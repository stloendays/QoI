# Algorithm upgrade plan (2026-10-25)

Request (2026-10-25 14:54): 「帮我看看论文算法还可以如何优化和升级，并开始，不需要我审批，进入计划模式，最终完成就行」.
Branch `research/algo-upgrade-20261025` from revision 10 (`0d74c39`), worktree `D:\Research\QoI-algo-upgrade-20261025`.
This file is the plan; the protocols, writer and tests are committed before any material of either study is run.

## 1. Where the revision-10 algorithm leaves bytes on the table

Read-only pass over `analysis/qoac_v03_rdo/`, `analysis/operator_aware_codec_hartree_v02/`,
`analysis/qoac_h_strong_baselines/`, `analysis/archive_truncation_20261024/`, `analysis/general_qoac_law/` and the
revision-8–10 decisions. Every Hartree writer of the paper (A1 law, A2 truncation, A3 operational allocation) shares one
container: the v0.2 Hermitian-orbit topology, 32 radial shells, a JSON header and one zlib block of interleaved
smallest-width integers per shell. Three properties of that container, not of the allocation, limit the archive:

1. **Container and entropy coder.** The JSON header is 1.5–3 kB. At tau_H = 1e-4 a small object's whole stream is
   2–6 kB, so the header is up to half of it. zlib codes the quantized integers byte-wise without a probability model.
2. **The closed-form law has no zero-rate region.** A1 codes every shell, including shells whose operator-weighted
   signal is below the quantization noise the law assigns them. This is why truncation (A2) overtakes the law at 1e-4
   (archive 1,142 vs 1,036-fold) and why only the searched allocation (A3, 1,371-fold) beats both. Reverse
   water-filling — the closed-form rate–distortion solution for independent components — writes a component only if its
   signal exceeds the distortion level. Under the law's equal-slope steps Delta_k = alpha q_k^2 the operator-weighted
   high-rate noise is the same, alpha^2/12 per real component, in every orbit, so the rule needs no search: shell s is
   written iff its mean operator-weighted energy per real component exceeds alpha^2/12.
3. **Crystal symmetry is ignored.** Materials Project densities are symmetrized. A space-group operation maps a
   Fourier coefficient onto another with a known phase, c(h) = e^{2 pi i h·D M^{-1} T} c(h'), so most coefficients are
   predicted from one representative of their star. In the current container these duplicates are coded again
   (development: 1.9–3.8 coefficients per symmetry class on Cmmm materials).

## 2. Development evidence (P1 engineering materials only)

Prototype on the P1 engineering materials (development set; never in a confirmatory cohort), single process on the
laptop. Bytes at tau_H = 1e-6 / 1e-4 (CR in brackets):

| material | A1 law | A2 trunc. | A3 operational | W water-filling, new coder | O operational, new coder | W + symmetry |
|---|---|---|---|---|---|---|
| mp-3148759 (Cmmm, 0.25 M) | 17,674 / 5,615 | 18,892 / 3,608 | 15,365 / 3,148 | 13,332 / 2,057 | 13,272 / 2,047 | 5,064 / 1,068 |
| mp-2521964 (Cmmm, 0.37 M) | 9,158 / 4,572 | 7,903 / 2,177 | 6,308 / 1,881 | 5,251 / 931 | 5,195 / 923 | 2,467 / 670 |
| mp-1870388 (0.59 M) | 21,087 / 6,177 | 23,518 / 3,897 | 17,213 / 3,077 | 15,743 / 2,263 | 15,683 / 2,024 | — |

The closed-form water-filling allocation is within 0.4–1% of the searched optimum under the same coder on two
materials and within 12% at 1e-4 on the third; with symmetry the stream is 2.1–3.0× smaller again. Prototype choices
fixed from this exposure: kappa = 1 (the rate–distortion value; 0.25–4 tried, 1 best or tied), no dead-zone rounding
(r = 0.4, 0.3 tried, no gain), symmetry tolerance 1e-5 ptp in real space (1e-8 admitted only half the operations of
mp-3148759 and coded 8,484 instead of 5,064 bytes), per-shell choice of the smaller of the adaptive coder and zlib (the
adaptive coder alone lost to zlib on low shells, where zlib's matches already find symmetry duplicates).

## 3. Candidate directions and the choice

| direction | part of the algorithm | expected gain (from §2 and the record) | strongest comparison | compute | chosen |
|---|---|---|---|---|---|
| **D1 water-filling law** | closed-form allocation | law → within ~1–10% of the searched optimum at both tolerances; removes the truncation crossover at 1e-4 | A3 / operational optimum under the same coder; truncation under the same coder | one Vanda job, 92 materials | **yes** |
| **D2 writer: container + adaptive coder** | entropy coding and header of every writer | 1.1–1.3× at 1e-6, 1.5–2.5× at 1e-4 (header) | the same allocation with the old container; pointwise codecs (own entropy coders) | same job | **yes** |
| **D3 symmetry-predictive coding** | entropy coding: prediction from the space group | 2–3× on symmetric cells, 1× on P1 | the same writer without symmetry; truncation and operational allocation with symmetry | same job | **yes** |
| archive re-estimate | consequence of D1–D3 | the 8.50 TB archive under the upgraded writer | A3 (347/1,371-fold), law, truncation, pointwise, all recorded | one Vanda job, 300 objects | **yes (study 2)** |
| linearized allocation for more QoIs | allocation for nonlinear QoIs | — | — | new QoIs, new contracts | no: needs new contracts and QSQ probes; not completable this round |
| H+B / Bader contract rate | joint contract | small: B side is a partition map | — | — | no: the Bader side is dominated by the map, not the writer |
| sequential QSQ | probe cost | seconds per material; not a byte or certification gain | — | — | no: changes no reported number |
| GPU / FFT batching | speed | wall time only | — | — | no: the archive estimate is byte-bound, not time-bound |

## 4. Studies

### Study 1 — `analysis/waterfill_writer_20261025/` (92 law-protocol materials)

Question: under the Hartree contract, how many bytes does the closed-form water-filling law need with the new
container and symmetry-predictive coding, against the operational optimum and truncation under the identical coder, and
against the revision-10 arms? Cohort: the 60 P1 bulk and 32 P3b slab materials of the law protocol. Arms (all with the
new container; every stream decoded and certified, historical and Nyquist-safe Hartree relative RMS < tau):
L1 law, W1 water-filling, W1S water-filling + symmetry, T1S truncation + symmetry, O1 and O1S operational allocation
without/with symmetry. Recorded arms A1, A2, A3, A6 from the law protocol rows. Tolerances 1e-6 (primary), 1e-4
(co-primary for the allocation question), 1e-8 (descriptive). Criteria in the study's PROTOCOL.md.

### Study 2 — `analysis/archive_waterfill_20261025/` (300 archive objects)

The revision-10 whole-object archive frame, sample, storage rule, moment policy and estimators unchanged
(`analysis/archive_truncation_20261024/PROTOCOL.md`), with writers W1S and O1S. Descriptive, like the T/O study.

## 5. Execution

- Protocols, writer (`w1.py`, `qac.py`, `symmetry.py`), tests and Vanda scripts committed and pushed before any
  material run; Vanda project CFP04-CF-046, staging `/scratch/junbotong/qoi-algo-20261025`.
- Monitor `C:\Users\ASUS\.claude\tools\qoi_algo_monitor.py` generated from `qoi_xcl_monitor.py`, replayed before use,
  registered in the 监控总台 (hub id `qoi-algo-20261025`). It stages, installs, prefetches, probes, submits, collects
  with SHA-256 checks and, after collection, starts the headless Claude finalization (`analysis/server_runs_20261025b/FINALIZE_TASK.md`).
- Finalization: recompute the key ratios from the rows, write the results, and — for results that hold — revision 11
  (`paper/nc-rev11-20261025`, worktree `D:\Research\QoI-nc-rev11-20261025`), audits and build; then remove the staging
  directory.

## 6. Deliverables

`analysis/waterfill_writer_20261025/results/{RESULTS.md,SUMMARY.json,rows.csv}`,
`analysis/archive_waterfill_20261025/results/{RESULTS.md,SUMMARY.json,objects.csv}`, revision 11 PDF/DOCX if the
results hold, and `D:\Research\QoI-algo-upgrade-20261025\ALGORITHM_UPGRADE_REPORT_20261025.md`.
