# QOAC v0.3 — operator-metric rate-distortion-optimal allocation (engineering protocol)

Freeze date: 2026-10-06. Frozen before any v0.3 or bisection arm is run on any material.

## Motivation (from frozen evidence)

- E-field diagnosis: the per-shell Lagrangian slopes of the v0.2 power-law allocation are unequal (implied
  exponent 1.56 vs 1), and ~90% of orbits sit in the dead zone, so the high-rate law is not
  finite-rate optimal.
- Strongest-baseline study: v0.2 beats spectral truncation only 1.56x; truncation is the dominant mechanism
  over pointwise codecs.
- All frozen comparisons used a 25-point alpha ladder (2.15x per rung), so the certificate is overshot by up to
  a rung.

## Codec

`codec_qoac_v03.py`: the v0.2 Hermitian-orbit topology; Delta_k = mult_s * u_k with a per-shell multiplier
from a 2^(1/4) ladder or the shell dropped. Each shell's exact (zlib bytes, operator distortion) curve is
computed; a Lagrangian selection (bisection on lambda plus a feasibility-preserving greedy polish) meets
both the conservative-Nyquist (upper bound on historical) and the Nyquist-safe certificate with a 0.995
margin. Every reported stream is decode-verified with the frozen `hartree_error_metrics`.

## Population

The 12 QOAC-H engineering materials (`analysis/operator_aware_codec_hartree/results/PILOT_MANIFEST.csv`).
Development only.

## Arms (all certified by decode: historical and Nyquist-safe Hartree relative RMSE < tau)

| arm | description | search |
|---|---|---|
| A0 | v0.2 beta=2, frozen 25-point alpha ladder | ladder (frozen reference) |
| A1 | v0.2 beta=2 | continuous alpha bisection on spectral distortion |
| A2 | T1 spectral truncation, q_c in {k/32, k=1..32} | continuous alpha bisection per q_c, best q_c |
| A3 | **v0.3 RDO, operator prior u = w^{-1/2}, Hartree metric** | Lagrangian + polish |
| A4 | v0.3 RDO, flat prior, Hartree metric | Lagrangian + polish |
| A5 | v0.3 RDO operator-blind control: flat prior, L2 selection metric, no polish; lambda chosen only so that the Hartree certificate holds | Lagrangian |
| A6 | best of ZFP / SZ3 / SPERR | absolute-tolerance bisection with decode-verified Hartree errors |

Bisection arms: 60 iterations in log space; the reported row is the highest-CR evaluated point passing the
decode-verified certificate. CR = 8 * npoints / total stream bytes, including all headers.

Tolerances: tau_H in {1e-4, 1e-6, 1e-8}; primary 1e-6.

## Engineering gates (primary tau = 1e-6)

- **G1 — certification:** A3 certified in 12/12.
- **G2 — utility over the strongest fair-search competitors:** R3 = CR_A3 / max(CR_A1, CR_A2) > 1 in
  >= 10/12, and median R3 > 1.20.
- **G3 — the operator metric remains essential under optimal allocation:** median CR_A3 / CR_A5 > 2.0.

Descriptive: A0 vs A1 (ladder granularity), A4 vs A3 (value of the operator prior given RDO), A6 (fair-search
pointwise codecs), the secondary tolerances, encode/decode time.

## Continuation (frozen now; executed only if G1–G3 pass)

A confirmatory protocol on the fresh never-used populations (WS-0: P1 bulk 60 confirmatory; P3 slab 60
confirmatory if available) with the same arms and these criteria at tau = 1e-6:
1. all materials analyzable, zero pipeline failures, A3 certified for all;
2. R3 > 1 in >= 80% of materials;
3. median R3 > 1.15 and fixed-seed (20261006, 10,000 resamples) bootstrap 95% CI lower bound > 1.05;
4. median CR_A3 / CR_A6 > 5.

No codec parameter (ladder, margin, shells, zlib level, prior) may change between engineering and
confirmation.
