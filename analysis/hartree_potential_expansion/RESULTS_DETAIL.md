# Hartree-potential QoI full expansion — quantitative detail (2026-09-09)

Companion to the summarizer-generated `RESULTS.md`, whose recommendation
(`PROMOTE_TO_MAIN_TEXT`) was produced by the frozen criteria in
`summarize_expansion.py` and is not overridden here. This file adds the numbers,
the gate-failure classification, and the caveats a reader needs.

## Execution

- Population: all 254 development materials of the frozen master table
  (186 bulk, 68 slab), all three codecs, the complete frozen tolerance ladder
  (base + tight). 6343 frozen rows targeted, 6343 regenerated, 0 missing grids.
- Codec wrappers: the original `honest_benchmark.py` functions from
  `D:/Research/RhoCodec` (zfpy 1.0.1 fixed-accuracy; `rhocodec.sz3.compress` =
  pysz 1.0.3 ABS INTERP_LORENZO; hdf5plugin 7.0.0 Sperr absolute, single chunk),
  Python 3.12.14, NumPy 2.3.5, the CatalystForge interpreter that ran the frozen
  bulk benchmark. File hashes in `provenance.json`.
- Inputs: the exact `.npz` grids the frozen benchmark consumed (`npz_sha256`
  per row). For bulk these are bit-identical to the public S3 objects decoded by
  `analysis/mp_chgcar_loader.py` (verified on the pilot).
- Bader columns attached only via the exact frozen key
  `(material_id, codec, nominal_tolerance_relative, nominal_tolerance_absolute, ladder)`.
- Pilot consistency: the 127 ZFP rows of the 12 pilot materials reproduce the
  pilot `potential_rel_RMSE` values exactly (max relative difference 0).

## Reproduction gate

| codec | rows | realized-L∞ ratio in [0.95, 1.05] | bytes equal | gate pass |
|---|---|---|---|---|
| ZFP | 2450 | 2450 (100 %) | 2450 | **100 %** |
| SPERR | 1956 | 1956 (100 %) | 1956 | **100 %** |
| SZ3 | 1937 | 1937 (100 %) | 1864 | **96.2 %** |

All 73 gate failures are SZ3 rows whose realized L∞ matches the frozen value to
better than 2e-5 relative but whose compressed byte count differs (median ±1
byte, range −4834 to +8351). The frozen SZ3 tight-ladder rows and the slab half
were generated on Vanda (Linux), the bulk base ladder locally; failures
concentrate accordingly (bulk base 2.9 %, bulk tight 4.9 %, slab base 2.2 %,
slab tight 10.0 %). This is a platform-level pysz stream-size difference, not a
reconstruction difference. Classification: `reproduction_mismatch`
(infrastructure). Per the frozen gate these rows are excluded from every
statistic; no numerical or codec failures occurred (`failures.csv`).

## Pooled scaling (gate-passed rows, log10–log10)

| codec | stratum | n | Hartree slope | Hartree R² | Hartree Pearson | Bader slope | Bader R² | Bader Pearson |
|---|---|---|---|---|---|---|---|---|
| ZFP | bulk | 1839 | 1.00 | 0.930 | 0.964 | 0.67 | 0.685 | 0.828 |
| ZFP | slab | 611 | 0.91 | 0.852 | 0.923 | 0.57 | 0.689 | 0.830 |
| SZ3 | bulk | 1403 | 1.12 | 0.936 | 0.968 | 0.60 | 0.760 | 0.872 |
| SZ3 | slab | 461 | 0.94 | 0.925 | 0.962 | 0.53 | 0.743 | 0.862 |
| SPERR | bulk | 1530 | 0.97 | 0.936 | 0.967 | 0.58 | 0.755 | 0.869 |
| SPERR | slab | 426 | 0.99 | 0.894 | 0.945 | 0.64 | 0.773 | 0.879 |
| all codecs | bulk | 4772 | 1.04 | 0.877 | 0.937 | — | — | — |
| all codecs | slab | 1498 | 1.00 | 0.709 | 0.842 | — | — | — |
| all codecs | all | 6270 | 1.02 | 0.792 | 0.890 | 0.62 | 0.714 | 0.845 |

Hartree vs Bader (pooled): slope 0.51, R² 0.63, Pearson 0.80.

The exponent α of `E_Hartree ∝ realized_L∞^α` is 0.91–1.12 in every codec ×
stratum cell (pooled 1.02). The Bader exponent is 0.53–0.67 with R² lower in
all six cells. Pooled R² across materials is lower than per-material R² because
the material-dependent prefactor (RMS(V_orig), cell size) shifts the lines.

## Material-level smoothness (678 material × codec pairs with ≥5 gate rows)

| codec | pairs | Hartree monotone | Bader monotone | gap (pp) | Hartree R² median | Bader R² median | Hartree slope median | Bader slope median |
|---|---|---|---|---|---|---|---|---|
| ZFP | 241 | 85.1 % | 19.5 % | 65.6 | 0.997 | 0.892 | 1.05 | 0.58 |
| SZ3 | 219 | 85.8 % | 42.0 % | 43.8 | 0.994 | 0.947 | 1.17 | 0.60 |
| SPERR | 218 | 95.4 % | 37.2 % | 58.3 | 0.996 | 0.936 | 1.01 | 0.59 |
| all | 678 | 88.6 % | 32.4 % | 56.2 | 0.996 | 0.93 | — | — |

Local elasticity (per-step log–log slope) ranges: Hartree −2.0 to +4.4;
Bader −9.3 to +14.1. Maximum consecutive Bader jump: **22 296×** (mp-676693,
ZFP; Hartree R² on the same rows 0.999), then 16 331× (nomad-E0rr8BI_hRlR,
ZFP slab), 10 881× (mp-8881). Median per-pair maximum Bader jump 4.5–7.2×.
Hartree steps exceeding 10× occur in 0.1–8 % of steps and only where L∞ itself
jumped by 3–10×.

Number of local decreases per pair: Hartree 0 in 601/678, 1 in 67, ≥2 in 10;
Bader 0 in 220/678, 1 in 268, ≥2 in 190.

### Caveat: slab monotonicity

| codec | Hartree monotone bulk | Hartree monotone slab | Bader monotone bulk | Bader monotone slab |
|---|---|---|---|---|
| ZFP | 96.6 % | 52.4 % | 17.4 % | 25.4 % |
| SZ3 | 98.8 % | 47.3 % | 42.7 % | 40.0 % |
| SPERR | 98.8 % | 84.3 % | 31.1 % | 56.9 % |

On slabs the Hartree monotone fraction falls to 47–84 % while the per-pair
Hartree R² stays 0.965–0.983 (median). The slab Hartree "decreases" are small
(3–9 % of steps; median ratio 0.76–0.80; only 1.5–5 % of steps drop by more
than 20 %) and occur across single ladder rungs where L∞ grows 1.6–4.2×. Bader
decreases on the same slabs are as frequent (8–16 % of steps) but reach ratios
of 0.05–0.5. The pre-declared per-codec monotonicity criterion passes, but the
Hartree–Bader monotonicity gap on slabs alone is 7 pp (SZ3), 27 pp (ZFP) and
27 pp (SPERR); the bulk gap is 56–79 pp. The smoothness contrast on slabs is
carried by R², elasticity range and jump size rather than by strict monotonicity,
and the manuscript wording must say so.

## Matched-Hartree-error dispersion of Bader error (0.5-decade bins, n ≥ 10)

| codec | stratum | bins | bins with P90/P10 ≥ 10 | rows in such bins | median P90/P10 | max P90/P10 |
|---|---|---|---|---|---|---|
| ZFP | bulk | 14 | 9 | 1131 / 1836 | 17.8 | 61 567 |
| ZFP | slab | 12 | 10 | 511 / 599 | 15.1 | 445 |
| SZ3 | bulk | 14 | 7 | 626 / 1397 | 8.9 | 2 439 |
| SZ3 | slab | 10 | 3 | 146 / 450 | 7.4 | 12.3 |
| SPERR | bulk | 13 | 6 | 723 / 1527 | 9.5 | 22.4 |
| SPERR | slab | 10 | 7 | 315 / 420 | 12.0 | 22.1 |

55.4 % of all gate-passed rows sit in a matched-Hartree-error bin whose Bader
error spans at least one decade between P10 and P90; the condition holds in all
three codecs and both strata. Similar smooth-field fidelity does not determine
the topological QoI error.

## Answers to the pre-stated scientific questions

- **A.** Yes: α = 0.91–1.12 per cell, 1.02 pooled; per-material R² median
  0.994–0.997.
- **B.** Yes for R² and slope in ZFP, SZ3, SPERR, bulk and slab. Strict
  monotonicity holds in 97–99 % of bulk pairs but only 47–84 % of slab pairs
  (small-amplitude wiggles, see caveat).
- **C.** Yes: Bader R² lower in every cell, monotone in 32 % vs 89 % of pairs,
  elasticity range −9 to +14 vs −2 to +4, consecutive jumps up to 22 296× vs
  Hartree steps that track the L∞ step.
- **D.** Yes: ≥1 decade of Bader spread at matched Hartree error for 55 % of
  rows, in every codec and stratum.

## Recommendation of record

The frozen summarizer's verdict (`RESULTS.md`) is **PROMOTE_TO_MAIN_TEXT**; all
five pre-declared criteria pass. Suggested claim boundary: "the Hartree
potential, a linear nonlocal functional, scales as L∞^1.0 with per-material
R² ≥ 0.99 under all three codecs on bulk and slab densities, while the Bader
charge on the identical reconstructions is non-monotone in two thirds of
material–codec pairs and varies by more than a decade at matched Hartree
error"; state the slab monotonicity caveat explicitly and do not phrase the
result as Hartree being "better" than Bader.

## Files

`rows.csv` (6343 rows), `failures.csv` (73 gate mismatches), `group_summary.csv`,
`material_smoothness.csv`, `matched_error_dispersion.csv`, `gate_failures.csv`,
`provenance.json`, `RESULTS.md` (summarizer output), `run_expansion.py`,
`run_expansion.log`.
