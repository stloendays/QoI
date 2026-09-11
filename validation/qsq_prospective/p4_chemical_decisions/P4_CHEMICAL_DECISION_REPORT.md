# P4 chemical-decision utility validation

Reference-valid chemistry pairs: **5**. This is a deliberately small case-study cohort, not a prevalence sample.
Compressed solver evaluations accounted: **216/216**; successful rows: **72**; failed rows: **144**.

## Direct decision policies

| Policy | Retained / valid | Coverage | Adverse decisions | Retained error rate | Pair-bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|
| no_qualification | 40 / 40 | 100.0% | 0 | 0.0% | 0.0-0.0% |
| realized_linf_coverage_matched | 24 / 40 | 60.0% | 0 | 0.0% | 0.0-0.0% |
| archived_float32_probe | 40 / 40 | 100.0% | 0 | 0.0% | 0.0-0.0% |
| frozen_qsq | 24 / 40 | 60.0% | 0 | 0.0% | 0.0-0.0% |

## Selective escalation

| Policy | Resolved / valid | Needs review | Errors among resolved | Henkelman state calls | Henkelman policy wall time |
|---|---:|---:|---:|---:|---:|
| qsq_targeted | 24 / 40 | 16 (40.0%) | 0 (0.0% of resolved) | 32 | 0.0 s |
| escalate_all | 0 / 40 | 40 (100.0%) | 0 (nan% of resolved) | 72 | 0.0 s |

## Interpretation boundary

P4 tests practical decision utility on a small, outcome-blind, provenance-constrained chemistry cohort. It does not estimate population prevalence. Zero-direction compressed outputs are treated conservatively as adverse/unresolved rather than silently dropped. The reference is a two-implementation on-grid consensus, not a grid-converged physical Bader truth. P3B new-DFT convergence was explicitly deferred before P4 execution.
