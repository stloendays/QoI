# Deviations from the frozen protocol (`9959c07`)

Infrastructure only. Each entry is recorded before the run it affects.

## 1. PBS layout and memory envelope (2026-10-12, before the probe)

§7 says "one PBS array task per object" with memory D01–D08 16 GB, D09 64 GB, D10a–D10c 120 GB and one retry at
240 GB. Vanda allows 6 running jobs per user, so objects run as worker pools inside 36-core, 250 GB node jobs:
- `production_small.pbs`: D01–D08 with `xargs -P 30` (about 8 GB per worker), then D09 with `-P 3` (about 80 GB per
  worker);
- `production_large.pbs`: D10a–D10c with `-P 2` (about 125 GB per worker);
- `retry_memory.pbs`: one pass with `-P 1` (the full 250 GB node) for objects that failed with MemoryError or a
  killed worker.

D01–D08 objects are at most a few million grid points, far below 8 GB in this pipeline. An object that still runs out
of memory reaches the single-worker retry, whose envelope is at least the protocol's 240 GB, and the failure rule of
§5 applies after it. Writers, contract, storage rule, estimators and sample are unchanged.


## 2. Shell environment of the Vanda scripts (2026-10-12, before the probe)

Under `set -euo pipefail` a PBS job either has no `module` command (`/etc/profile` not sourced) or dies while sourcing `/etc/profile` (unset variables under `set -u`; verified on Vanda: exit 127). Every PBS script now runs `set +eu; source /etc/profile >/dev/null 2>&1; set -eu` before `module load`. The ARCH `install.sh` gets the same fix; its first launch had stopped silently before creating the venv. No scientific code changed.
