# WP-B — Density critical points as a second topology-sensitive QoI: results

All numbers below are read from `summary.csv`, which is computed by `analyze_wpb.py` from
`cp_reference.csv`, `cp_rows.csv`, `cp_probes.csv` and `failures.csv` (written by `run_wpb.py`).
Material-cluster bootstrap: 2,000 resamples, seed 20260928, percentile 95% intervals.

## Population actually run (declared before any statistic was computed)

- Population: **FULL_LADDER** (declared 2026-09-28T16:52:03 in `population.json`).
- Materials: 254 development materials (all rows of `materials_metadata.csv` with corpus `dev_*`).
- Reconstructions: all 6343 rows of `benchmark/master_benchmark_full.csv` regenerated at the stored `nominal_tolerance_absolute` (base and tight ladders, ZFP/SZ3/SPERR). Reproduction gate: realized L∞ within 0.95–1.05 of the stored `realized_Linf`.
- Perturbations: five QSQ seeds [20260905, 1, 2, 3, 4] plus 59 fresh iid labels 10000–10058 per material = 16256 probes (amplitude = the material's `probe_linf`; Generator(PCG64(seed)), uniform on [−ε, +ε)).

## Accounting

| Item | Count | Denominator |
|---|---:|---:|
| reconstruction_rows_scored | 6293 | 6343 |
| reconstruction_rows_gate_fail | 0 | 6343 |
| reconstruction_rows_other_failure | 50 | 6343 |
| probes_scored | 16256 | 16256 |
| probes_failed | 0 | 16256 |
| materials_reference_failed | 0 | 254 |

Failures are listed row by row in `failures.csv` (50 entries; 0 reproduction-gate, 50 other reconstruction, 0 probe). No failure is dropped from a denominator or counted as a pass.

## Reproduction of the frozen stack on this machine

- Realized L∞ / stored realized L∞ over all 6343 rows: min 0.999999446, max 1.000015962.
- Re-derived resolved Bader error within 1e-6 e of the stored value: 4968/6293 gate-passing rows (largest absolute difference 9.789 e); same side of the 1e-3 e threshold as the stored value: 6290/6293.
- Fresh-probe Bader response within 1e-6 e of the frozen P2 value: 14986/14986 (largest absolute difference 0 e).
- Five-seed Bader response within 1e-6 e of the frozen per-seed value: 1262/1270 (largest absolute difference 2.493 e).
- Reference n_max equal to BaderKit's own on-grid maxima count: 107/254 materials.

## Reference QoI

- n_max median 30 (range 2–1133); n_min median 24.5.
- Materials with n_max = natoms: 74/254; with at least one maximum in the vacuum basin: 55/254; with at least one atom whose basin holds no maximum: 68/254.

## Analysis 1 — QSQ-cp floor and eligibility

f^cp_m = max over the five seeds of |Δn_max|. Floor defined (all five seeds scored) for 254/254 materials.
Median f^cp = 0; f^cp = 0 for 141/254; 90th percentile 2.394e+04; max 3.456e+04.

| τ_cp | Eligible materials | Bulk | Slab |
|---|---:|---:|---:|
| 0 | 118/254 (46.46%) | 117/186 | 1/68 |
| 1 | 150/254 (59.06%) | 149/186 | 1/68 |
| 2 | 158/254 (62.20%) | 157/186 | 1/68 |

τ_cp = 0 requires an identical maximum-voxel set on all five seeds (protocol). Count-only variant (|Δn_max| = 0 on all five seeds): 141/254.

## Analysis 2 — Prospective test (P2 form), τ_cp = 0

| Endpoint | Group | Exceeding trials / trials | Rate [95% CI] | Materials |
|---|---|---:|---:|---:|
| abs(Δn_max) ≥ 1 (primary) | cp-eligible | 0/6962 | 0.00% [0.00%, 0.00%] | 118 |
| abs(Δn_max) ≥ 1 (primary) | screen-rejected | 6444/8024 | 80.31% [73.91%, 86.52%] | 136 |
| maximum set changed (secondary) | cp-eligible | 3/6962 | 0.04% [0.00%, 0.14%] | 118 |
| maximum set changed (secondary) | screen-rejected | 7509/8024 | 93.58% [90.58%, 96.24%] | 136 |

**Risk ratio (rejected / eligible), primary endpoint: inf [95% CI inf, inf]** (bootstrap resamples with infinite ratio: 2000, undefined: 0).
Risk ratio, secondary endpoint: 2172 [671.1, inf].
Fresh trials failed: 0/14986.

### Acceptance

Rule: QSQ generalizes to the cp QoI if the prospective risk ratio exceeds 5 with a 95% CI lower bound above 1.
**Verdict: QSQ_GENERALIZES_TO_CP_QOI** (RR = inf, CI lower bound = inf).

## Analysis 3 — Cross-QoI transfer

- Cohen's κ between Bader eligibility at 1e-3 e and cp eligibility at τ_cp = 0: **0.1337** [95% CI 0.0164, 0.2542], n = 254.
  Contingency: both eligible 75, Bader-only 68, cp-only 43, neither 68; raw agreement 56.30%.
- κ at τ_cp = 1 (secondary): 0.1056 [-0.01641, 0.2326].
- κ at τ_cp = 2 (secondary): 0.08201 [-0.04601, 0.204].
- Spearman ρ between log10 f_m (Bader) and f^cp_m: **0.1389** [95% CI 0.02798, 0.2554], n = 254.
- Spearman ρ between log10 f_m and the five-seed maximum Jaccard distance (secondary): 0.1932 [0.07689, 0.3094].

## Analysis 4 — Codec scoring (gate-passing reconstructions)

Gate-passing rows: 6293/6343. Pooled fraction with |Δn_max| = 0: 2163/6293 (34.37%); with identical maximum set: 1838/6293 (29.21%).

Fraction of rows with |Δn_max| = 0 by codec and nominal relative tolerance, split by cp-eligibility at τ_cp = 0 (k/n):

| Codec | Split | 1e-07 | 3e-07 | 1e-06 | 3e-06 | 1e-05 | 3e-05 | 0.0001 | 0.0003 | 0.001 | 0.003 | 0.01 | 0.03 | 0.1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ZFP | cp_eligible_tau0 | 75/75 | 75/75 | 75/75 | 75/75 | 116/118 | 103/113 | 97/113 | 84/111 | 62/111 | 31/110 | 10/105 | 1/81 | 1/36 |
| ZFP | cp_rejected_tau0 | 22/68 | 21/68 | 21/68 | 18/68 | 38/136 | 38/135 | 34/134 | 27/132 | 15/129 | 6/121 | 0/92 | 0/52 | 0/20 |
| SZ3 | cp_eligible_tau0 | 75/75 | 73/75 | 72/75 | 67/75 | 88/118 | 69/110 | 19/110 | 5/108 | 0/101 | 0/85 | 0/30 | 0/2 | – |
| SZ3 | cp_rejected_tau0 | 9/68 | 11/68 | 8/68 | 4/68 | 13/136 | 9/129 | 4/128 | 0/122 | 0/109 | 0/57 | 0/19 | 0/1 | – |
| SPERR | cp_eligible_tau0 | 75/75 | 73/75 | 73/75 | 68/75 | 93/118 | 73/112 | 36/111 | 15/106 | 8/101 | 5/89 | 0/61 | 0/12 | 0/2 |
| SPERR | cp_rejected_tau0 | 9/68 | 11/68 | 8/68 | 7/68 | 17/136 | 12/130 | 6/121 | 1/98 | 2/78 | 0/52 | 0/29 | 0/6 | 0/1 |

Certified-at-τ_cp rates (denominator = gate-passing rows of cp-eligible materials at that τ_cp; τ_cp = 0 requires an identical maximum set):

| τ_cp | Codec | Certified rows / eligible rows | Rate | Eligible materials with ≥1 certified rung |
|---|---|---:|---:|---:|
| 0 | ZFP | 760/1198 | 63.44% | 114/118 |
| 0 | SZ3 | 436/964 | 45.23% | 102/118 |
| 0 | SPERR | 479/1012 | 47.33% | 103/118 |
| 1 | ZFP | 1016/1503 | 67.60% | 147/150 |
| 1 | SZ3 | 598/1205 | 49.63% | 137/150 |
| 1 | SPERR | 671/1266 | 53.00% | 140/150 |
| 2 | ZFP | 1113/1579 | 70.49% | 156/158 |
| 2 | SZ3 | 656/1264 | 51.90% | 148/158 |
| 2 | SPERR | 716/1330 | 53.83% | 148/158 |
- Ignoring eligibility, rows meeting τ_cp = 0: 1838/6293 (29.21%).
- Ignoring eligibility, rows meeting τ_cp = 1: 2483/6293 (39.46%).
- Ignoring eligibility, rows meeting τ_cp = 2: 2722/6293 (43.25%).

## Analysis 5 — Operator contrast (same gate-passing rows)

- Spearman ρ between |Δn_max| and re-derived resolved Bader error: **0.5415** [95% CI 0.4813, 0.6001], n = 6293 rows.
- Spearman ρ between Jaccard distance and Bader error (secondary): 0.5768 [0.5219, 0.6306].
- Rows with |Δn_max| = 0 but Bader error ≥ 1e-3 e: **908/6293 (14.43%)** [95% CI 12.42%, 16.56%].
- Rows with |Δn_max| ≥ 1 but Bader error < 1e-3 e: **655/6293 (10.41%)** [95% CI 8.22%, 12.56%].
- Both fail: 3475/6293 (55.22%); both pass: 1255/6293 (19.94%).
- Conditional: P(Bader ≥ 1e-3 e | |Δn_max| = 0) = 908/2163 (41.98%); P(Bader < 1e-3 e | |Δn_max| ≥ 1) = 655/4130 (15.86%).
- Set-identity variant: identical set but Bader ≥ 1e-3 e 687/6293 (10.92%); set changed but Bader < 1e-3 e 759/6293 (12.06%).
- Same contrast on the perturbation probes: |Δn_max| = 0 but Bader ≥ 1e-3 e 3056/16256 (18.80%); |Δn_max| ≥ 1 but Bader < 1e-3 e 4120/16256 (25.34%); Spearman ρ 0.1612.

## Wall time

- Sum of per-material worker wall time: 282610 s (78.50 h).
- Sum of runner invocation wall time (2 invocation(s), 4 worker processes): 105049 s (29.18 h).

## Files

`cp_reference.csv` (per material), `cp_rows.csv` (per reconstruction, gate failures listed with status GATE_FAIL), `cp_probes.csv` (per perturbation), `cp_material_floors.csv` (per-material floors and eligibility), `summary.csv`, `failures.csv`, `population.json`, `provenance.json`, `run_log.txt`, `DEVIATIONS.md`.
