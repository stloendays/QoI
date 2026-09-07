# Figure 6 interpretation status

Date: 2026-09-07

## What the current matched-L∞ figure supports

The existing matched-realized-L∞ analysis supports two statements:

1. equal nominal tolerance is not equal realized pointwise distortion across codecs;
2. after matching realized L∞ alone, codec-dependent differences in resolved-Bader error and certification remain in the matched sample.

It does **not** by itself identify the residual as a spatial-geometry effect.

## Stricter dual-control result

The preregistered realized-L∞ + RMSE control (`mechanism/geometry_control_v0_1/MATCHED_LINF_RMSE_REPORT.md`) returned **NOT SUPPORTED** at the primary 0.10-dex dual caliper:

- ZFP/SZ3: no matched materials / no common support at the primary dual caliper;
- ZFP/SPERR: 48 matched materials, resolved-Bader error ratio 1.30 [1.09, 1.45] after good scalar balance (matched L∞ ratio 1.07; matched RMSE ratio 1.00);
- SZ3/SPERR: 185 matched materials, ratio 0.91 [0.874, 0.94].

Therefore the manuscript must not currently say that the matched-L∞ residual *demonstrates* or *proves* codec-specific error geometry. The dual-control analysis is a negative/common-support result and must be retained.

## Pending stronger test

The preregistered residual spatial-permutation intervention is the appropriate causal mechanism test. It holds each codec's residual value multiset fixed (therefore L∞, L1/L2, RMSE, signed mean and histogram) while changing only fine spatial assignment within original-density rank strata, then re-solves Bader.

Until that intervention is complete, the strongest allowed wording is:

> Matching realized L∞ removes the dominant nominal-tolerance confound but leaves codec-dependent chemical differences in the matched sample; scalar dual matching shows that these observational residuals cannot yet be uniquely attributed to spatial error geometry.
