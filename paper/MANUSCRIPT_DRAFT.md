# Chemical Fidelity Is Not a Pointwise Error: Topology-Induced Failure Modes in Lossy Compression of Electronic Densities

> Working JCTC manuscript draft. This document is the submission-oriented prose layer. `RESULTS.md` is retained as a historical research log and should not be treated as the final manuscript.
>
> External rate–fidelity results remain pending until the frozen corpus-scale run reaches a terminal, audited state. No success claim is made here in advance.

## Abstract

Lossy compression of scientific fields is commonly controlled in data space, for example by imposing a pointwise reconstruction bound. Such guarantees are convenient, but they do not establish preservation of downstream scientific quantities. We develop a stability-qualified workflow for certifying scientific-data approximations against a downstream quantity of interest (QoI) and apply it to atom-resolved Bader charges derived from electronic charge densities. The workflow separates four logically distinct outcomes: intrinsic instability of the QoI, numerical failure of the approximation contract, approximation-induced scientific error, and pipeline failure. Before any codec is judged, the intrinsic Bader stability floor of each material is measured using a pre-specified five-seed perturbation protocol at a material-specific floating-point scale. Only materials whose Bader charges are stable relative to a requested chemical tolerance are admitted to certification. Reconstructed densities are then audited against their requested pointwise error bounds and evaluated using both a fixed-domain diagnostic and a fully re-resolved Bader analysis in which atom domains are recomputed from the reconstructed field. Across the development benchmark of 6,343 retained codec rows from 254 materials, fixed-domain evaluation can substantially understate the chemically relevant error. A representative atom-level decomposition further shows that, for the worst-affected atom in the pre-specified mechanism set, the median error contribution associated with Bader-domain migration is 0.9995 of the total magnitude. We summarize scientifically valid operating points using a material-level Certified Compression Ratio (CCR), defined as the maximum compression ratio satisfying both intrinsic-QoI stability and downstream chemical fidelity. A frozen independent external evaluation is used to test transfer without retuning. The results establish that scientific fidelity is a property of the complete chain from numerical perturbation to downstream analysis, rather than of the pointwise reconstruction error alone.

## 1. Introduction

The storage and movement of high-dimensional scientific data increasingly compete with the cost of generating the data themselves. Electronic-structure calculations are a representative example: three-dimensional fields such as electronic charge density are retained because they support subsequent chemical analysis, visualization, charge partitioning, and reuse. Error-bounded lossy compression is therefore attractive when it reduces storage while retaining the scientific information needed downstream.

The usual compression contract, however, is stated in the representation space rather than the scientific decision space. A reconstructed field \(\tilde{\rho}(\mathbf r)\) may satisfy a stringent pointwise bound

\[
\|\tilde{\rho}-\rho\|_{\infty} \le \epsilon,
\]

without preserving a downstream observable to a comparably meaningful tolerance. This is not merely a matter of choosing a smaller \(\epsilon\). The downstream analysis may contain integration, optimization, thresholding, partitioning, topology changes, or solver bifurcations that transform a small field perturbation into a qualitatively different scientific result.

Bader analysis exposes this problem particularly clearly. Atom-resolved Bader charges are not obtained by integrating over a fixed, externally supplied domain. The atom domains are themselves derived from the topology of the charge-density field. Compression can therefore affect the result through two coupled channels: changing the density values within a domain and changing the domain itself. A comparison that reuses the original Bader partition measures only the first channel and can miss the dominant error mechanism.

A second difficulty is more fundamental. The quantity computed from the original uncompressed field is often treated as an exact reference. Yet a downstream numerical analysis can have its own material-specific stability floor. If an imperceptibly small perturbation of the original density changes an atom-resolved Bader charge by more than the requested scientific tolerance, then the material cannot honestly certify any compressor at that tolerance. Calling a codec a failure in this regime would attribute intrinsic QoI instability to the approximation method.

We therefore formulate lossy scientific-data evaluation as a **stability-qualified QoI certification problem**. The central principle is:

> An approximation can be certified against a downstream scientific quantity only after that quantity is shown to be numerically stable at the requested scientific tolerance.

The resulting workflow separates source integrity, intrinsic QoI stability, approximation fidelity, topology-sensitive downstream re-analysis, failure accounting, and rate–fidelity aggregation. We use three production error-bounded compressors—ZFP, SZ3, and SPERR—as probes of the framework rather than as the scope of the framework itself. The case study is atom-resolved Bader charge, but the methodological distinction between pointwise numerical error and downstream scientific validity is more general.

The paper addresses four questions. First, does an accepted pointwise error bound reliably rank reconstructions by chemical fidelity? Second, how much error is hidden when the downstream partition is held fixed rather than recomputed? Third, when is Bader charge itself stable enough to support a stated chemical tolerance? Finally, after enforcing both intrinsic stability and downstream fidelity, how much compression remains scientifically usable?

## 2. Methods

### 2.1 Overview: stability-qualified scientific-data certification

We organize the evaluation as the following sequence:

\[
\boxed{
\text{Provenance}
\rightarrow
\text{Intrinsic QoI stability}
\rightarrow
\text{Eligibility}
\rightarrow
\text{Approximation}
\rightarrow
\text{QoI re-analysis}
\rightarrow
\text{Topology audit}
\rightarrow
\text{Certification}
\rightarrow
\text{Rate--fidelity}
}
\]

The separation of these stages is intentional. A reconstructed field is not considered scientifically valid merely because it satisfies a codec-level numerical bound, and a codec is not considered scientifically invalid merely because a downstream quantity is intrinsically unstable.

For the present case study, the source object is an electronic charge density \(\rho_i(\mathbf r)\) for material \(i\), and the downstream QoI is the vector of atom-resolved Bader charges \(\mathbf Q_i\). Three scientific tolerances are evaluated throughout: \(\tau \in \{10^{-4},10^{-3},10^{-2}\}\) e.

The workflow yields four distinct verdict classes:

- **CERTIFIED**: the material is intrinsically eligible at \(\tau\), the numerical approximation is valid, and the re-resolved downstream error is below \(\tau\);
- **NOT_CERTIFIED**: the material is intrinsically eligible, but the downstream chemical error reaches or exceeds \(\tau\);
- **NON_EVALUABLE_BADER_UNSTABLE**: the Bader QoI itself is not sufficiently stable to support certification at \(\tau\);
- **PIPELINE_FAILURE**: provenance, parsing, source integrity, or another material-level prerequisite fails.

This classification prevents three qualitatively different phenomena—intrinsic analysis instability, codec-induced scientific error, and pipeline failure—from being pooled into a single pass/fail statistic.

### 2.2 Source provenance and integrity gate

Every source density is tied to explicit provenance metadata. For the formal external evaluation, source identity is fixed by URL, byte count, and SHA-256 digest. Parsing must reproduce the expected grid shape and composition metadata, all source values must be finite, and parser provenance is recorded. A failure at this stage prevents the material from entering the rate–fidelity analysis and is classified as a material-level `PIPELINE_FAILURE`.

Input-field properties that may be scientifically relevant but are not automatically attributable to a codec—for example a small negative density value already present in the source—are retained as diagnostics rather than converted into codec failures.

### 2.3 Intrinsic QoI stability and Protocol A.1

The uncompressed-field Bader result is treated as a reference only after a material-specific stability qualification. The final frozen protocol, Protocol A.1, defines a perturbation amplitude from the float32 round-trip \(L_\infty\) error of each material,

\[
\epsilon_i^{32}
=
\left\|
\operatorname{float64}[\operatorname{float32}(\rho_i)]-\rho_i
\right\|_{\infty}.
\]

For each material, five independently seeded perturbations are generated,

\[
\rho_i^{(s)} = \rho_i + u_i^{(s)},
\qquad
u_i^{(s)} \sim U(-\epsilon_i^{32},+\epsilon_i^{32}),
\]

with the pre-specified seeds \(s\in\{20260905,1,2,3,4\}\). Bader basins are re-derived independently for every perturbed density using the same on-grid implementation used elsewhere in the study. The intrinsic stability floor is

\[
F_i=
\max_s\max_a
\left|
Q_a(\rho_i^{(s)})-Q_a(\rho_i)
\right|,
\]

where \(a\) indexes atoms.

A material is eligible for a requested scientific tolerance \(\tau\) only when

\[
F_i < \tau.
\]

If \(F_i\ge\tau\), the correct outcome is `NON_EVALUABLE_BADER_UNSTABLE`, which is neither a pass nor a codec failure.

Protocol A.1 was introduced after calibration showed that the originally archived deterministic float32 round trip could severely understate watershed instability. Floating-point rounding is order preserving: it can create exact ties while preventing rank exchanges between voxels, making it unusually benign for an on-grid watershed. Equal-amplitude random perturbations remove this structural bias. The amplitude is therefore not claimed to define a perturbation-independent physical constant; rather, the stability floor is explicitly defined at the material-specific float32 round-trip scale and sensitivity to this choice is reported separately.

### 2.4 Lossy approximation and numerical-bound audit

Only after QoI eligibility has been defined do we evaluate lossy approximation. Three production codecs are tested: ZFP in fixed-accuracy mode, SZ3 in absolute-error INTERP_LORENZO mode, and SPERR in absolute-error single-chunk mode. The development benchmark contains 6,343 retained codec rows across 254 materials, comprising 4,627 base-ladder rows and 1,716 tight-ladder rows.

For every reconstructed field \(\tilde\rho_{i,c,k}\), where \(c\) denotes codec and \(k\) a frozen tolerance setting, we record the requested absolute tolerance and the realized pointwise error

\[
E_{\infty,i,c,k}
=
\|\tilde\rho_{i,c,k}-\rho_i\|_{\infty}.
\]

We also retain

\[
R_{\mathrm{bound}}
=
\frac{E_{\infty,i,c,k}}{\epsilon_{i,c,k}^{\mathrm{requested}}},
\]

because equal requested tolerances do not imply equal realized perturbations across codecs. Every successful retained development row respects its requested \(L_\infty\) bound. This explicit audit is important to the interpretation of cross-codec chemical error: a codec that realizes only a small fraction of its nominal budget is not being compared at the same actual field perturbation as a codec that saturates the requested bound.

### 2.5 Fixed-domain diagnostic versus re-resolved scientific contract

For every successful reconstruction, Bader error is measured in two ways.

The **fixed-basin diagnostic** integrates the reconstructed density over the atom domains obtained from the original field,

\[
E_{\mathrm{fixed}}
=
\max_a
\left|
Q_a(\tilde\rho;\Omega_a(\rho))
-
Q_a(\rho;\Omega_a(\rho))
\right|.
\]

This isolates the effect of changing the density values while holding the spatial partition fixed.

The headline scientific metric is instead the **resolved-basin error**,

\[
E_{\mathrm{resolved}}
=
\max_a
\left|
Q_a(\tilde\rho;\Omega_a(\tilde\rho))
-
Q_a(\rho;\Omega_a(\rho))
\right|,
\]

where Bader basins are independently recomputed from the reconstructed field. Certification always uses \(E_{\mathrm{resolved}}\), never the fixed-domain diagnostic.

This choice reflects the scientific workflow a user would actually perform on a decompressed density: the downstream analysis is rerun on the reconstructed object, rather than supplied with hidden domain labels from the original uncompressed field.

### 2.6 Error decomposition and topology diagnostics

The fixed-versus-resolved distinction provides a direct decomposition of the atom-level charge error. For atom \(a\),

\[
\Delta Q_a
=
\underbrace{
\int_{\Omega_a(\rho)}(\tilde\rho-\rho)\,d\mathbf r
}_{\Delta Q_a^{\mathrm{integrand}}}
+
\underbrace{
\left[
\int_{\Omega_a(\tilde\rho)}\tilde\rho\,d\mathbf r
-
\int_{\Omega_a(\rho)}\tilde\rho\,d\mathbf r
\right]
}_{\Delta Q_a^{\mathrm{domain}}}.
\]

The first term measures the density-value error inside a fixed original atom domain. The second measures the effect of changing the domain assignment itself. The implementation retains this identity atom by atom, together with domain-migration and Bader-topology diagnostics such as atom-domain migration fraction, vacuum-mask changes, and changes in the number of detected maxima.

The representative mechanism data comprise 1,665 atom-level rows from 12 pre-specified materials and 106 successful material–codec–tolerance operating points; two additional operating points are explicitly retained in the failure registry. The reported numerical closure of

\[
\Delta Q_a^{\mathrm{integrand}}+\Delta Q_a^{\mathrm{domain}}=\Delta Q_a
\]

has residual no larger than \(2\times10^{-16}\) e. For the atom with the largest absolute total error in each successful representative operating point, the median domain-term share is 0.9995. This mechanism result is intentionally scoped to the representative set and is not presented as a universal population-wide law.

### 2.7 Scientific certification

For material \(i\), codec \(c\), setting \(k\), and scientific tolerance \(\tau\), certification is defined by

\[
C_{i,c,k}(\tau)
=
\mathbf 1[F_i<\tau]\,
\mathbf 1[E_{\mathrm{resolved},i,c,k}<\tau].
\]

Thus, an accepted pointwise codec bound is necessary for a valid numerical row but is not sufficient for scientific certification. A reconstruction can be numerically compliant and still be `NOT_CERTIFIED` if the re-resolved downstream error exceeds the requested chemical tolerance.

Conversely, a material whose intrinsic Bader floor exceeds \(\tau\) is not included in the pass/fail denominator at that tolerance. It remains visible as `NON_EVALUABLE_BADER_UNSTABLE`.

### 2.8 Failure accounting

Failure semantics are frozen at two granularities.

**Material-level failures** include source-provenance failure, source-integrity failure, parsing failure, original-grid audit failure, and original-Bader failure. These prevent a valid material-level analysis and are reported as hard `PIPELINE_FAILURE` events.

**Row-level failures** occur after a material has validly entered the benchmark and affect only a particular material–codec–tolerance configuration. Examples include codec failure, reconstructed-grid audit failure, Bader-solver failure, or topology-diagnostic failure. Such rows are not counted as certified passes and are retained in an explicit row-failure registry. They do not erase successful rows for the same material, and a failed row does not trigger the staged 0.05 e early-stop rule.

This accounting is important because silently dropping unsuccessful codec rows would bias rate–fidelity summaries upward, whereas promoting every row-level numerical failure to a material-level failure would discard otherwise valid scientific information.

### 2.9 Certified Compression Ratio

The material-level rate–fidelity endpoint is the **Certified Compression Ratio (CCR)**. For material \(i\), codec \(c\), and scientific tolerance \(\tau\),

\[
\mathrm{CCR}_{i,c}(\tau)
=
\max_{k:C_{i,c,k}(\tau)=1}
\mathrm{CR}_{i,c,k}.
\]

CCR answers a direct scientific question: how strongly can this particular field be compressed by codec \(c\) while still supporting the downstream Bader result within \(\tau\)?

Materials, not codec rows, are the independent units in headline statistics. An eligible material with no certified setting has no CCR for that codec. Pairwise codec comparisons retain all admitted materials: if only one codec has a CCR it wins that material; if neither has a CCR the result is a tie; and the log-ratio effect size is summarized only for materials where both CCRs exist.

### 2.10 Frozen codec sampling policy

The codec ladders are inherited from the development benchmark and are not adapted to external outcomes. All materials receive the frozen base ladder evaluated from tighter to looser tolerances. The first successful retained row with \(E_{\mathrm{resolved}}\ge0.05\) e is kept as the failure boundary and terminates that material–codec base ladder. A row failure does not trigger this stop condition.

A tighter extension below relative tolerance \(10^{-5}\) is evaluated only for materials satisfying the pre-specified intrinsic-stability condition \(F_i<10^{-3}\) e, matching the development sampling policy. External results cannot add, remove, or relocate tolerance values.

### 2.11 External validation without retuning

The independent external corpus contains 65 frozen source systems: 37 AFLOW bulk systems and 28 NOMAD two-dimensional systems. Two systems were used to validate the new end-to-end harness before corpus-scale execution and had their rate–fidelity outputs inspected. They remain part of the full external release but are explicitly labeled **implementation sentinels** rather than untouched confirmation data.

The remaining 63 systems—36 AFLOW bulk and 27 NOMAD two-dimensional systems—form the pre-specified primary confirmatory rate–fidelity cohort. Their expected Protocol A.1 eligibility counts, fixed before external compression outcomes are inspected, are 16, 42, and 57 at \(\tau=10^{-4},10^{-3},10^{-2}\) e, respectively.

The external run uses the same Protocol A.1 definition, scientific tolerances, Bader implementation, codec modes, tolerance ladders, early stopping, failure semantics, and aggregation logic as the development analysis. No external result may trigger retuning. Consequently, reproduction or reversal of a development codec ordering is treated as a scientific outcome, not as a criterion for software success.

The full 65-system table is reported descriptively. Headline external rate–fidelity inference is reserved for the pre-specified 63-system confirmatory cohort.

**Status at this manuscript revision:** the frozen corpus-scale external rate–fidelity execution is still pending final audit. No external-success statement or external headline number should be inserted until that run is terminal and the aggregate outputs have passed their frozen invariants.

### 2.12 Reproducibility and execution record

The workflow records source hashes, manifest hashes, Protocol A.1 and stability-table hashes, development master-table hash, confirmatory-split hash, software versions, codec parameters, requested and realized pointwise error, downstream diagnostics, failure registries, and aggregation outputs.

Formal external execution is performed through GitHub Actions using a frozen preflight gate and a sharded corpus-scale workflow. Figure production for the submission manuscript is likewise intended to use repository-tracked R scripts executed in GitHub Actions, so that publication figures are generated from frozen tabular outputs rather than manually transcribed values.

## 3. Results

### 3.1 Pointwise numerical error does not determine chemical fidelity

The development benchmark shows that a valid pointwise error bound is not a chemical-fidelity guarantee. At matched nominal tolerances, codecs can produce markedly different re-resolved Bader errors, and the difference is partly explained by their different utilization of the requested \(L_\infty\) budget. In the released development table, SZ3 and SPERR typically realize values close to their requested absolute bound, whereas ZFP uses substantially less of the nominal budget. The result is not that a single nominal tolerance should be globally tightened, but that the scientific consequence of a pointwise perturbation is codec- and material-dependent.

### 3.2 Holding the Bader partition fixed understates the downstream error

The fixed-basin diagnostic is systematically less sensitive than the fully re-resolved analysis because it suppresses the domain-migration channel. This establishes a key evaluation principle: a downstream analysis should be rerun from the reconstructed data under the same conditions that would apply to a real user, rather than evaluated against hidden structural information inherited from the original field.

### 3.3 Domain migration is the dominant mechanism in the representative atom-level audit

The per-atom decomposition closes the mechanistic link between small field perturbations and larger downstream charge changes. Within the pre-specified 12-material mechanism set, the atom carrying the largest total Bader error is overwhelmingly dominated by the domain-migration term across successful operating points, with a median domain-term share of 0.9995. The statement is deliberately limited to this representative mechanism analysis; the population-level paper claim is that domain migration is a demonstrated failure mechanism, not that every material and tolerance is domain dominated.

### 3.4 Bader charge has a material-specific stability floor

Protocol A.1 shows that the downstream analysis itself can fail to support arbitrarily small chemical tolerances. This converts a previously implicit assumption into an explicit eligibility gate. A material that is non-evaluable at \(10^{-4}\) e can remain perfectly valid at \(10^{-2}\) e; eligibility is therefore a property of the material–QoI–tolerance combination, not a permanent exclusion label for the material.

The external stability analysis further shows that simple corpus labels do not provide a reliable shortcut for this determination. Instability is common enough to matter, but its magnitude must be measured per material rather than inferred from a broad structural category.

### 3.5 Stability qualification produces an honest rate–fidelity frontier

Once intrinsically unstable material–tolerance combinations are removed from the pass/fail denominator and certification is based on re-resolved Bader error, lossy compression remains useful on the development data. The appropriate rate metric is not the maximum raw compression ratio but the maximum compression ratio that survives the complete scientific contract. CCR therefore transforms a codec sweep into a material-level scientific operating frontier.

### 3.6 Requested and realized error budgets are not interchangeable across codecs

The requested codec tolerance is a control parameter, not a directly comparable perturbation magnitude. The realized-to-requested \(L_\infty\) ratio differs systematically across codecs, most notably for ZFP relative to SZ3 and SPERR. Interpreting chemical error at a nominally matched tolerance without auditing the realized perturbation would therefore conflate codec behavior with different effective perturbation strengths.

### 3.7 External transfer test

**Pending frozen external Full audit.** This section should be populated only after the 65-system row release and the pre-specified 63-system confirmatory aggregate pass their frozen invariants. The final text should report, without retuning, which development rate-ordering expectations transfer, which do not, how certification fractions and CCR distributions compare, and whether the fixed-versus-resolved and realized-bound mechanisms generalize.

## 4. Discussion

The central result is not that one pointwise tolerance is too loose. It is that scientific fidelity belongs to the complete chain from data perturbation to downstream analysis. A numerical field can satisfy a formal \(L_\infty\) contract and still alter a topology-dependent chemical observable beyond the tolerance a user actually cares about.

This distinction changes how scientific compression benchmarks should be interpreted. Pointwise norms remain essential because they provide deterministic numerical contracts and make codec behavior auditable. They are therefore not replaced. Instead, they become one layer of a larger certification stack. Numerical compliance answers whether the approximation respected its declared error budget; QoI certification answers whether the scientific analysis remained valid.

The stability gate is equally important. Without it, the original-data result is implicitly treated as exact, and downstream numerical instability can be misclassified as a codec failure. Protocol A.1 makes the reference calculation itself testable. In this sense, certification is conditional: a codec can only be judged at a scientific tolerance that the underlying analysis can resolve.

The fixed-versus-resolved comparison illustrates why downstream topology matters. Integrating the reconstructed density over original Bader domains measures a useful local field error, but it is not the scientific contract experienced by a user rerunning Bader analysis. The atom-level decomposition shows how a small density perturbation can reorganize domain assignments and dominate the resulting charge error. Similar logic is expected to apply to other analyses containing thresholding, segmentation, assignment, basin construction, or discrete topology changes, although those extensions are not established by the present case study.

The framework also sharpens codec comparison. A nominal tolerance is not an equal-perturbation condition when codecs use their error budgets differently. Comparing both requested and realized errors prevents a codec from appearing chemically superior merely because it systematically operates far inside its allowed bound. Conversely, scientific certification should not force all algorithms into an artificial matched-realized-error protocol if the practical question is how much scientifically valid compression each configured codec can deliver. CCR preserves that operational interpretation.

The external analysis is designed as a transfer test rather than a tuning loop. The 65-system manifest, implementation sentinels, 63-system confirmatory cohort, tolerance ladders, and aggregation semantics are fixed before the corpus-scale outcome is interpreted. If a development codec ranking reverses externally, that reversal is informative evidence about generalization rather than a reason to modify the protocol after the fact.

Several boundaries should remain explicit. This paper does not claim that Bader charge is the only scientifically relevant QoI, that the three codecs exhaust the compression design space, or that the present workflow is a universal standard. Bader analysis is used because it supplies a chemically interpretable and topology-sensitive stress test. The broader claim is methodological: downstream scientific quantities should be stability-qualified and re-evaluated from reconstructed data before a lossy scientific representation is called faithful.

## 5. Conclusions

We introduce a stability-qualified workflow for certifying lossy scientific-data approximations against downstream chemical observables. The workflow first asks whether the observable itself is numerically stable at the requested scientific tolerance, then audits the approximation contract, reruns the downstream analysis on the reconstructed data, records topology-sensitive failure mechanisms, and finally summarizes the scientifically valid operating points at the material level.

Applied to electronic charge densities and atom-resolved Bader charges, the framework shows that pointwise error control alone does not determine chemical fidelity and that fixed-domain evaluation can miss a dominant domain-migration contribution. Intrinsic Bader instability further imposes a material-specific floor below which codec pass/fail statements are not meaningful. Scientific compression is therefore most naturally described by a qualified rate–fidelity frontier rather than by compression ratio or pointwise error in isolation.

The practical implication is simple: **a scientific approximation should be certified against the analysis it is intended to support, and that analysis must itself be stable enough to serve as a reference.**

## Working figure/caption note for the workflow schematic

A workflow schematic can be used as a Methods figure, graphical abstract, or TOC-style overview without changing the existing main-figure numbering until the full manuscript figure architecture is finalized.

**Proposed caption:** *Stability-qualified workflow for scientific-data approximation. Source data first pass provenance and integrity checks. Before any approximation is evaluated, the intrinsic numerical stability of the downstream quantity of interest (QoI) is measured at the requested scientific tolerance. Only eligible material–tolerance combinations proceed to codec certification. Reconstructed fields are audited against their declared pointwise error bounds and analyzed through both fixed-domain and independently re-resolved downstream calculations. The latter defines the scientific certification contract, while topology and domain-migration diagnostics identify mechanism-level failure modes. Certified operating points are finally summarized by the material-level Certified Compression Ratio (CCR). This design separates intrinsic QoI instability, approximation-induced scientific error, and pipeline failure.*

## Manuscript claim guardrails

Until the external Full run is terminal and audited, do not write that the end-to-end rate–fidelity workflow has been externally confirmed. Permissible language is that the workflow is frozen and under independent corpus-scale evaluation, while external Protocol A.1 stability qualification is already complete.

After successful completion and audit, the strongest intended wording is: *The complete chemistry-aware rate–fidelity workflow was evaluated end-to-end on a pre-specified 63-system confirmatory cohort drawn from the frozen external corpus, with two previously inspected systems retained separately as implementation sentinels.*

Do not describe all 65 systems as untouched confirmation data, and do not generalize the representative 12-material domain-migration result into a universal population-wide statement.