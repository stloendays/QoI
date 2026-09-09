# Claim–evidence addendum — QoI-dependent fidelity

Date: 2026-09-09

This addendum records the new claims enabled by the electron-count negative control and the predeclared full Hartree-potential expansion. It supplements `CLAIM_EVIDENCE_MATRIX.md`; it does not change any frozen benchmark or Protocol A/A.1 definition.

| ID | Claim | Evidence | Status | Claim boundary |
|---|---|---|---|---|
| Q1 | Global electron-number conservation is not sufficient to certify atom-resolved Bader fidelity | Among 3,205 reconstructions with `|Delta N_e| < 1e-4 e`, 1,383 (43.15%) have resolved Bader error >= `1e-3 e`. Full corpus median `|Delta N_e|` ≈ `9.38e-5 e`; median resolved Bader error ≈ `4.00e-3 e` | **CONFIRMED** | Do not claim electron count is always preserved; loose-tolerance tails are non-negligible |
| Q2 | Hartree-potential error follows a smooth, approximately first-order response to realized density perturbation across the tested codecs and strata | Full expansion: 254 materials, 6,343 regenerated rows; 6,270 gate-passed. Hartree slope 0.91–1.12 in all codec × bulk/slab cells, pooled 1.02; per-material `R^2` median 0.994–0.997 | **CONFIRMED** | Do not claim universal strict monotonicity; slab rung-level monotonicity is weaker |
| Q3 | On identical reconstructions, topology-dependent Bader error is less smooth and less determined by realized `L_inf` than Hartree-potential error | Bader `R^2` is lower than Hartree in all six codec × stratum cells; material-level monotonicity 32.4% Bader vs 88.6% Hartree; local elasticity range Bader `-9.3` to `+14.1` vs Hartree `-2.0` to `+4.4`; largest Bader consecutive jump 22,296x while Hartree `R^2=0.999` on the same ladder | **CONFIRMED** | Phrase as different error-propagation structure, not Hartree being “better” |
| Q4 | Similar smooth-field fidelity does not uniquely determine topology-dependent local fidelity | In matched 0.5-decade Hartree-error bins, 55.4% of gate-passed rows lie in bins with Bader `P90/P10 >= 10`; such bins occur for every codec and both bulk/slab strata | **CONFIRMED** | Matching is on Hartree-error magnitude, not all possible field descriptors |
| Q5 | Scientific-fidelity contracts for lossy electronic-density compression must specify the downstream QoI, not only a reconstruction norm | Joint evidence from Q1–Q4 plus Bader stability qualification and matched-realized-`L_inf` analysis | **CONFIRMED as an evaluation principle on the tested observables** | Do not present as a theorem covering all scientific QoIs |

## Promotion decision

The Hartree full-expansion summarizer was frozen before the full run and returned `PROMOTE_TO_MAIN_TEXT`; all five predeclared promotion criteria passed without manual override. The main-text narrative should therefore include the QoI hierarchy rather than treating Hartree as an SI-only robustness test.

## Reproduction caveat

All 6,343 frozen rows were regenerated. ZFP and SPERR passed the complete reconstruction gate. SZ3 passed 96.2%; 73 excluded rows have realized `L_inf` matching the frozen value to better than `2e-5` relative but different compressed byte counts, concentrated in rows originally generated on a different Linux environment. These are recorded as infrastructure-level `reproduction_mismatch`, not codec or numerical failures.

## Slab caveat

Strict Hartree monotonicity is 47–84% on slabs depending on codec, lower than the 97–99% bulk values. However slab per-material Hartree `R^2` medians remain 0.965–0.983 and the downward fluctuations are small compared with Bader. Any manuscript statement about slabs must use smoothness/fit quality and jump amplitude rather than claiming universal monotonicity.
