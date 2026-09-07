# Figure 6 interpretation status

Date: 2026-09-07

## What the current matched-L∞ figure supports

The existing matched-realized-L∞ analysis supports two statements:

1. equal nominal tolerance is not equal realized pointwise distortion across codecs;
2. after matching realized L∞ alone, codec-dependent differences in resolved-Bader error and certification remain in the matched sample.

It does **not** by itself identify the residual as a spatial-geometry effect.

## The L∞-matched sample is strongly RMSE-imbalanced

The preregistered diagnostic in `mechanism/linf_matched_rmse_diagnostic_v0_1/LINF_MATCHED_RMSE_DIAGNOSTIC_REPORT.md` audits the exact logical weakness in an L∞-only interpretation. At the primary 0.10-dex L∞ caliper:

- **ZFP/SZ3:** 214 materials, 457 matched pairs; Bader-error ratio `0.557 [0.523, 0.599]`, but RMSE ratio is only `0.376 [0.365, 0.382]` while matched L∞ is `1.05`;
- **ZFP/SPERR:** 206 materials, 465 matched pairs; Bader-error ratio `0.601 [0.534, 0.664]`, but RMSE ratio is only `0.437 [0.426, 0.448]` while matched L∞ is `1.06`;
- **SZ3/SPERR:** 254 materials, 1848 pairs; Bader-error ratio `1.03 [0.977, 1.07]`, RMSE ratio `1.29 [1.27, 1.30]`, matched L∞ `1.00`.

The RMSE imbalance is large and persists at every pre-specified L∞ caliper from 0.05 to 0.30 dex. Therefore the apparent ~40% ZFP Bader-error advantage after L∞ matching is still confounded by a second scalar error-magnitude property: ZFP carries substantially less RMS error at comparable maximum error.

Equivalently, at the primary L∞ match the normalized error-energy shape factor `RMSE/L∞` is about `0.346×` for ZFP/SZ3 and `0.416×` for ZFP/SPERR. Equal maximum error is therefore very far from equal error distribution.

## Stricter dual-control result

The preregistered realized-L∞ + RMSE control (`mechanism/geometry_control_v0_1/MATCHED_LINF_RMSE_REPORT.md`) returned **NOT SUPPORTED** at the primary 0.10-dex dual caliper:

- ZFP/SZ3: no matched materials / no common support at the primary dual caliper;
- ZFP/SPERR: 48 matched materials, resolved-Bader error ratio `1.30 [1.09, 1.45]` after good scalar balance (matched L∞ ratio `1.07`; matched RMSE ratio `1.00`);
- SZ3/SPERR: 185 matched materials, ratio `0.91 [0.874, 0.94]`.

Thus the observational evidence does **not** support the statement that ZFP has an intrinsic spatial-geometry advantage once scalar error energy is controlled. The existing Figure 6 title/panel wording that calls the L∞-matched residual a “geometry effect” is too strong and must be revised.

## Pending intervention

The preregistered residual spatial-permutation intervention remains useful, but its question is now narrower and cleaner: does changing spatial assignment while holding the codec residual value multiset fixed alter Bader fidelity at all, and does it attenuate codec contrasts in the representative mechanism set?

The intervention preserves each codec's residual multiset (therefore L∞, L1/L2, RMSE, signed mean and histogram) and changes only fine spatial assignment within original-density rank strata. A provenance addendum freezes same-run pinned Bader baselines because the 2026-09-01 Windows Bader environment was not package-pinned.

## Allowed manuscript wording now

> Equal nominal tolerance is not equal realized distortion, and equal realized L∞ is still not equal error energy. In L∞-matched pairs, ZFP carries only ~38–44% of the RMSE of SZ3/SPERR, so the residual Bader advantage cannot be uniquely attributed to spatial error geometry. When both L∞ and RMSE are controlled, the ZFP advantage is not supported in the available common-support sample.
