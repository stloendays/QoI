# Manuscript certifiability patch — 2026-09-11

Apply this patch to `paper/MANUSCRIPT_CERTIFIABILITY_DRAFT_20260911.md` and to the next Word build. It records the post-draft quantitative audit without altering frozen benchmark data.

## Abstract insertion/replacement

After the sentence reporting Protocol A.1 non-evaluable fractions, add:

> On the 254-material development benchmark, this qualification changes the interpretation of binary codec outcomes: at 10^-4 and 10^-3 e, 518 of 533 (97.2%) and 296 of 310 (95.5%) apparent failures, respectively, occur on material–threshold pairs that are non-evaluable under Protocol A.1. Eligibility is not a relaxed pass criterion; at 10^-4 e, 106 of 229 naive passes also occur on non-evaluable pairs.

Recommended concluding Abstract sentence:

> The resulting benchmark therefore distinguishes genuine compression-induced violations from scientifically non-evaluable targets and replaces unconditional binary codec scoring with a stability-qualified, three-state rate–fidelity assessment.

## Results insertion: immediately after the three-state eligibility definition

### Stability qualification materially changes binary benchmark labels

The distinction is not merely semantic. At each chemical threshold, we compared the stability-qualified decision with a naive binary criterion that evaluates the Bader error while ignoring Protocol A.1 eligibility. Across the 762 material–codec decisions at each threshold, the naive criterion produces 533 apparent failures at 10^-4 e. Of these, 518 (97.2%) occur on material–threshold pairs that are non-evaluable under the independent stability qualification, leaving only 15 genuine failures among eligible pairs. At 10^-3 e, 296 of 310 apparent failures (95.5%) are similarly reclassified as non-evaluable, leaving 14 eligible failures. Even at 10^-2 e, 61 of 108 apparent failures (56.5%) occur on non-evaluable pairs.

Eligibility does not simply remove difficult failures or make the benchmark more permissive. It also invalidates apparent successes when the requested scientific precision is not independently resolved: at 10^-4 e, 106 of 229 naive passes (46.3%) occur on non-evaluable material–threshold pairs. The correction is therefore a change from an invalid binary label to a three-state measurement decision, not a relaxation of the scientific tolerance.

These results make the benchmark-validity consequence quantitative. At the two strictest contracts, more than 95% of apparent codec failures cannot be scientifically attributed to the compressor because the reference Bader analysis itself is not independently resolvable at the requested tolerance.

## Replace the final paragraph of “Tight reconstruction enters an analysis-limited regime”

Use:

> The frozen floor-normalized analysis provides a scale check on this interpretation. At the strictest 10^-4 e certified contract, median resolved-Bader-error / A.1-floor ratios are 1.23 for SPERR, 1.33 for SZ3, and 1.09 for ZFP, with P90 values between 2.86 and 3.25. Thus the strictest certified regime is already floor-scale. At 10^-3 e the medians broaden to 2.78–3.55 times the floor, and at 10^-2 e to 10.7–14.6 times, indicating increasing dominance of compression-induced error away from the strict regime. This pattern is consistent with an emerging analysis-limited regime at the strictest contract. Because the frozen floor-normalized summary is not a material-level plateau estimator, however, we do not claim a universal quantitative identity between the tight-ladder plateau and the Protocol A.1 floor.

## Discussion insertion

> The magnitude of the reclassification shows why eligibility is more than a reporting convention. At 10^-4 and 10^-3 e, 97.2% and 95.5% of the failures obtained by ignoring eligibility occur on targets that the independent reference analysis cannot resolve at the requested precision. Conversely, the same qualification also invalidates nominal passes on non-evaluable targets. The issue is therefore not whether an exclusion rule makes a codec look better or worse; it is whether the pass/fail label has a defined scientific meaning in the first place.

## Claim boundary

Do not state that Protocol A.1 proves a universal Bader uncertainty floor or that the tight-ladder plateau equals the A.1 floor material by material. The current evidence supports **floor-scale behavior at the strictest certified contract**, not an exact plateau–floor law.

Canonical evidence: `paper/CLAIM_EVIDENCE_ADDENDUM_20260911_CERTIFIABILITY.md` and `analysis/CERTIFIABILITY_AUDIT_20260911.md`.
