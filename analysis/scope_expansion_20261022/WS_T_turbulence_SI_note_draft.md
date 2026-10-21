# WS-T draft — SI note: QSQ beyond electronic densities (turbulence)

Status: **draft for the owner's decision.** It is not linked from the manuscript. The rev5 scope addendum
(`paper/WORKFLOW_SCOPE_ADDENDUM_20261003.md`) excludes cross-domain generality; this text only makes the
option cheap to take up. Every number is copied from the files named in brackets on branch
`ext/turbulence-n19-20261003`.

---

## Supplementary Note X. Qualification transfers to turbulent velocity fields when the panel is sized from its risk bound

**Why test it.** QSQ is defined on a measurement contract (stored field, downstream operator, tolerance), not
on electronic structure. We therefore ran it on a domain that changes all three:

- the stored object is a three-component velocity field;
- the operator is spatial differentiation followed by quadratic and threshold operations;
- the source is DNS of forced isotropic turbulence (JHTDB `isotropic1024coarse`).

Each sample is a 15³ cutout with a 13³ interior. There are two QoIs:

- the vortex mask (Q criterion above its per-cutout 90th percentile; response 1 − IoU, τ_M = 0.01);
- the enstrophy (relative change, τ_E = 1e-4).

The probe is uniform noise at the float16 round-trip amplitude
[`WP-J-turbulence/PROTOCOL.md`, `confirmatory_n19/PROTOCOL.md`].

**What failed first.** Both earlier tests are kept as failures.

- The five-probe pilot did not meet its acceptance: 62/64 cutouts were eligible at τ_M = 0.05
  [`WP-J-turbulence/RESULTS.md`].
- An independent 64-cutout confirmation with the same five-probe panel met the group-size and
  confidence-interval conditions. It missed the risk-ratio condition, with rejected/eligible fresh risk of
  3.71 (mask) and 3.18 (enstrophy) against the required 5 [`confirmatory/RESULTS.md`].

**Why it failed: a finite-panel ceiling.** For n exchangeable probes, the probability that a contract is
admitted although a later probe exceeds τ is

    p(1 − p)^n ≤ n^n / (n + 1)^(n+1),

with the maximum at p = 1/(n + 1).

- For n = 5 the ceiling is 6.70%.
- Derivative-based turbulence responses are continuous, and many cutouts sit near τ, so the five-probe
  panel ran close to that ceiling: the joint rates were 5.64% and 3.50% in the first confirmation.
- Bader responses of electronic densities sit far below it (0.90% at 1e-3 e)
  [`confirmatory_n19/PROTOCOL.md`].

**Second confirmation.** The panel was sized from the bound alone: n = 19, ceiling 1.89%. The protocol was
registered before the cohort was drawn: 64 new cutouts, with every earlier frame/origin key forbidden.
Definitions, thresholds and acceptance stayed unchanged. Both endpoints met acceptance
[`confirmatory_n19/RESULTS.md`]:

| endpoint | eligible / rejected | fresh risk (eligible vs rejected) | RR | risk-difference 95% CI | joint rate (bound) |
|---|---|---|---|---|---|
| vortex mask, τ_M = 0.01 | 22 / 42 | 2.311% vs 40.799% | 17.7 | [0.2943, 0.4795] | 0.79% (1.89%) |
| enstrophy, τ_E = 1e-4 | 15 / 49 | 1.921% vs 25.666% | 13.4 | [0.1893, 0.2873] | 0.45% (1.89%) |

**Reading.**

1. The qualification logic transfers unchanged to a vector field with a differential operator.
2. The panel size is not a free parameter. It follows from the admitted-but-exceeding rate a user will
   accept, through the closed-form ceiling above. Electronic densities happen to sit far from the n = 5
   ceiling.
3. **Disclosure.** The successful cohort came after two documented failures and a change of n. n was chosen
   from the bound, not from outcomes. A calibration replay on the earlier cutouts is reported in the
   protocol as design rationale, not as evidence.

---

## Options for the owner (not decided here)

- **(a)** Keep generality out (rev5 status quo).
- **(b)** Add this note to the SI, plus one Discussion sentence. That sentence costs words; the main text has
  8 words of headroom, so it needs a cut elsewhere.
- **(c)** The ceiling is already in rev5 SI 1.5 ("Finite-panel admission bound", with n = 5, 10, 19, 37).
  The turbulence result would be its first use as a *design rule*: choose n from the admitted-but-exceeding
  rate you accept. So the note can point to SI 1.5 instead of re-deriving the bound, which shortens it to
  roughly the table plus the disclosure paragraph.
