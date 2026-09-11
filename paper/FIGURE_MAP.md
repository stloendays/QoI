# Figure map

Updated 2026-09-11. Canonical figure-numbering, narrative-role, source, and provenance registry for the certifiability manuscript.

**Working title:** *Stability-qualified benchmarks for scientific compression of electronic densities*

## Narrative spine

The manuscript is organized around a benchmark-validity principle, not the already-established observation that raw reconstruction error does not automatically guarantee downstream QoI fidelity:

> **A downstream scientific tolerance is a valid compression benchmark only after the QoI is shown to be numerically identifiable at that tolerance.**

The reader-facing name for the qualification framework is **QoI Stability Qualification (QSQ)**. The figure logic is:

`measurement contract -> operator motivation -> binary-benchmark invalidity -> QSQ probe validation -> Bader mechanism -> fair codec comparison -> untouched external confirmation`

**Figure 3 is the central novelty-bearing figure.** Figure 2 supplies motivation, Figure 4 validates the eligibility procedure, Figure 5 explains the Bader-specific mechanism, Figure 6 controls a separate realized-distortion confound, and Figure 7 closes the evidence chain externally.

## Canonical figure registry

| Figure | Role | R source | Formal outputs | Status |
|---|---|---|---|---|
| 1 | Scientific-compression measurement contract | `figures/R/figure1_qoi_contract.R` | `figures/R/rendered/figure1_qoi_contract_R.{png,pdf,svg}` | **LOCKED** |
| 2 | Operator hierarchy on identical reconstructions | `figures/R/figure2_qoi_hierarchy.R` | `figures/R/rendered/figure2_qoi_hierarchy_R.{png,pdf,svg}` | **LOCKED** |
| 3 | Binary benchmark -> stability-qualified three-state certification | `figures/R/figure3_certification_landscape.R` | `figures/R/rendered/figure3_certification_landscape_R.{png,pdf,svg}` | **LOCKED 2026-09-11** |
| 4 | Archived float32 probe -> QSQ perturbation-probe validation | `figures/R/figure4_stability_protocol.R` | `figures/R/rendered/figure4_stability_protocol_R.{png,pdf,svg}` | **LOCKED** |
| 5 | Basin migration and topology-sensitive Bader amplification | `figures/R/figure5_topology_mechanism.R` | `figures/R/rendered/figure5_topology_mechanism_R.{png,pdf,svg}` | **LOCKED** |
| 6 | Nominal tolerance vs matched realized L-infinity | `figures/R/figure6_matched_realized_linf.R` | `figures/R/rendered/figure6_matched_realized_linf_R.{png,pdf,svg}` | **LOCKED** |
| 7 | Untouched external confirmation | `figures/R/figure7_external_confirmation.R` | `figures/R/rendered/figure7_external_confirmation_R.{png,pdf,svg}` | **LOCKED** |

## Figure 1 — Measurement contract

**Function:** conceptual entry point. Separates the codec's field-level reconstruction guarantee from the downstream scientific measurement. Electron number, Hartree potential, and Bader charge are introduced as distinct downstream operators; Bader explicitly re-partitions the reconstructed field.

**Take-home:** scientific certification requires a defined downstream operator and tolerance, not only a pointwise field bound.

## Figure 2 — Operator hierarchy

**Function:** motivation/background evidence, not the primary novelty claim.

Frozen evidence on identical reconstructions includes:
- 1,383/3,205 reconstructions with `|Delta N_e| < 1e-4 e` still have re-derived Bader error `>=1e-3 e` (43.15%);
- Hartree error follows an approximately first-order response to realized L-infinity (pooled exponent 1.02; median material `R^2` 0.994-0.997 across codecs);
- only 32.4% of material-codec Bader ladders are strictly monotone;
- 55.4% of gate-passing rows lie in matched-Hartree bins with Bader `P90/P10 >= 10`.

**Take-home:** operator structure changes how reconstruction perturbations propagate, motivating an explicit downstream measurement contract. Do not present “raw error != QoI fidelity” as a new discovery.

## Figure 3 — Binary benchmark versus three-state certification

**Function:** **central benchmark-validity result**.

**Caption:** `paper/FIGURE3_CAPTION_FINAL_20260911.md`.

**Analysis unit:** one material-codec decision at a fixed Bader threshold; 254 development materials × 3 codecs = **762 decisions per threshold**.

### A — Naive binary benchmark
- `1e-4 e`: 229 pass, 533 fail.
- `1e-3 e`: 452 pass, 310 fail.
- `1e-2 e`: 654 pass, 108 fail.

### B — QSQ three-state certification
- `1e-4 e`: 123 certified, 15 eligible failures, 624 non-evaluable.
- `1e-3 e`: 415 certified, 14 eligible failures, 333 non-evaluable.
- `1e-2 e`: 640 certified, 47 eligible failures, 75 non-evaluable.

### C — Failure reclassification
- `1e-4 e`: **518/533 = 97.2%** of naive failures are non-evaluable; 15 remain genuine eligible failures.
- `1e-3 e`: **296/310 = 95.5%** are non-evaluable; 14 remain genuine eligible failures.
- `1e-2 e`: **61/108 = 56.5%** are non-evaluable; 47 remain genuine eligible failures.
- Eligibility also invalidates apparent success: at `1e-4 e`, **106/229 = 46.3% of naive passes are non-evaluable**.

**Primary message:** at the two strictest contracts, more than 95% of apparent binary failures cannot be scientifically attributed to the compressor because the reference Bader analysis itself fails the independent numerical-eligibility test.

**Interpretation boundary:** QSQ does not “rescue” failing codecs. A non-evaluable material-threshold pair is neither pass nor failure; the binary label itself is invalid.

**Formal validation:** GitHub Actions run `34565814071` on source commit `1886f776f048395b47eb16129c1231e814922271`; artifact `10185973963`. PNG, PDF, and SVG were all generated, checked non-empty, and visually inspected. Repository copies are `617,779 B` PNG, `7,903 B` PDF, and `39,701 B` SVG.

## Figure 4 — QSQ probe validation

**Function:** validates why the QSQ perturbation test, rather than the archived float32 probe, defines eligibility.

The archived float32 probe is retained unchanged as provenance. QSQ uses five pre-specified fixed-seed uniform perturbations at the material's float32 L-infinity amplitude while preserving the tolerance set and reporting semantics.

Across 319 systems, QSQ non-evaluable fractions are 79.9% at `1e-4 e`, 41.4% at `1e-3 e`, and 9.7% at `1e-2 e`. In the 18-material pre-freeze calibration, archived float32 rounding creates a median of 82 exact neighbouring ties and zero voxel reassignment in 9/18 systems, versus 2/18 under the same-amplitude primary noise probe. In the formal paired comparison of all 254 development materials, the operative five-seed QSQ floor is a median of approximately **1.6×10^4** times the archived float32-probe floor.

**Take-home:** the qualification probe itself must excite the numerical failure channel relevant to the downstream operator.

## Figure 5 — Bader-specific mechanism

**Function:** mechanism, not general benchmark novelty.

Re-derived Bader scoring is the scientific metric because the basin is a functional of the reconstructed density. Fixed-basin scoring is diagnostic only; it suppresses domain migration. Representative decompositions show that domain migration can dominate the tight-tolerance response.

**Take-home:** compression can perturb both the density being integrated and the integration domain itself, explaining irregular Bader response.

## Figure 6 — Realized-distortion confounding control

**Function:** fair codec comparison after the benchmark-validity issue has been established.

At equal nominal tolerance, ZFP realizes approximately 0.17× the L-infinity perturbation of SZ3 or SPERR; SZ3/SPERR is approximately 1.00×. Within-material matching on `log10(realized_Linf)` with the primary 0.10-dex caliper gives re-derived Bader-error ratios of approximately ZFP/SZ3 = 0.557, ZFP/SPERR = 0.601, and SZ3/SPERR = 1.033.

**Take-home:** downstream tolerance must be qualified for measurability, and upstream codec comparison must use realized rather than nominal distortion.

## Figure 7 — Untouched external confirmation

**Function:** closing validation on 63 completed external systems / 1,689 retained rows with frozen rules and no retuning.

External QSQ eligibility is 16/63 at `1e-4 e`, 42/63 at `1e-3 e`, and 57/63 at `1e-2 e`. Median best-certified compression ratios remain tolerance dependent: approximately ZFP/SZ3/SPERR = 13.0/12.1/5.2× at `1e-4 e`, 18.8/18.8/6.4× at `1e-3 e`, and 40.6/65.9/10.8× at `1e-2 e`.

**Take-home:** the frozen stability-qualified decision logic and tolerance-dependent rate-fidelity frontier reproduce on untouched systems.

## Results order

1. **Figure 2:** establish the operator-level motivation/background on identical reconstructions; this is not the novelty claim.
2. Define QSQ eligibility and the three-state state space.
3. **Figure 3:** demonstrate that naive binary benchmarking is materially invalid at strict Bader thresholds; keep Figure 3 as the novelty-bearing result.
4. **Figure 4:** validate the QSQ perturbation probe against the archived float32 predecessor.
5. Report the tight-ladder result conservatively: at `1e-4 e`, median resolved-Bader-error/QSQ-floor is 1.09-1.33× across codecs; call this floor-scale and consistent with an emerging analysis-limited regime, not `plateau = floor`.
6. **Figure 5:** explain Bader domain migration.
7. **Figure 6:** control nominal-versus-realized distortion.
8. Report rate-fidelity only among eligible material-threshold pairs, using `benchmark/summary_a1.csv` rather than historical prose values.
9. **Figure 7:** close with untouched external confirmation.

## Main-text claim hierarchy

1. **Background:** pointwise/raw-data error alone is not a universal downstream guarantee.
2. **Central contribution:** requested QoI tolerances must be independently qualified for numerical identifiability before codec scoring.
3. **Headline evidence:** 97.2% and 95.5% of naive failures at `1e-4` and `1e-3 e` are reclassified as non-evaluable.
4. **Method requirement:** the qualification probe itself must be validated.
5. **Bader mechanism:** density-dependent basin migration can dominate re-derived charge error.
6. **Codec comparison:** nominal tolerance is not a common realized-distortion scale.
7. **Practical result:** eligible systems retain a substantial, tolerance-dependent certified compression frontier.
8. **External validation:** the frozen decision logic reproduces without retuning.

## Figure provenance

Locked formal runs retained for provenance:
- Figure 1: run `34371089020`, artifact `10111997887`.
- Figure 2: run `34352844171`, artifact `10104481700`.
- **Figure 3: run `34565814071`, artifact `10185973963`, source commit `1886f776f048395b47eb16129c1231e814922271`.**
- Figure 4: run `34370291570`, artifact `10111673650`.
- Figure 5: run `34349558487`, artifact `10103144848`.
- Figure 6: run `34340308601`, artifact `10099481566`.
- Figure 7: run `34369886843`, artifact `10111557054`.

The pre-2026-09-11 Figure 3 rendering (run `34369822427`, artifact `10111464747`) is retained as provenance but superseded by the binary-to-three-state redesign.

## Supplementary scope

Keep the following out of the main figure sequence: full electron-count and Hartree tables, reproduction-gate diagnostics, no-exclusion sensitivity, floor-relative sensitivity, QSQ seed/amplitude sensitivity, negative algorithm results, failure taxonomy, and external-baseline unit conversions.

Do not generalize the three studied QoIs to all scientific observables. The manuscript supports a general **evaluation principle** using one deeply validated topology-sensitive chemical QoI and two structurally distinct controls/comparators.

## Naming boundary

Reader-facing labels use **QoI Stability Qualification (QSQ)**, **QSQ stability floor**, **QSQ eligibility**, **QSQ perturbation probe**, and **archived float32 probe**. Historical internal identifiers and filenames containing `Protocol A`, `Protocol A.1`, or `_A1` are preserved only for provenance and reproducibility.
