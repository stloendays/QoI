# Claim–evidence addendum — QoI certifiability (2026-09-11)

## New headline claim: binary benchmark labels are invalid at strict QoI tolerances without eligibility qualification

### Claim

A downstream Bader tolerance cannot be used as an unconditional codec pass/fail criterion. At strict thresholds, most apparent codec failures occur on material–threshold pairs for which the uncompressed Bader analysis is itself non-evaluable under Protocol A.1.

### Frozen evidence

Unit: one material–codec decision at a fixed Bader threshold. Development corpus: 254 materials × 3 codecs = 762 decisions per threshold.

| threshold | naive failures | failures reclassified as non-evaluable | genuine eligible failures | fraction of naive failures reclassified |
|---:|---:|---:|---:|---:|
| 1e-4 e | 533 | 518 | 15 | **97.2%** |
| 1e-3 e | 310 | 296 | 14 | **95.5%** |
| 1e-2 e | 108 | 61 | 47 | **56.5%** |

The qualification is not permissive filtering. It also invalidates nominal passes: at 1e-4 e, 106 of 229 naive passes (46.3%) occur on A.1-non-evaluable pairs.

### Supported manuscript statement

> At the two strictest Bader contracts, binary pass/fail reporting is dominated by non-evaluable targets: 518 of 533 apparent failures (97.2%) at 10^-4 e and 296 of 310 (95.5%) at 10^-3 e occur on material–threshold pairs that fail the independent Protocol A.1 stability qualification. Only 15 and 14 apparent failures, respectively, remain genuine failures among eligible pairs. Eligibility is not a relaxed pass criterion: at 10^-4 e, 106 of 229 naive passes also occur on non-evaluable pairs. The scientifically meaningful benchmark is therefore three-state rather than binary.

### Interpretation boundary

Do not say that Protocol A.1 "rescues" failing codecs. It changes the logical validity of the label. A non-evaluable pair is neither a pass nor a fail.

---

## Supporting claim: the strictest certified regime is floor-scale

### Frozen evidence

Source: `supplement/S2_floor_relative.csv`.

At 1e-4 e, median resolved-Bader-error / A.1-floor ratios among certified points are:

- SPERR: 1.23× (P10 0.54, P90 3.20; n=39)
- SZ3: 1.33× (P10 0.75, P90 2.86; n=38)
- ZFP: 1.09× (P10 0.34, P90 3.25; n=46)

At 1e-3 e, medians rise to 2.78–3.55×; at 1e-2 e, to 10.7–14.6×.

### Supported manuscript statement

> At the strictest 10^-4 e certified contract, downstream Bader errors are already on the same scale as the independently measured Protocol A.1 stability floor, with median error-to-floor ratios of 1.09–1.33 across codecs. This floor-scale behavior is consistent with an emerging analysis-limited regime.

### Claim boundary

The current frozen analysis does **not** establish a universal material-level identity between a tight-ladder plateau and the A.1 floor. `S2_floor_relative.csv` is a floor-normalized summary over certified points, not a dedicated per-material plateau estimator or correlation analysis. Do not write `plateau = floor` or claim a universal quantitative law.

---

## Provenance

Derived from frozen outputs only:

- `benchmark/summary_a1.csv`
- `supplement/S1_S3_sensitivity.csv`
- `supplement/S2_floor_relative.csv`
- aggregation semantics in `figures/R/figure3_certification_landscape.R`

Audit and machine-readable tables:

- `analysis/CERTIFIABILITY_AUDIT_20260911.md`
- `analysis/certifiability_reclassification_pooled_20260911.csv`
- `analysis/certifiability_reclassification_by_codec_20260911.csv`

No frozen benchmark rows, Protocol A.1 outputs, or scientific thresholds were changed in this audit.
