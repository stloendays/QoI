# Supplementary Table S14 | Failure taxonomy, exclusions and negative-result audit

Generated 2026-09-11 from the canonical `failure_registry.csv` and the retracted/closed-track records in `paper/CLAIM_EVIDENCE_MATRIX.md`. This table preserves the distinction between scientific non-evaluability, downstream solver failure, infrastructure mismatch and superseded exploratory claims.

## S14a. Failure and exclusion semantics used in the submission

| State / category | Meaning | Scored as codec pass/fail? | Canonical source |
|---|---|---|---|
| `NON_EVALUABLE_BADER_UNSTABLE` | Reference Bader QoI fails **QSQ eligibility** at the requested tolerance | **No** — neither pass nor fail | `stability/eligibility_summary_A1.csv`; Figure 3/S4 |
| `bader_solver_failure` | Downstream Bader analysis did not return a valid row-level result | **No automatic codec attribution**; retained in audit | `failure_registry.csv` |
| `reproduction_mismatch` | Reproduction/platform check failed despite reconstructed scientific field remaining consistent | **No**; infrastructure exclusion from the affected formal analysis | Hartree reproduction-gate records |
| `basin_relabelling_symmetry_equivalent` | Apparent large atom-indexed charge change is a permutation among symmetry-equivalent basins | **Non-evaluable for position-indexed charge**, separately flagged | `failure_registry.csv` |
| eligible + not certified | Reference QoI is numerically eligible but compressed reconstruction exceeds the requested Bader contract | **Yes: genuine failure** | `benchmark/master_benchmark_full.csv` |
| eligible + certified | Reference QoI is eligible and the reconstruction satisfies the contract | **Yes: certified success** | `benchmark/master_benchmark_full.csv` |

## S14b. Explicit `failure_registry.csv` counts

| Registry category | Row records |
|---|---:|
| `bader_solver_failure` | 78 |
| `basin_relabelling_symmetry_equivalent` | 1 |

### Bader-solver failures by corpus and codec

| Corpus | Codec | Row failures |
|---|---|---:|
| dev_bulk | ZFP | 37 |
| dev_slab | SPERR | 4 |
| dev_slab | ZFP | 37 |

These counts describe explicit row-level failure records, not material-level non-evaluable counts. QSQ non-evaluability is stored in the stability/benchmark tables and must not be reconstructed from `failure_registry.csv`. Historical `_A1` source filenames remain unchanged for frozen-schema compatibility.

## S14c. Superseded exploratory statements retained for provenance but prohibited from the submission

| Superseded statement | Why it is not submission-valid |
|---|---|
| "SZ3 leaves 200x more chemical error than ZFP" | Fixed-basin metric; the full-table figure is much smaller |
| "The 6–12x matched-nominal ZFP/SZ3 resolved-Bader gap directly measures codec error geometry" | Equal nominal tolerance gives strongly unequal realized L∞; ZFP realizes ~0.17x the perturbation of SZ3/SPERR. The matched-realized residual is ~1.7–1.8x in the inverse SZ3/ZFP direction and is the appropriate evidence for structure beyond scalar L∞ |
| "SPERR ranks best under fixed basins and worst under re-derived basins" (pilot, claim 3) | 10-material sampling artefact; on 254 materials ZFP is best under both metrics |
| "SPERR is the strongest generic baseline" | Ranking reversed by the metric error |
| Any "compression ratio at equal chemical fidelity" of 130-600x | Inflated 10-20x by the fixed-basin metric |
| "Spatial error allocation is dead (bits/chemistry ratio ~1.0)" | Diagnostic used fixed basins and was blind to the dominant term |
| "Bulk float32 reaches 26x, lossy is pointless there" | Sampling bias: smallest-first ordering selected high-symmetry materials; full corpus gives 4.6x |
| Bias correction "2.08x on slabs" | Fixed-basin metric; gains largely evaporate honestly measured |
| "Bulk crystals have a median Bader stability floor of 6e-9 e" and every archived-float32-probe non-evaluable rate | The float32 probe is order-preserving and understates the floor substantially. The older ~8,700x intermediate summary is superseded for submission wording by the formal five-seed QSQ paired-development median shift of ~1.6×10^4. Archived values remain provenance only; QSQ values replace them for current claims |
| "BQB's 35:1 converts to about 7.8x against float64" | Wrong denominator twice over: BQB's reference is the Gaussian cube (13.167 B/value), not CHGCAR, and the ~36 B/value CHGCAR figure used included header and augmentation block. **The correct conversion is 21.3:1**, i.e. 3.01 bits per grid value. See `results/external_baselines/BASELINE_REPORT.md` |

## S14d. Closed baseline / algorithm tracks

- **External baselines:** BQB and den2bin remain related-work context rather than headline fair benchmarks because their task definitions and/or error-control contracts are not comparable to the frozen density-field L∞ benchmark. The measured denominator audit is retained in `results/external_baselines/BASELINE_REPORT.md`.
- **Algorithm track:** closed under the corrected re-derived-Bader metric. No proposed codec modification survived with sufficient evidence to become a contribution; the paper therefore presents a measurement/certification framework rather than a new compressor.

**Interpretation boundary.** A transparent SI should record failures and discarded exploratory claims, but these categories must not be pooled into a single “failure rate”. In particular, non-evaluable scientific targets are not codec failures, solver failures are not silently imputed as codec failures, and superseded pilot numbers are not reused in the manuscript.

**Machine-readable registry summary:** `supplement/S14_failure_registry_summary.csv`.
