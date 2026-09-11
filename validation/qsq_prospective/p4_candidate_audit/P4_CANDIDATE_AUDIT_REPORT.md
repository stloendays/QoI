# P4 outcome-blind chemistry candidate audit

Status: **CANDIDATE_UNIVERSE_FROZEN**

This audit was constructed from `materials_metadata.csv` and raw NOMAD structure files only. It does not read QSQ eligibility, codec outcomes, P2 fresh-probe outcomes, P3A outcomes, or Bader charges.

NOMAD development slab states audited: **68**; structure retrieval failures: **40**.
Chemistry/provenance/geometry-qualified directed addition pairs: **5**; excluded pair comparisons: **425**.

Frozen primary pairing rule: same NOMAD upload, same density-grid shape, same lattice within tolerance, 1-4 added H/C/O atoms, all state-A atoms mappable to state B within 0.35 A, and a persistent host atom within 3.0 A of an added atom. The target is the nearest persistent host atom chosen from geometry only.

| Upload | Description | Candidate pairs |
|---|---|---:|
| qM7AMKciQ7GRVR8rCNm0mw | RuO2 CO2RR, adsorbate and spectator variations | 2 |
| reTvTXQBTiSwmntKl7EmAQ | GaN electrochemical surfaces, with AECCARs | 3 |

## Interpretation boundary

These are candidate chemistry pairs, not yet P4 outcomes. Reference charge-transfer decisions, ambiguity margins, codec trials and qualification policies must be frozen/evaluated in subsequent stages. No pair may be added or removed later because of QSQ or codec performance; exclusions after this point must be provenance/reference failures and must remain visible in accounting.
