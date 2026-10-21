# WS-S2 reading — whole-object archive estimate (rho + m)

- **Run.** CI run 39635020731. Same frame, stratified 300-object sample, storage rule, expansion estimator and
  bootstrap seeds as the published archive estimates.
- **Measured.** 300/300 objects, 0 failures, 0 unmeasured.
- **Per object.** The charge-density block keeps its published stored size. The magnetization block is added
  under the per-atom moment contract: QSQ with the five frozen seeds, then the best of ZFP/SZ3/SPERR certified
  by the compiled binary, or lossless where the contract is not eligible.

## Qualification and cost of m

- **Eligibility.** The moment contract is eligible in 300/300 objects at 1e-2 mu_B and 299/300 at 1e-3
  mu_B. Floors have a median of 0 and a maximum of 1.07e-3 mu_B.
- **Certification.** The certified m stream is SZ3 in 226 objects, SPERR in 73 and ZFP in 1 (at 1e-2). At
  1e-3 one object stays lossless.
- **Cost relative to lossless rho.** The m stream costs a median 0.048% at 1e-2 mu_B (max 1.0%) and 0.072%
  at 1e-3 mu_B; the single lossless object reaches 1.01×.
- **Atom map.** The reference atom map (xz, the QOAC-B3 arm-L coder) has a median of 17.3 kB, or 0.25% of
  lossless rho.

## Archive ratios, whole served object

| charge-density contract | m contract | published (rho only) | rho + m [95% CI] | rho + m + atom map [95% CI] |
|---|---|---|---|---|
| Bader 1e-3 e | 1e-2 mu_B | 4.37 | 4.36 [3.62, 5.40] | 4.34 [3.61, 5.37] |
| Bader 1e-3 e | 1e-3 mu_B | 4.37 | 4.33 [3.60, 5.36] | 4.31 [3.59, 5.32] |
| Hartree law 1e-6 | 1e-2 mu_B | 356 | 317 [291, 350] | 232 [216, 252] |
| Hartree law 1e-6 | 1e-3 mu_B | 356 | 203 [131, 298] | 164 [113, 224] |
| pointwise 1e-6 | 1e-2 mu_B | 35.0 | 34.6 [32.4, 37.2] | 33.3 [31.2, 35.7] |

The other tolerances are in `RESULTS.md`.

## Reading

1. **The like-for-like objection is removed, and the headline numbers survive.** Once the whole served
   object is certified, the Bader-contract archive shrinks 4.36× (published 4.37×). The Hartree-law archive
   shrinks 317× with m at 1e-2 mu_B (232× if the atom map travels too), against 35× for pointwise codecs.
   The law's advantage over pointwise codecs stays about 9×.
2. **Which column applies.** The m certificate here is evaluated on the reference partition, so the
   strictest reading is the "+ atom map" column. S3 v2 showed that certifying m on the decoded partition
   instead costs the same bytes and removes the need for the map in 60/62 material-tolerance pairs under a
   Bader-certified rho'. For Hartree-law rho' streams, whose partition is not controlled, decoded-frame
   certification was not tested at first; S4 (`results/s4_hartree_decoded_frame/READING.md`) then tested it
   on the 16 engineering materials. At tau_H = 1e-6 with m at 1e-2 mu_B it composes in 16/16 at the same
   m bytes, which supports the 317× column without the map. The "+ atom map" column (232×) stays the bound
   that needs no further assumption.
3. **Scope.** The magnetization block adds a second physical field and a routine downstream analysis
   (per-atom moments) to the paper. It does so at a cost below 1% of the density for 300/300 archive objects
   at 1e-2 mu_B.
