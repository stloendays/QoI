# QSQ probe exchangeability and the finite-panel admission bound — protocol (2026-10-03)

Status: **declared before any probe in this package is evaluated.** Author instruction (2026-10-03):
"先在本机重算一遍 floor，确认探针可交换，然后把上界写进 Methods，Results 里加一句."

## Question

QSQ admits a material–contract pair when the maximum of n qualification-probe responses is below τ.
If the n qualification probes and a later probe are exchangeable draws from the declared perturbation
family, then for every material and every response distribution

P(admitted ∧ later probe ≥ τ) = p(1 − p)^n ≤ n^n / (n + 1)^(n+1),

where p is the material's exceedance probability under the declared family (with ties, ≤). For n = 5
the bound is 6.70%. The same exchangeability gives P(later probe > max of the n) = 1/(n + 1) for
continuous responses.

On the frozen data the fresh responses exceed the frozen five-probe floor in 19.08% of 14,986 trials,
against 1/6 = 16.67%; the same excess is present when all 64 probes are re-solved in one pipeline
(WP-B `cp_probes.csv`). The frozen QSQ seeds {20260905, 1, 2, 3, 4} are used directly as PCG64 seeds
and are therefore **the same five random streams for every material**, whereas the 59 fresh streams
are material-specific (SHA-256 of material, family and label). The pooled 1/6 identity holds on
average over the draw of the qualification streams; with five shared streams the pooled statistic
is one draw, not an average over 254 independent draws.

This package (a) reproduces the frozen five-seed floor locally and (b) tests the shared-stream
explanation with a qualification panel whose streams are independent across materials.

## Population and pipeline

All 254 development materials. Frozen loader, frozen Bader settings (BaderKit 0.10.2 on-grid,
vacuum tolerance 1e-3) and frozen amplitude ε = max|float32(ρ) − ρ|, exactly as WP-B
(`analysis/extensions_20260928/WP-B/run_wpb.py`, whose input loading, source verification, worker
initialisation and reference checks are imported unchanged). Pinned stack:
`D:\Research\QoI-final4-local\venv`. Density bytes from the SHA-256-verified local cache.

## Probes per material (11 Bader solves)

1. Reference Bader on the exact field.
2. **Frozen panel F**: the five frozen QSQ seeds, `Generator(PCG64(seed)).uniform(−ε, ε)`.
3. **Independent panel I**: five labels k = 1…5 with stream seed = first 8 bytes (little-endian) of
   SHA-256("QSQ-exch-20261003|<material_id>|iid_uniform|<k>"), same amplitude and generator.

Responses are the maximum absolute per-atom re-derived Bader charge change.

## Pre-declared analyses

A. **Floor reproduction.** Recomputed max over panel F versus the frozen floor
   (`stability/stability_floor_A1.csv`); report exact matches (|Δ| ≤ 1e-9 e) and eligibility
   agreement at 1e-4, 1e-3 and 1e-2 e.
B. **Exchangeability with independent streams.** Validation set: the 59 frozen fresh responses
   (`validation/qsq_prospective/p2_fresh_probes/outcomes.csv`). Statistic: pooled fraction of fresh
   responses strictly above max(panel I); material-cluster bootstrap 95% interval (2,000 resamples,
   seed 20261003). **Accepted** if the interval contains 1/6. The same statistic for panel F is
   reported alongside.
C. **Admission bound.** For panels F and I at each τ: joint rate P(admitted ∧ fresh ≥ τ) over all
   fresh trials, compared with 6.70%; conditional fresh risk among admitted materials; coverage.
D. **Panel agreement.** Eligibility agreement and Cohen's κ between panels F and I at each τ.

No analysis, statistic or acceptance rule is changed after outcomes are observed. Failures are
recorded per material and never dropped from denominators.

## Outputs

`probes.csv`, `material_summary.csv`, `summary.csv`, `failures.csv`, `RESULTS.md`, `provenance.json`;
checkpoints in `D:\Research\QoI-ext-cache\QSQ-exch\checkpoints`.
