# Matched realized-L∞ V1

This directory contains the reproducible within-material comparison that separates
**realized pointwise distortion magnitude** from codec-dependent **error-field structure**.

## Primary result

At equal nominal tolerance, ZFP realizes only ~0.17× the L∞ of SZ3/SPERR. After
matching reconstructions within material at comparable `realized_Linf` (primary
caliper 0.10 dex), the resolved-Bader gap shrinks substantially but remains:

- ZFP/SZ3 resolved Bader error = **0.557×** (95% material-bootstrap CI 0.525–0.598)
- ZFP/SPERR = **0.601×** (0.534–0.662)
- SZ3/SPERR = **1.033×** (0.976–1.072)

The ZFP residual remains ~0.56–0.60× across 0.05–0.30 dex matching calipers.
Therefore equal nominal tolerance was a major confound, but scalar L∞ magnitude
alone still does not determine chemical fidelity.

## Files

- `REPORT.md` — human-readable statistical report
- `schema_and_protocol.json` — detected schema and frozen analysis settings
- `equal_nominal_diagnostics.csv` — how unequal realized L∞ is at equal nominal tolerance
- `matching_diagnostics.csv` — common-support and match-quality diagnostics
- `matched_effects_summary.csv` — effects and material-bootstrap CIs at all calipers
- `matched_pairs_primary_0p10dex.csv` — row-level primary matched pairs
- `headline_results.json` — machine-readable primary results

Analysis source: `../matched_realized_linf_v1.py`

Figure: `../../figures/R/rendered/figure6_matched_realized_linf_R.png`

Manuscript draft: `../../paper/MATCHED_REALIZED_LINF_RESULTS.md`
