# Deviations

Infrastructure-only changes after the protocol was fixed, numbered, each recorded before the run it affects.

D1 (2026-10-24 09:40, monitor takeover, infrastructure only). The monitor launched the shared downloader
`analysis/server_runs_20261024/vanda/prefetch.py` three times as `venv/bin/python prefetch.py` without loading the
`Python/3.12.3-GCCcore-13.3.0` module, so the venv interpreter failed at start (`libpython3.12.so.1.0: cannot open
shared object file`) and nothing was downloaded. Change: the downloader and the monitor's `status.py` call now run after
`source /etc/profile; module load Python/3.12.3-GCCcore-13.3.0`, as `common.sh` and `install.sh` already do. No study
file, input list, QoI, tolerance, writer, search, estimator, population or failure rule changed.

D2 (2026-10-24 16:50, author instruction "先处理服务器上 XC 实验的探针失败（NOMAD slab 那项），修好后按协议让监控继续跑完";
writer search). The probe (job 1482180) failed on slab nomad-deLeLsqokf9I: in Part 2 the L writer (v02, beta = 2)
raised `OverflowError: quantized coefficient would overflow int64` at the bracket's lower end alpha = 1e-14·ptp, which
`bisect_scale` evaluates first, and the exception ended the material as FAILED. At that scale the encoder cannot store
the slab's coefficients (|c / Delta| exceeds 0.95 of the int64 range), so no stream exists there. Change: for the L and
U writers the lower end of the alpha bracket is max(1e-14·ptp, alpha_floor), where alpha_floor is the smallest scale at
which every quantized coefficient fits the encoder's integer range (steps are linear in alpha, so alpha_floor =
max|c / Delta(alpha=1)| / (0.95·int64 max), times 1 + 1e-6). Where 1e-14·ptp was already representable (every bulk
material in the probe), the bracket and therefore every result is unchanged; below alpha_floor no stream exists, so
the search, the predicate, the smallest-passing-stream rule and the writers are otherwise unchanged. The P writer,
Part 1, populations, QoI, tolerances, estimators and failure rule are unchanged. The failed probe's checkpoint for
nomad-deLeLsqokf9I and `probe/verdict.json` are removed and the probe is rerun by the monitor (REPROBE marker,
monitor rule added the same day).
