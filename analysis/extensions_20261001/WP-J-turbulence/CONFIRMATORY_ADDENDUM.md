# Independent JHTDB confirmation addendum — 2026-10-01

Status: **frozen before any confirmatory cutout is fetched or analyzed.**

The first 64-cutout JHTDB pilot completed exactly as predeclared. Its primary vortex-mask threshold, `tau_M = 0.05`, did not satisfy the predeclared minimum group-size criterion because 62/64 cutouts were eligible and only 2/64 were rejected. The primary pilot acceptance criterion is therefore **NOT MET**.

The same pilot also contained a predeclared stricter secondary threshold, `tau_M = 0.01`, which yielded a balanced 31/33 eligibility split and strong prospective separation. Because this observation is now known, it is treated only as **calibration evidence** and is not promoted to independent confirmation.

A new, non-overlapping confirmatory cohort is therefore frozen below.

## Confirmatory cohort

- Dataset: JHTDB `isotropic1024coarse`.
- 64 new `15^3` cutouts.
- Same grid spacing, derivative algorithm, Q-criterion definition, reference P90 mask threshold, float16-equivalent velocity perturbation scale, five QSQ seeds, and 59 fresh seeds as the pilot.
- Sampling keys use the independent namespace `QSQ-JHTDB-CONFIRM-20261001`.
- Exact time-origin keys present in the pilot manifest are forbidden.
- The confirmatory manifest is frozen before data retrieval.

## Confirmatory thresholds

### Primary vortex-mask endpoint

The confirmatory primary threshold is

[
\tau_M = 0.01
]

for response `1 - IoU`.

This threshold was already predeclared as a pilot secondary endpoint. Its use as the confirmatory primary threshold is explicitly calibration-driven and is tested only on the new cohort.

### Secondary enstrophy endpoint

The original pilot thresholds were too loose for the measured enstrophy response: all 64 pilot cutouts were QSQ-eligible even at `tau_E = 1e-3`.

For the independent confirmatory cohort, the enstrophy threshold is frozen at

[
\tau_E = 10^{-4}.
]

This value is a one-significant-digit calibration target near the pilot median five-probe enstrophy floor (~`1.1e-4`). Pilot observations at this threshold are not used as confirmatory evidence.

## Acceptance

The cross-domain generality statement is independently supported if the **confirmatory vortex-mask endpoint** satisfies all three:

1. at least 10/64 eligible and 10/64 rejected;
2. fresh rejected-to-eligible exceedance risk ratio >= 5;
3. cutout-cluster bootstrap 95% interval for the fresh risk difference excludes zero.

The enstrophy endpoint is a separate secondary test. If it satisfies the same three conditions, it supports transfer of QSQ across two derivative-based QoIs with different response structure.

No threshold, perturbation amplitude, QoI definition, seed set, sample count or numerical algorithm may change after confirmatory outcomes are observed.

## Interpretation lock

- The failed `tau_M=0.05` pilot primary endpoint remains recorded.
- Pilot `tau_M=0.01` results are calibration evidence, not independent confirmation.
- Only the new cohort can support the confirmatory claim.
- A successful 15-cube confirmation establishes cross-domain proof-of-principle, not a production-scale turbulence compression benchmark.
