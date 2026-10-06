# QOAC v0.3 engineering — results

CI run 37479356703; 12 QOAC-H engineering materials; 0 failures in every arm. Every reported stream is
decode-verified (historical and Nyquist-safe Hartree relative RMSE < tau). Implementation detail: bisection
stops when the log-space bracket is below 1e-9 (the protocol allowed up to 60 iterations).

## Gates (primary tau = 1e-6)

| gate | criterion | result |
|---|---|---|
| G1 certification | A3 certified 12/12 | **GO** (12/12) |
| G2 utility | R3 = CR_A3 / max(CR_A1, CR_A2) > 1 in >= 10/12 and median > 1.20 | **NO-GO** (12/12 wins, median 1.099, min 1.046) |
| G3 operator metric essential | median CR_A3 / CR_A5 > 2.0 | **GO** (2.206) |

`confirmatory_authorized = false`. v0.3 is not confirmed as a better codec under this protocol.

## Median certified CR

| arm | tau 1e-4 | tau 1e-6 | tau 1e-8 |
|---|---|---|---|
| A0 v0.2, frozen ladder | 1636 | 378 | 39.9 |
| A1 v0.2, alpha bisection | 1754 | 396 | 51.2 |
| A2 truncation, alpha bisection, q_c = k/32 | 1427 | 217 | 28.1 |
| A3 v0.3 RDO, operator prior | **3305** | **435** | **53.3** |
| A4 v0.3 RDO, flat prior | 3314 | 432 | 53.5 |
| A5 v0.3 RDO, operator-blind control | 1215 | 166 | 15.3 |
| A6 best ZFP/SZ3/SPERR, tolerance bisection | 128 | 29.6 | 9.7 |

Ratios (medians over materials): A3/best(A1,A2) = 1.41 / 1.10 / 1.04; A3/A5 = 1.58 / 2.21 / 2.84;
A3/A4 = 0.995 / 0.999 / 0.998; A1/A0 = 1.09 / 1.09 / 1.20; A3/A6 = 21.3 / 12.1 / 5.8.

## What the engineering data show

1. **The closed-form operator law is near-optimal at tight tolerances.** The v0.2 power law Delta ∝ |G|^2,
   given the same continuous search, comes within 10% (tau = 1e-6) and 4% (tau = 1e-8) of the exact
   operational Lagrangian optimum over 32 shells. The finite-rate gain is large only at the loose
   tolerance (1.41x at 1e-4), consistent with the dead-zone diagnosis of the E-field study.
2. **The gain comes from the operator metric, not the shape of the prior.** RDO with a flat in-shell prior
   equals RDO with the operator prior (ratio 0.998). The same optimal machinery in the L2 metric is 1.6–2.8x
   worse while certifying the same Hartree contract.
3. **Equalized search matters for fair comparison.** Continuous tolerance search improves v0.2 by 1.09–1.20x
   and the pointwise codecs similarly. With fair search, truncation is 1.8x behind v0.2 at 1e-6.

## Consequence for the program

v0.3 is retained as an **operational-optimum reference** (an upper benchmark for any allocation in a given
operator metric), not as the headline codec. Hypotheses 1 and 2 above were formed on engineering data, so
they need a new frozen protocol on the fresh population before they can be claimed.
