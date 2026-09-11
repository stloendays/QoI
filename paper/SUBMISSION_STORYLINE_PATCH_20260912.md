# Submission storyline patch — 2026-09-12

Status: **INTEGRATED ON SUBMISSION STORYLINE BRANCH**

Scientific scope: **FROZEN_FOR_SUBMISSION**. This patch changes narrative emphasis only; it does not alter data, thresholds, endpoints, cohorts, or scientific claims.

## Revised abstract

Scientific-compression benchmarks commonly ask whether a reconstructed field preserves a downstream quantity of interest (QoI), but this assumes that the reference QoI itself can support the requested numerical tolerance. We test this assumption for Bader charges derived from compressed electronic densities and introduce **QoI Stability Qualification (QSQ)** as a qualification layer applied before codec scoring. Across 254 development systems compressed with ZFP, SZ3 and SPERR, completing the same tight search ladder for all materials added 1,332/1,332 successful reconstructions and showed that, at $10^{-3}\,e$, failure to find a numerical pass occurs for 3.3% of QSQ-eligible versus 66.4% of screen-rejected material–codec pairs (20.34-fold). We then froze the five-seed QSQ gate and challenged it prospectively with 59 pre-registered fresh iid-uniform perturbations per material (14,986/14,986 valid trials). The gate admitted 143/254 materials (56.3% coverage); fresh-threshold exceedance risk was 1.600% in admitted materials versus 81.325% in screen-rejected materials, a 50.83-fold separation under the declared perturbation model. An independent Henkelman on-grid implementation reproduced QSQ classification in 24/24 systems at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$ ($\kappa=1.000$; floor-rank $\rho=0.995$), whereas near-grid differences showed that the downstream analysis algorithm remains part of the measurement contract. In an outcome-blind five-pair chemical case study, all 60/60 compressed charge-transfer directions were preserved even without QSQ, showing that strict numerical qualification and coarse qualitative decision preservation are distinct contracts. Together, these results establish a validated workflow in which **QoI stability qualification precedes eligibility, compression evaluation and certification**, separating reference robustness from fixed-pipeline reconstruction agreement. QSQ is an empirical risk-stratification procedure for the stated numerical contract, not a worst-case stability guarantee.

## Revised end of Introduction

Here we ask a logically prior question to conventional QoI-aware compression: **when is a requested downstream tolerance itself a valid benchmark?** We study Bader charge because its density-dependent basin assignment provides a stringent topology-sensitive test, with total electron number and the periodic Hartree potential as structurally distinct controls. Our workflow first qualifies each material–tolerance pair using QSQ, then evaluates compression only within that declared measurement contract. We test the resulting framework in four stages: equalizing codec search opportunity across all 254 development materials; prospectively challenging the frozen QSQ gate with 14,986 unseen perturbations; transferring the classification to an independent Bader implementation under matched on-grid semantics; and probing the boundary between strict numerical fidelity and a coarser qualitative chemical decision. The resulting evidence hierarchy is therefore controlled, prospective and implementation-aware rather than a retrospective reinterpretation of codec failures.

## Figure 3 lead-in paragraph

The central validation is not the historical fraction of apparent codec failures that become non-evaluable after qualification; those fractions depend on the original tolerance-ladder design. We therefore tested QSQ in two stronger ways. First, we removed unequal codec search opportunity by completing the same four tight settings for every development material. Second, after freezing the QSQ gate, amplitudes and thresholds, we challenged it with 59 genuinely fresh perturbations per material. Figure 3 combines these two controls: the equal-search experiment asks whether QSQ still identifies difficult benchmark targets when all materials receive the same codec opportunity, whereas the prospective experiment asks whether the frozen gate predicts unseen downstream response risk.

## Figure 3 result paragraph

Equalizing search opportunity added 1,332/1,332 successful reconstructions. At the primary $10^{-3}\,e$ contract, no-pass risk remained sharply separated: 3.3% for QSQ-eligible versus 66.4% for screen-rejected material–codec pairs, a 20.34-fold ratio. The prospective test was stronger still. Across 14,986/14,986 valid fresh perturbations, QSQ admitted 143/254 materials (56.3% coverage); admitted materials showed 135/8,437 threshold exceedances (1.600%), whereas screen-rejected materials showed 5,326/6,549 (81.325%), giving a 50.83-fold rejected-to-eligible risk ratio. The same directional separation held at the two pre-specified secondary thresholds. Thus, the central empirical result is prospective risk stratification under a declared perturbation model, not a design-independent claim that a fixed percentage of codec failures is invalid.

## P3A interpretation paragraph

The independent-implementation experiment addresses whether QSQ merely captures idiosyncrasies of the primary Bader software. Under matched on-grid basin-assignment semantics, the Henkelman implementation reproduced the frozen QSQ classification for all 24 systems at all three thresholds ($\kappa=1.000$) and preserved floor ordering ($\rho=0.995$). Near-grid agreement was lower, demonstrating the complementary boundary: QSQ is not implementation-free. The correct inference is therefore transfer across implementations within a declared analysis class, while the numerical analysis itself remains part of the measurement contract. This experiment does not establish electronic-structure grid convergence or a unique physical Bader reference.

## P4 interpretation paragraph

The outcome-blind chemical case study tests a different question: whether strict numerical qualification is necessary for preserving a coarse qualitative decision. It is not, at least for this frozen endpoint. All 60/60 common-tight charge-transfer sign decisions preserved the reference direction, while QSQ at $10^{-3}\,e$ retained only 36/60 trials; both qualified and unqualified policies had zero observed sign errors. This null correctness result is informative because it shows that the required measurement contract depends on the scientific decision. A $10^{-3}\,e$ per-atom numerical contract and a large-margin sign decision are not interchangeable endpoints. QSQ should therefore be matched to the scientific tolerance being claimed, rather than applied as a universal filter for every downstream interpretation.

## Revised opening of Discussion

The principal result of this study is not that pointwise reconstruction error can propagate irregularly into a downstream QoI; that is already established in scientific compression and numerical analysis. The stronger conclusion is that **benchmark scoring itself should be conditioned on whether the downstream QoI can support the requested tolerance under a declared numerical-analysis contract**. In our Bader-charge case study, this claim survives an equal-search control and, more importantly, prospective validation: the frozen QSQ screen separates 1.600% from 81.325% unseen perturbation exceedance risk at the primary $10^{-3}\,e$ endpoint, while retaining 56.3% of materials. Independent on-grid implementation transfer further shows that the separation is not specific to one software package, whereas near-grid differences make explicit that the analysis semantics remain part of the contract.

## Revised closing of Discussion

The practical output of this framework is therefore not a universal codec leaderboard or a binary declaration that a reconstruction is scientifically valid. It is a conditional measurement statement: first establish whether the QoI is numerically qualified at the requested tolerance under an explicit perturbation and analysis model; then evaluate codec fidelity and rate within that eligible set; finally report stronger scientific interpretations only when their own decision margins and uncertainty models have been validated. For the present study, this logic is summarized as **QSQ -> eligibility -> compression evaluation -> certification**. The framework is deliberately narrower than a worst-case guarantee, but stronger than retrospective benchmark reclassification because its central screen is tested prospectively and across an independent implementation.

## Interpretation locks

Do not restore any of the following as headline claims:

- `97.2% / 95.5% of failures are invalid`;
- `QSQ rescues codec failures`;
- `five seeds certify worst-case stability`;
- `P3A proves DFT grid convergence`;
- `QSQ improves correctness for the P4 sign endpoint`;
- `plateau = QSQ floor`;
- `pointwise error does not imply QoI fidelity` as the main novelty.

Historical full-record reclassification remains secondary provenance. Figure 3 must lead with **P1 equal-search separation** and **P2 prospective risk stratification**.
