# Global electron-count deviation negative control

Question: can the approximately twofold codec-associated Bader-error residual be explained by global electron-count/integral deviation rather than Bader-domain migration?

Analysis set: Protocol-A.1 eligible at 1e-3 e; nominal relative tolerance <=0.01; conservative complete-case exclusion of 20 failure-affected materials; common realized-Linf support [1.0049e-05, 24.9933].
Rows/materials: 3925 / 132. Electron-deviation pseudocount = half the minimum positive observed value = 1.266e-10.

## Codec coefficients

- SZ3/ZFP, M0_Linf_codec_material: **2.34x** [2.15,2.53], p=6.66e-92.
- SZ3/ZFP, M_electron: **2.58x** [2.23,2.97], p=1.66e-38.
- SZ3/ZFP, M_reassign: **0.96x** [0.83,1.10], p=0.55.
- SZ3/ZFP, M_both: **1.02x** [0.87,1.18], p=0.839.

- SPERR/ZFP, M0_Linf_codec_material: **2.08x** [1.91,2.26], p=5.11e-66.
- SPERR/ZFP, M_electron: **2.06x** [1.90,2.24], p=6.44e-65.
- SPERR/ZFP, M_reassign: **0.94x** [0.82,1.07], p=0.36.
- SPERR/ZFP, M_both: **0.94x** [0.82,1.07], p=0.339.

## Covariate coefficients

- M_electron, logElectronDev: beta=-0.030 [-0.057,-0.003], p=0.0277.
- M_reassign, logReassign: beta=0.880 [0.723,1.037], p=5.78e-28.
- M_both, logElectronDev: beta=-0.017 [-0.040,0.006], p=0.139.
- M_both, logReassign: beta=0.879 [0.722,1.036], p=5.25e-28.

## Interpretation rule

- If adding global electron-count deviation leaves codec multipliers near the M0 values while reassignment collapses them toward 1, global conservation error is not a plausible explanation of the codec-associated residual.
- If electron-count deviation itself strongly attenuates the codec coefficient, the manuscript must describe global integral bias as an additional mechanism and avoid attributing the residual mainly to basin migration.
- The model is an observational negative control and must not be described as causal mediation.

## Within-material Spearman matrix

|                       |   within_logQ |   within_logL |   within_logElectronDev |   within_logReassign |
|:----------------------|--------------:|--------------:|------------------------:|---------------------:|
| within_logQ           |      1        |      0.93936  |                0.857852 |             0.963107 |
| within_logL           |      0.93936  |      1        |                0.881357 |             0.970185 |
| within_logElectronDev |      0.857852 |      0.881357 |                1        |             0.885736 |
| within_logReassign    |      0.963107 |      0.970185 |                0.885736 |             1        |
