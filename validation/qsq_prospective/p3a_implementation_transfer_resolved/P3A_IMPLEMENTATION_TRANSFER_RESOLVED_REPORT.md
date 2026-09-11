# P3A implementation-transfer resolved analysis

Final 24-system panel summary combines **4 first-run complete materials** from run `34605557997` with the predeclared engineering retry of **20 previously unresolved materials**.

Retry accounting: **360/360**; retry successes: **360**; retry recorded failures: **0**. Final complete material-solver summaries: **72/72**.

Maximum absolute difference between recreated and frozen BaderKit five-seed floors among complete cases: **8.71338e-11 e**.

## Classification transfer

| tau | Independent implementation | Comparable | Ambiguous | Unresolved | Agreement | Cohen kappa | Eligible->rejected | Rejected->eligible |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1e-04 e | henkelman_ongrid | 24 | 0 | 0 | 100.0% | 1.000 | 0 | 0 |
| 1e-04 e | henkelman_neargrid | 23 | 1 | 0 | 82.6% | 0.593 | 1 | 3 |
| 1e-03 e | henkelman_ongrid | 24 | 0 | 0 | 100.0% | 1.000 | 0 | 0 |
| 1e-03 e | henkelman_neargrid | 24 | 0 | 0 | 83.3% | 0.667 | 0 | 4 |
| 1e-02 e | henkelman_ongrid | 24 | 0 | 0 | 100.0% | 1.000 | 0 | 0 |
| 1e-02 e | henkelman_neargrid | 24 | 0 | 0 | 95.8% | 0.882 | 0 | 1 |

## Floor-rank transfer

| Solver | Complete materials | Spearman rho vs frozen BaderKit floor |
|---|---:|---:|
| baderkit_ongrid | 24 | 1.000 |
| henkelman_ongrid | 24 | 0.995 |
| henkelman_neargrid | 24 | 0.754 |

## Provenance and interpretation boundary

The original run `34605557997` is retained unchanged. Its 360 recorded failures were classified before retry as a single pre-solver archive-serialization compatibility-gate failure family. The retry changes no scientific panel, perturbation seeds/amplitudes, solver definition, threshold, or QSQ decision; it only uses the precision of the archived decimal token for provenance compatibility and reliably captures explicit runner exit codes.

This deterministic 24-system panel tests implementation transfer, not population prevalence. P3A still does not establish electronic-structure grid convergence or a unique physical Bader reference; those questions belong to P3B.
