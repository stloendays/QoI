# Study 3 — structure-factor prediction in the water-filling writer (W2), 92 law-protocol materials

Request (2026-10-25 21:08): 「再看看有啥能继续升级研究的开始完善！」. Branch `research/algo-upgrade2-20261025` from
revision 11 (`1cfc871`). Plan: `paper/nc_reopen/ALGORITHM_UPGRADE2_PLAN_20261025.md`. This protocol, the writer
(`w2.py`), the runner, the aggregator and the tests are committed before any cohort material is run.

## Question

Under the Hartree contract, how much does structure-factor prediction (SFP) reduce the water-filling writer's
stream, and does the closed-form allocation stay at the operational optimum when the residual is coded?

## Writer

`w2.py`: per radial shell and species a quadratic form factor (degree reduced in shells with fewer than 4 orbits per
parameter), fitted by operator-weighted least squares on the structure factors of the stored structure; integer
parameters (one step per shell, quantization adding at most 2% of the residual energy); a shell's prediction is kept
if it leaves less than 50% of the shell's operator-weighted energy. The residual is coded by the W1 writer
(water-filling law, adaptive container, symmetry). The W2 stream carries the species, float32 fractional coordinates
and the parameters; every stream is decoded by `w2.decode` and certified. The writer reports the smallest certified
stream of three variants: no prediction, prediction on every kept shell, prediction on the kept shells that the
water-filling rule writes.

## Cohort, arms, tolerances

- Cohort: the 60 P1 bulk and 32 P3b slab materials of the law protocol (`analysis/fresh_population_20261006`,
  confirmatory manifests), SHA-256 checked.
- Arms: **W1S** (revision 11's writer, recomputed), **W2S** (W2 with symmetry), **W2** (W2 without symmetry),
  **O2S** (arm A3's Lagrangian selection on the W1 curves of the SFP residual, symmetry, prediction on every kept
  shell). Recorded: A1, A2, A3, A6 (law protocol rows).
- Tolerances: tau_H = 1e-6 (primary) and 1e-4. Certificate: historical and Nyquist-safe Hartree relative RMS < tau.

## Criteria (cr = raw bytes / stream bytes; medians with 10,000 bootstrap resamples, seed 20261025)

- **G1 prediction gain:** cr(W2S)/cr(W1S) at 1e-6 over all materials, median >= 1.15 and 95% CI lower bound >= 1.10.
- **G2 closed form at the optimum with prediction:** cr(O2S)/cr(W2S) median <= 1.05 and CI upper bound <= 1.08 at
  1e-6 and at 1e-4.
- **Validity:** >= 90 analyzable materials; every arm certified at both tolerances; W1S bytes equal revision 11's
  W1S rows for all but at most 2 materials at each tolerance.
- Descriptive: W2S against A1, A2, A3 and A6; by cohort; by number of symmetry operations; variants chosen; SFP
  shells and block bytes; W2 against W1S (prediction without symmetry against symmetry without prediction).

A criterion that fails is reported as failed; nothing is re-tuned on cohort materials.

## Development exposure

Only P1 engineering materials (`P1_ENGINEERING_MANIFEST.csv`), on the laptop, before this protocol: form-factor
degree 0, 1, 2, 3, 4, 6 (2 best over both tolerances; 3 better at 1e-6 by 5%, worse at 1e-4), gate 0.5 and 0.8 (0.5),
quantization 2% and 0.5% (no difference). Final writer on ten engineering materials (W1S → W2S bytes): at 1e-6
1.15–2.40-fold smaller (4,965 → 2,824 on mp-3148759, 38,488 → 22,417 on mp-1924242 without symmetry, 19,174 → 8,004
on mp-1832643); at 1e-4 1.00–1.45-fold, the no-prediction variant chosen on five. Known answer for the probe:
`results/DEV_KNOWN_ANSWER.json` (mp-2521964).
