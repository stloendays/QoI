# P2 prospective fresh-perturbation validation

Execution status: **COMPLETE**

Pre-registered outcomes accounted: **14986/14,986**; successful: **14986**; unresolved/failed: **0**.

The original five-seed QSQ gate was held fixed. These 59 streams per development material were pre-registered as held-out iid-uniform perturbations and were not used to modify the legacy gate.

| tau | Gate group | Materials | Acceptance fraction | Fresh trials | Exceedances | Fresh exceedance risk | 95% material-cluster CI | Materials with >=1 exceedance |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1e-04 e | eligible | 46 | 18.1% | 2714 | 109 | 4.016% | 1.548–7.406% | 15 (32.6%) |
| 1e-04 e | screen_rejected | 208 | 18.1% | 12272 | 10669 | 86.938% | 83.475–90.165% | 208 (100.0%) |
| 1e-03 e | eligible | 143 | 56.3% | 8437 | 135 | 1.600% | 0.782–2.596% | 20 (14.0%) |
| 1e-03 e | screen_rejected | 111 | 56.3% | 6549 | 5326 | 81.325% | 75.981–86.257% | 110 (99.1%) |
| 1e-02 e | eligible | 229 | 90.2% | 13511 | 20 | 0.148% | 0.000–0.377% | 2 (0.9%) |
| 1e-02 e | screen_rejected | 25 | 90.2% | 1475 | 1174 | 79.593% | 66.983–90.712% | 24 (96.0%) |

## Frozen-gate discrimination

| tau | Accepted materials | Rejected materials | Risk: eligible | Risk: rejected | Rejected/eligible risk ratio |
|---:|---:|---:|---:|---:|---:|
| 1e-04 e | 46 | 208 | 4.016% | 86.938% | 21.65x |
| 1e-03 e | 143 | 111 | 1.600% | 81.325% | 50.83x |
| 1e-02 e | 229 | 25 | 0.148% | 79.593% | 537.69x |

## Interpretation boundary

The primary endpoint is 1e-3 e. The 1e-4 and 1e-2 e rows are prespecified secondary endpoints and use the same 59 response vectors rather than independent experiments. Trial-level rates are descriptive within repeated perturbations; uncertainty is clustered by material. If any trials are unresolved, conservative rates count them as adverse and are stored in the machine-readable cohort table.

A material with zero exceedances in 59 valid iid draws has a one-sided 95% exact per-cell upper bound of about 4.95% under the declared Bernoulli model. This is not a simultaneous guarantee across 254 materials and does not establish worst-case stability. A failed QSQ screen also does not prove that any observed codec discrepancy was caused by reference instability.

The scientifically relevant test is whether the frozen gate prospectively separates low-risk from high-risk reference responses at useful acceptance coverage. This report therefore emphasizes conditional exceedance risk, acceptance fraction and rejected/eligible risk ratio rather than a large exclusion percentage alone.
