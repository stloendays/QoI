# Self-contained HB bytes

This directory implements the frozen 2026-10-12 label-map byte analysis.
The confirmatory manifest is run only by GitHub Actions on Ubuntu 24.04.
The workflow builds Henkelman Bader 1.05 and uses eight deterministic shards.
It is started by `workflow_dispatch` or by the main session's `RUN_SENTINEL` push.

The shard command is:

```text
python run_selfcontained.py --manifest ... --shard-count 8 --shard-index 0 --bader ... --output-dir ...
```

After all shards finish, aggregate with:

```text
python aggregate_selfcontained.py --manifest ... --shards-root ... --output-dir results
```

The local test command is `python -m unittest test_selfcontained.py`.
The Windows checkout has no Henkelman binary, so do not use it for a confirmatory run.
The aggregate step writes `per_material.csv`, `summary.csv`, `SUMMARY.json`, and `RESULTS_DRAFT.md`.
