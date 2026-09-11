# QSQ research audit

Status: executed retrospective audit, not prospective confirmation.

Source commit: `6aeef9eed05df5551dcec4109174de4a62a8d7c2`. Frozen inputs unchanged; original Figure 3 counts reproduced exactly.

## Common-ladder comparison

| design | tau_e | n_decisions | unavailable | numerical_pass | no_pass_observed | non_evaluable_no_pass | fraction_no_pass_non_evaluable | non_evaluable_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_record | 0.0001 | 762 | 0 | 229 | 533 | 518 | 0.971857 | 0.818898 |
| full_record | 0.001 | 762 | 0 | 452 | 310 | 296 | 0.954839 | 0.437008 |
| full_record | 0.01 | 762 | 0 | 654 | 108 | 61 | 0.564815 | 0.0984252 |
| base_only | 0.0001 | 762 | 0 | 22 | 740 | 616 | 0.832432 | 0.818898 |
| base_only | 0.001 | 762 | 0 | 238 | 524 | 296 | 0.564885 | 0.437008 |
| base_only | 0.01 | 762 | 0 | 643 | 119 | 61 | 0.512605 | 0.0984252 |
| shared_base_rungs | 0.0001 | 762 | 0 | 22 | 740 | 616 | 0.832432 | 0.818898 |
| shared_base_rungs | 0.001 | 762 | 0 | 238 | 524 | 296 | 0.564885 | 0.437008 |
| shared_base_rungs | 0.01 | 762 | 0 | 643 | 119 | 61 | 0.512605 | 0.0984252 |

`base_only` removes the eligibility-targeted tight extension. `shared_base_rungs` additionally keeps only within-material nominal rungs observed for all three codecs; this is observed-support sensitivity, not a missingness cure. Neither makes nominal error equal realized error. `no_pass_observed` means no available rung passed, not proof of intrinsic compressor failure. Full per-codec results, material-cluster intervals, eligibility prevalence and no-pass risks are in `ladder_summary.csv`. Report prevalence alongside reclassification: an already-large excluded population can produce a large concentration of no-pass outcomes.

## Four training seeds to one held-out seed

| tau_e | n_materials | eligible_splits | heldout_exceedances | heldout_exceedance_fraction | affected_materials | material_cluster_ci_low | material_cluster_ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.0001 | 319 | 338 | 18 | 0.0532544 | 18 | 0.0303011 | 0.0816327 |
| 0.001 | 319 | 947 | 12 | 0.0126716 | 12 | 0.00617841 | 0.0207373 |
| 0.01 | 319 | 1441 | 1 | 0.000693963 | 1 | 0 | 0.00213828 |

Each material occurs in five correlated splits; uncertainty resamples materials, never treats 1,595 splits as independent materials. Seeds were already used in development. This estimates retrospective four-seed screening fragility, NOT the false-eligibility rate of the deployed five-seed rule on fresh perturbations. A degenerate bootstrap interval at zero events is NOT a zero upper error bound. Results for one/two/three training seeds are exploratory and have different held-out-set sizes, so their rates are not a controlled seed-budget comparison. External descriptive records are not the 63-system confirmatory cohort.

## Next decisive experiments

Freeze a new perturbation/validation manifest before new runs; retain the current QSQ record. Test fresh seeds and independently specified perturbation families; measure both rejection coverage and conditional held-out exceedance risk. Separate deterministic pipeline fidelity from perturbation robustness. A single valid counterexample refutes uniform robustness; no finite random probe panel establishes it without assumptions. Under independent Bernoulli trials from one fixed perturbation distribution, zero exceedances in n trials gives one-sided 95% upper limit 1-0.05**(1/n). This is about perturbation risk for that target/family, not risk across materials or all possible perturbations.

For n=5 this limit is 0.450720; for n=59 it is 0.049508. Multiple families/materials require separately declared multiplicity handling.

## Integrity

No densities, reconstruction rows, seeds, thresholds, protocol files or frozen labels were changed. All outputs are additive; no new scientific measurements were synthesized.
