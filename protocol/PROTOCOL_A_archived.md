# Stability-qualified evaluation protocol — FROZEN

**Frozen: 2026-09-04, before the stability floors of the full corpus were
inspected and before any benchmark was scored against them.**

This document may not be edited to accommodate a result. If a later finding
makes the protocol look wrong, that is recorded as a separate, dated amendment
with the reason, and both versions are reported.

---

## 1. Why this protocol exists

A quantity of interest can only serve as a fidelity contract if it is
numerically well-conditioned in the regime being tested. Asking "does this
codec preserve the Bader charge to 0.01 e" presumes the Bader charge of that
system is defined to better than 0.01 e in the first place.

A pilot on 20 materials showed it often is not. Perturbing the field by a
float32 round trip — a uniform relative error near 4e-8, chemically nothing —
and re-deriving the basins produced Bader deviations spanning ten orders of
magnitude, with some slab systems exceeding 1e-2 e. For those systems no codec
can pass a 1e-2 e contract, and a benchmark that scores them is measuring the
watershed's luck.

## 2. The stability floor

For material *i*:

```
floor_i = max_a | Q_a( f32(rho_i), basins re-derived from f32(rho_i) )
                - Q_a( rho_i,      basins derived from rho_i        ) |
```

where `f32(.)` is a float64 → float32 → float64 round trip, `Q_a` is the Bader
charge of atom *a* computed as the basin-integrated density divided by the
number of voxels, and basins come from `baderkit` with `method="ongrid"`.

`floor_i` is the smallest chemical deviation the system can exhibit under a
perturbation that is, physically, nothing. It is a property of the system and
the partitioning algorithm, not of any codec.

Computed by `scripts/stability_floor.py` → `results/stability/stability_floor.csv`.

## 3. Protocol A — stability-qualified exclusion (the main-text protocol)

For a chemical threshold τ and material *i*:

| condition | label |
|---|---|
| `floor_i >= τ` | `NON_EVALUABLE_BADER_UNSTABLE` |
| `floor_i < τ` | `ELIGIBLE` |

A `NON_EVALUABLE` material is **neither a pass nor a fail**. It is excluded from
the rate–fidelity statistics at that threshold and **its exclusion is reported**.

Frozen thresholds: **τ ∈ {1e-4, 1e-3, 1e-2} e**.

For every threshold and every stratum the following must be reported alongside
any headline number:

- eligible N
- non-evaluable N
- fraction non-evaluable
- the same three, split by **bulk** and **slab**

Silently dropping a non-evaluable material is a protocol violation.

## 4. Stratification

Every main figure, main table and summary statistic reports at least:

- **overall**
- **bulk** (Materials Project crystals, n = 186)
- **slab** (NOMAD surfaces and adsorbate systems, n = 68)

If bulk and slab behave differently, an aggregate statistic alone is not
acceptable.

## 5. Sensitivity analyses (Supplement only)

Reported to show the conclusions do not hinge on Protocol A, never as the
headline:

- **S1, no exclusion.** Every material scored, floors ignored.
- **S2, floor-relative metric.** Report `dQ_i / floor_i` instead of `dQ_i`.
- **S3, inflated threshold.** `τ_eff,i = max(τ, k · floor_i)` for k ∈ {2, 5, 10}.

## 6. What the protocol deliberately does not do

- It does not tune τ to make a method look better.
- It does not exclude a material for any reason other than `floor_i >= τ`.
- It does not use the fixed-basin deviation for eligibility. The fixed-basin
  number is a diagnostic for the metric-failure analysis and is never a contract.

## 7. Statistical reporting rules

For every reported quantity: **N, median, IQR**, and p90/p95 where a tail
matters. Codec comparisons are **paired by material**, with paired bootstrap
confidence intervals. Ratios are reported as the **median of per-material
ratios**, never as a ratio of means.

## 8. Amendments

None. Any future amendment appends here with its date and reason, and results
under both versions are reported.
