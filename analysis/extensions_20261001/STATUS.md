# QSQ optimization status — 2026-10-01

## WP-H — exact sequential early-rejection QSQ

**Status: COMPLETE / acceptance met.**

At the primary `tau = 1e-3 e`:
- 254/254 eligibility decisions exactly match the frozen five-seed QSQ.
- Mean probe solves: 5.000 -> 3.335 (-33.3%).
- Mean total QSQ Bader solves including the reference: 6.000 -> 4.335 (-27.8%).
- 99/111 rejected materials are rejected on seed 1; 106/111 by seed 2.
- Integrated into the frozen WP-E BISECT writer cost model, mean end-to-end solves over all development materials fall 12.004 -> 10.339 (-13.9%) with unchanged archive compression and zero misses.
- A regression-checked writer integration layer is now committed under `WP-H/run_writer_with_sequential_qsq.py`; it inherits all WP-E scientific decisions and is allowed to change only solve counts.

This optimization may replace the implementation of binary eligibility at a declared tolerance because it is mathematically classification-equivalent. It does **not** replace full five-seed execution when the numerical stability floor itself is required.

## WP-I — partition-reference-only sensitivity decomposition

**Status: PREDECLARED / implementation ready / no scientific result yet.**

The G3 arm is implemented and packaged for pilot -> production -> aggregation:
- exact CHGCAR;
- perturbed AECCAR0+AECCAR2 reference only;
- same WP-G perturbation amplitude and seed mapping;
- Henkelman Bader 1.05 on-grid;
- one reference + five probes per analyzable material;
- no codec ladder rerun;
- three-material pilot with deterministic validation before full production;
- checkpoint status utility and full 53-material PBS job.

The acceptance rule and mechanism claim were committed before any G3 outcome was observed. Reader-facing conclusions must wait for the 53 checkpoint records and aggregation.

## Manuscript status

No current manuscript claim, figure, threshold, or frozen QSQ endpoint has been changed by this branch.
