# JCTC Main-Figure Assembly Plan v0.1

**Date:** 2026-09-06  
**Target:** Journal of Chemical Theory and Computation, Article  
**Principle:** freeze scientific estimands first; polish layout second. No figure may introduce a claim stronger than the manuscript/SI lints permit.

## Global production rules

- Main text uses **six figures**.
- Figure numbering remains 1–6.
- Use the same terminology as the JCTC manuscript: *re-derived Bader error*, *fixed-basin diagnostic*, *Protocol-A.1 numerical stability floor*, *realized L∞*, *basin reassignment*, *NON_EVALUABLE_BADER_UNSTABLE*.
- Do not use “intrinsic noise floor,” “causal mediation,” “universal best codec,” or same-nominal comparisons as pure spatial-structure evidence.
- All uncertainty should be defined in captions; material-level/bootstrap inference must not be visually confused with row-level sample size.
- Vector output preferred for charts (`SVG`/`PDF` retained as source-quality files); high-resolution raster exports can be made for the submission portal if required.
- Final font sizes, axes, legends, and panel labels must remain legible after embedding in the ACS Fast Format manuscript.

---

## Figure 1 — Evaluation contract schematic

### Scientific role

Establish the paper’s conceptual framework before any codec comparison:

`compressed field -> realized field error -> re-derived Bader partition -> chemical error`

with an independent eligibility gate:

`reference QoI -> Protocol A.1 -> resolvable?`

### Panels / elements

1. original electron-density field \(\rho\);
2. compression/reconstruction to \(\tilde\rho\) with measured \(L_\infty\);
3. split into fixed-basin diagnostic versus re-derived Bader analysis;
4. decomposition \(\Delta Q_{total}=\Delta Q_{integrand}+\Delta Q_{domain}\);
5. small Protocol-A.1 eligibility gate distinguishing `NON_EVALUABLE` from codec failure.

### Status

**Needs original schematic artwork.** No additional numerical data required.

### JCTC emphasis

Make this look like a computational-chemistry method diagram, not a generic data-compression infographic. The dominant visual object should be an electron-density/Bader-partition motif.

---

## Figure 2 — Fixed-basin scoring suppresses downstream error

### Scientific role

Demonstrate why the downstream analysis must be re-executed after reconstruction.

### Frozen headline

Re-derived Bader error exceeds fixed-basin error in **99.7% of 4,627** successful base-ladder rows.

### Recommended panels

**a.** log–log scatter of re-derived versus fixed-basin maximum per-atom Bader error with equality line.  
**b.** codec × core-tolerance paired-ratio summary.  
**c.** fraction with re-derived > fixed at core tolerances.

### Current assets

- `figures_v03/Figure2_fixed_vs_resolved_draft.svg`
- PDF/PNG counterparts
- figure-data exports under `paper_data_v03/`

### Production status

**Statistics frozen; visual redesign/polish only.**

### Important caption rule

Do not present 52.8× as a universal factor. The ratio is strongly codec/tolerance dependent. The denominator-robust main statement is the 99.7% directionality result.

---

## Figure 3 — Bader-domain migration mechanism

### Scientific role

Provide the mechanistic bridge between codec-associated reconstruction structure and downstream Bader error.

### Recommended panels

**a. Direct decomposition, representative set.** Show bounded domain share and/or integrand/domain contributions for the 12-material, 106-case set. Headline median domain share = **0.995**, IQR 0.965–0.999, 84.9% >0.90; closure residual <= \(2.22\times10^{-16}\) e.

**b. Reassignment versus measured pointwise error.** Show that similar realized \(L_\infty\) values can correspond to differing amounts of basin reassignment.

**c. Spatial example.** Reference/reconstructed basin labels plus reassigned voxels around a representative interatomic boundary.

**d. Full-benchmark attenuation.** Material-FE codec multipliers at A.1 \(10^{-3}\) e complete-case scale: SZ3/ZFP 2.34 -> 0.96 and SPERR/ZFP 2.08 -> 0.94 after reassignment; reassignment beta 0.880, p=5.78e-28.

### Current status

**Partially frozen.** Panels a/d can be built from current evidence. Panel c requires an appropriate existing spatial case/label visualization source. The full per-atom file is unavailable.

### Per-atom rule

If `mechanism/basin_error_decomposition_per_atom.csv` arrives before submission, use it only under the preregistered case/material aggregation plan. Do not treat atoms as independent replicates. Upgrade panel a only if the result survives material-level bootstrap and leave-one-material-out sensitivity.

If the file does not arrive, Figure 3 is still publishable with the existing representative-set direct decomposition plus full-benchmark attenuation.

---

## Figure 4 — QoI resolvability and probe validation

### Scientific role

Show that Bader charge itself must be numerically defined at the requested accuracy, and that the stability probe must perturb algorithmically relevant structure.

### Frozen headline

Protocol A.1 non-evaluable fraction:

- \(10^{-4}\) e: **79.9%**
- \(10^{-3}\) e: **41.4%**
- \(10^{-2}\) e: **9.7%**

### Recommended panels

**a.** non-evaluable fraction vs contract, overall + corpus strata.  
**b.** archived float32-probe floor versus A.1 noise-probe floor in calibration set.  
**c.** ties / zero-reassignment probe diagnostics.  
**d.** metadata-predictability audit with development CV and untouched external AUROC.

### Current assets

- `figures_v03/Figure4_resolvability_probe_draft.svg`
- PDF/PNG counterparts
- `stability/` and `paper_data_v03/fig4_*` data

### Production status

**Statistics frozen; visual redesign/polish only.**

### Important visual rule

A.1 values must be labelled as protocol-defined numerical stability results, not intrinsic material properties.

---

## Figure 5 — Separate bound utilization from residual reconstruction structure

### Scientific role

Answer the strongest reviewer objection: ZFP’s same-nominal advantage is partly because it realizes much smaller \(L_\infty\), but that does not explain the full Bader-error difference.

### Recommended panels

**a. Bound utilization.** `realized_Linf / nominal_bound`: ZFP median 0.1575; SZ3/SPERR ~1.0.  
**b. Complete-case matched realized-L∞.** At A.1 \(10^{-3}\) e: SZ3/ZFP 1.82 [1.68,2.01], n=119; SPERR/ZFP 2.00 [1.79,2.25], n=115.  
**c. Mechanism attenuation.** Same complete-case material-FE multipliers before/after adding reassignment.

### Current assets

- `figures_v03/Figure5_magnitude_structure_draft.svg`
- PDF/PNG counterparts
- complete-case and mechanism-attenuation CSV/MD outputs

### Production status

**Statistics frozen; visual redesign/polish only.**

### Important interpretation rule

Call the approximately twofold effect a **codec-associated residual after controlling realized pointwise magnitude**, not a causal codec effect.

---

## Figure 6 — Contract-dependent certified compression frontier

### Scientific role

Translate the fidelity framework into the practical storage/accuracy decision.

### Recommended visualization

Compression ratio versus certification coverage, stratified bulk/slab; label points by Bader contract and codec.

### Frozen examples

- bulk, \(10^{-2}\) e: SZ3 51.8× /95.2%; ZFP 30.0× /98.8%.
- slab, \(10^{-2}\) e: SZ3 67.8× /77.0%; ZFP 40.5× /96.7%.
- bulk, \(10^{-3}\) e: SZ3 12.9× /99.0%; ZFP 13.5× /99.0%.
- bulk, \(10^{-4}\) e: ZFP 7.63× /100%, n=42.

### Current assets

- `figures_v03/Figure6_certified_frontier_draft.svg`
- PDF/PNG counterparts
- `benchmark/best_certified_a1.csv`

### Production status

**Statistics frozen; visual redesign/polish only.**

### Strict slab caveat

Only **four** slab materials are A.1-admitted at \(10^{-4}\) e; that point/row must be visually and textually marked descriptive.

---

# Supporting figures / tables allocation

Move reviewer-oriented robustness out of the main visual flow:

- denominator-floor and material-balanced fixed-basin ratio audit;
- matching-caliper sensitivity;
- common-support interpolation sensitivity;
- complete-case failure removal table;
- seed-dependence distributions;
- probe-amplitude sensitivity;
- symmetry-equivalent relabeling sensitivity;
- global electron-count negative control;
- full certified-frontier numerical tables;
- lossless baselines;
- failure taxonomy.

These belong in the SI unless one becomes necessary to answer a specific reviewer concern.

# Figure completion gates

## Ready for final graphic polish now

- Figure 1 conceptual schematic
- Figure 2
- Figure 4
- Figure 5
- Figure 6

## Conditional

- Figure 3: final atom-level enhancement depends on whether per-atom data arrive, but the current representative-set + attenuation version is already scientifically supportable.

# Final acceptance checklist

- [ ] every panel has one clear estimand;
- [ ] sample size/denominator stated in caption where needed;
- [ ] confidence intervals identify bootstrap/model source;
- [ ] no pseudoreplication language;
- [ ] no codec color/ordering inconsistencies across figures;
- [ ] strict slab n=4 clearly marked;
- [ ] figure text readable at manuscript embedding size;
- [ ] all six figures cited in numerical order;
- [ ] SVG/PDF source retained and raster export checked;
- [ ] final figure hashes recorded in `SUBMISSION_MANIFEST_TEMPLATE_v0.1.md`.
