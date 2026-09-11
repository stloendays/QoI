# Independent perturbation validation and common-ladder completion

Specified 2026-09-11, after inspection of the frozen common-ladder and retrospective seed-holdout audit. **New outcomes have not been measured by this work order.** This is an additive research extension, not an amendment of the archived protocol. The method name remains QoI Stability Qualification (QSQ).

## Scope and non-leakage

Primary population: all 254 development materials in the frozen benchmark. These materials are not new external data. New seed realizations provide an independent perturbation test of the already-fixed five-seed gate, conditional on these materials and the declared distribution. The existing 63-system external cohort is already observed and cannot be repurposed as untouched validation for an upgraded policy.

Before scientific execution, generate and commit `execution_manifest.json`, `missing_tight_jobs.csv`, `fresh_seed_jobs.csv` and `convergence_panel.csv` using `scripts/prepare_qsq_confirmation.py`. Input SHA-256 values and the preparation source commit must be recorded. Freeze the original compute-runner commit, density loader, solver versions and environment hashes in an execution addendum before starting. Until those are linked, the work orders are **PREPARED, NOT EXECUTED**.

## Primary common-ladder extension

Use the four tight nominal settings already present in the frozen master table; do not introduce a different tolerance grid. Request every missing development material-codec-tight-setting tuple, including QSQ-non-evaluable materials. Under the current record this is 111 materials x 3 codecs x 4 settings = 1,332 planned jobs. Store all attempts, including solver errors and missing-input errors. A candidate without a valid downstream result is unavailable, not an automatic numerical failure or pass.

Retain the existing base-only, shared-observed-base and full-record analyses. The completed common tight ladder is a separate analysis, not a retroactive modification of Figure 3's frozen counts. All comparisons must report support, attempted and completed settings, both numerical pass/fail and QSQ eligibility, exclusion prevalence, and material-cluster uncertainty.

## Primary independent probe test

Keep the deployed five-seed gate and the material-specific float32 Linf amplitude unchanged. For every development material, generate 59 fresh iid uniform perturbation fields at that amplitude. Fresh seed labels are 10000 through 10058, none of which belongs to the old set {20260905,1,2,3,4}.

Define each actual PRNG stream from the first eight bytes, interpreted little-endian, of SHA-256 over `QSQ-heldout|material_id|iid_uniform|seed_label`. Use NumPy Generator(PCG64(stream_seed)), float64 uniform draws on [-epsilon,+epsilon), and the original validated field shape/order. Record NumPy version, shape, ordering, stream_seed and measured Linf. A reproducible pseudorandom construction implements the declared sampling model; statistical independence is an assumption to state, not a property inferred from reproducibility alone.

Primary endpoint: reference Bader response >= 1e-3 e among materials admitted by the original five-seed gate. Thresholds 1e-4 and 1e-2 e are prespecified secondary endpoints. Also report responses in the rejected group rather than hide that population. Record maximum per-atom response, baseline and perturbed atom-resolved charges, basin labels or their hashes, voxel reassignment, integrated charge difference, solver status, runtime and peak memory when available.

There are 254 x 59 = 14,986 planned primary probe jobs. The same response vector supports all three thresholds; thresholds are not three independent experiments.

No new probe outcome is used to modify the legacy admission rule. Tuning an extension requires a separately declared calibration pool and later independent validation. Do not compare seed budgets using held-out sets whose sizes change with budget; a separate fixed validation panel must be shared by the budget arms.

## Additional perturbation families: secondary controls, not pooled replicas

Unconstrained iid uniform noise is retained as the exact-comparability numerical stress test. It is not automatically a physically realistic uncertainty model: in vacuum it can produce negative density values.

For a nonnegative reference and uniform voxel volumes, a charge-neutral density-preserving control can use u_i in [-1,1], w_i=min(1,rho_i/epsilon), c=sum(w_i u_i)/sum(w_i), and eta_i=(epsilon/2) w_i (u_i-c). Then sum(eta_i)=0, |eta_i|<=epsilon, and rho_i+eta_i>=0. Handle epsilon=0 and sum(w)=0 explicitly as degenerate controls, not random evidence. For nonuniform volumes use volume-weighted sums. If the reference already has negative entries, label the control inapplicable and investigate the representation; do not silently clip the reference. Floating-point residuals in neutrality and positivity must be reported and checked against a specified numerical tolerance in the runner.

A spatially correlated secondary control can generate periodic Gaussian-filtered iid fields at fixed correlation lengths of one and four grid spacings, scale u into [-1,1], and apply the same weighted neutral transformation. Freeze the filter, normalization and RNG implementation before these runs. Actual Linf, L2, charge deviation and correlation measures must be reported; do not assume these fields have the same realized amplitude as the iid family.

Amplitude multipliers 0.1 and 10 are secondary sensitivity analyses. They do not replace the primary amplitude after outcomes are seen. New families require their own committed job lists and cannot be pooled into the iid sample-size calculation.

## Statistical reporting and decision criteria

For a fixed material/family/threshold, report k/n exceedances and a one-sided 95% exact binomial upper bound under the iid Bernoulli assumption. With zero events in 59 independent validation draws, the bound is 1-0.05^(1/59)=0.049508. This is a per-cell statement, not a simultaneous certificate for all materials or families. Simultaneous claims require a predeclared multiplicity correction and sufficient n; do not apply an uncorrected 59-draw claim to every cell at once.

Cohort-level summaries must resample materials (and preserve their probe clusters), not count every voxel, atom or repeated seed as an independent material. Report the acceptance fraction as well as conditional exceedance risk. Solver failure is a separate event; provide conservative accounting that treats unresolved trials as adverse when computing any advertised upper reliability bound, or withhold that bound.

A single valid exceedance refutes a uniform <tau reference-stability statement. A finite panel with no exceedances does not prove worst-case stability. This experiment does not on its own identify the causal source of a codec discrepancy.

## Convergence panel preparation

Select three systems by deterministic SHA-256 ordering in each of eight strata: bulk/slab crossed with the four frozen floor bands below 1e-4, 1e-4 to below 1e-3, 1e-3 to below 1e-2, and at least 1e-2 e. This gives 24 targeted development systems. Use these for numerical-mechanism comparison, not population prevalence estimates.

A subsequent execution addendum must fix genuine density-grid recomputation settings, valence/all-electron conventions, atom correspondence, independent Bader implementations and convergence endpoints. Interpolated copies of one density field cannot be described as new electronic-structure convergence calculations.

## Outputs and execution status

Prepared work orders are not scientific results. Completion requires raw input and runner fingerprints, timestamped requested-job records, all successful or failed outcomes, and an immutable output manifest. No additional outcome is assumed successful merely because a script or GitHub workflow was created.

Primary references: NIST exact binomial limits, https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm; Yu and Trinkle Bader integration, https://arxiv.org/abs/1010.4916. See `paper/ROBUST_FIDELITY_FOUNDATIONS.md` for the distinction between numerical agreement, reference robustness and coupled recompression.
