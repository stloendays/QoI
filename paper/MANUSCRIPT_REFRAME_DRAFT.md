# Manuscript reframe draft — 2026-09-09

## Working title

**Scientific Fidelity Is QoI-Dependent: Certifying Lossy Compression of Electronic Densities**

Alternative, more mechanism-forward title:

**From Density Error to Chemical Error: QoI-Dependent Failure Modes in Lossy Compression of Electronic Densities**

---

## Abstract

Lossy compression of electronic-structure data is typically controlled by a reconstruction error bound, yet downstream chemical observables need not inherit that bound in a predictable way. We study 6,343 compressed electron-density reconstructions spanning 254 bulk and slab systems and three error-bounded compressors (ZFP, SZ3, and SPERR), and evaluate scientific fidelity through observables with distinct mathematical structure. Preservation of the global electron count is an insufficient certificate of local chemical fidelity: among reconstructions with total-electron deviation below 10^-4 e, 43.15% still exceed 10^-3 e in re-derived Bader-charge error. In contrast, the Hartree potential, a linear nonlocal functional of the density, exhibits a smooth near-linear response to realized pointwise perturbation, with E_H proportional to L_inf^1.02 overall and median per-material log-log R^2 of 0.994-0.997 across codecs. Bader charge on the identical reconstructions is substantially less regular: only 32.4% of material-codec pairs are monotone, local response exponents span -9.3 to +14.1, and individual tolerance steps produce charge-error jumps up to 22,296-fold. At matched Hartree-potential error, 55.4% of reconstructions lie in bins where Bader error spans at least one decade, showing that similar smooth-field fidelity does not determine topological local fidelity. We further show that fixed-basin evaluation systematically understates Bader error, that Bader charge possesses an intrinsic stability floor that must be qualified before compression can be certified, and that equal nominal tolerances across codecs do not imply equal realized perturbations. These results establish a QoI-aware certification framework in which compression fidelity is determined jointly by the realized reconstruction error and the downstream observable operator, rather than by a scalar density norm alone.

---

## Results narrative

### 1. Pointwise reconstruction control is not a scientific fidelity guarantee

The benchmark contains 6,343 frozen reconstruction rows over 254 electronic-density fields, comprising 186 bulk systems and 68 slabs, with ZFP, SZ3, and SPERR evaluated over base and tight tolerance ladders. The central question is not whether the reconstructed density is numerically close to the reference field, but whether a controlled perturbation of the density preserves the scientific observable that is subsequently extracted from it.

A first negative control is total electron number, a global linear integral of the density. Across all reconstructions, electron-count deviation is typically far smaller than re-derived Bader-charge error. More importantly, global conservation and local chemical fidelity decouple directly: 3,205 reconstructions satisfy |Delta N_e| < 10^-4 e while retaining a finite re-derived Bader result, yet 1,383 of these (43.15%) have Bader error >= 10^-3 e. Thus, even very tight conservation of the integrated density is not sufficient to certify atom-resolved charge fidelity.

This control motivates a more general question: is the sensitivity observed for Bader charge simply a consequence of perturbing the density, or does it depend on the mathematical structure of the downstream quantity of interest?

### 2. The downstream QoI operator determines the error-propagation regime

To separate density perturbation magnitude from observable structure, we evaluate the periodic Hartree potential on the same frozen reconstructions. The Hartree map is linear and nonlocal,

V_H(G) = 4 pi rho(G) / |G|^2,  G != 0,

with the G = 0 component gauge-fixed to zero. The primary fidelity metric is the relative RMS potential error, RMS(V_recon - V_ref) / RMS(V_ref).

The full expansion reproduces all 6,343 frozen rows, with ZFP and SPERR passing the frozen reconstruction gate on 100% of rows and SZ3 on 96.2%; the 73 excluded SZ3 rows reproduce realized L_inf to within 2e-5 relative but differ in compressed byte count because part of the frozen SZ3 corpus was generated on a different platform, and are retained explicitly as infrastructure-level reproduction mismatches.

Across the 6,270 gate-passing rows, Hartree-potential error follows an approximately first-order response to the realized density perturbation. The pooled exponent is 1.02, and every codec-by-stratum cell lies between 0.91 and 1.12. Material-level fits are substantially tighter than pooled fits because material-dependent prefactors shift the curves vertically: median per-material R^2 is 0.997 for ZFP, 0.994 for SZ3, and 0.996 for SPERR. Hartree error is monotone in 88.6% of material-codec pairs overall.

Bader charge behaves differently on the identical reconstructed fields. Its pooled log-log slopes are shallower (0.53-0.67 by codec and stratum), R^2 is lower in every codec-by-stratum cell, and only 32.4% of material-codec pairs are monotone. Local response exponents span -9.3 to +14.1, compared with -2.0 to +4.4 for the Hartree potential. The most extreme single-rung Bader jump is 22,296-fold for mp-676693 under ZFP, even though the Hartree response on the same material has R^2 = 0.999.

The contrast is not reducible to one observable simply having a larger error scale. When reconstructions are grouped into 0.5-decade bins of comparable Hartree-potential error, 55.4% of all gate-passing rows fall in bins where the Bader-error P90/P10 ratio is at least 10. This condition appears for all three codecs and in both bulk and slab strata. Similar smooth-field fidelity therefore does not uniquely determine topology-dependent local fidelity.

For slabs, strict rung-to-rung Hartree monotonicity is weaker than for bulk systems, especially for ZFP and SZ3. However, the slab material-level Hartree fits remain tight (median R^2 = 0.965-0.983), and the local decreases are small compared with the magnitude and frequency of Bader jumps. Accordingly, the defensible distinction is smooth, approximately power-law Hartree response versus strongly non-monotone Bader response, not universal Hartree monotonicity.

### 3. Bader fidelity is topology-sensitive and must be evaluated on re-derived basins

The Bader operator differs fundamentally from the preceding controls because its integration domain is itself a functional of the density. The atomic charge is evaluated over a basin Omega_A[rho] whose zero-flux boundary changes when rho changes. Consequently, the total charge error can be decomposed conceptually into an integrand contribution and a domain-migration contribution,

Delta Q_total = Delta Q_integrand + Delta Q_domain.

Evaluating a reconstructed density on the reference basins suppresses this second term and systematically understates the scientific error. The corrected metric therefore re-solves the Bader partition on every reconstruction. Across the benchmark, the fixed-basin metric can underestimate the re-derived error by large factors and can mis-order non-winning codecs. The scientific fidelity contract must therefore be defined on the actual downstream pipeline, not on a frozen surrogate of that pipeline.

The mechanism analysis further shows that domain migration dominates the relevant tight-tolerance regime in representative systems. This explains why Bader error can jump despite a smooth change in pointwise density error: the observable is not merely integrating a perturbed field over a fixed domain; the domain itself can change discontinuously under small perturbations.

### 4. The QoI has its own numerical stability floor

A compression error can only be certified against a target tolerance tau when the downstream observable is itself defined stably at that scale. Protocol A.1 quantifies this intrinsic Bader stability floor using five fixed-seed uniform-noise probes at the float32 L_inf amplitude and takes the maximum induced charge deviation as the qualification floor.

This qualification is essential. Across the 319 development and external systems used for stability analysis, 80% are not evaluable at a 10^-4 e Bader contract and 41% are not evaluable at 10^-3 e under A.1. The earlier float32 round-trip probe substantially understated this floor because it is order-preserving and therefore largely invisible to the watershed tie-breaking mechanism; the corrected noise probe increases the measured floor by a median factor of about 8,700.

The implication is that a compressor cannot be judged against a scientific tolerance that the observable itself cannot resolve. Certification must therefore be conditional on QoI eligibility rather than treating all materials as equally measurable.

### 5. Nominal codec tolerances must be replaced by realized perturbations

Equal requested tolerances do not produce equal realized L_inf across codecs. ZFP uses only a fraction of the nominal error budget relative to SZ3 and SPERR, so comparisons at equal nominal tolerance confound error magnitude with error-field structure.

Within-material matching on realized L_inf reduces the apparent ZFP advantage substantially but does not eliminate it. At the primary 0.10-dex caliper, re-derived Bader error remains 0.557 times that of SZ3 and 0.601 times that of SPERR for matched ZFP reconstructions, whereas SZ3 and SPERR are statistically similar in Bader error. The surviving residual supports an error-structure contribution beyond scalar L_inf magnitude, but does not identify a unique geometric statistic responsible for it.

### 6. Stability-qualified compression remains useful

After correcting the fidelity metric, qualifying Bader stability, and comparing codecs on realized rather than nominal perturbation, lossy compression remains useful over exact alternatives. At the 10^-2 e Bader contract, median best-certified compression ratios reach approximately 52x for SZ3 and 30x for ZFP in bulk systems, compared with only a few-fold reduction for generic lossless baselines. At tighter contracts the achievable ratios fall substantially and codec ordering changes, underscoring that there is no universally best compressor independent of the scientific tolerance.

The proper output of the benchmark is therefore not a single codec ranking but a stability-qualified rate-fidelity frontier conditioned on the downstream QoI.

### 7. The framework reproduces on untouched external systems

The frozen external confirmatory cohort contains 63 systems and 1,689 retained scientific rows, with zero material-level pipeline failures and zero codec bound violations. All three pre-specified directional rate-fidelity expectations reproduce on the completed cohort. External validation also preserves the main mechanistic conclusion that Bader instability is common and not reliably predicted by simple material proxies, while the originally suspected bulk-versus-vacuum stability dichotomy does not generalize.

This external result narrows the scope of the manuscript appropriately: the transferable finding is not that one structural class is universally more fragile, but that downstream QoI stability must be measured rather than assumed.

---

## Discussion

The principal result is that a density reconstruction error does not have a unique scientific meaning. The same reconstructed field can preserve a global integral, perturb a smooth nonlocal potential in an approximately first-order manner, and simultaneously produce a strongly non-monotone error in a topology-dependent atomic partition. The relevant object is therefore not the norm of Delta rho alone, but the composition Q[rho + Delta rho], where Q is the downstream scientific operator.

The three observables examined here form a deliberate hierarchy rather than a collection of unrelated properties. Total electron number is a global linear functional; the Hartree potential is linear but nonlocal; Bader charge introduces a density-dependent topological partition before integration. The progression from global linear to smooth nonlocal to topology-dependent operators is accompanied by a progression from conservation, to smooth error propagation, to strong non-monotonicity and discontinuous local amplification. This does not imply that one observable is intrinsically superior to another. Instead, it shows that fidelity contracts must be constructed in the mathematical space of the observable that will actually be used.

This distinction is particularly important for scientific compression. Error-bounded compressors certify properties of the reconstructed field, typically through a scalar pointwise bound or a rate-distortion objective. Such guarantees are necessary but not sufficient for downstream science. For smooth linear observables, they may propagate predictably. For operators containing segmentation, argmax, thresholding, topology changes, basin reassignment, or other state-dependent decisions, small field perturbations can cross structural boundaries and generate disproportionately large changes in the reported quantity.

Bader analysis provides a concrete instance of this broader class. Its zero-flux basins are not passive integration masks; they are recomputed from the perturbed field. Any fidelity analysis that freezes those basins changes the downstream operator and therefore measures the wrong quantity. The same logic is likely relevant to other scientific workflows that derive discrete structures from continuous fields, but the present data support this claim directly only for Bader partitioning and should not be generalized to all downstream observables without further validation.

The stability floor adds a second qualification. Even a formally exact compressor cannot certify an observable at a tolerance below the reproducibility of the observable itself under numerically negligible perturbations. Scientific compression should therefore separate two questions: whether the observable is numerically identifiable at the target tolerance, and, conditional on that eligibility, how much compression preserves it. Protocol A.1 operationalizes this separation for Bader charge.

The combined framework suggests a practical evaluation sequence for future scientific-data compression studies: measure the realized reconstruction perturbation rather than relying on nominal codec controls; evaluate the complete downstream operator rather than a frozen surrogate; quantify the intrinsic stability of the QoI; and report rate-fidelity only on eligible systems while retaining failures explicitly. Under this formulation, compression quality becomes a property of the pair (compressor, QoI), not of the compressor alone.

---

## Claim boundaries that must remain explicit

1. Do not claim that Hartree potential is universally monotone; slab systems show small rung-to-rung deviations despite high R^2.
2. Do not claim that Hartree is "better" than Bader. The conclusion concerns operator-dependent sensitivity, not scientific value.
3. Do not generalize the Bader topology mechanism to all chemical observables.
4. Do not use equal nominal tolerance as evidence for codec-specific chemistry preservation.
5. Do not present Protocol A as current; A.1 is the corrected stability protocol, with A retained only as provenance.
6. Do not state that slabs are universally less stable than bulk systems; external validation falsifies that generalization.
7. Keep the 73 SZ3 stream-size mismatches visible as infrastructure reproduction mismatches, not silent exclusions.
