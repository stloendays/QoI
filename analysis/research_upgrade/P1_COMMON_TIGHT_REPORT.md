# P1 completed common tight-ladder audit

Execution status: **COMPLETE**

Pre-registered jobs accounted: **1332/1332**; successful rows: **1332**; recorded failures: **0**.

The first P1 pass recorded 24 source-download timeouts, all belonging to two NOMAD materials. Those keys were retried without changing codec, Bader, tolerance, or source-identity semantics. The original timeout table is retained as `validation/qsq_prospective/p1_common_tight/initial_source_timeout_failures.csv`.

The historical 6,343-row benchmark remains unchanged. These are additive prospective measurements used only to remove unequal tight-ladder search opportunity.

| Bader threshold | Numerical pass | No pass observed | QSQ screen-rejected | Screen-rejected among no-pass | 95% material-cluster CI | No-pass risk: eligible | No-pass risk: screen-rejected | Risk ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1e-04 e | 252 | 510 | 624 | 97.1% | 95.0–98.8% | 10.9% | 79.3% | 7.30× |
| 1e-03 e | 527 | 235 | 333 | 94.0% | 90.0–97.4% | 3.3% | 66.4% | 20.34× |
| 1e-02 e | 711 | 51 | 75 | 100.0% | 100.0–100.0% | 0.0% | 68.0% | inf× |

## Interpretation boundary

After equalizing the pre-registered tight settings, this audit estimates the association between the frozen QSQ screen and failure to find a numerically passing reconstruction. It does not establish that a particular codec discrepancy was caused by reference instability, and it does not prospectively validate the five-seed QSQ screen. P2 addresses fresh-perturbation validation.

The primary quantities are no-pass risk in eligible versus screen-rejected groups and their material-cluster uncertainty. The fraction of no-pass outcomes located in the screen-rejected group must always be reported together with screen-rejection prevalence.
