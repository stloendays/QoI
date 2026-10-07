# QOAC-HB slab cohort selected on AECCAR availability (N = 4) — frozen criteria (PROTOCOL.md `69f8fc2`)

Selection (PROTOCOL.md section 2): 119 pool rows, 33 reduced formulas, 5 uploads; 33/33 formulas visited, 118 rows
attempted; 4 accepted, 114 rejected `no_aeccar`, 0 rejected at the CHGCAR, header-grid or AECCAR input-QC steps.
**N = 4** (2 uploads, 2 entries each).

CI run 37600232959 (workflow `hb_slab_aeccar_cohort.yml`, head `4eee3f6`, 2026-10-07 09:23–10:06 UTC, conclusion
success, 21/21 jobs); results commit `e99ba3e`. 4/4 materials successful, 0 FAILED, 0 MISSING, 0 setting failures.
Byte counts and SHA-256 of all eight AECCAR downloads are in `results/manifest/aeccar_downloads.csv`. Criteria
evaluated with `evaluate_criteria.py` unchanged (committed bytes SHA-256 `0729424b…`, primary population only,
`CRITERIA.json` in this directory); its tests pass (5/5), `test_cohort_tables.py` passes (7/7).
Bootstrap: seed 20261007, 10,000 resamples of the median.

## Primary analysis (N = 4, all planned)

| criterion | result | threshold | pass |
|---|---|---|---|
| 1. analyzable and jointly certified (R3, best post, all three tau_B) | 4/4 | >= ceil(4 x 46/48) = 4/4 | yes |
| 2. joint overhead at tau_B = 1e-4 (CR_hartree_only / CR_joint) | n = 4, median 1.010, CI [1.008, 1.032] | <= 1.10, CI upper <= 1.15 | yes |
| 3. utility at tau_B = 1e-4 (R3 / max of J, T1, GF at their best posts) | 4/4 wins, median 1.218, CI [1.185, 1.544], min 1.185 | >= ceil(4 x 36/48) = 3/4, > 1.10, CI lower > 1.00 | yes |

**Confirmatory PASS** on the population of N = 4 entries (criteria 1, 2 and 3). No sole certifier (0/4).

## Failures

- Materials: none (0/4 FAILED or MISSING).
- Settings: none (`failures.csv` empty).
- Uncertified (base, post, tau_B) streams after the at most 5 Bader attempts, counted by the aggregator as results: 204
  of 540 non-`hartree_only` streams. GP 108/108 (36 at each tau_B); R3 17 at 1e-3, 31 at 1e-4, 31 at 1e-5 (none at its
  best joint post-processor); T1 6 at 1e-4 and 6 at 1e-5; J 1 at 1e-4 and 4 at 1e-5. GF 0.

## Descriptive (4 analysed slabs; npoints 1,474,560–3,870,720; 23–53 atoms; Ga11H4N11, Ga11HN11, HRu16(CO11)3, Ru16C3O34)

- Certified R3 best-post streams: 12/12 (4 materials x 3 tau_B), every one with maximum atomic-charge error <= tau_B
  (largest error / tau_B 0.346) and reassigned-voxel fraction 0.
- R3 best joint post-processor: `none` 3/4 and `hap:0.0001` 1/4 at tau_B = 1e-3; `hap:0.0001` 4/4 at 1e-4 and 1e-5.
- Median joint overhead: 1.000 at 1e-3, 1.010 at 1e-4 and 1e-5. Median R3 joint CR: 590.7 at 1e-3, 585.1 at 1e-4 and
  1e-5.
- CTP decisions (R3, evaluated rows): projected 0/12 at 1e-3, 1/1 at 1e-4, 1/1 at 1e-5.
- Median joint CR at tau_B = 1e-4: R3 585.1, J 487.4, T1 257.8, GF 37.4.
- Utility ratio at 1e-4: 4/4 > 1, range 1.185–1.544.
