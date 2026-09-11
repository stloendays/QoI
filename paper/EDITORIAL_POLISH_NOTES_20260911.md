# Editorial polish notes — 2026-09-11

## Recommended submission draft

Use `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md` as the current reader-facing submission draft. Keep `paper/MANUSCRIPT_CERTIFIABILITY_DRAFT_20260911.md` as the evidence-rich provenance draft.

## Editorial strategy

The polished version follows a Nature/ACS-style narrative rather than a chronological research log:

1. **Open with the scientific decision problem, not the codec.** The abstract and introduction now begin from the assumption hidden in QoI benchmarking: a requested tolerance must itself be numerically resolvable before it can define pass/fail.
2. **State the novelty positively and narrowly.** The manuscript no longer spends repeated sentences defending that `pointwise error != QoI fidelity` is prior art. That point remains background; the contribution is the logically prior eligibility test.
3. **Make Figure 3 the narrative pivot.** The central quantitative result is now reached quickly: 97.2% and 95.5% of naive failures at the two strictest Bader contracts are non-evaluable, and 46.3% of naive passes at `1e-4 e` are also non-evaluable.
4. **Use declarative Results headings.** Each section states the scientific conclusion rather than naming the analysis procedure.
5. **Separate result from interpretation.** Results report what the data show; Discussion explains why the result matters, how it relates to prior QoI-aware compression, and where the generalization stops.
6. **Reduce repetitive caveats.** Claim boundaries are retained once at the point where they matter (Bader specificity, protocol dependence, plateau/floor boundary) rather than repeated after every paragraph.
7. **Use active, compact sentences.** Long noun chains, repeated phrases such as “the resulting framework”, and meta-writing such as “this is not used to claim…” were reduced.
8. **Put methods after the scientific narrative.** The polished draft follows a reader-first sequence: Introduction → Results → Discussion → Methods → availability.

## Structural changes relative to the provenance draft

### Title

Recommended title:

**Stability-qualified benchmarks for scientific compression of electronic densities**

This is shorter than the previous title, contains no acronym, and states both the methodological contribution and application domain without claiming universality across all scientific observables.

Alternative titles for journal-specific tuning:

- **Numerical identifiability sets the validity of scientific-compression benchmarks** — broader and more conceptual; use only if the editor is comfortable with the generalization beyond Bader.
- **When is a scientific-compression benchmark valid? Stability-qualified certification of electronic densities** — more editorial and accessible, but longer.
- **Downstream numerical stability defines valid scientific-compression contracts** — compact and concept-driven.

### Abstract

The abstract was substantially compressed. It now follows a five-part sequence:

`problem → benchmark design → headline reclassification → mechanism/confound controls → implication`

Secondary numerical details such as the full floor-normalized distributions were removed from the abstract because they compete with the main 97.2% / 95.5% result.

### Introduction

The introduction is reduced to five paragraphs:

1. scientific-data problem;
2. established QoI-aware compression literature and the remaining gap;
3. benchmark-validity principle;
4. why Bader is a stringent test and why electron count/Hartree are controls;
5. study design and contribution.

### Results

The preferred Results sequence is now aligned with the formal figure sequence:

- **Figure 2:** operator-dependent error propagation;
- **Figure 3:** binary benchmark → three-state certification (**central result**);
- **Figure 4:** validation of the stability probe;
- **Figure 5:** Bader-specific basin-migration mechanism;
- **Figure 6:** realized-distortion confounding control;
- **Figure 7:** frozen external confirmation.

The tight-regime floor analysis is placed immediately after probe validation because it connects the eligibility measurement to the observed strict-contract regime.

### Discussion

The Discussion is no longer a second Results section. It is organized around four questions:

1. What new logical step does this add beyond QoI-preserving compression?
2. Why is Bader an informative stress test but not a universal mechanism?
3. Why must both the downstream target and upstream realized distortion be qualified?
4. What is the scope of generalization and what must be specified in a reproducible scientific-compression contract?

The previous separate Conclusions section was removed from the polished draft because it repeated the Discussion. If the target ACS journal requires or strongly prefers a Conclusions section, the final Discussion paragraph can be moved into a short Conclusions section without changing content.

## Claim boundaries that must remain unchanged

- Do not claim that this work first discovered that pointwise error fails to determine QoI fidelity.
- Do not call a non-evaluable decision a codec failure or a codec success.
- Do not describe Protocol A.1 as “rescuing” failures; it invalidates unsupported positive labels as well as negative labels.
- Do not claim a universal `plateau = stability floor` relation. The supported statement is: **the strictest certified regime is floor-scale, consistent with an emerging analysis-limited regime**.
- Do not claim that the matched-realized residual identifies a specific geometric statistic of codec error. It supports an error-structure contribution beyond scalar `L_inf` only.
- Do not generalize Bader basin migration to arbitrary QoIs.

## Journal-specific preparation still required

The prose is now deliberately journal-neutral at the Nature/ACS level. Before actual submission, one final format pass should be made for the chosen journal.

- **Nature-family target:** keep the concise abstract, avoid a redundant Conclusions section, and retain Methods after Discussion. Check the specific journal's main-text and Methods length limits.
- **ACS Central Science / similar broad ACS target:** the current prose is suitable, but the journal-specific limit on total manuscript size and the number of main-text figures should be checked. If a ~5-figure expectation is enforced, Figures 1 or 4 and one supporting mechanistic figure are the first candidates for consolidation or Supporting Information; Figure 3 should remain in the main text.
- **Chemistry-specialist ACS target:** retain more Bader-method detail and consider a short Conclusions section.

## Remaining pre-submission items

1. Replace the repository-only Data and Code Availability statement with a persistent archival DOI (for example, a frozen release deposited in an archival repository) before publication.
2. Perform a final reference audit against `paper/REFERENCES.md` and the selected journal's reference requirements.
3. Decide whether the target journal needs 5, 6 or 7 main-text figures before building the final Word/PDF submission package.
4. Run one consistency audit across manuscript, captions, Figure Map and Supplement for the terms `eligible`, `certified`, `eligible but not certified`, and `non-evaluable`.
5. Build the final Word manuscript only from the polished draft and the locked data-driven figures.
