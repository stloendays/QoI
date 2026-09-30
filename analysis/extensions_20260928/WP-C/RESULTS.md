# WP-C — Codec-shaped perturbation family for QSQ

Reader-facing name: QSQ. All numbers below are read from the CSV files in this directory; none is transcribed by hand.

## Population actually run

- Materials: 254 development materials (186 bulk, 68 slab).
- Codecs: ZFP, SZ3, SPERR. Probes per material x codec: k in {0, 1, 2, 3, 4, 5} (k = 0 unshifted; k >= 1 periodic shifts).
- Plan executed: **full pre-declared plan** — 4572 Bader re-solves planned, 4572 completed, 0 failed (4572 accounted); 762 codec round trips.
- Failures by stage: none. Failed rows stay in every denominator (a material x codec with any failed k >= 1 solve has an undefined codec-shaped floor and is counted as `n_undefined_ratio`).
- Base rung used: all 762 material x codec pairs at nominal relative tolerance 1e-5; per-codec row counts: SPERR @ 1e-05: 1524; SZ3 @ 1e-05: 1524; ZFP @ 1e-05: 1524.
- Residual reproduction: |log10(reproduced L_inf / frozen realized_Linf)| max = 2.406e-07 dex over 762 pairs.
- Probe amplitude: |L_inf(delta) - eps_m| / eps_m max = 1.194e-16 (requirement <= 1e-12) over 4572 probes.
- Wall time of the run: 0.68 h (2454 s); summed Bader solve time 8449 s; summed codec round-trip time 541 s.

## Analysis 1 — Codec-shaped floor f^c_m versus iid floor f_m

f^c_m = max over k >= 1 of the Bader response; f_m = frozen `stability_floor_A1_e`. Statistic: log10(f^c_m / f_m), material-median with material-cluster bootstrap 95% CI (2,000 resamples, seed 20260928).

| Codec | Stratum | n (defined / total) | median log10(f^c/f) [95% CI] | mean | p05 / p25 / p75 / p95 | frac f^c > f [95% CI] |
|---|---|---:|---:|---:|---:|---:|
| ZFP | all | 254 / 254 | -0.196 [-0.255, -0.134] | -0.319 | -1.019 / -0.476 / -0.016 / +0.101 | 0.189 [0.142, 0.236] (48/254) |
| ZFP | bulk | 186 / 186 | -0.120 [-0.195, -0.061] | -0.291 | -1.043 / -0.416 / -0.001 / +0.116 | 0.226 [0.167, 0.285] (42/186) |
| ZFP | slab | 68 / 68 | -0.306 [-0.452, -0.239] | -0.393 | -1.011 / -0.686 / -0.122 / +0.041 | 0.088 [0.029, 0.162] (6/68) |
| SZ3 | all | 254 / 254 | -0.000 [-0.010, +0.008] | -0.007 | -0.351 / -0.083 / +0.057 / +0.322 | 0.496 [0.433, 0.555] (126/254) |
| SZ3 | bulk | 186 / 186 | +0.000 [-0.010, +0.014] | -0.005 | -0.362 / -0.076 / +0.056 / +0.303 | 0.500 [0.425, 0.575] (93/186) |
| SZ3 | slab | 68 / 68 | -0.001 [-0.045, +0.017] | -0.013 | -0.335 / -0.086 / +0.069 / +0.304 | 0.485 [0.368, 0.603] (33/68) |
| SPERR | all | 254 / 254 | -0.027 [-0.042, -0.010] | -0.056 | -0.442 / -0.130 / +0.034 / +0.233 | 0.398 [0.338, 0.457] (101/254) |
| SPERR | bulk | 186 / 186 | -0.032 [-0.045, -0.009] | -0.060 | -0.507 / -0.148 / +0.034 / +0.242 | 0.398 [0.328, 0.468] (74/186) |
| SPERR | slab | 68 / 68 | -0.018 [-0.054, +0.002] | -0.046 | -0.428 / -0.111 / +0.035 / +0.204 | 0.397 [0.294, 0.515] (27/68) |

### Acceptance verdict (pre-declared rule, applied per codec)

- **ZFP: CONSERVATIVE** — median log10(f^c/f) = -0.196, 95% CI [-0.255, -0.134], n = 254/254 materials.
- **SZ3: NOT DISTINGUISHABLE FROM 0 (neither conservative nor anti-conservative by the pre-declared rule)** — median log10(f^c/f) = -0.000, 95% CI [-0.010, +0.008], n = 254/254 materials.
- **SPERR: CONSERVATIVE** — median log10(f^c/f) = -0.027, 95% CI [-0.042, -0.010], n = 254/254 materials.

Rule: iid family is *conservative* for codec c if the material-median log10(f^c/f) < 0 with the bootstrap 95% CI excluding 0; *anti-conservative* if > 0 with CI excluding 0.

## Analysis 2 — Eligibility agreement (iid vs codec-shaped floor)

Eligibility at tau: floor < tau (same rule as the frozen gate). Flip counts are reported in full; the flip list with material IDs and direction is in `eligibility_flips.csv`.

| Codec | tau (e) | n | iid eligible | codec-shaped eligible | both eligible | both rejected | flips iid-eligible -> codec-rejected | flips iid-rejected -> codec-eligible | agreement | Cohen's kappa [95% CI] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ZFP | 0.0001 | 254 | 46 | 88 | 44 | 164 | 2 | 44 | 0.819 | 0.550 [0.447, 0.655] |
| ZFP | 0.001 | 254 | 143 | 166 | 142 | 87 | 1 | 24 | 0.902 | 0.795 [0.718, 0.864] |
| ZFP | 0.01 | 254 | 229 | 235 | 229 | 19 | 0 | 6 | 0.976 | 0.851 [0.710, 0.954] |
| SZ3 | 0.0001 | 254 | 46 | 56 | 42 | 194 | 4 | 14 | 0.929 | 0.780 [0.677, 0.870] |
| SZ3 | 0.001 | 254 | 143 | 143 | 135 | 103 | 8 | 8 | 0.937 | 0.872 [0.809, 0.928] |
| SZ3 | 0.01 | 254 | 229 | 227 | 226 | 24 | 3 | 1 | 0.984 | 0.914 [0.811, 0.981] |
| SPERR | 0.0001 | 254 | 46 | 57 | 41 | 192 | 5 | 16 | 0.917 | 0.745 [0.637, 0.846] |
| SPERR | 0.001 | 254 | 143 | 143 | 135 | 103 | 8 | 8 | 0.937 | 0.872 [0.810, 0.928] |
| SPERR | 0.01 | 254 | 229 | 229 | 227 | 23 | 2 | 2 | 0.984 | 0.911 [0.811, 0.980] |

## Analysis 3 — Alignment effect: log10(response at k = 0 / median response over k >= 1)

| Codec | Stratum | n defined | median [95% CI] | frac k0 > shifted median | p05 / p95 |
|---|---|---:|---:|---:|---:|
| ZFP | all | 254 / 254 | -0.000 [-0.035, +0.026] | 0.500 | -2.531 / +0.863 |
| ZFP | bulk | 186 / 186 | -0.052 [-0.086, -0.021] | 0.392 | -2.817 / +0.798 |
| ZFP | slab | 68 / 68 | +0.220 [+0.118, +0.302] | 0.794 | -0.451 / +0.854 |
| SZ3 | all | 254 / 254 | +0.019 [+0.001, +0.039] | 0.571 | -0.769 / +0.651 |
| SZ3 | bulk | 186 / 186 | +0.010 [-0.027, +0.028] | 0.538 | -0.914 / +0.516 |
| SZ3 | slab | 68 / 68 | +0.088 [+0.011, +0.168] | 0.662 | -0.435 / +0.882 |
| SPERR | all | 254 / 254 | -0.014 [-0.037, +0.002] | 0.457 | -0.851 / +0.465 |
| SPERR | bulk | 186 / 186 | -0.013 [-0.042, +0.003] | 0.457 | -1.000 / +0.472 |
| SPERR | slab | 68 / 68 | -0.017 [-0.065, +0.025] | 0.456 | -0.398 / +0.386 |

## Analysis 4 — Link to the Fourier mechanism

Spearman rho between log10(f^c_m / f_m) and the low-G error-energy fraction of the codec residual r (Nyquist-safe radial spectrum, `analysis/hartree_spectral_mechanism` convention: q = |G|/|G|_max over safe modes, low-G = q <= 0.25). Material-cluster bootstrap CI.

| Codec | n | Spearman rho [95% CI] | median low-G fraction of r |
|---|---:|---:|---:|
| ZFP | 254 | +0.002 [-0.125, +0.126] | 0.1252 |
| SZ3 | 254 | -0.166 [-0.284, -0.043] | 0.2279 |
| SPERR | 254 | -0.104 [-0.227, +0.022] | 0.0821 |

## Analysis 5 — Predictive value among materials admitted at 1e-3 e

Population: materials with iid floor f_m < 1e-3 e. Outcome: P2 fresh exceedance rate p_m = fraction of the 59 fresh iid trials with `bader_response_max_e` >= 1e-3 e. Spearman rho of log10 f_m and of log10 f^c_m with p_m; the difference rho(f^c) - rho(f) uses the same material resamples.

| Codec | n admitted | n with any fresh exceedance | rho(f_iid, p) [95% CI] | rho(f^c, p) [95% CI] | rho(f^c) - rho(f) [95% CI] |
|---|---:|---:|---:|---:|---:|
| ZFP | 143 | 20 | +0.549 [+0.433, +0.640] | +0.420 [+0.288, +0.534] | -0.128 [-0.218, -0.050] |
| SZ3 | 143 | 20 | +0.549 [+0.433, +0.640] | +0.544 [+0.417, +0.644] | -0.005 [-0.044, +0.030] |
| SPERR | 143 | 20 | +0.549 [+0.433, +0.640] | +0.559 [+0.434, +0.657] | +0.011 [-0.023, +0.045] |

## Files

- `probe_outcomes.csv` — one row per material x codec x k (measured L_inf, response, reassigned voxels, label hashes, charges).
- `floors.csv` — per material x codec: f_m, f^c_m, per-k responses, eligibility at each tau, alignment ratio, residual spectral summary, P2 rate.
- `floor_ratio_summary.csv` (analysis 1), `agreement.csv` + `eligibility_flips.csv` (analysis 2), `alignment.csv` (analysis 3), `spectral_link.csv` (analysis 4), `predictive.csv` (analysis 5).
- `spectra.csv` — Nyquist-safe spectral metrics and 32-bin radial error-energy profile of every codec residual.
- `failures.csv` — every planned row that did not complete; `run_manifest.json`, `provenance.json`, `DEVIATIONS.md`.

