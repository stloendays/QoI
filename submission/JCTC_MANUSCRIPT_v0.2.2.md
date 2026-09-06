# Chemical Fidelity beyond Pointwise Error Bounds: Stability and Bader-Domain Migration in Lossy-Compressed Electron Densities

**JCTC Article submission draft v0.2.2 — 2026-09-06**

## Abstract

Error-bounded compression controls the reconstructed electron-density field, whereas chemical analysis acts on quantities derived from that field. We examine the gap between these two levels for Bader charge analysis using 6,343 successful reconstructions of 254 density-functional-theory electron densities compressed with SZ3, ZFP, and SPERR. The central distinction is whether Bader basins are held fixed or re-derived after decompression. Across 4,627 base-ladder reconstructions, re-derived charge error exceeds the fixed-basin estimate in 99.7% of cases. Equal requested tolerances also produce unequal perturbations: ZFP realizes a median 0.158 of its requested L-infinity bound, whereas SZ3 and SPERR nearly saturate theirs. Matching codecs by realized L-infinity error and applying a stability-qualified chemical contract retains 1.82-fold and 2.00-fold Bader-error ratios for SZ3/ZFP and SPERR/ZFP in a conservative complete-case analysis. Direct decomposition in a representative 12-material mechanism set gives a median bounded domain-migration contribution of 0.995, and full-benchmark models show that the codec-associated residual collapses after basin reassignment is included but not after global electron-count deviation is included. A calibrated five-seed stability protocol further identifies 41.4% of 319 systems as non-evaluable at a 10^-3 e charge contract. Together, these results define a chemical-fidelity workflow in which a compressed field is evaluated by its realized perturbation, the downstream partition is re-derived, and certification is performed only at numerically resolvable QoI scales.

# 1. Introduction

Real-space electron-density fields are central intermediates in electronic-structure workflows. They support charge partitioning, bonding analysis, visualization, archival reuse, and increasingly data-driven post-processing. In high-throughput density-functional-theory (DFT) calculations, these volumetric fields can become a substantial storage and I/O burden even after the underlying electronic-structure calculation is complete. Chemistry-specific work has shown that volumetric trajectories, including electron-density grids, can be compressed efficiently without changing their values when a lossless representation is used [14]. Lossy compression addresses a different regime: it exchanges exact reconstruction for a controlled numerical perturbation and therefore requires a scientific criterion for deciding which perturbations remain acceptable. General-purpose compressors such as ZFP, SZ3, and SPERR expose explicit pointwise error controls [1–3], making the field-level reconstruction error easy to specify and verify.

The scientific object of interest, however, is rarely an individual grid value. Chemical conclusions are drawn from quantities of interest (QoIs): integrated charges, extrema, interfaces, critical points, segmentations, or other outputs of a post-processing pipeline. A field norm and a downstream scientific error therefore answer different questions. QoI-preserving compression has formalized this distinction for selected downstream operators [4], while topology-aware methods preserve extrema, contour trees, Morse–Smale structures, or local order that ordinary pointwise bounds do not encode [5–9]. Recent approaches further model spatial compression-error correlations or expose task-specific QoI/compression trade-offs [10,11]. The central methodological problem is consequently to define the correct fidelity contract for the analysis actually performed on the reconstructed field.

Bader charge analysis makes that problem especially sharp. In the atoms-in-molecules construction, the electron density defines atomic basins, and atomic charges are obtained by integrating the density over those basins [12,13]. Grid implementations follow local ascent relations to assign voxels to atomic regions [13]. The integration domain is therefore not external to the field: it is reconstructed from the field itself. A perturbation can change a Bader charge through two coupled channels—changes in density values within a basin and movement of the basin boundary. An evaluation that reuses the original basin suppresses the second channel by construction.

This field-derived-domain structure connects the problem to a growing JCTC literature on the downstream use of approximate electron densities. Gong, Zhao, and Tang showed that machine-learned electron densities can exhibit property errors associated with real-space integration and grid discretization and developed adaptive integration to improve downstream evaluation [15]. Nguyen and co-workers subsequently evaluated learned charge-conditioned electron densities through downstream Bader partitioning and electrostatic-potential analysis across a broad external benchmark [20]. Together, these studies establish that electron-density quality is most informative when it is assessed through the analyses that consume the field. Lossy compression creates a complementary controlled-perturbation setting: the reference density is already available, the reconstruction error can be measured directly, and the Bader partition can itself migrate after decompression. The resulting question is not simply whether the density is close pointwise, but what field-level guarantee is sufficient for a quantitative chemical-fidelity contract.

We address that question through a stability-qualified benchmark of SZ3, ZFP, and SPERR on DFT electron-density fields. The study separates requested error from realized error, fixed-domain integration from re-derived chemical analysis, and QoI resolvability from codec certification. The resulting evidence supports a simple principle: for a field-dependent chemical analysis, scientific fidelity must be evaluated at the level of the re-executed analysis rather than inferred from the field bound alone.

# 2. Scientific question and benchmark design

## 2.1 Scientific question: what must be preserved for a compressed density to remain chemically usable?

Let the reference electron density be \(\rho\) and a decompressed reconstruction be \(\tilde\rho\). A conventional error-bounded compressor controls a field-level quantity such as

\[
L_\infty = \|\tilde\rho-\rho\|_\infty.
\]

For Bader analysis, the relevant chemical output also depends on the partition operator \(\mathcal B(\cdot)\), which maps a density field to its atomic basins. The primary downstream error is therefore

\[
\Delta Q_{\mathrm{resolved}}
=
\max_a\left|
Q_a[\tilde\rho,\mathcal B(\tilde\rho)]
-
Q_a[\rho,\mathcal B(\rho)]
\right|,
\]

where \(a\) indexes atoms. A fixed-basin diagnostic instead evaluates

\[
\Delta Q_{\mathrm{fixed}}
=
\max_a\left|
Q_a[\tilde\rho,\mathcal B(\rho)]
-
Q_a[\rho,\mathcal B(\rho)]
\right|.
\]

These expressions differ only in the reconstruction of the integration domain, but that difference determines whether domain migration is measured. Figure 1 summarizes the resulting evaluation chain: codec bound \(\rightarrow\) realized field perturbation \(\rightarrow\) re-derived Bader partition \(\rightarrow\) Bader charge error, with QoI resolvability acting as the certification gate.

## 2.2 Development benchmark and stability corpus

The development benchmark contains 254 DFT charge-density fields from the Materials Project [17]: 186 bulk materials and 68 slab systems. The stability analysis adds 37 AFLOW bulk systems [18] and 28 NOMAD two-dimensional or vacuum-containing systems [19], producing a 319-system stability corpus. Source provenance, formulas, grid sizes, atom counts, byte counts, source URLs, checksums, and available licensing metadata are recorded in `materials_metadata.csv` and `external_test_MANIFEST.json`.

Three general-purpose error-bounded compressors are evaluated: SZ3 through `pysz` 1.0.3 in absolute `INTERP_LORENZO` mode, ZFP through `zfpy` 1.0.1 in fixed-accuracy mode, and SPERR through `hdf5plugin` 7.0.0 in absolute single-chunk mode. Compression ratio is measured relative to the float64 field payload.

The base tolerance ladder spans relative requested bounds from \(10^{-5}\) to \(10^{-1}\), converted to absolute bounds using the peak-to-peak range of each density. Runs are stopped after the re-derived Bader error reaches 0.05 e. A tight ladder at \(10^{-7}\), \(3\times10^{-7}\), \(10^{-6}\), and \(3\times10^{-6}\) resolves the strict-accuracy region for Protocol-A.1-eligible materials. The resulting master table contains 6,343 successful reconstructions: 4,627 base-ladder rows and 1,716 tight-ladder rows. Every successful row satisfies its requested pointwise bound.

Bader partitions are computed with `baderkit` 0.10.2 [16] using `method="ongrid"`. For each successful reconstruction, the benchmark records requested tolerance, measured `realized_Linf`, compression ratio, fixed-basin error, re-derived Bader error, total electron-count deviation, and the number and fraction of voxels whose Bader labels change after reconstruction.

## 2.3 A chemical contract requires a resolvable reference observable

A Bader-charge threshold \(\tau\) is meaningful only when the reference Bader analysis is stable at that scale. Protocol A.1 measures numerical resolvability by perturbing each reference density with matched-amplitude additive uniform noise. For material \(i\), the perturbation amplitude is

\[
\epsilon_i=\|\mathrm{float32}(\rho_i)-\rho_i\|_\infty.
\]

Five perturbations \(U_s(-\epsilon_i,+\epsilon_i)\) are generated with preregistered seeds \(\{20260905,1,2,3,4\}\). The Bader partition is re-derived after every perturbation, and the Protocol-A.1 stability floor is the maximum atom-wise charge deviation across the five seeds. The chemical contracts evaluated here are \(\tau\in\{10^{-4},10^{-3},10^{-2}\}\) e. A material enters codec certification only when its Protocol-A.1 floor is below the chosen \(\tau\).

This design produces three distinct denominators throughout the paper: successful reconstructions describe codec behavior, Protocol-A.1-admitted systems define chemically evaluable cases, and certified rows identify operating points that satisfy the downstream charge contract. Keeping these levels separate makes the benchmark a test of scientific usability rather than a single compression score.

# 3. Codec error structure

## 3.1 Equal requested tolerances are not equal realized perturbations

All three codecs respect their requested pointwise bounds, but they use those bounds differently. Across successful reconstructions, the median ratio

\[
U=\frac{L_{\infty,\mathrm{realized}}}{L_{\infty,\mathrm{nominal}}}
\]

is 0.1575 for ZFP and approximately 1.000 for both SZ3 and SPERR (Fig. 5a). ZFP therefore operates substantially inside its nominal error budget, whereas SZ3 and SPERR nearly saturate theirs. A comparison at equal requested tolerance consequently mixes two effects: the amount of pointwise perturbation actually introduced and the spatial structure of that perturbation.

This distinction is visible in same-nominal comparisons. At the central nominal relative tolerance of \(10^{-3}\), the re-derived Bader error is much larger for SZ3 and SPERR than for ZFP, but ZFP simultaneously realizes a much smaller \(L_\infty\). Requested tolerance is therefore an operational codec setting, not a common physical perturbation scale.

## 3.2 Matching realized \(L_\infty\) reveals a residual codec-dependent structure

To compare reconstruction structure at similar perturbation magnitude, operating points are matched within each material by measured \(L_\infty\). The primary nonparametric procedure uses mutual nearest neighbours in \(\log_{10}L_\infty\) with a 0.10-decade caliper. At the \(10^{-3}\) e Protocol-A.1 contract, the qualified all-successful analysis gives median Bader-error ratios of 1.90 [1.70, 2.20] for SZ3/ZFP and 1.87 [1.63, 2.08] for SPERR/ZFP.

A conservative complete-case analysis removes every material with any registered downstream failure for any codec at nominal relative tolerance \(\le 0.01\). Twenty materials are removed, leaving 234 development materials. On this common material set, the matched ratios remain 1.82 [1.68, 2.01] for SZ3/ZFP across 119 materials and 2.00 [1.79, 2.25] for SPERR/ZFP across 115 materials (Fig. 5b). Within-material interpolation on common log–log \(L_\infty\) support gives 2.07 [1.95, 2.19] and 1.99 [1.83, 2.21], respectively.

The first compression result is therefore a separation of scales. ZFP gains substantially from lower bound utilization, but realized magnitude does not fully determine the downstream Bader response. After magnitude is aligned, an approximately twofold difference remains and points to reconstruction structure as the next variable to explain.

# 4. QoI / Chemical fidelity

## 4.1 Re-deriving the Bader partition changes the fidelity assessment

Across 4,627 successful base-ladder reconstructions, the re-derived Bader error exceeds the fixed-basin error in 99.7% of cases (Fig. 2a). The pooled median re-derived/fixed ratio is 52.8. The size of the ratio varies strongly with codec and tolerance: at nominal relative tolerance \(10^{-3}\), median paired ratios are 35.3 for SPERR, 2.9 for SZ3, and 70.7 for ZFP; at \(10^{-4}\), the corresponding values are 133.0, 9.0, and 224.2 (Fig. 2b).

The stable conclusion is the direction of the effect. Integrating the reconstructed density over the original basins removes a reconstruction-dependent error channel and therefore produces a systematically smaller estimate of chemical error. The magnitude is codec- and tolerance-dependent because the fixed-basin contribution and the amount of basin motion change differently across operating points. Figure 2 therefore reports both the directional 99.7% result and stratified multiplicative ratios rather than reducing the effect to a single universal factor.

Denominator sensitivity supports the same interpretation. The pooled median resolved/fixed ratio remains 52.8 when denominator floors between \(10^{-15}\) and \(10^{-8}\) e are applied and is 52.6 at a \(10^{-6}\) e floor. A material-balanced aggregation gives 59.5 [50.8, 70.3]. Re-derived analysis is thus the chemically relevant scoring path, while fixed-basin integration serves as a diagnostic that isolates the within-domain contribution.

## 4.2 Bader fidelity is defined only above the numerical resolvability floor

Protocol A.1 shows that the downstream observable itself has a finite numerical resolution. Across all 319 systems, 255 (79.9%) are non-evaluable at \(10^{-4}\) e, 132 (41.4%) at \(10^{-3}\) e, and 31 (9.7%) at \(10^{-2}\) e (Fig. 4a). These fractions establish the usable precision range of the reference analysis under the stated perturbation protocol.

The practical consequence is a two-stage chemical contract. First, the reference Bader analysis must be resolvable at \(\tau\). Second, the compressed reconstruction must satisfy \(\Delta Q_{\mathrm{resolved}}<\tau\). This separation prevents numerical instability of the reference partition from being mixed with codec error and makes the certification threshold an experimentally interpretable property of the full analysis pipeline.

The resolvability pattern is not captured by conventional low-cost metadata. Logistic models based on system type, grid size, atom count, points per atom, and available vacuum/cell descriptors show external AUROC values of 0.409, 0.387, and 0.398 at \(10^{-4}\), \(10^{-3}\), and \(10^{-2}\) e, respectively (Fig. 4d). Direct stability qualification therefore provides information that these metadata do not recover across the tested corpora.

# 5. Mechanism: why \(L_\infty\) fails

## 5.1 Bader error separates into integrand error and domain-migration error

For atomic basin \(a\), the total Bader-charge perturbation can be written as

\[
\Delta Q_a
=
\Delta Q_{a,\mathrm{integrand}}
+
\Delta Q_{a,\mathrm{domain}}.
\]

The integrand term measures the effect of changing density values while retaining the reference basin; the domain term measures the effect of changing the basin itself. In a representative mechanism set of 12 materials spanning the observed stability range, three codecs, and three tolerances, 106 successful material–codec–tolerance cases satisfy this decomposition to a maximum closure residual of \(2.22\times10^{-16}\) e.

Because the two terms can partially cancel, domain dominance is summarized using

\[
f_{\mathrm{domain}}
=
\frac{|\Delta Q_{\mathrm{domain}}|}
{|\Delta Q_{\mathrm{domain}}|+|\Delta Q_{\mathrm{integrand}}|}.
\]

At the maximum-error atom, the median \(f_{\mathrm{domain}}\) is 0.995 with an interquartile range of 0.965–0.999; 84.9% of cases exceed 0.90 (Fig. 3a). In these representative mechanism cases, the dominant measured contribution to Bader-charge error is therefore movement of the integration domain.

## 5.2 Basin reassignment explains the full-benchmark residual left after matching \(L_\infty\)

The direct decomposition identifies the physical error channel, while voxel reassignment provides a scalable full-benchmark measure of how strongly the Bader partition changes. We fit material-fixed-effect models at the \(10^{-3}\) e A.1 contract on common realized-\(L_\infty\) support. A base model includes measured \(L_\infty\), codec, and material identity. An expanded model additionally includes the fraction of voxels whose Bader labels change after reconstruction.

On the conservative complete-case material set, the base model gives codec multipliers of 2.34 for SZ3/ZFP and 2.08 for SPERR/ZFP. Adding voxel reassignment changes those multipliers to 0.96 and 0.94, respectively (Fig. 3d and Fig. 5c). The reassignment term has a log–log coefficient of 0.880 [0.723, 1.037] with \(p=5.78\times10^{-28}\). The approximately twofold residual observed after matching field magnitude is therefore absorbed by a variable that directly records movement of the field-derived partition.

A global electron-count control separates this mechanism from simple integral bias. Adding absolute electron-count deviation to the base model leaves the SZ3/ZFP multiplier at 2.58 and the SPERR/ZFP multiplier at 2.06. When electron-count deviation and reassignment are included together, the electron-count coefficient is \(-0.017\) [\(-0.040,0.006\)], \(p=0.139\), while the reassignment coefficient remains 0.879 [0.722, 1.036], \(p=5.25\times10^{-28}\). The structural redistribution of grid points among Bader basins, rather than a global loss or gain of integrated charge, tracks the codec-associated Bader residual.

## 5.3 The missing information in a pointwise bound is local ordering and domain geometry

A pointwise \(L_\infty\) bound constrains the amplitude of the reconstruction error at every voxel. It does not specify how neighbouring errors are correlated, whether local ascent relations are preserved, or whether the watershed-like basin assignment remains unchanged. Two reconstructions can therefore have similar \(L_\infty\) while producing different local order changes and different basin migration.

This mechanism connects the chemical result to topology- and order-aware compression. TopoSZ preserves extrema and contour-tree relations [5], later methods preserve or correct Morse–Smale structures [7,8], and recent local-order-preserving compression explicitly protects neighbouring value order and critical points [9]. Bader analysis is particularly sensitive to this class of structure because its grid assignments follow local ascent. The benchmark therefore identifies a concrete chemical target for future compressor design: preservation of the discrete relations that define field-derived integration domains.

# 6. Robustness, failure regimes, and implications

## 6.1 Stability-probe calibration reveals an algorithm-aware numerical floor

The stability protocol itself must perturb the mathematical structure used by the downstream algorithm. A deterministic float64→float32→float64 round trip is monotone for unequal values and tends to preserve local order while creating exact ties. For an on-grid Bader watershed, this perturbation is unusually structure-preserving.

Calibration on 18 materials demonstrates the difference. Float32 rounding creates a median 82 exact neighbouring ties, while matched-amplitude additive noise creates none. Zero voxel reassignment occurs in 9/18 systems under float32 rounding and 2/18 under random noise. Across the full 319-system corpus, replacing the archived float32 probe with matched-amplitude noise raises the median stability floor by approximately 8,700-fold in the single-seed comparison. The five-seed Protocol A.1 then changes single-seed eligibility decisions for 35, 17, and 2 systems at \(10^{-4}\), \(10^{-3}\), and \(10^{-2}\) e, respectively.

Probe amplitude also matters. Changing the perturbation amplitude from 0.1× to 10× shifts the floor by a median 0.76 decades across the calibration set. Protocol A.1 is therefore interpreted as a numerical stability floor at a stated perturbation amplitude, with the perturbation family and seed aggregation forming part of the analysis contract.

## 6.2 Registered downstream failures define a distinct operating regime

The benchmark records 77 exceptional downstream events separately from successful reconstructions: 76 Bader-solver failures and one symmetry-equivalent basin-relabeling event. At nominal relative tolerance \(\le 0.01\), 24 registered failures occur across 20 materials, including 20 ZFP cases and four SPERR cases. These events identify a high-distortion regime in which the downstream analysis itself ceases to return a standard comparable output.

The complete-case analysis removes all 20 affected materials and reproduces the central matched-\(L_\infty\) result on the remaining 234 materials: 1.82× for SZ3/ZFP and 2.00× for SPERR/ZFP at \(10^{-3}\) e. The residual therefore persists on a common material support where all three codec families have successful downstream evaluations.

The symmetry-equivalent relabeling case provides a complementary failure mode. For `aflow-Al8Cu4U1_ICSD_601801`, a large position-indexed floor reflects permutation of equivalent Al basins while the charge multiset remains unchanged. Removing this case changes overall non-evaluable fractions only from 79.94% to 79.87%, 41.38% to 41.19%, and 9.72% to 9.43% across the three contracts. This event is useful as a taxonomy example: a numerical workflow can fail through solver breakdown, domain instability, or label equivalence, and those states carry different scientific meanings.

## 6.3 The optimal compression operating point depends on the chemical contract

After Protocol-A.1 qualification, compressor selection becomes a Pareto problem in compression ratio and certification coverage (Fig. 6). At \(10^{-2}\) e for bulk systems, SZ3 reaches a median best certified ratio of 51.8× with 95.2% coverage, while ZFP reaches 30.0× with 98.8% coverage. For slabs, SZ3 reaches 67.8× with 77.0% coverage and ZFP reaches 40.5× with 96.7% coverage.

At \(10^{-3}\) e, bulk ratios converge: 12.9× for SZ3 and 13.5× for ZFP, both near 99% certification. On slabs, ZFP reaches 15.3× with 100% coverage and SZ3 14.1× with 85% coverage. At \(10^{-4}\) e, ZFP leads the bulk frontier at 7.6×, compared with 6.3× for SZ3 and 4.2× for SPERR. Four slab materials are admitted at this strictest contract, giving a small-sample view of the same frontier rather than a population summary.

The practical implication is that codec choice is downstream-contract dependent. Compression ratio alone does not determine the preferred operating point; chemical precision and certification coverage jointly determine which reconstruction is useful.

## 6.4 Implications for chemical data infrastructure and compressor design

The benchmark suggests a general workflow for reusable electronic-structure data. A stored compressed field should carry more than a nominal codec tolerance. Its scientific metadata can include the realized reconstruction error, the downstream analysis used for certification, the numerical resolvability scale of that analysis, and the certified operating range. This converts compression from a storage-only decision into a property-aware data-quality decision.

For Bader analysis, the mechanism points toward order- and domain-aware compression objectives. Protecting local ascent relations, critical structures, or basin geometry is more directly aligned with chemical fidelity than minimizing pointwise amplitude alone. Existing topology- and local-order-preserving compressors [5–9] provide concrete algorithmic families for testing this direction on the benchmark.

The same evaluation logic is naturally applicable to other field-derived analyses. The strongest transfer is expected for observables whose domains, labels, thresholds, or topological objects are reconstructed from the field. In those settings, three questions can be posed in sequence: is the reference QoI numerically resolvable, does reconstruction change the derived structure, and does that structural change control the downstream error? Bader charge supplies a chemically explicit case in which all three questions can be measured directly.

# 7. Conclusion

Pointwise error bounds remain valuable guarantees on reconstructed electron-density fields, but they do not by themselves define chemical fidelity for a field-dependent analysis. In the Bader problem, the missing variable is the response of the integration domains themselves. Re-derived Bader error exceeds fixed-basin error in 99.7% of successful base-ladder reconstructions, and a representative direct decomposition attributes a median 0.995 of the bounded maximum-atom error contribution to domain migration.

Separating nominal tolerance from realized \(L_\infty\) further clarifies the codec comparison. ZFP uses a much smaller fraction of its requested error budget, yet an approximately twofold Bader-error difference remains after realized-error matching. That residual is absorbed when basin reassignment is included in material-controlled models and is not absorbed by global electron-count deviation. The resulting mechanism links reconstruction structure to movement of the Bader partition and then to chemical error.

Finally, chemical certification has a numerical resolution scale of its own. Protocol A.1 identifies 41.4% of the 319-system corpus as non-evaluable at a \(10^{-3}\) e Bader-charge contract, establishing resolvability as a prerequisite for meaningful codec certification. The resulting workflow—measure realized field error, re-derive the downstream structure, qualify the reference QoI, and report a contract-dependent compression frontier—provides a practical route from numerical compression guarantees to scientifically interpretable electronic-structure data.

## Data and Software Availability

The benchmark data, Protocol A.1 stability measurements, failure registry, provenance metadata, mechanism data used in the manuscript, supplementary sensitivity tables, and statistical analysis scripts are maintained in the project repository at https://github.com/stloendays/QoI. A versioned archival release with a persistent identifier will be frozen before formal submission so that the published record maps to an immutable data-and-software snapshot. Source URLs, checksums, and licensing metadata for the underlying material fields are recorded in `materials_metadata.csv`.

## References

1. Diffenderfer, J.; Fox, A. L.; Hittinger, J. A. F.; Sanders, G.; Lindstrom, P. G. Error Analysis of ZFP Compression for Floating-Point Data. *SIAM J. Sci. Comput.* **2019**, *41*, A1867–A1898. DOI: 10.1137/18M1168832.
2. Liang, X.; Zhao, K.; Di, S.; Li, S.; Underwood, R.; Gok, A. M.; Tian, J.; Deng, J.; Calhoun, J. C.; Tao, D.; Chen, Z.; Cappello, F. SZ3: A Modular Framework for Composing Prediction-Based Error-Bounded Lossy Compressors. *IEEE Trans. Big Data* **2023**, *9*, 485–498. DOI: 10.1109/TBDATA.2022.3201176.
3. Li, S.; Lindstrom, P.; Clyne, J. Lossy Scientific Data Compression With SPERR. In *2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*; IEEE, 2023; pp 1007–1017. DOI: 10.1109/IPDPS54959.2023.00104.
4. Jiao, P.; Di, S.; Guo, H.; Zhao, K.; Tian, J.; Tao, D.; Liang, X.; Cappello, F. Toward Quantity-of-Interest Preserving Lossy Compression for Scientific Data. *Proc. VLDB Endow.* **2022**, *16* (4), 697–710. DOI: 10.14778/3574245.3574255.
5. Yan, L.; Liang, X.; Guo, H.; Wang, B. TopoSZ: Preserving Topology in Error-Bounded Lossy Compression. *IEEE Trans. Vis. Comput. Graph.* **2024**, *30* (1), 1302–1312. DOI: 10.1109/TVCG.2023.3326920.
6. Gorski, N.; Liang, X.; Guo, H.; Yan, L.; Wang, B. A General Framework for Augmenting Lossy Compressors With Topological Guarantees. *IEEE Trans. Vis. Comput. Graph.* **2025**, *31*, 3693–3705. DOI: 10.1109/TVCG.2025.3567054.
7. Li, Y.; Xia, M.; Liang, X.; Wang, B.; Guo, H. Preserving Discrete Morse–Smale Complexes in Error-Bounded Lossy Compression. *IEEE Trans. Vis. Comput. Graph.* **2026**, *32* (7), 6593–6609. DOI: 10.1109/TVCG.2026.3684385.
8. Li, Y.; Xia, M.; Liang, X.; Wang, B.; Underwood, R.; Di, S.; Sharma, H.; Beniwal, D.; Cappello, F.; Guo, H. pMSz: A Distributed Parallel Algorithm for Correcting Extrema and Morse-Smale Segmentations in Lossy Compression. In *2026 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*; IEEE, 2026. DOI: 10.1109/IPDPS65963.2026.00025.
9. Fallin, A.; Gorski, N.; Agarwal, T.; Wang, B.; Gopalakrishnan, G.; Burtscher, M. Fast Topology-Aware Lossy Data Compression with Full Preservation of Critical Points and Local Order. *IEEE Trans. Big Data* **2026**. DOI: 10.1109/TBDATA.2026.3705355.
10. Liu, Y.; Jiang, B.; Yang, T.; Di, S.; Underwood, R.; Jin, S. TOPIQ: Statistical Error Propagation for Quantity-of-Interest Prediction under Lossy Compression. Accepted at *SC 2026*; arXiv:2608.26912, 2026. DOI: 10.48550/arXiv.2608.26912.
11. Liu, G.; Li, Y.; Ren, C.; Underwood, R.; Liang, X.; Wang, B.; Di, S.; Cappello, F.; Guo, H. FZ-VIS: A Visual Analytics Framework for Quantities-of-Interest-Aware Scientific Lossy Compression. Accepted at *IEEE VIS 2026 / IEEE Trans. Vis. Comput. Graph.*; arXiv:2608.08386, 2026. DOI: 10.48550/arXiv.2608.08386.
12. Bader, R. F. W. *Atoms in Molecules: A Quantum Theory*; Oxford University Press: Oxford, 1990.
13. Henkelman, G.; Arnaldsson, A.; Jónsson, H. A Fast and Robust Algorithm for Bader Decomposition of Charge Density. *Comput. Mater. Sci.* **2006**, *36*, 354–360. DOI: 10.1016/j.commatsci.2005.04.010.
14. Brehm, M.; Thomas, M. An Efficient Lossless Compression Algorithm for Trajectories of Atom Positions and Volumetric Data. *J. Chem. Inf. Model.* **2018**, *58* (10), 2092–2107. DOI: 10.1021/acs.jcim.8b00501.
15. Gong, J.; Zhao, Z.; Tang, B. Z. Bridging Machine Learning and Electron Density Theory with Adaptive Real-Space Integration. *J. Chem. Theory Comput.* **2026**. DOI: 10.1021/acs.jctc.6c01124.

16. Weaver, S. M.; Warren, S. BaderKit: A Python Package for Grid-based Bader Charge Analysis. *J. Open Source Softw.* **2026**, *11* (121), 9943. DOI: 10.21105/joss.09943.
17. Horton, M. K.; Huck, P.; Yang, R. X.; et al. Accelerated Data-Driven Materials Science with the Materials Project. *Nat. Mater.* **2025**, *24*, 1522–1532. DOI: 10.1038/s41563-025-02272-0.
18. Curtarolo, S.; Setyawan, W.; Wang, S.; Xue, J.; Yang, K.; Taylor, R. H.; Nelson, L. J.; Hart, G. L. W.; Sanvito, S.; Buongiorno-Nardelli, M.; Mingo, N.; Levy, O. AFLOWLIB.ORG: A Distributed Materials Properties Repository from High-Throughput *ab Initio* Calculations. *Comput. Mater. Sci.* **2012**, *58*, 227–235. DOI: 10.1016/j.commatsci.2012.02.002.
19. Draxl, C.; Scheffler, M. The NOMAD Laboratory: From Data Sharing to Artificial Intelligence. *J. Phys. Mater.* **2019**, *2*, 036001. DOI: 10.1088/2515-7639/ab13bb.
20. Nguyen, T. M.; Tawfik, S. A.; Tran, T.; Venkatesh, S. ChargeFlow: Flow-Matching Refinement of Charge-Conditioned Electron Densities. *J. Chem. Theory Comput.* **2026**, *22* (16), 8481–8492. DOI: 10.1021/acs.jctc.6c00585.
