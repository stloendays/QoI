# Server runs of 2026-10-24 (Vanda): archive under truncation / operational optimum, and the XC-energy QoI

Two studies share one staging root, environment and monitor:

| study | protocol | runner | aggregate |
|---|---|---|---|
| whole-object archive, writers T (A2) and O (A3) | `analysis/archive_truncation_20261024/PROTOCOL.md` | `run_archive_truncation.py run` | `run_archive_truncation.py aggregate` |
| exchange-correlation energy of the stored density | `analysis/nonlinear_xc_20261024/PROTOCOL.md` | `run_xc.py` | `aggregate_xc.py` |

Pipeline (`vanda/`), driven by `C:\Users\ASUS\.claude\tools\qoi_srv_monitor.py` (scheduled task `qoi-srv-monitor-60m`,
monitor folder `D:\Research\QoI-ext-cache\monitor-srv-20261024`); nothing is submitted before 2026-10-24 04:45 (author
instruction to submit five hours after 2026-10-23 23:40):

1. stage: `git archive` of this branch's pushed head (study paths) and of the frozen validation tree (`893f931`) to
   `/scratch/junbotong/qoi-srv-20261024`, SHA-256 checked;
2. `install.sh` (login node): venv with the frozen pins + PySCF, Henkelman Bader 1.05 built from
   `mechanism/independent_bader_20260908/reference_source`;
3. `prefetch.py` (login node): 300 archive objects and 92 P1/P3b sources, size / SHA-256 checked, `inputs/MANIFEST.tsv`;
4. `probe.pbs`: libxc cross-check, known-answer writer check, two archive objects and two materials end to end;
   verdict `status.py --probe`;
5. `production_arch_small.pbs`, `production_arch_large.pbs`, `production_xc.pbs` after a passing probe;
6. `collect.sh`, copy-back with SHA-256, local aggregation into each study's `results/`.

Local checks: `archive_truncation_20261024/test_archive_truncation.py` (the aggregator reproduces the published 316.4,
1,036.3, 34.57 and 9.153), `archive_truncation_20261024/check_writers.py` (T and O reproduce the recorded A2/A3 bytes),
`nonlinear_xc_20261024/test_xc.py`; monitor `--replay` (22 cases).
