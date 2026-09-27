# Author-authorized scope addendum — Fourier-spectrum mechanism integration

Date: 2026-09-27

## Scope action

The previously frozen submission story is explicitly reopened by author request for one validated extension only: integration of the completed Fourier-spectrum mechanism audit of the matched-distortion Hartree control.

The predecessor manuscript, claim matrix, figure map and scope-freeze records are preserved unchanged on their original branches and in Git history. This branch re-freezes the reader-facing manuscript after integrating the new evidence.

## Canonical claim

A downstream scientific-compression tolerance can be interpreted only after the reference QoI is qualified for numerical stability, and even after scalar reconstruction magnitude is controlled, downstream fidelity can remain codec dependent because the downstream operator weights the spatial or frequency structure of reconstruction error non-uniformly.

## Supporting claims in dependency order

1. **Reference stability is a separate benchmark axis.** QSQ determines whether the requested downstream tolerance is numerically supportable under the declared perturbation model.
2. **Scalar pointwise distortion is not a complete codec-comparison condition.** Within-material realized-L-infinity matching removes a major magnitude confound but leaves residual downstream differences.
3. **The matched-distortion Hartree residual has an operator-resolved mechanism.** Across the exact 457 ZFP/SZ3 matched pairs from 214 materials, the historical Hartree ratio 0.0776221 is reproduced and remains 0.0776219 under a Nyquist-safe Hermitian Poisson operator.
4. **Frequency allocation is the dominant component of the Hartree codec effect.** The pairwise identity closes to numerical precision; the material-median absolute-log share attributed to spectral Hartree susceptibility is 62.0%, with lower ZFP susceptibility in 99.5% of materials.
5. **The mechanism is operator specific, not a universal Fourier explanation for Bader charge.** Bader remains nonlinear and topology sensitive; the Hartree audit establishes the general principle that error structure matters through its interaction with the downstream operator.

## Decisive evidence

- `analysis/hartree_spectral_mechanism/results/matched_pair_mechanism.csv`
- `analysis/hartree_spectral_mechanism/results/reconstruction_spectral_metrics.csv`
- `analysis/hartree_spectral_mechanism/results/radial_spectrum_summary.csv`
- `analysis/hartree_spectral_mechanism/results/mechanism_ratio_summary.csv`
- `analysis/hartree_spectral_mechanism/results/SUMMARY.json`
- `analysis/hartree_spectral_mechanism/results/REPORT.md`

## Non-negotiable interpretation boundaries

- The Fourier audit does **not** replace QSQ as the central contribution.
- The Hartree spectral mechanism is not asserted as the unique mechanism for re-derived Bader error.
- Historical Hartree results remain reproducible; the Nyquist-safe operator is a parity-checked mechanism operator and does not retroactively redefine the original benchmark.
- P1–P4 cohorts, thresholds, perturbation families, and QSQ decision rules are unchanged.
- The new main-text figure must be generated from versioned CSV/JSON outputs, with source code retained alongside SVG/PDF/PNG exports.
