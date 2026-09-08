# External confirmatory evidence for manuscript claims — 2026-09-08

Status: **62/63 confirmatory systems completed**. This is external-support evidence, not a redefinition of the frozen 63-system confirmatory cohort.

Frozen scientific implementation: `893f931b3045b0b628329db81999c2f439d4e830`.

Aggregate source: 59 successful GitHub Actions confirmatory outputs + three locally completed systems (`aflow-B1C1F6K1_ICSD_1194`, `aflow-B6H2O13Sr3_ICSD_262541`, `aflow-Mo3Na1O16P3_ICSD_66877`), aggregated with the frozen `validation/aggregate_formal_external.py`.

Current aggregate: **62 systems, 1669 rows, 0 boundary violations, 0 material-level failures**. The missing system is `aflow-Cl1O12Pb5V3_ICSD_203074`, which failed at AFLOW upstream retrieval after three HTTP-500 retries. Its Protocol-A.1 floor is 0.0036 e, so it affects only the `1e-2` evaluable denominator (56 observed vs 57 frozen expected) and does not affect the `1e-4` or `1e-3` statistics.

## External evidence mapped to existing claims

### Claim 1 — scalar pointwise L∞ magnitude does not determine chemical fidelity

External replication supports the development-side distortion argument:

- median realized-L∞ fraction of nominal budget: ZFP **0.153**, development **0.158**;
- SZ3 and SPERR: approximately **0.99999** externally;
- thus equal nominal tolerance is again not an equal-distortion comparison.

Error-structure diagnostic `abs(mean_signed_error) / RMSE` is also nearly unchanged between external and development data:

- SZ3: **0.035 external vs 0.037 development**;
- ZFP: **0.005 vs 0.003**;
- SPERR: **0.001 vs 0.001**.

This externally reproduces the qualitative separation between scalar pointwise distortion magnitude and downstream chemical fidelity. It supports an error-field-structure contribution beyond scalar L∞ but does not identify one unique spatial mechanism.

### Claim 6b — Bader instability is common and not predictable from cheap proxies

Observed Protocol-A.1 evaluable counts in the current 62-system confirmatory aggregate are:

- `tau = 1e-4`: **16/62**;
- `tau = 1e-3`: **42/62**;
- `tau = 1e-2`: **56/62**.

The frozen expected 63-system counts are 16 / 42 / 57. The sole difference at `1e-2` is exactly the missing `aflow-Cl1O12Pb5V3_ICSD_203074` system, which is eligible only at `1e-2`.

External median Protocol-A.1 floor is approximately **3.4e-4 e**, compared with approximately **7.5e-4 e** in development. The external set is numerically more stable overall, but widespread non-evaluability at strict thresholds remains.

### Claim 7 — a QoI must be stability-qualified before serving as a fidelity contract

The external cohort independently reproduces the need for stability qualification. At `1e-4`, only 16 of the 62 completed confirmatory systems are A.1-evaluable; at `1e-3`, 42 are evaluable. These counts agree exactly with the frozen expected counts because the single missing system is ineligible at both thresholds.

The frozen `build_confirmatory_external.py` correctly refuses to declare PASS at 62 systems; this completeness gate was not bypassed.

### Claim 8 — lossy compression remains worthwhile over exact alternatives

All three pre-specified external codec-ordering directions reproduce:

| tau (e) | Codec | External median certified compression ratio [95% CI] | Development median | Expected direction |
|---:|---|---:|---:|---|
| 1e-4 | ZFP | 13.0 [7.1, 20.4] | 7.8 | ZFP > SZ3 > SPERR |
| 1e-4 | SZ3 | 12.1 [7.3, 17.7] | 6.4 | ZFP > SZ3 > SPERR |
| 1e-4 | SPERR | 5.2 [4.2, 6.2] | 4.2 | ZFP > SZ3 > SPERR |
| 1e-3 | ZFP | 18.76 [14.3, 25.0] | 13.8 | ZFP ≈ SZ3 > SPERR |
| 1e-3 | SZ3 | 18.76 [12.1, 24.6] | 13.2 | ZFP ≈ SZ3 > SPERR |
| 1e-3 | SPERR | 6.4 [5.9, 6.9] | 5.8 | ZFP ≈ SZ3 > SPERR |
| 1e-2 | SZ3 | 68.2 [43.6, 103.8] | 57.7 | SZ3 > ZFP > SPERR |
| 1e-2 | ZFP | 40.7 [35.4, 46.6] | 31.9 | SZ3 > ZFP > SPERR |
| 1e-2 | SPERR | 10.8 [10.2, 12.5] | 10.3 | SZ3 > ZFP > SPERR |

Paired comparisons are also directionally consistent:

- at `1e-2`, SZ3 beats ZFP on **89% [80%, 96%]** of paired materials (development: 80%);
- at `1e-4`, ZFP beats SZ3 on **69% [44%, 88%]** (development: 89%);
- SPERR loses to each of ZFP and SZ3 on roughly **84–91%** of paired materials across the three thresholds.

The `1e-4` ZFP-SZ3 separation is weaker externally: medians are 13.0 vs 12.1 and the confidence intervals overlap. Manuscript wording should therefore emphasize directional reproduction and certification coverage rather than a strong quantitative separation.

## Additional mechanism replication

Holding Bader basins fixed strongly understates the re-derived Bader error externally:

- ZFP median understatement: **124x**;
- SPERR: **219x**;
- SZ3: **20x**;
- **82% of external rows** understate resolved-Bader error by more than 10x under fixed basins.

Development medians are approximately 180x, 194x, and 16x, respectively. The qualitative mechanism is therefore reproduced independently.

## Important cross-corpus qualification

The external NOMAD 2D subset is not geometrically equivalent to the development adsorbate/slab subset. At `1e-2`, external NOMAD 2D reaches approximately 115x for SZ3 and 49x for ZFP, compared with development-slab values near 68x and 40x. These systems should be described as **vacuum-containing 2D systems**, not as a direct slab-geometry replication.

## Current manuscript-safe summary

Use:

> **62/63 confirmatory systems completed; all pre-specified directional rate–fidelity expectations and the principal mechanism-level expectations reproduced.**

Do not use:

- `63/63 external confirmation complete`;
- `the frozen confirmatory gate passed`;
- `the missing AFLOW system was excluded from the frozen cohort`.

The missing AFLOW system remains a documented upstream execution failure. If the 62-system aggregate is reported before the final material is recovered, it should be labelled as an **execution-incomplete external sensitivity result**, not as a redefined confirmatory cohort.
