# P3B provenance-recovery audit

Panel accounting: **24/24 systems**. Automated candidate-complete: **12/24**. Human scientific review is still required before any DFT recomputation work order is frozen.

NOMAD systems: **12**; Materials Project systems: **12**.

| Material | Type | Source | Candidate categories | Auto status |
|---|---|---|---:|---|
| mp-753334 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-631399 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-1223939 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-1025517 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-1044003 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-1039028 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-759554 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-28105 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-1114492 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-1187022 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-606377 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| mp-756647 | bulk | Materials Project | 2/10 | INCOMPLETE_PROVENANCE |
| nomad-FPTBoTAPMQA8 | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad-FVlJ8rpkyGT5 | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad-ZvTQv6REajO4 | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad-0xMhYZKiiVKL | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad-6x45-ylTvOvZ | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad-064_5lUOyDQI | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad--33WrhYeNt5f | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad-1DBJPWgjPfWO | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad---3hBedCnC_e | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad-8tU1rEspJ26T | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad-BiuRBghVF7ns | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |
| nomad--5wLHf6mG5_K | slab | NOMAD surfaces/adsorbates | 10/10 | AUTO_CANDIDATE_COMPLETE |

## Interpretation boundary

`AUTO_CANDIDATE_COMPLETE` means only that the automated audit found evidence candidates for every required provenance category. It is not permission to run P3B until those candidates are reviewed for exactness and internal consistency. Missing provenance is reported honestly; no generic VASP defaults are substituted.
