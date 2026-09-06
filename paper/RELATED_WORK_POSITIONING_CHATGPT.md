# Related-work and novelty positioning — 2026-09-06

This note is an editorial guardrail for the QoI manuscript. It is intentionally conservative: it identifies claims that are already established in scientific compression and isolates what this manuscript can defend as its own contribution. Checked against literature available through 2026-09-06.

## 1. Claims we should NOT present as novel

### Pointwise error control does not imply downstream-QoI fidelity
This is established. Jiao et al. explicitly frame the gap between raw-data error control and downstream quantities of interest and derive preservation theory for several QoI families.

- Pu Jiao et al., *Toward Quantity-of-Interest Preserving Lossy Compression for Scientific Data*, PVLDB 16(4), 697–710, 2022/2023. DOI: https://doi.org/10.14778/3574245.3574255

Therefore avoid language such as “first demonstration that pointwise error does not preserve scientific QoIs.”

### Pointwise bounds do not preserve topology
This is also established. TopoSZ and later topology-preserving frameworks explicitly motivate their methods by the failure of pointwise-bounded compressors to preserve critical points, contour trees or related descriptors.

- Lin Yan et al., *TopoSZ: Preserving Topology in Error-Bounded Lossy Compression*, IEEE TVCG 30(1), 1302–1312, 2024. DOI: https://doi.org/10.1109/TVCG.2023.3326920
- Nathaniel Gorski et al., *A General Framework for Augmenting Lossy Compressors With Topological Guarantees*, IEEE TVCG 31(6), 3693–3705, 2025. DOI: https://doi.org/10.1109/TVCG.2025.3567054

Do not frame “topology matters” by itself as the novelty.

### Error correlation / structure can matter to QoIs
By 2026, statistical-QoI work explicitly models spatial compression-error correlation and data–error coupling.

- Youyuan Liu et al., *TOPIQ: Statistical Error Propagation for Quantity-of-Interest Prediction under Lossy Compression*, accepted SC 2026 / arXiv:2608.26912. https://arxiv.org/abs/2608.26912

Thus our stronger contribution is not merely that “spatial correlation matters”; it is the specific discontinuous, field-derived-domain mechanism measured for Bader partitioning and the separation of realized-error magnitude from residual codec-associated structure.

## 2. Closest 2026 topology work — must be discussed

### Full local-order preservation
The closest conceptual neighbor is the Local-Order-Preserving Compressor, which preserves the relative ordering of neighboring values rather than only selected topological summaries.

- Alex Fallin et al., *Fast Topology-Aware Lossy Data Compression with Full Preservation of Critical Points and Local Order*, IEEE Transactions on Big Data, 2026. DOI: https://doi.org/10.1109/TBDATA.2026.3705355 ; arXiv:2603.26968

This is highly relevant because the on-grid Bader watershed follows local ascent relations. Our Protocol-A failure is likewise explained by monotone float32 rounding preserving order, while generic noise at comparable amplitude changes the partition. The manuscript should therefore state that local-order-preserving compression is a natural algorithmic direction suggested by the present chemistry-specific evaluation, not claim that no existing compressor addresses order preservation.

### Other recent topology-aware compressors
- Tripti Agarwal et al., *TopoSZp: Lightweight Topology-Aware Error-controlled Compression for Scientific Data*, arXiv:2602.17552.
- Yuxiao Li et al., *Preserving Discrete Morse-Smale Complexes in Error-Bounded Lossy Compression*, IEEE TVCG 32(7), 6593–6609, 2026, DOI: https://doi.org/10.1109/TVCG.2026.3684385

These methods preserve topological objects that are closer to our mechanism than generic SZ/ZFP/SPERR. They are relevant related work even though the present paper's experimental scope is an evaluation of general-purpose pointwise-error-bounded compressors rather than a topology-aware codec bake-off.

## 3. Electronic-density compression baseline

Lossless compression of volumetric/electron-density trajectories predates this work. BQB reports strong lossless compression on Gaussian Cube electron-density trajectories, so “compression of electron density” is not novel.

- Martin Brehm and Martin Thomas, *An Efficient Lossless Compression Algorithm for Trajectories of Atom Positions and Volumetric Data*, J. Chem. Inf. Model. 58(10), 2092–2107, 2018. DOI: https://doi.org/10.1021/acs.jcim.8b00501

Our manuscript already treats BQB as related work / a denominator-sensitive external baseline rather than a directly comparable pointwise-error-controlled Bader-fidelity codec.

## 4. What this manuscript can defend as distinctive

### A. Field-derived integration domains are part of the QoI
The Bader charge is not a fixed functional evaluated on a fixed region. The reconstructed field defines the integration domains through a watershed partition, and those domains can migrate after compression. Reusing original basins removes this error channel by construction. The measured decomposition

`Delta Q_total = Delta Q_integrand + Delta Q_domain`

therefore exposes a failure mode that is more specific than generic downstream-QoI distortion.

Current evidence: representative mechanism set has bounded domain-dominance `|domain|/(|domain|+|integrand|)` median 0.995, with 84.9% above 0.90 and machine-precision closure.

### B. The QoI is stability-qualified before it is used as a fidelity contract
A compressor cannot meaningfully be certified at a threshold finer than the numerical resolvability of the downstream observable. Protocol A.1 turns this from an informal caveat into an explicit eligibility layer with NON_EVALUABLE semantics rather than silently counting unstable systems as passes or failures.

This should be framed as a general evaluation principle demonstrated on Bader analysis, not as a claim that no prior scientific workflow has ever studied numerical stability.

### C. The stability probe itself is validated against the algorithmic structure of the QoI
The archived float32 probe is monotone/order-preserving and therefore unusually benign for an order-dependent watershed. The replacement probe was calibrated, seed-tested and amplitude-tested before eligibility statistics were recomputed. This self-correction is a methodological result: a stability probe that respects the relevant discrete invariant can report false robustness.

### D. Nominal error-budget utilization is separated from residual structure
ZFP realizes only ~0.158 of its requested bound, while SZ3/SPERR nearly saturate theirs. The paper therefore does not attribute same-nominal codec gaps wholesale to spatial structure. It separately shows:

1. a large bound-utilization effect, and
2. a residual ~2x codec-associated Bader-error difference after matching measured Linf and restricting to stability-qualified materials.

This is stronger and more defensible than a same-tolerance comparison.

### E. Basin reassignment statistically accounts for the codec-associated residual
Reviewer stress tests show that, at the 1e-3 e eligibility contract, the material-fixed-effect codec multipliers are ~2x when controlling measured Linf, but attenuate to approximately 1 after adding the fraction of reassigned voxels. This is mediation-consistent statistical evidence linking the codec-associated residual to basin migration. It complements, rather than replaces, the direct decomposition in the representative mechanism set.

Do not call this regression causal mediation: reassignment is a post-compression variable and may share unmeasured causes with Bader error.

## 5. Recommended novelty paragraph

The manuscript should position itself approximately as follows:

> Prior work has established that pointwise error guarantees need not preserve downstream quantities of interest or topological descriptors. We study a distinct failure mode that arises when the downstream quantity is evaluated over domains that are themselves derived from the reconstructed field. For Bader charge analysis, re-deriving those domains reveals an error channel that fixed-domain evaluation suppresses; direct decomposition identifies basin migration as the dominant contribution in a representative mechanism set. We further separate nominal error-budget utilization from residual codec-associated structure, and require the Bader observable to pass a calibrated numerical-stability test before it is used as a fidelity contract. The result is an evaluation framework in which the field error is measured as realized, the downstream analysis is rerun, and non-resolvable QoIs are reported as non-evaluable rather than scored.

## 6. Reviewer question we should anticipate

**Why were topology-/local-order-preserving compressors not included as primary baselines?**

Safe answer: the present study asks whether the guarantees exposed by widely used general-purpose pointwise-error-bounded compressors are sufficient for a field-derived chemical QoI, and develops the evaluation protocol needed to answer that question. Topology- and local-order-preserving codecs optimize a different guarantee and are therefore related algorithmic solutions rather than equivalent baselines. The mechanism found here makes them a natural next test. If space/resources allow before submission, one topology/local-order-preserving codec would be a useful supplementary validation, but the core evaluation claim does not depend on proposing or ranking such codecs.

Do not say that topology-aware codecs are irrelevant, or that none can preserve Bader basins.
