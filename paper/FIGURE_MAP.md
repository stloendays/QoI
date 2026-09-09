# Figure map

Updated 2026-09-09. This is the canonical figure-numbering and provenance registry for the submission manuscript.

**Working title:** *Scientific Fidelity Is QoI-Dependent: Certifying Lossy Compression of Electronic Densities*

## Narrative spine

A pointwise density-error bound is not a scientific-fidelity bound. The same reconstructed density can preserve a global linear observable, propagate smoothly through a nonlocal linear operator, and exhibit strongly irregular error in a topology-dependent local observable. Scientific fidelity is therefore treated as a property of the pair `(reconstruction, downstream QoI operator)`.

Bader charge is the deeply validated topology-sensitive case. Its basins are re-derived after reconstruction, its error contains a domain-migration component, and its use as a compression contract is conditional on a material-specific Protocol A.1 stability floor. Codec comparisons supporting scientific claims use realized rather than nominal distortion.

---

## Canonical manuscript figure registry

| Figure | Canonical role | R source | Formal rendered outputs | Main-text role | Status |
|---|---|---|---|---|---|
| 1 | From density error to QoI-dependent scientific error | `figures/R/figure1_qoi_contract.R` | `figures/R/rendered/figure1_qoi_contract_R.{png,pdf,svg}` | conceptual framing / operator hierarchy | **LOCKED** |
| 2 | QoI hierarchy: electron count -> Hartree -> Bader | `figures/R/figure2_qoi_hierarchy.R` | `figures/R/rendered/figure2_qoi_hierarchy_R.{png,pdf,svg}` | operator-dependent error propagation | **LOCKED** |
| 3 | Stability-aware chemical certification landscape | `figures/R/figure3_certification_landscape.R` | `figures/R/rendered/figure3_certification_landscape_R.{png,pdf,svg}` | eligibility + certification decision | **LOCKED** |
| 4 | Protocol A -> A.1 stability-floor correction | `figures/R/figure4_stability_protocol.R` | `figures/R/rendered/figure4_stability_protocol_R.{png,pdf,svg}` | intrinsic QoI identifiability | **LOCKED** |
| 5 | Topology-induced amplification in re-solved Bader response | `figures/R/figure5_topology_mechanism.R` | `figures/R/rendered/figure5_topology_mechanism_R.{png,pdf,svg}` | Bader-specific mechanism | **LOCKED** |
| 6 | Equal nominal tolerance vs matched realized L-infinity | `figures/R/figure6_matched_realized_linf.R` | `figures/R/rendered/figure6_matched_realized_linf_R.{png,pdf,svg}` | fair codec comparison after distortion matching | **LOCKED** |
| 7 | Untouched external confirmation of the decision frontier | `figures/R/figure7_external_confirmation.R` | `figures/R/rendered/figure7_external_confirmation_R.{png,pdf,svg}` | closing validation / practical value | **LOCKED** |

## Locked figure provenance

- **Figure 1:** final CI run `34371089020`; artifact `10111997887`. Exact vector schematic generated in R; PNG/PDF/SVG cross-checked after spacing and Bader-decomposition correction.
- **Figure 2:** final CI run `34352844171`; artifact `10104481700`. PNG/PDF/SVG generated from the formal QoI-hierarchy source and visually QA'd after readability/statistic correction.
- **Figure 3:** final CI run `34369822427`; artifact `10111464747`. Three-format output validated after two-row layout and codec-independent eligibility correction.
- **Figure 4:** final CI run `34370291570`; artifact `10111673650`. Three-format output validated after separating the paired 254-development comparison from the 319-system A.1 eligibility cohort.
- **Figure 5:** final CI run `34349558487`; artifact `10103144848`. PNG/PDF/SVG visually cross-checked with no clipping, legend collision, or invalid log-axis labels.
- **Figure 6:** final CI run `34340308601`; artifact `10099481566`. PNG/PDF/SVG visually cross-checked after the realized-L-infinity matching analysis was frozen.
- **Figure 7:** final CI run `34369886843`; artifact `10111557054`. External-confirmatory four-panel render validated with frozen bootstrap summaries and audit counts.

All formal figure workflows validate non-empty PNG/PDF/SVG outputs and commit the formal renderings to `main`. Figure 1, 3, 4 and 7 use the shared serialized writeback group `qoi-formal-figure-writeback` to prevent generated-binary push races.

---

## Figure 1 — Scientific fidelity is defined by the downstream QoI operator

**Canonical source:** `figures/R/figure1_qoi_contract.R`.

The conceptual flow is `rho -> error-bounded codec -> rho_tilde = rho + Delta rho -> downstream QoI`. Three operator lanes are shown:

1. total electron number: global linear control,
2. Hartree potential: linear nonlocal comparator,
3. Bader charge: topology-dependent partition followed by integration.

The Bader lane explicitly re-partitions after reconstruction and shows the conceptual decomposition `Delta Q_total = Delta Q_integrand + Delta Q_domain`.

**Primary message:** the codec constrains the reconstructed field, but scientific fidelity is determined only after the downstream operator is applied.

---

## Figure 2 — QoI hierarchy reveals operator-dependent error propagation

**Canonical source:** `figures/R/figure2_qoi_hierarchy.R`.

- Electron-number conservation is an insufficient certificate of local Bader fidelity: 1,383 of 3,205 reconstructions satisfying `|Delta N_e| < 1e-4 e` still have re-derived Bader error `>= 1e-3 e` (43.15%).
- Gate-passing Hartree rows show a smooth approximately first-order response to realized L-infinity; the pooled exponent is 1.02 and median material-level `R^2` is 0.994-0.997 across codecs.
- Bader response is substantially less regular on the same reconstructions; strict material-codec monotonicity is 32.4% versus 88.6% for Hartree overall.
- At comparable Hartree fidelity, Bader error can still span orders of magnitude: 55.4% of gate-passing rows lie in 0.5-decade Hartree bins whose Bader `P90/P10` spread is at least 10x.

**Caveat:** do not claim universal Hartree monotonicity; slab ladders contain small local reversals.

---

## Figure 3 — Chemical certification is a stability-aware decision problem

**Canonical source:** `figures/R/figure3_certification_landscape.R`.

The figure separates Protocol A.1 eligibility from codec success. Panel A reports stability-qualified certification, Panel B shows the codec-independent material eligibility ceiling, and Panel C quantifies the overstatement obtained when the Bader error criterion is counted without eligibility.

**Primary message:** compression success is scientifically interpretable only after the downstream observable is identifiable at the requested tolerance.

---

## Figure 4 — Stability is a property of the observable and its measurement protocol

**Canonical source:** `figures/R/figure4_stability_protocol.R`.

Protocol A remains archived provenance. Protocol A.1 changes the numerical probe to five fixed-seed uniform perturbations at the float32 L-infinity amplitude while retaining the frozen tolerance set, exclusion semantics, and reporting rules.

Panels A-B use the paired development subset of 254 density fields for which archived A and A.1 outputs can be compared. Panel C uses all 319 development + external systems with a finite A.1 floor and therefore defines the eligibility ceiling used for headline certification.

**Primary message:** a QoI cannot serve as a fidelity contract at a precision below its own numerical/topological reproducibility.

---

## Figure 5 — Topology-induced amplification explains irregular Bader response

**Canonical source:** `figures/R/figure5_topology_mechanism.R`.

The figure compares re-solved Bader error with the fixed-basin contribution, exposes signed per-atom domain-migration terms, shows representative full tolerance ladders, and relates rung-to-rung Bader jumps to basin reassignment over the frozen benchmark.

**Primary message:** re-solving a density-dependent partition can amplify a smooth field perturbation through Bader basin migration. This is a Bader-specific mechanism and is not generalized to every scientific QoI.

---

## Figure 6 — Equal nominal tolerance conflates distortion magnitude with error geometry

**Canonical source:** `figures/R/figure6_matched_realized_linf.R`.

At equal nominal tolerance, ZFP realizes only about 0.17x the L-infinity perturbation of SZ3/SPERR, whereas SZ3 and SPERR are close to 1.00x relative to one another. Within-material matching on `log10(realized_Linf)` at the primary 0.10-dex caliper substantially reduces the apparent codec gap but does not remove it. The same matched pairs are used for Bader-error, compression-ratio, and Protocol A.1 certification effects.

**Primary message:** equal nominal tolerance is not a valid test of error geometry. Realized distortion must be controlled before residual codec differences are interpreted.

---

## Figure 7 — Untouched external systems reproduce the stability-qualified decision frontier

**Canonical source:** `figures/R/figure7_external_confirmation.R`.

The pre-frozen 63-system external cohort contains 1,689 retained scientific rows, zero material-level pipeline failures and zero codec-bound violations. Three row-level Bader-solver failures remain explicitly audited.

The figure reports:

- external best-certified compression ratios with frozen bootstrap intervals,
- the tolerance-dependent SZ3-versus-ZFP win transition,
- replication of codec-dependent nominal-budget use,
- Protocol A.1 eligibility increasing from 16/63 at `1e-4 e` to 42/63 at `1e-3 e` and 57/63 at `1e-2 e`.

**Primary message:** the stability-qualified decision logic and tolerance-dependent codec ordering reproduce without retuning on untouched systems.

---

## Non-canonical legacy figure sources

- `figures/R/figure2_fixed_vs_resolved.R`: retained for provenance; superseded by `figure2_qoi_hierarchy.R`.
- `figures/R/figure6_compression_chemistry_tradeoff.R`: retained for provenance; superseded by `figure6_matched_realized_linf.R`.
- The earlier plan that labelled a rate-QoI frontier as Figure 5 is retired. Figure 5 is the formal topology-mechanism figure.

---

## Main-text claim hierarchy

1. **General:** reconstruction error alone does not define scientific fidelity; downstream QoI structure matters.
2. **Mechanistic:** identical reconstructions can produce smooth Hartree response but strongly irregular Bader response.
3. **Bader-specific:** basin migration is part of the actual downstream operator; fixed-basin scoring is not the fidelity metric for re-derived Bader analysis.
4. **Qualification:** Bader charge has a material-specific stability floor; contracts below that floor are non-evaluable.
5. **Comparison:** nominal codec controls are not commensurate; realized distortion must be matched before codec residuals are interpreted.
6. **Practical:** after Protocol A.1 qualification and realized-distortion control, lossy compression remains scientifically useful over a substantial tolerance-dependent frontier.
7. **Validation:** the frozen external cohort reproduces the decision-level findings without supporting a universal bulk-versus-vacuum stability generalization.

Do not generalize these three QoIs to all scientific observables. The manuscript supports a general evaluation principle with one deeply validated topology-sensitive chemistry case and two structurally distinct controls/comparators.

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
