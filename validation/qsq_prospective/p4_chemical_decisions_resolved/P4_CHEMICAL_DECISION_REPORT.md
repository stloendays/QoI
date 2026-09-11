# P4 resolved engineering-retry note

The primary scientific design is unchanged. The immutable first run produced 72 successful cells and 144 path-engineering failures. A pre-retry taxonomy assigned all 144 failures to missing work-directory creation. The retry executed exactly those failed keys and returned 144/144 successes; final policy analysis therefore uses 216/216 successful solver cells.

# P4 chemical-decision utility validation

Reference-valid chemistry pairs: **5**. This is a deliberately small case-study cohort, not a prevalence sample.
Compressed solver evaluations accounted: **216/216**; successful rows: **216**; failed rows: **0**.

## Direct decision policies

| Policy | Retained / valid | Coverage | Adverse decisions | Retained error rate | Pair-bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|
| no_qualification | 60 / 60 | 100.0% | 0 | 0.0% | 0.0-0.0% |
| realized_linf_coverage_matched | 36 / 60 | 60.0% | 0 | 0.0% | 0.0-0.0% |
| archived_float32_probe | 60 / 60 | 100.0% | 0 | 0.0% | 0.0-0.0% |
| frozen_qsq | 36 / 60 | 60.0% | 0 | 0.0% | 0.0-0.0% |

## Selective escalation

| Policy | Resolved / valid | Needs review | Errors among resolved | Henkelman state calls | Henkelman policy wall time |
|---|---:|---:|---:|---:|---:|
| qsq_targeted | 60 / 60 | 0 (0.0%) | 0 (0.0% of resolved) | 48 | 397.2 s |
| escalate_all | 60 / 60 | 0 (0.0%) | 0 (0.0% of resolved) | 108 | 733.3 s |

## Interpretation boundary

P4 tests practical decision utility on a small, outcome-blind, provenance-constrained chemistry cohort. It does not estimate population prevalence. Zero-direction compressed outputs are treated conservatively as adverse/unresolved rather than silently dropped. The reference is a two-implementation on-grid consensus, not a grid-converged physical Bader truth. P3B new-DFT convergence was explicitly deferred before P4 execution.
