# Deployment cost — results

Materials: 20; runner CPUs: AMD EPYC 7763 64-Core Processor, AMD EPYC 9V45 96-Core Processor, AMD EPYC 9V74 80-Core Processor, Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz.

Reproduction: streams = 420, certified = 418, bytes_equal_recorded = 256, max_abs_byte_difference = 23327.0, search_param_mismatch = 0.

## P1_CONFIRMATORY, τ = 0.0001

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 585 [509, 687] | 0.0363 [0.0328, 0.0478] | n/a | 0.0177 [0.0146, 0.0241] | 209 [196, 251] | 28.4 [24.8, 37.5] | 29.2 [26.1, 37] | 0.0178 [0.0147, 0.0242] |
| law, reference implementation | 585 [509, 687] | 0.0412 [0.0329, 0.057] | n/a | 0.0502 [0.0418, 0.0678] | 76.5 [68.4, 89.2] | 11.4 [11.3, 11.9] | 14.7 [14.6, 14.8] | 0.0503 [0.0419, 0.0679] |
| operational optimum (A3) | 1.11e+03 [833, 1.33e+03] | 1.41 [1, 2.18] | n/a | 0.018 [0.015, 0.0274] | 163 [159, 283] | 11.6 [11.4, 12.1] | 28 [25.3, 34.9] | 0.018 [0.0151, 0.0275] |
| A3, reference implementation | 1.11e+03 [833, 1.33e+03] | 1.41 [1, 2.17] | n/a | 0.038 [0.0319, 0.0568] | 91.8 [83.4, 122] | 11.8 [11.6, 12.1] | 14.5 [14.4, 15] | 0.0381 [0.032, 0.0568] |
| best of ZFP/SZ3/SPERR (A6) | 73.9 [60.2, 130] | 0.0111 [0.00951, 0.0167] | n/a | 0.00481 [0.00422, 0.00699] | 926 [478, 1.21e+03] | 4.34 [2.4, 5.46] | 4.24 [3.87, 5.34] | 0.00553 [0.00507, 0.00749] |
| MGARD s=-2 | 57.2 [39.8, 72.1] | 0.0878 [0.0782, 0.116] | n/a | 0.0878 [0.0744, 0.109] | 43.7 [37.5, 53.5] | 0 [0, 0.0236] | 2.99 [2.99, 3] | 0.0887 [0.0748, 0.11] |
| QPET (best of 9) | 142 [124, 170] | 0.0508 [0.0459, 0.0662] | n/a | 0.0192 [0.0167, 0.0232] | 200 [189, 232] | 0.0261 [0.0219, 0.0379] | 3 [2.99, 3] | 0.0195 [0.0169, 0.0234] |
| float64+zlib-6 | 1.66 [1.12, 1.73] | 0.0916 [0.068, 0.129] | n/a | 0.0123 [0.00893, 0.0158] | 344 [311, 461] | 3 [2.89, 3.87] | 3.81 [3.63, 3.95] | 0.0375 [0.0279, 0.046] |
| float64+zstd-3 | 2.6 [1.56, 3.34] | 0.00782 [0.0043, 0.00946] | n/a | 0.0024 [0.0019, 0.00304] | 1.95e+03 [1.46e+03, 2.71e+03] | 2.91 [2.59, 3.19] | 2.46 [2.38, 2.74] | 0.0168 [0.0113, 0.025] |
| source file as archived | 0.607 [0.559, 0.771] | n/a | n/a | 0.315 [0.223, 0.407] | 13.5 [13.1, 14] | n/a | n/a | 0.367 [0.262, 0.482] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.0347 [0.0239, 0.0422] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.11 [1.06, 1.24], n=20, A1 lower in 17
- encode: operational optimum (A3) 37.4 [29.4, 47.5], n=20, A1 lower in 20
- encode: A3, reference implementation 37 [29.4, 47.1], n=20, A1 lower in 20
- encode: best of ZFP/SZ3/SPERR (A6) 0.298 [0.273, 0.538], n=20, A1 lower in 1
- encode: float64+zlib-6 2.26 [1.77, 3.03], n=20, A1 lower in 19
- encode: float64+zstd-3 0.148 [0.131, 0.233], n=20, A1 lower in 0
- encode: MGARD s=-2 2.49 [2.33, 2.59], n=20, A1 lower in 20
- encode: QPET (best of 9) 1.4 [1.35, 1.58], n=20, A1 lower in 20
- decode: law, reference implementation 2.92 [2.76, 3.07], n=20, A1 lower in 20
- decode: operational optimum (A3) 1.07 [1.02, 1.26], n=20, A1 lower in 16
- decode: A3, reference implementation 2.34 [2.21, 2.57], n=20, A1 lower in 20
- decode: best of ZFP/SZ3/SPERR (A6) 0.258 [0.204, 0.545], n=20, A1 lower in 0
- decode: float64+zlib-6 0.638 [0.524, 0.749], n=20, A1 lower in 1
- decode: float64+zstd-3 0.125 [0.0914, 0.146], n=20, A1 lower in 0
- decode: MGARD s=-2 5.13 [4.63, 5.66], n=20, A1 lower in 20
- decode: QPET (best of 9) 1.11 [0.946, 1.22], n=20, A1 lower in 12
- decode: raw float64 0 [0, 0], n=20, A1 lower in 0
- decode: source file as archived 14.9 [14.4, 17.5], n=20, A1 lower in 20
- ttf_0.1Gbps: law, reference implementation 2.87 [2.7, 3.01], n=20, A1 lower in 20
- ttf_0.1Gbps: operational optimum (A3) 1.06 [1.01, 1.24], n=20, A1 lower in 14
- ttf_0.1Gbps: A3, reference implementation 2.29 [2.16, 2.49], n=20, A1 lower in 20
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 0.587 [0.469, 0.687], n=20, A1 lower in 0
- ttf_0.1Gbps: float64+zlib-6 12.6 [9.58, 15.3], n=20, A1 lower in 20
- ttf_0.1Gbps: float64+zstd-3 7.24 [4.95, 11.6], n=20, A1 lower in 20
- ttf_0.1Gbps: MGARD s=-2 5.38 [4.8, 5.75], n=20, A1 lower in 20
- ttf_0.1Gbps: QPET (best of 9) 1.2 [1.02, 1.32], n=20, A1 lower in 14
- ttf_0.1Gbps: raw float64 16.1 [15.3, 19.2], n=20, A1 lower in 20
- ttf_0.1Gbps: source file as archived 41.7 [38.3, 50.1], n=20, A1 lower in 20
- ttf_1Gbps: law, reference implementation 2.92 [2.75, 3.06], n=20, A1 lower in 20
- ttf_1Gbps: operational optimum (A3) 1.07 [1.02, 1.25], n=20, A1 lower in 16
- ttf_1Gbps: A3, reference implementation 2.33 [2.2, 2.56], n=20, A1 lower in 20
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.303 [0.223, 0.552], n=20, A1 lower in 0
- ttf_1Gbps: float64+zlib-6 1.87 [1.44, 2.33], n=20, A1 lower in 18
- ttf_1Gbps: float64+zstd-3 0.829 [0.606, 1.32], n=20, A1 lower in 9
- ttf_1Gbps: MGARD s=-2 5.16 [4.65, 5.66], n=20, A1 lower in 20
- ttf_1Gbps: QPET (best of 9) 1.12 [0.953, 1.24], n=20, A1 lower in 13
- ttf_1Gbps: raw float64 1.67 [1.57, 2], n=20, A1 lower in 20
- ttf_1Gbps: source file as archived 17.6 [16.7, 20.7], n=20, A1 lower in 20
- ttf_10Gbps: law, reference implementation 2.92 [2.75, 3.06], n=20, A1 lower in 20
- ttf_10Gbps: operational optimum (A3) 1.07 [1.02, 1.26], n=20, A1 lower in 16
- ttf_10Gbps: A3, reference implementation 2.34 [2.21, 2.56], n=20, A1 lower in 20
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.263 [0.206, 0.546], n=20, A1 lower in 0
- ttf_10Gbps: float64+zlib-6 0.761 [0.61, 0.916], n=20, A1 lower in 2
- ttf_10Gbps: float64+zstd-3 0.215 [0.155, 0.251], n=20, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 5.13 [4.63, 5.66], n=20, A1 lower in 20
- ttf_10Gbps: QPET (best of 9) 1.11 [0.947, 1.22], n=20, A1 lower in 12
- ttf_10Gbps: raw float64 0.168 [0.157, 0.201], n=20, A1 lower in 0
- ttf_10Gbps: source file as archived 15.1 [14.7, 17.8], n=20, A1 lower in 20

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/20); best of ZFP/SZ3/SPERR (A6) 0.0259 Gbit/s (A1 smaller and faster in 0/20); float64+zlib-6 3.55 Gbit/s (A1 smaller and faster in 1/20); float64+zstd-3 0.809 Gbit/s (A1 smaller and faster in 0/20); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 20/20); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 12/20); raw float64 1.67 Gbit/s (A1 smaller and faster in 0/20); source file as archived inf Gbit/s (A1 smaller and faster in 20/20)

Fastest to a usable field: 0.1Gbps: A1 0/20 ({'A6': 19, 'A3': 1}); 1Gbps: A1 0/20 ({'A6': 17, 'L_zstd': 3}); 10Gbps: A1 0/20 ({'RAW': 10, 'L_zstd': 8, 'A6': 2})

## P1_CONFIRMATORY, τ = 1e-06

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 187 [134, 223] | 0.0346 [0.0283, 0.0472] | 0.42 [0.328, 0.505] | 0.0181 [0.0146, 0.0249] | 214 [199, 259] | 23.7 [21.1, 30.4] | 27 [24.3, 33.9] | 0.0184 [0.0149, 0.0252] |
| law, reference implementation | 187 [134, 223] | 0.044 [0.0358, 0.0616] | n/a | 0.0489 [0.0417, 0.0657] | 77.6 [71.5, 92.4] | 11.6 [11.4, 12.1] | 14.6 [14.4, 15.2] | 0.0492 [0.0418, 0.066] |
| operational optimum (A3) | 233 [146, 289] | 1.41 [1, 2.16] | 1.78 [1.28, 2.43] | 0.0184 [0.0157, 0.028] | 160 [155, 285] | 11.8 [11.6, 12.2] | 28 [25.3, 34.8] | 0.0187 [0.016, 0.0281] |
| A3, reference implementation | 233 [146, 289] | 1.41 [0.998, 2.17] | n/a | 0.0402 [0.0346, 0.0605] | 81.7 [73.3, 118] | 11.9 [11.5, 12.2] | 14.5 [14.3, 15] | 0.0406 [0.0349, 0.0607] |
| best of ZFP/SZ3/SPERR (A6) | 16 [13.9, 22.4] | 0.013 [0.00806, 0.0202] | 9.5 [8.05, 12.9] | 0.00723 [0.0051, 0.0123] | 677 [211, 934] | 0.36 [0.249, 6.16] | 2.12 [2.11, 5.86] | 0.00978 [0.00791, 0.0146] |
| MGARD s=-2 | 9.54 [8.72, 11.4] | 0.0912 [0.0788, 0.117] | 9.11 [7.85, 11.6] | 0.101 [0.0821, 0.12] | 37.5 [34.3, 45.7] | 0.0231 [0, 0.0329] | 3 [2.99, 3] | 0.104 [0.0851, 0.123] |
| QPET (best of 9) | 26.5 [24.3, 32.3] | 0.0696 [0.0628, 0.09] | 48.5 [39.8, 61.4] | 0.0346 [0.0285, 0.037] | 130 [114, 142] | 0 [0, 0.032] | 3 [3, 3.01] | 0.0358 [0.0296, 0.0385] |
| float64+zlib-6 | 1.66 [1.12, 1.73] | 0.0916 [0.068, 0.129] | n/a | 0.0123 [0.00893, 0.0158] | 344 [311, 461] | 3 [2.89, 3.87] | 3.81 [3.63, 3.95] | 0.0375 [0.0279, 0.046] |
| float64+zstd-3 | 2.6 [1.56, 3.34] | 0.00782 [0.0043, 0.00946] | n/a | 0.0024 [0.0019, 0.00304] | 1.95e+03 [1.46e+03, 2.71e+03] | 2.91 [2.59, 3.19] | 2.46 [2.38, 2.74] | 0.0168 [0.0113, 0.025] |
| source file as archived | 0.607 [0.559, 0.771] | n/a | n/a | 0.315 [0.223, 0.407] | 13.5 [13.1, 14] | n/a | n/a | 0.367 [0.262, 0.482] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.0347 [0.0239, 0.0422] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.32 [1.14, 1.39], n=20, A1 lower in 19
- encode: operational optimum (A3) 37.4 [29.6, 49.7], n=20, A1 lower in 20
- encode: A3, reference implementation 37.4 [29.4, 49.7], n=20, A1 lower in 20
- encode: best of ZFP/SZ3/SPERR (A6) 0.26 [0.228, 0.828], n=20, A1 lower in 4
- encode: float64+zlib-6 2.46 [1.87, 3.36], n=20, A1 lower in 19
- encode: float64+zstd-3 0.159 [0.131, 0.25], n=20, A1 lower in 0
- encode: MGARD s=-2 2.63 [2.33, 2.94], n=20, A1 lower in 20
- encode: QPET (best of 9) 2.19 [1.92, 2.34], n=20, A1 lower in 20
- search: operational optimum (A3) 3.74 [3.32, 5.41], n=20, A1 lower in 20
- search: best of ZFP/SZ3/SPERR (A6) 25.8 [18.8, 29.6], n=20, A1 lower in 20
- search: MGARD s=-2 23.7 [21, 25.7], n=20, A1 lower in 20
- search: QPET (best of 9) 125 [109, 132], n=20, A1 lower in 20
- decode: law, reference implementation 2.95 [2.79, 3.09], n=20, A1 lower in 20
- decode: operational optimum (A3) 1.1 [1.01, 1.3], n=20, A1 lower in 14
- decode: A3, reference implementation 2.6 [2.38, 2.73], n=20, A1 lower in 20
- decode: best of ZFP/SZ3/SPERR (A6) 0.295 [0.275, 1.02], n=20, A1 lower in 7
- decode: float64+zlib-6 0.668 [0.525, 0.787], n=20, A1 lower in 1
- decode: float64+zstd-3 0.127 [0.0984, 0.151], n=20, A1 lower in 0
- decode: MGARD s=-2 5.82 [5.4, 6.66], n=20, A1 lower in 20
- decode: QPET (best of 9) 1.88 [1.52, 1.98], n=20, A1 lower in 20
- decode: raw float64 0 [0, 0], n=20, A1 lower in 0
- decode: source file as archived 15.5 [14.4, 16.5], n=20, A1 lower in 20
- ttf_0.1Gbps: law, reference implementation 2.75 [2.49, 2.88], n=20, A1 lower in 20
- ttf_0.1Gbps: operational optimum (A3) 1.06 [0.988, 1.25], n=20, A1 lower in 14
- ttf_0.1Gbps: A3, reference implementation 2.41 [2.29, 2.54], n=20, A1 lower in 20
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 1.47 [1.25, 1.74], n=20, A1 lower in 17
- ttf_0.1Gbps: float64+zlib-6 12.1 [8.99, 14.4], n=20, A1 lower in 20
- ttf_0.1Gbps: float64+zstd-3 7.38 [4.58, 10.3], n=20, A1 lower in 20
- ttf_0.1Gbps: MGARD s=-2 6.68 [6.14, 7.57], n=20, A1 lower in 20
- ttf_0.1Gbps: QPET (best of 9) 2.17 [1.83, 2.4], n=20, A1 lower in 20
- ttf_0.1Gbps: raw float64 14.9 [14.4, 18.4], n=20, A1 lower in 20
- ttf_0.1Gbps: source file as archived 39.9 [35.4, 44.8], n=20, A1 lower in 20
- ttf_1Gbps: law, reference implementation 2.9 [2.76, 3.06], n=20, A1 lower in 20
- ttf_1Gbps: operational optimum (A3) 1.09 [1.01, 1.3], n=20, A1 lower in 14
- ttf_1Gbps: A3, reference implementation 2.58 [2.37, 2.71], n=20, A1 lower in 20
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.456 [0.389, 1.06], n=20, A1 lower in 7
- ttf_1Gbps: float64+zlib-6 1.87 [1.5, 2.4], n=20, A1 lower in 18
- ttf_1Gbps: float64+zstd-3 0.92 [0.592, 1.35], n=20, A1 lower in 9
- ttf_1Gbps: MGARD s=-2 5.91 [5.52, 6.75], n=20, A1 lower in 20
- ttf_1Gbps: QPET (best of 9) 1.93 [1.55, 2.02], n=20, A1 lower in 20
- ttf_1Gbps: raw float64 1.69 [1.58, 2.03], n=20, A1 lower in 20
- ttf_1Gbps: source file as archived 18.3 [16.5, 19.3], n=20, A1 lower in 20
- ttf_10Gbps: law, reference implementation 2.94 [2.79, 3.09], n=20, A1 lower in 20
- ttf_10Gbps: operational optimum (A3) 1.1 [1.01, 1.3], n=20, A1 lower in 14
- ttf_10Gbps: A3, reference implementation 2.59 [2.38, 2.72], n=20, A1 lower in 20
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.309 [0.29, 1.03], n=20, A1 lower in 7
- ttf_10Gbps: float64+zlib-6 0.785 [0.624, 0.944], n=20, A1 lower in 4
- ttf_10Gbps: float64+zstd-3 0.213 [0.158, 0.277], n=20, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 5.83 [5.41, 6.67], n=20, A1 lower in 20
- ttf_10Gbps: QPET (best of 9) 1.88 [1.52, 1.98], n=20, A1 lower in 20
- ttf_10Gbps: raw float64 0.171 [0.159, 0.207], n=20, A1 lower in 0
- ttf_10Gbps: source file as archived 15.8 [14.6, 16.7], n=20, A1 lower in 20

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/20); best of ZFP/SZ3/SPERR (A6) 0.222 Gbit/s (A1 smaller and faster in 7/20); float64+zlib-6 3.7 Gbit/s (A1 smaller and faster in 1/20); float64+zstd-3 0.91 Gbit/s (A1 smaller and faster in 0/20); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 20/20); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 20/20); raw float64 1.7 Gbit/s (A1 smaller and faster in 0/20); source file as archived inf Gbit/s (A1 smaller and faster in 20/20)

Fastest to a usable field: 0.1Gbps: A1 11/20 ({'A1': 11, 'A3': 6, 'A6': 3}); 1Gbps: A1 2/20 ({'A6': 10, 'L_zstd': 7, 'A1': 2, 'A3': 1}); 10Gbps: A1 0/20 ({'RAW': 12, 'L_zstd': 8})

## P1_CONFIRMATORY, τ = 1e-08

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 27.6 [19.4, 39.2] | 0.0611 [0.0426, 0.0745] | n/a | 0.0171 [0.0145, 0.0244] | 205 [196, 281] | 24.1 [22, 30.4] | 27.1 [24.4, 33.9] | 0.0202 [0.0155, 0.0261] |
| law, reference implementation | 27.6 [19.4, 39.2] | 0.0688 [0.0493, 0.0846] | n/a | 0.0473 [0.0431, 0.0685] | 72.8 [68.4, 96] | 11.8 [11.4, 12.1] | 14.7 [14.6, 15.1] | 0.0504 [0.0441, 0.0712] |
| operational optimum (A3) | 28.3 [19.6, 40.8] | 1.43 [1.01, 2.22] | n/a | 0.0198 [0.0166, 0.0299] | 151 [145, 269] | 11.9 [11.6, 12.1] | 28 [25.3, 34.9] | 0.0216 [0.0189, 0.032] |
| A3, reference implementation | 28.3 [19.6, 40.8] | 1.43 [1.01, 2.19] | n/a | 0.0449 [0.038, 0.0698] | 74.5 [68.9, 104] | 12 [11.7, 12.4] | 14.6 [14.4, 15] | 0.0479 [0.0395, 0.0718] |
| best of ZFP/SZ3/SPERR (A6) | 7.05 [6.26, 8.42] | 0.0176 [0.012, 0.0285] | n/a | 0.0112 [0.00768, 0.0189] | 470 [127, 605] | 1.01 [0.716, 6.92] | 2.21 [2.2, 6.25] | 0.017 [0.0139, 0.0244] |
| MGARD s=-2 | 4.92 [4.84, 5.17] | 0.099 [0.0868, 0.123] | n/a | 0.13 [0.108, 0.158] | 29 [26.7, 35] | 0 [0, 0] | 3 [3, 3] | 0.141 [0.114, 0.166] |
| QPET (best of 9) | 9.78 [8.94, 11] | 0.0951 [0.0802, 0.122] | n/a | 0.058 [0.0442, 0.0637] | 77.7 [68.5, 96] | 0.0291 [0.0224, 0.0621] | 2.99 [2.97, 2.99] | 0.0617 [0.0471, 0.0669] |
| float64+zlib-6 | 1.66 [1.12, 1.73] | 0.0916 [0.068, 0.129] | n/a | 0.0123 [0.00893, 0.0158] | 344 [311, 461] | 3 [2.89, 3.87] | 3.81 [3.63, 3.95] | 0.0375 [0.0279, 0.046] |
| float64+zstd-3 | 2.6 [1.56, 3.34] | 0.00782 [0.0043, 0.00946] | n/a | 0.0024 [0.0019, 0.00304] | 1.95e+03 [1.46e+03, 2.71e+03] | 2.91 [2.59, 3.19] | 2.46 [2.38, 2.74] | 0.0168 [0.0113, 0.025] |
| source file as archived | 0.607 [0.559, 0.771] | n/a | n/a | 0.315 [0.223, 0.407] | 13.5 [13.1, 14] | n/a | n/a | 0.367 [0.262, 0.482] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.0347 [0.0239, 0.0422] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.11 [1.08, 1.21], n=20, A1 lower in 20
- encode: operational optimum (A3) 25.3 [21.3, 28.4], n=20, A1 lower in 20
- encode: A3, reference implementation 25 [21.4, 28.3], n=20, A1 lower in 20
- encode: best of ZFP/SZ3/SPERR (A6) 0.235 [0.187, 0.808], n=20, A1 lower in 3
- encode: float64+zlib-6 1.33 [1.2, 2.13], n=20, A1 lower in 17
- encode: float64+zstd-3 0.103 [0.0823, 0.135], n=20, A1 lower in 0
- encode: MGARD s=-2 1.89 [1.57, 2.19], n=20, A1 lower in 20
- encode: QPET (best of 9) 1.68 [1.3, 1.99], n=20, A1 lower in 18
- decode: law, reference implementation 2.87 [2.78, 2.96], n=20, A1 lower in 20
- decode: operational optimum (A3) 1.12 [1.05, 1.36], n=20, A1 lower in 18
- decode: A3, reference implementation 2.77 [2.61, 2.81], n=20, A1 lower in 20
- decode: best of ZFP/SZ3/SPERR (A6) 0.419 [0.392, 1.6], n=20, A1 lower in 7
- decode: float64+zlib-6 0.643 [0.547, 0.763], n=20, A1 lower in 1
- decode: float64+zstd-3 0.123 [0.0971, 0.143], n=20, A1 lower in 0
- decode: MGARD s=-2 7.41 [6.98, 8], n=20, A1 lower in 20
- decode: QPET (best of 9) 2.93 [2.23, 3.19], n=20, A1 lower in 18
- decode: raw float64 0 [0, 0], n=20, A1 lower in 0
- decode: source file as archived 15 [14, 19.1], n=20, A1 lower in 20
- ttf_0.1Gbps: law, reference implementation 2.16 [1.82, 2.34], n=20, A1 lower in 20
- ttf_0.1Gbps: operational optimum (A3) 1.07 [1.01, 1.18], n=20, A1 lower in 16
- ttf_0.1Gbps: A3, reference implementation 2.02 [1.87, 2.18], n=20, A1 lower in 20
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 1.86 [1.63, 2.23], n=20, A1 lower in 20
- ttf_0.1Gbps: float64+zlib-6 7.08 [5.76, 8.03], n=20, A1 lower in 20
- ttf_0.1Gbps: float64+zstd-3 3.89 [2.97, 5.84], n=20, A1 lower in 20
- ttf_0.1Gbps: MGARD s=-2 5.97 [5.32, 7.37], n=20, A1 lower in 20
- ttf_0.1Gbps: QPET (best of 9) 2.33 [2.13, 2.62], n=20, A1 lower in 20
- ttf_0.1Gbps: raw float64 10.4 [8.46, 11.9], n=20, A1 lower in 20
- ttf_0.1Gbps: source file as archived 24.3 [21.3, 28.4], n=20, A1 lower in 20
- ttf_1Gbps: law, reference implementation 2.74 [2.56, 2.87], n=20, A1 lower in 20
- ttf_1Gbps: operational optimum (A3) 1.1 [1.04, 1.32], n=20, A1 lower in 18
- ttf_1Gbps: A3, reference implementation 2.63 [2.49, 2.73], n=20, A1 lower in 20
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.706 [0.589, 1.67], n=20, A1 lower in 7
- ttf_1Gbps: float64+zlib-6 1.78 [1.33, 2.07], n=20, A1 lower in 18
- ttf_1Gbps: float64+zstd-3 0.83 [0.534, 1.14], n=20, A1 lower in 7
- ttf_1Gbps: MGARD s=-2 7.4 [6.69, 7.79], n=20, A1 lower in 20
- ttf_1Gbps: QPET (best of 9) 2.82 [2.28, 2.99], n=20, A1 lower in 18
- ttf_1Gbps: raw float64 1.54 [1.42, 2.08], n=20, A1 lower in 20
- ttf_1Gbps: source file as archived 16.3 [15, 21.2], n=20, A1 lower in 20
- ttf_10Gbps: law, reference implementation 2.86 [2.76, 2.94], n=20, A1 lower in 20
- ttf_10Gbps: operational optimum (A3) 1.12 [1.05, 1.35], n=20, A1 lower in 18
- ttf_10Gbps: A3, reference implementation 2.75 [2.6, 2.8], n=20, A1 lower in 20
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.448 [0.412, 1.61], n=20, A1 lower in 7
- ttf_10Gbps: float64+zlib-6 0.772 [0.632, 0.901], n=20, A1 lower in 3
- ttf_10Gbps: float64+zstd-3 0.2 [0.15, 0.254], n=20, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 7.41 [6.96, 7.97], n=20, A1 lower in 20
- ttf_10Gbps: QPET (best of 9) 2.92 [2.24, 3.17], n=20, A1 lower in 18
- ttf_10Gbps: raw float64 0.163 [0.156, 0.224], n=20, A1 lower in 0
- ttf_10Gbps: source file as archived 15.1 [14.1, 19.3], n=20, A1 lower in 20

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/20); best of ZFP/SZ3/SPERR (A6) 0.453 Gbit/s (A1 smaller and faster in 7/20); float64+zlib-6 3.51 Gbit/s (A1 smaller and faster in 1/20); float64+zstd-3 0.782 Gbit/s (A1 smaller and faster in 0/20); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 20/20); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 18/20); raw float64 1.59 Gbit/s (A1 smaller and faster in 0/20); source file as archived inf Gbit/s (A1 smaller and faster in 20/20)

Fastest to a usable field: 0.1Gbps: A1 16/20 ({'A1': 16, 'A3': 4}); 1Gbps: A1 2/20 ({'A6': 9, 'L_zstd': 8, 'A1': 2, 'A3': 1}); 10Gbps: A1 0/20 ({'RAW': 12, 'L_zstd': 8})

