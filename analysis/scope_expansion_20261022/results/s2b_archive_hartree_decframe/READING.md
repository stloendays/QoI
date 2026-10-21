# WS-S2b reading — map-free whole-object Hartree archive (decoded-frame moments)

- **Run.** CI run 39644226010 on the frozen 300-object archive sample: 300/300 objects, 0 failures.
- **Law streams.** Each object's law stream at tau_H = 1e-6 was regenerated with the committed search and
  re-certified for Hartree. The regenerated sizes match the recorded ones byte-for-byte in 174/300 objects,
  and within 0.016% in every object (ratio 0.99986–1.00016). The ratio below uses the recorded sizes, as the
  published estimate does.
- **m.** m was certified against the moments read on the partition of the law's rho', with the S2 QSQ gate
  and final verification by the compiled binary. No atom map is stored.

| m contract | m certified on the decoded partition | R whole object, no map [95% CI] | published (rho only) | S2 with the reference-frame certificate + atom map |
|---|---|---|---|---|
| 1e-2 mu_B | 300/300 | **316 [290, 350]** | 356 | 232 [216, 252] |
| 1e-3 mu_B | 291/300 (8 lossless: migration exceeds tau_mu; 1 not eligible) | 44.6 [23.5, 124] | 356 | 164 [113, 224] |

- **Migration.** Partition migration under the law's rho' moved moments by a median 1e-6 mu_B and at most
  7.3e-3 mu_B.

## Reading

- **At the moment tolerance 1e-2 mu_B the map-free figure is measured.** The whole served object, density
  plus magnetization, shrinks 316-fold under the Hartree law at 1e-6, with no partition stored. This
  confirms S2's 317× (reference frame) and S4's engineering result on all 300 archive objects.
- **At 1e-3 mu_B, keep the map.** Eight objects cannot be certified on the decoded partition and fall back
  to lossless m, which costs most because these objects are large. Carrying the atom map is then far better
  (164× in S2). The practical rule is to store the map only when decoded-frame certification fails. That
  hybrid was not computed here; it lies between 164× and 316×.
- **Recommended headline (if option 2 is taken).** "Certified storage of the whole served objects would
  shrink the 8.50 TB archive 4.4-fold for Bader charges at 10⁻³ e and, with the law, 316-fold for the
  Hartree potential at 10⁻⁶, magnetic moments certified to 10⁻² μB (pointwise: 35-fold)."
