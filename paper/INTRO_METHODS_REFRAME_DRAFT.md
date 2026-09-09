# Introduction and Methods reframe draft — 2026-09-09

## Introduction

Lossy compression of electronic-structure data is usually evaluated in the space in which the compressor operates: pointwise or norm-bounded distortion of a scalar field. That description is necessary for numerical control, but it is not sufficient for scientific use. Electronic densities are rarely an endpoint. They are inputs to downstream operators that produce chemically meaningful quantities, and those operators can differ fundamentally in mathematical structure. A fixed bound on density reconstruction error therefore need not translate into a fixed bound on scientific error.

This distinction is especially important for topological observables. The Bader charge of atom A is an integral over a basin Omega_A[rho] whose boundary is itself determined by the reconstructed density. A perturbation therefore affects both the integrand and the integration domain. By contrast, the total electron number is a global linear integral of rho, while the periodic electronic Hartree potential is a linear nonlocal transform obtained from Poisson's equation. These three observables provide a controlled hierarchy in which the same reconstructed density is propagated through operators of increasing structural sensitivity: global linear integration, smooth nonlocal transformation, and density-dependent topological partitioning.

We use this hierarchy to ask a narrower and more consequential question than which compressor minimizes a field norm: when does a reconstruction remain scientifically faithful for a specified downstream quantity of interest (QoI)? We benchmark three error-bounded lossy compressors, ZFP, SZ3 and SPERR, on 254 development charge-density fields spanning bulk and slab systems. For each reconstruction we distinguish requested tolerance from realized L-infinity perturbation, recompute topology-dependent Bader partitions, and compare their response with global electron-number conservation and Hartree-potential fidelity. We then introduce a stability-qualified certification protocol that excludes contracts more precise than the intrinsic numerical stability of the QoI itself and validate the resulting rate-fidelity conclusions on a frozen external cohort.

The results show that scientific fidelity is operator-dependent. Global electron-number conservation can coexist with Bader-charge failure. The Hartree-potential error follows an approximately first-order response to realized density perturbation across all three codecs, with material-level log-log R2 values near unity, whereas Bader errors are substantially less regular and can undergo orders-of-magnitude jumps on the identical reconstructions. Even at matched Hartree-potential error, Bader error frequently spans more than one decade. These findings motivate a QoI-aware view of scientific compression: reconstruction bounds control the field, while downstream certification must additionally account for the structure and intrinsic stability of the scientific operator.

## Methods — study design

### Development corpus and frozen reconstruction table

The development corpus contains 254 electronic-density fields, comprising 186 bulk systems and 68 slab systems. The frozen benchmark table contains 6,343 reconstruction rows generated with ZFP, SZ3 and SPERR over the pre-specified base and tight tolerance ladders. Each row records the requested tolerance, realized L-infinity error, compression ratio, reconstructed-density diagnostics, fixed-basin and re-solved Bader errors, voxel reassignment statistics, and Protocol A.1 stability and eligibility fields. The master table is treated as read-only throughout all downstream analyses.

### Reconstruction fidelity and reproduction gate

For extension analyses requiring regenerated density fields, the original codec wrappers used to create the frozen benchmark were reused without modification: `encode_zfp`, `encode_sz3` and `encode_sperr` from the original RhoCodec benchmark implementation. Regenerated rows were matched to frozen rows by material identifier, codec, nominal relative tolerance, nominal absolute tolerance and ladder. A row entered downstream Hartree statistics only if the regenerated realized L-infinity value reproduced the frozen value within the pre-declared gate and the frozen stream-size criterion was satisfied. ZFP and SPERR reproduced all rows; 73 SZ3 rows were excluded because compressed stream size differed across platforms despite realized L-infinity agreeing to within 2e-5 relative. These exclusions are classified as infrastructure-level reproduction mismatches rather than codec or scientific failures.

### Total electron-number control

The total electron number is treated as a global linear negative-control QoI. For each reconstruction we use the absolute deviation in the cell-integrated electron number, |Delta N|. The primary decoupling diagnostic asks whether a reconstruction can satisfy |Delta N| < 1e-4 e while simultaneously violating a local Bader fidelity criterion of 1e-3 e. This analysis is not used to claim that electron number is universally preserved by lossy compression; it tests only whether global conservation is a sufficient certificate for atom-resolved chemical fidelity.

### Hartree-potential QoI

For periodic systems, the electronic Hartree potential was evaluated from the density in reciprocal space. With the zero-frequency component fixed to zero to remove the arbitrary potential gauge,

V_H(G) = 4 pi rho(G) / |G|^2,   G != 0.

For each reconstruction, the same linear operator was applied to the density error Delta rho = rho_recon - rho_ref. The primary Hartree metric is

E_H = RMS[V_H(rho_recon) - V_H(rho_ref)] / RMS[V_H(rho_ref)].

We also record a normalized maximum potential deviation. Scaling with realized L-infinity is evaluated on log10-log10 axes using pooled and material-level linear fits. Material-level regularity is summarized by slope, R2, strict rung-to-rung monotonicity and local log-log elasticity.

### Bader QoI and topology-dependent error

Bader charges are recomputed on every reconstructed density rather than evaluated on basins inherited from the reference density. This distinction is essential because the basin Omega_A[rho] depends on the reconstructed field. The total atom-resolved charge error is therefore interpreted as containing both an integrand perturbation and a domain-migration contribution. Fixed-basin quantities are retained only as diagnostics of evaluation bias and are not used as the primary fidelity metric.

### Matched-Hartree-error analysis

To test whether smooth-field fidelity determines Bader fidelity, gate-passing rows are grouped into 0.5-decade bins of Hartree-potential error. Within each codec and system-type stratum, Bader-error dispersion is summarized by the P90/P10 ratio for bins containing at least the pre-specified minimum number of rows. A ratio of at least 10 denotes one decade of Bader dispersion at similar Hartree fidelity. This analysis is intentionally conditional on the same reconstructed densities and therefore isolates downstream operator response rather than gross differences in reconstruction quality.

### QoI stability qualification and certification

A scientific fidelity contract at threshold tau is considered evaluable only if the intrinsic Protocol A.1 stability floor of that QoI is below tau. Protocol A.1 uses five pre-registered fixed-seed uniform perturbations at the float32 L-infinity amplitude and defines the material floor as the maximum induced re-solved Bader deviation over seeds. The archived order-preserving float32 round-trip probe is retained for provenance but is not used for current eligibility because it substantially understates topology sensitivity. Certified compression is then reported only among eligible material-threshold pairs and requires the re-solved Bader error to remain below tau.

### External confirmatory validation

The primary external confirmatory cohort was frozen before final analysis. All 63 pre-frozen systems ultimately completed, with row-level Bader solver failures retained explicitly as failures rather than converted into passes. No scientific definitions, codec settings, tolerance ladders, early-stop rules or Protocol A.1 semantics were changed during completion of the final system. External validation is used to test directional rate-fidelity conclusions and the prevalence of QoI instability; development-set exploratory generalizations that failed externally are not retained as headline claims.

## Claim boundary for the manuscript

The manuscript should state that, for the tested electronic-density reconstructions, downstream error propagation depends on QoI operator structure. It should not claim a universal ordering of all possible observables, should not describe Hartree potential as intrinsically 'better' than Bader charge, and should not treat strict monotonicity on slabs as universal. The supported distinction is between a smooth approximately power-law Hartree response and a substantially more irregular topology-dependent Bader response on the same reconstructions.
