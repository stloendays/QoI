# Proposed claim-evidence update after realized-Linf and reviewer stress tests

Branch-only proposal. Do not overwrite the frozen main-branch claim matrix until the per-atom mechanism commit is available and the wording is accepted.

## A. Existing Claim 1 — split into two claims

### Claim 1a — nominal pointwise bounds do not determine chemical fidelity
**Status: CONFIRMED.**

Keep the current A.1-admitted same-nominal headline numbers in the frozen claim matrix (6.4x / 9.2x / 12.4x for SZ3/ZFP at 1e-4 / 1e-3 / 1e-2). However, change the interpretation: these ratios mix two effects because the codecs use their nominal pointwise budgets differently.

Evidence for bound utilization:
- SZ3 median realized/nominal L∞ = 1.000.
- SPERR = 1.000.
- ZFP = 0.1575 (IQR 0.1323–0.1939).

Therefore same-nominal comparisons alone are not evidence that spatial structure causes the entire codec gap.

### Claim 1b — a codec-associated residual remains after controlling realized L∞ and QoI resolvability
**Status: CONFIRMED.**

Primary stability-qualified result at tau = 1e-3 e and <=0.10 dex realized-L∞ matching:
- SZ3/ZFP = 1.90x [1.70, 2.20], 128 materials, SZ3 worse in 91.4%.
- SPERR/ZFP = 1.87x [1.63, 2.08], 124 materials, SPERR worse in 79.8%.

Reviewer stress tests:
- Restrict nominal relative tolerance to <=0.01: SZ3/ZFP 1.82x [1.68,2.03]; SPERR/ZFP 2.01x [1.84,2.38].
- Alternative within-material common-support interpolation: 2.08x [1.96,2.16] and 2.04x [1.88,2.21].
- Conservative complete-case exclusion of every material with any <=0.01 registered failure (20 materials removed; 254 -> 234): matched ratios 1.82x [1.68,2.01] and 2.00x [1.79,2.25]; interpolation 2.07x [1.95,2.19] and 1.99x [1.83,2.21].

Safe wording:
> At comparable measured pointwise error and among systems on which Bader charge is resolvable at the requested contract, codec identity remains associated with an approximately twofold difference in re-derived Bader-charge error.

Do not call the adjusted codec coefficient itself causal.

Evidence files:
- `analysis_output/stability_qualified_structure_effect.md`
- `analysis_output/reviewer_stress_tests.md`
- `analysis_output/complete_case_failure_sensitivity.md`

## B. Existing Claim 2 — fixed-basin evaluation is biased
**Status: CONFIRMED, strengthened.**

Across all 4,627 successful base-ladder rows:
- resolved error > fixed-basin error in 99.7% of rows;
- median resolved/fixed ratio 52.8x overall;
- SPERR 100.1x, SZ3 8.0x, ZFP 106.9x.

This is stronger and more transparent than saying only “9–11x smaller,” but manuscript denominators must state that these are successful base-ladder rows and ratios use finite values.

Evidence: `analysis_output/reviewer_stress_tests.md`.

## C. Existing Claim 4 — domain migration dominates

### Narrow claim
> In the preregistered/representative 12-material mechanism set, movement of the re-derived Bader domains dominates the measured maximum-atom charge error.

**Status: CONFIRMED for the representative mechanism set.**

Evidence:
- 106 successful mechanism cases across 12 materials.
- decomposition closure residual <= 2.22e-16 e.
- bounded dominance `|domain|/(|domain|+|integrand|)` median 0.995, IQR 0.965–0.999.
- 84.9% of cases exceed 0.90.

Use the bounded dominance definition; do not use `|domain|/|total|` as a dominance fraction because cancellation can make it exceed one.

### Full-corpus generalization
> Domain migration is the dominant mechanism for all or most of the full 254-material corpus.

**Status: NOT ESTABLISHED.**

The 12-material mechanism set is intentionally representative rather than exhaustive. Keep general wording conditional until the per-atom table lands and its selection/generalization limits are explicit.

## D. New mechanism-consistency claim — basin reassignment explains the codec-associated residual statistically

**Status: CONFIRMED as attenuation / mediation-consistent evidence; NOT causal mediation.**

At A.1 tau=1e-3 e, <=0.01 nominal relative tolerance, common realized-L∞ support, material fixed effects:
- SZ3/ZFP: 2.32x before reassignment adjustment -> 0.98x after adding reassigned-voxel fraction.
- SPERR/ZFP: 2.10x -> 0.95x.
- reassignment coefficient = 0.840 log10-Q per log10 reassigned fraction [0.691,0.988].

Complete-case version removing all 20 low-tolerance failure-affected materials:
- SZ3/ZFP: 2.34x -> 0.96x.
- SPERR/ZFP: 2.08x -> 0.94x.
- reassignment coefficient = 0.880 [0.723,1.037], p=5.78e-28.

Safe wording:
> The approximately twofold codec-associated residual is almost completely attenuated after conditioning on the amount of basin reassignment, consistent with basin migration mediating the link between codec-specific reconstruction structure and Bader-charge error.

Required caveat:
- `frac_voxels_reassigned` is a post-compression variable and is not randomized.
- attenuation therefore supports the mechanism but is not a formal causal-mediation estimate.
- the direct decomposition is the stronger mechanistic evidence.

## E. Failure-registry interpretation

**Status: CLOSED as a major threat to the matched-L∞ result, with explicit reporting required.**

At nominal relative tolerance <=0.01 there are 24 registered failure rows across 20 materials:
- ZFP 20 failures (bulk 1 at 0.01; slab 4 at 0.003 and 15 at 0.01).
- SPERR 4 slab failures (3 at 1e-4; 1 at 0.003).

These failures are non-random across codecs, so successful-row analysis alone could in principle be selectively censored. The complete-case analysis removes the entire affected material regardless of which codec failed and leaves the ~2x matched/interpolated codec residual essentially unchanged. This should be reported as a sensitivity analysis, not hidden.

## F. Claim wording hierarchy for the manuscript

1. **Primary evaluation claim:** the downstream QoI must be re-derived from the reconstructed field rather than evaluated on frozen original domains.
2. **Stability claim:** the QoI must be numerically resolvable at the intended contract, and the stability probe itself must perturb the algorithmically relevant structure.
3. **Magnitude/structure claim:** nominal tolerance conflates bound utilization with error structure; a ~2x codec-associated residual remains after realized-L∞ and stability control.
4. **Mechanism claim:** direct representative-set decomposition plus full-table reassignment attenuation identifies basin migration as the mechanism consistent with that residual.
5. **Practical claim:** the best certified compression choice changes with the chemical contract and certification coverage; no codec is universally best.

## G. Claims to avoid

- “This is the first work to show pointwise bounds do not preserve QoIs.”
- “The ~6–12x same-nominal gap is caused by spatial error structure.”
- “Codec identity causally doubles Bader error.”
- “Basin migration dominates every material in the corpus.”
- “Bader resolvability is fundamentally unpredictable.”
- “ZFP is universally the best compressor.”
