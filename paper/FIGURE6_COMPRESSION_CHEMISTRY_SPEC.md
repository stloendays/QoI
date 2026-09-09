# Figure 6 — Compression–chemistry tradeoff

## Canonical role

**Title:** *Compression–chemistry tradeoffs depend on realized perturbation, not nominal tolerance alone*

This is a main-text decision figure. It links the earlier QoI/operator results back to practical compressor selection:

`nominal control -> realized density perturbation -> QoI response -> chemical certification`

The figure must be generated from the frozen development benchmark, not from illustrative/synthetic points.

## Panels

### A. Realized error-budget usage differs by codec

Show `realized_Linf_over_nominal` against requested relative tolerance. The purpose is to make the nominal-control confounder visible before comparing chemical outcomes. The manuscript may report the data-derived codec medians, but the plotting script must calculate them from the frozen table rather than hard-code them.

### B. Compression ratio versus realized perturbation

Compare rate using `realized_Linf / value_ptp`, not nominal tolerance. This is the fair scalar-magnitude comparison axis.

### C. Bader response at matched realized perturbation

Plot re-solved Bader error against realized relative perturbation and highlight one data-driven one-decade window. The highlighted window is visual context, not a new inference protocol. It shows that similar scalar density-error magnitude can still map to a broad topology-sensitive chemical response.

### D. Stability-aware certification frontier

For each chemical tolerance `tau = 1e-4, 1e-3, 1e-2 e`, define the curve as:

> the fraction of Protocol A.1-eligible materials for which at least one certified reconstruction achieves compression ratio greater than or equal to the x-axis threshold.

This definition makes the frontier monotone and decision-interpretable. Do **not** hard-code a winning codec or imply a universal winner; the plotted frozen data determine the ranking and any crossings.

## Canonical source and outputs

Source:
- `figures/R/figure6_compression_chemistry_tradeoff.R`

Rendered outputs:
- `figures/R/rendered/figure6_compression_chemistry_tradeoff_R.svg`
- `figures/R/rendered/figure6_compression_chemistry_tradeoff_R.png`
- `figures/R/rendered/figure6_compression_chemistry_tradeoff_R.pdf`

The prior `figures/R/figure6_matched_realized_linf.R` remains as a supporting matched-analysis visualization and should not be deleted; its matched within-material evidence is still useful for Results/SI and for validating claims about residual codec differences after scalar L-infinity matching.

## Word-manuscript inclusion

When a Word manuscript is generated, include the **canonical rendered Figure 6** in the main text. Prefer the high-resolution PNG for DOCX compatibility while retaining SVG/PDF as publication assets. Do not insert the earlier illustrative mockup if the data-driven render is available.

## Claim boundary

Supported:
- equal nominal tolerance does not imply equal realized perturbation;
- realized distortion is the correct first alignment variable for codec comparison;
- scalar realized L-infinity alone does not determine Bader chemical error;
- the rate/fidelity decision frontier depends on the requested chemical contract.

Not supported from this figure alone:
- one codec is universally best;
- scalar L-infinity fully explains codec-specific error geometry;
- these rankings generalize beyond the tested density/QoI setting without external evidence.
