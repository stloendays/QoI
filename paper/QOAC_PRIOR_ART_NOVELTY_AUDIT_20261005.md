# QOAC-H prior-art and novelty audit — 2026-10-05

Status: literature-positioning record for manuscript integration. This is not a claim that no unpublished or unindexed work exists.

## Question audited

What part of QOAC-H is scientifically new, given established work on QoI-preserving scientific compression, transform coding, and electronic-structure compression?

## Bottom line

Do **not** claim any of the following as new:

1. lossy compression designed around a downstream quantity of interest;
2. mapping a QoI tolerance into a compression error-control rule;
3. using a linear-operator norm to guide scientific compression;
4. adaptive or frequency-dependent quantization in transform coding;
5. compression of electron-density- or Hartree-related objects in quantum chemistry.

The defensible contribution is narrower and stronger:

> **QSQ first establishes that the declared Hartree contract is numerically resolvable; a matched-distortion Fourier diagnosis then identifies the exact operator-weighted error geometry, that geometry is converted into a reciprocal-space quantization law, and the decoded field is finally recertified under the original downstream Hartree contract.**

The evidence therefore supports a **diagnosis-to-design** contribution, not a generic "first QoI-aware compressor" claim.

## Closest prior-art families

### 1. MGARD and bounded-linear QoI control

Ainsworth et al., *SIAM Journal on Scientific Computing* 41, A2146–A2171 (2019), DOI 10.1137/18M1208885, developed multilevel compression with quantitative control of user-prescribed derived quantities. MGARD-QoI computes an operator norm and uses the requested QoI tolerance to determine the primary-data compression tolerance. Later XGC work adapted multilevel coefficient quantization to QoI characteristics.

Overlap with QOAC-H:
- downstream linear operators matter;
- operator information can alter quantization/error allocation;
- QoI error can be bounded rather than inferred from generic field error.

Difference:
- MGARD provides a general multilevel norm/error-control construction;
- QOAC-H starts from a measured codec-dependent Hartree failure mechanism and uses the **exact diagonal Fourier symbol** of the periodic Poisson/Hartree operator to define the transform-domain distortion;
- the resulting scientific design law is specific and explicit: squared Hartree error weights density-error modes as (|G|^{-4}), giving the frozen high-rate allocation (Delta_Gpropto |G|^2);
- QOAC-H is embedded in QSQ qualification and post-decode certification, so the target tolerance is not used unless the reference analysis itself resolves it.

Conclusion: MGARD is essential prior art and prevents any broad claim of first operator-aware or first linear-QoI-preserving compression.

### 2. Jiao et al. QoI-preserving scientific compression

Jiao et al., *Proceedings of the VLDB Endowment* 16, 697–710 (2022), DOI 10.14778/3574245.3574255, derive error-control theory that maps requested tolerances for several QoI families into data-level bounds and integrate the result with prediction-based compressors.

Overlap:
- explicit downstream-QoI tolerance;
- mathematically derived relation between data error and QoI error;
- comparison against general-purpose compressors.

Difference:
- the Jiao framework controls QoIs by deriving sufficient raw-data bounds;
- QOAC-H changes **where error is placed in the operator eigenbasis**, rather than merely tightening a scalar or pointwise data bound;
- QOAC-H's central derivation is motivated by an observed codec effect under matched realized distortion.

### 3. QPET

Liu et al., *Proceedings of the VLDB Endowment* 18, 2440–2453 (2025), DOI 10.14778/3742728.3742739, introduced QPET, a portable QoI-preservation framework that uses numerical/probabilistic approximations to derive pointwise error bounds for differentiable univariate and multivariate QoIs and integrates them into several error-bounded compressors.

Overlap:
- QoI-specific compression design;
- substantial compression-ratio improvements under a downstream fidelity criterion;
- portability/error-bound tuning as an optimization problem.

Difference:
- QPET is primarily a pointwise-error-bound auto-tuning layer for differentiable QoIs;
- QOAC-H derives a **global reciprocal-space distortion geometry from the physical operator itself**, then implements a transform codec whose coefficient precision follows that geometry;
- the QOAC-H manuscript claim should therefore be about operator-eigenbasis error allocation plus QSQ/certification, not generic QoI preservation.

### 4. Constraint-satisfaction / learned QoI preservation

Lee et al., *Applied Sciences* 12, 6718 (2022), DOI 10.3390/app12136718, and subsequent scalable work combine learned compression, error-bounded residual coding and a QoI constraint-satisfaction step.

Overlap:
- downstream QoI is part of the compression objective;
- reconstructed data are modified to satisfy derived constraints.

Difference:
- QOAC-H does not repair QoIs after generic compression;
- the downstream operator determines the transform-domain quantizer before coding.

### 5. TOPIQ and post-hoc QoI uncertainty propagation

Liu et al., TOPIQ, arXiv:2608.26912 (2026), predicts QoI-level bias and uncertainty under lossy compression using compact compression-error metadata and operator composition.

Overlap:
- downstream operator structure is explicit;
- generic pointwise error bounds are insufficient.

Difference:
- TOPIQ predicts uncertainty for already-compressed data;
- QOAC-H uses operator structure to **design the compressed representation**, then measures the decoded QoI directly.

### 6. Classical transform coding

Weighted-distortion transform coding and bit allocation are established signal-processing ideas. Goyal, *IEEE Signal Processing Magazine* 18(5), 9–21 (2001), DOI 10.1109/79.952802, reviews the transform/quantization/bit-allocation framework. Standard high-resolution weighted-MSE theory implies coefficient-dependent quantization precision under a weighted quadratic distortion.

Implication for novelty:
- the Lagrange-multiplier algebra leading from a diagonal weighted quadratic distortion to a coefficient-dependent quantizer is **not itself novel**;
- the contribution is identifying the scientific weight from the exact Hartree operator and validating that this diagnosis-derived law materially changes scientific compression performance.

### 7. Electronic-structure and Hartree-related compression

Chinnamsetty et al., *The Journal of Chemical Physics* 127, 084110 (2007), DOI 10.1063/1.2761871, studied best separable tensor approximations of electron densities and Hartree potentials. Lara et al., *Journal of Chemical Theory and Computation* 22, 3327–3340 (2026), DOI 10.1021/acs.jctc.5c01988, compress the atomic-orbital basis using density-matrix-derived natural atomic orbitals. PaSTRI (2018) compresses two-electron integrals.

Overlap:
- compression in electronic-structure calculations;
- electron-density/Hartree-related objects may be compressed or approximated.

Difference:
- these works do not establish the present QSQ-qualified, Hartree-error-certified stored-density codec with (|G|^{-4})-derived reciprocal-space error allocation.

## Targeted-search conclusion

Targeted searches covered combinations of:
- quantity-of-interest preserving lossy compression;
- operator-aware scientific compression;
- Fourier/spectral quantization;
- Poisson/Hartree compression;
- electron-density compression;
- task-aware transform compression.

No retrieved work matched the full combination:

1. qualify the reference measurement contract before codec scoring;
2. diagnose an empirical matched-distortion codec effect through the exact downstream operator;
3. diagonalize that operator in reciprocal space;
4. derive the transform-domain quantization law from the operator-induced distortion;
5. use an explicitly Hermitian, conservative Nyquist representation;
6. certify the actual decoded field with the original downstream QoI;
7. validate on a disjoint frozen cohort and then a full 254-material census.

This supports a differentiated contribution but **does not justify an absolute "first ever" statement**.

## Reader-facing novelty wording

Preferred:

> Prior QoI-preserving compressors derive data-level error controls, adapt multilevel quantization, or enforce downstream constraints. Here the downstream operator is used differently: after the Hartree codec effect is resolved mechanistically in reciprocal space, its exact Fourier weighting is converted into the compression distortion itself. QSQ first establishes that the requested Hartree tolerance is numerically resolvable, and the decoded density is then recertified under that same contract.

Also acceptable:

> This work closes a diagnosis-to-design loop: the same operator that explains codec-dependent Hartree error determines how compression error is allocated.

Avoid:
- "the first QoI-aware compressor";
- "the first operator-aware compressor";
- "the first physics-informed compressor";
- "the first frequency-weighted compressor";
- "the first compression method for electron density or Hartree potential".

## Quantitative evidence available for the claim

Mechanism test:
- 12/12 engineering materials: operator-derived (β=2) allocation beats operator-blind (β=0) at matched storage;
- median Hartree-error ratio = 0.0767117.

Disjoint confirmation:
- 48/48 previously unseen materials analyzable, 0 failures;
- 48/48 QOAC-H wins against each material's best certified ZFP/SZ3/SPERR baseline;
- median CR ratio = 15.016;
- bootstrap 95% CI = [11.204, 21.461];
- bulk median = 11.203; slab median = 25.699;
- 48/48 selected rows also satisfy the Nyquist-safe Hartree guardrail.

Full development-population census:
- 254 materials, 6,350 settings, 0 failures;
- at (\tau_H=10^{-6}), 253/253 comparable materials favor QOAC-H;
- median CR ratio = 12.463;
- 5th percentile = 4.459;
- minimum = 2.444;
- bulk median = 10.960; slab median = 27.733;
- all 254 selected QOAC-H rows satisfy the Nyquist-safe guardrail at this tolerance.

## Manuscript implication

The previous manuscript treated the Fourier Hartree audit as a terminal diagnostic. The new evidence changes the scientific story: diagnosis now produces an actionable codec whose performance is independently confirmed.

Recommended main-text sequence:

1. matched-distortion Fourier mechanism;
2. operator-derived distortion and quantization law;
3. disjoint confirmatory compression comparison;
4. full-population/tolerance census;
5. stability-qualified rate-fidelity decision.

The QSQ contribution remains logically prior: if the requested QoI tolerance is not resolvable, no downstream codec certificate should be interpreted scientifically.
