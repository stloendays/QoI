# WP-H — Exact sequential early-rejection QSQ

The frozen five-seed QSQ eligibility rule was evaluated on all 254 development materials using the original seed order `20260905, 1, 2, 3, 4`. The sequential implementation stops as soon as any observed response is greater than or equal to the requested tolerance. Because the frozen rule uses the maximum over the same five seeds, this early rejection cannot change a binary eligibility decision.

## Primary endpoint

At `tau = 1e-3 e`:

- eligibility agreement with the frozen five-seed QSQ is **254/254 (100%)**;
- frozen eligible materials: **143/254**;
- mean probe solves fall from **5.000 to 3.335 per material**, a **33.3% reduction**;
- including the one reference solve, mean Bader solves fall from **6.000 to 4.335**, a **27.8% reduction**;
- among the 111 rejected materials, **99/111 (89.2%)** are rejected by the first seed and **106/111 (95.5%)** by the first two seeds;
- rejected materials require a mean of **1.189 probes**, while eligible materials necessarily require all five.

The pre-declared WP-H acceptance criterion is therefore **met**: classification is exactly preserved and the primary-threshold mean probe count is below 4.0.

## Threshold dependence

| tau (e) | eligible | agreement | mean probes | probe reduction | mean total solves | total-solve reduction |
|---:|---:|---:|---:|---:|---:|---:|
| 1e-4 | 46/254 | 254/254 | 1.906 | 61.9% | 2.906 | 51.6% |
| 1e-3 | 143/254 | 254/254 | 3.335 | 33.3% | 4.335 | 27.8% |
| 1e-2 | 229/254 | 254/254 | 4.626 | 7.5% | 5.626 | 6.2% |

The gain is largest when the requested tolerance rejects many materials, because a single threshold exceedance proves the final five-seed maximum will fail the same contract.

## Scope of the optimization

Sequential early rejection preserves **binary eligibility at a specified tolerance**, but it does not recover the exact five-seed floor for materials stopped early. Full five-seed evaluation is still required when the numerical value of the floor is itself an analysis endpoint, for example continuous-risk calibration or mechanistic correlation. The optimization is therefore suitable for deployment/certification workflows that need a yes/no qualification at a declared tolerance.

Files: `sequential_material.csv`, `sequential_summary.csv`, `analyze_sequential_qsq.py`, `provenance.json`.
