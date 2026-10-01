# WP-I — Partition-reference-only sensitivity decomposition

Analyzable materials: **50/53**. The same three published AECCAR inputs that failed in WP-G remain explicit input failures: `mp-1192831`, `mp-1193567`, and `mp-776331`.

## Primary endpoint at tau = 1e-3 e

- G1 (exact all-electron reference): **50/50 eligible**.
- G2 (CHGCAR + all-electron reference perturbed): **3/50 eligible**.
- G3 (exact CHGCAR, all-electron reference perturbed only): **3/50 eligible**.
- G3 non-evaluable: **47/50 (94.0%)**.
- Material-median `f_G3 / f_G2 = 1.000` (bootstrap 95% CI approximately 1.000–1.000).
- Median basin-reassignment fraction: G2 = **0.0196262**, G3 = **0.0196262**.
- Median reassignment ratio G3/G2 = **1.000**.
- Fraction with `f_G3 >= 0.5 f_G2`: **1.000**.
- Fraction with `f_G3 >= 0.9 f_G2`: **1.000**.
- Pre-declared dominance criterion: **MET**.

## Threshold comparison

| tau (e) | G1 eligible | G2 eligible | G3 eligible |
|---:|---:|---:|---:|
| 1e-4 | 50/50 | 0/50 | 0/50 |
| 1e-3 | 50/50 | 3/50 | 3/50 |
| 1e-2 | 50/50 | 17/50 | 17/50 |

Under the predeclared finite-panel perturbation protocol, G3 reproduces the G2 eligibility counts at all three thresholds. The material-median floor ratio and median basin-reassignment ratio are both 1.000, and every analyzable material satisfies `f_G3 >= 0.9 f_G2`.

## Interpretation

These results support the predeclared statement that **perturbation of the partition-defining all-electron reference is the dominant source of the observed G2 QSQ instability**. Within the tested 50-material analyzable set and frozen five-seed perturbation panel, adding CHGCAR perturbation on top of the perturbed all-electron reference does not measurably increase the primary floor or basin-reassignment metrics at the reported precision.

This does **not** imply that CHGCAR errors are universally irrelevant to Bader charge. It shows that, for the tested standard all-electron-reference Bader measurement contract and the frozen perturbation scales, instability is controlled overwhelmingly by the field that defines the partition topology.

The result therefore strengthens the contract-aware QSQ interpretation: stability qualification should perturb the inputs that are actually approximate in the deployed measurement contract, and partition-defining references can require a different precision policy from the integrated charge field.
