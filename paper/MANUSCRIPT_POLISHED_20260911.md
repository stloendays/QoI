# Stability-Qualified Certification of Lossy Compression for Electronic-Density QoIs

**Submission-facing polished manuscript — 2026-09-11.** This version integrates the audited 21-reference literature set directly into the manuscript and supersedes the earlier citation-light draft for prose/citation review. Numerical claims remain tied to the frozen benchmark assets.

## Abstract

Scientific-compression benchmarks often judge reconstructed data against a downstream quantity-of-interest (QoI) tolerance, but such a tolerance is interpretable only if the reference analysis itself is numerically identifiable at that scale. We introduce a stability-qualified certification framework for lossy compression of electronic densities in which QoI eligibility is established before any compressor is scored. The study contains 6,343 frozen reconstructions of 254 bulk and slab densities generated with ZFP, SZ3, and SPERR, together with an untouched 63-system external cohort. Bader charge is used as a deeply validated topology-sensitive chemical QoI, while total electron number and the periodic Hartree potential provide global-linear and linear-nonlocal controls. Under Protocol A.1, a material-specific Bader stability scale is measured from five fixed-seed perturbations at the float32 L-infinity scale. Across 319 development and external systems, 79.9% are non-evaluable at a 10^-4 e Bader contract, 41.4% at 10^-3 e, and 9.7% at 10^-2 e. The consequence for benchmark semantics is large. On the 254-system development corpus, 518 of 533 apparent binary failures (97.2%) at 10^-4 e and 296 of 310 (95.5%) at 10^-3 e occur on material-threshold pairs that fail the independent stability qualification, leaving only 15 and 14 genuine failures among eligible pairs. Eligibility is not a permissive filter: at 10^-4 e, 106 of 229 naive passes (46.3%) are also non-evaluable. On identical reconstructions, Hartree-potential error exhibits an approximately first-order response to realized field perturbation, whereas re-derived Bader charge is substantially less regular because its density-dependent integration domains can migrate. At the strictest certified contract, median resolved-Bader-error-to-stability-floor ratios are 1.09-1.33 across codecs, consistent with an emerging analysis-limited regime but not establishing a universal plateau-floor identity. Equal nominal codec tolerances also produce unequal realized perturbations; matching within material on realized L-infinity removes much, but not all, of the apparent codec difference. The frozen eligibility and certification rules reproduce on the external cohort without retuning. The resulting benchmark separates genuine compression-induced violations from scientifically non-evaluable targets and replaces an unconditional codec leaderboard with a stability-qualified rate-fidelity decision problem.

**Keywords:** scientific data compression; quantity of interest; benchmark validity; Bader charge; electronic density; numerical stability; error-bounded compression; scientific fidelity

## Introduction

Scientific simulations and electronic-structure calculations increasingly generate floating-point data volumes that are expensive to store, move, and revisit, making lossy compression an established component of the scientific-data-reduction landscape [1,18]. Error-bounded methods are attractive because they expose explicit control over reconstruction distortion, while different codec families realize that control through substantially different representations and algorithms [1]. The present benchmark uses three established families: ZFP, SZ3, and SPERR [2-4]. Compression is also directly relevant to quantum chemistry and electronic-structure workflows: PaSTRI was developed for error-bounded reduction of two-electron integrals [21], SZ3 has been evaluated on GAMESS quantum-chemistry data [3], and recent work has explored threshold-based lossy compression of atomic-orbital spaces in density-functional calculations [19]. These studies establish domain relevance, but they do not address certification of a stored real-space electron-density field against a downstream Bader-charge tolerance.

Electron density is not merely an archival field. It is re-used for charge partitioning, electrostatic analysis, feature extraction, visualization, and downstream data-driven workflows. The central difficulty is therefore not only whether a reconstructed density satisfies a field-level norm, but whether later scientific analyses remain trustworthy. Conventional post-compression assessment frameworks such as Z-checker systematically characterize distortion in reconstructed scientific data [5]. A separate line of work has moved further toward derived quantities: multilevel reduction methods provide quantitative control of accuracy in derived quantities [12], and QoI-preserving compression explicitly treats downstream quantities as design targets rather than incidental diagnostics [6]. Application-facing pipelines have likewise been developed to preserve scientifically important QoIs in fusion data, including constraint-based and learned approaches and scalable online implementations [13,14,20].

These advances establish that raw-data error alone is not a sufficient description of scientific fidelity. Topology-aware compression sharpens the same point from a structural perspective: TopoSZ constrains topological features in addition to pointwise error [7], and a later general framework augments multiple lossy compressors with contour-tree guarantees [15]. More recently, TOPIQ has proposed statistical propagation from compression metadata to QoI-level bias and uncertainty [11]. The question addressed here is therefore deliberately narrower and logically prior to these preservation or prediction tasks: **when is a requested QoI tolerance itself a valid benchmark for judging a compressor?**

That question matters whenever the downstream analysis has its own numerical sensitivity. A scientific threshold `tau` is meaningful as a compression contract only if the reference analysis can itself distinguish changes at that scale. Otherwise, an observed failure to satisfy `tau` can mix two conceptually different quantities: error introduced by reconstruction and instability intrinsic to the downstream analysis procedure. Treating both as codec failure creates a benchmark-validity problem. The evaluation must first establish whether a material-QoI-threshold combination is numerically eligible and only then ask whether a compressed reconstruction satisfies the scientific contract.

Bader charge provides a stringent setting in which to test this logic. In the quantum theory of atoms in molecules, atomic regions are defined from the topology of the electron-density gradient field [17]. Practical Bader algorithms assign or integrate grid volume according to gradient-ascent basins, and the literature has progressively addressed robustness, lattice bias, integration accuracy, and convergence on discrete grids [8,9,16]. More general treatments of topological analysis on arbitrary grids make the dependence on numerical representation explicit [10]. Consequently, a perturbation can alter not only the density values integrated inside an atomic region but also the basin assignment itself. The downstream operator is state-dependent because the integration domain changes with the reconstructed field. Bader sensitivity is therefore not presented here as a new fact; it supplies a concrete chemical case in which benchmark eligibility, complete downstream re-execution, and mechanism-aware certification can be tested at scale.

We compare Bader charge with two controls evaluated on the same reconstructions. Total electron number is a global linear integral. The periodic Hartree potential is linear but nonlocal and provides a smooth-field comparator. This operator hierarchy is used to separate a general benchmark-validity contribution from the chemistry-specific mechanism. The objective is not to rank the importance of the observables, but to determine how the same reconstruction perturbation propagates through operators with different mathematical structure.

The benchmark contains 6,343 frozen reconstruction rows spanning 254 development density fields, including 186 bulk systems and 68 slabs, compressed with ZFP, SZ3, and SPERR over base and tight tolerance ladders. Protocol A.1 independently measures a material-specific Bader stability scale before codec certification. Each material-threshold pair is then assigned to one of three states: **eligible and certified**, **eligible but not certified**, or **non-evaluable because the uncompressed Bader observable is unstable at the requested precision**. We additionally re-derive Bader basins after every reconstruction, decompose representative errors into fixed-domain and domain-migration contributions, and match codec outputs within material by realized rather than nominal L-infinity distortion. Finally, we apply the frozen rules to an untouched 63-system external cohort.

The resulting contribution is a stability-qualified scientific-compression benchmark. It makes a logical distinction that is hidden by unconditional binary reporting: a compressor should be penalized for violating a scientific tolerance only when that tolerance is independently resolvable by the downstream analysis. This distinction converts QoI fidelity from an unconditional error threshold into an auditable measurement contract.

## Results

### A scientific tolerance must be qualified before it can be used as a compression contract

Protocol A.1 defines the numerical eligibility of the Bader charge independently of codec output. For each material, five fixed-seed uniform perturbations are applied at an amplitude equal to the material's float32 L-infinity perturbation scale. The maximum re-derived Bader deviation across the five probes defines the material-specific stability floor. The main chemical tolerances are 10^-4, 10^-3, and 10^-2 e. A material-threshold pair is eligible only when the measured A.1 floor is below the requested tolerance.

This qualification strongly constrains the strictest contracts. Across the combined 319 development and external systems, 79.9% are non-evaluable at 10^-4 e, 41.4% are non-evaluable at 10^-3 e, and 9.7% are non-evaluable at 10^-2 e. These values do not describe compressor failure rates. They describe the fraction of systems for which the requested Bader precision is not independently supported by the frozen numerical qualification procedure.

The resulting decision space has three states. An **eligible-certified** reconstruction belongs to a material-threshold pair that passes the stability qualification and has re-derived Bader error below `tau`. An **eligible-not-certified** reconstruction belongs to a numerically identifiable pair but violates the Bader contract after compression. A **non-evaluable** pair has a stability floor at or above `tau` and is excluded from codec pass/fail scoring at that precision. The third state is essential: assigning it to either the pass or failure class would attach a scientific label at a precision the downstream measurement does not independently resolve.

### Stability qualification overturns the binary benchmark at strict Bader thresholds

We next asked how much the benchmark changes when the eligibility test is applied before codec scoring. Figure 3 makes this comparison on the development corpus using one material-codec decision as the unit of analysis. At each threshold there are 254 materials × 3 codecs = 762 decisions. Under naive binary reporting, which applies the Bader error threshold while ignoring eligibility, the benchmark contains 533 apparent failures at 10^-4 e, 310 at 10^-3 e, and 108 at 10^-2 e (Fig. 3A).

The stability-qualified view is markedly different (Fig. 3B). At 10^-4 e, the same 762 decisions resolve into 123 certified cases, 15 genuine eligible failures, and 624 non-evaluable cases. At 10^-3 e, they resolve into 415 certified, 14 genuine eligible failures, and 333 non-evaluable cases. At 10^-2 e, the corresponding counts are 640, 47, and 75. The key effect is therefore not a small correction to a pass rate but a change in the state space used to interpret the benchmark.

Among the naive failures, **518 of 533 (97.2%) at 10^-4 e and 296 of 310 (95.5%) at 10^-3 e are reclassified as non-evaluable after Protocol A.1 qualification**, leaving only 15 and 14 genuine failures among eligible pairs, respectively (Fig. 3C). Even at 10^-2 e, 61 of 108 apparent failures (56.5%) occur on non-evaluable material-threshold pairs. This correction is not a device for making codecs appear more successful. Eligibility also invalidates naive passes: at 10^-4 e, 106 of 229 apparent passes (46.3%) occur on non-evaluable pairs. Thus, both positive and negative binary labels can be scientifically invalid when the requested QoI tolerance lies below the independently measured numerical stability scale.

Figure 3 therefore establishes the central benchmark-validity result of this study: at strict Bader contracts, unconditional binary pass/fail reporting is dominated by decisions for which the downstream observable is not independently evaluable. The scientifically meaningful benchmark is three-state rather than binary.

### Conventional reconstruction fidelity motivates, but does not define, the certification problem

The same frozen reconstructions demonstrate why a downstream contract cannot be replaced by a generic field-level metric. Total electron number is used as a global linear control. Among 3,205 reconstructions with total-electron deviation below 10^-4 e and a finite re-derived Bader result, 1,383 (43.15%) still have Bader error at or above 10^-3 e. Tight conservation of a global integral is therefore insufficient to certify atom-resolved Bader fidelity.

The periodic Hartree potential supplies a stronger smooth-field comparator. Across 6,270 reconstruction-gate-passing rows, Hartree-potential error follows an approximately first-order response to realized density perturbation. The pooled log-log exponent is 1.02, and median material-level R^2 is 0.997 for ZFP, 0.994 for SZ3, and 0.996 for SPERR. These results establish a comparatively regular response on the same reconstructed fields.

Re-derived Bader charge is markedly less regular. Only 32.4% of material-codec pairs are strictly monotone across the tolerance ladder, and local response exponents span -9.3 to +14.1. Individual frozen tolerance steps can produce very large charge-error jumps, including a 22,296-fold illustrative case. At comparable Hartree-potential error, Bader-error dispersion remains broad: 55.4% of gate-passing rows lie in 0.5-decade Hartree-error bins whose Bader-error P90/P10 ratio is at least 10. Thus, similar smooth-field fidelity does not uniquely determine the local topology-sensitive response.

These observations are not used to claim that QoI dependence is newly discovered. Their role in the present framework is to show why the downstream operator must be included in the measurement contract before benchmark validity can be assessed.

### Protocol A.1 corrects a misleading stability probe

The original Protocol A is retained unchanged as provenance. Its float32 round-trip probe was found to be strongly order-preserving and therefore insufficiently sensitive to the watershed-like tie-breaking that can change an on-grid Bader partition. A probe can appear artificially stable when it preserves the local ordering on which the partition algorithm depends.

Protocol A.1 changes the probe rather than the scientific tolerance set or reporting semantics. It uses five pre-specified fixed-seed uniform perturbations with amplitude tied to the float32 L-infinity scale and takes the maximum induced re-derived Bader deviation as the material stability floor. The five-seed maximum is deliberately conservative: seed sensitivity is treated as uncertainty in the qualification procedure rather than optimized away after inspection.

The correction changes the inferred floor heterogeneously across materials, not by a simple multiplicative rescaling. This observation is methodologically important for certification: the numerical qualification procedure must be validated against the structure of the downstream operator. A stability test that cannot excite the relevant failure channel is not a meaningful basis for declaring a QoI measurable.

### The strictest certified regime becomes floor-scale

The extended tight-tolerance ladder is interpreted as a regime-identification experiment rather than merely as an effort to push codec settings lower. If compression-induced perturbation were the only relevant error source, progressively tighter reconstruction would be expected to continue reducing downstream error in a commensurate manner. For a topology-sensitive numerical analysis, however, the observed response can approach the scale of the numerical instability of the downstream evaluation itself.

The frozen floor-normalized analysis supports this interpretation at the strictest contract without establishing a universal plateau law. At 10^-4 e, the median resolved-Bader-error-to-A.1-floor ratio among certified points is 1.09 for ZFP, 1.33 for SZ3, and 1.23 for SPERR; the corresponding P90 values are 3.25, 2.86, and 3.20. The certified reconstruction error is therefore already on the same order as the independently measured stability floor. At 10^-3 e, the medians increase to 2.78-3.55× the floor, and at 10^-2 e to 10.7-14.6×, indicating a progressive return to a regime in which codec-induced error is larger than the analysis floor.

We therefore describe the 10^-4 e regime as **floor-scale and consistent with an emerging analysis-limited regime**. The current frozen analysis does not establish a material-by-material identity between a tight-ladder plateau and the A.1 stability floor, and no such universal equality is claimed.

### Basin migration identifies the Bader-specific error channel

Bader analysis differs from the linear controls because its integration domain depends on the input density. For atom `A`, the reconstructed charge can be written conceptually as an integral over a basin `Omega_A[rho_recon]`, whereas the reference charge uses `Omega_A[rho_ref]`. The total charge change therefore contains both an integrand contribution and a domain-migration contribution.

Fixed-basin evaluation suppresses the latter term by applying the reconstructed density to the reference basin labels. That procedure changes the downstream operator and is retained only as a mechanistic diagnostic. The scientific-fidelity metric used for certification re-solves the Bader partition after every reconstruction.

Representative per-atom decompositions show that domain migration can dominate the tight-tolerance Bader response. Full tolerance ladders likewise contain abrupt Bader changes despite smoothly changing field distortion. These results give a chemistry-specific explanation for why a small reconstruction norm can coexist with irregular downstream response. They do not imply that every QoI shares the same mechanism, nor that one scalar voxel-reassignment statistic fully predicts the error.

### Equal nominal codec tolerance is not equal realized distortion

A second benchmark-validity issue arises when codecs are compared at equal requested tolerance. The nominal bound is an input parameter, not a common realized perturbation scale. In the frozen data, ZFP realizes only about 0.17 times the L-infinity perturbation of SZ3 or SPERR at equal nominal tolerance, whereas SZ3 and SPERR are close to one another. Direct equal-nominal comparisons therefore mix differences in perturbation magnitude with differences in error-field structure.

We control this confounding by matching reconstructions within material on log10(realized L-infinity), without replacement, using a primary 0.10-dex caliper. Matching substantially reduces the apparent codec gap but does not eliminate it. At the primary caliper, the matched re-derived Bader error for ZFP is 0.557 times that of SZ3 and 0.601 times that of SPERR, while SZ3 and SPERR are similar (ratio 1.033). This residual is consistent with a contribution from error-field structure beyond scalar maximum magnitude, although it does not identify a unique geometric descriptor.

The practical implication is that scientific-compression comparison requires two qualifications: the **downstream tolerance must be eligible**, and the **upstream distortion used to compare codecs must be measured rather than inferred from a nominal setting**.

### Stability-qualified rate-fidelity is tolerance dependent

For each eligible material-threshold pair, the benchmark selects the best certified reconstruction available on the frozen codec ladder and reports its compression ratio. This produces a rate-fidelity frontier rather than a universal codec ranking.

The ordering changes with the chemical contract. On the development data, SZ3 has the strongest median certified compression ratio at 10^-2 e, ZFP and SZ3 are much closer at 10^-3 e, and ZFP has the advantage at 10^-4 e among the much smaller eligible cohort. SPERR has lower certified compression ratios in these comparisons. These transitions are consistent with a trade-off between compression aggressiveness, realized distortion, and topology-sensitive downstream fidelity.

Because eligibility shrinks sharply at strict tolerance, codec results must always be reported conditional on the scientifically measurable cohort. A high or low certification rate at 10^-4 e cannot be interpreted without also reporting how many materials were eligible for a 10^-4 e Bader contract in the first place.

### The frozen decision procedure reproduces on an untouched external cohort

The external confirmatory cohort contains 63 completed systems and 1,689 retained scientific rows. The frozen protocol is applied without retuning. There are zero material-level pipeline failures and zero codec error-bound violations; three row-level Bader-solver failures remain explicitly recorded in the audit.

Protocol A.1 finds 16/63 external systems eligible at 10^-4 e, 42/63 at 10^-3 e, and 57/63 at 10^-2 e. The rate-fidelity ordering is also tolerance dependent. At 10^-4 e, the external median best-certified compression ratios are approximately 13.0× for ZFP, 12.1× for SZ3, and 5.2× for SPERR. At 10^-3 e, ZFP and SZ3 are both about 18.8×, compared with about 6.4× for SPERR. At 10^-2 e, SZ3 reaches about 65.9×, ahead of ZFP at 40.6× and SPERR at 10.8×.

The external cohort therefore reproduces the central operational pattern: the measurable cohort expands as the scientific tolerance is relaxed, and the preferred rate-fidelity trade-off depends on the requested contract. The output of the framework is not an unconditional statement that one codec is best. It is a decision rule conditioned on QoI eligibility, realized reconstruction, and target scientific precision.

## Methods

### Frozen benchmark design

The development benchmark comprises 6,343 frozen reconstruction rows over 254 electronic-density fields: 186 bulk systems and 68 slabs. The three implemented compressor families are ZFP, SZ3/SZ, and SPERR, whose primary algorithm references are [2-4]. Each is evaluated over base and extended tight tolerance ladders. Every row records material identity, codec configuration, requested tolerance, realized distortion, compression size, downstream QoI errors, and stability-qualification status. Once a protocol or benchmark table was frozen, subsequent analyses consumed the frozen outputs rather than silently regenerating or replacing earlier results.

Rows that fail a pre-specified solver or reproduction condition remain visible in the audit. The benchmark therefore distinguishes scientific exclusion, numerical non-evaluability, and infrastructure-level mismatch rather than combining them into one missing-data category.

### Realized reconstruction distortion

Requested codec tolerance is treated as a control input. The primary field-level distortion variable is the measured L-infinity error between the reconstructed and reference densities. Compression ratio is computed from frozen byte counts. Equal-nominal comparisons are retained as diagnostics, but codec analyses intended to separate magnitude from residual structure use within-material matching on log10(realized L-infinity), without replacement, with a primary caliper of 0.10 dex.

### Electron number and Hartree potential

Total electron number is evaluated as a global linear control. The periodic Hartree potential is used as a linear nonlocal comparator; the G = 0 component is gauge-fixed to zero. The primary Hartree metric is relative RMS potential error. Pooled slopes, material-level R^2, strict monotonicity, and local response exponents are reported separately to avoid conflating overall smooth scaling with rung-level reversals.

### Re-derived Bader charge

Bader partitioning follows the density-topological definition of atomic basins [17] and the established numerical literature on grid-based partitioning and integration [8-10,16]. Because the basin is a functional of the density, certification recomputes the partition for every reconstructed field. The primary Bader metric is the maximum absolute per-atom charge difference between reconstructed and reference analyses. Fixed-basin calculations are used only to quantify the contribution suppressed when reference domains are held constant.

### Protocol A.1 eligibility

For each material, Protocol A.1 applies five fixed-seed uniform perturbations at an amplitude equal to the material's float32 L-infinity scale. After each perturbation the Bader partition and charges are re-derived. The material-specific stability floor is the maximum induced Bader deviation across the five probes.

For threshold `tau`:

`eligible(m, tau) := stability_floor_A1(m) < tau`

For a reconstruction `r` of material `m`:

`certified(r, tau) := eligible(m, tau) AND Bader_error_resolved(r) < tau`

When `eligible(m, tau)` is false, the status is `NON_EVALUABLE_BADER_UNSTABLE`. Such cases are not counted as codec successes or failures at that threshold.

### Binary-to-three-state reclassification audit

The Figure 3 audit uses one material-codec decision at a fixed Bader threshold as the analysis unit. For each of 254 development materials and each of three codecs, the frozen tolerance ladder is reduced to a binary diagnostic and a stability-qualified decision. The naive diagnostic is positive if any available reconstruction satisfies the Bader threshold while ignoring eligibility (`certified_at_tau_ignoring_eligibility`). The qualified decision first applies the material-level Protocol A.1 eligibility flag and then asks whether any reconstruction is certified under the operative definition. Each of the 762 decisions per threshold is therefore assigned to **certified**, **eligible but not certified**, or **non-evaluable**. Reclassification fractions are computed among naive failures, with naive passes on non-evaluable pairs reported separately to show that eligibility is not a permissive failure filter.

### Mechanism decomposition

For representative materials, the Bader charge change is decomposed conceptually into a contribution from density change evaluated on the reference domain and a residual contribution associated with migration of the re-derived domain. Per-atom decomposition is combined with tolerance-ladder diagnostics and voxel-reassignment summaries. The decomposition is interpreted as a Bader-specific mechanism and not generalized to arbitrary QoIs without evidence.

### External confirmation

The external cohort is kept separate from development analysis. All thresholds, probe definitions, eligibility rules, and codec-scoring semantics are frozen before external evaluation. The confirmatory analysis tests material-level completion, codec error-bound behavior, Protocol A.1 eligibility, tolerance-dependent certified compression ratios, and realized-distortion asymmetry.

### Reproducibility

Formal figures are generated from versioned R source files and frozen CSV inputs, with PNG, PDF, and SVG exported from the same source. Protocol A remains archived unchanged; Protocol A.1 is the operative qualification procedure. The repository retains the failure registry, stability tables, external manifest, mechanism decompositions, claim-evidence records, and chronological command history required to reconstruct the reported decisions.

## Discussion

Prior scientific-compression research has already moved beyond generic field-error metrics. Mathematical reduction frameworks quantify accuracy in derived quantities [12], QoI-preserving methods make downstream quantities explicit compression targets [6], and application-specific pipelines preserve selected QoIs through constraints, learned representations, and scalable online execution [13,14,20]. TOPIQ extends this direction by predicting QoI-level bias and uncertainty from compression metadata [11]. These studies answer how to preserve, bound, or predict downstream error once the QoI and its target are accepted. The present work asks a different prerequisite question: **is that target itself numerically resolvable on the reference data before it is used to assign a codec pass or failure?**

Topology-aware compression provides a second important boundary on the claim. TopoSZ and subsequent general topological-augmentation frameworks show that strict pointwise bounds do not by themselves guarantee preservation of discrete topological descriptors, and they modify the compression procedure to protect specified structures [7,15]. Our contribution is not another topology-preserving codec. Instead, it is a benchmark-validity rule that qualifies the downstream measurement before any codec is scored. This distinction is important because a compressor cannot be held responsible for violating a tolerance that the downstream analysis cannot independently resolve.

The numerical sensitivity of Bader analysis is likewise established rather than claimed as novel. QTAIM defines atomic regions from the topology of the electron density [17], and grid-based implementations have long addressed discretization, lattice bias, basin assignment, integration accuracy, and convergence [8,9,16]. Modern arbitrary-grid analysis further emphasizes that topological results are inseparable from numerical representation [10]. We use this established sensitivity as the test bed for a different contribution: turning numerical identifiability into an explicit eligibility condition for scientific-compression benchmarking.

Figure 3 shows why this requirement is consequential rather than semantic. At 10^-4 and 10^-3 e, respectively, 97.2% and 95.5% of apparent binary failures are attached to material-threshold pairs that fail the independent Protocol A.1 eligibility test. Only 15 and 14 apparent failures at those thresholds remain genuine failures among eligible pairs. At the strictest threshold, nearly half of naive passes are also non-evaluable. The qualification therefore does not simply reduce a failure rate; it invalidates both positive and negative labels whenever the requested measurement precision is unsupported. The benchmark must change from binary to three-state.

This distinction separates two questions that are otherwise easy to conflate. The first is a measurement question: is the QoI numerically identifiable at the requested precision? The second is a compression question: conditional on that eligibility, does a reconstructed field preserve the QoI within the requested tolerance? Only the second question can support a codec failure attribution. The three-state classification makes this logic explicit and auditable.

Bader analysis is an informative stress test because its numerical sensitivity has a concrete structural origin. The integration domains are not fixed objects; they are re-derived from the field. A reconstruction can therefore perturb both the density and the partition used to integrate it, consistent with the basin-based numerical formulation of established Bader algorithms [8,9,16]. Fixed-basin scoring removes this second channel and can substantially understate the downstream response. The floor-normalized analysis also shows that the strictest certified regime is already on the same scale as the independently measured stability floor. This observation is consistent with an emerging analysis-limited regime, but the current data do not establish a universal material-level equality between a tight-ladder plateau and the A.1 floor.

The framework does not require that every QoI possess a Bader-like topological floor. A smooth, stable QoI may remain eligible at much stricter tolerances. The general principle is procedural rather than mechanistic: the qualification test should probe numerical sensitivity relevant to the downstream operator, and eligibility should be established before compression scoring. Protocol A.1 itself illustrates why this matters. The archived float32 round-trip appeared stable partly because it preserved local ordering and did not adequately excite the relevant partition changes. A measurement-certification workflow must validate the probe as well as the quantity it probes.

Realized-distortion matching addresses a separate source of invalid comparison. ZFP, SZ3, and SPERR employ different coding strategies [2-4], so equal nominal settings should not be assumed to imply equal realized perturbations. In our frozen benchmark, the large difference between ZFP and SZ3/SPERR at equal requested tolerance shows that a codec leaderboard based only on nominal settings can confound realized distortion with downstream robustness. Matching measured L-infinity greatly reduces this confounding, while the remaining Bader difference suggests that the spatial structure of error also matters. This residual is described conservatively: the current evidence supports an error-structure contribution but does not identify a unique geometric invariant that controls Bader fidelity.

The external cohort strengthens the decision-level result. Without retuning, the same qualification logic yields a strongly tolerance-dependent measurable cohort and a tolerance-dependent rate-fidelity ordering. At the same time, earlier structural generalizations such as a universal bulk-versus-vacuum stability distinction do not survive external confirmation. That negative result is consistent with the central argument: QoI stability should be measured for the case at hand rather than inferred from a coarse material category.

The electronic-structure context also clarifies the scope of the contribution. Previous quantum-chemistry compression work has targeted objects such as two-electron integrals [21] or atomic-orbital spaces [19], and general scientific-compression systems have been tested on quantum-chemistry workloads [3,18]. Our benchmark instead treats a stored real-space electron density as the compressed object and asks whether a downstream chemical observable is certifiable at a requested tolerance. These problems are complementary rather than competing.

There are two important limits to the present study. First, the benchmark establishes the certification framework deeply for Bader charge, with Hartree potential and electron count serving as controls; it does not prove a universal law for all scientific observables. Second, the numerical eligibility floor is protocol-defined. Protocol A.1 is calibrated to a specific small-perturbation scale and a fixed five-seed conservative rule. Different downstream algorithms or numerical representations may require a different qualification probe. This is precisely why the measurement procedure must be part of the scientific compression contract.

The broader implication is that a reproducible scientific-compression contract should specify at least five elements: the QoI definition, the downstream evaluation algorithm, a validated intrinsic-stability qualification, the acceptable QoI tolerance, and the realized reconstruction condition. A nominal codec setting alone is insufficient to define scientific validity. This requirement complements, rather than replaces, existing work on QoI preservation, error propagation, and topology-aware compression [6,7,11-15,20].

## Conclusions

A downstream error threshold is not automatically a valid compression benchmark. Before a compressor is judged against a scientific tolerance, the downstream quantity of interest must first be shown to be numerically identifiable at that scale. Applying this principle to electronic-density compression yields three distinct outcomes—eligible and certified, eligible but not certified, and non-evaluable—rather than forcing every reconstruction into an unconditional pass/fail label.

The distinction materially changes the interpretation of the benchmark. At 10^-4 and 10^-3 e, 97.2% and 95.5% of apparent binary failures, respectively, are reclassified as non-evaluable by the independent Protocol A.1 stability test; at 10^-4 e, 46.3% of naive passes are also non-evaluable. These results show that stability qualification is not a relaxed pass rule but a prerequisite for assigning either outcome.

For Bader charge, this distinction is consequential because the density-dependent partition can migrate under small perturbations and because the analysis has a material-specific stability scale. Hartree-potential and electron-count controls show that the same reconstruction can behave much more regularly under smoother operators, while realized-L-infinity matching shows that codec comparisons must also control actual rather than nominal distortion.

The resulting framework reframes scientific compression from a codec leaderboard into a stability-qualified rate-fidelity decision problem. A compressor can only be held responsible for failing a downstream contract when the contract itself is scientifically measurable.

## References

1. Di, S. *et al.* A survey on error-bounded lossy compression for scientific datasets. **ACM Computing Surveys** **57**(11), Article 287, 1–38 (2025). https://doi.org/10.1145/3733104.
2. Lindstrom, P. Fixed-rate compressed floating-point arrays. **IEEE Transactions on Visualization and Computer Graphics** **20**, 2674–2683 (2014). https://doi.org/10.1109/TVCG.2014.2346458.
3. Liang, X. *et al.* SZ3: A modular framework for composing prediction-based error-bounded lossy compressors. **IEEE Transactions on Big Data** **9**, 485–498 (2023). https://doi.org/10.1109/TBDATA.2022.3201176.
4. Li, S., Lindstrom, P. & Clyne, J. Lossy scientific data compression with SPERR. In **2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)**, 1007–1017 (IEEE, 2023). https://doi.org/10.1109/IPDPS54959.2023.00104.
5. Tao, D., Di, S., Guo, H., Chen, Z. & Cappello, F. Z-checker: A framework for assessing lossy compression of scientific data. **The International Journal of High Performance Computing Applications** **33**, 285–303 (2019). https://doi.org/10.1177/1094342017737147.
6. Jiao, P., Di, S., Guo, H., Zhao, K., Tian, J., Tao, D., Liang, X. & Cappello, F. Toward quantity-of-interest preserving lossy compression for scientific data. **Proceedings of the VLDB Endowment** **16**, 697–710 (2022). https://doi.org/10.14778/3574245.3574255.
7. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving topology in error-bounded lossy compression. **IEEE Transactions on Visualization and Computer Graphics** **30**, 1302–1312 (2024). https://doi.org/10.1109/TVCG.2023.3326920.
8. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. **Computational Materials Science** **36**, 354–360 (2006). https://doi.org/10.1016/j.commatsci.2005.04.010.
9. Tang, W., Sanville, E. & Henkelman, G. A grid-based Bader analysis algorithm without lattice bias. **Journal of Physics: Condensed Matter** **21**, 084204 (2009). https://doi.org/10.1088/0953-8984/21/8/084204.
10. Hutcheon, M. J. & Teale, A. M. Topological analysis of functions on arbitrary grids: Applications to quantum chemistry. **Journal of Chemical Theory and Computation** **18**, 6077–6091 (2022). https://doi.org/10.1021/acs.jctc.2c00649.
11. Liu, Y., Jiang, B., Yang, T., Di, S., Underwood, R. & Jin, S. TOPIQ: Statistical error propagation for quantity-of-interest prediction under lossy compression. **arXiv** 2608.26912 (2026). https://arxiv.org/abs/2608.26912.
12. Ainsworth, M., Tugluk, O., Whitney, B. & Klasky, S. Multilevel techniques for compression and reduction of scientific data—quantitative control of accuracy in derived quantities. **SIAM Journal on Scientific Computing** **41**, A2146–A2171 (2019). https://doi.org/10.1137/18M1208885.
13. Gong, Q. *et al.* Maintaining trust in reduction: Preserving the accuracy of quantities of interest for lossy compression. In **Driving Scientific and Engineering Discoveries Through the Integration of Experiment, Big Data, and Modeling and Simulation**, Communications in Computer and Information Science **1512**, 22–39 (Springer, 2022). https://doi.org/10.1007/978-3-030-96498-6_2.
14. Lee, J., Gong, Q., Choi, J., Banerjee, T., Klasky, S., Ranka, S. & Rangarajan, A. Error-bounded learned scientific data compression with preservation of derived quantities. **Applied Sciences** **12**, 6718 (2022). https://doi.org/10.3390/app12136718.
15. Gorski, N., Liang, X., Guo, H., Yan, L. & Wang, B. A general framework for augmenting lossy compressors with topological guarantees. **IEEE Transactions on Visualization and Computer Graphics** **31**, 3693–3705 (2025). https://doi.org/10.1109/TVCG.2025.3567054.
16. Yu, M. & Trinkle, D. R. Accurate and efficient algorithm for Bader charge integration. **The Journal of Chemical Physics** **134**, 064111 (2011). https://doi.org/10.1063/1.3553716.
17. Bader, R. F. W. **Atoms in Molecules: A Quantum Theory** (Oxford University Press, 1990). https://doi.org/10.1093/oso/9780198551683.001.0001.
18. Cappello, F. *et al.* Use cases of lossy compression for floating-point data in scientific data sets. **The International Journal of High Performance Computing Applications** **33**, 1201–1220 (2019). https://doi.org/10.1177/1094342019853336.
19. Lara, A. O., Talbot, J. J., Wang, Z. & Head-Gordon, M. An algorithm for atom-centered lossy compression of the atomic orbital basis in density functional theory calculations. **Journal of Chemical Theory and Computation** **22**, 3327–3340 (2026). https://doi.org/10.1021/acs.jctc.5c01988.
20. Banerjee, T., Lee, J., Choi, J., Gong, Q., Chen, J., Chang, C.-S., Klasky, S., Rangarajan, A. & Ranka, S. Online and scalable data compression pipeline with guarantees on quantities of interest. In **2023 IEEE 19th International Conference on e-Science (e-Science)**, 1–10 (IEEE, 2023). https://doi.org/10.1109/e-Science58273.2023.10254934.
21. Gok, A. M., Di, S., Alexeev, Y., Tao, D., Mironov, V., Liang, X. & Cappello, F. PaSTRI: Error-bounded lossy compression for two-electron integrals in quantum chemistry. In **2018 IEEE International Conference on Cluster Computing (CLUSTER)**, 1–11 (IEEE, 2018). https://doi.org/10.1109/CLUSTER.2018.00013.

## Data and code availability

Frozen benchmark tables, Protocol A.1 stability outputs, the Figure 3 binary-to-three-state audit, mechanism decompositions, realized-distortion matching analyses, external confirmatory evidence, R figure sources, and claim-evidence records are versioned in the `stloendays/QoI` repository. The archived Protocol A outputs remain available alongside Protocol A.1 so that the qualification correction is auditable.

---

## Quantitative interpretation boundary for submission

The Figure 3 reclassification audit is complete and is approved as headline evidence. The tight-regime analysis supports a weaker mechanistic statement: at the 10^-4 e certified contract, resolved Bader errors are floor-scale (median error/floor 1.09-1.33 across codecs), consistent with an emerging analysis-limited regime. The current frozen analysis does **not** establish a universal material-level identity between the tight-ladder plateau and the Protocol A.1 floor, and the manuscript must not claim `plateau = floor` as a quantitative law.