<!-- Full-text prior-art check, 2026-10-12. Written by a partner agent (Codex) from the open-access full texts; reviewed in the main session, which re-read the key passages (Safeguards p. 12 combinators and p. 33 "spectral error safeguard in the future"; BlockMGARD reciprocal mentions are throughput and quantizer arithmetic). PDFs are not committed (copyright); SHA-256 values identify them. -->

# Full-text prior-art check for the QoI manuscript

Checked 2026-10-12. The manuscript was read read-only at `paper/MANUSCRIPT.md`, including the Introduction and Discussion sentences citing references 8-19 and the reference entries themselves. Page numbers below are the printed page numbers, which match the PDF page indices for all three PDFs.

## 1. Papers obtained and validated (numbers first)

| item | manuscript relationship | local PDF | full text | PDF pages | title page / validity check |
|---|---|---|---:|---:|---|
| Compression Safeguards | manuscript ref. 15 | `pdf/compression_safeguards.pdf` | yes | 110 | title, author block, abstract and DOI on p. 1; valid readable PDF; reused the pre-existing 59 MB file |
| Lee et al. 2022 | manuscript ref. 12 | `pdf/lee_2022.pdf` | yes | 21 | title, seven-author block, citation and DOI on p. 1; valid readable PDF |
| BlockMGARD | not currently cited | `pdf/blockmgard.pdf` | yes | 14 | title, eight-author block, arXiv ID and SC26 header on p. 1; valid readable PDF |

All three full texts were obtained without login or credentials. The Compression Safeguards landing page reports a 58,007 KB preprint, consistent with the existing local file. Local SHA-256 records are:

| local file | bytes | SHA-256 |
|---|---:|---|
| `compression_safeguards.pdf` | 59,399,172 | `5F4011BC08E78EF4B61355E9EF1C77AAA7B2928A0A2F07C7B89FEB8D9AF40A0D` |
| `lee_2022.pdf` | 1,578,742 | `E03BC1E07D0394CFC299F84499624E8BD251461AAA488E5DC1048EBAB6B5FEED` |
| `blockmgard.pdf` | 3,605,006 | `5D9D52231C4D2FDFDF92099074FB907F938038338DFC3C9C1EAF072BC07813EC` |

Sources used for acquisition and metadata:

- Compression Safeguards: [EGUsphere landing page](https://egusphere.copernicus.org/preprints/2026/egusphere-2026-4266/) and [Copernicus preprint PDF](https://egusphere.copernicus.org/preprints/2026/egusphere-2026-4266/egusphere-2026-4266.pdf).
- Lee et al. 2022: [MDPI article page](https://www.mdpi.com/2076-3417/12/13/6718), DOI [10.3390/app12136718](https://doi.org/10.3390/app12136718), and the official [MDPI PDF asset](https://mdpi-res.com/d_attachment/applsci/applsci-12-06718/article_deploy/applsci-12-06718.pdf?version=1656753351).
- BlockMGARD: [arXiv abstract page](https://arxiv.org/abs/2609.00205), [arXiv PDF](https://arxiv.org/pdf/2609.00205), and the [OpenAlex title search](https://api.openalex.org/works?search=BlockMGARD&per-page=25).

## 2. Verdicts at a glance

| question | verdict |
|---|---|
| a | CONFIRMED, with a one-shot rather than convergence-loop qualification |
| b | CONFIRMED |
| c | NOT FOUND |
| d | NOT FOUND |
| e | CONFIRMED |
| f | CONFIRMED, with exact Bregman/generalized-KL terminology |
| g | CONFIRMED |
| h | NOT FOUND |
| i | DIFFERS: generic ROI/tolerance-allocation overlap, but no Hartree/operator-symbol overlap |
| j | CONFIRMED: cite in the Introduction in the MGARD/ref. 8 context |

## 3. Answers and evidence

### a. Compression Safeguards: decoded-data correction and the kinds of bounds

**Verdict: CONFIRMED, with a one-shot qualification.**

**Evidence.** On p. 5, Section 2, the framework is defined as checking the user requirement and producing pointwise binary corrections applied to the lossy-decompressed approximation. On p. 6, Sections 2.1-2.2, the workflow is: compress, decompress, check, compute corrected data, encode the correction, and check the correction again; the correction is then applied during decompression. Thus it functionally guarantees the declared bound on the corrected decoded field. The normal algorithm is a validated one-shot correction, not an iterative numerical solve that keeps recomputing a correction until convergence. The optional iterative mode described on p. 13, Section 3.5, reduces or skips some already computed corrections; it is not the primary correction mechanism.

The paper supports the following bound classes:

- **Pointwise data bounds:** maximum absolute, relative and ratio error, p. 11, Section 3.2.
- **Derived QoI bounds:** pointwise and stencil QoIs with absolute, relative or ratio error bounds, p. 12, Section 3.4. The implementation also covers finite-difference/stencil quantities, comparisons, classifications, isosurfaces, sign/value preservation, missing values and regionally varying requirements, with examples discussed on pp. 12-13 and in Section 5.
- **Global or regional requirements in principle:** the framework uses broad language about local, regional and global safety requirements on pp. 3 and 8, but that statement is not a demonstrated reciprocal-space or physical global-operator implementation.
- **Spectral/frequency-weighted bounds:** not found. There is no Poisson/Hartree potential, reciprocal-space symbol, Fourier weighting, or frequency-dependent quantization-step law in the paper.

**Short quote (p. 6, Section 2.1):** “the corrected data is guaranteed to satisfy them”.

**Suggested wording change:** none required for the manuscript's statement that ref. 15 enforces bounds through post-correction. If the word `until` is used elsewhere, the literal mechanism should be described as a correction followed by validation, normally in one shot.

### b. Compression Safeguards: combining several safeguards or QoIs on one stream

**Verdict: CONFIRMED.**

**Evidence.** The reference implementation has an explicit composition section: p. 10, Section 3.1, introduces composition with safe intervals; p. 11, Section 3.3, provides logical and regional compositions; and p. 12, Section 3.3, defines `any`, `all` and `select` combinators over pointwise and stencil safeguards. The numcodecs frontend described on p. 13, Section 3.5, can place the compressed data, losslessly compressed corrections and checksum in one combined byte stream. The xarray frontend on p. 14, Section 3.6, can instead keep corrections separate for chunked workflows, so `one stream` is an available frontend representation rather than a requirement of every storage mode. The capability is explicit even though the reported evaluation mostly exercises individual examples rather than a Hartree-plus-Bader-style multi-physics contract.

**Short quote (p. 12, Section 3.3):** “can combine over both pointwise and stencil safeguards”.

The manuscript's phrase `combinable safeguards` is substantively accurate. `Composable safeguards` would be closer to the paper's own terminology, but this is a style refinement, not a factual correction.

### c. Compression Safeguards: global linear-operator QoIs and spectral allocation

**Verdict: NOT FOUND.**

**Evidence.** The paper mentions global requirements generically in Section 1 (p. 3) and says that binary corrections can handle local, regional or global safety requirements in Section 2.3 (p. 8). However, its concrete QoI implementation on p. 12, Section 3.4, is described in terms of pointwise and stencil expression-tree propagation; pp. 15-17, Section 4 and Tables 1-2, likewise characterize the implementation by pointwise/stencil QoIs, symbolic/numeric interval analysis and combinators. The evaluated examples are weather/climate quantities such as finite differences, kinetic energy, vorticity, Laplacian and dSSIM, not a Poisson or Hartree potential. No reciprocal-space weighting, frequency allocation, electronic-structure field or Δ(G) proportional to |G|^2 rule appears in the full text.

**Short quote (p. 12, Section 3.4):** “pointwise absolute, relative, and ratio error bounds over both pointwise and stencil QoIs”.

This is an absence of a demonstrated prior art instance, not proof that a sufficiently general future safeguard API could never encode a global scalar function. The manuscript's specific reciprocal-space-operator novelty claim is not displaced by ref. 15.

### d. Compression Safeguards: pre-scoring resolution/capability test analogous to QSQ

**Verdict: NOT FOUND.**

**Evidence.** The safeguard workflow checks the decoded approximation against the declared safety requirement after compression and then validates the generated correction (p. 6, Sections 2.1-2.2). Section 3.4 (p. 12) says that QoIs are evaluated in a configurable floating-point type chosen to represent the input accurately; this is a numerical evaluation-precision choice, not a perturbation-based stability floor. The paper contains no QSQ-like probe panel, no reference-analysis capability test before compression scoring, no eligible/non-evaluable state based on the reference analysis, and no estimate of fresh exceedance risk before compression. Its experiments in Section 5 (pp. 19 onward) score safeguard violations after compression.

**Short quote (p. 12, Section 3.4):** “The quantities of interest are evaluated using numpy in a configurable floating-point data type”.

The manuscript's contrast that prior approaches do not by themselves establish whether a numerical reference can resolve its tolerance remains supported for ref. 15.

### e. Compression Safeguards: author list and year

**Verdict: CONFIRMED.**

**Evidence.** The complete title and author block are on p. 1. The order and names are:

Juniper Tyree; Robert Underwood; Clément Bouvier; Daniel Köhler; Tim Reichelt; Peter Dueben; Sara Faghih-Naini; Heikki Järvinen; Milan Klöwer.

The title page carries the 2026 preprint DOI/footer, and the official EGUsphere landing-page citation gives the same nine-author list and year 2026. Manuscript ref. 15 therefore matches the paper's title, author group and year; the lower-case `trust` in the manuscript title is only capitalization.

**Short quote (p. 1, title block):** “Compression Safeguards: Building Trust into Lossy Data Compression”.

**Suggested wording change:** none.

### f. Lee et al. 2022: constraint satisfaction, preserved quantities and objective

**Verdict: CONFIRMED, with exact Bregman/generalized-KL terminology.**

**Evidence.** On p. 7, Section 3.2, constraint satisfaction is applied to the reconstructed primary data after residual post-processing, not during autoencoder training. On p. 8, Section 3.2.1, the generic problem is an equality-constrained optimization, minimizing a distance from the decompressed output \(f^0\) subject to \(h(f)=0\). For XGC, the constraint system uses the true density to linearize the relevant expressions and obtains four independent per-node moment constraints on p. 9: density, parallel-flow moment, perpendicular kinetic-energy moment and parallel kinetic-energy moment (the latter is the rewritten/modified parallel-temperature quantity). The application description on pp. 4-5 also names density, parallel flow, perpendicular and parallel temperatures, plus flux-surface-averaged density and temperature.

The chosen objective is not an \(L_2\) or \(L_\infty\) norm. Equation (21), p. 9, uses the Bregman divergence generated by \(\phi(f)=f\log f\), namely the generalized relative-entropy/KL or I-divergence form

\[
D_\phi(f\,\|\,f^0)=\sum_{i,j}\left[f_{ij}\log\left(\frac{f_{ij}}{f^0_{ij}}\right)-f_{ij}+f^0_{ij}\right]
\]

after a small positive ReLU floor makes the histogram entries positive. The authors call it a Bregman divergence for the \(f\log f\) entropy function; they do not literally label it `Kullback-Leibler` in the article. Newton optimization of the dual obtains Lagrange multipliers on p. 10, and those multipliers are quantized with an explicit PD/QoI error analysis on pp. 10-11.

**Short quote (p. 9, Section 3.2.1):** “the Bregman divergence for the f log f entropy function”.

Thus the manuscript's description of an entropy-divergence correction applied to XGC velocity moments is accurate. For maximum literal precision, `generalized KL/I-divergence generated by f\log f` is preferable to treating it as an unspecified entropy penalty, but no substantive change is required.

### g. BlockMGARD: what it does

**Verdict: CONFIRMED.**

**Evidence.** The p. 1 abstract and Section I describe BlockMGARD as a GPU lossy compressor with region-of-interest (ROI) support. Section IV (p. 4) gives the pipeline: In-cache Block decomposition, global MGARD decomposition, quantization with ROI error control and lossless encoding. Section IV-A (pp. 4-5) uses fixed 8 x 8 x 8 blocks in GPU shared memory with compile-time index tables. Section IV-B (pp. 5-6) combines L local block levels and M global MGARD levels and chooses configurations under a time budget. Section IV-C (pp. 6-8) maps multiple ROI tolerances to blocks and propagates the strictest tolerance conservatively across hierarchy boundaries; Section IV-D (p. 8) fuses local decomposition and quantization. It evaluates five HPC simulation datasets against MGARD-X, cuZFP and VGC, emphasizing throughput, compression ratio, raw reconstruction error and ROI visual fidelity.

**Short quote (p. 1, abstract):** “fine-grained, ROI error control for feature preservation”.

### h. BlockMGARD: derived QoIs, operator norms and MGARD smoothness (s)

**Verdict: NOT FOUND.**

**Evidence.** The paper's Section II-B (p. 3) states that MGARD as a prior method can extend error bounds to derived QoIs, but this is background about MGARD, not a BlockMGARD QoI experiment or a BlockMGARD operator-norm formulation. BlockMGARD's own evaluation in Section V-A (p. 8) uses a relative L-infinity raw-reconstruction bound at 10^-2, 10^-4 and 10^-6; its ROI mode changes the spatial tolerance map, not the downstream quantity being measured. The conclusion (p. 12, Section VI) again claims block-granularity ROI control guaranteeing L-infinity bounds. The paper contains no Hartree/Poisson QoI, no operator norm, no Sobolev smoothness parameter s, and no MGARD-s-style derived-quantity allocation.

**Short quote (p. 8, Section V-A):** “our evaluation is based on the L∞-norm relative error bound”.

### i. BlockMGARD: overlap with the QoI manuscript's claims

**Verdict: DIFFERS, with limited generic overlap.**

**Evidence.** There is a real but general overlap: both use a multilevel MGARD-style decomposition and nonuniform error allocation. BlockMGARD assigns spatially varying raw-data tolerances to ROI blocks and, on pp. 7-8, Section IV-C, propagates the strictest block tolerance through local levels; its global-level budget is then distributed uniformly across the M global levels. This is a GPU/hierarchy and ROI allocation mechanism. It is not allocation from a downstream physical operator symbol.

The full BlockMGARD text has no Hartree or Poisson potential, no electronic-structure density, no reciprocal-space G, no Fourier/spectral weighting, no Delta(G) proportional to |G|^2 law, and no QSQ-like reference-resolution gate. Its only frequency-adjacent statement is that a dataset's high-frequency content can make block-boundary artifacts more visible in the compression-ratio results (p. 9, Section V-C); that is not frequency-dependent step-size allocation.

**Short quote (p. 7, Section IV-C):** “strictest tolerance among all fine-level blocks”.

**Suggested wording change/addition.** Add the following sentence in the Introduction immediately after the ref. 8/MGARD context, if the authors want the related-work boundary to be explicit:

> Contemporaneous GPU work such as BlockMGARD instead assigns spatially varying raw-data tolerances to ROI blocks and propagates the strictest tolerance through a hybrid MGARD hierarchy; it does not use a downstream physical operator or a reciprocal-space symbol.

No change is needed to the manuscript's specific claim that the present Hartree allocation is derived from the physical reciprocal-space operator.

### j. Whether to cite BlockMGARD and where

**Verdict: CONFIRMED: cite it in the Introduction, in the ref. 8/MGARD related-work context.**

**Exact bibliographic record.**

Yanliang Li, Qian Gong, Qing Liu, Jaemoon Lee, Norbert Podhorszki, Scott Klasky, Xin Liang, and Jieyang Chen, *BlockMGARD: Accelerating Adaptive Scientific Data Reduction with Region-of-Interest Error Control on GPUs*, SC26 (IEEE/ACM International Conference for High Performance Computing, Networking, Storage and Analysis), 2026, arXiv:2609.00205v1, DOI [10.48550/arXiv.2609.00205](https://doi.org/10.48550/arXiv.2609.00205).

The first page identifies the SC26 conference manuscript and gives the conference dates as 15-20 November 2026; as of this check date, the safe bibliographic label is an arXiv preprint/SC26 conference manuscript rather than an already completed proceedings publication. OpenAlex returned one exact paper match, W7207880371, and a separate software artifact titled `MasterVChicken/MGARD: sc26-BlockMGARD-v1` (W7154949799, Zenodo DOI 10.5281/zenodo.19656827); the latter is not a second paper and is excluded from the paper list.

**Short quote (p. 4, Section IV):** “a hybrid hierarchy that combines L local In-cache Block levels with M global levels”.

**One-sentence reasoning.** Cite BlockMGARD in the Introduction because it is adjacent MGARD-based GPU/ROI raw-error work that a reader may expect in the compression background, while its lack of a physical downstream operator means it does not need to be used as a Discussion comparator for the Hartree/QSQ claims.

**Suggested citation sentence:**

> Recent GPU-oriented MGARD work has combined block-local and global decomposition with ROI-level raw-error control and conservative tolerance propagation (Li et al., 2026).

## 4. Bottom-line manuscript impact

- Ref. 15's author list, year and post-correction/composition description are supportable. The paper does not supply the manuscript's reciprocal-space Hartree allocation or QSQ qualification.
- Ref. 12's entropy-divergence wording is supportable; the exact objective is an f log f-generated Bregman/generalized-KL divergence, and the exact XGC constraints are velocity-histogram moments rather than an electronic-structure operator.
- BlockMGARD should be added as adjacent GPU/ROI/MGARD prior art in the Introduction. It does not require weakening the manuscript's specific Hartree-symbol, frequency-allocation or QSQ claims.

No file under `this repository` or any other repository was edited. The only intended outputs in this working folder are this report and the three PDFs under `pdf\`.
