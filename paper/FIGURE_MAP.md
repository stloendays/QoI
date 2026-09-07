# Figure map

Updated: 2026-09-07.

This map follows the figure numbering already used in `figures/drafts/` and the polished R work in `figures/R/`. Scientific content is frozen before final styling. A panel is DATA-READY only when its source data exist in the release; EXTERNAL-PENDING means the panel is reserved for the frozen corpus-scale external run and will not be populated from pilot/sentinel outcomes.

**Working title:** *Chemical Fidelity Is Not a Pointwise Error: Topology-Induced Failure Modes in Lossy Compression of Electronic Densities*

## Narrative spine

Lossy scientific compressors control pointwise reconstruction error, but chemistry is evaluated through a derived observable whose integration domains can move when the field is perturbed. A fixed-basin evaluation therefore understates the real downstream error. The observable itself also has a material-dependent stability floor, so fidelity can only be judged after QoI qualification. Under the corrected Protocol A.1, lossy compression remains useful, but certified rates depend on the downstream chemical contract and on the codec's realized—not merely requested—perturbation. Representative atom-level decomposition identifies domain migration as the dominant term at the worst-affected atom. Frozen independent external validation then tests which development conclusions transfer without retuning.

---

## Figure 1 — Honest rate–chemical-fidelity frontier

Headline development figure: compression ratio versus resolved/re-derived Bader-charge error, with ZFP, SZ3 and SPERR separated and bulk/slab shown explicitly. Only Protocol A.1-admitted material/threshold combinations enter certification statements. Threshold guides at 1e-4, 1e-3 and 1e-2 e make the scientific contract visible.

The tight ladder is complete and merged; it is no longer a pending dependency.

*Primary data:* `benchmark/master_benchmark_full.csv` (6,343 rows; 254 materials), `benchmark/best_certified_a1.csv`, `benchmark/summary_a1.csv`.

*Status:* **DATA-READY**. Final publication rendering still needed.

---

## Figure 2 — Fixed-basin evaluation understates downstream error

Paired fixed-basin versus resolved-basin Bader error, with the identity line and the degree of understatement. The scientific point is not merely that two numerical metrics differ: reconstruction can move the Bader partition itself, so integrating over the original basins omits a topological/domain term.

The codec winner is often robust, but fixed basins materially distort error magnitude and can change the ordering of the non-winning codecs. Certification therefore uses the resolved/re-derived partition.

*Primary data:* `benchmark/master_benchmark_full.csv`.

*Existing scripts:* `figures/R/figure2_fixed_vs_resolved.R`, `figures/drafts/figure2_fixed_vs_resolved.py`.

*Status:* **DATA-READY; R draft exists**.

---

## Figure 3 — Certification landscape across chemical tolerances

For each Protocol A.1 scientific threshold, show the distinction between:

- evaluable versus non-evaluable materials;
- certified versus not certified among evaluable materials;
- codec-dependent Certified Compression Ratio (CCR).

This figure is the operational version of the proposed workflow: stability qualification precedes fidelity certification rather than being treated as a post-hoc caveat.

*Primary data:* `benchmark/best_certified_a1.csv`, `benchmark/summary_a1.csv`, `benchmark/pairwise_a1.csv`, Protocol A.1 eligibility tables in `stability/`.

*Existing scripts:* `figures/R/figure3_certification_landscape.R`, `figures/drafts/figure3_certification_landscape.py`.

*Status:* **DATA-READY; R draft exists**.

---

## Figure 4 — The QoI stability floor and Protocol A → A.1 correction

Show the material-dependent Bader stability floor and why the archived float32 round-trip probe was inadequate. Protocol A.1 uses the frozen five-seed equal-amplitude noise probe because the order-preserving float32 round trip can leave the on-grid watershed ordering unchanged and therefore miss partition instability.

Panels should include the A versus A.1 contrast, threshold-dependent non-evaluable fractions, and the probe-calibration example demonstrating that equal-L-infinity perturbations can trigger large basin reassignment even when the float32 probe does not.

*Primary data:* files in `stability/`, including the A.1 seed table, eligibility summaries and probe calibration; archived Protocol A retained for provenance.

*Existing scripts:* `figures/R/figure4_stability_protocol.R`, `figures/drafts/figure4_stability_floor.py`.

*Status:* **DATA-READY; R draft exists**.

---

## Figure 5 — Requested versus realized L∞ error budget

Compare `realized_Linf_over_nominal` across codecs. The same requested absolute bound does not imply the same realized perturbation: ZFP systematically uses only a fraction of the requested budget, while SZ3 and SPERR typically approach it much more closely. This provides a mechanistic explanation for why nominally matched tolerances can yield very different chemical errors.

This figure must not claim that conservative realization is the only cause of codec differences; it is one measured mechanism that separates requested pointwise control from actual field perturbation.

*Primary data:* `benchmark/master_benchmark_full.csv`.

*Existing script:* `figures/drafts/figure5_realized_error_budget.py`.

*Status:* **DATA-READY; scientific draft exists**.

---

## Figure 6 — Pointwise error is not chemical error

At matched nominal tolerance, show the spread in resolved Bader error and the per-material codec ratios. Development results show that SZ3's resolved Bader error exceeds ZFP's by a per-material median of approximately 6.4x at 1e-4, 9.2x at 1e-3 and 12.4x at 1e-2 on the matched sets, despite all retained codec rows respecting their requested L∞ bounds.

The figure supports the central statement that a pointwise error contract is not itself a chemical-fidelity contract.

*Primary data:* `benchmark/master_benchmark_full.csv`.

*Existing script:* `figures/drafts/figure6_pointwise_vs_chemical.py`.

*Status:* **DATA-READY; scientific draft exists**.

---

## Figure 7 — Error-structure mechanism: domain migration at the atom level

Use the representative mechanism set to decompose, for every atom,

`ΔQ_total = ΔQ_integrand + ΔQ_domain`.

The released atom-level table contains 1,665 rows across 12 representative materials and 106 successful material/codec/tolerance points; two additional ZFP points are recorded as BaderKit failures in `failure_registry.csv`. The decomposition identity closes to numerical precision (reported residual ≤ 2e-16). At the atom carrying the largest absolute total error in each successful point, the reported median domain-term share is 0.9995.

The manuscript claim must remain scoped correctly: in this pre-specified representative mechanism set, the worst-affected atom is overwhelmingly domain-migration dominated. The 12-material design does not justify asserting population-wide universality by itself.

*Primary data:* `mechanism/basin_error_decomposition_per_atom.csv`, `mechanism/basin_error_decomposition_summary.csv`, `failure_registry.csv`.

*Existing script:* `figures/drafts/figure7_error_structure_mechanism.py`; it should be refreshed to consume the atom-level release table directly where appropriate.

*Status:* **DATA-READY; atom-level data gap CLOSED**.

---

## Figure 8 — Independent external generalization and confirmatory transfer

This is the only main-figure scientific dependency still open.

The frozen external corpus contains 65 systems (37 AFLOW bulk + 28 NOMAD 2D). External Protocol A.1 stability qualification is already complete. For rate–fidelity, the primary confirmatory cohort was frozen before corpus-scale execution at 63 systems (36 AFLOW bulk + 27 NOMAD 2D), excluding only the two implementation sentinels from headline rate–fidelity analysis.

The final panels should separate two questions:

1. **QoI stability transfer:** which stability conclusions reproduce across development and external strata?
2. **Rate–fidelity transfer:** certification fraction, CCR, pairwise codec outcomes, realized/requested perturbation and fixed/resolved diagnostics on the confirmatory 63 systems.

No pilot or sentinel result may be substituted for the corpus-scale confirmatory result.

*Primary data already frozen:* external manifest and Protocol A.1 stability tables.

*Pending data:* aggregate outputs from GitHub Actions run `34074537547`, including all-65 descriptive and confirmatory-63 summaries.

*Status:* **EXTERNAL-PENDING**.

---

## Supplementary figure/table map

| Item | Content | Primary release data | Status |
|---|---|---|---|
| S1 | No-exclusion sensitivity | `supplement/` sensitivity table | DATA-READY |
| S2 | Bader error relative to material's own stability floor | `supplement/` floor-relative table | DATA-READY |
| S3 | Inflated threshold sensitivity, τ_eff = max(τ, k·floor) | `supplement/` sensitivity table | DATA-READY |
| S4 | Probe-amplitude sensitivity | `supplement/` amplitude table | DATA-READY |
| S5 | Seed dependence of Protocol A.1 floor | `stability/` seed table | DATA-READY |
| S6 | Negative result: boundary-aware allocation | retained negative-result evidence | DATA-READY |
| S7 | Negative result: promolecule prior | retained negative-result evidence | DATA-READY |
| S8 | Failure taxonomy and registry | `failure_registry.csv` plus external failure registries | DEVELOPMENT READY; external appendix pending Full |
| S9 | External compressor baselines / unit-normalization audit | retained baseline report | DATA-READY |
| S10 | Full atom-level mechanism table and representative-case selection audit | `mechanism/basin_error_decomposition_per_atom.csv` | DATA-READY |

The symmetry-folding bulk claim remains dropped because it was not regenerated under the corrected metric and is not needed for the paper's contribution.

## Current manuscript state

Figures 1–7 are scientifically supported by released development data. Figure 8 is reserved for the frozen external Full result. The project therefore has a stable main-figure architecture; the remaining work is external evidence closure, figure refinement, captioning and manuscript writing rather than discovery of another core experiment.