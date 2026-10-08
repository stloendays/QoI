# QOAC-HB self-computed slab cohort (N = 32) — frozen criteria (PROTOCOL.md `ae0076a`)

Cohort (PROTOCOL.md sections 1–6, `COHORT.md`): MP summary 2026-09-28 -> 5,524 ranked formulas; 62 visited, 40 slabs drawn; 39 converged (ALGO = Normal), 1 NELM twice after the ALGO = All fallback (draw rank 11, HfMnF6); input QC 39/39 pass; **N = 32** (draw ranks 1–10 and 12–33), npoints 1,568,000–5,376,000, 8–40 atoms. Density files: GitHub release `data-hb-selfslab-20261008` (96 assets, 1,805,055,269 bytes), served by `run_joint_selfslab.py` (DEVIATIONS D2); 96/96 downloads recorded in `results/manifest/release_downloads.csv` match the `cohort.csv` byte count and SHA-256.

CI run 37723028989 (workflow `hb_selfslab_cohort.yml`, head `4f22046`, 2026-10-08 03:30–06:00 UTC, conclusion success, 21/21 jobs); results commit `00f8b38`. 32/32 materials successful, 0 FAILED, 0 MISSING, 0 setting failures. Criteria evaluated with `analysis/hb_slab_aeccar_cohort_20261007/evaluate_criteria.py` in place and unchanged (committed bytes SHA-256 `0729424b…`, primary population only, `CRITERIA.json` in this directory); its tests pass (5/5), and the adapter test `test_run_joint_selfslab.py` passes (11/11). Bootstrap: seed 20261007, 10,000 resamples of the median.

## Primary analysis (N = 32, all planned)

| criterion | result | threshold | pass |
|---|---|---|---|
| 1. analyzable and jointly certified (R3, best post, all three tau_B) | 26/32 | >= ceil(32 x 46/48) = 31/32 | **no** |
| 2. joint overhead at tau_B = 1e-4 (CR_hartree_only / CR_joint) | n = 26, median 1.011, CI [1.007, 1.014] | <= 1.10, CI upper <= 1.15 | yes |
| 3. utility at tau_B = 1e-4 (R3 / max of J, T1, GF at their best posts) | 26/32 wins, median 1.453, CI [1.353, 1.532], min 1.229 | >= ceil(32 x 36/48) = 24/32, > 1.10, CI lower > 1.00 | yes |

**Confirmatory FAIL** on the population of N = 32 slabs (criteria 1, 2 and 3: fail, pass, pass). Sole certifiers: 0/26.

## Failures

- Materials: none (0/32 FAILED or MISSING).
- Settings: 0 (`failures.csv`).
- Criterion 1 misses (R3 at its best joint post-processor not certified at all three tau_B), 6/32, all SUCCESS materials, listed with every R3 Bader attempt of the material:

| material_id | formula | atoms | npoints | R3 certified at 1e-3 / 1e-4 / 1e-5 | R3 attempts | smallest R3 Bader error (e) | largest reassigned fraction | J, T1, GF certified at all three tau_B |
|---|---|---:|---:|---|---:|---:|---:|---|
| `mp-aaabxapz` | Ti2CoIr | 24 | 2,949,120 | no / no / no | 75 | 0.001295 | 0 | yes |
| `mp-aaaabsyn` | Li2GaAu | 24 | 2,949,120 | yes / no / no | 65 | 0.000670 | 0 | yes |
| `mp-aaacezrr` | LiZrSe2 | 24 | 4,032,000 | yes / no / no | 55 | 0.000806 | 0 | yes |
| `mp-aaabxhim` | Li2PdAu | 24 | 2,752,512 | yes / no / no | 60 | 0.000910 | 0 | yes |
| `mp-aaabxbrv` | Sc2PdPt | 24 | 3,600,000 | no / no / no | 75 | 0.001691 | 0 | yes |
| `mp-aaacpkjv` | HfZrOs2 | 24 | 3,317,760 | no / no / no | 75 | 0.001043 | 0 | yes |

- Uncertified (base, post, tau_B) streams after the at most 5 Bader attempts, counted by the aggregator as results: 1547 of 4320 non-`hartree_only` streams (R3 110 at 1e-3, 232 at 1e-4, 244 at 1e-5; J 0 at 1e-3, 2 at 1e-4, 28 at 1e-5; T1 4 at 1e-3, 23 at 1e-4, 39 at 1e-5; GF 0 at 1e-3, 0 at 1e-4, 1 at 1e-5; GP 288 at 1e-3, 288 at 1e-4, 288 at 1e-5); R3 at its best joint post-processor: 0.

## Descriptive (32 analysed slabs)

- Certified R3 best-post streams: 29/32 at 0.001, 26/32 at 0.0001, 26/32 at 1e-05; largest Bader error / tau_B 0.910, largest reassigned-voxel fraction 0.
- R3 best joint post-processor: 0.001: `none` 29; 0.0001: `hap:0.0001` 25, `none` 1; 1e-05: `hap:0.0001` 26.
- Median joint overhead (R3): 1.000 at 0.001 (n = 29), 1.011 at 0.0001 (n = 26), 1.011 at 1e-05 (n = 26). Median R3 joint CR: 1392.0 at 0.001, 1479.6 at 0.0001, 1479.6 at 1e-05.
- CTP decisions (R3, evaluated rows): projected 0/116 at 0.001, 10/20 at 0.0001, 11/11 at 1e-05.
- Median joint CR at tau_B = 1e-4 (certified materials): R3 1479.6 (26/32), J 975.3 (32/32), T1 764.5 (32/32), GF 45.2 (32/32), GP n/a (0/32).
- Utility ratio at 1e-4: 26/26 > 1, min 1.229.
- HB runtime per material on a runner: 370–2477 s (median 1293 s).
