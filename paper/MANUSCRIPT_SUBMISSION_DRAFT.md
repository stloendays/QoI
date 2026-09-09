# Scientific Fidelity Is QoI-Dependent: Certifying Lossy Compression of Electronic Densities

## Abstract

Lossy compression of electronic-structure data is typically controlled by a reconstruction error bound, yet downstream chemical observables need not inherit that bound in a predictable way. We study 6,343 compressed electron-density reconstructions spanning 254 bulk and slab systems and three error-bounded compressors (ZFP, SZ3, and SPERR), and evaluate scientific fidelity through observables with distinct mathematical structure. Preservation of global electron number is an insufficient certificate of local chemical fidelity: among reconstructions with total-electron deviation below 10^-4 e, 43.15% still exceed 10^-3 e in re-derived Bader-charge error. In contrast, the Hartree potential, a linear nonlocal functional of the density, exhibits a smooth near-linear response to realized pointwise perturbation, with an overall log-log exponent of 1.02 and median per-material R^2 of 0.994-0.997 across codecs. Bader charge on the identical reconstructions is substantially less regular: only 32.4% of material-codec pairs are monotone, local response exponents span -9.3 to +14.1, and individual tolerance steps produce charge-error jumps up to 22,296-fold. We further show that fixed-basin evaluation suppresses the domain-migration component of Bader error, that the observable has a material-specific stability floor that must be qualified before compression can be certified, and that equal nominal tolerances across codecs do not imply equal realized perturbations. Within-material matching on realized L-infinity reduces the apparent codec gap substantially but does not eliminate it. The resulting stability-qualified decision pattern reproduces on an untouched 63-system external cohort with zero material-level pipeline failures and zero codec-bound violations. Scientific compression fidelity is therefore determined jointly by the realized reconstruction and the downstream quantity-of-interest operator, rather than by a scalar density norm alone.

**Keywords:** scientific data compression; electronic density; quantity of interest; Bader charge; Hartree potential; error-bounded compression; scientific fidelity

## Introduction

Electronic-structure calculations increasingly produce large three-dimensional fields whose storage, movement, and repeated analysis can become a substantial part of the computational workflow. Electron densities are a canonical example: the field is not merely an output to be archived, but an input to later charge partitioning, electrostatic analysis, visualization, and data-driven workflows. Error-bounded lossy compression has therefore become an important route to scientific-data reduction because it can provide large reductions while maintaining explicit control over reconstruction error [1-4]. The key scientific question, however, is not simply whether the reconstructed field is numerically close to its reference. It is whether the scientific observable extracted from that field remains trustworthy.

Most scientific-compression benchmarks are naturally organized around rate-distortion quantities, including pointwise error, norm-based distortion, and compression ratio, and frameworks such as Z-checker have made systematic post-compression assessment substantially more rigorous [1,5]. These quantities are necessary for characterizing the reconstructed field, but they do not by themselves define downstream scientific fidelity. If a scientific analysis applies an operator Q to a density rho, the relevant perturbation is Q[rho + Delta rho] - Q[rho], not Delta rho in isolation. This gap has motivated explicit quantity-of-interest (QoI) preserving compression, in which downstream analysis error is treated as part of the compression objective [6]. Related work on topology-preserving compression further demonstrates that a pointwise error bound can be insufficient when downstream interpretation depends on topological structure [7].

The present study asks this question in electronic-structure data using three observables chosen to form a deliberate operator hierarchy on the same reconstructed densities (Figure 1). Total electron number is a global linear integral and serves as a conservation control. The periodic Hartree potential is also linear but nonlocal, providing a smooth-field comparator. Bader charge is qualitatively different: it is evaluated by partitioning the density into atom-centered basins bounded by zero-flux surfaces, so its integration domains are themselves functions of the density [8,9]. In a grid-based implementation, each reconstruction can therefore change both the integrand and the partition over which the integrand is evaluated. This makes Bader charge a concrete topology-sensitive QoI rather than simply another scalar error metric.

That distinction exposes three methodological problems that conventional rate-distortion evaluation does not resolve. First, applying a reconstructed density to the reference Bader basins freezes a state-dependent part of the downstream operator and can suppress the error caused by basin migration. Second, a requested chemical tolerance is meaningful only if the uncompressed observable itself is reproducible at that scale under numerically negligible perturbations. Third, codec controls are not automatically commensurate: the same requested tolerance can produce different realized L-infinity perturbations across compressors. A codec-specific scientific advantage can therefore be interpreted only after separating intrinsic QoI stability, realized distortion magnitude, and residual error-field structure.

Here we construct a frozen QoI-aware certification benchmark around 6,343 compressed electron-density reconstructions from 254 bulk and slab systems and three error-bounded compressors: ZFP [2], SZ3/SZ [3], and SPERR [4]. We first compare electron-number conservation, Hartree-potential error, and re-derived Bader error on identical reconstructions. We then quantify stability-qualified certification, correct the numerical qualification probe in Protocol A.1, decompose the Bader response into fixed-basin and domain-migration contributions, and match codec outputs within material on realized L-infinity. Finally, we apply the frozen decision rules to an untouched 63-system external confirmatory cohort. The resulting framework treats compression quality as a property of the pair (reconstruction, downstream QoI operator), rather than as a property of the codec alone.

## Results

### Pointwise reconstruction control is not a scientific fidelity guarantee

The benchmark contains 6,343 frozen reconstruction rows over 254 electronic-density fields, comprising 186 bulk systems and 68 slabs, with ZFP, SZ3, and SPERR evaluated over base and tight tolerance ladders. The central question is not whether a reconstruction satisfies a numerical field error alone, but whether that controlled perturbation preserves the observable subsequently extracted from the field.

Total electron number provides a stringent negative control because it is a global linear integral of the density. Across the benchmark, electron-count deviation is typically much smaller than re-derived Bader-charge error. More importantly, the two fidelity criteria decouple directly: 3,205 reconstructions satisfy |Delta N_e| < 10^-4 e while retaining a finite re-derived Bader result, yet 1,383 of these (43.15%) have Bader error >= 10^-3 e. Tight global conservation is therefore insufficient to certify atom-resolved charge fidelity.

### The downstream QoI operator determines the error-propagation regime

To separate perturbation magnitude from observable structure, we evaluate the periodic Hartree potential on the same frozen reconstructions. The Hartree map is linear and nonlocal, with the G = 0 component gauge-fixed to zero. The primary fidelity metric is the relative RMS potential error, RMS(V_recon - V_ref) / RMS(V_ref).

The full expansion reproduces all 6,343 frozen rows. ZFP and SPERR pass the frozen reconstruction gate on 100% of rows and SZ3 on 96.2%. The 73 excluded SZ3 rows reproduce realized L-infinity to within 2e-5 relative but differ in compressed byte count because part of the frozen SZ3 corpus was generated on a different platform. These rows are retained explicitly as infrastructure-level reproduction mismatches rather than silently removed.

Across the 6,270 gate-passing rows, Hartree-potential error follows an approximately first-order response to the realized density perturbation (Figure 2). The pooled exponent is 1.02, every codec-by-stratum cell lies between 0.91 and 1.12, and median material-level R^2 is 0.997 for ZFP, 0.994 for SZ3, and 0.996 for SPERR. Hartree error is strictly monotone in 88.6% of material-codec pairs overall. Slab ladders show more local reversals than bulk ladders, so the supported statement is a smooth approximately power-law response rather than universal strict monotonicity.

Bader charge behaves differently on the identical reconstructed fields. Its pooled log-log slopes are shallower (0.53-0.67 by codec and stratum), R^2 is lower in every codec-by-stratum cell, and only 32.4% of material-codec pairs are strictly monotone. Local response exponents span -9.3 to +14.1, compared with -2.0 to +4.4 for the Hartree potential. The most extreme frozen single-rung Bader jump is 22,296-fold for mp-676693 under ZFP, even though the Hartree response on the same material has R^2 = 0.999.

The contrast is not reducible to one observable merely having a larger error scale. When reconstructions are grouped into 0.5-decade bins of comparable Hartree-potential error, 55.4% of all gate-passing rows fall in bins where the Bader-error P90/P10 ratio is at least 10. Similar smooth-field fidelity therefore does not uniquely determine topology-dependent local fidelity.

### Chemical certification is a stability-aware decision problem

A downstream chemical contract is scientifically interpretable only when the observable is itself identifiable at the requested tolerance. We therefore separate *eligibility* from *codec success*. A material-threshold pair first has to pass the Protocol A.1 Bader-stability qualification; only then can a reconstructed density be counted as certified when its re-derived Bader error lies below the requested chemical tolerance.

This distinction changes the interpretation of apparent success (Figure 3). At tight tolerances, the stability floor places a material-level ceiling on how much of the corpus can be evaluated at all. Counting only the downstream error criterion while ignoring eligibility systematically overstates scientific success because non-identifiable material-threshold pairs are treated as if their reported charge errors represented meaningful measurements. The benchmark therefore reports three distinct states: eligible and certified, eligible but not certified, and non-evaluable because the uncompressed Bader observable is unstable at the requested precision.

### The QoI stability floor depends on the measurement protocol

The original Protocol A is retained unchanged as provenance. Its float32 round-trip probe, however, is strongly order-preserving and proved insufficiently sensitive to the watershed-like tie-breaking that can change a grid-based Bader partition. Protocol A.1 therefore changes the probe, not the scientific contract: five fixed-seed uniform perturbations are applied at an amplitude equal to the float32 L-infinity scale, while the tolerance set, exclusion semantics, and reporting rules remain frozen.

The corrected probe materially changes the inferred stability floor (Figure 4). On the paired development subset, the shift is highly heterogeneous rather than a simple global rescaling, demonstrating that the correction cannot be represented by multiplying every material by one constant. Across the combined development and external systems, the A.1 floor directly sets the measurable cohort at each chemical tolerance. Approximately 80% of systems are not evaluable at a 10^-4 e Bader contract and 41% are not evaluable at 10^-3 e. A compressor therefore cannot be credited or penalized for a precision that the downstream observable itself cannot resolve.

### Topology-induced basin migration explains irregular Bader response

Bader analysis differs from the preceding controls because the integration domain Omega_A[rho] is itself a functional of the density [8,9]. The re-derived charge change can therefore be decomposed conceptually into an integrand contribution and a domain-migration contribution,

Delta Q_total = Delta Q_integrand + Delta Q_domain.

Evaluating a reconstruction on the reference basins suppresses the second term and changes the downstream operator being measured. The corrected fidelity metric therefore re-solves the Bader partition after every reconstruction.

Mechanism analysis shows that the resulting domain term can dominate the relevant tight-tolerance response in representative systems (Figure 5). Re-solved errors can depart strongly from their fixed-basin counterparts, per-atom decompositions expose signed domain-migration contributions, and full tolerance ladders show abrupt Bader jumps even when the field perturbation changes smoothly. Across the frozen benchmark, rung-to-rung jump severity is associated with basin reassignment. This association is used descriptively; the data support topology-driven domain migration as a Bader-specific mechanism, not a universal causal model for every downstream scientific observable.

### Nominal codec tolerance must be replaced by realized perturbation

Requested codec tolerances are not a common distortion scale. At equal nominal tolerance, ZFP realizes only about 0.17 times the L-infinity perturbation of SZ3 or SPERR, whereas SZ3 and SPERR are close to one another (Figure 6a). Equal-nominal comparisons therefore conflate the magnitude of the perturbation with any difference in its spatial structure.

We address this confounding by matching reconstructions within material on log10(realized L-infinity), without replacement, using a primary caliper of 0.10 dex. Matching substantially reduces the apparent ZFP advantage but does not eliminate it (Figure 6b-d). At the primary caliper, re-derived Bader error for matched ZFP reconstructions is 0.557 times that of SZ3 and 0.601 times that of SPERR, whereas SZ3 and SPERR are statistically similar in Bader error. The residual supports an error-structure contribution beyond scalar L-infinity magnitude, but does not identify a unique geometric statistic responsible for that residual.

### Stability-qualified decisions reproduce on untouched external systems

The frozen external confirmatory cohort contains 63 completed systems and 1,689 retained scientific rows. There are zero material-level pipeline failures and zero codec error-bound violations; three row-level Bader-solver failures remain visible in the audit rather than being promoted to material-level failures. No thresholds or selection rules were retuned on the external cohort.

The confirmatory data reproduce the tolerance-dependent decision pattern (Figure 7). At 10^-4 e, the external median best-certified compression ratios are approximately 13.0x for ZFP, 12.1x for SZ3, and 5.2x for SPERR. At 10^-3 e, ZFP and SZ3 are essentially tied at about 18.8x and both exceed SPERR at about 6.4x. At 10^-2 e, SZ3 rises to about 65.9x, ahead of ZFP at 40.6x and SPERR at 10.8x. The pairwise transition is correspondingly sharp: SZ3 beats ZFP in 31% of eligible external materials at 10^-4 e, 36% at 10^-3 e, and 89% at 10^-2 e.

The external cohort also reproduces the realized-distortion asymmetry: certified ZFP points use only a small fraction of their nominal L-infinity budget, whereas SZ3 and SPERR cluster near full budget use. Protocol A.1 eligibility increases from 16/63 systems at 10^-4 e to 42/63 at 10^-3 e and 57/63 at 10^-2 e. The practical output is therefore not a universal codec leaderboard, but a stability-qualified rate-fidelity frontier whose ordering depends on the scientific tolerance.

## Methods

### Frozen benchmark and study design

The study was organized as a frozen row-level benchmark in which each scientific conclusion is traceable to a specific reconstructed electron density and downstream evaluation. The primary corpus contains 6,343 reconstruction rows spanning 254 density fields: 186 bulk systems and 68 slab systems. Each field was evaluated with ZFP [2], SZ3/SZ [3], and SPERR [4] over base and extended tight-tolerance ladders. Once a protocol or benchmark table was frozen, subsequent analyses consumed the frozen outputs rather than silently regenerating or replacing earlier results.

The benchmark records material identity, structural stratum, codec, requested tolerance, realized reconstruction error, compressed size, compression ratio, downstream QoI errors, and stability-qualification state. Rows that failed a pre-specified reproduction gate were retained as provenance. In the Hartree expansion, 73 SZ3 rows closely reproduced realized L-infinity but differed in compressed byte count because part of the frozen corpus had been generated on a different platform; these rows were excluded only from gate-dependent Hartree summaries and remain explicitly audited.

### Reconstruction controls and realized distortion

Requested codec tolerance was treated as an input control rather than a common physical distortion scale. The primary field-level distortion variable was the realized L-infinity error of the reconstructed density; normalization by the density peak-to-peak range was used where a scale-free comparison was required. Compression ratio was computed from the frozen uncompressed and compressed byte counts.

Codec comparisons at equal nominal tolerance were retained only as diagnostics. For scientific comparisons intended to separate distortion magnitude from residual codec effects, reconstructed fields were matched within material on log10(realized L-infinity), without replacement, using a primary caliper of 0.10 dex. Effects were then summarized on the matched pairs for re-derived Bader error, compression ratio, and Protocol A.1 certification.

### Electron number and Hartree potential

Total electron number was used as a global linear control. The absolute electron-count deviation was compared directly with the re-derived Bader error for the same reconstruction rows.

The periodic Hartree potential was used as a linear nonlocal comparator. For nonzero reciprocal vectors, the potential is proportional to rho(G)/|G|^2, with the G = 0 component gauge-fixed to zero. The primary metric was the relative root-mean-square deviation between reconstructed and reference potentials. Pooled log-log slopes, material-level R^2, strict rung-to-rung monotonicity, and local response exponents were analyzed separately so that strong overall regularity did not conceal local reversals.

### Re-derived Bader charge

Bader partitioning assigns a density grid to atom-centered basins through the topology of the charge density [8,9]. Because the basin Omega_A[rho] depends on rho, Bader fidelity was evaluated by recomputing the partition for every reconstructed density before atomic charges were compared with the reference. Fixed-basin calculations were retained only as a mechanistic comparator; they were not used as the primary scientific-fidelity contract.

The mechanism analysis decomposes the re-derived charge change conceptually into the density change inside the reference basin and the additional contribution produced by changing the basin itself. Representative per-atom decompositions were combined with full-benchmark ladder diagnostics to relate irregular Bader jumps to basin reassignment. The reported associations are descriptive and do not assume that reassigned voxel fraction is a complete causal statistic.

### Protocol A.1 stability qualification

A downstream tolerance tau was considered scientifically evaluable only when the uncompressed Bader observable was stable below that scale. Protocol A remains archived provenance. Protocol A.1 replaces the archived float32 round-trip probe with five fixed-seed uniform-noise probes whose amplitude is equal to the float32 L-infinity perturbation scale; the tolerance set, exclusion semantics, and reporting rules are unchanged.

The maximum induced re-derived Bader charge deviation across the five probes defines the material-specific A.1 stability floor. The main chemical tolerances are 10^-4, 10^-3, and 10^-2 e. A material-threshold pair is eligible only when its A.1 floor lies below the requested tolerance. A reconstruction can then be certified only if the pair is eligible and the re-derived Bader error is below tau. Non-evaluable pairs are neither counted as successes nor failures.

### Rate-fidelity and external confirmation

For every eligible material-threshold pair, the best certified reconstruction was selected from the frozen codec ladder and its compression ratio was retained. Material-level summaries produce a stability-qualified rate-fidelity frontier rather than a single global ranking.

The external confirmatory cohort was kept separate from development analysis and contains 63 completed systems with 1,689 retained rows. Frozen protocol rules were applied without retuning. Confirmatory outcomes include material-level completion, codec error-bound behavior, tolerance-dependent rate-fidelity ordering, A.1 eligibility, and realized-distortion asymmetry. External analysis was also used to test the scope of structural generalizations; the completed cohort does not support a universal bulk-versus-vacuum stability distinction.

### Statistical analysis and figure reproducibility

Positive-valued distortion/error relationships were analyzed in log-log space. Material-level fits were emphasized when material-dependent prefactors produced vertical offsets in pooled data. Strict monotonicity was reported separately from R^2. Bader dispersion at comparable smooth-field fidelity was evaluated as the P90/P10 Bader-error ratio within 0.5-decade Hartree-error bins.

Confidence intervals shown for frozen material-level and external summaries were generated by the corresponding bootstrap analyses recorded in the repository. Realized-distortion matching used the pre-specified 0.10-dex primary caliper and was performed within material without replacement. Formal manuscript figures are generated from versioned R source files and frozen CSV inputs, with PNG, PDF, and SVG exported from the same source so that raster and vector manuscripts use identical data and geometry.

## Discussion

The principal result is that a density reconstruction error does not have a unique scientific meaning. The same reconstructed field can preserve a global integral, perturb a smooth nonlocal potential in an approximately first-order manner, and simultaneously produce strongly irregular error in a topology-dependent atomic partition. The relevant object is therefore not a norm of Delta rho alone, but the composition Q[rho + Delta rho], where Q is the downstream scientific operator.

This conclusion is consistent with the broader move from raw-data distortion assessment toward QoI-aware scientific compression [5,6], but it sharpens that principle in two ways. First, the complete downstream operator must be evaluated: freezing Bader basins changes the operator and suppresses the topology-driven domain term. Second, the QoI must be numerically identifiable at the target tolerance before compression success can be defined. Error-bounded reconstruction and downstream certification are therefore related but distinct guarantees.

The comparison with TopoSZ is also instructive [7]. Topology-preserving compression demonstrates that preserving critical structure may require information beyond a scalar pointwise error bound. The present work does not claim that Bader partitioning is equivalent to contour-tree topology, nor that one topology statistic universally predicts downstream scientific error. Instead, Bader analysis supplies a deeply validated chemistry-specific example in which a density-dependent partition can migrate under small field perturbations and thereby generate a discontinuous component of the reported observable.

Protocol A.1 adds a measurement-theoretic qualification to this picture. Even a formally exact compressor cannot certify an observable at a tolerance below the reproducibility of the observable itself under numerically negligible perturbations. Scientific compression should therefore separate two questions: whether a QoI is identifiable at the requested tolerance, and, conditional on that eligibility, how much data reduction preserves it. Treating non-identifiable cases as compression failures would conflate properties of the downstream measurement with properties of the codec.

Realized-distortion matching provides a parallel qualification for codec comparisons. Equal nominal tolerances create a misleading test because the compressors use the nominal budget differently. After matching actual L-infinity perturbation, much of the apparent codec gap disappears, while a smaller residual remains. That residual is consistent with an error-structure contribution but does not, by itself, establish a unique geometric mechanism. This boundary is important: the benchmark supports realized-distortion-controlled scientific comparisons, not a claim that one scalar descriptor fully explains why two error fields with the same L-infinity norm can produce different Bader responses.

Finally, the untouched external cohort shows that the framework remains useful as a decision procedure. The same tolerance-dependent ordering, A.1 eligibility logic, and realized-budget asymmetry appear without retuning. At the same time, an initially plausible bulk-versus-vacuum stability generalization does not survive external confirmation. This negative result strengthens the central methodological point: QoI stability should be measured rather than inferred from a simple material class.

## Conclusions

Scientific fidelity cannot be inferred from a scalar reconstruction bound alone. On identical compressed electron densities, total electron number, Hartree potential, and Bader charge occupy distinct error-propagation regimes that reflect their operator structure. Global conservation can coexist with failed local charge fidelity; the Hartree potential responds smoothly and approximately first-order to realized perturbation; and Bader charge can change irregularly because its density-dependent integration domains themselves migrate.

A defensible compression decision therefore requires four linked steps: evaluate the complete downstream operator, qualify the intrinsic stability of the QoI, compare codecs using realized rather than nominal distortion, and report rate-fidelity only on scientifically eligible cases. Under this framework, lossy compression remains practically useful, but there is no universal codec ranking independent of the QoI and target tolerance. Compression quality is a property of the pair (reconstruction, downstream scientific operator), not of the compressor alone.

## References

1. Di, S. *et al.* A survey on error-bounded lossy compression for scientific datasets. **ACM Computing Surveys** (2025). https://doi.org/10.1145/3733104.
2. Lindstrom, P. Fixed-rate compressed floating-point arrays. **IEEE Transactions on Visualization and Computer Graphics** **20**, 2674-2683 (2014). https://doi.org/10.1109/TVCG.2014.2346458.
3. Di, S. & Cappello, F. Fast error-bounded lossy HPC data compression with SZ. In **2016 IEEE International Parallel and Distributed Processing Symposium (IPDPS)**, 730-739 (IEEE, 2016). https://doi.org/10.1109/IPDPS.2016.11.
4. Li, S., Lindstrom, P. & Clyne, J. Lossy scientific data compression with SPERR. In **2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)**, 1007-1017 (IEEE, 2023). https://doi.org/10.1109/IPDPS54959.2023.00104.
5. Tao, D., Di, S., Guo, H., Chen, Z. & Cappello, F. Z-checker: A framework for assessing lossy compression of scientific data. **The International Journal of High Performance Computing Applications** **33**, 285-303 (2019). https://doi.org/10.1177/1094342017737147.
6. Jiao, P., Di, S., Guo, H., Zhao, K., Tian, J., Tao, D., Liang, X. & Cappello, F. Toward quantity-of-interest preserving lossy compression for scientific data. **Proceedings of the VLDB Endowment** **16**, 697-710 (2022). https://doi.org/10.14778/3574245.3574255.
7. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving topology in error-bounded lossy compression. **IEEE Transactions on Visualization and Computer Graphics** **30**, 1302-1312 (2024). https://doi.org/10.1109/TVCG.2023.3326920.
8. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. **Computational Materials Science** **36**, 354-360 (2006). https://doi.org/10.1016/j.commatsci.2005.04.010.
9. Tang, W., Sanville, E. & Henkelman, G. A grid-based Bader analysis algorithm without lattice bias. **Journal of Physics: Condensed Matter** **21**, 084204 (2009). https://doi.org/10.1088/0953-8984/21/8/084204.

## Data and code availability

The frozen benchmark tables, Protocol A.1 stability outputs, matched-realized-distortion analyses, mechanism-decomposition outputs, external confirmatory evidence, and R source files used to generate the formal manuscript figures are versioned in the project repository at `https://github.com/stloendays/QoI`. Archived protocol outputs are retained alongside the operative A.1 analysis so that the numerical qualification change remains auditable.
