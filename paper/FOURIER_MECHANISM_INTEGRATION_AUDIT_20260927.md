# Fourier-mechanism manuscript integration audit — 2026-09-27

Status: **PASS / RE-FROZEN**

Branch: `paper/fourier-mechanism-integration-20260927`

## Canonical reader-facing sources

- `paper/MANUSCRIPT.md`
- `paper/CURRENT_PAPER_STORY.md`
- `paper/SUPPLEMENTARY_INFORMATION.md`
- `paper/FIGURE_MAP.md`
- `paper/CLAIM_EVIDENCE_MATRIX.md`
- `paper/FIGURE7_CAPTION_FINAL_20260927.md`
- `README.md`

The 2026-09-11 predecessor manuscript and dated story/SI files remain preserved in Git history and were not overwritten.

## Scope control

The only author-authorized scientific extension is the completed Fourier-spectrum mechanism audit of the existing Hartree control. P1–P4 definitions, QSQ cohorts, thresholds and perturbation rules are unchanged. The scope addendum is `paper/FOURIER_MECHANISM_SCOPE_ADDENDUM_20260927.md`.

QSQ remains the central contribution. The Fourier result provides operator-resolved mechanistic support for the residual codec effect after realized-$L_\infty$ matching.

## Scientific evidence lock

Primary mechanism population:
- 457 exact ZFP/SZ3 matched pairs
- 214 materials
- 914 regenerated reconstructions

Headline values:
- historical Hartree ratio: 0.0776221
- Nyquist-safe Hartree ratio: 0.0776219
- maximum safe Parseval relative error: 1.30e-15
- material-level total spectral-energy factor: 0.376
- material-level spectral Hartree-susceptibility factor: 0.203
- material-median absolute-log share from spectral structure: 62.0%
- materials with lower ZFP spectral Hartree susceptibility: 99.5%
- materials with higher ZFP spectral centroid: 98.1%
- materials with lower ZFP low-G error-energy fraction: 99.1%
- material-level low-G fraction ratio, ZFP/SZ3: 0.416

Machine-readable sources:
- `analysis/hartree_spectral_mechanism/results/matched_pair_mechanism.csv`
- `analysis/hartree_spectral_mechanism/results/reconstruction_spectral_metrics.csv`
- `analysis/hartree_spectral_mechanism/results/radial_spectrum_summary.csv`
- `analysis/hartree_spectral_mechanism/results/mechanism_ratio_summary.csv`
- `analysis/hartree_spectral_mechanism/results/SUMMARY.json`

## Equation–code parity

The reader-facing manuscript and SI now define
`G_s` as the non-zero reciprocal-space modes outside excluded even-grid Nyquist planes, matching the implementation mask
`(g2 > 0) & (~nyq)`.

All Hartree-weighted sums in the canonical manuscript/SI use this safe set. The exact pairwise decomposition is

`R_H = sqrt(E_ZFP/E_SZ3) * sqrt(S_H,ZFP/S_H,SZ3)`

with
`S_H = W_H/E`
and both `E` and `W_H` evaluated over `G_s`.

The direct-space/Fourier-space identity closes to machine precision in the completed audit.

## Main-figure integration

### Figure 7 — Fourier-spectrum mechanism

Source:
- `figures/R/figure7_fourier_spectrum_mechanism.R`

Formal outputs:
- `figures/R/rendered/figure7_fourier_spectrum_mechanism_R.png`
- `figures/R/rendered/figure7_fourier_spectrum_mechanism_R.pdf`
- `figures/R/rendered/figure7_fourier_spectrum_mechanism_R.svg`

Final drift-assertion render:
- GitHub Actions run: `36312408741`
- conclusion: **success**
- source assertions bind 457 pairs, 214 materials, status, radial-bin counts and the three displayed mechanism centers to `SUMMARY.json`.

Visual QA:
- first render identified overlap between lower-panel titles;
- C/D titles and caption were shortened;
- final render has no panel-title overlap;
- ZFP/SZ3 colors remain consistent with the manuscript figure family.

### Figure 8 — external confirmation

Source:
- `figures/R/figure8_external_confirmation.R`

Formal outputs:
- `figures/R/rendered/figure8_external_confirmation_R.png`
- `figures/R/rendered/figure8_external_confirmation_R.pdf`
- `figures/R/rendered/figure8_external_confirmation_R.svg`

Final terminology render:
- GitHub Actions run: `36312160314`
- conclusion: **success**
- historical reader-facing labels `Protocol A.1` / `A.1 qualification` were replaced by QSQ terminology.
- underlying external scientific analysis is unchanged.

## Cross-document consistency

- Main-text new mechanism section cites Fig. 7.
- Untouched external confirmation now cites Fig. 8.
- Figure map, current-story file and claim–evidence matrix use the same numbering.
- Claim 18 records the Fourier mechanism as **CONFIRMED**.
- Reader-facing methods use QSQ terminology; historical `Protocol A/A.1` identifiers remain only where needed for provenance/file paths.
- No `TODO`, `FIXME`, author-note or stale Fig. 7 external-confirmation markers remain in the canonical manuscript/story/SI.
- Integrated abstract is 250 words.

## Interpretation boundary

The confirmed mechanism is:
`codec -> reciprocal-space reconstruction-error allocation -> downstream operator weighting -> Hartree error`.

It is valid to generalize that scalar pointwise distortion can be insufficient when the downstream operator is spatially or spectrally selective.

It is **not** valid to claim that the nonlinear re-derived Bader residual is uniquely governed by the same Fourier statistic. For Bader, basin migration and topology-sensitive reassignment remain the direct mechanism evidence.

## Re-freeze decision

The manuscript is re-frozen on this branch after integration of the Fourier-spectrum mechanism. Further new scientific endpoints, cohorts, perturbation families or primary thresholds require another explicit scope-reopening addendum.
