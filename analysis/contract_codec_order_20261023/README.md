# Contract and codec order at matched density error (2026-10-23)

Re-analysis of the committed 254-material development benchmark (`benchmark/master_benchmark_full.csv`). It asks
whether two reconstructions that match in density error keep their codec order when the Bader contract changes from
reference basins to basins re-derived from the decoded density.

- `analyze_rank_reversal.py`: re-runs the outcome-blind SZ3/SPERR selection (one pair per material, realized
  $L_\infty$ and RMSE within 0.10 dex), checks every selected row and value of `inputs/matched_real_material_pairs.csv`
  against the benchmark, and writes `results/rank_reversal_summary.json`, `material_level_rank_reversal.csv` and
  `rank_reversal_caliper_sensitivity.csv`.
- `analyze_migration_coupling.py`: Spearman correlations of the re-derived error ratio with the reassigned-voxel
  fraction and three scalar diagnostics, material bootstrap; writes `results/migration_coupling_*.{json,csv}`.
- `RESULTS.md`: the tables, generated from the two JSON summaries.
- Supplementary Fig. 1: `figures/nc/si/figS_order/make_figS_order.py`.

Run from this directory:

```
python analyze_rank_reversal.py --master ../../benchmark/master_benchmark_full.csv \
    --pairs inputs/matched_real_material_pairs.csv --output results --figures results/_figs
python analyze_migration_coupling.py --pairs inputs/matched_real_material_pairs.csv --results results --figures results/_figs
```

Both scripts hash their text inputs with CR removed (benchmark `d94839fd…`, pairs `fb6e77dc…`). Origin: the
private package `stloendays/Essay-Work_Store`, branch `research/rhocodec-mechanism-20261023` (`9c83cd5`), archive
SHA-256 `9faf33ed31abdc76a3cb7032ed38f541cafb471038d292850674972ae3953479`; rerun here on the repository benchmark
with identical counts (185 pairs, 109 reversals) and correlations.
