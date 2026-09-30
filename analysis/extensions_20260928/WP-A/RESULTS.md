# WP-A — Calibrated risk model for QSQ: results

Frozen inputs, repository commit `b74ede8` (branch base `paper-20260927`), protocol `analysis/extensions_20260928/PROTOCOL.md` (SHA-256 `c2002d615bf3…`). Statistics only; no density download, codec round trip or Bader solve was run. Wall time of `run_wpa.py`: 152.2 s. Failures: none (0 rows dropped; the package performs no solver or download step, so `failures.csv` is not applicable).

## Verdict (acceptance rule applied literally)

**The binary gate is not improved by the continuous statistic on these data** (protocol acceptance: both conditions must hold; condition (ii) fails).

- Condition (i), held-out Brier lower than the gate with a material-bootstrap 95% CI excluding zero: **met** for every calibrated model. Isotonic on x: ΔBrier = -0.0187 [-0.0240, -0.0140]; best model (Logistic on x + secondary (+ log10 τ)): ΔBrier = -0.0239 [-0.0300, -0.0182] (pooled over τ, 762 material–τ rows, 44,958 trials).
- Condition (ii), coverage at p* = 2% and τ = 1e-3 e exceeds 56.3%: **not met**. The cross-validated isotonic contract admits 115/254 materials = 45.3% [39.0%, 51.6%] versus 143/254 = 56.3% for the gate. Among the admitted, the held-out exceedance rate is 16/6785 = 0.236% [0.000%, 0.657%], versus the gate's 135/8437 = 1.600%.
- Reading: the continuous statistic is a sharper and better-calibrated predictor than the gate (all three models: lower Brier and log loss, higher AUC), but a contract that promises ≤ 2% risk must stop at x* = -0.256 (f_m ≤ 0.55 τ; fold-wise cutoffs -0.263 to -0.222), because the fresh-exceedance risk rises from below 1% to about 10% between x ≈ −0.26 and x = 0. The gate's 1.600% is the average over that whole band, not a rate that holds uniformly inside it.

## Anchor verification (before any fit)

- `outcomes.csv`: 14,986 rows, 254 materials, 59 trials per material, 0 non-finite responses.
- τ = 1e-3 e: eligible (f_m < τ) 143 materials, 135/8,437 exceedances (1.600%); rejected 111 materials, 5,326/6,549 (81.325%). All anchors reproduced; f_m equals the five-seed maximum of `floor_noise_resolved_e` for all 254 materials.

## Design

- Predictor x_m(τ) = log10(f_m/τ), τ ∈ {1e-4, 1e-3, 1e-2} e; pooled fits with log10 τ as covariate (isotonic: pooled on x, see `DEVIATIONS.md` item 2). Secondary predictors: log10 five-seed median, log10 five-seed mean, five-seed log10 span.
- Outcome y = 1[bader_response_max_e ≥ τ] per fresh trial; 254 × 59 × 3 = 44,958 trial–τ rows; 762 material–τ rows.
- 10-fold CV over materials, folds from SHA-256 of material_id with seed 20260928 (fold sizes 23, 23, 32, 27, 19, 19, 28, 28, 26, 29); all logistic fits converged in every fold.
- Material-cluster bootstrap, 2,000 resamples, seed 20260928, for every CI below.

## Held-out metrics, pooled over τ (762 material–τ rows, 44,958 trials)

| Model | Brier | Log loss | AUC | ECE (10 equal-count bins) | ΔBrier vs gate | Δlog loss vs gate |
|---|---|---|---|---|---|---|
| Binary gate (1.600% / 81.325%) | 0.0651 [0.0575, 0.0725] | 0.2287 [0.2080, 0.2485] | 0.9356 [0.9261, 0.9452] | 0.0205 [0.0136, 0.0361] | — | — |
| Logistic on x (+ log10 τ) | 0.0474 [0.0421, 0.0526] | 0.1600 [0.1427, 0.1775] | 0.9844 [0.9809, 0.9876] | 0.0193 [0.0111, 0.0291] | -0.0178 [-0.0236, -0.0123] | -0.0687 [-0.0848, -0.0518] |
| Isotonic on x | 0.0464 [0.0409, 0.0519] | 0.1559 [0.1382, 0.1731] | 0.9826 [0.9787, 0.9860] | 0.0068 [0.0035, 0.0162] | -0.0187 [-0.0240, -0.0140] | -0.0728 [-0.0871, -0.0587] |
| Logistic on x + secondary (+ log10 τ) | 0.0412 [0.0367, 0.0462] | 0.1465 [0.1287, 0.1683] | 0.9868 [0.9831, 0.9897] | 0.0124 [0.0071, 0.0205] | -0.0239 [-0.0300, -0.0182] | -0.0822 [-0.1001, -0.0609] |

Values are point estimates with material-bootstrap 95% CIs. Lowest held-out Brier: Logistic on x + secondary (+ log10 τ) (0.0412); lowest ECE: isotonic on x.

## Held-out metrics per τ (254 material–τ rows, 14,986 trials each)

| τ (e) | Model | Brier | AUC | ECE | ΔBrier vs gate |
|---|---|---|---|---|---|
| 0.0001 | Binary gate (1.600% / 81.325%) | 0.1027 [0.0843, 0.1213] | 0.8045 [0.7559, 0.8523] | 0.0535 [0.0408, 0.0856] | — |
| 0.0001 | Logistic on x (+ log10 τ) | 0.0635 [0.0501, 0.0778] | 0.9662 [0.9522, 0.9775] | 0.0180 [0.0092, 0.0349] | -0.0392 [-0.0511, -0.0285] |
| 0.0001 | Isotonic on x | 0.0669 [0.0519, 0.0829] | 0.9627 [0.9475, 0.9753] | 0.0329 [0.0173, 0.0483] | -0.0358 [-0.0461, -0.0269] |
| 0.0001 | Logistic on x + secondary (+ log10 τ) | 0.0582 [0.0456, 0.0721] | 0.9711 [0.9583, 0.9811] | 0.0101 [0.0070, 0.0250] | -0.0445 [-0.0574, -0.0327] |
| 0.001 | Binary gate (1.600% / 81.325%) | 0.0752 [0.0593, 0.0935] | 0.9234 [0.9012, 0.9430] | 0.0171 [0.0135, 0.0457] | — |
| 0.001 | Logistic on x (+ log10 τ) | 0.0617 [0.0489, 0.0745] | 0.9751 [0.9651, 0.9836] | 0.0421 [0.0255, 0.0587] | -0.0135 [-0.0266, -0.0018] |
| 0.001 | Isotonic on x | 0.0574 [0.0454, 0.0696] | 0.9732 [0.9629, 0.9823] | 0.0218 [0.0119, 0.0399] | -0.0179 [-0.0297, -0.0074] |
| 0.001 | Logistic on x + secondary (+ log10 τ) | 0.0518 [0.0407, 0.0631] | 0.9797 [0.9712, 0.9865] | 0.0143 [0.0101, 0.0329] | -0.0235 [-0.0356, -0.0129] |
| 0.01 | Binary gate (1.600% / 81.325%) | 0.0175 [0.0085, 0.0280] | 0.9807 [0.9650, 0.9924] | 0.0148 [0.0134, 0.0305] | — |
| 0.01 | Logistic on x (+ log10 τ) | 0.0170 [0.0099, 0.0244] | 0.9944 [0.9888, 0.9984] | 0.0172 [0.0060, 0.0264] | -0.0005 [-0.0062, 0.0044] |
| 0.01 | Isotonic on x | 0.0150 [0.0081, 0.0227] | 0.9945 [0.9889, 0.9984] | 0.0079 [0.0023, 0.0168] | -0.0026 [-0.0074, 0.0012] |
| 0.01 | Logistic on x + secondary (+ log10 τ) | 0.0137 [0.0080, 0.0201] | 0.9956 [0.9912, 0.9986] | 0.0118 [0.0036, 0.0233] | -0.0038 [-0.0110, 0.0020] |

At τ = 1e-2 e the Brier improvement over the gate is not resolved (CIs include zero); at τ = 1e-4 and 1e-3 e it is.

## Reliability table, pooled over τ, held-out (10 equal-count bins of ~76 material–τ rows)

**Binary gate (1.600% / 81.325%)**

| bin | n materials–τ | n trials | predicted range | mean predicted | exceedances | observed |
|---|---|---|---|---|---|---|
| 0 | 77 | 4,543 | 1.60e-02–1.60e-02 | 0.0160 | 77 | 0.0169 |
| 1 | 76 | 4,484 | 1.60e-02–1.60e-02 | 0.0160 | 30 | 0.0067 |
| 2 | 76 | 4,484 | 1.60e-02–1.60e-02 | 0.0160 | 57 | 0.0127 |
| 3 | 76 | 4,484 | 1.60e-02–1.60e-02 | 0.0160 | 35 | 0.0078 |
| 4 | 76 | 4,484 | 1.60e-02–1.60e-02 | 0.0160 | 29 | 0.0065 |
| 5 | 77 | 4,543 | 1.60e-02–8.13e-01 | 0.4302 | 2056 | 0.4526 |
| 6 | 76 | 4,484 | 8.13e-01–8.13e-01 | 0.8133 | 3589 | 0.8004 |
| 7 | 76 | 4,484 | 8.13e-01–8.13e-01 | 0.8133 | 3765 | 0.8397 |
| 8 | 76 | 4,484 | 8.13e-01–8.13e-01 | 0.8133 | 3934 | 0.8773 |
| 9 | 76 | 4,484 | 8.13e-01–8.13e-01 | 0.8133 | 3861 | 0.8611 |

**Logistic on x (+ log10 τ)**

| bin | n materials–τ | n trials | predicted range | mean predicted | exceedances | observed |
|---|---|---|---|---|---|---|
| 0 | 77 | 4,543 | 2.20e-16–5.86e-06 | 0.0000 | 0 | 0.0000 |
| 1 | 76 | 4,484 | 5.93e-06–1.52e-04 | 0.0000 | 0 | 0.0000 |
| 2 | 76 | 4,484 | 1.65e-04–1.71e-03 | 0.0007 | 0 | 0.0000 |
| 3 | 76 | 4,484 | 1.79e-03–1.16e-02 | 0.0051 | 8 | 0.0018 |
| 4 | 76 | 4,484 | 1.19e-02–1.02e-01 | 0.0472 | 104 | 0.0232 |
| 5 | 77 | 4,543 | 1.03e-01–4.61e-01 | 0.2449 | 1026 | 0.2258 |
| 6 | 76 | 4,484 | 4.61e-01–8.29e-01 | 0.6414 | 3313 | 0.7388 |
| 7 | 76 | 4,484 | 8.54e-01–9.89e-01 | 0.9478 | 4080 | 0.9099 |
| 8 | 76 | 4,484 | 9.89e-01–9.99e-01 | 0.9964 | 4451 | 0.9926 |
| 9 | 76 | 4,484 | 9.99e-01–1.00e+00 | 0.9999 | 4451 | 0.9926 |

**Isotonic on x**

| bin | n materials–τ | n trials | predicted range | mean predicted | exceedances | observed |
|---|---|---|---|---|---|---|
| 0 | 77 | 4,543 | 0.00e+00–0.00e+00 | 0.0000 | 1 | 0.0002 |
| 1 | 76 | 4,484 | 0.00e+00–0.00e+00 | 0.0000 | 0 | 0.0000 |
| 2 | 76 | 4,484 | 0.00e+00–0.00e+00 | 0.0000 | 0 | 0.0000 |
| 3 | 76 | 4,484 | 0.00e+00–5.84e-04 | 0.0002 | 7 | 0.0016 |
| 4 | 76 | 4,484 | 5.84e-04–4.89e-02 | 0.0195 | 103 | 0.0230 |
| 5 | 77 | 4,543 | 4.94e-02–6.20e-01 | 0.2308 | 1169 | 0.2573 |
| 6 | 76 | 4,484 | 6.20e-01–7.87e-01 | 0.7380 | 3223 | 0.7188 |
| 7 | 76 | 4,484 | 7.87e-01–9.82e-01 | 0.9138 | 4054 | 0.9041 |
| 8 | 76 | 4,484 | 9.82e-01–9.94e-01 | 0.9894 | 4431 | 0.9882 |
| 9 | 76 | 4,484 | 9.96e-01–1.00e+00 | 0.9972 | 4445 | 0.9913 |

**Logistic on x + secondary (+ log10 τ)**

| bin | n materials–τ | n trials | predicted range | mean predicted | exceedances | observed |
|---|---|---|---|---|---|---|
| 0 | 77 | 4,543 | 1.58e-18–4.40e-07 | 0.0000 | 0 | 0.0000 |
| 1 | 76 | 4,484 | 5.15e-07–3.94e-05 | 0.0000 | 0 | 0.0000 |
| 2 | 76 | 4,484 | 4.31e-05–4.44e-04 | 0.0002 | 0 | 0.0000 |
| 3 | 76 | 4,484 | 4.75e-04–4.98e-03 | 0.0020 | 39 | 0.0087 |
| 4 | 76 | 4,484 | 5.13e-03–8.04e-02 | 0.0319 | 144 | 0.0321 |
| 5 | 77 | 4,543 | 8.05e-02–3.98e-01 | 0.2141 | 790 | 0.1739 |
| 6 | 76 | 4,484 | 4.03e-01–8.48e-01 | 0.6719 | 3273 | 0.7299 |
| 7 | 76 | 4,484 | 8.51e-01–9.96e-01 | 0.9609 | 4264 | 0.9509 |
| 8 | 76 | 4,484 | 9.96e-01–1.00e+00 | 0.9988 | 4449 | 0.9922 |
| 9 | 76 | 4,484 | 1.00e+00–1.00e+00 | 1.0000 | 4474 | 0.9978 |

Per-τ reliability tables are in `reliability.csv` (subsets `tau_0.0001`, `tau_0.001`, `tau_0.01`).

## Contract table (cross-validated isotonic risk; admission is held-out)

x_cutoff = largest x at which the isotonic risk fitted on all 254 materials is ≤ p*; admission uses the fold-wise cutoffs from the training folds only (range given). Coverage = admitted / 254; observed = held-out exceedances / trials among the admitted.

| p* | τ (e) | x_cutoff (all) | fold cutoffs min…max | admitted / 254 | coverage [95% CI] | exceedances / trials | observed rate [95% CI] |
|---|---|---|---|---|---|---|---|
| 0.5% | 0.0001 | -0.509 | -0.509…-0.256 | 15 | 5.9% [3.1%, 9.1%] | 15 / 885 | 1.695% [0.000%, 4.237%] |
| 0.5% | 0.001 | -0.509 | -0.509…-0.256 | 96 | 37.8% [31.9%, 44.1%] | 1 / 5,664 | 0.018% [0.000%, 0.057%] |
| 0.5% | 0.01 | -0.509 | -0.509…-0.256 | 199 | 78.3% [73.2%, 83.1%] | 0 / 11,741 | 0.000% [0.000%, 0.000%] |
| 1% | 0.0001 | -0.256 | -0.263…-0.240 | 25 | 9.8% [6.3%, 13.8%] | 16 / 1,475 | 1.085% [0.000%, 2.677%] |
| 1% | 0.001 | -0.256 | -0.263…-0.240 | 115 | 45.3% [39.0%, 51.6%] | 16 / 6,785 | 0.236% [0.000%, 0.657%] |
| 1% | 0.01 | -0.256 | -0.263…-0.240 | 210 | 82.7% [77.6%, 87.0%] | 0 / 12,390 | 0.000% [0.000%, 0.000%] |
| 2% | 0.0001 | -0.256 | -0.263…-0.222 | 25 | 9.8% [6.3%, 13.8%] | 16 / 1,475 | 1.085% [0.000%, 2.677%] |
| 2% | 0.001 | -0.256 | -0.263…-0.222 | 115 | 45.3% [39.0%, 51.6%] | 16 / 6,785 | 0.236% [0.000%, 0.657%] |
| 2% | 0.01 | -0.256 | -0.263…-0.222 | 211 | 83.1% [78.0%, 87.4%] | 0 / 12,449 | 0.000% [0.000%, 0.000%] |
| 5% | 0.0001 | -0.142 | -0.144…-0.127 | 38 | 15.0% [11.0%, 19.7%] | 71 / 2,242 | 3.167% [0.695%, 6.831%] |
| 5% | 0.001 | -0.142 | -0.144…-0.127 | 127 | 50.0% [43.7%, 55.9%] | 42 / 7,493 | 0.561% [0.114%, 1.147%] |
| 5% | 0.01 | -0.142 | -0.144…-0.127 | 219 | 86.2% [81.9%, 90.2%] | 0 / 12,921 | 0.000% [0.000%, 0.000%] |
| 10% | 0.0001 | -0.058 | -0.060…0.017 | 45 | 17.7% [13.4%, 22.8%] | 106 / 2,655 | 3.992% [1.427%, 7.333%] |
| 10% | 0.001 | -0.058 | -0.060…0.017 | 138 | 54.3% [48.0%, 60.2%] | 143 / 8,142 | 1.756% [0.770%, 2.963%] |
| 10% | 0.01 | -0.058 | -0.060…0.017 | 228 | 89.8% [85.8%, 93.3%] | 9 / 13,452 | 0.067% [0.000%, 0.206%] |

Binary gate (x < 0) at each τ, for comparison:

| τ (e) | admitted / 254 | coverage [95% CI] | exceedances / trials | realized risk [95% CI] |
|---|---|---|---|---|
| 0.0001 | 46 | 18.1% [13.8%, 23.2%] | 109 / 2,714 | 4.016% [1.445%, 7.280%] |
| 0.001 | 143 | 56.3% [50.0%, 62.2%] | 135 / 8,437 | 1.600% [0.761%, 2.603%] |
| 0.01 | 229 | 90.2% [86.2%, 93.7%] | 20 / 13,511 | 0.148% [0.000%, 0.371%] |

At the gate's own realized risk (p* = 1.6%, comparison row, not pre-declared) the isotonic contract at τ = 1e-3 e admits 115/254 = 45.3% with 16/6,785 = 0.236% observed, against the gate's 143/254 = 56.3% with 135/8,437 = 1.600%. A 5% contract reaches 127/254 and a 10% contract 138/254; none of the five pre-declared levels reaches the gate's coverage at τ = 1e-3 e.

## Logistic coefficients (all 254 materials, cluster-robust SE by material)

| Model | Term | Coef | SE | z | p |
|---|---|---|---|---|---|
| logistic_x | const | -0.439 | 0.445 | -0.99 | 3.24e-01 |
| logistic_x | x | 6.362 | 0.419 | 15.17 | 5.71e-52 |
| logistic_x | log10_tau | 0.274 | 0.142 | 1.92 | 5.43e-02 |
| logistic_x_secondary | const | -0.555 | 0.383 | -1.45 | 1.47e-01 |
| logistic_x_secondary | x | -2.529 | 2.915 | -0.87 | 3.86e-01 |
| logistic_x_secondary | log10_tau | -9.725 | 3.015 | -3.23 | 1.26e-03 |
| logistic_x_secondary | log10_seed_median | -1.830 | 1.554 | -1.18 | 2.39e-01 |
| logistic_x_secondary | log10_seed_mean | 11.333 | 4.337 | 2.61 | 8.97e-03 |
| logistic_x_secondary | seed_log10_span | -0.359 | 0.948 | -0.38 | 7.05e-01 |

In the secondary-predictor model x, log10 seed-median and log10 seed-mean are strongly collinear (individual SEs are wide); the held-out Brier, not the coefficients, is the evidence that the seed spread adds information.

## Files

- `material_risk.csv` — 762 rows (material × τ): f_m, x, secondary predictors, fold, 59-trial exceedance count and rate, held-out risk from each model (`risk_cv_*`), full-data fits (`risk_full_*`), fold-wise isotonic cutoffs.
- `cv_metrics.csv` — held-out Brier, log loss, AUC, ECE and differences versus the gate, with bootstrap CIs, pooled and per τ.
- `reliability.csv` — 10-bin reliability tables per model, pooled and per τ.
- `contract_table.csv` — the contract table above (five p* levels, the 1.6% comparison row, and the gate).
- `coefficients.csv`, `cv_folds.csv` — logistic coefficients; fold sizes and per-fold cutoffs.
- `fig_calibration.png` / `.svg` — (a) reliability diagram, (b) risk versus x with the isotonic, logistic and gate curves and the 762 material–τ points.
- `provenance.json` — commit, input SHA-256s, anchors, seeds, fold rule, package versions, pip freeze, verdict, wall time. `DEVIATIONS.md` — operational choices where the protocol is silent (no rule changed).
