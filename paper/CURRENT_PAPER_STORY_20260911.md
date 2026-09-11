# Current paper story — 2026-09-11

## One-sentence thesis

**A downstream scientific tolerance should be used to score scientific compression only after the reference QoI has been qualified for numerical stability at that tolerance; otherwise fixed-pipeline reconstruction agreement and robustness of the scientific interpretation are mixed into one binary label.**

## What the paper is actually about

The manuscript is not framed around the established observation that small pointwise reconstruction error need not imply small downstream QoI error. That is background motivation.

The contribution is a **benchmark-validity and measurement-contract framework** for scientific compression. The reader-facing qualification framework is **QoI Stability Qualification (QSQ)**. The evaluation order is:

`QoI Stability Qualification (QSQ) -> eligibility -> compression evaluation -> certification`

rather than simply:

`field error -> QoI error -> pass/fail`.

For Bader charge, each material–threshold pair has one of three operational states:

1. **eligible + certified** — the reference response passes the stated stability qualification and the compressed reconstruction satisfies the Bader contract;
2. **eligible + not certified** — the reference response passes qualification, but the reconstruction violates the contract;
3. **non-evaluable under the stated QSQ test** — the reference response fails the qualification at that tolerance, so compression agreement and reference robustness must be reported separately rather than collapsed into a scientifically interpreted binary score.

Numerical agreement remains a defined quantity in all three states. QSQ does not prove that a particular observed reconstruction deviation was or was not caused by the codec.

## Central quantitative evidence

### P1 — equal search opportunity

The historical full-record 97.2% / 95.5% reclassification fractions were found to depend strongly on the fact that the extra tight ladder had been targeted to the 143 materials eligible at `1e-3 e`. Those values remain provenance and are no longer the headline.

The missing tight ladder was therefore completed for all 111 other development materials: **1,332/1,332 additive reconstructions succeeded**. At the primary `1e-3 e` contract, failure to find a numerical pass under the now-equalized search opportunity occurs in **3.3% of eligible** versus **66.4% of QSQ screen-rejected** material–codec pairs, a **20.34× risk ratio**. The corresponding values are 10.9% vs 79.3% at `1e-4 e` and 0.0% vs 68.0% at `1e-2 e`.

This supports a strong association between the QSQ state and benchmark difficulty after removing unequal search opportunity. It is not a causal codec attribution result.

### P2 — prospective fresh-perturbation validation

The original five-seed QSQ gate was frozen before running **59 genuinely fresh iid-uniform perturbations per material** on all 254 development materials: **14,986/14,986 valid outcomes; unresolved = 0**.

At the pre-specified primary `1e-3 e` endpoint:

- QSQ accepts **143/254 materials = 56.3% coverage**;
- accepted materials have **135/8,437 = 1.600%** fresh threshold exceedances, material-cluster 95% CI **0.782–2.596%**;
- QSQ-rejected materials have **5,326/6,549 = 81.325%** fresh exceedances, 95% CI **75.981–86.257%**;
- rejected/eligible risk ratio = **50.83×**;
- at least one fresh exceedance occurs in **20/143** accepted materials versus **110/111** rejected materials.

Secondary pre-specified endpoints preserve the direction: `1e-4 e`, 4.016% vs 86.938% (21.65×); `1e-2 e`, 0.148% vs 79.593% (537.69×).

This is the strongest evidence for QSQ: the frozen five-seed screen prospectively stratifies unseen response risk under the declared iid-uniform perturbation model. It is **not** a worst-case certificate, a simultaneous guarantee for every material, or new-material generalization.

### P3A — independent implementation transfer

A deterministic 24-system panel, stratified across bulk/slab and four frozen QSQ floor bands, was evaluated with BaderKit on-grid, independent Henkelman on-grid and Henkelman near-grid implementations using the same historical five perturbation fields.

The first execution contained 360 recorded failures, but all were frozen and classified before retry as one pre-solver provenance-comparison error caused by applying a binary-ULP equality gate to decimal-serialized historical amplitudes. No recorded failure had reached a Bader solver. The engineering-only retry changed only the serialization-aware compatibility check and exit-code capture; the scientific panel, perturbations, solvers, density identities and thresholds were unchanged. The retry completed **360/360 with zero failures**, yielding **72/72 complete material–solver summaries**.

Resolved results:

- recreated BaderKit floors match the frozen floors to maximum absolute difference **8.71338e-11 e**;
- **Henkelman on-grid: 24/24 classification agreement at `1e-4`, `1e-3`, and `1e-2 e`, Cohen kappa = 1.000 at every threshold; Spearman floor-rank rho = 0.995**;
- **Henkelman near-grid:** agreement **82.6% / 83.3% / 95.8%** across the same thresholds; floor-rank rho = **0.754**.

The interpretation is deliberately two-sided: QSQ stratification is not merely an artifact of the original BaderKit implementation when the same on-grid basin-assignment class is used, but changing the numerical basin-assignment algorithm creates a measurable implementation-sensitive boundary. **P3A does not establish electronic-structure grid convergence or a unique physical Bader reference.**

## Supporting evidence chain

### Same reconstruction, different operator response

Electron number and periodic Hartree potential provide smoother controls on the same reconstructed densities. Hartree error follows an approximately first-order response to realized field perturbation (pooled log–log exponent ~1.02; median material R² = 0.997 ZFP, 0.994 SZ3, 0.996 SPERR), whereas re-derived Bader charge is much less regular.

### Bader-specific mechanism

Bader integration domains are re-derived from the reconstructed density. Compression can therefore perturb both density values and basin assignment. Fixed-basin scoring suppresses the domain-migration contribution and can substantially understate the response obtained by rerunning the actual downstream analysis. The mechanism is Bader-specific and is not generalized to arbitrary QoIs.

### Analysis-limited regime: supported wording

At the strictest `1e-4 e` certified contract, resolved Bader errors are on the same scale as the independently measured QSQ floor: median error/floor is approximately **1.09× for ZFP, 1.33× for SZ3, and 1.23× for SPERR**.

Supported wording:

> **The strictest certified regime is floor-scale, consistent with an emerging analysis-limited regime.**

Do not claim a universal material-level identity `plateau = floor`.

### Fair codec comparison requires realized-distortion control

Equal nominal codec tolerances do not produce equal realized perturbations. At matched nominal tolerance, realized L-infinity ratios are approximately ZFP/SZ3 = 0.17 and ZFP/SPERR = 0.17. Within-material matching on realized L-infinity reduces this confounding; the remaining Bader difference supports a residual error-structure contribution without identifying a unique geometric invariant.

### External confirmation

The untouched 63-system external cohort is evaluated under the same frozen qualification and certification rules with no retuning. External QSQ eligibility expands with relaxed tolerance (16/63, 42/63, 57/63 at `1e-4`, `1e-3`, `1e-2 e`), and the best certified compression-rate ordering changes with the requested scientific contract. The output is therefore a **stability-qualified rate–fidelity frontier**, not a universal codec leaderboard.

## Figure logic

- **Figure 1:** scientific-compression measurement contract.
- **Figure 2:** operator hierarchy / motivation.
- **Figure 3:** **central validation figure — equal-search benchmark test + prospective fresh-perturbation risk stratification.**
- **Figure 4:** archived float32 probe -> QSQ perturbation-probe validation.
- **Figure 5:** Bader basin-migration mechanism; implementation transfer remains supporting evidence rather than a second headline.
- **Figure 6:** nominal-vs-realized distortion confounding control.
- **Figure 7:** untouched external confirmation.

## Current research boundary and next gate

**P3A is complete. P3B is not.** The next high-value research task is true electronic-structure grid convergence on cases for which the original calculation inputs or an equivalent reproducible calculation protocol can be recovered. Interpolation of an existing density does not count.

The P4 chemistry-decision utility protocol has already been frozen outcome-blind. It should be executed after the P3 numerical-reference question is closed sufficiently to define the high-precision reference.

P5, transfer to a second topology-sensitive task, remains optional and should be undertaken only if it can be added without diluting the electronic-density story.

## Claim boundaries

Do not use the following as headline novelty:

- “pointwise error does not imply QoI fidelity” — established background;
- “Bader has a numerical/grid floor” — established numerical-analysis background;
- “Bader basin migration is a universal QoI mechanism” — unsupported generalization;
- “QSQ rescues codec failures” — incorrect interpretation;
- “95% of codec failures are invalid” — ladder-design-sensitive historical framing;
- “five seeds certify worst-case stability” — false;
- “24-system P3A proves grid convergence” — false;
- “plateau equals the QSQ floor” — stronger than the data support.

The canonical contribution is **validated QoI stability qualification before scientifically interpreting benchmark scoring**, with explicit reporting of the qualification model and its limits.

## Naming boundary

Reader-facing text uses **QoI Stability Qualification (QSQ)**, **QSQ stability floor**, **QSQ eligibility**, **stability probe**, and **archived float32 probe**. Historical repository identifiers such as `Protocol A`, `Protocol A.1`, and filenames containing `_A1` remain unchanged only where needed for frozen provenance and reproducibility.
