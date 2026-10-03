# Supplementary Information

## Numerical stability qualification for downstream-fidelity benchmarks of compressed electronic densities

This Supplementary Information (SI) is organized to support the main-text benchmark-validity claim without duplicating the primary narrative. The main manuscript establishes the three-state certification logic and its headline consequence. The SI documents denominator conventions, qualification provenance, sensitivity analyses, extended operator controls, mechanistic robustness, matching diagnostics, rate–fidelity tables, external confirmation, and failure semantics.

The SI uses versioned data assets from the repository. Supplementary results are generated from machine-readable sources rather than transcribed manually.


## Supplementary Note 1 — Cohorts, denominators and data provenance

The development benchmark contains **254 electronic-density fields**, comprising **186 bulk** and **68 slab** systems. Across ZFP, SZ3 and SPERR and the fixed base/tight tolerance ladders, the development benchmark contains **6,343 retained reconstruction rows**.

The numerical-stability qualification has a broader fixed universe of **319 systems**. This total is composed of 186 development bulk systems, 68 development slabs, 37 external bulk systems and 28 external vacuum-containing 2D systems (QSQ eligibility summary; repository reader-facing provenance index). The external stability set therefore contains **65 records** and is distinct from the **63-system primary external rate–fidelity confirmatory cohort**. The latter was pre-specified separately for confirmatory scoring and contains 1,689 retained scientific rows. A 65-system external descriptive aggregate also contains 1,755 rows.

This distinction is important because different questions use different denominators:

- **254 development systems**: primary codec benchmark, binary-to-three-state reclassification, electron-count control, Hartree control, realized-distortion matching.
- **319 stability-tested systems**: QSQ stability-floor and eligibility summaries.
- **65 external descriptive systems**: descriptive external stability/robustness universe.
- **63 external confirmatory systems**: pre-specified primary external rate–fidelity confirmation.

These denominator labels are reported explicitly so that the 254-, 319-, 65- and 63-system populations remain distinguishable throughout the manuscript and SI.

Exact cohort manifests and machine-readable benchmark assets are mapped in the repository reader-facing provenance index.


## Supplementary Note 2 — QoI Stability Qualification and order-preserving control

An order-preserving round-trip control uses a deterministic float64 → float32 → float64 conversion at the same material-specific amplitude scale. This control is unusually benign for an on-grid watershed partition because it preserves much of the local value ordering.

QoI Stability Qualification (QSQ) is a perturbation-based numerical identifiability test defined on a complete measurement contract. The contract specifies the QoI, downstream numerical algorithm, scientific tolerance and the role of each input as exact or approximate. Exact inputs remain fixed; only approximate inputs are perturbed.

For the primary self-partitioned Bader contract, the density is the sole approximate input and serves both as the integrated charge field and the partition-defining field. Let

$
\epsilon_m = \|\text{float32}(\rho_m)-\rho_m\|_\infty.
$

Five pre-specified uniform perturbations $U(-\epsilon_m,+\epsilon_m)$ are applied with seeds $\{20260905,1,2,3,4\}$. Bader basins are re-derived after each perturbation. The QSQ stability floor for this contract is

$
f_m=\max_s\max_a |Q_a(\rho_m+\delta_{m,s})-Q_a(\rho_m)|.
$

A Bader tolerance $\tau$ is eligible only when $f_m<\tau$. If $f_m\ge\tau$, the material–contract pair is non-evaluable under that QSQ test and is neither a codec pass nor a codec failure. For fixed-threshold binary qualification, evaluation may stop after the first probe with response $\ge\tau$ because the full five-seed maximum must then fail the same contract; the complete panel is retained whenever the numerical value of $f_m$ is required.

The 18-material calibration panel shows why perturbation structure matters (probe calibration panel and QSQ method record; repository reader-facing provenance index):

- the order-preserving round-trip control produced a median of **82 exact neighbouring ties** and reassigned zero voxels in **9/18** calibration systems;
- the non-order-preserving QSQ perturbation probe produced no exact ties and reassigned zero voxels in only **2/18** systems;
- across five seeds, the per-material log10 floor span had a median of **0.47 decades** and reached **2.4 decades**;
- a single-seed eligibility verdict changed across seeds in 3/18 materials at $10^{-4}\,e$, 2/18 at $10^{-3}\,e$, and 1/18 at $10^{-2}\,e$;
- over a two-decade amplitude sweep (×0.1 to ×10), the floor changed by a median of **0.76 decades** (P10 0.00; P90 2.02), demonstrating that the reported floor is qualification-defined rather than an amplitude-free material constant.

Across the complete 319-system stability corpus, the QSQ non-evaluable fractions are **79.9%** at $10^{-4}\,e$, **41.4%** at $10^{-3}\,e$, and **9.7%** at $10^{-2}\,e$ (QSQ eligibility summary; repository reader-facing provenance index).

One extreme QSQ response, `aflow-Al8Cu4U1_ICSD_601801`, corresponds to a permutation of symmetry-equivalent Al basins rather than a literal multi-electron chemical transfer. It is recorded as a symmetry-equivalent basin relabelling case and remains non-evaluable for a position-indexed atomic-charge QoI.

Exact implementation filenames and method-control records are mapped in the repository reader-facing provenance index and are not used as scientific method names here.


## Supplementary Note 3 — Sensitivity analyses for eligibility and certification

The principal benchmark uses the pre-specified QSQ eligibility rule. Four sensitivity analyses test how the reported conclusions depend on alternative reporting choices.

### S1 — No-exclusion diagnostic

The no-exclusion diagnostic applies the Bader threshold directly without stability qualification. It quantifies how conventional binary reporting changes when non-evaluable material–threshold pairs are allowed to masquerade as pass/fail outcomes.

### S2 — Error relative to the independent stability floor

For certified reconstructions, the floor-relative analysis reports $\Delta Q_\text{Bader}/f_m$. At $10^{-4}\,e$, median ratios are **1.23** for SPERR, **1.33** for SZ3 and **1.09** for ZFP, with P90 values **3.20**, **2.86** and **3.25**, respectively. The strictest certified regime is therefore floor-scale. At $10^{-3}\,e$, median ratios broaden to 2.78–3.55, and at $10^{-2}\,e$ to 10.7–14.6. These data support an emerging analysis-limited regime at the strictest contract but do **not** establish a universal material-level identity between a tight-ladder plateau and the QSQ floor.

### S3 — Inflated-threshold stress test

The inflated-threshold stress test evaluates alternative thresholds multiplied by $k=2,5,10$. This analysis tests whether qualitative codec conclusions arise only from a particular hard cutoff. It is a robustness analysis and does not replace the pre-specified chemical contracts.

### S4 — Probe-amplitude sensitivity

The 18-material amplitude sweep reports floors at ×0.1, ×1 and ×10 of the QSQ perturbation amplitude. The heterogeneity across materials is part of the result: some systems are plateau-like while others scale substantially. The purpose is to demonstrate qualification-procedure dependence transparently, not to tune the amplitude post hoc.


## Supplementary Note 4 — Extended operator controls

### Electron-count negative control

All **6,343** development reconstruction rows were examined for total-electron-count fidelity. Among **3,205** rows with $|\Delta N_e|<10^{-4}\,e$ and a finite re-derived Bader result, **1,383 (43.15%)** still have Bader error $\ge10^{-3}\,e$. Global electron-number conservation is therefore not a sufficient certificate of atom-resolved chemical fidelity.

### Hartree-potential control

The full Hartree expansion targets the same 6,343 reconstruction rows. A pre-specified reproduction gate retains **6,270** rows for formal statistics. The pooled relation between Hartree error and realized $L_\infty$ has a log–log slope of **1.02**. Across 678 material–codec pairs with at least five gate-passing points, median material-level Hartree $R^2$ is approximately **0.994–0.997** by codec, whereas Bader response is much less regular. Hartree is strictly monotone in 88.6% of such pairs versus 32.4% for Bader.

The 73 Hartree reproduction-gate failures are all SZ3 rows with reconstruction distortion reproduced to within approximately $2\times10^{-5}$ relative, but compressed byte counts differing across platforms. They are classified as infrastructure reproduction mismatches and excluded from formal Hartree statistics; they are not codec or numerical failures.

At matched Hartree error, Bader response remains dispersed: **55.4%** of gate-passing rows lie in 0.5-decade Hartree-error bins where the Bader P90/P10 ratio is at least 10. This supports the use of structurally distinct downstream operators in the main manuscript without claiming that Hartree is universally “better” than Bader.

### Fourier-spectrum mechanism audit

The full-population mechanism audit uses the **exact 457 ZFP/SZ3 within-material realized-$L_\infty$ matched pairs across 214 materials** from the Hartree analysis. The corresponding **914 reconstructions** were regenerated from the versioned codec rows. A reconstruction entered the spectral audit only after both its realized $L_\infty$ and its reference-implementation Hartree relative RMSE reproduced the stored matched-pair target.

The reference-implementation matched-pair Hartree center is **0.0776220566**, and the regenerated calculation reproduces it at **0.0776220566**. To test whether this large codec effect could arise from a discrete-FFT implementation artifact, the audit also defines a Nyquist-safe Hermitian Poisson operator. For even grids in non-orthogonal cells, Nyquist-plane modes are alias-equivalent under sign reversal while the continuum $|G|^2$ expression contains cross terms. The mechanism operator therefore sets $G=0$ and all even-grid Nyquist-plane modes to zero and applies $4\pi/|G|^2$ to all remaining modes. This gives a Hartree ratio of **0.0776219202**, essentially unchanged from the reference-implementation result.

Let $\mathcal{G}_s$ denote the non-zero reciprocal-space modes that do not lie on an excluded even-grid Nyquist plane. For the Nyquist-safe operator,

$$
\text{RMS}(\Delta V_H)^2=
\frac{(4\pi)^2}{N^2}
\sum_{G\in\mathcal{G}_s}\frac{|\Delta\rho(G)|^2}{|G|^4},
$$

and the maximum relative discrepancy between the direct real-space Hartree RMS and the Fourier-space expression is **$1.30\times10^{-15}$** across all selected reconstructions. The corresponding direct Hartree ratio and square root of the Hartree-weighted spectral ratio agree to numerical precision.

Define

$$
E=\sum_{G\in\mathcal{G}_s}|\Delta\rho(G)|^2,
\qquad
W_H=\sum_{G\in\mathcal{G}_s}\frac{|\Delta\rho(G)|^2}{|G|^4},
\qquad
S_H=\frac{W_H}{E}.
$$

For every matched pair,

$$
R_H=
\sqrt{\frac{E_{\text{ZFP}}}{E_{\text{SZ3}}}}
\sqrt{\frac{S_{H,\text{ZFP}}}{S_{H,\text{SZ3}}}}.
$$

The separately aggregated material-level centers are **0.376** for the total spectral-energy factor and **0.203** for the spectral Hartree-susceptibility factor. These separately aggregated centers are descriptive and are not expected to multiply exactly; the multiplicative identity is checked and satisfied pairwise. The material-median absolute-log contribution from spectral susceptibility is **62.0%**, showing that frequency allocation is the dominant component of the matched-distortion Hartree codec effect.

The directional diagnostics are highly consistent across materials: **99.5%** have lower ZFP spectral Hartree susceptibility, **98.1%** have a higher ZFP spectral centroid, and **99.1%** have a lower ZFP low-$G$ error-energy fraction. The material-level center of the ZFP/SZ3 low-$G$ fraction ratio is **0.416**. Here $q=|G|/G_{\max}$ over non-zero Nyquist-safe modes, with low $G$ defined as $q\le0.25$ and high $G$ as $q\ge0.75$.

The mechanism conclusion is intentionally operator specific. The Hartree result demonstrates that matched pointwise distortion does not imply matched downstream error when codecs distribute reconstruction error differently over frequencies that the downstream operator weights unequally. It does **not** establish that the nonlinear, topology-sensitive Bader residual is controlled by the same single Fourier descriptor.

The matched-pair mechanism table, reconstruction-level spectral metrics, radial spectra and mechanism summaries are mapped in the repository reader-facing provenance index.


## Supplementary Note 5 — Binary-to-three-state reclassification

The binary-to-three-state audit uses one material–codec decision per Bader threshold on the full benchmark record, giving **254 materials × 3 codecs = 762 decisions per threshold** (Supplementary Fig. S7 and Supplementary Table S4). Versioned pooled and codec-resolved summaries support the reported counts.

At $10^{-4}\,e$, a naive binary benchmark reports 533 failures, of which **518 (97.2%)** occur on non-evaluable material–threshold pairs; only 15 remain genuine eligible failures. At $10^{-3}\,e$, **296/310 (95.5%)** naive failures are non-evaluable, leaving 14 genuine failures. At $10^{-2}\,e$, **61/108 (56.5%)** are non-evaluable, leaving 47 genuine failures. These fractions describe the full record as it was built, in which the extra tight ladder was run only for the materials eligible at $10^{-3}\,e$, so screen-rejected materials had fewer settings at which to pass. With the same tight settings completed for every material, the no-pass risk at $10^{-3}\,e$ is 3.3% for eligible versus 66.4% for screen-rejected material–codec pairs, a 20.34-fold ratio (main-text Fig. 3c); this equal-search ratio is the measure reported in the main text.

The qualification is not a permissive rescue rule: at $10^{-4}\,e$, **106/229 (46.3%)** naive passes also occur on non-evaluable pairs. Supplementary Table S4 reports the codec-by-codec decomposition.


## Supplementary Note 6 — Extended Bader mechanism and cross-implementation robustness

The scientific Bader metric re-derives atom-centred basins after every reconstruction. Fixed-basin scoring is retained only as a diagnostic because it suppresses the domain-migration component.

The mechanism tables evaluate representative systems across three codecs and three chemical tolerances, separating the charge change into an integrand contribution on the reference domain and a residual domain-migration contribution. Supplementary Table S10 and Supplementary Fig. S5 report the full representative-case matrix beyond the selected main-text examples.

A separate independent-Bader study provides an implementation-robustness check. It contains **1,560/1,560 expected outcome rows** across a stratified panel and three solver modes. Henkelman on-grid reproduces BaderKit on-grid codec response with a median ratio of **1.00** (IQR approximately 0.92–1.005), aside from systems whose unperturbed basin sets differ. Codec ordering at relative tolerance $10^{-4}$ is preserved across BaderKit on-grid, Henkelman on-grid and Henkelman near-grid. These results remain supplementary because they validate robustness rather than define the central benchmark claim.


## Supplementary Note 7 — Realized-distortion matching diagnostics

Equal nominal codec tolerance is not a common realized-distortion scale. At equal nominal settings, median realized-$L_\infty$ ratios are approximately **0.170** for ZFP/SZ3, **0.170** for ZFP/SPERR and **1.00** for SZ3/SPERR.

The primary within-material match uses a **0.10-dex** caliper in $\log_{10}(L_\infty)$, without replacement, and bootstraps materials rather than rows. At this caliper, the matched datasets contain 457 ZFP–SZ3 pairs from 214 materials, 465 ZFP–SPERR pairs from 206 materials, and 1,848 SZ3–SPERR pairs from 254 materials. Median larger/smaller realized-$L_\infty$ is approximately 1.14 for the ZFP comparisons and 1.00 for SZ3/SPERR.

After matching, re-derived Bader-error ratios are **0.557** for ZFP/SZ3 (95% material-bootstrap CI 0.525–0.598), **0.601** for ZFP/SPERR (0.534–0.662), and **1.033** for SZ3/SPERR (0.976–1.072). Supplementary Figure S6 shows sensitivity across 0.05, 0.10, 0.20 and 0.30 dex together with common-support counts; the main text reports the primary 0.10-dex result and notes that the direction is robust across the pre-specified calipers.


## Supplementary Note 8 — Stability-qualified rate–fidelity tables

For each eligible material–threshold pair, the benchmark selects the highest compression ratio on the fixed codec ladder that satisfies the re-derived Bader contract. The QSQ-certified benchmark summary, pairwise codec summary and best certified operating-point table are mapped through the repository reader-facing provenance index.

Supplementary Table S13 reports, for each $\tau$, stratum and codec, the admitted denominator, non-evaluable denominator, certified count/fraction, median best-certified compression ratio, bootstrap confidence interval and distributional quantiles. Pairwise win fractions are reported separately rather than folded into a single ranking label.

Supplementary Table S13 is generated directly from the current machine-readable development and external rate–fidelity summaries.


## Supplementary Note 9 — External confirmation

The primary external confirmatory cohort contains **63/63 completed systems**, **1,689 retained scientific rows**, **0 material-level pipeline failures**, **0 codec-bound violations** and **3 preserved row-level Bader solver failures** affecting two materials. The 65-system descriptive aggregate contains **65/65 systems** and **1,755 rows**, also with zero material-level failures and zero bound violations.

For the primary 63-system confirmatory cohort, QSQ eligibility counts are **16**, **42** and **57** systems at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$, respectively. The three pre-specified rate–fidelity directions reproduce: ZFP > SZ3 > SPERR at $10^{-4}\,e$, ZFP ≈ SZ3 > SPERR at $10^{-3}\,e$, and SZ3 > ZFP > SPERR at $10^{-2}\,e$. The ZFP–SZ3 separation at the strictest threshold is narrower than in development and is treated as a modest external difference.

Row-level solver failures and recovery provenance are retained in the repository audit. The SI separately reports the 65-system descriptive aggregate and distinguishes vacuum-containing 2D systems from development adsorbate slabs.


## Supplementary Note 10 — Failure taxonomy and negative results

The failure registry records explicit row-level analysis failures and exclusions. Scientific non-evaluability, Bader-solver failure, reproduction mismatch and symmetry-equivalent basin relabelling are treated as distinct categories. These categories are not converted into missing data or codec failure.

Negative algorithmic results are valuable supplementary evidence because they delimit the paper's contribution. The claim–evidence matrix records that boundary-aware allocation did not improve compression, the promolecule prior was detrimental, and symmetry folding did not yield a robust advantage. These results are summarized compactly in Supplementary Table S14 rather than developed into a competing algorithm narrative. The paper's contribution is the measurement/certification framework, not a new codec.



## Supplementary Note 11 — Outcome-blind chemical-decision boundary case study

An outcome-blind chemistry and geometry audit of the 68 NOMAD development slabs selected five paired states before QSQ, codec or Bader outcomes were inspected for inclusion. All five passed the pre-specified two-implementation source-reference rule. Across ZFP, SZ3 and SPERR on the four common tight settings, all 60 direct qualitative target-atom charge-transfer directions were preserved after compression. QSQ at $10^{-3}\,e$ retained 36/60 trials from three pairs, while the unqualified baseline retained all 60; both had zero observed sign errors. This deliberately negative result shows that the strict numerical Bader contract and a coarse sign-level chemical interpretation are different fidelity targets. Full pair-level reference values and policy accounting are provided in Supplementary Tables S15-S16.

The resolved compressed analysis contains 216/216 successful solver cells. No new electronic-structure calculation was used; the source reference is a BaderKit/Henkelman on-grid consensus under the declared density representation.




## Supplementary Note 12 — Continuous QSQ risk calibration

The measured stability floor contains graded risk information beyond the binary eligibility flag. Models based on $x_m(\tau)=\log_{10}(f_m/\tau)$ were evaluated by 10-fold cross-validation over materials against the frozen 59-trial prospective outcomes.

Across 44,958 trial-threshold outcomes, all calibrated models reduced held-out Brier score relative to the binary gate. The best logistic model reached 0.0412 versus 0.0651 for the gate, while isotonic regression reached 0.0464. The pre-declared replacement criterion also required greater coverage under a 2% risk contract at $10^{-3}\,e$. This was not met: cross-validated isotonic admission was 115/254 materials (45.3%) versus 143/254 (56.3%) for the binary gate. The admitted isotonic subset showed 16/6,785 fresh exceedances (0.236%).

The continuous statistic is therefore a sharper prospective risk predictor, but these data do not justify replacing the simpler binary QSQ eligibility contract. The reason is structural rather than paradoxical: prospective risk increases steeply as the measured floor approaches the requested tolerance, so imposing a stringent probability threshold shifts the operational cutoff inside the simple condition $f_m<\tau$ and sacrifices coverage. The analysis therefore explains why a transparent binary qualification boundary remains preferable for the primary benchmark even though the underlying floor carries graded information.

## Supplementary Note 13 — Qualification of grid-local density extrema

A second topology-sensitive QoI was defined directly on the sampled density grid. A voxel is a strict local maximum when its value exceeds all 26 neighbours and a strict local minimum when it is smaller than all 26 neighbours under periodic indexing. No smoothing, interpolation, or continuous critical-point search is applied; the reader-facing term is therefore **grid-local density extrema**.

All 254 development materials were evaluated. The full reconstruction analysis regenerated 6,343 benchmark rows; 6,293 were scored and 50 had recorded non-gate reconstruction failures. All 16,256 perturbation evaluations completed: five qualification perturbations and 59 fresh perturbations per material.

At the strict endpoint, qualification requires the maximum-voxel set to remain identical under all five QSQ perturbations. This admits 118/254 materials. The count-only five-seed criterion admits 141/254 and is retained as a secondary diagnostic.

Prospectively, 0/6,962 fresh trials on qualified materials change the number of maxima, compared with 6,444/8,024 (80.31%) on screen-rejected materials. For maximum-set identity, the corresponding rates are 3/6,962 (0.04%) and 7,509/8,024 (93.58%).

Cross-QoI transfer is weak. Comparing strict extrema eligibility with Bader eligibility at $10^{-3}\,e$ gives 75 both eligible, 68 Bader-only, 43 extrema-only, and 68 neither; raw agreement is 56.3% and Cohen's $\kappa$ is 0.1337 (95% bootstrap interval 0.0164–0.2542). Spearman correlation between the Bader and extrema stability floors is 0.1389 (0.0280–0.2554).

The observables are also non-redundant on reconstructed fields. Among 6,293 scored reconstructions, 908 (14.43%) preserve the maximum count while having Bader error at least $10^{-3}\,e$, whereas 655 (10.41%) change the maximum count while keeping Bader error below $10^{-3}\,e$.

These results support a general qualification principle while showing that the evaluability boundary depends on the downstream QoI.

## Supplementary Note 14 — Codec-shaped perturbation robustness

Codec-shaped probes were constructed from residual fields at the common base relative tolerance of $10^{-5}$, periodically shifted to remove original alignment, and rescaled to the same material-specific QSQ amplitude. All 4,572 planned Bader re-solves completed.

The material-median $\log_{10}(f_m^{c}/f_m)$ is −0.196 for ZFP (95% CI −0.255 to −0.134), −0.000 for SZ3 (−0.010 to +0.008), and −0.027 for SPERR (−0.042 to −0.010). Under the pre-declared rule, the iid family is conservative on aggregate for ZFP and SPERR and statistically indistinguishable from the codec-shaped family for SZ3.

At $10^{-3}\,e$, iid-versus-codec-shaped eligibility agreement is 0.902 for ZFP and 0.937 for SZ3 and SPERR. Among the 143 iid-qualified materials, codec-shaped floors do not improve prediction of the frozen 59-trial prospective risk. For ZFP, the Spearman correlation falls from 0.549 for the iid floor to 0.420 for the codec-shaped floor, a difference of −0.128 (95% CI −0.218 to −0.050); differences for SZ3 and SPERR are unresolved.

Correlation between low-$G$ residual-energy fraction and the codec-shaped/iid floor ratio is near zero for ZFP, weakly negative for SZ3, and unresolved for SPERR. The Fourier mechanism that explains Hartree error therefore does not provide a common scalar explanation for Bader stability.

## Supplementary Note 15 — Reference-density predictors do not replace direct QSQ measurement

Complete reference-density descriptors were obtained for 318/319 systems; one external AFLOW density remained unavailable and is preserved as a recorded failure.

The strongest univariate association with $\log_{10} f_m$ is the fraction of basin-boundary neighbour gaps below the QSQ perturbation scale, with Spearman $\rho=0.554$ (95% CI 0.463–0.639). Other boundary-gap and near-tie descriptors also correlate with the floor, supporting a link between numerical fragility and local ordering margins near basin boundaries.

Nested 10-fold cross-validation of the pre-declared ridge model gives $R^2=0.238$ and RMSE 0.932 decades over the 318 descriptor-complete systems. Fitting on the 254 development systems and evaluating on the 64 descriptor-complete external systems gives held-out $R^2=0.134$ (95% CI −0.410 to 0.385) and RMSE 1.208 decades. The pre-declared external $R^2\ge 0.5$ replacement criterion is not met.

These descriptors are scientifically informative but are not sufficient to replace direct QSQ measurement. Their partial success is mechanistically plausible because small ordering gaps near basin boundaries identify locally fragile regions. Their limited external transfer is also plausible because the final Bader response is a collective, nonlinear consequence of ascent-path changes, basin topology, grid semantics, chemistry and system class rather than a single local descriptor. In the present benchmark, stability therefore remains an empirically measured property of a specified density, QoI and downstream algorithm.

## Supplementary Note 16 — All-electron-reference Bader measurement contracts

Bader analysis can use separate fields for the quantity being integrated and for the topology that defines the atomic basins. To quantify the effect of these input roles, 53 development materials with published CHGCAR, AECCAR0 and AECCAR2 data were evaluated using Henkelman Bader 1.05 in on-grid mode with vacuum threshold 0.001. Three materials had entirely non-finite published AECCAR0 inputs and were retained as input failures, leaving 50 analyzable materials.

The exact baseline integrates CHGCAR over basins defined by the exact all-electron reference $\rho_{\mathrm{AE}}=\mathrm{AECCAR0}+\mathrm{AECCAR2}$. Three QSQ contracts were evaluated with the same five seed labels and material-specific float32 $L_\infty$ amplitudes:

1. **Charge-field perturbation:** CHGCAR approximate; all-electron reference exact.
2. **Joint perturbation:** CHGCAR approximate; all-electron reference approximate.
3. **Partition-field perturbation:** CHGCAR exact; all-electron reference approximate.

At $10^{-3}\,e$, the charge-field contract is eligible for **50/50** analyzable materials, whereas the joint and partition-field contracts are each eligible for only **3/50**. At $10^{-4}\,e$, the corresponding counts are 50/50, 0/50 and 0/50; at $10^{-2}\,e$, they are 50/50, 17/50 and 17/50 (main-text Fig. 5f).

The partition-field perturbation reproduces the joint-perturbation response essentially exactly at the population level. The material-median ratio of the partition-field stability floor to the joint floor is **1.000** (bootstrap 95% interval numerically indistinguishable from 1.000 at the reported precision). The fraction of analyzable materials satisfying $f_{\mathrm{partition}}\ge0.5f_{\mathrm{joint}}$ is 1.000, and the fraction satisfying $f_{\mathrm{partition}}\ge0.9f_{\mathrm{joint}}$ is also 1.000. Median basin-reassignment fractions are **0.0196262** for both the joint and partition-field contracts, giving a median reassignment ratio of **1.000**.

These results show that, under the tested all-electron-reference Bader contract and perturbation scales, numerical instability is dominated by the field that defines the partition topology. They do not imply that CHGCAR error is universally irrelevant to Bader charge; rather, they show that the exact-versus-approximate role of each input is part of the scientific measurement contract that QSQ must qualify.

## Supplementary Note 17 — Certifying writer

The certifying writer turns qualification and certification into one per-field procedure: run QSQ, leave a non-evaluable field uncompressed, search the codec ladders of an eligible field, and return the selected reconstruction with its certificate. It was evaluated on the 6,343 frozen development rows of 254 materials without new computation (Supplementary Fig. S10). QSQ costs one reference and five probe Bader solves; each queried rung costs one solve.

**Policies.** EXHAUSTIVE evaluates every rung of every codec (the oracle). SCAN evaluates each codec from its loosest rung downwards and stops at the first certified rung. BISECT bisects each codec's ladder over rung index, moving looser after a certified rung and tighter otherwise. Each multi-codec policy returns the certified row with the largest compression ratio among the rows it evaluated across ZFP, SZ3 and SPERR; single-codec SCAN and BISECT variants were evaluated for comparison. The adoption rule was fixed before any policy outcome was computed: the fewest mean solves among multi-codec policies whose archive compression at $10^{-3}\,e$ is at least 0.98 times the oracle and whose miss rate is at most 2%. BISECT met the rule.

**Metrics.** Archive compression at $\tau$ is $\sum$ raw bytes $/\sum$ stored bytes over eligible materials, where a material for which the policy returns nothing is stored at raw size. A miss is an eligible material with at least one certifiable row for which the policy returns none.

| $\tau$ ($e$) | Eligible | Policy | Archive CR | Oracle CR | Fraction of oracle [95% CI] | Misses | Solves per eligible material |
|---:|---:|---|---:|---:|---|---:|---:|
| $10^{-4}$ | 46 | EXHAUSTIVE | 8.47 | 8.47 | 1.0000 | 0/46 | 38.5 |
| $10^{-4}$ | 46 | SCAN | 8.47 | 8.47 | 1.0000 | 0/46 | 34.3 |
| $10^{-4}$ | 46 | BISECT | 8.45 | 8.47 | 0.9976 [0.9918, 1.0000] | 0/46 | 16.7 |
| $10^{-3}$ | 143 | EXHAUSTIVE | 15.13 | 15.13 | 1.0000 | 0/143 | 37.0 |
| $10^{-3}$ | 143 | SCAN | 15.13 | 15.13 | 1.0000 | 0/143 | 26.8 |
| $10^{-3}$ | 143 | BISECT | 14.90 | 15.13 | 0.9848 [0.9695, 0.9959] | 0/143 | 16.7 |
| $10^{-2}$ | 229 | EXHAUSTIVE | 24.79 | 24.79 | 1.0000 | 0/227 | 32.2 |
| $10^{-2}$ | 229 | SCAN | 24.79 | 24.79 | 1.0000 | 0/227 | 17.3 |
| $10^{-2}$ | 229 | BISECT | 24.55 | 24.79 | 0.9901 [0.9698, 0.9982] | 0/227 | 15.9 |

At $10^{-2}\,e$, two of the 229 eligible materials have no certifiable row on the frozen ladder, so the miss denominator is 227.

**Codec search versus ladder search.** Single-codec writers retain much less of the oracle archive compression. At $10^{-3}\,e$, BISECT restricted to ZFP, SZ3 or SPERR retains 0.836, 0.351 and 0.271 of the oracle, with 1, 7 and 6 misses respectively; the best single-codec variant (SCAN-ZFP) retains 0.840. Searching across codecs therefore contributes more than exhaustive search along any single ladder.

**Non-monotone ladders.** BISECT assumes that certification is monotone along a ladder. Re-derived Bader error is not monotone in tolerance (main text), so bisection can stop at a tighter certified rung than the oracle; this is the source of the 1.5% shortfall at $10^{-3}\,e$. Every returned row was evaluated by the policy, and certificate validity was re-checked mechanically.

**Sequential qualification.** Replacing the fixed six-solve QSQ cost by exact sequential early rejection changes no returned row, stored size, certificate or miss. Mean end-to-end cost over all 254 materials falls from 7.93 to 4.84 solves at $10^{-4}\,e$ (−39.0%), from 12.00 to 10.34 at $10^{-3}\,e$ (−13.9%) and from 14.91 to 14.54 at $10^{-2}\,e$ (−2.5%).

**Certificate.** For every material and $\tau$ the writer records the outcome, the returned codec and setting, the compression ratio and the number of Bader solves; the certified Bader error and the QSQ floor are those of the evaluated frozen row. A deployed certificate carries the contract (QoI, algorithm, tolerance, roles and hashes of the inputs), the perturbation scale and seed panel, the number of probes evaluated, the outcome code (`QOI_CERTIFIED`, `QOI_NOT_CERTIFIED` or `REFERENCE_NOT_RESOLVED`), the selected codec and operating point, the verified downstream error, the compressed size and the provenance commit, so that what was qualified can be reconstructed and not only which codec was used.

## Supplementary Note 18 — Finite-panel admission bound and probe exchangeability

**Bound.** QSQ admits a contract when the maximum of $n$ qualification responses is below $\tau$. Let $p$ be the probability that one probe from the declared perturbation family gives a response of at least $\tau$. If the $n$ qualification probes and a later probe are exchangeable, the probability that the contract is admitted and the later probe still exceeds $\tau$ is $\mathbb{E}[p(1-p)^{n}]$, whatever the response distribution. Since $p(1-p)^{n}$ is maximized at $p=1/(n+1)$, this joint probability is at most $n^{n}/(n+1)^{n+1}$:

| Panel size $n$ | 5 | 10 | 19 | 37 |
|---:|---:|---:|---:|---:|
| Bound on joint admission and exceedance | 6.70% | 3.50% | 1.89% | 0.98% |

Exchangeability also implies that a later response exceeds the maximum of the panel with probability $1/(n+1)$ for continuous responses (one-sided tolerance limits; Wilks, main-text ref. 23). The bound is a property of the finite-panel rule over the draw of the probes; it is not a conditional risk among admitted contracts and not a worst-case statement.

**Shared seeds in the frozen design.** The five frozen QSQ seeds are used directly as PCG64 seeds, so every material receives the same five random streams, whereas the 59 prospective streams are material-specific. The pooled fraction of fresh responses above the frozen five-probe floor is 19.08% (2,859/14,986; material-cluster 95% CI 17.16–21.01%) against the exchangeable value 1/6. With shared streams the 254 materials do not average over independent panels, so the pooled fraction is one realization rather than an estimate of 1/6.

**Local recomputation.** A package declared before any probe was evaluated (repository `analysis/extensions_20261003/QSQ-exchangeability/`) re-solved, for all 254 development materials, the reference and the five frozen probes in the frozen pipeline, and added a second five-probe panel whose streams are drawn independently for each material (SHA-256 of material identity and label). All 2,794 Bader solves succeeded.

- The recomputed frozen floor matches the published floor exactly ($|\Delta|\le10^{-9}\,e$) in 252/254 materials; the two exceptions (`mp-1296`, 0.181 versus 2.632 $e$; `nomad-3ermMygSkKxT`, 2.058 versus 2.028 $\times10^{-4}\,e$) do not change eligibility. Eligibility agrees in 254/254 materials at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$.
- With material-independent streams, 16.52% of fresh responses exceed the five-probe maximum (2,475/14,986; 95% CI 14.74–18.39%). The interval contains 1/6, meeting the pre-declared exchangeability criterion.
- Eligibility under the independent panel agrees with the frozen panel in 237/254, 242/254 and 253/254 materials ($\kappa$ = 0.776, 0.904 and 0.977 at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$).

**Observed joint admission and exceedance** (all 14,986 fresh trials; bound 6.70% for $n=5$):

| $\tau$ ($e$) | Frozen panel: joint rate | Conditional risk among admitted | Coverage | Independent panel: joint rate | Conditional risk among admitted | Coverage |
|---:|---:|---:|---:|---:|---:|---:|
| $10^{-4}$ | 0.727% (109) | 4.016% | 46/254 | 0.928% (139) | 5.013% | 47/254 |
| $10^{-3}$ | 0.901% (135) | 1.600% | 143/254 | 0.721% (108) | 1.317% | 139/254 |
| $10^{-2}$ | 0.133% (20) | 0.148% | 229/254 | 0.207% (31) | 0.228% | 230/254 |

The Bader contract operates far below the ceiling because its responses are well separated across materials: most materials respond either far below or far above $\tau$. The ceiling is approached only when many contracts have an exceedance probability near $1/(n+1)$, which is the regime in which a larger panel is needed; the table above gives the panel size for a target joint rate.
