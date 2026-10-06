# General-QOAC law — prospective confirmation on the fresh P1 population

Freeze date: 2026-10-06. Frozen before any prediction or compression is computed on any P1 material.

## Population

`analysis/fresh_population_20261006/P1_CONFIRMATORY_MANIFEST.csv`: 60 fresh Materials Project bulk CHGCARs, never used in the
project (WS-0; ids and reduced formulas excluded against all 60 branches; selection rule frozen before download). The 12
`P1_ENGINEERING_MANIFEST.csv` materials are run through the identical pipeline as a technical shakedown. Their results are
reported but do not enter any criterion.

## Part A — Hartree potential: is the closed-form operator law near the operational optimum?

Code: `analysis/qoac_v03_rdo/run_engineering.py` (`material`), unchanged from the v0.3 engineering run; arms A0–A6 as in
`analysis/qoac_v03_rdo/DESIGN.md`. All streams are decode-verified (historical and Nyquist-safe Hartree relative RMSE < tau).
Primary tau = 1e-6; 1e-4 and 1e-8 are descriptive.

Hypotheses were formed on the 12 engineering materials (bulk medians at 1e-6: A3/A1 1.08, A3/A5 1.87, A1/A6 7.0,
A1/A2 1.37). Criteria at tau = 1e-6 (fixed-seed 20261006 bootstrap, 10,000 resamples, of the median):

- **A-H1 near-optimality of the closed-form law:** median CR_A3/CR_A1 <= 1.15 and CI upper bound <= 1.20.
- **A-H2 the operator metric is essential:** CR_A3 > CR_A5 in >= 90% of materials, median CR_A3/CR_A5 > 1.5, and CI lower
  bound > 1.35.
- **A-H3 closed-form law vs pointwise codecs, equal search:** CR_A1 > CR_A6 in >= 95%, and median CR_A1/CR_A6 > 4.
- **A-H4 closed-form law vs spectral truncation, equal search:** CR_A1 > CR_A2 in >= 75%, and median CR_A1/CR_A2 > 1.15.
- Validity: >= 58/60 materials analyzable, and A1 and A3 certified on every analyzable material.

## Part B — six operators: is the gain predictable before compression?

Operators (WS-B library `analysis/general_qoac_operators/operators.py`): `density` (control), `density_gradient`,
`density_laplacian`, `hartree_field`, `hartree_potential`, `gaussian_smoothed_density(sigma = 0.5 A)`.

For each material and operator, two arms of the closed-form policy codec (`analysis/general_qoac_law/policy_codec.py`):
- **opt:** u = w^{-1/2} (power_q with p = 0, -1, -2, 1, 2 respectively, or the Gaussian policy);
- **blind:** u = 1.

Each arm uses continuous alpha bisection on the exact orbit-space Nyquist-safe relative RMSE in that operator's metric
(margin 0.995). Every stream is decode-verified with `operators.relative_error(..., variant 'safe')` < tau. Targets: tau = 1e-6
(primary) and 1e-4. Observed gain: G_obs = bytes_blind / bytes_opt.

**Prediction (computed and committed in a separate CI run before any compression run starts):** WS-B finite-rate
Laplacian-ECSQ predictor `gain_predictors.finite_rate_gain(model, log_w, opt, blind, tau)` on each material's reference
spectrum:

    G_pred = (F + R_blind/8) / (F + R_opt/8),

where R are the predicted bits and F is the geometry-only container size (`run_calibration.fixed_bytes_v02`). The high-rate
predictor (a) is recorded alongside, without criteria.

Criteria at tau = 1e-6, pooled over the 60 materials x 5 non-control operators:
- **B-H1 calibration:** median |ln(G_pred/G_obs)| <= ln(1.25).
- **B-H2 ranking:** Spearman rank correlation between G_pred and G_obs >= 0.85.
- **B-H3 operator ordering:** for every pair of operators whose median G_pred differ by more than 5%, the median G_obs
  are ordered the same way.
- **B-H4 null-gain operators:** for every operator with median G_pred < 1.05 (predicted no material gain), G_obs is in
  [0.90, 1.11] in >= 80% of materials.
- Control: for `density`, opt and blind are the same policy; G_obs = 1 is a pipeline check.
- Validity: >= 58/60 materials analyzable; every opt and blind arm certified.

## Execution order (enforced by CI)

1. `PHASE=predict`: compute predictions for P1 engineering + confirmatory; commit
   `analysis/general_qoac_law/results/predictions/`.
2. `PHASE=run`: preflight refuses to start unless the committed predictions exist for every material. Then run Part A and
   Part B, and aggregate with the criteria above.

No codec parameter, operator definition, policy, margin or tolerance may change after step 1.

## Amendment 1 (2026-10-06, after the P1 confirmation; before any P3b candidate is downloaded)

A second prospective cohort, **P3b**, consists of fresh NOMAD VASP surface slabs drawn under
`analysis/fresh_population_20261006/P3B_SELECTION_RULE.md`: one material per distinct reduced formula, at most 6 per
upload, and every used upload, id and formula excluded. It is analysed with this protocol unchanged:
- the same Part A and Part B arms, tolerances and criteria;
- predictions committed before compression;
- validity scaled to at least n - 2 of n.

The workflow is `.github/workflows/general_qoac_law_p3b.yml`, with phases select, predict and run, each controlled by
`analysis/general_qoac_law/P3B_PHASE`. P3b tests whether the confirmed law transfers to surfaces from a second database.
It does not alter the P1 result.
