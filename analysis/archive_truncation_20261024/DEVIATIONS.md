# Deviations

Infrastructure-only changes after the protocol was fixed, numbered, each recorded before the run it affects.

D1 (2026-10-24 09:40, monitor takeover, infrastructure only). The monitor launched the shared downloader
`analysis/server_runs_20261024/vanda/prefetch.py` three times as `venv/bin/python prefetch.py` without loading the
`Python/3.12.3-GCCcore-13.3.0` module, so the venv interpreter failed at start (`libpython3.12.so.1.0: cannot open
shared object file`) and nothing was downloaded. Change: the downloader and the monitor's `status.py` call now run after
`source /etc/profile; module load Python/3.12.3-GCCcore-13.3.0`, as `common.sh` and `install.sh` already do. No study
file, input list, QoI, tolerance, writer, search, estimator, population or failure rule changed.

## Partition reuse in the decoded-frame moment certificate (found 2026-10-25, after the results)

`certify_m` passes the partition id "dec" for every decoded density, and `run_spin_s1.Bader` rewrites the partition
field only when the id changes, so every (writer, tau) pair after the first read the first writer's 1e-6 decoded
partition. Density streams and Hartree certificates are unaffected. Rerun with every decoded partition rebuilt:
`analysis/archive_partition_fix_20261025/` (study 5 of the second algorithm upgrade); its estimates replace this
study's wherever they are cited.
