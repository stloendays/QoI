# Hartree-QSQ reconstruction parity audit

Rows: **6343**; scientific gate failures: **1**; compressed-byte exact rows: **6270/6343 (98.8%)**.

## By codec

| Codec | rows | L∞ match | gate pass | compressed bytes exact |
|---|---:|---:|---:|---:|
| ('SPERR',) | 1956 | 100.00% | 100.00% | 100.00% |
| ('SZ3',) | 1937 | 99.95% | 99.95% | 96.23% |
| ('ZFP',) | 2450 | 100.00% | 100.00% | 100.00% |

## Matched-pair parity

| Pair | pairs | both exact | exact fraction | materials with >=1 exact pair |
|---|---:|---:|---:|---:|
| ZFP/SZ3 | 457 | 448 | 98.03% | 213 |
| ZFP/SPERR | 465 | 465 | 100.00% | 206 |
| SZ3/SPERR | 1847 | 1778 | 96.26% | 254 |

Direct same-reconstruction Hartree/Bader pairwise interpretation is restricted to matched pairs for which both regenerated codec outputs are byte-count exact diagnostics; if exactness is insufficient, the follow-up mechanism audit must recompute Bader on the regenerated fields.
