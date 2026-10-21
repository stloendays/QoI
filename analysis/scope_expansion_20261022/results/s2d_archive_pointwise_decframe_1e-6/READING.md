# WS-S2d reading — whole-object archive under the best pointwise codec (A6), tau_H = 1e-6

- **Run.** CI run 39660568135 on the 300 archive-sample objects.
- **Streams.** Each object's A6 stream (best of ZFP/SZ3/SPERR, committed search) was regenerated and
  re-certified.
  - 299/300 objects succeeded.
  - mp-2626824 (D10b) failed: its regenerated SPERR stream fell just outside its Hartree certificate, the
    known regeneration effect also seen in the deployment-cost run.
  - Regenerated sizes match the record within 0.4% (byte-identical in 269/299).
- **m.** m was certified on the partition of the A6 rho' at 1e-2 mu_B: 299/299.

| policy for the failed object | R_P whole object [95% CI] | R_L / R_P like-for-like [95% CI] |
|---|---|---|
| m kept losslessly (the aggregation script's default) | 30.8 [24.8, 36.4] | — |
| **atom map + reference-frame m (S2), same fallback as the law rows** | **34.6 [32.4, 37.2]** | **9.15 [8.45, 10.0]** |

- **Inputs.** R_L uses the S2b map-free law figure, with the same fallback rule (atom map where decoded-frame
  m fails; needed for 0/300 objects at 1e-6). Seed 20261012.

## Reading

- **Like-for-like result.** With both writers storing the whole object under the same moment policy, the
  pointwise archive shrinks 34.6-fold and the law archive 316-fold: the law's archive is 9.2-fold smaller
  (published rho-only: 10.2-fold).
- **Why the gap narrows.** m costs the same bytes for both writers, so it dilutes the law's advantage
  slightly.
- **The "lossless m" variant.** It is not a fair comparison. A single 86 MB object whose rho regeneration
  failed then pays lossless m, which moves the stratified estimate by 4 units.
