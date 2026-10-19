# Deployment cost — results

Materials: 1; runner CPUs: AMD EPYC 9V45 96-Core Processor.

Reproduction: streams = 21, certified = 21, bytes_equal_recorded = 10, max_abs_byte_difference = 631.0, search_param_mismatch = 0.

## P1_CONFIRMATORY, τ = 0.0001

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 343 [343, 343] | 0.00927 [0.00927, 0.00927] | n/a | 0.00439 [0.00439, 0.00439] | 320 [320, 320] | 0 [0, 0] | 0 [0, 0] | 0.00442 [0.00442, 0.00442] |
| law, reference implementation | 343 [343, 343] | 0.0104 [0.0104, 0.0104] | n/a | 0.0133 [0.0133, 0.0133] | 106 [106, 106] | 0 [0, 0] | 0 [0, 0] | 0.0133 [0.0133, 0.0133] |
| operational optimum (A3) | 835 [835, 835] | 0.265 [0.265, 0.265] | n/a | 0.00401 [0.00401, 0.00401] | 350 [350, 350] | 0 [0, 0] | 0 [0, 0] | 0.00403 [0.00403, 0.00403] |
| A3, reference implementation | 835 [835, 835] | 0.274 [0.274, 0.274] | n/a | 0.0113 [0.0113, 0.0113] | 125 [125, 125] | 0 [0, 0] | 0 [0, 0] | 0.0113 [0.0113, 0.0113] |
| best of ZFP/SZ3/SPERR (A6) | 404 [404, 404] | 0.0064 [0.0064, 0.0064] | n/a | 0.00253 [0.00253, 0.00253] | 555 [555, 555] | 0 [0, 0] | 0 [0, 0] | 0.00256 [0.00256, 0.00256] |
| MGARD s=-2 | 173 [173, 173] | 0.0227 [0.0227, 0.0227] | n/a | 0.0219 [0.0219, 0.0219] | 64.2 [64.2, 64.2] | 98 [98, 98] | 100 [100, 100] | 0.022 [0.022, 0.022] |
| QPET (best of 9) | 297 [297, 297] | 0.0199 [0.0199, 0.0199] | n/a | 0.00624 [0.00624, 0.00624] | 225 [225, 225] | 97.1 [97.1, 97.1] | 100 [100, 100] | 0.00628 [0.00628, 0.00628] |
| float64+zlib-6 | 4.49 [4.49, 4.49] | 0.00823 [0.00823, 0.00823] | n/a | 0.0013 [0.0013, 0.0013] | 1.08e+03 [1.08e+03, 1.08e+03] | 0 [0, 0] | 0 [0, 0] | 0.0038 [0.0038, 0.0038] |
| float64+zstd-3 | 9.46 [9.46, 9.46] | 0.00136 [0.00136, 0.00136] | n/a | 0.000257 [0.000257, 0.000257] | 5.47e+03 [5.47e+03, 5.47e+03] | 0 [0, 0] | 0 [0, 0] | 0.00145 [0.00145, 0.00145] |
| source file as archived | 1.07 [1.07, 1.07] | n/a | n/a | 0.102 [0.102, 0.102] | 13.8 [13.8, 13.8] | n/a | n/a | 0.112 [0.112, 0.112] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.0112 [0.0112, 0.0112] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.12 [1.12, 1.12], n=1, A1 lower in 1
- encode: operational optimum (A3) 28.6 [28.6, 28.6], n=1, A1 lower in 1
- encode: A3, reference implementation 29.5 [29.5, 29.5], n=1, A1 lower in 1
- encode: best of ZFP/SZ3/SPERR (A6) 0.69 [0.69, 0.69], n=1, A1 lower in 0
- encode: float64+zlib-6 0.888 [0.888, 0.888], n=1, A1 lower in 0
- encode: float64+zstd-3 0.146 [0.146, 0.146], n=1, A1 lower in 0
- encode: MGARD s=-2 2.45 [2.45, 2.45], n=1, A1 lower in 1
- encode: QPET (best of 9) 2.15 [2.15, 2.15], n=1, A1 lower in 1
- decode: law, reference implementation 3.03 [3.03, 3.03], n=1, A1 lower in 1
- decode: operational optimum (A3) 0.915 [0.915, 0.915], n=1, A1 lower in 0
- decode: A3, reference implementation 2.57 [2.57, 2.57], n=1, A1 lower in 1
- decode: best of ZFP/SZ3/SPERR (A6) 0.577 [0.577, 0.577], n=1, A1 lower in 0
- decode: float64+zlib-6 0.297 [0.297, 0.297], n=1, A1 lower in 0
- decode: float64+zstd-3 0.0586 [0.0586, 0.0586], n=1, A1 lower in 0
- decode: MGARD s=-2 4.99 [4.99, 4.99], n=1, A1 lower in 1
- decode: QPET (best of 9) 1.42 [1.42, 1.42], n=1, A1 lower in 1
- decode: raw float64 0 [0, 0], n=1, A1 lower in 0
- decode: source file as archived 23.2 [23.2, 23.2], n=1, A1 lower in 1
- ttf_0.1Gbps: law, reference implementation 2.89 [2.89, 2.89], n=1, A1 lower in 1
- ttf_0.1Gbps: operational optimum (A3) 0.88 [0.88, 0.88], n=1, A1 lower in 0
- ttf_0.1Gbps: A3, reference implementation 2.42 [2.42, 2.42], n=1, A1 lower in 1
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 0.596 [0.596, 0.596], n=1, A1 lower in 0
- ttf_0.1Gbps: float64+zlib-6 5.58 [5.58, 5.58], n=1, A1 lower in 1
- ttf_0.1Gbps: float64+zstd-3 2.58 [2.58, 2.58], n=1, A1 lower in 1
- ttf_0.1Gbps: MGARD s=-2 4.78 [4.78, 4.78], n=1, A1 lower in 1
- ttf_0.1Gbps: QPET (best of 9) 1.4 [1.4, 1.4], n=1, A1 lower in 1
- ttf_0.1Gbps: raw float64 23.8 [23.8, 23.8], n=1, A1 lower in 1
- ttf_0.1Gbps: source file as archived 43.9 [43.9, 43.9], n=1, A1 lower in 1
- ttf_1Gbps: law, reference implementation 3.02 [3.02, 3.02], n=1, A1 lower in 1
- ttf_1Gbps: operational optimum (A3) 0.911 [0.911, 0.911], n=1, A1 lower in 0
- ttf_1Gbps: A3, reference implementation 2.55 [2.55, 2.55], n=1, A1 lower in 1
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 0.579 [0.579, 0.579], n=1, A1 lower in 0
- ttf_1Gbps: float64+zlib-6 0.861 [0.861, 0.861], n=1, A1 lower in 0
- ttf_1Gbps: float64+zstd-3 0.327 [0.327, 0.327], n=1, A1 lower in 0
- ttf_1Gbps: MGARD s=-2 4.97 [4.97, 4.97], n=1, A1 lower in 1
- ttf_1Gbps: QPET (best of 9) 1.42 [1.42, 1.42], n=1, A1 lower in 1
- ttf_1Gbps: raw float64 2.54 [2.54, 2.54], n=1, A1 lower in 1
- ttf_1Gbps: source file as archived 25.4 [25.4, 25.4], n=1, A1 lower in 1
- ttf_10Gbps: law, reference implementation 3.03 [3.03, 3.03], n=1, A1 lower in 1
- ttf_10Gbps: operational optimum (A3) 0.915 [0.915, 0.915], n=1, A1 lower in 0
- ttf_10Gbps: A3, reference implementation 2.56 [2.56, 2.56], n=1, A1 lower in 1
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 0.577 [0.577, 0.577], n=1, A1 lower in 0
- ttf_10Gbps: float64+zlib-6 0.354 [0.354, 0.354], n=1, A1 lower in 0
- ttf_10Gbps: float64+zstd-3 0.0856 [0.0856, 0.0856], n=1, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 4.99 [4.99, 4.99], n=1, A1 lower in 1
- ttf_10Gbps: QPET (best of 9) 1.42 [1.42, 1.42], n=1, A1 lower in 1
- ttf_10Gbps: raw float64 0.256 [0.256, 0.256], n=1, A1 lower in 0
- ttf_10Gbps: source file as archived 23.4 [23.4, 23.4], n=1, A1 lower in 1

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/1); best of ZFP/SZ3/SPERR (A6) 0 Gbit/s (A1 smaller and faster in 0/1); float64+zlib-6 0.801 Gbit/s (A1 smaller and faster in 0/1); float64+zstd-3 0.28 Gbit/s (A1 smaller and faster in 0/1); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 1/1); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 1/1); raw float64 2.55 Gbit/s (A1 smaller and faster in 0/1); source file as archived inf Gbit/s (A1 smaller and faster in 1/1)

Fastest to a usable field: 0.1Gbps: A1 0/1 ({'A6': 1}); 1Gbps: A1 0/1 ({'L_zstd': 1}); 10Gbps: A1 0/1 ({'L_zstd': 1})

## P1_CONFIRMATORY, τ = 1e-06

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 195 [195, 195] | 0.00932 [0.00932, 0.00932] | 0.197 [0.197, 0.197] | 0.00372 [0.00372, 0.00372] | 378 [378, 378] | 0 [0, 0] | 0 [0, 0] | 0.00378 [0.00378, 0.00378] |
| law, reference implementation | 195 [195, 195] | 0.0109 [0.0109, 0.0109] | n/a | 0.0132 [0.0132, 0.0132] | 106 [106, 106] | 0 [0, 0] | 0 [0, 0] | 0.0133 [0.0133, 0.0133] |
| operational optimum (A3) | 278 [278, 278] | 0.258 [0.258, 0.258] | 0.464 [0.464, 0.464] | 0.00401 [0.00401, 0.00401] | 350 [350, 350] | 0 [0, 0] | 0 [0, 0] | 0.00405 [0.00405, 0.00405] |
| A3, reference implementation | 278 [278, 278] | 0.27 [0.27, 0.27] | n/a | 0.011 [0.011, 0.011] | 128 [128, 128] | 0 [0, 0] | 0 [0, 0] | 0.011 [0.011, 0.011] |
| best of ZFP/SZ3/SPERR (A6) | 43.3 [43.3, 43.3] | 0.0404 [0.0404, 0.0404] | 1.78 [1.78, 1.78] | 0.00521 [0.00521, 0.00521] | 270 [270, 270] | 0 [0, 0] | 0 [0, 0] | 0.00547 [0.00547, 0.00547] |
| MGARD s=-2 | 14.2 [14.2, 14.2] | 0.0251 [0.0251, 0.0251] | 2.47 [2.47, 2.47] | 0.0251 [0.0251, 0.0251] | 56 [56, 56] | 97 [97, 97] | 100 [100, 100] | 0.0259 [0.0259, 0.0259] |
| QPET (best of 9) | 43.6 [43.6, 43.6] | 0.0406 [0.0406, 0.0406] | 13.8 [13.8, 13.8] | 0.00888 [0.00888, 0.00888] | 158 [158, 158] | 97 [97, 97] | 100 [100, 100] | 0.00914 [0.00914, 0.00914] |
| float64+zlib-6 | 4.49 [4.49, 4.49] | 0.00823 [0.00823, 0.00823] | n/a | 0.0013 [0.0013, 0.0013] | 1.08e+03 [1.08e+03, 1.08e+03] | 0 [0, 0] | 0 [0, 0] | 0.0038 [0.0038, 0.0038] |
| float64+zstd-3 | 9.46 [9.46, 9.46] | 0.00136 [0.00136, 0.00136] | n/a | 0.000257 [0.000257, 0.000257] | 5.47e+03 [5.47e+03, 5.47e+03] | 0 [0, 0] | 0 [0, 0] | 0.00145 [0.00145, 0.00145] |
| source file as archived | 1.07 [1.07, 1.07] | n/a | n/a | 0.102 [0.102, 0.102] | 13.8 [13.8, 13.8] | n/a | n/a | 0.112 [0.112, 0.112] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.0112 [0.0112, 0.0112] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.17 [1.17, 1.17], n=1, A1 lower in 1
- encode: operational optimum (A3) 27.7 [27.7, 27.7], n=1, A1 lower in 1
- encode: A3, reference implementation 29 [29, 29], n=1, A1 lower in 1
- encode: best of ZFP/SZ3/SPERR (A6) 4.34 [4.34, 4.34], n=1, A1 lower in 1
- encode: float64+zlib-6 0.884 [0.884, 0.884], n=1, A1 lower in 0
- encode: float64+zstd-3 0.146 [0.146, 0.146], n=1, A1 lower in 0
- encode: MGARD s=-2 2.7 [2.7, 2.7], n=1, A1 lower in 1
- encode: QPET (best of 9) 4.35 [4.35, 4.35], n=1, A1 lower in 1
- search: operational optimum (A3) 2.35 [2.35, 2.35], n=1, A1 lower in 1
- search: best of ZFP/SZ3/SPERR (A6) 9.04 [9.04, 9.04], n=1, A1 lower in 1
- search: MGARD s=-2 12.5 [12.5, 12.5], n=1, A1 lower in 1
- search: QPET (best of 9) 69.9 [69.9, 69.9], n=1, A1 lower in 1
- decode: law, reference implementation 3.55 [3.55, 3.55], n=1, A1 lower in 1
- decode: operational optimum (A3) 1.08 [1.08, 1.08], n=1, A1 lower in 1
- decode: A3, reference implementation 2.96 [2.96, 2.96], n=1, A1 lower in 1
- decode: best of ZFP/SZ3/SPERR (A6) 1.4 [1.4, 1.4], n=1, A1 lower in 1
- decode: float64+zlib-6 0.35 [0.35, 0.35], n=1, A1 lower in 0
- decode: float64+zstd-3 0.0691 [0.0691, 0.0691], n=1, A1 lower in 0
- decode: MGARD s=-2 6.74 [6.74, 6.74], n=1, A1 lower in 1
- decode: QPET (best of 9) 2.39 [2.39, 2.39], n=1, A1 lower in 1
- decode: raw float64 0 [0, 0], n=1, A1 lower in 0
- decode: source file as archived 27.3 [27.3, 27.3], n=1, A1 lower in 1
- ttf_0.1Gbps: law, reference implementation 3.21 [3.21, 3.21], n=1, A1 lower in 1
- ttf_0.1Gbps: operational optimum (A3) 1.03 [1.03, 1.03], n=1, A1 lower in 1
- ttf_0.1Gbps: A3, reference implementation 2.66 [2.66, 2.66], n=1, A1 lower in 1
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 1.82 [1.82, 1.82], n=1, A1 lower in 1
- ttf_0.1Gbps: float64+zlib-6 6.13 [6.13, 6.13], n=1, A1 lower in 1
- ttf_0.1Gbps: float64+zstd-3 2.83 [2.83, 2.83], n=1, A1 lower in 1
- ttf_0.1Gbps: MGARD s=-2 7.67 [7.67, 7.67], n=1, A1 lower in 1
- ttf_0.1Gbps: QPET (best of 9) 2.67 [2.67, 2.67], n=1, A1 lower in 1
- ttf_0.1Gbps: raw float64 26.2 [26.2, 26.2], n=1, A1 lower in 1
- ttf_0.1Gbps: source file as archived 48.1 [48.1, 48.1], n=1, A1 lower in 1
- ttf_1Gbps: law, reference implementation 3.51 [3.51, 3.51], n=1, A1 lower in 1
- ttf_1Gbps: operational optimum (A3) 1.07 [1.07, 1.07], n=1, A1 lower in 1
- ttf_1Gbps: A3, reference implementation 2.92 [2.92, 2.92], n=1, A1 lower in 1
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 1.45 [1.45, 1.45], n=1, A1 lower in 1
- ttf_1Gbps: float64+zlib-6 1.01 [1.01, 1.01], n=1, A1 lower in 1
- ttf_1Gbps: float64+zstd-3 0.383 [0.383, 0.383], n=1, A1 lower in 0
- ttf_1Gbps: MGARD s=-2 6.85 [6.85, 6.85], n=1, A1 lower in 1
- ttf_1Gbps: QPET (best of 9) 2.42 [2.42, 2.42], n=1, A1 lower in 1
- ttf_1Gbps: raw float64 2.98 [2.98, 2.98], n=1, A1 lower in 1
- ttf_1Gbps: source file as archived 29.7 [29.7, 29.7], n=1, A1 lower in 1
- ttf_10Gbps: law, reference implementation 3.54 [3.54, 3.54], n=1, A1 lower in 1
- ttf_10Gbps: operational optimum (A3) 1.08 [1.08, 1.08], n=1, A1 lower in 1
- ttf_10Gbps: A3, reference implementation 2.96 [2.96, 2.96], n=1, A1 lower in 1
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 1.4 [1.4, 1.4], n=1, A1 lower in 1
- ttf_10Gbps: float64+zlib-6 0.417 [0.417, 0.417], n=1, A1 lower in 0
- ttf_10Gbps: float64+zstd-3 0.101 [0.101, 0.101], n=1, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 6.75 [6.75, 6.75], n=1, A1 lower in 1
- ttf_10Gbps: QPET (best of 9) 2.39 [2.39, 2.39], n=1, A1 lower in 1
- ttf_10Gbps: raw float64 0.302 [0.302, 0.302], n=1, A1 lower in 0
- ttf_10Gbps: source file as archived 27.6 [27.6, 27.6], n=1, A1 lower in 1

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/1); best of ZFP/SZ3/SPERR (A6) inf Gbit/s (A1 smaller and faster in 1/1); float64+zlib-6 1.01 Gbit/s (A1 smaller and faster in 0/1); float64+zstd-3 0.327 Gbit/s (A1 smaller and faster in 0/1); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 1/1); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 1/1); raw float64 3.01 Gbit/s (A1 smaller and faster in 0/1); source file as archived inf Gbit/s (A1 smaller and faster in 1/1)

Fastest to a usable field: 0.1Gbps: A1 1/1 ({'A1': 1}); 1Gbps: A1 0/1 ({'L_zstd': 1}); 10Gbps: A1 0/1 ({'L_zstd': 1})

## P1_CONFIRMATORY, τ = 1e-08

| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |
|---|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 36.4 [36.4, 36.4] | 0.0133 [0.0133, 0.0133] | n/a | 0.00395 [0.00395, 0.00395] | 356 [356, 356] | 0 [0, 0] | 0 [0, 0] | 0.00426 [0.00426, 0.00426] |
| law, reference implementation | 36.4 [36.4, 36.4] | 0.0158 [0.0158, 0.0158] | n/a | 0.0139 [0.0139, 0.0139] | 101 [101, 101] | 0 [0, 0] | 0 [0, 0] | 0.0142 [0.0142, 0.0142] |
| operational optimum (A3) | 38.7 [38.7, 38.7] | 0.271 [0.271, 0.271] | n/a | 0.00459 [0.00459, 0.00459] | 306 [306, 306] | 0 [0, 0] | 0 [0, 0] | 0.00488 [0.00488, 0.00488] |
| A3, reference implementation | 38.7 [38.7, 38.7] | 0.274 [0.274, 0.274] | n/a | 0.0122 [0.0122, 0.0122] | 116 [116, 116] | 0 [0, 0] | 0 [0, 0] | 0.0125 [0.0125, 0.0125] |
| best of ZFP/SZ3/SPERR (A6) | 12.5 [12.5, 12.5] | 0.0128 [0.0128, 0.0128] | n/a | 0.00789 [0.00789, 0.00789] | 178 [178, 178] | 0 [0, 0] | 0 [0, 0] | 0.00879 [0.00879, 0.00879] |
| MGARD s=-2 | 5.7 [5.7, 5.7] | 0.0266 [0.0266, 0.0266] | n/a | 0.0332 [0.0332, 0.0332] | 42.3 [42.3, 42.3] | 97 [97, 97] | 100 [100, 100] | 0.0352 [0.0352, 0.0352] |
| QPET (best of 9) | 12.7 [12.7, 12.7] | 0.0331 [0.0331, 0.0331] | n/a | 0.0125 [0.0125, 0.0125] | 113 [113, 113] | 97 [97, 97] | 100 [100, 100] | 0.0134 [0.0134, 0.0134] |
| float64+zlib-6 | 4.49 [4.49, 4.49] | 0.00823 [0.00823, 0.00823] | n/a | 0.0013 [0.0013, 0.0013] | 1.08e+03 [1.08e+03, 1.08e+03] | 0 [0, 0] | 0 [0, 0] | 0.0038 [0.0038, 0.0038] |
| float64+zstd-3 | 9.46 [9.46, 9.46] | 0.00136 [0.00136, 0.00136] | n/a | 0.000257 [0.000257, 0.000257] | 5.47e+03 [5.47e+03, 5.47e+03] | 0 [0, 0] | 0 [0, 0] | 0.00145 [0.00145, 0.00145] |
| source file as archived | 1.07 [1.07, 1.07] | n/a | n/a | 0.102 [0.102, 0.102] | 13.8 [13.8, 13.8] | n/a | n/a | 0.112 [0.112, 0.112] |
| raw float64 | 1 [1, 1] | n/a | n/a | 0 [0, 0] | n/a [n/a, n/a] | n/a | n/a | 0.0112 [0.0112, 0.0112] |

Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):

- encode: law, reference implementation 1.19 [1.19, 1.19], n=1, A1 lower in 1
- encode: operational optimum (A3) 20.4 [20.4, 20.4], n=1, A1 lower in 1
- encode: A3, reference implementation 20.6 [20.6, 20.6], n=1, A1 lower in 1
- encode: best of ZFP/SZ3/SPERR (A6) 0.964 [0.964, 0.964], n=1, A1 lower in 0
- encode: float64+zlib-6 0.62 [0.62, 0.62], n=1, A1 lower in 0
- encode: float64+zstd-3 0.102 [0.102, 0.102], n=1, A1 lower in 0
- encode: MGARD s=-2 2 [2, 2], n=1, A1 lower in 1
- encode: QPET (best of 9) 2.49 [2.49, 2.49], n=1, A1 lower in 1
- decode: law, reference implementation 3.51 [3.51, 3.51], n=1, A1 lower in 1
- decode: operational optimum (A3) 1.16 [1.16, 1.16], n=1, A1 lower in 1
- decode: A3, reference implementation 3.08 [3.08, 3.08], n=1, A1 lower in 1
- decode: best of ZFP/SZ3/SPERR (A6) 2 [2, 2], n=1, A1 lower in 1
- decode: float64+zlib-6 0.33 [0.33, 0.33], n=1, A1 lower in 0
- decode: float64+zstd-3 0.0651 [0.0651, 0.0651], n=1, A1 lower in 0
- decode: MGARD s=-2 8.41 [8.41, 8.41], n=1, A1 lower in 1
- decode: QPET (best of 9) 3.16 [3.16, 3.16], n=1, A1 lower in 1
- decode: raw float64 0 [0, 0], n=1, A1 lower in 0
- decode: source file as archived 25.8 [25.8, 25.8], n=1, A1 lower in 1
- ttf_0.1Gbps: law, reference implementation 2.41 [2.41, 2.41], n=1, A1 lower in 1
- ttf_0.1Gbps: operational optimum (A3) 1.06 [1.06, 1.06], n=1, A1 lower in 1
- ttf_0.1Gbps: A3, reference implementation 2.14 [2.14, 2.14], n=1, A1 lower in 1
- ttf_0.1Gbps: best of ZFP/SZ3/SPERR (A6) 2.4 [2.4, 2.4], n=1, A1 lower in 1
- ttf_0.1Gbps: float64+zlib-6 3.74 [3.74, 3.74], n=1, A1 lower in 1
- ttf_0.1Gbps: float64+zstd-3 1.72 [1.72, 1.72], n=1, A1 lower in 1
- ttf_0.1Gbps: MGARD s=-2 7.52 [7.52, 7.52], n=1, A1 lower in 1
- ttf_0.1Gbps: QPET (best of 9) 3.03 [3.03, 3.03], n=1, A1 lower in 1
- ttf_0.1Gbps: raw float64 16 [16, 16], n=1, A1 lower in 1
- ttf_0.1Gbps: source file as archived 29.4 [29.4, 29.4], n=1, A1 lower in 1
- ttf_1Gbps: law, reference implementation 3.33 [3.33, 3.33], n=1, A1 lower in 1
- ttf_1Gbps: operational optimum (A3) 1.15 [1.15, 1.15], n=1, A1 lower in 1
- ttf_1Gbps: A3, reference implementation 2.92 [2.92, 2.92], n=1, A1 lower in 1
- ttf_1Gbps: best of ZFP/SZ3/SPERR (A6) 2.06 [2.06, 2.06], n=1, A1 lower in 1
- ttf_1Gbps: float64+zlib-6 0.893 [0.893, 0.893], n=1, A1 lower in 0
- ttf_1Gbps: float64+zstd-3 0.339 [0.339, 0.339], n=1, A1 lower in 0
- ttf_1Gbps: MGARD s=-2 8.26 [8.26, 8.26], n=1, A1 lower in 1
- ttf_1Gbps: QPET (best of 9) 3.14 [3.14, 3.14], n=1, A1 lower in 1
- ttf_1Gbps: raw float64 2.64 [2.64, 2.64], n=1, A1 lower in 1
- ttf_1Gbps: source file as archived 26.4 [26.4, 26.4], n=1, A1 lower in 1
- ttf_10Gbps: law, reference implementation 3.5 [3.5, 3.5], n=1, A1 lower in 1
- ttf_10Gbps: operational optimum (A3) 1.16 [1.16, 1.16], n=1, A1 lower in 1
- ttf_10Gbps: A3, reference implementation 3.06 [3.06, 3.06], n=1, A1 lower in 1
- ttf_10Gbps: best of ZFP/SZ3/SPERR (A6) 2 [2, 2], n=1, A1 lower in 1
- ttf_10Gbps: float64+zlib-6 0.39 [0.39, 0.39], n=1, A1 lower in 0
- ttf_10Gbps: float64+zstd-3 0.0944 [0.0944, 0.0944], n=1, A1 lower in 0
- ttf_10Gbps: MGARD s=-2 8.39 [8.39, 8.39], n=1, A1 lower in 1
- ttf_10Gbps: QPET (best of 9) 3.16 [3.16, 3.16], n=1, A1 lower in 1
- ttf_10Gbps: raw float64 0.282 [0.282, 0.282], n=1, A1 lower in 0
- ttf_10Gbps: source file as archived 25.8 [25.8, 25.8], n=1, A1 lower in 1

Break-even bandwidth (A1 first to a usable field below it): operational optimum (A3) 0 Gbit/s (A1 smaller and faster in 0/1); best of ZFP/SZ3/SPERR (A6) inf Gbit/s (A1 smaller and faster in 1/1); float64+zlib-6 0.829 Gbit/s (A1 smaller and faster in 0/1); float64+zstd-3 0.238 Gbit/s (A1 smaller and faster in 0/1); MGARD s=-2 inf Gbit/s (A1 smaller and faster in 1/1); QPET (best of 9) inf Gbit/s (A1 smaller and faster in 1/1); raw float64 2.77 Gbit/s (A1 smaller and faster in 0/1); source file as archived inf Gbit/s (A1 smaller and faster in 1/1)

Fastest to a usable field: 0.1Gbps: A1 1/1 ({'A1': 1}); 1Gbps: A1 0/1 ({'L_zstd': 1}); 10Gbps: A1 0/1 ({'L_zstd': 1})

