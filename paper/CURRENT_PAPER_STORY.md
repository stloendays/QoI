# Current paper story — 2026-10-05

**Active title:** *Numerical stability qualification and operator-aware compression of electronic densities*

## 2026-10-05 QOAC-H diagnosis-to-design integration

Governing record: `paper/QOAC_SCOPE_ADDENDUM_20261005.md`. This is an author-authorized scope reopening after the Hartree codec design, disjoint confirmation and full-population census completed.

- **Scientific transition:** the Hartree line no longer ends at Fourier diagnosis. The verified sequence is now `QSQ qualification -> matched-distortion Fourier diagnosis -> operator-derived error allocation -> QOAC-H -> decoded-field Hartree certification`.
- **Design law:** Hartree squared error weights reciprocal density error by $|G|^{-4}$; the frozen high-rate transform model therefore gives $\Delta_G\propto|G|^2$. The exponent 2 was frozen before QOAC-H outcomes and compared with operator-blind exponent 0.
- **Mechanism test:** 12/12 materials favor the operator-derived allocation at matched serialized storage; median Hartree-error ratio = **0.0767117**.
- **Disjoint confirmation:** 48/48 previously unseen materials favor QOAC-H over each material's best certified ZFP/SZ3/SPERR baseline at $10^{-6}$ Hartree relative RMSE; median CR ratio **15.016×**, bootstrap 95% CI **11.204–21.461**, bulk **11.203×**, slab **25.699×**, safe guardrail **48/48**.
- **Full development census:** 254 materials, 6,350 settings, 0 failures. At $10^{-6}$, **253/253 comparable wins**, median **12.463×**, P05 **4.459×**, minimum **2.444×**. Every comparable system favors QOAC-H across the six tested Hartree tolerances.
- **Novelty boundary:** generic QoI-aware compression, operator-aware error control and transform-domain bit allocation are established prior art. The differentiated contribution is the QSQ-qualified **diagnosis-to-design loop** in which the exact physical operator first explains the codec effect and then defines the compression distortion, followed by direct downstream recertification.
- **Figure architecture:** new Fig. 8 carries QOAC-H; the existing untouched external confirmation becomes reader-facing Fig. 9.

## 2026-10-03 workflow integration

Governing record: `paper/WORKFLOW_SCOPE_ADDENDUM_20261003.md`. No experiment added, no claim removed.

- **Organization:** qualification → certification → diagnosis (Fig. 1 redrawn accordingly). Five stated contributions
  close the Introduction: contract-level qualification; validation (equal search, prospective, implementation
  transfer, finite-panel admission bound); QoI-specific evaluability (grid-local extrema); per-operator diagnosis
  (Bader partition field, Hartree Fourier allocation); scientific-use decisions (frontier, certifying writer, P4,
  external cohort).
- **Outcome labels:** certified / not certified / non-evaluable, with reason codes `QOI_CERTIFIED`,
  `QOI_NOT_CERTIFIED`, `REFERENCE_NOT_RESOLVED`.
- **Certifying writer (Results + SI Note 17 + Supplementary Fig. S10):** 98.5% of oracle archive compression at
  1e-3 e (14.90× vs 15.13×), 0/143 misses, 16.7 vs 37.0 Bader solves per eligible material; sequential QSQ brings
  end-to-end cost to 10.3 solves per material.
- **Finite-panel admission bound (Methods + one Results sentence + SI Note 18):** P(admitted ∧ later probe ≥ τ)
  ≤ nⁿ/(n+1)ⁿ⁺¹ = 6.70% for n = 5 under exchangeable probes; observed 0.901% at 1e-3 e. Local recomputation:
  floor reproduced 252/254, eligibility 254/254; independent-stream panel 16.52% above the five-probe maximum
  (CI 14.74–18.39%, contains 1/6).
- **Positioning:** Compression Safeguards (Tyree et al. 2026) cited with Jiao et al. and TOPIQ; QSQ is a
  precondition for enforcing or predicting a QoI requirement.
- **Discussion:** what each outcome licenses (contract change, coarser decision, tolerance matching, codec search).

## One-sentence thesis

**Scientific compression should be scored only after the complete measurement contract is qualified at the requested tolerance; once that ruler is valid, the downstream operator can diagnose which reconstruction errors matter and can directly define where compression error should be allocated, with the decoded object recertified under the same scientific contract.**

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

- **Figure 1:** three-stage workflow (qualification → certification → diagnosis) with the three outcome labels.
- **Figure 2:** operator hierarchy / motivation.
- **Figure 3:** **central validation figure — per-material floor vs fresh risk (a), the finite-panel admission bound with every material on it (b), equal-search control (c), prospective risk at three thresholds (d).**
- **Figure 4:** order-preserving control versus QSQ perturbation validation.
- **Figure 5:** Bader basin-migration mechanism, with panel f for the all-electron-reference contract decomposition; implementation transfer remains supporting evidence rather than a second headline.
- **Figure 6:** nominal-vs-realized distortion confounding control.
- **Figure 7:** Fourier-spectrum mechanism audit of matched ZFP/SZ3 Hartree pairs.
- **Figure 8:** QOAC-H diagnosis-to-design: operator-derived allocation, mechanism ablation, 48-material disjoint confirmation and 254-material tolerance census.
- **Figure 9:** untouched external confirmation.

## Current research scope

**The submission scope was explicitly reopened and re-frozen on 2026-10-05 for QOAC-H.** The governing record is `paper/QOAC_SCOPE_ADDENDUM_20261005.md`.

P0–P4, the QSQ definition, primary Bader cohorts, perturbation model and thresholds remain unchanged. The new reader-facing scientific line is Hartree-specific and uses already completed evidence: the matched-distortion Fourier mechanism, prospective operator-derived quantizer, disjoint 48-material confirmation and 254-material development census. The qualification framework remains logically prior to codec scoring; QOAC-H does not replace QSQ.

The main-text architecture is now nine figures. No further new scientific endpoint, perturbation family, primary cohort, DFT convergence experiment or new operator-specific codec should be added before submission without another explicit author decision. Remaining work is Figure 8 construction, figure/caption/SI synchronization, reference-style regeneration, archival DOI, and final DOCX/PDF QA.

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

The canonical contribution is now **validated QoI stability qualification coupled to a diagnosis-to-design demonstration**: first establish whether a scientific tolerance is numerically resolvable, then use the downstream operator to diagnose and, for the Hartree control, actively allocate reconstruction error, and finally recertify the decoded field. The Hartree codec result is specific to that linear operator and does not transfer the $|G|^2$ law to Bader.

## Naming boundary

Reader-facing text uses **QoI Stability Qualification (QSQ)**, **QSQ stability floor**, **QSQ eligibility**, **stability probe**, **measurement contract**, and **order-preserving control**. The complete measurement-contract definition is the canonical QSQ definition. Exact implementation filenames and development history remain only in provenance.
