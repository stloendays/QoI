# Deviations from the frozen protocol (`8f98f8b`)

Infrastructure only. Each entry is recorded before the run it affects.

## 1. PBS layout (2026-10-12, before the probe)

§9 says "A PBS array runs one (material, configuration) search set per task". Vanda allows 6 running jobs per user,
so the 1,656 (material, configuration) tasks run as a worker pool inside node jobs instead: one 36-core, 250 GB node
per `production.pbs` job, `xargs -P 32` over `tasks.txt`, `OMP_NUM_THREADS=1`. Each task writes its own checkpoint
and a resubmitted job skips complete ones. Configurations, intervals, certificate, τ, statistics and population are
unchanged.
