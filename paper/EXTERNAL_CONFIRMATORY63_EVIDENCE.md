# Final external confirmatory evidence — 63/63

Status: **PASS** (2026-09-08)

The primary external rate–fidelity cohort was frozen at 63 systems before the corpus-scale run. Following completion of the final AFLOW recovery, all 63 systems are now complete under the frozen scientific implementation (`893f931b3045b0b628329db81999c2f439d4e830`). The final confirmatory aggregate contains 1,689 retained rows, no material-level pipeline failures, no codec-bound violations, and the exact pre-frozen Protocol A.1 eligible counts of 16, 42, and 57 systems at `1e-4`, `1e-3`, and `1e-2` e.

## Claim support

### Rate–fidelity ordering

The three pre-specified development-set directional expectations all reproduce:

- `1e-4 e`: **ZFP > SZ3 > SPERR** — medians 13.03, 12.06, 5.17.
- `1e-3 e`: **ZFP ≈ SZ3 > SPERR** — medians 18.76, 18.76, 6.40.
- `1e-2 e`: **SZ3 > ZFP > SPERR** — medians 65.89, 40.57, 10.82.

At `1e-2 e`, SZ3 beats ZFP on 89.47% of admitted external materials (bootstrap interval 80.70–96.49%). At `1e-4 e`, ZFP beats SZ3 on 68.75%; the direction remains consistent with development but the effect is narrower and should not be described as a strong separation.

### Realized distortion budget

The recovered final material preserves the characteristic budget-realization behavior: ZFP median realized-L∞ / nominal = 0.1569, while SZ3 and SPERR are essentially 1.0. Together with the 62-system interim aggregate, this completes the external replication of the development observation that equal nominal tolerance is not a codec-independent distortion control.

### Resolved versus fixed-basin Bader error

The external cohort reproduces the development finding that fixed-basin integration can substantially understate the error obtained when Bader basins are re-derived on the reconstructed field. This remains evidence that downstream partition response cannot be inferred from fixed-domain integration alone.

### Error-field organization

External error-structure diagnostics reproduce the development pattern, including larger directional signed-bias fraction for SZ3 than ZFP/SPERR. Separately, the independent Bader/error-organization supplement in `mechanism/independent_bader_20260908/` shows that the perturbation response is not specific to BaderKit and that rearranging the same error-value multiset can change Bader response, while a periodic shift is approximately null. This supports the cautious claim that error-field organization matters beyond scalar distortion magnitude, without asserting a unique boundary-local causal mechanism.

## Independent Bader implementation robustness

The supplementary cross-implementation study is deliberately separate from the frozen benchmark and external confirmatory analysis. It contains 1,560/1,560 expected outcome rows across a stratified development panel and three solver modes. Henkelman on-grid reproduces BaderKit on-grid codec response with median ratio 1.00 (IQR 0.92–1.005), aside from systems whose unperturbed baselines already differ because of basin-set differences. Codec ordering at relative tolerance `1e-4` is preserved across BaderKit on-grid, Henkelman on-grid, and Henkelman near-grid.

## Required manuscript nuance

The external cohort is generally more numerically stable than the development corpus, so external CCRs are commonly higher. At `1e-4 e`, the ZFP–SZ3 gap narrows substantially and confidence intervals overlap. NOMAD isolated 2D systems should be described as `vacuum-containing 2D` rather than as direct geometric replicas of adsorbate slabs.

## Recommended manuscript sentence

> On the fully completed 63-system pre-frozen external cohort, all three pre-specified rate–fidelity directional expectations reproduced: ZFP > SZ3 > SPERR at 10^-4 e, ZFP ≈ SZ3 > SPERR at 10^-3 e, and SZ3 > ZFP > SPERR at 10^-2 e. The external data also reproduced the principal mechanistic diagnostics identified in development, while the ZFP–SZ3 separation at the tightest tolerance was appreciably narrower.

Machine-readable source: `validation/final_external_confirmatory63_20260908/confirmatory63/`.
