# Nonlinear QoI (PBE exchange-correlation energy) — results

Run on Vanda 2026-10-24 (probe 1483574 PASS after DEVIATIONS D2; production 1483604), collected and SHA-checked by
`qoi_srv_monitor.py` (collect SHA b2e674ea856a). 92/92 materials SUCCESS (P1 60 bulk crystals, P3b 32 slabs), 0 failed.
Aggregates: `results/SUMMARY.json`; rows: `results/transfer_rows.csv`, `results/xc_contract_rows.csv`. Reviewed in the
main session; the paired ratios below were recomputed from the 552 contract rows and match the summary.

## Part 2 — certification under the XC contract (|dE_xc^PBE| < tau_x per atom)

Every material was eligible and every writer certified at both tolerances. Median certified compression ratio:

| cohort | tau_x (meV/atom) | P (best pointwise) | L (Hartree law) | U (uniform reciprocal steps) |
|---|---|---|---|---|
| P1 bulk (60) | 1 | 79.7 | 484.5 | 413.5 |
| P1 bulk (60) | 0.1 | 30.0 | 220.6 | 212.6 |
| P3b slabs (32) | 1 | 61.9 | 271.9 | 265.0 |
| P3b slabs (32) | 0.1 | 30.7 | 80.7 | 75.6 |

Paired medians (95% bootstrap CI; wins):

| cohort | tau_x | L/P | U/P | L/U |
|---|---|---|---|---|
| P1 | 1 | 5.43 (4.18–7.48; 60/60) | 5.03 (4.13–7.18; 60/60) | 1.03 (0.99–1.09; 35/60) |
| P1 | 0.1 | 6.89 (5.31–8.65; 59/60) | 5.72 (4.31–8.30; 59/60) | 1.09 (1.05–1.17; 40/60) |
| P3b | 1 | 2.92 (2.18–4.67; 32/32) | 3.01 (2.07–4.64; 32/32) | 1.04 (1.00–1.07; 22/32) |
| P3b | 0.1 | 1.91 (1.24–3.93; 25/32) | 1.84 (1.37–4.02; 27/32) | 1.01 (0.94–1.06; 16/32) |

Reciprocal-space coding certifies 5–7-fold more than pointwise codecs on bulk crystals and 2–3-fold more on slabs; the
Hartree weight |G|^2 adds only 1–9% over uniform reciprocal steps for this local functional.

## Part 1 — XC error of the law protocol's Hartree-certified streams

Median |dE_xc^PBE| (meV/atom) of the regenerated streams; count below 1 meV/atom in brackets.

| cohort | tau_H | A1 law | A2 truncation | A3 operational | A6 pointwise |
|---|---|---|---|---|---|
| P1 | 1e-8 | 0.0004 (60/60) | 0.0002 (60/60) | 0.0004 (60/60) | 0.0001 (60/60) |
| P1 | 1e-6 | 0.069 (59/60) | 0.039 (60/60) | 0.052 (59/60) | 0.011 (60/60) |
| P1 | 1e-4 | 8.9 (9/60) | 4.0 (13/60) | 9.5 (9/60) | 2.2 (17/60) |
| P3b | 1e-8 | 0.098 (32/32) | 0.006 (32/32) | 0.041 (32/32) | 0.0002 (32/32) |
| P3b | 1e-6 | 3.9 (3/32) | 0.28 (23/32) | 3.2 (5/32) | 0.061 (32/32) |
| P3b | 1e-4 | 355 (0/32) | 85 (0/32) | 311 (0/32) | 45 (4/32) |

A Hartree certificate does not certify the XC energy: on slabs at tau_H = 1e-6 the law's streams leave a median
3.9 meV/atom. The XC energy needs its own contract (Part 2), as the measurement-contract framing predicts.

Regeneration on Vanda: 1,073 of 1,104 regenerated streams re-passed their Hartree certificate. The other 31 are A2 at
tau_H = 1e-8 (17 bulk, 13 slabs; Hartree error 1.007–1.085 x tau) and one A6 SZ3 slab at 1e-4 (1.92 x tau, bytes
104,215 vs 110,381 recorded). Byte counts of A1–A3 are within 0.16% of the record (A3 identical), A6 within 5.6%: the
law protocol ran on another platform (numpy FFT and SZ3 builds). Part 1 is descriptive (PROTOCOL §6); the XC errors
are reported for the regenerated streams as they are.
