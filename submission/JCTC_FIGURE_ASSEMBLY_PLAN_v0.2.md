# JCTC Main-Figure Assembly Plan v0.2

**Date:** 2026-09-06  
**Target:** Journal of Chemical Theory and Computation, Article

The six main figures are numbered by first appearance in `JCTC_MANUSCRIPT_v0.2.3.md`. Scientific estimands are frozen; production work changes layout, labeling, and visual clarity only.

## Figure 1 — Evaluation contract schematic

**Role:** define the full chain before any codec comparison:

`codec bound -> realized field perturbation -> re-derived Bader partition -> chemical error`

with the independent eligibility gate:

`reference QoI -> Protocol A.1 -> resolvable?`

**Elements:** reference density, reconstruction, measured \(L_\infty\), fixed-basin diagnostic, re-derived partition, integrand/domain decomposition, and Protocol-A.1 qualification.

**Status:** original schematic artwork required; no new numerical analysis.

---

## Figure 2 — Codec error structure at matched realized perturbation

**Role:** separate nominal-bound utilization from residual reconstruction structure.

**Panels:**
- **a.** realized/nominal \(L_\infty\) utilization: ZFP median 0.1575; SZ3/SPERR approximately 1.0.
- **b.** complete-case matched realized-\(L_\infty\) at \(\tau=10^{-3}\) e: SZ3/ZFP 1.82 [1.68, 2.01], n=119; SPERR/ZFP 2.00 [1.79, 2.25], n=115.
- **c.** material-fixed-effect multipliers before and after inclusion of basin reassignment.

**Source asset:** current `figures_v03/Figure5_magnitude_structure_draft.*` becomes submission Figure 2.

**Status:** statistics frozen; visual redesign only.

---

## Figure 3 — Fixed-basin versus re-derived chemical fidelity

**Role:** show why Bader analysis must be rerun on the reconstructed density.

**Headline:** re-derived Bader error exceeds fixed-basin error in 99.7% of 4,627 successful base-ladder reconstructions.

**Panels:**
- **a.** re-derived versus fixed-basin scatter with equality line.
- **b.** codec × core-tolerance paired-ratio summary.
- **c.** fraction with re-derived error greater than fixed-basin error.

**Source asset:** current `figures_v03/Figure2_fixed_vs_resolved_draft.*` becomes submission Figure 3.

**Status:** statistics frozen; visual redesign only.

---

## Figure 4 — QoI resolvability and stability-probe validation

**Role:** define the usable numerical precision of the Bader observable and validate the perturbation family used to measure it.

**Headline non-evaluable fractions:** 79.9% at \(10^{-4}\) e, 41.4% at \(10^{-3}\) e, and 9.7% at \(10^{-2}\) e.

**Panels:** non-evaluable fraction, archived-float32 versus A.1 floor, tie/reassignment probe diagnostics, and external resolvability-prediction audit.

**Source asset:** `figures_v03/Figure4_resolvability_probe_draft.*` remains Figure 4.

**Status:** statistics frozen; visual redesign only.

---

## Figure 5 — Bader-domain migration mechanism

**Role:** connect reconstruction structure to movement of field-derived integration domains and then to charge error.

**Panels:**
- **a.** representative 12-material direct decomposition; median bounded domain share 0.995, IQR 0.965–0.999, 84.9% above 0.90, closure residual at most \(2.22\times10^{-16}\) e.
- **b.** voxel reassignment versus measured \(L_\infty\).
- **c.** representative spatial basin-label migration example.
- **d.** material-scale mechanism-consistency model: SZ3/ZFP 2.34 -> 0.96 and SPERR/ZFP 2.08 -> 0.94 after inclusion of reassignment; reassignment coefficient 0.880, \(p=5.78\times10^{-28}\).

**Source mapping:** the scientific role previously assigned to old Figure 3 becomes submission Figure 5.

**Status:** panels a, b, and d are supported by current evidence; panel c requires production of the final spatial visualization from an existing representative case.

---

## Figure 6 — Contract-dependent certified compression frontier

**Role:** translate the fidelity framework into the practical storage/accuracy decision.

**Visualization:** median best certified compression ratio versus certification coverage, stratified by bulk/slab, codec, and Bader contract.

**Frozen examples:**
- bulk, \(10^{-2}\) e: SZ3 51.8× / 95.2%; ZFP 30.0× / 98.8%.
- slab, \(10^{-2}\) e: SZ3 67.8× / 77.0%; ZFP 40.5× / 96.7%.
- bulk, \(10^{-3}\) e: SZ3 12.9× / 99.0%; ZFP 13.5× / 99.0%.
- bulk, \(10^{-4}\) e: ZFP 7.63× / 100%, n=42.

**Source asset:** `figures_v03/Figure6_certified_frontier_draft.*` remains Figure 6.

**Status:** statistics frozen; visual redesign only. The four admitted slabs at \(10^{-4}\) e are shown as a small-sample strict-contract stratum.

---

## Submission-file mapping

| Submission figure | Existing draft source | Scientific section |
|---|---|---|
| Figure 1 | new artwork | Sec. 2 |
| Figure 2 | old Figure5 magnitude/structure | Sec. 3 |
| Figure 3 | old Figure2 fixed/resolved | Sec. 4.1 |
| Figure 4 | old Figure4 resolvability/probe | Sec. 4.2 |
| Figure 5 | old Figure3 mechanism | Sec. 5 |
| Figure 6 | old Figure6 frontier | Sec. 6.3 |

Final exported files should use the submission numbering rather than the historical draft filenames.
