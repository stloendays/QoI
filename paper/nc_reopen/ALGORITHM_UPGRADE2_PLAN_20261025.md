# Second algorithm upgrade plan (2026-10-25)

Request (2026-10-25 21:08): 「再看看有啥能继续升级研究的开始完善！」. Branch `research/algo-upgrade2-20261025` from
revision 11 (`1cfc871`), worktree `D:\Research\QoI-algo2-20261025`. Protocols, writer, runners, aggregators, tests and
Vanda scripts are committed before any cohort material or archive object is run.

## 1. Where revision 11's archive bytes are

Stratum-weighted from `analysis/archive_waterfill_20261025/results/objects.csv` (writer W):

| tau_H | density share | magnetization share | density bytes from cells with 1 / 2 symmetry operations |
|---|---|---|---|
| 1e-6 | 80.6% | 19.4% | 51.6% / 23.4% |
| 1e-4 | 36.5% | 63.5% | 47.7% / 23.9% |

Symmetry-predictive coding gains nothing on the cells that hold three quarters of the density bytes, and at 1e-4 the
magnetization stream — still written by pointwise codecs (SZ3 226, SPERR 73, ZFP 1 of 300 objects) — holds most of
the archive.

## 2. Directions

| direction | part of the algorithm | development evidence (P1 engineering materials only) | chosen |
|---|---|---|---|
| **D4 W2M: operator-aware magnetization stream** | the magnetization writer | the moment contract is a linear basin-integration operator; its symbol falls as q^-4 (Porod), the Hartree weight; W1 water-filling on m with alpha searched against the moments: 273 vs 6,750 B (CoOF), 437 vs 15,320 B, 715 vs 2,227 B; non-magnetic 26–63 B | **yes** |
| **D5 structure-factor prediction (SFP)** | density prediction without symmetry | per-shell quadratic form factors per species on the structure factors: W1S → W2S 1.15–2.40-fold at 1e-6 (1.72-fold on the cell without symmetry), 1.00–1.45-fold at 1e-4 | **yes** |
| **Partition fix** | correctness of revision 10/11 moment certificates | `certify_m` reused the first decoded partition for later (writer, tau) pairs (`analysis/archive_partition_fix_20261025/PROTOCOL.md`) | **yes (rerun)** |
| per-shell degree choice in SFP | side information | degree 3 better at 1e-6 by 5%, worse at 1e-4 | no: fixed degree 2 |
| linearized allocation for more QoIs | new contracts | — | no: needs new contracts and probes |
| GPU throughput | speed | — | no: the archive estimate is byte-bound |

## 3. Studies

- **Study 3** `analysis/sfp_spin_writer_20261025/` — W2 on the 92 law-protocol materials (W1S, W2S, W2, O2S; criteria
  G1 prediction gain, G2 closed form at the optimum with prediction, validity incl. reproduction of revision 11's W1S).
- **Study 4** `analysis/archive_w2_20261025/` — the 300-object archive under V (W2S + W2M) and VP (W2S + pointwise
  magnetization on the same partition); criteria A1 (V/W), M1 (magnetization stream), validity.
- **Study 5** `analysis/archive_partition_fix_20261025/` — T, O, W, Q rerun with every decoded partition rebuilt.

## 4. Execution

Vanda (CFP04-CF-046), staging `/scratch/junbotong/qoi-algo2-20261025`, scripts `analysis/server_runs_20261025c/vanda`.
Monitor `C:\Users\ASUS\.claude\tools\qoi_algo2_monitor.py` (generated from `qoi_algo_monitor.py`; replay 37/37), task
`qoi-algo2-monitor-60m`, hub id `qoi-algo2-20261025`; after collection it starts the headless finalization
`analysis/server_runs_20261025c/FINALIZE_TASK.md`: review, results, revision 12 (`paper/nc-rev12-20261025`; the
corrected T/O/W/Q numbers enter in any case, the new writers where their criteria hold), report
`D:\Research\QoI-algo2-20261025\ALGORITHM_UPGRADE2_REPORT_20261025.md`, staging removed.
