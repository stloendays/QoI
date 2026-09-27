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

QoI Stability Qualification (QSQ) uses a perturbation-based numerical identifiability test. For material $m$, let

$$
\epsilon_m = \|\text{float32}(\rho_m)-\rho_m\|_\infty.
$$

Five pre-specified uniform perturbations $U(-\epsilon_m,+\epsilon_m)$ are applied with seeds $\{20260905,1,2,3,4\}$. Bader basins are re-derived after each perturbation. The material-specific QSQ stability floor is

$$
f_m=\max_s\max_a |Q_a(\rho_m+\delta_{m,s})-Q_a(\rho_m)|.
$$

A Bader tolerance $\tau$ is eligible only when $f_m<\tau$. If $f_m\ge\tau$, the material–threshold pair is assigned `NON_EVALUABLE_BADER_UNSTABLE` and is neither a codec pass nor a codec failure.

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

The primary Figure 3 audit uses one material–codec decision per Bader threshold, giving **254 materials × 3 codecs = 762 decisions per threshold**. Versioned pooled and codec-resolved summaries support the reported counts.

At $10^{-4}\,e$, a naive binary benchmark reports 533 failures, of which **518 (97.2%)** occur on non-evaluable material–threshold pairs; only 15 remain genuine eligible failures. At $10^{-3}\,e$, **296/310 (95.5%)** naive failures are non-evaluable, leaving 14 genuine failures. At $10^{-2}\,e$, **61/108 (56.5%)** are non-evaluable, leaving 47 genuine failures.

The qualification is not a permissive rescue rule: at $10^{-4}\,e$, **106/229 (46.3%)** naive passes also occur on non-evaluable pairs. Supplementary Table S4 reports the codec-by-codec decomposition beyond the pooled Figure 3 presentation.


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

