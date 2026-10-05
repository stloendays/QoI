# QOAC-H strongest-baseline study — results

Status: **COMPLETE.** 48 frozen confirmatory materials; T1 21,600 rows, M 3,600 rows, V 7,200 rows;
0 failures in every arm. T1 and V ran in run 37333223318 and M in run 37337260152 (amendment 2). MGARD was
built from upstream commit `ac53ff9cec8cf2dee08892f0400ae0ddb755b193` with TCLAP 1.4 headers. Certificate
(identical to the frozen confirmatory): historical and Nyquist-safe Hartree relative RMSE < 1e-6.

## Primary result — pre-declared band: advantage retained

R_new = CR_QOAC-H / best certified CR over T1 and M:
- **45/48 wins**, median **1.564x**, bootstrap 95% CI **[1.376, 1.622]**, minimum 0.843x.
- Bulk median 1.351x, slab median 1.571x.
- Every material had a certified new-baseline row.

The best new baseline is spectral truncation T1 in 48/48 materials.

## Per arm

| arm | median certified CR | QOAC-H / arm: wins, median (95% CI) |
|---|---|---|
| QOAC-H (frozen) | 383 | — |
| T1 spectral truncation | 233 | 45/48, 1.56x (1.38–1.62) |
| ZFP/SZ3/SPERR (frozen) | 22.1 | 48/48, 15.0x |
| M MGARD (best of s = inf, 0, -1; s = -1 selected in 36/48) | 16.0 | 48/48, 19.4x (16.4–24.0) |
| V stored Hartree potential (ZFP/SZ3/SPERR on V_H; contract-changing) | — | 48/48, 19.4x (16.5–21.2) |

Selected T1 cutoffs: q_c = 0.30 (18), 0.15 (17), 0.20 (9), 0.50 (4). T1 without a cutoff (q_c = 1, i.e.
uniform Fourier quantization) reaches median CR 87.8.

## Density fidelity of the certified streams (medians)

| | density Linf | density RMSE |
|---|---|---|
| QOAC-H | 1.89 | 0.096 |
| T1 | 2.82 | 0.148 |
| MGARD | 0.59 | — |

QOAC-H certifies at higher compression than T1 while also distorting the density less.

## Reading

1. Most of QOAC-H's 15x advantage over pointwise-error codecs comes from representing the density in the
   Hartree operator's eigenbasis and discarding the high-|G| modes. A two-parameter spectral truncation
   already reaches ~10x over ZFP/SZ3/SPERR.
2. The operator-derived continuous allocation Delta_G ∝ |G|^2 adds a further 1.56x over the best truncation
   (45/48 materials). This holds even though truncation had 9x the search opportunity, and QOAC-H also gives
   lower density error. This is the quantity that measures the value of the operator law itself.
3. MGARD with s <= -1 and storing V_H directly with pointwise codecs are both far weaker (~19x).

Within the frozen ladders, s = -1 was the weakest MGARD norm tested. More negative s values were not
evaluated.
