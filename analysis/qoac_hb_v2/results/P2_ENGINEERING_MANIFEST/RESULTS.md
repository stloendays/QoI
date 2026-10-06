# QOAC-HB v2 engineering (12 fresh P2) — gate evaluation under DESIGN.md (`8a784a4`)

CI run 37495653659; 12/12 materials successful; 0 setting failures. Gates are evaluated from
`joint_v2_best_post.csv` and `joint_v2_material.csv` exactly as defined in DESIGN.md.

| gate | result | threshold | pass |
|---|---|---|---|
| E1 feasibility (R3 best joint post certified at tau_B = 1e-3, 1e-4, 1e-5) | 12/12 | >= 11/12 | yes |
| E2 joint overhead at tau_B = 1e-4 (CR_hartree_only / CR_joint, R3) | median 1.000 (1.000 in all 12) | <= 1.10 | yes |
| E4 utility at tau_B = 1e-4 (R3 best post / max over J, T1, GF best post) | 12/12 wins, median 1.355 (min 1.167) | >= 9/12, > 1.10 | yes |

**Confirmation authorized.**

Descriptive:
- R3 best joint post-processor is `none` (unprojected stream verified by Bader) in 12/12 at tau_B = 1e-3 and 1e-4. At
  1e-5 it is `hap:0.0001` in 7/12 and `none` in 5/12. Median joint overhead at 1e-5 is 1.0032.
- CTP decisions (R3): projected 0/48 at 1e-3, 0/48 at 1e-4, 12/32 at 1e-5.
- E3 (HAP vs uniform, R3, tau_B = 1e-5): median CR ratio 1.00 where both certify. The Hartree-aware correction does not
  change the certified rung here.
- Median joint CR at tau_B = 1e-4: R3 297, J 224, T1 191, GF 17.1. R3 Hartree-only 297.

Reading: under an exact AECCAR partition, a Hartree-certified operator-aware stream already carries Bader charges to
1e-4 e at no extra cost. Certify-then-project removes the projection penalty that made the frozen QOAC-HB v1
confirmatory fail.
