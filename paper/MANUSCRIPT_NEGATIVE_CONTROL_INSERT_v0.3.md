# Manuscript insertion — global conservation negative control

Use this paragraph at the end of Results section 4 (“Basin reassignment statistically accounts for the codec-associated residual”) or as the first paragraph of the corresponding Supplementary Results.

## Recommended Results text

The attenuation is not reproduced by a simpler global-conservation proxy. As a negative control, we added the absolute deviation in total integrated electron count (`electron_count_abs_dev`) to the same complete-case, material-fixed-effect model. This variable does not attenuate the codec-associated residual: the SZ3/ZFP multiplier changes from 2.34 to 2.58 and the SPERR/ZFP multiplier from 2.08 to 2.06. By contrast, adding the reassigned-voxel fraction reduces the multipliers to 0.96 and 0.94. When both covariates are included, the codec multipliers remain near unity (1.02 and 0.94), the global electron-count term is not significant (log–log coefficient −0.017, 95% CI −0.040 to 0.006; p=0.139), and basin reassignment remains strongly associated with Bader error (0.879, 0.722–1.036; p=5.25×10^-28). Thus the codec-associated pattern is not explained by a global integration/conservation error; the variable that specifically records redistribution of the field-derived Bader domains accounts for the residual.

## Recommended Discussion sentence

A global electron-count deviation provides a useful negative control: it is correlated with increasing perturbation magnitude but does not absorb the codec-associated residual once measured L∞ and material identity are controlled, whereas basin reassignment does. This contrast strengthens the interpretation that the relevant structural error is redistribution among atomic domains rather than simple loss of total integrated charge.

## Scope caveat

This is an observational negative-control analysis, not causal mediation. `electron_count_abs_dev` and `frac_voxels_reassigned` are both post-compression quantities and strongly covary with reconstruction magnitude. The direct integrand/domain identity in the representative mechanism set remains the primary mechanistic evidence.

Data: `paper_data_v03/global_conservation_negative_control.md` and `paper_data_v03/global_conservation_negative_control_coefficients.csv`.
