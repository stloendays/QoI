# Vanda runs of 2026-10-25 (algorithm upgrade)

Studies `analysis/waterfill_writer_20261025/` (92 law-protocol materials, W1 writer arms) and
`analysis/archive_waterfill_20261025/` (300 archive objects, writers W and Q). Staging
`/scratch/junbotong/qoi-algo-20261025/`, project CFP04-CF-046, queue `auto`.

Driven end to end by `C:\Users\ASUS\.claude\tools\qoi_algo_monitor.py` (stage → install → prefetch → probe →
production → collect → finalize). Do not qsub by hand; read the monitor's `STATUS.md` first.

| script | what |
|---|---|
| `vanda/install.sh` | login node: venv with the frozen pins, Bader 1.05 |
| `vanda/prefetch.py` | login node: 300 archive objects, 92 cohort sources, the development material |
| `vanda/probe.pbs` | test suites, development known answer, two cohort materials, two archive objects |
| `vanda/production_w1.pbs` | study 1, 92 materials |
| `vanda/production_arch_small.pbs`, `production_arch_large.pbs` | study 2 |
| `vanda/collect.sh` | tarball of checkpoints, probe and logs with SHA-256 |
| `FINALIZE_TASK.md` | the headless finalization the monitor starts after collection |
