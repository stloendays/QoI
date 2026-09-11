# Supplementary Tables S15-S16 — P4 chemical-decision boundary case study

These tables are generated directly from the frozen P4 reference and resolved compressed-decision outputs. The five-pair cohort is a targeted case study, not a prevalence sample.

## Supplementary Table S15 | Outcome-blind chemistry pairs and two-implementation source references

| Pair | Source chemistry | State A → State B | Added atoms | Target | Δq BaderKit (e) | Δq Henkelman (e) | Pair QSQ eligible at 1e-3 e |
|---|---|---|---|---|---:|---:|---:|
| P4-0bee6570d469f6e6 | GaN electrochemical surfaces, with AECCARs | Ga22N22 → Ga22N22H2H2 | H:4 | N | 0.528936 | 0.528936 | True |
| P4-85ad494c25e36fcd | GaN electrochemical surfaces, with AECCARs | Ga15N15H2H1 → Ga15N15H3H3 | H:3 | N | 0.522669 | 0.522669 | True |
| P4-aea19e4e1e460df6 | GaN electrochemical surfaces, with AECCARs | Ga15N15 → Ga15N15H2H1 | H:3 | N | 0.610388 | 0.610388 | True |
| P4-c7fb774cc03c2a96 | RuO2 CO2RR, adsorbate and spectator variations | O31Ru16 → H3C1O31Ru16 | C:1;H:3 | O | 0.421202 | 0.421201 | False |
| P4-d744aa576ee628c3 | RuO2 CO2RR, adsorbate and spectator variations | Ru16C3O33 → Ru16C3O34H1 | H:1;O:1 | Ru | -0.131815 | -0.131814 | False |

Reference acceptance was frozen before charge outcomes: identical non-zero sign in BaderKit and Henkelman on-grid, minimum |Δq| ≥ 0.02 e, and inter-solver |Δq| disagreement ≤ 0.01 e. All five pairs passed.

## Supplementary Table S16 | Frozen direct-selection and optional escalation policies

### Direct decision policies, pooled across codecs

| Policy | Retained / valid | Coverage | Adverse or zero-direction decisions | Error rate | Unique retained pairs |
|---|---:|---:|---:|---:|---:|
| no_qualification | 60 / 60 | 100.0% | 0 | 0.0% | 5 |
| realized_linf_coverage_matched | 36 / 60 | 60.0% | 0 | 0.0% | 5 |
| archived_float32_probe | 60 / 60 | 100.0% | 0 | 0.0% | 5 |
| frozen_qsq | 36 / 60 | 60.0% | 0 | 0.0% | 3 |

### Optional independent-solver escalation

| Policy | Resolved / valid | Needs review | Errors among resolved | Henkelman state calls | Henkelman wall time (s) |
|---|---:|---:|---:|---:|---:|
| qsq_targeted | 60 / 60 | 0 | 0 | 48 | 397.2 |
| escalate_all | 60 / 60 | 0 | 0 | 108 | 733.3 |

Interpretation: no policy improves sign correctness because the unqualified common-tight baseline already has zero adverse decisions. QSQ is more conservative than this coarse sign contract. The lower independent-solver call count for targeted escalation is an audit-cost comparison only.
