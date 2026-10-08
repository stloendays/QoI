# QOAC-HB wide NOMAD slab cohort (N = 1) — frozen criteria (PROTOCOL.md `2ad4c68`)

Selection (PROTOCOL.md section 2; `selection/selection_log.json`):

| step | rows |
|---|---:|
| frame (P3b) | 820 |
| re-listed dropped entries | 194 identified, 0 resolved (+0) |
| CHGCAR header readable | 556 |
| size window 150,000 <= npoints <= 3,870,720 | 303 (4 below, 249 above) |
| after NOMAD id exclusion (352 ids) | 188 |
| after slab-formula exclusion (105 formulas) | 20 (10 formulas, 13 uploads) |
| AECCAR0 + AECCAR2 present, headers on the CHGCAR grid | 6 (1 formula, `Ni`; 6 uploads) |
| passed the input checks | 6/6 |
| drawn, **N** | **1** (`nomad-eKxYecHu4VTk`, Ni, 36x36x216 = 279,936 points, 2 atoms) |

CI run 37714279960 (workflow `hb_slab_nomad_wide.yml`, head `74116a7`, 2026-10-08 01:42–01:46 UTC, conclusion
success, 21/21 jobs); results commit `1ecac5c`. 1/1 material successful, 0 FAILED, 0 MISSING, 0 setting failures.
Byte counts and SHA-256 of both AECCAR downloads match `aeccar_sources.csv` (`results/manifest/aeccar_downloads.csv`).
Criteria evaluated with `evaluate_criteria.py` unchanged (committed bytes SHA-256 `0729424b…`, primary population only,
`CRITERIA.json` in this directory); its tests pass (5/5), `test_cohort_tables.py` passes (7/7).
Bootstrap: seed 20261007, 10,000 resamples of the median (with n = 1 every resample equals the single value).

## Primary analysis (N = 1, all planned)

| criterion | result | threshold | pass |
|---|---|---|---|
| 1. analyzable and jointly certified (R3, best post, all three tau_B) | 1/1 | >= ceil(1 x 46/48) = 1/1 | yes |
| 2. joint overhead at tau_B = 1e-4 (CR_hartree_only / CR_joint) | n = 1, median 1.000, CI [1.000, 1.000] | <= 1.10, CI upper <= 1.15 | yes |
| 3. utility at tau_B = 1e-4 (R3 / max of J, T1, GF at their best posts) | 1/1 wins, median 1.466, CI [1.466, 1.466], min 1.466 | >= ceil(1 x 36/48) = 1/1, > 1.10, CI lower > 1.00 | yes |

**Confirmatory PASS** on the population of N = 1 entry (criteria 1, 2 and 3). No sole certifier (0/1).

## Failures

- Materials: none (0/1 FAILED or MISSING).
- Settings: none (`failures.csv` empty).
- Uncertified (base, post, tau_B) streams after the at most 5 Bader attempts, counted by the aggregator as results: 30
  of 135 non-`hartree_only` streams: GP 27/27 (9 at each tau_B; GP has no candidates on fresh materials) and R3 1 at
  each tau_B (none at its best joint post-processor). J, T1 and GF 0.
- Selection: 264 frame rows whose CHGCAR is served with 0 bytes; 194 re-listed entries whose `rawdir` answers HTTP 500;
  14 rows in the pool without AECCAR files.

## Descriptive (1 analysed slab)

- Certified R3 best-post streams: 3/3 (tau_B 1e-3, 1e-4, 1e-5), best post-processor `none` at all three, joint CR
  428.9, maximum atomic-charge error 9.0e-6 e (error / tau_B 0.900 at 1e-5), reassigned-voxel fraction 0, Hartree
  relative RMSE 9.81e-7.
- Joint overhead 1.000 at all three tau_B.
- CTP decisions (R3, evaluated rows): unprojected 4/4 at each tau_B.
- Joint CR at tau_B = 1e-4: R3 428.9, J 292.6, T1 248.2, GF 36.1.
- Utility ratio: 1.466 at 1e-3 and 1e-4, 1.477 at 1e-5.
