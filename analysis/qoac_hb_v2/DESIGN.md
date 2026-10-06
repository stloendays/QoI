# QOAC-HB v2 — one stream certified for Hartree potential and Bader charge (fresh P2)

Freeze date: 2026-10-07. Frozen before any HB v2 run on any P2 material.

## Joint contract (per tau_B)

- Hartree relative RMSE < 1e-6, historical and Nyquist-safe, on the final stream.
- Actual Henkelman Bader 1.05 (`-b ongrid -vac 0.001`, exact AECCAR0 + AECCAR2 reference): maximum atomic-charge error
  <= tau_B and zero basin reassignment.
- tau_B in {1e-3, 1e-4, 1e-5} e. Primary: 1e-4.

## Arms (`run_joint_v2.py` at `77caf5d`)

Base codecs: **R3** (QOAC v0.3 operational optimum, Hartree metric), **J** (QOAC-H v0.2 frozen ladder), **T1** (spectral
truncation ladder) and **GF** (ZFP/SZ3/SPERR at `abs_tol/ptp = logspace(-9, -1, 25)`).

Post-processors: `none`, `uniform`, `hap:mu` and `ctp-uniform`, `ctp-hap:mu` for mu in {1e-4, 1e-2, 1}, plus the
reference `hartree_only` (no Bader requirement and no side channel).

Bytes include the payload, the side channel whenever a projection is stored, and the CTP flag byte. For each
(material, tau_B, base), the best joint post-processor is the one with the highest certified joint CR. This is an
encoder-side choice that every base receives equally.

## Populations

- Engineering: `analysis/fresh_population_20261006/P2_ENGINEERING_MANIFEST.csv` (12 fresh bulk materials with AECCAR,
  never used before WS-0; also the population of the descriptive B3 real-material study, which does not use the
  joint contract).
- Confirmatory: `P2_CONFIRMATORY_MANIFEST.csv` (48), used only if the engineering gates authorize it.

## Engineering gates

- **E1 feasibility:** R3 at its best joint post-processor is certified at all three tau_B in >= 11/12.
- **E2 joint overhead:** at tau_B = 1e-4, median CR_R3,hartree_only / CR_R3,joint(best post) <= 1.10.
- **E4 utility:** at tau_B = 1e-4, CR_R3,joint(best post) / max over {J, T1, GF} of the joint CR at each base's best
  post-processor > 1 in >= 9/12, and median > 1.10.
- E3 (descriptive): at tau_B = 1e-5, the R3 joint CR with Hartree-aware projection (best of `hap:*`, `ctp-hap:*`)
  divided by the R3 joint CR with uniform projection (best of `uniform`, `ctp-uniform`). Also reported: the fraction
  of materials where CTP projected.

Confirmation is authorized only if E1, E2 and E4 all pass.

## Confirmatory criteria (48 materials; frozen now)

1. >= 46/48 analyzable and certified (E1 definition).
2. Joint overhead at tau_B = 1e-4: median <= 1.10 and fixed-seed (20261007, 10,000 resamples) bootstrap CI upper
   bound <= 1.15.
3. Utility at tau_B = 1e-4: >= 36/48 wins, median > 1.10, and bootstrap CI lower bound > 1.00.

E3 is reported for every tau_B.
