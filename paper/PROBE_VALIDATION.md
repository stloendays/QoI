# Why the stability probe itself must be validated

*Main-text section. Every number is script-generated from a committed file;
sources are named inline.*

A quantity of interest can only serve as a fidelity contract if it is
well-conditioned, and the natural way to test conditioning is to perturb the
field by an amount that is chemically nothing and watch the QoI. We did this
with the most obvious such perturbation — a float32 round trip, a uniform
relative error of about 4×10⁻⁸ — and froze the resulting eligibility protocol
before scoring any codec against it (Protocol A, 2026-09-04). That probe was
wrong, and the way it was wrong is instructive enough to be a result.

## The float32 round trip is the one perturbation a watershed cannot see

Rounding is monotone. No two voxels ever exchange rank under it, so the
steepest-ascent direction that the on-grid Bader partition follows is preserved
almost everywhere. What rounding *does* do is quantise the field onto a coarser
value grid and thereby create exact ties between neighbours — a median of 82
per material in our calibration set (`results/stability/probe_calibration.csv`).
The watershed resolves exact ties deterministically and identically in the
original and perturbed fields. The probe therefore reports a stability that
belongs to the tie-breaking rule, not to the material.

Any perturbation without this property tells a different story. On
`mp-1007755` (HfAu), Protocol A reports a floor of 5.9×10⁻¹⁰ e with zero voxels
reassigned. Uniform noise of the same L∞ reassigns 364 voxels and moves a
Bader charge by 1.6×10⁻³ e; noise at *one hundredth* of that amplitude — which
flips the order of no axis-neighbour pair at all — still reassigns 361 voxels
and moves the charge by 1.2×10⁻³ e. ZFP at a relative tolerance of 10⁻⁷, a
smaller absolute perturbation than the float32 round trip, gives 4.3×10⁻³ e.
(Table: `results/stability/PROTOCOL_A1.md` §2.)

The failure is not subtle once seen. It went unseen because the probe was
chosen for being "obviously negligible" rather than for being representative of
the perturbations a codec actually produces, and because its verdict — most
bulk crystals stable to 10⁻⁹ e — was the comfortable one.

## Scale of the correction

Replacing the probe by additive uniform noise at the same amplitude
(`scripts/stability_floor_noise.py`, single seed, all 319 systems) raises the
median floor by a factor of **8 700** (p10 1.9, p90 2.9×10⁵). The float32 probe
reassigns zero voxels in 62 % of systems; the noise probe in 1.9 %. The
non-evaluable fraction of the whole corpus becomes

| τ (e) | Protocol A (float32), archived | noise, single seed | **Protocol A.1** (max over 5 seeds) |
|---|---:|---:|---:|
| 10⁻⁴ | 23.2 % | 69.0 % | **79.9 %** |
| 10⁻³ | 7.2 % | 36.1 % | **41.4 %** |
| 10⁻² | 2.2 % | 9.1 % | **9.7 %** |

(`results/stability/eligibility_summary_a1.csv`.) At a 10⁻³ e contract,
two fifths of all systems — development and external, bulk and vacuum-containing
alike — have no Bader charge defined well enough to test. Under Protocol A we
would have scored them and attributed the resulting scatter to the codecs.

## The replacement probe was calibrated before it was frozen

Three questions were put to the noise probe on a stratified eighteen-material
subset before Protocol A.1 was written
(`scripts/probe_calibration.py`):

*Does it break the false stability?* Yes: zero exact ties created, zero
reassignments in 2/18 materials against 9/18 for float32.

*Is one seed enough?* No. Across five seeds the per-material floor spans a
median 0.47 and up to 2.4 decades, and the eligibility verdict flips with the
seed in 3/18 materials at τ = 10⁻⁴. Protocol A.1 therefore uses five
pre-registered seeds and takes the **maximum** floor — the conservative
direction, which can only move a material from eligible to excluded. On the
full corpus this matters: the five-seed maximum changes the single-seed verdict
for 35, 17 and 2 of 319 systems at τ = 10⁻⁴, 10⁻³ and 10⁻² (seed spread of the
floor: median 0.37 decades, p90 0.88, max 3.8).

*Is the amplitude a free choice?* Only partly. Over two decades of amplitude the
floor moves by a median 0.76 decades: half the materials sit on a plateau,
half scale sub-linearly. The floor is a property of the material *at a stated
amplitude*, and A.1 states it (the float32 L∞). Sensitivity to the amplitude
is reported as S4 in the Supplement.

## What this changes in the paper, and what it does not

The probe replacement does not touch the compression measurements: every codec
row in the master table is probe-independent. It changes which rows are
*admissible* at each threshold, and it changes two claims. The observation
that instability is common and unpredictable from system class, vacuum content,
grid density or atom count survives with larger numbers; the earlier
bulk/slab contrast, already falsified on external data under Protocol A, does
not reappear under A.1 (rank effect P(vacuum floor > bulk floor): development
0.564, external 0.382).

The methodological point is the one we would have made anyway, now with
ourselves as the example: a QoI-based fidelity contract needs a stability
qualification, and the qualification needs a probe that has itself been shown
to perturb the thing the QoI depends on. A probe that is order-preserving
tests nothing about an algorithm that depends only on order.
