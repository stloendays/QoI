# Figure map

Updated 2026-09-09. This file is the canonical figure-numbering registry for the manuscript. Figure numbering follows the formal R sources currently used for the paper; legacy scripts may remain in the repository for provenance but do not define the manuscript numbering.

**Working title:** *Scientific Fidelity Is QoI-Dependent: Certifying Lossy Compression of Electronic Densities*

## Narrative spine

A pointwise density-error bound is not a scientific-fidelity bound. The same reconstructed density can preserve a global linear observable, produce a smooth and nearly power-law error in a nonlocal linear observable, and simultaneously exhibit strongly non-monotone error in a topology-dependent local observable. Fidelity is therefore treated as a property of the pair `(reconstruction, downstream QoI operator)`, not of the reconstruction alone.

Bader charge is the deeply validated topology-sensitive case. It requires re-partitioning after reconstruction, exhibits domain-migration error, has a material-specific stability floor, and must be stability-qualified before certification. Protocol A is frozen provenance; Protocol A.1 is the operative qualification protocol. Codec comparisons that support scientific claims use realized rather than nominal distortion.

---

## Canonical manuscript figure registry

| Figure | Canonical role | R source | Formal rendered outputs | Main-text role | Status |
|---|---|---|---|---|---|
| 1 | From density error to QoI-dependent scientific error | schematic / design source | final artwork TBD | conceptual framing | READY FOR DESIGN |
| 2 | QoI hierarchy: electron count -> Hartree -> Bader | `figures/R/figure2_qoi_hierarchy.R` | `figures/R/rendered/figure2_qoi_hierarchy_R.{png,pdf,svg}` | Results: operator-dependent error propagation | FORMAL R SOURCE; lock audit pending |
| 3 | Stability-aware chemical certification landscape | `figures/R/figure3_certification_landscape.R` | `figures/R/rendered/figure3_certification_landscape_R.{png,pdf,svg}` | Results: eligibility + certification decision | DATA-READY |
| 4 | Protocol A -> A.1 stability-floor correction | `figures/R/figure4_stability_protocol.R` | `figures/R/rendered/figure4_stability_protocol_R.{png,pdf,svg}` | Results: intrinsic QoI identifiability | DATA-READY |
| 5 | Topology-induced amplification in re-solved Bader response | `figures/R/figure5_topology_mechanism.R` | `figures/R/rendered/figure5_topology_mechanism_R.{png,pdf,svg}` | Results: Bader-specific mechanism | QA PASSED; final lock pending |
| 6 | Equal nominal tolerance vs matched realized L-infinity | `figures/R/figure6_matched_realized_linf.R` | `figures/R/rendered/figure6_matched_realized_linf_R.{png,pdf,svg}` | Results: fair codec comparison after distortion matching | QA PASSED; final lock pending |
| 7 | External confirmation and practical value | final R source TBD | final artwork TBD | closing validation / practical value | DATA-READY / DESIGN PENDING |

### Non-canonical legacy figure sources

- `figures/R/figure2_fixed_vs_resolved.R`: retained as provenance; superseded as a main-text Figure 2 source by `figure2_qoi_hierarchy.R`.
- `figures/R/figure6_compression_chemistry_tradeoff.R`: retained as provenance; superseded as a main-text Figure 6 source by `figure6_matched_realized_linf.R`.
- The earlier plan that labelled the rate-QoI frontier as Figure 5 is retired. Figure 5 is now the formal topology-mechanism figure. Practical rate-fidelity results remain part of the Results narrative and closing practical-value evidence; they must not overwrite the canonical Figure 5 numbering.

---

## Figure 1 — From density error to QoI-dependent scientific error

Conceptual schematic: original density `rho` -> codec at requested tolerance -> reconstructed density `rho_tilde` -> downstream operators:

1. total electron count `N_e = integral rho` (global linear control),
2. Hartree potential `V_H = nabla^{-2} rho` (linear nonlocal comparator),
3. Bader charge `q_A = integral_{Omega_A[rho]} rho`, with density-dependent topological domains.

The Bader path must show re-partitioning after reconstruction and the decomposition `Delta Q_total = Delta Q_integrand + Delta Q_domain`.

**Primary message:** density fidelity is not scientific fidelity; the downstream operator is part of the fidelity contract.

*Data:* schematic only. *Status:* READY FOR DESIGN.

---

## Figure 2 — QoI hierarchy reveals operator-dependent error propagation

**Canonical source:** `figures/R/figure2_qoi_hierarchy.R`.

**(a) Electron-number negative control.** Global electron conservation does not certify local Bader fidelity; 1,383 of 3,205 reconstructions with `|Delta N_e| < 1e-4 e` still have re-derived Bader error >= `1e-3 e` (43.15%).

**(b) Hartree error vs realized L-infinity.** Gate-passing rows show a smooth approximately first-order response. Pooled exponent is 1.02; codec-by-stratum slopes are 0.91-1.12 and median material-level `R^2` is 0.994-0.997.

**(c) Bader response on identical reconstructions.** Bader error is less regular, with lower `R^2` and 32.4% material-codec strict monotonicity versus 88.6% for Hartree overall.

**(d) Matched-Hartree-error dispersion.** In 0.5-decade Hartree-error bins, 55.4% of gate-passing rows lie in bins where the Bader `P90/P10` spread is at least 10x. The largest frozen Bader jump is 22,296x (`mp-676693`, ZFP) while the Hartree ladder remains smooth (`R^2 = 0.999`).

**Slab caveat:** do not claim universal Hartree monotonicity. The supported contrast is smooth approximately power-law Hartree response versus substantially more non-monotone Bader response.

*Data:* `analysis/electron_count_qoi/`, `analysis/hartree_potential_expansion/`, and `benchmark/master_benchmark_full.csv`.

---

## Figure 3 — Chemical certification is a stability-aware decision problem

**Canonical source:** `figures/R/figure3_certification_landscape.R`.

The figure reports Protocol A.1-valid certification by codec and chemical tolerance, the identifiability ceiling imposed by the uncompressed Bader stability floor, and the overstatement that results when eligibility is ignored.

**Primary message:** codec success is scientifically interpretable only after the downstream QoI is identifiable at the requested tolerance.

*Data:* `benchmark/master_benchmark_full.csv`, using the frozen Protocol A.1 eligibility/certification fields.

---

## Figure 4 — Protocol A -> A.1 stability floor

**Canonical source:** `figures/R/figure4_stability_protocol.R`.

Protocol A remains archived provenance. Protocol A.1 uses fixed-seed uniform perturbations at the float32 L-infinity amplitude while retaining the frozen tolerance set, exclusion semantics and reporting rules. The figure quantifies the change in measured Bader stability floor and the consequences for evaluability.

**Primary message:** a QoI cannot serve as a fidelity contract at a precision at which that QoI is not itself numerically/topologically identifiable.

*Data:* `stability/stability_floor_A1.csv` and `stability/stability_floor_A_archived_float32.csv`.

---

## Figure 5 — Topology-induced amplification explains irregular Bader response

**Canonical source:** `figures/R/figure5_topology_mechanism.R`.

**(a)** Re-solved Bader error versus the fixed-basin/integrand contribution, with basin reassignment encoded by colour.

**(b)** Signed per-atom decomposition into integrand and domain-migration contributions. Large atomic deviations expose the domain term.

**(c)** Representative full-ladder trajectories comparing fixed-basin and re-solved Bader errors across smooth, intermediate and jump cases.

**(d)** Rung-to-rung Bader jump severity versus basin reassignment over the frozen benchmark. The reported Spearman association is descriptive and is not presented as a causal model.

**Primary message:** for Bader charge, re-solving the density-dependent partition can amplify a smooth field perturbation through topology-driven domain migration. This is a Bader-specific mechanism and must not be generalized to every downstream QoI.

*Data:* `benchmark/master_benchmark_full.csv`, `mechanism/basin_error_decomposition_summary.csv`, `mechanism/basin_error_decomposition_per_atom.csv`.

*QA:* final CI run `34349558487`; artifact `10103144848`; PNG/PDF/SVG visually cross-checked with no clipping or legend/title overlap.

---

## Figure 6 — Equal nominal tolerance conflates distortion magnitude with error geometry

**Canonical source:** `figures/R/figure6_matched_realized_linf.R`.

**(a)** Equal-nominal diagnostic: ZFP realizes about 0.17x the L-infinity perturbation of SZ3/SPERR at the same requested tolerance, while SZ3/SPERR is about 1.00x.

**(b)** Within-material matching on `log10(realized_Linf)`: at the primary 0.10-dex caliper, the dramatic equal-nominal error gap shrinks substantially but does not vanish.

**(c)** Compression-ratio effects on the same matched pairs.

**(d)** Protocol A.1 certification-rate differences on the matched comparisons.

**Primary message:** scalar L-infinity magnitude is insufficient to explain the full codec difference, but equal nominal tolerance is not a valid test of error geometry; realized distortion must be controlled first.

*Data:* `analysis/matched_realized_linf_v1/matched_effects_summary.csv` and `analysis/matched_realized_linf_v1/equal_nominal_diagnostics.csv`.

*QA:* final CI run `34340308601`; artifact `10099481566`; PNG/PDF/SVG visually cross-checked.

---

## Figure 7 — External confirmation and practical value

A compact closing figure should combine:

**(a) External confirmatory cohort.** 63/63 primary systems complete, 1,689 retained rows, zero material-level pipeline failures, zero codec bound violations, and reproduction of the pre-specified directional rate-fidelity expectations.

**(b) Lossless versus stability-qualified lossy compression.** Compare exact/lossless baselines with the best certified lossy compression at each QoI threshold.

*Data:* `validation/final_external_confirmatory63_20260908/`, `paper/EXTERNAL_CONFIRMATORY63_EVIDENCE.md`, lossless baseline outputs and A.1 summary tables. *Status:* DATA-READY / DESIGN PENDING.

---

## Main-text claim hierarchy

1. **General:** reconstruction error alone does not define scientific fidelity; downstream QoI structure matters.
2. **Mechanistic:** on identical reconstructions, Hartree-potential error follows a smooth approximately first-order response to realized L-infinity, whereas Bader error is more non-monotone and can vary by orders of magnitude at comparable smooth-field fidelity.
3. **Bader-specific:** topology-sensitive Bader error is strongly affected by basin migration, so fixed-basin scoring is not the fidelity metric for the actual downstream pipeline.
4. **Qualification:** Bader charge has a material-specific stability floor; contracts below that floor are not evaluable and must not be counted as compression failures or successes.
5. **Comparison:** nominal codec controls are not commensurate; realized distortion must be matched before residual codec differences are interpreted.
6. **Practical:** after Protocol A.1 qualification and realized-distortion control, lossy compression remains scientifically useful over a substantial part of the rate-fidelity frontier.

Do not generalize from these three QoIs to all scientific observables. The manuscript supports a general evaluation principle with one deeply validated topology-sensitive case and two structurally distinct controls/comparators.

---

## Supplementary material

| Panel | Content | Disposition |
|---|---|---|
| S1 | Full electron-count summaries by codec/tolerance | new SI |
| S2 | Full Hartree group tables, per-material fits and slab monotonicity diagnostics | new SI |
| S3 | Hartree reproduction-gate failures: 73 SZ3 byte-count mismatches | new SI / provenance |
| S4 | No-exclusion sensitivity | retain |
| S5 | Floor-relative error and inflated-threshold sensitivity | retain |
| S6 | Probe amplitude and seed sensitivity | retain |
| S7 | Negative result: boundary-aware allocation | retain |
| S8 | Negative result: promolecule prior | retain |
| S9 | Failure taxonomy / registry | retain |
| S10 | External baselines and unit conversions | retain |

The old standalone bulk-versus-slab stability generalization must not return as a headline claim; that generalization was not reproduced externally.
