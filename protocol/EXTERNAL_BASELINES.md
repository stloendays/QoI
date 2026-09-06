# External baseline closure: BQB and den2bin

Date: 2026-09-04.

## Summary

| | BQB (Brehm & Thomas 2018) | den2bin (Filot) |
|---|---|---|
| Runnable here (Windows, no compiler, no WSL) | **YES** — prebuilt Win64 binary, no dependencies | **NO** — source only, needs C++/CMake/Boost/OpenMP |
| Fair head-to-head against ZFP / SZ3 / SPERR | **NO** | **NO** |
| Ratio denominator | ASCII Gaussian cube, 13.167 B/value | ASCII CHGCAR, 18.2 B/value |
| Headline converted to float64 | 35:1 → **21.3:1** | 10–12:1 → **4.4–5.3:1** |
| Disposition | related work; optional single-frame supplementary row | related work only; excluded |

---

## 1. Correction of record: our earlier BQB conversion was wrong

An earlier note in this project converted BQB's 35:1 to "about 7.8x against
float64" by dividing by a CHGCAR-text denominator of ~36 B/value. **Both halves
of that were wrong.**

- BQB's reference format is the **Gaussian cube**, not CHGCAR.
- The ~36 B/value figure came from dividing a whole CHGCAR file by its grid
  count, which includes the header and the augmentation-occupancy block.

Measured directly on a real CHGCAR (`Rh-CeO2` bulk CeO2, 72³ grid, grid block
isolated between the dimension line and the `augmentation` marker):

```
grid block 6,793,116 bytes / 373,248 values = 18.200 bytes per value
```

That is CHGCAR. The Gaussian cube format is normatively `(6E13.5)`
(Gaussian `cubegen` spec, matched by CP2K's `cubecruncher.f90`), giving
`13 + 1/6 = 13.1667` B/value with LF line endings.

**The corrected conversion is therefore 35 × 8 / 13.1667 = 21.3:1 against
float64, or 3.01 bits per grid value** — not 7.8:1. The earlier figure
understated BQB by a factor of 2.7 and must not be cited.

## 2. Conversion rules to be used from here on

Report **bits per grid value**. It carries no denominator and is immune to this
entire class of error. Convert to a ratio only when a reviewer asks.

```
bits_per_value = 8 * B_ref / R_reported
R_vs_float64   = R_reported * (8 / B_ref)
```

| Reference format | B_ref (bytes/value) | factor to float64 | source |
|---|---:|---:|---|
| Gaussian cube `(6E13.5)`, LF | 13.1667 | ×0.6076 | Gaussian cubegen spec; normative |
| ASCII CHGCAR | **18.200** | ×0.4396 | **measured here**, not assumed |
| float32 | 4 | ×2.0 | — |
| float64 | 8 | ×1.0 | — |

VASP does not publish a CHGCAR format descriptor — the wiki only guarantees
space separation — so 18.200 is a measurement of our own files and should be
re-measured if the corpus changes writer (pymatgen and VASP differ).

---

## 3. BQB

### 3.1 What 35:1 is measured against

The paper's abstract states it against text formats explicitly: "around 15:1 for
typical position trajectories **in the XYZ format**. For volumetric data
trajectories **in Gaussian Cube format** … around 35:1".

Two independent confirmations that the reference is text, not binary:

- The `bqbtool` manual sets working precision in **significant digits**, default
  5, "as specified in the original Gaussian Cube format", and defines lossless
  as "bitwise identical to the original trajectory" — i.e. to the cube text.
- On raw binary input the manual states the ratio "will be very similar to
  bzip2", and that there is "no significant reason to use bqbtool instead of
  bzip2 for compressing binary files".

So BQB's headline is inseparable from a text denominator. Note also that the
cube's `E13.5` rendering is already a ~1e-5 to 1e-6 relative truncation of the
float64 density: **BQB is lossless with respect to an already-lossy rendering.**

### 3.2 Every reported ratio

| Ratio | Data | Reference | Mode |
|---|---|---|---|
| ~35:1 | volumetric density, **MD trajectory** | ASCII cube | lossless-to-text, spatial + temporal |
| ~15:1 (abstract) / up to 20:1 (site) | atom positions | ASCII XYZ | lossless-to-text |
| ~5:1 | volumetric via bzip2/xz, their own baseline | ASCII cube | lossless |
| ≈ bzip2 | arbitrary binary | the binary itself | lossless |

**No single-frame or static-density ratio is published anywhere.** That gap is
stated rather than interpolated.

### 3.3 Lossless only?

Nominally lossless, with two coarse decade-quantized knobs: `-vsigni N`
(significant digits, default 5, max 9 — effectively a pointwise *relative*
control) and `-veps E` (values below 10⁻ᴱ truncated to zero, which the manual
concedes "is no longer lossless"). **There is no absolute L∞ target, no PSNR
target, no rate target.** BQB cannot be placed on a rate–distortion curve
against error-bounded compressors; only nine discrete relative-precision points
exist.

### 3.4 Dependence on temporal coherence

Substantial, and stated by the authors: the algorithm "uses temporal
extrapolation techniques to reach high compression ratios", and key frames
"are larger, because they can't exploit knowledge on frame history".

CP2K's `E_DENSITY_BQB` exposes this directly:

> **HISTORY** — "Controls how many previous steps are taken into account for
> extrapolation in compression. Use a value of 1 to compress the frames
> independently." Default: **10**.

A single static density is the degenerate case — one key frame, `HISTORY 1`,
temporal extrapolation inoperative. **That is not the configuration under which
35:1 was measured.**

### 3.5 Applicability

Mechanically applicable to a one-frame cube. **Not applicable to CHGCAR**: the
tool reads Gaussian cube only for volumetric input. Converting CHGCAR → cube
would change the denominator from 18.2 to 13.17 B/value, truncate precision from
~12 significant digits to ~5, and discard the PAW augmentation occupancies — so
it would no longer be the same bytes the other compressors were given.

Documented limitation, CP2K docs: "Currently does not work with changing cell
vector (NpT ensemble)." Irrelevant to static fields but worth one sentence.

### 3.6 Runnability

**Runnable.** A prebuilt Win64 executable is published
(`brehm-research.de/files/bqbtool-win64-201208.zip`, Dec 2020, ~1.1 MiB); the
manual states it "does not require any external libraries". No Python binding
exists — MDAnalysis issue #2107 has had no activity since 2018.

### 3.7 Verdict

**Not a fair head-to-head**, for four independent reasons, any one sufficient:

1. **Denominator mismatch** — 35:1 is against 13.17 B/value text; our ratios are
   against 8 B/value float64. Quoting side by side inflates BQB by 1.65×.
2. **Different task** — 35:1 requires temporal extrapolation across MD frames;
   our benchmark is single static fields, where CP2K sets `HISTORY 1` and the
   authors warn ratios drop. No single-frame number is published.
3. **Different error semantics** — lossless-to-text with nine discrete relative
   precisions; it cannot accept an L∞ target.
4. **The authors' own disclaimer** — on binary input, "very similar to bzip2".

**Disposition.** Cite in related work as the state of the art for lossless
archival of cube-format AIMD trajectories. Quote 35:1 *with* its qualifier and
*with* the 21.3:1 float64 equivalent in the same sentence. Declare it out of
scope for single-static-field error-bounded comparison.

**Optional supplementary row.** Because it *is* runnable, one honest data point
would close the reviewer question "why not BQB?" with data rather than argument:
convert one static density to cube, run `bqbtool compress voltraj -vsigni 5`,
report **bits per value**, and label it explicitly *"lossless to ASCII cube,
single frame, no temporal model, not error-bounded."* It caps precision near
1e-5 relative, so it belongs beside the SZ3 rel-1e-5 point, not on the lossless
line. **Not yet run.**

---

## 4. den2bin

### 4.1 State

Last push **2017-12-31**, no releases, no tests, no CI, no publication, 4 stars.
The documented install path is a personal Debian APT repo using `apt-key`, a
mechanism removed in Debian 12. Treat as dead.

### 4.2 What it does

VASP CHGCAR/LOCPOT only, no cube. Normalizes the grid to [-0.5, 0.5], tiles into
`blocksize³` blocks, applies a 3D DCT, and **keeps coefficients by index-sum
cutoff** `i + j + k < q` — a triangular-corner truncation, not a magnitude
threshold and not a quantizer. Survivors are stored as **raw float32** with no
quantization, then bzip2'd. It **discards the PAW augmentation occupancies**, so
a round trip is not a faithful CHGCAR.

### 4.3 Error guarantee

**None.** The only feedback is a post-hoc **mean absolute error** per grid point.
That is the wrong statistic for a Bader contract: a grid-mean absolute error is
dominated by the large near-empty volume and conceals L∞ excursions at the
nuclear cusps, which is exactly where basin boundaries and charge integration
live. Block-DCT corner truncation additionally injects blocking artifacts and
Gibbs ringing at density maxima, with nothing bounding either.

### 4.4 Reported ratios, and what they really mean

Both are against ASCII CHGCAR:

- "10–12:1 lossless" → **4.4–5.3:1 vs float64**. And it is **not lossless**: the
  mode stores float32 (~7 significant digits) where CHGCAR carries ~12. Listing
  it as lossless beside SZ3-lossless would be a factual error.
- "up to 250:1 lossy" → **110:1 vs float64**, but only at `-q ≤ 2`. At the
  README's own recommended `-b 4 -q 4`, 20 of 64 coefficients survive = 1.25
  bytes/gridpoint = **6.4:1 against float64 before bzip2**.

### 4.5 Verdict

**Not runnable** here: source-only C++ needing CMake, Boost, libbz2, glm, tclap
and OpenMP, with no Windows binary, no conda and no pip package.

**Not comparable even if built**, for five reasons: no error control of any kind;
the only error feedback is the wrong statistic; its "lossless" mode is float32;
block-DCT ringing is unbounded exactly at density peaks; and it drops the
augmentation occupancies.

**Disposition.** Excluded from the benchmark. One sentence in related work: an
early domain-specific block-DCT approach to CHGCAR compression, unpublished,
unmaintained since 2017, offering a quality knob with no error guarantee — which
is precisely the gap error-bounded compressors fill. The exclusion is
motivation, not an omission.

**Adjacent.** The same author's maintained successor `den2obj` reads CHGCAR,
PARCHG and cube, but its compression is lossless container compression rather
than error-bounded, and it is documented Linux-only with no Windows binary. Not
a substitute baseline; worth a citation.

---

## 5. Two rules this closure imposes on the manuscript

1. **Never place a text-referenced ratio beside a binary-referenced one without
   conversion.** BQB's 35:1 and SZ3's ratios differ by a 1.65× denominator
   artefact before any algorithm is compared. Standardise on bits per grid value.
2. **Neither tool may appear as "lossless" in a table with SZ3-lossless.** BQB is
   lossless to a ~5-significant-digit ASCII rendering; den2bin is lossless to
   float32. Both belong on the relative-error axis, not the lossless line.
