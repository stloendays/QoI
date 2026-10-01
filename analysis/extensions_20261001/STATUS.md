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

**Status: COMPLETE / pre-declared dominance criterion met.**

The G3 arm completed on Vanda using PBS jobs `1419834` (pilot), `1419835` (production), and `1419836` (finalize). Finalized denominator: 53 planned, 50 analyzable successes, 3 pre-documented AECCAR input failures.

Primary result at `tau = 1e-3 e`:
- G1 eligible: 50/50;
- G2 eligible: 3/50;
- G3 eligible: 3/50;
- G3 non-evaluable: 47/50 (94.0%);
- median `f_G3/f_G2 = 1.000`;
- median basin-reassignment ratio G3/G2 = 1.000;
- all 50 analyzable materials satisfy `f_G3 >= 0.9 f_G2`.

All three pre-declared dominance criteria are met. The result supports the interpretation that perturbation of the partition-defining all-electron reference is the dominant source of the observed G2 instability under the frozen protocol.

Execution details:
- exact CHGCAR;
- perturbed AECCAR0+AECCAR2 reference only;
- same WP-G perturbation amplitude and seed mapping;
- Henkelman Bader 1.05 on-grid;
- one reference + five probes per analyzable material;
- no codec ladder rerun;
- three-material pilot with deterministic validation before full production;
- checkpoint status utility and full 53-material PBS job.

The acceptance rule and mechanism claim were committed before any G3 outcome was observed. The 53 checkpoints have now been finalized and aggregated; reader-facing integration still requires explicit manuscript adjudication.

## Manuscript status

No current manuscript claim, figure, threshold, or frozen QSQ endpoint has been changed by this branch.


## Contract-aware QSQ interface

**Status: SPECIFICATION FROZEN FOR THIS EXTENSION.**

`CONTRACT_AWARE_QSQ_SPEC.md` now defines a reusable measurement-contract interface:
- every input field is declared exact, approximate, derived, or excluded;
- QSQ perturbs only approximate inputs;
- binary qualification uses the same finite-panel max-response rule;
- exact sequential early rejection is permitted for fixed-threshold eligibility;
- full five-seed execution remains required when the numerical floor itself is an endpoint;
- certificates record the contract hash and input-handling semantics, not only the selected codec.

This specification is development-layer infrastructure and does not alter the current manuscript until WP-I and manuscript integration are explicitly adjudicated.
