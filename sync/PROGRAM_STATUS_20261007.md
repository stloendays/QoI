# QSQ / General-QOAC program status — 2026-10-07

Every number is copied from a committed results file. The frozen manuscript `paper/qoac-integration-20261005`
(QSQ + QOAC-H) is unchanged. Supabase table `qoi_qoac_experiments` indexes every entry below.

## Prospectively confirmed (protocol and predictions committed before execution; never-used materials)

| claim | P1: 60 fresh MP bulk | P3b: 32 fresh NOMAD slabs | source |
|---|---|---|---|
| Gain of operator-aware allocation predicted before compression (5 operators) | median error 2.4%, Spearman 0.978 (300 pairs) | 2.9%, 0.979 (160 pairs) | `analysis/general_qoac_law/results/RESULTS.md` |
| Operator metric essential under optimal allocation (A3/A5) | 2.12x, 60/60 | 3.43x, 32/32 | same |
| Closed-form law vs equal-search ZFP/SZ3/SPERR (A1/A6), Hartree 1e-6 | 10.2x, 60/60 | 18.5x, 32/32 | same |
| Closed-form law vs equal-search spectral truncation (A1/A2) | 1.32x, 52/60 | 1.41x, 27/32 | same |
| Closed-form law near the operational optimum (A3/A1 <= 1.15) | **1.105 (pass)** | **1.222 (fail)** | same |

Gain predictions per operator (P1 / P3b, G_pred vs G_obs): gradient 1.014/1.011 and 1.012/1.015; Laplacian 1.040/1.042
and 1.031/1.047; Hartree field 1.151/1.149 and 1.164/1.165; Hartree potential 2.72/2.61 and 3.55/3.14; Gaussian
(sigma = 0.5 A) 17.6/12.1 and 22.0/15.3. The Gaussian gain is overstated by about 1.45x in both cohorts.

## Confirmatory (earlier program, frozen)

- QOAC-H v0.2: 48/48, 15.0x over best certified ZFP/SZ3/SPERR (frozen ladders); 254-material census 253/253.
- Strongest baselines (48): 1.56x over spectral truncation (45/48); MGARD 19.4x behind; stored V_H 19.4x behind.
- QOAC-B2 (38): Bader exact, zero reassignment, 1.86x.

## Engineering, retrospective, descriptive

- v0.3 RDO engineering (12): G2 NO-GO (1.10 < 1.20); G3 GO (A3/A5 2.21).
- Gain-predictor retrospective calibration (12): Hartree 0.083 vs 0.077; E-field 0.790 vs 0.806.
- B3 real materials (12 fresh P2): the Henkelman partition transcription matches the compiled binary in 11/11. A
  partition-faithful AECCAR gives 12/12 zero reassignment at 17x the size of a lossless label map. The label map
  (12.9 kB median) reproduces binary charges in 12/12.
- QOAC-HB joint (old 50): 50/50 jointly certified; confirmatory median 1.224 < 1.25 (FAIL).

## NO-GO / FAIL record (provenance)

E-field beta=1 gates (A, B, C); beta-map M2; v0.3 G2; QOAC-HB confirmatory median; B1 residual transform; P3b A-H1.

## Running / next

- QOAC-HB v2 engineering on fresh P2 (CI run 37495653659). Protocol `8a784a4` covers HAP/CTP, tau_B = 1e-3/1e-4/1e-5
  and the Hartree-only overhead. If its gates pass, the 48-material confirmation follows.
- Story / claim–evidence drafts: `paper/program-story-draft-20261007` (two alternative drafts) still need P3b
  numbers.
- Prior-art: `research/prior-art-program-20261006` (+ verification addendum); full-text check of UNVERIFIED citations
  pending.
- Author decisions pending: reopen the frozen manuscript or write a second paper; venue; whether near-optimality is
  claimed for bulk only.
