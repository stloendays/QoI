# Manuscript narrative reframe — 2026-09-11

## Decision

The manuscript must **not** present either of the following as the primary novelty:

1. pointwise reconstruction error does not guarantee downstream QoI fidelity; or
2. grid-based Bader charge has finite numerical sensitivity.

Both are established ideas in adjacent literatures. The manuscript should instead center on a stricter question:

> **Can a requested downstream QoI tolerance be scientifically certified at all before a compressor is judged against it?**

The operational contribution is therefore a **stability-qualified scientific-compression benchmark** that separates three logically distinct states:

- **eligible + certified**: the uncompressed QoI is numerically identifiable at the requested tolerance and the compressed reconstruction satisfies the QoI contract;
- **eligible + not certified**: the QoI is identifiable at that tolerance, but the compressor/reconstruction violates the QoI contract;
- **non-evaluable / ineligible**: the uncompressed QoI itself is not stable at that tolerance, so the benchmark cannot legitimately label the compressor pass or fail at that precision.

This reframe changes the paper from a generic QoI-aware compression study into a study of **QoI certifiability and benchmark validity**.

---

## Central scientific claim

Preferred one-sentence claim:

> **A downstream scientific tolerance is a valid compression benchmark only after the quantity of interest is shown to be numerically identifiable at that tolerance; otherwise benchmark outcomes confound compressor-induced error with analysis-induced instability.**

Equivalent compact form:

`QoI stability qualification -> eligibility -> compression evaluation -> certification`

not merely:

`field error -> QoI error`

The latter remains necessary background, not the headline contribution.

---

## Literature boundary

### What is already known

- Error-bounded compressors control raw-data distortion, while downstream QoIs can require their own error guarantees. Jiao et al. explicitly established this direction for multiple QoI families (PVLDB 2022, DOI 10.14778/3574245.3574255).
- Topology-preserving compression has shown that a pointwise error bound can fail to preserve downstream topological structure.
- Bader analysis is grid- and partition-sensitive; finite numerical convergence/sensitivity of Bader charges is not itself a new observation.
- Recent work such as TOPIQ (arXiv:2608.26912, 2026) further moves the field toward QoI-level error propagation and uncertainty prediction.

### What this manuscript should claim

The target gap is narrower and stronger:

1. **pre-certification numerical eligibility** of a downstream chemical QoI;
2. explicit separation of **non-evaluable** cases from genuine compressor failures;
3. demonstration that this separation changes the interpretation of scientific-compression benchmarks;
4. mechanistic identification of the Bader-specific analysis-limited regime through basin re-derivation/domain migration;
5. honest codec comparison after controlling realized rather than nominal distortion;
6. frozen external confirmation of the resulting stability-qualified decision framework.

Do not claim that this is the first work to care about QoIs in scientific compression.

---

## The benchmark-validity argument

For material `m` and requested QoI tolerance `tau`, define an independently measured intrinsic stability scale `delta0(m)` under the frozen Protocol A.1 probe.

Eligibility:

`eligible(m, tau) := delta0(m) < tau`

Compression certification for reconstruction `r`:

`certified(r, tau) := eligible(m, tau) AND E_QoI(r) < tau`

The important logical point is:

> If `delta0(m) >= tau`, the scientifically correct state is **NON_EVALUABLE_BADER_UNSTABLE**, not codec failure.

This distinction must be maintained in all headline success rates, tables and figures.

---

## Why the plateau matters

The tight-tolerance extension should not be framed as merely extending a codec tolerance ladder. Its scientific purpose is to identify the transition from a compression-limited regime to an analysis-limited regime.

Desired interpretation:

- at larger reconstruction perturbations, observed QoI error contains a substantial compression-induced component;
- as realized field distortion decreases, that component shrinks;
- once the perturbation is below the effective numerical/topological sensitivity of the Bader procedure, further tightening no longer produces proportional improvement in resolved Bader error;
- the resulting plateau should be compared quantitatively with the independently measured Protocol A.1 stability scale.

The strongest supported version would show that the plateau scale and the independently measured stability floor agree sufficiently to identify the same analysis-limited regime.

Avoid saying only “the error stops decreasing”; the paper must connect the plateau to **benchmark identifiability**.

---

## Revised Results logic

### Result 1 — Conventional field fidelity is not the paper's novelty

Use electron count / Hartree / Bader to establish the operator hierarchy and motivate why downstream evaluation is necessary. Explicitly cite prior QoI-preserving and topology-preserving work so this section is framed as context plus an electronic-density demonstration, not as a first-principles novelty claim.

### Result 2 — A scientific QoI contract requires an eligibility test

Introduce Protocol A.1 before reporting tight-threshold codec success. Define the three states: eligible-certified, eligible-not-certified, non-evaluable.

Primary question:

> At each requested Bader tolerance, how much of the corpus is actually measurable at that precision before compression is considered?

### Result 3 — Ignoring eligibility changes benchmark interpretation

Directly compare:

- apparent pass/fail statistics without stability qualification; versus
- stability-qualified certification.

Report how many nominal failures are reclassified as **non-evaluable** rather than compressor failures. This is the cleanest empirical demonstration of benchmark-validity impact.

### Result 4 — Tight compression enters an analysis-limited regime

Use the tight ladder to test whether resolved Bader error approaches a material-specific plateau rather than following the codec tolerance indefinitely. Relate that plateau to Protocol A.1 stability.

### Result 5 — Basin migration explains why Bader is especially vulnerable

Retain the fixed-basin versus re-derived-basin decomposition. This is the Bader-specific mechanism, not the universal contribution.

### Result 6 — Codec comparison must control realized distortion

Retain matched-realized-`L_inf` analysis. Nominal tolerance is not a codec-independent distortion scale. Any residual Bader difference after matching is evidence for error-field structure beyond scalar maximum error.

### Result 7 — External confirmation

Use the untouched 63-system cohort to show that the eligibility distribution and stability-qualified decision pattern reproduce without retuning.

---

## Manuscript wording changes

### Abstract

The abstract should open with benchmark validity, not the generic statement that QoIs differ from pointwise error.

Preferred architecture:

1. Scientific-compression benchmarks often apply downstream error thresholds directly to reconstructed data.
2. Such a threshold is meaningful only if the uncompressed analysis itself is numerically identifiable at that scale.
3. We introduce a stability-qualified certification framework for compressed electron densities, using Bader charge as a topology-sensitive chemical QoI and Hartree/electron-count controls to separate operator regimes.
4. Protocol A.1 independently measures material-specific Bader stability before any codec is scored.
5. The framework separates genuine codec failures from non-evaluable material-threshold pairs, identifies an analysis-limited tight-error regime, and retains decision-relevant differences after matching realized distortion.
6. The frozen decision rules reproduce on the untouched external cohort.
7. Conclusion: downstream QoI tolerance must be qualified before it can serve as a scientific compression contract.

### Introduction

The introduction should state explicitly that QoI-aware compression is prior art. The unresolved problem is not “should we care about QoIs?” but:

> **What makes a requested QoI tolerance itself a valid and auditable benchmark?**

### Discussion

Separate three layers:

- **known principle:** raw-data error alone is not a downstream scientific guarantee;
- **new evaluation principle tested here:** downstream tolerance requires independent numerical eligibility before compressor scoring;
- **Bader-specific mechanism:** density-dependent partition migration creates an analysis-limited regime and makes strict thresholds especially vulnerable to misinterpretation.

---

## Figure roles under the new story

- **Figure 2:** motivation/operator hierarchy. It should support “different operators propagate the same reconstruction differently,” not carry the novelty claim by itself.
- **Figure 5:** Bader mechanism. Fixed-basin vs re-derived-basin and domain migration explain the instability channel.
- **Figure 6:** confounding control. Equal nominal tolerance is not equal realized distortion; matching realized `L_inf` tests the residual error-geometry contribution.
- The eligibility / stability figure becomes conceptually central and should appear before codec leaderboard-style results.
- The tight-tolerance/plateau evidence should be explicitly labelled as a transition toward an **analysis-limited regime** if the quantitative correspondence is supported.

---

## Claims to avoid

Do not write:

- “We are the first to show that pointwise error does not guarantee QoI fidelity.”
- “Bader charge has a numerical floor, therefore our method is novel.”
- “SZ3/SPERR fail at 1e-3 e” when the corresponding material-threshold pair is ineligible.
- “The plateau proves the compressor cannot improve further” unless the compressor-induced component has been separated from analysis instability.
- “One codec is universally best.”

Prefer:

- “At this threshold the QoI is not independently resolvable, so the codec cannot be scientifically judged against that contract.”
- “Among eligible material-threshold pairs, ...”
- “The stability-qualified benchmark distinguishes non-evaluable targets from genuine reconstruction failures.”

---

## Required quantitative checks before final submission

The current evidence already supports the framework, but the strongest version of the manuscript should report these explicitly:

1. For each `tau`, counts/fractions of **eligible-certified / eligible-not-certified / non-evaluable** pairs.
2. Reclassification table showing how naive pass/fail interpretation changes after eligibility qualification.
3. Relationship between the tight-ladder Bader plateau scale and Protocol A.1 stability floor at the material level.
4. Fraction of apparent strict-threshold failures that are actually non-evaluable rather than eligible failures.
5. External-cohort reproduction of the same quantities without retuning.

If item 3 is weak, keep the plateau as supporting evidence and do not make quantitative floor–plateau equivalence a headline claim.

---

## Working title options

Primary:

**Can This QoI Be Certified? Stability-Qualified Lossy Compression of Electronic Densities**

More conservative:

**Stability-Qualified Certification of Lossy Compression for Electronic-Density QoIs**

More benchmark-focused:

**When Is a Scientific Compression Benchmark Valid? QoI Certifiability in Electronic-Density Compression**

The existing title *Scientific Fidelity Is QoI-Dependent* can remain as a fallback, but it foregrounds a principle that is already established and therefore understates the manuscript's more specific contribution.

---

## Canonical manuscript thesis

> **The scientific question is not only whether compression preserves a downstream quantity of interest, but whether the requested QoI tolerance is itself numerically resolvable. By qualifying that tolerance before codec scoring, the benchmark can distinguish genuine compression-induced failures from targets that the downstream analysis cannot meaningfully resolve, producing an auditable stability-qualified rate–fidelity frontier.**
