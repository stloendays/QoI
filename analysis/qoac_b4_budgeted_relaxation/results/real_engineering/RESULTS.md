# QOAC-B4 real-material engineering — results (descriptive)

- **Run.** CI run 39630018118, 2026-10-21, on the 12 P2 engineering materials (the same ones QOAC-B3 used).
- **Contract.** Compiled Henkelman Bader 1.05, `-b ongrid -vac 0.001`, exact CHGCAR, reference = AECCAR0 +
  AECCAR2.
- **Arms.** Each delta has a paired B3 strict-correction baseline on the same base stream, plus B4 for
  tau_B ∈ {1e-3, 1e-4} e × theta ∈ {0.5, 0.9}.
- **Rows.** 12/12 materials produced rows. The one failure record is B3's known Gate 0 comparison defect on
  mp-2302539 (a 74 GiB array); its arms ran normally.

## Construction check (compiled binary)

- **Certified.** 144/144 B4 streams: every per-atom Bader error was below tau_B.
- **No violations.** Atom-map changes outside R: 0 in every group. Bound violations (actual error above the
  a-priori bound + 2e-6 e): 0 in every group.
- **Error vs bound.** The largest actual error was 0.88 tau_B, against a bound of 0.90 tau_B (theta = 0.9,
  tau = 1e-4).

So the a-priori bound holds on real materials when checked by the production Bader code, not only by the
Python transcription.

## Bytes (B4 / B3, same base stream; total = base + side information)

| delta | tau_B (e) | theta | median total ratio | best material | materials where B4 is smaller |
|---|---|---|---|---|---|
| 1e-3 | 1e-3 | 0.9 | 0.9945 | 0.971 | 12/12 |
| 1e-2 | 1e-3 | 0.9 | 0.9890 | 0.951 | 12/12 |
| 5e-2 | 1e-3 | 0.9 | 1.0254 | 0.865 | 4/12 |
| 1e-3 | 1e-4 | 0.9 | 0.9993 | 0.993 | 11/12 |
| 1e-2 | 1e-4 | 0.9 | 0.9992 | 0.952 | 10/12 |
| 5e-2 | 1e-4 | 0.9 | 1.0257 | 0.865 | 4/12 |

All 12 groups are in `SUMMARY.json`. At delta = 5e-2, B4 is *larger* than B3 in 8/12 materials. Every
relaxed voxel forbids its neighbours from stepping into it, and at loose bounds the escalations this forces
outweigh the edits saved.

**Never-worse selection.** The encoder keeps whichever of the B3 and B4 streams is smaller. The decoder does
not need to know which, because both are level maps on the same base stream. This makes the median ratio
≤ 1.000 in every group (at delta = 5e-2: 1.000, with the best material at 0.865).

## Why the effect is small

Per material, at tau_B = 1e-3 e and theta = 0.9 (`rows.csv`):

- **Where B4 helps.** Side information drops 30–70% where B3's side information is a small fraction of the
  base payload:
  - mp-2229470: side 0.32× at delta = 1e-3;
  - mp-2302539 and mp-2327119: about 0.6×.
  There the total changes by only a few per cent.
- **Where B4 does not help.** Where side information dominates (mp-16720: side/base 1.45–7.7; mp-1956443,
  mp-1945523), only 59–297 voxels could be relaxed. The per-atom budget of 0.9 × 10⁻³ e is used up by a
  handful of boundary voxels, so the costly reassignments are not ones the Bader tolerance can absorb.

## Reading against PROTOCOL.md section 5

- **Construction check:** passed.
- **Byte effect:** total ratios are not clearly below 1 at delta ≥ 1e-2 (median 0.989 at best), so
  relaxation is **not** worth carrying forward as a compression method on this contract.
- **Label map:** the lossless label map stays about 20× smaller (median total / label 20–34). This is
  unchanged from B3's recommendation.
- **What survives:** a validated statement that the Henkelman partition can be relaxed under a *proved*
  per-atom charge bound. It could be useful in an SI sentence on contract-budgeted topology preservation, but
  it is not a byte win.
