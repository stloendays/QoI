# QOAC-B2 — fixed-partition Bader constraint projection confirmation

Freeze date: 2026-10-05

Status: prospective confirmatory protocol defined after QOAC-B1 engineering and before any QOAC-B transform is applied to the frozen 38-material holdout.

## Engineering result that motivated this protocol

QOAC-B1 established two distinct facts on the 12-material engineering set:

1. Fixed-partition basin-sum closure is the correct Bader-sensitive mechanism. Selected reconstructions had zero actual Henkelman Bader error and zero reassignment.
2. Encoding a basin-mean-subtracted residual is a poor rate representation: the residual arm had median CR ratio 0.401 versus the frozen G1 baseline and 0.299 versus projection-only.

The projection-only arm, by contrast, adds only O(number of partition regions) side information to an ordinary codec and leaves the field distortion nearly unchanged.

This confirmatory protocol therefore tests QOAC-B as a **constraint-projection wrapper**, not as a new entropy transform.

## Frozen holdout

Use exactly the 38 materials already frozen by QOAC-B1 in:

    analysis/operator_aware_bader_fixed_partition/results/FROZEN_HOLDOUT_MANIFEST.csv

These materials were not transformed or evaluated by QOAC-B1 engineering.

No material may be added, removed or replaced.

## Declared measurement contract

Partition-defining input:
- exact AECCAR0 + AECCAR2;
- Henkelman Bader 1.05 on-grid semantics: -b ongrid -vac 0.001.

Integrated field:
- CHGCAR compressed by the frozen ZFP/SZ3/SPERR settings already present in WP-G.

For every successful frozen WP-G G1 row on every holdout material:

1. reproduce the same generic codec and absolute CHGCAR tolerance;
2. decode the generic field;
3. use the exact-reference partition labels;
4. store the exact discrete target sum for every non-negative partition region;
5. uniformly shift each decoded region so that its discrete sum equals the original region sum;
6. count the complete side channel in bytes;
7. rerun Henkelman Bader on the projected field with exact AECCAR.

No codec tolerance is tuned on the holdout.

## What QOAC-B2 is claiming

The confirmatory claim is not that the wrapper always improves compression ratio.

It is:

> Under a qualified fixed Bader partition, a decoded error-bounded density can be projected onto the Bader charge constraints with negligible storage overhead and small field-distortion inflation, converting generic codec operating points into Bader-certified reconstructions without storing only the final atomic charges.

The full three-dimensional density remains available after decoding.

## Primary Bader contract

    tau_B = 1e-3 e.

Secondary reporting:

    1e-4 e and 1e-2 e.

## Gate A — actual solver guarantee

Across **every transformed holdout row**:

- actual max Henkelman atomic-charge error <= 2e-6 e;
- actual partition-label reassignment fraction = 0;
- scaled discrete region-sum closure <= 1e-9.

This is deliberately stronger than checking only selected best rows.

## Gate B — rate overhead

For

    overhead = side_channel_bytes / generic_payload_bytes,

require:

- median overhead < 0.1%;
- 95th percentile overhead < 1%;
- maximum overhead < 5%.

The exact AECCAR is part of the declared downstream measurement contract and is not charged to either generic G1 or QOAC-B2 CHGCAR bytes.

## Gate C — field-fidelity preservation

For

    r_Linf = Linf(projected reconstruction) / Linf(generic reconstruction),

require:

- median r_Linf <= 1.01;
- 95th percentile r_Linf <= 1.10;
- maximum r_Linf <= 1.25.

This prevents the Bader guarantee from being obtained by silently degrading the raw density field.

## Gate D — rescue of generic Bader failures

At tau_B = 1e-3 e, define the pre-existing generic-failure set as all frozen G1 rows with

    generic Bader error >= tau_B.

A row is rescued if QOAC-B2 satisfies the actual Bader contract and

    Linf_projected <= 1.05 * Linf_generic.

Require:

- at least 80% of generic-failure rows are rescued;
- at least 80% of holdout materials that contain one or more generic-failure rows have at least one rescued row.

The same rescue statistics are reported, but not gated, at 1e-4 e and 1e-2 e.

## Rate-fidelity reporting

For completeness, also report at each Bader tolerance:
- number of generic-failure rows;
- number and fraction rescued;
- distribution of side-channel overhead;
- distribution of field-Linf inflation;
- per-codec rescue fractions.

Do not interpret the same-setting side-channel overhead as a new entropy-codec compression gain.

## Interpretation boundary

Passing QOAC-B2 supports a fixed-partition guarantee layer.

It does not establish:
- preservation when AECCAR is itself compressed;
- preservation of Bader topology without an exact reference;
- a Fourier/eigenvalue allocation law for Bader;
- superiority for unrelated QoIs.

Compression of the partition-defining field remains the separate QOAC-B3/topology-aware problem.
