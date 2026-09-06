# Fixed-basin understatement: denominator-robust audit

Base successful paired rows: **4627**. Resolved > fixed in **99.70%**.

- fixed error <= 1e-12 e: 0.0% of rows.
- fixed error <= 1e-10 e: 0.0% of rows.
- fixed error <= 1e-08 e: 0.0% of rows.
- fixed error <= 1e-06 e: 4.4% of rows.
- fixed error <= 1e-05 e: 19.5% of rows.
- fixed error <= 0.0001 e: 43.9% of rows.

## 1. Ratio sensitivity to denominator floor

- denominator floor 1e-15 e: median resolved/fixed* = **52.8x** [49.3,57.8].
- denominator floor 1e-12 e: median resolved/fixed* = **52.8x** [49.3,57.8].
- denominator floor 1e-10 e: median resolved/fixed* = **52.8x** [49.3,57.8].
- denominator floor 1e-08 e: median resolved/fixed* = **52.8x** [49.3,57.8].
- denominator floor 1e-06 e: median resolved/fixed* = **52.6x** [49.2,57.6].
- denominator floor 1e-05 e: median resolved/fixed* = **45.0x** [42.2,47.7].
- denominator floor 0.0001 e: median resolved/fixed* = **21.8x** [20.6,23.1].

## 2. Material-balanced log-ratio

- Per-material median of the within-material median ratio: **59.5x** [50.8,70.3], 254 materials.
- SPERR: material-balanced ratio **118.0x** [87.2,167.7], 254 materials.
- SZ3: material-balanced ratio **7.8x** [6.5,9.4], 254 materials.
- ZFP: material-balanced ratio **117.2x** [99.4,131.7], 254 materials.

## 3. Core nominal tolerances

- rel=0.0001, SPERR, n=237: median paired ratio **133.0x** [117.0,150.4]; ratio of median errors **132.9x**; resolved>fixed 100.0%.
- rel=0.0001, SZ3, n=238: median paired ratio **9.0x** [8.4,10.3]; ratio of median errors **9.6x**; resolved>fixed 100.0%.
- rel=0.0001, ZFP, n=247: median paired ratio **224.2x** [198.6,282.5]; ratio of median errors **227.1x**; resolved>fixed 100.0%.
- rel=0.001, SPERR, n=181: median paired ratio **35.3x** [28.5,42.6]; ratio of median errors **34.7x**; resolved>fixed 100.0%.
- rel=0.001, SZ3, n=210: median paired ratio **2.9x** [2.6,3.2]; ratio of median errors **3.1x**; resolved>fixed 97.6%.
- rel=0.001, ZFP, n=240: median paired ratio **70.7x** [64.9,82.5]; ratio of median errors **69.1x**; resolved>fixed 99.6%.
- rel=0.01, SPERR, n=90: median paired ratio **10.3x** [8.6,13.8]; ratio of median errors **11.0x**; resolved>fixed 100.0%.
- rel=0.01, SZ3, n=49: median paired ratio **1.7x** [1.4,2.1]; ratio of median errors **1.6x**; resolved>fixed 91.8%.
- rel=0.01, ZFP, n=206: median paired ratio **30.4x** [27.0,33.5]; ratio of median errors **30.7x**; resolved>fixed 100.0%.

## 4. A.1-qualified core comparisons

- A.1 tau=0.0001 e, nominal rel=0.0001, SPERR, n=46: paired ratio **95.7x** [80.3,113.1], ratio-of-medians **91.7x**, resolved>fixed 100.0%.
- A.1 tau=0.0001 e, nominal rel=0.0001, SZ3, n=45: paired ratio **5.9x** [4.6,8.3], ratio-of-medians **6.1x**, resolved>fixed 100.0%.
- A.1 tau=0.0001 e, nominal rel=0.0001, ZFP, n=46: paired ratio **123.6x** [106.1,160.9], ratio-of-medians **133.1x**, resolved>fixed 100.0%.
- A.1 tau=0.001 e, nominal rel=0.001, SPERR, n=106: paired ratio **33.9x** [26.0,39.8], ratio-of-medians **31.5x**, resolved>fixed 100.0%.
- A.1 tau=0.001 e, nominal rel=0.001, SZ3, n=130: paired ratio **2.6x** [2.5,3.0], ratio-of-medians **2.9x**, resolved>fixed 96.2%.
- A.1 tau=0.001 e, nominal rel=0.001, ZFP, n=142: paired ratio **58.5x** [51.2,67.3], ratio-of-medians **56.1x**, resolved>fixed 99.3%.
- A.1 tau=0.01 e, nominal rel=0.01, SPERR, n=85: paired ratio **10.3x** [8.6,13.9], ratio-of-medians **11.2x**, resolved>fixed 100.0%.
- A.1 tau=0.01 e, nominal rel=0.01, SZ3, n=44: paired ratio **1.7x** [1.4,1.8], ratio-of-medians **1.5x**, resolved>fixed 90.9%.
- A.1 tau=0.01 e, nominal rel=0.01, ZFP, n=193: paired ratio **29.8x** [26.3,33.3], ratio-of-medians **29.8x**, resolved>fixed 100.0%.

## Recommendation

Use `resolved > fixed in 99.7% of successful base-ladder rows` as the denominator-robust directional headline. Report a multiplicative understatement only with an explicitly stated aggregation and denominator treatment. Avoid presenting the raw pooled 52.8x median as if it were invariant to near-zero fixed-basin errors.
