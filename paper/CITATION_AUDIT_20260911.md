# Citation audit for `MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md`

**Audit date:** 2026-09-11  
**Reference universe:** `paper/REFERENCES.md`, refs. 1–21  
**Scope:** Introduction, Discussion, and Methods claims most likely to be scrutinized for prior-art positioning, missing attribution, miscitation, or citation dumping.

## Audit outcome

**Status: PASS with conservative novelty framing.**

All 21 canonical references are now used in the polished manuscript for a defined evidentiary purpose. The revised citation structure deliberately avoids using the 2026 TOPIQ preprint as the sole support for any foundational claim, avoids presenting established Bader/grid sensitivity as novelty, and avoids describing adjacent quantum-chemistry compression papers as prior work on real-space electron-density-field compression.

The central novelty boundary remains:

> Prior work establishes error-bounded scientific compression, QoI-aware error control, topology-aware compression, and numerical sensitivity in grid-based downstream analysis. The present contribution is the **pre-certification eligibility step**: testing whether a requested downstream tolerance is numerically identifiable on the reference data before that tolerance is used to assign codec success or failure.

## Claim-level audit

| Manuscript claim | Final citation(s) | Audit decision |
|---|---:|---|
| Error-bounded lossy compression is mature scientific-data infrastructure; ZFP, SZ3 and SPERR are representative codecs used here. | [1–4] | Appropriate. Survey + primary codec papers. Four references are justified because three named codecs require three primary citations. |
| Lossy compression reduces storage/I/O burdens in scientific workflows. | [18] | Appropriate. Broad scientific-use-case paper; no need to attach all codec references again. |
| Quantum-chemistry/electronic-structure workflows already contain lossy-compression work. | [3,19,21] | Appropriate with object-level qualification. SZ3 includes GAMESS use cases; PaSTRI compresses two-electron integrals; Lara et al. compress an AO/NAO representation. None is described as real-space density-field compression. |
| Post-compression scientific-data assessment is established. | [5] | Appropriate. Z-checker is used only for the assessment-framework claim. |
| QoI-aware compression/error control is established prior art. | [6,12] | Appropriate. Jiao et al. + Ainsworth et al. carry the theoretical/mathematical burden. |
| Application-specific pipelines preserve or guarantee QoIs. | [13,14,20] | Appropriate. These are separated from the mathematical QoI-control papers rather than bundled into one citation dump. |
| Pointwise error bounds need not preserve selected topological descriptors; explicit topology guarantees exist. | [7,15] | Appropriate. The text specifies selected topological descriptors and does not imply Bader preservation. |
| QoI-level bias/uncertainty prediction is emerging. | [11] | Appropriate only as recent context. The manuscript labels this as recent statistical work; foundational claims remain anchored by peer-reviewed [6,12–15,20]. |
| QTAIM/Bader basins are defined by electron-density topology. | [17] | Appropriate. Foundational monograph carries the conceptual definition. |
| Grid-based Bader analysis has established numerical issues involving basin assignment/integration, lattice bias and convergence. | [8–10,16] | Appropriate. Primary algorithm and modern numerical/topological treatments. This background is explicitly not claimed as novel. |
| Codec-specific control mechanisms mean equal nominal settings are not automatically comparable across codecs. | [1–4] | Appropriate as contextual support; the actual realized-distortion asymmetry is an internal empirical result and therefore does not require an external citation. |

## Reference-by-reference usage map

1. **Di et al., survey** — broad error-bounded scientific-compression context; also supports codec-comparison context.
2. **Lindstrom, ZFP** — primary ZFP method citation in Introduction/Methods.
3. **Liang et al., SZ3** — primary SZ3 citation; also supports GAMESS application context.
4. **Li et al., SPERR** — primary SPERR method citation.
5. **Tao et al., Z-checker** — post-compression assessment framework.
6. **Jiao et al.** — rigorous QoI-preserving compression prior art.
7. **Yan et al., TopoSZ** — topology preservation beyond pointwise bounds.
8. **Henkelman et al.** — practical Bader decomposition algorithm.
9. **Tang et al.** — lattice-bias-aware grid Bader analysis.
10. **Hutcheon & Teale** — arbitrary-grid topological analysis and numerical/discretization context.
11. **Liu et al., TOPIQ** — recent QoI bias/uncertainty propagation context only.
12. **Ainsworth et al.** — mathematical error control for derived quantities.
13. **Gong et al.** — application-specific QoI-preserving scientific-data reduction.
14. **Lee et al.** — learned error-bounded compression with derived-quantity preservation.
15. **Gorski et al.** — general augmentation framework for topological guarantees.
16. **Yu & Trinkle** — accurate Bader basin integration and convergence.
17. **Bader monograph** — foundational QTAIM definition of atomic basins.
18. **Cappello et al.** — broad scientific lossy-compression use cases, storage/I/O motivation.
19. **Lara et al.** — recent adjacent DFT lossy-compression work; explicitly identified as AO-basis compression rather than electron-density-field compression.
20. **Banerjee et al.** — scalable compression pipeline with QoI guarantees.
21. **Gok et al., PaSTRI** — quantum-chemistry two-electron-integral compression context.

## Introduction audit

### What changed

The literature is now introduced in functional layers rather than as a long undifferentiated citation bundle:

1. **Scientific-compression maturity and codecs:** [1–4,18].
2. **Domain-specific chemistry/electronic-structure precedent:** [3,19,21].
3. **QoI-aware mathematical control:** [6,12].
4. **QoI-preserving scientific pipelines:** [13,14,20].
5. **Topology-aware guarantees:** [7,15].
6. **Emerging QoI uncertainty prediction:** [11].
7. **Bader/QTAIM foundations and numerical analysis:** [8–10,16,17].

This ordering lets the novelty question appear only after the strongest competing prior art has been acknowledged.

### Missing-citation check

No major external factual claim in the Introduction remains unsupported. The paragraph defining the paper's proposed eligibility logic is intentionally uncited because it states the present study's conceptual framework rather than a claim about prior literature.

### Miscitation check

- [19] is no longer vulnerable to being read as prior electron-density-field compression; the compressed object is named explicitly as the atomic-orbital representation.
- [7,15] are not described as Bader-preserving methods.
- [11] is not used to establish the historical existence of QoI-aware compression.
- [8–10,16,17] are used to acknowledge established Bader/QTAIM numerical structure rather than to imply a new discovery.

### Citation-dumping check

No Introduction sentence carries more than four citations. Multi-reference groups correspond to distinct named methods or a tightly defined literature family. The prior-art paragraph is deliberately split into theory, workflow, topology, and uncertainty sentences.

## Discussion audit

### What changed

The earlier sentence citing `[5–7,11]` for all QoI-aware prior art was too coarse. It mixed assessment, QoI preservation, topology preservation, and uncertainty prediction into one bundle and omitted several directly relevant works. It has been replaced by four claim-specific sentences:

- mathematical QoI control: [6,12];
- operational QoI-preserving pipelines: [13,14,20];
- topology-aware methods: [7,15];
- recent statistical QoI prediction: [11].

This makes the novelty boundary auditable and reduces the chance that a reviewer interprets the manuscript as overlooking closely related work.

The Bader mechanism paragraph now cites [17] for the conceptual topology and [8–10,16] for grid-based implementation/numerical integration. The codec-comparison paragraph cites [1–4] only for general codec-specific control mechanisms; all quantitative matched-distortion results remain supported by the paper's own data.

A new chemistry-scope paragraph cites [3,18,19,21] to pre-empt the objection that electronic-structure compression already exists. It states precisely why those papers are adjacent rather than overlapping: they compress other objects or address other validation targets.

### Missing-citation check

No major prior-art statement in the Discussion remains uncited. Claims that derive directly from this benchmark—97.2%/95.5% reclassification, floor-scale behaviour, matching results, and external replication—correctly remain uncited because their support is the study's own figures/tables/data.

### Citation-dumping check

No Discussion sentence uses an indiscriminate long list. The largest bundles are [1–4], where all four are needed to support a statement about the codec families used, and [8–10,16], where the sentence explicitly summarizes the grid-based Bader numerical literature.

## Methods audit

- `Benchmark design` now cites the primary method papers for the actual codec families: [2–4].
- `Re-derived Bader charge` now distinguishes the foundational QTAIM definition [17] from grid-based algorithm/numerical integration literature [8–10,16].
- Protocol A.1, three-state eligibility, reclassification, matching settings, and external confirmation are study-specific procedures and therefore do not receive decorative external citations.

## Claims deliberately left uncited

The following are internally generated results or study definitions and should not be padded with external references:

- 6,343 reconstruction rows; 254 development systems; 63 external systems.
- Protocol A.1 five-seed floor values and eligibility fractions.
- 97.2%, 95.5%, 56.5% failure reclassification and 46.3% non-evaluable naive passes.
- Hartree scaling exponent and material-level $R^2$ values.
- Bader monotonicity, local exponents and jump statistics.
- error-to-floor ratios.
- fixed-basin/domain-migration decomposition results.
- nominal-vs-realized $L_\infty$ ratios and matched-error ratios.
- certified compression-ratio rankings and external-cohort results.

These should be traced to figures, supplementary tables, frozen CSVs, and the claim–evidence matrix rather than to external literature.

## Final novelty sentence approved for submission drafting

> Existing work has developed error-bounded compression, QoI-aware error control, QoI-preserving pipelines and topology-preserving reconstruction. We add a distinct precondition for scientific benchmark validity: the requested downstream tolerance must first be shown to be numerically identifiable on the reference data before pass/fail attribution to compression is meaningful.

## Remaining reference work before final submission

1. Convert the Markdown numeric references into the exact target-journal reference style only after the journal is selected.
2. Verify every DOI, author list, year, volume and page range against Crossref/publisher metadata in the final bibliography pass.
3. If TOPIQ receives a peer-reviewed publication before submission, replace the arXiv entry with the published version without changing the role it plays in the narrative.
4. Avoid adding more references unless they close a genuine conceptual gap; the present 21-reference core is sufficient for the current Introduction/Discussion architecture.