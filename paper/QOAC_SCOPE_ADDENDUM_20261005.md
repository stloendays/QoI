# QOAC-H manuscript integration scope addendum — 2026-10-05

Author-authorized scope reopening: user requested continued development and manuscript integration after the QOAC-H mechanism, engineering, disjoint confirmation and full-population census completed.

This addendum preserves the 2026-10-03 manuscript as the predecessor and defines the new active story on branch `paper/qoac-integration-20261005`.

## Scientific change

The prior manuscript ended the Hartree line at diagnosis:

    matched distortion -> Fourier mechanism

The completed QOAC-H evidence now closes a further causal/design step:

    qualification -> matched-distortion diagnosis -> operator-derived codec design -> decoded-field certification

This is a substantive new result and is allowed to change the main Results hierarchy and figure count.

## Naming

Reader-facing scientific name: **QOAC-H**, expanded once as **QoI- and operator-aware Hartree compression**.

Do not expose internal development labels such as v0.1 or v0.2 in the manuscript, figures, captions or SI narrative. They remain repository provenance only.

## Canonical claim

> After QSQ establishes that the Hartree contract is numerically resolvable, the Fourier symbol of the downstream Hartree operator can be used to allocate compression error where the operator is least sensitive, converting a diagnosed codec effect into a substantially more efficient certified representation.

## Evidence hierarchy

1. **Mechanism** — existing 457-pair Fourier audit over 214 materials: Hartree sensitivity follows the operator's reciprocal-space weighting and codec error allocation explains much of the matched-distortion effect.
2. **Design law** — high-rate weighted-transform model applied to the Hartree error metric yields (Delta_Gpropto |G|^2); (eta=2) was frozen before QOAC-H results and compared with operator-blind (eta=0).
3. **Mechanism experiment** — 12/12 materials favor (eta=2); median Hartree error ratio 0.0767 at matched storage.
4. **Disjoint confirmation** — 48 unseen materials; 48/48 wins; median CR ratio 15.016; bootstrap 95% CI [11.204, 21.461]; all safe guardrails pass.
5. **Population census** — 254 development materials, 6,350 settings, 0 failures. At (10^{-6}), 253/253 comparable materials favor QOAC-H; median 12.463x, fifth percentile 4.459x, minimum 2.444x.

## Novelty boundary

Follow `paper/QOAC_PRIOR_ART_NOVELTY_AUDIT_20261005.md`.

Do not claim generic novelty for QoI preservation, operator-aware compression, transform bit allocation, or electronic-structure compression.

The manuscript novelty is the **QSQ-qualified diagnosis-to-design loop using the exact downstream Hartree operator**, plus prospective/disjoint/full-population validation.

## Main-text architecture

Add one Results subsection immediately after the existing Fourier mechanism subsection:

    Operator-weighted error allocation converts diagnosis into a certified codec

This subsection contains:
- Hartree distortion in reciprocal space;
- the frozen (Delta_Gpropto |G|^2) law;
- the 12-material operator-blind ablation;
- the 48-material disjoint confirmation;
- the 254-material census at the primary (10^{-6}) contract.

Add a compact second paragraph or table in Results/Discussion for the tolerance census (10^{-8})–(10^{-3}).

## Figure architecture

The previous eight-figure freeze is thawed.

Preferred:
- Fig. 7 remains mechanism and gains a final design-law schematic/panel only if legible.
- New **Fig. 8**: QOAC-H design and rate-fidelity evidence.
  - a: operator weight (1/|G|^4) -> quantization step (Delta_Gpropto |G|^2);
  - b: (eta=2) vs (eta=0) matched-storage Hartree error;
  - c: 48-material disjoint confirmatory QOAC-H/best-baseline CR ratio;
  - d: full-population ratio across the six Hartree tolerances.
- Existing external-cohort figure becomes Fig. 9.

Do not merge the QOAC-H result into a tiny inset: it now supports a primary design claim.

## Abstract

Add one decisive QOAC-H number, not the entire census. Preferred abstract statistic:

> On a disjoint 48-material cohort, QOAC-H beat each material's best certified ZFP/SZ3/SPERR baseline, with a median 15.0-fold compression-ratio advantage at (10^{-6}) Hartree relative RMSE; a 254-material census retained the same direction across every comparable system.

If abstract length becomes excessive, remove a secondary existing quantitative detail rather than omitting the new primary design result.

## Discussion

Add the conceptual step:

> Qualification determines whether the ruler is usable; operator-aware coding determines where error can be placed; certification verifies the actual decoded object.

Explicitly distinguish this from:
- MGARD linear-QoI/operator-norm control;
- Jiao/QPET pointwise or scalar error-bound derivation;
- constraint-satisfaction post-processing;
- TOPIQ post-hoc uncertainty prediction.

## References to add

Required:
- Liu et al., QPET, PVLDB 18, 2440–2453 (2025), DOI 10.14778/3742728.3742739.
- Goyal, Theoretical foundations of transform coding, IEEE Signal Processing Magazine 18(5), 9–21 (2001), DOI 10.1109/79.952802.
- Chinnamsetty et al., Tensor product approximation with optimal rank in quantum chemistry, J. Chem. Phys. 127, 084110 (2007), DOI 10.1063/1.2761871.

Existing MGARD, Jiao, Lee/Banerjee, TOPIQ, Lara and PaSTRI references remain.

## Claim protection

The QOAC-H result is Hartree-specific. Do not state that:
- the same (|G|^2) law applies to Bader;
- QOAC-H preserves arbitrary QoIs;
- high raw-density Linf error is generally acceptable;
- the 254-material development census is an external-population generalization test.

The disjoint 48-material cohort is the confirmatory sample. The 254-material run is an exhaustive development-population census.
