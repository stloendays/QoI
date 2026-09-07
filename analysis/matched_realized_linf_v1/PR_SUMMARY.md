# PR summary — matched realized-L∞ V1

## Why this analysis was needed

The master table showed that ZFP, SZ3 and SPERR do not realize the same L∞ even
when given the same nominal tolerance. The previous matched-nominal comparison
therefore could not separate codec error structure from actual distortion
magnitude.

## What changed

- Added a standard-library Python analysis that matches codec outputs **within material** on `log10(realized_Linf)` without replacement.
- Primary matching caliper: 0.10 dex; sensitivity: 0.05, 0.10, 0.20, 0.30 dex.
- Material-level bootstrap uncertainty prevents repeated rungs from being treated as independent samples.
- Added a GitHub Actions workflow that reruns the analysis and renders Figure 6 in R.
- Added manuscript-ready Results wording and corrected Claim 1 / Figure 6 documentation.

## Headline result

Equal nominal tolerance strongly exaggerates the ZFP–SZ3 separation because ZFP
realizes only ~0.17× the L∞ of SZ3/SPERR. At matched realized L∞, ZFP retains a
smaller but robust resolved-Bader advantage: 0.557× ZFP/SZ3 and 0.601× ZFP/SPERR
at the primary 0.10-dex caliper, while SZ3/SPERR is 1.033× and statistically
indistinguishable. The residual is stable across 0.05–0.30 dex.

This changes the causal interpretation from “the 6–12× matched-nominal gap is an
error-geometry effect” to “equal nominal tolerance is a major realized-distortion
confound, but scalar L∞ still does not determine chemical fidelity.”
