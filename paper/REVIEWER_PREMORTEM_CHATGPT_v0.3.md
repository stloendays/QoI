# Reviewer premortem — manuscript v0.3

Purpose: anticipate technically serious reviewer objections before submission and map each objection to the existing evidence, required manuscript wording, and any remaining action. This is not a response letter; it is a pre-submission stress test.

## Risk 1 — “The codec gap is just because ZFP realizes a smaller error than SZ3/SPERR.”

**Severity:** originally critical; now closed as a major threat.

**Evidence already available:**
- median realized/nominal L∞: ZFP 0.1575, SZ3 ~1.000, SPERR ~1.000;
- primary A.1-qualified 0.10-dex realized-L∞ matching at 1e-3 e: SZ3/ZFP 1.90× [1.70,2.20], SPERR/ZFP 1.87× [1.63,2.08];
- conservative complete-case: 1.82× [1.68,2.01] and 2.00× [1.79,2.25];
- alternate common-support interpolation: 2.07× [1.95,2.19] and 1.99× [1.83,2.21].

**Required wording:** equal nominal tolerance mixes bound utilization and residual codec-associated structure. Never attribute the 6–12× same-nominal gap entirely to structure.

**Remaining action:** none for core claim.

---

## Risk 2 — “The approximately twofold residual is an artefact of failed Bader cases being omitted.”

**Severity:** closed as a major threat.

**Evidence:** 24 registered failures at nominal relative tolerance <=0.01 across 20 materials (20 ZFP, 4 SPERR). Removing every affected material from every codec leaves 234 materials and essentially unchanged matched/interpolated ratios.

**Required wording:** state explicitly that the complete-case rule is intentionally conservative and removes successful rows from other codecs as well.

**Remaining action:** keep failure registry auditable in supplement.

---

## Risk 3 — “The twofold residual is statistical but has no mechanism.”

**Severity:** substantially reduced; strongest current result.

**Evidence:**
1. direct 12-material decomposition: median bounded domain dominance 0.995, 84.9% >0.90, machine-precision closure;
2. full-benchmark attenuation: complete-case codec effects 2.34×/2.08× collapse to 0.96×/0.94× after adding reassigned-voxel fraction;
3. reassignment slope 0.880 [0.723,1.037], p=5.78e-28.

**Required wording:** call regression “mechanism-consistent attenuation” or “mediation-consistent evidence,” not causal mediation.

**Remaining action:** full per-atom decomposition when the pending third commit lands; use the preregistered case/material aggregation plan and leave-one-material-out sensitivity.

---

## Risk 4 — “The direct mechanism set has only 12 materials; you overgeneralize.”

**Severity:** open but controlled.

**Evidence:** representative-set decomposition plus full-table reassignment attenuation.

**Required wording:** “domain migration dominates in the representative mechanism set.” Do not state that direct decomposition proves dominance for all 254 materials.

**Remaining action:** per-atom table strengthens internal consistency but will not convert 12 selected materials into a random sample of 254. Preserve scope even if the per-atom result is very strong.

---

## Risk 5 — “Fixed-basin underestimation ratios blow up because the denominator is nearly zero.”

**Severity:** closed for direction; controlled for magnitude.

**Evidence:** resolved > fixed in 99.7% of 4,627 base rows. Pooled median ratio remains 52.6× after imposing a 1e-6 e denominator floor, but ratios vary substantially by codec/tolerance.

**Required wording:** use the 99.7% directional result as the headline. Any multiplicative ratio must state aggregation, codec/tolerance and denominator treatment.

**Remaining action:** none.

---

## Risk 6 — “The Bader stability floor is arbitrary because it depends on a chosen random probe.”

**Severity:** important but converted into a methodological contribution.

**Evidence:**
- archived float32 probe is monotone/order-preserving and creates exact ties;
- calibrated matched-amplitude noise removes ties and perturbs assignments more strongly;
- calibration: median float32/noise floor contrast, tie/reassignment diagnostics;
- seed span median 0.47 decades, maximum 2.39;
- amplitude sensitivity median 0.76 decades over 0.1×→10×;
- A.1 freezes perturbation family, amplitude rule, five seeds and max aggregation.

**Required wording:** “Protocol-A.1 numerical stability floor at the stated perturbation amplitude,” never “intrinsic Bader floor.”

**Remaining action:** include amplitude/seed sensitivity in supplement and exact seed list in Methods.

---

## Risk 7 — “Five random seeds are insufficient.”

**Severity:** moderate.

**Current defense:** A.1 was calibrated before freezing; five-seed max is conservative and preregistered. Single-seed instability was demonstrated explicitly. The manuscript does not claim convergence of the maximum over all possible perturbations.

**Required wording:** operational reproducibility rather than exhaustive worst-case certification.

**Potential optional supplement:** running 20–50 seeds on a small calibration subset would quantify saturation of the empirical maximum, but it is not required to preserve the current claim because A.1 is a declared protocol rather than a theorem.

---

## Risk 8 — “The perturbation amplitude is pegged to float32 L∞ for historical convenience, not chemistry.”

**Severity:** moderate.

**Current defense:** the amplitude is a reproducible numerical perturbation scale chosen before headline A.1 statistics; amplitude sensitivity is reported rather than hidden. The purpose is to determine whether a proposed Bader contract is resolvable under a stated numerical perturbation, not to identify a universal physical noise scale.

**Required wording:** avoid interpreting the eligibility boundary as a fundamental chemical constant.

**Optional future extension:** report eligibility curves as a function of probe amplitude, but retain frozen A.1 as primary.

---

## Risk 9 — “The 2.15 e external floor is just symmetry-equivalent atom relabeling.”

**Severity:** closed for headline statistics; must remain transparent.

**Evidence:** one registered `basin_relabelling_symmetry_equivalent` case; charge multiset unchanged. Removing it changes non-evaluable fractions by <0.3 percentage points at all contracts and barely changes external AUROC.

**Required wording:** identify it explicitly as a position-indexed QoI pathology and separate it from chemical charge redistribution.

**Remaining action:** if atom correspondence/symmetry-aware matching becomes part of the final workflow, report it as a sensitivity, not a retroactive change to frozen A.1.

---

## Risk 10 — “Why use maximum per-atom Bader error instead of mean/RMS charge error?”

**Severity:** likely reviewer question.

**Defense:** certification is a worst-atom chemical contract: one catastrophically wrong atomic charge can invalidate the downstream interpretation even if mean error is small. The max metric was fixed before final analysis and aligns naturally with a per-system pass/fail threshold.

**Required Methods sentence:** the system-level QoI error is the maximum absolute atom-wise charge deviation, chosen as a conservative contract that prevents averaging away localized basin failures.

**Optional supplement:** mean/RMS per-atom errors can be reported descriptively once the per-atom table lands, but should not replace the frozen primary endpoint.

---

## Risk 11 — “Bader labels are permutation-sensitive; why compare atom indices at all?”

**Severity:** important conceptual issue.

**Defense:** for ordinary systems atom identities are defined by nuclear positions and position-indexed charges are chemically meaningful. The known symmetry-equivalent relabeling pathology is explicitly registered and sensitivity-tested. A permutation-invariant multiset metric would answer a different QoI question and could hide chemically meaningful swaps between inequivalent sites.

**Required wording:** atom-indexed charge is the primary chemical contract; permutation-invariant matching is an optional symmetry-pathology sensitivity only.

---

## Risk 12 — “The external prediction AUROC <0.5 could simply reflect distribution shift/sign reversal, not absence of predictability.”

**Severity:** wording issue, not core threat.

**Evidence:** development CV is only modest, external generalization is poor, and the directional bulk/slab contrast does not replicate.

**Required wording:** “conventional metadata do not generalize as useful predictors across the tested corpora.” Do not say “resolvability is fundamentally unpredictable.”

**Remaining action:** no need for more ML models unless prediction becomes a central paper claim; it should remain a supporting negative result.

---

## Risk 13 — “Why only SZ3, ZFP and SPERR? Modern topology/local-order-preserving compressors exist.”

**Severity:** likely in 2026.

**Defense:** the study evaluates whether guarantees exposed by widely used general-purpose pointwise-error-bounded compressors are sufficient for a field-derived chemical QoI. Modern topology/order-aware codecs optimize different guarantees and are related algorithmic solutions, not required controls for this evaluation question.

**Required Related Work:** explicitly discuss TopoSZ, DMSC-preserving methods and the 2026 local-order-preserving compressor. State that the released benchmark is a natural testbed for these methods.

**Optional extension:** one compatible topology/local-order-aware codec in the supplement would strengthen the paper, but should not delay submission unless the target venue is explicitly compression-algorithm-centric.

---

## Risk 14 — “This is not novel; QoI-aware compression already exists.”

**Severity:** high if positioning is sloppy; controlled if wording is precise.

**Defense:** do not claim generic QoI novelty. Distinctive combination:
- field-derived integration domain is itself recomputed from reconstructed data;
- direct integrand/domain decomposition;
- QoI resolvability eligibility before certification;
- stability-probe validation against algorithmic invariants;
- nominal-bound-utilization versus realized-error-structure separation;
- reassignment attenuation linking full-table codec residual to the domain mechanism.

**Required wording:** evaluation/contract paper for field-derived chemical domains, not “first QoI-aware compressor.”

---

## Risk 15 — “Could global charge conservation explain the Bader errors instead of basin migration?”

**Severity:** moderate.

**Available evidence:** master table contains `electron_count_abs_dev`, while direct decomposition separates integrand and domain terms and finds domain dominance.

**Recommended additional post-processing:** explicitly test whether total/electron-count deviation predicts resolved Bader error after controlling realized L∞ and whether codec residual persists after adding it. This is cheap and uses existing master-table columns. If the effect is negligible relative to basin reassignment, report as a supplementary negative control.

**Status:** worth doing before manuscript freeze; no new compression/Bader runs required.

---

## Risk 16 — “Reassigned-voxel fraction is only a count; a few high-density voxels may matter more than many low-density voxels.”

**Severity:** real mechanism nuance.

**Defense:** this is exactly why the regression is only supporting evidence; direct charge decomposition is primary. The per-atom table will expose charge-weighted domain contributions directly.

**Optional future metric:** density-weighted reassigned mass or interface-localized reassignment if source label maps remain available. Do not invent this if it requires re-running the entire benchmark solely for one reviewer-proof metric.

---

## Risk 17 — “Early stopping at re-derived Bader error >=0.05 e biases codec comparisons.”

**Severity:** controlled for strict-contract results.

**Defense:** the central 1e-3/1e-2 certification analyses and matched-error stress tests restrict attention to operating regions far below the loose early-stop regime; the tight ladder was added specifically to resolve strict operating points. Matching/interpolation sensitivity further reduces dependence on nominal ladder alignment.

**Required wording:** explain early-stop rule in Methods and do not use censored loose-region same-nominal results as mechanistic evidence.

---

## Risk 18 — “The slab result at 1e-4 is based on only four eligible materials.”

**Severity:** presentation issue.

**Evidence:** n=4 in best-certified table.

**Required wording:** explicitly call strictest slab frontier descriptive. Do not use it as a broad slab ranking claim.

---

## Risk 19 — “Statistical pseudoreplication: thousands of rows/atoms from the same materials.”

**Severity:** high if mishandled; currently controlled.

**Defense:** primary matched ratios are summarized within material then bootstrapped across materials; fixed-effect regressions cluster standard errors by material; the per-atom analysis plan pre-specifies case/material aggregation rather than atom-level independent inference.

**Remaining action:** ensure every figure caption states material-level uncertainty where applicable.

---

## Risk 20 — “Is the final paper about compression, computational chemistry, or scientific methodology?”

**Severity:** editorial/venue risk.

**Recommended identity:** scientific-data methodology / scientific compression evaluation demonstrated on computational chemistry.

Core one-sentence thesis:

> A pointwise reconstruction guarantee is not a chemical fidelity contract when the downstream observable is defined on field-derived domains; the observable must be re-derived, shown to be numerically resolvable, and evaluated at the realized perturbation scale.

This identity should drive title, abstract, figures and venue selection.

# Remaining high-value work before submission

1. Finish and audit the preregistered per-atom mechanism table; update Figure 3 without changing the claim scope.
2. Run the cheap global-electron-count negative-control regression from existing master-table columns.
3. Replace all placeholder compressor references with verified bibliographic records.
4. Perform a final machine check that every numeric claim in the manuscript maps to `HEADLINE_NUMBER_REGISTRY_v03` or an explicitly named stratified table.
5. Choose target venue and adapt length/style only after scientific content is frozen.

# Work that is NOT currently justified

- rerunning the full benchmark with more generic compressors solely to increase codec count;
- changing frozen Protocol A.1 thresholds or seeds after seeing the outcomes;
- replacing the max-atom endpoint with a friendlier average metric;
- converting the reassignment regression into a causal claim;
- claiming a universal mechanism across all scientific QoIs.
