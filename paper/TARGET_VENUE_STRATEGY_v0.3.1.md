# Target venue strategy — manuscript v0.3.1

Date: 2026-09-06

This ranking assumes the current scientific scope is preserved: one demanding field-derived-domain QoI (Bader charge), a large released benchmark, a validated QoI-resolvability protocol, realized-error statistical controls and a mechanism analysis. It does **not** assume that another QoI or a new topology-aware codec will be added merely to satisfy venue expectations.

## Executive recommendation

### If maximum upside is the priority

1. **Nature Computational Science** — reach submission.
2. **Journal of Chemical Theory and Computation (JCTC)** — strongest technical fit if the reach submission is declined.
3. **Journal of Chemical Information and Modeling (JCIM)** or **Patterns** — strong alternatives depending whether the final emphasis is chemical methodology or cross-domain scientific-data methodology.

### If efficiency / probability of a technically engaged review is the priority

1. **JCTC**.
2. **JCIM**.
3. **Patterns**.
4. **npj Computational Materials** only if the materials/DFT-data-infrastructure framing becomes substantially stronger.

## 1. Nature Computational Science — reach

### Why it fits

The journal explicitly covers computational techniques, algorithms, tools and frameworks across disciplines including computational chemistry and computational materials science. The manuscript's strongest cross-disciplinary thesis is not codec ranking but a general evaluation principle:

> when a downstream observable is defined on field-derived domains, a pointwise reconstruction guarantee is not itself a scientific-fidelity contract.

The released benchmark, validated stability protocol, failure taxonomy and mechanism triangulation give the paper more than a narrow case study.

### Main editorial risk

The direct application is still one downstream chemical QoI. A Nature Computational Science editor may ask whether the conceptual advance is sufficiently general beyond Bader partitioning or whether the paper belongs in a specialist computational-chemistry journal.

### How to pitch without new science

Lead with the general three-layer framework:

`field guarantee -> QoI resolvability -> re-derived downstream fidelity`

Then present Bader charge as an unusually stringent exemplar because the field defines both the integrand and its integration domains.

Do **not** lead with “SZ3 versus ZFP versus SPERR.”

### Should we add a second QoI solely for this journal?

No. A late weak second QoI can dilute the mechanism story. Submit the coherent paper first if the upside is worth the desk-rejection risk. A genuinely independent second field-derived-domain observable would be better treated as future generalization unless it is already available cheaply and scientifically motivated.

## 2. Journal of Chemical Theory and Computation — best technical fit

### Why it fits especially well

JCTC explicitly welcomes advances in computational methodology and data science relevant to chemistry and materials science, including DFT and electronic-structure workflows. The present work is not a straightforward application of DFT; it develops and validates a methodology for deciding when compressed electronic-structure data preserve a downstream chemical analysis.

The fit is strengthened by very recent JCTC literature on electron-density fidelity. Gong, Zhao and Tang (2026; DOI `10.1021/acs.jctc.6c01124`) identify a downstream-fidelity gap for machine-learned electron densities caused by real-space integration/grid issues and introduce adaptive integration. That paper is adjacent but distinct: the present manuscript isolates compression-induced migration of field-derived Bader domains and adds explicit QoI-resolvability certification.

### Likely reviewer strengths

A JCTC reviewer is more likely than a generic data-compression reviewer to understand why:

- Bader atom identity matters;
- a max-atom error contract is chemically conservative;
- re-partitioning is essential;
- a symmetry-equivalent basin permutation is a special pathology rather than ordinary charge redistribution;
- a protocol-defined numerical resolvability floor matters before certification.

### Main reviewer risk

They may ask whether three compression algorithms are sufficient, or whether a topology/local-order-preserving comparator should be included after the mechanism is identified.

Current response: the paper asks whether **general-purpose pointwise guarantees** are sufficient, not whether every modern topology-aware compressor is optimal. Recent topology/order-preserving methods belong in Related Work and are natural future tests of the released benchmark. A compatible topology-aware codec can be added as supplementary validation if trivial to run, but is not required for the evaluation claim.

### Current recommendation

**Best first submission if we want the highest probability that the paper is judged on its actual chemical/computational methodology rather than on whether it is broad enough for a general computational-science journal.**

## 3. Journal of Chemical Information and Modeling — strong alternative

### Why it fits

JCIM explicitly covers chemical informatics, molecular modeling, computer-science techniques applied to chemical problems, computational methods and efficient algorithms/software. The benchmark/data-release/reproducibility component and compression methodology can be emphasized naturally.

### Why it is slightly less direct than JCTC

The current scientific center of gravity is electron-density/Bader fidelity and numerical methodology rather than molecular representation, chemical databases or informatics in the narrower sense. JCIM is credible, but JCTC is a cleaner intellectual home for a DFT-derived field and numerical-analysis contract.

### Best framing for JCIM

Emphasize:

- released chemical-data benchmark;
- reproducible Protocol A.1;
- compressor evaluation methodology;
- machine-readable failure registry and provenance;
- implications for scalable storage/analysis of electronic-structure data.

## 4. Patterns — cross-domain data-science alternative

### Why it fits

Patterns publishes data-science research across computational, physical and life sciences and values reusable research outputs. The manuscript has several features attractive to that audience:

- a general scientific-data evaluation framework;
- a benchmark with full provenance;
- explicit reproducibility/failure semantics;
- a lesson about why raw-data metrics do not necessarily certify downstream analysis;
- open methodology that can be transferred to other field-derived QoIs.

### Main weakness

The paper's strongest mechanistic insight is chemical and Bader-specific. For Patterns, the introduction and discussion would need to foreground the general data-science contract more strongly and reduce specialist codec details in the narrative.

## 5. npj Computational Materials — plausible but not first choice

### Why it can fit

The journal covers significant development and application of computational techniques in materials science. The corpus contains bulk/slab electronic-structure data and the method is relevant to large-scale computational-materials data infrastructure.

### Why it is not currently the cleanest fit

The paper does not discover, design or explain a material property. Its central contribution is a scientific-data fidelity methodology. Without a stronger materials-science consequence, JCTC/JCIM/Nature Computational Science/Patterns are more direct homes.

## Venues I would not prioritize for the current paper identity

### Pure data-compression / systems venues

A compression venue may reasonably expect a new compressor, throughput innovation or formal guarantee. This manuscript primarily supplies an evaluation contract and chemical failure mechanism. Those communities remain important related work, but they are not automatically the best editorial home.

### Pure materials-discovery journals

The current result is about integrity of computational data and downstream interpretation, not a new material or material-property prediction. Reframing it as discovery would weaken the paper.

## Recommended sequential strategy

### Strategy A — upside-first

1. Submit the scientifically frozen paper to **Nature Computational Science** with a general computational-science cover letter.
2. If declined editorially, make only editor/reviewer-informed positioning changes, not new unfrozen benchmark choices.
3. Submit to **JCTC** with the chemical-fidelity and electron-density methodology foregrounded.
4. Use **JCIM** or **Patterns** as the next branch depending the feedback received.

### Strategy B — efficiency-first

1. Submit directly to **JCTC** after the per-atom Figure 3 audit and final figure polish.
2. If the main objection is “more informatics/data-platform than theory,” move to **JCIM**.
3. If the objection is “too chemistry-specific but strong data-science principle,” adapt to **Patterns**.

## What changes by venue — and what must not change

### Can change

- title emphasis;
- abstract opening sentence;
- order and density of codec implementation detail;
- prominence of benchmark/resource aspects;
- cover letter and significance paragraph;
- figure typography/layout according to journal style.

### Must remain scientifically fixed

- Protocol A.1 thresholds/seeds/eligibility semantics;
- primary max-atom Bader endpoint;
- realized-L∞ matching rule and complete-case sensitivity;
- distinction between direct representative-set mechanism evidence and full-table attenuation;
- NON_EVALUABLE versus codec failure;
- no universal codec winner;
- no causal interpretation of codec coefficients;
- no claim that generic QoI-fidelity concerns are novel.

## Venue-specific one-line pitches

### Nature Computational Science

> Scientific compression needs contracts at the level of downstream analysis: in electron-density data, bounded field error can move field-derived atomic domains, while the observable itself may be too numerically unstable to certify at the requested precision.

### JCTC

> We establish when error-bounded compression of DFT electron densities preserves Bader charges, separating numerical resolvability, realized reconstruction magnitude and compression-induced migration of atomic integration domains.

### JCIM

> A reproducible benchmark and stability-qualified protocol show how to certify lossy compression of electronic-structure data against downstream atomic-charge analyses rather than raw-grid error alone.

### Patterns

> A downstream scientific quantity cannot be certified from raw-data error alone when its analysis domains are derived from the reconstructed field; we provide a reproducible evaluation contract and benchmark that separates data error, task resolvability and analysis failure.

## Current recommendation before the per-atom file lands

Do not decide the final venue by adding new calculations. Finish the preregistered per-atom audit, polish Figures 1–6 and then choose between:

- **Nature Computational Science first** if maximizing upside is worth a likely higher editorial-screen risk;
- **JCTC first** if maximizing fit and technically informed peer review is the priority.
