# Unified QOAC framework and Bader novelty boundary — 2026-10-05

Status: research-design record after completed QOAC-H, QOAC-B2 and QOAC-B3 evidence. This is not yet a manuscript scope reopening.

## Unified principle

The common object is not a particular Fourier law. It is the **measurement structure** that determines which information must survive compression.

### Class I — diagonalizable linear operators

For a downstream linear map

    y = L x,

with scientific quadratic distortion

    D^2 = ||L delta x||^2
        = delta x^* L^* L delta x,

diagonalizing L^*L gives mode sensitivities lambda_k. Under the first-order high-rate scalar-quantization model,

    Delta_k proportional to lambda_k^(-1/2)
            = 1 / sigma_k(L).

QOAC-H is the inverse-Laplacian example:
- Hartree potential sensitivity amplitude ~ |G|^-2;
- squared-error weight ~ |G|^-4;
- allocation Delta_G ~ |G|^2.

This class changes **error allocation before or during compression**.

### Class II — fixed low-dimensional scientific constraints

If the scientific measurement can be written on a fixed state as

    A x = q,

but a generic compressor already represents x efficiently in its native coordinates, it can be preferable to preserve that representation and project the decoded field onto the constraint manifold.

For a fixed Bader partition, each atomic charge is a basin integral. The QOAC-B2 uniform per-basin correction is simultaneously the minimum-Linf and minimum-L2 unconstrained correction that restores the exact discrete basin sum.

This class uses

    generic compression -> minimum-disturbance projection -> certification.

### Class III — unstable discrete state induced by a continuous field

If the downstream algorithm first derives a discrete state

    s = T(r)

from a numerically fragile continuous reference r, and the later scientific measurement depends on s more directly than on the full r, the archive can compile and store s losslessly rather than demanding a lossy reconstruction of r reproduce T(r).

QOAC-B3 is this case:
- r = AECCAR0 + AECCAR2;
- T = frozen Henkelman on-grid Bader partition;
- s = exact integer AtIndex partition map.

The exact partition is then combined with the QOAC-B2 projected CHGCAR.

This class performs

    exact analysis once -> compile sufficient discrete state -> lossless state coding.

## Evidence now available

### QOAC-H

- 48/48 disjoint confirmatory wins at tau_H=1e-6;
- median CR ratio 15.016x;
- full 254-material census at 1e-6: 253/253 comparable wins, median 12.463x.

### QOAC-B2

Development:
- 12 materials;
- kappa=4 auxiliary CHGCAR Linf budget;
- 11/12 wins;
- median CR ratio 1.782x;
- actual Bader error 0 for 12/12.

Frozen holdout:
- 38/38 analyzable;
- 34/38 wins;
- median CR ratio 1.865x;
- bootstrap 95% CI [1.759, 1.985];
- actual Bader error 0 for 38/38;
- zero reassignment for 38/38;
- all pre-frozen confirmatory criteria passed.

Combined 50-material descriptive population:
- 45/50 wins;
- median 1.861x;
- P05 0.9995x;
- 50/50 Bader error 0;
- 50/50 reassignment 0.

### QOAC-B3

12-material engineering:
- exact partition round trip 12/12;
- max direct-map/Henkelman charge discrepancy 4.97e-7 e;
- median lossless-AE / exact-partition bytes 176.85x;
- complete compiled archive wins 12/12;
- median baseline/compiled archive bytes 97.39x.

Full 50-material descriptive census:
- 50/50 complete, 0 failures;
- exact partition decode 50/50;
- max direct-map/Henkelman discrepancy 4.97e-7 e;
- lossless-AE / partition bytes:
  - minimum 121.26x,
  - P05 125.25x,
  - median 210.66x,
  - P95 841.05x,
  - maximum 1522.47x;
- complete archive baseline/compiled ratio:
  - wins 50/50,
  - minimum 12.29x,
  - P05 46.55x,
  - median 92.52x,
  - P95 190.18x,
  - maximum 270.36x.

## Prior-art boundary

Do not claim that QOAC-B is the first:
- topology-aware compressor;
- segmentation-preserving compressor;
- decoded-field correction method;
- QoI constraint-satisfaction compressor;
- lossless label/segmentation-map coder.

Relevant adjacent work includes:
- TopoSZ, which derives contour-tree constraints and incorporates them into error-controlled compression;
- MSz, which edits reconstructed fields to recover Morse-Smale segmentations;
- the 2025 general framework for augmenting lossy compressors with topological guarantees, which stores variable-precision corrections;
- QoI-preserving learned/scalable pipelines that include constraint-satisfaction postprocessing;
- generic lossless segmentation-map coding.

The supported research distinction is **Bader measurement-contract decomposition and compression**:
1. QSQ identifies the partition-defining reference as the dominant instability source.
2. Exact-reference Bader is decomposed into a continuous integrated field and a discrete partition state.
3. The CHGCAR is preserved by a mathematically minimal fixed-basin projection after generic compression.
4. The fragile continuous partition reference is replaced, for the declared Bader-specific archive contract, by a losslessly compiled exact Henkelman partition.
5. All claims remain tied to the frozen on-grid Henkelman semantics.

## Scope boundary

A compiled Bader partition is not a substitute for AECCAR for arbitrary future analyses.

It is a sufficient state only for the declared downstream Bader partition/integration contract under the frozen algorithmic semantics.

Likewise, the QOAC-B2 projected CHGCAR is not automatically certified for Hartree or other QoIs; those require their own qualification/certification.

## Next generality test

The next Class-I operator is the Hartree electric field

    E_H = -grad V_H.

Its Fourier sensitivity amplitude is proportional to |G|^-1, so the pre-specified high-rate allocation is

    Delta_G proportional to |G|.

The predicted exponent is therefore beta=1, distinct from:
- Hartree potential beta=2;
- operator-blind beta=0.

A successful frozen beta=1 ablation would show that QOAC is responding to the downstream operator rather than encoding a generic preference for low-frequency accuracy.
