# Writing README — JCTC manuscript

This file defines the writing rules for `submission/JCTC_MANUSCRIPT_v0.2.md` and later submission drafts.

## 1. Narrative architecture

The manuscript follows one forward scientific argument:

`field compression`  
→ `realized codec error structure`  
→ `chemical/QoI fidelity`  
→ `domain-migration mechanism`  
→ `robustness and failure regimes`  
→ `practical implications`

The seven top-level manuscript sections are fixed unless there is a strong scientific reason to change them:

1. Introduction
2. Scientific question and benchmark design
3. Codec error structure
4. QoI / Chemical fidelity
5. Mechanism: why L∞ fails
6. Robustness, failure regimes, and implications
7. Conclusion

`Data and Software Availability` and `References` follow the numbered scientific narrative and are not counted as Sections 8 and 9.

## 2. No defensive-writing architecture

Do **not** create a standalone `Limitations` section.

Scope, uncertainty, unusual cases, and failure regimes belong where they advance the science:

- numerical edge cases → Section 6;
- statistical sensitivity → Section 6;
- mechanism scope → Section 5;
- strict-sample interpretation → Section 6;
- future generalization → Section 6.4 or Conclusion.

The manuscript should sound like a paper explaining what was learned, not a response letter anticipating reviewer objections.

### Avoid recurring defensive constructions

Avoid phrases such as:

- `we acknowledge that ...`
- `a limitation of this work is ...`
- `we deliberately restrict ...`
- `we cannot establish ...`
- `this should not be interpreted as ...` repeated throughout the manuscript
- `to address a reviewer concern ...`
- `we subjected the result to ...` when a direct scientific description is available
- `this does not invalidate ...`
- `we are not claiming ...`
- `the study is not ...`
- discussion of internal pilot mistakes, abandoned claims, branch history, or manuscript-development history.

Use a positive scope statement instead.

**Defensive:**  
`We deliberately restrict this direct decomposition claim to the 12-material mechanism set.`

**Preferred:**  
`The direct decomposition characterizes a 12-material mechanism set spanning the observed stability range; full-benchmark reassignment provides complementary population-scale evidence.`

**Defensive:**  
`These results do not establish that Bader resolvability is fundamentally unpredictable.`

**Preferred:**  
`Conventional low-cost metadata do not recover Bader resolvability across the tested external corpora.`

**Defensive:**  
`The strict slab result should not be interpreted as a population-level ranking.`

**Preferred:**  
`Four slab materials enter the 10^-4 e contract, providing a small-sample view of the strict frontier.`

## 3. Paragraph logic

Every scientific paragraph should primarily do one of four jobs:

1. pose a question;
2. present evidence;
3. explain a mechanism;
4. state an implication.

A strong result subsection usually follows:

`question → measurement → quantitative result → physical/statistical interpretation → transition`

Do not start a paragraph with reviewer-facing qualification when the same information can follow the result as scope.

## 4. Evidence hierarchy

Use the evidence at the scale where it is strongest.

### Full benchmark

Use for:

- 6,343 successful reconstructions;
- 254 development materials;
- 4,627 base-ladder rows;
- bound utilization;
- fixed-basin versus re-derived error;
- failure registry;
- complete-case matching;
- material-fixed-effect models;
- compression/certification frontier.

### Stability corpus

Use for:

- 319-system Protocol A.1 statistics;
- 79.9%, 41.4%, 9.7% non-evaluable fractions;
- external predictability tests;
- symmetry-relabel sensitivity.

### Representative mechanism set

Use for:

- direct integrand/domain decomposition;
- median bounded domain contribution = 0.995;
- decomposition closure;
- representative spatial examples.

Do not convert atom count into an independent statistical sample size. Material-level or case-level inference is the default.

## 5. Statistical language

Use causal language only for algebraic or algorithmic relationships that are directly defined by the analysis.

Preferred terms for regression evidence:

- `associated with`
- `accounts statistically for`
- `absorbs the codec-associated residual`
- `mechanism-consistent`
- `tracks`

Avoid repeatedly announcing `not causal`. One concise methods-level statement is sufficient when needed.

Report matched codec effects as ratios with confidence intervals and denominator/sample size where space permits.

The conservative reviewer-facing matched result at the central contract is:

- SZ3/ZFP = **1.82× [1.68, 2.01]**, 119 materials;
- SPERR/ZFP = **2.00× [1.79, 2.25]**, 115 materials.

## 6. Numerical terminology

Use these terms consistently:

- `requested tolerance` or `nominal bound` for codec settings;
- `realized L∞` for measured field perturbation;
- `fixed-basin error` for integration over reference domains;
- `re-derived Bader error` for the primary chemical-fidelity metric;
- `Protocol-A.1 numerical stability floor at the stated perturbation amplitude` for the reference-QoI stability measurement;
- `admitted` or `evaluable` for systems whose floor is below the contract;
- `certified` for a codec operating point satisfying the downstream Bader threshold;
- `registered downstream failure` for solver/analysis failures.

Do not call Protocol A.1 an intrinsic material property or intrinsic noise floor.

`NON_EVALUABLE_BADER_UNSTABLE` is an analysis-state label. In prose, prefer `non-evaluable at the stated Bader-charge contract`.

## 7. Fixed-basin result

The directional headline is:

> Re-derived Bader error exceeds fixed-basin error in 99.7% of 4,627 successful base-ladder reconstructions.

The pooled 52.8× ratio is a valid descriptive statistic but is not a universal multiplier. Stratified codec/tolerance ratios belong in Figure 2 and Supporting Information.

## 8. Protocol A → A.1 writing rule

The archived float32 probe is discussed as a scientific observation about algorithm-aware perturbation design, not as an apology or development mistake.

Preferred logic:

`monotone rounding preserves local order unusually well`  
→ `Bader watershed depends on local ascent/order`  
→ `matched-amplitude noise perturbs the relevant structure`  
→ `seed and amplitude calibration define Protocol A.1`

Do not narrate internal chronology unless it explains the method scientifically.

## 9. Failure-regime writing rule

Failures are results about operating regimes, not embarrassments to be hidden.

Use Section 6 to distinguish:

- ordinary successful reconstruction;
- reference QoI non-evaluability;
- Bader solver failure under strong reconstruction distortion;
- symmetry-equivalent basin relabeling;
- strict-contract small-sample strata.

Write each state in terms of what it tells us about the analysis pipeline.

## 10. Related-work positioning

Do not claim novelty for the generic statement `pointwise error does not guarantee QoI fidelity`.

The manuscript contribution is the combined chemical contract:

1. a field-derived Bader integration domain;
2. re-derived versus fixed-domain evaluation;
3. Protocol-A.1 QoI resolvability qualification;
4. separation of nominal bound utilization from realized error magnitude;
5. direct domain-migration decomposition;
6. full-benchmark reassignment attenuation;
7. contract-dependent compression/certification frontier.

Relevant prior categories:

- general QoI-preserving compression [4];
- topology/local-order-preserving compression [5–9];
- QoI error propagation and visualization [10,11];
- electron-density downstream integration fidelity [15].

## 11. Figure-to-section map

- **Figure 1** → Section 2: scientific question and evaluation chain
- **Figure 2** → Section 4: fixed-basin vs re-derived chemical fidelity
- **Figure 3** → Section 5: domain-migration mechanism
- **Figure 4** → Sections 4 and 6: resolvability and probe calibration
- **Figure 5** → Sections 3 and 5: realized L∞ and residual structure
- **Figure 6** → Section 6: contract-dependent compression frontier

Figures should answer scientific questions rather than mirror the manuscript outline mechanically.

## 12. Revision discipline

Before changing a headline number, check `paper_data_v03/HEADLINE_NUMBER_REGISTRY_v03.md`.

Before changing a scientific claim, check the frozen evidence hierarchy and corresponding analysis outputs.

Editorial rewriting may change emphasis, ordering, and phrasing without reopening frozen estimands.

The temporarily unavailable per-atom mechanism table may refine Figure 3 and the direct-mechanism subsection. It does not automatically reopen Protocol A.1, the master benchmark, realized-L∞ matching, complete-case analysis, or the overall narrative.

## 13. Target voice

The target voice is:

- concise;
- quantitative;
- mechanism-first;
- confident about measured results;
- explicit about scope without sounding apologetic;
- written for computational chemists, not for a compression-only audience.

A useful test for every paragraph is:

> Does this paragraph help the reader understand the scientific question, evidence, mechanism, or implication?

If the paragraph mainly anticipates criticism, move the underlying scientific content to Section 6 or the Supporting Information and rewrite it as a result.
