# QOAC-H v0.2 sanity audit

Date: 2026-10-05

This audit was performed after the engineering pilot completed and before any disjoint confirmatory cohort was frozen.

## Accounting and execution

- 12/12 engineering materials completed.
- 312/312 planned rows completed.
- 0 failures.
- All serialized streams report exactly one exact reciprocal mode: G=0.
- Compression ratio uses raw float64 bytes (8 * npoints) divided by the complete serialized QOAC-H byte stream, including header, lattice, shape, alpha, shell metadata, DC payload, integer payload and zlib framing.
- The existing ZFP/SZ3/SPERR baseline uses the same 8 * npoints raw-byte denominator.

## Reality / Hermitian invariants

Across all certificate rows:
- maximum decoded imaginary leakage = 2.46724e-12;
- maximum mean-density deviation = 3.97904e-13;
- exact reciprocal modes = 1 for every row.

## Historical versus Nyquist-safe Hartree

Across all 300 certificate rows:

    safe_error / historical_error

has:
- median = 0.999949;
- minimum = 0.985186;
- maximum = 0.999999999999.

For the best certified v0.2 row of every one of the 12 materials:
- historical Hartree relative RMSE < 1e-6;
- Nyquist-safe Hartree relative RMSE < 1e-6.

Therefore the engineering gain is not produced by exploiting the historical Nyquist convention.

## Rate-distortion behavior

For every material:
- compression ratio is monotone nondecreasing over the frozen alpha ladder;
- historical Hartree error is monotone nondecreasing over the frozen alpha ladder.

This removes the non-monotone-search concern seen in nonlinear Bader certification and supports later accelerated alpha search if desired.

## Interpretation boundary

The large compression gains are Hartree-specific, not universal field-fidelity claims. Some best-certified rows have large real-space density Linf/RMSE while retaining the Hartree contract. That behavior is expected from the operator-aware objective and is precisely why post-reconstruction QoI certification remains mandatory.

Conclusion: the v0.2 representation passes the implementation and metric-consistency audit. A disjoint confirmatory experiment may now be frozen without further codec changes.
