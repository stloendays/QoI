# WP-C — deviations and fixed interpretations

Recorded before the corresponding statistic was computed. None changes an analysis rule of
`PROTOCOL.md`; items 1–2 are environment substitutions, items 3–6 pin details the protocol leaves
to the implementation.

1. **Operating system.** The protocol's stack is Ubuntu; this run used Windows 11 (see
   `provenance.json: platform`). Python is 3.12.14 (uv-managed CPython), and every package in
   `validation/requirements-external-e2e.txt` from commit 893f931 is installed at the exact pinned
   version (`provenance.json: pip_freeze`). The codec wrappers, loader and Bader settings are imported
   from the frozen scripts unchanged; the construction was checked on `mp-1007755` before the run
   (frozen `realized_Linf` reproduced to <= 8.4e-13 dex on all three codecs, probe L_inf equal to
   eps_m to <= 1.2e-16 relative).
2. **Process model.** Materials were executed in a 6-process pool (4 numba threads each) with
   per-material JSON checkpoints outside the repository (`_wpc/work/checkpoints/`); the density blob
   cache is `_wpc/cache/` (outside the repository, SHA-256 verified on every read). Largest grids were
   scheduled first. This affects wall time only.
3. **Stream string codec label.** `stream = SHA-256("QSQ-codecshape|material_id|codec|k")[:8]`
   little-endian, with `codec` spelled exactly as the protocol lists it: `ZFP`, `SZ3`, `SPERR`. The
   realized stream seed and shift vector are stored per row in `probe_outcomes.csv`.
4. **Shift vector draw.** `v_k = [rng.integers(0, n_i) for i in (0, 1, 2)]`, three sequential draws
   from `Generator(PCG64(stream))`, uniform over each grid axis; applied with `numpy.roll` on axes
   (0, 1, 2).
5. **Undefined codec-shaped floor.** f^c_m is the max over k >= 1 of successful solves; if any
   k >= 1 solve for a material x codec failed, f^c_m is left undefined (NaN) rather than computed on a
   partial set, and the material is counted in `n_undefined_ratio` / `n_undefined` of every table.
   Failed rows remain in `failures.csv` and in all denominators.
6. **Eligibility rule.** Eligible at tau means floor < tau (the frozen P2 aggregator's rule), applied
   identically to f_m and f^c_m.
7. **Base rung.** Every one of the 762 material x codec pairs has a 1e-5 relative base rung in
   `benchmark/master_benchmark_full.csv`, so the fallback to the smallest available rung was never
   used (`base_rung_is_1e-5` is True on every row of `probe_outcomes.csv`).
