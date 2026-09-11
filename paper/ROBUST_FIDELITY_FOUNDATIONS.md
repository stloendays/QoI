# Numerical fidelity and robust scientific fidelity

Research extension opened 2026-09-11. This note defines targets for the next experiments. It does not change the frozen QSQ protocol, measured charges, thresholds or historical labels. The elementary inequalities below are mathematical groundwork, not a claim of a novel general theorem.

## 1. Two questions that must not be conflated

Let F be the fully specified downstream numerical operator, including density representation, grid, solver, basin convention, atom correspondence and boundary conditions. Let rho be its reference input and rho_tilde a decoded input.

**Fixed-pipeline numerical fidelity:** D = ||F(rho_tilde) - F(rho)||_infinity. This discrepancy is well defined even when F is sensitive to small input changes. In particular, an exact reconstruction under the same deterministic pipeline has D = 0. Failure of a reference-stability screen does not make this equality disappear.

**Reference robustness:** select and justify an admissible perturbation set A, containing zero, and define S = sup_{eta in A} ||F(rho+eta)-F(rho)||_infinity. S depends on A, F and rho. It is not automatically an intrinsic material constant, nor a continuum-limit Bader error estimate.

The frozen QSQ rule combines an empirical reference screen with numerical agreement. This is a useful operational classification, but not yet a worst-case or calibrated probabilistic certificate.

## 2. A target with a genuine error budget

One possible robust target is the reference-envelope discrepancy

R = sup_{eta in A} ||F(rho_tilde)-F(rho+eta)||_infinity.

It compares one fixed reconstruction output with all admissible reference outputs. It is appropriate only when this is the intended scientific contract; it is not the only possible robustness definition.

For finite S,

max(D, S-D) <= R <= D+S.

Proof: eta=0 gives R>=D. The triangle inequality gives each reference-to-reconstruction discrepancy at most D+S. The reverse triangle inequality gives R>=S-D after taking the supremum. No independence assumption is needed.

Consequently, D+S<tau is sufficient for R<tau. Testing D<tau and S<tau separately is not sufficient: in one dimension, take F(rho)=0, F(rho_tilde)=0.8 tau and one admissible reference output F(rho+eta)=-0.8 tau. Both separate tests pass, but R=1.6 tau.

The finite-probe maximum S_hat is a lower bound on S when all probes belong to A. Substituting S_hat for S in the sufficient condition does NOT turn it into a worst-case certificate. A mathematical bound or an explicitly probabilistic target is required.

## 3. A distinct coupled-pipeline target

For a codec C, another possible target is

R_coupled = sup_{eta in A} ||F(C(rho+eta))-F(rho+eta)||_infinity.

This tests compression agreement when the uncertain input is perturbed and then recompressed. It requires new codec/downstream evaluations; it cannot be inferred from the reference-only probe table. Do not silently substitute this target for the reference-envelope target.

For chemical decisions g(F(rho)), directly assess sign, ordering or threshold decisions under their stated uncertainty model. Bader charges must not be equated automatically with formal oxidation states.

## 4. Statistical screening with a declared perturbation distribution

For a fixed material, fixed operator and a declared distribution P, define p_ref(tau) = Pr_{eta~P}(||F(rho+eta)-F(rho)||_infinity >= tau). Analogous exceedance probabilities can be defined for the reference-envelope or coupled-pipeline targets. They are different estimands and need separate measurements.

If a candidate/policy was selected before an independent validation panel and the panel consists of n iid Bernoulli exceedance indicators with k exceedances, a one-sided exact binomial upper confidence limit can bound this conditional risk. For k=0, confidence 1-alpha gives p_upper = 1-alpha^(1/n).

At alpha=0.05, n=5 gives p_upper=0.450720 and n=59 gives p_upper=0.049508. Thus five uneventful probes do not certify a 5% exceedance risk. This calculation is for one fixed target and distribution. It does not certify worst-case stability, distribution shift, every material simultaneously, or the error rate of the deployed five-seed QSQ rule using the same five development observations.

To make simultaneous claims over M predeclared cells, one conservative approach is alpha_cell=alpha_total/M. For zero events and a target risk p0, a fixed sample size must satisfy n >= ceil(log(alpha_cell)/log(1-p0)). Alternatively report clearly labelled per-cell intervals and reserve the family-wise claim. Do not stop at the first favourable fixed-n interval; use a fixed validation panel or a separately justified sequential method.

Exact-binomial methodological source: NIST Dataplot, EXACT BINOMIAL, https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm (accessed 2026-09-11).

## 5. Evidence already available, and what it cannot establish

The common-ladder audit in `analysis/research_upgrade/REPORT.md` reproduces the frozen Figure 3 counts, then shows that the fraction of no-pass decisions on QSQ-non-evaluable materials changes from 97.2%/95.5%/56.5% in the full record to 83.2%/56.5%/51.3% on the base ladder. Eligibility itself was not changed. The high full-record proportions are sensitive to eligibility-targeted tight-ladder access; they are not design-independent causal attribution estimates.

The four-training-seed/one-held-out-seed audit gives 18/338, 12/947 and 1/1441 held-out exceedances among retrospectively admitted material-splits at the three thresholds. Materials, not splits, are the resampling units. The seeds were already used in development; this is screening-fragility evidence, not prospective confirmation.

## 6. Required research advance

The upgraded study must compare policies at comparable useful coverage and computational cost, not reward abstaining on everything. Required baselines include fixed-pipeline agreement alone, the archived float32 screen, frozen five-seed QSQ, and any development-calibrated risk-controlled extension. Fresh perturbations, an independent convergence panel, and genuine task decisions provide the validation; the choice of policy and scientific endpoint must precede confirmatory outcomes.
