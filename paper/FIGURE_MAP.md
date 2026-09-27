# Figure map

Updated 2026-09-27. Canonical figure-numbering, narrative role, source, and provenance registry for the current submission scope.

**Active title:** *Numerical stability qualification for downstream-fidelity benchmarks of compressed electronic densities*

## Narrative spine

The manuscript is organized around a benchmark-validity and measurement-contract principle:

> **Scientific compression should be scored only after the reference QoI is qualified at the requested tolerance, and codec comparisons should be interpreted through the downstream operator and realized reconstruction-error structure rather than nominal pointwise bounds alone.**

The reader-facing framework is **QoI Stability Qualification (QSQ)**. The operative decision order is:

`QoI Stability Qualification -> eligibility -> compression evaluation -> certification`

The manuscript does **not** claim novelty for the general observation that small pointwise reconstruction error can coexist with large downstream QoI error. That is motivation. The validation hierarchy is:

`P1 equal-search control -> P2 prospective fresh-perturbation validation -> P3A independent on-grid implementation transfer`

with **P4** as a secondary measurement-contract boundary case study and the Fourier audit as operator-resolved mechanism support.

## Canonical figure registry

| Figure | Role | R source | Formal outputs | Status |
|---|---|---|---|---|
| 1 | Scientific-compression measurement contract | `figures/R/figure1_qoi_contract.R` | `figures/R/rendered/figure1_qoi_contract_R.{png,pdf,svg}` | **LOCKED** |
| 2 | Operator hierarchy on identical reconstructions | `figures/R/figure2_qoi_hierarchy.R` | `figures/R/rendered/figure2_qoi_hierarchy_R.{png,pdf,svg}` | **LOCKED** |
| 3 | **Central validation: equal-search control + prospective QSQ risk stratification** | `figures/R/figure3_certification_landscape.R` | `figures/R/rendered/figure3_certification_landscape_R.{png,pdf,svg}` | **LOCKED — P1/P2 version** |
| 4 | Order-preserving control vs validated QSQ perturbation | `figures/R/figure4_stability_protocol.R` | `figures/R/rendered/figure4_stability_protocol_R.{png,pdf,svg}` | **LOCKED** |
| 5 | Basin migration and topology-sensitive Bader amplification | `figures/R/figure5_topology_mechanism.R` | `figures/R/rendered/figure5_topology_mechanism_R.{png,pdf,svg}` | **LOCKED** |
| 6 | Nominal tolerance vs matched realized L-infinity | `figures/R/figure6_matched_realized_linf.R` | `figures/R/rendered/figure6_matched_realized_linf_R.{png,pdf,svg}` | **LOCKED** |
| 7 | Fourier-spectrum mechanism at matched realized distortion | `figures/R/figure7_fourier_spectrum_mechanism.R` | `figures/R/rendered/figure7_fourier_spectrum_mechanism_R.{png,pdf,svg}` | **LOCKED** |
| 8 | Untouched external confirmation | `figures/R/figure8_external_confirmation.R` | `figures/R/rendered/figure8_external_confirmation_R.{png,pdf,svg}` | **LOCKED** |

## Figure 1 — Measurement contract

**Function:** conceptual entry point. Separate field-level reconstruction error from downstream scientific validity. The key reader-facing logic should be visible without reading the caption:

`reference density -> QSQ -> eligible? -> compression evaluation -> certified / not certified`

If QSQ rejects the material–threshold pair, numerical codec agreement is still reportable, but robustness of the scientific interpretation is not collapsed into the same binary label.

**Take-home:** benchmark validity precedes codec scoring.

## Figure 2 — Operator hierarchy

**Function:** motivation/background evidence, not the headline novelty.

Frozen evidence on identical reconstructions includes:
- 1,383/3,205 reconstructions with `|Delta N_e| < 1e-4 e` still have re-derived Bader error `>=1e-3 e` (43.15%);
- Hartree error follows an approximately first-order response to realized L-infinity (pooled exponent 1.02; median material `R^2` 0.994-0.997 across codecs);
- only 32.4% of material-codec Bader ladders are strictly monotone;
- 55.4% of gate-passing rows lie in matched-Hartree bins with Bader `P90/P10 >= 10`.

**Take-home:** downstream operator structure changes perturbation propagation, motivating a measurement contract.

## Figure 3 — Central validation figure

**Function:** carry the main scientific evidence, not the historical reclassification headline.

**Caption:** `paper/FIGURE3_CAPTION_FINAL_20260911.md` (content revised 2026-09-12 to frozen P1/P2 hierarchy).

### Panel A — Frozen gate predicts fresh perturbation risk

Primary endpoint: `tau = 1e-3 e`.

- QSQ admitted: **143/254 = 56.3% coverage**.
- Fresh perturbations: **59 per material; 14,986/14,986 valid physical trials overall**.
- Eligible group: **135/8,437 = 1.600%** exceedance risk, material-cluster 95% CI **0.782–2.596%**.
- Screen-rejected group: **5,326/6,549 = 81.325%**, 95% CI **75.981–86.257%**.
- Rejected / eligible risk ratio: **50.83×**.

### Panel B — Equal-search control

The originally asymmetric tight ladder is completed for all 111 previously uncovered materials:

- **1,332/1,332** additive reconstructions successful.
- At `1e-3 e`, no-pass risk: **3.3% eligible vs 66.4% screen-rejected**, RR **20.34×**.
- At `1e-4 e`: **10.9% vs 79.3%**, RR **7.30×**.
- At `1e-2 e`: **0% vs 68.0%**.

**Take-home:** QSQ separation persists after codec search opportunity is equalized.

### Panel C — Pre-specified secondary thresholds

Fresh perturbation exceedance risk:

- `1e-4 e`: **4.016% eligible vs 86.938% rejected**, RR **21.65×**.
- `1e-3 e`: **1.600% vs 81.325%**, RR **50.83×**.
- `1e-2 e`: **0.148% vs 79.593%**, RR **537.69×**.

The same 59 response vectors per material support all three thresholds; they are not independent experiments.

**Primary message:** the frozen five-seed QSQ gate prospectively stratifies unseen response risk under the declared iid-uniform perturbation model, and this finding is not explained by unequal compression-search depth.

**Interpretation boundary:** do not claim worst-case stability, simultaneous per-material certification, causal codec attribution, or new-material prospective generalization.

### Historical Figure 3 evidence

The full-record reclassification values **97.2% / 95.5% / 56.5%** remain reproducible but are ladder-design-sensitive because the original tight extension was targeted to eligible materials. They are retained as provenance / sensitivity evidence, not as the Figure 3 headline and not as a design-independent causal misattribution estimate.

## Figure 4 — QSQ probe validation

**Function:** show that a qualification probe must excite the numerical failure mode of the downstream operator.

The archived float32 round-trip probe is retained as provenance. QSQ uses five pre-specified non-order-preserving uniform perturbations at each material's float32 L-infinity amplitude. In the formal paired development comparison, the operative five-seed QSQ floor is a median of approximately **1.6×10^4** times the archived float32-probe floor.

**Take-home:** stability qualification itself must be validated; a numerically tiny but structurally inappropriate perturbation can give a false sense of stability.

## Figure 5 — Bader-specific mechanism and implementation boundary

**Function:** explain why re-derived Bader charge can be irregular and locate the measurement-contract boundary.

Re-derived Bader scoring is the scientific metric because basin assignment is a functional of the reconstructed density. Fixed-basin scoring suppresses domain migration and is diagnostic only.

P3A supporting result:
- 24-system deterministic panel;
- independent Henkelman **on-grid** classification agreement: **24/24 at all three thresholds**, `kappa = 1.000`;
- floor-rank Spearman `rho = 0.995`;
- near-grid agreement: **82.6% / 83.3% / 95.8%**, `rho = 0.754`.

**Take-home:** the effect transfers across an independent implementation when analysis semantics are matched, but it is not implementation-free; the downstream algorithm belongs to the measurement contract.

Do not describe P3A as DFT grid convergence or as identifying a unique physical Bader reference.

## Figure 6 — Realized-distortion confounding control

**Function:** ensure codec comparison is not confounded by nominal tolerance.

At equal nominal tolerance, ZFP realizes approximately 0.17× the L-infinity perturbation of SZ3 or SPERR. Within-material matching on realized L-infinity gives re-derived Bader-error ratios approximately:
- ZFP/SZ3 = **0.557**;
- ZFP/SPERR = **0.601**;
- SZ3/SPERR = **1.033**.

**Take-home:** after benchmark validity is established, fair codec comparison still requires realized rather than nominal distortion control.

## Figure 7 — Fourier-spectrum mechanism at matched realized distortion

**Function:** convert the residual codec effect from a descriptive matched-$L_\infty$ observation into an operator-resolved mechanism result.

Primary population: the exact **457 ZFP/SZ3 matched pairs across 214 materials** from the full Hartree analysis.

Required panels:
- **A:** radial reconstruction-error energy versus normalized reciprocal magnitude, showing the ZFP spectrum shifted away from low $G$ relative to SZ3;
- **B:** Hartree-weighted radial spectrum / $|G|^{-4}$ operator emphasis;
- **C:** exact pairwise decomposition into total spectral-energy and spectral Hartree-susceptibility factors, with material-level centers **0.376**, **0.203**, and Hartree ratio **0.07762**;
- **D:** material-level distribution of the absolute-log contribution from spectral structure, median **62.0%**, with annotations for lower ZFP susceptibility (**99.5%**), higher ZFP centroid (**98.1%**) and lower ZFP low-$G$ fraction (**99.1%**).

Parity checks that must be stated in the caption or SI:
- historical Hartree ratio: **0.0776221**;
- Nyquist-safe Hartree ratio: **0.0776219**;
- maximum Parseval relative error: **1.30×10^-15**.

**Take-home:** matched pointwise distortion is not a complete reconstruction condition. Frequency allocation matters because the Hartree operator weights long-wavelength error much more strongly.

Do **not** state that this Fourier statistic uniquely explains the Bader residual.

## Figure 8 — Untouched external confirmation

**Function:** close the empirical chain using the frozen decision rules on the 63-system untouched external cohort.

External QSQ eligibility is 16/63 at `1e-4 e`, 42/63 at `1e-3 e`, and 57/63 at `1e-2 e`. Certified rate–fidelity ordering changes with the requested scientific contract.

**Take-home:** the frozen stability-qualified evaluation logic reproduces without retuning, while the preferred codec remains tolerance dependent.

## P4 — Chemical contract boundary

P4 is intentionally **not** promoted into a new main headline figure. It belongs in Results/Discussion and Supplementary Tables S15–S16.

Frozen result:
- 5/5 outcome-blind chemistry pairs pass the two-implementation source-reference gate;
- 216/216 compressed solver cells resolve;
- 60/60 common-tight charge-transfer sign decisions preserve the reference direction;
- unqualified baseline: 0 observed sign errors;
- QSQ at `1e-3 e`: retains 36/60 trials from 3/5 pairs, also 0 errors.

**Interpretation:** strict numerical QSQ qualification is not equivalent to preservation of a coarse, large-margin qualitative chemical direction. This is measurement-contract boundary evidence, not a QSQ correctness-gain headline.

## Results order

1. **Figure 1:** define the measurement-contract problem and three-state evaluation logic.
2. **Figure 2:** establish operator-dependent perturbation propagation as motivation.
3. Define the frozen QSQ screen and distinguish reference robustness from fixed-pipeline numerical agreement.
4. **Figure 3:** lead with P1 equal-search control and P2 prospective fresh-perturbation validation; this is the central result.
5. **Figure 4:** validate the QSQ perturbation probe against the archived float32 predecessor.
6. Report the strictest certified regime as **floor-scale, consistent with an emerging analysis-limited regime**; do not claim `plateau = floor`.
7. **Figure 5:** explain basin migration and report P3A implementation transfer as support.
8. Report **P4** as a null correctness / contract-boundary case study.
9. **Figure 6:** control nominal-versus-realized distortion for codec comparison.
10. **Figure 7:** close the matched-distortion residual mechanistically with the Fourier-spectrum Hartree audit.
11. Report stability-qualified rate–fidelity only among eligible material–threshold pairs.
12. **Figure 8:** close with untouched external confirmation.

## Main-text claim hierarchy

1. **Background:** pointwise/raw-data error is not a universal downstream guarantee.
2. **Central contribution:** benchmark tolerances should be independently qualified for QoI numerical stability before scientifically interpreting codec scoring.
3. **Primary controlled evidence:** after equalizing compression-search opportunity, `1e-3 e` no-pass risk is **3.3% vs 66.4% (20.34×)**.
4. **Strongest prospective evidence:** the frozen QSQ gate separates fresh-perturbation risk **1.600% vs 81.325% (50.83×)** at `1e-3 e`, with **56.3% coverage**.
5. **Transfer evidence:** matched on-grid independent implementation gives **24/24 agreement**, while near-grid differences define the analysis-semantic boundary.
6. **Contract-boundary evidence:** a coarse qualitative charge-transfer sign remains correct in all 60/60 tested reconstructions, so strict numerical qualification and qualitative decision preservation are not interchangeable.
7. **Mechanistic support:** density-dependent basin migration explains irregular Bader amplification.
8. **Fair codec comparison:** nominal tolerance is not a common realized-distortion scale.
9. **Operator-resolved mechanism:** after realized-$L_\infty$ matching, reciprocal-space error allocation explains the Hartree codec effect through the $|G|^{-4}$ weighting of squared error.
10. **Practical output:** among eligible systems, the certified compression frontier depends on the requested scientific contract.

## Figure provenance

Locked formal runs retained for provenance:
- Figure 1: run `34371089020`, artifact `10111997887`.
- Figure 2: run `34352844171`, artifact `10104481700`.
- Historical binary-to-three-state Figure 3: run `34565814071`, artifact `10185973963`, source commit `1886f776f048395b47eb16129c1231e814922271`.
- Current P1/P2 Figure 3 source: `figures/R/figure3_certification_landscape.R`; its frozen source contains hard assertions against the completed P1/P2 machine-readable summaries and exports PNG/PDF/SVG from the same code.
- Figure 4: run `34370291570`, artifact `10111673650`.
- Figure 5: run `34349558487`, artifact `10103144848`.
- Figure 6: run `34340308601`, artifact `10099481566`.
- Figure 7: source `figures/R/figure7_fourier_spectrum_mechanism.R`; final caption `paper/FIGURE7_CAPTION_FINAL_20260927.md`; rendered from `analysis/hartree_spectral_mechanism/results/` on the manuscript-integration branch.
- Figure 8: source `figures/R/figure8_external_confirmation.R`; outputs `figures/R/rendered/figure8_external_confirmation_R.{png,pdf,svg}`.

## Submission scope lock

P0–P4 remain resolved. P3B new DFT grid convergence is deferred. P5 remains **NO-GO for the current submission**. The only reopened line is the author-authorized Fourier-spectrum mechanism integration documented in `paper/FOURIER_MECHANISM_SCOPE_ADDENDUM_20260927.md`; it uses the existing Hartree control and does not alter QSQ cohorts, thresholds or perturbation definitions.

The scope is re-frozen after this integration. No further scientific endpoint, perturbation family, primary cohort, DFT convergence experiment or primary threshold should be added before submission without another explicit scope-reopening addendum.

Remaining work is manuscript/figure/SI alignment, archival DOI, journal-specific formatting, and final Word/PDF assembly.
