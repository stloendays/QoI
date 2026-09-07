# Matched-realized-L∞ analysis: Results draft

**Status:** analysis complete on the 6,343-row master benchmark; manuscript wording below is intended to replace the earlier interpretation of equal-nominal codec gaps as pure error-geometry effects.

## Result

Equal nominal tolerances do not expose the codecs to equal pointwise distortion. Across the 254-material benchmark, ZFP realizes a median L∞ only **0.170×** that of SZ3 and **0.170×** that of SPERR at the same requested absolute tolerance, whereas SZ3 and SPERR realize essentially the same L∞ (**1.00×** median ratio). Thus, the previously reported 6–12× separation in re-derived Bader error between ZFP and SZ3 at matched nominal tolerance mixes two effects: ZFP uses substantially less of the requested error budget, and the codecs distribute a given perturbation differently in space.

To separate those contributions, codec outputs were rematched **within the same material** on `log10(realized_Linf)`, without replacement. The primary caliper was 0.10 dex, corresponding to a maximum L∞ mismatch of 1.259×. This yielded **457 ZFP–SZ3 pairs across 214 materials**, **465 ZFP–SPERR pairs across 206 materials**, and **1,848 SZ3–SPERR pairs across all 254 materials**. The median residual L∞ mismatch was 1.138× for ZFP–SZ3 and 1.136× for ZFP–SPERR; SZ3 and SPERR were already essentially exactly matched.

After controlling realized L∞, the large nominal-tolerance gap **shrinks strongly but does not disappear**. At the primary 0.10-dex caliper, the material-level median ratio of re-derived Bader error is **0.557 for ZFP/SZ3** (95% material-bootstrap CI **0.525–0.598**) and **0.601 for ZFP/SPERR** (95% CI **0.534–0.662**). Equivalently, at comparable realized L∞, SZ3 carries about **1.79×** the resolved Bader error of ZFP and SPERR about **1.66×**. By contrast, SZ3 and SPERR are statistically indistinguishable on the resolved metric (**1.033×**, 95% CI **0.976–1.072**).

The residual ZFP advantage is insensitive to the matching width. For ZFP/SZ3, the resolved-error ratio remains **0.583, 0.557, 0.591 and 0.599** at calipers of 0.05, 0.10, 0.20 and 0.30 dex, respectively, with every bootstrap interval below 1. ZFP/SPERR is similarly stable at approximately **0.59–0.60×** across the same calipers. The result therefore cannot be explained by a narrow-support artifact of the primary match.

The distinction is decision-relevant. Among pairs jointly eligible under Protocol A.1 at τ = 0.01 e, ZFP exceeds SZ3 in certification probability by **14.9 percentage points** (95% CI **10.9–19.0 pp**) and exceeds SPERR by **17.0 pp** (95% CI **12.8–21.3 pp**) at the primary caliper, while SZ3 and SPERR differ by only **−1.5 pp** (95% CI **−3.6 to +0.7 pp**). Therefore a scalar pointwise bound is not sufficient to predict whether a reconstructed density preserves the chemical observable even after the scalar magnitude of the perturbation is controlled.

The rate side shows the complementary trade-off. At matched realized L∞, ZFP reaches only **0.326×** the compression ratio of SZ3 (95% CI **0.312–0.339**), but **2.67×** that of SPERR (95% CI **2.52–2.76**). SZ3 reaches **3.58×** the compression ratio of SPERR (95% CI **3.35–3.82**). Thus, the codec that minimizes resolved chemical error at a fixed realized L∞ is not necessarily the codec that maximizes rate, and rate–fidelity comparisons should treat distortion magnitude and distortion geometry as separate axes.

## Manuscript-level interpretation

The correct conclusion is more nuanced than the earlier matched-nominal statement. **Most of the dramatic ZFP-versus-SZ3 chemical-error gap at equal nominal tolerance is a realized-distortion confound**, because ZFP uses only about one-sixth of the requested L∞ budget. However, matching the actual L∞ does not collapse the codecs onto a common chemical-error curve: ZFP retains an approximately **1.7–1.8×** resolved-Bader advantage over SZ3/SPERR. This persistent residual is direct evidence that **L∞ magnitude alone is insufficient** and that the spatial geometry of the reconstruction error matters for a topology-sensitive observable.

A concise formulation for the main text is:

> Equal nominal tolerances substantially exaggerate codec-dependent chemical error because the codecs realize different fractions of the requested L∞ budget. After rematching reconstructions within material at comparable realized L∞, the ZFP–SZ3 resolved-Bader gap contracts from the earlier multi-fold nominal comparison to ~1.8×, but remains robust across matching calipers. The persistence of this residual at controlled L∞ demonstrates that pointwise distortion magnitude alone does not determine chemical fidelity; the spatial structure of the error remains consequential.

## Claim correction

The earlier statement “SZ3 is 6–12× worse than ZFP, therefore pointwise error geometry explains the gap” should **not** be used causally. The 6–12× matched-nominal result remains a descriptive measurement, but it conflates realized error magnitude and spatial error structure. The defensible causal evidence is the matched-realized result above.

Recommended replacement for Claim 1:

**Pointwise L∞ magnitude does not determine chemical fidelity.** Equal nominal tolerance is itself confounded because ZFP realizes ~0.17× the L∞ of SZ3/SPERR. After within-material matching on realized L∞, ZFP still carries only 0.557× the resolved Bader error of SZ3 and 0.601× that of SPERR at the primary 0.10-dex caliper, while SZ3 and SPERR are indistinguishable. The residual is stable from 0.05–0.30 dex and therefore identifies an error-geometry contribution beyond scalar L∞ magnitude.

## Reproducibility

- Analysis script: `analysis/matched_realized_linf_v1.py`
- Primary matched pairs: `analysis/matched_realized_linf_v1/matched_pairs_primary_0p10dex.csv`
- All caliper effects: `analysis/matched_realized_linf_v1/matched_effects_summary.csv`
- Equal-nominal distortion diagnostic: `analysis/matched_realized_linf_v1/equal_nominal_diagnostics.csv`
- Machine-readable headline: `analysis/matched_realized_linf_v1/headline_results.json`
- Figure script: `figures/R/figure6_matched_realized_linf.R`
