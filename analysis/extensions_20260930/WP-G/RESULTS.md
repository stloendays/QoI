# WP-G — Qualification under all-electron-reference Bader

Henkelman Bader 1.05 on-grid (`-b ongrid -vac 0.001`) on NUS Vanda (DEVIATIONS.md 1–3); 50 of 53 materials succeeded, 3 failure records. Arms: V valence reference, G1 exact AECCAR0+AECCAR2 reference, G2 reference also perturbed/compressed.

## Acceptance (τ = 1e-3 e)

- G2 non-evaluable: 47/50 (94%) → **QSQ is needed under the standard practice**.
- G1 eligible: 50/50, G2 eligible: 3/50 → **an exact all-electron reference removes the instability**.
- With the 3 failed materials counted against each claim (n = 53): G2 non-evaluable 50/53 (94%) → **QSQ is needed under the standard practice**; G1 eligible 50/53, G2 eligible 3/53 → **not met (G1 50/53 eligible, G2 3/53)**.

## Eligibility (paired, n = 50)

| τ (e) | frozen baderkit (valence) | V | G1 | G2 | McNemar V→G1 (gain/loss, p) | V→G2 | G1→G2 |
|---:|---:|---:|---:|---:|---|---|---|
| 0.0001 | 9 | 9 | 50 | 0 | 41/0 p=9.09e-13 | 0/9 p=0.00391 | 0/50 p=1.78e-15 |
| 0.001 | 25 | 25 | 50 | 3 | 25/0 p=5.96e-08 | 1/23 p=2.98e-06 | 0/47 p=1.42e-14 |
| 0.01 | 44 | 45 | 50 | 17 | 5/0 p=0.0625 | 0/28 p=7.45e-09 | 0/33 p=2.33e-10 |

## Floors

| arm | relative to | material-median log10 ratio [95% CI] | fraction increased |
|---|---|---|---:|
| G1 | V | -8.33 [-8.97, -7.59] | 0.00 |
| G1 | frozen baderkit | -8.33 [-8.94, -7.68] | 0.00 |
| G2 | V | 1.39 [1.07, 1.73] | 0.92 |
| G2 | frozen baderkit | 1.38 [1.03, 1.70] | 0.92 |

## Certification

| τ (e) | arm | eligible | median best certified CR | ZFP / SZ3 / SPERR / none best |
|---:|---|---:|---:|---|
| 0.0001 | V | 9 | 9.36 | 0.44 / 0.11 / 0.44 / 0.00 |
| 0.0001 | G1 | 50 | 32.42 | 0.40 / 0.14 / 0.46 / 0.00 |
| 0.0001 | G2 | 0 | nan | 0.00 / 0.00 / 0.00 / 0.00 |
| 0.001 | V | 25 | 15.90 | 0.36 / 0.20 / 0.44 / 0.00 |
| 0.001 | G1 | 50 | 84.40 | 0.18 / 0.36 / 0.46 / 0.00 |
| 0.001 | G2 | 3 | 5.00 | 0.33 / 0.00 / 0.33 / 0.33 |
| 0.01 | V | 45 | 76.47 | 0.09 / 0.51 / 0.40 / 0.00 |
| 0.01 | G1 | 50 | 242.15 | 0.04 / 0.56 / 0.40 / 0.00 |
| 0.01 | G2 | 17 | 11.97 | 0.41 / 0.12 / 0.29 / 0.18 |

## Basin reassignment on the same rungs

| arm | rows | median reassigned fraction | P90 |
|---|---:|---:|---:|
| V | 1242 | 0.00411 | 0.0432 |
| G1 | 1242 | 0 | 0 |
| G2 | 1242 | 0.186 | 0.912 |

Codec rows reproduced within 0.95–1.05 of the frozen realized L∞: 1242 of 1242 evaluated (1242 total).

Files: `reference.csv`, `probes.csv`, `rows.csv`, `summary.csv`, `failures.csv`, `fig_ae_reference.{png,svg,pdf}`, `provenance.json`, `DEVIATIONS.md`, `vanda_results/`.
