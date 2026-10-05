# QOAC-H v0.1 engineering execution log

## 2026-10-05 — invalidated pilot run 2

GitHub Actions run: `37266231086`.

The run passed preflight and began the frozen 12-material pilot. A read-only audit of completed shard artifacts found an impossible invariant: every reconstruction within a material had the same density error and Hartree relative RMSE exactly 1.0 for all alpha values and for both beta=0 and beta=2.

This was traced to an implementation defect in `decode_blob`: `f.real.ravel()` and `f.imag.ravel()` can allocate copies because real/imag views of a complex array are strided. Shell assignments therefore modified temporary arrays rather than the complex spectrum `f`. Active reciprocal modes remained zero after decoding.

Disposition:
- run 2 is invalid engineering output and must not be used as scientific evidence;
- no GO/NO-GO gate was evaluated from it;
- no pilot population, alpha ladder, beta values, scientific threshold, matching rule, or GO criterion was changed;
- the decoder was repaired by assigning directly through the contiguous complex flat view;
- regression tests were added to verify decoded active coefficients exactly equal the intended quantized coefficients and that different alpha values yield different reconstructions.

This log preserves the distinction between implementation debugging and prospective scientific evaluation.
