# Whole-object archive under the W1 writer — results

Objects checkpointed 300, SUCCESS 300 of 300. Fold reduction R of the 8.50 TB Materials Project archive (Hartree-certified complete objects), stratified expansion estimate with 95% bootstrap interval (seed 20261012, 2000 resamples, paired across writers).

Run on Vanda 2026-10-25 (probe 1491770 PASS, production 1491800 and 1491801), collected by `qoi_algo_monitor.py`
(tarball SHA-256 be574d60b72a…); R_W and R_Q recomputed independently from `objects.csv` by
`analysis/waterfill_writer_20261025/review_recompute.py` (maximum relative difference 2e-16). 300/300 objects SUCCESS;
every object certified under W and Q at both tolerances, magnetization on the decoded frame in 300/300.

## Reading

At 1e-6 the W writer stores the archive in about 15.3 GB, 555-fold (95% CI 492–635), 1.60-fold smaller than
revision 10's operational allocation (paired 1.51–1.70, entirely above the revision-10 interval 317–387) and 16.1-fold
smaller than the pointwise writer. At 1e-4 it stores 1,818-fold (1,549–2,119), 1.33-fold smaller than revision 10's
operational allocation. The gain at 1e-4 is smaller because the magnetization stream, written by the same pointwise
moment policy for every writer, holds 63.5% of the archive-weighted stored bytes under W at that tolerance (19.4% at 1e-6). Operational allocation in
the same writer (Q) stores the same archive (Q/W 1.006 at 1e-6, 0.997 at 1e-4). 248/300 objects used a symmetry group
(median order 4).

| writer | tau_H = 1e-6 | tau_H = 1e-4 |
|---|---|---|
| P pointwise (recorded) | 34.6 (32.4–37.2) | — |
| T truncation A2 (revision 10) | 232.5 (211.4–259.9) | 1,142.3 (1,017.8–1,286.0) |
| L closed-form law A1 (revision 10) | 316.4 (290.4–349.9) | 1,036.3 (926.9–1,152.2) |
| O operational allocation A3 (revision 10) | 347.2 (317.1–386.6) | 1,371.1 (1,208.9–1,549.8) |
| W water-filling law, W1 writer, symmetry | 555.2 (491.9–635.0) | 1,818.0 (1,548.6–2,119.0) |
| Q operational allocation, W1 writer, symmetry | 558.4 (494.6–638.5) | 1,813.0 (1,544.5–2,112.9) |

| paired ratio | 1e-6 | 1e-4 |
|---|---|---|
| W/O | 1.599 (1.507–1.704) | 1.326 (1.273–1.385) |
| W/L | 1.755 (1.651–1.870) | 1.754 (1.645–1.881) |
| W/T | 2.388 (2.253–2.543) | 1.591 (1.507–1.687) |
| W/P | 16.060 (14.265–18.187) | — |
| Q/O | 1.608 (1.515–1.713) | 1.322 (1.271–1.381) |
| Q/W | 1.006 (1.004–1.008) | 0.997 (0.996–0.999) |

Counts:

- W 1e-06: eligible 300, certified 300, decoded-frame m 300
- W 0.0001: eligible 300, certified 300, decoded-frame m 300
- Q 1e-06: eligible 300, certified 300, decoded-frame m 300
- Q 0.0001: eligible 300, certified 300, decoded-frame m 300

Objects with a symmetry group used: 248/300; median group order 4.0.
