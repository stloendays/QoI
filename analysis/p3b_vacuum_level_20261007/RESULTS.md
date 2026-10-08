# P3b vacuum-level (work-function) error — results

CI run 37598559834, a single run that completed with 34/34 jobs successful. Protocol `47b110a` (frozen before any
decoded stream), sentinel `0e584d3`, results `4946f9f`. Definitions are in `PROTOCOL.md`; there are no deviations
after the run started (`DEVIATIONS.md`).

- Population: 32/32 slabs loaded, and every source matched the manifest SHA-256 and byte count. Preflight also checked
  the manifest and the recorded `part_a_rows.csv` against their committed SHA-256.
- Streams: 480 planned (32 slabs x 5 arms x 3 tau), 480 recorded, 480 reproduced exactly (0 excluded).
- Vacuum: 27/32 slabs qualify; 5 do not (section 4). n evaluated = 27 for every arm x tau.
- |Delta Phi| is in meV. P95 uses `numpy.quantile(..., 0.95, method="linear")`. The fractions are strict (< 1 meV,
  < 10 meV) over n evaluated.

## 1. |Delta Phi| per arm

### tau = 1e-6

| arm | n | median | P95 | max | < 1 meV | < 10 meV |
|---|---|---|---|---|---|---|
| A1 closed-form law | 27 | 0.00401 | 0.0211 | 0.0452 | 27/27 (1.000) | 27/27 (1.000) |
| A2 spectral truncation | 27 | 0.552 | 1.86 | 2.97 | 19/27 (0.704) | 27/27 (1.000) |
| A3 operational optimum | 27 | 0.00396 | 0.0136 | 0.0339 | 27/27 (1.000) | 27/27 (1.000) |
| A5 operator-blind RD optimum | 27 | 0.283 | 1.58 | 2.50 | 23/27 (0.852) | 27/27 (1.000) |
| A6 best of ZFP/SZ3/SPERR | 27 | 0.340 | 1.85 | 2.16 | 19/27 (0.704) | 27/27 (1.000) |

### tau = 1e-4

| arm | n | median | P95 | max | < 1 meV | < 10 meV |
|---|---|---|---|---|---|---|
| A1 | 27 | 1.09 | 5.34 | 6.06 | 12/27 (0.444) | 27/27 (1.000) |
| A2 | 27 | 41.0 | 197 | 385 | 0/27 (0.000) | 2/27 (0.074) |
| A3 | 27 | 1.72 | 6.72 | 8.26 | 9/27 (0.333) | 27/27 (1.000) |
| A5 | 27 | 21.2 | 265 | 347 | 1/27 (0.037) | 10/27 (0.370) |
| A6 | 27 | 35.5 | 158 | 238 | 0/27 (0.000) | 2/27 (0.074) |

### tau = 1e-8

| arm | n | median | P95 | max | < 1 meV | < 10 meV |
|---|---|---|---|---|---|---|
| A1 | 27 | 1.04e-5 | 3.89e-5 | 8.13e-5 | 27/27 (1.000) | 27/27 (1.000) |
| A2 | 27 | 0.00386 | 0.0117 | 0.0173 | 27/27 (1.000) | 27/27 (1.000) |
| A3 | 27 | 1.53e-5 | 1.58e-4 | 2.02e-4 | 27/27 (1.000) | 27/27 (1.000) |
| A5 | 27 | 0.00270 | 0.0188 | 0.0243 | 27/27 (1.000) | 27/27 (1.000) |
| A6 | 27 | 0.00418 | 0.0136 | 0.0430 | 27/27 (1.000) | 27/27 (1.000) |

## 2. Descriptive extras (meV)

The window columns give max |planar-averaged Delta V_H| over the vacuum window. tau * V_ref is the absolute Hartree
RMS bound of a stream certified at tau, with V_ref = `vref_rms_eV_hist`.

| tau | arm | window max, median | window max, maximum | tau * V_ref, median |
|---|---|---|---|---|
| 1e-6 | A1 | 0.0900 | 0.452 | 0.641 |
| 1e-6 | A2 | 0.617 | 3.79 | 0.641 |
| 1e-6 | A3 | 0.0815 | 0.403 | 0.641 |
| 1e-6 | A5 | 0.446 | 3.03 | 0.641 |
| 1e-6 | A6 | 0.588 | 2.78 | 0.641 |
| 1e-4 | A1 | 15.3 | 59.0 | 64.1 |
| 1e-4 | A2 | 64.7 | 447 | 64.1 |
| 1e-4 | A3 | 15.0 | 58.2 | 64.1 |
| 1e-4 | A5 | 28.7 | 443 | 64.1 |
| 1e-4 | A6 | 60.1 | 298 | 64.1 |
| 1e-8 | A1 | 4.39e-4 | 1.63e-3 | 6.41e-3 |
| 1e-8 | A2 | 6.05e-3 | 2.08e-2 | 6.41e-3 |
| 1e-8 | A3 | 4.73e-4 | 1.79e-3 | 6.41e-3 |
| 1e-8 | A5 | 3.70e-3 | 2.70e-2 | 6.41e-3 |
| 1e-8 | A6 | 6.21e-3 | 4.74e-2 | 6.41e-3 |

A6 codec used on the 27 evaluated slabs:
- tau = 1e-6: ZFP 24, SPERR 3;
- tau = 1e-4: ZFP 16, SZ3 6, SPERR 5;
- tau = 1e-8: ZFP 19, SZ3 8.

max |delta_electrons| over evaluated streams: A1, A2, A3 and A5 <= 4.6e-13 e; A6 0.187 e.

## 3. Reproduction check

Tolerance (PROTOCOL.md section 3): |Delta bytes| <= 16, both Hartree relative errors within 1e-6 relative, and both
< tau. Exact means identical bytes and errors within 1e-12. Route R regenerates from the recorded parameter string;
route S reruns `run_engineering.material` unchanged.

| tau | arm | recorded | R reproduced | R exact | S reproduced | S exact | used exact | via R | via S | not reproduced |
|---|---|---|---|---|---|---|---|---|---|---|
| 1e-6 | A1 | 32 | 7 | 0 | 32 | 32 | 32 | 0 | 32 | 0 |
| 1e-6 | A2 | 32 | 0 | 0 | 32 | 32 | 32 | 0 | 32 | 0 |
| 1e-6 | A3 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 0 | 0 |
| 1e-6 | A5 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 0 | 0 |
| 1e-6 | A6 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 0 | 0 |
| 1e-4 | A1 | 32 | 32 | 0 | 32 | 32 | 32 | 0 | 32 | 0 |
| 1e-4 | A2 | 32 | 7 | 0 | 32 | 32 | 32 | 0 | 32 | 0 |
| 1e-4 | A3 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 0 | 0 |
| 1e-4 | A5 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 0 | 0 |
| 1e-4 | A6 | 32 | 25 | 22 | 32 | 32 | 32 | 22 | 10 | 0 |
| 1e-8 | A1 | 32 | 4 | 0 | 32 | 32 | 32 | 0 | 32 | 0 |
| 1e-8 | A2 | 32 | 0 | 0 | 32 | 32 | 32 | 0 | 32 | 0 |
| 1e-8 | A3 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 0 | 0 |
| 1e-8 | A5 | 32 | 32 | 32 | 32 | 32 | 32 | 32 | 0 | 0 |
| 1e-8 | A6 | 32 | 23 | 23 | 32 | 32 | 32 | 23 | 9 | 0 |

Totals:
- route S: 480/480 exact;
- route R: 322/480 within tolerance, 269/480 exact;
- streams used: 480/480 exact, 269 via R and 211 via S;
- not reproduced: 0.

Where both routes are exact (269 streams), Delta Phi_R = Delta Phi_S, with difference 0. Where R reproduced only
within tolerance (53 streams), max |Delta Phi_R - Delta Phi_S| = 0.0176 meV.

## 4. Vacuum windows and reference Hartree RMS

Rule: vacuum planes have a planar-averaged reference density < 1e-3 of its maximum; the run must be at least 3.0 A; the
window is its central half. In the 27 qualifying slabs the normal is axis 2. The vacuum run is 3.03–27.08 A (median
6.71 A) and the window 1.55–13.64 A.

Five slabs do not qualify and are excluded from the vacuum statistics; their 75 streams are regenerated and reproduced
exactly:

| material_id | formula | longest vacuum run (axes 0 / 1 / 2, A) |
|---|---|---|
| `nomad-DfpU7vvNQ-Vo` | Lu2Br2O | 0 / 0 / 0 |
| `nomad-deLeLsqokf9I` | Nb2Se3 | 0 / 0 / 1.59 |
| `nomad-bEMTXRvdLPTu` | EuS | 0 / 0 / 2.83 |
| `nomad-DcwYU1UzKNe8` | Ti(PO4)2 | 0 / 0 / 0 |
| `nomad-hk3gUBk-5QN5` | Ga2Te3 | 0 / 0 / 0 |

V_ref = `vref_rms_eV_hist` = (k_e / V_cell) r_h, the denominator of the certified historical relative error.
- Over the 32 slabs it runs 63.6–3273 eV (median 528 eV).
- `vref_rms_eV_safe` equals it to 4.4e-16 relative.
- The independent 3-D eV computation `vref_rms_eV_own3d` agrees to 4.4e-16 relative.

| material_id | formula | grid | V_ref RMS (eV) | vacuum run (A) | window (A) | qualifies |
|---|---|---|---|---|---|---|
| `nomad-G-yDaY8qmw5_` | TiO2 | 40x108x360 | 1584.3 | 19.11 | 9.61 | yes |
| `nomad-vbsqs8Js2fzW` | ZnSiN2 | 56x56x500 | 3273.3 | 21.56 | 10.93 | yes |
| `nomad-slKw7W6vu-8S` | HRu16(CO16)2 | 96x96x420 | 966.1 | 10.40 | 5.23 | yes |
| `nomad-wpVo8yTF7eRr` | Sr8Fe5Re5O28 | 84x84x384 | 700.4 | 4.87 | 2.47 | yes |
| `nomad-IZPVe_A6_quS` | Sr5Ti7O19 | 60x84x480 | 1331.2 | 10.84 | 5.46 | yes |
| `nomad-uxkQqRHBpSox` | Ti4C3 | 80x40x320 | 751.5 | 10.08 | 5.04 | yes |
| `nomad-a3nHf0dBA8BK` | Cu44Ni | 100x100x240 | 643.7 | 4.81 | 2.52 | yes |
| `nomad-DfpU7vvNQ-Vo` | Lu2Br2O | 60x60x216 | 63.6 | 0.00 | 0.00 | no |
| `nomad-uI3dGHZQPhUQ` | VCu44 | 100x100x240 | 640.8 | 4.81 | 2.52 | yes |
| `nomad-vGEh154443lz` | ZnGeN2 | 56x64x432 | 2243.7 | 18.54 | 9.42 | yes |
| `nomad-3wOOZLfv7lb_` | Ga11(HN5)2 | 72x108x420 | 1675.0 | 12.81 | 6.44 | yes |
| `nomad--QPBOSBRk9z4` | Ga7HN8 | 80x48x448 | 1949.2 | 12.68 | 6.42 | yes |
| `nomad-C-8aMchGaf7P` | HfC | 96x96x192 | 434.3 | 6.33 | 3.32 | yes |
| `nomad-ZzgnSZOSnag2` | In3SbTe2 | 64x72x360 | 279.9 | 3.03 | 1.55 | yes |
| `nomad-TSS0Y8O9xp8A` | Ga16(HN5)3 | 108x48x400 | 1523.6 | 11.33 | 5.74 | yes |
| `nomad-deLeLsqokf9I` | Nb2Se3 | 56x56x216 | 174.3 | 1.59 | 0.82 | no |
| `nomad-OLo5BGMUENyW` | ZrC | 96x96x196 | 484.1 | 6.55 | 3.37 | yes |
| `nomad-BLbUQWtMdS99` | ZnSnN2 | 56x72x480 | 2183.9 | 19.99 | 10.04 | yes |
| `nomad-bEMTXRvdLPTu` | EuS | 64x64x216 | 194.8 | 2.83 | 1.52 | no |
| `nomad-ViaCyatoI3FA` | Ti3H2O7 | 56x140x252 | 346.1 | 5.36 | 2.71 | yes |
| `nomad-gPlluuEHW2ND` | SnSe | 64x64x180 | 123.0 | 3.69 | 1.95 | yes |
| `nomad-DcwYU1UzKNe8` | Ti(PO4)2 | 96x80x216 | 142.5 | 0.00 | 0.00 | no |
| `nomad-Lt4FFQvyPw8a` | NbC | 96x96x192 | 496.5 | 6.43 | 3.27 | yes |
| `nomad-O_yuQGDsVTCx` | Ga8HN8 | 80x48x448 | 1915.6 | 10.77 | 5.42 | yes |
| `nomad-hYJ7QAq46DqB` | Cu44H3PtC | 100x100x240 | 635.8 | 3.44 | 1.76 | yes |
| `nomad-hk3gUBk-5QN5` | Ga2Te3 | 112x112x224 | 99.9 | 0.00 | 0.00 | no |
| `nomad-BGv3HMr4F-YZ` | Ti3C2 | 80x40x280 | 499.0 | 8.72 | 4.43 | yes |
| `nomad-NOOih6wwVxT5` | P | 56x72x540 | 302.4 | 27.08 | 13.64 | yes |
| `nomad-CVWFkEoST7FX` | SbPb3S4 | 64x64x280 | 174.6 | 3.19 | 1.69 | yes |
| `nomad-HCM86CvqrAFu` | MoC | 96x96x192 | 554.2 | 6.55 | 3.42 | yes |
| `nomad-bUeGvZ6vwC_l` | TiC | 96x96x192 | 500.4 | 6.71 | 3.40 | yes |
| `nomad-g7Z9ilV401H7` | TaC | 96x96x192 | 501.5 | 6.42 | 3.26 | yes |

## 5. Failures

- Material failures (download, SHA-256, load): 0/32.
- Route-level failures (route R or route S raising, or `material` reporting a failure): 0. `results/failures.csv` is
  empty.
- Streams not reproduced: 0/480.
- Slabs without a qualifying vacuum: 5/32 (75 streams), excluded from section 1 only.

## 6. Provenance and files

- Branch `research/p3b-vacuum-level-20261007`; base `87b3a65` (`paper/nc-reopen-20261007`).
- Commits: protocol `47b110a`, sentinel `0e584d3`, CI result `4946f9f`.
- CI run 37598559834 (`.github/workflows/p3b_vacuum_level.yml`). Recorded streams are from P3b law CI run 37493518929,
  result commit `eaa3267`.
- Files in `analysis/p3b_vacuum_level_20261007/`:
  - `PROTOCOL.md`, `DEVIATIONS.md`, `RESULTS.md`;
  - code: `vacuum_level.py`, `run_vacuum_level.py`, `aggregate_vacuum_level.py`, `test_vacuum_level.py` (17 tests);
  - `results/per_slab_dphi.csv` (480 rows: slab x arm x tau, with both routes);
  - `results/slabs.csv`, `results/summary.csv`, `results/SUMMARY.json`, `results/failures.csv`;
  - `results/RUN_ID`, `results/pip_freeze_shard.txt`.
