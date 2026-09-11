# Current paper story — 2026-09-11

## One-sentence thesis

**A downstream scientific tolerance is a valid compression benchmark only after the QoI has been shown to be numerically identifiable at that tolerance; otherwise binary benchmark outcomes confound compressor-induced error with instability of the downstream analysis.**

## What the paper is actually about

This manuscript is no longer framed around the established observation that small pointwise reconstruction error does not guarantee small downstream QoI error. That result is background motivation.

The contribution is a **benchmark-validity and measurement-contract framework** for scientific compression. The evaluation order is:

`QoI stability qualification -> eligibility -> compression evaluation -> certification`

rather than simply:

`field error -> QoI error -> pass/fail`.

For Bader charge, each material-threshold pair has one of three scientifically distinct states:

1. **eligible + certified** — the reference QoI is resolvable at the requested tolerance and the compressed reconstruction satisfies the Bader contract;
2. **eligible + not certified** — the reference QoI is resolvable, but the reconstruction violates the contract; this is a legitimate compression failure;
3. **non-evaluable** — the reference Bader analysis itself is not stable at the requested tolerance, so the codec can be assigned neither pass nor fail.

## Headline quantitative result

The central Figure 3 audit uses 254 development materials × 3 codecs = **762 material–codec decisions per Bader threshold**.

| Bader contract | Naive failures | Reclassified non-evaluable | Genuine eligible failures | Fraction of naive failures reclassified |
|---|---:|---:|---:|---:|
| 1e-4 e | 533 | 518 | 15 | **97.2%** |
| 1e-3 e | 310 | 296 | 14 | **95.5%** |
| 1e-2 e | 108 | 61 | 47 | 56.5% |

At the two strictest contracts, more than 95% of apparent binary failures cannot be scientifically attributed to the compressor because the reference Bader analysis is non-evaluable at the requested precision.

The correction is not a permissive exclusion rule. It also invalidates apparent successes: at **1e-4 e, 106 of 229 naive passes (46.3%) are non-evaluable**. The correct benchmark therefore changes the label space, rather than merely lowering the failure rate.

## Supporting evidence chain

### Independent QoI eligibility

Protocol A.1 measures a material-specific Bader stability floor from five fixed-seed uniform perturbations at the material's float32 L-infinity perturbation scale. Across 319 development + external systems, the non-evaluable fraction is:

- **79.9%** at 1e-4 e;
- **41.4%** at 1e-3 e;
- **9.7%** at 1e-2 e.

These percentages describe the measurability of the downstream QoI, not codec performance.

### Same reconstruction, different operator response

Electron number and periodic Hartree potential provide smoother controls on the same reconstructed densities. Hartree error follows an approximately first-order response to realized field perturbation (pooled log-log exponent ~1.02; median material R^2 = 0.997 ZFP, 0.994 SZ3, 0.996 SPERR), whereas re-derived Bader charge is much less regular.

This operator comparison motivates why downstream analysis must be part of the scientific contract, but it is not itself the paper's novelty claim.

### Bader-specific mechanism

Bader integration domains are re-derived from the reconstructed density. Compression can therefore perturb both the density values and the basin assignment. Fixed-basin scoring suppresses the domain-migration contribution and can substantially understate the scientific error.

This explains the Bader-specific sensitivity, but the manuscript does not generalize basin migration to arbitrary QoIs.

### Analysis-limited regime: supported wording

At the strictest 1e-4 e certified contract, resolved Bader errors are on the same scale as the independently measured A.1 floor: median error/floor is approximately **1.09× for ZFP, 1.33× for SZ3, and 1.23× for SPERR**.

Supported wording:

> **The strictest certified regime is floor-scale, consistent with an emerging analysis-limited regime.**

Do not claim a universal material-level identity `plateau = floor` from the current frozen evidence.

### Fair codec comparison requires realized-distortion control

Equal nominal codec tolerances do not produce equal realized perturbations. At matched nominal tolerance, realized L-infinity ratios are approximately ZFP/SZ3 = 0.17 and ZFP/SPERR = 0.17. Within-material matching on realized L-infinity reduces this confounding; the remaining Bader difference supports a residual error-structure contribution without identifying a unique geometric invariant.

### External confirmation

The untouched 63-system external cohort is evaluated under the same frozen qualification and certification rules with no retuning. External eligibility expands with relaxed tolerance (16/63, 42/63, 57/63 at 1e-4, 1e-3, 1e-2 e), and the best certified compression-rate ordering changes with the requested scientific contract. Therefore the output is a **stability-qualified rate-fidelity frontier**, not a universal codec leaderboard.

## Figure logic

- **Figure 1:** scientific-compression measurement contract.
- **Figure 2:** operator hierarchy / motivation.
- **Figure 3:** **central benchmark-validity result — binary benchmark -> three-state certification.**
- **Figure 4:** Protocol A -> A.1 qualification-probe validation.
- **Figure 5:** Bader basin-migration mechanism.
- **Figure 6:** nominal-vs-realized distortion confounding control.
- **Figure 7:** untouched external confirmation.

## Claim boundaries

Do not use the following as headline novelty:

- “pointwise error does not imply QoI fidelity” — established background;
- “Bader has a numerical/grid floor” — established numerical-analysis background;
- “Bader basin migration is a universal QoI mechanism” — unsupported generalization;
- “Protocol A.1 rescues codec failures” — incorrect interpretation;
- “plateau equals A.1 floor” — stronger than the frozen data support.

The canonical claim is **QoI certifiability before benchmark scoring**.
