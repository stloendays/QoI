# Manuscript writing rules — JCTC QoI paper

Status: ACTIVE writing constraints for the submission manuscript.

These rules govern `paper/MANUSCRIPT_DRAFT.md` and any future DOCX manuscript. They are writing constraints, not scientific protocol rules.

## 1. Use affirmative scientific writing

State what the data show, why it matters, and what mechanism supports the interpretation. Avoid reviewer-facing or defensive constructions such as:

- "we do not claim..."
- "this should not be interpreted as..."
- "this is not universal..."
- "we cannot conclude..." when a positive scope-bounded statement is available
- repeated disclaimers about what the work is not

Scope claims positively and locally instead. Example:

Preferred: "Across the pre-specified representative mechanism set, domain migration accounts for essentially all of the error at the most affected atom."

Avoid: "We do not claim that domain migration universally dominates all materials."

## 2. Preserve the mature narrative structure of the earlier Word manuscript

The preferred scientific order is:

1. Introduction
2. Scientific question and benchmark design
3. Codec error structure
4. QoI / chemical fidelity
5. Mechanism: domain migration and field-derived partitions
6. Robustness, failure regimes, rate–fidelity, and implications
7. Conclusion

The manuscript should read as a scientific argument, not as a chronological project log and not as a protocol manual.

## 3. The workflow is the methodological contribution, but the paper remains chemistry-first

The workflow should be expressed compactly as:

`Source provenance -> intrinsic QoI stability -> eligibility -> compression/reconstruction -> re-derived QoI -> topology/domain audit -> certification -> rate–fidelity`

Use this chain to organize Methods and Figure 1. Do not let implementation bookkeeping dominate the main-text narrative.

## 4. Keep protocol language out of ordinary prose when possible

Machine-readable verdict labels such as `CERTIFIED`, `NOT_CERTIFIED`, `NON_EVALUABLE_BADER_UNSTABLE`, and `PIPELINE_FAILURE` are useful in Methods, tables, and reproducibility records. In Results and Discussion, prefer natural scientific language unless the exact label is analytically important.

Likewise, details such as hashes, shard counts, CI job structure, and file names belong primarily in Methods, Data/Software Availability, Supporting Information, or repository documentation.

## 5. No standalone Limitations section

Integrate scope boundaries into the relevant Results or Discussion paragraph. Do not collect limitations into a separate defensive section.

## 6. Negative results are evidence

Present negative or falsified hypotheses as scientific findings that narrow the mechanism or design space. Avoid apologetic language.

Preferred: "The experiment ruled out symmetry folding as the source of the fidelity advantage."

Avoid: "Unfortunately, the symmetry hypothesis failed."

## 7. Scope by naming the population, not by self-weakening

Use phrases such as:

- "in the 254-material development benchmark"
- "across the pre-specified 12-material mechanism set"
- "among Protocol-A.1-admitted materials"
- "in the pre-specified 63-system confirmatory cohort"

These phrases define the evidential scope directly and eliminate the need for repeated caveats.

## 8. Separate manuscript claims from internal claim guardrails

Internal files may contain `CONFIRMED`, `FALSIFIED`, `PENDING`, prohibited wording, and release gates. The manuscript should translate those controls into clean scientific prose. Do not copy internal audit language verbatim into the article.

## 9. Preserve the old Word manuscript as the voice/structure reference, not as the numerical source of truth

The earlier Word manuscript establishes the preferred article voice and organization. Numerical values, figure numbering, corpus definitions, and external-validation statements must be refreshed against the current versioned repository outputs before submission.

Known examples of content requiring current-release reconciliation include the mechanism summary (latest representative-set median worst-atom domain share: 0.9995), current figure architecture, CCR terminology, and the frozen external 65 / 2 implementation sentinels / 63 confirmatory design.

## 10. Do not write external success before the frozen run is audited

Before terminal audit, describe the external analysis design in Methods and leave outcome-dependent Results unwritten. After completion, report the observed result directly; do not frame agreement as success and disagreement as failure. External transfer is a scientific outcome.

## 11. Main-text style target

Target a compact JCTC research-article voice:

- chemistry and scientific interpretation first;
- quantitative statements where evidence is closed;
- active verbs;
- minimal meta-commentary;
- minimal project-history narration;
- equations only when they define the contract or mechanism;
- terminology consistent across Abstract, Methods, Results, figures, and Supporting Information.

## 12. Core take-home formulation

The paper should converge on the affirmative principle:

> Scientific fidelity is a property of the complete chain from numerical perturbation to downstream analysis. A scientific-data approximation should therefore be certified at the level of the analysis it is intended to support, after the intrinsic stability of that quantity has been established.
