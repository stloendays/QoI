# QOAC-B2 complete 50-material result

Date: 2026-10-05

Status: descriptive combination of the 12-material engineering panel and the independently frozen 38-material holdout. Confirmatory inference remains based on the 38-material holdout alone.

## Primary contract

- exact AECCAR partition;
- Bader tolerance: 1e-3 e;
- auxiliary CHGCAR budget: kappa = 4 relative to the realized Linf of each material's best frozen generic Bader-certified G1 baseline;
- projected candidate selected only from the pre-existing WP-G codec/tolerance ladder;
- complete basin-sum side channel counted in bytes.

## Combined population result

Across all 50 analyzable all-electron-reference materials:

- actual Bader error: **50/50 = 0**;
- basin reassignment: **50/50 = 0**;
- compression-ratio wins over the best frozen G1 baseline: **45/50**;
- median CR ratio: **1.861x**;
- P05: **0.9995x**;
- P25: **1.696x**;
- P75: **2.136x**;
- P95: **8.216x**;
- minimum: **0.9967x**;
- maximum: **10.978x**;
- median final-Linf / baseline-Linf ratio: **3.060x**;
- maximum side-channel fraction: **0.999%**.

Selected projected candidates use SZ3 for 37/50 materials and SPERR for 13/50.

## Evidence hierarchy

Engineering development:
- 12 materials;
- primary kappa=4: 11/12 wins;
- median CR ratio 1.782x;
- actual Bader error 0 for 12/12.

Frozen holdout:
- 38/38 analyzable, zero pipeline failures;
- 34/38 wins;
- median CR ratio 1.865x;
- bootstrap 95% CI [1.759, 1.985];
- actual Bader error 0 for 38/38;
- zero reassignment for 38/38;
- all pre-frozen confirmatory criteria passed.

The 50-material combined statistics are descriptive and do not replace the frozen holdout inference.

## Mechanistic conclusion

QOAC-B1 showed that an explicit basin-mean / zero-sum-residual transform is compression-hostile even though it is mathematically aligned with the Bader nullspace.

QOAC-B2 instead leaves the generic compressor in its native smooth spatial representation and applies the exact fixed-basin constraint only after decoding. For each basin, the uniform correction is simultaneously the minimum-Linf and minimum-L2 correction that restores the exact discrete basin sum.

The validated Bader design principle is therefore:

    preserve the compression-friendly field representation;
    enforce the low-dimensional scientific constraint by projection;
    certify the corrected object.

This is distinct from the Hartree design, where the linear operator directly changes transform-domain bit allocation.

## Next problem

The remaining Bader-specific instability is the partition-defining AECCAR field. Existing WP-I evidence shows that reference-only perturbation reproduces the joint perturbation floor and basin reassignment essentially exactly.

QOAC-B3 will therefore investigate whether the exact discrete Bader partition can be stored as a compact, lossless sufficient-state side channel instead of requiring a lossy AECCAR reconstruction to reproduce the topology.
