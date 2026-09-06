# Complete-case sensitivity to registered downstream failures

A conservative complete-case analysis removes an entire material if any registered compressor/Bader case for that material failed at nominal relative tolerance <=0.01, regardless of which codec failed. This prevents selective survival of successful rows from favouring a codec in matched-realized-Linf comparisons.

- Low-tolerance failure rows: **24** across **20 unique materials**.
- Master materials before/after exclusion: 254 -> **234**.
- Low-tolerance failures by codec: {'ZFP': 20, 'SPERR': 4}.

- tau=0.0001 e, SZ3/ZFP, 0.10-dex matching: 40 materials; **1.91x** [1.49, 2.63], A worse 95.0%, median L∞ ratio 0.918.
- tau=0.0001 e, SZ3/ZFP, common-support interpolation: 44 materials; **2.37x** [2.06, 2.83], A worse 100.0%.
- tau=0.0001 e, SPERR/ZFP, 0.10-dex matching: 39 materials; **1.86x** [1.61, 2.19], A worse 82.1%, median L∞ ratio 0.919.
- tau=0.0001 e, SPERR/ZFP, common-support interpolation: 44 materials; **1.96x** [1.66, 2.27], A worse 93.2%.
- tau=0.001 e, SZ3/ZFP, 0.10-dex matching: 119 materials; **1.82x** [1.68, 2.01], A worse 91.6%, median L∞ ratio 0.965.
- tau=0.001 e, SZ3/ZFP, common-support interpolation: 132 materials; **2.07x** [1.95, 2.19], A worse 97.0%.
- tau=0.001 e, SPERR/ZFP, 0.10-dex matching: 115 materials; **2.00x** [1.79, 2.25], A worse 81.7%, median L∞ ratio 0.965.
- tau=0.001 e, SPERR/ZFP, common-support interpolation: 132 materials; **1.99x** [1.83, 2.21], A worse 94.7%.
- tau=0.01 e, SZ3/ZFP, 0.10-dex matching: 183 materials; **1.78x** [1.68, 1.93], A worse 90.7%, median L∞ ratio 0.938.
- tau=0.01 e, SZ3/ZFP, common-support interpolation: 208 materials; **1.96x** [1.80, 2.09], A worse 95.7%.
- tau=0.01 e, SPERR/ZFP, 0.10-dex matching: 178 materials; **1.86x** [1.72, 2.00], A worse 79.2%, median L∞ ratio 0.931.
- tau=0.01 e, SPERR/ZFP, common-support interpolation: 209 materials; **1.88x** [1.70, 2.03], A worse 88.0%.

## Mechanism attenuation on complete-case materials

- log reassignment coefficient: **0.880** [95% 0.723, 1.037], p=5.78e-28.
- SZ3/ZFP: realized-L∞ + material FE **2.34x** -> after adding reassignment **0.96x**.
- SPERR/ZFP: realized-L∞ + material FE **2.08x** -> after adding reassignment **0.94x**.
