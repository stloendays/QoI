# QOAC-B1 — fixed-partition Bader compression engineering pilot

Freeze date: 2026-10-05

Status: prospective engineering study. This branch does not modify the active manuscript. The purpose is to test whether the Bader measurement contract admits a second compression geometry that is fundamentally different from the Hartree/Fourier case.

## Scientific hypothesis

With the all-electron partition field held exact, Henkelman on-grid Bader basins are fixed by the reference field. Bader charge of atom i then reduces to a linear integral over a fixed basin,

    Q_i(rho | Omega) = integral_{Omega_i} rho(r) dr.

The high-dimensional CHGCAR field therefore decomposes into:
- one basin-integral-sensitive mode per partition region;
- a large within-basin zero-sum nullspace that does not change the fixed-partition Bader charges.

QOAC-B1 tests whether protecting the low-dimensional basin sums while coding only the nullspace residual improves Bader-certified compression without relaxing the final raw-field Linf relative to the best certified generic-codec row.

## Contract

Partition-defining input:
- AECCAR0 + AECCAR2;
- kept exact;
- Henkelman Bader 1.05 semantics inherited from WP-G: -b ongrid -vac 0.001.

Integrated field:
- CHGCAR;
- compressed.

Primary Bader tolerance:

    tau_B = 1e-3 e.

Secondary engineering tolerances:

    1e-4 e and 1e-2 e.

The exact-reference setting is deliberate. It isolates compression of the integrated field from the already demonstrated partition-field instability.

## Population split

Start from the 50 WP-G materials with successful finite all-electron-reference analysis.

Before running QOAC-B1:
- sort the 50 materials by npoints;
- divide into 12 contiguous size strata;
- select one engineering material per stratum by minimum SHA-256 of
  "QOAC-B1-ENGINEERING|" + material_id;
- the remaining 38 materials are frozen as untouched holdout.

No QOAC-B1 result, codec ranking, Bader error, chemistry, or prior best compression ratio enters the split.

The holdout must not be executed unless the engineering gate authorizes confirmation.

## Three evaluated arms

### G1 — frozen generic baseline

Use the existing WP-G exact-reference rows for ZFP, SZ3 and SPERR. These are the authority for baseline:
- compressed bytes;
- realized CHGCAR Linf;
- actual Henkelman Bader error;
- zero basin reassignment under exact AECCAR.

### P — post-decode basin projection

1. Compress/decompress the original CHGCAR with the same codec and absolute tolerance as the corresponding G1 row.
2. Using exact-reference Bader labels, compute the original discrete sum in every partition region.
3. Shift each decoded region by a uniform offset so that its discrete sum exactly matches the original region sum.
4. Count the basin-sum side channel in serialized bytes.

This arm tests whether fixed-partition Bader error is actually the low-dimensional basin-sum component.

### R — basin-residual QOAC-B1

1. From the exact-reference label map, compute the original discrete sum in each partition region.
2. Subtract each region's mean from the CHGCAR, producing a residual with zero sum in every region.
3. Compress/decompress this residual with the same generic backend and absolute tolerance as the corresponding G1 row.
4. Project the decoded residual back to exact zero sum in every region.
5. Add the stored exact region means.
6. Apply a final floating-point basin-sum projection to remove roundoff.
7. Count the side channel in serialized bytes.

The side channel contains one float64 target sum for every integer partition label from 0 through the maximum partition label, plus an explicit fixed wrapper header. Labels beyond the atom count, if emitted by the exact-reference Henkelman partition, are preserved rather than discarded. The exact AECCAR is part of the declared measurement contract and is not charged to QOAC-B1, exactly as it is not charged to the frozen G1 CHGCAR compression ratios.

## Why region label 0 is included

Henkelman may assign vacuum/unclaimed voxels label 0 and may emit additional partition-region labels beyond the atom count. QOAC-B1 preserves the discrete sum of every emitted non-negative region label. This keeps the total CHGCAR sum stable and avoids obtaining a Bader guarantee by silently moving charge into vacuum.

## Backend ladder

Reuse every successful WP-G G1 row for each engineering material:
- same backend: ZFP, SZ3 or SPERR;
- same nominal absolute CHGCAR tolerance;
- no additional codec tolerance is introduced.

This makes the transform/projection the only new variable.

## Rate accounting

Raw bytes:

    8 * npoints

for float64 CHGCAR data.

QOAC-B1 bytes:

    backend compressed bytes
    + actual basin-sum side-channel bytes
    + fixed wrapper header bytes.

No entropy estimate substitutes for actual backend payload bytes.

## Fixed-partition closure

For every P and R reconstruction, record

    max_i |S_i(reconstruction) - S_i(reference)|,

where S_i is the discrete sum over partition region i.

Expected closure is floating-point roundoff. Closure is a construction invariant, not the scientific certificate.

## Actual Bader certification

The transform is never accepted solely from the algebraic closure.

For each engineering material and each tau_B in {1e-4, 1e-3, 1e-2}:

1. Find the best certified frozen G1 baseline row.
2. Let epsilon_star be that row's realized CHGCAR Linf.
3. For P and R independently, choose the highest-total-CR row satisfying

       final_Linf <= 1.05 * epsilon_star.

4. Reconstruct that candidate again.
5. Run Henkelman Bader with exact AECCAR.
6. Record actual max atomic-charge error and basin reassignment fraction.

Thus the primary competitive comparison does not buy rate by accepting worse worst-case CHGCAR distortion than the frozen baseline.

## Engineering gates

At the primary tau_B = 1e-3 e:

### Gate A — nullspace mechanism

- 12/12 R candidates have zero basin reassignment;
- 12/12 actual Henkelman Bader errors are <= 2e-6 e;
- all selected reconstructions have basin-sum closure <= 1e-9 times max(1, max absolute reference region sum).

### Gate B — matched-field competitive utility

Define

    R_CR = CR_R / CR_best_G1

using the matched-Linf rule above.

GO requires:
- at least 9/12 materials have R_CR > 1;
- median R_CR > 1.05.

### Gate C — transform value beyond repair-only

At the same matched-Linf contract, compare residual arm R with projection-only arm P.

GO requires:

    median(CR_R / CR_P) > 1.02.

This gate distinguishes a useful basin-adapted representation from a post-hoc charge repair alone.

Confirmation on the frozen 38-material holdout is authorized only if Gates A and B pass. Gate C determines whether the residual transform itself is retained as the primary QOAC-B representation or whether the next engineering iteration should redesign the nullspace coder.

## Secondary reporting

For every row retain:
- final CHGCAR Linf and RMSE;
- mean-density deviation;
- backend payload bytes;
- side-channel bytes;
- total bytes and CR;
- maximum discrete basin-sum closure error;
- number of atomic basins, number of label-0 voxels, and fraction of field energy in the residual;
- encode/decode wall time.

## Interpretation boundary

A successful fixed-partition result does not prove that compressed AECCAR preserves Bader topology.

It establishes a narrower statement:

> Once the partition-defining reference is stable and held exact, Bader charge exposes a low-dimensional basin-integral-sensitive subspace and a high-dimensional within-basin nullspace that can be exploited for compression.

Compression of the partition-defining field is a separate QOAC-B2 problem.
