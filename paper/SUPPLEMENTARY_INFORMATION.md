# Supplementary Information

## The downstream operator qualifies, predicts and shapes the certified compression of electronic densities

This Supplementary Information (SI) holds the evidence that the main text cites but does not display. Every number is copied from, or rounded from, the committed repository file named in the note; Supplementary Note 8 lists those files with the commit that last changed them. Notation follows the main text: $\tau$ is the Hartree relative root-mean-square potential tolerance, $\tau_B$ the Bader charge tolerance, A0–A6 the arms of the law protocol, R3, J, T1 and GF the base codecs of the joint contract.

Contents:

- Supplementary Note 1. QSQ validations
- Supplementary Note 2. Hartree mechanism, frozen-ladder QOAC-H confirmation, census and strongest baselines
- Supplementary Note 3. Bader contracts under an exact partition: basin projection, partition transcription and storage
- Supplementary Note 4. Joint certification: engineering cohort and per-tolerance description
- Supplementary Note 5. Law protocol tables per tolerance and per operator
- Supplementary Note 6. Gain-predictor calibration
- Supplementary Note 7. Population construction
- Supplementary Note 8. Source files
- Supplementary Fig. 1. Bader storage contracts on real materials


## Supplementary Note 1 — QSQ validations

### 1.1 Cohorts and denominators

The development benchmark contains 254 electronic-density fields (186 Materials Project bulk crystals and 68 NOMAD slabs) and 6,343 retained ZFP, SZ3 and SPERR reconstruction rows. The QSQ stability universe has 319 systems: the 254 development systems, 37 external AFLOW bulk systems and 28 external NOMAD vacuum-containing 2D systems. The external stability set (65 records) is distinct from the 63-system external confirmatory cohort (1,689 retained rows; 0 material-level pipeline failures; 0 codec-bound violations; 3 recorded row-level Bader-solver failures affecting two materials).

### 1.2 Definition and probe design

For the self-partitioned Bader contract the density is the sole approximate input. With $\epsilon_m=\lVert\mathrm{float32}(\rho_m)-\rho_m\rVert_\infty$, five uniform perturbations $U(-\epsilon_m,+\epsilon_m)$ with seeds $\{20260905,1,2,3,4\}$ are applied, basins are re-derived, and

$$
f_m=\max_s\max_a |Q_a(\rho_m+\delta_{m,s})-Q_a(\rho_m)|,\qquad \text{eligible}\iff f_m<\tau .
$$

For a fixed $\tau$, probing may stop at the earliest response $\ge\tau$; this exact sequential rule reproduced 254/254 development classifications at $10^{-3}\,e$ while reducing the mean number of probe solves from 5.000 to 3.335.

The probe must excite the downstream failure mode. In an 18-material calibration panel, an order-preserving float32 round trip produced a median of 82 exact neighbouring ties and reassigned zero voxels in 9/18 systems; the non-order-preserving QSQ probe produced no exact ties and reassigned zero voxels in 2/18. Across five seeds the per-material floor span had a median of 0.47 decades (maximum 2.4); a single-seed verdict changed across seeds in 3/18, 2/18 and 1/18 materials at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$. Over a ×0.1 to ×10 amplitude sweep the floor changed by a median of 0.76 decades (P10 0.00, P90 2.02). Across the 254 development materials the five-seed floor is a median of about $1.6\times10^{4}$ times the round-trip response, and the five-seed maximum changes eligibility relative to a single seed for 35, 17 and 2 of 319 systems at the three thresholds. Across the 319-system universe the screen rejects 79.9%, 41.4% and 9.7% at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$ (development only: 81.9%, 43.7%, 9.8%). One extreme response (`aflow-Al8Cu4U1_ICSD_601801`) is a permutation of symmetry-equivalent Al basins and is recorded as basin relabelling.

### 1.3 Prospective test

The five-seed gate, thresholds and amplitudes were fixed before 59 fresh perturbations per material (labels 10000–10058) were run; all 14,986 trials produced valid outcomes.

| $\tau_B$ ($e$) | admitted | qualified: exceedances / trials (risk; cluster 95% CI) | rejected: exceedances / trials (risk; cluster 95% CI) | materials with any exceedance (qualified / rejected) | risk ratio |
|---:|---:|---|---|---|---:|
| $10^{-4}$ | 46/254 | 109/2,714 (4.016%; 1.548–7.406%) | 10,669/12,272 (86.938%; 83.475–90.165%) | 15/46 / 208/208 | 21.65 |
| $10^{-3}$ | 143/254 | 135/8,437 (1.600%; 0.782–2.596%) | 5,326/6,549 (81.325%; 75.981–86.257%) | 20/143 / 110/111 | 50.83 |
| $10^{-2}$ | 229/254 | 20/13,511 (0.148%; 0.000–0.377%) | 1,174/1,475 (79.593%; 66.983–90.712%) | 2/229 / 24/25 | 537.69 |

The same 59 response vectors serve all three thresholds. A material with zero exceedances in 59 valid draws has a one-sided 95% exact per-cell upper bound of about 4.95%.

### 1.4 Equal-search control and three-state reclassification

Completing the same four tight settings for every material added 1,332/1,332 successful reconstructions. The fraction of material–codec pairs with no passing reconstruction was 10.9% (qualified) versus 79.3% (rejected) at $10^{-4}\,e$, 3.3% versus 66.4% (20.34-fold) at $10^{-3}\,e$, and 0.0% versus 68.0% at $10^{-2}\,e$. On the record as built (762 material–codec decisions per threshold), 518/533 (97.2%), 296/310 (95.5%) and 61/108 (56.5%) naive failures fall on non-evaluable pairs at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$; at $10^{-4}\,e$, 106/229 (46.3%) naive passes also fall on non-evaluable pairs.

### 1.5 Finite-panel admission bound and exchangeability

Let $X_k=\mathbf{1}[r_k\ge\tau]$. Admission means $X_1=\cdots=X_n=0$; the event of interest is admission followed by $X_{n+1}=1$. Under independent, identically distributed draws *conditional on each material–contract pair* with exceedance probability $p$, its probability is $p(1-p)^n$. Maximizing over $p\in[0,1]$ yields

$
\Pr(X_1=\cdots=X_n=0,\,X_{n+1}=1)\le\max_{0\le p\le 1}p(1-p)^n=\frac{n^n}{(n+1)^{n+1}},
$

with the maximum at $p=1/(n+1)$. The same inequality holds after averaging over materials with heterogeneous $p$, **provided conditional independence holds within each pair**. It does not follow from exchangeability alone. For any finite exchangeable panel, symmetry instead gives

$
\Pr(X_1=\cdots=X_n=0,\,X_{n+1}=1)=\frac{\Pr(\sum_{k=1}^{n+1}X_k=1)}{n+1}\le\frac1{n+1}.
$

This weaker bound is sharp: exactly one exceedance uniformly positioned among $n+1$ draws is exchangeable and attains $1/(n+1)$. Neither inequality bounds $\Pr(X_{n+1}=1\mid\mathrm{admitted})$ or the error of a codec reconstruction, which is not sampled by the same perturbation mechanism. Wilks' order-statistic result (main-text ref. 37) motivates the independent-sampling setting, rather than a guarantee from unrestricted exchangeability.

| panel size $n$ | 5 | 10 | 19 | 37 |
|---:|---:|---:|---:|---:|
| conditional-i.i.d. upper bound | 6.70% | 3.50% | 1.89% | 0.98% |
| finite-exchangeability upper bound | 16.67% | 9.09% | 5.00% | 2.63% |

| $\tau_B$ ($e$) | frozen panel: joint rate (events) | conditional risk among admitted | coverage | independent panel: joint rate (events) | conditional risk | coverage |
|---:|---:|---:|---:|---:|---:|---:|
| $10^{-4}$ | 0.727% (109) | 4.016% | 46/254 | 0.928% (139) | 5.013% | 47/254 |
| $10^{-3}$ | 0.901% (135) | 1.600% | 143/254 | 0.721% (108) | 1.317% | 139/254 |
| $10^{-2}$ | 0.133% (20) | 0.148% | 229/254 | 0.207% (31) | 0.228% | 230/254 |

The frozen seeds are shared by all materials, so the pooled fraction of fresh responses above the frozen floor (19.08%; 2,859/14,986; cluster CI 17.16–21.01%) is one realization. A recomputation declared before any probe was evaluated (2,794 Bader solves, all successful) reproduced the frozen floor in 252/254 materials with unchanged eligibility in 254/254; with streams drawn independently per material, 16.52% of fresh responses (2,475/14,986; 95% CI 14.74–18.39%) exceeded the five-probe maximum, consistent with the exchangeable value 1/6. Eligibility under the independent panel agreed with the frozen panel in 237/254, 242/254 and 253/254 materials ($\kappa$ = 0.776, 0.904, 0.977).

### 1.6 Evaluability belongs to the contract (all-electron reference)

Of 53 development materials with published CHGCAR, AECCAR0 and AECCAR2, 50 were analyzable (three had non-finite AECCAR0). With Henkelman Bader 1.05 (on-grid, vacuum threshold 0.001) and basins of $\rho_{\mathrm{AE}}=\mathrm{AECCAR0}+\mathrm{AECCAR2}$:

| contract | $10^{-4}\,e$ | $10^{-3}\,e$ | $10^{-2}\,e$ |
|---|---:|---:|---:|
| charge field approximate, partition reference exact | 50/50 | 50/50 | 50/50 |
| both approximate | 0/50 | 3/50 | 17/50 |
| partition reference approximate, charge field exact | 0/50 | 3/50 | 17/50 |

The material-median ratio of the partition-only floor to the joint floor was 1.000; every material had a partition-only floor at least 90% of the joint floor; median basin-reassignment fractions were 0.0196262 for both contracts.

### 1.7 Implementation transfer

On a deterministic 24-system panel (bulk and slab; four floor bands), independent Henkelman on-grid analysis reproduced QSQ eligibility in 24/24 systems at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$ ($\kappa=1.000$ at each) with floor Spearman $\rho=0.995$; the near-grid variant agreed in 82.6%, 83.3% and 95.8% ($\rho=0.754$). A separate study (1,560/1,560 rows) gave a median Henkelman/BaderKit on-grid response ratio of 1.00 (IQR about 0.92–1.005).

### 1.8 A second topology-sensitive QoI: grid-local density extrema

A voxel is a strict local maximum (minimum) when it exceeds (is below) all 26 periodic neighbours. All 16,256 perturbation evaluations completed. Requiring an identical maximum set across the five probes admits 118/254 materials. Prospectively, 0/6,962 fresh trials on qualified materials changed the number of maxima versus 6,444/8,024 (80.31%; 73.91–86.52%) on rejected materials; maximum-set changes were 3/6,962 versus 7,509/8,024 (93.58%). Eligibility agreement with Bader at $10^{-3}\,e$ was 56.3% (75 both, 68 Bader only, 43 extrema only, 68 neither; $\kappa=0.1337$, 0.0164–0.2542); floor Spearman 0.1389 (0.0280–0.2554). On 6,293 scored reconstructions, 908 (14.43%) preserved the maximum count while failing the Bader $10^{-3}\,e$ contract and 655 (10.41%) changed it while passing.

### 1.9 External cohort

The frozen rules applied without retuning to 63 external systems admitted 16, 42 and 57 at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$. Median best-certified compression ratios were about 13.0× (ZFP), 12.1× (SZ3) and 5.2× (SPERR) at $10^{-4}\,e$; 18.8× (ZFP and SZ3) and 6.4× (SPERR) at $10^{-3}\,e$; and 65.9× (SZ3), 40.6× (ZFP) and 10.8× (SPERR) at $10^{-2}\,e$. In development, SZ3 led at $10^{-2}\,e$ (bulk 51.8× [47.7, 60.3]; slab 67.8× [59.6, 70.6]) ahead of ZFP (30.0×; 40.5×) and SPERR (11.5×; 8.1×).

### 1.10 Certifying writer

The writer runs QSQ, leaves non-evaluable fields uncompressed, bisects each codec's ladder for eligible fields and returns the best certified reconstruction it evaluated, with its certificate. The adoption rule (fewest solves among multi-codec policies with at least 0.98 of oracle archive compression and at most 2% misses at $10^{-3}\,e$) was fixed before any outcome.

| $\tau_B$ ($e$) | eligible | policy | archive CR | oracle CR | fraction of oracle [95% CI] | misses | solves per eligible material |
|---:|---:|---|---:|---:|---|---:|---:|
| $10^{-4}$ | 46 | BISECT | 8.45 | 8.47 | 0.9976 [0.9918, 1.0000] | 0/46 | 16.7 |
| $10^{-3}$ | 143 | BISECT | 14.90 | 15.13 | 0.9848 [0.9695, 0.9959] | 0/143 | 16.7 |
| $10^{-2}$ | 229 | BISECT | 24.55 | 24.79 | 0.9901 [0.9698, 0.9982] | 0/227 | 15.9 |

The exhaustive oracle costs 38.5, 37.0 and 32.2 solves per eligible material. The best single-codec writer retained at most 0.840 of the oracle at $10^{-3}\,e$. Exact sequential QSQ lowers mean end-to-end cost over all 254 materials from 7.93 to 4.84, 12.00 to 10.34 and 14.91 to 14.54 solves at the three thresholds, with unchanged outputs.

### 1.11 Further QSQ analyses

- **Floor-scale regime.** At $10^{-4}\,e$ the median certified Bader error is 1.09 (ZFP), 1.33 (SZ3) and 1.23 (SPERR) times the QSQ floor (P90 3.25, 2.86, 3.20); at $10^{-3}\,e$, 2.78–3.55; at $10^{-2}\,e$, 10.7–14.6.
- **Chemical direction.** Five outcome-blind GaN and RuO₂ slab pairs passed a two-implementation source-reference gate; all 60 compressed sign decisions preserved the reference sign, with QSQ at $10^{-3}\,e$ retaining 36/60 (216/216 solver cells).
- **Codec-shaped probes.** Material-median $\log_{10}(f^c_m/f_m)$ was −0.196 (ZFP), −0.000 (SZ3) and −0.027 (SPERR); iid–codec-shaped eligibility agreement at $10^{-3}\,e$ was 0.902, 0.937 and 0.937, and codec-shaped floors did not improve prediction of fresh risk (ZFP Spearman 0.549 iid versus 0.420).
- **Continuous risk.** Models of $\log_{10}(f_m/\tau)$ reduced held-out Brier score (best logistic 0.0412, isotonic 0.0464, binary gate 0.0651; 44,958 trial–threshold outcomes); under a 2% risk contract at $10^{-3}\,e$ isotonic admission was 115/254 materials against 143/254 for the binary gate, so the binary rule is retained for coverage.
- **Reference-density descriptors.** The fraction of basin-boundary neighbour gaps below the probe scale correlates with $\log_{10} f_m$ (Spearman 0.554, 0.463–0.639); a ridge model reached held-out external $R^2=0.134$, so the floor is measured directly.
- **Operator controls.** Among 3,205 reconstructions with $|\Delta N_e|<10^{-4}\,e$, 1,383 (43.15%) had Bader error $\ge10^{-3}\,e$. Hartree error scales with realized $L_\infty$ with pooled log–log slope 1.02 (6,270 gate-passing rows; median material $R^2$ 0.994–0.997); only 32.4% of Bader ladders are strictly monotone.


### 1.12 Archive estimate (Materials Project charge-density archive)

**Frame and sample.**
- **Protocol.** Frozen at `cb6438c` (2026-09-30) before any sampled density was read.
- **Frame.** 415,289 objects, 8.4976 TB as gzipped JSON.
- **Sample.** Stratified, 300 objects: 30 per stored-size decile D01–D09, with the top decile split 15/10/5 at 80 and 150 MB.

**Storage rule at τ.**
- Certified reconstruction (certifying writer over the ZFP, SZ3 and SPERR ladders) when the contract is eligible and a rung is certified.
- Lossless float64 + zlib otherwise.
- The current gzipped size if the object failed.

**Estimators.** Stratified expansion, with stratified bootstrap intervals (2,000 resamples, seed 20260930).

**Execution.**
- A laptop completed 243 objects.
- The other 57 exceeded its memory and ran on GitHub-hosted runners. Before that, five laptop objects were rerun on the cloud runners to check consistency between the two platforms: every eligibility, certification decision, writer choice, compressed size, floor and probe matched; the only differences were four Bader errors at never-certifiable coarse rungs (0.067–0.93 e).
- 293 of 300 objects completed. The 7 failures (6 lost runners, 1 time limit) keep their stored size.
- Platform, consistency decision and reruns are recorded in the repository (WP-F `DEVIATIONS.md` 6–13).

| $\tau$ ($e$) | $R$ vs gzipped JSON [95% CI] | saving (TB) | $R$ vs float64 | $R$ vs lossless float64 [95% CI] | non-evaluable, objects [95% CI] | non-evaluable, bytes |
|---|---|---|---|---|---|---|
| $10^{-4}$ | 2.36 [2.19, 2.58] | 4.90 | 1.45 | 1.27 [1.19, 1.38] | 74.0% [69.0, 78.7] | 72.2% |
| $10^{-3}$ | 4.37 [3.64, 5.46] | 6.55 | 3.04 | 2.66 [2.21, 3.27] | 35.9% [30.4, 41.6] | 32.8% |
| $10^{-2}$ | 8.99 [6.45, 13.42] | 7.55 | 8.97 | 7.87 [5.61, 12.10] | 11.7% [8.2, 15.5] | 11.0% |

**Attribution of archive gain.** Changing gzipped JSON to lossless float64 + zlib alone gives a 2.00× archive-level gain; the separate "vs lossless" column reports the benefit of QSQ-gated, Bader-certified ZFP/SZ3/SPERR compression. No operator-aware Fourier codec was run in this archive sampling test. The two factors are estimated against explicit format comparators and should not be read as measurements of the Fourier law's archive-scale performance.

**Prospective check of the certifying writer** (D01–D09 full ladders; 0 misses at every τ):

| $\tau$ ($e$) | eligible objects with a certifiable rung | fraction of oracle archive compression |
|---|---|---|
| $10^{-4}$ | 64 | 0.982 |
| $10^{-3}$ | 166 | 0.953 |
| $10^{-2}$ | 232 | 0.931 |


## Supplementary Note 2 — Hartree mechanism, frozen-ladder QOAC-H confirmation, census and strongest baselines

### 2.1 Matched-distortion comparison

At equal nominal tolerance, ZFP's median realized $L_\infty$ is 0.170 times that of SZ3 and of SPERR; SZ3 and SPERR are about matched (1.00). Within-material matching on $\log_{10}L_\infty$ (0.10-dex caliper, without replacement) gives 457 ZFP–SZ3 pairs (214 materials), 465 ZFP–SPERR pairs (206) and 1,848 SZ3–SPERR pairs (254). Matched re-derived Bader-error ratios are 0.557 (ZFP/SZ3; 0.525–0.598), 0.601 (ZFP/SPERR; 0.534–0.662) and 1.033 (SZ3/SPERR; 0.976–1.072), with the direction preserved across calipers of 0.05–0.30 dex.

### 2.2 Spectral audit of the Hartree effect

The 914 reconstructions of the 457 ZFP–SZ3 pairs were regenerated and each reproduced its stored $L_\infty$ and Hartree error. The reference matched-pair Hartree centre is 0.0776220566, reproduced at 0.0776220566; under the Nyquist-safe operator (even-grid Nyquist planes and $G=0$ removed) it is 0.0776219202. The largest relative discrepancy between real-space and Fourier-space Hartree RMS is $1.296\times10^{-15}$. With $E=\sum_{\mathcal G_s}|\Delta\rho(G)|^2$, $W_H=\sum_{\mathcal G_s}|\Delta\rho(G)|^2/|G|^4$ and $S_H=W_H/E$, each pair's ratio factors exactly into $\sqrt{E_{\text{ZFP}}/E_{\text{SZ3}}}\sqrt{S_{H,\text{ZFP}}/S_{H,\text{SZ3}}}$; the separately aggregated centres are 0.375963 and 0.202683, and susceptibility carries a material-median 62.0% of the absolute log effect. In 99.5% of materials ZFP has the lower spectral Hartree susceptibility, in 98.1% the higher spectral centroid and in 99.1% the lower low-$G$ error fraction ($q=|G|/G_{\max}\le0.25$); the material-level low-$G$ fraction ratio is 0.416.

### 2.3 Frozen-ladder QOAC-H

QOAC-H implements $\Delta_G=\alpha(|G|_{\text{safe}}/G_{\max,\text{safe}})^2$ on the Hermitian-orbit representation (main-text Methods) with a frozen 25-point ladder $\alpha/\mathrm{ptp}(\rho)\in[10^{-7},10^{1}]$; it is arm A0 of the law protocol and base J of the joint contract. Maximum imaginary leakage in the engineering audit was $2.47\times10^{-12}$ and maximum mean-density deviation $3.98\times10^{-13}$.

**Mechanism ablation (12 engineering materials).** At matched serialized storage, exponent 2 gave lower Hartree error than exponent 0 in 12/12 materials; median error ratio 0.0767117.

**Disjoint confirmation (48 materials, 24 bulk and 24 slab; ladder search for every arm).** Selected by size stratification and a fixed SHA-256 rule after excluding the engineering materials; 1,200 settings with zero failures. QOAC-H beat each material's best certified ZFP, SZ3 or SPERR result in 48/48 materials (Wilson 95% interval 0.926–1.000), median compression-ratio ratio 15.016 (bootstrap 95% CI 11.204–21.461); bulk 11.203, slab 25.699. Every selected row also passed the Nyquist-safe guardrail.

**Census (254 development materials; 6,350/6,350 settings, zero failures; ladder search).**

| $\tau$ | QSQ eligible | comparable | wins | median ratio | P05 | minimum | bulk median | slab median |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $10^{-8}$ | 193 | 107 | 107/107 | 4.324 | 1.507 | 1.222 | 2.799 | 6.400 |
| $10^{-7}$ | 254 | 204 | 204/204 | 6.911 | 2.239 | 1.461 | 5.139 | 16.263 |
| $10^{-6}$ | 254 | 253 | 253/253 | 12.463 | 4.459 | 2.444 | 10.960 | 27.733 |
| $10^{-5}$ | 254 | 254 | 254/254 | 14.749 | 5.575 | 3.068 | 12.908 | 30.879 |
| $10^{-4}$ | 254 | 254 | 254/254 | 14.017 | 4.348 | 1.707 | 11.467 | 21.384 |
| $10^{-3}$ | 254 | 254 | 254/254 | 7.593 | 1.953 | 1.032 | 7.335 | 7.686 |

### 2.4 Strongest baselines (48 confirmatory materials; protocol frozen before the run)

Certificate as in the confirmation (historical and Nyquist-safe Hartree relative error below $10^{-6}$); zero failures in every arm (T1 21,600 rows, MGARD 3,600, stored $V_H$ 7,200). Search rule: QOAC-H frozen 25-point ladder; T1 ladder per cutoff; MGARD best of $s=\infty,0,-1$; stored $V_H$ by ZFP, SZ3 and SPERR on the potential, which changes the contract.

| arm | median certified CR | QOAC-H / arm: wins, median (95% CI) |
|---|---:|---|
| QOAC-H (frozen ladder) | 383 | — |
| T1 spectral truncation | 233 | 45/48, 1.564 (1.376–1.622); minimum 0.843 |
| ZFP/SZ3/SPERR (frozen ladders) | 22.1 | 48/48, 15.0 |
| MGARD ($s=-1$ selected in 36/48) | 16.0 | 48/48, 19.4 (16.4–24.0) |
| stored $V_H$ | — | 48/48, 19.4 (16.5–21.2) |

T1 was the best new baseline in 48/48 materials (selected cutoffs $q_c$ = 0.30 in 18, 0.15 in 17, 0.20 in 9, 0.50 in 4); uniform Fourier quantization ($q_c=1$) reached median CR 87.8. Median density $L_\infty$ and RMSE of the certified streams were 1.89 and 0.096 for QOAC-H and 2.82 and 0.148 for T1. These ladder-searched ratios and the equal-search ratios of the main text (A1/A6, A1/A2) answer different questions and are reported separately.


## Supplementary Note 3 — Bader contracts under an exact partition

### 3.1 Basin-sum projection after generic compression (38-material holdout)

With the AECCAR partition reference held exact, the decoded CHGCAR is corrected by the uniform per-basin shift that restores each stored basin sum, the minimum-$L_2$ and minimum-$L_\infty$ correction for disjoint basins, following constraint-satisfaction post-processing (main-text ref. 12). An auxiliary density budget, $L_\infty(P)\le\kappa\,\epsilon^{G1}_m$, where $\epsilon^{G1}_m$ is the realized $L_\infty$ of the best frozen generic Bader-certified row, prevents arbitrary compression followed by projection; $\kappa=4$ was fixed on 12 engineering materials (11/12 wins, median 1.782; maximum side channel 0.7117%).

On the frozen 38-material holdout ($\tau_B=10^{-3}\,e$): 38/38 analyzable with zero pipeline failures; maximum Bader error 0.0 $e$; zero basin reassignment in 38/38; 34/38 wins over the best frozen generic Bader-certified baseline; median compression-ratio ratio 1.865 (bootstrap 95% CI 1.759–1.985); P05 0.999, minimum 0.997; maximum side-channel fraction 0.999%; median $L_\infty$ ratio 3.09.

### 3.2 Transcription of the Henkelman partition (12 fresh P2 engineering materials)

Henkelman Bader 1.05 (`-b ongrid -vac 0.001`), exact CHGCAR, reference AECCAR0 + AECCAR2. The partition (volnum) was identical voxel for voxel in 11/11 materials with Gate 0 output (0 mismatching voxels); maxima 3,339/3,339 matched; every reference field was regular (0 violations of R1 and R2); the atom map was identical in 9/11 (minimum voxel agreement 97.9%); the literal transcription (run for at most 400,000 points) was identical in 3/3. For one material (mp-2302539) the comparison code exceeded memory (a 74 GiB pairwise maxima array); its arms ran normally.

### 3.3 Storing the partition (Supplementary Fig. 1)

The main-text 48-material joint test assumes the exact all-electron partition is already available, so its compression ratios and unity *incremental* overhead exclude the reference partition's storage. When the partition must travel with the reconstructed density, a self-contained contract can instead store a lossless basin-label map, or compress AECCAR with a correction that recovers the identical Henkelman partition. The following 12-material engineering test quantifies these *partition representations*, not end-to-end total byte savings for all 48 confirmed crystals.

| arm | zero reassignment | max Bader error ($e$) | median side / base | median total / label map |
|---|---:|---:|---:|---:|
| A2, relative bound $10^{-3}$ | 12/12 | 0 | 0.057 | 17.3 |
| A2, $10^{-2}$ | 12/12 | 0 | 0.33 | 16.3 |
| A2, $5\times10^{-2}$ | 12/12 | 0 | 1.63 | 27.1 |
| A1, $10^{-3}$ | 12/12 | 0 | 0.28 | 21.1 |
| A1, $10^{-2}$ | 12/12 | 0 | 1.35 | 29.5 |
| A1, $5\times10^{-2}$ | 12/12 | 0 | 5.20 | 56.9 |

Before correction the base quantizer alone reassigns a median 45–91% of voxels; after correction no voxel is reassigned. The label map round-trips exactly in 12/12 materials, charges recomputed from it match the binary in 12/12 (maximum difference $5.0\times10^{-7}\,e$), and its median size is 12.9 kB (atom map) and 21.8 kB (volnum map). For analyses requiring only charges in the fixed basins, the natural self-contained representation is a compressed CHGCAR stream plus a lossless basin-label map (the tested partition-faithful AECCAR representations require at least about 16-fold the label-map bytes in this engineering cohort). A projection can be added when the decoded basin sums miss $\tau_B$; the partition-faithful AECCAR representation serves users who need a partition-defining density field. The 48-material test did not measure these combined self-contained bytes, and a basin-label map alone does not establish robustness to recomputing the basin topology from a perturbed partition-defining density.

**Supplementary Fig. 1 | Bader storage contracts on real materials.** **a**, Total stored bytes of the partition-faithful AECCAR arms (A1, A2 at relative bounds $10^{-3}$, $10^{-2}$ and $5\times10^{-2}$) divided by the bytes of the lossless atom label map, per material (12 fresh P2 engineering materials; bar, median; medians 16.3–56.9); every arm gives zero basin reassignment and zero Bader error. **b**, Lossless label-map size per material: atom map (median 12.9 kB) and volnum map (21.8 kB); lines join the two maps of one material. Source: `analysis/qoac_b3_design/results/real_engineering/rows.csv` (columns `arm, delta, total_bytes, label_ctx_bytes_atom, label_ctx_bytes_volnum, reassigned_volnum_frac`).


## Supplementary Note 4 — Joint certification: engineering cohort and per-tolerance description

Protocol and criteria were frozen before any run (commit `8a784a4`); confirmation was authorized only if engineering gates E1, E2 and E4 passed.

**Engineering cohort (12 fresh P2 materials; 0 setting failures).** E1: R3 at its best joint post-processor certified at all three $\tau_B$ in 12/12. E2: joint overhead at $10^{-4}\,e$, median 1.000 (1.000 in all 12). E4: R3 over the best of J, T1 and GF at $10^{-4}\,e$, 12/12 wins, median 1.355 (minimum 1.167). Median joint compression ratios at $10^{-4}\,e$: R3 297 (Hartree-only 297), J 224, T1 191, GF 17.1.

**Per-tolerance description.**

| quantity | cohort | $\tau_B=10^{-3}\,e$ | $10^{-4}\,e$ | $10^{-5}\,e$ |
|---|---|---|---|---|
| R3 best post-processor | confirmatory (48) | none 48/48 | none 48/48 | none 33/48; Hartree-aware ($\mu=10^{-4}$) 15/48 |
| | engineering (12) | none 12/12 | none 12/12 | none 5/12; Hartree-aware ($\mu=10^{-4}$) 7/12 |
| certify-then-project: projected decisions | confirmatory | 0/192 | 0/192 | 31/165 |
| | engineering | 0/48 | 0/48 | 12/32 |
| median joint overhead (R3) | confirmatory | 1.000 | 1.000 [1.000, 1.000] | 1.000 |
| | engineering | — | 1.000 | 1.0032 |

The exact AECCAR partition is reused for reference and decoded Bader solves; hence the reported zero voxel reassignment tests consistency with that fixed partition and should not be read as a test of topology under a lossy partition reference. Median R3 joint compression ratio for the compressed charge stream in the confirmatory cohort is 298 at every $\tau_B$. At $10^{-5}\,e$, Hartree-aware and uniform projection gave the same certified ratio (median ratio 1.00; $n=35$ confirmatory materials where both certify). Confirmatory criteria: 48/48 jointly certified (threshold 46/48); overhead median 1.000, CI [1.000, 1.000] (thresholds 1.10, 1.15); utility 48/48 wins, median 1.317, CI [1.269, 1.360], minimum 1.096 (thresholds 36/48, 1.10, CI lower bound 1.00). Bootstrap seed 20261007, 10,000 resamples.

The Hartree-aware projection minimizes $\lVert Hc\rVert^2/s_H+\mu\lVert c\rVert^2/s_\rho$ subject to the basin-sum constraints, with $s_H=\lVert H\rho_{\text{ref}}\rVert^2$ and $s_\rho=\lVert\rho_{\text{ref}}\rVert^2$; it reduces to the uniform shift as $\mu\to\infty$. The constant mode is fixed by the constraints and the zero-mean part is solved from a regularized, Jacobi-scaled Cholesky system; the derivation and unit tests are in the repository (joint-contract code, DERIVATION.md).


## Supplementary Note 5 — Law protocol tables per tolerance and per operator

Values are rounded from the committed `SUMMARY.json` of each run; bootstrap seed 20261006, 10,000 resamples of the median. Both cohorts ran with zero pipeline failures, and A1 and A3 were certified for every material at every tolerance.


**Part A, P1, 60 Materials Project bulk crystals** (median certified compression-ratio ratio, bootstrap 95% CI, wins/n)

| ratio | $\tau=10^{-4}$ | $\tau=10^{-6}$ | $\tau=10^{-8}$ |
|---|---|---|---|
| A3/A1 (optimum / law) | 1.582 [1.490, 1.698], 60/60 | 1.105 [1.090, 1.146], 60/60 | 1.033 [1.028, 1.039], 60/60 |
| A3/A5 (operator / blind metric) | 1.327 [1.262, 1.449], 60/60 | 2.122 [1.919, 2.460], 60/60 | 1.604 [1.495, 1.717], 60/60 |
| A1/A6 (law / pointwise codecs) | 9.097 [7.445, 11.656], 59/60 | 10.235 [9.129, 12.089], 60/60 | 3.304 [2.878, 3.674], 60/60 |
| A1/A2 (law / truncation) | 0.793 [0.729, 0.932], 20/60 | 1.319 [1.273, 1.351], 52/60 | 1.593 [1.569, 1.620], 60/60 |
| A3/A0 (optimum / frozen ladder) | 1.705 [1.621, 1.828], 60/60 | 1.330 [1.272, 1.374], 60/60 | 1.158 [1.126, 1.190], 60/60 |
| A1/A0 (continuous / frozen ladder) | 1.057 [1.043, 1.077], 58/60 | 1.133 [1.098, 1.176], 60/60 | 1.116 [1.091, 1.145], 60/60 |

**Part B, P1, 60 Materials Project bulk crystals** (medians over materials; predicted / measured gain, median absolute log error, fraction of materials with measured gain in [0.90, 1.11])

| operator | $\tau=10^{-6}$: $G_\text{pred}$ / $G_\text{obs}$ | abs log error | in band | $\tau=10^{-4}$: $G_\text{pred}$ / $G_\text{obs}$ | abs log error | in band |
|---|---|---|---|---|---|---|
| density (control) | 1.000 / 1.000 | 0.000 | 100.0% | 1.000 / 1.000 | 0.000 | 100.0% |
| gradient | 1.014 / 1.011 | 0.006 | 100.0% | 1.030 / 1.032 | 0.009 | 100.0% |
| Laplacian | 1.039 / 1.042 | 0.012 | 98.3% | 1.075 / 1.066 | 0.025 | 78.3% |
| Hartree field | 1.151 / 1.149 | 0.014 | 25.0% | 1.124 / 1.103 | 0.017 | 60.0% |
| Hartree potential | 2.723 / 2.615 | 0.078 | 0.0% | 1.556 / 1.442 | 0.079 | 6.7% |
| Gaussian, $\sigma=0.5$ Å | 17.607 / 12.104 | 0.431 | 0.0% | 2.679 / 2.018 | 0.230 | 0.0% |

Pooled at $\tau=10^{-6}$: 300 pairs, median absolute log error 0.024, Spearman 0.978.

Pooled at $\tau=10^{-4}$: 300 pairs, median absolute log error 0.034, Spearman 0.944.

**Part A, P3b, 32 NOMAD surface slabs** (median certified compression-ratio ratio, bootstrap 95% CI, wins/n)

| ratio | $\tau=10^{-4}$ | $\tau=10^{-6}$ | $\tau=10^{-8}$ |
|---|---|---|---|
| A3/A1 (optimum / law) | 2.220 [1.837, 2.490], 32/32 | 1.222 [1.138, 1.359], 32/32 | 1.082 [1.055, 1.104], 32/32 |
| A3/A5 (operator / blind metric) | 1.815 [1.623, 2.362], 32/32 | 3.432 [2.888, 4.076], 32/32 | 3.039 [2.433, 3.358], 32/32 |
| A1/A6 (law / pointwise codecs) | 15.914 [13.013, 17.594], 32/32 | 18.530 [15.815, 23.071], 32/32 | 6.999 [4.691, 9.615], 32/32 |
| A1/A2 (law / truncation) | 0.691 [0.525, 0.887], 8/32 | 1.413 [1.284, 1.721], 27/32 | 2.155 [1.859, 2.333], 32/32 |
| A3/A0 (optimum / frozen ladder) | 2.305 [2.037, 2.561], 32/32 | 1.386 [1.331, 1.530], 32/32 | 1.292 [1.221, 1.356], 32/32 |
| A1/A0 (continuous / frozen ladder) | 1.054 [1.026, 1.068], 32/32 | 1.077 [1.054, 1.102], 32/32 | 1.201 [1.160, 1.256], 32/32 |

**Part B, P3b, 32 NOMAD surface slabs** (medians over materials; predicted / measured gain, median absolute log error, fraction of materials with measured gain in [0.90, 1.11])

| operator | $\tau=10^{-6}$: $G_\text{pred}$ / $G_\text{obs}$ | abs log error | in band | $\tau=10^{-4}$: $G_\text{pred}$ / $G_\text{obs}$ | abs log error | in band |
|---|---|---|---|---|---|---|
| density (control) | 1.000 / 1.000 | 0.000 | 100.0% | 1.000 / 1.000 | 0.000 | 100.0% |
| gradient | 1.012 / 1.015 | 0.007 | 100.0% | 1.027 / 1.047 | 0.022 | 100.0% |
| Laplacian | 1.031 / 1.047 | 0.023 | 96.9% | 1.062 / 1.068 | 0.023 | 84.4% |
| Hartree field | 1.164 / 1.165 | 0.015 | 6.2% | 1.120 / 1.098 | 0.018 | 65.6% |
| Hartree potential | 3.553 / 3.142 | 0.171 | 0.0% | 2.125 / 1.568 | 0.209 | 0.0% |
| Gaussian, $\sigma=0.5$ Å | 22.011 / 15.256 | 0.497 | 0.0% | 4.071 / 2.546 | 0.308 | 0.0% |

Pooled at $\tau=10^{-6}$: 160 pairs, median absolute log error 0.029, Spearman 0.979.

Pooled at $\tau=10^{-4}$: 160 pairs, median absolute log error 0.040, Spearman 0.914.

**Pooled over both cohorts** (92 materials, 460 operator–material pairs, density control excluded; `POOLED_P1_P3B.json`):

| statistic | $\tau=10^{-6}$ | $\tau=10^{-4}$ |
|---|---:|---:|
| median absolute log error | 0.026 | 0.035 |
| Spearman, all pairs | 0.977 | 0.935 |
| fraction of pairs within 25% | 0.800 | 0.857 |
| within-operator Spearman: gradient | 0.238 | 0.473 |
| within-operator Spearman: Laplacian | 0.442 | 0.617 |
| within-operator Spearman: Hartree field | 0.844 | 0.669 |
| within-operator Spearman: Hartree potential | 0.792 | 0.808 |
| within-operator Spearman: Gaussian, $\sigma=0.5$ Å | 0.895 | 0.800 |

Gradient and Laplacian gains lie close to 1 (medians 1.011–1.068 across cohorts and tolerances), so their within-operator rank correlations measure ordering inside a narrow range; their gains fall inside the null band [0.90, 1.11] as predicted (tables above).

**P1 shakedown cohort** (12 materials run through the identical pipeline; not part of any criterion): A3/A1 1.156, A3/A5 2.26, A1/A6 9.80, A1/A2 1.24 at $\tau=10^{-6}$; Part B median absolute log error 0.024, Spearman 0.979.

### 5.1 QoI-oriented comparator configurations (P1 and P3b; protocol `16e8890`, run 37620406802)

- **Arms.**
  - M2: MGARD (CODARcode/MGARD commit ac53ff9), smoothness $s=-2$.
  - M-best: MGARD, best of $s\in\{\infty,0,-1,-2\}$.
  - Q: QPET, block average over $b^3$ blocks with $b=4,8,16$, on SZ3, HPEZ and SPERR hosts; best of nine configurations.
- **Scope of QPET.** Its source implements local and regional QoIs (here block-average density over $4^3$, $8^3$, $16^3$ voxels), not the nonlocal Hartree/Poisson QoI. The Hartree certificate is imposed after decoding on every arm, so these gains quantify a particular implementable QPET configuration rather than superiority to all possible Hartree-aware compressors.
- **Search and certificate.** Each configuration used the same certificate and bisection policy as A1/A6. A1/A6 are previously recorded values, not rerun in this baseline experiment. The HPEZ-backed QPET configurations required float32 input whereas A1 read the original float64 density; the SPERR-backed QPET host accepted float64. The QPET and MGARD figures therefore are end-to-end configurations under the common Hartree acceptance metric, not a strict equal-input-precision ablation.
- **Coverage.** 92 of 92 materials and 3,588 searches; every search certified a point.
- **Codec crashes.** The tested upstream HPEZ executable aborted or segfaulted in 3,450 of 52,839 evaluated QPET configurations on P1 and 443 of 29,468 on P3b (within the QPET runs), while SPERR-QPET had no execution errors. These count as non-passing points. Every search ultimately found a certified point. The crash burden and floating-point input asymmetry prevent interpreting the reported ratios as a head-to-head optimal QPET implementation.
- **Statistics.** Bootstrap seed 20261006, 10,000 resamples of the median. Every ratio below is a win in every material.

**Median certified compression ratio**

| cohort | $\tau$ | A1 | A2 | A3 | A6 | M2 | M-best | Q |
|---|---|---|---|---|---|---|---|---|
| P1 (60) | $10^{-4}$ | 818 | 969 | 1,303 | 79.2 | 59.2 | 73.4 | 158 |
| P1 (60) | $10^{-6}$ | 195 | 152 | 224 | 16.0 | 10.2 | 10.9 | 29.4 |
| P1 (60) | $10^{-8}$ | 24.6 | 14.9 | 25.0 | 7.12 | 5.06 | 5.28 | 9.99 |
| P3b (32) | $10^{-4}$ | 1,771 | 2,309 | 3,552 | 108 | 196 | 244 | 257 |
| P3b (32) | $10^{-6}$ | 504 | 353 | 647 | 23.3 | 21.0 | 23.1 | 46.0 |
| P3b (32) | $10^{-8}$ | 64.9 | 27.2 | 70.3 | 10.0 | 8.65 | 8.89 | 18.2 |

**Median per-material ratio [95% CI]**

| cohort | $\tau$ | A1/M2 | A1/M-best | A1/Q | A3/M2 | A3/Q |
|---|---|---|---|---|---|---|
| P1 | $10^{-4}$ | 12.5 [11.4, 15.4] | 9.75 [9.00, 13.1] | 5.22 [4.60, 5.93] | 20.5 [17.2, 23.4] | 7.97 [6.84, 9.33] |
| P1 | $10^{-6}$ | 18.2 [15.3, 21.7] | 16.6 [14.3, 19.5] | 6.31 [5.53, 6.95] | 20.3 [17.5, 25.0] | 6.91 [5.92, 8.15] |
| P1 | $10^{-8}$ | 4.69 [4.27, 5.77] | 4.55 [4.11, 5.67] | 2.33 [2.00, 2.85] | 4.79 [4.32, 6.09] | 2.36 [2.05, 2.97] |
| P3b | $10^{-4}$ | 7.97 [5.32, 11.1] | 6.63 [4.17, 9.04] | 7.56 [5.07, 9.13] | 15.0 [9.31, 20.2] | 15.6 [9.67, 21.5] |
| P3b | $10^{-6}$ | 21.0 [17.5, 27.9] | 19.6 [15.7, 24.9] | 9.47 [8.14, 12.8] | 27.3 [20.1, 35.6] | 11.3 [9.62, 16.5] |
| P3b | $10^{-8}$ | 7.99 [5.20, 11.8] | 7.42 [4.91, 10.8] | 3.84 [2.70, 4.83] | 8.43 [5.42, 13.3] | 4.09 [2.88, 5.28] |

### 5.2 Fixed-reference vacuum Hartree shifts on slabs (P3b; protocol `47b110a`, run 37598559834)

- **Definition and limitation.** The reported $\Delta\Phi$ is the mean planar-averaged **Hartree error** in the central half of a vacuum window identified from the reference density. Fermi energy, ionic and exchange-correlation terms are fixed. This is a compression-induced electrostatic vacuum-level proxy, **not** the change in a fully self-consistently recomputed DFT work function. The vacuum screen uses a density threshold, not a direct flat-potential-plateau criterion or a dipole-correction convergence test.
- **Coverage.** 27 of 32 slabs have at least 3 Å of threshold-defined vacuum. The qualifying runs range from 3.03 to 27.08 Å (median 6.71 Å), with averaging windows of 1.55 to 13.64 Å. Five slabs, Lu$_2$Br$_2$O, Ti(PO$_4$)$_2$, Ga$_2$Te$_3$, Nb$_2$Se$_3$ and EuS, have no qualifying vacuum run.
- **Streams.** All 480 certified streams were regenerated and reproduced their recorded bytes and Hartree errors exactly:
  - A3 and A5 from their recorded parameters;
  - A1, A2 and A6 by rerunning the unchanged deterministic search where the recorded nine-digit parameter did not reproduce the stream.
- **Absolute scale.** The reference Hartree-potential RMS is 63.6–3,273 eV (median 528 eV). The absolute RMS bound $\tau V_\text{ref}$ is therefore a median 64.1 meV at $10^{-4}$, 0.641 meV at $10^{-6}$ and 0.0064 meV at $10^{-8}$.

**Fixed-reference vacuum Hartree shift $|\Delta\Phi|$ (meV) over 27 slabs: median / P95 / maximum; counts below 1 and 10 meV**

| arm | $\tau=10^{-4}$ | $\tau=10^{-6}$ | $\tau=10^{-8}$ |
|---|---|---|---|
| A1 law | 1.09 / 5.34 / 6.06; 12, 27 | 0.0040 / 0.021 / 0.045; 27, 27 | 1.0e-5 / 3.9e-5 / 8.1e-5; 27, 27 |
| A2 truncation | 41.0 / 197 / 385; 0, 2 | 0.55 / 1.86 / 2.97; 19, 27 | 0.0039 / 0.012 / 0.017; 27, 27 |
| A3 operational optimum | 1.72 / 6.72 / 8.26; 9, 27 | 0.0040 / 0.014 / 0.034; 27, 27 | 1.5e-5 / 1.6e-4 / 2.0e-4; 27, 27 |
| A5 blind RD optimum | 21.2 / 265 / 347; 1, 10 | 0.28 / 1.58 / 2.50; 23, 27 | 0.0027 / 0.019 / 0.024; 27, 27 |
| A6 best pointwise codec | 35.5 / 158 / 238; 0, 2 | 0.34 / 1.85 / 2.16; 19, 27 | 0.0042 / 0.014 / 0.043; 27, 27 |

Median per-slab ratio $|\Delta\Phi|_{\text{A6}}/|\Delta\Phi|_{\text{A1}}$: 33.4 at $10^{-4}$ and 71.7 at $10^{-6}$, with A1 lower in 27/27 slabs at both tolerances. This descriptive ratio comes from `analysis/p3b_vacuum_level_20261007/results/per_slab_dphi.csv`; it was not a pre-declared statistic. A larger-vacuum/dipole-sensitive test would be needed to interpret the proxy as a converged work-function error.


## Supplementary Note 6 — Gain-predictor calibration

The predictor form was fixed by a retrospective calibration on the 12 QOAC-H engineering materials (commit `f4baa7a`), before the law protocol was frozen (`fe2e08a`); the calibration observations were known when the predictors were written, and the predictor was then tested only on the unused P1 and P3b cohorts. Predictor (a) is the high-rate orbit-only expression, in which every component has error $\Delta^2/12$ and rate $h-\log_2\Delta$; predictor (b) is the finite-rate Laplacian model of the main-text Methods, evaluated on the frozen ladder.

| quantity | observed median | predictor | predicted median | median abs log error | Spearman $\rho$ | direction correct |
|---|---:|---|---:|---:|---:|---:|
| Hartree, exponent 2 / exponent 0 error ratio | 0.0767 | (a) high-rate | 0.0496 | 0.362 | 0.94 | 12/12 |
| | | (b) finite-rate | 0.0832 | 0.148 | 0.96 | 12/12 |
| electric (Hartree) field, exponent 1 / exponent 0 | 0.806 | (a) high-rate | 0.783 | 0.037 | 0.71 | 12/12 |
| | | (b) finite-rate | 0.790 | 0.021 | 0.58 | 12/12 |
| electric (Hartree) field, exponent 1 / exponent 2 | 0.928 | (a) high-rate | 0.913 | 0.021 | −0.49 | 10/12 |
| | | (b) finite-rate | 0.922 | 0.018 | 0.52 | 12/12 |

The high-rate expression overstates the Hartree gain about 1.4-fold in every material; the dead zone of the finite-rate model removes most of that bias. Absolute model compression ratios deviate from observation by a median of 0.068 dex, and these errors partly cancel in ratios between policies, which are the quantities predicted.


## Supplementary Note 7 — Population construction

**Development and external sets.** 254 development densities (186 Materials Project bulk, 68 NOMAD slabs from five uploads); 65 external stability records (37 AFLOW bulk, 28 NOMAD vacuum-containing 2D); 63 external confirmatory systems. These sets supplied every QSQ result and the frozen-ladder QOAC-H evidence.

**Fresh populations (rule `10e7863`, frozen before any candidate download; SHA-256 of the rule `25d6f04f…3f133778b`).** The exclusion set scanned 60 repository branches (1,688 unique text blobs) and contains 833 identifiers (368 `mp-*` ids, 486 Materials Project S3 task ids, 96 NOMAD entry ids, 70 `nomad-*` material ids) and 291 distinct reduced formulas. Only metadata (listing entry, size, SHA-256, grid shape, atom count, reduced formula, lattice, finiteness and positivity of the density) was read; no QoI or compression outcome was computed on any candidate.

| | P1 | P2 |
|---|---|---|
| source | Materials Project bulk, CHGCAR | Materials Project bulk, CHGCAR + AECCAR0 + AECCAR2 |
| frame after pre-filter | 270,278 task ids | 135,534 task ids |
| strata (keys per stratum) | 72 (3,753–3,754) | 60 (2,258–2,259) |
| engineering + confirmatory | 12 + 60 | 12 + 48 |
| candidates downloaded / rejected | 72 / 0 | 64 / 4 (2 grid size, 2 excluded formula) |
| npoints, min / median / max | 175,616 / 1,045,248 / 4,741,632 | 175,616 / 884,736 / 5,832,000 |
| atoms, min / median / max | 2 / 12 / 72 | 2 / 7 / 64 |

The S3 listing (bucket `materialsproject-parsed`, 2026-10-06 14:16–14:38 UTC) contained 415,475 task ids with a CHGCAR and 138,804 with CHGCAR, AECCAR0 and AECCAR2. All 132 accepted materials have distinct task ids and reduced formulas, none is in the exclusion set, and P1 and P2 are disjoint. For 117/132 materials the Materials Project material id is not recorded in the file and the task id is used as identifier; formula exclusion also excludes other tasks of a used material.

**P3b (rule `39ba728`; cohort drawn in `d1c1050`).** Frame: the frozen public NOMAD listing (`results.material.structural_type = surface`, `program_name = VASP`; 16,275 entries, 820 with a retrievable CHGCAR size). Rows between 1 and 80 MB were kept; uploads containing an already-used NOMAD entry, used ids and used reduced formulas (including every P1 and P2 formula) were dropped. Formulas were visited in SHA-256 order of a fixed salt plus formula, and within a formula entries in SHA-256 order; the earliest entry that parses, has a finite density with positive sum, has $1.5\times10^5\le$ npoints $\le6.0\times10^6$ and comes from an upload with fewer than six accepted materials was accepted, one per formula. Because a size-stratified slab draw under the general rule could supply at most 23 materials, slabs were drawn one per reduced formula; 32 slabs entered the cohort, with no engineering split.

Every manifest records material id, task or entry id, source URL, byte count and SHA-256; `PROVENANCE.json` records listing timestamps and the hashes of every index, frame, exclusion file, script and manifest.


## Supplementary Note 8 — Source files

Every number in the main text and this SI is taken from a committed file of the public repository (see Data availability). The file-by-file table, with the commit that last changed each file, is `paper/nc_reopen/SOURCE_FILES.md` in that repository; protocols, manifests, per-material tables and the register of every protocol with its outcome are in the same repository.
