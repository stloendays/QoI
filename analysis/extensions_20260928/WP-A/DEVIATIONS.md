# WP-A — deviations and operational choices

No pre-declared rule of the WP-A section of `../PROTOCOL.md` was changed. The protocol leaves
several mechanical details unspecified; the choices below were fixed in `run_wpa.py` before
any outcome-dependent number was inspected, and are recorded here so they can be audited.

## Operational choices (protocol silent)

1. **Fold assignment.** `fold = int(sha256("20260928|" + material_id).hexdigest(), 16) mod 10`.
   Resulting fold sizes (materials): 23, 23, 32, 27, 19, 19, 28, 28, 26, 29 (sum 254). The same
   fold holds a material for all three τ, so no material appears in both training and test.
2. **τ as covariate.** For the two logistic fits the covariate is `log10(τ)` alongside
   `x = log10(f_m/τ)`. Isotonic regression is univariate by construction, so it is fitted on the
   pooled 762 material–τ rows with τ entering only through `x` (sample weight = 59 trials, i.e.
   uniform). This is the only way "pooled across τ" can be realised for an isotonic fit.
3. **Secondary predictors** are the literal quantities named in the protocol:
   `log10(median over 5 seeds of floor_noise_resolved_e)`, `log10(mean over 5 seeds)`, and
   `log10(max) − log10(min)` over the five seeds. They are not normalised by τ (τ is a separate
   covariate, so the parameterisation is equivalent for an unpenalised logistic fit).
4. **Logistic estimation.** Unpenalised maximum likelihood (`statsmodels` GLM, binomial family)
   on the 44,958 trial-level rows (14,986 trials × 3 τ); cluster-robust covariance by material
   (254 clusters) as pre-declared. The predictions do not depend on the covariance choice.
5. **Metric level.** Brier score, log loss and AUC are computed at the trial level (the outcome
   `y_{m,s}(τ)` is a trial); predictions are constant within a material–τ pair. AUC uses the
   Mann–Whitney statistic with ties counted 0.5. ECE and the reliability table use 10
   equal-count bins over the 762 material–τ rows (or 254 rows per τ), with observed = pooled
   exceedances / pooled trials in the bin. Because every material has exactly 59 trials,
   trial-weighted and material-weighted bin means coincide.
6. **Ties in equal-count binning.** The binary gate has only two distinct predicted values, so
   equal-count bins must split tied predictions. Ties are broken by a deterministic pseudo-random
   key, `sha256("20260928|tiebreak|material_id|τ")`, which splits a tied group without regard to
   x or outcome; the ECE of a constant-within-group model is therefore the tie-pooled value plus
   sampling noise, not an inflated value.
7. **Log loss with predicted 0 or 1.** Isotonic regression predicts exact 0 or 1 in the tails;
   predictions are clipped to `[1e-6, 1 − 1e-6]` for the log loss only. Brier, AUC and ECE use the
   unclipped predictions.
8. **Bootstrap.** Material-cluster bootstrap, 2,000 resamples, `numpy.random.default_rng(20260928)`,
   applied to the fixed out-of-fold predictions (models are not refitted inside the bootstrap).
   The same 2,000 resamples are used for every metric, every subset, the Brier/log-loss
   differences versus the gate, and the contract-table coverages and observed rates.
9. **Contract cutoff.** The protocol asks for "the largest x at which the cross-validated
   isotonic risk ≤ p*". Implemented as: for each fold k, the isotonic model fitted on the other
   nine folds defines a monotone step function; its cutoff `x*_k(p*)` is the largest training x
   whose fitted risk is ≤ p* (−∞ if none). Held-out materials in fold k are admitted at τ iff
   `x_m(τ) ≤ x*_k(p*)`. Coverage and the observed exceedance rate among the admitted are therefore
   fully held-out. The single `x_cutoff` column reports the same quantity from the isotonic
   model fitted on all 254 materials; the fold-wise minimum, median and maximum are reported
   alongside. An extra comparison row at p* = 1.6% (the gate's realised eligible-group risk) is
   included and labelled `isotonic_cv_gate_risk_comparison`; it is not one of the five
   pre-declared p* levels.
10. **Extra files.** `coefficients.csv` (logistic coefficients with cluster-robust SE) and
    `cv_folds.csv` (fold membership sizes and per-fold cutoffs) are written in addition to the
    pre-declared outputs; nothing pre-declared is omitted.
11. **Environment.** The package is statistics-only, so it was run on Windows 11 with
    CPython 3.12.14 (uv-managed) rather than the Ubuntu scientific stack; package versions are
    in `provenance.json`. No density, codec or Bader code was executed.

## Reruns

The script was run three times. The second run changed only the x-axis range of panel (b) of
`fig_calibration` (from the full data range to [−3.2, 3.2], with the 9 rows at x < −3 and the
5 rows at x > 3 noted in the panel); the third moved that note so it no longer overlaps the
points. No statistic, seed, fold, fit or table changed between the runs: the SHA-256 of every
CSV output was identical after runs 2 and 3 (checked before committing).
