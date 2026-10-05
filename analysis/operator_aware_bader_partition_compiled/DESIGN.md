# QOAC-B3 — compiled exact Bader partition state

Freeze date: 2026-10-05

Status: engineering study after successful QOAC-B2 confirmation.

## Motivation

WP-I established that perturbing the partition-defining all-electron reference alone reproduces the joint-reference instability: at tau_B=1e-3 e, only 3/50 materials remain eligible when AECCAR is perturbed, while exact AECCAR makes 50/50 eligible.

QOAC-B2 established that once the partition is fixed, CHGCAR can be compressed aggressively and corrected by a minimum-Linf/minimum-L2 basin projection while preserving actual Henkelman Bader charges.

B3 therefore asks a different question:

> For a Bader-specific archive, must the exact AECCAR field itself be retained, or is the exact discrete Henkelman partition map the sufficient state needed by the downstream measurement?

B3 does **not** claim to reconstruct AECCAR. It compiles the nonlinear partition operation into a losslessly stored discrete partition state.

## Scientific object

Using exact AECCAR0 + AECCAR2 and Henkelman Bader 1.05 with

    -b ongrid -vac 0.001 -p atom_index

produce the exact integer partition map L(r).

B3 stores L(r) losslessly.

A decoded map is accepted only if

    L_decoded(r) == L_exact(r)

for every voxel.

## Direct integration equivalence

For VASP CHGCAR density values rho(r) and cell volume V on an N-point uniform grid, the on-grid charge assigned to atomic region i is evaluated as

    Q_i^map = (V / N) * sum_{r : L(r)=i} rho(r).

For the engineering study this direct integration is compared against the Henkelman ACF atomic charge from the same exact-reference run.

Primary equivalence gate:

    max_i |Q_i^map - Q_i^Henkelman| <= 2e-6 e.

If this identity does not hold under the repository decoder conventions, B3 stops; no storage claim is made.

## Lossless partition encodings

Two fixed encodings are evaluated:

### Packed-label + zlib

- choose the smallest unsigned integer type that can hold max(L):
  uint8, uint16 or uint32;
- flatten in Fortran grid order;
- zlib level 6;
- count a compact binary header in total bytes.

### Run-length + zlib

- same smallest label type;
- Fortran-order run-length encoding as (label, uint32 run_length);
- zlib level 6;
- count the same class of compact binary header.

The smaller complete serialized stream is the B3 partition representation.

The decoder must reproduce the exact map bit-for-bit.

## Exact-reference storage comparator

For a Bader-specific exact-reference archive, the minimum continuous reference field is the combined

    AE = AECCAR0 + AECCAR2

rather than the two components separately.

The comparator stores AE exactly as float64 and applies zlib level 6. A fixed 32-byte field header is included.

This is intentionally more favorable than comparing against raw uncompressed AECCAR.

Define

    R_partition = bytes(lossless AE) / bytes(lossless partition map).

## End-to-end Bader archive comparison

At tau_B=1e-3 e:

Baseline exact-reference archive:

    best frozen G1 CHGCAR payload
    + losslessly compressed exact combined AE field.

Compiled Bader archive:

    QOAC-B2 kappa=4 projected CHGCAR stream
    + exact partition-map stream.

The QOAC-B2 stream already includes its basin-sum side channel.

Define

    R_archive = bytes(baseline archive) / bytes(compiled archive).

Common crystal-structure metadata are excluded from both sides.

## Engineering population

Use the same 12 development materials used for QOAC-B1/B2 engineering.

No new codec or tolerance tuning occurs in B3.

## Engineering gates

### Gate A — semantic equivalence

- 12/12 partition streams decode exactly;
- 12/12 direct map-integrated atomic charges agree with Henkelman within 2e-6 e.

### Gate B — partition representation efficiency

- partition map is smaller than losslessly compressed exact AE for 12/12 materials;
- median R_partition > 2.

### Gate C — complete archive utility

- compiled archive is smaller than the exact-reference baseline archive in at least 10/12 materials;
- median R_archive > 1.25.

If Gates A and B pass, the same frozen encoding is eligible for a descriptive 50-material census. Because all 50 materials have already participated in WP-G/WP-I and QOAC-B2 evidence, that census is not described as an untouched confirmation.

## Scope boundary

B3 preserves the **discrete on-grid Bader partition state**, not the continuous AECCAR field.

It is appropriate when the declared downstream contract is Bader partition/integration under the frozen Henkelman semantics.

It does not preserve arbitrary future analyses that require the original AECCAR values.
