# Supplementary extension — QoI generality and qualification robustness

This supplementary extension records the four pre-declared analyses in `analysis/extensions_20260928/PROTOCOL.md`. The main manuscript promotes only the second-QoI generality result; the other work packages remain robustness, method-selection, and limitation evidence.

## S12. Continuous QSQ risk calibration

The measured stability floor contains graded risk information beyond the binary eligibility flag. Models based on (x_m(\tau)=\log_{10}(f_m/\tau)) were evaluated by 10-fold cross-validation over materials against the frozen 59-trial prospective outcomes.

Across 44,958 trial-threshold outcomes, all calibrated models reduced held-out Brier score relative to the binary gate. The best logistic model reached 0.0412 versus 0.0651 for the gate, while isotonic regression reached 0.0464. The pre-declared replacement criterion also required greater coverage under a 2% risk contract at (10^{-3} e). This was not met: cross-validated isotonic admission was 115/254 materials (45.3%) versus 143/254 (56.3%) for the binary gate. The admitted isotonic subset showed 16/6,785 fresh exceedances (0.236%).

The continuous statistic is therefore a sharper prospective risk predictor, but these data do not justify replacing the simpler binary QSQ eligibility contract.

## S13. Qualification of grid-local density extrema

A second topology-sensitive QoI was defined directly on the sampled density grid. A voxel is a strict local maximum when its value exceeds all 26 neighbours and a strict local minimum when it is smaller than all 26 neighbours under periodic indexing. No smoothing, interpolation, or continuous critical-point search is applied; the reader-facing term is therefore **grid-local density extrema**.

All 254 development materials were evaluated. The full reconstruction analysis regenerated 6,343 benchmark rows; 6,293 were scored and 50 had recorded non-gate reconstruction failures. All 16,256 perturbation evaluations completed: five qualification perturbations and 59 fresh perturbations per material.

At the strict endpoint, qualification requires the maximum-voxel set to remain identical under all five QSQ perturbations. This admits 118/254 materials. The count-only five-seed criterion admits 141/254 and is retained as a secondary diagnostic.

Prospectively, 0/6,962 fresh trials on qualified materials change the number of maxima, compared with 6,444/8,024 (80.31%) on screen-rejected materials. For maximum-set identity, the corresponding rates are 3/6,962 (0.04%) and 7,509/8,024 (93.58%).

Cross-QoI transfer is weak. Comparing strict extrema eligibility with Bader eligibility at (10^{-3} e) gives 75 both eligible, 68 Bader-only, 43 extrema-only, and 68 neither; raw agreement is 56.3% and Cohen's kappa is 0.1337 (95% bootstrap interval 0.0164-0.2542). Spearman correlation between the Bader and extrema stability floors is 0.1389 (0.0280-0.2554).

The observables are also non-redundant on reconstructed fields. Among 6,293 scored reconstructions, 908 (14.43%) preserve the maximum count while having Bader error at least (10^{-3} e), whereas 655 (10.41%) change the maximum count while keeping Bader error below (10^{-3} e).

These results support a general qualification principle while showing that the evaluability boundary depends on the downstream QoI.

## S14. Codec-shaped perturbation robustness

Codec-shaped probes were constructed from residual fields at the common base relative tolerance of (10^{-5}), periodically shifted to remove original alignment, and rescaled to the same material-specific QSQ amplitude. All 4,572 planned Bader re-solves completed.

The material-median (log_{10}(f_m^c/f_m)) is -0.196 for ZFP (95% CI -0.255 to -0.134), -0.000 for SZ3 (-0.010 to +0.008), and -0.027 for SPERR (-0.042 to -0.010). Under the pre-declared rule, the iid family is conservative on aggregate for ZFP and SPERR and statistically indistinguishable from the codec-shaped family for SZ3.

At (10^{-3} e), iid-versus-codec-shaped eligibility agreement is 0.902 for ZFP and 0.937 for SZ3 and SPERR. Among the 143 iid-qualified materials, codec-shaped floors do not improve prediction of the frozen 59-trial prospective risk. For ZFP, the Spearman correlation falls from 0.549 for the iid floor to 0.420 for the codec-shaped floor, a difference of -0.128 (95% CI -0.218 to -0.050); differences for SZ3 and SPERR are unresolved.

Correlation between low-G residual-energy fraction and the codec-shaped/iid floor ratio is near zero for ZFP, weakly negative for SZ3, and unresolved for SPERR. The Fourier mechanism that explains Hartree error therefore does not provide a common scalar explanation for Bader stability.

## S15. Reference-density predictors do not replace direct QSQ measurement

Complete reference-density descriptors were obtained for 318/319 systems; one external AFLOW density remained unavailable and is preserved as a recorded failure.

The strongest univariate association with (log_{10} f_m) is the fraction of basin-boundary neighbour gaps below the QSQ perturbation scale, with Spearman rho 0.554 (95% CI 0.463-0.639). Other boundary-gap and near-tie descriptors also correlate with the floor, supporting a link between numerical fragility and local ordering margins near basin boundaries.

Nested 10-fold cross-validation of the pre-declared ridge model gives (R^2=0.238) and RMSE 0.932 decades over the 318 descriptor-complete systems. More importantly, fitting on the 254 development systems and evaluating on the 64 descriptor-complete external systems gives held-out (R^2=0.134) (95% CI -0.410 to 0.385) and RMSE 1.208 decades. The pre-declared external (R^2\ge 0.5) replacement criterion is not met.

These descriptors are scientifically informative but are not sufficient to replace direct QSQ measurement. In the present benchmark, stability remains an empirically measured property of a specified density, QoI, and downstream algorithm.
