# Frozen FFCz Hartree baseline

This directory implements the frozen protocol in `PROTOCOL.md` for the P1/P3b
cohorts and the `mp-3148759` probe material.

1. On Vanda, run `vanda/install.sh` to load the pinned modules, create the
   pinned Python environment, build FFCz CPU, and record the build evidence.
2. Run `vanda/prefetch.py` on the login node to stage both cohort manifests,
   the engineering manifest, and every verified source byte under `inputs/`.
3. Submit `vanda/probe.pbs`; inspect `probe/probe.json` before production.
4. Submit `vanda/production.pbs`; it uses 32 workers inside one 36-core node
   and resumes from complete task checkpoints.
5. Run `vanda/collect.sh` and copy back the archive, checkpoints, and hashes.
6. Locally run `python aggregate_ffcz.py --raw-root results_raw` to create
   `results/material.csv`, `summary.csv`, `SUMMARY.json`, and `RESULTS_DRAFT.md`.

`run_ffcz.py --check-inputs` verifies the frozen LF-byte SHA-256 table.
`run_ffcz.py --list-tasks` prints the 92 × 18 production task ids.
The probe uses a non-cubic 48 × 56 × 72 C-order array and numpy FFT checks.
