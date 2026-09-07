# Chemical Fidelity beyond Pointwise Error Bounds: Stability and Bader-Domain Migration in Lossy-Compressed Electron Densities

## Abstract

Error-bounded compression controls the reconstructed electron-density field, whereas chemical analysis acts on quantities derived from that field. We examine the gap between these two levels for atom-resolved Bader charge analysis using 6,343 retained reconstructions of 254 density-functional-theory electron densities compressed with SZ3, ZFP, and SPERR. The benchmark separates requested error from realized perturbation, fixed-domain integration from fully re-derived Bader analysis, and codec fidelity from the intrinsic numerical stability of the downstream quantity of interest (QoI). Equal requested tolerances do not imply equal field perturbations: ZFP realizes a median of approximately 0.158 of its requested L-infinity bound, whereas SZ3 and SPERR operate close to the requested bound. More importantly, holding the original Bader partition fixed systematically understates downstream charge error because it suppresses reconstruction-induced domain motion. A representative atom-level mechanism analysis spanning 12 materials, three codecs, and 106 successful operating points closes the charge-error decomposition to within 2 x 10^-16 e and gives a median domain-term share of 0.9995 at the most affected atom. A calibrated five-seed stability protocol further shows that Bader charge itself has a material-specific numerical resolution: across the 319-system stability corpus, approximately 80%, 41%, and 10% of systems are non-evaluable at 10^-4, 10^-3, and 10^-2 e, respectively. We therefore define a stability-qualified chemical contract and summarize valid operating points by a material-level Certified Compression Ratio (CCR), the maximum compression ratio that preserves the re-derived Bader result within a specified chemical tolerance. The resulting workflow links numerical perturbation, downstream topology, and chemical fidelity in a single auditable rate-fidelity framework.

## 1. Introduction

Real-space electron-density fields are central intermediates in electronic-structure workflows. They support charge partitioning, bonding analysis, visualization, archival reuse, and increasingly data-driven post-processing. In high-throughput density-functional-theory (DFT) calculations, these volumetric fields can become a substantial storage and I/O burden even after the underlying electronic-structure calculation is complete. Error-bounded lossy compression offers a direct remedy by replacing exact storage with a controlled numerical approximation. General-purpose compressors such as ZFP, SZ3, and SPERR expose explicit error controls [1-3], making the reconstruction error straightforward to specify and audit.

The scientific object of interest, however, is rarely an individual grid value. Chemical conclusions are drawn from quantities of interest (QoIs): integrated charges, extrema, interfaces, critical points, segmentations, or other outputs of a post-processing pipeline. A field norm and a downstream scientific error therefore answer different questions. QoI-preserving compression has formalized this distinction for selected downstream operators [4], while topology-aware methods preserve extrema, contour trees, Morse-Smale structures, or local order that ordinary pointwise bounds do not encode [5-9]. Recent approaches further model spatial compression-error correlations or expose task-specific QoI/compression trade-offs [10,11]. These developments motivate a more direct question for chemical data: what fidelity contract should be applied to the analysis actually performed on a reconstructed field?

Bader charge analysis makes that question especially sharp. In the atoms-in-molecules construction, the electron density defines atomic basins, and atomic charges are obtained by integrating the density over those basins [12,13]. Grid implementations follow local ascent relations to assign voxels to atomic regions [13,16]. The integration domain is therefore not external to the field: it is reconstructed from the field itself. A perturbation can change a Bader charge through two coupled channels - changes in density values within a basin and movement of the basin boundary. An evaluation that reuses the original basin suppresses the second channel by construction.

The reference analysis also has a finite numerical resolution. If a chemically negligible perturbation of the original density changes the re-derived Bader partition enough to move an atom-resolved charge beyond the requested tolerance, that material does not support a meaningful codec pass/fail statement at that scale. The reference QoI must therefore be qualified before it can serve as a fidelity contract.

We address these coupled issues through a stability-qualified benchmark of SZ3, ZFP, and SPERR on DFT electron-density fields. The study separates requested error from realized error, fixed-domain integration from re-derived chemical analysis, intrinsic QoI resolvability from codec certification, and raw compression ratio from chemically valid rate-fidelity. The resulting evidence supports a compact principle: **scientific fidelity is a property of the complete chain from numerical perturbation to downstream analysis**.

## 2. Scientific question and benchmark design

### 2.1 What must be preserved for a compressed density to remain chemically usable?

Let the reference electron density be \(\rho\) and the reconstructed field be \(\tilde{\rho}\). A conventional error-bounded compressor controls a field-level quantity such as

\[
\|\tilde{\rho}-\rho\|_{\infty} \leq \epsilon.
\]

For Bader analysis, the relevant chemical output also depends on the partition operator \(\Omega(\rho)\), which maps a density field to atom-resolved integration domains. The primary downstream error for atom \(a\) is therefore

\[
\Delta Q_a^{\mathrm{resolved}}
=
Q_a\!\left(\tilde{\rho};\Omega_a(\tilde{\rho})\right)
-
Q_a\!\left(\rho;\Omega_a(\rho)\right).
\]

A fixed-basin diagnostic instead evaluates

\[
\Delta Q_a^{\mathrm{fixed}}
=
Q_a\!\left(\tilde{\rho};\Omega_a(\rho)\right)
-
Q_a\!\left(\rho;\Omega_a(\rho)\right).
\]

These expressions differ only in whether the integration domain is reconstructed after decompression, but that difference determines whether domain migration is measured.

The complete evaluation chain is

**source provenance -> intrinsic QoI stability -> eligibility -> compression/reconstruction -> re-derived QoI -> topology/domain audit -> certification -> rate-fidelity**.

The workflow is designed so that each stage answers a different scientific question. Provenance establishes that the source object is the intended one. Stability qualification establishes the chemical precision that the downstream analysis can resolve. Compression then introduces a controlled numerical perturbation, the downstream analysis is rerun from the reconstructed field, and the resulting chemical error is judged only at resolvable tolerances. Rate-fidelity is summarized after those scientific conditions have been enforced.

### 2.2 Development benchmark and stability corpus

The development benchmark contains 254 DFT charge-density fields spanning 186 bulk materials and 68 slab systems. Three production error-bounded compressors are evaluated: SZ3 through pysz 1.0.3 in absolute INTERP_LORENZO mode, ZFP through zfpy 1.0.1 in fixed-accuracy mode, and SPERR through hdf5plugin 7.0.0 in absolute single-chunk mode. Compression ratio is measured relative to the float64 field payload.

The released master table contains 6,343 retained successful reconstruction rows: 4,627 from the base tolerance ladder and 1,716 from a tighter extension used to resolve the strict-accuracy regime. The tight extension is applied only to materials satisfying the pre-specified Protocol-A.1 stability condition. All successful retained rows satisfy their requested pointwise error bound.

Bader partitions are computed with BaderKit 0.10.2 using `method="ongrid"` [16]. For each successful reconstruction the benchmark records the requested tolerance, realized \(L_\infty\) error, realized/requested error ratio, compression ratio, fixed-basin charge error, re-derived Bader charge error, and topology/domain-migration diagnostics.

The stability analysis expands the material set with 37 AFLOW bulk systems [18] and 28 NOMAD two-dimensional or vacuum-containing systems [19], producing a 319-system stability corpus. Source provenance, formulas, grid sizes, atom counts, byte counts, source URLs, checksums, and available licensing metadata are retained in the versioned repository.

### 2.3 A chemical contract requires a resolvable reference observable

Protocol A.1 measures the numerical resolvability of atom-resolved Bader charge before codec certification. For material \(i\), the perturbation amplitude is the float32 round-trip \(L_\infty\) error

\[
\epsilon_i^{32}
=
\left\|
\operatorname{float64}[\operatorname{float32}(\rho_i)]-\rho_i
\right\|_{\infty}.
\]

Five perturbations are generated with the pre-specified seeds \(\{20260905,1,2,3,4\}\),

\[
\rho_i^{(s)} = \rho_i + u_i^{(s)}, \qquad u_i^{(s)} \sim U(-\epsilon_i^{32},+\epsilon_i^{32}).
\]

The Bader partition is re-derived after every perturbation, and the stability floor is

\[
F_i
=
\max_s\max_a
\left|
Q_a(\rho_i^{(s)})-Q_a(\rho_i)
\right|.
\]

The chemical contracts evaluated throughout are \(\tau \in \{10^{-4},10^{-3},10^{-2}\}\) e. A material enters codec certification at tolerance \(\tau\) only when \(F_i<\tau\). This produces three distinct analytical levels: successful reconstructions describe codec behavior, Protocol-A.1-admitted material-tolerance combinations define chemically evaluable cases, and certified reconstructions identify operating points that satisfy the downstream charge contract.

Protocol A.1 replaces an archived deterministic float32 round-trip probe. Calibration showed that monotone rounding can preserve local order while creating exact ties, making it unusually benign for an on-grid watershed. Equal-amplitude additive noise perturbs the order-dependent structure used by the Bader assignment and therefore provides a more informative stability stress test at the same numerical scale.

### 2.4 Chemical certification and Certified Compression Ratio

For material \(i\), codec \(c\), setting \(k\), and chemical tolerance \(\tau\), a successful reconstruction is certified when

\[
F_i<\tau
\qquad\text{and}\qquad
E_{\mathrm{resolved},i,c,k}<\tau,
\]

where

\[
E_{\mathrm{resolved},i,c,k}
=
\max_a
\left|
Q_a(\tilde{\rho}_{i,c,k};\Omega_a(\tilde{\rho}_{i,c,k}))
-
Q_a(\rho_i;\Omega_a(\rho_i))
\right|.
\]

The material-level rate metric is the **Certified Compression Ratio (CCR)**,

\[
\mathrm{CCR}_{i,c}(\tau)
=
\max_{k:\,\mathrm{certified}}
\mathrm{CR}_{i,c,k}.
\]

CCR asks how strongly a particular electron-density field can be compressed while still supporting the intended Bader analysis within \(\tau\). Materials, rather than codec rows, are the independent units in headline rate-fidelity statistics.

Failures are retained at the level at which they occur. Material-level provenance, parsing, source-integrity, or original-Bader failures prevent a valid material analysis. Row-level codec or downstream-analysis failures affect only that material-codec-tolerance operating point and remain explicitly registered without erasing successful rows for the same material. This preserves the distinction between scientific non-certification and pipeline failure while preventing silent complete-case inflation of the rate-fidelity frontier.

### 2.5 Frozen external transfer design

The independent external corpus contains 65 frozen source systems: 37 AFLOW bulk systems and 28 NOMAD two-dimensional systems. Two systems were used as implementation sentinels while validating the end-to-end harness. They remain part of the complete external release, while the remaining 63 systems - 36 AFLOW bulk and 27 NOMAD two-dimensional systems - form the pre-specified primary confirmatory rate-fidelity cohort.

The external analysis inherits Protocol A.1, the three scientific tolerances, codec modes, tolerance ladders, Bader implementation, early-stopping rule, failure accounting, and CCR aggregation from the development study. The frozen confirmatory cohort contains 16, 42, and 57 Protocol-A.1-admitted systems at \(10^{-4}\), \(10^{-3}\), and \(10^{-2}\) e, respectively. External transfer is therefore evaluated without changing the scientific contract or adapting the tolerance grid to external outcomes.

## 3. Codec error structure

### 3.1 Equal requested tolerances are not equal realized perturbations

All three codecs respect their requested pointwise bounds, but they use those bounds differently. Across the released benchmark, ZFP realizes a median \(L_\infty\)-to-requested ratio of approximately 0.158, whereas SZ3 and SPERR operate close to 1.0. ZFP therefore perturbs the field substantially less than its nominal tolerance would suggest, while SZ3 and SPERR nearly saturate the available error budget.

A requested tolerance is consequently an operational codec setting rather than a common physical perturbation scale. Same-nominal comparisons mix the amount of perturbation with the spatial structure of that perturbation. The realized-error audit separates these two effects and is therefore carried forward in every cross-codec interpretation.

### 3.2 Pointwise magnitude does not determine the downstream Bader response

Among Protocol-A.1-admitted development materials, matched nominal tolerances produce large and systematic codec differences in re-derived Bader error. Relative to ZFP, the per-material median SZ3/ZFP Bader-error ratio is 6.4 at the \(10^{-4}\) e contract, 9.2 at \(10^{-3}\) e, and 12.4 at \(10^{-2}\) e; SZ3 gives the larger error for 98-100% of the contributing materials. SPERR shows the same qualitative separation from ZFP.

Part of this difference follows directly from bound utilization: ZFP generally applies a smaller realized perturbation. The remaining scientific question is why a pointwise-compliant perturbation can produce such different charge responses once the downstream partition is reconstructed. The fixed-versus-resolved analysis and atom-level decomposition address that mechanism directly.

## 4. QoI / chemical fidelity

### 4.1 Re-deriving the Bader partition changes the fidelity assessment

The fixed-basin diagnostic and re-derived Bader analysis score the same reconstructed fields but answer different questions. The fixed-basin calculation measures only the change in the density integrated over the original atom domains. Re-derived analysis also allows the atom domains themselves to move.

Across codecs and structural strata, fixed-basin charge deviations are approximately 9-11 times smaller than the corresponding re-derived deviations in the released development analysis. The direction is consistent: holding the partition fixed systematically removes an error channel that is present when a user reruns Bader analysis on the decompressed field.

This distinction changes the fidelity contract. Fixed-basin integration remains useful as a mechanism diagnostic because it isolates the within-domain contribution. The re-derived result is the chemically relevant endpoint because it reproduces the analysis path applied to an independently stored reconstructed density.

### 4.2 Bader fidelity is defined only above the numerical resolvability floor

Protocol A.1 shows that the downstream observable itself has a finite numerical resolution. Across all 319 systems in the stability corpus, approximately 80% are non-evaluable at a \(10^{-4}\) e charge contract, 41% at \(10^{-3}\) e, and 10% at \(10^{-2}\) e. A stringent chemical threshold is therefore meaningful only for the subset of materials whose reference Bader analysis is stable at that scale.

The external strata reinforce this interpretation. At \(10^{-4}\) e, 71-94% of each tested stratum is non-evaluable; at \(10^{-3}\) e the range is 21-45%; at \(10^{-2}\) e it falls to 0-16%. The earlier development-only hypothesis that slab systems should be intrinsically less stable than bulk materials does not transfer as a general rule. The robust result is instead that Bader instability is common, strongly material dependent, and best measured directly rather than inferred from a broad structure label.

The certification problem therefore has two steps. The reference Bader result must first be resolvable at \(\tau\); the compressed reconstruction must then preserve that result within \(\tau\). This separates instability of the analysis from error introduced by the codec.

## 5. Mechanism: domain migration in a field-derived partition

### 5.1 Bader charge error separates into integrand and domain terms

For atomic basin \(a\), the total charge perturbation can be written as

\[
\Delta Q_a
=
\underbrace{
\int_{\Omega_a(\rho)}(\tilde{\rho}-\rho)\,d\mathbf r
}_{\Delta Q_a^{\mathrm{integrand}}}
+
\underbrace{
\left[
\int_{\Omega_a(\tilde{\rho})}\tilde{\rho}\,d\mathbf r
-
\int_{\Omega_a(\rho)}\tilde{\rho}\,d\mathbf r
\right]
}_{\Delta Q_a^{\mathrm{domain}}}.
\]

The integrand term measures the effect of changing density values while retaining the reference basin. The domain term measures the effect of changing which voxels belong to that atom.

The representative mechanism dataset contains 1,665 atom-level rows from 12 pre-specified materials, three codecs, and 106 successful material-codec-tolerance operating points. Two additional operating points are retained in the failure registry. The decomposition satisfies

\[
\Delta Q_a^{\mathrm{integrand}}
+
\Delta Q_a^{\mathrm{domain}}
=
\Delta Q_a
\]

with a reported residual no larger than \(2\times10^{-16}\) e.

At the atom carrying the largest absolute total error in each successful operating point, the median domain-term share is 0.9995. In this representative mechanism set, the dominant measured contribution at the worst-affected atom is therefore movement of the field-derived integration domain rather than the density-value integral over a fixed basin.

### 5.2 The missing information in a pointwise bound is local ordering and domain geometry

A pointwise bound constrains the amplitude of the reconstruction error at every voxel. It does not specify how neighboring errors are correlated, whether local ascent relations are preserved, or whether watershed-like assignments remain unchanged. Two reconstructions can therefore satisfy comparable \(L_\infty\) bounds while producing different local order changes and different Bader-domain migration.

This mechanism connects the chemical result to topology- and order-aware compression. TopoSZ preserves topological structures under error-bounded compression [5], later methods preserve or correct Morse-Smale structures [7,8], and recent local-order-preserving compression explicitly protects neighboring value order and critical points [9]. Bader analysis supplies a chemically explicit target for this class of structure because its atom assignments depend on local ascent through the density field.

The implication for compressor design is specific: preserving the discrete relations that determine field-derived integration domains is more closely aligned with Bader fidelity than minimizing pointwise amplitude alone. The contribution here is the evaluation target and mechanism, which provides a direct criterion for future codec design.

## 6. Robustness, failure regimes, rate-fidelity, and implications

### 6.1 Stability-probe calibration reveals an algorithm-aware numerical floor

The stability probe must perturb the mathematical structure used by the downstream algorithm. A deterministic float64 -> float32 -> float64 round trip is monotone for unequal values and tends to preserve local order while creating exact ties. For an on-grid Bader watershed, this perturbation is unusually structure preserving.

Calibration showed that the archived float32 probe could understate the Bader stability floor by orders of magnitude. Across the calibration set, equal-amplitude additive noise breaks the false stability while preserving the perturbation scale; five seeds are required because eligibility can change with the realization. The final Protocol A.1 floor is therefore the maximum atom-wise deviation across the pre-specified five-seed set.

Probe amplitude remains part of the numerical contract. Varying the perturbation amplitude across two decades shifts the floor by a median 0.76 decades in the calibration study. The resulting stability floor is interpreted at a stated perturbation scale, which makes the reference precision explicit rather than implicit.

### 6.2 Registered downstream failures define a distinct operating regime

The workflow records source-level failures, codec-row failures, Bader-solver failures, topology-diagnostic failures, and symmetry-equivalent basin relabeling separately from successful chemical comparisons. These outcomes are scientifically informative because they identify regimes where the downstream analysis ceases to return a standard comparable result.

Row-level failures are retained without discarding otherwise valid operating points for the same material. Conversely, failed rows are never treated as successful or omitted from the audit trail. This preserves the full rate-fidelity denominator while separating ordinary non-certification from analysis breakdown.

The symmetry-equivalent relabeling example is particularly instructive. In `aflow-Al8Cu4U1_ICSD_601801`, noise can exchange position-indexed Bader assignments between symmetry-equivalent Al atoms while leaving the charge multiset unchanged. The event reveals a label-semantic instability of the downstream analysis rather than a multi-electron change in the underlying chemistry. Treating such cases explicitly strengthens the interpretation of every ordinary certified or non-certified comparison.

### 6.3 The optimal compression operating point depends on the chemical contract

Once Protocol-A.1 qualification and re-derived Bader certification are enforced, the rate-fidelity frontier changes systematically with \(\tau\). Across the full 254-material development benchmark, the number of admitted materials is 46 at \(10^{-4}\) e, 143 at \(10^{-3}\) e, and 229 at \(10^{-2}\) e.

At \(10^{-4}\) e, median CCR values are 7.84x for ZFP, 6.37x for SZ3, and 4.21x for SPERR. ZFP certifies all 46 admitted materials, compared with 38 for SZ3 and 39 for SPERR. At \(10^{-3}\) e, ZFP and SZ3 converge to median CCR values of 13.83x and 13.19x, while SPERR reaches 5.78x; certification fractions are 99.3%, 95.1%, and 95.8%, respectively. At \(10^{-2}\) e, the ordering changes: SZ3 reaches a median CCR of 57.66x, ZFP 31.90x, and SPERR 10.32x, with corresponding certification fractions of 90.4%, 98.3%, and 90.8%.

The same contract dependence appears across structural strata. At \(10^{-2}\) e, bulk SZ3 reaches a median CCR of 51.78x and slab SZ3 67.75x, while ZFP reaches 30.02x and 40.45x, respectively. At \(10^{-3}\) e, ZFP and SZ3 are close on bulk materials and ZFP leads on the slab subset. At \(10^{-4}\) e, the admitted slab set contains only four materials, so the bulk result carries the population-level weight at that strictest contract.

These frontiers show why compression ratio alone is not the correct operating metric. The preferred codec changes with chemical precision and certification coverage. CCR expresses that dependence directly at the material level.

### 6.4 Lossy compression remains worthwhile after chemical qualification

Exact and nominally lossless baselines remain much closer to unity than the certified lossy frontiers. In the development release, representative bulk medians are approximately 2.1x for float64+zstd, 3.0x for float64+xz, and 4.6x for float32+zstd; corresponding slab medians are approximately 1.1x, 1.2x, and 2.2x. At the \(10^{-2}\) e chemical contract, chemically certified lossy compression reaches median ratios tens of times larger for SZ3 and ZFP while maintaining high certification coverage among admitted materials.

The advantage survives the stability gate because the comparison is no longer between raw lossy ratio and exact storage. It is between exact storage and the best operating point that respects both the numerical approximation contract and the downstream chemical contract.

### 6.5 Independent transfer tests the workflow rather than tuning it

The external study is designed to test whether development rate-fidelity behavior transfers under the same frozen scientific contract. The complete 65-system external corpus is retained for descriptive reporting, and the 63-system cohort not used for implementation diagnostics provides the confirmatory rate-fidelity population. The external run uses the same stability qualification, tolerance ladders, codec modes, Bader analysis, failure semantics, and CCR definition as the development benchmark.

<!-- EXTERNAL_RATE_FIDELITY_RESULTS_PENDING: replace this comment with the audited 63-system confirmatory results and all-65 descriptive summary after the frozen Full run is terminal. Report agreement or disagreement with the development codec ordering as a scientific result, without retuning. -->

### 6.6 Implications for chemical data infrastructure

The benchmark suggests a practical metadata model for reusable electronic-structure data. A compressed field can carry not only a codec name and nominal tolerance, but also the realized reconstruction error, the downstream analysis used for certification, the numerical resolvability scale of that analysis, and the certified operating range. Compression then becomes a property-aware data-quality decision rather than a storage-only decision.

The same evaluation logic is most directly transferable to analyses whose domains, labels, thresholds, or topological objects are reconstructed from the field. In such workflows, three questions can be posed in sequence: is the reference QoI numerically resolvable, does reconstruction alter the derived structure, and does that structural change control the downstream error? Bader charge provides a chemically explicit case in which all three questions can be measured directly.

## 7. Conclusion

Pointwise error bounds remain valuable guarantees on reconstructed electron-density fields, but they do not by themselves define chemical fidelity for a field-dependent analysis. In Bader analysis, the missing variable is the response of the integration domains themselves. Re-derived evaluation exposes an error channel that fixed-basin integration suppresses, and atom-level decomposition in the representative mechanism set shows that domain migration accounts for essentially all of the error at the most affected atom.

Separating requested tolerance from realized perturbation further clarifies codec behavior. ZFP operates substantially inside its requested error budget, whereas SZ3 and SPERR use nearly all of theirs. The resulting differences in Bader response therefore reflect both perturbation magnitude and reconstruction structure. Chemical fidelity is recovered only by evaluating the complete path from field perturbation to re-derived downstream analysis.

Finally, the downstream observable has a numerical resolution scale of its own. Protocol A.1 establishes that a large fraction of materials cannot support arbitrarily strict position-indexed Bader-charge contracts, making intrinsic QoI stability a prerequisite for meaningful codec certification. The Certified Compression Ratio then converts the surviving operating points into a material-level rate-fidelity frontier.

Together, these results define a general scientific-data certification principle: **a numerical approximation should be certified at the level of the analysis it is intended to support, after the intrinsic stability of that quantity has been established.**

## Data and Software Availability

The benchmark data, Protocol A.1 stability measurements, failure registry, provenance metadata, mechanism tables, supplementary sensitivity analyses, workflow specifications, and figure-generation scripts are maintained in the project repository. A versioned archival release with a persistent identifier will be frozen before formal submission so that the published record maps to an immutable data-and-software snapshot. Source URLs, checksums, and available licensing metadata for the underlying material fields are retained with the release.

## References

1. Diffenderfer, J.; Fox, A. L.; Hittinger, J. A. F.; Sanders, G.; Lindstrom, P. G. Error Analysis of ZFP Compression for Floating-Point Data. *SIAM J. Sci. Comput.* **2019**, *41*, A1867-A1898. DOI: 10.1137/18M1168832.
2. Liang, X.; Zhao, K.; Di, S.; Li, S.; Underwood, R.; Gok, A. M.; Tian, J.; Deng, J.; Calhoun, J. C.; Tao, D.; Chen, Z.; Cappello, F. SZ3: A Modular Framework for Composing Prediction-Based Error-Bounded Lossy Compressors. *IEEE Trans. Big Data* **2023**, *9*, 485-498. DOI: 10.1109/TBDATA.2022.3201176.
3. Li, S.; Lindstrom, P.; Clyne, J. Lossy Scientific Data Compression With SPERR. In *2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*; IEEE, 2023; pp 1007-1017. DOI: 10.1109/IPDPS54959.2023.00104.
4. Jiao, P.; Di, S.; Guo, H.; Zhao, K.; Tian, J.; Tao, D.; Liang, X.; Cappello, F. Toward Quantity-of-Interest Preserving Lossy Compression for Scientific Data. *Proc. VLDB Endow.* **2022**, *16* (4), 697-710. DOI: 10.14778/3574245.3574255.
5. Yan, L.; Liang, X.; Guo, H.; Wang, B. TopoSZ: Preserving Topology in Error-Bounded Lossy Compression. *IEEE Trans. Vis. Comput. Graph.* **2024**, *30* (1), 1302-1312. DOI: 10.1109/TVCG.2023.3326920.
6. Gorski, N.; Liang, X.; Guo, H.; Yan, L.; Wang, B. A General Framework for Augmenting Lossy Compressors With Topological Guarantees. *IEEE Trans. Vis. Comput. Graph.* **2025**, *31*, 3693-3705. DOI: 10.1109/TVCG.2025.3567054.
7. Li, Y.; Xia, M.; Liang, X.; Wang, B.; Guo, H. Preserving Discrete Morse-Smale Complexes in Error-Bounded Lossy Compression. *IEEE Trans. Vis. Comput. Graph.* **2026**, *32* (7), 6593-6609. DOI: 10.1109/TVCG.2026.3684385.
8. Li, Y.; Xia, M.; Liang, X.; Wang, B.; Underwood, R.; Di, S.; Sharma, H.; Beniwal, D.; Cappello, F.; Guo, H. pMSz: A Distributed Parallel Algorithm for Correcting Extrema and Morse-Smale Segmentations in Lossy Compression. In *2026 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*; IEEE, 2026. DOI: 10.1109/IPDPS65963.2026.00025.
9. Fallin, A.; Gorski, N.; Agarwal, T.; Wang, B.; Gopalakrishnan, G.; Burtscher, M. Fast Topology-Aware Lossy Data Compression with Full Preservation of Critical Points and Local Order. *IEEE Trans. Big Data* **2026**. DOI: 10.1109/TBDATA.2026.3705355.
10. Liu, Y.; Jiang, B.; Yang, T.; Di, S.; Underwood, R.; Jin, S. TOPIQ: Statistical Error Propagation for Quantity-of-Interest Prediction under Lossy Compression. Accepted at SC 2026; arXiv:2608.26912, 2026. DOI: 10.48550/arXiv.2608.26912.
11. Liu, G.; Li, Y.; Ren, C.; Underwood, R.; Liang, X.; Wang, B.; Di, S.; Cappello, F.; Guo, H. FZ-VIS: A Visual Analytics Framework for Quantities-of-Interest-Aware Scientific Lossy Compression. Accepted at IEEE VIS 2026 / *IEEE Trans. Vis. Comput. Graph.*; arXiv:2608.08386, 2026. DOI: 10.48550/arXiv.2608.08386.
12. Bader, R. F. W. *Atoms in Molecules: A Quantum Theory*; Oxford University Press: Oxford, 1990.
13. Henkelman, G.; Arnaldsson, A.; Jonsson, H. A Fast and Robust Algorithm for Bader Decomposition of Charge Density. *Comput. Mater. Sci.* **2006**, *36*, 354-360. DOI: 10.1016/j.commatsci.2005.04.010.
14. Brehm, M.; Thomas, M. An Efficient Lossless Compression Algorithm for Trajectories of Atom Positions and Volumetric Data. *J. Chem. Inf. Model.* **2018**, *58* (10), 2092-2107. DOI: 10.1021/acs.jcim.8b00501.
15. Gong, J.; Zhao, Z.; Tang, B. Z. Bridging Machine Learning and Electron Density Theory with Adaptive Real-Space Integration. *J. Chem. Theory Comput.* **2026**. DOI: 10.1021/acs.jctc.6c01124.
16. Weaver, S. M.; Warren, S. BaderKit: A Python Package for Grid-based Bader Charge Analysis. *J. Open Source Softw.* **2026**, *11* (121), 9943. DOI: 10.21105/joss.09943.
17. Horton, M. K.; Huck, P.; Yang, R. X.; et al. Accelerated Data-Driven Materials Science with the Materials Project. *Nat. Mater.* **2025**, *24*, 1522-1532. DOI: 10.1038/s41563-025-02272-0.
18. Curtarolo, S.; Setyawan, W.; Wang, S.; Xue, J.; Yang, K.; Taylor, R. H.; Nelson, L. J.; Hart, G. L. W.; Sanvito, S.; Buongiorno-Nardelli, M.; Mingo, N.; Levy, O. AFLOWLIB.ORG: A Distributed Materials Properties Repository from High-Throughput Ab Initio Calculations. *Comput. Mater. Sci.* **2012**, *58*, 227-235. DOI: 10.1016/j.commatsci.2012.02.002.
19. Draxl, C.; Scheffler, M. The NOMAD Laboratory: From Data Sharing to Artificial Intelligence. *J. Phys. Mater.* **2019**, *2*, 036001. DOI: 10.1088/2515-7639/ab13bb.
