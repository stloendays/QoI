# Frozen archive-law run

1. Set `STUDY=analysis/archive_hartree_law_20261012` after staging this study, repository code, and frozen validation directory under `/scratch/junbotong/qoi-archive-law-20261012/`.
2. On Vanda, run `bash $STUDY/vanda/install.sh`.
3. From the staging root, run `$STUDY/vanda/venv/bin/python $STUDY/vanda/prefetch.py`.
4. Generate the complete list: `$STUDY/vanda/venv/bin/python $STUDY/run_archive_law.py --list-tasks > $STUDY/vanda/tasks.tsv`.
5. Split the list for the frozen pools:
   `awk -F '\t' '$2 ~ /^D0[1-9]$/' $STUDY/vanda/tasks.tsv > $STUDY/vanda/tasks_small.txt`.
6. `awk -F '\t' '$2 ~ /^D10[abc]$/' $STUDY/vanda/tasks.tsv > $STUDY/vanda/tasks_large.txt`.
7. Submit `$STUDY/vanda/probe.pbs`; it prints and runs the first D01 and first D10c sample objects.
8. Submit `$STUDY/vanda/production_small.pbs` and `$STUDY/vanda/production_large.pbs` after the probe.
9. The small job uses `-P 30` for D01–D08 and `-P 3` for D09; the large job uses `-P 2` for D10a–D10c.
10. Resubmit either production job safely when needed; complete checkpoints are skipped.
11. Submit `$STUDY/vanda/retry_memory.pbs` once for missing, MemoryError, or recorded worker-failure objects.
12. Inspect progress with `$STUDY/vanda/venv/bin/python $STUDY/vanda/status.py --root $STUDY/vanda`.
13. Run `bash $STUDY/vanda/collect.sh` and verify `SHA256SUMS` before copying results back.
14. Locally, run `python $STUDY/aggregate_archive_law.py --checkpoints $STUDY/vanda/checkpoints --out $STUDY/results` with the frozen NumPy/Pandas environment.
15. The local aggregate writes `objects.csv`, `estimates.csv`, `strata_results.csv`, `failures.csv`, `SUMMARY.json`, and `RESULTS_DRAFT.md`.
16. The run requires the frozen validation directory as `--frozen-validation-dir` (the PBS files use `$ROOT/frozen_validation`).
17. All writer outcomes are decoded Hartree certificates; no A2, A3, or A5 arm is run.
