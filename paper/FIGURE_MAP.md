# Figure map

Updated 2026-09-11. This is the canonical figure-numbering, narrative-role, and provenance registry for the certifiability manuscript.

**Working title:** *Stability-Qualified Certification of Lossy Compression for Electronic-Density QoIs*

## Narrative spine

The paper is no longer organized around the generic observation that pointwise reconstruction error does not guarantee downstream QoI fidelity. That observation is established prior art and serves only as motivation. The main contribution is a benchmark-validity principle:

> **A downstream scientific tolerance is a valid compression benchmark only after the QoI is shown to be numerically identifiable at that tolerance.**

The main-text figure sequence therefore follows a measurement-contract logic:

`operator motivation -> benchmark invalidity -> qualification-probe validation -> Bader mechanism -> fair codec comparison -> untouched external confirmation`

The scientific hierarchy is deliberate. **Figure 3 is the central result.** Figure 2 motivates why the downstream operator matters; Figure 4 validates the qualification procedure; Figure 5 explains the Bader-specific mechanism; Figure 6 controls a separate realized-distortion confound; Figure 7 tests whether the frozen decision logic reproduces externally.

---

## Canonical manuscript figure registry

| Figure | Canonical role | R source | Formal rendered outputs | Main-text function | Status |
|---|---|---|---|---|---|
| 1 | Scientific-compression measurement contract | `figures/R/figure1_qoi_contract.R` | `figures/R/rendered/figure1_qoi_contract_R.{png,pdf,svg}` | conceptual entry point | **LOCKED** |
| 2 | Operator hierarchy on identical reconstructions | `figures/R/figure2_qoi_hierarchy.R` | `figures/R/rendered/figure2_qoi_hierarchy_R.{png,pdf,svg}` | motivation / background evidence | **LOCKED** |
| 3 | Binary benchmark -> three-state certification | `figures/R/figure3_certification_landscape.R` | `figures/R/rendered/figure3_certification_landscape_R.{png,pdf,svg}` | **central benchmark-validity result** | **REFRAMED 2026-09-11; CI rendering** |
| 4 | Protocol A -> A.1 probe correction and eligibility qualification | `figures/R/figure4_stability_protocol.R` | `figures/R/rendered/figure4_stability_protocol_R.{png,pdf,svg}` | qualification-method validation | **LOCKED** |
| 5 | Basin migration and topology-sensitive Bader amplification | `figures/R/figure5_topology_mechanism.R` | `figures/R/rendered/figure5_topology_mechanism_R.{png,pdf,svg}` | Bader-specific mechanism | **LOCKED** |
| 6 | Nominal tolerance vs matched realized L-infinity | `figures/R/figure6_matched_realized_linf.R` | `figures/R/rendered/figure6_matched_realized_linf_R.{png,pdf,svg}` | confounding-control analysis | **LOCKED** |
| 7 | Untouched external confirmation | `figures/R/figure7_external_confirmation.R` | `figures/R/rendered/figure7_external_confirmation_R.{png,pdf,svg}` | external validation / practical frontier | **LOCKED** |

---

## Figure 1 — The measurement contract precedes codec scoring

**Canonical source:** `figures/R/figure1_qoi_contract.R`.

The schematic maps `rho -> codec -> rho_tilde -> downstream QoI` and separates the field-level reconstruction bound from the downstream scientific measurement. Electron number, Hartree potential, and Bader charge are shown as structurally distinct operators; the Bader lane explicitly re-partitions the reconstructed field.

**Role in the paper:** conceptual framing only. Figure 1 introduces the distinction between a reconstruction guarantee and a downstream measurement contract, but it does not carry the novelty claim by itself.

**Take-home message:** a codec constrains the reconstructed field; scientific certification requires an explicitly defined downstream operator and tolerance.

---

## Figure 2 — Operator structure explains why a downstream contract is needed

**Canonical source:** `figures/R/figure2_qoi_hierarchy.R`.

Figure 2 uses the same frozen reconstructions to compare three downstream responses:

- total electron number as a global linear integral,
- periodic Hartree potential as a linear nonlocal comparator,
- re-derived Bader charge as a topology-sensitive, density-dependent partition.

Key frozen evidence:

- 1,383 of 3,205 reconstructions with `|Delta N_e| < 1e-4 e` still have re-derived Bader error `>= 1e-3 e` (43.15%);
- Hartree error follows an approximately first-order response to realized L-infinity (pooled exponent 1.02; median material `R^2` 0.994-0.997 across codecs);
- only 32.4% of material-codec Bader ladders are strictly monotone;
- 55.4% of gate-passing rows lie in matched-Hartree bins with Bader `P90/P10 >= 10`.

**Role in the paper:** motivation, not primary novelty. This figure establishes that the benchmark must explicitly include the downstream operator, but the manuscript must not imply that “raw error != QoI fidelity” is newly discovered here.

**Take-home message:** identical reconstruction perturbations can propagate regularly through one operator and irregularly through another, so the scientific contract must be defined downstream.

---

## Figure 3 — Binary Bader benchmarking is invalid at strict thresholds without eligibility qualification

**Canonical source:** `figures/R/figure3_certification_landscape.R`.

**Caption source:** `paper/FIGURE3_CAPTION_FINAL_20260911.md`.

Figure 3 is the manuscript's central benchmark-validity result and is deliberately structured as a before/after decision problem.

### Panel A — Naive binary benchmark

Each threshold contains 254 development materials × 3 codecs = **762 material-codec decisions**. Without the Protocol A.1 eligibility gate:

- `1e-4 e`: 229 naive passes, 533 naive failures;
- `1e-3 e`: 452 naive passes, 310 naive failures;
- `1e-2 e`: 654 naive passes, 108 naive failures.

### Panel B — Stability-qualified three-state certification

The same 762 decisions are reassigned to the scientifically valid state space:

- `1e-4 e`: 123 certified, 15 eligible failures, 624 non-evaluable;
- `1e-3 e`: 415 certified, 14 eligible failures, 333 non-evaluable;
- `1e-2 e`: 640 certified, 47 eligible failures, 75 non-evaluable.

### Panel C — What the binary benchmark gets wrong

Among naive failures:

- `1e-4 e`: **518/533 = 97.2%** are reclassified as non-evaluable; only 15 are genuine eligible failures;
- `1e-3 e`: **296/310 = 95.5%** are reclassified as non-evaluable; only 14 are genuine eligible failures;
- `1e-2 e`: **61/108 = 56.5%** are reclassified as non-evaluable; 47 are genuine eligible failures.

Qualification does not merely remove failures. At `1e-4 e`, **106/229 = 46.3% of naive passes are also non-evaluable**.

**Primary message:** at the two strictest Bader contracts, more than 95% of apparent binary failures cannot be scientifically attributed to the compressor because the reference Bader analysis itself fails the independent numerical-eligibility test.

**Interpretation boundary:** never write that Protocol A.1 “rescues” failing codecs. A non-evaluable decision is neither a pass nor a failure; the binary label itself is invalid.

**Placement:** this figure should appear early in Results, immediately after Protocol A.1 eligibility is defined, and before codec leaderboard/rate-fidelity results.

---

## Figure 4 — The qualification probe itself must be validated

**Canonical source:** `figures/R/figure4_stability_protocol.R`.

Protocol A is retained unchanged as provenance. Protocol A.1 replaces the order-preserving float32 round-trip probe with five pre-specified fixed-seed uniform perturbations at the material's float32 L-infinity amplitude, while retaining the tolerance set and exclusion/reporting semantics.

Panels comparing Protocol A and A.1 use the paired development subset; the eligibility ceiling uses the complete 319-system development + external stability corpus.

Frozen A.1 non-evaluable fractions across 319 systems are:

- 79.9% at `1e-4 e`,
- 41.4% at `1e-3 e`,
- 9.7% at `1e-2 e`.

**Role in the paper:** methodological validation supporting Figure 3. It establishes that the eligibility test is not an arbitrary post-hoc filter and that the probe must excite the numerical failure channel relevant to the downstream operator.

**Take-home message:** the measurement procedure must itself be qualified before it can certify numerical identifiability.

---

## Figure 5 — Basin migration supplies the Bader-specific mechanism

**Canonical source:** `figures/R/figure5_topology_mechanism.R`.

The figure compares re-derived Bader error with fixed-basin error, resolves signed per-atom domain-migration contributions, and connects abrupt tolerance-ladder Bader changes to changes in the density-dependent partition.

The scientific Bader metric always re-solves the partition. Fixed-basin scoring is a diagnostic only because holding the reference basin fixed removes the domain-migration channel from the downstream operator.

**Role in the paper:** mechanism, not general benchmark novelty. It explains why Bader is a stringent stress test for certifiability without claiming that every QoI has the same topology-driven behavior.

**Take-home message:** small field perturbations can alter both the integrand and the integration domain; the latter can dominate the re-derived Bader response.

---

## Figure 6 — Realized-distortion matching removes a separate codec-comparison confound

**Canonical source:** `figures/R/figure6_matched_realized_linf.R`.

At equal nominal tolerance, ZFP realizes only about 0.17× the L-infinity perturbation of SZ3 or SPERR, while SZ3/SPERR is approximately 1.00×. Equal nominal tolerance is therefore not a fair test of codec error structure.

Within-material matching on `log10(realized_Linf)` with the primary 0.10-dex caliper yields matched re-derived Bader-error ratios of approximately:

- ZFP/SZ3 = 0.557,
- ZFP/SPERR = 0.601,
- SZ3/SPERR = 1.033.

The matched pairs also support compression-ratio and certification-rate comparisons.

**Role in the paper:** confounding-control analysis. Figure 6 is important for fair codec interpretation but is explicitly secondary to the certifiability result in Figure 3.

**Take-home message:** the benchmark must qualify both sides of the comparison: downstream tolerance must be measurable, and upstream distortion must be measured rather than inferred from nominal codec settings.

---

## Figure 7 — The frozen decision rule reproduces on untouched systems

**Canonical source:** `figures/R/figure7_external_confirmation.R`.

The untouched confirmatory cohort contains 63 completed systems and 1,689 retained scientific rows, with zero material-level pipeline failures and zero codec error-bound violations; three row-level Bader-solver failures remain explicitly audited.

Protocol A.1 external eligibility is:

- 16/63 at `1e-4 e`,
- 42/63 at `1e-3 e`,
- 57/63 at `1e-2 e`.

External median best-certified compression ratios remain tolerance dependent:

- `1e-4 e`: ZFP ~13.0×, SZ3 ~12.1×, SPERR ~5.2×;
- `1e-3 e`: ZFP ~18.8×, SZ3 ~18.8×, SPERR ~6.4×;
- `1e-2 e`: SZ3 ~65.9×, ZFP ~40.6×, SPERR ~10.8×.

**Role in the paper:** closing validation. The external cohort tests the frozen eligibility + certification procedure without retuning and does not restore the falsified universal bulk-versus-vacuum stability generalization.

**Take-home message:** the stability-qualified decision logic and tolerance-dependent rate-fidelity frontier reproduce on untouched systems.

---

## Recommended Results order

1. Define Protocol A.1 eligibility and the three-state decision space.
2. **Figure 3:** show that naive binary benchmarking is materially invalidated by eligibility qualification.
3. **Figure 2:** use electron-count/Hartree/Bader contrasts to motivate why the operator must be part of the contract. If the journal prefers conventional conceptual ordering, Figure 2 may appear immediately before Figure 3 in layout, but the prose must still make Figure 3 the novelty-bearing result.
4. **Figure 4:** validate why A.1, rather than archived Protocol A, is the operative stability qualification.
5. Report the tight-ladder floor-scale observation conservatively: at `1e-4 e`, median resolved-Bader-error/A.1-floor is 1.09-1.33× across codecs; do not claim universal `plateau = floor`.
6. **Figure 5:** explain the Bader-specific domain-migration mechanism.
7. **Figure 6:** control nominal-vs-realized distortion before interpreting codec residuals.
8. Report stability-qualified rate-fidelity among eligible pairs only.
9. **Figure 7:** close with untouched external confirmation.

---

## Main-text claim hierarchy

1. **Background:** raw-data error alone is not a universal downstream scientific guarantee.
2. **Central contribution:** a requested downstream tolerance must be independently qualified for numerical identifiability before it is used to score a compressor.
3. **Headline evidence:** 97.2% and 95.5% of naive failures at `1e-4` and `1e-3 e` are reclassified as non-evaluable under Protocol A.1.
4. **Measurement-method requirement:** the qualification probe itself must be validated against the downstream numerical operator.
5. **Bader mechanism:** density-dependent basin migration can dominate re-derived charge error.
6. **Codec-comparison control:** nominal codec tolerance is not a common realized-distortion scale.
7. **Practical result:** among eligible material-threshold pairs, lossy compression retains a substantial, tolerance-dependent certified rate-fidelity frontier.
8. **External validation:** the frozen decision logic reproduces without retuning on the 63-system external cohort.

---

## Locked / legacy provenance

Previously validated formal runs retained for provenance:

- Figure 1: run `34371089020`, artifact `10111997887`.
- Figure 2: run `34352844171`, artifact `10104481700`.
- Figure 4: run `34370291570`, artifact `10111673650`.
- Figure 5: run `34349558487`, artifact `10103144848`.
- Figure 6: run `34340308601`, artifact `10099481566`.
- Figure 7: run `34369886843`, artifact `10111557054`.

The pre-2026-09-11 Figure 3 certification-landscape rendering (run `34369822427`, artifact `10111464747`) is retained as provenance but is superseded by the binary-to-three-state redesign. The current Figure 3 source retains the same canonical path so its existing CI workflow continues to validate PNG/PDF/SVG and write the formal renderings back to `main`.

Non-canonical legacy sources remain versioned:

- `figures/R/figure2_fixed_vs_resolved.R` — superseded by the operator-hierarchy Figure 2;
- `figures/R/figure6_compression_chemistry_tradeoff.R` — superseded by realized-L-infinity matching;
- earlier rate-QoI plans previously labeled Figure 5 — retired.

---

## Supplementary material

| Panel | Content | Disposition |
|---|---|---|
| S1 | Full electron-count summaries by codec/tolerance | new SI |
| S2 | Full Hartree group tables, per-material fits, slab monotonicity diagnostics | new SI |
| S3 | Hartree reproduction-gate failures / provenance | new SI |
| S4 | No-exclusion sensitivity | retain |
| S5 | Floor-relative error and inflated-threshold sensitivity | retain |
| S6 | Protocol A.1 probe amplitude and seed sensitivity | retain |
| S7 | Negative result: boundary-aware allocation | retain |
| S8 | Negative result: promolecule prior | retain |
| S9 | Failure taxonomy / registry | retain |
| S10 | External baselines and unit conversions | retain |

Do not generalize the three studied QoIs to all scientific observables. The manuscript supports a general **evaluation principle** using one deeply validated topology-sensitive chemical QoI and two structurally distinct controls/comparators.
