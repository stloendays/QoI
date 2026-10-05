# General-QOAC electric-field engineering log

## 2026-10-05 — first frozen exponent test

Planned settings: 900.
Completed settings: 900.
Failures: 0.

Prospective prediction:
- electric-field squared-error weight: 1/|G|^2;
- high-rate predicted exponent: beta = 1.

Frozen gates:
- Gate A beta=1 vs beta=0: wins >=9/12 and median matched-storage error ratio <0.70;
- Gate B beta=1 vs beta=2: wins >=9/12 and median matched-storage error ratio <0.90;
- Gate C certified-rate ablation at relative electric-field RMSE 1e-6.

Observed:
- beta=1 beats beta=0 in 12/12 materials; median matched-storage error ratio 0.8063683; Gate A NO-GO.
- beta=1 beats beta=2 in 10/12 materials; median matched-storage error ratio 0.9280491; Gate B NO-GO.
- certified-rate beta=1 wins 7/12; median CR ratio versus best wrong exponent 1.031283; Gate C NO-GO.

Decision:
- no disjoint electric-field holdout may be executed;
- do not weaken the original gates after observing results;
- retain the result as evidence that the operator-predicted beta=1 shifts the rate-distortion geometry in the predicted direction, but that the finite-rate serialized optimum may differ from the ideal high-rate exponent;
- authorize a second engineering-only beta-map on the same 12 materials to locate the finite-rate optimum before any confirmatory cohort is frozen.

The Nyquist-safe electric-field metric was fixed before material execution after preflight demonstrated the derivative ambiguity of even-grid Nyquist modes. The safe spectral metric closes against explicit real-space three-component spectral differentiation.
