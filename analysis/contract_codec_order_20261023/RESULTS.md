# Contract and codec order at matched density error — results

Re-analysis of the 254-material development benchmark `benchmark/master_benchmark_full.csv` (6,343 rows;
SHA-256 of the LF text d94839fd8b72e81e…). One SZ3/SPERR pair per material, chosen without Bader outcomes:
both realized density $L_\infty$ and RMSE within 0.10 dex, minimum summed absolute log mismatch
(`analyze_rank_reversal.py`, which re-runs the selection and checks every selected row against the benchmark).
Re-derived Bader error = maximum atomic-charge error with basins re-derived from the decoded density (the
self-partitioned Bader contract of the manuscript); fixed-partition error = the same charges integrated over the
reference basins.

## Codec order

| set | pairs | SPERR smaller error, fixed partition | SPERR smaller error, re-derived basins | order reversed | reversed fraction (Wilson 95% CI) | median SZ3/SPERR, fixed (95% CI) | median SZ3/SPERR, re-derived (95% CI) |
|---|---|---|---|---|---|---|---|
| all | 185 | 185/185 | 76/185 | 109/185 | 58.9% (51.7–65.8%) | 14.90 (13.37–16.49) | 0.936 (0.870–0.988) |
| bulk | 117 | 117/117 | 51/117 | 66/117 | 56.4% (47.4–65.1%) | 11.61 (10.68–12.49) | 0.980 (0.917–1.044) |
| slab | 68 | 68/68 | 25/68 | 43/68 | 63.2% (51.4–73.7%) | 22.41 (18.97–27.90) | 0.829 (0.680–0.971) |

Caliper sensitivity (both distortion measures within the caliper):

| caliper (dex) | pairs | reversed |
|---|---|---|
| 0.05 | 165 | 95/165 |
| 0.075 | 175 | 102/175 |
| 0.1 | 185 | 109/185 |
| 0.15 | 199 | 114/199 |
| 0.2 | 214 | 120/214 |

## Tolerance decisions on QSQ-admitted materials

| $\tau_B$ ($e$) | admitted pairs | SZ3 and SPERR decisions differ, fixed partition | differ, re-derived basins |
|---|---|---|---|
| 0.001 | 115 | 45/115 | 2/115 |
| 0.01 | 170 | 44/170 | 21/170 |

## Correlates of the re-derived error ratio (log SZ3/SPERR; Spearman, material bootstrap 95% CI)

| diagnostic | all (185) | bulk (117) | slab (68) |
|---|---|---|---|
| reassigned-voxel fraction | 0.607 (0.502–0.698) | 0.554 (0.414–0.680) | 0.676 (0.512–0.792) |
| fixed-partition Bader error | -0.138 (-0.278–0.007) | -0.094 (-0.271–0.095) | -0.014 (-0.244–0.226) |
| density RMSE | -0.074 (-0.208–0.070) | -0.247 (-0.400–-0.073) | 0.356 (0.106–0.571) |
| density maximum error | -0.027 (-0.174–0.130) | -0.092 (-0.287–0.106) | 0.112 (-0.150–0.351) |

SZ3 reassigned fewer voxels than SPERR in 173/185 pairs.
