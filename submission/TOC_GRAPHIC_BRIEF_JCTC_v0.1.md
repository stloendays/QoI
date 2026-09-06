# JCTC Table-of-Contents Graphic Brief

**Version:** v0.1 — 2026-09-06  
**Purpose:** original graphical summary for the JCTC Table of Contents.

## Core visual message

A small pointwise reconstruction error can produce a much larger chemical error when the reconstructed field changes the Bader partition itself.

The graphic should communicate one causal-looking workflow without claiming formal causality:

`matched / bounded field error -> different Bader-domain migration -> different Bader charge error`

A secondary visual cue should indicate that a Bader-charge contract is only meaningful when the reference observable is numerically resolvable.

## Recommended composition

Use a clean horizontal three-stage layout, designed to remain legible at TOC scale.

### Left — electron-density reconstruction

Show one compact electron-density field or isosurface motif split into two reconstructed variants. A small common bracket or badge above them reads:

**matched L∞**

The two reconstructions should have similar overall amplitude but visibly different local error texture. Do not imply that one field has a larger pointwise bound.

### Center — Bader partition response

Overlay simple basin boundaries or watershed-style regions on each reconstruction. One reconstruction keeps boundaries relatively stable; the other shows a small but clear boundary migration around an interatomic region.

Minimal label:

**basin migration**

Avoid formal contour-tree or Morse–Smale symbols because the manuscript does not claim preservation or failure of those exact topological objects.

### Right — downstream chemical fidelity

Show two stylized atoms with Bader-charge labels or a compact charge-difference indicator. The reconstruction with stronger basin migration should map to larger `ΔQ_Bader`.

Minimal label:

**ΔQ_Bader**

Optionally include a small gate/check mark beneath the output:

**resolvable?**

This should remain secondary; the main visual story is domain migration.

## Text budget

Keep visible text to at most four short labels:

- matched L∞
- basin migration
- ΔQ_Bader
- resolvable?  (optional)

Do not place the manuscript title or long explanatory sentences inside the graphic.

## Visual style

- Original vector-style scientific artwork, not screenshots from papers or software.
- White or transparent background.
- One consistent electron-density visual language across both reconstructions.
- Basin boundaries should be visually distinct from density magnitude.
- Use high contrast that survives reduction to TOC size and grayscale conversion.
- Avoid decorative 3D effects that obscure the scientific mechanism.
- No journal logo, Nature-style masthead, or copyrighted external imagery.

## Scientific guardrails

The graphic must **not** imply any of the following:

- that equal nominal tolerance means equal realized error;
- that codec identity is itself a causal variable;
- that all Bader error in all 254 materials is proven to arise from domain migration;
- that Protocol A.1 defines an intrinsic, amplitude-free material property;
- that the study proposes a new compressor.

## Current evidence represented by the graphic

- Re-derived Bader error exceeds fixed-basin error in 99.7% of 4,627 base-ladder successful reconstructions.
- At the 10^-3 e stability contract, conservative realized-L∞-matched comparisons retain approximately twofold codec-associated Bader-error differences.
- In material-controlled models, adding basin reassignment reduces the codec multipliers from approximately 2x to approximately 1x, whereas global electron-count deviation does not.
- Direct domain/integrand decomposition is currently claimed only for the representative 12-material mechanism set.

## Production note

JCTC currently requires a graphical summary for the Table of Contents. Prepare the final art to the current ACS/JCTC upload specification and verify dimensions in the submission portal immediately before upload; a compact ACS TOC aspect ratio around 3.25 in × 1.75 in is an appropriate working canvas for the draft.
