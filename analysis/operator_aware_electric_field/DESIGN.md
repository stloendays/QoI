# QOAC-E — operator-specific compression for the Hartree electric field

Freeze date: 2026-10-05

Status: prospective operator-generality engineering study. No electric-field result was inspected before this protocol was defined.

## Scientific question

QOAC-H showed that the Hartree potential rewards an operator-derived reciprocal-space allocation

    Delta_G proportional to |G|^2.

That result alone cannot distinguish a general operator principle from a simpler heuristic that merely protects low-frequency density modes.

The Hartree electric field supplies a stronger test because

    E_H = -grad V_H

and therefore, for G != 0,

    E_H(G) = -i G 4 pi rho(G) / |G|^2.

Its response amplitude scales as

    |E_H(G)| / |rho(G)| proportional to 1 / |G|,

so the squared downstream error weight is proportional to |G|^-2.

Under the same frozen high-rate scalar-quantization approximation used for QOAC-H,

    Delta_G proportional to |G|.

The pre-specified electric-field exponent is therefore

    beta = 1.

## Competing allocations

Evaluate exactly three reciprocal-space allocation exponents:

- beta = 0: operator-blind spectral quantization;
- beta = 1: electric-field-derived allocation;
- beta = 2: Hartree-potential-derived allocation.

All three use the identical audited QOAC-H v0.2 Hermitian-orbit representation:
- full orthonormal FFT;
- one canonical coefficient per Hermitian orbit;
- only G=0 exact;
- conservative minimum-alias reciprocal norm for Nyquist coordinates;
- 32 radial storage shells;
- zlib level 6;
- complete serialized bytes define rate.

The only intended variable is beta.

## Development population

Reuse the exact 12-material QOAC-H engineering manifest:

    analysis/operator_aware_codec_hartree/results/PILOT_MANIFEST.csv

This is a development panel, not an independent confirmation.

No electric-field metric was used to select these materials.

## Alpha ladder

For every beta evaluate exactly:

    alpha / ptp(rho) = logspace(1e-7, 1e1, 25).

Total planned rows:

    12 materials x 3 beta values x 25 alpha values = 900.

## Electric-field metric

For a decoded real-space density, compute the periodic Hartree electric field directly from the decoded field:

    E_H(G) = -i 4 pi G rho(G) / |G|^2,  G != 0.

The vector relative RMSE is

    D_E =
      sqrt( mean( |E_tilde(r) - E_ref(r)|^2 ) )
      /
      sqrt( mean( |E_ref(r)|^2 ) ),

where |E|^2 = E_x^2 + E_y^2 + E_z^2.

Two implementations are reported:

### Nyquist-safe primary metric

Modes lying on any even-grid Nyquist plane are excluded from the downstream field operator. This avoids assigning a continuum vector direction to an alias-equivalent Nyquist mode.

This metric is the primary mechanism metric.

### Historical FFT-convention guardrail

All nonzero rFFT modes are included using the repository's standard FFT signed-frequency convention.

The historical value is reported as a guardrail against an apparent gain created solely by safe-plane exclusion.

The codec itself does not leave Nyquist planes exact and continues to quantize them using the conservative minimum-alias |G|.

## Matched-storage mechanism comparison

Within each material, greedily match beta pairs by serialized compression ratio with a maximum difference of

    0.05 dex in log10(CR).

Require at least three matched pairs for a material-level comparison.

For each material compute the median matched-pair ratio:

    R_10 = D_E(beta=1) / D_E(beta=0)

and

    R_12 = D_E(beta=1) / D_E(beta=2).

## Frozen engineering gates

### Gate A — operator-aware gain over blind allocation

GO requires:
- all 12 materials mechanism-evaluable;
- beta=1 better than beta=0 in at least 9/12 materials;
- material-median R_10 < 0.70.

### Gate B — operator specificity

GO requires:
- all 12 materials mechanism-evaluable;
- beta=1 better than beta=2 in at least 9/12 materials;
- material-median R_12 < 0.95.

This gate is important: passing it would show that the correct downstream exponent matters and that over-protecting low-G modes according to the Hartree-potential law is suboptimal for the electric field.

### Gate C — metric-convention consistency

For every material, the beta=1 versus beta=0 direction under the historical electric-field metric must agree with the Nyquist-safe direction.

This is a direction-only guardrail, not a performance threshold.

A disjoint electric-field confirmatory cohort is authorized only if Gates A, B and C all pass.

## Interpretation

A successful result supports:

> The preferred reciprocal-space precision law follows the downstream operator's spectral sensitivity, rather than a universal preference for low-frequency accuracy.

It does not yet establish generality beyond periodic electronic-density operators. A later cross-domain operator, such as turbulence vorticity, is required for that stronger claim.
