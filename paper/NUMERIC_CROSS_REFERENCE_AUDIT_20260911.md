# Numeric and cross-reference audit — 2026-09-11

**Scope:** reader-facing polished manuscript, Figures 1–7, currently built Supplementary objects, claim–evidence registry, and machine-readable source-of-record tables.

**Overall status: PASS AFTER CORRECTIONS.** The headline benchmark-validity numbers were already consistent. Three stale intermediate values were found and corrected: the Protocol A calibration zero-reassignment percentage, the Protocol A.1/archived floor-shift factor used in prose, and the development `1e-2 e` rate–fidelity summary. A stale development-bulk A.1 median floor in the claim–evidence matrix was also corrected.

## High-risk numeric audit

| Claim / object | Source of record | Recomputed value | Submission status |
|---|---|---:|---|
| Development reconstruction corpus | `benchmark/master_benchmark_full.csv` / operator audits | 254 systems; 6,343 rows | PASS |
| Stability universe | `stability/eligibility_summary_A1.csv` | 319 systems | PASS |
| A.1 non-evaluable fraction | `stability/eligibility_summary_A1.csv` | 79.94% / 41.38% / 9.72% at 1e-4 / 1e-3 / 1e-2 e | PASS |
| Figure 3 naive failures reclassified | `analysis/certifiability_reclassification_pooled_20260911.csv` | 518/533 = 97.2%; 296/310 = 95.5%; 61/108 = 56.5% | PASS |
| Figure 3 naive passes non-evaluable | same | 106/229 = 46.3% at 1e-4 e | PASS |
| Protocol A calibration: exact neighbour ties | `stability/probe_calibration.csv` | median 82 under archived float32 | PASS |
| Protocol A calibration: zero voxel reassignment | same | archived float32 9/18; same-amplitude primary noise 2/18 | **CORRECTED** (old prose said 62%) |
| Formal A.1/archived floor shift | `stability/stability_floor_A1.csv` + archived table; Figure 4 calculation | n=254 paired development materials; median 1.58e+04x (~1.6e4x) | **CORRECTED** (old prose used ~8.7e3 and wrong population label) |
| Development-bulk A.1 floor median | `stability/eligibility_summary_A1.csv` | 6.729e-4 e | **CORRECTED** in claim–evidence matrix |
| Strict certified error/A.1 floor | `supplement/S2_floor_relative.csv` | ZFP 1.091; SZ3 1.329; SPERR 1.232 median at 1e-4 e | PASS |
| Matched realized-Linf Bader effects | `analysis/matched_realized_linf_v1/REPORT.md` | ZFP/SZ3 0.557; ZFP/SPERR 0.601; SZ3/SPERR 1.033 | PASS |
| External eligibility | `external_summary_a1.csv` | 16/63; 42/63; 57/63 | PASS |
| External median CCR | `external_summary_a1.csv` | 1e-2 e: ZFP 40.57x; SZ3 65.89x; SPERR 10.82x | PASS |

## Corrected development rate–fidelity values at 1e-2 e

The polished manuscript and claim–evidence registry now use `benchmark/summary_a1.csv` directly.

| Stratum | Codec | n admitted | Certified fraction | Median CCR [95% bootstrap CI] |
|---|---|---:|---:|---:|
| bulk | SZ3 | 168 | 95.2% | 51.8x [47.7, 60.3] |
| bulk | ZFP | 168 | 98.8% | 30.0x [27.1, 31.9] |
| bulk | SPERR | 168 | 95.8% | 11.5x [10.1, 13.2] |
| slab | SZ3 | 61 | 77.0% | 67.8x [59.6, 70.6] |
| slab | ZFP | 61 | 96.7% | 40.5x [35.8, 44.9] |
| slab | SPERR | 61 | 77.0% | 8.1x [7.7, 8.6] |

Historical prose values such as bulk SZ3 52.0x [48.0, 61.7] and slab SZ3 69.6x [65.9, 72.3] are intermediate summaries and must not be used in the final submission package.

## Figure-by-figure consistency

- **Figure 1:** conceptual measurement contract; no high-risk numerical statistic.
- **Figure 2:** electron-count 3,205/1,383 result and Hartree 6,270-row / slope 1.02 / material-R2 statistics agree with the dedicated operator audits.
- **Figure 3:** 762 decisions per threshold and all binary-to-three-state counts agree with the frozen pooled reclassification CSV and Supplementary Table S4.
- **Figure 4:** manuscript wording now matches the pre-freeze 18-material calibration and the current formal paired-development Figure 4 calculation. The historical ~8,700x statement is not used as the current five-seed A.1/archived comparison.
- **Figure 5:** mechanism statements remain qualitative/representative in the polished manuscript and do not overgeneralize basin migration to arbitrary QoIs.
- **Figure 6:** equal-nominal realized-Linf ratios and 0.10-dex matched effects agree with `analysis/matched_realized_linf_v1/REPORT.md`.
- **Figure 7:** 63 systems, 1,689 retained rows, 0 material failures, 0 bound violations, 3 row-level Bader solver failures, eligibility 16/42/57 and tolerance-dependent CCR values agree with the frozen external confirmatory files.

## Supplementary cross-reference state

Safe to cite now:
- Tables **S1–S9** are built as submission-facing drafts/objects.
- Figures **S1–S4 and S7** are locked R-generated objects.
- The polished manuscript currently cites built/locked operator-control, stability, reclassification and floor-scale SI objects as appropriate.

Deferred until built/locked:
- Tables S10–S14.
- Figures S5, S6 and S8.

This prevents the final Word/PDF from containing dangling Supplementary references.

## Denominator lock

Do not interchange these analysis universes:
- **254** = development benchmark.
- **319** = 254 development + 65 external descriptive/stability records.
- **65** = external descriptive/stability set.
- **63** = primary untouched confirmatory cohort.

## Submission rules frozen by this audit

1. Machine-readable tables override historical prose summaries.
2. `non-evaluable` is neither pass nor fail.
3. Figure 3 fractions use naive failures as denominators (533/310/108), not all 762 decisions.
4. The 46.3% value is 106/229 naive passes at 1e-4 e that are non-evaluable.
5. The `1e-4 e` floor result is **floor-scale / consistent with an emerging analysis-limited regime**, not a universal `plateau = floor` law.
6. Protocol A remains archived; Protocol A.1 is operative.
7. Development rate–fidelity values must be regenerated from `benchmark/summary_a1.csv` at build time.
8. External rate–fidelity values must be regenerated from the frozen 63-system confirmatory tables, not the 65-system descriptive aggregate.
