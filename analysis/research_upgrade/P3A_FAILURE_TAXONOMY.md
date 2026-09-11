# P3A first-run failure taxonomy

Frozen before any engineering retry on 2026-09-11 (Asia/Singapore).

## Scope

This audit classifies every recorded failure from the first P3A implementation-transfer run, GitHub Actions run `34605557997`. The original run and its aggregate commit `99f5adcaf08f7556b5d05fdb16f75b465592f52b` remain preserved as provenance.

## Complete accounting

- Planned solver evaluations: **432** = 24 materials × 3 solvers × (1 baseline + 5 frozen perturbation seeds).
- Successful rows in the first run: **72**.
- Recorded failure rows: **360**.
- Materials represented by failures: **20/24**.
- Failure stage: **360/360 `source_or_grid`**.
- Failure count by solver: **120 BaderKit on-grid + 120 Henkelman on-grid + 120 Henkelman near-grid**.
- Each affected material contributes exactly **18** failed cells, i.e. all three solvers and all six baseline/perturbed states are blocked together.

## Error-signature taxonomy

All **360/360** failures share one error family:

`RuntimeError: legacy float32 amplitude mismatch ...`

No recorded failure in the first run is a Bader-solver failure, atom-mapping failure, vacuum-handling failure, grid-shape failure, or source-download failure. The gate runs before the three solver implementations, so the 20 affected materials were not scientifically evaluated by P3A in the first run.

The mismatch is between (i) the float32 round-trip amplitude re-derived directly from the source density and (ii) the historical `probe_linf` value stored in `stability/stability_floor_A1_per_seed.csv`. The original P3A runner compared those values at an approximately binary-ULP tolerance. Historical CSV values are decimal serializations and, for affected rows, are shorter than the re-derived binary64 value. Representative archived values include `0.0001220593749167` and `0.0001219406249219`, while the corresponding re-derived values are `0.00012205937491671648` and `0.00012194062492199009`. This is far below any scientific perturbation scale but exceeds the inappropriate binary-ULP provenance gate.

## Independent workflow bookkeeping defect

The first-run workflow has a second, non-scientific defect. The runner intentionally exits with code `2` when a shard is fully accounted but contains recorded failures. GitHub's shell wrapper uses `-e`; therefore the pipeline can terminate before `exit_code.txt` is written, and the reporting step subsequently substitutes `99`. This can make a fully accounted shard appear to have an infrastructure/accounting failure. The aggregate nevertheless downloaded all shard artifacts and enforced the 432-cell accounting.

## Retry eligibility

A targeted engineering retry is permitted because all unresolved cells are blocked before any scientific solver call by the same provenance-comparison gate. The retry may change only:

1. amplitude *compatibility checking*: compare the source-rederived amplitude with the exact archived decimal token using a tolerance implied by that token's decimal serialization precision, while continuing to use the frozen archived amplitude for the historical five-seed perturbation generation;
2. workflow exit-code capture: disable shell `errexit` only long enough to capture the runner's explicit `0/2` return code and archive it reliably.

The retry must **not** change the 24-system panel, historical seed set `{20260905,1,2,3,4}`, solver definitions, Henkelman source, BaderKit version, density source identity, atom mapping, perturbation family, QSQ thresholds, or the original P1/P2 results.

Only the 20 materials listed in `validation/qsq_prospective/p3a_retry_materials.txt` are eligible for the targeted retry. The four first-run complete materials are retained as frozen first-run measurements for the combined 24-system analysis.

## Interpretation

The first run does **not** demonstrate 360 scientific implementation failures. It demonstrates 360 recorded cells blocked by one overly strict provenance gate. Likewise, the four complete materials do not by themselves establish 24-system implementation transfer. P3A remains unresolved until the predeclared engineering retry is completed and the combined 24-system analysis is re-aggregated.