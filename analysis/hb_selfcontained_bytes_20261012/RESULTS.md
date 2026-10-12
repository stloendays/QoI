# Self-contained joint Hartree + Bader storage on the P2 confirmatory crystals — results

Protocol `d084d4a` (frozen 2026-10-12 03:22 UTC), implementation `c6be2e5`, run started by `d71c08b`: GitHub Actions run
38201584592, 8 shards, all jobs successful. Numbers below are copied from `results/summary.csv`,
`results/materials.csv` and `results/SUMMARY.json`; the main session recomputed the tau_B = 1e-4 e values from
`results/materials.csv` and the committed HB v2 files and found them identical.

## Label maps (48 materials)

- Round trip exact in 48/48. Per-atom charges summed over the stored labels match the binary's `ACF.dat` in 48/48
  (largest difference 5.0e-7 e; tolerance 1e-5 e). No material is unaccounted.
- Stored label bytes (xz stream plus 16-byte header): median 11,774 (95% CI 10,052–22,416), range 1,180–124,904.
  Context-model estimate: median 12,752.5.

## Self-contained storage, tau_B = 1e-4 e

| metric | median | 95% CI | min | max |
|---|---:|---|---:|---:|
| CR_sc, R3 | 188.2 | 171.9–200.1 | 66.3 | 426.2 |
| CR_sc, J | 159.6 | 138.6–166.9 | 50.0 | 336.9 |
| CR_sc, T1 | 140.7 | 112.5–155.9 | 37.5 | 388.8 |
| CR_sc, GF | 17.98 | 15.67–22.49 | 10.50 | 37.60 |
| U_sc = CR_sc(R3) / best other base | 1.168 | 1.150–1.201 | 1.040 | 1.410 |
| CR_sc(R3) / CR_sc(GF) | 10.23 | 8.36–11.78 | 3.37 | 22.09 |
| O_sc = (R3 joint stream + labels) / Hartree-only stream | 1.670 | 1.539–1.741 | 1.157 | 4.414 |
| partition share of the R3 archive | 0.401 | 0.347–0.426 | 0.136 | 0.773 |

R3 has the highest self-contained CR in 48/48 materials. GP has no certified joint stream in the HB v2 file and
enters no comparison.

At tau_B = 1e-3 e every value equals the 1e-4 e value except the CI bounds (R3 CR_sc 188.2, 171.9–202.3). At 1e-5 e:
R3 CR_sc 188.0 (171.1–198.8), U_sc 1.171 (1.148–1.201; 48/48 wins), R3/GF 10.23, O_sc 1.674.

## Reading

Certifying the Bader charges adds no stream bytes (HB v2: overhead 1.000). Carrying the partition as a lossless
label map makes the archive self-contained at a median 11.8 kB per material; R3 then keeps a median CR of 188,
10.2-fold the pointwise codecs and above every other base in 48/48 materials.
