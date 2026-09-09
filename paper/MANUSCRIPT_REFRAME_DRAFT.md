# Manuscript reframe draft — 2026-09-09

## Working title

**Scientific Fidelity Is QoI-Dependent: Certifying Lossy Compression of Electronic Densities**

---

## Abstract

Lossy compression of electronic-structure data is typically controlled by a reconstruction error bound, yet downstream chemical observables need not inherit that bound in a predictable way. We study 6,343 compressed electron-density reconstructions spanning 254 bulk and slab systems and three error-bounded compressors (ZFP, SZ3, and SPERR), and evaluate scientific fidelity through observables with distinct mathematical structure. Preservation of the global electron count is an insufficient certificate of local chemical fidelity: among reconstructions with total-electron deviation below 10^-4 e, 43.15% still exceed 10^-3 e in re-derived Bader-charge error. In contrast, the Hartree potential, a linear nonlocal functional of the density, exhibits a smooth near-linear response to realized pointwise perturbation, with E_H proportional to L_inf^1.02 overall and median per-material log-log R^2 of 0.994-0.997 across codecs. Bader charge on the identical reconstructions is substantially less regular: only 32.4% of material-codec pairs are monotone, local response exponents span -9.3 to +14.1, and individual tolerance steps produce charge-error jumps up to 22,296-fold. At matched Hartree-potential error, 55.4% of reconstructions lie in bins where Bader error spans at least one decade, showing that similar smooth-field fidelity does not determine topological local fidelity. We further show that fixed-basin evaluation systematically understates Bader error, that Bader charge possesses an intrinsic stability floor that must be qualified before compression can be certified, and that equal nominal tolerances across codecs do not imply equal realized perturbations. These results establish a QoI-aware certification framework in which compression fidelity is determined jointly by the realized reconstruction error and the downstream observable operator, rather than by a scalar density norm alone.

**Keywords:** scientific data compression; electronic density; quantity of interest; Bader charge; Hartree potential; stability-aware certification

---

## Introduction

Electronic-structure calculations increasingly produce large three-dimensional fields whose storage and movement can rival or exceed the cost of the calculations that generated them. Electron densities are a canonical example: they are retained not only as numerical fields, but as inputs to later analyses, visualization, charge partitioning, electrostatic calculations, and data-driven workflows. Error-bounded lossy compression is therefore attractive because it can reduce storage and I/O while imposing an explicit bound on reconstruction error. Yet a bound on the reconstructed field answers only a numerical question. Scientific reuse depends on whether the downstream observable extracted from that field remains trustworthy.

Most compression benchmarks are naturally organized around rate-distortion quantities such as pointwise error, relative error, peak signal-to-noise ratio, or compression ratio. These metrics are necessary for characterizing a compressor, but they do not by themselves define scientific fidelity. A downstream quantity of interest (QoI) applies an operator Q to the reconstructed density, and the relevant error is therefore Q[rho + Delta rho] - Q[rho], not Delta rho alone. Different operators can respond very differently to the same perturbation: a global integral may average errors away, a smooth nonlocal operator may propagate them continuously, and an operator that contains segmentation or topology-dependent domains can change abruptly when a small perturbation crosses a structural boundary. A scientifically meaningful compression contract must therefore be expressed in the space of the downstream QoI as well as in the space of the reconstructed field.

We examine this distinction using three observables chosen to form a deliberate operator hierarchy on identical electron-density reconstructions. Total electron number is a global linear integral and serves as a conservation control. The periodic Hartree potential is also linear, but nonlocal, and therefore tests whether a smooth field-level response can be predicted from the realized density perturbation. Bader charge is qualitatively different because the integration domains are determined by the topology of the density itself. Its zero-flux basins must be re-derived after reconstruction, so the operator contains a state-dependent partition before integration. This hierarchy allows us to ask whether irregular downstream behavior reflects the magnitude of the density error or the mathematical structure of the observable that consumes it.

Bader analysis also exposes two methodological issues that are easily hidden by conventional rate-distortion evaluation. First, evaluating reconstructed densities on reference basins changes the downstream operator by freezing the very domains that may migrate under perturbation, and can therefore understate scientific error. Second, the Bader observable has its own numerical and topological stability floor: a target charge tolerance is not meaningful for a material if numerically negligible perturbations already change the re-derived charge by more than that tolerance. In addition, nominal codec tolerances are not directly comparable across compressors because the same requested tolerance can produce very different realized L-infinity perturbations. These effects must be separated before any codec-specific scientific advantage can be interpreted.

Here we build a QoI-aware certification framework around a frozen benchmark of 6,343 compressed electron-density reconstructions from 254 bulk and slab systems, evaluated with ZFP, SZ3, and SPERR. We first establish operator-dependent error propagation by comparing electron-number conservation, Hartree-potential error, and re-derived Bader error on the same reconstructions. We then decompose Bader error into fixed-basin and topology-driven contributions, qualify material-specific Bader identifiability with the corrected Protocol A.1 stability test, and compare codecs after matching the realized L-infinity perturbation within material. Finally, we test the resulting decision rules on an untouched 63-system external confirmatory cohort. The central result is that scientific fidelity is not a property of a compressor in isolation: it is a property of the pair consisting of the realized reconstruction and the downstream QoI operator.

---

## Results

We organize the results as a sequence of increasingly stringent questions: whether a conventional reconstruction-level control predicts downstream science, whether distinct QoI operators respond similarly on identical reconstructions, whether Bader irregularity is explained by topology-dependent basin migration, whether the observable is identifiable at the requested chemical tolerance, and whether codec differences persist after realized distortion is controlled.

### 1. Pointwise reconstruction control is not a scientific fidelity guarantee

The benchmark contains 6,343 frozen reconstruction rows over 254 electronic-density fields, comprising 186 bulk systems and 68 slabs, with ZFP, SZ3, and SPERR evaluated over base and tight tolerance ladders. The central question is not whether the reconstructed density is numerically close to the reference field, but whether a controlled perturbation of the density preserves the scientific observable that is subsequently extracted from it.

A first negative control is total electron number, a global linear integral of the density. Across all reconstructions, electron-count deviation is typically far smaller than re-derived Bader-charge error. More importantly, global conservation and local chemical fidelity decouple directly: 3,205 reconstructions satisfy |Delta N_e| < 10^-4 e while retaining a finite re-derived Bader result, yet 1,383 of these (43.15%) have Bader error >= 10^-3 e. Thus, even very tight conservation of the integrated density is not sufficient to certify atom-resolved charge fidelity.

This control motivates a more general question: is the sensitivity observed for Bader charge simply a consequence of perturbing the density, or does it depend on the mathematical structure of the downstream quantity of interest?

### 2. The downstream QoI operator determines the error-propagation regime

To separate density perturbation magnitude from observable structure, we evaluate the periodic Hartree potential on the same frozen reconstructions. The Hartree map is linear and nonlocal, with the G = 0 component gauge-fixed to zero. The primary fidelity metric is the relative RMS potential error, RMS(V_recon - V_ref) / RMS(V_ref).

The full expansion reproduces all 6,343 frozen rows, with ZFP and SPERR passing the frozen reconstruction gate on 100% of rows and SZ3 on 96.2%; the 73 excluded SZ3 rows reproduce realized L_inf to within 2e-5 relative but differ in compressed byte count because part of the frozen SZ3 corpus was generated on a different platform, and are retained explicitly as infrastructure-level reproduction mismatches.

Across the 6,270 gate-passing rows, Hartree-potential error follows an approximately first-order response to the realized density perturbation. The pooled exponent is 1.02, and every codec-by-stratum cell lies between 0.91 and 1.12. Material-level fits are substantially tighter than pooled fits because material-dependent prefactors shift the curves vertically: median per-material R^2 is 0.997 for ZFP, 0.994 for SZ3, and 0.996 for SPERR. Hartree error is monotone in 88.6% of material-codec pairs overall.

Bader charge behaves differently on the identical reconstructed fields. Its pooled log-log slopes are shallower (0.53-0.67 by codec and stratum), R^2 is lower in every codec-by-stratum cell, and only 32.4% of material-codec pairs are monotone. Local response exponents span -9.3 to +14.1, compared with -2.0 to +4.4 for the Hartree potential. The most extreme single-rung Bader jump is 22,296-fold for mp-676693 under ZFP, even though the Hartree response on the same material has R^2 = 0.999.

The contrast is not reducible to one observable simply having a larger error scale. When reconstructions are grouped into 0.5-decade bins of comparable Hartree-potential error, 55.4% of all gate-passing rows fall in bins where the Bader-error P90/P10 ratio is at least 10. This condition appears for all three codecs and in both bulk and slab strata. Similar smooth-field fidelity therefore does not uniquely determine topology-dependent local fidelity.

For slabs, strict rung-to-rung Hartree monotonicity is weaker than for bulk systems, especially for ZFP and SZ3. However, the slab material-level Hartree fits remain tight (median R^2 = 0.965-0.983), and the local decreases are small compared with the magnitude and frequency of Bader jumps. Accordingly, the defensible distinction is smooth, approximately power-law Hartree response versus strongly non-monotone Bader response, not universal Hartree monotonicity.

The operator-dependent contrasts are summarized in Figure 2 using the locked data-driven render from `figures/R/figure2_qoi_hierarchy.R`.

### 3. Bader fidelity is topology-sensitive and must be evaluated on re-derived basins

The Bader operator differs fundamentally from the preceding controls because its integration domain is itself a functional of the density. The atomic charge is evaluated over a basin Omega_A[rho] whose zero-flux boundary changes when rho changes. Consequently, the total charge error can be decomposed conceptually into an integrand contribution and a domain-migration contribution,

Delta Q_total = Delta Q_integrand + Delta Q_domain.

Evaluating a reconstructed density on the reference basins suppresses this second term and systematically understates the scientific error. The corrected metric therefore re-solves the Bader partition on every reconstruction. Across the benchmark, the fixed-basin metric can underestimate the re-derived error by large factors and can mis-order non-winning codecs. The scientific fidelity contract must therefore be defined on the actual downstream pipeline, not on a frozen surrogate of that pipeline.

The mechanism analysis further shows that domain migration dominates the relevant tight-tolerance regime in representative systems. This explains why Bader error can jump despite a smooth change in pointwise density error: the observable is not merely integrating a perturbed field over a fixed domain; the domain itself can change discontinuously under small perturbations.

The topology-sensitive amplification mechanism is summarized in the locked Figure 5 render from `figures/R/figure5_topology_mechanism.R`.

### 4. The QoI has its own numerical stability floor

A compression error can only be certified against a target tolerance tau when the downstream observable is itself defined stably at that scale. Protocol A.1 quantifies this intrinsic Bader stability floor using five fixed-seed uniform-noise probes at the float32 L_inf amplitude and takes the maximum induced charge deviation as the qualification floor.

This qualification is essential. Across the 319 development and external systems used for stability analysis, 80% are not evaluable at a 10^-4 e Bader contract and 41% are not evaluable at 10^-3 e under A.1. The earlier float32 round-trip probe substantially understated this floor because it is order-preserving and therefore largely invisible to the watershed tie-breaking mechanism; the corrected noise probe increases the measured floor by a median factor of about 8,700.

The implication is that a compressor cannot be judged against a scientific tolerance that the observable itself cannot resolve. Certification must therefore be conditional on QoI eligibility rather than treating all materials as equally measurable.

### 5. Nominal codec tolerances must be replaced by realized perturbations

Equal requested tolerances do not produce equal realized L_inf across codecs. ZFP uses only a fraction of the nominal error budget relative to SZ3 and SPERR, so comparisons at equal nominal tolerance confound error magnitude with error-field structure.

Within-material matching on realized L_inf reduces the apparent ZFP advantage substantially but does not eliminate it. At the primary 0.10-dex caliper, re-derived Bader error remains 0.557 times that of SZ3 and 0.601 times that of SPERR for matched ZFP reconstructions, whereas SZ3 and SPERR are statistically similar in Bader error. The surviving residual supports an error-structure contribution beyond scalar L_inf magnitude, but does not identify a unique geometric statistic responsible for it.

The realized-distortion-controlled comparison is shown in the locked Figure 6 render from `figures/R/figure6_matched_realized_linf.R`.

### 6. Stability-qualified compression remains useful

After correcting the fidelity metric, qualifying Bader stability, and comparing codecs on realized rather than nominal perturbation, lossy compression remains useful over exact alternatives. At the 10^-2 e Bader contract, median best-certified compression ratios reach approximately 52x for SZ3 and 30x for ZFP in bulk systems, compared with only a few-fold reduction for generic lossless baselines. At tighter contracts the achievable ratios fall substantially and codec ordering changes, underscoring that there is no universally best compressor independent of the scientific tolerance.

The proper output of the benchmark is therefore not a single codec ranking but a stability-qualified rate-fidelity frontier conditioned on the downstream QoI.

### 7. The framework reproduces on untouched external systems

The frozen external confirmatory cohort contains 63 systems and 1,689 retained scientific rows, with zero material-level pipeline failures and zero codec bound violations. All three pre-specified directional rate-fidelity expectations reproduce on the completed cohort. External validation also preserves the main mechanistic conclusion that Bader instability is common and not reliably predicted by simple material proxies, while the originally suspected bulk-versus-vacuum stability dichotomy does not generalize.

This external result narrows the scope of the manuscript appropriately: the transferable finding is not that one structural class is universally more fragile, but that downstream QoI stability must be measured rather than assumed.

---

## Methods

### Study design and frozen benchmark

The study was designed as a frozen, row-level benchmark in which every scientific conclusion is traceable to a specific reconstructed density and downstream evaluation. The primary corpus contains 6,343 reconstruction rows spanning 254 electronic-density fields: 186 bulk systems and 68 slab systems. Each field was evaluated with three error-bounded compressors, ZFP, SZ3, and SPERR, over base and extended tight-tolerance ladders. Once a protocol or table was frozen, later analyses consumed the frozen outputs rather than silently regenerating or replacing earlier results. This separation was used to distinguish scientific findings from platform or pipeline provenance.

The benchmark retains codec identity, requested tolerance, realized reconstruction error, compressed size, compression ratio, system stratum, downstream QoI errors, and stability-qualification flags. Rows that failed a pre-specified reproduction gate were retained as provenance rather than silently removed. In the Hartree expansion, all ZFP and SPERR rows reproduced the frozen reconstruction gate, whereas 73 SZ3 rows reproduced realized L-infinity closely but differed in compressed byte count because part of the frozen SZ3 corpus had been generated on a different platform; these rows were excluded from gate-dependent Hartree summary statistics but remained visible as infrastructure-level mismatches.

### Compression controls and realized distortion

Requested codec tolerance was treated as an input control rather than as a directly comparable physical distortion. The primary field-level distortion variable was the realized L-infinity error of the reconstructed density, with normalization by the density peak-to-peak range where a scale-free comparison was required. Compression ratio was computed from the frozen uncompressed and compressed byte counts. Codec comparisons at equal nominal tolerance were used only as diagnostics because the three compressors consume their nominal error budgets differently.

For comparisons intended to separate distortion magnitude from residual error-field structure, reconstructions were matched within material on log10(realized L-infinity). Matching was performed without replacement using a primary caliper of 0.10 dex. Codec-pair effects were then summarized on the matched rows for re-derived Bader error, compression ratio, and stability-qualified certification rate. Equal-nominal results were retained only to demonstrate the magnitude of the original confounding.

### Downstream quantities of interest

**Electron number.** Total electron number was used as a global linear control because it integrates the density over the simulation cell. The absolute deviation in total electron count was compared directly with the re-derived Bader error on the same reconstruction rows. This control tests whether tight global conservation is sufficient to certify atom-resolved chemical fidelity; it is not used as a substitute for the Bader metric.

**Periodic Hartree potential.** The Hartree potential was evaluated as a linear nonlocal comparator on the same frozen reconstructions. In reciprocal space, the periodic map is proportional to rho(G)/|G|^2 for nonzero reciprocal vectors, with the G = 0 component gauge-fixed to zero. The primary error metric was the relative root-mean-square deviation between reconstructed and reference Hartree potentials. Log-log slopes, material-level R^2 values, monotonicity, and rung-to-rung response were used to characterize how smoothly this QoI propagated realized density perturbations.

**Bader charge.** Bader fidelity was evaluated on re-derived basins: the Bader partition was recomputed from each reconstructed density before atomic charges were compared with the reference result. This is essential because the Bader integration domains are themselves density-dependent. Fixed-basin calculations were retained only as a mechanistic comparator and were not used as the scientific fidelity contract. The benchmark reports the frozen re-derived Bader error metric for each reconstruction and applies material-level stability qualification before a row is counted as certifiable at a specified charge tolerance.

### Topology-mechanism decomposition

To distinguish field perturbation inside a fixed domain from error caused by domain migration, representative systems were analyzed with a decomposition of the re-derived charge change into an integrand contribution and a domain-migration contribution. Conceptually, Delta Q_total = Delta Q_integrand + Delta Q_domain. The integrand term evaluates the density change while retaining the reference basin, whereas the domain term captures the additional change produced when the basin itself is re-solved from the perturbed density.

The mechanism analysis was intentionally used as a Bader-specific explanation rather than generalized to every downstream observable. Figure 5 combines the representative decomposition with full-benchmark ladder diagnostics to show how basin reassignment accompanies irregular rung-to-rung Bader jumps. Association between reassigned voxel fraction and jump severity is reported descriptively and is not interpreted as a unique causal model.

### Protocol A.1 stability qualification

A downstream tolerance was considered scientifically evaluable only when the uncompressed QoI was itself stable at that scale. Protocol A is retained as the archived provenance protocol. The operative Protocol A.1 changes only the numerical probe: it applies five fixed-seed uniform-noise perturbations with amplitude equal to the float32 L-infinity perturbation scale, while preserving the pre-specified tolerance set, exclusion semantics, and reporting rules. The maximum induced re-derived Bader charge deviation across the probes defines the material-specific stability floor used for eligibility.

The chemical tolerances evaluated in the main certification analysis are 10^-4, 10^-3, and 10^-2 e. A material-threshold pair is eligible only when its Protocol A.1 stability floor is below the requested chemical tolerance. Compressor success is then evaluated conditional on that eligibility. Non-evaluable material-threshold pairs are therefore neither counted as compression successes nor as compression failures. This separation prevents a compressor from being penalized for a precision that the downstream observable cannot numerically identify.

### Rate-fidelity certification

For each eligible material-threshold pair, a reconstruction was considered scientifically certified only when the complete downstream pipeline produced a re-derived Bader error below the specified charge tolerance. Compression-ratio summaries were computed from certified rows, and the resulting output is a stability-qualified rate-fidelity frontier rather than a single global codec ranking. Tight-tolerance ladder points were retained to reveal plateaus where reducing the codec tolerance no longer reduces the resolved Bader error.

### External confirmatory cohort

The final external confirmatory cohort was kept separate from development analysis and contains 63 systems with 1,689 retained scientific rows. The cohort was processed with the frozen scientific rules and Protocol A.1 qualification rather than being used to tune thresholds or select favorable materials. Material-level pipeline completion, codec error-bound behavior, rate-fidelity directionality, and the stability conclusions were then evaluated as confirmatory outcomes.

External analysis was also used to test the scope of mechanistic generalizations. The completed cohort reproduced the main decision-level findings while falsifying the stronger claim that slab or vacuum-containing systems are universally less stable than bulk systems. The manuscript therefore retains the transferable conclusion that stability must be measured for the QoI rather than inferred from a simple structural class.

### Statistical analysis and reproducibility

Relationships between realized distortion and downstream error were analyzed in log-log space when both variables were positive. Pooled slopes were used as descriptive summaries, while material-level fits were emphasized when material-dependent prefactors produced vertical offsets in pooled data. Strict rung-to-rung monotonicity was reported separately from R^2 so that small local reversals were not hidden by an otherwise smooth material-level trend. Matched-Hartree-error dispersion was summarized with the Bader-error P90/P10 ratio within 0.5-decade Hartree-error bins.

Figure 5 material-level effects and matched Figure 6 effects use bootstrap confidence intervals where specified by the frozen analysis. The primary realized-distortion matching caliper was 0.10 dex and matching was performed within material without replacement. Figure-generation scripts are written in R, use frozen CSV inputs, and export PNG, PDF, and SVG from the same source. The formal Figure 2, Figure 5, and Figure 6 renders used in the manuscript are generated directly from their repository R scripts rather than from schematic or manually redrawn substitutes.

---

## Discussion

The principal result is that a density reconstruction error does not have a unique scientific meaning. The same reconstructed field can preserve a global integral, perturb a smooth nonlocal potential in an approximately first-order manner, and simultaneously produce a strongly non-monotone error in a topology-dependent atomic partition. The relevant object is therefore not the norm of Delta rho alone, but the composition Q[rho + Delta rho], where Q is the downstream scientific operator.

The three observables examined here form a deliberate hierarchy rather than a collection of unrelated properties. Total electron number is a global linear functional; the Hartree potential is linear but nonlocal; Bader charge introduces a density-dependent topological partition before integration. The progression from global linear to smooth nonlocal to topology-dependent operators is accompanied by a progression from conservation, to smooth error propagation, to strong non-monotonicity and discontinuous local amplification. This does not imply that one observable is intrinsically superior to another. Instead, it shows that fidelity contracts must be constructed in the mathematical space of the observable that will actually be used.

This distinction is particularly important for scientific compression. Error-bounded compressors certify properties of the reconstructed field, typically through a scalar pointwise bound or a rate-distortion objective. Such guarantees are necessary but not sufficient for downstream science. For smooth linear observables, they may propagate predictably. For operators containing segmentation, argmax, thresholding, topology changes, basin reassignment, or other state-dependent decisions, small field perturbations can cross structural boundaries and generate disproportionately large changes in the reported quantity.

Bader analysis provides a concrete instance of this broader class. Its zero-flux basins are not passive integration masks; they are recomputed from the perturbed field. Any fidelity analysis that freezes those basins changes the downstream operator and therefore measures the wrong quantity. The same logic is likely relevant to other scientific workflows that derive discrete structures from continuous fields, but the present data support this claim directly only for Bader partitioning and should not be generalized to all downstream observables without further validation.

The stability floor adds a second qualification. Even a formally exact compressor cannot certify an observable at a tolerance below the reproducibility of the observable itself under numerically negligible perturbations. Scientific compression should therefore separate two questions: whether the observable is numerically identifiable at the target tolerance, and, conditional on that eligibility, how much compression preserves it. Protocol A.1 operationalizes this separation for Bader charge.

The combined framework suggests a practical evaluation sequence for future scientific-data compression studies: measure the realized reconstruction perturbation rather than relying on nominal codec controls; evaluate the complete downstream operator rather than a frozen surrogate; quantify the intrinsic stability of the QoI; and report rate-fidelity only on eligible systems while retaining failures explicitly. Under this formulation, compression quality becomes a property of the pair (compressor, QoI), not of the compressor alone.

The practical consequence is a change in what a compression benchmark should optimize and report. A scientifically useful benchmark should not ask only how many bytes can be removed at a given field norm; it should identify the downstream operator, measure the realized perturbation, verify that the QoI is itself stable at the requested tolerance, and then report the achievable rate-fidelity frontier on eligible cases. This decision-aware ordering converts an apparent codec leaderboard into a reproducible scientific contract and makes negative results informative rather than ambiguous.

---

## Conclusions

Scientific fidelity cannot be inferred from a scalar reconstruction bound alone. Across identical compressed electron densities, total electron number, Hartree potential, and Bader charge occupy distinct error-propagation regimes that follow their operator structure. Global conservation can coexist with failed local charge fidelity; the Hartree potential responds smoothly and approximately first-order to realized perturbation; and Bader charge can change irregularly because the topology-dependent integration domains themselves migrate.

A defensible compression decision therefore requires four linked steps: evaluate the complete downstream operator, qualify the intrinsic stability of the QoI, compare codecs using realized rather than nominal distortion, and report rate-fidelity only on scientifically eligible cases. Under this framework, lossy compression remains useful, but there is no universal codec ranking independent of the QoI and target tolerance. The broader contribution is an evaluation principle: compression quality is a property of the pair (reconstruction, downstream scientific operator), not of the compressor alone.

---

## Data and code availability

The frozen benchmark tables, Protocol A.1 stability outputs, matched-realized-distortion analyses, mechanism-decomposition outputs, and R source files used to generate the formal manuscript figures are versioned in the project repository: https://github.com/stloendays/QoI. The repository retains archived protocol provenance alongside the operative A.1 analysis so that changes in numerical qualification are auditable.

---

## Claim boundaries that must remain explicit

1. Do not claim that Hartree potential is universally monotone; slab systems show small rung-to-rung deviations despite high R^2.
2. Do not claim that Hartree is "better" than Bader. The conclusion concerns operator-dependent sensitivity, not scientific value.
3. Do not generalize the Bader topology mechanism to all chemical observables.
4. Do not use equal nominal tolerance as evidence for codec-specific chemistry preservation.
5. Do not present Protocol A as current; A.1 is the corrected stability protocol, with A retained only as provenance.
6. Do not state that slabs are universally less stable than bulk systems; external validation falsifies that generalization.
7. Keep the 73 SZ3 stream-size mismatches visible as infrastructure reproduction mismatches, not silent exclusions.
