# The downstream operator qualifies, predicts and shapes the certified compression of electronic densities

## Abstract

Compressed scientific fields are judged by quantities computed from the reconstruction, yet the reference analysis may not resolve the requested tolerance. QoI Stability Qualification (QSQ) qualifies the measurement contract before any codec is scored: across 254 electronic densities, a five-probe screen separated fresh Bader threshold-exceedance risks of 1.600% (135/8,437 trials) in qualified and 81.325% (5,326/6,549) in rejected materials. For linear operators, the operator symbol fixes where compression error belongs and what that gains. In pre-registered tests on 60 unused bulk crystals and 32 unused surface slabs, gains predicted before compression for five operators matched measurement (Spearman 0.978 and 0.979). For the Hartree potential, the closed-form law certified 10.2-fold (60/60) and 18.5-fold (32/32) more compression than equal-search pointwise codecs; for bulk crystals it lies within 10.5% of the operational optimum. On 48 further unused crystals, one stream certified Hartree potential and Bader charges together (48/48) at median byte overhead 1.000.

## Introduction

Electronic-structure databases store electron densities on dense real-space grids, and error-bounded lossy compressors such as ZFP, SZ3 and SPERR are the standard means of reducing such floating-point fields.<sup>1–4</sup> Lossy compression is used across scientific workflows<sup>5</sup> and in quantum chemistry, for two-electron integrals and atomic-orbital bases.<sup>6,7</sup> A stored density is rarely the scientific result. The result is a quantity computed from it: a potential, a field, an atomic charge.

Downstream fidelity is therefore an accepted requirement of scientific compression. Multilevel methods control user-prescribed derived quantities through operator norms;<sup>8</sup> error-control theory maps quantity-of-interest (QoI) tolerances to data-level bounds;<sup>9</sup> QPET tunes pointwise bounds for differentiable QoIs;<sup>10</sup> application pipelines preserve several QoIs at once, including by constraint satisfaction after decompression;<sup>11–13</sup> TOPIQ predicts QoI bias and uncertainty from compressed data;<sup>14</sup> Compression Safeguards and FFCz correct decoded data until declared pointwise, QoI or spectral bounds hold;<sup>15,16</sup> progressive retrieval guarantees errors on derivable QoIs;<sup>17</sup> and topology-aware compressors preserve discrete structure that pointwise bounds miss.<sup>18,19</sup> These methods bound, predict or enforce the error of a declared QoI.

Task-based quantization established that a quantizer should be designed for the task it serves rather than for the signal itself.<sup>20</sup> Coefficient-dependent step sizes under a weighted squared error are classical high-rate allocation,<sup>21,22</sup> and step-size maps tuned to a downstream error model have long been used in image coding.<sup>23</sup> Here we apply that principle to stored physical fields. The task is a physical operator with an exact reciprocal-space symbol, and every decoded field is recertified under that operator.

Measurement science adds a step that compression benchmarks omit. Analytical chemistry does not report a concentration below a method's limit of quantification,<sup>24</sup> and measurement-system analysis compares gauge variation with the tolerance before the gauge accepts or rejects parts.<sup>25</sup> In a compression benchmark the reference analysis plays the gauge, and its capability under the declared contract decides whether a tolerance can be scored at all.

Here we show that the downstream operator governs certified compression at three points (Fig. 1a). It qualifies: QSQ decides whether the complete measurement contract resolves the requested tolerance, and its verdict predicts fresh risk. It shapes: for linear operators, the operator symbol yields a closed-form allocation law, which we test prospectively on unused bulk crystals and surface slabs from two databases. It predicts: the gain of operator-aware over operator-blind allocation, computed from the operator symbol and the reference spectrum and committed before compression, matches the measured gain for five operators. Finally, one stream is certified for the Hartree potential and for Bader charges together. Every confirmatory result follows a protocol committed before its outcomes (Methods, Table 1).

## Results

### A tolerance is scored only after the measurement contract resolves it

A measurement contract declares the QoI, the downstream numerical algorithm, the scientific tolerance $\tau$ and the role of every input as exact or approximate. QSQ perturbs the approximate inputs five times at their own float32 precision scale, takes the maximum downstream response as the stability floor $f_C$, and admits the contract when $f_C<\tau$ (Methods). Each material–contract–tolerance decision then ends in one of three outcomes: certified, not certified, or non-evaluable (Fig. 1a). For Bader charge, atomic basins follow the topology of a partition-defining density,<sup>26</sup> and grid algorithms re-derive them for every input.<sup>27–29</sup>

We froze the five-probe screen and challenged it with 59 fresh perturbations for each of 254 development densities (186 Materials Project bulk crystals, 68 NOMAD slabs). All 14,986 trials produced valid Bader outcomes. At $10^{-3}\,e$, QSQ admitted 143/254 materials. Qualified materials exceeded the threshold in 135/8,437 fresh trials (1.600%; material-cluster 95% CI 0.782–2.596%), rejected materials in 5,326/6,549 (81.325%; 75.981–86.257%), and 20/143 versus 110/111 materials showed any exceedance (Fig. 1b). The separation held at $10^{-4}\,e$ (46/254 admitted; 4.016% versus 86.938%) and at $10^{-2}\,e$ (229/254; 0.148% versus 79.593%). Fresh risk rose steeply as a material's floor approached the tolerance (Fig. 1c).

Qualification also governs codec comparisons. When the same tight settings were completed for every material (1,332/1,332 added reconstructions), the fraction of material–codec pairs with no passing reconstruction at $10^{-3}\,e$ was 3.3% for qualified and 66.4% for rejected pairs, a 20.34-fold ratio (Fig. 1d). A finite panel carries a distribution-free guarantee: for exchangeable probes, the joint probability of admission and a later exceedance is at most $n^n/(n+1)^{n+1}$, 6.70% for $n=5$; the observed joint rate was 0.901%.

Evaluability belongs to the contract, not to the material. With Henkelman Bader 1.05 and an all-electron partition reference (AECCAR0 + AECCAR2), perturbing only the integrated charge field left 50/50 analyzable materials eligible at $10^{-3}\,e$, whereas perturbing the partition reference left 3/50. Holding the partition reference exact is therefore a contract choice that makes Bader charges scorable; it defines the Bader contract used for joint certification below. Implementation transfer, a second topology-sensitive QoI and an external cohort are reported in Supplementary Note 1.

### The operator symbol explains the codec effect and fixes a closed-form allocation law

At matched realized $L_\infty$ distortion, codecs still differ in Hartree-potential error. For 457 ZFP/SZ3 pairs matched within material (214 materials), the material-level Hartree-error ratio was 0.0776221, and 0.0776219 under a Nyquist-safe Poisson operator; the real-space error agreed with its Fourier expression to a relative discrepancy of $1.296\times10^{-15}$. Writing $E$ for the error energy over non-zero, Nyquist-safe modes and $S_H=W_H/E$ for the Hartree susceptibility, with $W_H=\sum_G|\Delta\rho(G)|^2/|G|^4$, each pair's ratio factors exactly as

$$
R_H=\sqrt{\frac{E_{\text{ZFP}}}{E_{\text{SZ3}}}}\,\sqrt{\frac{S_{H,\text{ZFP}}}{S_{H,\text{SZ3}}}}.
$$

The material-level centres were 0.375963 for the energy factor and 0.202683 for the susceptibility factor (Fig. 2b), and frequency allocation carried a material-median 62.0% of the absolute log effect. ZFP places less error energy in the long-wavelength modes that the Hartree symbol amplifies (Fig. 2a).

The same symbol prescribes the allocation. For a linear operator diagonal in reciprocal space with symbol $a(G)$, the squared operator error of a density error $\delta\rho$ is $\sum_G w(G)\,|\delta\rho(G)|^2$ with weight $w=|a|^2$. Under high-rate scalar quantization, minimizing this weighted error at fixed rate gives the classical step-size law<sup>21,22</sup>

$$
\Delta_G\propto w(G)^{-1/2}.
$$

For the Hartree potential, $a=4\pi/|G|^2$, so $w\propto|G|^{-4}$ and $\Delta_G\propto|G|^2$ (Fig. 2c). The allocation algebra is textbook; what the operator adds is the weight, taken from physics rather than from perception or signal statistics, and the certificate: every stream is decoded and its Hartree error recomputed from the real-space field. A frozen-ladder implementation of this law was confirmed earlier on a disjoint 48-material cohort and a 254-material census (Supplementary Note 2).

### Under equal search, the law certifies an order of magnitude more than pointwise codecs on bulk crystals and surface slabs

We tested the law prospectively on 60 Materials Project bulk crystals and 32 NOMAD surface slabs that had never been used in the project (Methods). Three arms received the same continuous search with decode-verified certificates: the closed-form law (A1), spectral truncation at the best of 32 cutoffs (A2), and the best of ZFP, SZ3 and SPERR (A6). The Hartree contract is relative root-mean-square potential error below $\tau$, with historical and Nyquist-safe evaluation. Both cohorts ran with zero pipeline failures.

At $\tau=10^{-6}$, the law certified a median 10.2-fold more compression than the best pointwise codec on bulk crystals (95% CI 9.13–12.09; 60/60 materials) and 18.5-fold more on slabs (15.8–23.1; 32/32) (Fig. 3a). It exceeded spectral truncation 1.32-fold (1.27–1.35; 52/60) and 1.41-fold (1.28–1.72; 27/32) (Fig. 3b). The advantage over pointwise codecs held at every tolerance: 9.10-, 10.2- and 3.30-fold on bulk crystals and 15.9-, 18.5- and 7.0-fold on slabs at $10^{-4}$, $10^{-6}$ and $10^{-8}$ (Fig. 3c; per-tolerance tables in Supplementary Note 5).

The advantage over truncation is a property of tight tolerances. It grows to 1.59-fold (bulk) and 2.16-fold (slabs) at $10^{-8}$, whereas at $10^{-4}$ truncation certifies more (ratios 0.79 and 0.69). At that rate most coefficients fall in the quantizer's dead zone, the regime in which low-rate transform-coding theory replaces the high-rate law [CITATION NEEDED: Mallat & Falzon 1998, low-bit-rate transform coding; Sullivan 1996, dead-zone scalar quantization of Laplacian sources]. Operational allocation, examined next, covers that regime.

### The operator metric carries the gain, and the system class sets the optimizer's share

To separate the metric from the optimizer, we built the operational optimum (A3): Lagrangian selection, per radial shell, over exact pairs of compressed bytes and operator distortion,<sup>30,31</sup> targeted directly at the decode-verified Hartree certificate. Its control (A5) runs the same machinery in the operator-blind $L_2$ metric, with the Lagrange multiplier chosen only so that the same Hartree certificate holds.

The metric carries the gain. At $\tau=10^{-6}$, the optimum under the operator metric certified 2.12-fold more than the optimum under the blind metric on bulk crystals (95% CI 1.92–2.46; 60/60) and 3.43-fold more on slabs (2.89–4.08; 32/32) (Fig. 4a). The ratio exceeded 1.3 at every tolerance (bulk 1.33, 2.12 and 1.60; slabs 1.82, 3.43 and 3.04 at $10^{-4}$, $10^{-6}$ and $10^{-8}$).

The optimizer's share depends on the system class. For bulk crystals the closed-form law is within 10.5% of the operational optimum (median ratio 1.105, 95% CI 1.090–1.146, 60 crystals); for surface slabs operational allocation adds 22% (median ratio 1.222, 95% CI 1.138–1.359, 32 slabs), at a Hartree tolerance of $10^{-6}$ (Fig. 4b). The share shrinks as the tolerance tightens (bulk 1.58, 1.10 and 1.03; slabs 2.22, 1.22 and 1.08 at $10^{-4}$, $10^{-6}$ and $10^{-8}$). The closed-form law is therefore the encoder for bulk crystals at tight tolerances, and operational allocation the encoder for surfaces, for loose tolerances and for joint contracts.

### One stream certifies the Hartree potential and Bader charges together

A stored density usually serves more than one analysis. We froze a joint contract before any run (Methods): Hartree relative error below $10^{-6}$ on the final stream, and Henkelman Bader charges with an exact all-electron partition reference, maximum atomic-charge error at most $\tau_B$ and zero basin reassignment, for $\tau_B=10^{-3}$, $10^{-4}$ and $10^{-5}\,e$. Four base codecs competed: the operational Hartree encoder (R3, the A3 codec), the frozen-ladder law (J), spectral truncation (T1) and the best of ZFP, SZ3 and SPERR (GF). Each base received the same post-processors, including uniform per-basin projection, which restores each basin's charge with the minimum-norm correction in the manner of constraint-satisfaction post-processing,<sup>12</sup> and certify-then-project, which projects only when the decoded stream fails the Bader contract.

On 48 fresh bulk crystals, one stream from R3, certified for the Hartree potential at $10^{-6}$, was also certified for Bader charges with zero basin reassignment at $10^{-3}$, $10^{-4}$ and $10^{-5}\,e$ in 48/48 materials. At $10^{-4}\,e$ its joint compression ratio equalled its Hartree-only ratio (median overhead 1.000, 95% CI 1.000–1.000; Fig. 5a) and exceeded that of the best other base codec under the same joint contract in 48/48 materials (median 1.317-fold, 95% CI 1.269–1.360; minimum 1.096). Median joint compression ratios were 298 for R3, 213 for J, 212 for T1 and 18.6 for GF (Fig. 5b).

The Hartree certificate already carries the Bader charges under an exact partition. The unprojected stream was the best joint choice in 48/48 materials at $10^{-3}$ and $10^{-4}\,e$, certify-then-project applied a projection in 0/192, 0/192 and 31/165 decisions at the three tolerances (Fig. 5c), and the median overhead was 1.000 at every $\tau_B$. The 12-material engineering cohort that authorized this test gave the same picture (12/12; overhead 1.000; 12/12 wins, median 1.355; Supplementary Note 4). When a source must be self-contained, the partition itself can be stored losslessly as a label map or as a partition-faithful all-electron reference (Supplementary Note 3).

### The gain is predicted before compression from the operator symbol and the reference spectrum

Whether operator-aware coding is worth deploying depends on the operator. For five linear operators of the density (gradient, Laplacian, Hartree field, Hartree potential and Gaussian smoothing with $\sigma=0.5$ Å) and the density itself as control, we compared operator-weighted allocation ($\Delta_G\propto w^{-1/2}$) with operator-blind allocation (uniform steps) at equal operator error and recorded the measured gain $G_{\text{obs}}$ as the ratio of their compressed sizes. Before any compression, we computed the predicted gain $G_{\text{pred}}$ for every material and operator from the operator symbol and the material's reference spectrum alone, with a finite-rate entropy-coded quantization model (Methods), and committed the predictions to the repository.

The predictions matched. At $\tau=10^{-6}$, the median absolute log error was 0.024 over 300 bulk pairs and 0.029 over 160 slab pairs, with Spearman rank correlations of 0.978 and 0.979 (Fig. 6a); pooled over the 92 materials, 0.026 and 0.977, with 80% of pairs within 25% (per-operator tables in Supplementary Note 5). Every pair of operators was ordered as predicted, and the density control gave $G_{\text{obs}}=1$. At $\tau=10^{-4}$ the errors were 0.034 and 0.040, with Spearman 0.944 and 0.914 (Fig. 6b). Within each operator that gains, the predictor also ranked the materials (pooled Spearman 0.79 for the Hartree potential, 0.84 for the Hartree field, 0.89 for Gaussian smoothing).

The operator symbol sets which operators gain (Fig. 6c). Derivative operators gain little: predicted and measured median gains were 1.014 and 1.011 for the gradient and 1.039 and 1.042 for the Laplacian on bulk crystals (slabs: 1.012 and 1.015; 1.031 and 1.047), and the measured gain fell within [0.90, 1.11] in 100% and 98.3% of bulk crystals (100% and 96.9% of slabs), as predicted. The Hartree field gains about 15% (1.151 and 1.149; slabs 1.164 and 1.165), the Hartree potential 2.6–3.1-fold (2.72 and 2.61; slabs 3.55 and 3.14), and Gaussian smoothing an order of magnitude (17.6 and 12.1; slabs 22.0 and 15.3). The predictor is the classical coding-gain construction<sup>32</sup> [CITATION NEEDED: Huang & Schultheiss 1963, block quantization; Wei, Shaw & Varley 1997, perceptual coding gain] evaluated with a physical weight and a finite-rate dead-zone model; compression-ratio prediction from data statistics is established separately [CITATION NEEDED: Underwood et al. 2023, black-box prediction of lossy compression ratios].

## Discussion

The downstream operator enters certified compression at each stage, and each stage licenses a different decision. Qualification decides whether a tolerance can be scored at all; a non-evaluable outcome is resolved by changing the contract, not the codec, as holding the Bader partition reference exact moved eligibility from 3/50 to 50/50. Gain prediction decides, before any compression run, whether operator-aware coding is worth deploying for a given operator: about 1–5% for derivative operators, two- to three-fold for the Hartree potential, an order of magnitude for smoothing. The system class decides the encoder: the closed-form law for bulk crystals at tight tolerances, operational allocation for surfaces and loose tolerances. Certification decides whether the decoded object meets the contract, for one operator or for several.

The operator is thus the unit of design. Task-based quantization<sup>20</sup> and weighted transform coding<sup>21–23</sup> supply the principle and the algebra; QoI-preserving compressors supply bounds, corrections and predictions for declared quantities.<sup>8–17</sup> The present work adds the physical instantiation and its quantified consequences: the symbol of the downstream operator, read on each material's reciprocal lattice, explains a codec effect at matched distortion, fixes a closed-form allocation, forecasts its gain, and defines the certificate under which the decoded field is accepted. The operator metric, not the optimizer, carries the gain (2.12- and 3.43-fold at equal optimization), which is why a physically correct weight matters more than a better search.

Joint certification shows how contracts compose. Several QoIs have been controlled on one stream before, in fusion data, progressive retrieval and combinable safeguards.<sup>11,12,15,17</sup> Here the two contracts differ in kind: a global elliptic-operator norm on the reciprocal lattice and integrals over a topologically defined real-space partition, certified by the production Bader code. Under an exact partition, the Hartree certificate already carried the Bader charges to $10^{-4}\,e$ at no measurable cost, and a projection was needed only at $10^{-5}\,e$.

The results are defined on linear reciprocal-space operators of the valence density and on the exact-partition Bader contract; on bulk crystals from the Materials Project and surface slabs from NOMAD; and on Hartree tolerances from $10^{-4}$ to $10^{-8}$. Within that scope, every confirmatory number follows a protocol, population rule and, where applicable, prediction file committed before its outcomes, and the full register of protocols and outcomes is public. For electronic-structure data, the question shifts from whether a density can be compressed to which analyses its stored form must support, and the operator of each analysis then says how to store it.

## Methods

### Measurement contract and QSQ

A contract $C$ specifies the QoI, the downstream algorithm, the tolerance $\tau$ and whether each input is exact or approximate. QSQ perturbs only approximate inputs. For an approximate density $\rho_m$, $\epsilon_m=\lVert\mathrm{float32}(\rho_m)-\rho_m\rVert_\infty$, and five fixed-seed perturbations $U(-\epsilon_m,+\epsilon_m)$ (seeds 20260905, 1, 2, 3, 4) are applied. The floor is $f_C=\max_k r_{C,k}$, the largest response over the five probes (for Bader charge, the maximum absolute per-atom charge change with re-derived basins), and

$$
\text{eligible}(C,\tau)\equiv f_C<\tau,\qquad \text{certified}(r,C,\tau)\equiv\text{eligible}(C,\tau)\land \Delta Q(r)<\tau .
$$

An ineligible pair is non-evaluable; an eligible pair with no certified reconstruction is not certified. If the $n$ qualification responses and a later response are exchangeable, $P[\text{eligible}\land r^\ast\ge\tau]=\mathbb{E}[p(1-p)^n]\le n^n/(n+1)^{n+1}$, the one-sided tolerance-limit argument.<sup>33</sup> The prospective test used 59 fresh seeds per material (labels 10000–10058, PCG64 streams from SHA-256 of material, family and label); the work order of 14,986 keys was hashed before execution. The all-electron-reference contract used Henkelman Bader 1.05 (`-b ongrid -vac 0.001`) with CHGCAR integrated over basins of $\rho_{\text{AE}}=\text{AECCAR0}+\text{AECCAR2}$. Full QSQ protocols are in Supplementary Note 1 and the repository.

### Hermitian-orbit representation and certificate

Densities are transformed with an orthonormal FFT. Reciprocal indices are partitioned into Hermitian orbits under $k\mapsto-k \pmod N$, one canonical coefficient is stored per orbit, and $G=0$ is the only coefficient stored exactly. On even grids, a Nyquist coordinate is alias-equivalent to $\pm N/2$; for every such mode the alias choices are enumerated and the minimum $|G|^2_{\text{safe}}$ is used, so no mode receives a looser step from a sign convention. A policy assigns $\Delta_G=\alpha\,u_G$; for the closed-form law $u_G=w(G)^{-1/2}$ normalized at $G_{\max,\text{safe}}$, giving $\Delta_G=\alpha(|G|_{\text{safe}}/G_{\max,\text{safe}})^2$ for the Hartree potential. Real and imaginary parts are rounded to integers, grouped into 32 radial shells with the smallest sufficient signed integer type, and compressed with zlib level 6. Compression ratio is $8N$ divided by the complete stream bytes, headers included. Every stream is decoded and certified when the Hartree relative root-mean-square error is below $\tau$ under both the historical operator ($4\pi/|G|^2$, $G=0$ set to zero) and the Nyquist-safe operator (even-grid Nyquist planes also removed), for which

$$
\mathrm{RMS}(\Delta V_H)^2=\frac{(4\pi)^2}{N^2}\sum_{G\in\mathcal G_s}\frac{|\Delta\rho(G)|^2}{|G|^4}.
$$

For the spectral audit, ZFP and SZ3 reconstructions of the 254 development densities were matched within material on $\log_{10}$ of realized $L_\infty$, without replacement, with a caliper of 0.10 dex; the 914 reconstructions of the 457 pairs were regenerated and had to reproduce their stored $L_\infty$ and Hartree error before entering the audit. Material-level centres are computed from within-material medians on the log scale; the multiplicative decomposition is exact for each pair.

### Arms and the operational optimum

Arms follow the frozen protocol. A0: closed-form law, frozen 25-point ladder $\alpha/\mathrm{ptp}(\rho)\in[10^{-7},10^{1}]$. A1: closed-form law, continuous $\alpha$ bisection. A2: spectral truncation at cutoff $q_c\in\{k/32\}$, bisection per cutoff, best cutoff. A3: operational optimum, $\Delta_k=m_s u_k$ with a per-shell multiplier from a $2^{1/4}$ ladder or the shell dropped, selected by bisection on the Lagrange multiplier over each shell's exact (zlib bytes, operator distortion) curve plus a feasibility-preserving greedy polish, under both Hartree certificates with margin 0.995. A5: the same machinery with a flat prior and $L_2$ selection metric, multiplier chosen only so that the Hartree certificate holds. A6: best of ZFP, SZ3 and SPERR<sup>2–4</sup> by absolute-tolerance bisection. Bisection arms use 60 iterations in log space and report the highest-ratio evaluated point that passes the decoded certificate; A1, A2 and A6 therefore have equal search. Tolerances were $\tau\in\{10^{-4},10^{-6},10^{-8}\}$, primary $10^{-6}$.

### Gain predictor

Part B used six operators with squared weights $w=1$ (density), $|G|^2$ (gradient), $|G|^4$ (Laplacian), $|G|^{-2}$ (Hartree field), $|G|^{-4}$ (Hartree potential) and $\exp(-\sigma^2|G|^2)$, $\sigma=0.5$ Å (Gaussian smoothing). The operator-weighted arm used $u=w^{-1/2}$ and the blind arm $u=1$; each used continuous $\alpha$ bisection on the Nyquist-safe relative error in that operator's metric (margin 0.995), every stream was decode-verified, and $G_{\text{obs}}=\text{bytes}_{\text{blind}}/\text{bytes}_{\text{opt}}$. The predictor models each real coefficient component as a zero-mean Laplacian whose variance is the reference spectral power averaged over 256 radial $|G|$ bins, quantized by rounding with ideal entropy coding, for which output entropy and mean squared error have exact closed forms. For each policy, $\alpha$ is solved for the target operator error, giving predicted payload bits $R$, and

$$
G_{\text{pred}}=\frac{F+R_{\text{blind}}/8}{F+R_{\text{opt}}/8},
$$

where $F$ is the geometry-only container size. The model includes the dead zone that the high-rate law ignores. Its form was fixed by a retrospective calibration on 12 engineering materials (Supplementary Note 6) and then tested only prospectively.

### Populations and pre-registration chronology

Populations were drawn under rules frozen before any candidate was downloaded and excluding every identifier (833) and reduced formula (291) used anywhere in the project. P1 (12 shakedown + 60 confirmatory) and P2 (12 engineering + 48 confirmatory, with AECCAR0 and AECCAR2) are Materials Project bulk crystals drawn by hash rank within size strata from the open S3 listing<sup>[CITATION NEEDED: Materials Project database]</sup>; P3b is 32 NOMAD VASP surface slabs<sup>[CITATION NEEDED: NOMAD repository]</sup>, one per reduced formula and at most six per upload. Only metadata was read before the freeze; no outcome was computed on any candidate. Table 1 lists the commit order; commits are on the public repository and timestamps are UTC. Full protocols, manifests, provenance hashes and the register of every protocol with its outcome are in the repository.

**Table 1 | Pre-registration chronology.**

| step | commit | time (UTC) |
|---|---|---|
| Population selection rule and exclusion set frozen | `10e7863` | 2026-10-06 14:27 |
| P1 and P2 manifests drawn | `708dd37` | 2026-10-06 15:09 |
| Law protocol (Parts A and B, criteria) frozen | `fe2e08a` | 2026-10-06 15:26 |
| P1 predictions committed | `d5fc30b` | 2026-10-06 15:32 |
| P1 run recorded | `4164519` | 2026-10-06 15:54 |
| P3b selection rule and protocol amendment frozen | `39ba728` | 2026-10-06 15:59 |
| P3b cohort drawn | `d1c1050` | 2026-10-06 16:03 |
| P3b predictions committed | `c1e6564` | 2026-10-06 16:08 |
| P3b run recorded | `eaa3267` | 2026-10-06 16:23 |
| Joint-contract protocol and criteria frozen | `8a784a4` | 2026-10-06 16:25 |
| Joint-contract engineering gates passed | `e095a0c` | 2026-10-06 16:42 |
| Joint-contract confirmation recorded | `e4d9d0b` | 2026-10-06 18:00 |

### Joint contract and certify-then-project

The joint contract requires Hartree relative error below $10^{-6}$ (historical and Nyquist-safe) on the final stream and, with Henkelman Bader 1.05 (`-b ongrid -vac 0.001`, exact AECCAR0 + AECCAR2 reference), maximum atomic-charge error at most $\tau_B$ and zero basin reassignment. Bases: R3 (the A3 codec), J (frozen-ladder law), T1 (truncation ladder) and GF (ZFP, SZ3 and SPERR at $\text{abs\_tol}/\mathrm{ptp}=10^{-9}$ to $10^{-1}$, 25 points). Post-processors: none; uniform projection, which adds $d_i/N_i$ on basin $i$ to restore the stored basin sums; Hartree-aware projection, which minimizes $\lVert Hc\rVert^2/s_H+\mu\lVert c\rVert^2/s_\rho$ subject to the same sums ($\mu\in\{10^{-4},10^{-2},1\}$); and certify-then-project, which stores a one-byte flag, runs Bader on the unprojected stream and applies a projection only if that stream fails. Bytes include payload, side channel and flag. For each material, $\tau_B$ and base, the best post-processor is the one with the highest certified joint ratio, a choice every base receives. Overhead is $\text{CR}_{\text{Hartree-only}}/\text{CR}_{\text{joint}}$ for R3; utility is the R3 joint ratio over the maximum joint ratio of J, T1 and GF.

### Statistics

Medians and percentile 95% confidence intervals of the median come from 10,000 bootstrap resamples over materials with fixed seeds (20261006 for the law protocol, 20261007 for the joint contract). Pre-registered criteria were, for the law: near-optimality median $\text{CR}_{A3}/\text{CR}_{A1}\le1.15$ with CI upper bound $\le1.20$; operator metric median $\text{CR}_{A3}/\text{CR}_{A5}>1.5$, CI lower bound $>1.35$, wins $\ge90\%$; pointwise codecs median $>4$, wins $\ge95\%$; truncation median $>1.15$, wins $\ge75\%$; prediction median $|\ln(G_{\text{pred}}/G_{\text{obs}})|\le\ln1.25$ and Spearman $\ge0.85$ over operator–material pairs, operator ordering preserved, and $G_{\text{obs}}\in[0.90,1.11]$ in $\ge80\%$ of materials for operators with median $G_{\text{pred}}<1.05$. For the joint contract: $\ge46/48$ jointly certified; overhead median $\le1.10$ with CI upper bound $\le1.15$; utility $\ge36/48$ wins, median $>1.10$, CI lower bound $>1.00$. QSQ intervals are material-cluster bootstrap intervals. Spearman correlations are computed over operator–material pairs, excluding the density control.

## Data availability

Source densities are public. Bulk crystals are Materials Project charge densities (CHGCAR, AECCAR0, AECCAR2) from the open S3 bucket `materialsproject-parsed` (listing of 2026-10-06);<sup>[CITATION NEEDED: Materials Project database]</sup> surface slabs are NOMAD VASP entries retrieved through the public NOMAD API;<sup>[CITATION NEEDED: NOMAD repository]</sup> the external QSQ cohort also uses AFLOW densities.<sup>[CITATION NEEDED: AFLOW repository]</sup> Every manifest records identifier, URL, byte count and SHA-256. All derived tables, per-material results, prediction files, protocols and the register of every protocol with its outcome are in the public repository https://github.com/stloendays/QoI. An archival snapshot will be deposited at Zenodo (DOI: [placeholder: to be minted at submission]).

## Code availability

All code (QSQ, codecs, arms, gain predictor, joint-contract runner, statistics and figure scripts) is in the public repository https://github.com/stloendays/QoI, with the continuous-integration workflows that ran each pre-registered phase. The archival snapshot is the Zenodo record above (DOI: [placeholder: to be minted at submission]).

## References

1. Di, S. *et al.* A survey on error-bounded lossy compression for scientific datasets. *ACM Comput. Surv.* **57**, 287 (2025).
2. Lindstrom, P. Fixed-rate compressed floating-point arrays. *IEEE Trans. Vis. Comput. Graph.* **20**, 2674–2683 (2014).
3. Liang, X. *et al.* SZ3: A modular framework for composing prediction-based error-bounded lossy compressors. *IEEE Trans. Big Data* **9**, 485–498 (2023).
4. Li, S., Lindstrom, P. & Clyne, J. Lossy scientific data compression with SPERR. In *Proc. 2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)* 1007–1017 (IEEE, 2023).
5. Cappello, F. *et al.* Use cases of lossy compression for floating-point data in scientific data sets. *Int. J. High Perform. Comput. Appl.* **33**, 1201–1220 (2019).
6. Gok, A. M. *et al.* PaSTRI: Error-bounded lossy compression for two-electron integrals in quantum chemistry. In *Proc. 2018 IEEE International Conference on Cluster Computing (CLUSTER)* 1–11 (IEEE, 2018).
7. Lara, A. O., Talbot, J. J., Wang, Z. & Head-Gordon, M. An algorithm for atom-centered lossy compression of the atomic orbital basis in density functional theory calculations. *J. Chem. Theory Comput.* **22**, 3327–3340 (2026).
8. Ainsworth, M., Tugluk, O., Whitney, B. & Klasky, S. Multilevel techniques for compression and reduction of scientific data—quantitative control of accuracy in derived quantities. *SIAM J. Sci. Comput.* **41**, A2146–A2171 (2019).
9. Jiao, P. *et al.* Toward quantity-of-interest preserving lossy compression for scientific data. *Proc. VLDB Endow.* **16**, 697–710 (2022).
10. Liu, J. *et al.* QPET: A versatile and portable quantity-of-interest-preservation framework for error-bounded lossy compression. *Proc. VLDB Endow.* **18**, 2440–2453 (2025).
11. Gong, Q. *et al.* Maintaining trust in reduction: Preserving the accuracy of quantities of interest for lossy compression. In *Driving Scientific and Engineering Discoveries Through the Integration of Experiment, Big Data, and Modeling and Simulation* 22–39 (Springer, 2022).
12. Lee, J. *et al.* Error-bounded learned scientific data compression with preservation of derived quantities. *Appl. Sci.* **12**, 6718 (2022).
13. Banerjee, T. *et al.* Online and scalable data compression pipeline with guarantees on quantities of interest. In *Proc. 2023 IEEE 19th International Conference on e-Science (e-Science)* 1–10 (IEEE, 2023).
14. Liu, Y. *et al.* TOPIQ: Statistical error propagation for quantity-of-interest prediction under lossy compression. Preprint at https://arxiv.org/abs/2608.26912 (2026).
15. Tyree, J. *et al.* Compression Safeguards: Building trust into lossy data compression. *EGUsphere* https://doi.org/10.5194/egusphere-2026-4266 (2026).
16. Ren, C. *et al.* FFCz: Fast Fourier correction for spectrum-preserving lossy compression of scientific data. Preprint at https://arxiv.org/abs/2601.01596 (2026).
17. Wu, X. *et al.* Error-controlled progressive retrieval of scientific data under derivable quantities of interest. In *Proc. International Conference for High Performance Computing, Networking, Storage and Analysis (SC24)* (IEEE, 2024); preprint at https://arxiv.org/abs/2411.05333. [CITATION NEEDED: SC24 proceedings DOI and pages]
18. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving topology in error-bounded lossy compression. *IEEE Trans. Vis. Comput. Graph.* **30**, 1302–1312 (2024).
19. Gorski, N., Liang, X., Guo, H., Yan, L. & Wang, B. A general framework for augmenting lossy compressors with topological guarantees. *IEEE Trans. Vis. Comput. Graph.* **31**, 3693–3705 (2025).
20. Shlezinger, N., Eldar, Y. C. & Rodrigues, M. R. D. Hardware-limited task-based quantization. *IEEE Trans. Signal Process.* **67**, 5223–5238 (2019).
21. Gersho, A. & Gray, R. M. *Vector Quantization and Signal Compression* (Springer, 1992).
22. Goyal, V. K. Theoretical foundations of transform coding. *IEEE Signal Process. Mag.* **18**, 9–21 (2001).
23. Watson, A. B. DCT quantization matrices visually optimized for individual images. In *Proc. SPIE* **1913** (1993).
24. Currie, L. A. Nomenclature in evaluation of analytical methods including detection and quantification capabilities (IUPAC Recommendations 1995). *Pure Appl. Chem.* **67**, 1699–1723 (1995).
25. Automotive Industry Action Group. *Measurement Systems Analysis Reference Manual*, 4th edn (AIAG, 2010).
26. Bader, R. F. W. *Atoms in Molecules: A Quantum Theory* (Oxford Univ. Press, 1990).
27. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. *Comput. Mater. Sci.* **36**, 354–360 (2006).
28. Tang, W., Sanville, E. & Henkelman, G. A grid-based Bader analysis algorithm without lattice bias. *J. Phys.: Condens. Matter* **21**, 084204 (2009).
29. Yu, M. & Trinkle, D. R. Accurate and efficient algorithm for Bader charge integration. *J. Chem. Phys.* **134**, 064111 (2011).
30. Shoham, Y. & Gersho, A. Efficient bit allocation for an arbitrary set of quantizers. *IEEE Trans. Acoust. Speech Signal Process.* **36**, 1445–1453 (1988).
31. Ortega, A. & Ramchandran, K. Rate-distortion methods for image and video compression. *IEEE Signal Process. Mag.* **15**, 23–50 (1998).
32. Jayant, N. S. & Noll, P. *Digital Coding of Waveforms* (Prentice-Hall, 1984).
33. Wilks, S. S. Determination of sample sizes for setting tolerance limits. *Ann. Math. Stat.* **12**, 91–96 (1941).

## Figure legends

**Fig. 1 | A scientific tolerance can be scored only once the measurement contract resolves it.** **a**, Workflow: the contract (QoI, algorithm, tolerance, exact or approximate inputs) is qualified by QSQ; an operator-derived design produces a stream that is decoded and certified; each decision is certified, not certified or non-evaluable. **b**, Fresh threshold-exceedance risk in QSQ-qualified and rejected materials at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$ (254 materials, 59 fresh perturbations each; at $10^{-3}\,e$, 1.600% versus 81.325%); 95% CIs are material-cluster bootstrap intervals. **c**, Per-material fresh exceedance fraction against the QSQ floor relative to the tolerance. **d**, Equal-search control: fraction of material–codec pairs with no passing reconstruction at $10^{-3}\,e$ after completing the same tight settings for every material (3.3% versus 66.4%).

**Fig. 2 | The operator's spectral weight explains the codec effect at matched distortion and fixes the allocation law.** **a**, Radial error spectra of ZFP and SZ3 reconstructions matched on realized $L_\infty$. **b**, Exact pairwise decomposition of the Hartree-error ratio into total spectral energy (material-level centre 0.375963) and Hartree susceptibility (0.202683); 457 pairs, 214 materials. **c**, The Hartree symbol $4\pi/|G|^2$ gives the squared-error weight $|G|^{-4}$ and the step-size law $\Delta_G\propto|G|^2$.

**Fig. 3 | Under equal search, the closed-form law certifies an order of magnitude more than pointwise codecs.** **a**, Certified compression ratio of the law (A1) against the best of ZFP, SZ3 and SPERR (A6) at Hartree relative error $10^{-6}$, for 60 bulk crystals and 32 surface slabs (medians 10.2-fold and 18.5-fold). **b**, A1 against spectral truncation (A2) at $10^{-6}$ (1.32-fold, 52/60; 1.41-fold, 27/32). **c**, Medians with bootstrap 95% CIs of A1/A6 and A1/A2 at $10^{-4}$, $10^{-6}$ and $10^{-8}$ for each cohort. All streams decode-verified; A1, A2 and A6 have equal continuous search.

**Fig. 4 | The operator metric carries the gain; the optimizer's share depends on the system class.** **a**, Operational optimum under the operator metric (A3) over the same optimum under the blind metric (A5), per material, at three tolerances (at $10^{-6}$: 2.12-fold, 60/60; 3.43-fold, 32/32). **b**, Operational optimum over the closed-form law (A3/A1) by system class at three tolerances; at $10^{-6}$ the law is within 10.5% of the optimum for bulk crystals (median 1.105, 95% CI 1.090–1.146) and operational allocation adds 22% for slabs (1.222, 1.138–1.359).

**Fig. 5 | One operator-aware stream certifies the Hartree potential and Bader charges together.** 48 fresh bulk crystals; Hartree relative error $10^{-6}$; Henkelman Bader charges with exact partition reference and zero basin reassignment. **a**, Joint overhead (Hartree-only over joint compression ratio) of the operational encoder R3 at $\tau_B=10^{-3}$, $10^{-4}$ and $10^{-5}\,e$ (median 1.000 at each). **b**, Joint compression ratio at $\tau_B=10^{-4}\,e$ for R3, frozen-ladder law (J), truncation (T1) and pointwise codecs (GF) (medians 298, 213, 212 and 18.6; R3 best in 48/48, median 1.317-fold over the best other base). **c**, Certify-then-project decisions per $\tau_B$ (projections 0/192, 0/192 and 31/165).

**Fig. 6 | The gain of operator-aware allocation is predicted before compression.** **a**, Predicted against measured gain at $\tau=10^{-6}$ for 300 bulk and 160 slab material–operator pairs; colour, operator; marker, cohort; density control at (1, 1); line, identity (median absolute log error 0.024 and 0.029; Spearman 0.978 and 0.979; pooled 0.977). **b**, The same at $\tau=10^{-4}$. **c**, Per-operator medians, predicted and measured, ordered by predicted gain, with the null-gain band [0.90, 1.11]. Predictions were committed before compression (P1 `d5fc30b`, P3b `c1e6564`).
