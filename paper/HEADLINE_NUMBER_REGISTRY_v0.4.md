# Headline number registry v0.4

**Date: 2026-09-08**

Use this file as the numerical source-of-truth for manuscript v0.4. Values are grouped by evidence layer so development, external confirmation and independent robustness are not conflated.

## A. Development benchmark

- Development materials: **254**
- Successful compressed reconstructions: **6,343**
  - base ladder: **4,627**
  - tight ladder: **1,716**
- Codecs: **SZ3, ZFP, SPERR**
- Development master table: `benchmark/master_benchmark_full.csv`

### Fixed-basin vs re-derived Bader

- Re-derived Bader error > fixed-basin error in **99.7%** of 4,627 successful base-ladder rows.
- Mechanism interpretation must emphasize direction and domain migration; do not quote one universal understatement factor.

### Representative domain decomposition

- Representative materials: **12**
- Median bounded domain contribution: **0.995**
- IQR: **0.965–0.999**
- Fraction >0.90: **84.9%**

### Realized pointwise-error budget

- ZFP median `realized_Linf / nominal`: approximately **0.158**
- SZ3: approximately **1.000**
- SPERR: approximately **1.000**

### Matched realized-L∞, primary 0.10-decade caliper

| Pair | Resolved-Bader error ratio A/B | 95% material-bootstrap CI | Interpretation |
|---|---:|---:|---|
| ZFP / SZ3 | **0.557** | **0.525–0.598** | SZ3 ≈ 1.79× ZFP |
| ZFP / SPERR | **0.601** | **0.534–0.662** | SPERR ≈ 1.66× ZFP |
| SZ3 / SPERR | **1.033** | **0.976–1.072** | similar |

At τ=1e-2 e among jointly A.1-eligible matched pairs:
- ZFP − SZ3 certification: **+14.9 percentage points**
- ZFP − SPERR: **+17.0 percentage points**

### Material-fixed-effect mechanism attenuation

- Base multiplier SZ3/ZFP: **2.34**
- Base multiplier SPERR/ZFP: **2.08**
- After voxel-reassignment term: **0.96**, **0.94**
- Reassignment coefficient: **0.880 [0.723, 1.037]**
- p = **5.78×10^-28**

## B. Protocol A.1 numerical resolvability

Stability corpus: **319 systems** = 254 development + 65 frozen external.

| Bader contract | Non-evaluable | Fraction |
|---|---:|---:|
| 1e-4 e | **255 / 319** | **79.9%** |
| 1e-3 e | **132 / 319** | **41.4%** |
| 1e-2 e | **31 / 319** | **9.7%** |

Required wording: **Protocol-A.1 numerical stability floor at the stated perturbation amplitude.**

Do not call this an intrinsic material constant or a universal Bader precision limit.

## C. Final frozen external validation

### Completeness

Primary confirmatory cohort:
- **63/63 systems complete**
- **1,689 retained rows**
- **0 material-level pipeline failures**
- **0 pointwise-bound violations**
- **3 row-level Bader solver failures**, explicitly retained
- Frozen A.1 eligible counts: **16 / 42 / 57** at 1e-4 / 1e-3 / 1e-2 e
- `confirmatory_metadata.json`: **PASS**

Full descriptive corpus:
- **65/65 systems complete**
- **1,755 retained rows**
- **0 material-level failures**
- **0 bound violations**

### External primary certified compression ratio

| τ (e) | ZFP median CCR [95% CI] | SZ3 median CCR [95% CI] | SPERR median CCR [95% CI] | Frozen direction |
|---|---|---|---|---|
| 1e-4 | **13.03 [7.09, 20.43]** | **12.06 [7.28, 17.72]** | **5.17 [4.23, 6.23]** | ZFP > SZ3 > SPERR |
| 1e-3 | **18.76 [14.27, 25.04]** | **18.76 [12.14, 24.56]** | **6.40 [5.88, 6.88]** | ZFP ≈ SZ3 > SPERR |
| 1e-2 | **40.57 [35.40, 46.03]** | **65.89 [40.67, 101.85]** | **10.82 [10.18, 12.44]** | SZ3 > ZFP > SPERR |

All three pre-specified directional expectations: **REPRODUCED**.

### External paired comparisons

- At 1e-2 e: SZ3 beats ZFP in **89.47%** of eligible materials; bootstrap interval **80.70–96.49%**.
- At 1e-4 e: ZFP beats SZ3 in **68.75%** of eligible materials.
- At 1e-3 e: ZFP beats SZ3 in **64.29%** of eligible materials.
- SPERR loses to ZFP in **87.5% / 90.48% / 84.21%** at 1e-4 / 1e-3 / 1e-2.
- SPERR loses to SZ3 in **75.0% / 85.71% / 84.21%**.

Interpretation: the tight-threshold ZFP–SZ3 direction reproduces, but the external effect is narrower than development. Do not use “strongly superior” for ZFP at 1e-4.

### Last recovered Cl system

`aflow-Cl1O12Pb5V3_ICSD_203074`
- status: **COMPLETE**
- A.1 floor: **0.0035547403 e**
- attempted rows: **21**
- retained rows: **20**
- row-level Bader failures: **1**
- source bytes: **2,437,424**
- SHA256: `eb5872d5229ab8e3f7360c0add9e8619cf357bff1e11a7e494b68f2d5c36e983`
- median realized/nominal: ZFP **0.1569**, SZ3 **0.999998**, SPERR **0.999987**

## D. Independent Bader implementation supplement

Panel: 12 stability-stratified development materials + one separately labeled sentinel.

- Expected outcome rows: **1,560 / 1,560 complete**
- Henkelman on-grid / BaderKit on-grid codec-response ratio: median **1.00**, IQR **0.92–1.005**
- 10/12 representative five-seed noise floors agree to BaderKit print precision.

At relative tolerance 1e-4:

| Ratio | BaderKit | Henkelman on-grid | Henkelman near-grid |
|---|---:|---:|---:|
| SZ3 / ZFP Bader error | **6.2×** | **4.8×** | **3.2×** |
| SPERR / ZFP Bader error | **6.7×** | **5.5×** | **2.9×** |

Absolute floors can be implementation-dependent for materials whose **unperturbed** basin sets differ. The robustness claim is qualitative ordering and perturbation sensitivity, not equality of every atomic charge.

### Spatial controls

BaderKit median log2(control / source-codec response):
- global permutation: **0.26**
- density-stratified permutation: **0.26**
- periodic shift: **0.02**

Across solvers:
- SZ3 response typically increases by about **1.3–1.4×** when spatial autocorrelation is destroyed
- ZFP: about **1.1–1.3×**
- SPERR: no consistent increase
- periodic translation is approximately **null**

Independent supplement BaderKit median bounded domain share:
- codec rows: **0.990**
- spatial controls: **0.996**
- noise: **0.9999**
- float32 perturbation: **0.02**

## E. Manuscript-safe top-line conclusion

> **Pointwise error control is a reconstruction guarantee, not by itself a chemical-fidelity guarantee. In electron-density compression, trustworthy Bader-QoI certification requires measured realized distortion, re-execution of the field-derived partition, explicit numerical-resolvability qualification, and validation across independent data and implementation.**

## F. Claims that must not return

- “The 6–12× same-nominal codec gap is a pure error-geometry effect.”
- “Changing fixed to resolved Bader reverses the best codec.”
- “Protocol A.1 measures an intrinsic Bader precision limit.”
- “SZ3/ZFP ordering is universal across all thresholds.”
- “Spatial permutation proves a unique boundary-local causal mechanism.”
- “Henkelman and BaderKit give identical absolute charges/floors on every material.”
