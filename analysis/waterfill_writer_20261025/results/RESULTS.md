# Water-filling law and the W1 writer on the law-protocol cohort — results

Materials analyzable 92/92 (failed: none). Every W1-family stream decoded from its bytes and certified (historical and Nyquist-safe Hartree relative RMS < tau). Ratios are medians over materials of per-material compression-ratio ratios, 95% bootstrap intervals of the median (seed 20261025, 10,000 resamples); wins = materials with ratio > 1.

Run on Vanda 2026-10-25 (probe 1491770 PASS, production 1491799), collected by `qoi_algo_monitor.py` (tarball SHA-256
be574d60b72a…, checkpoints identical to the pre-collection copy); every ratio recomputed independently from `rows.csv`
and the law-protocol rows by `review_recompute.py` (maximum relative difference 1e-16; 0 certificate violations).

## Reading

- **The closed form is at the operational optimum once zeros are entropy-coded.** Under the same writer, operational
  allocation on the writer's exact per-shell curves (O1S) stores the median material in 0.999 of the water-filling
  law's compression ratio at 1e-6 (bulk 0.998, slabs 1.001) and 0.979 at 1e-4: the per-shell search gains nothing and
  pays for its 32 shell multipliers. Revision 10's optimizer share (A3/A1 1.105 bulk, 1.222 slabs at 1e-6; 1.58 / 2.22
  at 1e-4) was a cost of the zlib container.
- **Water-filling against truncation.** W1S beats T1S (the same writer, truncation allocation, A2 search) in 92/92 at
  every tolerance (1.34-fold at 1e-4, 1.45 at 1e-6, 1.58 at 1e-8); the 1e-4 crossover of revision 10 (A1/A2 0.79 bulk,
  0.69 slabs) does not occur. The water-filling rule itself adds little over the plain law in this writer
  (W1/L1 1.000–1.015), because the adaptive coder already codes dead-zone shells in a fraction of a bit.
- **Attribution of the gain over revision-10 A3 (2.34-fold at 1e-6, 2.68 at 1e-4):** adaptive arithmetic coding and the
  binary header (L1/A1 1.34 at 1e-6, 2.51 at 1e-4), and symmetry-predictive coding (W1S/W1 1.91 at 1e-6; 1.00 for the
  18 materials with a trivial grid group, 3.90 for groups of 9–24 operations). Against the best pointwise codec the
  writer certifies 35.7-fold more at 1e-6 and 48.1-fold at 1e-4; the pointwise codecs use no symmetry.

## Criteria

- **H1 closed form at the optimum (O1S/W1S <= 1.05, CI upper <= 1.08, 1e-6 and 1e-4): met.**
- **H2 water-filling over truncation (W1S > T1S in >= 90%, 1e-6 and 1e-4): met.**
- **H3 writer over revision-10 A3 (median W1S/A3 > 1.3, CI lower > 1.2, 1e-6): met.**
- **validity (>= 90/92 analyzable, all W1 arms certified): met.**

## tau_H = 1e-06

| ratio (CR) | median | 95% CI | wins |
|---|---|---|---|
| operational / water-filling, same writer (H1) | 0.999 | 0.997–1.001 | 39/92 |
| water-filling / truncation, same writer (H2) | 1.450 | 1.415–1.525 | 92/92 |
| W1S / revision-10 operational allocation A3 (H3) | 2.337 | 2.137–2.690 | 92/92 |
| W1S / revision-10 law A1 | 2.911 | 2.362–3.703 | 92/92 |
| W1S / revision-10 truncation A2 | 3.739 | 3.215–4.293 | 92/92 |
| W1S / best pointwise codec A6 | 35.656 | 28.451–46.364 | 92/92 |
| attribution: container + coder (L1 / A1) | 1.337 | 1.292–1.414 | 92/92 |
| attribution: water-filling (W1 / L1) | 1.015 | 1.012–1.019 | 73/92 |
| attribution: symmetry (W1S / W1) | 1.913 | 1.829–2.137 | 68/92 |
| operational / water-filling without symmetry (O1 / W1) | 1.004 | 1.001–1.011 | 60/92 |
| O1S / A3 | 2.409 | 2.134–2.680 | 92/92 |
| T1S / A2 | 2.618 | 2.256–2.734 | 92/92 |

By cohort (P1 bulk / P3b slabs):

| ratio | P1 median (wins/n) | P3b median (wins/n) |
|---|---|---|
| O1S/W1S | 0.998 (21/60) | 1.001 (18/32) |
| W1S/T1S | 1.413 (60/60) | 1.735 (32/32) |
| W1S/A3 | 3.014 (60/60) | 2.109 (32/32) |
| W1S/A1 | 3.490 (60/60) | 2.440 (32/32) |
| W1S/A6 | 35.656 (60/60) | 35.698 (32/32) |
| W1S/W1 | 2.817 (45/60) | 1.822 (23/32) |

Symmetry gain W1S/W1 by number of grid operations:

- 1 operations: median 1.000 (n = 18)
- 2-8 operations: median 1.883 (n = 49)
- 9-24 operations: median 3.898 (n = 14)
- >24 operations: median 2.137 (n = 11)

## tau_H = 0.0001

| ratio (CR) | median | 95% CI | wins |
|---|---|---|---|
| operational / water-filling, same writer (H1) | 0.979 | 0.970–0.983 | 15/92 |
| water-filling / truncation, same writer (H2) | 1.344 | 1.301–1.406 | 92/92 |
| W1S / revision-10 operational allocation A3 (H3) | 2.684 | 2.190–2.997 | 92/92 |
| W1S / revision-10 law A1 | 4.732 | 3.778–5.522 | 92/92 |
| W1S / revision-10 truncation A2 | 3.658 | 3.370–3.788 | 92/92 |
| W1S / best pointwise codec A6 | 48.081 | 42.424–61.119 | 92/92 |
| attribution: container + coder (L1 / A1) | 2.512 | 2.267–2.657 | 92/92 |
| attribution: water-filling (W1 / L1) | 1.000 | 1.000–1.008 | 43/92 |
| attribution: symmetry (W1S / W1) | 1.696 | 1.619–1.824 | 68/92 |
| operational / water-filling without symmetry (O1 / W1) | 0.990 | 0.987–0.993 | 23/92 |
| O1S / A3 | 2.628 | 2.168–2.887 | 92/92 |
| T1S / A2 | 2.705 | 2.175–2.873 | 92/92 |

By cohort (P1 bulk / P3b slabs):

| ratio | P1 median (wins/n) | P3b median (wins/n) |
|---|---|---|
| O1S/W1S | 0.977 (8/60) | 0.982 (7/32) |
| W1S/T1S | 1.289 (60/60) | 1.601 (32/32) |
| W1S/A3 | 3.064 (60/60) | 2.241 (32/32) |
| W1S/A1 | 4.970 (60/60) | 4.175 (32/32) |
| W1S/A6 | 44.790 (60/60) | 70.127 (32/32) |
| W1S/W1 | 1.912 (45/60) | 1.560 (23/32) |

Symmetry gain W1S/W1 by number of grid operations:

- 1 operations: median 1.000 (n = 18)
- 2-8 operations: median 1.728 (n = 49)
- 9-24 operations: median 2.529 (n = 14)
- >24 operations: median 1.646 (n = 11)

## tau_H = 1e-08

| ratio (CR) | median | 95% CI | wins |
|---|---|---|---|
| operational / water-filling, same writer (H1) | 1.003 | 1.001–1.006 | 64/92 |
| water-filling / truncation, same writer (H2) | 1.580 | 1.552–1.609 | 92/92 |
| W1S / revision-10 operational allocation A3 (H3) | 2.413 | 2.115–2.847 | 90/92 |
| W1S / revision-10 law A1 | 2.675 | 2.197–3.222 | 92/92 |
| W1S / revision-10 truncation A2 | 4.732 | 3.906–5.632 | 92/92 |
| W1S / best pointwise codec A6 | 11.218 | 8.879–13.593 | 92/92 |
| attribution: container + coder (L1 / A1) | 1.121 | 1.085–1.157 | 92/92 |
| attribution: water-filling (W1 / L1) | 1.004 | 1.002–1.011 | 70/92 |
| attribution: symmetry (W1S / W1) | 1.955 | 1.888–2.960 | 68/92 |
| operational / water-filling without symmetry (O1 / W1) | 1.008 | 1.004–1.015 | 72/92 |
| O1S / A3 | 2.422 | 2.117–2.951 | 92/92 |
| T1S / A2 | 2.598 | 2.357–3.428 | 92/92 |

By cohort (P1 bulk / P3b slabs):

| ratio | P1 median (wins/n) | P3b median (wins/n) |
|---|---|---|
| O1S/W1S | 1.001 (38/60) | 1.008 (26/32) |
| W1S/T1S | 1.539 (60/60) | 1.927 (32/32) |
| W1S/A3 | 2.898 (59/60) | 2.117 (31/32) |
| W1S/A1 | 3.035 (60/60) | 2.199 (32/32) |
| W1S/A6 | 11.778 (60/60) | 9.919 (32/32) |
| W1S/W1 | 2.825 (45/60) | 1.877 (23/32) |

Symmetry gain W1S/W1 by number of grid operations:

- 1 operations: median 1.000 (n = 18)
- 2-8 operations: median 1.940 (n = 49)
- 9-24 operations: median 4.569 (n = 14)
- >24 operations: median 3.167 (n = 11)

## Symmetry

Materials with a symmetry group used: 74/92; median group order 4.0; status counts {'OK': 91, 'closure fails on the density': 1}.

## Certified counts

L1_1e-06 92, L1_0.0001 92, L1_1e-08 92, W1_1e-06 92, W1_0.0001 92, W1_1e-08 92, W1S_1e-06 92, W1S_0.0001 92, W1S_1e-08 92, T1S_1e-06 92, T1S_0.0001 92, T1S_1e-08 92, O1_1e-06 92, O1_0.0001 92, O1_1e-08 92, O1S_1e-06 92, O1S_0.0001 92, O1S_1e-08 92
