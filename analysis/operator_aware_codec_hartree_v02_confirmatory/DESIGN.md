# QOAC-H v0.2 disjoint confirmatory experiment

Freeze date: 2026-10-05

This experiment is frozen only after the v0.2 engineering implementation passed its post-engineering sanity audit. No QOAC-H v0.2 result from the confirmatory materials has been inspected before this protocol is defined.

## Frozen codec

The codec is the audited QOAC-H v0.2 Hermitian-orbit implementation inherited from branch research/qoac-h-v02-20261005.

No change to:
- beta = 2;
- conservative Nyquist alias metric;
- Hermitian-orbit representation;
- zlib level = 6;
- shell count = 32;
- alpha ladder;
- Hartree certificate.

## Confirmatory population

Exactly 48 previously unseen development materials:
- 24 bulk;
- 24 slab.

The 12 v0.1/v0.2 engineering materials are excluded before selection.

Within each system type:
1. restrict to development-corpus records;
2. exclude all engineering material IDs;
3. sort by npoints, then material_id;
4. divide the ordered list into 24 contiguous size strata;
5. within each stratum select the material with minimum SHA-256 of

       "QOAC-H-V02-CONFIRM|" + material_id.

Selection uses metadata only. It does not use codec performance, Hartree error, baseline ranking, chemistry, or QOAC-H output.

## Frozen alpha ladder

For every material run exactly 25 settings:

    alpha / ptp(rho) = logspace(1e-7, 1e1, 25).

No adaptive tuning, bisection, or post-hoc extension is allowed.

## Primary certificate

Primary threshold:

    tau_H = 1e-6 historical Hartree relative RMSE.

For each material, the QOAC-H candidate is the highest serialized compression ratio among evaluated rows satisfying the historical threshold.

The selected QOAC-H candidate must also satisfy:

    Nyquist-safe Hartree relative RMSE < 1e-6.

Failure of this safe guardrail is a confirmatory failure for that material.

The baseline candidate is the highest reproduced compression ratio among frozen ZFP/SZ3/SPERR rows satisfying:
- scientific_reproduction_gate_pass = true;
- historical Hartree relative RMSE < 1e-6.

## Primary comparison

For each material define

    R = CR_QOAC-H / CR_best-baseline.

The confirmatory claim is supported only if all of the following frozen criteria hold:

1. 48/48 materials are analyzable with zero QOAC-H setting failures.
2. 48/48 selected QOAC-H rows pass the Nyquist-safe guardrail.
3. At least 36/48 materials have R > 1.
4. Median R > 1.50.
5. Fixed-seed nonparametric bootstrap 95% CI lower bound for median R > 1.25.
6. Median R > 1.25 separately in bulk and slab subsets.
7. Wilson 95% lower confidence bound for the win fraction is > 0.50.

No criterion may be changed after execution begins.

## Secondary reporting

Report:
- per-material best QOAC-H CR and best baseline CR;
- baseline codec identity;
- historical and safe Hartree errors;
- density Linf and RMSE of the selected QOAC-H row;
- alpha selected from the frozen ladder;
- bulk/slab stratified medians;
- encode/decode timing;
- mean-density deviation and imaginary leakage.

Large real-space density error does not invalidate a Hartree-specific certificate, but it must remain visible as a scope boundary.

## Interpretation

Passing this experiment supports a disjoint-sample claim that operator-derived Hermitian-orbit compression provides materially higher Hartree-certified compression than the best evaluated ZFP/SZ3/SPERR baseline under the same tau_H=1e-6 scientific-use contract.

It does not establish superiority for Bader charge or arbitrary downstream QoIs.
