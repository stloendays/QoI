# Current paper story — 2026-10-01

**Active title:** *Numerical stability qualification for downstream-fidelity benchmarks of compressed electronic densities*

## One-sentence thesis

**Scientific compression should be scored only after the complete measurement contract is qualified at the requested tolerance; evaluability depends on the QoI, numerical algorithm and exact-versus-approximate input roles, while codec performance further depends on the downstream operator and the spatial/frequency structure of reconstruction error.**

## What the paper is actually about

The manuscript is not framed around the established observation that small pointwise reconstruction error need not imply small downstream QoI error. That is background motivation.

The contribution is a **measurement contract for benchmark validity** in scientific compression. The reader-facing qualification framework is **QoI Stability Qualification (QSQ)**. QSQ is defined from the outset on the complete contract: QoI, numerical algorithm, scientific tolerance and the role of every input as exact or approximate. Only approximate inputs are perturbed. The evaluation order is:

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

A deterministic 24-system panel, stratified across bulk/slab and four QSQ floor bands, was evaluated with the primary on-grid analysis, independent Henkelman on-grid analysis and Henkelman near-grid analysis using the same five perturbation fields.

Resolved results:
- **Henkelman on-grid:** 24/24 classification agreement at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$, Cohen's $\kappa=1.000$ at every threshold; Spearman floor-rank $\rho=0.995$.
- **Henkelman near-grid:** agreement **82.6% / 83.3% / 95.8%** across the same thresholds; $\rho=0.754$.

The scientific conclusion is that QSQ classification transfers across an independent implementation when basin-assignment semantics are matched, but is not implementation-free. Engineering failure taxonomy and retry provenance remain in the repository audit rather than the scientific story.

### Measurement-contract decomposition — partition-defining reference field

QSQ treats input roles as part of the scientific contract. A dedicated all-electron-reference Bader experiment separates the integrated charge field from the partition-defining field. At the primary $10^{-3}\,e$ threshold, exact all-electron reference + perturbed CHGCAR is 50/50 eligible, while perturbing the all-electron reference gives 3/50 eligibility whether CHGCAR is exact or perturbed. The reference-only/joint floor ratio and median basin-reassignment ratio are both 1.000.

This is direct mechanism evidence that, under the tested standard all-electron-reference Bader contract, numerical instability is dominated by the partition-defining field. It also demonstrates why QSQ must qualify the complete material–QoI–algorithm–input-handling contract rather than assign a material-level stability label.

### P4 — outcome-blind chemical-decision boundary case

A chemistry/provenance/geometry-only audit of the 68 NOMAD development slabs froze **five paired chemical states** before QSQ, codec, P2/P3A or Bader outcomes were used for inclusion. All five passed the pre-specified BaderKit/Henkelman on-grid reference gate. The resolved compression analysis contains **216/216 successful solver cells** and **60/60** common-tight qualitative target-atom charge-transfer directions matching the frozen reference.

This is a deliberately useful **null correctness result**. The unqualified baseline already has zero sign errors, while QSQ at `1e-3 e` retains **36/60 trials from 3/5 pairs** and also has zero errors. QSQ therefore does not improve this coarse endpoint; instead, P4 demonstrates that strict numerical Bader fidelity and preservation of a large-margin qualitative chemical direction are distinct measurement contracts. Under the pre-specified optional independent-solver audit, QSQ-targeted escalation uses 48 Henkelman reconstructed-state calls / 397.2 s versus 108 / 733.3 s for blanket escalation; this is audit-cost reduction only, not a correctness gain.

## Supporting evidence chain

### Same reconstruction, different operator response

Electron number and periodic Hartree potential provide smoother controls on the same reconstructed densities. Hartree error follows an approximately first-order response to realized field perturbation (pooled log–log exponent ~1.02; median material R² = 0.997 ZFP, 0.994 SZ3, 0.996 SPERR), whereas re-derived Bader charge is much less regular.

### Bader-specific mechanism

Bader stability depends on the field that defines the partition topology. In the primary self-partitioned contract, the same density is both the integrated charge field and the partition-defining field, so perturbation can change values and basin assignment together. In the all-electron-reference contract, these roles can be separated.

Across 53 planned development materials with published all-electron inputs, 50 are analyzable and three retain non-finite AECCAR0 input failures. At $10^{-3}\,e$, keeping the all-electron partition reference exact while perturbing CHGCAR leaves **50/50 eligible**. Perturbing both fields gives **3/50 eligible**. Holding CHGCAR exact and perturbing only the all-electron reference also gives **3/50 eligible**. The material-median reference-only/joint stability-floor ratio is **1.000**, the median basin-reassignment ratio is **1.000**, and all 50 analyzable materials satisfy $f_{\mathrm{ref-only}}\ge0.9f_{\mathrm{joint}}$.

Thus, under the tested contract, the observed Bader instability is controlled overwhelmingly by perturbation of the partition-defining reference field. Fixed-partition scoring suppresses this channel. This mechanism is Bader-specific and is not generalized to arbitrary QoIs.

### Analysis-limited regime: supported wording

At the strictest `1e-4 e` certified contract, resolved Bader errors are on the same scale as the independently measured QSQ floor: median error/floor is approximately **1.09× for ZFP, 1.33× for SZ3, and 1.23× for SPERR**.

Supported wording:

> **The strictest certified regime is floor-scale, consistent with an emerging analysis-limited regime.**

Do not claim a universal material-level identity `plateau = floor`.

### Qualification generalizes, but evaluability is QoI-specific

The pre-declared second-topology-QoI extension applies the same qualification logic to **grid-local density extrema**: strict local maxima and minima of the sampled density relative to their 26-neighbour voxel neighbourhood. This is a discrete grid observable and is not presented as a continuous QTAIM critical-point calculation.

At the strict maximum-set endpoint, **118/254** development materials are qualified. Across the 59 fresh perturbations per material, qualified materials show **0/6,962** maximum-count changes versus **6,444/8,024 = 80.31%** among screen-rejected materials; the secondary maximum-set endpoint changes in **3/6,962** versus **7,509/8,024 = 93.58%** trials. The qualification principle therefore transfers to a second topology-sensitive QoI.

However, the evaluability boundary does not transfer from Bader charge. Agreement between Bader eligibility at `1e-3 e` and grid-local-extrema eligibility is only **Cohen's kappa = 0.1337**, and the corresponding stability floors have **Spearman rho = 0.1389**. The reader-facing conclusion is:

> **The qualification principle generalizes across topology-sensitive QoIs, but the set of scientifically evaluable systems is QoI-specific.**

### Probe-family robustness

A codec-shaped perturbation extension tests whether the codec-independent iid probe misses compressor-specific failure directions. At the primary `1e-3 e` endpoint, iid versus codec-shaped eligibility agreement is **0.902 for ZFP** and **0.937 for SZ3 and SPERR**. The iid floor is conservative on aggregate for ZFP and SPERR and statistically indistinguishable from the codec-shaped floor for SZ3 under the pre-declared rule. Among the 143 iid-admitted materials, codec-shaped floors do not improve prospective prediction of fresh iid exceedance risk and are worse for ZFP. This supports retaining a codec-independent qualification probe rather than making evaluability codec-specific.

### Discussion-only interpretive evidence

Two completed extensions are intentionally excluded from the Results hierarchy, main figures and Abstract.

- **Continuous risk calibration:** the measured floor contains graded prospective-risk information, but a stringent calibrated risk cutoff moves inside the binary eligibility boundary and reduces coverage. This explains why the transparent binary rule is retained as a qualification boundary rather than promoted as a per-material probability guarantee.
- **Reference-density predictors:** boundary-gap descriptors correlate with the measured Bader floor, but external prediction is weak. This is consistent with a nonlinear collective basin-reassignment problem in which local ordering margins matter without fully determining the response. These descriptors inform mechanism but do not replace direct QSQ measurement.

If either point remains in the submitted paper, it should appear only in Discussion, with quantitative details in the SI.

### Fair codec comparison requires realized-distortion control

Equal nominal codec tolerances do not produce equal realized perturbations. At matched nominal tolerance, realized L-infinity ratios are approximately ZFP/SZ3 = 0.17 and ZFP/SPERR = 0.17. Within-material matching on realized L-infinity reduces this confounding; the remaining Bader difference supports a residual error-structure contribution, but the nonlinear Bader residual is not assigned to a single Fourier descriptor.

### Fourier-spectrum mechanism closes the Hartree codec effect

The exact 457 ZFP/SZ3 matched pairs from 214 materials reproduce the historical Hartree-error ratio at **0.0776221**. A Nyquist-safe Hermitian Poisson operator gives **0.0776219**, with the direct-space/Fourier-space identity closing to a maximum relative error of **1.30e-15**.

The exact pairwise decomposition separates total spectral error magnitude from operator-weighted frequency allocation. The material-level centers are **0.376** for the total spectral-energy factor and **0.203** for the spectral Hartree-susceptibility factor. Frequency structure contributes a material-median **62.0%** of the absolute-log codec effect; **99.5%** of materials have lower ZFP Hartree susceptibility, **98.1%** have a higher ZFP spectral centroid, and **99.1%** have a lower ZFP low-G error-energy fraction.

This is a mechanism result for the Hartree control: ZFP shifts reconstruction error away from the long-wavelength modes amplified most strongly by the Hartree operator. It supports the general principle that scalar pointwise distortion is insufficient when the downstream operator is spatially or spectrally selective, without claiming that the Bader residual is controlled by the same Fourier statistic.

### External confirmation

The untouched 63-system external cohort is evaluated under the same frozen qualification and certification rules with no retuning. External QSQ eligibility expands with relaxed tolerance (16/63, 42/63, 57/63 at `1e-4`, `1e-3`, `1e-2 e`), and the best certified compression-rate ordering changes with the requested scientific contract. The output is therefore a **stability-qualified rate–fidelity frontier**, not a universal codec leaderboard.

## Figure logic

- **Figure 1:** scientific-compression measurement contract.
- **Figure 2:** operator hierarchy / motivation.
- **Figure 3:** **central validation figure — equal-search benchmark test + prospective fresh-perturbation risk stratification.**
- **Figure 4:** order-preserving control versus QSQ perturbation validation.
- **Figure 5:** Bader basin-migration mechanism; implementation transfer remains supporting evidence rather than a second headline.
- **Figure 6:** nominal-vs-realized distortion confounding control.
- **Figure 7:** Fourier-spectrum mechanism audit of matched ZFP/SZ3 Hartree pairs.
- **Figure 8:** untouched external confirmation.

## Current research scope

**The submission scope has been re-frozen after the author-authorized QoI-generality extension.** P0–P4 remain unchanged; P3B new-DFT grid convergence remains deferred and P5 remains NO-GO. The Fourier-spectrum Hartree mechanism remains the operator-specific mechanism line. The pre-declared WP-A–WP-D extension package has now been adjudicated under `paper/QOI_GENERALITY_SCOPE_ADDENDUM_20260930.md`: WP-B enters the main scientific story as a second topology-sensitive QoI; WP-C supports probe-family robustness; WP-A and WP-D are explicitly Discussion-only interpretive evidence and do not define new Results, Methods, Abstract claims or main figures.

The validation hierarchy remains **P1 equal-search control → P2 prospective fresh-perturbation validation → P3A independent on-grid implementation transfer**, with P4 as a secondary measurement-contract boundary/null case. The Fourier audit is mechanistic support for codec-error structure and operator weighting; it does not replace QSQ as the central contribution or alter any primary QSQ cohort, threshold or perturbation definition.

No further scientific endpoint, perturbation family, primary cohort, DFT convergence experiment or primary threshold should be added before submission without another explicit scope-reopening addendum. The current eight-figure main-text architecture remains unchanged; the second-QoI generality result is integrated as a compact Results subsection with detailed supporting evidence in the SI. Remaining work is claim-evidence synchronization, figure/SI assembly, archival DOI, journal-specific formatting and final Word/PDF generation.

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

The canonical contribution is **validated QoI stability qualification before scientifically interpreting benchmark scoring**, with explicit reporting of the qualification model and its limits. The Fourier audit strengthens the supporting physical logic: after reference stability and scalar realized distortion are controlled, downstream error can still depend strongly on how codec reconstruction error is distributed relative to the downstream operator.

## Naming boundary

Reader-facing text uses only **QoI Stability Qualification (QSQ)**, **QSQ stability floor**, **QSQ eligibility**, **stability probe**, **measurement contract**, and **order-preserving control**. There is no reader-facing distinction such as “upgraded QSQ”, “QSQ 2.0” or “contract-aware QSQ”: the complete measurement-contract definition is the canonical QSQ definition. Exact implementation filenames and development history remain only in provenance.
