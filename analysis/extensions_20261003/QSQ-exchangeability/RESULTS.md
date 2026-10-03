# QSQ probe exchangeability — results

Materials analysed: **254/254** (material-level failures: 0; probe failures: 0). Protocol: `PROTOCOL.md`.

## A. Local recomputation of the frozen five-seed floor

- exact floor matches (|Δ| ≤ 1e-9 e): **252/254**; max |Δ| = 2.45 e
- eligibility agreement at τ = 0.0001 e: **254/254**
- eligibility agreement at τ = 0.001 e: **254/254**
- eligibility agreement at τ = 0.01 e: **254/254**

## B. Exchangeability (fresh responses above the five-probe maximum; exchangeable value 1/6 = 16.67%)

- independent per-material streams: **16.52%** (2475/14986), 95% CI 14.74–18.39% → **ACCEPTED: CI contains 1/6**
- frozen shared seeds: 19.08% (2859/14986), 95% CI 17.16–21.01%

## C. Joint admission-and-exceedance rate (bound for n = 5: 6.70%)

| τ (e) | panel | joint rate | conditional risk among admitted | coverage |
|---:|---|---:|---:|---:|
| 0.0001 | frozen (shared seeds) | 0.727% (109/14986) | 4.016% | 46/254 |
| 0.0001 | independent streams | 0.928% (139/14986) | 5.013% | 47/254 |
| 0.001 | frozen (shared seeds) | 0.901% (135/14986) | 1.600% | 143/254 |
| 0.001 | independent streams | 0.721% (108/14986) | 1.317% | 139/254 |
| 0.01 | frozen (shared seeds) | 0.133% (20/14986) | 0.148% | 229/254 |
| 0.01 | independent streams | 0.207% (31/14986) | 0.228% | 230/254 |

## D. Agreement between the frozen and independent panels

- τ = 0.0001 e: agreement 237/254, κ = 0.776
- τ = 0.001 e: agreement 242/254, κ = 0.904
- τ = 0.01 e: agreement 253/254, κ = 0.977
