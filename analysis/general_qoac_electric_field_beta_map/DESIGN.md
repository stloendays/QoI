# General-QOAC electric-field beta map

Freeze date: 2026-10-05

Status: second engineering-only refinement after the first prospective beta=1 test returned directional improvement but failed the pre-specified strong-effect gates. No disjoint electric-field holdout has been selected or executed.

## Purpose

The ideal high-rate derivation predicts

    Delta_G propto |G|

for Hartree electric-field fidelity, corresponding to beta=1 in the Hermitian-orbit codec.

The first frozen engineering test showed:
- beta=1 beats beta=0 in 12/12 materials at matched serialized storage;
- beta=1 beats beta=2 in 10/12;
- effect sizes were smaller than the pre-specified GO thresholds.

This beta-map asks whether the finite-rate serialized optimum remains near beta=1 but is shifted by:
- non-asymptotic scalar quantization;
- coefficient-amplitude distributions;
- shellwise integer-width changes;
- zlib entropy coding.

This is development calibration only. It does not retroactively change the first experiment's NO-GO result.

## Population

Reuse exactly the same 12 engineering materials.

The frozen electric-field holdout remains unselected and unexecuted.

## Beta grid

Evaluate the full grid

    beta in {0, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00}.

Existing beta={0,1,2} rows from the completed first engineering experiment are reused unchanged.

New computation is restricted to

    beta in {0.25,0.50,0.75,1.25,1.50,1.75}.

For each new beta use the same frozen alpha ladder:

    alpha / ptp(rho) = logspace(1e-7,1e1,25).

New planned rows:

    12 * 6 * 25 = 1800.

Combined beta-map rows:

    12 * 9 * 25 = 2700.

No additional beta or alpha value may be added after execution begins.

## Primary electric-field metric

Use the already frozen Nyquist-safe electric-field relative RMSE.

The formal all-mode historical spectral metric remains a diagnostic only.

## Common-rate interpolation

Direct pair matching can leave slightly different storage locations for different beta values. The beta-map therefore compares all exponents on the same per-material serialized-rate support.

For each material and beta:
1. take successful rows with positive CR and positive safe electric-field error;
2. sort by log10(CR);
3. collapse duplicate log10(CR) values by retaining the minimum log10(error);
4. linearly interpolate log10(error) as a function of log10(CR).

For each material, define the common overlap:

    L = max_beta min(log10 CR_beta)
    U = min_beta max(log10 CR_beta).

Require U > L.

Use exactly 11 target rates equally spaced over the interior interval

    [L + 0.05(U-L), U - 0.05(U-L)].

No extrapolation is allowed.

## Material-level finite-rate optimum

At every common target rate, interpolate the safe electric-field error for every beta.

For each material and beta compute

    S_m(beta) =
      median_target [
        log10 D_E(beta,target)
        - log10 D_E(beta=1,target)
      ].

The material-level optimum is the beta minimizing S_m(beta).

Ties within 1e-12 are resolved by:
1. smallest |beta-1|;
2. then smaller beta.

## Global finite-rate optimum

For every beta compute

    S_global(beta) = median_material S_m(beta).

The development-selected finite-rate exponent beta_star is the beta minimizing S_global(beta), with the same deterministic tie rule.

This definition is frozen before the new beta rows are calculated.

## Engineering interpretation gates

These gates determine whether a future disjoint electric-field confirmation is scientifically justified.

### Gate M1 — operator prediction remains locally informative

GO if

    beta_star in [0.75, 1.50].

This allows finite-rate correction but requires the optimum to remain near the beta=1 operator prediction rather than collapsing to the operator-blind beta=0 or Hartree beta=2 endpoints.

### Gate M2 — calibrated optimum beats both wrong endpoint geometries

For each material evaluate the median common-rate error ratios

    D_E(beta_star) / D_E(beta=0)
    D_E(beta_star) / D_E(beta=2).

GO if:
- beta_star beats beta=0 in at least 9/12 materials;
- beta_star beats beta=2 in at least 9/12 materials;
- global median ratio versus beta=0 < 0.80;
- global median ratio versus beta=2 < 0.95.

### Gate M3 — beta=1 remains near the calibrated optimum

At the same common rate targets compute

    D_E(beta=1) / D_E(beta_star).

GO if the global median ratio is < 1.10.

This gate distinguishes a modest finite-rate correction from a failure of the operator-derived exponent.

## Next step if M1-M3 pass

Freeze a new disjoint confirmatory cohort that excludes:
- the 12 electric-field engineering materials;
- the 48 QOAC-H confirmatory materials.

The confirmatory exponent will be beta_star, frozen from this development map.

The confirmatory analysis must also report beta=1 as a theory-only comparator so that empirical calibration is not conflated with the analytic prediction.

No holdout execution is authorized by this file alone; authorization requires completed M1-M3 results.

## Scope

The beta-map calibrates only the finite-rate realization of the electric-field operator within the current Hermitian-orbit/zlib representation.

It does not modify:
- the electric-field operator derivation;
- the QOAC-H beta=2 result;
- QOAC-B projection results;
- the original electric-field engineering NO-GO record.
