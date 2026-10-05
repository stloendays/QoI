# QOAC-H v0.1 — operator-aware Hartree compression pilot

Date frozen: 2026-10-05

Status: prospective research branch. This experiment does not modify the frozen manuscript, QSQ definitions, or prior Hartree mechanism evidence.

## Scientific question

Can the known Hartree/Poisson operator be used to place reconstruction error in reciprocal space more efficiently than operator-blind scalar quantization, and ultimately more efficiently than the existing ZFP/SZ3/SPERR benchmark ladders?

For electron density rho and reconstruction error delta rho,

D_H^2 is proportional to

    sum_{G != 0} |delta rho(G)|^2 / |G|^4.

Under the high-rate scalar-quantization approximation E|delta_G|^2 proportional to Delta_G^2, minimizing Hartree distortion at fixed rate gives the first-order allocation law

    Delta_G proportional to |G|^2.

QOAC-H v0.1 tests that law directly. The exponent beta=2 is fixed before any QOAC-H result is produced. beta=0 is the operator-blind spectral-quantization ablation.

## Codec contract

1. Transform the real-space density with an orthonormal real FFT.
2. Compute physical reciprocal vectors from the material lattice, not FFT indices alone.
3. Preserve G=0 exactly.
4. Preserve every even-grid Nyquist plane exactly. This avoids the alias/Hermitian ambiguity already identified in the Hartree mechanism audit and prevents metric gaming.
5. For all remaining modes use

       Delta_G = alpha * (|G| / G_max)^beta.

6. Quantize real and imaginary coefficient components independently with nearest-integer rounding.
7. Group coefficients by radial shell for storage only; within each shell use the smallest signed integer dtype that can represent all quantized values and zlib-compress the block.
8. The serialized stream contains all metadata required for decoding, including lattice, shape, alpha, beta, shell count, exact special coefficients and compressed shell payloads.
9. Decode the serialized bytes, inverse FFT, then recompute the downstream Hartree quantity. The design surrogate never substitutes for the downstream certificate.

Primary method: beta=2.
Primary ablation: beta=0.

## Pilot population

The pilot contains exactly 12 development materials: 6 bulk and 6 slab.

Selection is outcome-blind and deterministic from materials_metadata.csv only:
- restrict to development bulk/slab records;
- within each system type, sort by npoints;
- divide the ordered population into six contiguous size strata;
- in each stratum select the material with the smallest SHA-256 of the string "QOAC-H-V01|" + material_id.

No QOAC-H output, prior codec ranking, Hartree error, Bader result or QSQ eligibility enters material selection. The exact generated manifest is archived with the pilot outputs.

## Alpha ladder

For every material and both beta values, run 25 settings:

    alpha / ptp(rho) = logspace(1e-7, 1e1, 25).

This is an exhaustive pilot ladder. No bisection or adaptive search is used in v0.1.

## Primary Hartree contract

Primary scientific-use threshold:

    tau_H = 1e-6 relative Hartree RMSE.

The historical Hartree operator is the primary certification metric for continuity with the completed full-population Hartree-QSQ study. The Nyquist-safe metric is reported in parallel. Because QOAC-H preserves Nyquist planes exactly, numerator discrepancies between the two operators should be limited to numerical roundoff; denominators remain operator-specific.

## Mechanism GO / NO-GO

Within each material, beta=2 and beta=0 rows are greedily matched without replacement on log10(compression ratio), with a 0.05-dex caliper.

A material is mechanism-evaluable only with at least three matched pairs.

For each evaluable material compute the median

    r_H = D_H(beta=2) / D_H(beta=0).

Mechanism GO requires both:
- at least 75% of evaluable materials have r_H < 1;
- the median material-level r_H is < 0.70.

This gate tests the operator-derived allocation itself and is independent of whether the prototype entropy coder beats mature codecs.

## Competitive GO / NO-GO

At tau_H = 1e-6, for each material:
- QOAC-H candidate = highest actual serialized compression ratio among beta=2 settings satisfying the historical Hartree contract;
- baseline candidate = highest reproduced compression ratio among ZFP/SZ3/SPERR frozen Hartree rows satisfying the same contract and scientific reproduction gate.

Define

    r_CR = CR_QOAC-H / CR_best-existing-baseline.

Competitive GO requires:
- at least 9/12 materials have a comparable certified QOAC-H and baseline row;
- median r_CR > 1.05;
- fixed-seed bootstrap 95% CI lower bound for the median r_CR is > 1.0.

A mechanism GO with competitive NO-GO is still scientifically useful: it means the operator-derived error placement works, while the v0.1 serialization/rate model requires engineering improvement.

## Secondary guardrails

Every reconstruction records:
- density Linf error;
- density RMSE;
- mean-density deviation;
- negative-density voxel fraction and its change from reference;
- serialized bytes and compression ratio;
- encode and decode wall time;
- historical and Nyquist-safe Hartree relative RMSE.

These are diagnostic guardrails, not substitute optimization objectives.

## Baseline and provenance policy

The existing analysis/hartree_qsq_full/results/hartree_codec_rows.csv is the baseline authority; no prior codec result is recomputed for the pilot.

The source loader and scientific environment reuse the frozen external stack at commit 893f931b3045b0b628329db81999c2f439d4e830, as in the completed Hartree mechanism audit.

All source SHA-256 and byte counts must pass before a material is analyzed. Failures are retained explicitly.

## Interpretation boundaries

Do not claim from this pilot:
- universal optimality of beta=2 outside the linear Hartree/Poisson operator;
- QoI-aware compression novelty in general;
- Bader improvement;
- cross-domain generality;
- production-code superiority from idealized rate estimates.

Only actual serialized bytes count as the primary QOAC-H rate in this pilot.
