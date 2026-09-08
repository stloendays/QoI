# External confirmatory rate–fidelity validation — 62/63 status (2026-09-08)

This note records the external validation result obtained from the frozen scientific implementation without changing any frozen protocol, corpus definition, codec settings, thresholds, exclusion semantics, or aggregation logic.

## Scope and provenance

- Frozen scientific implementation: `893f931b3045b0b628329db81999c2f439d4e830`
- Aggregator: frozen `validation/aggregate_formal_external.py` from commit `893f931...`
- Confirmatory cohort definition remains the frozen 63-system cohort in `validation/external_rate_fidelity_split.json`.
- Inputs used here: 59 successful GitHub Actions confirmatory results + three locally completed systems:
  - `aflow-B1C1F6K1_ICSD_1194`
  - `aflow-B6H2O13Sr3_ICSD_262541`
  - `aflow-Mo3Na1O16P3_ICSD_66877`
- Current aggregate: **62/63 confirmatory systems**, **1669 rows**, **0 boundary violations**, **0 material-level failures**.
- Local aggregate output reported at: `results/aggregate_confirmatory62_20260908`.
- The frozen `build_confirmatory_external.py` correctly stops because `62 != 63`; that gate was not bypassed.

The single missing confirmatory system is `aflow-Cl1O12Pb5V3_ICSD_203074`, which failed at the AFLOW upstream retrieval stage after three HTTP-500 retries. Its Protocol-A.1 floor is 0.0036 e, so it is ineligible at 1e-4 and 1e-3 and eligible only at 1e-2. Therefore its absence does not change any 1e-4 or 1e-3 statistics, while the 1e-2 eligible denominator is 56 instead of the frozen expected 57.

This record must not be described as a 63/63 completeness pass. The frozen cohort definition is unchanged; the missing system is recorded as an upstream execution failure, not silently removed from the frozen design.

## Completeness and eligibility audit

Observed Protocol-A.1 evaluable counts:

| tau (e) | Observed evaluable | Frozen expected | Difference |
|---:|---:|---:|---:|
| 1e-4 | 16 | 16 | 0 |
| 1e-3 | 42 | 42 | 0 |
| 1e-2 | 56 | 57 | -1 |

The only persistent row-level failures are for `nomad2d-1_3Aeqri4-hc`, ZFP at nominal relative tolerances 0.03 and 0.1, both Bader-solver `IndexError` rows. They remain in the failure registry under the frozen semantics and are not counted as passes.

## Primary rate–fidelity result: median certified compression ratio

External values below use the 62 completed confirmatory systems. Development values are from the 254-material development corpus.

| tau (e) | Codec | External median CCR [95% CI] | Development median CCR | Frozen directional expectation | Result |
|---:|---|---:|---:|---|---|
| 1e-4 | ZFP | 13.0 [7.1, 20.4] | 7.8 | ZFP > SZ3 > SPERR | reproduced |
| 1e-4 | SZ3 | 12.1 [7.3, 17.7] | 6.4 | ZFP > SZ3 > SPERR | reproduced |
| 1e-4 | SPERR | 5.2 [4.2, 6.2] | 4.2 | ZFP > SZ3 > SPERR | reproduced |
| 1e-3 | ZFP | 18.76 [14.3, 25.0] | 13.8 | ZFP ≈ SZ3 > SPERR | reproduced |
| 1e-3 | SZ3 | 18.76 [12.1, 24.6] | 13.2 | ZFP ≈ SZ3 > SPERR | reproduced |
| 1e-3 | SPERR | 6.4 [5.9, 6.9] | 5.8 | ZFP ≈ SZ3 > SPERR | reproduced |
| 1e-2 | SZ3 | 68.2 [43.6, 103.8] | 57.7 | SZ3 > ZFP > SPERR | reproduced |
| 1e-2 | ZFP | 40.7 [35.4, 46.6] | 31.9 | SZ3 > ZFP > SPERR | reproduced |
| 1e-2 | SPERR | 10.8 [10.2, 12.5] | 10.3 | SZ3 > ZFP > SPERR | reproduced |

All three pre-specified directional rate–fidelity expectations from the development corpus reproduce on the frozen external data available at 62/63 completeness.

## Paired codec comparisons

- At tau = 1e-2, SZ3 beats ZFP on **89%** of materials, 95% CI **[80%, 96%]**; development value: 80%.
- At tau = 1e-4, ZFP beats SZ3 on **69%** of materials, 95% CI **[44%, 88%]**; development value: 89%.
- SPERR loses to each of ZFP and SZ3 on approximately **84–91%** of paired materials across all three thresholds, consistent with the development direction.

At 1e-4, the ZFP–SZ3 separation is weaker externally: medians 13.0 vs 12.1 with overlapping confidence intervals. The manuscript should therefore avoid describing ZFP as clearly or strongly superior at 1e-4. A more defensible external statement is that ZFP certifies all 16 evaluable systems, while SZ3 and SPERR each have two evaluable systems with no certified rung.

## Mechanism-level replication

### Realized error budget

Median `realized_Linf / nominal_tolerance_absolute`:

- ZFP external: **0.153**; development: **0.158**.
- SZ3 external: approximately **0.99999**.
- SPERR external: approximately **0.99999**.

Thus equal nominal tolerance remains a codec-dependent distortion budget externally: ZFP again realizes only about 15% of the requested L∞ bound, whereas SZ3 and SPERR operate essentially at the bound.

### Fixed-basin understatement

Median fixed-basin understatement of re-derived Bader error externally:

- ZFP: **124x**
- SPERR: **219x**
- SZ3: **20x**

Development values are approximately 180x, 194x, and 16x, respectively. Across the external rows, **82%** underestimate resolved-Bader error by more than 10x when basins are held fixed.

### Error-structure diagnostic

For `abs(mean_signed_error) / RMSE`:

| Codec | External | Development |
|---|---:|---:|
| SZ3 | 0.035 | 0.037 |
| ZFP | 0.005 | 0.003 |
| SPERR | 0.001 | 0.001 |

The cross-corpus pattern is therefore nearly unchanged. SZ3 carries roughly seven times the directional signed-bias fraction of ZFP on the external set. This supports the qualitative claim that the codec with the best rate at loose chemical tolerance can still have a less favorable downstream chemical error structure.

This diagnostic supports an error-structure contribution; it does not by itself identify a unique spatial/topological mechanism.

## Cross-corpus differences that are not counterexamples

1. **The external corpus is numerically more stable overall.** Median Protocol-A.1 floor is 3.4e-4 e externally versus 7.5e-4 e in development. Accordingly, the external evaluable fraction at 1e-4 is about 26%, versus about 18% in development. This is consistent with the generally higher external CCR values.

2. **The 1e-4 ZFP advantage over SZ3 is weaker externally.** The direction remains ZFP > SZ3 > SPERR, but the ZFP/SZ3 magnitude is smaller and confidence intervals overlap. Manuscript wording should emphasize directional reproduction and certification coverage rather than a strong quantitative separation.

3. **The NOMAD 2D subset is not geometrically equivalent to the development slab subset.** At 1e-2, external NOMAD 2D reaches approximately 115x for SZ3 and 49x for ZFP, above development-slab values around 68x/40x. NOMAD 2D systems are isolated monolayers with substantial vacuum, whereas the development slab set contains adsorbate/slab geometries. This should be described as validation on vacuum-containing 2D systems, not a direct replication of the development slab geometry class.

## Scientific interpretation

At the present 62/63 completion state, the frozen external data reproduce:

1. the three pre-specified codec-ordering directions across tau = 1e-4, 1e-3, and 1e-2;
2. the codec-dependent realized-L∞ budget behavior;
3. the systematic failure of fixed-basin scoring to represent re-derived Bader error;
4. the cross-codec signed-error/RMSE structure seen in development.

Therefore the development conclusions generalize directionally to the independent frozen external corpus observed so far. This is strong external support, but the formal 63/63 completeness gate remains open because `aflow-Cl1O12Pb5V3_ICSD_203074` is missing for an upstream AFLOW HTTP-500 reason.

## Reporting rule

Use the phrase **"62/63 confirmatory systems completed; all pre-specified directional expectations reproduced"** for the current state.

Do not state:

- "63/63 external confirmation complete";
- "the missing material was removed from the frozen cohort";
- "the frozen confirmatory gate passed".

The missing AFLOW material should remain explicitly documented as an upstream retrieval failure. If a final manuscript analysis elects to report the 62-system completed set, it must be labelled as a documented execution-incomplete sensitivity result rather than a redefinition of the frozen 63-system confirmatory cohort.
