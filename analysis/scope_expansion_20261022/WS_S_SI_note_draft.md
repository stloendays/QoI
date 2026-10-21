# WS-S draft — SI note: the magnetization block as a second measurement contract

Status: draft for the owner. Numbers marked *pending* come from S2 and S3 v2, which are running. Every
number cites its result file on branch `research/scope-expansion-20261022`.

---

## Supplementary Note Y. The magnetization block: a second field, a second contract

**The object the archive serves.** Every sampled Materials Project charge-density object carries two
volumetric blocks: the total density and the magnetization density, m = rho↑ − rho↓.

- **Prevalence.** 210/210 objects in the development and engineering sets, and 300/300 in the archive
  sample, carry the magnetization block. It accounts for 52% of the serialized text (expansion estimate of
  its byte share: 0.5195) [`results/s0_spin_census/`, `results/s0b_archive_spin_bytes/`].
- **Near-zero blocks are still large.** In 134/300 archive objects the block is close to zero (mean
  |m| < 1e-3 mu_B). Stored losslessly it nevertheless costs about as much as rho itself (median ratio 1.02).

**Contract.** The QoI is the set of per-atom magnetic moments: the compiled Henkelman code integrates m over
the Bader partition of rho (`bader CHGCAR(m) -ref REFCAR(rho) -b ongrid`). Tolerance tau_mu is in mu_B.

**Qualification** [`results/s1_spin_engineering/`]. QSQ with the five frozen seeds, with rho and m
perturbed at their float32 amplitudes:

- the floor has a median of 1.4e-5 mu_B and a maximum of 6.3e-3 mu_B;
- the contract is eligible in 16/16 materials at 1e-2 mu_B and in 15/16 at 1e-3.

**Certification with rho exact.**

- **Magnetic materials.** The best of ZFP/SZ3/SPERR certified every magnetic material at every tolerance.
  The certified m stream costs a median 0.08%, 0.32% and 0.84% of lossless rho at 1e-1, 1e-2 and 1e-3 mu_B
  (maxima 0.34%, 1.1% and 2.5%).
- **Non-magnetic materials.** Their m is numerical noise and certifies at the search cap.
- **Verification.** Every certified point was re-run through the binary.

**Composition with the charge contract** [`results/s3_joint_contracts_v1/`]. Here rho is stored lossy under
the resolved Bader contract, so the partition moves.

- **Migration effect.** Moment errors caused by migration alone stayed at or below 1.9e-3 mu_B. The gross
  charge on reassigned voxels reached a median 0.11 e at tau_B = 1e-2 e, but |m| is small at basin
  boundaries.
- **m certified on the reference partition.** The two contracts composed without a stored partition:
  - in every material-tolerance pair at tau_B = 1e-3 e;
  - in 27/32 at 1e-2 e, where the five misses are budget overruns by the migration term.
- **Decoded-frame certification** [`results/s3_joint_contracts_v2/`]. The encoder knows rho', so it can
  certify m' against the moments on the decoded partition directly.
  - The two contracts then compose without a stored partition in 60/62 material-tolerance pairs, at a
    median byte cost of 1.00× (range 0.97–1.30).
  - The two exceptions sit at tau_B = 1e-2 e with tau_mu = 1e-3 mu_B. There migration alone moves a moment by
    1.6e-3 and 1.9e-3 mu_B, so the partition itself must be stored, or rho' tightened.

**Whole-object archive estimate** [`results/s2_archive_whole_object/`]. Same frame, sample, estimators and
seeds as the published estimates, with m stored under the moment contract (lossless where not eligible).

- **Qualification and cost.** The contract qualified in 300/300 objects at 1e-2 mu_B. The certified m streams
  cost a median 0.05% of lossless rho (maximum 1.0%).
- **Ratios for the whole served object.** Bader 1e-3 e: 4.36× [3.62, 5.40]. Hartree law 1e-6: 317×
  [291, 350]; 232× [216, 252] with the reference atom map (median 17 kB) carried along. Pointwise codecs:
  34.6×.
- **Map-free reading of the Hartree row** [`results/s4_hartree_decoded_frame/`]. Certifying m on the
  partition of the law's rho' composed in 16/16 engineering materials at tau_H = 1e-6 and tau_mu = 1e-2
  mu_B, at the same m bytes. This supports the map-free figure.

---

## One-sentence main-text candidates

- **Scope sentence (Methods, archive):** "Each object also carries a magnetization block (52% of its bytes),
  stored here under a per-atom moment contract (Supplementary Note Y)."
- **Results/Discussion:** "The same qualification and certification extend to the magnetization density:
  per-atom moments qualified in 16/16 test materials and cost a median 0.3% of the lossless density at
  10⁻² μB."
