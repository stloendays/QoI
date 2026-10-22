# WS-A0 reading — what the public Materials Project parsed bucket holds

- **Listing.** Anonymous S3 listing on 2026-10-21 17:32 UTC (keys and sizes only), run 39643967650.
- **Totals.** 17 top-level prefixes, 26.10 TB in all.

| prefix | objects | TB | relation to this paper |
|---|---|---|---|
| chgcars/ | 415,480 | 8.50 | the frame of both archive estimates (rho + magnetization block) |
| locpots/ | 158,019 | 2.73 | local potential on the same grids, the Hartree contract's target field (see below) |
| mp-volumetric-chgcars/ | 88,237 | 2.24 | a second charge-density collection (not examined) |
| aeccar0s/ + aeccar1s/ + aeccar2s/ | 416,500 | 3.49 | all-electron reference fields: the partition contract (QOAC-B3; label map median 12.9 kB) |
| elfcars/ | 107,481 | 0.11 | electron localization function (not examined) |
| defects/, bandstructures/, core/, root, others | — | 9.03 | not volumetric densities, or not examined |

## Reading

- **Share of the volumetric holdings.** The 8.50 TB charge-density frame is about half of the bucket's
  volumetric holdings. Counting chgcars, mp-volumetric-chgcars, locpots, the three AECCAR prefixes and
  elfcars, those holdings total 17.07 TB. The `defects/` and root prefixes may hold more and were not
  opened.
- **Two adjacent products tie into the paper's contracts.**
  - **AECCARs (3.49 TB).** They exist mainly to define the Bader partition. QOAC-B3 showed that the partition
    is reproduced exactly by a lossless label map about 17× smaller than a partition-faithful AECCAR.
  - **LOCPOTs (2.73 TB).** They store the local potential. Its Hartree part is exactly what the
    Hartree-certified density reproduces; the ionic and exchange-correlation parts are not.
- **Not claimed.** Nothing here supports dropping either product. Both are possible extensions only: an
  AECCAR contract (partition plus whatever else users read from it) and a LOCPOT contract.
