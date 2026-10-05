# QOAC-H v0.2 full development-population census

Freeze date: 2026-10-05

Status: exhaustive post-confirmatory population audit.

The v0.2 codec, beta=2 law, Hermitian-orbit representation, conservative Nyquist metric, zlib level, shell count and 25-point alpha ladder are frozen from the successful disjoint confirmatory experiment. No codec tuning is permitted in this census.

## Population

Analyze every development material in materials_metadata.csv with system_type in {bulk, slab}.

Frozen population count:
- 186 bulk;
- 68 slab;
- 254 total.

This is a census of the complete development population, not an additional holdout sample. It therefore reports population performance descriptively rather than using sampling uncertainty as the main evidence.

## Frozen codec search

For each material evaluate exactly:

    alpha / ptp(rho) = logspace(1e-7, 1e1, 25)

with:
- beta = 2;
- shell_count = 32;
- zlib_level = 6;
- only G=0 stored exactly.

## Hartree scientific-use ladder

Evaluate these downstream tolerances:

    1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3

For each material and tolerance tau:

1. QSQ eligibility requires

       hartree_qsq_response_scale_rel_RMSE < tau.

2. QOAC-H candidate is the highest serialized CR among evaluated rows with

       historical Hartree relative RMSE < tau.

3. The selected QOAC-H row must also satisfy

       Nyquist-safe Hartree relative RMSE < tau.

4. Baseline candidate is the highest reproduced CR among frozen ZFP/SZ3/SPERR rows with:
   - scientific_reproduction_gate_pass = true;
   - historical Hartree relative RMSE < tau.

5. For materials with both candidates define

       R(tau) = CR_QOAC-H / CR_best-baseline.

## Required reporting

For every tau report:
- QSQ-eligible material count;
- comparable material count;
- QOAC-H win count and win fraction;
- median, 5th, 25th, 75th and 95th percentiles of R;
- minimum R;
- median absolute QOAC-H CR;
- median absolute best-baseline CR;
- bulk median R;
- slab median R;
- count passing the Nyquist-safe guardrail.

Also retain per-material/tolerance rows and all 6350 raw QOAC-H settings.

## Completeness gate

The census is valid only if:
- 254/254 materials are planned;
- 6350/6350 QOAC-H settings complete;
- zero setting/material failures;
- every serialized row records exact_modes = 1.

No performance threshold is used to decide whether the census is retained.
