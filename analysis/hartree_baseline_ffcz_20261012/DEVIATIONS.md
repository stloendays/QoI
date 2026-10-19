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


## 4. `ffcz_cpu` argument order (2026-10-19, after the failed probe 1463471, before its rerun)

Implementation bug, not a protocol change. Probe 1463471 (2026-10-18) failed 4/4 synthetic checks and 234/234 shakedown
evaluations at the FFCz step: `ffcz_command` put `-3 Nx Ny Nz` last, and the `Parsing()` of FFCz `CPU/main.cpp`
(`96649b3`) rejects a size that ends argv ("Missing size for 1D data"). The size now follows `-d`; flags and values are
unchanged. `test_ffcz.py` checks the position and gains a real `ffcz_cpu` correction-and-decode round trip (run on
Vanda: spatial and REL frequency bounds met). The failed probe output is kept as `probe_failed_1463471/` in staging.


## 5. FFCz PTW semantics and the probe gate (2026-10-19, author decision, before the probe rerun)

The synthetic probe check of §7 found that `-F PTW r` does not deliver the protocol's bound |ΔF(k)| ≤ r·|F(k)|: on the
48 × 56 × 72 field with an SZ3 base, max_k |ΔF(k)| / (r|F(k)|) was 4,790 at r = 1e-2 and 479,034 at r = 1e-4 (REL: 0.0030
and 0.30, confirmed). Reading FFCz `CPU/` at `96649b3`:
- `check_convergence_ptw` accepts a coefficient when |F+ΔF|²/|F|² lies in [√(1−r), √(1+r)], a magnitude-only
  condition with the phase free, or when both components of the unnormalized error are at most
  min(1−√(1−r), √(1+r)−1)/√2 + 1e-6 in absolute terms, so coefficients small against that constant are not held to
  a relative bound;
- `project_frequency_constraints_ptw` is called with `params_.delta_ptw`, which `ProjectionSolver::initialize` never
  sets (only `params_.delta`), so a PTW projection step reads an uninitialized value. On the synthetic field the
  convergence check passed at iteration 0 and no projection ran.

Author decision (2026-10-19): keep all 18 configurations and run PTW with the authors' code unchanged. Every PTW point,
like every REL point, is accepted or rejected by the decoded Hartree certificate of §2, which does not depend on
FFCz's own bound. The probe gate uses the REL frequency check only; the PTW ratios are still computed and reported
(`ptw_frequency_bounds_confirmed` in `probe.json`). The FFCz source and binary are not modified.
