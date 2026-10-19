# Deployment cost — results

Materials: 92; runner CPUs: AMD EPYC 7763 64-Core Processor, AMD EPYC 9V45 96-Core Processor, AMD EPYC 9V74 80-Core Processor, INTEL(R) XEON(R) PLATINUM 8573C, Intel(R) Xeon(R) 6973P-C, Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz.

Reproduction: streams = 1927, certified = 1898, bytes_equal_recorded = 1171, max_abs_byte_difference = 26338.0, search_param_mismatch = 0.

## P1_CONFIRMATORY, τ = 0.0001

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 818 [679, 933] | 0.0804 [0.0574, 0.103] | n/a | 0.0389 [0.0317, 0.052] | 188 [185, 202] | 3.88 [3.85, 3.92] | 5.03 [5.03, 5.04] | 0.039 [0.0318, 0.0522] |
| law, reference implementation | 818 [679, 933] | 0.0862 [0.0639, 0.119] | n/a | 0.104 [0.0757, 0.134] | 75.9 [72.4, 78.5] | 6.95 [6.62, 6.98] | 11.5 [10.7, 11.6] | 0.105 [0.0758, 0.134] |
| operational optimum (A3) | 1.3e+03 [1.09e+03, 1.48e+03] | 3.47 [2.77, 5.1] | n/a | 0.0243 [0.0185, 0.0321] | 310 [301, 318] | 4.16 [3.96, 4.46] | 3.43 [3.37, 3.48] | 0.0244 [0.0186, 0.0323] |
| A3, reference implementation | 1.3e+03 [1.09e+03, 1.48e+03] | 3.49 [2.74, 5.1] | n/a | 0.0822 [0.0629, 0.11] | 88.5 [85.6, 93.1] | 4.46 [4.27, 4.48] | 11.5 [11.5, 11.5] | 0.0822 [0.063, 0.11] |
| best of ZFP/SZ3/SPERR (A6) | 79.2 [67.3, 126] | 0.0274 [0.0211, 0.0386] | n/a | 0.0113 [0.00816, 0.0153] | 901 [745, 1.02e+03] | 2.84 [2.22, 3.64] | 3.49 [3.17, 3.61] | 0.0122 [0.00861, 0.0173] |
| MGARD s=-2 | 59.2 [52.7, 68.4] | 0.18 [0.144, 0.264] | n/a | 0.169 [0.132, 0.246] | 44.1 [42.7, 46.8] | 0 [0, 0] | 3 [2.99, 3] | 0.17 [0.133, 0.246] |
| QPET (best of 9) | 155 [136, 175] | 0.1 [0.0817, 0.129] | n/a | 0.0374 [0.03, 0.0457] | 231 [219, 246] | 0.00508 [0, 0.0079] | 3 [2.99, 3] | 0.0379 [0.0306, 0.0463] |
| float64+zlib-6 | 1.09 [1.07, 1.16] | 0.228 [0.184, 0.321] | n/a | 0.0301 [0.0234, 0.0397] | 281 [252, 330] | 3.77 [3.62, 3.81] | 3.05 [3.02, 3.08] | 0.0887 [0.0734, 0.122] |
| float64+zstd-3 | 1.26 [1.19, 1.45] | 0.015 [0.0126, 0.0229] | n/a | 0.00712 [0.00449, 0.00933] | 1.33e+03 [1.16e+03, 1.59e+03] | 2.96 [2.91, 3.03] | 2 [2, 2] | 0.0589 [0.049, 0.0846] |
| source file as archived | 0.555 [0.549, 0.563] | n/a | n/a | 0.609 [0.528, 0.785] | 13.6 [13.5, 13.8] | n/a | n/a | 0.745 [0.621, 0.939] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.0669 [0.0566, 0.0899] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.13 [1.1, 1.23], n=60, A1 lower in 57
- encode: operational optimum (A3) 49.1 [44.4, 55.4], n=60, A1 lower in 60
- encode: A3, reference implementation 49 [44.5, 55.2], n=60, A1 lower in 60
- encode: best of ZFP/SZ3/SPERR (A6) 0.297 [0.264, 0.357], n=60, A1 lower in 0
- encode: float64+zlib-6 2.96 [2.74, 3.12], n=60, A1 lower in 59
- encode: float64+zstd-3 0.155 [0.145, 0.195], n=60, A1 lower in 0
- encode: MGARD s=-2 2.36 [2.3, 2.5], n=60, A1 lower in 60
- encode: QPET (best of 9) 1.25 [1.22, 1.37], n=59, A1 lower in 53
- decode: law, reference implementation 2.61 [2.51, 2.73], n=60, A1 lower in 60
- decode: operational optimum (A3) 0.615 [0.606, 0.626], n=60, A1 lower in 0
- decode: A3, reference implementation 2.1 [2.04, 2.2], n=60, A1 lower in 60
- decode: best of ZFP/SZ3/SPERR (A6) 0.223 [0.193, 0.257], n=60, A1 lower in 0
- decode: float64+zlib-6 0.733 [0.716, 0.745], n=60, A1 lower in 2
- decode: float64+zstd-3 0.161 [0.153, 0.173], n=60, A1 lower in 0
- decode: MGARD s=-2 4.33 [4.17, 4.48], n=60, A1 lower in 60
- decode: QPET (best of 9) 0.906 [0.85, 0.943], n=59, A1 lower in 16
- decode: raw float64 0 [0, 0], n=60, A1 lower in 0
- decode: source file as archived 13.8 [13.7, 14.2], n=60, A1 lower in 60
- ttf_0.1Gbps: law, reference implementation 2.55 [2.46, 2.69], n=60, A1 lower in 60
- ttf_0.1Gbps: operational optimum (A3) 0.617 [0.609, 0.625], n=60, A1 lower in 0
- ttf_0.1Gbps: A3, reference implementation 2.08 [2, 2.17], n=60, A1 lower in 60
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 0.477 [0.446, 0.532], n=60, A1 lower in 0
- ttf_0.1Gbps: float64+zlib-6 14.1 [13.6, 14.5], n=60, A1 lower in 60
- ttf_0.1Gbps: float64+zstd-3 12.1 [11.3, 13.4], n=60, A1 lower in 60
- ttf_0.1Gbps: MGARD s=-2 4.51 [4.35, 4.67], n=60, A1 lower in 60
- ttf_0.1Gbps: QPET (best of 9) 0.984 [0.922, 1.03], n=59, A1 lower in 25
- ttf_0.1Gbps: raw float64 14.8 [14.6, 15.7], n=60, A1 lower in 60
- ttf_0.1Gbps: source file as archived 40.1 [39.2, 41.4], n=60, A1 lower in 60
- ttf_1Gbps: law, reference implementation 2.6 [2.5, 2.73], n=60, A1 lower in 60
- ttf_1Gbps: operational optimum (A3) 0.615 [0.606, 0.626], n=60, A1 lower in 0
- ttf_1Gbps: A3, reference implementation 2.1 [2.04, 2.2], n=60, A1 lower in 60
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.256 [0.221, 0.291], n=60, A1 lower in 0
- ttf_1Gbps: float64+zlib-6 2.08 [2.03, 2.13], n=60, A1 lower in 58
- ttf_1Gbps: float64+zstd-3 1.39 [1.29, 1.52], n=60, A1 lower in 43
- ttf_1Gbps: MGARD s=-2 4.35 [4.2, 4.49], n=60, A1 lower in 60
- ttf_1Gbps: QPET (best of 9) 0.914 [0.858, 0.951], n=59, A1 lower in 17
- ttf_1Gbps: raw float64 1.5 [1.48, 1.62], n=60, A1 lower in 60
- ttf_1Gbps: source file as archived 16.6 [16.2, 16.9], n=60, A1 lower in 60
- ttf_10Gbps: law, reference implementation 2.6 [2.51, 2.73], n=60, A1 lower in 60
- ttf_10Gbps: operational optimum (A3) 0.615 [0.606, 0.626], n=60, A1 lower in 0
- ttf_10Gbps: A3, reference implementation 2.1 [2.04, 2.2], n=60, A1 lower in 60
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.225 [0.196, 0.261], n=60, A1 lower in 0
- ttf_10Gbps: float64+zlib-6 0.873 [0.851, 0.884], n=60, A1 lower in 12
- ttf_10Gbps: float64+zstd-3 0.287 [0.262, 0.31], n=60, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 4.33 [4.17, 4.48], n=60, A1 lower in 60
- ttf_10Gbps: QPET (best of 9) 0.907 [0.851, 0.943], n=59, A1 lower in 16
- ttf_10Gbps: raw float64 0.151 [0.148, 0.162], n=60, A1 lower in 0
- ttf_10Gbps: source file as archived 14 [13.9, 14.5], n=60, A1 lower in 60

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/60); best of ZFP/SZ3/SPERR (A6) 0.0255 Gbit/s (A1 smaller and faster in 0/60); float64+zlib-6 5.12 Gbit/s (A1 smaller and faster in 2/60); float64+zstd-3 1.48 Gbit/s (A1 smaller and faster in 0/60); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 60/60); QPET (best of 9) 0.0803 Gbit/s (A1 smaller and faster in 16/59); raw float64 1.51 Gbit/s (A1 smaller and faster in 0/60); source file as archived inf Gbit/s (A1 smaller and faster in 60/60)

Fastest to a usable field: 0.1Gbps: A1 0/60 ({'A6': 52, 'A3': 8}); 1Gbps: A1 0/60 ({'A6': 57, 'L_zstd': 3}); 10Gbps: A1 0/60 ({'RAW': 42, 'A6': 11, 'L_zstd': 7})

## P1_CONFIRMATORY, τ = 1e-06

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 195 [161, 231] | 0.0698 [0.0594, 0.102] | 0.382 [0.279, 0.51] | 0.0401 [0.0313, 0.053] | 189 [186, 201] | 6.12 [6.1, 6.16] | 5.04 [5.03, 5.04] | 0.0404 [0.0316, 0.0542] |
| law, reference implementation | 195 [161, 231] | 0.0942 [0.0687, 0.131] | n/a | 0.106 [0.077, 0.135] | 75.5 [71.9, 78.7] | 6.92 [6.6, 8.45] | 11.5 [10.5, 11.6] | 0.106 [0.0771, 0.137] |
| operational optimum (A3) | 224 [179, 285] | 3.47 [2.82, 5.13] | 3.63 [2.91, 5.26] | 0.0264 [0.0214, 0.0369] | 283 [273, 294] | 4.31 [3.98, 4.48] | 4.04 [3.94, 4.18] | 0.0265 [0.0224, 0.0376] |
| A3, reference implementation | 224 [179, 285] | 3.48 [2.79, 5.11] | n/a | 0.0875 [0.0649, 0.107] | 87 [82.8, 95.4] | 4.44 [4.18, 4.48] | 11.5 [11.1, 11.5] | 0.0878 [0.065, 0.108] |
| best of ZFP/SZ3/SPERR (A6) | 16 [14.8, 20.2] | 0.0331 [0.0244, 0.0396] | 18.1 [15.3, 24.8] | 0.0188 [0.0139, 0.0235] | 633 [441, 746] | 0.483 [0.311, 4.13] | 2 [2, 3.86] | 0.0241 [0.0181, 0.0309] |
| MGARD s=-2 | 10.2 [9.66, 10.6] | 0.188 [0.145, 0.27] | 17.9 [14.6, 26.3] | 0.189 [0.154, 0.273] | 38.7 [37.6, 42.4] | 0.0108 [0.00664, 0.0158] | 3 [3, 3] | 0.194 [0.16, 0.285] |
| QPET (best of 9) | 29.4 [25, 31.1] | 0.132 [0.108, 0.166] | 91.2 [74.3, 132] | 0.0574 [0.0474, 0.066] | 138 [130, 149] | 0.00862 [0.00508, 0.0138] | 3 [2.99, 3] | 0.0599 [0.0494, 0.0681] |
| float64+zlib-6 | 1.09 [1.07, 1.16] | 0.228 [0.184, 0.321] | n/a | 0.0301 [0.0234, 0.0397] | 281 [252, 330] | 3.77 [3.62, 3.81] | 3.05 [3.02, 3.08] | 0.0887 [0.0734, 0.122] |
| float64+zstd-3 | 1.26 [1.19, 1.45] | 0.015 [0.0126, 0.0229] | n/a | 0.00712 [0.00449, 0.00933] | 1.33e+03 [1.16e+03, 1.59e+03] | 2.96 [2.91, 3.03] | 2 [2, 2] | 0.0589 [0.049, 0.0846] |
| source file as archived | 0.555 [0.549, 0.563] | n/a | n/a | 0.609 [0.528, 0.785] | 13.6 [13.5, 13.8] | n/a | n/a | 0.745 [0.621, 0.939] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.0669 [0.0566, 0.0899] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.3 [1.26, 1.34], n=60, A1 lower in 59
- encode: operational optimum (A3) 50.9 [45.3, 55.7], n=60, A1 lower in 60
- encode: A3, reference implementation 51.2 [45.5, 56.1], n=60, A1 lower in 60
- encode: best of ZFP/SZ3/SPERR (A6) 0.283 [0.246, 0.426], n=60, A1 lower in 2
- encode: float64+zlib-6 3.01 [2.74, 3.19], n=60, A1 lower in 59
- encode: float64+zstd-3 0.185 [0.154, 0.204], n=60, A1 lower in 0
- encode: MGARD s=-2 2.58 [2.36, 2.76], n=60, A1 lower in 60
- encode: QPET (best of 9) 1.8 [1.69, 1.96], n=60, A1 lower in 59
- search: operational optimum (A3) 9.27 [8.23, 10.5], n=60, A1 lower in 60
- search: best of ZFP/SZ3/SPERR (A6) 46.9 [43.1, 53.2], n=60, A1 lower in 60
- search: MGARD s=-2 48.5 [45.3, 50.1], n=60, A1 lower in 60
- search: QPET (best of 9) 228 [213, 257], n=60, A1 lower in 60
- decode: law, reference implementation 2.63 [2.54, 2.74], n=60, A1 lower in 60
- decode: operational optimum (A3) 0.693 [0.682, 0.705], n=60, A1 lower in 0
- decode: A3, reference implementation 2.19 [2.11, 2.3], n=60, A1 lower in 60
- decode: best of ZFP/SZ3/SPERR (A6) 0.354 [0.266, 0.445], n=60, A1 lower in 11
- decode: float64+zlib-6 0.728 [0.702, 0.746], n=60, A1 lower in 3
- decode: float64+zstd-3 0.159 [0.153, 0.171], n=60, A1 lower in 0
- decode: MGARD s=-2 4.92 [4.83, 5.14], n=60, A1 lower in 60
- decode: QPET (best of 9) 1.44 [1.37, 1.54], n=60, A1 lower in 60
- decode: raw float64 0 [0, 0], n=60, A1 lower in 0
- decode: source file as archived 13.9 [13.7, 14.2], n=60, A1 lower in 60
- ttf_0.1Gbps: law, reference implementation 2.51 [2.39, 2.56], n=60, A1 lower in 60
- ttf_0.1Gbps: operational optimum (A3) 0.711 [0.697, 0.731], n=60, A1 lower in 0
- ttf_0.1Gbps: A3, reference implementation 2.08 [2.02, 2.15], n=60, A1 lower in 60
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 1.32 [1.23, 1.43], n=60, A1 lower in 55
- ttf_0.1Gbps: float64+zlib-6 13.2 [12.4, 13.5], n=60, A1 lower in 60
- ttf_0.1Gbps: float64+zstd-3 11.4 [9.94, 12.1], n=60, A1 lower in 60
- ttf_0.1Gbps: MGARD s=-2 5.88 [5.75, 6.14], n=60, A1 lower in 60
- ttf_0.1Gbps: QPET (best of 9) 1.85 [1.74, 2], n=60, A1 lower in 60
- ttf_0.1Gbps: raw float64 14.1 [13.7, 15], n=60, A1 lower in 60
- ttf_0.1Gbps: source file as archived 37.8 [36.9, 39.3], n=60, A1 lower in 60
- ttf_1Gbps: law, reference implementation 2.62 [2.53, 2.72], n=60, A1 lower in 60
- ttf_1Gbps: operational optimum (A3) 0.694 [0.683, 0.708], n=60, A1 lower in 0
- ttf_1Gbps: A3, reference implementation 2.18 [2.11, 2.26], n=60, A1 lower in 60
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.467 [0.395, 0.579], n=60, A1 lower in 12
- ttf_1Gbps: float64+zlib-6 2.06 [1.98, 2.13], n=60, A1 lower in 58
- ttf_1Gbps: float64+zstd-3 1.38 [1.21, 1.5], n=60, A1 lower in 44
- ttf_1Gbps: MGARD s=-2 5.06 [4.93, 5.19], n=60, A1 lower in 60
- ttf_1Gbps: QPET (best of 9) 1.49 [1.4, 1.59], n=60, A1 lower in 60
- ttf_1Gbps: raw float64 1.49 [1.47, 1.6], n=60, A1 lower in 60
- ttf_1Gbps: source file as archived 16.5 [16, 17], n=60, A1 lower in 60
- ttf_10Gbps: law, reference implementation 2.63 [2.54, 2.74], n=60, A1 lower in 60
- ttf_10Gbps: operational optimum (A3) 0.694 [0.682, 0.705], n=60, A1 lower in 0
- ttf_10Gbps: A3, reference implementation 2.19 [2.11, 2.3], n=60, A1 lower in 60
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.362 [0.279, 0.456], n=60, A1 lower in 11
- ttf_10Gbps: float64+zlib-6 0.861 [0.833, 0.886], n=60, A1 lower in 12
- ttf_10Gbps: float64+zstd-3 0.282 [0.264, 0.306], n=60, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 4.94 [4.84, 5.15], n=60, A1 lower in 60
- ttf_10Gbps: QPET (best of 9) 1.45 [1.37, 1.55], n=60, A1 lower in 60
- ttf_10Gbps: raw float64 0.151 [0.148, 0.16], n=60, A1 lower in 0
- ttf_10Gbps: source file as archived 14.2 [14, 14.5], n=60, A1 lower in 60

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/60); best of ZFP/SZ3/SPERR (A6) 0.171 Gbit/s (A1 smaller and faster in 11/60); float64+zlib-6 4.84 Gbit/s (A1 smaller and faster in 3/60); float64+zstd-3 1.46 Gbit/s (A1 smaller and faster in 0/60); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 60/60); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 60/60); raw float64 1.5 Gbit/s (A1 smaller and faster in 0/60); source file as archived inf Gbit/s (A1 smaller and faster in 60/60)

Fastest to a usable field: 0.1Gbps: A1 0/60 ({'A3': 59, 'A6': 1}); 1Gbps: A1 0/60 ({'A6': 36, 'A3': 19, 'L_zstd': 5}); 10Gbps: A1 0/60 ({'RAW': 52, 'L_zstd': 8})

## P1_CONFIRMATORY, τ = 1e-08

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 24.6 [20.9, 29.3] | 0.117 [0.0967, 0.168] | n/a | 0.0413 [0.0343, 0.0561] | 183 [180, 194] | 4.97 [4.8, 6.67] | 5.04 [5.03, 5.04] | 0.0425 [0.0361, 0.0621] |
| law, reference implementation | 24.6 [20.9, 29.3] | 0.141 [0.114, 0.195] | n/a | 0.104 [0.0801, 0.142] | 74.1 [71.3, 77.3] | 6.97 [6.86, 6.99] | 11.6 [11.2, 11.6] | 0.107 [0.0812, 0.151] |
| operational optimum (A3) | 25 [21.3, 30.6] | 3.53 [2.77, 5.19] | n/a | 0.0412 [0.0361, 0.0548] | 181 [161, 189] | 4.47 [4.09, 4.85] | 5.01 [5, 5.02] | 0.0437 [0.039, 0.057] |
| A3, reference implementation | 25 [21.3, 30.6] | 3.54 [2.77, 5.19] | n/a | 0.0966 [0.0772, 0.128] | 75.8 [72.4, 81] | 4.48 [4.46, 4.48] | 11.5 [11.2, 11.5] | 0.0986 [0.0807, 0.135] |
| best of ZFP/SZ3/SPERR (A6) | 7.12 [6.62, 7.98] | 0.0458 [0.0305, 0.0586] | n/a | 0.0297 [0.0203, 0.0362] | 482 [343, 505] | 0.804 [0.614, 4.47] | 2 [2, 4.16] | 0.041 [0.029, 0.0546] |
| MGARD s=-2 | 5.05 [4.93, 5.19] | 0.2 [0.158, 0.279] | n/a | 0.251 [0.207, 0.338] | 29.9 [28.2, 32.3] | 0.0118 [0.00638, 0.0164] | 3 [2.99, 3] | 0.262 [0.218, 0.361] |
| QPET (best of 9) | 9.97 [9.14, 10.6] | 0.185 [0.152, 0.221] | n/a | 0.0982 [0.0847, 0.116] | 80 [77.9, 92.5] | 0.0125 [0.00657, 0.0185] | 3 [3, 3] | 0.105 [0.09, 0.124] |
| float64+zlib-6 | 1.09 [1.07, 1.16] | 0.228 [0.184, 0.321] | n/a | 0.0301 [0.0234, 0.0397] | 281 [252, 330] | 3.77 [3.62, 3.81] | 3.05 [3.02, 3.08] | 0.0887 [0.0734, 0.122] |
| float64+zstd-3 | 1.26 [1.19, 1.45] | 0.015 [0.0126, 0.0229] | n/a | 0.00712 [0.00449, 0.00933] | 1.33e+03 [1.16e+03, 1.59e+03] | 2.96 [2.91, 3.03] | 2 [2, 2] | 0.0589 [0.049, 0.0846] |
| source file as archived | 0.555 [0.549, 0.563] | n/a | n/a | 0.609 [0.528, 0.785] | 13.6 [13.5, 13.8] | n/a | n/a | 0.745 [0.621, 0.939] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.0669 [0.0566, 0.0899] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.15 [1.13, 1.19], n=60, A1 lower in 60
- encode: operational optimum (A3) 29.1 [27.9, 30.9], n=60, A1 lower in 60
- encode: A3, reference implementation 29.3 [27.9, 31.1], n=60, A1 lower in 60
- encode: best of ZFP/SZ3/SPERR (A6) 0.21 [0.179, 0.36], n=60, A1 lower in 7
- encode: float64+zlib-6 1.61 [1.51, 1.72], n=60, A1 lower in 58
- encode: float64+zstd-3 0.104 [0.0827, 0.138], n=60, A1 lower in 0
- encode: MGARD s=-2 1.54 [1.46, 1.65], n=60, A1 lower in 59
- encode: QPET (best of 9) 1.32 [1.24, 1.45], n=60, A1 lower in 53
- decode: law, reference implementation 2.6 [2.49, 2.7], n=60, A1 lower in 60
- decode: operational optimum (A3) 1.13 [1.08, 1.15], n=60, A1 lower in 45
- decode: A3, reference implementation 2.41 [2.36, 2.55], n=60, A1 lower in 60
- decode: best of ZFP/SZ3/SPERR (A6) 0.418 [0.371, 0.577], n=60, A1 lower in 21
- decode: float64+zlib-6 0.695 [0.673, 0.72], n=60, A1 lower in 2
- decode: float64+zstd-3 0.158 [0.148, 0.163], n=60, A1 lower in 0
- decode: MGARD s=-2 6.33 [6.1, 6.6], n=60, A1 lower in 60
- decode: QPET (best of 9) 2.37 [2.27, 2.55], n=60, A1 lower in 57
- decode: raw float64 0 [0, 0], n=60, A1 lower in 0
- decode: source file as archived 13.6 [13.1, 13.8], n=60, A1 lower in 60
- ttf_0.1Gbps: law, reference implementation 1.98 [1.93, 2.03], n=60, A1 lower in 60
- ttf_0.1Gbps: operational optimum (A3) 1.05 [1.03, 1.06], n=60, A1 lower in 42
- ttf_0.1Gbps: A3, reference implementation 1.88 [1.81, 1.94], n=60, A1 lower in 60
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 1.71 [1.58, 1.93], n=60, A1 lower in 59
- ttf_0.1Gbps: float64+zlib-6 8.01 [6.6, 9.01], n=60, A1 lower in 60
- ttf_0.1Gbps: float64+zstd-3 6.08 [5.38, 7.6], n=60, A1 lower in 59
- ttf_0.1Gbps: MGARD s=-2 5.65 [5.44, 6.04], n=60, A1 lower in 60
- ttf_0.1Gbps: QPET (best of 9) 2.27 [2.11, 2.44], n=60, A1 lower in 60
- ttf_0.1Gbps: raw float64 9.71 [9.02, 10.6], n=60, A1 lower in 60
- ttf_0.1Gbps: source file as archived 24.4 [22.1, 27.5], n=60, A1 lower in 60
- ttf_1Gbps: law, reference implementation 2.47 [2.4, 2.57], n=60, A1 lower in 60
- ttf_1Gbps: operational optimum (A3) 1.12 [1.07, 1.14], n=60, A1 lower in 44
- ttf_1Gbps: A3, reference implementation 2.32 [2.27, 2.41], n=60, A1 lower in 60
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.651 [0.572, 0.845], n=60, A1 lower in 21
- ttf_1Gbps: float64+zlib-6 1.86 [1.75, 1.98], n=60, A1 lower in 58
- ttf_1Gbps: float64+zstd-3 1.27 [1.07, 1.33], n=60, A1 lower in 39
- ttf_1Gbps: MGARD s=-2 6.16 [5.99, 6.42], n=60, A1 lower in 60
- ttf_1Gbps: QPET (best of 9) 2.36 [2.28, 2.48], n=60, A1 lower in 57
- ttf_1Gbps: raw float64 1.4 [1.36, 1.48], n=60, A1 lower in 60
- ttf_1Gbps: source file as archived 15.4 [14.6, 15.8], n=60, A1 lower in 60
- ttf_10Gbps: law, reference implementation 2.59 [2.48, 2.68], n=60, A1 lower in 60
- ttf_10Gbps: operational optimum (A3) 1.13 [1.08, 1.15], n=60, A1 lower in 44
- ttf_10Gbps: A3, reference implementation 2.39 [2.34, 2.54], n=60, A1 lower in 60
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.448 [0.392, 0.611], n=60, A1 lower in 21
- ttf_10Gbps: float64+zlib-6 0.821 [0.795, 0.853], n=60, A1 lower in 10
- ttf_10Gbps: float64+zstd-3 0.277 [0.24, 0.287], n=60, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 6.31 [6.1, 6.59], n=60, A1 lower in 60
- ttf_10Gbps: QPET (best of 9) 2.37 [2.27, 2.54], n=60, A1 lower in 57
- ttf_10Gbps: raw float64 0.146 [0.143, 0.152], n=60, A1 lower in 0
- ttf_10Gbps: source file as archived 13.7 [13.2, 14], n=60, A1 lower in 60

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/60); best of ZFP/SZ3/SPERR (A6) 0.307 Gbit/s (A1 smaller and faster in 21/60); float64+zlib-6 3.95 Gbit/s (A1 smaller and faster in 2/60); float64+zstd-3 1.35 Gbit/s (A1 smaller and faster in 0/60); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 60/60); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 57/60); raw float64 1.42 Gbit/s (A1 smaller and faster in 0/60); source file as archived inf Gbit/s (A1 smaller and faster in 60/60)

Fastest to a usable field: 0.1Gbps: A1 40/60 ({'A1': 40, 'A3': 18, 'L_zstd': 1, 'A6': 1}); 1Gbps: A1 8/60 ({'A6': 32, 'L_zstd': 11, 'A3': 9, 'A1': 8}); 10Gbps: A1 0/60 ({'RAW': 52, 'L_zstd': 8})

## P3B_CONFIRMATORY, τ = 0.0001

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 1.77e+03 [1.43e+03, 1.97e+03] | 0.121 [0.102, 0.143] | n/a | 0.0666 [0.0487, 0.076] | 189 [187, 233] | 3.92 [3.86, 5.83] | 5.01 [5.01, 5.02] | 0.0667 [0.0488, 0.0761] |
| law, reference implementation | 1.77e+03 [1.43e+03, 1.97e+03] | 0.156 [0.119, 0.169] | n/a | 0.17 [0.14, 0.195] | 81.1 [75.8, 88] | 8.47 [6.59, 8.56] | 11.7 [10.2, 11.9] | 0.171 [0.14, 0.195] |
| operational optimum (A3) | 3.55e+03 [2.7e+03, 4.11e+03] | 2.85 [1.74, 3.69] | n/a | 0.0403 [0.03, 0.0452] | 315 [311, 378] | 4.3 [3.49, 4.48] | 3.35 [3.31, 3.38] | 0.0403 [0.03, 0.0453] |
| A3, reference implementation | 3.55e+03 [2.7e+03, 4.11e+03] | 2.83 [1.75, 3.7] | n/a | 0.145 [0.107, 0.162] | 91.4 [86.9, 113] | 4.48 [4.26, 4.94] | 11.5 [10, 12] | 0.145 [0.107, 0.162] |
| best of ZFP/SZ3/SPERR (A6) | 108 [100, 120] | 0.0174 [0.0104, 0.0271] | n/a | 0.00764 [0.00544, 0.0112] | 1.91e+03 [1.32e+03, 2.38e+03] | 0.175 [0.0234, 1.91] | 2 [2, 2.83] | 0.009 [0.00676, 0.0127] |
| MGARD s=-2 | 196 [173, 264] | 0.296 [0.227, 0.339] | n/a | 0.282 [0.209, 0.311] | 46.4 [44.9, 56.3] | 0 [0, 0.00683] | 3 [2.99, 3] | 0.283 [0.21, 0.312] |
| QPET (best of 9) | 258 [199, 292] | 0.175 [0.151, 0.196] | n/a | 0.0596 [0.0546, 0.067] | 247 [231, 274] | 0.00791 [0.00542, 0.00988] | 3 [3, 3] | 0.0605 [0.0551, 0.0676] |
| float64+zlib-6 | 1.05 [1.05, 1.06] | 0.32 [0.281, 0.392] | n/a | 0.0435 [0.039, 0.0525] | 295 [254, 332] | 3.86 [3.8, 3.9] | 3 [2.98, 3.03] | 0.139 [0.119, 0.165] |
| float64+zstd-3 | 1.05 [1.05, 1.17] | 0.0161 [0.0134, 0.0194] | n/a | 0.00804 [0.00667, 0.0122] | 1.4e+03 [1.08e+03, 1.76e+03] | 3.05 [2.97, 3.12] | 2 [2, 2] | 0.104 [0.0623, 0.127] |
| source file as archived | 0.439 [0.439, 0.578] | n/a | n/a | 0.295 [0.274, 0.438] | 39.9 [35.7, 48.5] | n/a | n/a | 0.543 [0.523, 0.689] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.113 [0.106, 0.126] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.19 [1.15, 1.3], n=32, A1 lower in 30
- encode: operational optimum (A3) 25.9 [18.9, 30], n=32, A1 lower in 32
- encode: A3, reference implementation 25.5 [19.4, 30.1], n=32, A1 lower in 32
- encode: best of ZFP/SZ3/SPERR (A6) 0.1 [0.0864, 0.242], n=32, A1 lower in 0
- encode: float64+zlib-6 2.91 [2.63, 3.04], n=32, A1 lower in 32
- encode: float64+zstd-3 0.141 [0.127, 0.151], n=32, A1 lower in 0
- encode: MGARD s=-2 2.25 [2.1, 2.43], n=32, A1 lower in 32
- encode: QPET (best of 9) 1.44 [1.3, 1.53], n=28, A1 lower in 22
- decode: law, reference implementation 2.62 [2.52, 2.87], n=32, A1 lower in 32
- decode: operational optimum (A3) 0.604 [0.596, 0.612], n=32, A1 lower in 0
- decode: A3, reference implementation 2.13 [2.09, 2.27], n=32, A1 lower in 32
- decode: best of ZFP/SZ3/SPERR (A6) 0.107 [0.0864, 0.159], n=32, A1 lower in 0
- decode: float64+zlib-6 0.744 [0.707, 0.808], n=32, A1 lower in 2
- decode: float64+zstd-3 0.17 [0.146, 0.175], n=32, A1 lower in 0
- decode: MGARD s=-2 4.12 [4.05, 4.23], n=32, A1 lower in 32
- decode: QPET (best of 9) 0.857 [0.787, 0.961], n=28, A1 lower in 7
- decode: raw float64 0 [0, 0], n=32, A1 lower in 0
- decode: source file as archived 5.31 [3.86, 6.5], n=32, A1 lower in 32
- ttf_0.1Gbps: law, reference implementation 2.59 [2.51, 2.85], n=32, A1 lower in 32
- ttf_0.1Gbps: operational optimum (A3) 0.603 [0.595, 0.612], n=32, A1 lower in 0
- ttf_0.1Gbps: A3, reference implementation 2.11 [2.07, 2.25], n=32, A1 lower in 32
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 0.311 [0.242, 0.387], n=32, A1 lower in 0
- ttf_0.1Gbps: float64+zlib-6 15 [14.1, 16.5], n=32, A1 lower in 32
- ttf_0.1Gbps: float64+zstd-3 14 [12.2, 14.8], n=32, A1 lower in 32
- ttf_0.1Gbps: MGARD s=-2 4.18 [4.05, 4.34], n=32, A1 lower in 32
- ttf_0.1Gbps: QPET (best of 9) 0.941 [0.822, 1.01], n=28, A1 lower in 10
- ttf_0.1Gbps: raw float64 15 [14.8, 18.4], n=32, A1 lower in 32
- ttf_0.1Gbps: source file as archived 38 [36, 43], n=32, A1 lower in 32
- ttf_1Gbps: law, reference implementation 2.62 [2.52, 2.87], n=32, A1 lower in 32
- ttf_1Gbps: operational optimum (A3) 0.603 [0.596, 0.612], n=32, A1 lower in 0
- ttf_1Gbps: A3, reference implementation 2.13 [2.09, 2.26], n=32, A1 lower in 32
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.136 [0.105, 0.169], n=32, A1 lower in 0
- ttf_1Gbps: float64+zlib-6 2.2 [2.1, 2.4], n=32, A1 lower in 32
- ttf_1Gbps: float64+zstd-3 1.58 [1.36, 1.66], n=32, A1 lower in 23
- ttf_1Gbps: MGARD s=-2 4.12 [4.05, 4.24], n=32, A1 lower in 32
- ttf_1Gbps: QPET (best of 9) 0.864 [0.79, 0.966], n=28, A1 lower in 8
- ttf_1Gbps: raw float64 1.51 [1.49, 1.86], n=32, A1 lower in 32
- ttf_1Gbps: source file as archived 8.09 [7.36, 9.81], n=32, A1 lower in 32
- ttf_10Gbps: law, reference implementation 2.62 [2.52, 2.87], n=32, A1 lower in 32
- ttf_10Gbps: operational optimum (A3) 0.603 [0.596, 0.612], n=32, A1 lower in 0
- ttf_10Gbps: A3, reference implementation 2.13 [2.09, 2.27], n=32, A1 lower in 32
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.111 [0.0884, 0.16], n=32, A1 lower in 0
- ttf_10Gbps: float64+zlib-6 0.888 [0.849, 0.978], n=32, A1 lower in 9
- ttf_10Gbps: float64+zstd-3 0.315 [0.267, 0.333], n=32, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 4.12 [4.05, 4.24], n=32, A1 lower in 32
- ttf_10Gbps: QPET (best of 9) 0.858 [0.787, 0.961], n=28, A1 lower in 7
- ttf_10Gbps: raw float64 0.151 [0.149, 0.186], n=32, A1 lower in 0
- ttf_10Gbps: source file as archived 5.43 [4.28, 6.69], n=32, A1 lower in 32

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/32); best of ZFP/SZ3/SPERR (A6) 0.0208 Gbit/s (A1 smaller and faster in 0/32); float64+zlib-6 5.63 Gbit/s (A1 smaller and faster in 2/32); float64+zstd-3 1.7 Gbit/s (A1 smaller and faster in 0/32); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 32/32); QPET (best of 9) 0.0607 Gbit/s (A1 smaller and faster in 7/28); raw float64 1.51 Gbit/s (A1 smaller and faster in 0/32); source file as archived inf Gbit/s (A1 smaller and faster in 32/32)

Fastest to a usable field: 0.1Gbps: A1 0/32 ({'A6': 27, 'A3': 5}); 1Gbps: A1 0/32 ({'A6': 27, 'L_zstd': 5}); 10Gbps: A1 0/32 ({'A6': 21, 'L_zstd': 7, 'RAW': 4})

## P3B_CONFIRMATORY, τ = 1e-06

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 504 [418, 619] | 0.113 [0.101, 0.127] | 0.683 [0.488, 0.802] | 0.0652 [0.0501, 0.0738] | 191 [188, 237] | 6.58 [6.13, 7.35] | 5.01 [5.01, 5.02] | 0.0656 [0.0507, 0.0738] |
| law, reference implementation | 504 [418, 619] | 0.153 [0.125, 0.171] | n/a | 0.175 [0.141, 0.19] | 80.6 [75.4, 85.7] | 6.62 [6.54, 8.46] | 11.4 [9.79, 11.8] | 0.175 [0.141, 0.19] |
| operational optimum (A3) | 647 [459, 883] | 2.84 [1.75, 3.7] | 3.04 [2, 3.89] | 0.0439 [0.033, 0.048] | 302 [294, 347] | 4.48 [4.35, 4.98] | 3.63 [3.56, 3.7] | 0.0441 [0.0335, 0.048] |
| A3, reference implementation | 647 [459, 883] | 2.9 [1.76, 3.65] | n/a | 0.147 [0.109, 0.164] | 88.5 [85.1, 111] | 4.48 [4.46, 4.74] | 11.6 [10.5, 12.2] | 0.147 [0.11, 0.164] |
| best of ZFP/SZ3/SPERR (A6) | 23.3 [20.9, 27.3] | 0.019 [0.0143, 0.026] | 32.9 [27.7, 38.6] | 0.0108 [0.00831, 0.014] | 1.23e+03 [1.08e+03, 1.39e+03] | 0.124 [0.098, 0.164] | 2 [2, 2] | 0.0162 [0.012, 0.0196] |
| MGARD s=-2 | 21 [19.8, 23.9] | 0.317 [0.232, 0.343] | 30.5 [22.3, 32.7] | 0.309 [0.224, 0.336] | 43.8 [42.2, 52.1] | 0 [0, 0.00765] | 3 [3, 3] | 0.315 [0.23, 0.342] |
| QPET (best of 9) | 46 [43.9, 56.7] | 0.195 [0.139, 0.24] | 132 [110, 152] | 0.0777 [0.0494, 0.0849] | 189 [175, 200] | 0.00771 [0.00502, 0.0106] | 3 [2.99, 3] | 0.0797 [0.0504, 0.088] |
| float64+zlib-6 | 1.05 [1.05, 1.06] | 0.32 [0.281, 0.392] | n/a | 0.0435 [0.039, 0.0525] | 295 [254, 332] | 3.86 [3.8, 3.9] | 3 [2.98, 3.03] | 0.139 [0.119, 0.165] |
| float64+zstd-3 | 1.05 [1.05, 1.17] | 0.0161 [0.0134, 0.0194] | n/a | 0.00804 [0.00667, 0.0122] | 1.4e+03 [1.08e+03, 1.76e+03] | 3.05 [2.97, 3.12] | 2 [2, 2] | 0.104 [0.0623, 0.127] |
| source file as archived | 0.439 [0.439, 0.578] | n/a | n/a | 0.295 [0.274, 0.438] | 39.9 [35.7, 48.5] | n/a | n/a | 0.543 [0.523, 0.689] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.113 [0.106, 0.126] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.32 [1.3, 1.36], n=32, A1 lower in 32
- encode: operational optimum (A3) 28.3 [20.2, 31.2], n=32, A1 lower in 32
- encode: A3, reference implementation 28.7 [20.2, 31.2], n=32, A1 lower in 32
- encode: best of ZFP/SZ3/SPERR (A6) 0.179 [0.161, 0.198], n=32, A1 lower in 2
- encode: float64+zlib-6 3.18 [2.79, 3.3], n=32, A1 lower in 32
- encode: float64+zstd-3 0.155 [0.14, 0.162], n=32, A1 lower in 0
- encode: MGARD s=-2 2.51 [2.3, 2.81], n=32, A1 lower in 32
- encode: QPET (best of 9) 1.8 [1.56, 2.01], n=32, A1 lower in 25
- search: operational optimum (A3) 4.81 [3.31, 5.89], n=32, A1 lower in 32
- search: best of ZFP/SZ3/SPERR (A6) 51.6 [45, 56.5], n=32, A1 lower in 32
- search: MGARD s=-2 44.2 [39.3, 46.4], n=32, A1 lower in 32
- search: QPET (best of 9) 196 [181, 207], n=32, A1 lower in 32
- decode: law, reference implementation 2.63 [2.52, 2.79], n=32, A1 lower in 32
- decode: operational optimum (A3) 0.653 [0.636, 0.661], n=32, A1 lower in 0
- decode: A3, reference implementation 2.22 [2.14, 2.3], n=32, A1 lower in 32
- decode: best of ZFP/SZ3/SPERR (A6) 0.186 [0.165, 0.194], n=32, A1 lower in 3
- decode: float64+zlib-6 0.746 [0.71, 0.814], n=32, A1 lower in 3
- decode: float64+zstd-3 0.174 [0.158, 0.178], n=32, A1 lower in 0
- decode: MGARD s=-2 4.54 [4.42, 4.6], n=32, A1 lower in 32
- decode: QPET (best of 9) 1.17 [1.02, 1.28], n=32, A1 lower in 23
- decode: raw float64 0 [0, 0], n=32, A1 lower in 0
- decode: source file as archived 5.54 [3.88, 6.77], n=32, A1 lower in 32
- ttf_0.1Gbps: law, reference implementation 2.55 [2.49, 2.72], n=32, A1 lower in 32
- ttf_0.1Gbps: operational optimum (A3) 0.657 [0.639, 0.673], n=32, A1 lower in 0
- ttf_0.1Gbps: A3, reference implementation 2.18 [2.1, 2.23], n=32, A1 lower in 32
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 0.915 [0.733, 1.01], n=32, A1 lower in 11
- ttf_0.1Gbps: float64+zlib-6 14.7 [14.1, 15.9], n=32, A1 lower in 32
- ttf_0.1Gbps: float64+zstd-3 13.9 [12.5, 14.6], n=32, A1 lower in 32
- ttf_0.1Gbps: MGARD s=-2 5.16 [4.93, 5.28], n=32, A1 lower in 32
- ttf_0.1Gbps: QPET (best of 9) 1.43 [1.21, 1.57], n=32, A1 lower in 26
- ttf_0.1Gbps: raw float64 15 [14.6, 17.8], n=32, A1 lower in 32
- ttf_0.1Gbps: source file as archived 37.4 [35.5, 41.6], n=32, A1 lower in 32
- ttf_1Gbps: law, reference implementation 2.62 [2.52, 2.78], n=32, A1 lower in 32
- ttf_1Gbps: operational optimum (A3) 0.653 [0.636, 0.663], n=32, A1 lower in 0
- ttf_1Gbps: A3, reference implementation 2.21 [2.13, 2.3], n=32, A1 lower in 32
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.26 [0.224, 0.283], n=32, A1 lower in 3
- ttf_1Gbps: float64+zlib-6 2.2 [2.12, 2.52], n=32, A1 lower in 32
- ttf_1Gbps: float64+zstd-3 1.6 [1.43, 1.67], n=32, A1 lower in 23
- ttf_1Gbps: MGARD s=-2 4.6 [4.47, 4.66], n=32, A1 lower in 32
- ttf_1Gbps: QPET (best of 9) 1.19 [1.03, 1.31], n=32, A1 lower in 24
- ttf_1Gbps: raw float64 1.53 [1.5, 1.89], n=32, A1 lower in 32
- ttf_1Gbps: source file as archived 8.21 [7.6, 9.98], n=32, A1 lower in 32
- ttf_10Gbps: law, reference implementation 2.63 [2.52, 2.79], n=32, A1 lower in 32
- ttf_10Gbps: operational optimum (A3) 0.653 [0.636, 0.662], n=32, A1 lower in 0
- ttf_10Gbps: A3, reference implementation 2.22 [2.14, 2.3], n=32, A1 lower in 32
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.192 [0.172, 0.202], n=32, A1 lower in 3
- ttf_10Gbps: float64+zlib-6 0.89 [0.849, 0.992], n=32, A1 lower in 10
- ttf_10Gbps: float64+zstd-3 0.321 [0.285, 0.333], n=32, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 4.54 [4.43, 4.61], n=32, A1 lower in 32
- ttf_10Gbps: QPET (best of 9) 1.17 [1.02, 1.28], n=32, A1 lower in 23
- ttf_10Gbps: raw float64 0.153 [0.15, 0.19], n=32, A1 lower in 0
- ttf_10Gbps: source file as archived 5.66 [4.32, 7], n=32, A1 lower in 32

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/32); best of ZFP/SZ3/SPERR (A6) 0.0892 Gbit/s (A1 smaller and faster in 3/32); float64+zlib-6 5.66 Gbit/s (A1 smaller and faster in 3/32); float64+zstd-3 1.73 Gbit/s (A1 smaller and faster in 0/32); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 32/32); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 23/32); raw float64 1.53 Gbit/s (A1 smaller and faster in 0/32); source file as archived inf Gbit/s (A1 smaller and faster in 32/32)

Fastest to a usable field: 0.1Gbps: A1 0/32 ({'A3': 25, 'A6': 6, 'Q': 1}); 1Gbps: A1 0/32 ({'A6': 26, 'L_zstd': 6}); 10Gbps: A1 0/32 ({'RAW': 12, 'A6': 11, 'L_zstd': 9})

## P3B_CONFIRMATORY, τ = 1e-08

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 64.9 [49.6, 97.1] | 0.142 [0.123, 0.161] | n/a | 0.0666 [0.0518, 0.074] | 191 [186, 222] | 6.35 [4.77, 6.98] | 5.01 [5.01, 5.02] | 0.0701 [0.0553, 0.0747] |
| law, reference implementation | 64.9 [49.6, 97.1] | 0.174 [0.158, 0.185] | n/a | 0.175 [0.145, 0.197] | 77.9 [74.1, 85.4] | 6.49 [6.48, 6.97] | 11.4 [9.7, 11.7] | 0.177 [0.148, 0.199] |
| operational optimum (A3) | 70.3 [52.1, 107] | 2.89 [1.77, 3.76] | n/a | 0.058 [0.0445, 0.0691] | 221 [209, 249] | 4.89 [4.48, 4.98] | 4.98 [4.97, 4.99] | 0.0601 [0.0475, 0.0695] |
| A3, reference implementation | 70.3 [52.1, 107] | 2.88 [1.78, 3.73] | n/a | 0.156 [0.129, 0.187] | 83.9 [79, 92.8] | 4.48 [4.3, 4.97] | 11.2 [9.55, 12] | 0.158 [0.134, 0.188] |
| best of ZFP/SZ3/SPERR (A6) | 10 [9.09, 11.4] | 0.0346 [0.0267, 0.0457] | n/a | 0.0202 [0.0173, 0.0284] | 677 [599, 766] | 0.407 [0.362, 0.549] | 2 [2, 2] | 0.0328 [0.0302, 0.0386] |
| MGARD s=-2 | 8.61 [8.35, 9.22] | 0.324 [0.244, 0.355] | n/a | 0.365 [0.274, 0.396] | 37.4 [35.8, 42.1] | 0.00462 [0, 0.0079] | 3 [3, 3] | 0.377 [0.289, 0.409] |
| QPET (best of 9) | 18.2 [16.1, 22.3] | 0.248 [0.178, 0.311] | n/a | 0.115 [0.0795, 0.141] | 110 [101, 120] | 0.0097 [0.00683, 0.016] | 3 [2.99, 3] | 0.123 [0.0828, 0.148] |
| float64+zlib-6 | 1.05 [1.05, 1.06] | 0.32 [0.281, 0.392] | n/a | 0.0435 [0.039, 0.0525] | 295 [254, 332] | 3.86 [3.8, 3.9] | 3 [2.98, 3.03] | 0.139 [0.119, 0.165] |
| float64+zstd-3 | 1.05 [1.05, 1.17] | 0.0161 [0.0134, 0.0194] | n/a | 0.00804 [0.00667, 0.0122] | 1.4e+03 [1.08e+03, 1.76e+03] | 3.05 [2.97, 3.12] | 2 [2, 2] | 0.104 [0.0623, 0.127] |
| source file as archived | 0.439 [0.439, 0.578] | n/a | n/a | 0.295 [0.274, 0.438] | 39.9 [35.7, 48.5] | n/a | n/a | 0.543 [0.523, 0.689] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.113 [0.106, 0.126] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.22 [1.17, 1.29], n=32, A1 lower in 32
- encode: operational optimum (A3) 21.7 [16.6, 24.2], n=32, A1 lower in 32
- encode: A3, reference implementation 21.6 [16.5, 24.2], n=32, A1 lower in 32
- encode: best of ZFP/SZ3/SPERR (A6) 0.214 [0.184, 0.249], n=32, A1 lower in 0
- encode: float64+zlib-6 2.37 [2.19, 2.51], n=32, A1 lower in 32
- encode: float64+zstd-3 0.119 [0.11, 0.125], n=32, A1 lower in 0
- encode: MGARD s=-2 2.13 [1.85, 2.28], n=32, A1 lower in 32
- encode: QPET (best of 9) 1.86 [1.54, 1.95], n=32, A1 lower in 25
- decode: law, reference implementation 2.68 [2.54, 2.79], n=32, A1 lower in 32
- decode: operational optimum (A3) 0.895 [0.856, 0.95], n=32, A1 lower in 8
- decode: A3, reference implementation 2.44 [2.36, 2.58], n=32, A1 lower in 32
- decode: best of ZFP/SZ3/SPERR (A6) 0.301 [0.276, 0.351], n=32, A1 lower in 0
- decode: float64+zlib-6 0.734 [0.705, 0.78], n=32, A1 lower in 2
- decode: float64+zstd-3 0.166 [0.142, 0.172], n=32, A1 lower in 0
- decode: MGARD s=-2 5.28 [5.14, 5.39], n=32, A1 lower in 32
- decode: QPET (best of 9) 1.95 [1.62, 2.11], n=32, A1 lower in 26
- decode: raw float64 0 [0, 0], n=32, A1 lower in 0
- decode: source file as archived 5.57 [3.87, 6.37], n=32, A1 lower in 32
- ttf_0.1Gbps: law, reference implementation 2.27 [2.18, 2.36], n=32, A1 lower in 32
- ttf_0.1Gbps: operational optimum (A3) 0.897 [0.872, 0.946], n=32, A1 lower in 6
- ttf_0.1Gbps: A3, reference implementation 2.14 [1.99, 2.2], n=32, A1 lower in 32
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 1.47 [1.29, 1.66], n=32, A1 lower in 31
- ttf_0.1Gbps: float64+zlib-6 12 [11.1, 12.8], n=32, A1 lower in 32
- ttf_0.1Gbps: float64+zstd-3 10.8 [9.14, 12], n=32, A1 lower in 32
- ttf_0.1Gbps: MGARD s=-2 5.74 [5.23, 6.2], n=32, A1 lower in 32
- ttf_0.1Gbps: QPET (best of 9) 2.12 [1.85, 2.42], n=32, A1 lower in 26
- ttf_0.1Gbps: raw float64 12.7 [12.2, 13.6], n=32, A1 lower in 32
- ttf_0.1Gbps: source file as archived 30.9 [26.8, 35.2], n=32, A1 lower in 32
- ttf_1Gbps: law, reference implementation 2.64 [2.51, 2.74], n=32, A1 lower in 32
- ttf_1Gbps: operational optimum (A3) 0.895 [0.859, 0.95], n=32, A1 lower in 8
- ttf_1Gbps: A3, reference implementation 2.42 [2.31, 2.5], n=32, A1 lower in 32
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.48 [0.427, 0.528], n=32, A1 lower in 0
- ttf_1Gbps: float64+zlib-6 2.16 [2.04, 2.26], n=32, A1 lower in 32
- ttf_1Gbps: float64+zstd-3 1.53 [1.29, 1.59], n=32, A1 lower in 23
- ttf_1Gbps: MGARD s=-2 5.36 [5.21, 5.45], n=32, A1 lower in 32
- ttf_1Gbps: QPET (best of 9) 1.98 [1.66, 2.14], n=32, A1 lower in 26
- ttf_1Gbps: raw float64 1.5 [1.45, 1.69], n=32, A1 lower in 32
- ttf_1Gbps: source file as archived 7.52 [7.26, 9.36], n=32, A1 lower in 32
- ttf_10Gbps: law, reference implementation 2.67 [2.54, 2.78], n=32, A1 lower in 32
- ttf_10Gbps: operational optimum (A3) 0.895 [0.856, 0.95], n=32, A1 lower in 8
- ttf_10Gbps: A3, reference implementation 2.44 [2.36, 2.58], n=32, A1 lower in 32
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.319 [0.292, 0.374], n=32, A1 lower in 0
- ttf_10Gbps: float64+zlib-6 0.874 [0.85, 0.945], n=32, A1 lower in 7
- ttf_10Gbps: float64+zstd-3 0.312 [0.258, 0.328], n=32, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 5.29 [5.15, 5.4], n=32, A1 lower in 32
- ttf_10Gbps: QPET (best of 9) 1.96 [1.63, 2.11], n=32, A1 lower in 26
- ttf_10Gbps: raw float64 0.152 [0.148, 0.177], n=32, A1 lower in 0
- ttf_10Gbps: source file as archived 5.69 [4.27, 6.54], n=32, A1 lower in 32

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/32); best of ZFP/SZ3/SPERR (A6) 0.193 Gbit/s (A1 smaller and faster in 0/32); float64+zlib-6 5.26 Gbit/s (A1 smaller and faster in 2/32); float64+zstd-3 1.65 Gbit/s (A1 smaller and faster in 0/32); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 32/32); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 26/32); raw float64 1.51 Gbit/s (A1 smaller and faster in 0/32); source file as archived inf Gbit/s (A1 smaller and faster in 32/32)

Fastest to a usable field: 0.1Gbps: A1 5/32 ({'A3': 21, 'A1': 5, 'Q': 5, 'A6': 1}); 1Gbps: A1 0/32 ({'A6': 24, 'L_zstd': 7, 'A3': 1}); 10Gbps: A1 0/32 ({'RAW': 23, 'L_zstd': 9})

## Failures

- {'material_id': 'mp-2508193', 'arm': 'Q', 'tau': 0.0001, 'op': 'encode', 'error': '\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'free(): invalid pointer\\n\'\n'}
- {'material_id': 'mp-2508193', 'arm': 'Q', 'tau': 0.0001, 'op': 'decode', 'error': '\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'free(): invalid pointer\\n\'\n'}
- {'material_id': 'nomad-vbsqs8Js2fzW', 'arm': 'Q', 'tau': 0.0001, 'op': 'encode', 'error': '"/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'double free or corruption (out)\\n\'\n'}
- {'material_id': 'nomad-vbsqs8Js2fzW', 'arm': 'Q', 'tau': 0.0001, 'op': 'decode', 'error': '"/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'double free or corruption (out)\\n\'\n'}
- {'material_id': 'nomad-deLeLsqokf9I', 'arm': 'Q', 'tau': 0.0001, 'op': 'encode', 'error': 'ome/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'free(): invalid next size (normal)\\n\'\n'}
- {'material_id': 'nomad-deLeLsqokf9I', 'arm': 'Q', 'tau': 0.0001, 'op': 'decode', 'error': 'ome/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'free(): invalid next size (normal)\\n\'\n'}
- {'material_id': 'nomad-O_yuQGDsVTCx', 'arm': 'Q', 'tau': 0.0001, 'op': 'encode', 'error': '"/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'double free or corruption (out)\\n\'\n'}
- {'material_id': 'nomad-O_yuQGDsVTCx', 'arm': 'Q', 'tau': 0.0001, 'op': 'decode', 'error': '"/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'double free or corruption (out)\\n\'\n'}
- {'material_id': 'nomad--QPBOSBRk9z4', 'arm': 'Q', 'tau': 0.0001, 'op': 'encode', 'error': 'home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'double free or corruption (!prev)\\n\'\n'}
- {'material_id': 'nomad--QPBOSBRk9z4', 'arm': 'Q', 'tau': 0.0001, 'op': 'decode', 'error': 'home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 593, in main\n    print(json.dumps(child(json.loads(a.child))))\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 219, in child\n    cli_base = cli_baseline(arm, p, op)\n               ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 336, in cli_baseline\n    _, pe = run_cli(comp)\n            ^^^^^^^^^^^^^\n  File "/home/runner/work/QoI/QoI/repo/analysis/deployment_cost_20261012/run_cost.py", line 112, in run_cli\n    raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")\nRuntimeError: hpez rc=-6 stderr=\'double free or corruption (!prev)\\n\'\n'}
