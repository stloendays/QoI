# Whole-object archive under spectral truncation and the operational optimum — results

Run on Vanda 2026-10-24 (production 1483600 and 1483602 after probe 1483574 PASS), collected and SHA-checked by
`qoi_srv_monitor.py` (collect SHA b2e674ea856a). 300/300 archive objects SUCCESS; every object certified under T (A2
spectral truncation) and O (A3 operational optimum) at both tolerances, magnetization on the decoded frame in 300/300.
Aggregates: `results/SUMMARY.json`; rows: `results/objects.csv`. Reviewed in the main session.

## Archive reduction of the 8.50 TB Materials Project archive (Hartree-certified complete objects)

Fold reduction R (95% bootstrap CI; seed 20261012, 2,000 resamples). L (closed-form law) and P (pointwise codecs) are the
whole-object study's earlier estimates, carried in the same summary.

| writer | tau_H = 1e-6 | tau_H = 1e-4 |
|---|---|---|
| P pointwise | 34.6 (32.4–37.2) | — |
| T spectral truncation (A2) | 232.5 (211.4–259.9) | 1,142 (1,018–1,286) |
| L closed-form law (A1) | 316.4 (290.4–349.9) | 1,036 (927–1,152) |
| O operational optimum (A3) | 347.2 (317.1–386.6) | 1,371 (1,209–1,550) |

Paired ratios: at 1e-6, O/T 1.49 (1.46–1.53), L/T 1.36 (1.33–1.39), O/L 1.10 (1.09–1.10), O/P 10.0, T/P 6.7, L/P 9.2.
At 1e-4, O/T 1.20 (1.18–1.23), O/L 1.32 (1.27–1.39), and L/T 0.91 (0.86–0.94): at the loose tolerance spectral truncation
stores the archive smaller than the closed-form law, and the operational optimum stores it smaller than both.
