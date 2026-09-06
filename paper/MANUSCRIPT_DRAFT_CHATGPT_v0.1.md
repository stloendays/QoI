# Chemical Fidelity Is Not a Pointwise Error: Topology-Induced Failure Modes in Lossy Compression of Electronic Densities

**Manuscript draft v0.1 — 2026-09-06**  
Editorial/statistical draft on `analysis/chatgpt-postprocess-20260906`. The frozen `main` branch is unchanged. Numerical claims are drawn from the released tables plus the reproducible post-processing in `analysis_output/`. The full per-atom decomposition can replace the current summary-level mechanism panel when it is committed.

## Abstract

Error-bounded lossy compression is increasingly used to reduce the storage and I/O cost of scientific fields, but a bound on reconstructed field values is not, in general, a bound on a downstream scientific observable. We test this distinction for density-derived Bader charges using 6,343 compressed reconstructions of 254 density-functional-theory charge-density fields, three pointwise-error-bounded compressors (SZ3, ZFP and SPERR), and an independent 319-system stability corpus. A naive evaluation that integrates reconstructed densities over the original Bader basins suppresses the dominant source of chemical error: when the basins are re-derived from each reconstruction, the resolved error exceeds the fixed-basin estimate by more than an order of magnitude for most operating points. Error decomposition over 12 representative materials identifies migration of the field-derived integration domains as the dominant contribution, with a median bounded domain-dominance fraction of 0.995.

Codec differences are also not explained by nominal tolerance alone. ZFP realizes a median of only 0.158 of its requested pointwise error bound, whereas SZ3 and SPERR nearly saturate theirs. Nevertheless, after matching reconstructions within 0.10 decades of measured L-infinity error, SZ3 and SPERR still produce 1.81-fold and 1.72-fold larger median Bader-charge errors than ZFP. The effect survives stability qualification: among systems whose Bader charges are resolvable to 10^-3 e under a preregistered perturbation protocol, the matched ratios are 1.90 [1.70, 2.20] and 1.87 [1.63, 2.08], respectively. Material-fixed-effect models give consistent approximately twofold codec effects after controlling measured L-infinity error.

A second limitation arises before compression is considered: the quantity of interest itself is not numerically resolvable at every requested accuracy. Under a calibrated five-seed, non-monotone stability probe, 41.4% of 319 systems are non-evaluable at a 10^-3 e Bader-charge contract and 79.9% at 10^-4 e. Conventional descriptors do not predict this eligibility on untouched external data. Despite these constraints, lossy compression remains useful: the highest certifiable compression ratio depends strongly on the chemical contract, with SZ3 leading at 10^-2 e, ZFP and SZ3 becoming comparable near 10^-3 e, and ZFP leading at 10^-4 e. These results motivate a stability-qualified view of scientific compression in which the downstream analysis is re-executed, the realized rather than nominal field error is measured, and the quantity of interest is shown to be well-defined before fidelity is certified.

## Introduction

Large-scale simulations and instruments increasingly produce scientific fields faster than they can be economically stored, transferred or repeatedly analyzed. Error-bounded lossy compression addresses this pressure by allowing controlled numerical distortion in exchange for substantial reductions in data volume. Modern scientific compressors such as ZFP, SZ3 and SPERR provide modes that constrain pointwise reconstruction errors while exploiting different transform, prediction and quantization strategies [1–3]. Such guarantees are attractive because they are explicit, inexpensive to check and independent of the downstream application.

The scientific user, however, rarely cares about every field value equally. Decisions are based on quantities of interest (QoIs): integrated energies, extrema, interfaces, topological features, derived transport quantities, atomic charges and other outputs of post-processing pipelines. This gap between raw-data error and QoI error has motivated methods that directly preserve selected derived quantities [4] and topology-aware compressors that augment value-error control with constraints on topological structure [5]. These developments make a broader point: a small or bounded perturbation of the stored field is not sufficient evidence that the scientific interpretation of that field is preserved.

Electronic charge density provides a stringent test of this problem because many chemically meaningful observables are defined through structures derived from the density itself. In Bader's atoms-in-molecules construction, space is partitioned into atomic basins separated by zero-flux surfaces, and atomic charges are obtained by integrating the density over these basins [6–8]. Grid-based implementations assign field points to basins by following local ascent relations. Consequently, compression can alter a Bader charge in two conceptually distinct ways: it can perturb density values within a fixed basin, and it can change the basin assignment itself. The latter is a domain error. If the original basins are reused to score a reconstructed density, domain migration is suppressed by construction and the evaluation no longer represents the analysis a scientist would perform on the reconstructed field.

A second issue is more fundamental. A QoI can serve as an accuracy contract only if the QoI is numerically stable at the requested scale. If perturbations far below chemical relevance can change the Bader assignment by more than the proposed contract, a compressor cannot meaningfully be certified against that contract. Stability itself is also protocol-dependent: a perturbation probe can be accidentally aligned with invariances of the downstream algorithm and therefore report false robustness. In the present study, an initially frozen float32 round-trip probe was found to be order-preserving and unusually benign for an order-dependent on-grid watershed. We retained that protocol unchanged as an archived record, calibrated a non-monotone replacement probe, and froze Protocol A.1 before recomputing eligibility and headline statistics.

Here we develop an evaluation framework around these two requirements: **re-derive the QoI from the reconstruction, and qualify the QoI before using it as a fidelity contract**. We benchmark SZ3, ZFP and SPERR on 254 DFT charge-density fields across bulk and slab systems, supplement the original tolerance ladder with tighter operating points, and evaluate Bader charges after re-partitioning every reconstruction. We then separate two mechanisms that are conflated by comparisons at equal nominal tolerance: differences in how much of a pointwise error budget each codec actually uses, and residual differences associated with the spatial structure of the realized error. Finally, we test whether Bader resolvability can be predicted from conventional system descriptors and evaluate the practical compression–certification frontier.

The resulting picture is not that one compressor is universally superior. Instead, pointwise error, QoI stability, error geometry and downstream partition dynamics form distinct layers of the scientific fidelity problem. A compressor can respect its mathematical error bound and still perturb the scientific observable disproportionately; a QoI can also be too unstable to support the desired contract in the first place. Scientific compression therefore requires a contract defined at the level at which scientific conclusions are actually drawn.

## Results

### 1. Benchmark construction and an honest downstream metric

The released master table contains 6,343 successful compressed reconstructions of 254 development materials: 4,627 rows on the base tolerance ladder and 1,716 rows on a tighter ladder. Each row records the requested pointwise tolerance, measured L-infinity reconstruction error, compression ratio, fixed-basin Bader error, re-derived Bader error, voxel reassignment and Protocol-A.1 eligibility. Failed downstream solves are not silently discarded as passes; 77 exceptional records are kept in a separate failure registry, comprising 76 Bader-solver failures and one symmetry-equivalent basin-relabeling case.

The primary chemical error is

\[
\Delta Q_{\mathrm{resolved}} = \max_a \left| Q_a[\tilde\rho,\,\mathcal B(\tilde\rho)] - Q_a[\rho,\,\mathcal B(\rho)] \right|,
\]

where \(\rho\) and \(\tilde\rho\) are the original and reconstructed densities and \(\mathcal B\) denotes the Bader partition derived from its argument. The diagnostic fixed-basin error instead evaluates the reconstructed density on \(\mathcal B(\rho)\). This distinction is essential because the latter calculation prevents any basin migration from contributing to the reported error.

Across finite ratios in the complete base-ladder audit, the re-derived error is a median 52.8-fold larger than the fixed-basin estimate, with a 90th percentile of 738.8-fold; 96.5% of operating points exceed a twofold understatement. The exact headline factor depends on the analysis subset used for a given figure, but the direction is universal enough to change the interpretation of the benchmark. Fixed-basin scoring is therefore retained only as a diagnostic, not as a chemical-fidelity metric.

This correction also falsified an early pilot claim. In a ten-material subset, fixed-basin and re-derived scoring appeared to reverse the identity of the best codec. On the full corpus, ZFP is the best codec under both metrics for the overwhelming majority of materials; what changes more often is the ordering of the two non-winning codecs. The revised result is scientifically stronger because it isolates the genuine evaluation error without relying on a sampling-dependent ranking reversal.

### 2. Domain migration, rather than within-basin value error, dominates the chemical error

For a Bader basin \(\Omega_a\), the charge perturbation can be decomposed schematically as

\[
\Delta Q_a = \Delta Q_{a,\mathrm{integrand}} + \Delta Q_{a,\mathrm{domain}},
\]

where the first term integrates the density perturbation over a fixed domain and the second captures the effect of changing which grid cells belong to the atom. We evaluated this decomposition for 12 materials chosen across the measured stability range, three codecs and three compression tolerances. The current summary contains 106 successful material–codec–tolerance cases and closes numerically to within 2.22 x 10^-16 e at the maximum-error atom.

Because cancellation can make \(|\Delta Q_{\mathrm{domain}}|/|\Delta Q_{\mathrm{total}}|\) exceed unity, we quantify dominance using the bounded fraction

\[
f_{\mathrm{domain}} = \frac{|\Delta Q_{\mathrm{domain}}|}{|\Delta Q_{\mathrm{domain}}| + |\Delta Q_{\mathrm{integrand}}|}.
\]

Its median is 0.995, with an interquartile range of 0.965–0.999; 84.9% of cases exceed 0.90. Thus, compression-induced Bader error is usually not the integral of a slightly wrong density over the same atom. It is predominantly the consequence of changing the atom's integration domain. This mechanism explains why a field-level norm cannot by itself determine the downstream charge error: two errors with similar amplitude can trigger different basin reallocations.

### 3. Equal nominal tolerance conflates bound utilization with error structure

All 6,343 successful reconstructions satisfy their requested pointwise error bounds. However, the codecs do not use those bounds similarly. The measured ratio \(\|\tilde\rho-\rho\|_\infty/\epsilon_{\mathrm{nominal}}\) has a median of 1.000 for SZ3 and SPERR but only 0.1575 for ZFP (interquartile range 0.1323–0.1939). Therefore, a comparison at the same nominal tolerance gives ZFP a substantially smaller realized field perturbation.

This observation changes the interpretation of the original same-tolerance result. On all successful base-ladder pairs, SZ3 produces median re-derived Bader errors 4.78, 7.77 and 11.80 times those of ZFP at nominal relative tolerances of 10^-4, 10^-3 and 10^-2, respectively. But the corresponding median ratios of realized L-infinity error are 5.85, 6.49 and 8.46. The large same-nominal chemical gap therefore contains an important **bound-utilization effect** and cannot be attributed entirely to spatial error structure.

To isolate the residual structure effect, we matched operating points within each material by measured L-infinity error rather than nominal tolerance. Mutual-nearest matches were required to lie within 0.10 decades in \(\log_{10} L_\infty\). This produced 457 SZ3–ZFP matches from 214 materials. The median material-level L-infinity ratio was 0.951, yet the median Bader-error ratio remained 1.81 [95% bootstrap CI 1.70, 1.95], with SZ3 worse in 90.2% of materials. SPERR–ZFP gave a ratio of 1.72 [1.54, 1.89]. Varying the matching window from 0.10 to 0.25 decades changed the SZ3–ZFP estimate only from 1.81 to 1.69.

The result is not caused by including materials whose Bader charges are themselves unstable. Restricting the analysis to Protocol-A.1-eligible systems before matching gives SZ3–ZFP ratios of 1.96 [1.61, 2.75], 1.90 [1.70, 2.20] and 1.85 [1.72, 2.00] for eligibility contracts of 10^-4, 10^-3 and 10^-2 e. The direction holds in 92.9%, 91.4% and 91.0% of materials. SPERR–ZFP ratios are 1.57, 1.87 and 1.73 over the same contracts.

As a complementary analysis, we fit material-fixed-effect models over the common realized-L-infinity support,

\[
\log_{10}\Delta Q = \alpha_{\mathrm{material}} + \beta\log_{10}L_\infty + \gamma_{\mathrm{codec}} + \text{codec}\times\log_{10}L_\infty.
\]

At the 10^-3 e stability contract, the codec effect at the centered realized-error scale is 2.23-fold [2.09, 2.39] for SZ3 and 2.00-fold [1.86, 2.16] for SPERR relative to ZFP. The estimates remain approximately twofold at the 10^-2 e contract and increase, rather than disappear, on the most stable 10^-4 e subset. Together, matching and fixed-effects analysis support a two-part interpretation: ZFP's same-nominal advantage is partly due to conservative use of its requested error budget, but a substantial codec-specific residual remains at comparable measured error amplitude. The latter is consistent with different spatial error structures interacting differently with Bader basin boundaries.

### 4. Bader charge has its own numerical resolvability limit

A compression result should only be scored against a Bader-charge threshold \(\tau\) if the uncompressed system itself supports a Bader charge stable at that scale. Protocol A.1 defines a material-specific stability floor by adding uniform noise \(U(-\epsilon_i,+\epsilon_i)\), where \(\epsilon_i\) equals that material's float32 round-trip L-infinity perturbation, recomputing the Bader partition, and taking the maximum charge deviation over five preregistered seeds. A material is eligible at \(\tau\) only when this floor is below \(\tau\).

The resulting eligibility loss is substantial. Across 319 systems, 79.9% are non-evaluable at 10^-4 e, 41.4% at 10^-3 e and 9.7% at 10^-2 e. The 10^-3 e result is particularly important: a threshold that might otherwise be interpreted simply as a stricter compression requirement is not a well-defined Bader contract for roughly two fifths of the corpus. Those systems are not codec failures. They are excluded from pass/fail certification and reported separately as `NON_EVALUABLE_BADER_UNSTABLE`.

One extreme case, `aflow-Al8Cu4U1_ICSD_601801`, illustrates why failure taxonomy matters. Its apparent 2.15 e stability floor arises from permutation of symmetry-equivalent Al basins: the position-indexed charges change, but the multiset of charges is preserved. Protocol A.1 correctly treats the position-indexed QoI as non-evaluable, while the failure registry marks the event as `basin_relabelling_symmetry_equivalent` so that it is not interpreted as a two-electron chemical perturbation.

### 5. The stability probe itself must be validated

Protocol A.1 exists because the original frozen probe failed a validation test. Protocol A used a float64 -> float32 -> float64 round trip as a chemically negligible perturbation. Rounding is monotone, however, and therefore preserves the ordering of unequal voxel values. For an on-grid watershed whose assignment follows ascent relations, this is an unusually favorable perturbation. It can also introduce exact ties that are resolved deterministically in both the reference and perturbed fields.

In an 18-material calibration set, the float32 probe created a median of 82 exact neighboring ties and caused zero voxel reassignment in 9 of 18 materials. Matched-amplitude uniform noise created no exact ties and produced zero reassignment in only 2 of 18. Across the full 319-system corpus, replacing the archived float32 probe by a non-monotone noise probe raised the single-seed floor by a median factor of approximately 8,700. The calibration further showed that one random seed was insufficient: the log10 floor spans a median 0.47 decades and as much as 2.39 decades across seeds. Protocol A.1 therefore uses five preregistered seeds and takes the maximum floor, a conservative choice that can remove a material from eligibility but cannot promote an unstable material into a pass.

Amplitude is also load-bearing. Changing the perturbation amplitude by two decades moves the floor by a median 0.76 decades. We therefore do not describe the measured value as an intrinsic, amplitude-free property of the material. It is a **protocol-defined numerical stability floor at the stated perturbation amplitude**. This distinction is central to reproducibility and prevents the stability analysis from being presented as a universal constant of Bader charge.

### 6. Cheap system descriptors do not generalize as predictors of resolvability

The stability floor varies strongly across materials, but the practical value of Protocol A.1 would be reduced if eligibility could be inferred reliably from simple metadata. We therefore tested conventional descriptors available before compression: system type, number of grid points, atom count, points per atom, slab cell length and vacuum fraction. Logistic models were evaluated by fivefold cross-validation on the development data and then applied once to the untouched external strata.

Development AUROC values are modest (0.643 at 10^-4 e and 0.637 at 10^-3 e), and the apparent signal does not transfer. External AUROC is 0.409, 0.387 and 0.398 for eligibility at 10^-4, 10^-3 and 10^-2 e, respectively, with balanced accuracies near or below 0.5. These results do not prove that resolvability is fundamentally unpredictable from all possible features; they show that the cheap descriptors ordinarily available for screening are insufficient to replace direct stability measurement across corpora.

This external failure also clarifies the earlier bulk-versus-slab observation. A development-set directional contrast does not reproduce on the external AFLOW bulk and NOMAD two-dimensional sets. The general result is not that slabs are intrinsically less stable. It is that instability is common across system classes and cannot be safely inferred from a coarse geometric category.

### 7. The useful compression frontier depends on the scientific contract

After stability qualification, the practical output of the benchmark is the highest compression ratio achieved while satisfying a Bader-charge contract. At \(\tau=10^{-2}\) e, SZ3 achieves the highest median certified ratio: approximately 52x for bulk and 70x for slabs, compared with 30x and 41x for ZFP and 12x and 8x for SPERR. This advantage reflects SZ3's aggressive use of the permitted field-error budget. Certification coverage must be considered alongside ratio, however; on slabs at this contract, ZFP certifies a larger fraction of admitted materials.

As the contract tightens, the ordering changes. At 10^-3 e, bulk medians are 12.9x for SZ3 and 13.5x for ZFP, effectively a tie under paired uncertainty, while ZFP retains higher coverage on slabs. At 10^-4 e, ZFP leads the bulk certified ratio at 7.6x, followed by SZ3 at 6.3x and SPERR at 4.2x. The tighter ladder is essential here because the original ladder censored the best certifiable operating point for some admitted materials.

The correct engineering conclusion is therefore not that one codec is globally superior. The preferred operating point is a Pareto problem over compression ratio, certification coverage and the QoI contract. A codec that is advantageous under a loose chemical tolerance may lose that advantage when the same data are required to preserve a stricter downstream observable.

## Discussion

### Pointwise guarantees and scientific guarantees are different objects

The benchmark demonstrates three separations that are often collapsed into a single idea of "accuracy." First, a nominal codec tolerance is not the same as the error a codec realizes. Second, even at comparable realized L-infinity error, downstream Bader error differs systematically among codecs. Third, the Bader observable itself may not be stable at the requested threshold. A pointwise error guarantee is therefore necessary information about a reconstruction but is not sufficient evidence of scientific fidelity.

This conclusion complements prior QoI-preserving compression work. Jiao et al. formalized the gap between raw-data error control and downstream QoIs and developed error-control theory for several families of derived quantities [4]. TopoSZ similarly showed that ordinary pointwise bounds do not guarantee preservation of topological structures [5]. Bader charge exposes an additional complication: the quantity is an integral over a domain that is itself computed from the perturbed field. The mapping from field values to the integration partition can change discretely. In such problems, preserving values within a norm and preserving the derived scientific domain are separable requirements.

### The mechanism explains why fixed-domain validation is unsafe

The mechanism decomposition gives a concrete reason for the failure. Nearly all of the charge error in the representative cases is associated with domain migration rather than the direct integral of value error within a fixed basin. A fixed-domain evaluator therefore removes the very channel through which compression most strongly perturbs the QoI. This has a broader methodological implication: when a downstream analysis recomputes segmentation, connectivity, phase labels, regions of interest or any other data-dependent domain, compression validation must rerun that operation. Reusing an original segmentation can produce an apparently stable derived quantity by construction.

### Realized-error matching changes, but does not erase, the codec story

The finding that ZFP realizes only about one sixth of the requested error budget is important. Without measuring realized L-infinity error, the large same-nominal differences could be mistaken for pure evidence about error geometry. Matching reduces those differences substantially, from factors of roughly 5–12 to factors around 1.7–2.0. That reduction is informative rather than disappointing: it identifies how much of the effect is caused by bound utilization.

The residual is nevertheless robust. It persists under strict realized-error matching, across matching windows, under material fixed effects and after restricting to stability-qualified systems. We therefore interpret codec identity as a proxy for error structure beyond amplitude, not as a causal label in itself. Establishing which spatial descriptors of the error field mediate the residual difference is a natural next algorithmic question, but it is not required for the present evaluation claim.

### Stability qualification changes the semantics of failure

A central reporting choice in this work is that `NON_EVALUABLE_BADER_UNSTABLE` is neither a pass nor a codec failure. Treating instability as failure would penalize a compressor for a threshold the reference analysis cannot reliably define; ignoring it would create false precision. The eligibility layer makes the contract explicit. It also prevents the stability floor from being treated as a nuisance variable that can be absorbed into error bars after the fact.

The correction from Protocol A to A.1 is part of this contribution. The archived float32 probe was frozen before its blind spot was discovered. Rather than rewriting the protocol, we retained it, documented why it failed, calibrated a replacement and recomputed all probe-dependent statistics. This record provides a practical example of why a stability probe must be validated against the mathematical structure used by the downstream algorithm. "Small" is not a sufficient property of a perturbation; it must also be capable of exciting the relevant failure mode.

### Limitations

The study uses Bader charge as a demanding exemplar rather than claiming that all scientific QoIs behave identically. Smooth algebraic quantities may admit much tighter analytic relationships between field norms and QoI error, whereas partition- or topology-dependent observables can be discontinuous with respect to local perturbations. Extending the protocol to additional electronic-structure outputs, including density-derived critical points or integrated observables with different partition rules, would test the generality of the framework.

The three compressors also represent distinct widely used algorithmic families rather than an exhaustive survey of scientific compression. The residual codec effect should not be interpreted as a universal ranking of transform- versus prediction-based methods. In addition, 76 loose-tolerance reconstructions fail in the downstream Bader solver and are registered separately; the benchmark therefore distinguishes attempted cases from successful downstream evaluations in every denominator.

Finally, Protocol A.1 defines stability at the float32-round-trip L-infinity amplitude and uses the maximum over five random seeds. This is deliberately conservative and reproducible, but not amplitude-free. Supplementary sensitivity analysis quantifies how the floor moves with perturbation scale. A different scientific application may require a different probe amplitude and perturbation family.

## Methods

### Data and provenance

The compression benchmark contains 254 development charge-density fields: 186 bulk systems and 68 slab systems. The stability analysis expands this set to 319 systems by adding a strict external corpus of 37 AFLOW bulk systems and 28 NOMAD two-dimensional/vacuum-containing systems. Source densities are public and provenance, source URLs, hashes, sizes and licenses are recorded in `materials_metadata.csv` and `external_test_MANIFEST.json`. No new DFT calculation was performed for the benchmark.

### Compressors and tolerance ladders

Three error-bounded compressors were evaluated: SZ3 through `pysz` 1.0.3 in absolute `INTERP_LORENZO` mode, ZFP through `zfpy` 1.0.1 in fixed-accuracy mode, and SPERR through `hdf5plugin` 7.0.0 in absolute single-chunk mode. Compression ratio is reported relative to the float64 field payload (8 bytes per grid value).

The base ladder uses relative requested tolerances from 10^-5 to 10^-1, converted to absolute bounds using each field's peak-to-peak range. Runs are early-stopped once the re-derived Bader error reaches 0.05 e. A tight ladder at 10^-7, 3x10^-7, 10^-6 and 3x10^-6 was added for 143 Protocol-A.1-eligible materials to resolve the strict-accuracy frontier. Measured `realized_Linf` is retained for every successful reconstruction, and all rows satisfy the requested pointwise bound.

### Bader fidelity metrics

Bader partitions were computed with `baderkit` 0.10.2 using `method="ongrid"`. The primary fidelity metric is the maximum absolute per-atom charge difference after re-deriving the Bader basins from the reconstructed density. For diagnostic purposes, the reconstructed density is also integrated over the original basins. Their ratio is reported as the fixed-basin understatement factor.

### Protocol A.1 stability qualification

For material \(i\), let

\[
\epsilon_i = \|\mathrm{float32}(\rho_i)-\rho_i\|_\infty.
\]

Protocol A.1 generates five additive perturbations \(U_s(-\epsilon_i,+\epsilon_i)\) using preregistered seeds {20260905, 1, 2, 3, 4}, re-derives the Bader partition for each perturbation, and defines the stability floor as the maximum atom-wise charge deviation over all five seeds. The evaluated contracts are \(\tau\in\{10^{-4},10^{-3},10^{-2}\}\) e. A material is eligible when its floor is less than \(\tau\). Otherwise its status is `NON_EVALUABLE_BADER_UNSTABLE` and it is excluded from the pass/fail denominator while remaining explicitly reported.

Protocol A, which used a deterministic float32 round trip as the perturbation, remains archived unchanged. Protocol A.1 changed only the probe and seed aggregation; thresholds, exclusion semantics and reporting rules were retained.

### Probe calibration

Before Protocol A.1 was frozen, the replacement probe was calibrated on 18 materials stratified by corpus and preliminary stability. Five random seeds were tested at the reference amplitude, and the primary seed was additionally evaluated at 0.1x and 10x amplitude. Calibration endpoints include the Bader floor, exact neighbor ties, voxel reassignments and local axis-order flips. The five-seed maximum was selected because single-seed eligibility changed for multiple calibration materials.

### Basin-error decomposition

For representative cases, the per-atom Bader-charge difference is decomposed into a fixed-domain integrand term and a domain-migration term. The current summary reports these terms at the atom of largest total charge error for 12 stability-stratified materials, three codecs and three tolerances. A bounded domain-dominance fraction, \(|\Delta Q_{domain}|/(|\Delta Q_{domain}|+|\Delta Q_{integrand}|)\), is used for mechanism summaries to avoid ratios above unity caused by cancellation.

### Statistical analysis

Headline certification summaries use material-paired bootstrap confidence intervals. To distinguish nominal-bound utilization from residual error-structure effects, additional analyses were performed on the released master table. Within each material, SZ3–ZFP and SPERR–ZFP operating points were matched by mutual nearest neighbor in \(\log_{10}(\mathrm{realized}\ L_\infty)\), with the primary window restricted to 0.10 decades. The material-level median QoI-error ratio was then bootstrapped over materials. Sensitivity windows of 0.15, 0.20 and 0.25 decades were evaluated.

A complementary material-fixed-effect model was fitted over the common measured-L-infinity support of the codecs. The response was \(\log_{10}\Delta Q_{resolved}\); predictors were centered \(\log_{10}L_\infty\), codec identity, their interaction and material fixed effects. Standard errors were clustered by material. The entire matching and regression analysis was repeated after restricting the master table to Protocol-A.1 eligibility at each chemical contract.

To test whether eligibility could be screened without direct perturbation, logistic models using conventional metadata (system type, log grid size, log atom count, log points per atom, vacuum fraction and slab cell length) were evaluated by stratified fivefold cross-validation on development systems and then applied without refitting to the external strata. AUROC, balanced accuracy and Brier score were recorded.

## Data and code availability

The frozen release tables, protocol documents, provenance records and claim–evidence matrix are stored in the `stloendays/QoI` repository. Reproducible statistical post-processing for realized-L-infinity matching, fixed-effect models and descriptor predictability is kept on the isolated branch `analysis/chatgpt-postprocess-20260906`; it does not modify the frozen data on `main`.

## References

1. Diffenderfer, J., Fox, A. L., Hittinger, J. A. F., Sanders, G. & Lindstrom, P. G. Error Analysis of ZFP Compression for Floating-Point Data. *SIAM Journal on Scientific Computing* **41**, A1867–A1898 (2019). https://doi.org/10.1137/18M1168832
2. Liang, X. et al. SZ3: A Modular Framework for Composing Prediction-Based Error-Bounded Lossy Compressors. *IEEE Transactions on Big Data* **9**, 485–498 (2023). https://doi.org/10.1109/TBDATA.2022.3201176
3. Li, S., Lindstrom, P. & Clyne, J. Lossy Scientific Data Compression With SPERR. In *2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)* (2023). https://doi.org/10.1109/IPDPS54959.2023.00104
4. Jiao, P. et al. Toward Quantity-of-Interest Preserving Lossy Compression for Scientific Data. *Proceedings of the VLDB Endowment* **16**, 697–710 (2022). https://doi.org/10.14778/3574245.3574255
5. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving Topology in Error-Bounded Lossy Compression. *IEEE Transactions on Visualization and Computer Graphics* **30**, 1302–1312 (2024). https://doi.org/10.1109/TVCG.2023.3326920
6. Bader, R. F. W. *Atoms in Molecules: A Quantum Theory*. Oxford University Press (1990).
7. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. *Computational Materials Science* **36**, 354–360 (2006). https://doi.org/10.1016/j.commatsci.2005.04.010
8. Sanville, E., Kenny, S. D., Smith, R. & Henkelman, G. Improved grid-based algorithm for Bader charge allocation. *Journal of Computational Chemistry* **28**, 899–908 (2007). https://doi.org/10.1002/jcc.20575
