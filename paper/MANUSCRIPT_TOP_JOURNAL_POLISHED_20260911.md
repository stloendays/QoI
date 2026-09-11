# Stability-qualified benchmarks for scientific compression of electronic densities

## Abstract

Lossy compression of scientific fields is commonly evaluated by asking whether a downstream quantity of interest (QoI) remains within a prescribed tolerance. That comparison assumes that the reference analysis can itself resolve the requested tolerance. Here we test and formalize this assumption for Bader charges derived from compressed electronic densities. We analyse 6,343 frozen reconstructions of 254 bulk and slab systems generated with ZFP, SZ3 and SPERR, together with an untouched 63-system external cohort. Protocol A.1 measures a material-specific numerical stability floor from five fixed-seed perturbations before codec scoring. At Bader contracts of $10^{-4}\,e$ and $10^{-3}\,e$, 97.2% and 95.5% of apparent binary failures, respectively, are non-evaluable after stability qualification; at $10^{-4}\,e$, 46.3% of apparent passes are also non-evaluable. Re-derived Bader charges respond irregularly because basin boundaries migrate, whereas Hartree-potential error scales approximately linearly with realized density perturbation. Matching codecs by realized $L_\infty$ further removes nominal-tolerance confounding. The frozen qualification and certification rules reproduce on the external cohort without retuning. These results establish a three-state benchmark—certified, eligible but not certified, and non-evaluable—and show that downstream numerical identifiability is a prerequisite for assigning scientific-compression success or failure.

**Keywords:** scientific data compression; quantity of interest; benchmark validity; Bader charge; electronic density; numerical stability

## Introduction

Electronic-structure calculations produce three-dimensional fields that are expensive to store, transfer and reanalyse. Electron density is a particularly consequential example because it is not merely an archival output: subsequent charge partitioning, electrostatic analysis and data-driven workflows operate directly on the stored field. Error-bounded lossy compression can reduce this burden while constraining reconstruction error [1–4]. Yet a field-level error bound does not, by itself, define the fidelity of every scientific quantity subsequently extracted from the reconstruction.

Scientific-compression research has increasingly moved from generic distortion metrics towards downstream quantities of interest. Z-checker formalized systematic post-compression error analysis [5], QoI-preserving methods explicitly target derived scientific quantities [6], and topology-preserving approaches show that small pointwise errors can still alter discrete scientific structure [7]. More recently, TOPIQ has addressed statistical propagation of compression error into QoI-level bias and uncertainty [11]. These developments establish that downstream quantities matter. They leave a more basic question unresolved: **when is the requested QoI tolerance itself a valid benchmark?**

A downstream tolerance is meaningful only if the reference analysis can distinguish changes at that scale. Otherwise, a reconstruction that exceeds the tolerance may reflect either compression-induced error or numerical instability of the analysis used to define the target. A binary pass/fail benchmark cannot separate these possibilities. We therefore treat numerical identifiability as a prerequisite for codec scoring: the reference QoI is first qualified at the requested tolerance, and only qualified material–threshold pairs are assigned compression success or failure (Fig. 1).

Bader charge provides a stringent chemical test of this principle. Bader analysis partitions the density into atom-centred basins defined by the topology of the field [8,9], and grid-based topological analyses are known to exhibit representation and convergence effects [10]. A perturbation can therefore change both the density values being integrated and the basin boundaries over which the integration is performed. We use total electron number and the periodic Hartree potential as global-linear and linear-nonlocal controls, respectively, to separate this Bader-specific mechanism from the more general benchmark-validity question.

Here we analyse 6,343 frozen reconstructions of 254 development densities (186 bulk systems and 68 slabs) compressed with ZFP, SZ3 and SPERR over base and tight tolerance ladders. We introduce Protocol A.1 to measure a material-specific Bader stability scale before codec certification, re-derive Bader basins after every reconstruction, decompose representative errors into fixed-domain and domain-migration contributions, and compare codecs after matching by realized rather than nominal $L_\infty$ distortion. We then apply the frozen decision rules, without retuning, to an untouched external cohort of 63 systems. The resulting framework replaces an unconditional codec leaderboard with a stability-qualified rate–fidelity benchmark in which a compressor is judged only against scientific tolerances that the downstream analysis can independently resolve.

## Results

### Identical field perturbations propagate differently through downstream operators

The same reconstructed density can be highly faithful for one observable and unreliable for another because the downstream operators have different mathematical structure (Fig. 2). Total electron number provides the simplest control. Among 3,205 reconstructions with an absolute electron-count deviation below $10^{-4}\,e$ and a finite re-derived Bader result, 1,383 (43.15%) nevertheless have a Bader error of at least $10^{-3}\,e$. Tight conservation of a global integral therefore does not certify atom-resolved charge fidelity.

The periodic Hartree potential is nonlocal but linear and behaves much more regularly. Across 6,270 reconstruction-gate-passing rows, Hartree-potential error scales approximately linearly with realized density perturbation, with a pooled log–log exponent of 1.02. Median material-level $R^2$ values are 0.997 for ZFP, 0.994 for SZ3 and 0.996 for SPERR. The response is therefore close to first order over the measured range.

Re-derived Bader charge is substantially less regular. Only 32.4% of material–codec tolerance ladders are strictly monotone, and local response exponents range from −9.3 to +14.1. Individual adjacent tolerance steps can produce large discontinuous changes, including a 22,296-fold illustrative jump. Even when reconstructions are grouped by similar Hartree-potential error, Bader errors remain widely dispersed: 55.4% of gate-passing rows fall in 0.5-decade matched-Hartree bins with a Bader-error P90/P10 ratio of at least 10. These controls do not constitute the central novelty of the study; rather, they establish why a valid scientific-compression benchmark must explicitly include the downstream analysis.

### Stability qualification changes the benchmark from binary to three-state

We next asked whether the requested Bader tolerances are themselves numerically identifiable. Protocol A.1 applies five fixed-seed, non-order-preserving perturbations to each reference density at an amplitude equal to that material's float32 $L_\infty$ scale. The maximum re-derived Bader deviation across the five probes defines a material-specific stability floor. A Bader contract $\tau$ is eligible only when this independently measured floor is below $\tau$.

Eligibility decreases sharply as the requested precision becomes stricter. Across all 319 development and external systems, 79.9% are non-evaluable at $10^{-4}\,e$, 41.4% at $10^{-3}\,e$, and 9.7% at $10^{-2}\,e$. These fractions are properties of the reference analysis under the frozen qualification protocol; they are not codec failure rates.

The consequence for benchmark interpretation is large (Fig. 3). The development corpus contains 254 materials and three codecs, giving 762 material–codec decisions at each Bader threshold. A naive binary benchmark, which applies the Bader tolerance without testing eligibility, reports 533 failures at $10^{-4}\,e$, 310 at $10^{-3}\,e$, and 108 at $10^{-2}\,e$. After stability qualification, the same decisions resolve into three scientifically distinct states. At $10^{-4}\,e$, there are 123 certified decisions, 15 eligible failures and 624 non-evaluable decisions; at $10^{-3}\,e$, the corresponding counts are 415, 14 and 333; at $10^{-2}\,e$, they are 640, 47 and 75.

Most apparent failures at the strictest thresholds are therefore not attributable to the compressor. Of the 533 naive failures at $10^{-4}\,e$, 518 (97.2%) occur on non-evaluable material–threshold pairs. At $10^{-3}\,e$, 296 of 310 naive failures (95.5%) are likewise non-evaluable. Even at $10^{-2}\,e$, 61 of 108 apparent failures (56.5%) fall outside the eligible benchmark. Importantly, eligibility is not a permissive filter that only removes failures: at $10^{-4}\,e$, 106 of 229 naive passes (46.3%) are also non-evaluable. Stability qualification therefore changes the label space itself. A material–threshold pair is either **eligible and certified**, **eligible but not certified**, or **non-evaluable**; the third state can be assigned neither success nor failure at the requested precision.

### A valid stability probe must excite the numerical failure mode

The qualification procedure itself must be tested against the structure of the downstream analysis. The archived Protocol A used a float32 round trip as its stability probe. We found that this perturbation is strongly order-preserving and can therefore leave an on-grid watershed partition apparently unchanged even when comparably small non-order-preserving perturbations alter basin assignments (Fig. 4).

This distinction is substantial rather than cosmetic. The float32 probe generates a median of 82 exact neighbouring ties and reassigns zero voxels in 62% of tested systems, whereas non-order-preserving noise at the same, or even 100-fold smaller, amplitude can reassign hundreds of voxels. Across the full stability corpus, the Protocol A.1 noise-based floor is a median of approximately $8.7\times10^3$ times larger than the archived float32 floor. The effect is also heterogeneous across materials, ruling out a simple global rescaling.

Protocol A.1 therefore retains the scientific tolerance set and reporting semantics but replaces the probe with five pre-specified fixed-seed uniform perturbations. The maximum response across seeds is used as a conservative floor. Relative to a single-seed decision, the five-seed maximum changes eligibility for 35 of 319 systems at $10^{-4}\,e$, 17 at $10^{-3}\,e$, and 2 at $10^{-2}\,e$. The lesson is methodological: a QoI can be declared numerically identifiable only with a qualification probe that is capable of exciting the numerical instability relevant to that operator.

### The strictest certified regime approaches the analysis floor

The tight tolerance ladder provides an independent view of the transition from compression-dominated to analysis-limited behaviour. At the strictest certified Bader contract, $10^{-4}\,e$, the median ratio of resolved Bader error to the Protocol A.1 stability floor is 1.09 for ZFP, 1.33 for SZ3 and 1.23 for SPERR; the corresponding 90th percentiles are 3.25, 2.86 and 3.20. The remaining reconstruction error is therefore already of the same order as the independently measured numerical floor.

This relation weakens as the contract is relaxed. At $10^{-3}\,e$, median error-to-floor ratios rise to 2.78–3.55, and at $10^{-2}\,e$ to 10.7–14.6. We therefore describe the strictest certified regime as **floor-scale and consistent with an emerging analysis-limited regime**. The present data do not establish a universal material-by-material equality between a tight-ladder plateau and the Protocol A.1 floor, and no such equality is assumed in the certification rule.

### Basin migration provides a Bader-specific mechanism for irregular amplification

Bader analysis differs from the linear controls because its integration domain is itself a functional of the density (Fig. 5). For atom $A$, the reference charge is integrated over $\Omega_A[\rho]$, whereas the reconstructed charge is evaluated over $\Omega_A[\tilde\rho]$. The total charge deviation therefore combines a change in the integrand with a change in the integration domain.

Holding the reference basin fixed suppresses the latter contribution and changes the downstream operator being evaluated. We therefore use re-derived basins for scientific certification and retain fixed-basin calculations only as a mechanistic diagnostic. Representative per-atom decompositions show that domain migration can dominate large Bader deviations at tight perturbations, while full tolerance ladders contain abrupt charge changes despite smoothly varying field distortion. This mechanism explains why Bader response can be discontinuous even when smoother observables remain well behaved. It is specific to density-dependent partitioning and is not assumed to generalize to arbitrary QoIs.

### Realized distortion, not nominal tolerance, is required for fair codec comparison

Codec tolerances are control inputs rather than common measures of realized perturbation. At equal nominal tolerance, ZFP produces a median realized $L_\infty$ only 0.170 times that of SZ3 and 0.170 times that of SPERR; SZ3 and SPERR are approximately matched. Direct comparison at equal requested tolerance therefore conflates two effects: the magnitude of the realized perturbation and the spatial structure of the codec error (Fig. 6A).

We separate these effects by matching reconstructions within each material on $\log_{10}(L_\infty)$, without replacement, using a primary caliper of 0.10 dex. After matching, ZFP retains lower re-derived Bader error than SZ3 (ratio 0.557; 95% material-bootstrap confidence interval, 0.525–0.598) and SPERR (0.601; 0.534–0.662), whereas SZ3 and SPERR are statistically similar (1.033; 0.976–1.072) (Fig. 6B). The residual persists across calipers from 0.05 to 0.30 dex. These data support a contribution from error-field structure beyond scalar $L_\infty$ magnitude, but they do not identify a unique spatial descriptor that controls Bader fidelity.

The comparison therefore requires two distinct qualifications: the downstream scientific tolerance must be numerically eligible, and codecs must be compared using measured rather than nominal reconstruction distortion. Failure to control either quantity can create a misleading ranking.

### Stability-qualified rate–fidelity rankings depend on the scientific contract

Among eligible material–threshold pairs, we select the highest compression ratio that satisfies the Bader contract on the frozen codec ladder. The resulting rate–fidelity frontier is strongly tolerance dependent. At $10^{-2}\,e$ in the development set, SZ3 provides the largest median certified compression ratio in both bulk and slab strata (52.0× [48.0, 61.7] and 69.6× [65.9, 72.3], respectively), ahead of ZFP (30.0× [27.2, 31.7] and 40.5× [37.0, 44.9]) and SPERR (11.6× [10.1, 13.4] and 8.1× [7.7, 9.4]). At $10^{-3}\,e$, ZFP and SZ3 become much closer, and at $10^{-4}\,e$ ZFP has the advantage among the much smaller eligible cohort. Thus, no single codec dominates across scientific contracts.

These rankings must be interpreted together with eligibility. Tightening the Bader tolerance does not merely reduce the compression ratio that can be certified; it also changes which material–threshold pairs support a meaningful scientific decision. Reporting a codec success rate without the corresponding eligible denominator would therefore mix compression performance with numerical identifiability.

### Frozen decision rules reproduce on an untouched external cohort

We finally applied the complete qualification and certification procedure to 63 untouched external systems without changing thresholds, probe definitions or codec-scoring rules (Fig. 7). The external analysis produced 1,689 retained rows, with zero material-level pipeline failures and zero codec error-bound violations; three row-level Bader-solver failures remain explicitly recorded in the audit.

Protocol A.1 identifies 16 of 63 systems as eligible at $10^{-4}\,e$, 42 at $10^{-3}\,e$, and 57 at $10^{-2}\,e$. The certified rate–fidelity ranking again changes with the contract. At $10^{-4}\,e$, median best-certified compression ratios are approximately 13.0× for ZFP, 12.1× for SZ3 and 5.2× for SPERR. At $10^{-3}\,e$, ZFP and SZ3 are both approximately 18.8×, compared with 6.4× for SPERR. At $10^{-2}\,e$, SZ3 reaches 65.9×, ahead of ZFP at 40.6× and SPERR at 10.8×.

The external cohort therefore reproduces the operational conclusions without retuning: the measurable cohort expands as the requested tolerance is relaxed, and the preferred codec depends on the scientific contract. Earlier coarse generalizations, including a universal bulk-versus-vacuum stability distinction, do not reproduce externally. Numerical eligibility is better measured for each case than inferred from broad structural categories.

## Discussion

Scientific-compression benchmarks usually treat the downstream tolerance as given. Our results show that this assumption can fail before the codec is evaluated. At strict Bader contracts, more than 95% of apparent binary failures occur where the reference analysis itself is not independently resolvable at the requested precision. The same qualification also invalidates apparent passes. The central issue is therefore not how to make a codec look more successful, but whether a binary scientific label is defined at all.

This result extends, rather than repeats, established QoI-aware compression work. Previous studies have shown that raw-data error does not uniquely determine downstream fidelity and have developed methods to constrain, preserve or predict QoI error [5–7,11]. Our framework adds a logically prior step: before propagating or constraining a QoI error against a target tolerance, the target must be shown to lie above the numerical resolution of the reference analysis. This distinction separates a **measurement question**—is the QoI identifiable at the requested scale?—from a **compression question**—conditional on that identifiability, does the reconstruction satisfy the contract? Only the second question supports attribution of failure to the codec.

Bader charge makes this distinction visible because its numerical sensitivity has a concrete structural origin. Reconstructing the density can move basin boundaries as well as alter values within the basins. Fixed-domain scoring removes this channel and can therefore underestimate the response that would be obtained by rerunning the actual downstream analysis. The tightest certified reconstructions also approach the independently measured Bader stability floor, consistent with a crossover towards an analysis-limited regime. Neither feature should be universalized: a smooth QoI may remain identifiable at much tighter tolerances, and a different topology-sensitive algorithm may require a different qualification probe.

Protocol A.1 illustrates a second consequence of the framework: the stability test itself is part of the measurement contract. The archived float32 probe was numerically small but structurally inappropriate because it largely preserved the ordering that drives the on-grid partition. A valid qualification procedure must therefore probe the failure modes of the downstream operator, not merely impose an arbitrarily small perturbation. The five-seed maximum used here is intentionally conservative and protocol-defined; its purpose is to make the eligibility decision explicit and auditable rather than to estimate an intrinsic material constant independent of algorithm and representation.

The same logic applies to codec comparison. Equal nominal tolerances do not imply equal realized errors, and equal scalar $L_\infty$ does not fully determine the downstream response. Matching on realized distortion removes a major confound, while the remaining codec differences indicate that error structure also contributes. A scientifically interpretable benchmark should therefore specify both the downstream measurement contract and the upstream reconstruction condition under which codecs are compared.

Two limitations define the scope of the present conclusions. First, we establish the certification framework deeply for one topology-sensitive chemical observable, with electron number and Hartree potential serving as controls; we do not claim a universal numerical floor or a universal error-propagation law across all QoIs. Second, eligibility is necessarily protocol dependent. The appropriate perturbation family, amplitude and numerical analysis may differ for other downstream quantities. These are not reasons to omit qualification; they are reasons to report the qualification procedure as part of the benchmark.

More broadly, a reproducible scientific-compression benchmark should specify at least five elements: the QoI definition, the downstream evaluation algorithm, a validated stability qualification, the acceptable scientific tolerance and the realized reconstruction condition. Under this view, the output is not a single codec leaderboard but a conditional decision: whether a scientific target is evaluable and, if so, which reconstruction achieves the best rate while satisfying it. Numerical identifiability is therefore not an auxiliary diagnostic of scientific compression; it is a prerequisite for assigning scientific success or failure.

## Methods

### Benchmark design

The development benchmark contains 6,343 frozen reconstruction rows from 254 electronic-density fields: 186 bulk systems and 68 slabs. ZFP, SZ3/SZ and SPERR were evaluated over a base tolerance ladder and an extended tight ladder. Each row records material identity, codec configuration, requested tolerance, realized distortion, compressed size, downstream QoI errors and stability-qualification status. Frozen outputs were used for all downstream analyses; earlier protocol versions were retained as provenance rather than overwritten.

Rows that fail a pre-specified solver or reproduction condition remain in the audit trail. Scientific non-evaluability, downstream solver failure and infrastructure mismatch are recorded separately rather than collapsed into a single missing-data category.

### Realized reconstruction distortion

Requested codec tolerance was treated as a control parameter. The primary realized field distortion was

$$
E_\infty = \lVert \tilde{\rho}-\rho \rVert_\infty,
$$

where $\rho$ and $\tilde{\rho}$ denote the reference and reconstructed densities. Compression ratios were computed from frozen byte counts. Equal-nominal comparisons were retained as diagnostics. To compare codecs at similar actual perturbation magnitude, reconstructions were matched within material on $\log_{10}(E_\infty)$ without replacement, using a primary caliper of 0.10 dex and sensitivity calipers from 0.05 to 0.30 dex.

### Control observables

Total electron number was evaluated as a global linear control. The periodic Hartree potential was used as a linear nonlocal comparator, with the $G=0$ component fixed to zero. The primary Hartree metric was relative root-mean-square potential error. Pooled log–log slopes, material-level $R^2$, monotonicity and local response exponents were evaluated separately so that overall scaling was not conflated with local ladder reversals.

### Re-derived Bader charge

Bader partitioning assigns grid points to atom-centred basins defined by the density topology [8–10]. Because the basin depends on the input density, the partition was recomputed for every reconstructed field. The primary chemical-fidelity metric was the maximum absolute per-atom charge difference between reconstructed and reference analyses. Fixed-basin calculations, in which the reference basin labels were retained, were used only for mechanism analysis.

### Protocol A.1 and eligibility

For material $m$, Protocol A.1 applies five pre-specified fixed-seed uniform perturbations at an amplitude equal to the material's float32 $L_\infty$ scale. Bader basins and charges are re-derived after each perturbation. The stability floor $f_m$ is the maximum induced Bader deviation across the five probes.

For a requested Bader tolerance $\tau$,

$$
\mathrm{eligible}(m,\tau) \equiv f_m < \tau.
$$

For reconstruction $r$ of material $m$ with re-derived Bader error $\Delta Q_B(r)$,

$$
\mathrm{certified}(r,\tau) \equiv \mathrm{eligible}(m,\tau) \land \Delta Q_B(r)<\tau.
$$

If $f_m\geq\tau$, the material–threshold pair is assigned `NON_EVALUABLE_BADER_UNSTABLE` and is counted as neither a codec success nor a codec failure at that tolerance.

### Binary-to-three-state reclassification

The Figure 3 audit uses one material–codec decision at a fixed Bader threshold as the analysis unit. For each of 254 development materials and each of three codecs, the frozen tolerance ladder was reduced to (i) a naive binary diagnostic that ignores eligibility and (ii) the stability-qualified decision. A naive pass was recorded when any available reconstruction satisfied the Bader threshold irrespective of eligibility. The qualified decision first applied the material-level Protocol A.1 flag and then determined whether any reconstruction was certified. This yielded 762 decisions per threshold assigned to **certified**, **eligible but not certified**, or **non-evaluable**. Reclassification fractions were calculated among naive failures; naive passes on non-evaluable pairs were reported separately.

### Bader mechanism decomposition

For representative systems, the Bader charge change was decomposed into a density-change contribution evaluated on the reference domain and a residual domain-migration contribution. Per-atom decompositions were evaluated together with tolerance-ladder trajectories and voxel-reassignment diagnostics. This decomposition was used to identify a Bader-specific mechanism and was not extrapolated to observables with different operators.

### External confirmation

The external cohort was kept separate from development analyses. All scientific tolerances, perturbation definitions, eligibility rules and codec-scoring semantics were frozen before external evaluation. The confirmatory analysis assessed pipeline completion, codec error-bound compliance, Protocol A.1 eligibility, tolerance-dependent certified compression ratios and realized-distortion asymmetry.

### Reproducibility

Formal figures are generated from versioned R sources and frozen data tables, with PNG, PDF and SVG exported from the same code. Protocol A remains archived unchanged and Protocol A.1 is the operative qualification procedure. The repository retains the failure registry, stability tables, external manifest, mechanism decompositions, matching outputs, claim–evidence records and chronological analysis history required to reconstruct the reported decisions.

## Data and code availability

Frozen benchmark tables, Protocol A.1 stability outputs, binary-to-three-state reclassification data, mechanism decompositions, realized-distortion matching analyses, external confirmatory results, R figure sources and claim–evidence records are versioned in the public `stloendays/QoI` repository. Archived Protocol A outputs are retained alongside Protocol A.1 so that the change in qualification procedure remains auditable. A persistent archival DOI should be assigned to the final frozen release before publication.

## References

The canonical numbered references are maintained in `paper/REFERENCES.md`. This draft uses references [1–11] from that file.
