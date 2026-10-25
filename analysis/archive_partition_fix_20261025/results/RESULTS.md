# Study 5 — partition fix: results

Revision 10's T/O and revision 11's W/Q rerun with every decoded Bader partition rebuilt (study 4's `whole_archive.py`, same estimator).

| writer | committed | fixed | change |
|---|---|---|---|
| T_1e-06 | 232.5 | 232.5 | +0.00% |
| O_1e-06 | 347.2 | 347.3 | +0.04% |
| W_1e-06 | 555.2 | 555.2 | +0.00% |
| Q_1e-06 | 558.4 | 557.9 | -0.07% |
| T_0.0001 | 1,142.3 | 1,115.4 | -2.36% |
| O_0.0001 | 1,371.1 | 1,324.9 | -3.37% |
| W_0.0001 | 1,818.0 | 1,735.4 | -4.54% |
| Q_0.0001 | 1,813.0 | 1,725.8 | -4.81% |

At 1e-6 the first writer of each study (T, W) used its own partition, and the second writer's decoded densities are
close enough to it that O and Q change by < 0.1%. At 1e-4 every writer's estimate falls by 2.4–4.8%: with their own
1e-4 partitions, 4 (T), 8 (O), 8 (W) and 6 (Q) objects no longer certify the moments from the decoded density and are
stored with the reference atom map (larger), and the magnetization streams of 45 (T), 56 (O), 50 (W) and 55 (Q) other
objects change (29, 30, 27, 32 of them larger). At 1e-6, 5 O and 5 Q magnetization streams change. Density streams,
Hartree certificates, L and P are unchanged. The corrected estimates (with 95% CI, study 4 SUMMARY.json):
T 232 (211–260) / 1,115 (992–1,255); O 347 (317–387) / 1,325 (1,158–1,511); W 555 (492–635) / 1,735 (1,470–2,048);
Q 558 (494–638) / 1,726 (1,457–2,041) at 1e-6 / 1e-4. Paired W/O: 1.60 (1.51–1.70) and 1.31 (1.26–1.37).
