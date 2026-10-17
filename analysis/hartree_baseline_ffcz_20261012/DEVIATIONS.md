# Deviations from the frozen protocol (`8f98f8b`)

Infrastructure only. Each entry is recorded before the run it affects.

## 1. PBS layout (2026-10-12, before the probe)

§9 says "A PBS array runs one (material, configuration) search set per task". Vanda allows 6 running jobs per user,
so the 1,656 (material, configuration) tasks run as a worker pool inside node jobs instead: one 36-core, 250 GB node
per `production.pbs` job, `xargs -P 32` over `tasks.txt`, `OMP_NUM_THREADS=1`. Each task writes its own checkpoint
and a resubmitted job skips complete ones. Configurations, intervals, certificate, τ, statistics and population are
unchanged.


## 2. Shell environment of the Vanda scripts (2026-10-12, before the probe)

Under `set -euo pipefail` a PBS job either has no `module` command (`/etc/profile` not sourced) or dies while sourcing `/etc/profile` (unset variables under `set -u`; verified on Vanda: exit 127). Every PBS script now runs `set +eu; source /etc/profile >/dev/null 2>&1; set -eu` before `module load`. The ARCH `install.sh` gets the same fix; its first launch had stopped silently before creating the venv. No scientific code changed.


## 3. Base-codec wrapper bug fixes (2026-10-17, after the failed probe 1462110, before its rerun)

Implementation bugs, not protocol changes. Probe 1462110 (2026-10-16) failed 4/4 synthetic checks and 234/234 shakedown
evaluations with `base-compress requires --input and --abs-bound`: `compress_base` passed `abs_bound` positionally into
`_worker_cmd`'s `output_path` slot, so no base compression (ZFP, SZ3, SPERR) ever ran and FFCz was never reached. It is now
passed by keyword. Testing the full subprocess round trip exposed a second defect behind the first: the SPERR decoder
subprocess did not import `hdf5plugin`, so the SPERR HDF5 filter was unregistered and decoding failed; it now imports it.
`test_ffcz.py` gains a command-construction test and a compress→decompress subprocess round trip for all three base codecs
that checks the absolute bound. Configurations, eps_b, intervals, r grid, certificate, statistics, population and failure
rules are unchanged. The failed probe output is kept as `probe_failed_1462110/` in staging.
