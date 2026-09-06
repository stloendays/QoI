# Reviewer stress tests

Primary stress tests restrict the compressor ladder to nominal relative tolerance <= 0.01. This removes the loose 0.03/0.1 region where registered Bader-solver failures concentrate and reduces sensitivity to codec-specific early stopping.

## 1. Failure-registry audit

- Total registry rows: 77; rows at nominal relative tolerance <=0.01: **24**.
- Low-tolerance failures by codec: {'ZFP': 20, 'SPERR': 4}.
- Failure categories overall: {'bader_solver_failure': 76, 'basin_relabelling_symmetry_equivalent': 1}.

## 2. Stability-qualified matched-realized-Linf sensitivity in the failure-free ladder

- tau=0.0001 e, SZ3/ZFP, <= 0.050 dex: 35 pairs / 25 materials; QoI ratio **1.80x** [1.29, 2.47], A worse in 80.0%; median L∞ ratio 0.977.
- tau=0.0001 e, SZ3/ZFP, <= 0.075 dex: 54 pairs / 37 materials; QoI ratio **1.96x** [1.55, 2.93], A worse in 89.2%; median L∞ ratio 0.966.
- tau=0.0001 e, SZ3/ZFP, <= 0.100 dex: 79 pairs / 41 materials; QoI ratio **1.96x** [1.55, 2.73], A worse in 95.1%; median L∞ ratio 0.920.
- tau=0.0001 e, SZ3/ZFP, <= 0.150 dex: 163 pairs / 46 materials; QoI ratio **2.03x** [1.85, 2.57], A worse in 100.0%; median L∞ ratio 0.884.
- tau=0.0001 e, SPERR/ZFP, <= 0.050 dex: 34 pairs / 24 materials; QoI ratio **1.89x** [1.41, 2.29], A worse in 79.2%; median L∞ ratio 0.976.
- tau=0.0001 e, SPERR/ZFP, <= 0.075 dex: 51 pairs / 36 materials; QoI ratio **1.82x** [1.45, 2.26], A worse in 80.6%; median L∞ ratio 0.969.
- tau=0.0001 e, SPERR/ZFP, <= 0.100 dex: 75 pairs / 40 materials; QoI ratio **1.91x** [1.63, 2.22], A worse in 82.5%; median L∞ ratio 0.920.
- tau=0.0001 e, SPERR/ZFP, <= 0.150 dex: 161 pairs / 46 materials; QoI ratio **1.97x** [1.75, 2.20], A worse in 89.1%; median L∞ ratio 0.877.
- tau=0.001 e, SZ3/ZFP, <= 0.050 dex: 88 pairs / 69 materials; QoI ratio **1.74x** [1.55, 2.00], A worse in 82.6%; median L∞ ratio 0.978.
- tau=0.001 e, SZ3/ZFP, <= 0.075 dex: 141 pairs / 100 materials; QoI ratio **1.83x** [1.66, 2.08], A worse in 88.0%; median L∞ ratio 0.970.
- tau=0.001 e, SZ3/ZFP, <= 0.100 dex: 232 pairs / 124 materials; QoI ratio **1.82x** [1.68, 2.03], A worse in 91.1%; median L∞ ratio 0.965.
- tau=0.001 e, SZ3/ZFP, <= 0.150 dex: 492 pairs / 143 materials; QoI ratio **1.85x** [1.74, 2.00], A worse in 96.5%; median L∞ ratio 0.947.
- tau=0.001 e, SPERR/ZFP, <= 0.050 dex: 84 pairs / 65 materials; QoI ratio **1.99x** [1.49, 2.48], A worse in 80.0%; median L∞ ratio 0.975.
- tau=0.001 e, SPERR/ZFP, <= 0.075 dex: 131 pairs / 94 materials; QoI ratio **2.00x** [1.76, 2.29], A worse in 83.0%; median L∞ ratio 0.970.
- tau=0.001 e, SPERR/ZFP, <= 0.100 dex: 217 pairs / 119 materials; QoI ratio **2.01x** [1.84, 2.38], A worse in 82.4%; median L∞ ratio 0.971.
- tau=0.001 e, SPERR/ZFP, <= 0.150 dex: 477 pairs / 141 materials; QoI ratio **2.11x** [1.89, 2.27], A worse in 90.8%; median L∞ ratio 0.971.
- tau=0.01 e, SZ3/ZFP, <= 0.050 dex: 140 pairs / 110 materials; QoI ratio **1.72x** [1.57, 1.86], A worse in 86.4%; median L∞ ratio 0.976.
- tau=0.01 e, SZ3/ZFP, <= 0.075 dex: 218 pairs / 157 materials; QoI ratio **1.72x** [1.59, 1.86], A worse in 87.9%; median L∞ ratio 0.962.
- tau=0.01 e, SZ3/ZFP, <= 0.100 dex: 346 pairs / 193 materials; QoI ratio **1.78x** [1.68, 1.93], A worse in 90.2%; median L∞ ratio 0.946.
- tau=0.01 e, SZ3/ZFP, <= 0.150 dex: 680 pairs / 223 materials; QoI ratio **1.79x** [1.70, 1.88], A worse in 94.6%; median L∞ ratio 0.906.
- tau=0.01 e, SPERR/ZFP, <= 0.050 dex: 131 pairs / 101 materials; QoI ratio **1.99x** [1.75, 2.43], A worse in 84.2%; median L∞ ratio 0.969.
- tau=0.01 e, SPERR/ZFP, <= 0.075 dex: 204 pairs / 146 materials; QoI ratio **1.87x** [1.74, 2.14], A worse in 81.5%; median L∞ ratio 0.957.
- tau=0.01 e, SPERR/ZFP, <= 0.100 dex: 326 pairs / 185 materials; QoI ratio **1.88x** [1.74, 2.05], A worse in 80.0%; median L∞ ratio 0.935.
- tau=0.01 e, SPERR/ZFP, <= 0.150 dex: 655 pairs / 222 materials; QoI ratio **1.88x** [1.74, 2.09], A worse in 85.1%; median L∞ ratio 0.907.

## 3. Within-material log-log interpolation on common realized-Linf support

- tau=0.0001 e, SZ3/ZFP: 46 materials; interpolated QoI ratio **2.37x** [2.08, 2.86], A worse in 100.0%.
- tau=0.0001 e, SPERR/ZFP: 46 materials; interpolated QoI ratio **2.00x** [1.72, 2.27], A worse in 93.5%.
- tau=0.001 e, SZ3/ZFP: 143 materials; interpolated QoI ratio **2.08x** [1.96, 2.16], A worse in 97.2%.
- tau=0.001 e, SPERR/ZFP: 143 materials; interpolated QoI ratio **2.04x** [1.88, 2.21], A worse in 95.1%.
- tau=0.01 e, SZ3/ZFP: 225 materials; interpolated QoI ratio **1.95x** [1.79, 2.08], A worse in 95.6%.
- tau=0.01 e, SPERR/ZFP: 226 materials; interpolated QoI ratio **1.92x** [1.79, 2.05], A worse in 88.9%.

## 4. Mechanism attenuation after adding basin-reassignment and fixed-basin terms

- M1_plus_reassignment: reassignment coefficient beta=0.840 log10-Q per log10 reassigned-fraction [95% 0.691, 0.988].
- M2_plus_reassignment_fixed: reassignment coefficient beta=0.842 log10-Q per log10 reassigned-fraction [95% 0.694, 0.989].
- Regression common realized-L∞ support: [1e-05, 25], 4218 rows / 143 materials.
- SZ3/ZFP codec effect: M0 **2.32x** -> +reassignment **0.98x** -> +reassignment+fixed-basin **0.92x**.
- SPERR/ZFP codec effect: M0 **2.10x** -> +reassignment **0.95x** -> +reassignment+fixed-basin **0.94x**.

## 5. Fixed-basin metric directionality

- Among 4627 successful base-ladder rows, resolved error exceeds fixed-basin error in **99.7%** of rows.
- SPERR: median resolved/fixed ratio **100.1x** [90.4, 112.1], resolved > fixed in 99.9%.
- SZ3: median resolved/fixed ratio **8.0x** [7.0, 8.6], resolved > fixed in 99.2%.
- ZFP: median resolved/fixed ratio **106.9x** [99.2, 120.1], resolved > fixed in 99.9%.
