# P1 completed common tight-ladder audit

Execution status: **COMPLETE_WITH_RECORDED_FAILURES**

Pre-registered jobs accounted: **1332/1332**; successful rows: **1308**; recorded failures: **24**.

The historical 6,343-row benchmark remains unchanged. These are additive prospective measurements used only to remove unequal tight-ladder search opportunity.

| Bader threshold | Numerical pass | No pass observed | QSQ screen-rejected | Screen-rejected among no-pass | 95% material-cluster CI | No-pass risk: eligible | No-pass risk: screen-rejected | Risk ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1e-04 e | 250 | 512 | 624 | 97.1% | 95.0–98.8% | 10.9% | 79.6% | 7.33× |
| 1e-03 e | 523 | 239 | 333 | 94.1% | 90.1–97.4% | 3.3% | 67.6% | 20.70× |
| 1e-02 e | 708 | 54 | 75 | 94.4% | 84.4–100.0% | 0.4% | 68.0% | 155.72× |

## Interpretation boundary

This audit answers a narrower and cleaner question than the historical full-record Figure 3: after giving every development material the same pre-registered tight settings for all three codecs, how strongly is failure to find a numerically passing reconstruction associated with the frozen QSQ screen? It does not show that a codec discrepancy was caused by reference instability, and it does not validate the five-seed QSQ screen against fresh perturbations. P2 addresses the latter.

The primary quantities to carry forward are the completed-common-ladder no-pass risks in eligible versus screen-rejected groups, their material-cluster uncertainty, and the risk ratio. The fraction of no-pass outcomes that happen to lie in the screen-rejected group must always be reported together with screen-rejection prevalence.
