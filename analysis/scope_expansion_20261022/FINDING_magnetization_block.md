# Finding — the archive estimates leave out the magnetization block (2026-10-22)

Status: measured, needs the owner's decision. Nothing in the manuscript has been changed.

## What was measured

- **S0, census.** Runs over 210 objects: the MP rows of the development panel plus the P1/P2 engineering
  sets (`results/s0_spin_census/`).
  - All 210 carry a magnetization block, `data.diff`; none has an all-zero block.
  - 87 have at least one atom with |mu| ≥ 0.1 mu_B (descriptive on-grid partition).
- **S0b, the 300 archive objects.** Re-reads the same stratified 300-object sample used by WP-F and by the
  archive-Hartree run (`results/s0b_archive_spin_bytes/`).
  - 300/300 objects measured and 300/300 carry the block.
  - Median share of the serialized text: 0.521.
  - Median lossless (zlib-6, float64) size of m relative to that of rho: 1.020. The block of a non-magnetic
    object is numerical noise and compresses no better than the density itself.
- **Coverage of the estimates.** Both archive estimates compute their certified and lossless stores from the
  total block only (`run_wpf.py`: `field = grid.total`; `raw64_bytes = 8 * field.size`). The denominator,
  however, is the full gzipped JSON, which contains both blocks. The manuscript and SI never mention the
  magnetization block.

## Sensitivity

The aggregation script first reproduces the published point estimates exactly from the committed object
tables: Bader 4.367 at 1e-3 e and Hartree law 356.04 at 1e-6. It then recomputes them with the same
stratified expansion estimator. Bootstrap intervals use seed 20261022, so they differ slightly from the
published ones.

| contract | tolerance | R as published | R vs the charge-density block only | R if m is kept losslessly |
|---|---|---|---|---|
| Bader | 1e-3 e | 4.37 | 2.10 [1.76, 2.61] | 1.40 [1.34, 1.47] |
| Bader | 1e-2 e | 8.99 | 4.32 [3.02, 6.78] | 1.68 [1.59, 1.75] |
| Hartree law | 1e-6 | 356 | 171 [156, 188] | 1.94 [1.93, 1.96] |
| Hartree law | 1e-4 | 1,751 | 841 [795, 893] | 1.95 [1.94, 1.97] |
| pointwise | 1e-6 | 35.0 | 16.8 [15.8, 18.0] | 1.85 [1.84, 1.87] |

- **"Block only"** is the like-for-like reading of a charge-density claim: the bytes of the file attributable
  to the total block, times the published ratio.
- **"m lossless"** is what happens if the archive must still serve the magnetization block and nothing better
  than lossless storage is available for it. Then m dominates, and every writer lands near 2×.

## Why it matters

- **A reviewer can check this in minutes.** The abstract's "would shrink the 8.50 TB Materials Project archive
  4.4-fold … 356-fold" reads as a statement about the archive as served.
- **Ratios between writers are unaffected.** The law vs pointwise factor (10.2×) does not change, because both
  writers store the same block.
- **The fix is also the scope expansion.** Per-atom magnetic moments are a routine downstream analysis of the
  same file. A certified, contract-qualified store for m (WS-S1, running) turns the archive estimate into a
  statement about the whole served object, and adds a second physical field to the paper.

## Options (owner's decision)

1. **Reword, smallest change.** Make the archive claims refer to the charge-density content: Bader 2.1×
   (1e-3 e) and Hartree 171× (1e-6). Add one Methods sentence saying the magnetization block is excluded.
2. **Keep whole-archive claims.** Store m under a moment contract (S1 engineering, then an archive rerun of
   (rho, m)), and report both the charge-density-only and whole-object ratios.
3. **Do both.** Option 1 now for correctness; option 2 as the extension.
