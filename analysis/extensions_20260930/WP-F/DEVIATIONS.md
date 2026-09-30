# WP-F deviations and execution notes

Recorded before the affected step runs. No pre-declared analysis, estimator, storage rule or
acceptance criterion is changed.

1. **Execution platform.** Windows 11 with the pinned scientific stack in
   `D:\Research\QoI-final4-local\venv`, as WP-B ran (WP-B `DEVIATIONS.md` 1); the protocol names this
   stack. Certificates therefore certify this fixed pipeline.

2. **Ladder only where a certificate is possible (2026-09-30, before the first sampled density was
   read).** The protocol's D01–D09 text says the full union ladder is evaluated for every object. The
   runner evaluates it only for objects that are QSQ-eligible at the loosest τ (f_m < 1e-2 e). For an
   object not eligible at 1e-2 e it is not eligible at any τ, the storage rule assigns lossless bytes at
   every τ, and none of the pre-declared endpoints (R(τ), non-evaluable fractions, codec mix, the
   prospective writer check, which is defined over eligible objects) uses its ladder. Skipping it
   changes no reported number and saves about one sixth of the Bader solves.

3. **Processing order.** Within each group objects are processed smallest first, so that memory-heavy
   objects come last; the order cannot change any per-object result.

4. **Workers and memory (2026-09-30, before launch).** The protocol's cost note assumed 4 workers for
   D01–D09 alongside 1 for D10. Only about 5 GB of RAM was free at launch, so the groups run one after
   the other: D01–D09 with 3 workers, then D10a–D10c with 1 worker. An object whose worker process dies
   (the pool reports it; typically memory) is re-run once on its own after its group finishes; the
   second outcome is final and is what the protocol's "attempted once, then counted as failed" refers
   to, so that a failure reflects the object and not the scheduling.
