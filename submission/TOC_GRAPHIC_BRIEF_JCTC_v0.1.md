# JCTC Table-of-Contents Graphic Brief

**Version:** v0.2 — 2026-09-06  
**Purpose:** original graphical summary for the JCTC Table of Contents.

## Working production specification

Use an ACS TOC working canvas of **3.25 in wide × 1.75 in high**. The final upload specification should still be checked in the live ACS Publishing Center on submission day.

Submission label/caption:

**For Table of Contents Only**

The graphic must be an original creation, remain legible at final reduced size, and avoid paragraph-length text.

## Core visual message

A small and matched pointwise reconstruction error can lead to different chemical errors when the reconstructed field changes the Bader partition itself.

The graphic should communicate a mechanism-consistent workflow without presenting the observational regression as formal causality:

`matched realized L∞ -> different basin migration -> different ΔQ_Bader`

A secondary visual cue should indicate that a Bader-charge contract is only meaningful when the reference observable is numerically resolvable.

## Recommended composition

Use a clean horizontal three-stage layout that can be understood at phone-screen scale.

### Left — matched reconstructed electron-density fields

Show one compact reference density motif feeding two reconstructed variants. The two variants should have comparable pointwise magnitude but visibly different local error texture.

Minimal label:

**matched realized L∞**

Do not imply that equal nominal codec tolerance means equal realized error.

### Center — Bader partition response

Overlay simple basin boundaries or watershed-style regions on both reconstructed variants. One branch keeps boundaries relatively stable; the other shows a small but clear boundary migration near an interatomic region.

Minimal label:

**basin migration**

Avoid contour-tree or Morse–Smale notation because the paper does not claim preservation or failure of those exact topological objects.

### Right — downstream chemical fidelity

Show two stylized atomic charge readouts or compact charge-difference bars. The branch with stronger basin migration maps to the larger downstream Bader error.

Minimal label:

**ΔQ_Bader**

A small gate below the output may read:

**resolvable?**

This gate is secondary; domain migration remains the main visual story.

## Text budget

Preferred visible text: three labels.

- matched realized L∞
- basin migration
- ΔQ_Bader

Optional fourth label:

- resolvable?

Do not place the paper title, codec names, detailed numerical values, or explanatory sentences inside the TOC graphic.

## Visual style

- original vector-style scientific artwork;
- white or transparent background;
- one consistent electron-density visual language across both reconstructions;
- basin boundaries visually distinct from density magnitude;
- high contrast that survives reduction and grayscale viewing;
- minimal 3D perspective;
- no screenshots, journal logos, publisher branding, or copyrighted external imagery.

## Scientific guardrails

The graphic must **not** imply:

- that equal nominal tolerance means equal realized error;
- that codec identity is itself a causal variable;
- that all Bader error in all 254 materials is directly decomposed into domain migration;
- that Protocol A.1 defines an intrinsic amplitude-free material property;
- that the work proposes a new compressor.

## Evidence represented by the graphic

- Re-derived Bader error exceeds fixed-basin error in 99.7% of 4,627 successful base-ladder reconstructions.
- At the 10^-3 e stability contract, conservative realized-L∞-matched comparisons retain approximately twofold codec-associated Bader-error differences.
- In material-controlled models, adding basin reassignment reduces codec multipliers from approximately 2x to approximately 1x, whereas global electron-count deviation does not.
- Direct domain/integrand decomposition is currently claimed for the representative 12-material mechanism set.

## Final visual acceptance test

Before upload:

1. view the graphic at exactly 3.25 × 1.75 in;
2. view it on a phone without zooming;
3. verify all labels remain legible;
4. verify the scientific story can be understood without the manuscript caption;
5. verify no element implies same-nominal matching or universal codec ranking;
6. export a publication-quality vector or high-resolution file accepted by the live ACS portal.
