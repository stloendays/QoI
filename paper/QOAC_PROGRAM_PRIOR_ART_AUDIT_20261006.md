# QOAC program prior-art and novelty audit (C1–C4): 2026-10-06

Status: literature-positioning record for four program-level claims. It extends
`paper/QOAC_PRIOR_ART_NOVELTY_AUDIT_20261005.md` (the QOAC-H audit). That audit's standards apply here,
and its conclusions are not repeated: no "first QoI-aware / operator-aware / frequency-weighted
compressor" wording, and MGARD-QoI, Jiao et al., QPET, Lee et al., TOPIQ, Goyal 2001 and the
electronic-structure works it lists are already positioned. This document cites those works again only
where a C1–C4 claim overlaps them in a new way.

This is not a claim that no unpublished or unindexed work exists.

## 0. How the sources were checked (read before citing anything below)

**Limitation.** This session's network egress policy blocked direct access to every primary source
host tried: arxiv.org, doi.org, api.crossref.org, ieeexplore.ieee.org, mdpi.com, vldb.org, osti.gov,
par.nsf.gov, ornl.gov, doaj.org and di.ens.fr. No source could be *opened*. Verification was done through
web-search index results only: publisher, repository, DBLP and institutional listings that show title,
authors, venue and year, plus abstract snippets. The verification levels below are therefore weaker
than "opened and read":

| tag | meaning |
|---|---|
| **[M]** | Title, authors, venue and year are confirmed by at least one independent index or publisher listing in search results. The content statement rests on the abstract or index snippet. |
| **[M+DOI]** | As [M], and the DOI or arXiv id also appeared in a search-result URL or listing. |
| **UNVERIFIED** | Something (usually the DOI, sometimes the exact title or a content detail) could not be confirmed. Do not paste into a manuscript before checking it against the publisher page. |

**Before submission, every entry must be re-checked against the full text.** This applies especially
to the content claims about Lee et al. (C3), Wu et al. (C1/C4) and Compression Safeguards (C3/C4),
where this audit's overlap judgement depends on method details taken from snippets.

Query families searched (general web index, standard and extended modes): MGARD / MGARD-QoI /
Sobolev-norm control; QoI-preserving compression (Jiao, QPET, QoZ, Fixed-PSNR, TOPIQ, progressive
retrieval); constraint-satisfaction QoI post-processing (Lee, Banerjee); post-hoc correction frameworks
(Compression Safeguards, FFCz, cluster preservation); Shoham–Gersho / Lagrangian bit allocation;
Ortega–Ramchandran and Sullivan–Wiegand RDO; RDOQ; weighted-MSE and perceptual coding gain;
Huang–Schultheiss; Jayant–Noll; low-rate and dead-zone transform-coding theory (Mallat–Falzon, Sullivan,
rho-domain); task-based and indirect (remote-source) rate-distortion; compression-ratio prediction;
electron-density, wavefunction and Bader-related compression; Coulomb-metric density fitting;
multi-QoI preservation. SIAM, IEEE, ACM, VLDB, SC and JCTC/JCP were reached only through that general
index, not through native database search. Google Scholar itself was not reachable.

---

## C1: Rate-distortion-optimal allocation in a downstream linear-operator metric

Claim under audit: per-band (per-shell) Lagrangian selection over exact operational (zlib byte,
operator-distortion) curves, with direct targeting of the decode-verified Hartree certificate. Two
empirical findings go with it: (a) the closed-form high-rate law Delta ∝ w^(-1/2) (here Delta_G ∝ |G|^2)
comes within about 10% (tau = 1e-6) and 4% (tau = 1e-8) of that operational optimum; (b) the same
optimizer in the operator-blind L2 metric is about 2.2x worse at tau = 1e-6, with the same Hartree
certificate (`analysis/qoac_v03_rdo/results/RESULTS.md`, 12 engineering materials, development only).

### Closest prior art

1. **Shoham & Gersho (1988).** Y. Shoham, A. Gersho, "Efficient bit allocation for an arbitrary set of
   quantizers," *IEEE Trans. Acoust., Speech, Signal Process.* 36(9), 1445–1453.
   DOI 10.1109/29.90373 **[M+DOI]**. This is the Lagrangian (convex-hull) allocation over an arbitrary,
   irregular set of operational quantizer (rate, distortion) points.
2. **Ortega & Ramchandran (1998).** A. Ortega, K. Ramchandran, "Rate-distortion methods for image and
   video compression," *IEEE Signal Process. Mag.* 15(6), 23–50. DOI 10.1109/79.733495 **[M+DOI]**.
   This tutorial standardizes operational RD and Lagrangian / bisection-on-lambda allocation.
3. **Sullivan & Wiegand (1998).** G. J. Sullivan, T. Wiegand, "Rate-distortion optimization for video
   compression," *IEEE Signal Process. Mag.* 15(6), 74–90 **[M]**. The DOI 10.1109/79.733497 is
   **UNVERIFIED**.
4. **RDOQ.** M. Karczewicz, Y. Ye, I. Chong, "Rate distortion optimized quantization," ITU-T SG16 Q.6
   (VCEG) contribution VCEG-AH21, Antalya, Jan. 2008 **[M]**. This is a standards document with no DOI.
   It applies coefficient-level RD decisions with an entropy-coder model.
5. **Gersho & Gray (1992).** A. Gersho, R. M. Gray, *Vector Quantization and Signal Compression*,
   Springer (Kluwer) SECS 159. DOI 10.1007/978-1-4615-3626-0 **[M+DOI]**. It contains high-resolution
   bit allocation under weighted MSE, where Delta_k ∝ w_k^(-1/2) is the textbook solution. The exact
   chapter and section are not checked: **UNVERIFIED**.
6. **Watson (1993).** A. B. Watson, "DCT quantization matrices visually optimized for individual
   images," *Proc. SPIE* 1913. DOI 10.1117/12.152694 **[M+DOI]**. It optimizes per-coefficient step
   sizes for a downstream (perceptual) error model on a per-image basis, which is the image-coding
   analogue of an operator-weighted step-size map.
7. **MGARD Sobolev / QoI control.** Ainsworth, Tugluk, Whitney, Klasky, *SIAM J. Sci. Comput.* 41(4),
   A2146–A2171 (2019), DOI 10.1137/18M1208885 **[M+DOI]**. The companion "multivariate case" paper is
   in *SIAM J. Sci. Comput.* 41(2) (2019) **[M]**, with DOI **UNVERIFIED**. The software paper is
   Gong et al., "MGARD: A multigrid framework for high-performance, error-controlled data compression
   and refactoring," *SoftwareX* 24, 101590 (2023), DOI 10.1016/j.softx.2023.101590 **[M+DOI]**.
   MGARD's smoothness parameter s selects a Sobolev-type norm (s < 0 approximates negative-norm,
   smoothing-operator metrics). Our own strongest-baseline study ran MGARD at s = -1, and it lost by
   about 19x (`analysis/qoac_h_strong_baselines/results/RESULTS.md`). That MGARD's s maps to a precise
   H^s norm is from the existing audit and the MGARD literature; the detail was not re-verified here.
8. **Wu et al. (SC24).** X. Wu, Q. Gong, J. Chen, Q. Liu, N. Podhorszki, X. Liang, S. Klasky,
   "Error-controlled progressive retrieval of scientific data under derivable quantities of interest,"
   SC24 (IEEE). arXiv:2411.05333 **[M+DOI for arXiv id]**. The proceedings DOI is **UNVERIFIED**. It
   selects which precision segments (bit-planes) to retrieve so that a QoI error bound is guaranteed, an
   operational size-versus-QoI-error decision driven by a QoI target. Whether its selection is Lagrangian
   or greedy is **UNVERIFIED**.
9. **Fixed-quality targeting.** D. Tao, S. Di, X. Liang, Z. Chen, F. Cappello, "Fixed-PSNR lossy
   compression for scientific data," IEEE CLUSTER 2018, 314–318, arXiv:1805.07384 **[M]**. J. Liu et
   al., "Dynamic quality metric oriented error bounded lossy compression for scientific datasets" (QoZ),
   SC22, arXiv:2310.14133 **[M]**. Both tune a compressor to hit a user-specified global quality metric.
10. **Indirect / remote-source rate-distortion.** H. S. Witsenhausen, "Indirect rate distortion
    problems," *IEEE Trans. Inf. Theory* 26(5), 518–521 (1980) **[M]**, DOI **UNVERIFIED**. With
    Gaussian reverse water-filling (Cover & Thomas, *Elements of Information Theory*, Wiley; edition and
    DOI **UNVERIFIED**), this gives the information-theoretic optimum when the distortion is measured
    after a linear map, i.e. reverse water-filling on the operator-weighted spectrum. N. Shlezinger,
    Y. C. Eldar, M. R. D. Rodrigues, "Hardware-limited task-based quantization," *IEEE Trans. Signal
    Process.* 67(20), 5223–5238 (2019), arXiv:1807.08305 **[M]**, DOI **UNVERIFIED**, designs quantizers
    for recovering a linear function of the input.

### What overlaps

- **Lagrangian selection over exact operational curves** is Shoham–Gersho / Ortega–Ramchandran /
  RDOQ-standard. Bisection on lambda plus a feasibility polish is a known implementation pattern.
- **Weighted-MSE high-rate step-size law** Delta ∝ w^(-1/2) is textbook (Gersho & Gray, Goyal 2001).
- **Optimizing compression for a distortion measured after a linear operator** has theoretical prior
  art: indirect RD, task-based quantization, MGARD negative-norm control.
- **Targeting a downstream quality metric or QoI certificate directly** has prior art: Fixed-PSNR, QoZ,
  MGARD-QoI, and Wu et al.'s QoI-guaranteed retrieval.

### What differs (defensible)

- The distortion metric is the **exact diagonal symbol of a physical operator** (|G|^-4 for Hartree) on
  a conservative Hermitian-orbit set. The constraint is the program's **decode-verified two-sided
  certificate** (historical and Nyquist-safe), not a proxy bound. No retrieved scientific-compression
  work runs exact operational RD allocation in a *physical-operator* metric for a DFT density.
- The paper's scientific content is the **quantified answer to "how much does optimal allocation add
  beyond the closed-form law?"**:
  - the closed-form law is within about 10% / 4% of the operational optimum at tau = 1e-6 / 1e-8;
  - the gain is 1.41x only at the loose tolerance 1e-4, consistent with the dead-zone regime;
  - the prior shape does not matter once RDO runs in the right metric (A3/A4 = 0.998).

  This is a measurement in a new application, not a new allocation algorithm.
- The **operator-metric-versus-L2 ablation under identical optimal machinery** (A3/A5 = 2.21x at
  tau = 1e-6, 1.58x to 2.84x across tolerances) isolates the value of the metric from the value of the
  optimizer. No retrieved work reports this ablation for an electronic-structure QoI.

### Constraints from the program's own evidence

- v0.3 **failed G2** (median 1.099 vs 1.20) and `confirmatory_authorized = false`. Every C1 number is
  12-material development data, and the RESULTS file says the hypotheses "need a new frozen protocol on
  the fresh population before they can be claimed." The manuscript may present them as engineering
  observations, not as confirmed findings.
- v0.3 is positioned as an **operational-optimum reference**, not a better codec.

### Verdict C1

Defensible:
> "Using exact operational rate-distortion allocation in the Hartree-operator metric as an upper
> benchmark, the closed-form high-rate law Delta_G ∝ |G|^2 comes within about 10% of the operational
> optimum at tau = 1e-6 (12 development materials). The same optimizer in an operator-blind L2 metric is
> about 2.2x worse under the same Hartree certificate, which isolates the operator metric, rather than
> the optimizer, as the source of the gain."

Avoid:
- "first rate-distortion-optimal QoI compressor" or "first Lagrangian allocation for a QoI";
- "novel RDO algorithm" or "new bit-allocation method" (it is Shoham–Gersho-class);
- "we derive the optimal allocation Delta ∝ w^(-1/2)" without crediting it as classical high-rate
  weighted-MSE theory;
- any confirmatory wording ("demonstrates", "establishes") for the 10% and 2.2x figures until a frozen
  fresh-population protocol reproduces them.

---

## C2: A-priori prediction of the operator-aware gain from the operator symbol and the mode distribution

Claim under audit: the matched-rate RMSE gain of operator-weighted over operator-blind allocation is
predicted from the operator symbol and the orbit (|G|) distribution alone, as a transform-coding-gain /
AM-over-GM-of-weights expression. Finite-rate dead-zone corrections are included. The E-field case is
predicted at only about 20% (theory median ratio 0.783) against about 20x for Hartree (theory 0.050).

### Closest prior art

1. **Classical coding gain.** J. J. Y. Huang, P. M. Schultheiss, "Block quantization of correlated
   Gaussian random variables," *IEEE Trans. Commun. Syst.* CS-11, 289–296 (1963) **[M]**, DOI
   **UNVERIFIED**. N. S. Jayant, P. Noll, *Digital Coding of Waveforms*, Prentice-Hall (1984) **[M]**.
   Gersho & Gray (1992, above). These establish optimal-allocation gain as an arithmetic/geometric-mean
   ratio. With a weighted distortion, the same algebra gives an AM/GM ratio of the weights (times
   variances).
2. **Perceptual (weighted) coding gain.** X. Wei, M. J. Shaw, M. R. Varley, ICASSP 1997. The paper
   defines a "perceptual coding gain" for optimum bit allocation under perceptually shaped noise **[M]**.
   The exact title and pages are **UNVERIFIED**. A search snippet attributes a weighted-AM/weighted-GM
   form to this line of work, but which paper carries that form is **UNVERIFIED**. Under a different
   weight source, this is the same mathematical object as C2's high-rate predictor.
3. **Low-rate / dead-zone departures from high-rate theory.** S. Mallat, F. Falzon, "Analysis of low
   bit rate image transform coding," *IEEE Trans. Signal Process.* 46(4), 1027–1042 (1998) **[M]**.
   The pages and the DOI 10.1109/78.668557 are **UNVERIFIED**. The paper shows that high-resolution
   D(R) ∝ 2^(-2R) fails at low rate, where performance is governed by the number of nonzero (significant)
   coefficients. G. J. Sullivan, "Efficient scalar quantization of exponential and Laplacian random
   variables," *IEEE Trans. Inf. Theory* 42(5), 1365–1374 (1996) **[M]**, DOI **UNVERIFIED**, covers
   optimal dead-zone plus uniform-threshold quantization. Z. He, S. K. Mitra, "A linear source model and
   a unified rate control algorithm for DCT video coding," *IEEE Trans. Circuits Syst. Video Technol.*
   12(11), 970–982 (2002) **[M]**, DOI **UNVERIFIED**, models rate as linear in the fraction of zero
   coefficients (rho-domain). Together these are prior art for "dead-zone fraction controls the
   finite-rate behaviour" (`general_qoac_electric_field_diagnosis` D2).
4. **Compression-ratio prediction for scientific data.** R. Underwood, J. Bessac, D. Krasowska, J. C.
   Calhoun, S. Di, F. Cappello, "Black-box statistical prediction of lossy compression ratios for
   scientific data," *Int. J. High Perform. Comput. Appl.* (2023), arXiv:2305.08801 **[M]**, DOI
   **UNVERIFIED**. A related NJIT-listed paper, "Compression ratio modeling and estimation across error
   bounds for lossy compression" **[M]**, has authors and venue **UNVERIFIED**. Both predict compression
   ratio from data statistics or compressor internals, not from a downstream operator.
5. **Indirect RD / reverse water-filling** (C1 item 10). This gives the exact Gaussian-model optimum for
   a linear-operator distortion, from which a gain expression also follows.

### What overlaps

- The **high-rate gain formula itself** (AM/GM of weights under entropy-coded uniform quantization)
  is classical coding-gain / perceptual-coding-gain algebra. Its density-independence at high rate,
  where only the weight distribution matters, follows directly from that algebra.
- **"High-rate theory breaks down because most coefficients are zeroed"** is established low-rate
  transform-coding knowledge (Mallat–Falzon, rho-domain, dead-zone quantization).

### What differs (defensible)

- The weights come from a **physical operator symbol on the crystal reciprocal lattice** (|G|^-4
  Hartree, |G|^-2 E-field). The mode distribution is the conservative Hermitian-orbit set of each
  material, so the predictor needs **no density data**. No retrieved work uses coding gain to forecast,
  per material, the benefit of operator-aware allocation for a scientific QoI. No retrieved work uses it
  to explain why one operator (Hartree) yields a large effect while another (E-field) yields a small one.
- The **cross-operator diagnosis** is the scientifically useful result: |G|^-2 is close to the 3-D mode
  density, so the AM/GM spread is small and the gain is at most about 20%. This explains a frozen NO-GO
  as a gate set beyond the theoretical ceiling, not as a wrong operator law. It is also a usable
  methodological recommendation: derive effect-size gates from the orbit set before execution.

### Constraints from the program's own evidence

- **Provenance:** the D1 prediction was derived **after** the E-field NO-GO was known (stated in
  `general_qoac_electric_field_diagnosis/results/RESULTS.md`). The Hartree "calibration" (0.050
  predicted vs 0.077 observed) is also retrospective. **The word "a-priori" can describe the inputs (the
  operator symbol and orbit set only, no outcome data) but must not describe the timing.** Nothing has
  yet been predicted prospectively and then confirmed.
- **The finite-rate dead-zone correction is a diagnosis, not a validated predictor.** D2 shows
  actual/high-rate RMSE ratios of 0.75, 0.39 and 0.19 for beta = 0, 1, 2. D4 shows unequal Lagrangian
  slopes (implied exponent 1.56). The program proposes "a finite-rate Laplacian/deadzone model" but has
  not built or tested one. Any "including finite-rate corrections" wording is currently unsupported.

### Verdict C2

Defensible:
> "Classical transform-coding-gain theory, evaluated on the operator symbol and each material's
> reciprocal-lattice orbit set alone, accounts for the size of the operator-aware advantage. It predicts
> a roughly twenty-fold matched-rate RMSE reduction for the Hartree operator (|G|^-4) but only about 20%
> for the electric field (|G|^-2). This explains, after the fact, why one operator gives a large effect
> and the other a small one. The remaining gap is attributable to the low-rate dead-zone regime."

With a future frozen protocol, the program could add: "...and per-material effect-size gates derived
from this expression were frozen before execution and then met/not met."

Avoid:
- "first a-priori theory of QoI-aware compression gain" or "new coding-gain theory";
- "predicted a priori" for the E-field or Hartree cases (both are retrospective);
- "finite-rate theory" or "dead-zone-corrected prediction" until such a model is specified, frozen and
  tested;
- presenting AM/GM-of-weights as derived here without citing classical / perceptual coding gain.

---

## C3: Minimum-disturbance constraint projection after generic compression for non-spectral QoIs (Bader)

Claim under audit: decode, then apply the fixed-partition uniform correction c_j = Delta_i / N_i on
each exact-reference Bader basin. This is simultaneously minimum-Linf and minimum-L2 among corrections
that restore each region sum, and it gives numerically zero Bader error with zero reassignment. A
Hartree-aware variant would minimize the Hartree (H^-1) error of the correction subject to the same
region-sum constraints.

### Closest prior art

1. **Lee et al. (2022)**, already in the QOAC-H audit. J. Lee, Q. Gong, J. Choi, T. Banerjee,
   S. Klasky, S. Ranka, A. Rangarajan, "Error-bounded learned scientific data compression with
   preservation of derived quantities," *Appl. Sci.* 12(13), 6718. DOI 10.3390/app12136718 **[M+DOI]**.
   Per index snippets, the QoI step is a **Lagrangian constrained optimization that minimizes the change
   to the reconstructed primary data subject to linear moment constraints** (XGC moments). It is solved
   by dual maximization with Newton's method, and the multipliers are stored with a product quantizer.
   **This is the same mathematical construction as C3's L2 projection**: minimum-norm correction onto an
   affine set defined by linear QoIs. The exact norm and any weighting used are **UNVERIFIED** (full text
   not opened).
2. **Banerjee et al.** T. Banerjee, J. Choi, J. Lee, Q. Gong, J. Chen, S. Klasky, A. Rangarajan,
   S. Ranka, "Scalable hybrid learning techniques for scientific data compression," arXiv:2212.10733
   **[M+DOI for arXiv id]**. This is the GPU pipeline with the same constraint-satisfaction
   post-processing, preserving QoIs "within floating-point error". The journal version is **UNVERIFIED**.
3. **Jiao et al. (VLDB 2022)**, already in the QOAC-H audit. The **regional average** is one of its four
   QoI families, preserved by deriving pointwise bounds, not by post-projection. Bader charges are
   regional sums, so the "region-sum QoI" family itself is not new.
4. **Compression Safeguards.** J. Tyree, R. Underwood, C. Bouvier, D. Köhler, T. Reichelt, P. Dueben,
   S. Faghih-Naini, H. Järvinen, M. Klöwer, "Compression Safeguards: Building trust into lossy data
   compression," EGUsphere preprint egusphere-2026-4266 (2026) **[M]**. The DOI is **UNVERIFIED**. It
   wraps any compressor with user-declared safeguards, including QoI bounds and regions of interest, and
   produces a stored **correction** so that they hold after decompression. This is a general
   "generic compressor plus correction guarantees a declared property" framework.
5. **FFCz.** C. Ren, R. Underwood, S. Di, E. Kutay, Z. Lukić, A. Yener, F. Cappello, H. Guo, "FFCz:
   Fast Fourier correction for spectrum-preserving lossy compression of scientific data,"
   arXiv:2601.01596 (2026) **[M+DOI for arXiv id]**. It corrects SZ3/ZFP/SPERR output by iterative
   projection onto the intersection of spatial and frequency-domain error constraints. This is
   post-compression projection for a *spectral* QoI.
6. **Ren et al. (2026).** C. Ren, S. Di, K. Heitmann, F. Cappello, H. Guo, "Preserving clusters in
   error-bounded lossy compression of scientific particle data," arXiv:2604.18801 **[M]**. It is a
   correction-based preservation of a topological/partition QoI (single-linkage clustering) after
   off-the-shelf compressors.
7. **Coulomb-metric constrained fitting (for the Hartree-aware variant).** B. I. Dunlap, J. W. D.
   Connolly, J. R. Sabin, "On some approximations in applications of Xα theory," *J. Chem. Phys.* 71,
   3396 (1979) **[M]**, DOI **UNVERIFIED**. O. Vahtras, J. Almlöf, M. W. Feyereisen, "Integral
   approximations for LCAO-SCF calculations," *Chem. Phys. Lett.* 213, 514–518 (1993) **[M]**, DOI
   **UNVERIFIED**. Variational (robust) density fitting minimizes the Coulomb (H^-1) self-energy of the
   density error, classically with a total-charge constraint by Lagrange multiplier. That the charge
   constraint appears in Dunlap 1979 specifically is **UNVERIFIED**. The Hartree-aware projection is
   generalized least squares in this same Coulomb metric with *several* region-charge constraints.
8. **Moment-conserving wavelets.** "Towards fully dynamic omnitrees: Moment-conserving anisotropic
   compression with wavelets," arXiv:2607.04881 (2026) **[M]**. Authors are **UNVERIFIED**. It notes
   that Haar compression conserves mass (and higher-order wavelets conserve higher moments), which is
   conservation built into the transform rather than projection.
9. **Bader algorithm.** Henkelman/Tang grid Bader (e.g. W. Tang, E. Sanville, G. Henkelman,
   *J. Phys.: Condens. Matter* 21, 084204 (2009)). This is **[M]** for the existence of the
   `tang09_084204` paper. The full citation and DOI must be taken from the program's existing
   bibliography and are **UNVERIFIED** here.

No retrieved work compresses DFT densities while preserving Bader charges.

### What overlaps

- **Minimum-L2 correction subject to linear QoI constraints after lossy compression** is Lee et al.'s
  constraint-satisfaction step. It is also the standard orthogonal projection onto an affine set.
- With disjoint indicator constraints, the minimum-L2 solution is the uniform per-region shift. That it
  is also minimum-Linf follows from one line each of Cauchy–Schwarz and the triangle inequality. **This
  is an elementary observation, not a contribution**, though worth stating because it makes the
  correction simultaneously optimal in both norms the program reports.
- "Generic compressor plus stored correction guarantees a declared property" is the Compression
  Safeguards framing. FFCz and cluster preservation do the same for spectral and topological QoIs.
- The Hartree-aware variant is constrained generalized least squares in the Coulomb metric, a standard
  construction in density fitting.

### What differs (defensible)

- **The QoI**: Bader charges are defined by a *partition computed from a reference field*
  (zero-flux surfaces of the AECCAR density). B2 holds that partition exact and certifies with the
  actual Henkelman Bader code on the decoded, projected field, including **zero basin reassignment**.
  This is end-to-end certification with the production analysis tool, not a bound derived from linear
  algebra.
- **The auxiliary density contract** (Linf ≤ kappa · epsilon^G1) explicitly rules out the degenerate
  "compress arbitrarily, then project" solution. Prior constraint-satisfaction work bounds primary-data
  error through the base compressor. The kappa frontier is a disclosed design choice, not novelty.
- **The empirical finding that matters scientifically**: under an exact partition, the Hartree-certified
  QOAC-H stream already meets the Bader contract before projection (≤ 5.3e-5 e, about 20x below tau_B,
  50/50 materials). Projection is then *net harmful* to the Hartree budget (it pushed 45% of
  confirmatory materials one rung down). This negative-interaction observation, where one QoI's repair
  costs another's certificate, is not reported in the retrieved post-correction literature, which treats
  single declared properties or combines them logically.
- The Hartree-aware projection is **proposed, not executed**. It is listed under "Next iteration
  (requires a new frozen protocol)." Nothing about its performance can be claimed.

### Verdict C3

Defensible:
> "Following constraint-satisfaction post-processing for linear QoIs (Lee et al.), we restore
> exact-partition Bader charges by the minimum-norm region-sum correction, which for disjoint basins is
> the uniform per-basin shift and is simultaneously Linf- and L2-minimal. Actual Henkelman Bader analysis
> on the decoded fields confirms numerically zero charge error with no basin reassignment."

Also defensible, and probably more interesting:
> "Under an exact partition, Bader charges were not the binding constraint: Hartree-certified streams
> already met the Bader contract, and the projection consumed Hartree budget."

Avoid:
- "novel projection", "new optimal correction", or a theorem-style presentation of the uniform
  shift's optimality as a contribution (cite it as elementary, or as Lee et al.'s construction
  specialized);
- "first post-compression QoI repair" or "first constraint projection for scientific compression"
  (Lee 2022; Banerjee; Compression Safeguards; FFCz);
- any performance claim for the Hartree-aware projection (unexecuted). When it is executed, cite
  Coulomb-metric constrained density fitting as the methodological ancestor;
- "topology-preserving" or "Bader-preserving compression" without the qualifier "exact reference
  partition". Compressing the partition-defining field is the separate B3 problem.

---

## C4: Certifying one stored stream jointly for several downstream QoIs (Hartree + Bader)

Claim under audit: a single QOAC-H stream plus projection and side channel is certified against both
the Hartree contract and the Bader contract.

### Closest prior art

1. **Gong et al. (2022).** Q. Gong, X. Liang, B. Whitney, J. Y. Choi, J. Chen, L. Wan, "Maintaining
   trust in reduction: Preserving the accuracy of quantities of interest for lossy compression," in
   *Smoky Mountains Computational Sciences and Engineering Conference (SMC 2021)*, Commun. Comput. Inf.
   Sci. 1512, 22–39 (Springer, 2022) **[M]**. The DOI is **UNVERIFIED**. It uses MGARD's QoI theory to
   keep **several XGC QoIs** (density, temperature, flux-surface-averaged momenta) accurate, with
   QoI-adapted coefficient quantization.
2. **Lee et al. (2022)** (above). One post-processing step satisfies **multiple** moment constraints
   simultaneously.
3. **Jiao et al. (VLDB 2022) and QPET (VLDB 2025)**, both already in the QOAC-H audit. They cover
   univariate and multivariate QoIs across several families. Whether either derives *one* pointwise
   bound satisfying *several distinct* QoI tolerances at once is **UNVERIFIED** from snippets. The
   natural construction (minimum of per-QoI bounds) is obvious and should be assumed known.
4. **Wu et al. (SC24)** (C1 item 8). It guarantees errors for QoIs "composited by the basis of derivable
   QoIs" and is evaluated with "a diverse set of QoIs" **[M]**. Whether one retrieval simultaneously
   satisfies several QoI bounds is **UNVERIFIED**.
5. **Compression Safeguards (2026)** (C3 item 4). Safeguards for QoIs and regions of interest can be
   **combined with logical combinators**. One corrected stream that satisfies several declared
   properties is therefore an explicit feature of that framework.
6. **FFCz (2026)** (C3 item 5). One corrected stream jointly bounds spatial pointwise error and
   frequency-domain error, two heterogeneous QoIs.
7. **TOPIQ** (QOAC-H audit). It predicts error statistics for several QoIs from one compressed stream,
   but does not certify them.

### What overlaps

- "One compressed representation, several QoIs controlled at once" is established: XGC multi-QoI
  (Gong; Lee), multivariate QoI theory (Jiao; QPET), combinable safeguards, and spatial-plus-spectral
  joint bounds (FFCz).
- Post-decode verification of a QoI on the actual reconstruction is standard practice in this
  literature (trial-and-error baselines, Fixed-PSNR-style checks, safeguards).

### What differs (defensible)

- The QoIs are **heterogeneous in kind**:
  - a global elliptic-operator norm on the reciprocal lattice (Hartree, with a two-sided
    Nyquist-safe certificate);
  - integrals over a topologically defined real-space partition (Bader), certified by the production
    Bader code.

  No retrieved work jointly certifies an operator-norm QoI and a partition-integral QoI for an
  electronic-structure field.
- The program documents the **interaction** between the two certificates: repairing one costs budget
  in the other.

### Constraints from the program's own evidence

- **QOAC-HB confirmatory formally FAILED criterion 4** (median R_J 1.224 vs required 1.25).
  Supported: one stream satisfies both contracts in 50/50 materials, and it beats the best projected
  competitor in 39/50 at a cohort-dependent median ratio of about 1.2–1.6x.
  Not supported: the joint-contract compression advantage at the frozen effect size.
- Because Bader was non-binding before projection, the joint certificate is currently dominated by the
  Hartree contract. Present it as "both contracts verified on one stream," not as a strong
  multi-objective trade-off.

### Verdict C4

Defensible:
> "A single stored density stream was verified against two heterogeneous downstream contracts: a
> reciprocal-space Hartree certificate and exact-partition Bader charges computed by the production
> Bader code. This held in all 50 materials tested. The pre-registered confirmatory effect-size
> criterion for a joint-contract compression advantage was not met (median 1.22x vs 1.25x required)."

Avoid:
- "first multi-QoI certified compression" or "first joint QoI preservation" (Gong 2022, Lee 2022,
  Jiao 2022, Compression Safeguards, FFCz);
- "QOAC-HB outperforms competitors under the joint contract" as a confirmed result (formal FAIL);
- implying that the joint certificate generalizes to "arbitrary downstream QoIs" (B2's own
  interpretation boundary excludes this).

---

## Cross-cutting observations

1. **Every C1–C4 mechanism has a classical or recent ancestor.** RDO and allocation belong to
   Shoham–Gersho, Ortega–Ramchandran and RDOQ. Coding gain belongs to Huang–Schultheiss, Jayant–Noll and
   perceptual coding gain. Low-rate effects belong to Mallat–Falzon and Sullivan. Projection belongs to
   Lee et al., Compression Safeguards and FFCz. Multi-QoI control belongs to Gong, Lee, Jiao and QPET.
   The program's novelty is the **combination, the physical-operator instantiation, and the quantified,
   pre-registered evidence**, not any single mechanism.
2. **The program's own rigour is a differentiator to state openly.** No retrieved QoI-compression work
   reports frozen protocols, disjoint confirmatory cohorts, pre-registered effect-size gates, and
   published NO-GO / FAIL outcomes. This is a positioning statement, not a novelty claim: a reviewer
   may know counterexamples. Phrase it as "we follow a pre-registered protocol," not as "unlike all
   prior work."
3. **The weakest point for reviewers** is that C1's and C2's headline numbers are development-only and
   retrospective respectively. A high-impact submission should either run the frozen fresh-population
   protocol first, or label these numbers explicitly as engineering observations and post-hoc
   diagnosis.
4. **Residual search risk:** native databases (Scholar, Scopus, WoS, IEEE Xplore, ACS) were not
   queried, and no full texts were opened. The highest-risk areas for an unseen close match are:
   - (i) operator-weighted or negative-Sobolev-norm allocation in MGARD follow-ups after 2023
     (BlockMGARD, arXiv:2609.00205, region-of-interest error control, was seen in results but not
     assessed);
   - (ii) the full text of Compression Safeguards (its QoI-safeguard semantics may cover region sums
     exactly);
   - (iii) lossy compression of plane-wave DFT densities in 2025–2026 materials-database work.

## Ranked defensible novelty statements (for a high-impact journal submission)

1. **Diagnosis-to-design for a physical operator, with an optimality check.** "The Hartree operator's
   exact reciprocal-space symbol, which explains the measured codec-dependent Hartree error, defines the
   compression metric. The resulting closed-form allocation comes within about 10% of the exact
   operational rate-distortion optimum (development data), while the same optimizer in an operator-blind
   metric is about 2.2x worse." This builds on the QOAC-H audit and adds the C1 ablation. Requires: the
   frozen fresh-population run, or explicit development labelling.
2. **Cross-operator explanation of effect size from operator symbol and mode geometry.**
   "Classical coding-gain theory, evaluated on the operator symbol and reciprocal-lattice orbit set
   without density data, explains why the Hartree operator yields a roughly twenty-fold advantage while
   the electric field yields at most about 20%." The novelty is the instantiation and its use for
   setting gates. Present it as post-hoc explanation until a prospective test exists.
3. **Heterogeneous joint certification on one stream with documented interaction.** "One stored density
   stream satisfies both a reciprocal-space Hartree certificate and exact-partition Bader charges
   (production Bader code, zero reassignment) in 50/50 materials. The Bader repair consumes Hartree
   budget, which shows that multi-QoI contracts interact." Report the formal confirmatory FAIL alongside
   it.
4. **Exact-partition Bader preservation by minimum-norm projection** (credited to Lee et al.'s
   constraint satisfaction), with production-code certification. This is useful and verifiable, but
   methodologically incremental. Use it as a supporting result, not a headline.
5. **Methodological positioning (not a novelty claim):** pre-registered gates, disjoint confirmatory
   cohorts, and publication of NO-GO / FAIL outcomes for QoI compression.

Wording to avoid everywhere: "first", "novel" (attached to RDO, coding gain, projection or multi-QoI),
"a priori" as a timing claim, "finite-rate theory" (not yet built), "Hartree-aware projection improves…"
(not executed), and "confirmed" for any v0.3 or QOAC-HB rate advantage.
