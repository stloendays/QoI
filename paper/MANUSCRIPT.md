# The downstream operator qualifies, predicts and shapes the certified compression of electronic densities

Junbo Tong<sup>1</sup>

<sup>1</sup>National University of Singapore, Singapore.

ORCID: Junbo Tong, https://orcid.org/0009-0006-5158-3471

## Abstract

Compressed fields are judged by quantities computed from them, yet the reference analysis may not resolve the tolerance at which a quantity of interest (QoI) is scored. Here the downstream operator decides whether, how and how far an electronic density can be compressed. QoI Stability Qualification (QSQ) screens the measurement contract: in 254 densities, five probes separated fresh Bader exceedance risks of 1.6% and 81.3% in qualified and rejected materials. For linear operators, the reciprocal-space symbol prescribes the allocation and predicts its gain before compression (Spearman 0.978 and 0.979 on new crystals and slabs); for the nonlinear exchange-correlation energy, its linearization prescribes nearly the Hartree allocation. For the Hartree potential, the law certified 6.3–9.5-fold more than QoI-preserving QPET and over 20-fold more than Fourier-corrected FFCz. Certified storage would shrink the 8.50 TB Materials Project archive 347-fold, against 35-fold for pointwise codecs, and one stream certifies Hartree and Bader quantities together.

## Introduction

Electronic-structure databases store electron densities on dense real-space grids, and error-bounded lossy compressors such as ZFP, SZ3 and SPERR are the standard means of reducing such fields.<sup>1–5</sup> In quantum chemistry they compress two-electron integrals and atomic-orbital bases.<sup>6,7</sup> Yet a stored density is rarely the scientific result: the result is a quantity of interest (QoI) computed from it, such as a potential, a field or an atomic charge.

Downstream fidelity is an established target of scientific compression. Existing methods control derived quantities through multilevel operator norms,<sup>8</sup> QoI-aware error bounds,<sup>9</sup> and differentiable-QoI adaptation;<sup>10</sup> preserve multiple QoIs by constrained reconstruction;<sup>11–13</sup> predict QoI bias and uncertainty;<sup>14</sup> enforce bounds through post-correction;<sup>15,16</sup> guarantee progressive retrieval accuracy;<sup>17</sup> and preserve discrete topology.<sup>18,19</sup> These methods make a declared QoI faithful to its reference; they do not establish whether the reference analysis can resolve the declared tolerance.

Task-based quantization designs a quantizer for the task it serves rather than for the signal.<sup>20</sup> Weighted step sizes are classical high-rate allocation,<sup>21,22</sup> and step maps tuned to a downstream error model are used in image coding<sup>23</sup> and scientific compression.<sup>24</sup> For a stored electronic density the task is often a physical operator with an exact reciprocal-space symbol, which could set the allocation, forecast its benefit and define the certificate at once.

Measurement science adds a step that compression benchmarks omit. Analytical chemistry does not report a concentration below a method's limit of quantification,<sup>25</sup> and measurement-system analysis compares gauge variation with the tolerance before the gauge accepts or rejects parts.<sup>26</sup> In a compression benchmark the reference analysis plays the gauge, and its capability under the declared contract decides whether a tolerance can be scored at all.

Here the measurement contract, not the field, is the object that compression must satisfy, and the downstream operator has three roles in it (Fig. 1): QSQ qualifies the contract and predicts fresh numerical risk; the reciprocal-space symbol of a linear operator determines an allocation law; and that symbol with the reference spectrum predicts coding gain before compression. We test allocation and prediction on new bulk crystals and surface slabs, then certify one bulk-crystal stream for the Hartree potential and exact-partition Bader charges. Each cohort test ran under populations and acceptance criteria fixed before its outcomes were computed (Methods; Table 1).

## Results

### A tolerance is scored only after the measurement contract resolves it

A measurement contract declares the QoI, the downstream numerical algorithm, the scientific tolerance $\tau$ and the role of every input as exact or approximate. QSQ perturbs the approximate inputs five times at their own float32 precision scale, takes the maximum downstream response as the stability floor $f_C$, and admits the contract when $f_C<\tau$ (Methods). Each material–contract–tolerance decision then ends in one of three outcomes: certified, not certified, or non-evaluable (Fig. 1b). For Bader charge, atomic basins follow the topology of a partition-defining density,<sup>27</sup> and grid algorithms re-derive them for every input.<sup>28–30</sup>

We fixed the five-probe screen and challenged it with 59 fresh perturbations for each of 254 development densities (186 Materials Project bulk crystals, 68 NOMAD slabs). At $10^{-3}\,e$, QSQ admitted 143/254 materials. Qualified materials exceeded the threshold in 135/8,437 fresh trials (1.60%; material-cluster 95% CI 0.78–2.60%) and rejected materials in 5,326/6,549 (81.3%; 76–86%); almost every rejected material, but few qualified ones, showed any exceedance (Fig. 2a,d). The separation held at $10^{-4}$ and $10^{-2}\,e$ (Supplementary Note 1).

Qualification also governs codec comparisons. At equal tight settings, the no-pass fraction at $10^{-3}\,e$ was 3.3% for qualified and 66.4% for rejected material–codec pairs (Fig. 2c). Because probes and fresh perturbations are independent draws from one perturbation law, a finite panel carries a guarantee: the joint probability of admission and a later exceedance is at most $n^n/(n+1)^{n+1}$, 6.70% for $n=5$ (Methods). The observed joint rate was 0.90% (Fig. 2b).

Evaluability belongs to the contract, not to the material. With Henkelman Bader 1.05 and an all-electron partition reference (AECCAR0 + AECCAR2), perturbing only the integrated charge field left 50/50 analyzable materials eligible at $10^{-3}\,e$, whereas perturbing the partition reference left 3/50. Holding the partition reference exact therefore makes Bader charges scorable and defines the Bader contract used below.

The contract also decides which codec is better. In 185 development materials, an SZ3 and a SPERR reconstruction were matched in density maximum and root-mean-square error within 0.10 dex, without Bader outcomes. With reference basins SPERR gave the smaller Bader error in 185/185 materials; with basins re-derived from the decoded density, as the QSQ contract prescribes, SZ3 did in 109/185. The re-derived error ratio followed the ratio of reassigned voxels (Spearman 0.607), not the matched density errors (Supplementary Note 1 and Supplementary Fig. 1). Matched field distortion therefore fixes neither the outcome nor the codec order of a topology-defined QoI.

Qualification also sets what an archive gains. We applied QSQ, a certifying ZFP/SZ3/SPERR writer and the Bader certificate to a stratified sample of 300 objects of the public Materials Project charge-density archive (415,289 objects, 8.50 TB as gzipped JSON; Methods). The total density is stored certified where eligible and losslessly otherwise, the magnetization density under a per-atom magnetic-moment contract. At $10^{-3}\,e$ the archive shrinks 4.34-fold (95% CI 3.61–5.37), although 35.9% of objects are non-evaluable and kept lossless. Lossless binary storage alone gives 0.99-fold; certified compression gives 5.35-fold over it (other tolerances, Supplementary Note 1).

### The operator symbol explains the codec effect and fixes a closed-form allocation law

At matched realized $L_\infty$ distortion, codecs still differ in Hartree-potential error. For 457 ZFP/SZ3 pairs matched within material (214 materials), the material-level Hartree-error ratio was 0.0776 under both the historical and a Nyquist-safe Poisson operator. Writing $E$ for the error energy over non-zero, Nyquist-safe modes and $S_H=W_H/E$ for the Hartree susceptibility, with $W_H=\sum_G|\Delta\rho(G)|^2/|G|^4$, each pair's ratio factors exactly as

$$
R_H=\sqrt{\frac{E_{\text{ZFP}}}{E_{\text{SZ3}}}}\,\sqrt{\frac{S_{H,\text{ZFP}}}{S_{H,\text{SZ3}}}}.
$$

Both factors favour ZFP, the susceptibility factor more strongly (Fig. 3c): frequency allocation carried a material-median 62.0% of the absolute log effect (Fig. 3d). ZFP places less error energy in the long-wavelength modes that the Hartree symbol amplifies (Fig. 3a,b).

The same symbol prescribes the allocation. For a linear operator diagonal in reciprocal space with symbol $a(G)$, the squared operator error of a density error $\delta\rho$ is $\sum_G w(G)\,|\delta\rho(G)|^2$ with weight $w=|a|^2$. Under high-rate scalar quantization, minimizing this weighted error at fixed rate gives the classical step-size law<sup>21,22</sup>

$$
\Delta_G\propto w(G)^{-1/2}.
$$

For the Hartree potential, $a=4\pi/|G|^2$, so $w\propto|G|^{-4}$ and $\Delta_G\propto|G|^2$. The rule is classical; the operator supplies the weight and the certificate. A fixed-ladder version was confirmed on 48 further crystals and a 254-material census (Supplementary Note 2).

On one density the law's action can be followed shell by shell (KCN, the material of Figs. 1a and 3e; Fig. 4). The step grows as $|G|^2$ from the exactly stored $G=0$ (Fig. 4a). Beyond $q=|G|/G_{\max}\approx0.26$ the root-mean-square reference coefficient falls below the step and quantizes to zero (Fig. 4c), so 97.5% of the bytes sit in the 10 innermost of 32 shells (Fig. 4e). Within $q\le0.25$ the Hartree error per mode stayed nearly flat across shells, the law's equal-distortion signature, whereas under uniform steps it spanned five orders of magnitude, dominated by the lowest shell as for pointwise codecs (Fig. 4d). At a decoded Hartree error of $10^{-6}$ the law certified a compression ratio of 133, against 115 for truncation at its best cutoff and at most 15.7 for ZFP, SZ3 and SPERR (Fig. 4b).

### Under equal search, the law certifies more than pointwise, QoI-preserving and Fourier-corrected codecs

We tested the law prospectively on 60 Materials Project bulk crystals and 32 NOMAD surface slabs new to the project (Methods). Three arms received the same continuous search with decode-verified certificates: the closed-form law (A1), spectral truncation at the best of 32 cutoffs (A2), and the best of ZFP, SZ3 and SPERR (A6). The Hartree contract is relative root-mean-square potential error below $\tau$.

At $\tau=10^{-6}$, the law certified a median 10.2-fold more compression than the best pointwise codec on bulk crystals (95% CI 9.13–12.09; 60/60 materials) and 18.5-fold more on slabs (15.8–23.1; 32/32) (Fig. 5a). It exceeded spectral truncation 1.32-fold (1.27–1.35; 52/60) and 1.41-fold (1.28–1.72; 27/32) (Fig. 5b). The advantage over pointwise codecs held at $10^{-4}$ and $10^{-8}$, at least 3.30-fold (Fig. 5c,d; Supplementary Note 3).

The advantage holds against compressors built to preserve derived quantities. QPET<sup>10</sup> and MGARD<sup>8</sup> received the same search and certificate on the same 92 materials. QPET bounds local quantities, so it bounded the closest one, the block average of the density (Methods); MGARD used $s=-2$, the smoothness matching the Hartree weight $|G|^{-4}$. At $\tau=10^{-6}$ the best QPET configuration read the full float64 density (SPERR host) in 60/60 bulk crystals and 26/32 slabs. The law certified 6.31-fold more than QPET on bulk crystals (95% CI 5.53–6.95; 60/60) and 9.47-fold more on slabs (8.14–12.8; 32/32), and 18.2- and 21.0-fold more than MGARD with $s=-2$ (Fig. 5e), winning in every material at all three tolerances (Supplementary Note 3). Correcting a pointwise stream in Fourier space does not recover the Hartree weight either. FFCz,<sup>16</sup> which corrects ZFP, SZ3 or SPERR reconstructions to a frequency-domain bound, received the same search and certificate. At $\tau=10^{-6}$ it certified 24/60 bulk crystals and 27/32 slabs, and in each of them the law certified more, 20.3-fold (95% CI 13.0–24.4) and 22.7-fold (18.1–27.5) (Fig. 5e).

The advantage over truncation grows at tight tolerances, to 1.59-fold (bulk) and 2.16-fold (slabs) at $10^{-8}$; at $10^{-4}$ most coefficients fall in the quantizer's dead zone, where low-rate transform-coding theory replaces the high-rate law<sup>31,32</sup> and truncation certifies more (0.79 and 0.69). Operational allocation (A3, next section) exceeded truncation in every material at every tolerance (Supplementary Note 3).

The certificate has a direct physical reading on surfaces. The work function is read from stored data as the electrostatic vacuum level minus the stored Fermi energy; with the ionic potential exact, a decoded density shifts it by $\Delta\Phi$, the planar-averaged Hartree-potential error in the vacuum. For the 27 slabs with at least 3 Å of vacuum, the law's certified streams at $\tau=10^{-6}$ moved the work function by a median 0.004 meV, against 0.34 meV for the best pointwise codec, and at every plane of every vacuum window its error was at most 0.45 meV (pointwise: up to 2.8 meV). At $\tau=10^{-4}$, $|\Delta\Phi|$ stayed below 10 meV in 27/27 slabs for the law and in 2/27 for the best pointwise codec (Fig. 5f; Supplementary Note 3).

At archive scale the advantage compounds. Under the Hartree contract every object of the archive sample was eligible at $\tau=10^{-6}$. With per-atom moments certified on the Bader basins of the decoded density and the total density written by operational allocation, the archive shrinks from 8.50 TB to an estimated 24 GB, 347-fold (95% CI 317–387), against 316-fold for the closed-form law, 232-fold for truncation and 34.6-fold for the best pointwise codec. At $\tau=10^{-4}$ it shrinks 1,371-fold, against 1,142-fold for truncation (Supplementary Note 4 and Supplementary Fig. 2).

### The law's certified streams are the cheapest to produce and fast to retrieve

Timed on the same 92 materials (Table 2; Methods), certification costs the law least, because its Hartree distortion is exact in orbit space. At $\tau=10^{-6}$ its certified search took a median 0.38 s per bulk crystal and 0.68 s per slab, about 50-fold less than for the pointwise codecs and MGARD and about 200-fold less than for QPET. At 1 Gbit s$^{-1}$ law streams delivered the usable density 16.5- and 8.2-fold sooner than the files the archives distribute.

**Table 2 | Deployment cost of certified Hartree compression at $\tau=10^{-6}$.** Medians over 60 bulk crystals / 32 slabs (P1 / P3b) at the certified points of Fig. 5, regenerated from the recorded parameters; one material per GitHub-hosted runner, single thread, each operation in a fresh process. Certified search: the arm's complete certified compression from the raw field (A6 searches all three codecs, QPET all nine configurations). Encode and decode: medians of five repetitions after a warm-up. Decode memory: peak resident set above the loaded input in units of the float64 field ($8N$ bytes); for QPET and MGARD, the codec program's peak above its footprint on a $16^3$ field. Time to field: $8\,\text{bytes}/B+\text{decode time}$ at $B=1$ Gbit s$^{-1}$. Archived file: Materials Project gzipped JSON and NOMAD CHGCAR as served; its decode is parsing to a float64 array. Paired ratios, intervals and $\tau=10^{-4}$, $10^{-8}$: Supplementary Note 3.

| codec | certified CR | stream (kB) | certified search (s) | encode (s) | decode (ms) | decode memory (× field) | time to field (ms) |
|---|---|---|---|---|---|---|---|
| closed-form law (A1) | 195 / 504 | 43.2 / 23.0 | 0.38 / 0.68 | 0.070 / 0.113 | 40 / 65 | 5.0 / 5.0 | 40 / 66 |
| operational optimum (A3) | 224 / 647 | 39.2 / 19.2 | 3.6 / 3.0 | 3.47 / 2.84 | 26 / 44 | 4.0 / 3.6 | 27 / 44 |
| best of ZFP, SZ3, SPERR (A6) | 16.0 / 23.3 | 489 / 571 | 18.1 / 32.9 | 0.033 / 0.019 | 19 / 11 | 2.0 / 2.0 | 24 / 16 |
| QPET, best of nine | 29.4 / 46.0 | 283 / 327 | 91 / 132 | 0.132 / 0.195 | 57 / 78 | 3.0 / 3.0 | 60 / 80 |
| MGARD, $s=-2$ | 10.2 / 21.0 | 783 / 656 | 17.9 / 30.5 | 0.188 / 0.317 | 189 / 309 | 3.0 / 3.0 | 194 / 315 |
| archived file | 0.55 / 0.44 | 14,719 / 32,292 | – | – | 609 / 295 | – | 745 / 543 |

### The operator metric carries the gain, and the system class sets the optimizer's share

To separate the metric from the optimizer, we built the operational optimum (A3): Lagrangian selection, per radial shell, over exact pairs of compressed bytes and operator distortion,<sup>33,34</sup> targeted directly at the decode-verified Hartree certificate. Its control (A5) runs the same machinery in the operator-blind $L_2$ metric, with the Lagrange multiplier chosen only so that the same Hartree certificate holds.

The gain ladder separates three factors (Fig. 6a). At $\tau=10^{-6}$, operator-blind transform allocation (A5) beat the best pointwise codec 5.6-fold (bulk) and 7.3-fold (slabs), the operator law (A1) added 1.89- and 2.66-fold, and operational allocation (A3) a further 1.105- and 1.222-fold.

The metric carries the gain. At $\tau=10^{-6}$, the optimum under the operator metric certified 2.12-fold more than the optimum under the blind metric on bulk crystals (95% CI 1.92–2.46; 60/60) and 3.43-fold more on slabs (2.89–4.08; 32/32) (Fig. 6b), and exceeded 1.3 at every tolerance (Supplementary Note 3).

The optimizer's share depends on the system class. At $\tau=10^{-6}$, the closed-form law was within 10.5% of the operational optimum on bulk crystals (95% CI of A3/A1 1.090–1.146), whereas on slabs operational allocation added 22% (1.138–1.359), above the declared near-optimality threshold of 1.15 (Fig. 6c). The share shrank at tighter tolerances, to 1.03 and 1.08 at $10^{-8}$. The closed-form law is therefore the encoder for bulk crystals at tight tolerances, and operational allocation the encoder for surfaces, for loose tolerances and for joint contracts.

### One stream certifies the Hartree potential and Bader charges together

A stored density usually serves more than one analysis. We fixed a joint contract and its acceptance criteria before any run (Methods): Hartree relative error below $10^{-6}$ on the final stream, and Henkelman Bader charges with an exact all-electron partition reference, maximum atomic-charge error at most $\tau_B$ and zero basin reassignment, for $\tau_B=10^{-3}$, $10^{-4}$ and $10^{-5}\,e$. Four base codecs competed: the operational Hartree encoder (R3, the A3 codec), the fixed-ladder law (J), spectral truncation (T1) and the best of ZFP, SZ3 and SPERR (GF). Each base received the same post-processors, including uniform per-basin projection, which restores each basin's charge with the additive correction of smallest $L_2$ and $L_\infty$ norm, the Euclidean counterpart of the entropy-divergence constraint satisfaction applied to velocity moments of fusion data,<sup>12</sup> and certify-then-project, which projects only when the decoded stream fails the Bader contract.

On 48 fresh bulk crystals, one stream from R3, certified for the Hartree potential at $10^{-6}$, was also certified for Bader charges with zero basin reassignment at $10^{-3}$, $10^{-4}$ and $10^{-5}\,e$ in 48/48 materials. At $10^{-4}\,e$ its joint compression ratio equalled its Hartree-only ratio (median overhead 1.000; Fig. 7d): certifying the charges added no stream bytes. It exceeded the best other base codec in 48/48 materials (median 1.317-fold, 95% CI 1.269–1.360; Fig. 7a,b). Every certified stream kept its maximum atomic-charge error at or below $\tau_B$ with no voxel reassigned (144/144 stream–tolerance pairs; Fig. 7c). Stored with its partition as a lossless basin-label map (median 11.8 kB), the archive is self-contained: R3 then kept a median compression ratio of 188 (95% CI 172–200), 10.2-fold that of the pointwise codecs, and stayed highest in 48/48 materials (Supplementary Note 5).

The Hartree certificate already carries the Bader charges under an exact partition. The unprojected stream was the best joint choice in 48/48 materials at $10^{-3}$ and $10^{-4}\,e$ and in 33/48 at $10^{-5}\,e$, whereas the pointwise streams needed uniform projection in about two of every five materials (Fig. 7e); certify-then-project applied no projection at $10^{-3}$ or $10^{-4}\,e$ (Fig. 7d). Supplementary Note 6 compares the label map with a partition-faithful all-electron reference (Supplementary Fig. 3).

### The gain is predicted before compression from the operator symbol and the reference spectrum

Whether operator-aware coding is worth deploying depends on the operator. For five linear operators of the density (gradient, Laplacian, Hartree field, Hartree potential and Gaussian smoothing with $\sigma=0.5$ Å) and the density itself as control, we compared operator-weighted allocation ($\Delta_G\propto w^{-1/2}$) with operator-blind allocation (uniform steps) at equal operator error and recorded the measured gain $G_{\text{obs}}$ as the ratio of their compressed sizes. Before any compression, we computed the predicted gain $G_{\text{pred}}$ for every material and operator from the operator symbol and the material's reference spectrum alone, with a finite-rate entropy-coded quantization model (Methods).

The predictions tracked measurements across operators. At $\tau=10^{-6}$, the median absolute log error was 0.024 over 300 bulk pairs and 0.029 over 160 slab pairs, with Spearman rank correlations of 0.978 and 0.979 (Fig. 8a); 80% of pairs were predicted within 25%, every pair of operators was ordered as predicted, and the density control gave $G_{\text{obs}}=1$. At $\tau=10^{-4}$ the Spearman correlations were 0.944 and 0.914 (Fig. 8b). Within each operator that gains, the predictor also ranked the materials (pooled Spearman 0.79–0.89; Fig. 8d–f).

The operator symbol sets which operators gain (Fig. 8c): derivative operators less than 5%, the Hartree field about 15%, the Hartree potential 2.6–3.1-fold and Gaussian smoothing an order of magnitude, each as predicted (Supplementary Note 3). The predictor is the classical coding-gain construction<sup>35,36</sup> evaluated with a physical weight and a finite-rate dead-zone model; compression-ratio prediction from data statistics is established separately.<sup>37</sup>

The principle reaches a nonlinear QoI through its linearization. To first order, the error of the PBE<sup>38</sup> exchange-correlation energy $E_{\text{xc}}$ is the inner product of the density error with the potential $v_{\text{xc}}$, whose spectral weight falls across the innermost shells about as steeply as the Hartree weight. Shell steps set by that weight certified as much as the closed-form law on bulk crystals (median ratios 0.99–1.00; 0.93–0.96 on slabs). Under an $E_{\text{xc}}$ contract of 1 or 0.1 meV per atom, the law certified 5.4- and 6.9-fold more than the best pointwise codec on bulk crystals and 2.9- and 1.9-fold more on slabs (Supplementary Note 7). A Hartree certificate does not carry $E_{\text{xc}}$ on slabs (median error 3.9 meV per atom at $10^{-6}$), so the energy needs its own contract.

## Discussion

The downstream operator enters certified compression at each stage, and each stage licenses a different decision. Qualification decides whether a tolerance can be scored at all, and a non-evaluable outcome is resolved by changing the contract, not the codec. Gain prediction decides, before compression, whether operator-aware coding is worth deploying. The system class decides the encoder. Certification decides whether the decoded object meets every requested contract, and at archive scale the Hartree-certified store of complete objects is 347-fold smaller than the public one.

Two ideas carry these decisions. The first is that the measurement contract belongs to the quantity of interest. QoI-preserving compressors make a declared quantity faithful to its reference;<sup>8–17</sup> the contract adds the algorithm that computes it and the role of each input, and these decide evaluability: changing only the role of the partition reference moved Bader eligibility from 3/50 to 50/50 materials, and changing only how basins are derived reversed the codec order in 109/185 materials at matched density error. The second is that the operator is the unit of design, for linear analyses and, through its linearization, for the exchange-correlation energy. Beyond task-based and weighted transform coding,<sup>20–23</sup> the symbol of the downstream operator, read on each material's reciprocal lattice, explains a codec effect at matched distortion, fixes a closed-form allocation, forecasts its gain and defines the certificate. The operator metric, not the optimizer, carries the gain (2.12- and 3.43-fold at equal optimization). For the same reason, compressors that preserve local quantities stay 6.3- and 9.5-fold behind and Fourier correction of a pointwise stream more than 20-fold: the Hartree weight decides where error is placed across reciprocal space, which neither a block average nor a correction after pointwise coding reproduces.

Joint certification shows how contracts compose. Several QoIs have been controlled on one stream before.<sup>11,12,15,17</sup> Here one stream meets two linear constraints at opposite scales, a global elliptic-operator norm on the reciprocal lattice and charge sums over the fixed basins of a topologically defined partition, certified by the production Bader code. The Hartree certificate already carried the Bader charges to $10^{-4}\,e$ at no stream cost, and with its partition the stream is a self-contained archive 10.2-fold smaller than the pointwise alternative. Per-atom magnetic moments certified on the basins of the decoded density composed with the charge contract in 60/62 material–tolerance pairs (Supplementary Note 4).

These results change what an electronic-structure archive must ask of a stored density: not whether it can be compressed, but which analyses it must support. The operator of each analysis then says how to store the density, and its certificate says whether the stored form suffices, jointly for the Hartree potential and Bader charges on Materials Project bulk crystals under the exact-partition Bader contract.

## Methods

### Measurement contract and QSQ

QSQ perturbs only the approximate inputs of a contract $C$. For an approximate density $\rho_m$, $\epsilon_m=\lVert\mathrm{float32}(\rho_m)-\rho_m\rVert_\infty$, and five fixed-seed perturbations $U(-\epsilon_m,+\epsilon_m)$ (seeds 20260905, 1, 2, 3, 4) are applied. The floor is $f_C=\max_k r_{C,k}$, the largest response over the five probes (for Bader charge, the maximum absolute per-atom charge change with re-derived basins), and

$$
\text{eligible}(C,\tau)\equiv f_C<\tau,\qquad \text{certified}(r,C,\tau)\equiv\text{eligible}(C,\tau)\land \Delta Q(r)<\tau .
$$

An ineligible pair is non-evaluable; an eligible pair with no certified reconstruction is not certified. For a given material, the five probes and every fresh perturbation are independent draws of the same uniform perturbation, so with exceedance probability $p$ the probability of $n$ non-exceedances followed by one exceedance is $p(1-p)^n\le n^n/(n+1)^{n+1}$ (6.70% for $n=5$), the one-sided tolerance-limit argument;<sup>39</sup> the proof and the role of independence are in Supplementary Note 1. The all-electron Bader contract used Henkelman Bader 1.05 (`-b ongrid -vac 0.001`), CHGCAR integrated over the exact $\rho_{\mathrm{AE}}=\mathrm{AECCAR0}+\mathrm{AECCAR2}$ partition. For the codec-order comparison, each material contributed at most one SZ3/SPERR pair, the one with the smallest summed absolute log mismatch.

### Hermitian-orbit representation and certificate

Densities are transformed with an orthonormal FFT. Reciprocal indices are partitioned into Hermitian orbits under $k\mapsto-k \pmod N$, one representative coefficient is stored per orbit, and $G=0$ is the only coefficient stored exactly. On even grids, a Nyquist coordinate is alias-equivalent to $\pm N/2$; for every such mode the alias choices are enumerated and the minimum $|G|^2_{\text{safe}}$ is used, so no mode receives a looser step from a sign convention. A policy assigns $\Delta_G=\alpha\,u_G$; for the closed-form law $u_G=w(G)^{-1/2}$ normalized at $G_{\max,\text{safe}}$, giving $\Delta_G=\alpha(|G|_{\text{safe}}/G_{\max,\text{safe}})^2$ for the Hartree potential. Real and imaginary parts are rounded to integers, grouped into 32 radial shells with the smallest sufficient signed integer type, and compressed with zlib level 6. Compression ratio is $8N$ divided by the complete stream bytes, headers included. Every stream is decoded and certified when the Hartree relative root-mean-square error is below $\tau$ under both the historical operator ($4\pi/|G|^2$, $G=0$ set to zero) and the Nyquist-safe operator (even-grid Nyquist planes also removed), for which

$$
\mathrm{RMS}(\Delta V_H)^2=\frac{(4\pi)^2}{N^2}\sum_{G\in\mathcal G_s}\frac{|\Delta\rho(G)|^2}{|G|^4}.
$$

For the spectral audit, ZFP and SZ3 reconstructions were matched within material on $\log_{10}$ realized $L_\infty$ (Supplementary Note 2); material-level centres are within-material medians on the log scale.

### Arms and the operational optimum

A1: closed-form law, continuous $\alpha$ bisection. A2: spectral truncation at cutoff $q_c\in\{k/32\}$, bisection per cutoff, best cutoff. A3: operational optimum, $\Delta_k=m_s u_k$ with a per-shell multiplier from a $2^{1/4}$ ladder or the shell dropped, selected by bisection on the Lagrange multiplier over each shell's exact (zlib bytes, operator distortion) curve plus a feasibility-preserving greedy polish, under both Hartree certificates with margin 0.995. A5: the same machinery with a flat prior and $L_2$ selection metric, multiplier chosen only so that the Hartree certificate holds. A6: best of ZFP, SZ3 and SPERR<sup>2–4</sup> by absolute-tolerance bisection. Bisection arms use 60 iterations in log space and report the highest-ratio evaluated point that passes the decoded certificate; A1, A2 and A6 therefore have equal search. Tolerances were $\tau\in\{10^{-4},10^{-6},10^{-8}\}$, primary $10^{-6}$.

### QoI-preserving baselines and work-function error

These analyses and the FFCz comparison follow protocols fixed before execution (Table 1) and use the A1/A6 search and the decoded Hartree certificate on P1 and P3b; the A arms are the recorded values of the law run. MGARD<sup>8</sup> was built from upstream source and run with smoothness $s=-2$; the best of $s\in\{\infty,0,-1,-2\}$ is reported in Supplementary Note 3. QPET<sup>10</sup> (authors' artifact; versions in Supplementary Note 3) bounded the block average of the density over $b^3$ blocks ($b=4,8,16$) on SZ3, HPEZ and SPERR hosts, with its absolute QoI bound as the searched parameter and its pointwise bound set to the value range so that it never binds; the best of the nine configurations is reported. FFCz<sup>16</sup> (authors' code) corrected ZFP, SZ3 and SPERR reconstructions in 18 configurations (Supplementary Note 3), searching its frequency bound; the best is reported. Evaluations that crashed inside a codec count as non-passing points; every QPET and MGARD search certified a point. For each slab, the surface normal and the vacuum window come from the reference density alone: planes whose planar-average density is below $10^{-3}$ of its maximum are vacuum, the normal is the axis with the thickest contiguous vacuum run, slabs with at least 3 Å of vacuum qualify (27 of 32), and the window is the central half of the run. $\Delta\Phi$ is the window mean of the planar-averaged error of $V_H(G)=4\pi k_e\,\rho(G)/|G|^2$, $k_e=14.399645$ eV Å: the change in the electrostatic vacuum level and, with the stored Fermi energy and the exact ionic potential, in the work function read from the stored density. The largest planar-averaged error over the window is recorded with it.

### Deployment cost

Under a protocol fixed before the run (Table 1), every certified point of A1, A3, A6, MGARD ($s=-2$) and QPET was regenerated, decoded and recertified, single-threaded, one runner per material. A streaming decoder reads law and operational streams 2.6-fold faster than the reference implementation (Supplementary Note 3).

### Archive estimate

The frame is every `chgcars/mp-<n>.json.gz` object of the open Materials Project bucket listed on 2026-09-30, minus the development set (415,289 objects, 8.4976 TB). Three hundred objects were drawn by hash rank within stored-size strata (Supplementary Note 4). Per object, QSQ ran with the five probes, the certifying writer searched the ZFP, SZ3 and SPERR ladders, and stored bytes followed the storage rule fixed with the sample. Stratified expansion estimators give the archive reduction factor $R(\tau)$, with stratified bootstrap intervals (2,000 resamples, seed 20260930). Objects that failed keep their stored size. The Hartree archive applied the same design to writers A1, A2, A3 and A6 with their equal search, the decoded Hartree certificate at $\tau\in\{10^{-4},10^{-6},10^{-8}\}$ and QSQ on the Hartree response (bootstrap seed 20261012). Every object holds a total and a magnetization density block, and both are counted: per-atom magnetic moments are certified at $10^{-2}\,\mu_\mathrm{B}$ on the Bader partition of the decoded total density, with a lossless atom-label map where that fails (Supplementary Note 4).

### Exchange-correlation contract

$E_{\text{xc}}^{\text{PBE}}$ of the stored total density is evaluated on its own grid with Fourier gradients. The contract is $|\Delta E_{\text{xc}}|<\tau_x$ per atom, $\tau_x\in\{1,0.1\}$ meV, with QSQ on the same response and the 60-step bisection with the decoded energy as predicate. The linearized allocation steps shell $s$ by $\alpha\,(W_s/W_{\max})^{-1/2}$, with $W_s$ the shell mean of $|v_{\text{xc}}(G)|^2$ and $v_{\text{xc}}$ the exact derivative of the discrete energy; flat shell steps in the same container are its control (Supplementary Note 7).

### Single-density diagnostics

Fig. 4 uses one development density (KCN, mp-676693, $84\times96\times108$ grid) and the codecs of the arms: the law codec with continuous $\alpha$ ($\Delta_G=\alpha q^2$, as A1), the same codec with uniform steps (the operator-blind arm of the gain test), the truncation codec at each of the 32 cutoffs, and ZFP, SZ3 and SPERR by absolute tolerance. Certified points use the bisection of the arms above, with decode back-off. Radial statistics use 48 equal bins in $q=|G|_{\text{safe}}/G_{\max,\text{safe}}$; the decoded error energy per mode is weighted by $|G|^{-4}$.

### Gain predictor

Part B used six operators with squared weights $w=1$ (density), $|G|^2$ (gradient), $|G|^4$ (Laplacian), $|G|^{-2}$ (Hartree field), $|G|^{-4}$ (Hartree potential) and $\exp(-\sigma^2|G|^2)$, $\sigma=0.5$ Å (Gaussian smoothing). The operator-weighted arm used $u=w^{-1/2}$ and the blind arm $u=1$; each used continuous $\alpha$ bisection on the Nyquist-safe relative error in that operator's metric (margin 0.995), every stream was decode-verified, and $G_{\text{obs}}=\text{bytes}_{\text{blind}}/\text{bytes}_{\text{opt}}$. The predictor models each real coefficient component as a zero-mean Laplacian whose variance is the reference spectral power averaged over 256 radial $|G|$ bins, quantized by rounding with ideal entropy coding, for which output entropy and mean squared error have exact closed forms. For each policy, $\alpha$ is solved for the target operator error, giving predicted payload bits $R$, and

$$
G_{\text{pred}}=\frac{F+R_{\text{blind}}/8}{F+R_{\text{opt}}/8},
$$

where $F$ is the geometry-only container size. The model includes the dead zone that the high-rate law ignores. Its form was fixed by a retrospective calibration on 12 engineering materials (Supplementary Note 8) and then tested only prospectively.

### Populations and protocol chronology

Populations were drawn under rules fixed before any candidate was downloaded and excluding every identifier (833) and reduced formula (291) used anywhere in the project. P1 (12 shakedown + 60 confirmatory) and P2 (12 engineering + 48 confirmatory, with AECCAR0 and AECCAR2) are Materials Project bulk crystals drawn by hash rank within size strata from the open S3 listing<sup>40</sup>; P3b is 32 NOMAD VASP surface slabs<sup>41</sup>, one per reduced formula and at most six per upload. Only metadata was read before the rules were fixed; no outcome was computed on any candidate (Table 1). Supplementary Note 9 details population construction and Supplementary Note 10 indexes the source files.

**Table 1 | Protocol chronology.** Commits on the public repository, in order; times in UTC.

| step | commit | time (UTC) |
|---|---|---|
| Archive-estimate protocol and sample fixed | `cb6438c` | 2026-09-30 11:02 |
| Population selection rule and exclusion set fixed | `10e7863` | 2026-10-06 14:27 |
| P1 and P2 manifests drawn | `708dd37` | 2026-10-06 15:09 |
| Law protocol (Parts A and B, criteria) fixed | `fe2e08a` | 2026-10-06 15:26 |
| P1 predictions committed | `d5fc30b` | 2026-10-06 15:32 |
| P1 run recorded | `4164519` | 2026-10-06 15:54 |
| P3b selection rule and protocol amendment fixed | `39ba728` | 2026-10-06 15:59 |
| P3b cohort drawn | `d1c1050` | 2026-10-06 16:03 |
| P3b predictions committed | `c1e6564` | 2026-10-06 16:08 |
| P3b run recorded | `eaa3267` | 2026-10-06 16:23 |
| Joint-contract protocol and criteria fixed | `8a784a4` | 2026-10-06 16:25 |
| Joint-contract engineering gates passed | `e095a0c` | 2026-10-06 16:42 |
| Joint-contract confirmation recorded | `e4d9d0b` | 2026-10-06 18:00 |
| Work-function protocol fixed | `47b110a` | 2026-10-07 09:08 |
| QoI-preserving baseline protocol fixed | `16e8890` | 2026-10-07 09:11 |
| Work-function run recorded | `4946f9f` | 2026-10-07 09:35 |
| QoI-preserving baseline run recorded | `027e69a` | 2026-10-07 13:42 |
| Self-contained joint-storage protocol fixed | `d084d4a` | 2026-10-12 03:22 |
| Self-contained joint-storage run recorded | `3ab3826` | 2026-10-12 03:59 |
| FFCz-baseline protocol fixed | `8f98f8b` | 2026-10-12 05:09 |
| Hartree-archive protocol fixed | `9959c07` | 2026-10-12 05:11 |
| Deployment-cost protocol fixed (amended after the probe) | `ef45ab2` | 2026-10-12 06:30 |
| Deployment-cost run recorded | `2ee1dab` | 2026-10-12 07:35 |
| Hartree-archive run recorded | `81ba218` | 2026-10-17 03:29 |
| FFCz-baseline run recorded | `eaf7427` | 2026-10-22 04:28 |
| Exchange-correlation and archive-writer protocols fixed | `75f091a` | 2026-10-23 16:17 |
| Exchange-correlation and archive-writer runs recorded | `534126e` | 2026-10-24 13:09 |
| Linearized exchange-correlation protocol fixed | `5e0c052` | 2026-10-24 13:23 |
| Linearized exchange-correlation run recorded | `b32e6d7` | 2026-10-24 14:05 |

### Joint contract and certify-then-project

The joint contract requires Hartree relative error below $10^{-6}$ (historical and Nyquist-safe) on the final stream and, with Henkelman Bader 1.05 (`-b ongrid -vac 0.001`, exact AECCAR0 + AECCAR2 reference), maximum atomic-charge error at most $\tau_B$ and zero basin reassignment. Bases: R3 (the A3 codec), J (fixed-ladder law), T1 (truncation ladder) and GF (ZFP, SZ3 and SPERR at $\text{abs\_tol}/\mathrm{ptp}=10^{-9}$ to $10^{-1}$, 25 points). Post-processors: none; uniform projection, which adds $d_i/N_i$ on basin $i$ to restore the stored basin sums; Hartree-aware projection, which minimizes $\lVert Hc\rVert^2/s_H+\mu\lVert c\rVert^2/s_\rho$ subject to the same sums ($\mu\in\{10^{-4},10^{-2},1\}$); and certify-then-project, which stores a one-byte flag, runs Bader on the unprojected stream and applies a projection only if that stream fails. Bytes include payload, side channel and flag. For each material, $\tau_B$ and base, the best post-processor is the one with the highest certified joint ratio, a choice every base receives. Overhead is $\text{CR}_{\text{Hartree-only}}/\text{CR}_{\text{joint}}$ for R3; utility is the R3 joint ratio over the maximum joint ratio of J, T1 and GF; both count stream bytes. Self-contained storage adds the exact-partition atom-index map, stored losslessly as xz-compressed 16-bit labels, to every base's stream (Table 1).

### Statistics

Medians and percentile 95% confidence intervals of the median come from 10,000 bootstrap resamples over materials with fixed seeds (20261006 for the law protocol, 20261007 for the joint contract). The acceptance criteria, fixed before each run, were, for the law: near-optimality median $\text{CR}_{A3}/\text{CR}_{A1}\le1.15$ with CI upper bound $\le1.20$; operator metric median $\text{CR}_{A3}/\text{CR}_{A5}>1.5$, CI lower bound $>1.35$, wins $\ge90\%$; pointwise codecs median $>4$, wins $\ge95\%$; truncation median $>1.15$, wins $\ge75\%$; prediction median $|\ln(G_{\text{pred}}/G_{\text{obs}})|\le\ln 1.25$ and Spearman $\ge0.85$ over operator–material pairs, operator ordering preserved, and $G_{\text{obs}}\in[0.90,1.11]$ in $\ge80\%$ of materials for operators with median $G_{\text{pred}}<1.05$. For the joint contract: $\ge46/48$ jointly certified; overhead median $\le1.10$ with CI upper bound $\le1.15$; utility $\ge36/48$ wins, median $>1.10$, CI lower bound $>1.00$. QSQ intervals are material-cluster bootstrap intervals. Spearman correlations are computed over operator–material pairs, excluding the density control.

## Data availability

Source densities are public. Bulk crystals are Materials Project charge densities (CHGCAR, AECCAR0, AECCAR2) from the open S3 bucket `materialsproject-parsed` (listing of 2026-10-06);<sup>40</sup> surface slabs are NOMAD VASP entries retrieved through the public NOMAD API;<sup>41</sup> the external QSQ cohort also uses AFLOW densities.<sup>42</sup> Every manifest records identifier, URL, byte count and SHA-256. Derived results, protocols and analysis scripts are in the research repository at https://github.com/stloendays/QoI. An archival release of the repository, with data, code and reproducibility manifests, will be deposited with a DOI at submission.

## Code availability

Source code for QSQ, operator-aware coding, certification and figure regeneration is available in the GitHub repository above. Its archival release and DOI are given under Data availability.

## References

1. Di, S. *et al.* A survey on error-bounded lossy compression for scientific datasets. *ACM Comput. Surv.* **57**, 1–38 (2025).
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
17. Wu, X. *et al.* Error-controlled progressive retrieval of scientific data under derivable quantities of interest. In *Proc. International Conference for High Performance Computing, Networking, Storage and Analysis (SC24)* 1–16 (IEEE, 2024).
18. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving topology in error-bounded lossy compression. *IEEE Trans. Vis. Comput. Graph.* **30**, 1302–1312 (2024).
19. Gorski, N., Liang, X., Guo, H., Yan, L. & Wang, B. A general framework for augmenting lossy compressors with topological guarantees. *IEEE Trans. Vis. Comput. Graph.* **31**, 3693–3705 (2025).
20. Shlezinger, N., Eldar, Y. C. & Rodrigues, M. R. D. Hardware-limited task-based quantization. *IEEE Trans. Signal Process.* **67**, 5223–5238 (2019).
21. Gersho, A. & Gray, R. M. *Vector Quantization and Signal Compression* (Springer, 1992).
22. Goyal, V. K. Theoretical foundations of transform coding. *IEEE Signal Process. Mag.* **18**, 9–21 (2001).
23. Watson, A. B. DCT quantization matrices visually optimized for individual images. In *Proc. SPIE* **1913**, 202–216 (1993).
24. Li, Y. *et al.* BlockMGARD: Accelerating adaptive scientific data reduction with region-of-interest error control on GPUs. Preprint at https://arxiv.org/abs/2609.00205 (2026).
25. Currie, L. A. Nomenclature in evaluation of analytical methods including detection and quantification capabilities (IUPAC Recommendations 1995). *Pure Appl. Chem.* **67**, 1699–1723 (1995).
26. Automotive Industry Action Group. *Measurement Systems Analysis Reference Manual*, 4th edn (AIAG, 2010).
27. Bader, R. F. W. *Atoms in Molecules: A Quantum Theory* (Oxford Univ. Press, 1990).
28. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. *Comput. Mater. Sci.* **36**, 354–360 (2006).
29. Tang, W., Sanville, E. & Henkelman, G. A grid-based Bader analysis algorithm without lattice bias. *J. Phys.: Condens. Matter* **21**, 084204 (2009).
30. Yu, M. & Trinkle, D. R. Accurate and efficient algorithm for Bader charge integration. *J. Chem. Phys.* **134**, 064111 (2011).
31. Mallat, S. & Falzon, F. Analysis of low bit rate image transform coding. *IEEE Trans. Signal Process.* **46**, 1027–1042 (1998).
32. Sullivan, G. J. Efficient scalar quantization of exponential and Laplacian random variables. *IEEE Trans. Inf. Theory* **42**, 1365–1374 (1996).
33. Shoham, Y. & Gersho, A. Efficient bit allocation for an arbitrary set of quantizers. *IEEE Trans. Acoust. Speech Signal Process.* **36**, 1445–1453 (1988).
34. Ortega, A. & Ramchandran, K. Rate-distortion methods for image and video compression. *IEEE Signal Process. Mag.* **15**, 23–50 (1998).
35. Huang, J. J. Y. & Schultheiss, P. M. Block quantization of correlated Gaussian random variables. *IEEE Trans. Commun. Syst.* **11**, 289–296 (1963).
36. Jayant, N. S. & Noll, P. *Digital Coding of Waveforms* (Prentice-Hall, 1984).
37. Underwood, R. *et al.* Black-box statistical prediction of lossy compression ratios for scientific data. *Int. J. High Perform. Comput. Appl.* **37**, 412–433 (2023).
38. Perdew, J. P., Burke, K. & Ernzerhof, M. Generalized gradient approximation made simple. *Phys. Rev. Lett.* **77**, 3865–3868 (1996).
39. Wilks, S. S. Determination of sample sizes for setting tolerance limits. *Ann. Math. Stat.* **12**, 91–96 (1941).
40. Jain, A. *et al.* Commentary: The Materials Project: a materials genome approach to accelerating materials innovation. *APL Mater.* **1**, 011002 (2013).
41. Draxl, C. & Scheffler, M. The NOMAD laboratory: from data sharing to artificial intelligence. *J. Phys. Mater.* **2**, 036001 (2019).
42. Curtarolo, S. *et al.* AFLOW: an automatic framework for high-throughput materials discovery. *Comput. Mater. Sci.* **58**, 218–226 (2012).

## Figure legends

**Fig. 1 | The downstream operator at each stage of certified compression.** **a**, The objects a Bader contract acts on for one material (KCN, mp-676693; ZFP at nominal relative tolerance $10^{-3}$): reference valence density (isosurface 0.60 $e\,\text{\AA}^{-3}$), its Bader basins coloured by owning atom, the decoded error $\tilde\rho-\rho$ (isosurfaces $\pm2.3\times10^{-4}\,e\,\text{\AA}^{-3}$) and the voxels whose Bader owner changes when basins are re-derived on $\tilde\rho$. **b**, The workflow. A contract declares the quantity of interest $Q$, the downstream algorithm, the tolerance $\tau$ and which inputs are exact or approximate. Qualification applies probes $\delta_k$ to the approximate inputs and records the stability floor $f_C=\max_k|\Delta Q_k|$; allocation and prediction read the operator symbol $a(G)$; certification re-runs each analysis on the decoded field. Outcomes: certified, not certified and non-evaluable.

**Fig. 2 | The five-probe QSQ screen stratifies fresh downstream numerical risk.** **a**, Stability floor of each of the 254 development materials against the fraction of its 59 fresh perturbations whose re-derived Bader response reaches $\tau=10^{-3}\,e$ (dashed line); admitted (navy) and rejected (red) materials. **b**, Finite-panel admission bound $p(1-p)^5$ for independent probes, with each material at its fresh exceedance fraction. **c**, No-pass risk of eligible and rejected material–codec pairs after completing equal tight settings for every material (762 decisions per threshold). **d**, Fresh exceedance risk of admitted and rejected materials at $\tau=10^{-4}$, $10^{-3}$ and $10^{-2}\,e$. Intervals are material-cluster bootstrap 95% CIs.

**Fig. 3 | The Hartree operator's spectral weight explains the codec effect at matched distortion.** **a**, Radial reconstruction-error spectra of 457 within-material ZFP/SZ3 pairs matched on realized $L_\infty$ (214 materials): medians of non-zero, Nyquist-safe error-energy fractions with pairwise interquartile ribbons. **b**, The same spectra weighted by $|G|^{-4}$. **c**, Material-level centres and bootstrap 95% CIs of the spectral-energy factor, the Hartree-susceptibility factor and the Hartree-error ratio. **d**, Share of the absolute log codec effect carried by the susceptibility factor. **e**, One matched pair (KCN, mp-676693): decoded density error at one isolevel and the Hartree-potential error for ZFP and SZ3.

**Fig. 4 | The operator symbol sets where the step, the error and the bytes go.** One density (KCN, mp-676693) and the Hartree potential; every stream is decoded and recertified. **a**, Quantization step $\Delta_G$ on the reciprocal plane through $G=0$ spanned by $\mathbf{b}_1$ and $\mathbf{b}_2$ for the closed-form law, uniform steps and spectral truncation at its best cutoff, each at its certified point for $\tau=10^{-6}$; $G=0$ (cross) is stored exactly. **b**, Compression ratio against decoded Hartree relative error; truncation is the lower envelope over 32 cutoffs; open circles, certified points at $10^{-4}$, $10^{-6}$ and $10^{-8}$. **c**, Root-mean-square reference coefficient and the step of each policy per radial bin, $q=|G|/G_{\max}$, at $10^{-6}$. **d**, Hartree error per mode relative to its all-mode mean, per radial bin, at $10^{-6}$. **e**, Compressed bytes per radial shell at $10^{-6}$.

**Fig. 5 | Under equal search, the closed-form law certifies more than pointwise, QoI-preserving and Fourier-corrected codecs and preserves slab work functions.** 60 new bulk crystals (P1, circles) and 32 new surface slabs (P3b, triangles); every stream is decoded and certified under the Hartree contract, and every arm receives equal continuous search. **a**, Certified compression ratio (CR) of the law (A1) against the best of ZFP, SZ3 and SPERR (A6) at Hartree relative error $10^{-6}$. **b**, A1 against spectral truncation (A2) at $10^{-6}$. **c**, Median ratios A1/A6 and A1/A2 with bootstrap 95% CIs at $10^{-4}$, $10^{-6}$ and $10^{-8}$. **d**, Certified CR against tolerance: median (line) and interquartile range (band). **e**, A1 against QPET bounding a block average of the density (best of nine configurations), MGARD with smoothness $s=-2$ and FFCz (best of 18 configurations, materials it certified) at $10^{-6}$. **f**, Work-function error $|\Delta\Phi|$ of the certified streams for the 27 slabs with a vacuum region at $10^{-4}$ and $10^{-6}$; bars, medians. Lines in **a**, **b** and **e** mark ratios 1 and 10. A3, operational optimum; A5, operator-blind rate–distortion optimum.

**Fig. 6 | The gain ladder separates transform coding, the operator weight and the optimizer.** Cohorts as in Fig. 5. **a**, Certified CR at a Hartree tolerance of $10^{-6}$ per material (thin lines) and median (bold) along the arms: best pointwise codec (A6), operator-blind rate–distortion optimum (A5), closed-form law (A1) and operational optimum in the operator metric (A3); labels give the median per-material ratio between rungs. **b**, A3/A5 per material at three tolerances. **c**, A3/A1 per material at three tolerances; dashed line, near-optimality threshold 1.15. Bars, medians; whiskers, bootstrap 95% CIs.

**Fig. 7 | One operator-aware stream certifies the Hartree potential and Bader charges together.** 48 new bulk crystals (P2). Joint contract: Hartree relative error below $10^{-6}$ and Henkelman Bader charges with an exact all-electron partition reference, error at most $\tau_B$ and no basin reassignment. **a**, Joint compression ratio of the operational Hartree encoder (R3) against the best other base codec per material at $\tau_B=10^{-4}\,e$, coloured by that base. **b**, Joint CR at $\tau_B=10^{-4}\,e$ for each base codec at its best post-processor: R3, fixed-ladder law (J), spectral truncation (T1) and pointwise codecs (GF). **c**, Maximum atomic-charge error of the certified R3 stream per material at each $\tau_B$ (red bars, $\tau_B$); zero errors are drawn on the dashed floor. **d**, Joint overhead (Hartree-only over joint CR) of R3 at each $\tau_B$, with the number of certify-then-project decisions that applied a projection. **e**, Post-processor that gave each base its best joint stream at each $\tau_B$.

**Fig. 8 | The gain of operator-aware allocation is predicted before compression.** Five operators (gradient, Laplacian, Hartree field, Hartree potential, Gaussian smoothing with $\sigma=0.5$ Å) on 60 new bulk crystals (circles) and 32 new surface slabs (triangles); predictions were committed before any compression run. **a**, Predicted against measured gain at $\tau=10^{-6}$ for 300 bulk and 160 slab material–operator pairs; line, identity; band, ±25%. **b**, The same at $\tau=10^{-4}$. **c**, Per-operator medians at $10^{-6}$, predicted (open) and measured (filled), ordered by predicted gain, with the density control and the null-gain band [0.90, 1.11] (shaded). **d–f**, Within-operator ranking at $10^{-6}$ over the 92 materials for the Hartree field, the Hartree potential and Gaussian smoothing.
