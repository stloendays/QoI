# Chemical Fidelity beyond Pointwise Error Bounds: Stability and Bader-Domain Migration in Lossy-Compressed Electron Densities

**JCTC Article submission draft v0.1 — 2026-09-06**

## Abstract

Reliable reuse of compressed electronic-structure data requires a fidelity criterion at the level of the downstream analysis, not only the stored field. We establish such a criterion for Bader charges computed from density-functional-theory electron densities. Across 6,343 successful reconstructions of 254 materials compressed with SZ3, ZFP, and SPERR, re-deriving the Bader partition after decompression yields larger charge errors than integrating over reference basins in 99.7% of 4,627 base-ladder cases. In a representative 12-material mechanism set, direct decomposition gives a median bounded domain-migration contribution of 0.995. Equal requested tolerances are also not equal perturbations: ZFP realizes a median 0.158 of its requested L-infinity bound, whereas SZ3 and SPERR nearly saturate theirs. Nevertheless, after matching realized L-infinity error and restricting to systems whose Bader charges are numerically resolvable to 10^-3 e, conservative complete-case comparisons retain 1.82-fold and 2.00-fold Bader-error ratios for SZ3/ZFP and SPERR/ZFP, respectively. These residuals collapse after accounting for basin reassignment but not global electron-count deviation. A calibrated five-seed stability protocol further finds 41.4% of 319 systems non-evaluable at 10^-3 e and 79.9% at 10^-4 e. The resulting workflow measures realized field error, re-executes field-dependent partitioning, and certifies downstream fidelity only where the chemical observable is numerically resolvable.

## Introduction

Real-space electron-density fields are central intermediates in electronic-structure workflows: they support charge partitioning, bonding analysis, visualization, archival reuse, and increasingly data-driven post-processing. For high-throughput density-functional-theory calculations, retaining such volumetric fields can impose substantial storage and I/O costs even when the underlying wavefunction calculation is no longer needed. Error-bounded lossy compression offers a natural remedy by trading controlled numerical distortion for reduced data volume. General-purpose compressors such as ZFP, SZ3, and SPERR expose explicit pointwise-error controls [1–3], but the chemical meaning of those controls depends on how downstream observables respond to the reconstructed field.

The scientist, however, rarely makes decisions from individual field values. Scientific conclusions are typically drawn from quantities of interest (QoIs): integrated observables, extrema, interfaces, critical points, segmentations, transport coefficients, atomic charges or other outputs of a post-processing pipeline. Prior work has already established that raw-data error control and downstream-QoI fidelity are distinct problems. QoI-preserving compression can derive guarantees for selected downstream operators [4], while topology-aware methods preserve extrema, contour trees, Morse–Smale structures or local order that pointwise bounds alone do not protect [5–9]. More recent frameworks explicitly model spatial compression-error correlation or allow scientists to explore task-specific compression–QoI trade-offs [10,11]. The question is therefore no longer whether downstream structure can matter in principle, but how to define and validate the appropriate scientific contract for a particular analysis.

Electron density provides a stringent test because chemically meaningful observables can depend on domains that are themselves derived from the field. In Bader's atoms-in-molecules construction, space is partitioned into atomic basins separated by zero-flux surfaces and atomic charges are obtained by integrating the electron density over those basins [12,13]. Grid-based implementations assign field points to atomic regions by following local ascent relations [13]. Compression can therefore alter a Bader charge through two channels: density values can change inside an otherwise fixed basin, and the basin assignment itself can change. The second contribution is a domain error. If an evaluation reuses the original basins when scoring a reconstructed density, it suppresses this channel by construction and no longer reproduces the analysis that would be performed on the decompressed field.

Recent work on machine-learned electron densities has independently highlighted a downstream-fidelity gap caused by real-space integration and grid discretization, and has addressed that problem through adaptive real-space integration [15]. The present setting is complementary but distinct: the electron density is a controlled lossy reconstruction of an existing electronic-structure field, and the dominant error channel studied here arises because the integration domains themselves are re-derived from that perturbed field. This distinction makes the partitioning operation part of the fidelity contract rather than a fixed numerical quadrature step.

A second issue arises even before compression is evaluated. A QoI can function as an accuracy contract only if the reference analysis is numerically resolvable at the requested scale. If chemically negligible numerical perturbations change the Bader assignment by more than the proposed threshold, it is not meaningful to certify a codec against that threshold. Moreover, the perturbation used to measure stability must itself be validated. A probe that accidentally preserves the discrete structure on which a downstream algorithm depends can report false robustness.

Here we develop a stability-qualified evaluation protocol for lossy-compressed electronic-structure fields with three explicit layers: field reconstruction, chemical-observable resolvability, and downstream fidelity. We benchmark SZ3, ZFP, and SPERR on 254 DFT electron-density fields spanning bulk and slab systems; re-run Bader partitioning on every reconstruction; measure realized L-infinity error rather than treating equal requested tolerance as equal perturbation; and qualify each material against a calibrated five-seed stability protocol before certification. Direct error decomposition and full-benchmark basin-reassignment statistics then identify how reconstruction differences propagate into charge error. The objective is not a universal codec ranking, but a computational-chemistry contract for deciding when compressed electron densities remain valid inputs to a field-dependent analysis.

## Results

### 1. The benchmark separates field reconstruction from downstream chemical fidelity

The released master table contains 6,343 successful compressed reconstructions of 254 development materials: 4,627 rows on the base tolerance ladder and 1,716 rows on a tighter ladder. Each row records the requested error tolerance, measured `realized_Linf`, compression ratio, fixed-basin Bader error, Bader error after re-deriving the partition, voxel reassignment and Protocol-A.1 eligibility. Exceptional downstream cases are retained separately in a 77-row registry rather than silently discarded; 76 are Bader-solver failures and one is a symmetry-equivalent basin-relabeling event.

The primary chemical-fidelity error is

\[
\Delta Q_{\mathrm{resolved}} = \max_a \left|Q_a[\tilde\rho,\mathcal B(\tilde\rho)]-Q_a[\rho,\mathcal B(\rho)]\right|,
\]

where \(\rho\) is the original density, \(\tilde\rho\) the reconstruction and \(\mathcal B(\rho)\) the Bader partition derived from its argument. The diagnostic fixed-basin error instead evaluates the reconstruction on the original partition,

\[
\Delta Q_{\mathrm{fixed}} = \max_a \left|Q_a[\tilde\rho,\mathcal B(\rho)]-Q_a[\rho,\mathcal B(\rho)]\right|.
\]

The distinction is not cosmetic. Across all 4,627 successful base-ladder rows, the re-derived error exceeds the fixed-basin error in 99.7% of cases (Fig. 2a). The pooled median ratio is 52.8, but the factor is not universal: at the core nominal tolerances it ranges from about 1.7 for SZ3 at 10^-2 to more than 200 for ZFP at 10^-4 (Fig. 2b). The denominator-robust conclusion is therefore directional rather than a single multiplicative constant: reusing the original partition almost always understates the Bader error and can do so by orders of magnitude.

This full-corpus result also corrects an early pilot interpretation. A ten-material pilot suggested that fixed- versus re-derived scoring could reverse the identity of the best codec. The full benchmark falsifies that ranking-reversal claim: ZFP is generally the best of the tested codecs under both metrics. The robust finding is instead that fixed-domain scoring hides the dominant error channel and should be treated as a diagnostic rather than as a chemical fidelity metric.

### 2. Movement of the Bader domains dominates the representative mechanism set

For an atomic basin \(\Omega_a\), the charge perturbation can be decomposed as

\[
\Delta Q_a = \Delta Q_{a,\mathrm{integrand}} + \Delta Q_{a,\mathrm{domain}},
\]

where the first term describes the effect of perturbing density values while retaining the reference domain and the second describes the effect of changing the integration domain. We evaluated this decomposition for a representative mechanism set of 12 materials spanning the measured stability range, three codecs and three compression tolerances. The current summary contains 106 successful material–codec–tolerance cases. At the maximum-error atom, the decomposition closes to within \(2.22\times10^{-16}\) e.

Cancellation can make \(|\Delta Q_{\mathrm{domain}}|/|\Delta Q_{\mathrm{total}}|\) exceed one, so dominance is summarized using the bounded quantity

\[
f_{\mathrm{domain}} = \frac{|\Delta Q_{\mathrm{domain}}|}{|\Delta Q_{\mathrm{domain}}|+|\Delta Q_{\mathrm{integrand}}|}.
\]

The median bounded domain contribution is 0.995, with an interquartile range of 0.965–0.999; 84.9% of cases exceed 0.90. Within this representative set, compression-induced Bader error is therefore predominantly associated with movement of the integration domain rather than with integrating a slightly perturbed density over an unchanged atom (Fig. 3a). We deliberately restrict this direct decomposition claim to the representative mechanism set until the full per-atom table is complete.

### 3. Equal nominal tolerance conflates bound utilization with error structure

Every successful reconstruction respects its requested pointwise error bound, but the codecs use that bound differently. The median ratio

\[
\frac{L_{\infty,\mathrm{realized}}}{L_{\infty,\mathrm{nominal}}}
\]

is 0.1575 for ZFP and approximately 1.000 for both SZ3 and SPERR (Fig. 5a). Thus, a same-nominal comparison gives ZFP a substantially smaller realized field perturbation. The large Bader-error differences at equal requested tolerance cannot therefore be interpreted as pure evidence of spatial error structure.

We separated the two effects by matching codec operating points within each material by measured, rather than requested, L∞ error. The preregistered Protocol-A.1-qualified analysis at \(\tau=10^{-3}\) e gives SZ3/ZFP = 1.90 [1.70, 2.20] and SPERR/ZFP = 1.87 [1.63, 2.08] when matches are required to fall within 0.10 decades in \(\log_{10}L_\infty\). SZ3 is worse in 91.4% of matched materials and SPERR in 79.8%. Material-fixed-effect models controlling measured L∞ give consistent approximately twofold codec-associated multipliers.

Because registered Bader failures are not uniformly distributed among codecs, we subjected the result to a conservative selective-survival test. At nominal relative tolerance <=0.01 there are 24 registered failures across 20 materials, including 20 ZFP cases and four SPERR cases. We removed the entire material whenever any codec failed, reducing the development set from 254 to 234 materials. At the 10^-3 e contract, the matched ratios remain 1.82 [1.68, 2.01] for SZ3/ZFP and 2.00 [1.79, 2.25] for SPERR/ZFP (Fig. 5b). Replacing nearest-neighbour matching with within-material log–log interpolation on common measured-L∞ support gives 2.07 [1.95, 2.19] and 1.99 [1.83, 2.21]. The approximately twofold residual is therefore not explained by nominal-bound utilization, the matching rule or selective survival of successful rows.

These analyses establish an association rather than a causal codec effect. Codec identity is a proxy for the reconstruction patterns produced by distinct algorithms. The mechanism connecting that residual to the downstream observable is examined directly through basin reassignment.

### 4. Basin reassignment statistically accounts for the codec-associated residual

The direct 12-material decomposition identifies domain migration in representative cases, but a separate question is whether changes in Bader assignment explain the codec-associated pattern across the full benchmark. We fitted material-fixed-effect models at the 10^-3 e A.1 contract on common realized-L∞ support. The base model predicts log re-derived Bader error from measured L∞, codec and material identity. An expanded model additionally includes the fraction of voxels whose Bader label changes after compression.

In the conservative complete-case analysis, the base model gives codec multipliers of 2.34 for SZ3 relative to ZFP and 2.08 for SPERR relative to ZFP. After adding the reassigned-voxel fraction, these multipliers attenuate to 0.96 and 0.94, respectively (Fig. 5c). The reassignment term has a log–log coefficient of 0.880 [0.723, 1.037] with \(p=5.78\times10^{-28}\). Thus, after material identity and measured pointwise magnitude are controlled, the variable that directly records movement of the field-derived partition statistically absorbs nearly all of the approximately twofold codec-associated residual.

We interpret this result as mechanism-consistent attenuation, not as formal causal mediation. Basin reassignment is a post-compression variable and is not randomized, and a voxel count does not encode which atoms exchange volume or how much electron density those voxels carry. The direct algebraic decomposition remains the primary mechanistic evidence. The attenuation result provides independent full-benchmark support for the same failure mode.

A global conservation proxy does not provide an alternative explanation for this attenuation. We added the absolute total electron-count deviation to the same complete-case material-fixed-effect model. This leaves the SZ3/ZFP multiplier essentially unabated (2.34 to 2.58) and the SPERR/ZFP multiplier unchanged (2.08 to 2.06), whereas adding basin reassignment reduces them to 0.96 and 0.94. When both post-compression covariates are included, the electron-count term is not significant (log–log coefficient −0.017, 95% CI −0.040 to 0.006; p=0.139), while the reassignment coefficient remains 0.879 [0.722, 1.036] (p=5.25×10^-28). Thus the codec-associated residual is not explained by simple global integral/conservation error; the structural variable that records redistribution among Bader domains is the one that absorbs the residual (Supplementary Fig. S13).

### 5. Bader charge has a protocol-defined numerical resolvability limit

A codec should be scored against a Bader-charge threshold \(\tau\) only if the uncompressed system supports a Bader result stable at that scale. Protocol A.1 defines a material-specific numerical stability floor by adding uniform noise \(U(-\epsilon_i,+\epsilon_i)\), where \(\epsilon_i\) is that material's float32-round-trip L∞ amplitude, re-deriving the Bader partition for five preregistered random seeds, and taking the maximum atom-wise charge deviation. A material is eligible only if this floor is below \(\tau\).

The eligibility loss is substantial. Across 319 systems, 255 (79.9%) are non-evaluable at \(10^{-4}\) e, 132 (41.4%) at \(10^{-3}\) e and 31 (9.7%) at \(10^{-2}\) e (Fig. 4a). These cases are not codec failures. They are reported as `NON_EVALUABLE_BADER_UNSTABLE` and removed from pass/fail certification at that contract.

One external material, `aflow-Al8Cu4U1_ICSD_601801`, has an extreme apparent floor caused by permutation of symmetry-equivalent Al basins rather than a change in the multiset of charges. Protocol A.1 remains frozen and therefore retains the position-indexed classification, but we report the case separately in the failure taxonomy. Removing this one known relabeling event changes the overall non-evaluable fractions only from 79.94% to 79.87%, 41.38% to 41.19% and 9.72% to 9.43% across the three contracts. The main resolvability conclusion is therefore not driven by the symmetry-labeling pathology.

### 6. The stability probe must perturb the mathematical structure used by the QoI algorithm

Protocol A.1 replaced, rather than silently edited, an earlier frozen stability probe. Protocol A used a deterministic float64→float32→float64 round trip. Rounding is monotone for unequal values and can preserve local order while creating exact ties. This is an unusually benign perturbation for an on-grid watershed whose assignments follow local ascent relations.

We validated the replacement before freezing A.1. In an 18-material calibration study, the archived float32 probe creates a median 82 exact neighboring ties, whereas matched-amplitude random noise creates none. Zero voxel reassignment occurs in 9/18 systems under the float32 probe but only 2/18 under random noise. At matched amplitude, the calibrated random-noise stability floor is a median 29-fold larger than the archived float32 result (Fig. 4b,c). The floor also varies across seeds: the within-material log10 range has a median 0.47 decades and reaches 2.39 decades. Protocol A.1 therefore uses five preregistered seeds and takes the maximum response.

The floor is not an intrinsic material constant. Changing probe amplitude from 0.1x to 10x shifts the floor by a median 0.76 decades. We therefore refer to it throughout as a **Protocol-A.1 numerical stability floor at the stated perturbation amplitude**, rather than as an amplitude-free property of Bader charge.

### 7. Conventional metadata do not generalize as predictors of Bader resolvability

If eligibility could be predicted accurately from cheap descriptors, explicit stability measurement might be avoidable. We tested descriptors available before compression, including system type, grid size, atom count, points per atom and available vacuum/cell information. Logistic models show modest development-set signal at the strict contracts, but it fails to transfer to the untouched external strata.

External AUROC is 0.409 at \(10^{-4}\) e, 0.387 at \(10^{-3}\) e and 0.398 at \(10^{-2}\) e (Fig. 4d). Excluding the known symmetry-equivalent relabeling case changes these values only marginally. These results do not establish that Bader resolvability is fundamentally unpredictable from all possible representations. They show that conventional low-cost metadata do not generalize well enough to replace direct stability qualification across the tested corpora.

### 8. The certified compression frontier is contract-dependent

After stability qualification, practical compressor selection is a joint problem in compression ratio and certification coverage rather than a single ranking. At \(\tau=10^{-2}\) e for bulk systems, SZ3 reaches a median best certified ratio of 51.8x with 95.2% certification among admitted rows, while ZFP reaches 30.0x with 98.8% certification. On slabs, the trade-off is sharper: SZ3 reaches 67.8x but certifies 77.0%, whereas ZFP reaches 40.5x and certifies 96.7% (Fig. 6).

As the chemical contract tightens, the ordering changes. At \(10^{-3}\) e, bulk medians are 12.9x for SZ3 and 13.5x for ZFP, with both near 99% certification in the best-certified table; on slabs, ZFP reaches 15.3x with 100% coverage while SZ3 reaches 14.1x with 85% coverage. At \(10^{-4}\) e, ZFP leads the bulk ratio at 7.6x compared with 6.3x for SZ3 and 4.2x for SPERR. Only four slab materials are admitted at this strictest contract, so the slab frontier is treated descriptively rather than as a population-level ranking.

The engineering conclusion is not that one codec is universally superior. The optimal operating point depends on the downstream charge contract and the desired certification coverage. A codec that is attractive at a loose scientific tolerance can lose that advantage as the downstream requirement tightens.

## Discussion

### Scientific fidelity requires a contract at the level of the analysis

The results separate three quantities that are often collapsed into a single notion of compression accuracy. A nominal codec tolerance is not the same as the error a codec realizes. A realized pointwise error magnitude is not sufficient to determine a field-derived downstream error. And the downstream quantity itself may not be numerically stable at the requested threshold. A pointwise bound therefore remains useful information about the reconstructed field, but it is not by itself a scientific fidelity guarantee.

The central evaluation principle is simple: **if the downstream analysis derives its own domains, labels or topology from the reconstructed field, that analysis must be re-executed during validation.** Reusing the original partition can make the reported QoI artificially stable by construction. Bader charge provides a chemically meaningful example because basin reassignment is not a secondary perturbation; in the representative direct decomposition it is the dominant measured contribution, and across the full benchmark it accounts statistically for the codec-associated residual after pointwise magnitude is controlled.

### The approximately twofold residual has a mechanistic interpretation

Measuring realized L∞ materially changes the codec story. ZFP's strong same-nominal performance is partly mechanical: it uses only about one sixth of its requested pointwise budget. Matching actual perturbation size reduces the apparent codec gap substantially. That reduction is scientifically useful because it separates a bound-utilization effect from a residual associated with codec-specific reconstruction patterns.

The remaining difference is robust across matching windows, interpolation on common support, stability qualification and conservative removal of failure-affected materials. More importantly, it almost disappears when basin reassignment is included in the material-controlled model. We therefore interpret the approximately twofold residual not as an intrinsic property of the codec label, but as evidence that different reconstruction patterns perturb the ascent relations defining Bader domains to different extents. Consistent with this interpretation, a global electron-count deviation does not attenuate the codec-associated residual once measured L∞ and material identity are controlled, whereas basin reassignment does.

This interpretation connects naturally with recent compression research that explicitly preserves topology or local order [5–9]. TopoSZ preserves extrema and contour-tree relations [5]; later methods can correct or preserve Morse–Smale structures [7,8]; and a 2026 compressor explicitly preserves critical points and local order [9]. These works do not make the present evaluation redundant. Instead, they supply algorithmic directions that are unusually well matched to the failure mode exposed here. Testing whether such guarantees reduce Bader domain migration is a logical next step for the released benchmark.

### QoI-aware compression is a growing field, so the novelty is the chemical contract rather than the generic premise

Prior work already derives QoI-specific compression guarantees [4], predicts QoI-level uncertainty from compression metadata while modeling spatial error correlation [10], and provides interactive QoI-aware compressor-selection workflows [11]. The present contribution is therefore not the generic statement that downstream quantities matter. Its distinctive elements are the combination of a field-derived integration domain, an explicit domain-migration decomposition, a stability-qualified eligibility layer, validation of the stability probe against algorithmically relevant structure, and separation of nominal error-budget utilization from residual reconstruction structure.

This positioning also clarifies why the primary benchmark uses general-purpose SZ3, ZFP and SPERR rather than attempting to rank every topology-aware codec. The study asks whether the guarantees exposed by widely used pointwise-error-bounded compressors are sufficient for a chemical QoI and defines the evaluation protocol needed to answer that question. Topology- and local-order-preserving compressors optimize a different guarantee. They are compelling follow-up baselines, but the validity of the evaluation result does not require turning the study into a broad codec bake-off.

### Stability qualification changes the semantics of failure

`NON_EVALUABLE_BADER_UNSTABLE` is intentionally neither a pass nor a codec failure. Treating an unstable reference as a codec failure would penalize the compressor for a precision the downstream calculation cannot reliably define; ignoring instability would create false precision. The eligibility layer separates these semantics explicitly.

The transition from Protocol A to A.1 is also part of the methodological result. The original protocol was kept as an archive after its blind spot was identified. A replacement probe was calibrated, seed-tested and amplitude-tested, and all probe-dependent headline statistics were recomputed under a dated protocol version. This record illustrates a broader principle: a perturbation used to assess numerical stability must be capable of disturbing the mathematical structure on which the downstream analysis depends. Small amplitude alone is not sufficient.

## Limitations

Bader charge is a demanding exemplar, not a claim about all scientific QoIs. Smooth algebraic functionals may admit substantially tighter relationships between field norms and downstream error, whereas partition-, threshold- or topology-dependent observables can respond discontinuously to local perturbations. Applying the same eligibility and re-derivation framework to additional electronic-structure quantities would test which aspects generalize beyond Bader analysis.

The direct algebraic decomposition currently covers a representative 12-material mechanism set rather than all 254 benchmark materials. Full-benchmark reassignment attenuation strongly triangulates the same failure mode, but it is not equivalent to a per-atom decomposition for every material. The per-atom mechanism table is therefore analyzed with material-level rather than atom-level inference once available; atoms are nested observations, not independent replicates.

The three compressors represent important general-purpose algorithmic families but are not exhaustive. In particular, recent local-order-, feature- and topology-preserving methods may better protect the discrete structures relevant to Bader analysis. Their omission from the primary benchmark limits codec-comparison scope but not the central conclusion that pointwise magnitude alone is an incomplete chemical fidelity contract.

Protocol A.1 is deliberately operational. Its stability floor depends on the chosen perturbation family, the float32-scale amplitude and the five-seed maximum. It should not be interpreted as an intrinsic constant of a material. Different downstream algorithms may require different probes and stability amplitudes.

Finally, the Bader solver itself fails on some highly distorted reconstructions. The failure registry is codec- and tolerance-dependent. Complete-case sensitivity demonstrates that these missing successful rows do not explain the matched-L∞ result, but all manuscript denominators must continue to distinguish attempted cases, successful downstream evaluations, eligible systems and certified systems.

## Methods

### Data, provenance and benchmark strata

The development compression benchmark contains 254 charge-density fields: 186 bulk materials and 68 slab systems. The stability analysis adds a strict external corpus of 37 AFLOW bulk systems and 28 NOMAD two-dimensional/vacuum-containing systems, giving 319 systems in total. Source URLs, byte counts, hashes, licenses, formulas, grid sizes and atom counts are recorded in `materials_metadata.csv` and `external_test_MANIFEST.json`. No new DFT calculation was required for the released benchmark.

### Compressors and error ladders

SZ3 was evaluated through `pysz` 1.0.3 in absolute `INTERP_LORENZO` mode, ZFP through `zfpy` 1.0.1 in fixed-accuracy mode, and SPERR through `hdf5plugin` 7.0.0 in absolute single-chunk mode. Compression ratio is reported relative to the float64 field payload.

The base ladder spans relative requested tolerances from 10^-5 to 10^-1, converted to absolute bounds using each field's peak-to-peak range. Runs are early-stopped after the re-derived Bader error reaches 0.05 e. A tight ladder at 10^-7, 3×10^-7, 10^-6 and 3×10^-6 was added for Protocol-A.1-eligible materials to resolve the strict-accuracy frontier. `realized_Linf` is measured directly for every successful reconstruction. All 6,343 successful rows respect their requested pointwise bound.

### Bader analysis and fidelity metrics

Bader partitions were computed with `baderkit` 0.10.2 using `method="ongrid"`. The primary downstream error is the maximum absolute per-atom charge difference after re-deriving the Bader partition from the reconstructed density. The reconstructed density is also integrated over the original basins to obtain a fixed-domain diagnostic. `n_voxels_reassigned` and `frac_voxels_reassigned` record changes in Bader labels between the reference and reconstructed partitions.

### Protocol A.1 stability qualification

For material \(i\), let

\[
\epsilon_i=\|\mathrm{float32}(\rho_i)-\rho_i\|_\infty.
\]

Protocol A.1 generates five additive uniform perturbations \(U_s(-\epsilon_i,+\epsilon_i)\) using preregistered seeds {20260905, 1, 2, 3, 4}. The Bader partition is re-derived for every perturbation. The material's stability floor is the maximum atom-wise Bader-charge deviation over the five seeds. The evaluated chemical contracts are \(\tau\in\{10^{-4},10^{-3},10^{-2}\}\) e. A material is eligible when its A.1 floor is below \(\tau\); otherwise it is reported as `NON_EVALUABLE_BADER_UNSTABLE` and is not assigned a codec pass/fail at that contract.

Protocol A, which used a deterministic float32 round trip as the perturbation, remains archived unchanged. Protocol A.1 changed the probe and seed aggregation while retaining the threshold set, exclusion semantics and reporting rules.

### Probe calibration

Before Protocol A.1 was frozen, the replacement probe was calibrated on 18 materials stratified across corpus and preliminary stability. Five random seeds were tested at the reference amplitude; the primary seed was additionally evaluated at 0.1x and 10x amplitude. Calibration endpoints include Bader floor, exact-neighbour ties, voxel reassignments and local axis-order flips. The five-seed maximum was selected as a conservative aggregation because single-seed floors varied materially across the calibration set.

### Direct basin-error decomposition

For representative cases, the per-atom charge difference is decomposed into a fixed-domain integrand term and a domain-migration term such that

\[
\Delta Q_{\mathrm{total}}=\Delta Q_{\mathrm{integrand}}+\Delta Q_{\mathrm{domain}}.
\]

The current summary reports the decomposition at the atom of largest total error for 12 stability-stratified materials, three codecs and three tolerances. The bounded dominance fraction \(|\Delta Q_{\mathrm{domain}}|/(|\Delta Q_{\mathrm{domain}}|+|\Delta Q_{\mathrm{integrand}}|)\) is used because cancellation can make \(|\Delta Q_{\mathrm{domain}}|/|\Delta Q_{\mathrm{total}}|>1\).

### Realized-L∞ matching

For each material and codec pair, operating points are compared by measured rather than requested L∞ error. The primary nonparametric procedure identifies mutual nearest neighbours in \(\log_{10}(\mathrm{realized}\ L_\infty)\) and retains pairs separated by at most 0.10 decades. Ratios are first summarized within material and then across materials. Uncertainty is obtained by material-level bootstrap resampling. Protocol-A.1-qualified analyses restrict the material set by eligibility at the stated Bader-charge contract before matching.

Sensitivity analyses use alternate calipers and a within-material interpolation procedure that evaluates each codec on common log–log measured-L∞ support. To address selective censoring by downstream failures, a complete-case analysis removes an entire material if any codec has any registered failure at nominal relative tolerance <=0.01. This removes 20 materials and leaves 234 development materials.

### Material-fixed-effect and mechanism-attenuation models

The response is \(\log_{10}\Delta Q_{\mathrm{resolved}}\). Base models include material fixed effects, centered \(\log_{10}L_\infty\) and codec indicators; standard errors are clustered by material. Mechanism-consistency models additionally include the reassigned-voxel fraction with a grid-scaled half-voxel pseudocount for zero-reassignment cases. The change in codec coefficients after adding reassignment is interpreted as attenuation evidence and not as a causal mediation estimate.

### Resolvability prediction audit

To test whether explicit stability measurement can be replaced by conventional metadata, logistic models use available low-cost descriptors including system type, grid size, atom count, points per atom and available vacuum/cell descriptors. Models are evaluated by stratified fivefold cross-validation on development systems and then applied without refitting to the untouched external strata. AUROC, balanced accuracy and Brier score are recorded. A symmetry-aware sensitivity excludes the single registered symmetry-equivalent relabeling case from the external evaluation without changing the frozen primary A.1 eligibility table.

### Compression-certification frontier

For each eligible material, codec and Bader contract, the best compression ratio among rows satisfying `Bader_error_resolved_e < tau` is recorded. Results are summarized by system type and codec as median best certified ratio and the fraction of admitted rows with a certified operating point. `NON_EVALUABLE_BADER_UNSTABLE` is not treated as a codec failure.

## Data and Software Availability

The benchmark data, Protocol A.1 stability measurements, failure registry, provenance metadata, mechanism data used in the manuscript, supplementary sensitivity tables, and statistical analysis scripts are maintained in the project repository at https://github.com/stloendays/QoI. A versioned archival release with a persistent identifier will be frozen before formal submission so that the published record maps to an immutable data-and-software snapshot. Source URLs, checksums, and licensing metadata for the underlying material fields are recorded in `materials_metadata.csv`.

## References

1. Diffenderfer, J., Fox, A. L., Hittinger, J. A. F., Sanders, G. & Lindstrom, P. G. Error Analysis of ZFP Compression for Floating-Point Data. *SIAM J. Sci. Comput.* **41**, A1867–A1898 (2019). DOI: 10.1137/18M1168832.
2. Liang, X., Zhao, K., Di, S., Li, S., Underwood, R., Gok, A. M., Tian, J., Deng, J., Calhoun, J. C., Tao, D., Chen, Z. & Cappello, F. SZ3: A Modular Framework for Composing Prediction-Based Error-Bounded Lossy Compressors. *IEEE Trans. Big Data* **9**, 485–498 (2023). DOI: 10.1109/TBDATA.2022.3201176.
3. Li, S., Lindstrom, P. & Clyne, J. Lossy Scientific Data Compression With SPERR. In *2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*, 1007–1017 (IEEE, 2023). DOI: 10.1109/IPDPS54959.2023.00104.
4. Jiao, P., Di, S., Guo, H., Zhao, K., Tian, J., Tao, D., Liang, X. & Cappello, F. Toward Quantity-of-Interest Preserving Lossy Compression for Scientific Data. *Proc. VLDB Endow.* **16**, 697–710 (2022/2023). DOI: 10.14778/3574245.3574255.
5. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving Topology in Error-Bounded Lossy Compression. *IEEE Trans. Vis. Comput. Graph.* **30**, 1302–1312 (2024). DOI: 10.1109/TVCG.2023.3326920.
6. Gorski, N., Liang, X., Guo, H., Yan, L. & Wang, B. A General Framework for Augmenting Lossy Compressors With Topological Guarantees. *IEEE Trans. Vis. Comput. Graph.* **31**, 3693–3705 (2025). DOI: 10.1109/TVCG.2025.3567054.
7. Li, Y., Xia, M., Liang, X., Wang, B. & Guo, H. Preserving Discrete Morse–Smale Complexes in Error-Bounded Lossy Compression. *IEEE Trans. Vis. Comput. Graph.* **32**, 6593–6609 (2026). DOI: 10.1109/TVCG.2026.3684385.
8. Li, Y.; Xia, M.; Liang, X.; Wang, B.; Underwood, R.; Di, S.; Sharma, H.; Beniwal, D.; Cappello, F.; Guo, H. pMSz: A Distributed Parallel Algorithm for Correcting Extrema and Morse-Smale Segmentations in Lossy Compression. In *2026 IEEE International Parallel and Distributed Processing Symposium (IPDPS)* (2026). DOI: 10.1109/IPDPS65963.2026.00025.
9. Fallin, A., Gorski, N., Agarwal, T., Wang, B., Gopalakrishnan, G. & Burtscher, M. Fast Topology-Aware Lossy Data Compression with Full Preservation of Critical Points and Local Order. *IEEE Trans. Big Data* (2026). DOI: 10.1109/TBDATA.2026.3705355.
10. Liu, Y.; Jiang, B.; Yang, T.; Di, S.; Underwood, R.; Jin, S. TOPIQ: Statistical Error Propagation for Quantity-of-Interest Prediction under Lossy Compression. Accepted at *SC 2026*; arXiv:2608.26912 (2026). DOI: 10.48550/arXiv.2608.26912.
11. Liu, G.; Li, Y.; Ren, C.; Underwood, R.; Liang, X.; Wang, B.; Di, S.; Cappello, F.; Guo, H. FZ-VIS: A Visual Analytics Framework for Quantities-of-Interest-Aware Scientific Lossy Compression. Accepted at *IEEE VIS 2026 / IEEE Trans. Vis. Comput. Graph.*; arXiv:2608.08386 (2026). DOI: 10.48550/arXiv.2608.08386.
12. Bader, R. F. W. *Atoms in Molecules: A Quantum Theory*. Oxford University Press (1990).
13. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. *Comput. Mater. Sci.* **36**, 354–360 (2006). DOI: 10.1016/j.commatsci.2005.04.010.
14. Brehm, M. & Thomas, M. An Efficient Lossless Compression Algorithm for Trajectories of Atom Positions and Volumetric Data. *J. Chem. Inf. Model.* **58**, 2092–2107 (2018). DOI: 10.1021/acs.jcim.8b00501.
15. Gong, J.; Zhao, Z.; Tang, B. Z. Bridging Machine Learning and Electron Density Theory with Adaptive Real-Space Integration. *J. Chem. Theory Comput.* (2026). DOI: 10.1021/acs.jctc.6c01124.
