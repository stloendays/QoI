# Three-way common-support Hartree spectral audit

Status: **confirmatory robustness extension; all previously frozen mechanism branches remain unchanged**.

## Why this audit exists

The pairwise three-codec extension found a coherent but unexpected pattern:

- ZFP/SZ3: total spectral-error magnitude and Hartree spectral susceptibility both favor ZFP.
- SZ3/SPERR: both factors favor SPERR, with susceptibility dominant.
- ZFP/SPERR: total spectral-error magnitude favors ZFP, while spectral susceptibility favors SPERR; the two factors oppose one another and the net Hartree ranking can change by system type.

Those three estimates were obtained from three different matched-pair populations.
This audit removes that population-composition ambiguity by requiring **three-way
common support**.

## Frozen source table

Use only rows from
`analysis/hartree_qsq_full/results/hartree_codec_rows.csv` with
`scientific_reproduction_gate_pass = True`.

No rematching of the frozen pairwise results is performed. Instead, a new
three-way robustness population is built directly from the same reproduced
Hartree rows.

## Symmetric three-way matching

Within each material, form every candidate tuple containing one ZFP, one SZ3,
and one SPERR row.

For a tuple with
`x_c = log10(realized_Linf_c)`, define

`span = max(x_ZFP, x_SZ3, x_SPERR) - min(x_ZFP, x_SZ3, x_SPERR)`.

A tuple is admissible only when

`span <= 0.10 dex`.

All admissible tuples are sorted by:

1. smallest span;
2. smallest sum of absolute deviations from the tuple mean in log-Linf;
3. frozen row indices, in the fixed order ZFP, SZ3, SPERR.

Greedily accept the next tuple only if none of its three reconstruction rows has
already been used for that material. Thus every accepted tuple is a symmetric,
without-replacement, all-pairwise common-support match.

The generated tuple protocol is itself archived and every downstream shard reads
that exact file.

## Reconstruction and operator gates

For each tuple endpoint:

- regenerate the reconstruction from the frozen nominal absolute tolerance;
- require reproduced realized L-infinity to match the protocol target within
  5e-6 dex;
- require the historical Hartree relative RMSE to match the protocol target
  within 5e-6 dex;
- retain the historical operator only for exact reproduction;
- compute mechanism quantities with the same Nyquist-safe Hermitian Hartree
  operator used in the closed ZFP/SZ3 audit.

The Nyquist-safe Parseval and weighted-spectrum identities must remain at
machine precision.

## Mechanism variables

For each codec reconstruction:

- total safe spectral error energy, E;
- low-G and high-G energy fractions;
- spectral centroid;
- Hartree-weighted error, W_H;
- spectral Hartree susceptibility, S_H = W_H / E.

For every tuple and every pair A/B,

`R_H(A/B) = sqrt(E_A/E_B) * sqrt(S_H,A/S_H,B)`

must hold exactly up to floating-point precision.

## Primary common-support question

The pairwise extension suggested an unexpected operator-susceptibility ordering

`SPERR < ZFP < SZ3`

(lower is less Hartree-sensitive error per unit total spectral error), with the
opposite centroid ordering

`SPERR > ZFP > SZ3`

and the same-direction low-G ordering

`SPERR < ZFP < SZ3`.

These are **post-pairwise hypotheses** and are tested here on an independent
three-way matched population.

Primary support requires:

1. all reproduction/operator identities pass;
2. material-level pairwise susceptibility centers have bootstrap 95% CIs wholly
   on the directions implied by SPERR < ZFP < SZ3;
3. at least 75% of materials have median tuple susceptibilities ordered
   SPERR < ZFP < SZ3.

Centroid and low-G summaries are supporting checks, not required for the primary
operator-susceptibility conclusion.

Bulk and slab subsets are reported separately.

No manuscript text is modified automatically.
