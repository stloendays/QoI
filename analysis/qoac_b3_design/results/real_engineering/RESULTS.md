# QOAC-B3 real-material engineering — results (descriptive; no pass/fail gate)

CI run 37492946467; the 12 fresh P2 engineering materials (`P2_ENGINEERING_MANIFEST.csv`); compiled Henkelman Bader
1.05, `-b ongrid -vac 0.001`, exact CHGCAR, reference = AECCAR0 + AECCAR2.

## Gate 0 — transcription vs compiled binary

- Partition (volnum): identical voxel for voxel in **11/11** materials with Gate 0 output; 0 mismatching voxels.
- Maxima: 3,339/3,339 matched.
- Every reference field is regular (R1 and R2: 0 violations).
- Atom map: identical in 9/11; minimum voxel agreement 97.9%.
- Literal transcription (run only for npoints <= 400,000): identical in 3/3.
- 1 material (mp-2302539) failed inside the Gate 0 code (a 74 GiB pairwise maxima array). This is an implementation
  defect of the comparison, not a partition disagreement. Its arms ran normally.

## Arms (12/12 materials each)

| arm | zero reassignment | max Bader error (e) | median side / base | median total / label map |
|---|---|---|---|---|
| A2, relative bound 1e-3 | 12/12 | 0 | 0.057 | 17.3 |
| A2, 1e-2 | 12/12 | 0 | 0.33 | 16.3 |
| A2, 5e-2 | 12/12 | 0 | 1.63 | 27.1 |
| A1, 1e-3 | 12/12 | 0 | 0.28 | 21.1 |
| A1, 1e-2 | 12/12 | 0 | 1.35 | 29.5 |
| A1, 5e-2 | 12/12 | 0 | 5.20 | 56.9 |

Before correction, the base quantizer alone reassigns a median 45–91% of voxels. After correction no voxel is
reassigned.

Arm L (lossless label map): exact round trip 12/12; charges recomputed from the stored labels match the binary
12/12 (max 5.0e-7 e); median 12.9 kB (atom map) and 21.8 kB (volnum map).

## Reading

A partition-faithful AECCAR (A2) can be compressed with a guaranteed identical Henkelman partition on real
materials. When only Bader charges are needed, a lossless label map is about 17x cheaper. The recommended
self-contained Bader contract is therefore: Hartree-certified CHGCAR stream + lossless label map (+ B2 projection
sums when the stream's region sums miss tau_B). A partition-faithful AECCAR is reserved for users who need the
partition field itself.
