# Three-way common-support Hartree spectral audit

Status: **COMMON_SUPPORT_OPERATOR_ORDER_SUPPORTED**

- Common-support triples: **428**
- Materials: **203**
- Maximum triple span: **0.09999 dex**
- Maximum safe Parseval relative error: **1.296e-15**

## Common-population pair decomposition

| pair | safe Hartree ratio | sqrt(total E ratio) | sqrt(spectral susceptibility ratio) |
|---|---:|---:|---:|
| ZFP/SZ3 | 0.0778141 | 0.377508 | 0.202822 |
| ZFP/SPERR | 0.676829 | 0.439756 | 1.44669 |
| SZ3/SPERR | 9.79988 | 1.21417 | 7.49354 |

## Material-level ordering

- SPERR < ZFP < SZ3 Hartree susceptibility: **75.9%** of 203 materials
- SPERR > ZFP > SZ3 spectral centroid: **75.4%** of 203 materials
- SPERR < ZFP < SZ3 low-G fraction: **76.4%** of 203 materials

The susceptibility ordering is the primary common-support mechanism test. Centroid and low-G fraction are supporting descriptors.

No frozen manuscript or prior mechanism branch was modified.
