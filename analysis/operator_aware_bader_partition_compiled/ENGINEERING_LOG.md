# QOAC-B3 engineering log

## 2026-10-05 — first semantic-equivalence run invalidated

The first 12-material B3 execution produced exact lossless partition-map round trips and strong storage reductions, but the direct label-integrated charges were compared to Henkelman using an incorrect extra cell-volume factor.

The repository decoder follows the VASP CHGCAR convention in which the decoded grid integrates to electron count by the grid average:

    Q = sum(grid values) / N_grid.

The invalid run used:

    Q = V_cell * sum(grid values) / N_grid,

which inflated the direct charges by approximately the cell volume and produced errors of order 10^3–10^4 e.

Actions:
- correct direct integration to sum/N_grid;
- keep the exact same 12 materials;
- keep both lossless partition encodings unchanged;
- keep Gates A/B/C unchanged;
- rerun from the beginning.

No 50-material B3 census was authorized or executed from the invalid run.
