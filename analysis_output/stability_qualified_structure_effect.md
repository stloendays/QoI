# Stability-qualified realized-Linf sensitivity

All analyses below first restrict materials to Protocol A.1 eligibility at the stated Bader-charge contract, then compare codecs over the full available base+tight ladders.

- A.1 eligible at tau=0.0001 e; SZ3/ZFP; <=0.10 dex: 105 pairs, 42 materials; median realized-Linf ratio 0.930; median resolved-Bader error ratio **1.96x** [95% bootstrap CI 1.61, 2.75]; A worse in 92.9% of materials.
- A.1 eligible at tau=0.0001 e; SPERR/ZFP; <=0.10 dex: 109 pairs, 42 materials; median realized-Linf ratio 0.947; median resolved-Bader error ratio **1.57x** [95% bootstrap CI 1.34, 1.85]; A worse in 78.6% of materials.
- A.1 eligible at tau=0.001 e; SZ3/ZFP; <=0.10 dex: 287 pairs, 128 materials; median realized-Linf ratio 0.963; median resolved-Bader error ratio **1.90x** [95% bootstrap CI 1.70, 2.20]; A worse in 91.4% of materials.
- A.1 eligible at tau=0.001 e; SPERR/ZFP; <=0.10 dex: 291 pairs, 124 materials; median realized-Linf ratio 0.965; median resolved-Bader error ratio **1.87x** [95% bootstrap CI 1.63, 2.08]; A worse in 79.8% of materials.
- A.1 eligible at tau=0.01 e; SZ3/ZFP; <=0.10 dex: 430 pairs, 200 materials; median realized-Linf ratio 0.953; median resolved-Bader error ratio **1.85x** [95% bootstrap CI 1.72, 2.00]; A worse in 91.0% of materials.
- A.1 eligible at tau=0.01 e; SPERR/ZFP; <=0.10 dex: 439 pairs, 193 materials; median realized-Linf ratio 0.953; median resolved-Bader error ratio **1.73x** [95% bootstrap CI 1.54, 1.93]; A worse in 78.2% of materials.

## Material-fixed-effect regression at matched realized-Linf scale

- A.1 eligible at tau=0.0001 e; SZ3 vs ZFP: **2.75x** [95% CI 2.40, 3.16], p=4.99e-47, n=1487 rows / 46 materials.
- A.1 eligible at tau=0.0001 e; SPERR vs ZFP: **1.97x** [95% CI 1.66, 2.33], p=3.34e-15, n=1487 rows / 46 materials.
- A.1 eligible at tau=0.001 e; SZ3 vs ZFP: **2.23x** [95% CI 2.09, 2.39], p=6.13e-115, n=4415 rows / 143 materials.
- A.1 eligible at tau=0.001 e; SPERR vs ZFP: **2.00x** [95% CI 1.86, 2.16], p=1.24e-71, n=4415 rows / 143 materials.
- A.1 eligible at tau=0.01 e; SZ3 vs ZFP: **2.02x** [95% CI 1.92, 2.13], p=3.8e-146, n=5975 rows / 229 materials.
- A.1 eligible at tau=0.01 e; SPERR vs ZFP: **1.77x** [95% CI 1.66, 1.88], p=6.78e-68, n=5975 rows / 229 materials.
