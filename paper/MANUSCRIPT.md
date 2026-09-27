# Numerical stability qualification for downstream-fidelity benchmarks of compressed electronic densities

## Abstract

Scientific-compression benchmarks usually score reconstructed fields against downstream quantities of interest (QoIs), implicitly assuming that the reference QoI is itself stable at the requested tolerance. We test this assumption for Bader charges and introduce **QoI Stability Qualification (QSQ)** before codec scoring. After equalizing compression-search opportunity across 254 systems, screen-rejected material–codec pairs were 20.34-fold more likely than QSQ-eligible pairs to lack a numerical pass at $10^{-3}\,e$. Prospective challenge with 59 unseen perturbations per material gave threshold-exceedance risks of 1.600% versus 81.325%, a 50.83-fold separation under the declared perturbation model. An independent on-grid Bader implementation reproduced all threshold classifications in a 24-system transfer panel, whereas near-grid differences showed that the downstream algorithm remains part of the measurement contract. At matched realized $L_\infty$, a Fourier audit of the Hartree control showed that frequency allocation, rather than pointwise error magnitude alone, explains much of the codec effect; spectral susceptibility accounted for a material-median 62.0% of the absolute-log difference. A coarse charge-transfer direction remained preserved even outside the strict numerical contract, confirming that numerical and qualitative fidelity are distinct targets. These results establish a workflow in which **QoI stability qualification precedes eligibility, compression evaluation and certification**, while downstream fidelity depends jointly on reference stability, the analysis operator and reconstruction-error structure.

**Keywords:** scientific data compression; quantity of interest; benchmark validity; Bader charge; electronic density; numerical stability

## Introduction

Electronic-structure calculations routinely generate high-dimensional floating-point data whose storage, transfer and repeated analysis can become a substantial computational burden. Error-bounded lossy compression has consequently become an important data-reduction strategy in scientific computing, with mature general-purpose compressors including ZFP, SZ3 and SPERR [1–4]. More broadly, lossy compression has been deployed to reduce storage and I/O costs across scientific workflows [5], including quantum-chemistry data such as two-electron integrals and application-specific GAMESS data streams [3,6]. Recent electronic-structure work has also explored lossy reduction inside density-functional calculations, although in that case the compressed object is the atomic-orbital basis rather than a stored real-space electron-density field [7].

The central difficulty is that a field-level error bound does not automatically define the fidelity of every scientific quantity subsequently extracted from the reconstruction. Z-checker formalized systematic post-compression assessment of reconstructed scientific data [8]. Mathematical and algorithmic work has since moved explicitly toward derived quantities: Jiao *et al.* developed error-control theory for several QoI families [9], and multilevel methods have provided quantitative control of user-prescribed derived quantities during data reduction [10]. Application-specific pipelines have further preserved or constrained QoIs in large scientific workflows, including fusion data [11–13]. In parallel, topology-aware compressors have shown that strict pointwise bounds need not preserve discrete topological structure and have introduced explicit topological guarantees [14,15]. Most recently, TOPIQ has addressed statistical prediction of QoI-level bias and uncertainty from compressed data [16]. Together, these studies establish that downstream fidelity must be treated as a first-class scientific requirement. They leave a logically prior question unresolved: **when is the requested QoI tolerance itself a valid benchmark?**

Two targets must be distinguished. Fixed-pipeline fidelity asks whether the decoded field reproduces the numerical result obtained from the exact reference input; this comparison remains well defined even for a sensitive analysis. Robust scientific fidelity additionally asks whether the interpretation survives a declared class of small input changes. We use QSQ to screen this second requirement and report its outcome alongside numerical agreement (Fig. 1). A failed screen does not show that a particular codec discrepancy was not compression-induced, and a successful finite probe panel is not a worst-case stability guarantee.

Bader charge provides a stringent chemical test of this principle. In the quantum theory of atoms in molecules, atomic basins are defined by the topology of the electron-density gradient field [17]. Practical grid-based Bader algorithms have progressively addressed robustness, lattice bias and integration accuracy [18–20], while modern treatments on arbitrary grids make discretization and numerical-topology dependence explicit [21]. A perturbation can therefore change both the density values being integrated and the basin boundaries over which the integration is performed. We use total electron number and the periodic Hartree potential as global-linear and linear-nonlocal controls, respectively, to separate this Bader-specific mechanism from the more general benchmark-validity question.

Here we establish a measurement contract for scientific compression in which numerical stability of the reference QoI is qualified before reconstruction fidelity is scored. Bader charge provides the topology-sensitive test case, while total electron number and the periodic Hartree potential provide structurally distinct controls. We evaluate QSQ with equalized codec search opportunity, prospective perturbations not used to define the gate, and an independent Bader implementation under matched on-grid semantics. We then test the boundary between strict numerical fidelity and a coarser chemical decision, and use a matched-distortion Fourier analysis of the Hartree control to resolve how codec-dependent error structure couples to a known downstream operator. This design separates reference robustness, reconstruction agreement and operator-specific error propagation within one reproducible benchmark.

## Results

### Identical field perturbations propagate differently through downstream operators

The same reconstructed density can be highly faithful for one observable and unreliable for another because the downstream operators have different mathematical structure (Fig. 2). Total electron number provides the simplest control. Among 3,205 reconstructions with an absolute electron-count deviation below $10^{-4}\,e$ and a finite re-derived Bader result, 1,383 (43.15%) nevertheless have a Bader error of at least $10^{-3}\,e$. Tight conservation of a global integral therefore does not certify atom-resolved charge fidelity. The full codec- and tolerance-resolved negative-control matrix is reported in Supplementary Table S8 and Supplementary Fig. S3.

The periodic Hartree potential is nonlocal but linear and behaves much more regularly. Across 6,270 reconstruction-gate-passing rows, Hartree-potential error scales approximately linearly with realized density perturbation, with a pooled log–log exponent of 1.02. Median material-level $R^2$ values are 0.997 for ZFP, 0.994 for SZ3 and 0.996 for SPERR. The response is therefore close to first order over the measured range. Full codec-level scaling, material-level smoothness and reproduction-gate diagnostics are provided in Supplementary Table S9 and Supplementary Fig. S3.

Re-derived Bader charge is substantially less regular. Only 32.4% of material–codec tolerance ladders are strictly monotone, and local response exponents range from −9.3 to +14.1. Individual adjacent tolerance steps can produce large discontinuous changes, including a 22,296-fold illustrative jump. Even when reconstructions are grouped by similar Hartree-potential error, Bader errors remain widely dispersed: 55.4% of gate-passing rows fall in 0.5-decade matched-Hartree bins with a Bader-error P90/P10 ratio of at least 10. These controls do not constitute the central novelty of the study; rather, they establish why a valid scientific-compression benchmark must explicitly include the downstream analysis.

### Reference stability and numerical agreement are distinct benchmark axes

QSQ applies five fixed-seed, non-order-preserving perturbations to each reference density at that material's float32 $L_\infty$ scale. The maximum Bader response defines the QSQ stability floor. A material is eligible when this measured response is below the requested tolerance. This is a finite-panel definition, not an upper bound on every admissible perturbation. The perturbation definition and calibration are reported in Supplementary Table S2 and Supplementary Fig. S2.

Across the 319-system development and external descriptive stability universe, the pre-specified QSQ screen rejects 79.9%, 41.4% and 9.7% at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$. These are screen-rejection fractions, not codec failure rates or universal material properties. The corresponding development-only fractions are 81.9%, 43.7% and 9.8% (Supplementary Table S3; research audit).

Retrospective reclassification rates are sensitive to unequal codec search opportunity, so we tested QSQ in two stronger ways. First, we completed the same four tight settings for every development material. Second, after pre-specifying the QSQ gate, amplitudes and thresholds, we challenged it with 59 fresh perturbations per material. Figure 3 combines these controls: the equal-search experiment tests benchmark difficulty under equal codec opportunity, whereas the prospective experiment tests whether the pre-specified QSQ screen predicts unseen downstream response risk.

Equalizing search opportunity added 1,332/1,332 successful reconstructions. At the primary $10^{-3}\,e$ contract, no-pass risk remained sharply separated: 3.3% for QSQ-eligible versus 66.4% for screen-rejected material–codec pairs, a 20.34-fold ratio. The prospective test was stronger still. Across 14,986/14,986 valid fresh perturbations, QSQ admitted 143/254 materials (56.3% coverage); admitted materials showed 135/8,437 threshold exceedances (1.600%), whereas screen-rejected materials showed 5,326/6,549 (81.325%), giving a 50.83-fold rejected-to-eligible risk ratio. The same directional separation held at the two pre-specified secondary thresholds. Thus, the central empirical result is prospective risk stratification under a declared perturbation model, not a design-independent claim that a fixed percentage of codec failures is invalid.

### A valid stability probe must excite the numerical failure mode

The qualification perturbation must excite the numerical degrees of freedom that can change the downstream analysis. As a negative control, a float32 round-trip perturbation is strongly order-preserving and can leave an on-grid basin assignment unchanged even when comparably small non-order-preserving perturbations alter basin boundaries [18–20] (Fig. 4).

In an 18-material calibration panel, the round-trip perturbation creates a median of 82 exact neighbouring ties and reassigns zero voxels in 9/18 systems, whereas a same-amplitude QSQ perturbation creates no exact neighbouring ties and reassigns zero voxels in only 2/18. Across the paired 254-material development set, the five-seed QSQ floor is a median of approximately $1.6\times10^4$ times the round-trip response, with substantial material-to-material variation (Supplementary Table S7 and Supplementary Fig. S2).

QSQ therefore uses five pre-specified uniform perturbations and takes the maximum response across seeds as the operational stability floor. Relative to a single-seed decision, the five-seed maximum changes eligibility for 35 of 319 systems at $10^{-4}\,e$, 17 at $10^{-3}\,e$, and 2 at $10^{-2}\,e$. A useful stability screen must probe relevant failure directions; a finite probe panel remains an empirical qualification, not a worst-case bound.

### Prospective validation quantifies the separation across thresholds

The prospective component of Fig. 3 challenged the deployed five-seed QSQ gate with 59 pre-registered fresh iid-uniform perturbations for each of the 254 development materials, using the same material-specific amplitude and no retuning. All 14,986 planned trials produced valid Bader outcomes. At the pre-specified primary threshold of $10^{-3}\,e$, QSQ admits 143/254 materials (56.3%). Among their 8,437 fresh trials, 135 exceed the threshold, corresponding to a 1.600% trial-level exceedance risk (95% material-cluster bootstrap interval, 0.782–2.596%). Among the 111 screen-rejected materials, 5,326 of 6,549 fresh trials exceed the threshold, a risk of 81.325% (75.981–86.257%). The rejected-to-eligible risk ratio is 50.83, and 20/143 admitted materials versus 110/111 rejected materials show at least one fresh exceedance.

The prespecified secondary thresholds show the same separation with different acceptance coverage. At $10^{-4}\,e$, 46/254 materials are admitted and fresh exceedance risks are 4.016% versus 86.938% (21.65-fold). At $10^{-2}\,e$, 229/254 are admitted and risks are 0.148% versus 79.593% (537.69-fold). Because the same 59 response vectors support all three thresholds, these are not three independent experiments. The fresh seeds validate prospective discrimination conditional on the development materials and declared iid-uniform perturbation model; they do not establish worst-case stability, simultaneous per-material guarantees, or new-material generalization. A material with zero exceedances in 59 valid iid draws has a one-sided 95% exact per-cell upper bound of approximately 4.95% under the stated Bernoulli model.

### The strictest certified regime approaches the analysis floor

The eligibility-targeted tight tolerance ladder provides a conditional diagnostic of the transition from compression-dominated to analysis-limited behaviour. At the strictest certified Bader contract, $10^{-4}\,e$, the median ratio of resolved Bader error to the QSQ stability floor is 1.09 for ZFP, 1.33 for SZ3 and 1.23 for SPERR; the corresponding 90th percentiles are 3.25, 2.86 and 3.20. The remaining reconstruction error is therefore already of the same order as the independently measured numerical floor.

This relation weakens as the contract is relaxed. At $10^{-3}\,e$, median error-to-floor ratios rise to 2.78–3.55, and at $10^{-2}\,e$ to 10.7–14.6. We therefore describe the strictest certified regime as **floor-scale and consistent with an emerging analysis-limited regime**. The present data do not establish a universal material-by-material equality between a tight-ladder plateau and the QSQ floor, and no such equality is assumed in the certification rule. Threshold- and codec-resolved error-to-floor distributions and the tight-ladder diagnostic are reported in Supplementary Table S6 and Supplementary Fig. S4.

### Basin migration provides a Bader-specific mechanism for irregular amplification

Bader analysis differs from the linear controls because its integration domain is itself a functional of the density (Fig. 5). For atom $A$, the reference charge is integrated over $\Omega_A[\rho]$, whereas the reconstructed charge is evaluated over $\Omega_A[\tilde\rho]$. The total charge deviation therefore combines a change in the integrand with a change in the integration domain, consistent with the density-defined basin construction underlying QTAIM and grid-based Bader analysis [17–20].

Holding the reference basin fixed suppresses the latter contribution and changes the downstream operator being evaluated. We therefore use re-derived basins for scientific certification and retain fixed-basin calculations only as a mechanistic diagnostic. Representative per-atom decompositions show that domain migration can dominate large Bader deviations at tight perturbations, while full tolerance ladders contain abrupt charge changes despite smoothly varying field distortion. This mechanism explains why Bader response can be discontinuous even when smoother observables remain well behaved. It is specific to density-dependent partitioning and is not assumed to generalize to arbitrary QoIs.

We next tested whether QSQ classification transfers across independent Bader implementations. A deterministically stratified 24-system panel spanning bulk and slab densities and four QSQ floor bands was evaluated with the primary on-grid analysis, independent Henkelman on-grid analysis and a Henkelman near-grid variant using the same five perturbation fields. Henkelman on-grid reproduced QSQ eligibility for all 24 systems at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$ (100% agreement; Cohen's $\kappa=1.000$ at each threshold) and preserved the stability-floor ordering (Spearman $\rho=0.995$). The near-grid variant gave 82.6%, 83.3% and 95.8% agreement, with $\rho=0.754$. Thus the classification transfers across an independent implementation when basin-assignment semantics are matched, whereas changing those semantics can shift the qualification boundary. The downstream numerical algorithm is therefore part of the measurement contract (Supplementary Table S11).

### A coarse chemical direction can remain stable outside a strict numerical contract

We next tested whether strict numerical qualification translates directly into a coarse chemical decision. Before inspecting QSQ or compression outcomes, an outcome-blind chemistry and geometry audit of the 68 NOMAD development slabs selected five paired states from GaN electrochemical-surface and RuO₂ CO₂RR datasets, together with a persistent local target atom for each pair. All five pairs passed a pre-specified source-reference gate requiring BaderKit on-grid and independent Henkelman on-grid analyses to agree on the non-zero sign of the target-atom charge change, with $|\Delta q|\ge 0.02\,e$ in both implementations and inter-implementation disagreement no greater than $0.01\,e$.

Across the three codecs and four common tight settings, all 60 reconstructed decisions preserved the reference sign. QSQ at $10^{-3}\,e$ retains 36/60 trials from three of the five pairs, but both the qualified subset and the unqualified set have zero observed sign errors. A strict per-atom numerical-fidelity contract is therefore not equivalent to preservation of a well-separated qualitative charge-transfer direction. The full pair-level decisions and optional independent-solver audit are reported in Supplementary Tables S15-S16.

### Realized distortion, not nominal tolerance, is required for fair codec comparison

Codec tolerances are control inputs rather than common measures of realized perturbation. At equal nominal tolerance, ZFP produces a median realized $L_\infty$ only 0.170 times that of SZ3 and 0.170 times that of SPERR; SZ3 and SPERR are approximately matched. Direct comparison at equal requested tolerance therefore conflates two effects: the magnitude of the realized perturbation and the spatial structure of the codec error (Fig. 6A).

We separate these effects by matching reconstructions within each material on $\log_{10}(L_\infty)$, without replacement, using a primary caliper of 0.10 dex. After matching, ZFP retains lower re-derived Bader error than SZ3 (ratio 0.557; 95% material-bootstrap confidence interval, 0.525–0.598) and SPERR (0.601; 0.534–0.662), whereas SZ3 and SPERR are statistically similar (1.033; 0.976–1.072) (Fig. 6B). The residual persists across calipers from 0.05 to 0.30 dex. These data establish a contribution from error-field structure beyond scalar $L_\infty$ magnitude. Because Bader basin assignment is nonlinear and topology-sensitive, the Bader residual itself cannot be assigned to a single Fourier descriptor from these data alone. We therefore use the linear Hartree control to test whether an analogous matched-distortion codec effect can be resolved mechanistically when the downstream operator is known.

The comparison therefore requires two distinct qualifications: the downstream scientific tolerance must be numerically eligible, and codecs must be compared using measured rather than nominal reconstruction distortion. Failure to control either quantity can create a misleading ranking.

### Fourier error structure explains the matched-distortion Hartree codec effect

We audited the exact 457 ZFP/SZ3 matched pairs from the full-population Hartree analysis, spanning 214 materials, and regenerated the corresponding 914 reconstructions (Fig. 7). The previously observed material-level Hartree-error ratio was reproduced exactly at 0.0776221. To exclude a discrete-FFT artifact, we repeated the calculation with a Nyquist-safe Hermitian Poisson operator. The resulting ratio was 0.0776219, and the direct real-space Hartree error agreed with the Fourier-space Parseval expression to a maximum relative discrepancy of $1.30\times10^{-15}$. The codec effect therefore survives the operator-parity correction.

Let $\mathcal{G}_s$ denote the non-zero reciprocal-space modes that do not lie on an excluded even-grid Nyquist plane. For each reconstruction error field $\Delta\rho$, the Nyquist-safe Hartree-weighted spectral energy is

$$
W_H = \sum_{G\in\mathcal{G}_s}\frac{|\Delta\rho(G)|^2}{|G|^4},
$$

and we define the spectral Hartree susceptibility as $S_H=W_H/E$, where $E=\sum_{G\in\mathcal{G}_s}|\Delta\rho(G)|^2$. Pairwise, the matched-distortion Hartree ratio decomposes exactly as

$$
R_H=
\sqrt{\frac{E_{\mathrm{ZFP}}}{E_{\mathrm{SZ3}}}}
\sqrt{\frac{S_{H,\mathrm{ZFP}}}{S_{H,\mathrm{SZ3}}}}.
$$

The separately aggregated material-level centers are 0.376 for the total spectral-energy factor and 0.203 for the spectral-susceptibility factor; the exact multiplicative identity is enforced pairwise rather than between these separately aggregated centers. Frequency allocation contributes a material-median 62.0% of the absolute log-scale effect. Consistently, 99.5% of materials have lower ZFP spectral Hartree susceptibility, 98.1% have a higher ZFP spectral centroid, and 99.1% have a lower ZFP low-$G$ error-energy fraction; the material-level low-$G$ fraction ratio is 0.416.

Thus the matched-$L_\infty$ codec effect is not explained by pointwise error magnitude alone. ZFP places substantially less of its reconstruction-error energy in the long-wavelength modes that the Hartree operator amplifies most strongly through the $|G|^{-4}$ squared-error weighting. This result does not imply that the Bader residual is controlled by the same Fourier statistic; rather, it establishes the broader mechanism that scientific fidelity depends on the interaction between reconstruction-error structure and the downstream operator.

### Stability-qualified rate–fidelity rankings depend on the scientific contract

Among eligible material–threshold pairs, we select the highest compression ratio that satisfies the Bader contract on the fixed codec ladder. The resulting rate–fidelity frontier is strongly tolerance dependent. At $10^{-2}\,e$ in the development set, SZ3 provides the largest median certified compression ratio in both bulk and slab strata (51.8× [47.7, 60.3] and 67.8× [59.6, 70.6], respectively), ahead of ZFP (30.0× [27.1, 31.9] and 40.5× [35.8, 44.9]) and SPERR (11.5× [10.1, 13.2] and 8.1× [7.7, 8.6]). At $10^{-3}\,e$, ZFP and SZ3 become much closer, and at $10^{-4}\,e$ ZFP has the advantage among the much smaller eligible cohort. Thus, no single codec dominates across scientific contracts. Exact machine-readable sources are mapped through the repository reader-facing provenance index.

These rankings must be interpreted together with eligibility. Tightening the Bader tolerance does not merely reduce the compression ratio that can be certified; it also changes which material–threshold pairs support a meaningful scientific decision. Reporting a codec success rate without the corresponding eligible denominator would therefore mix compression performance with numerical identifiability.

### Pre-specified decision rules reproduce on an untouched external cohort

We finally applied the complete qualification and certification procedure to 63 untouched external systems without changing thresholds, probe definitions or codec-scoring rules (Fig. 8). The external analysis produced 1,689 retained rows, with zero material-level pipeline failures and zero codec error-bound violations; three row-level Bader-solver failures remain explicitly recorded in the audit. This primary 63-system confirmatory cohort is distinct from the 65-system external descriptive/stability universe used in the 319-system stability summary (Supplementary Table S1).

QSQ identifies 16 of 63 systems as eligible at $10^{-4}\,e$, 42 at $10^{-3}\,e$, and 57 at $10^{-2}\,e$. The certified rate–fidelity ranking again changes with the contract. At $10^{-4}\,e$, median best-certified compression ratios are approximately 13.0× for ZFP, 12.1× for SZ3 and 5.2× for SPERR. At $10^{-3}\,e$, ZFP and SZ3 are both approximately 18.8×, compared with 6.4× for SPERR. At $10^{-2}\,e$, SZ3 reaches 65.9×, ahead of ZFP at 40.6× and SPERR at 10.8×.

The external cohort therefore reproduces the operational conclusions without retuning: the measurable cohort expands as the requested tolerance is relaxed, and the preferred codec depends on the scientific contract. The result also shows that numerical eligibility is better measured directly than inferred from broad structural categories.

## Discussion

The central result is that downstream compression scoring is scientifically interpretable only when the reference QoI can support the requested tolerance under a declared numerical-analysis contract. QSQ makes this requirement explicit. In the present Bader-charge benchmark, equalized search opportunity shows that screen-rejected material–codec pairs remain far more difficult to satisfy than eligible pairs, and prospective perturbations show an even stronger separation in unseen response risk. The classification also transfers across an independent on-grid Bader implementation. Together, these controls support QSQ as an empirical qualification of the reference analysis rather than a retrospective relabelling of compression outcomes.

This contribution is complementary to existing QoI-aware compression. Mathematical approaches can propagate or bound compression error for prescribed derived quantities [9,10], application-specific systems can enforce QoI fidelity in operational workflows [11–13], and topology-preserving methods can protect selected discrete structures that ordinary pointwise bounds do not preserve [14,15]. Statistical approaches such as TOPIQ further estimate QoI-level bias and uncertainty after compression [16]. QSQ addresses a logically distinct question: whether the uncompressed analysis itself is sufficiently stable for the requested tolerance to serve as a meaningful scientific contract. Fixed-pipeline agreement and robustness of the reference interpretation are therefore separate quantities and should be reported as such.

Bader charge exposes this distinction because the integration domain depends on the density. Reconstruction can alter both the values being integrated and the basin boundaries, so fixed-domain scoring suppresses a physically relevant numerical channel. The representative decompositions show that basin migration can dominate tight-tolerance deviations, while the strictest certified reconstructions approach the independently measured QSQ floor, consistent with an emerging analysis-limited regime. The qualification procedure must therefore perturb the degrees of freedom that can change basin assignment; the order-preserving round-trip control demonstrates why perturbation magnitude alone is insufficient. The implementation-transfer experiment adds a second boundary: classification is highly reproducible when on-grid basin semantics are matched, but changes when the assignment algorithm changes. Numerical identifiability is consequently a property of the material–analysis pair, not of the material alone.

The codec comparison reveals a complementary upstream requirement. Equal nominal tolerances do not produce equal realized perturbations, so codec ranking must first be conditioned on measured distortion. Even after matching realized $L_\infty$, residual differences remain. The Hartree control makes this residual interpretable because its downstream operator is known: the $|G|^{-4}$ weighting of squared density error strongly amplifies long-wavelength components, and ZFP places substantially less reconstruction-error energy in those modes than SZ3. Frequency allocation accounts for a material-median 62.0% of the absolute-log Hartree codec effect. Thus a scalar norm can be insufficient even after it is measured correctly; scientific fidelity depends on how the reconstruction-error field couples to the downstream operator.

The chemical-decision case study clarifies the opposite boundary. All tested charge-transfer directions remain correct even when strict numerical qualification excludes part of the set. A $10^{-3}\,e$ per-atom charge contract and the sign of a well-separated charge-transfer change are different scientific questions, with different margins and therefore different qualification requirements. Qualification should not be interpreted as a universal pass/fail label on a dataset; it is meaningful only relative to the decision being protected. This distinction is useful beyond Bader analysis because many scientific workflows mix high-precision numerical outputs with coarser categorical or directional conclusions.

The present evidence is deepest for one topology-sensitive chemical observable, and the appropriate perturbation model will differ for other analyses. Nevertheless, the benchmark suggests a general design principle for scientific compression: a fidelity claim should specify **(i)** the stability of the reference QoI, **(ii)** the downstream operator or algorithm, **(iii)** the scientific tolerance or decision margin, and **(iv)** the realized structure of the reconstruction error. These elements determine whether a target is evaluable and, if so, which compressed representation satisfies it at the best rate. For electronic-structure workflows, this shifts the question from whether charge-density data can be compressed at all [3,5–7] to whether the compressed representation preserves the particular analysis that will be performed on it. The same logic should apply whenever downstream scientific operators are numerically sensitive, nonlinear, topological, spatially selective or spectrally selective.

## Methods

### Benchmark design

The development benchmark contains 6,343 reconstruction rows from 254 electronic-density fields: 186 bulk systems and 68 slabs. ZFP, SZ3/SZ and SPERR were evaluated over a common base tolerance ladder and an extended tight ladder using their respective error-bounded compression frameworks [2–4]. Each row records material identity, codec configuration, requested tolerance, realized distortion, compressed size, downstream QoI errors and stability-qualification status. All analyses use versioned benchmark outputs with fixed cohort and denominator definitions (Supplementary Table S1).

Rows that fail a pre-specified solver or reproduction condition remain in the audit trail. Scientific non-evaluability, downstream solver failure and infrastructure mismatch are recorded separately rather than collapsed into a single missing-data category.

### Realized reconstruction distortion

Requested codec tolerance was treated as a control parameter. The primary realized field distortion was

$$
E_\infty = \lVert \tilde{\rho}-\rho \rVert_\infty,
$$

where $\rho$ and $\tilde{\rho}$ denote the reference and reconstructed densities. Compression ratios were computed from recorded byte counts. Equal-nominal comparisons were retained as diagnostics. To compare codecs at similar actual perturbation magnitude, reconstructions were matched within material on $\log_{10}(E_\infty)$ without replacement, using a primary caliper of 0.10 dex and sensitivity calipers from 0.05 to 0.30 dex.

### Control observables

Total electron number was evaluated as a global linear control. The periodic Hartree potential was used as a linear nonlocal comparator, with the $G=0$ component fixed to zero. The primary Hartree metric was relative root-mean-square potential error. Pooled log–log slopes, material-level $R^2$, monotonicity and local response exponents were evaluated separately so that overall scaling was not conflated with local ladder reversals.

### Fourier-spectrum mechanism audit

The mechanistic audit used the exact 457 ZFP/SZ3 pairs from the full-population within-material realized-$L_\infty$ matching analysis, covering 214 materials. The corresponding 914 reconstructions were regenerated from the versioned codec rows, and each regenerated realized $L_\infty$ value and reference-implementation Hartree relative RMSE had to reproduce the stored matched-pair target before the pair entered the spectral analysis.

For reconstruction error $\Delta\rho(\mathbf r)=\tilde{\rho}(\mathbf r)-\rho(\mathbf r)$, we evaluated the real-to-complex discrete Fourier transform $\Delta\rho(\mathbf G)$. On even grids in non-orthogonal cells, Nyquist-plane modes can be alias-equivalent under sign reversal while the continuum $|G|^2$ expression contains cross terms. We therefore retained the reference Hartree implementation as a reproduction diagnostic and defined a Nyquist-safe Hermitian operator for the mechanism audit by setting $G=0$ and all even-grid Nyquist-plane modes to zero and applying $4\pi/|G|^2$ to all remaining modes. Let $\mathcal{G}_s$ denote the non-zero modes outside those excluded Nyquist planes. The resulting operator obeys

$$
\mathrm{RMS}(\Delta V_H)^2
=
\frac{(4\pi)^2}{N^2}
\sum_{G\in\mathcal{G}_s}\frac{|\Delta\rho(G)|^2}{|G|^4}
$$

to numerical precision, where $N$ is the number of real-space grid points.

Frequency location was expressed as $q=|G|/G_{\max}$ over the Nyquist-safe non-zero modes. Low-$G$ and high-$G$ regions were defined as $q\le 0.25$ and $q\ge 0.75$, respectively. We recorded total spectral error energy, low- and high-$G$ fractions, the error-energy-weighted spectral centroid, the Hartree-weighted energy $W_H$, and the spectral Hartree susceptibility $S_H=W_H/E$. For each matched pair, the safe Hartree ratio was decomposed exactly into the square root of the total spectral-energy ratio and the square root of the susceptibility ratio. Material-level centers and 95% bootstrap intervals were computed after taking within-material medians on the log scale. Because the two decomposition factors are aggregated separately across materials, their reported centers are descriptive summaries; exact multiplicative closure is assessed pairwise.

### Re-derived Bader charge

Bader partitioning assigns grid points to atom-centred basins defined by the topology of the electron density [17]. The practical grid-based formulation and its numerical integration properties are established in refs. [18–21]. Because the basin depends on the input density, the partition was recomputed for every reconstructed field. The primary chemical-fidelity metric was the maximum absolute per-atom charge difference between reconstructed and reference analyses. Fixed-basin calculations, in which the reference basin labels were retained, were used only for mechanism analysis.

### Independent implementation-transfer validation

Implementation dependence was evaluated on a deterministic 24-system panel stratified by system type (bulk or slab) and four QSQ stability-floor bands, with three systems selected per stratum by a fixed hash order. The same five perturbation seeds and material-specific amplitudes were used without retuning. For each system we evaluated the baseline and five perturbed densities with BaderKit on-grid, independent Henkelman on-grid and Henkelman near-grid analyses. Eligibility-transfer statistics were computed at the same $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$ thresholds used elsewhere.

This test evaluates transfer across numerical Bader implementations on fixed density grids; it is not an electronic-structure grid-convergence test.

### Outcome-blind chemical-decision case study

The chemical-decision case-study cohort was constructed before reading QSQ, codec or Bader outcomes for candidate inclusion. Starting from the 68 NOMAD development slab states, primary pairs were required to share the same NOMAD upload provenance, density-grid shape and lattice within fixed tolerances; state B had to add one to four H/C/O atoms; all state-A atoms had to map to same-element atoms in state B within 0.35 Å; and a persistent host atom within 3.0 Å of an added atom was selected as the target using geometry only. This yielded five pairs across two source uploads.

For each pair and solver $s$, the qualitative endpoint was the sign of $\Delta q_s=q_s(B,\mathrm{target}_B)-q_s(A,\mathrm{target}_A)$. A binary source reference was accepted only when BaderKit 0.10.2 on-grid and Henkelman Bader 1.05 on-grid gave the same non-zero sign, both had $|\Delta q|\ge0.02\,e$, and their $\Delta q$ values differed by at most $0.01\,e$. All five pairs met this rule. Each state was then compressed with ZFP, SZ3 and SPERR at the common tight relative-tolerance ladder $\{10^{-7},3\times10^{-7},10^{-6},3\times10^{-6}\}$, giving 60 pair-codec-setting decisions. QSQ retention required both states in a pair to pass the five-seed QSQ screen at $10^{-3}\,e$.

The resolved analysis contains 216/216 successful compressed solver cells. No new electronic-structure calculation was used in this case study; the source reference is a two-implementation on-grid consensus rather than a grid-converged physical Bader truth.

### QoI Stability Qualification and eligibility

For material $m$, QSQ applies five pre-specified fixed-seed uniform perturbations at an amplitude equal to the material's float32 $L_\infty$ scale. Bader basins and charges are re-derived after each perturbation. The stability floor $f_m$ is the maximum induced Bader deviation across the five probes. The exact seed set, order-preserving control comparison and decision semantics are given in Supplementary Table S2.

For a requested Bader tolerance $\tau$,

$$
\mathrm{eligible}(m,\tau) \equiv f_m < \tau.
$$

For reconstruction $r$ of material $m$ with re-derived Bader error $\Delta Q_B(r)$,

$$
\mathrm{certified}(r,\tau) \equiv \mathrm{eligible}(m,\tau) \land \Delta Q_B(r)<\tau.
$$

If $f_m\geq\tau$, the material–threshold pair is assigned `NON_EVALUABLE_BADER_UNSTABLE` under the operational QSQ classification. Numerical agreement or disagreement is still retained on a separate axis. Here, certified denotes this finite-panel rule, not a worst-case or calibrated probabilistic guarantee.

### Binary-to-three-state sensitivity audit

The reclassification sensitivity audit uses one material–codec decision at a fixed Bader threshold as the analysis unit. For each of 254 development materials and each of three codecs, the available tolerance ladder was reduced to (i) a naive binary diagnostic that ignores eligibility and (ii) the stability-qualified decision. A naive pass was recorded when any available reconstruction satisfied the Bader threshold irrespective of eligibility. The qualified decision first applied the material-level QSQ eligibility flag and then determined whether any reconstruction was certified. This yielded 762 decisions per threshold assigned to **certified**, **eligible but not certified**, or **non-evaluable**. Reclassification fractions were calculated among naive failures; naive passes on non-evaluable pairs were reported separately.

### Common-ladder completion and prospective perturbation validation

The common-ladder audit uses the versioned master table without changing eligibility, thresholds or reconstruction outputs. We compare the full record, base-only rows, and the subset of base rungs observed for all three codecs within each material. We then prospectively complete the four pre-existing tight settings for all 111 materials that did not originally receive them, for 1,332 additive material–codec–setting evaluations. Numerical pass means that at least one available reconstruction has re-derived Bader error below the threshold; no-pass means that no evaluated rung passes, not that the codec could never pass under an untested setting. The 6,343-row development benchmark remains unchanged, and the additive common-tight results are stored separately. Material-cluster bootstrap intervals preserve codec observations within resampled materials.

For prospective QSQ validation, the five-seed gate, thresholds and material-specific perturbation amplitudes were pre-specified before execution. Each of the 254 development materials received 59 fresh seed labels (10000–10058) with deterministic PCG64 stream seeds generated from SHA-256 over material identity, perturbation family and seed label. The work order contained 14,986 unique material–seed keys and was hashed before execution. The primary endpoint was fresh Bader response $\geq10^{-3}\,e$; $10^{-4}$ and $10^{-2}\,e$ were pre-specified secondary endpoints. We report trial-level exceedance risk separately in QSQ-eligible and screen-rejected groups, acceptance coverage, the rejected-to-eligible risk ratio and material-cluster bootstrap intervals. The five-seed rule was not modified after observing fresh outcomes. All 14,986 planned trials produced valid outcomes. Exact manifests and machine-readable summaries are mapped through the repository reader-facing provenance index.

### Bader mechanism decomposition

For representative systems, the Bader charge change was decomposed into a density-change contribution evaluated on the reference domain and a residual domain-migration contribution. Per-atom decompositions were evaluated together with tolerance-ladder trajectories and voxel-reassignment diagnostics. This decomposition was used to identify a Bader-specific mechanism and was not extrapolated to observables with different operators.

### External confirmation

The external cohort was kept separate from development analyses. All scientific tolerances, perturbation definitions, eligibility rules and codec-scoring semantics were pre-specified before external evaluation. The confirmatory analysis assessed pipeline completion, codec error-bound compliance, QSQ eligibility, tolerance-dependent certified compression ratios and realized-distortion asymmetry. Supplementary Table S1 records the distinct 63-system confirmatory and 65-system descriptive/stability external universes.

### Reproducibility

Formal figures are generated from versioned R sources and versioned data tables, with PNG, PDF and SVG exported from the same code. QSQ is the operative qualification procedure; superseded controls are retained only in repository provenance. A reader-facing provenance index maps the stable scientific names used in the manuscript to exact machine-readable artifacts without exposing development identifiers in the scientific narrative. The repository also retains the failure registry, external manifest, mechanism decompositions, matching outputs and claim–evidence records required to reconstruct the reported decisions.

## Data and code availability

The public `stloendays/QoI` repository contains the benchmark tables, prospective QSQ validation outputs, stability-qualification results, mechanism decompositions, realized-distortion matching analyses, external confirmation, figure sources and claim–evidence records used in this study. The Fourier-spectrum mechanism audit includes the exact matched-pair table, reconstruction-level spectral metrics, radial spectra, summary statistics and R source for Fig. 7. The repository reader-facing provenance index provides stable scientific names for these assets and maps them to the exact implementation files. Superseded controls are retained separately for auditability. A DOI-backed archival snapshot of the version associated with the submitted manuscript will accompany the final publication record.

## References

1. Di, S. *et al.* A survey on error-bounded lossy compression for scientific datasets. **ACM Computing Surveys** **57**(11), Article 287, 1–38 (2025). https://doi.org/10.1145/3733104.
2. Lindstrom, P. Fixed-rate compressed floating-point arrays. **IEEE Transactions on Visualization and Computer Graphics** **20**, 2674–2683 (2014). https://doi.org/10.1109/TVCG.2014.2346458.
3. Liang, X. *et al.* SZ3: A modular framework for composing prediction-based error-bounded lossy compressors. **IEEE Transactions on Big Data** **9**, 485–498 (2023). https://doi.org/10.1109/TBDATA.2022.3201176.
4. Li, S., Lindstrom, P. & Clyne, J. Lossy scientific data compression with SPERR. In **2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)**, 1007–1017 (IEEE, 2023). https://doi.org/10.1109/IPDPS54959.2023.00104.
5. Cappello, F. *et al.* Use cases of lossy compression for floating-point data in scientific data sets. **The International Journal of High Performance Computing Applications** **33**, 1201–1220 (2019). https://doi.org/10.1177/1094342019853336.
6. Gok, A. M., Di, S., Alexeev, Y., Tao, D., Mironov, V., Liang, X. & Cappello, F. PaSTRI: Error-bounded lossy compression for two-electron integrals in quantum chemistry. In **2018 IEEE International Conference on Cluster Computing (CLUSTER)**, 1–11 (IEEE, 2018). https://doi.org/10.1109/CLUSTER.2018.00013.
7. Lara, A. O., Talbot, J. J., Wang, Z. & Head-Gordon, M. An algorithm for atom-centered lossy compression of the atomic orbital basis in density functional theory calculations. **Journal of Chemical Theory and Computation** **22**, 3327–3340 (2026). https://doi.org/10.1021/acs.jctc.5c01988.
8. Tao, D., Di, S., Guo, H., Chen, Z. & Cappello, F. Z-checker: A framework for assessing lossy compression of scientific data. **The International Journal of High Performance Computing Applications** **33**, 285–303 (2019). https://doi.org/10.1177/1094342017737147.
9. Jiao, P., Di, S., Guo, H., Zhao, K., Tian, J., Tao, D., Liang, X. & Cappello, F. Toward quantity-of-interest preserving lossy compression for scientific data. **Proceedings of the VLDB Endowment** **16**, 697–710 (2022). https://doi.org/10.14778/3574245.3574255.
10. Ainsworth, M., Tugluk, O., Whitney, B. & Klasky, S. Multilevel techniques for compression and reduction of scientific data—quantitative control of accuracy in derived quantities. **SIAM Journal on Scientific Computing** **41**, A2146–A2171 (2019). https://doi.org/10.1137/18M1208885.
11. Gong, Q. *et al.* Maintaining trust in reduction: Preserving the accuracy of quantities of interest for lossy compression. In **Driving Scientific and Engineering Discoveries Through the Integration of Experiment, Big Data, and Modeling and Simulation**, Communications in Computer and Information Science **1512**, 22–39 (Springer, 2022). https://doi.org/10.1007/978-3-030-96498-6_2.
12. Lee, J., Gong, Q., Choi, J., Banerjee, T., Klasky, S., Ranka, S. & Rangarajan, A. Error-bounded learned scientific data compression with preservation of derived quantities. **Applied Sciences** **12**, 6718 (2022). https://doi.org/10.3390/app12136718.
13. Banerjee, T., Lee, J., Choi, J., Gong, Q., Chen, J., Chang, C.-S., Klasky, S., Rangarajan, A. & Ranka, S. Online and scalable data compression pipeline with guarantees on quantities of interest. In **2023 IEEE 19th International Conference on e-Science (e-Science)**, 1–10 (IEEE, 2023). https://doi.org/10.1109/e-Science58273.2023.10254934.
14. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving topology in error-bounded lossy compression. **IEEE Transactions on Visualization and Computer Graphics** **30**, 1302–1312 (2024). https://doi.org/10.1109/TVCG.2023.3326920.
15. Gorski, N., Liang, X., Guo, H., Yan, L. & Wang, B. A general framework for augmenting lossy compressors with topological guarantees. **IEEE Transactions on Visualization and Computer Graphics** **31**, 3693–3705 (2025). https://doi.org/10.1109/TVCG.2025.3567054.
16. Liu, Y., Jiang, B., Yang, T., Di, S., Underwood, R. & Jin, S. TOPIQ: Statistical error propagation for quantity-of-interest prediction under lossy compression. **arXiv** 2608.26912 (2026). https://arxiv.org/abs/2608.26912.
17. Bader, R. F. W. **Atoms in Molecules: A Quantum Theory** (Oxford University Press, 1990). https://doi.org/10.1093/oso/9780198551683.001.0001.
18. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. **Computational Materials Science** **36**, 354–360 (2006). https://doi.org/10.1016/j.commatsci.2005.04.010.
19. Tang, W., Sanville, E. & Henkelman, G. A grid-based Bader analysis algorithm without lattice bias. **Journal of Physics: Condensed Matter** **21**, 084204 (2009). https://doi.org/10.1088/0953-8984/21/8/084204.
20. Yu, M. & Trinkle, D. R. Accurate and efficient algorithm for Bader charge integration. **The Journal of Chemical Physics** **134**, 064111 (2011). https://doi.org/10.1063/1.3553716.
21. Hutcheon, M. J. & Teale, A. M. Topological analysis of functions on arbitrary grids: Applications to quantum chemistry. **Journal of Chemical Theory and Computation** **18**, 6077–6091 (2022). https://doi.org/10.1021/acs.jctc.2c00649.
