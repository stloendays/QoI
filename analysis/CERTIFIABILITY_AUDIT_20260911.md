# QoI certifiability audit — 2026-09-11

## 1. Binary pass/fail reclassification under Protocol A.1

The unit of analysis is one material–codec decision at a fixed Bader threshold. There are 254 development materials × 3 codecs = 762 decisions per threshold. The naive binary decision uses the repository flag `certified_at_tau_ignoring_eligibility`; the qualified decision first applies the A.1 material-level eligibility gate.

| tau (e) | naive fail | reclassified as non-evaluable | genuine eligible fail | reclassified / naive fail | naive pass that was non-evaluable |
|---:|---:|---:|---:|---:|---:|
| 1e-04 | 533 | 518 | 15 | 97.2% | 106 (46.3% of naive passes) |
| 1e-03 | 310 | 296 | 14 | 95.5% | 37 (8.2% of naive passes) |
| 1e-02 | 108 | 61 | 47 | 56.5% | 14 (2.1% of naive passes) |

### Interpretation

- At 1e-4 e, 518 of 533 apparent failures (97.2%) occur on A.1-ineligible material–threshold pairs. Only 15 of 533 apparent failures remain genuine eligible failures after qualification.
- At 1e-3 e, 296 of 310 apparent failures (95.5%) are reclassified as non-evaluable; only 14 remain genuine eligible failures.
- At 1e-2 e, 61 of 108 apparent failures (56.5%) are non-evaluable and 47 are genuine eligible failures.
- Eligibility is not a device that merely turns failures into exclusions. It also invalidates naive passes: at 1e-4 e, 106 of 229 naive passes (46.3%) occur on non-evaluable pairs. The scientific correction is therefore a three-state decision, not a more permissive pass criterion.

**Headline result:** strict-threshold binary benchmarking is dominated by invalid labels. At 1e-4 and 1e-3 e, more than 95% of naive codec failures cannot be scientifically attributed to the compressor because the reference Bader analysis is not independently resolvable at the requested tolerance.

## 2. Floor-normalized error check: does the tight regime quantitatively equal the A.1 floor?

The current frozen supplement reports resolved Bader error divided by the A.1 stability floor for certified points. This is a scale-consistency check, not a material-level plateau correlation statistic.

| tau (e) | codec | n | median dQ/floor | P10 | P90 |
|---:|---|---:|---:|---:|---:|
| 1e-04 | SPERR | 39 | 1.23 | 0.54 | 3.20 |
| 1e-04 | SZ3 | 38 | 1.33 | 0.75 | 2.86 |
| 1e-04 | ZFP | 46 | 1.09 | 0.34 | 3.25 |
| 1e-03 | SPERR | 137 | 3.55 | 0.92 | 19.91 |
| 1e-03 | SZ3 | 136 | 2.78 | 0.90 | 16.59 |
| 1e-03 | ZFP | 142 | 3.39 | 0.82 | 17.82 |
| 1e-02 | SPERR | 208 | 14.22 | 1.53 | 127.07 |
| 1e-02 | SZ3 | 207 | 14.61 | 1.73 | 128.38 |
| 1e-02 | ZFP | 225 | 10.70 | 1.31 | 129.86 |

### Interpretation

- At the strictest 1e-4 e contract, certified reconstruction errors are the same order as the independently measured A.1 floor: codec medians are 1.09–1.33 × floor and P90 is 2.86–3.25 × floor.
- At 1e-3 e, the distribution broadens substantially: medians are 2.78–3.55 × floor and P90 is 16.6–19.9 × floor.
- At 1e-2 e, codec error dominates the floor for many certified points: medians are 10.7–14.6 × floor and P90 is about 127–130 × floor.

**Supported conclusion:** the strictest certified regime is floor-scale, consistent with an emerging analysis-limited regime.

**Not yet supported:** a universal or material-level identity between the tight-ladder plateau and the A.1 stability floor. The frozen S2 summary contains no material-level plateau estimator or correlation coefficient, so the manuscript should not claim `plateau ≈ floor` as an established quantitative law. The plateau should remain supporting evidence unless a dedicated material-level analysis is added.

## 3. Manuscript consequence

The reclassification result is strong enough to become a primary Results claim. The plateau/floor statement should be deliberately weaker: **floor-scale behavior at the strictest certified contract is observed, but quantitative plateau–floor equivalence is not established by the current frozen analysis.**

## Frozen sources

- `benchmark/summary_a1.csv`
- `supplement/S1_S3_sensitivity.csv`
- `supplement/S2_floor_relative.csv`
- `figures/R/figure3_certification_landscape.R` (defines the material-level `eligible`, `certified`, and `ignoring eligibility` aggregation semantics)

No frozen scientific output was modified by this audit.