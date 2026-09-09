# Figure map

Scientific logic first; no styling work until the evidence behind each panel is frozen. Every figure names the data file it is generated from. Updated 2026-09-09 after the full Hartree-potential QoI expansion.

**Working title:** *Scientific Fidelity Is QoI-Dependent: Certifying Lossy Compression of Electronic Densities*

**Alternate, more Bader-forward title:** *Chemical Fidelity Is Not a Pointwise Error: QoI-Dependent Failure Modes in Lossy Compression of Electronic Densities*

## Narrative spine

A pointwise density-error bound is not a scientific-fidelity bound. The same reconstructed density can preserve a global linear observable, produce a smooth and nearly power-law error in a nonlocal linear observable, and simultaneously exhibit strongly non-monotone error in a topology-dependent local observable. We therefore treat fidelity as a property of the pair `(reconstruction, downstream QoI operator)`, not of the reconstruction alone. Bader charge is the deeply validated topology-sensitive case: it requires re-partitioning after reconstruction, exhibits domain-migration error, has a material-specific stability floor, and must be stability-qualified before certification. Under that qualified contract, lossy compression remains useful and the codec ranking depends on realized rather than nominal distortion.

The manuscript should not claim that Hartree potential is "better" than Bader. The supported claim is that **QoI mathematical structure governs error propagation**.

---

## Figure 1 — From density error to QoI-dependent scientific error

Conceptual schematic. Original density `rho` -> codec at requested tolerance -> reconstructed density `rho_tilde` -> three downstream operators:

1. total electron count `N_e = integral rho` (global linear control),
2. Hartree potential `V_H = nabla^{-2} rho` (linear nonlocal comparator),
3. Bader charge `q_A = integral_{Omega_A[rho]} rho`, with density-dependent topological domains.

Show that a single scalar reconstruction error feeds different downstream maps. Include the Bader-specific correct evaluation path: basins must be re-derived from the reconstruction, with `Delta Q_total = Delta Q_integrand + Delta Q_domain`.

**Primary message:** density fidelity is not scientific fidelity; the downstream operator is part of the fidelity contract.

*Data:* schematic only; quantitative evidence appears in Figures 2–6. *Status:* READY FOR DESIGN.

---

## Figure 2 — QoI sensitivity hierarchy on identical reconstructions

This is the new mechanism figure and should be promoted to the main text.

**(a) Electron-number negative control.** Scatter or density plot of `|Delta N_e|` against resolved Bader error, with guides at `|Delta N_e| = 1e-4 e` and `Delta q_Bader = 1e-3 e`. Highlight the left-upper quadrant: 1,383 of 3,205 reconstructions with `|Delta N_e| < 1e-4 e` still have Bader error >= `1e-3 e` (43.15%). This establishes that global conservation is not a certificate of local chemical fidelity.

**(b) Hartree error vs realized L∞.** Log-log relationship for all gate-passed rows, faceted by codec and bulk/slab. Report slopes 0.91–1.12 and per-material `R^2` medians 0.994–0.997. Pooled exponent is 1.02.

**(c) Bader error on the same rows.** Same x-axis and facets. Bader pooled slopes are 0.53–0.67 with lower `R^2` in every codec × stratum cell. Material-level strict monotonicity is 32.4% for Bader versus 88.6% for Hartree overall.

**(d) Matched-Hartree-error dispersion.** For 0.5-decade Hartree-error bins, show `P90/P10` of Bader error. 55.4% of gate-passed rows lie in bins with at least one decade of Bader spread; the condition occurs in all three codecs and both bulk/slab strata. Annotate the largest Bader jump (22,296x, `mp-676693`, ZFP) while Hartree `R^2` on the same ladder is 0.999.

**Slab caveat:** do not label Hartree as universally monotone. Strict slab monotonicity is 47–84% depending on codec, while per-material slab Hartree `R^2` remains 0.965–0.983. The slab contrast is supported by smoothness, elasticity range and jump size, not strict rung-by-rung monotonicity.

*Data:* `analysis/electron_count_qoi/electron_bader_decoupling.csv`, `analysis/electron_count_qoi/summary_by_codec.csv`, `analysis/hartree_potential_expansion/rows.csv`, `group_summary.csv`, `material_smoothness.csv`, `matched_error_dispersion.csv`, `RESULTS_DETAIL.md`. *Status:* **DATA-READY / PROMOTE_TO_MAIN_TEXT**.

---

## Figure 3 — Why Bader is topology-sensitive: fixed basins fail and domain migration dominates

Combine the old fixed-basin and mechanism figures to keep the main text compact.

**(a)** Paired scatter `dQ_fixed` vs `dQ_resolved`, one point per material/codec/rung, faceted bulk/slab, identity line. Fixed-basin evaluation systematically understates the error.

**(b)** Error decomposition at representative materials: `Delta Q_integrand` versus `Delta Q_domain`, with fraction of voxels reassigned. The domain term dominates the tight-tolerance failure mode.

**(c)** A representative ladder showing a large Bader jump despite a smooth Hartree response may be used as the visual bridge from Figure 2 to the topology mechanism.

*Data:* frozen master table plus mechanism decomposition files; Figure 2 Hartree rows for the bridge example. *Status:* DATA-READY, with representative-case decomposition retained under its existing evidence limitations.

---

## Figure 4 — A QoI must be stability-qualified before certification

**(a)** Protocol A.1 stability-floor distributions across development and external strata, with contract thresholds at `1e-4`, `1e-3`, `1e-2 e`.

**(b)** Non-evaluable fraction at each threshold. Emphasize that the contract itself may be below the observable's numerical/topological stability floor.

**(c)** Probe validation: archived float32 floor versus A.1 floor. The order-preserving float32 probe understates the floor by a median factor of about 8,700; Protocol A remains provenance, A.1 is the operative qualification protocol.

**Primary message:** a downstream QoI cannot serve as a fidelity contract at a precision at which the QoI is not itself numerically identifiable.

*Data:* Protocol A.1 stability and probe-calibration outputs. *Status:* DATA-READY.

---

## Figure 5 — Honest rate–QoI-fidelity frontier under the qualified Bader contract

Compression ratio versus re-solved Bader error, ZFP/SZ3/SPERR, bulk/slab, restricted to A.1-eligible material-threshold pairs. Include tight ladder points and the low-error plateau where tighter codec tolerance no longer reduces resolved Bader error.

This is where the general framework returns to the practical compression question: after the QoI is correctly evaluated and qualified, what compression ratios are actually certifiable?

*Data:* `benchmark/master_benchmark_full.csv` plus A.1 eligibility tables. *Status:* DATA-READY; use final merged ladder rather than the older pending wording.

---

## Figure 6 — Nominal tolerance is not realized distortion

**(a)** Equal-nominal diagnostic: ZFP realizes about 0.17x the L∞ of SZ3/SPERR at the same requested tolerance, while SZ3/SPERR is about 1.00x.

**(b)** Within-material matching on `log10(realized_Linf)`: ZFP/SZ3 resolved-Bader error ratio 0.557 at the primary 0.10-dex caliper; ZFP/SPERR 0.601; SZ3/SPERR 1.033.

**(c)** Compression-ratio effects on the same matched pairs.

**(d)** A.1 certification differences at `tau = 0.01 e`.

**Primary message:** scalar L∞ magnitude is insufficient, but equal nominal tolerance is not a valid way to establish that; realized distortion must be controlled first.

*Data:* `analysis/matched_realized_linf_v1/`. *Status:* DATA-READY / existing rendered figure can be revised into the new numbering.

---

## Figure 7 — External confirmation and practical value

Use a compact two-part closing figure rather than two separate headline figures.

**(a) External confirmatory cohort.** Final 63/63 primary systems complete, 1,689 retained rows, zero material-level failures, zero bound violations, with all three pre-specified rate-fidelity directional expectations reproduced. Show the external certified compression-ratio summary and explicitly retain the narrower ZFP–SZ3 separation at `1e-4 e`.

**(b) Lossless versus qualified lossy.** Compare f64+zstd, f64+xz, f32+zstd with best certified lossy compression at each QoI threshold. This closes the paper by showing that the stricter scientific contract still permits substantial compression.

*Data:* `validation/final_external_confirmatory63_20260908/`, `paper/EXTERNAL_CONFIRMATORY63_EVIDENCE.md`, lossless baseline outputs, A.1 summary tables. *Status:* DATA-READY.

---

## Main-text claim hierarchy

1. **General:** reconstruction error alone does not define scientific fidelity; downstream QoI structure matters.
2. **Mechanistic:** on identical reconstructions, Hartree-potential error follows a smooth approximately first-order response to realized L∞, whereas Bader error is more non-monotone and can vary by orders of magnitude at matched Hartree error.
3. **Bader-specific:** the topology-sensitive error is strongly affected by basin migration, so fixed-basin scoring is invalid for fidelity assessment.
4. **Qualification:** Bader charge has a material-specific stability floor; contracts below that floor are not evaluable and must not be counted as compression failures or successes.
5. **Practical:** after controlling realized distortion and applying A.1 qualification, lossy compression remains useful and the codec tradeoff can be reported honestly.

Do not generalize from these three QoIs to all scientific observables. The manuscript supports a **general evaluation principle** with one deeply validated topology-sensitive case and two structurally distinct controls/comparators.

---

## Supplementary material

Move detail that no longer needs headline space out of the main figure sequence:

| Panel | Content | Disposition |
|---|---|---|
| S1 | Full electron-count summaries by codec/tolerance | new SI |
| S2 | Full Hartree group tables, per-material fits and slab monotonicity diagnostics | new SI |
| S3 | Hartree reproduction-gate failures: 73 SZ3 byte-count mismatches | new SI / provenance |
| S4 | No-exclusion sensitivity | retain |
| S5 | Floor-relative error and inflated-threshold sensitivity | retain |
| S6 | Probe amplitude and seed sensitivity | retain |
| S7 | Negative result: boundary-aware allocation | retain |
| S8 | Negative result: promolecule prior | retain |
| S9 | Failure taxonomy / registry | retain |
| S10 | External baselines and unit conversions | retain |

The old standalone "generality of slab vs bulk stability" figure should not remain a headline figure because that specific bulk/slab generalization was falsified externally. Its useful evidence is absorbed into Figure 4 and Figure 7.
