# WS-S2c reading — whole-object Hartree archive at tau_H = 1e-4

- **Run.** CI run 39651769782 on the 300 archive-sample objects: 300/300 objects, 0 failures.
- **Law streams.** Regenerated at 1e-4 and re-certified; sizes match the record within 0.05%, byte-identical
  in 202/300.
- **m.** m was certified on the partition of the law's rho'.

| m contract | certified on the decoded partition | map-free R [95% CI] | hybrid R (map only where needed) [95% CI] | published (rho only) |
|---|---|---|---|---|
| 1e-2 mu_B | 290/300 | 76.4 [42.3, 192] | **1,036 [927, 1,152]** | 1,751 |
| 1e-3 mu_B | 216/300 | 8.0 [6.5, 10.3] | 325 [174, 629] | 1,751 |

- **Hybrid policy.** Objects whose m cannot be certified on the decoded partition store the reference atom
  map plus the reference-frame certified m (from S2). The map is needed for 10 objects at 1e-2 mu_B and 84 at
  1e-3 mu_B. Seed 20261012.

## Reading

- **The partition moves too far at 1e-4.** The law's rho' at 1e-4 moves the partition enough that 10/300
  objects cannot certify m in the decoded frame at 1e-2 mu_B. Falling back to lossless m for them collapses
  the map-free ratio to 76×, because these objects are large.
- **The hybrid is the right policy.** Store the decoded-frame m, and add the atom map only for objects that
  need it. With the hybrid the whole object shrinks 1,036× at 1e-4 (m at 1e-2 mu_B), against 1,751× for rho
  alone.
- **Rule for every Hartree tolerance:** decoded-frame m where it certifies, the atom map otherwise. At 1e-6
  this gives 316× (map needed for 0/300 objects); at 1e-4 it gives 1,036× (10/300).
