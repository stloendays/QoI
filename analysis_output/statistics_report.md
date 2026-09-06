# Statistical post-processing audit

Generated from the frozen repository tables on branch `analysis/chatgpt-postprocess-20260906`.

## 1. Integrity and scope

- Master table: **6,343 rows**, **254 materials**, codecs = SPERR, SZ3, ZFP.
- Base ladder: **4,627 rows**; tight ladder: **1,716 rows**.
- `bound_respected` all true: **True**; maximum realized/nominal = **0.999999998**.
- Failure registry: **77 rows**; categories: {'bader_solver_failure': 76, 'basin_relabelling_symmetry_equivalent': 1}.

## 2. Bound utilization: nominal is not realized

- **SZ3**: median 1.0000; IQR [1.0000, 1.0000]; 5–95% [1.0000, 1.0000].
- **ZFP**: median 0.1575; IQR [0.1323, 0.1939]; 5–95% [0.0969, 0.2422].
- **SPERR**: median 1.0000; IQR [1.0000, 1.0000]; 5–95% [0.9971, 1.0000].

This directly separates a **bound-utilization effect** (how much of the requested pointwise budget a codec actually uses) from any **residual spatial-structure effect** at matched realized L∞.

### Same nominal compression tolerance

- SZ3/ZFP, nominal 0.0001: n=238, median resolved-QoI ratio **4.78×** [4.18, 5.64], A worse in 96.6%; median realized-L∞ ratio **5.85×**.
- SZ3/ZFP, nominal 0.001: n=210, median resolved-QoI ratio **7.77×** [6.49, 8.67], A worse in 98.1%; median realized-L∞ ratio **6.49×**.
- SZ3/ZFP, nominal 0.01: n=49, median resolved-QoI ratio **11.80×** [9.64, 12.75], A worse in 100.0%; median realized-L∞ ratio **8.46×**.
- SPERR/ZFP, nominal 0.0001: n=237, median resolved-QoI ratio **5.58×** [4.23, 7.02], A worse in 94.9%; median realized-L∞ ratio **5.90×**.
- SPERR/ZFP, nominal 0.001: n=181, median resolved-QoI ratio **5.32×** [4.59, 6.13], A worse in 96.7%; median realized-L∞ ratio **6.58×**.
- SPERR/ZFP, nominal 0.01: n=90, median resolved-QoI ratio **5.95×** [4.91, 7.82], A worse in 96.7%; median realized-L∞ ratio **7.97×**.

### Mutual-nearest matching on realized L∞

- SZ3/ZFP, ≤0.10 dex: 457 matched points from 214 materials; median material-level L∞ ratio 0.951; median QoI-error ratio **1.81×** [1.70, 1.95]; A worse in 90.2% of materials.
- SZ3/ZFP, ≤0.15 dex: 833 matched points from 241 materials; median material-level L∞ ratio 0.909; median QoI-error ratio **1.74×** [1.65, 1.88]; A worse in 95.0% of materials.
- SZ3/ZFP, ≤0.20 dex: 1089 matched points from 244 materials; median material-level L∞ ratio 0.869; median QoI-error ratio **1.71×** [1.63, 1.80]; A worse in 95.1% of materials.
- SZ3/ZFP, ≤0.25 dex: 1430 matched points from 247 materials; median material-level L∞ ratio 0.833; median QoI-error ratio **1.69×** [1.63, 1.79]; A worse in 94.7% of materials.
- SPERR/ZFP, ≤0.10 dex: 465 matched points from 206 materials; median material-level L∞ ratio 0.951; median QoI-error ratio **1.72×** [1.54, 1.89]; A worse in 77.7% of materials.
- SPERR/ZFP, ≤0.15 dex: 840 matched points from 241 materials; median material-level L∞ ratio 0.912; median QoI-error ratio **1.68×** [1.54, 1.78]; A worse in 83.4% of materials.
- SPERR/ZFP, ≤0.20 dex: 1091 matched points from 245 materials; median material-level L∞ ratio 0.876; median QoI-error ratio **1.74×** [1.62, 1.85]; A worse in 83.7% of materials.
- SPERR/ZFP, ≤0.25 dex: 1431 matched points from 248 materials; median material-level L∞ ratio 0.846; median QoI-error ratio **1.68×** [1.56, 1.83]; A worse in 86.7% of materials.

Interpretation rule: a large same-nominal ratio that collapses toward 1 after realized-L∞ matching is primarily a **bound-utilization** phenomenon; a ratio that remains materially above 1 after matching is evidence for a **codec-specific residual structure effect** beyond L∞ magnitude.

### Material-fixed-effect regression

Common realized-L∞ support: [1e-05, 70.2], n=6316, centered at log10 L∞=-0.950.
- C(codec, Treatment(reference='ZFP'))[T.SZ3]: beta=0.288 log10 units; multiplicative effect 1.94× [95% CI 1.84, 2.05], p=4.25e-128.
- C(codec, Treatment(reference='ZFP'))[T.SPERR]: beta=0.235 log10 units; multiplicative effect 1.72× [95% CI 1.61, 1.83], p=1.32e-63.
- logL_c:C(codec, Treatment(reference='ZFP'))[T.SZ3]: beta=-0.043 log10 units; multiplicative effect 0.91× [95% CI 0.84, 0.98], p=0.00928.
- logL_c:C(codec, Treatment(reference='ZFP'))[T.SPERR]: beta=-0.037 log10 units; multiplicative effect 0.92× [95% CI 0.86, 0.98], p=0.00687.

## 3. Fixed-basin versus resolved-basin error

Across the 4,627-row base ladder, finite resolved/fixed understatement ratios have median **52.8×**, p90 **738.8×**; 96.5% exceed 2×, 79.3% exceed 10×, and 37.8% exceed 100×.
- SPERR: median 100.1×; p90 821.7×; >2× in 99.9%.
- SZ3: median 8.0×; p90 58.5×; >2× in 88.6%.
- ZFP: median 106.9×; p90 1622.9×; >2× in 99.6%.

## 4. Compression–certification frontier

- τ=0.0001, bulk: SPERR: 4.2×, status {"CERTIFIED": 38, "UNCERTIFIED": 4}; SZ3: 6.3×, status {"CERTIFIED": 36, "UNCERTIFIED": 6}; ZFP: 7.6×, status {"CERTIFIED": 42}
- τ=0.0001, slab: SPERR: 3.9×, status {"CERTIFIED": 1, "UNCERTIFIED": 3}; SZ3: 8.4×, status {"CERTIFIED": 2, "UNCERTIFIED": 2}; ZFP: 10.5×, status {"CERTIFIED": 4}
- τ=0.001, bulk: SPERR: 6.2×, status {"CERTIFIED": 102, "UNCERTIFIED": 1}; SZ3: 12.9×, status {"CERTIFIED": 102, "UNCERTIFIED": 1}; ZFP: 13.5×, status {"CERTIFIED": 102, "UNCERTIFIED": 1}
- τ=0.001, slab: SPERR: 5.1×, status {"CERTIFIED": 35, "UNCERTIFIED": 5}; SZ3: 14.1×, status {"CERTIFIED": 34, "UNCERTIFIED": 6}; ZFP: 15.3×, status {"CERTIFIED": 40}
- τ=0.01, bulk: SPERR: 11.5×, status {"CERTIFIED": 161, "UNCERTIFIED": 7}; SZ3: 51.8×, status {"CERTIFIED": 160, "UNCERTIFIED": 8}; ZFP: 30.0×, status {"CERTIFIED": 166, "UNCERTIFIED": 2}
- τ=0.01, slab: SPERR: 8.1×, status {"CERTIFIED": 47, "UNCERTIFIED": 14}; SZ3: 67.8×, status {"CERTIFIED": 47, "UNCERTIFIED": 14}; ZFP: 40.5×, status {"CERTIFIED": 59, "UNCERTIFIED": 2}

## 5. Can conventional descriptors predict A.1 resolvability?

- τ=0.0001: dev 5-fold AUROC 0.643 ± 0.094; external AUROC **0.409**, balanced accuracy 0.484; eligibility prevalence dev/ext 18.1%/27.7%.
- τ=0.001: dev 5-fold AUROC 0.636 ± 0.048; external AUROC **0.387**, balanced accuracy 0.430; eligibility prevalence dev/ext 56.3%/67.7%.
- τ=0.01: dev 5-fold AUROC 0.472 ± 0.109; external AUROC **0.398**, balanced accuracy 0.338; eligibility prevalence dev/ext 90.2%/90.8%.

## 6. Protocol A.1 probe validation

- Matched float32 vs calibrated random-noise probe (amplitude factor 1): n=18, median floor ratio **29.0×**; float32 median exact ties 82 vs noise 0; zero voxel reassignment 9/18 vs 2/18.
- Across random seeds at amplitude 1: median log10-floor range **0.47 decades**; maximum **2.39 decades**.
- Amplitude sensitivity from 0.1× to 10×: median floor shift **0.76 decades** (IQR 0.25–1.05).

## 7. Basin-domain mechanism decomposition

- Rows: 106 (12 materials). Max absolute closure residual = **2.220e-16 e**.
- Bounded dominance fraction |domain|/(|domain|+|integrand|): median **0.995**, IQR [0.965, 0.999]; >0.90 in 84.9% of cases.
- |domain|/|total| at the maximum-error atom: median **1.000** (can exceed 1 under cancellation).

## 8. Failure registry

- bader_solver_failure: 76
- basin_relabelling_symmetry_equivalent: 1
- Failure rows remain outside the successful benchmark by design; manuscript denominators should therefore state whether they are successful-decode/Bader rows, eligible materials, or all attempted cases.

## 9. Claim wording decision rule

1. **Always safe:** A nominal pointwise error bound alone is insufficient to predict downstream Bader fidelity.
2. **Stronger claim only if matched analysis survives:** At comparable realized L∞, codec identity remains associated with materially different resolved Bader errors, implicating spatial error structure beyond magnitude alone.
3. If the matched ratio collapses to ~1, attribute the same-nominal difference mainly to **bound utilization**, not spatial structure.
4. Describe the A.1 stability floor as a **protocol-defined / probe-defined numerical stability floor**, not an intrinsic material constant, because it is amplitude- and seed-dependent.

