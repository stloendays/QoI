# Editorial decisions v0.2.1

## 1. Preferred title

**Pointwise Error Bounds Do Not Define Chemical Fidelity: Stability and Domain Migration in Lossy-Compressed Electron Densities**

Why this is preferred over the current working title *Chemical Fidelity Is Not a Pointwise Error: Topology-Induced Failure Modes in Lossy Compression of Electronic Densities*:

- `domain migration` is exactly what the direct decomposition measures;
- `stability` captures the Protocol-A.1 contribution, which is unusually important to the paper;
- `topology-induced` risks implying that the manuscript proves changes in a formal topological invariant such as a contour tree or Morse–Smale complex; the present evidence is stronger and more specific for Bader-domain reassignment/local ascent structure;
- the 2024–2026 topology-preserving compression literature is now crowded, so a title that names our actual chemistry-specific mechanism differentiates the paper more cleanly.

Strong shorter alternative:

**Beyond Pointwise Error Bounds: Stability and Domain Migration in Compressed Electron Densities**

More chemistry-forward alternative:

**When Error Bounds Fail Chemistry: Bader-Domain Migration in Lossy-Compressed Electron Densities**

Avoid `first`, `topology-preserving` or `topology failure` in the title unless a formal topological descriptor is added to the analysis.

## 2. Abstract wording correction for fixed-basin evaluation

Use this sentence in place of a standalone `52.8x` headline:

> Across 4,627 successful base-ladder reconstructions, the Bader error obtained after re-deriving the partition exceeds the fixed-basin estimate in 99.7% of cases. The multiplicative understatement is substantial but codec- and tolerance-dependent, showing that reusing the original domains suppresses a reconstruction-dependent error channel rather than introducing a single constant bias.

The pooled median resolved/fixed ratio (52.8x) is statistically real and robust to denominator floors through 1e-6 e, but it should appear in Results/Figure 2 with stratification, not as if it were a universal factor. At nominal relative tolerance 1e-3, for example, the medians are SPERR 35.3x, SZ3 2.9x and ZFP 70.7x.

## 3. Figure 2 wording

Main panel annotation:

> **Re-derived error > fixed-basin error in 99.7% of 4,627 successful base-ladder cases.**

Secondary panel:
- show log resolved/fixed ratio by codec and nominal tolerance;
- optionally place the pooled median 52.8x as a small reference annotation;
- state that the pooled median remains 52.6x under a 1e-6 e denominator floor and the material-balanced median is 59.5x;
- do not collapse all codecs/tolerances into “fixed basins understate by ~53x.”

## 4. Preferred mechanism language

Strong but defensible:

> Direct decomposition in a representative 12-material mechanism set identifies migration of the field-derived Bader domains as the dominant measured contribution. Across the full benchmark, the approximately twofold codec-associated residual at matched realized L∞ is almost completely attenuated after conditioning on the fraction of reassigned basin voxels, providing independent mechanism-consistent evidence for the same pathway.

Avoid:
- “basin migration causally mediates the codec effect”;
- “domain migration dominates all 254 materials”;
- “codec spatial structure causes a 2x Bader error.”

## 5. Preferred novelty sentence

> Prior work has shown that pointwise compression guarantees need not preserve downstream quantities of interest or topological descriptors. Here the downstream observable is additionally defined over integration domains reconstructed from the compressed field itself; we show that those domains migrate, that this migration dominates a representative direct decomposition, and that the observable must be stability-qualified before it can serve as a fidelity contract.

This distinguishes the manuscript from general QoI-preserving compression, TopoSZ-style topological preservation, 2026 local-order-preserving compression, and TOPIQ-style statistical error propagation without claiming that those literatures do not exist.
