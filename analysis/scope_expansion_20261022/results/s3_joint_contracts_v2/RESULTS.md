# WS-S3 v2 — decoded-frame certification of the moments

- **Run.** CI run 39639264368, on the 16 S1 engineering materials. 0 failure records.
- **Setup.** Same as v1: resolved Bader-certified rho' from the best of ZFP/SZ3/SPERR.
- **Arms on m.**
  - **Reference frame (v1 arm):** m' is certified on the reference partition.
  - **Decoded frame:** m' is certified against the moments read on the partition of rho', which the encoder
    knows.
- **Verification.** Both arms are verified by the compiled binary on the decoded partition.

## Counts (material × tau_mu pairs with a certified rho')

| tau_B (e) | tau_mu (mu_B) | reference frame | decoded frame |
|---|---|---|---|
| 1e-2 | 1e-2 | 14/16 | **16/16** |
| 1e-2 | 1e-3 | 13/16 | 14/16 (2 cases have no certifiable point) |
| 1e-3 | 1e-2 | 15/15 | 15/15 |
| 1e-3 | 1e-3 | 15/15 | 15/15 |

- **Reproducibility.** The reference-frame arm reproduces v1 exactly. FeCo9 has no certified rho' at
  tau_B = 1e-3 e.
- **Correctness.** Every decoded-frame point the search accepted is certified by the binary; the largest
  joint error is 0.997 tau_mu.
- **The 2 uncertifiable cases.** Sr2MgTiO4 and BaNdMgCo2O5 at tau_B = 1e-2 e with tau_mu = 1e-3 mu_B. Here
  partition migration alone moves a moment by more than 1e-3 mu_B, so no m' can compensate. These cases
  need either a tighter rho' contract or the stored atom map.
- **Byte cost.** The decoded-frame stream costs the same as the reference-frame one: median ratio 1.00,
  range 0.97–1.30.

## Reading

- **Composition without a map.** The charge contract and the moment contract compose without storing the
  partition in 60/62 material-tolerance pairs, at essentially no byte cost.
- **The design rule.** Certify each downstream quantity in the frame the user will actually compute it in,
  i.e. on the decoded partition, not the reference one.
- **What remains.** The remaining 2/62 are a genuine limit: when tau_mu is tighter than the moment shift the
  charge certificate allows, the partition itself must be stored (QOAC-B3 arm L) or rho' tightened.
