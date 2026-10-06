# QOAC-HB — joint Hartree + Bader certification results

## Engineering (12 materials) — E1 GO, E2 GO

0 material and 0 setting failures. J certifies the joint contract in 12/12. R_J > 1 in 9/12, median
**1.600x** (bootstrap 95% CI 1.149–1.818). Median certified CR: J 205, T1P 171, GP 15.1.

## Confirmatory (38 materials) — formal FAIL (criterion 4)

| frozen criterion | result |
|---|---|
| 38/38 analyzable, zero failures | pass |
| J certifies C_HB in >= 34/38 | pass (38/38) |
| R_J > 1 in >= 28/38 | pass (30/38) |
| median R_J > 1.25 | **fail (1.224)** |
| bootstrap 95% CI lower bound > 1.10 | pass (1.131; CI 1.131–1.478) |

Minimum R_J 0.652. Median certified CR: J 182, T1P 142, GP 14.9. Every certified stream in every arm has zero
basin reassignment and Bader error 0 e after projection; every arm certified on its first Bader attempt.
Side-channel fraction of J: 0.10–0.56%.

The joint-contract confirmatory claim at the frozen effect size is **not** supported. What the data support:
one QOAC-H stream plus projection satisfies both contracts in 50/50 materials, and it beats the best
projected competitor in 39/50 at a median ratio of about 1.2–1.6x (cohort-dependent).

## Observations (descriptive)

1. **Bader is not the binding constraint under an exact partition.** Before projection, the QOAC-H stream
   selected at the Hartree certificate already has Bader error <= 5.3e-5 e and zero reassignment in 50/50
   materials, about 20x below tau_B.
2. **The projection costs Hartree budget.** The piecewise-constant correction raises the Hartree error of J
   (confirmatory median 5.5e-7 -> 7.3e-7). In 45% of confirmatory materials (33% engineering) it pushes the
   best rung over 1e-6, and J falls one rung (a 2.15x alpha step) down the frozen ladder.

## Post-hoc diagnostic (unverified; not a result)

Taking J's best Hartree-certified rung without projection and without side channel gives median ratio 1.55
(35/38) against the projected competitors. This is not certified (Bader was not run on those rows). The
comparison is also asymmetric, since the competitors were projected. It only shows that the projection's
Hartree cost explains most of the shortfall.

## Next iteration (requires a new frozen protocol)

Either option must apply identically to every arm and be frozen before execution:
- **Certify-then-project:** project only if the unprojected stream fails the Bader contract.
- **Hartree-aware projection:** the correction minimizing the Hartree norm subject to the region sums
  (a constrained least-squares in the H^-1 metric), instead of the uniform minimum-L2 correction.
