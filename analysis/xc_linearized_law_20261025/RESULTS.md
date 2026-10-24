# The XC energy's own allocation law — results

Run on Vanda 2026-10-24 (probe 1485319 PASS; production 1485336), collected and SHA-checked by `qoi_xcl_monitor.py`
(collect SHA b9bd7b546567). 92/92 materials SUCCESS (P1 60 bulk crystals, P3b 32 slabs), 0 failed; every material eligible
and every writer certified at both tolerances. Aggregates: `results/SUMMARY.json`; rows: `results/xcl_rows.csv`; shell
weight profiles: `results/shell_weights.csv`. Reviewed in the main session.

## Certified compression ratio under the XC contract (median, 95% bootstrap CI)

| cohort | tau_x (meV/atom) | X (v_xc shell law) | F (flat steps) |
|---|---|---|---|
| P1 bulk (60) | 1 | 484.7 (355–643) | 439.1 (338–577) |
| P1 bulk (60) | 0.1 | 210.6 (139–301) | 199.5 (127–279) |
| P3b slabs (32) | 1 | 255.4 (178–443) | 256.8 (175–433) |
| P3b slabs (32) | 0.1 | 67.6 (41–130) | 74.2 (42–157) |

## Paired ratios (median, 95% CI, wins)

| cohort | tau_x | X/F (primary) | X/L | X/U | X/P | F/U |
|---|---|---|---|---|---|---|
| P1 | 1 | 1.02 (0.98–1.08; 34/60) | 1.00 (0.99–1.02; 30/60) | 1.05 (0.98–1.09; 35/60) | 5.39 (4.17–7.65; 60/60) | 1.01 (0.96–1.05) |
| P1 | 0.1 | 1.16 (1.06–1.22; 41/60) | 0.99 (0.97–1.01; 26/60) | 1.08 (1.03–1.14; 41/60) | 7.00 (5.43–9.18; 59/60) | 0.95 (0.87–1.04) |
| P3b | 1 | 1.01 (0.99–1.05; 18/32) | 0.96 (0.94–1.00; 12/32) | 1.01 (0.97–1.06; 18/32) | 2.69 (2.13–4.51; 32/32) | 0.99 (0.96–1.01) |
| P3b | 0.1 | 0.99 (0.95–1.01; 13/32) | 0.93 (0.89–1.00; 10/32) | 0.94 (0.91–0.97; 6/32) | 1.86 (1.27–3.72; 26/32) | 0.96 (0.94–0.99) |

L, U and P are the writers of `nonlinear_xc_20261024` (same platform, contract, QSQ and search).

## What the weights show

The XC potential's spectral weight falls as steeply over the first shells as the Hartree weight: median W_s/W_max is
3e-2 at shell 1, 5e-4 at shell 2 and 1e-6 by shell 9 in both cohorts, and the implied step ratio between the last and
first shell is 5,387 (bulk) and 1,490 (slabs), against 3,969 for the Hartree law's |G|^2 steps. The XC energy's own
first-order allocation is therefore close to the Hartree law, and certifies the same (X/L 0.99–1.00 on bulk crystals,
0.93–0.96 on slabs). Its gain over flat steps is 16% on bulk crystals at 0.1 meV/atom and within 2% elsewhere: the
5–7-fold (bulk) and 2–3-fold (slab) advantage over pointwise codecs comes from reciprocal-space coding, with the
operator weight adding at most 16%.

Side effect: the XC-certified X streams carry a Hartree error well below the F streams' (median 1.4e-6 vs 8.2e-6 on bulk
crystals and 1.6e-8 vs 2.5e-7 on slabs at 0.1 meV/atom), consistent with X and the Hartree law sharing one allocation.
