# WS-S3 v1 — do charge and moment contracts compose without a stored partition?

- **Run.** CI run 39635540126, on the 16 S1 engineering materials. 0 failure records.
- **Arms.** rho is stored by the resolved valence Bader contract: best of ZFP/SZ3/SPERR with the largest
  certified bound, partition re-derived from rho'. m is stored by the S1 moment contract, with the
  certificate evaluated on the *reference* partition.
- **Measurement.** Moments are read on the *decoded* partition with the compiled binary,
  `bader CHGCAR(m') -ref REFCAR(rho')`.

## Counts (material × tau_mu pairs)

| tau_B (e) | magnetic | non-magnetic |
|---|---|---|
| 1e-3 | 22/22 joint-certified (FeCo9 has no certified rho at 1e-3) | 8/8 |
| 1e-2 | 19/24 | 8/8 |

The 5 failing pairs come from 5 magnetic materials at tau_B = 1e-2 (BaRhF6, Li5Co3O8, GdInCu2, Sr2MgTiO4,
BaNdMgCo2O5).

Erratum: the commit message of the v2 change misstates the v1 counts ("26/27 at 1e-3"). The counts above
are the correct ones.

## What moves the moments

- **Migration alone is small.** With m exact and rho stored, moment errors come only from partition
  migration. They are at most 1.86e-3 mu_B, even though the gross charge carried by reassigned voxels reaches
  a median 0.11 e at tau_B = 1e-2 (0.0093 e at 1e-3). Migration happens at basin boundaries, where |m| is
  small.
- **The failures are budget overruns.** m' is certified on the reference partition and uses its full
  tau_mu, so the joint error can exceed tau_mu by the migration term.

## Reading

- **Without a stored map.** At tau_B = 1e-3 e the two contracts compose in every case. At 1e-2 e the
  migration term must be accounted for.
- **Fix tested in v2.** The encoder knows rho', so it certifies m' against the moments on the decoded
  partition directly. This "decoded-frame certification" composes by construction. v2 measures its byte cost
  against reference-frame certification.
