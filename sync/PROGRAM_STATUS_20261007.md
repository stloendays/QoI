# QSQ / General-QOAC program status — 2026-10-08

> **Updated 2026-10-08** for manuscript revision 3 (`paper/nc-revision3-20261008` at `91d53ee`), proposed as the
> next Nature Communications authority to replace `paper/nc-reopen-20261007` at `87b3a65` (revision 2). Revision 3
> merges the QoI-preserving baselines (`research/hartree-baselines-mgard-qpet-20261007`), P3b work-function analysis
> (`research/p3b-vacuum-level-20261007`), WP-F cloud completion (`research/wpf-cloud-completion-20261007`), and housekeeping
> (`paper/nc-housekeeping-20261007`, PR #13). Joint Hartree + Bader slab evaluation is concluded across four pre-registered
> cohorts; per Author decision (2026-10-08), the manuscript states joint certification for bulk crystals only (48/48), and
> slab work stops here.

Every number is copied from a committed results file. The frozen manuscript `paper/qoac-integration-20261005`
(QSQ + QOAC-H) is unchanged and kept as the historical record. Supabase table `qoi_qoac_experiments` indexes every
entry below.

## Manuscript authority

- Branch `paper/nc-revision3-20261008` at `91d53ee` (2026-10-08; revision 3, eight main figures) is proposed as the
  authority for the Nature Communications submission, replacing `paper/nc-reopen-20261007` at `87b3a65`.
- Source: `paper/MANUSCRIPT.md` (main text, Methods, 8 figure legends, Table 1, 40 references) and
  `paper/SUPPLEMENTARY_INFORMATION.md` (Supplementary Notes 1–8, Supplementary Fig. 1); number-to-file map
  `paper/nc_reopen/SOURCE_FILES.md`.
- New text in revision 3: abstract leads with QPET; archive-scale result (WP-F completed_v2); work-function paragraph;
  Fig. 5 panels e/f.
- Word count, display items and audit record: `paper/nc_reopen/WORD_COUNT.md` (4,947 words main text + Methods, 150 words
  abstract, 1,368 words in 8 figure legends, 40 references; 8 figures and Table 1), `paper/nc_reopen/AUDIT_20261007.md`
  (0 failures, 4 warnings; passes).
- Proof build: `figures/nc/release/NC_manuscript_20261008.pdf` and `figures/nc/release/NC_manuscript_20261008.docx`
  (SHA-256 in `figures/nc/release/MANIFEST_20261008.txt`; builder `figures/nc/build_nc_manuscript.py`).

## Author decisions — resolved

Resolved in `paper/nc_reopen/DECISIONS.md` (user, 2026-10-07 and 2026-10-08):

1. The frozen manuscript is **reopened** (not a second paper); the reopened text lives on `paper/nc-revision3-20261008`.
2. Venue: **Nature Communications** (Article).
3. Main-figure parameters: figure-studio defaults (183 mm, QoI house style).
4. **Joint Hartree + Bader on slabs stopped** (Author decision, 2026-10-08): the manuscript states joint certification
   for bulk crystals only (48/48), and slab work stops here.

Defaults adopted by the assistant and flagged for author review: title; encoder per system class (closed-form law for
bulk crystals, operational allocation R3 for surfaces and for the joint contract), under which the manuscript claims
near-optimality for bulk crystals only; pre-registration register in the repository; Bader storage comparison in the SI.

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

## QoI-preserving baselines (MGARD s = −2, QPET; protocol `16e8890`)

Source: `analysis/hartree_baselines_mgard_qpet_20261007/RESULTS.md` (branch `research/hartree-baselines-mgard-qpet-20261007`,
commit `a86be8b`; run 37620406802, results `027e69a`). Evaluated on 92 cohort materials (P1 60, P3b 32) with 0 material-level
failures across 3,588 searches:

- Primary τ = 1e-6:
  - P1 (60 MP bulk): A1 median certified CR 195 vs M2 10.2 (A1/M2 median 18.2, 95% CI [15.3, 21.7], 60/60 wins),
    M-best 10.9 (A1/M-best 16.6, 95% CI [14.3, 19.5], 60/60 wins), Q 29.4 (A1/Q 6.31, 95% CI [5.53, 6.95], 60/60 wins;
    A3/Q 6.91, 95% CI [5.92, 8.15], 60/60 wins).
  - P3b (32 NOMAD slabs): A1 median certified CR 504 vs M2 21 (A1/M2 median 21, 95% CI [17.5, 27.9], 32/32 wins),
    M-best 23.1 (A1/M-best 19.6, 95% CI [15.7, 24.9], 32/32 wins), Q 46 (A1/Q 9.47, 95% CI [8.14, 12.8], 32/32 wins;
    A3/Q 11.3, 95% CI [9.62, 16.5], 32/32 wins).
- τ = 1e-4: P1 A1/M2 median 12.5 (95% CI 11.4–15.4, 60/60 wins), A1/Q 5.22 (95% CI 4.6–5.93, 60/60 wins);
  P3b A1/M2 7.97 (95% CI 5.32–11.1, 32/32 wins), A1/Q 7.56 (95% CI 5.07–9.13, 32/32 wins).
- τ = 1e-8: P1 A1/M2 median 4.69 (95% CI 4.27–5.77, 60/60 wins), A1/Q 2.33 (95% CI 2–2.85, 60/60 wins);
  P3b A1/M2 7.99 (95% CI 5.2–11.8, 32/32 wins), A1/Q 3.84 (95% CI 2.7–4.83, 32/32 wins).

## Work-function (|ΔΦ|) error on P3b slabs (protocol `47b110a`)

Source: `analysis/p3b_vacuum_level_20261007/RESULTS.md` (branch `research/p3b-vacuum-level-20261007`, commit `6f03249`;
run 37598559834, results `4946f9f`). Evaluated across 5 arms and 3 tolerances on 32 P3b slabs (480/480 streams reproduced
exactly; 27/32 slabs qualify with vacuum run >= 3.0 Å):

- Primary τ = 1e-6 (n = 27):
  - A1 closed-form law: median |ΔΦ| 0.00401 meV (P95 0.0211 meV, max 0.0452 meV, 27/27 < 1 meV, 27/27 < 10 meV).
  - A3 operational optimum: median 0.00396 meV (P95 0.0136 meV, max 0.0339 meV, 27/27 < 1 meV, 27/27 < 10 meV).
  - Baselines: A2 spectral truncation median 0.552 meV (19/27 < 1 meV), A5 operator-blind RD optimum median 0.283 meV
    (23/27 < 1 meV), A6 best of ZFP/SZ3/SPERR median 0.340 meV (19/27 < 1 meV).
- τ = 1e-4 (n = 27): A1 median 1.09 meV (27/27 < 10 meV), A3 median 1.72 meV (27/27 < 10 meV) vs A2 41.0 meV
  (2/27 < 10 meV), A5 21.2 meV (10/27 < 10 meV), A6 35.5 meV (2/27 < 10 meV).
- τ = 1e-8 (n = 27): A1 median 1.04e-5 meV, A3 median 1.53e-5 meV vs A2 0.00386 meV, A5 0.00270 meV, A6 0.00418 meV
  (all arms 27/27 < 1 meV).

## Materials Project charge-density archive estimate (WP-F completed_v2)

Source: `analysis/extensions_20260930/WP-F/results_cloud/completed_v2/RESULTS.md` (branch `research/wpf-cloud-completion-20261007`,
commit `805747f`). Frame: 415,289 objects, 8.4976 TB (MP json.gz); stratified sample n = 300 (293 succeeded, 7 failed, after
rerunning 6 never-started objects per `DEVIATIONS.md` entries 12–13):

- Primary endpoint at τ = 1e-3 e: R = 4.367 [3.637, 5.458] vs current json.gz archive — storage saving (lower 95% bound
  3.64 > 1.5) — estimated saving of 6.55 TB [6.16, 6.94].
- Format gain alone (json.gz → lossless float64 + zlib, no scientific approximation): 2.00x.
- R vs lossless float64: 2.66 [2.21, 3.27] at 1e-3 e; 1.27 [1.19, 1.38] at 1e-4 e (saving 4.90 TB); 7.87 [5.61, 12.10]
  at 1e-2 e (saving 7.55 TB).
- Earlier estimates:
  - `completed` (v1, 288 succeeded, 12 failed): R(1e-3 e) = 3.815 [3.203, 4.701], estimated saving 6.27 TB [5.84, 6.69]
    (`results_cloud/completed/RESULTS.md`).
  - `laptop_as_frozen` (243 succeeded, 57 failed): R(1e-3 e) = 1.636 [1.580, 1.698], estimated saving 3.30 TB [3.12, 3.49],
    format gain 2.05x (`results_cloud/laptop_as_frozen/RESULTS.md`).
- Execution decisions: `analysis/extensions_20260930/WP-F/DEVIATIONS.md` entries 6–13 (cloud completion, platform consistency,
  and rerun of six never-started objects).

## Joint Hartree + Bader on one stream

### Bulk crystals (QOAC-HB v2, fresh P2; protocol `8a784a4`)

| | engineering (12) | confirmation (48) | source |
|---|---|---|---|
| jointly certified at tau_B = 1e-3, 1e-4, 1e-5 e (Hartree 1e-6) | 12/12 | 48/48 | `analysis/qoac_hb_v2/results/*/RESULTS.md` (branch `research/qoac-hb-v2-20261006`) |
| joint overhead at tau_B = 1e-4 (CR_Hartree-only / CR_joint) | 1.000 | 1.000, CI [1.000, 1.000] | same |
| R3 vs best of v0.2, truncation and ZFP/SZ3/SPERR (joint) | 12/12, 1.355x | 48/48, 1.317x, CI [1.27, 1.36] | same |
| projection needed (CTP) | 0 at 1e-3 / 1e-4; 12/32 at 1e-5 | 0 / 0; 31/165 at 1e-5 | same |

**Confirmatory PASS.** Hartree-aware projection gave the same certified rate as uniform projection (ratio 1.00).

### Slabs: four pre-registered cohorts (author decision: concluded, bulk only)

1. `research/qoac-hb-slab-20261007` (`analysis/qoac_hb_slab_20261007/results/manifest/RESULTS.md`, `f5c0ac1`): 32 fresh P3b slabs.
   Confirmatory FAIL: criterion 1 13/32 (threshold >= 31/32); criterion 2 PASS (overhead median 1.000, CI [1.000, 1.011]);
   criterion 3 FAIL on count (13/32 wins, median 1.398, CI [1.306, 1.517], min 1.141). Secondary analysis on 17 with AECCAR:
   FAIL 13/17 on criterion 1. On 13 analysed slabs: 39/39 streams certified, overhead median 1.000 at 1e-3 and 1e-4, 1.009 at 1e-5,
   utility median 1.398x (13/13 wins).
2. `research/hb-slab-aeccar-cohort-20261007` (`analysis/hb_slab_aeccar_cohort_20261007/RESULTS.md`, `bab69ec`): N = 4 selected on
   AECCAR availability. Confirmatory PASS on N = 4: criterion 1 4/4; criterion 2 overhead 1.010, CI [1.008, 1.032]; criterion 3
   utility median 1.218, CI [1.185, 1.544], min 1.185, 4/4 wins; 12/12 streams certified. Diagnosis in
   `analysis/hb_slab_aeccar_cohort_20261007/diagnosis/DIAGNOSIS.md`: 4/4 data defects in published NOMAD AECCAR0 files (3 all-NaN
   files with 2,419,200, 1,975,680, 1,658,880 NaNs; 1 Fortran exponent-overflow file with values up to 8.52e196 and sum / N = -2.43e191).
   AECCAR2 files of all four are valid.
3. `research/hb-slab-nomad-wide-20261007` (`analysis/hb_slab_nomad_wide_20261007/RESULTS.md`, `981a7db`): N = 1 with pre-screened
   AECCAR inputs across full NOMAD pool (`nomad-eKxYecHu4VTk`, Ni). Confirmatory PASS on N = 1: criterion 1 1/1; criterion 2
   overhead 1.000, CI [1.000, 1.000]; criterion 3 utility 1.466, CI [1.466, 1.466], 1/1 wins; 3/3 streams certified (joint CR 428.9).
4. `research/hb-selfslab-20261007` (`analysis/hb_selfslab_20261007/RESULTS.md`, `da3ea91`): 32 self-computed VASP slabs on NUS
   cluster (density release `data-hb-selfslab-20261008`, 96 assets, 1,805,055,269 bytes). Confirmatory FAIL (criteria 1, 2, 3: fail,
   pass, pass): criterion 1 FAIL 26/32 (threshold >= 31/32; 6 misses); criterion 2 PASS (overhead median 1.011, CI [1.007, 1.014]);
   criterion 3 PASS (utility median 1.453, CI [1.353, 1.532], min 1.229, 26/32 wins).

**Author decision (2026-10-08):** the manuscript states joint certification for bulk crystals only (48/48), and slab work stops here.

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

E-field beta=1 gates (A, B, C); beta-map M2; v0.3 G2; QOAC-HB confirmatory median; B1 residual transform; P3b A-H1;
QOAC-HB slabs (32 NOMAD slabs 13/32 FAIL; 32 self-computed VASP slabs 26/32 FAIL).

## Open items

- **Full-text checks of UNVERIFIED citations** (carried over from the prior-art verification, see
  `paper/nc_reopen/PRIOR_ART_ADDENDUM.md`): the full texts of Compression Safeguards (ref. 15) and BlockMGARD (not
  cited). The norm of Lee et al.'s constraint step was resolved in revision 2 (full text read 2026-10-07; see
  `paper/nc_reopen/DECISIONS.md` and the Lee et al. row of `PRIOR_ART_ADDENDUM.md`). Cloud
  containers may have egress to publisher sites blocked, so these checks need the author's network (NUS library).
- **Zenodo DOI** in Data availability and Code availability is a placeholder, to be minted at submission.
- **Author list, affiliations, ORCID and funding** are absent from the manuscript.
- **Joint Hartree + Bader certification on slabs: resolved by Author decision (2026-10-08).** The manuscript states
  joint certification for bulk crystals only (48/48), and slab work stops here.
- **P3b near-optimality A-H1 FAIL**: on slabs A3/A1 = 1.222 against the pre-registered gate <= 1.15; the manuscript
  states near-optimality for bulk crystals only and names operational allocation as the slab encoder.
- **B3 has no confirmatory run**: the partition transcription and storage results are the 12-material P2 engineering
  cohort only (Supplementary Note 3).
- Unmerged research branches awaiting an author decision: `sync/UNMERGED_BRANCHES_20261007.md`.
