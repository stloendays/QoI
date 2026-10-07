# Diagnosis of the four AECCAR loading failures of the QOAC-HB slab run

Diagnostic only. The recorded verdict of `analysis/qoac_hb_slab_20261007/` (confirmatory FAIL, 13/32 analysable) is
unchanged, and nothing in that directory was modified or rerun.

Date 2026-10-07. Script `diagnose_aeccar.py` (this directory). Environment: Python 3.12.14, numpy 2.4.6,
baderkit 0.10.2, pymatgen 2025.10.7 (the frozen stack of `893f931`, `requirements-external-e2e.txt`;
`diagnosis_environment.json`). Evidence tables: `aeccar_file_scan.csv` (one row per file) and
`aeccar_loader_results.csv` (one row per file and loader). The raw files are not committed.

## Method

For each of the 8 files (AECCAR0 and AECCAR2 of the 4 failed entries), plus both files of one entry that was analysed
and jointly certified in the slab run (`nomad-gPlluuEHW2ND`, control):

1. Downloaded from `https://nomad-lab.eu/prod/v1/api/v1/entries/<entry_id>/raw/<basename>`; byte count and SHA-256
   compared with the frozen listing `analysis/qoac_hb_slab_20261007/aeccar_sources.csv`.
2. Header read (species, counts, grid line). Every token of the first data block classified by a strict tokenizer:
   regular float, `NaN`, `Inf`, Fortran E-format with the `E` dropped (`0.123+193`, written by Fortran when the exponent
   has three digits), `*****` overflow, other. Values parsed against `nx*ny*nz`; non-finite, zero and negative counts;
   min and max; lines after the block checked for `augmentation occupancies` lines and for repeats of the grid line
   (extra spin blocks).
3. Loaded with baderkit `Grid.from_dynamic` (the parser of the slab adapter `run_joint_slab.parse_vasp_total`, and of
   `dev.build_grid` for NOMAD CHGCARs) and with pymatgen `Chgcar.from_file`; the returned arrays are compared with the
   strict scan.

## Results

All 10 downloads match the frozen listing in bytes and SHA-256. Every header grid equals the CHGCAR grid. No file has
augmentation-occupancy lines or a second (spin) block, and no file has `*****` or any other unclassified token.

| entry | file | bytes (gz) | grid (= CHGCAR) | values / grid | NaN | Fortran no-`E` (exponents) | zero | min | max | sum / N |
|---|---|---:|---|---:|---:|---|---:|---:|---:|---:|
| `nomad-IZPVe_A6_quS` | AECCAR0 | 149,832 | 60x84x480 | 2,419,200 / 2,419,200 | 2,419,200 | 0 | 0 | – | – | – |
| | AECCAR2 | 10,705,587 | 60x84x480 | 2,419,200 / 2,419,200 | 0 | 0 | 0 | -5.31e3 | 1.20e5 | 234.08 |
| `nomad-ViaCyatoI3FA` | AECCAR0 | 122,602 | 56x140x252 | 1,975,680 / 1,975,680 | 1,975,680 | 0 | 0 | – | – | – |
| | AECCAR2 | 13,702,551 | 56x140x252 | 1,975,680 / 1,975,680 | 0 | 0 | 0 | -3.61e2 | 3.28e4 | 148.00 |
| `nomad-DcwYU1UzKNe8` | AECCAR0 | 102,964 | 96x80x216 | 1,658,880 / 1,658,880 | 1,658,880 | 0 | 0 | – | – | – |
| | AECCAR2 | 11,502,532 | 96x80x216 | 1,658,880 / 1,658,880 | 0 | 0 | 0 | -1.28e2 | 2.35e4 | 136.00 |
| `nomad-hk3gUBk-5QN5` | AECCAR0 | 9,599,764 | 112x112x224 | 2,809,856 / 2,809,856 | 0 | 1,229,312 (+171 to +197) | 1,580,544 | -8.52e196 | 1.71e196 | -2.43e191 |
| | AECCAR2 | 17,857,135 | 112x112x224 | 2,809,856 / 2,809,856 | 0 | 0 | 0 | -4.88e2 | 1.82e4 | 88.00 |
| control `nomad-gPlluuEHW2ND` | AECCAR0 | 3,812,840 | 64x64x180 | 737,280 / 737,280 | 0 | 0 | 0 | -4.35e-5 | 4.80e7 | 250.08 |
| | AECCAR2 | 2,253,102 | 64x64x180 | 737,280 / 737,280 | 0 | 0 | 0 | -4.42e-1 | 6.65e4 | 40.17 |

sum / N is the sum of the values divided by the number of grid points (the electron count in VASP's rho x V
convention).

`nomad-hk3gUBk-5QN5` AECCAR0, in detail: every regular float token is exactly zero (1,580,544), and every other token
is a no-`E` token (1,229,312). The non-zero values all have magnitude between 4.94e170 and 8.52e196, and 612,201 of
them are negative. The first data line reads `0.65466110724+193 -.65526215870+193 0.65586654126+193 -.65647524294+193
0.65708927968+193`.

### Loaders

| entry | file | baderkit `Grid.from_dynamic` | pymatgen `Chgcar.from_file` |
|---|---|---|---|
| `nomad-IZPVe_A6_quS` | AECCAR0 | returns 60x84x480, all 2,419,200 values NaN | returns 60x84x480, all NaN |
| `nomad-ViaCyatoI3FA` | AECCAR0 | returns 56x140x252, all 1,975,680 NaN | returns 56x140x252, all NaN |
| `nomad-DcwYU1UzKNe8` | AECCAR0 | returns 96x80x216, all 1,658,880 NaN | returns 96x80x216, all NaN |
| `nomad-hk3gUBk-5QN5` | AECCAR0 | raises `ValueError: string or file could not be read to its end due to unmatched data` | raises `ValueError: could not convert string to float: '0.65466110724+193'` |
| all four | AECCAR2 | returns the CHGCAR grid, all finite, identical to the strict scan | same |
| control | AECCAR0, AECCAR2 | returns 64x64x180, all finite, identical to the strict scan | same |

Where the slab run failed:
- the three all-NaN AECCAR0 files load; AECCAR0 + AECCAR2 is all NaN; HB v2's check
  `ae.shape != chg.shape or not np.all(np.isfinite(ae))` (`run_joint_v2.py` line 245) raises `invalid AECCAR`;
- `nomad-hk3gUBk-5QN5` AECCAR0 raises inside baderkit's `np.fromstring` at the first no-`E` token, which is the
  slab run's `ValueError`.

## Classification

| entry | class | evidence |
|---|---|---|
| `nomad-IZPVe_A6_quS` | data defect | published AECCAR0: all 2,419,200 values are the literal token `NaN` |
| `nomad-ViaCyatoI3FA` | data defect | published AECCAR0: all 1,975,680 values are `NaN` |
| `nomad-DcwYU1UzKNe8` | data defect | published AECCAR0: all 1,658,880 values are `NaN` |
| `nomad-hk3gUBk-5QN5` | data defect | published AECCAR0: all 1,229,312 non-zero values have magnitude 4.94e170–8.52e196 (612,201 negative); sum / N = -2.43e191 |

For `nomad-hk3gUBk-5QN5` the token syntax is legal Fortran output, and neither Python loader reads it. A loader that
reads it returns the values above. They are finite (largest magnitude 8.52e196 < 1.8e308), so HB v2's `invalid AECCAR`
check would pass and Henkelman Bader would receive a reference with 612,201 negative values of magnitude at least
4.94e170. The file is unusable as a Bader reference whichever parser reads it, so it is a data defect and not a parser
defect.

The AECCAR2 files of all four entries are valid and load identically with both parsers.

## Consequence for Part B

No parser defect, so no adapter fix: `analysis/qoac_hb_slab_20261007/run_joint_slab.py` is used unchanged. Because
data defects exist, the new cohort's protocol declares an input-validity check before the draw: both AECCAR files must
parse with the adapter's parser (baderkit `Grid.from_dynamic`) to the CHGCAR grid with all-finite values. This check
rejects all four failure files above: the three all-NaN files fail finiteness and the `hk3gUBk-5QN5` file fails the
parse.
