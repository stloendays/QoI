# Manuscript v0.3.1 scientific-claim lint

Checks: 32; passed: 29; flagged/failed: 3.

- PASS — **version marker**: required token: Integrated manuscript draft v0.3.1
- PASS — **master size**: required token: 6,343
- PASS — **development materials**: required token: 254
- PASS — **base ladder**: required token: 4,627
- PASS — **fixed-v-resolved direction**: required token: 99.7%
- PASS — **representative mechanism dominance**: required token: 0.995
- PASS — **ZFP utilization**: required token: 0.1575
- PASS — **complete-case SZ3/ZFP**: required token: 1.82 [1.68, 2.01]
- PASS — **complete-case SPERR/ZFP**: required token: 2.00 [1.79, 2.25]
- PASS — **A1 1e-3 non-evaluable**: required token: 41.4%
- PASS — **A1 1e-4 non-evaluable**: required token: 79.9%
- PASS — **negative-control SZ3 electron model**: required token: 2.34 to 2.58
- PASS — **negative-control reassignment p**: required token: p=5.25×10^-28
- PASS — **symmetry pathology id**: required token: aflow-Al8Cu4U1_ICSD_601801
- PASS — **NON_EVALUABLE semantics**: required token: NON_EVALUABLE_BADER_UNSTABLE
- PASS — **SZ3 DOI**: required token: 10.1109/TBDATA.2022.3201176
- PASS — **SPERR DOI**: required token: 10.1109/IPDPS54959.2023.00104
- PASS — **predictability caveat**: required token: do not establish that Bader resolvability is fundamentally unpredictable
- PASS — **placeholder reference**: forbidden token: reference to be replaced
- PASS — **software placeholder**: forbidden token: [software/method reference
- PASS — **generic first-to-show claim**: forbidden token: first to show that pointwise
- PASS — **intrinsic Bader floor claim**: forbidden token: intrinsic Bader floor
- PASS — **representative-set scope explicit**: direct decomposition must not be generalized to all 254 materials
- PASS — **attenuation is non-causal**: reassignment is a post-compression variable
- PASS — **probe floor is protocol-defined**: avoid intrinsic-floor wording
- FLAG — **strict slab caveat**: 1e-4 slab frontier must be descriptive
- FLAG — **danger phrase review: causal codec effect**: hits=['causal codec effect']
- FLAG — **danger phrase review: universal codec winner**: hits=['universally best', 'universally superior']
- PASS — **danger phrase review: full-corpus mechanism overclaim**: hits=[]
- PASS — **reference 1 maps to ZFP**: opening [1–3] mapping
- PASS — **reference 2 maps to SZ3**: opening [1–3] mapping
- PASS — **reference 3 maps to SPERR**: opening [1–3] mapping

## Interpretation

This lint is a guardrail, not a substitute for editorial review. A flagged danger phrase can be harmless when used inside an explicit negation; such cases should be inspected manually rather than automatically deleted.
