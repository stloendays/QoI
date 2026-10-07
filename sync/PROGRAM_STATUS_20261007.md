# QSQ / General-QOAC program status — 2026-10-07

Every number is copied from a committed results file. The frozen manuscript `paper/qoac-integration-20261005`
(QSQ + QOAC-H) is unchanged and kept as the historical record. Supabase table `qoi_qoac_experiments` indexes every
entry below. Status updated 2026-10-07 after the Nature Communications reopening (branch
`paper/nc-housekeeping-20261007`).

## Manuscript authority

- Branch `paper/nc-reopen-20261007` at `6d54d94` (2026-10-07 08:26 +08:00) is the authority for the Nature
  Communications submission.
- Source: `paper/MANUSCRIPT.md` (main text, Methods, 7 figure legends, Table 1, 40 references) and
  `paper/SUPPLEMENTARY_INFORMATION.md` (Supplementary Notes 1–8, Supplementary Fig. 1); number-to-file map
  `paper/nc_reopen/SOURCE_FILES.md`.
- Proof build: `figures/nc/release/NC_manuscript_20261007.pdf` and `figures/nc/release/NC_manuscript_20261007.docx`
  (SHA-256 in `figures/nc/release/MANIFEST_20261007.txt`; builder `figures/nc/build_nc_manuscript.py`).
- Word count, display items and audit record: `paper/nc_reopen/WORD_COUNT.md`, `paper/nc_reopen/AUDIT_20261007.md`.

## Author decisions — resolved

Resolved in `paper/nc_reopen/DECISIONS.md` (user, 2026-10-07):

1. The frozen manuscript is **reopened** (not a second paper); the reopened text lives on `paper/nc-reopen-20261007`.
2. Venue: **Nature Communications** (Article).
3. Main-figure parameters: figure-studio defaults (183 mm, QoI house style).

Defaults adopted by the assistant and flagged for author review in the same file: title; encoder per system class
(closed-form law for bulk crystals, operational allocation R3 for surfaces and for the joint contract), under which the
manuscript claims near-optimality for bulk crystals only (the earlier open question); pre-registration register in the
repository; Bader storage comparison in the SI.

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

## Joint Hartree + Bader on one stream (QOAC-HB v2, fresh P2; protocol `8a784a4`)

| | engineering (12) | confirmation (48) | source |
|---|---|---|---|
| jointly certified at tau_B = 1e-3, 1e-4, 1e-5 e (Hartree 1e-6) | 12/12 | 48/48 | `analysis/qoac_hb_v2/results/*/RESULTS.md` (branch `research/qoac-hb-v2-20261006`) |
| joint overhead at tau_B = 1e-4 (CR_Hartree-only / CR_joint) | 1.000 | 1.000, CI [1.000, 1.000] | same |
| R3 vs best of v0.2, truncation and ZFP/SZ3/SPERR (joint) | 12/12, 1.355x | 48/48, 1.317x, CI [1.27, 1.36] | same |
| projection needed (CTP) | 0 at 1e-3 / 1e-4; 12/32 at 1e-5 | 0 / 0; 31/165 at 1e-5 | same |

**Confirmatory PASS.** Hartree-aware projection gave the same certified rate as uniform projection (ratio 1.00).

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

## Open items

- **Full-text checks of UNVERIFIED citations** (carried over from the prior-art verification, see
  `paper/nc_reopen/PRIOR_ART_ADDENDUM.md`): the norm of Lee et al.'s constraint step (ref. 12, cited for the
  minimum-norm basin correction); the full texts of Compression Safeguards (ref. 15) and BlockMGARD (not cited). Cloud
  containers may have egress to publisher sites blocked, so these checks need the author's network (NUS library).
- **Zenodo DOI** in Data availability and Code availability is a placeholder, to be minted at submission.
- **Author list, affiliations, ORCID and funding** are absent from the manuscript.
- **Joint Hartree + Bader certification is shown on bulk crystals only** (P2, 48/48). A slab confirmation is running on
  branch `research/qoac-hb-slab-20261007` (not yet on `origin` at the time of this update).
- **P3b near-optimality A-H1 FAIL**: on slabs A3/A1 = 1.222 against the pre-registered gate ≤ 1.15; the manuscript
  states near-optimality for bulk crystals only and names operational allocation as the slab encoder.
- **B3 has no confirmatory run**: the partition transcription and storage results are the 12-material P2 engineering
  cohort only (Supplementary Note 3).
- Unmerged research branches awaiting an author decision: `sync/UNMERGED_BRANCHES_20261007.md`.
