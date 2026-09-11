# Reference integration patch — 2026-09-11

This file records the citation edits to apply to `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md` after expanding the canonical bibliography to 21 references. It is intentionally narrow: it strengthens literature positioning without changing the frozen scientific claims or numerical results.

## 1. Introduction: first paragraph

Replace the final two sentences of the opening paragraph with:

> Error-bounded lossy compression has become a mature strategy for reducing scientific floating-point data while retaining explicit reconstruction constraints [1–5,18]. Compression has also entered quantum-chemistry and electronic-structure workflows, including GAMESS integral data and recent lossy reduction of DFT atomic-orbital spaces [3,19,21]. Yet a field-level error bound does not, by itself, define the fidelity of every scientific quantity subsequently extracted from the reconstruction.

Purpose: establish both the mature compression context and direct chemistry/electronic-structure relevance without implying that prior work already studied Bader-certifiability of stored real-space electron-density fields.

## 2. Introduction: QoI prior-art paragraph

Replace the current QoI-prior-art paragraph with:

> Scientific-compression research has increasingly moved from generic distortion metrics toward downstream quantities of interest. Mathematical multilevel methods can provide quantitative error control for classes of derived quantities [12], while application-specific pipelines have preserved or constrained QoIs in large scientific workflows [6,13,14,20]. Topology-aware compressors further show that strict pointwise bounds do not ensure preservation of discrete scientific structure [7,15], and recent work has begun to predict QoI-level bias and uncertainty directly [11]. These advances establish that downstream fidelity matters. They leave a logically prior question unresolved: **when is the requested QoI tolerance itself a valid benchmark?**

Purpose: make the novelty boundary much harder for a reviewer to attack. The manuscript now explicitly acknowledges both theory and end-to-end QoI-preserving systems.

## 3. Introduction: Bader/QTAIM paragraph

Replace the first two sentences of the current Bader paragraph with:

> Bader charge provides a stringent chemical test of this principle. In the quantum theory of atoms in molecules, atomic basins are defined by the topology of the electron-density gradient field [17]. Practical grid-based algorithms have progressively addressed robustness, lattice bias and integration accuracy [8,9,16], while modern arbitrary-grid treatments make the role of discretization and numerical topology explicit [10].

Continue with the existing sentence beginning:

> A perturbation can therefore change both the density values being integrated...

Purpose: distinguish the foundational QTAIM concept from numerical implementations and convergence literature.

## 4. Results: Protocol A.1 probe section

At the end of the first paragraph of `A valid stability probe must excite the numerical failure mode`, add citations to the established grid/topology literature:

> This behaviour is consistent with the fact that grid-based basin assignments depend on local gradient/topological structure rather than solely on a scalar norm of the perturbation [9,10,16].

Purpose: support the mechanistic plausibility of the probe correction without claiming the literature previously demonstrated the exact Protocol A → A.1 failure mode.

## 5. Discussion: prior-work positioning paragraph

Replace the second Discussion paragraph with:

> This result extends, rather than repeats, established QoI-aware compression work. Prior studies have developed mathematical bounds for derived quantities, application-specific QoI-preserving pipelines, and explicit topological guarantees under lossy compression [6,12–15,20]. Recent work has additionally begun to predict QoI-level uncertainty after compression [11]. Our framework adds a logically prior step: before a QoI error is propagated, constrained or compared with a target tolerance, the target must be shown to lie above the numerical resolution of the reference analysis. This separates a **measurement question**—is the QoI identifiable at the requested scale?—from a **compression question**—conditional on that identifiability, does the reconstruction satisfy the contract? Only the second question supports attribution of failure to the codec.

Purpose: explicitly position the paper after, rather than against, mature QoI-aware compression.

## 6. Discussion: chemistry/electronic-structure context

After the paragraph discussing Bader-specific mechanism, add one short sentence:

> Lossy compression has already proved useful in quantum-chemistry and DFT workflows [19,21], but those studies optimize different representations and scientific targets; they do not address whether a downstream charge-partitioning tolerance is itself numerically eligible for benchmark scoring.

Purpose: show that the paper is aware of chemistry-domain compression while preserving the distinction between representation compression and downstream Bader certification.

## 7. Methods: Bader references

Change:

> Bader partitioning assigns grid points to atom-centred basins defined by the density topology [8–10].

To:

> Bader partitioning assigns space to atom-centred basins defined by the topology of the electron density [17]; practical grid-based implementations and integration schemes are described in Refs. [8–10,16].

Purpose: cite the foundational theory separately from the numerical algorithms used to motivate the stability analysis.

## 8. Reference footer

Change:

> This draft uses references [1–11] from that file.

To:

> This draft uses references [1–21] from that file.

## 9. Newly added high-value references

- [12] Ainsworth *et al.* — mathematical control of derived quantities in MGARD; peer-reviewed SIAM J. Sci. Comput.
- [13] Gong *et al.* — QoI-preserving scientific reduction in a large fusion workflow.
- [14] Lee *et al.* — learned scientific compression with derived-quantity preservation.
- [15] Gorski *et al.* — 2025 general framework for adding topological guarantees to lossy compressors.
- [16] Yu & Trinkle — accurate Bader charge integration and convergence.
- [17] Bader — foundational QTAIM reference.
- [18] Cappello *et al.* — scientific lossy-compression use cases, including chemistry/HPC context.
- [19] Lara *et al.* — 2026 JCTC lossy compression in a DFT atomic-orbital representation; adjacent, not equivalent, prior art.
- [20] Banerjee *et al.* — scalable QoI-guaranteeing compression pipeline.
- [21] Gok *et al.* — PaSTRI error-bounded lossy compression for GAMESS two-electron integrals.

## 10. Submission positioning after this update

The literature story should now read as:

`generic error-bounded compression → QoI-aware guarantees → topology-aware guarantees → established Bader/QTAIM numerical sensitivity → chemistry/electronic-structure compression → this work: numerical eligibility before codec scoring`

The strongest defensible novelty sentence remains:

> **We do not introduce the idea that downstream QoIs matter; we show that a QoI tolerance must itself be numerically qualified before it can define a valid pass/fail compression benchmark.**

Do not claim that this work is the first use of lossy compression in electronic structure, the first QoI-aware compressor, the first topology-sensitive compression study, or the first observation of Bader grid sensitivity.