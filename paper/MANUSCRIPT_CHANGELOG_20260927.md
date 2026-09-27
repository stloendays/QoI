# Manuscript integration changelog — 2026-09-27

## Scope

Author-authorized integration of the completed Fourier-spectrum mechanism audit into the current QoI manuscript. The 2026-09-11 frozen manuscript remains preserved in Git history; the semantic canonical reader-facing sources on this branch are now `paper/MANUSCRIPT.md`, `paper/CURRENT_PAPER_STORY.md`, and `paper/SUPPLEMENTARY_INFORMATION.md`.

## Scientific changes

- Added the full-population Hartree spectral mechanism result: 457 exact ZFP/SZ3 matched pairs across 214 materials, 914 regenerated reconstructions.
- Reproduced the historical material-level Hartree ratio at 0.0776221 and verified a Nyquist-safe ratio of 0.0776219.
- Added Fourier/real-space parity check with maximum relative error 1.30e-15.
- Added exact pairwise decomposition into total spectral-energy and spectral Hartree-susceptibility factors.
- Added the material-level summaries 0.376 and 0.203, with explicit language that separately aggregated centers are not expected to multiply exactly.
- Added 62.0% material-median absolute-log contribution from spectral structure and the 99.5% / 98.1% / 99.1% directionality diagnostics.
- Updated the manuscript-level generalization to reference stability + downstream operator + reconstruction-error structure.

## Interpretation boundary

The Fourier mechanism is a confirmed mechanism for the linear Hartree control. The matched-$L_\infty$ Bader residual remains evidence for reconstruction-error structure beyond scalar distortion, but is not attributed to a single Fourier descriptor. QSQ remains the central contribution and P1–P4 definitions are unchanged.

## Figure changes

- New main **Figure 7**: Fourier-spectrum mechanism audit, generated in R directly from the versioned analysis CSV/JSON files.
- Previous external-confirmation Figure 7 becomes **Figure 8** through a semantic source alias; the underlying external analysis is unchanged.
- Figure 7 outputs are archived as PNG/PDF/SVG with R source retained.

## Files synchronized

- `paper/MANUSCRIPT.md`
- `paper/CURRENT_PAPER_STORY.md`
- `paper/CLAIM_EVIDENCE_MATRIX.md`
- `paper/FIGURE_MAP.md`
- `paper/SUPPLEMENTARY_INFORMATION.md`
- `paper/FOURIER_MECHANISM_SCOPE_ADDENDUM_20260927.md`
- `README.md`
- `figures/R/figure7_fourier_spectrum_mechanism.R`
- `figures/R/figure8_external_confirmation.R`
