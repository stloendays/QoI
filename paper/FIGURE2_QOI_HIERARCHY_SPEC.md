# Figure 2 specification — QoI operator hierarchy

## Purpose

Figure 2 is the central mechanism figure for the reframed manuscript. It must show that the same density reconstructions exhibit qualitatively different error-propagation behavior depending on the downstream QoI operator. It is not a codec leaderboard and must not imply that Hartree potential is scientifically superior to Bader charge.

## Figure title

**The downstream QoI operator determines how density perturbations propagate into scientific error**

## Panel layout

Use a 2 x 2 main layout with a narrow conceptual strip above the panels.

### Conceptual strip

Left-to-right hierarchy:

`rho(r)` -> `N_e = integral rho` -> `V_H = inverse-Laplacian[rho]` -> `Q_Bader = integral over Omega_A[rho] rho`

Under the three QoIs, annotate only the mathematical class:

- Total electron number: **global linear**
- Hartree potential: **linear nonlocal**
- Bader charge: **topology-dependent local**

Do not label this as a universal ordering of difficulty.

### Panel A — Global conservation does not certify local chemical fidelity

Scatter or density plot:

- x: `electron_count_abs_dev` (log scale)
- y: `Bader_error_resolved_e` (log scale)
- all available frozen reconstruction rows with finite values
- vertical guide: `1e-4 e`
- horizontal guide: `1e-3 e`

Highlight the upper-left region corresponding to:

`|Delta N_e| < 1e-4 e` and `Bader error >= 1e-3 e`.

Annotate:

- 3,205 rows preserve electron count below 1e-4 e
- 1,383 of these fail the 1e-3 e Bader criterion
- **43.15% decoupling fraction**

Message: global density conservation is not a certificate of atom-resolved chemical fidelity.

Data:
- `analysis/electron_count_qoi/electron_bader_decoupling.csv`
- `benchmark/master_benchmark_full.csv`

### Panel B — Hartree error follows realized L_inf smoothly

Plot gate-passing rows from the full Hartree expansion:

- x: `realized_Linf` (log scale)
- y: `potential_rel_RMSE` (log scale)
- facet or encode by codec without obscuring the common scaling
- distinguish bulk / slab using shape or secondary facet only if legible

Overlay pooled or codec-specific log-log fits. Prefer six thin fitted lines for codec x stratum and no fitted line across material identities if that creates a misleadingly low pooled R2 impression.

Primary annotations:

- pooled alpha = **1.02**
- codec x stratum alpha = **0.91-1.12**
- material-level median R2 = **0.994-0.997**

Message: the smooth nonlocal QoI exhibits approximately first-order propagation from realized pointwise perturbation.

Data:
- `analysis/hartree_potential_expansion/rows.csv`
- `analysis/hartree_potential_expansion/group_summary.csv`
- `analysis/hartree_potential_expansion/material_smoothness.csv`

### Panel C — Bader response is substantially less regular on identical reconstructions

Preferred form: paired distribution of material-level diagnostics rather than another dense scatter.

For each material-codec pair with >=5 gate-passing rows, compare Hartree and Bader:

Option 1, preferred:
- x: QoI (`Hartree`, `Bader`)
- y: material-level log-log R2
- paired lines for each material-codec pair, with distribution summary

Companion inset or annotation:
- Hartree monotone: **88.6%**
- Bader monotone: **32.4%**
- Hartree local elasticity: **-2.0 to +4.4**
- Bader local elasticity: **-9.3 to +14.1**
- maximum Bader consecutive jump: **22,296x**

If visual density is excessive, use violin/box distributions for R2 and annotate monotonic fractions separately.

Message: Bader error is less predictable from perturbation magnitude because the downstream partition can change with the density.

Data:
- `analysis/hartree_potential_expansion/material_smoothness.csv`
- `analysis/hartree_potential_expansion/RESULTS_DETAIL.md`

### Panel D — Similar smooth-field fidelity does not determine Bader fidelity

Plot matched-Hartree-error dispersion:

Preferred form:
- x: Hartree-error bin center (`potential_rel_RMSE`, 0.5-decade bins)
- y: Bader error P10-P90 band or P90/P10 dispersion
- separate traces/facets for codecs
- bulk/slab either facet or shape if readable

Emphasize bins where:

`P90(Bader error) / P10(Bader error) >= 10`.

Main annotation:

- **55.4%** of gate-passing rows lie in matched-Hartree-error bins with >=1 decade Bader spread
- condition occurs in all three codecs and both bulk/slab strata

Message: similar Hartree-potential fidelity is insufficient to infer Bader fidelity.

Data:
- `analysis/hartree_potential_expansion/matched_error_dispersion.csv`

## Caption skeleton

**Figure 2 | Scientific error propagation depends on the downstream QoI operator.** (A) Tight conservation of the global electron number does not guarantee preservation of re-derived Bader charges: 43.15% of reconstructions with |Delta N_e| < 10^-4 e still exceed 10^-3 e in Bader error. (B) The periodic Hartree potential, evaluated on the same reconstructed densities, follows an approximately first-order response to realized L_inf (pooled exponent 1.02; material-level median log-log R2 0.994-0.997). (C) Bader charge is substantially less regular across the same tolerance ladders, with monotonic behavior in 32.4% of material-codec pairs compared with 88.6% for the Hartree potential and individual Bader-error jumps up to 22,296-fold. (D) At matched Hartree-potential error, Bader fidelity remains broadly dispersed: 55.4% of gate-passing reconstructions occupy bins with at least one decade of Bader-error spread. Together these results show that reconstruction error alone does not determine scientific fidelity; the response depends on the mathematical structure of the downstream QoI.

## Slab caveat

Do not annotate Hartree as universally monotone. In slab systems strict monotonicity falls to 47-84% depending on codec, although material-level Hartree R2 remains 0.965-0.983 and deviations are small. If Panel C includes slab-only diagnostics, make this visually or textually explicit.

## Styling constraints

- Main text figure, not SI.
- Avoid bar-chart-heavy composition.
- No decorative molecular icons inside quantitative panels.
- Use identical codec mapping across all panels and the rest of the manuscript.
- Use logarithmic axes where errors span decades.
- Prefer material-level summaries over row-level overplotting when the message is response regularity.
- Do not use the phrase "Hartree is better than Bader" anywhere in the figure or caption.
- The visual hierarchy should read: conservation decouples -> smooth operator scales -> topological operator jumps -> matched smooth fidelity still cannot predict Bader fidelity.
