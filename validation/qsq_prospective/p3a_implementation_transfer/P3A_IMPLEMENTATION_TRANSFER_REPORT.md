# P3A implementation-transfer validation

Accounted solver evaluations: **432/432**; successful rows: **72**; failed rows: **360**.

Maximum absolute difference between recreated and frozen BaderKit five-seed floors among complete cases: **1.54445e-11 e**.

## Classification transfer

| tau | Independent implementation | Comparable | Ambiguous | Unresolved | Agreement | Cohen kappa | Eligible->rejected | Rejected->eligible |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1e-04 e | henkelman_ongrid | 4 | 0 | 20 | 100.0% | 1.000 | 0 | 0 |
| 1e-04 e | henkelman_neargrid | 4 | 0 | 20 | 50.0% | -0.333 | 1 | 1 |
| 1e-03 e | henkelman_ongrid | 4 | 0 | 20 | 100.0% | 1.000 | 0 | 0 |
| 1e-03 e | henkelman_neargrid | 4 | 0 | 20 | 75.0% | 0.500 | 0 | 1 |
| 1e-02 e | henkelman_ongrid | 4 | 0 | 20 | 100.0% | 1.000 | 0 | 0 |
| 1e-02 e | henkelman_neargrid | 4 | 0 | 20 | 75.0% | 0.000 | 0 | 1 |

## Floor-rank transfer

| Solver | Complete materials | Spearman rho vs frozen BaderKit floor |
|---|---:|---:|
| baderkit_ongrid | 4 | 1.000 |
| henkelman_ongrid | 4 | 1.000 |
| henkelman_neargrid | 4 | 0.400 |

## Interpretation boundary

This 24-system panel is deterministically stratified for numerical robustness, not sampled for population prevalence. Agreement supports transfer of the low-risk/high-risk stratification across the tested analysis implementations; disagreement, especially when accompanied by large unperturbed charge differences, defines an implementation-sensitive boundary. P3A does not establish electronic-structure grid convergence or a unique physical Bader reference.
