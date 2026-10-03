# Second independent JHTDB confirmation with a bound-sized qualification panel — pre-registration (2026-10-03)

Status: **frozen before the cohort manifest is generated and before any cutout of this cohort is fetched.**
Author instruction (2026-10-03): "如果你想要跨领域这条 claim，就按上面的界选 n，比如 n=19，重新预注册一个 JHTDB 队列 … 好滴，开始吧".

## Why a new cohort

The 64-cutout pilot did not meet its primary acceptance (62/64 eligible at τ_M = 0.05). The independent
64-cutout confirmation (`../confirmatory/`, `../CONFIRMATORY_ADDENDUM.md`) met the group-size and
confidence-interval conditions but not the risk-ratio condition: rejected/eligible fresh risk 3.71
(vortex mask, τ_M = 0.01) and 3.18 (enstrophy, τ_E = 1e-4) against a required 5. Both results stay
recorded as failed.

The diagnosis is the size of the qualification panel, not the qualification logic. For a finite panel of
n exchangeable probes, P(admitted ∧ later probe ≥ τ) = p(1 − p)^n ≤ n^n/(n + 1)^(n+1), with the
maximum at p = 1/(n + 1). For n = 5 the ceiling is 6.70%. Derivative-based turbulence responses are
continuous and many cutouts sit near τ, so the five-probe panel operates close to that ceiling: in the
confirmation the joint rate was 5.64% (mask) and 3.50% (enstrophy). Electronic-density Bader responses
are far from the ceiling (0.90% at 1e-3 e).

The qualification panel is therefore sized from the bound: **n = 19**, ceiling 1.89%. The choice of n
uses only the bound. A calibration replay on the pilot and first-confirmation cutouts (128 cutouts;
resampling 19 of each cutout's 64 exchangeable probes as the panel) is recorded here as design rationale,
not evidence: median eligible/rejected ≈ 19/45 (mask) and 15/49 (enstrophy), median risk ratio ≈ 25 and
≈ 8, and the three acceptance conditions jointly met in ≈ 100% and ≈ 85% of replays.

## Cohort

- Dataset JHTDB `isotropic1024coarse`, public testing token, one request at a time, within the
  published 4,096-point limit.
- **64 new 15 × 15 × 15 cutouts**; interior 13³ voxels used for derivatives.
- Sampling namespace `QSQ-JHTDB-CONFIRM2-20261003|<index>|<salt>`, SHA-256 → frame index and
  origins exactly as in the first confirmation. Every (frame, x0, y0, z0) key used by the pilot or the
  first confirmation is forbidden.
- Sample ids `jhtdb_conf2_000 … jhtdb_conf2_063`.

## Unchanged definitions

Grid spacing 2π/1024; second-order centred differences; Q criterion; enstrophy; reference vortex mask
= exact Q above its per-cutout 90th percentile; probe amplitude ε = max|float16(u) − u|; perturbation
U(−ε, ε) on every velocity component; responses 1 − IoU of the vortex mask and relative enstrophy
change. Implementation: `../run_qsq_turbulence.py` functions `fields` and `response`, imported unchanged.

## Probes per cutout

- **Qualification panel: 19 probes**, labels 30001–30019.
- **Fresh validation: 59 probes**, labels 10000–10058.
- Stream seed for every probe: first 8 bytes (little-endian) of
  SHA-256("QSQ-JHTDB|<sample_id>|velocity|<label>"), PCG64.

Floor f = max over the 19 qualification responses; eligible iff f < τ.

## Thresholds (fixed; identical to the first confirmation)

- Primary: vortex mask, **τ_M = 0.01** (1 − IoU).
- Secondary: enstrophy, **τ_E = 1e-4** (relative).

## Acceptance (identical to the first confirmation)

For each endpoint, all three:

1. at least 10/64 eligible and at least 10/64 rejected;
2. fresh rejected-to-eligible exceedance risk ratio ≥ 5;
3. cutout-cluster bootstrap 95% interval for the fresh risk difference excludes zero
   (5,000 resamples, seed 20261003).

The primary endpoint decides the cross-domain proof-of-principle statement. The secondary endpoint,
if also met, supports transfer across two derivative-based QoIs with different response structure.

## Pre-declared secondary reports (not acceptance)

- Joint admission-and-exceedance rate over all fresh trials versus the n = 19 ceiling 1.89%.
- The same endpoints computed with the first five qualification labels only (30001–30005), as a
  within-cohort n = 5 comparison.
- Cross-QoI eligibility agreement, Cohen's κ and floor Spearman ρ.

## Interpretation lock

- No threshold, amplitude, QoI definition, panel size, seed namespace, sample count or algorithm changes
  after the manifest is written.
- The pilot and first-confirmation failures remain recorded.
- A met primary endpoint establishes a cross-domain proof-of-principle on 15³ cutouts with a
  bound-sized panel; it is not a production-scale turbulence compression benchmark and does not enter
  the electronic-density manuscript.
- Fetch failures are recorded per cutout and count against neither group; they are reported with the
  denominator.
