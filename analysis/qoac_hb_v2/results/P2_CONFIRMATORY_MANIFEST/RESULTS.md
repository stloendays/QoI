# QOAC-HB v2 confirmation (48 fresh P2) — frozen criteria (DESIGN.md `8a784a4`)

CI run 37497825261; 48/48 materials successful; 0 setting failures. Engineering authorization: `P2_ENGINEERING_MANIFEST/RESULTS.md`.
Bootstrap: seed 20261007, 10,000 resamples of the median.

| criterion | result | threshold | pass |
|---|---|---|---|
| 1. analyzable and jointly certified (R3, best post, all three tau_B) | 48/48 | >= 46/48 | yes |
| 2. joint overhead at tau_B = 1e-4 (CR_hartree_only / CR_joint) | median 1.000, CI [1.000, 1.000] | <= 1.10, CI upper <= 1.15 | yes |
| 3. utility at tau_B = 1e-4 (R3 / max of J, T1, GF at their best posts) | 48/48 wins, median 1.317, CI [1.269, 1.360], min 1.096 | >= 36/48, > 1.10, CI lower > 1.00 | yes |

**Confirmatory PASS.**

Descriptive:
- R3 best joint post-processor: `none` in 48/48 at tau_B = 1e-3 and 1e-4. At 1e-5: `none` 33/48, `hap:0.0001` 15/48.
- Median joint overhead is 1.000 at every tau_B. Median R3 joint CR is 298 at every tau_B.
- CTP decisions (R3): projected 0/192 at 1e-3, 0/192 at 1e-4, 31/165 at 1e-5.
- HAP vs uniform at 1e-5 (R3, materials where both certify, n = 35): median CR ratio 1.00.
- Median joint CR at tau_B = 1e-4: R3 298, J 213, T1 212, GF 18.6.

Reading: under an exact AECCAR partition, one operator-aware stream certified for the Hartree potential at 1e-6 also
satisfies Bader charges to 1e-4 e with zero basin reassignment and no additional bytes. A projection is needed only at
1e-5 e, and then costs nothing measurable at the median. The Hartree-aware projection did not change certified rates
relative to the uniform one.

Derived count (from `joint_v2_best_post.csv` joined with `joint_v2_material.csv`; asserted in `figures/nc/fig5/make_fig5.py`):
the certified R3 best-post streams number 144/144 (48 materials x 3 tau_B), every one with maximum atomic-charge error
<= tau_B and reassigned-voxel fraction 0.
