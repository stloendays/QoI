# Research branches — decision list for the author (updated 2026-10-08)

Ten branches on `origin` hold completed or prepared work evaluated during the project. Status updated 2026-10-08
for manuscript revision 3 (`paper/nc-revision3-20261008` at `91d53ee`), which merged three research branches and
closed the slab program per author decision (2026-10-08). Numbers are copied from the result files on each branch
(paths below are on that branch).

| branch (tip) | content | headline | merged by revision 3? | suggested default |
|---|---|---|---|---|
| `research/qoac-b3-full-50-census-20261005` (`142ddc8`) | compiled-partition B3: lossless Bader partition map, 12-material engineering, 50-material descriptive census; unified framework note | census 50/50 exact; map 210.66x smaller than lossless AECCAR; complete archive 92.52x smaller, 50/50 | no (partly superseded) | keep unmerged; optional SI sentence |
| `research/qoac-electric-field-20261005` (`d3255fa`) | the B3 census branch plus a QOAC-E (electric-field) design, runner and workflow; no results | none | no (superseded) | keep unmerged |
| `research/qoac-h-v02-heldout-20261005` (`db4761a`) | a parallel QOAC-H v0.2 implementation, 12-material engineering, 242-material held-out confirmation | 241/241 wins, median 13.66x | no (superseded) | keep unmerged; optional SI replication sentence |
| `research/hartree-baselines-mgard-qpet-20261007` (`a86be8b`) | Hartree strongest baselines: MGARD s = −2 and QPET on P1 (60 bulk) and P3b (32 slabs), 3,588 searches | P1: A1/M2 18.2x, A1/Q 6.31x (60/60); P3b: A1/M2 21x, A1/Q 9.47x (32/32) | yes | merged in revision 3; cited in main text and Methods |
| `research/p3b-vacuum-level-20261007` (`6f03249`) | P3b vacuum-level (work-function) error across 5 arms and 3 tolerances on 27 qualifying slabs | at 1e-6: A1 median 0.00401 meV (27/27 < 1 meV), A3 0.00396 meV vs A2 0.552 meV, A6 0.340 meV | yes | merged in revision 3; cited in main text and Methods |
| `research/wpf-cloud-completion-20261007` (`805747f`) | WP-F Materials Project charge-density archive estimate completed in cloud (sample n = 300) | completed_v2: R(1e-3 e) = 4.367 [3.637, 5.458] vs json.gz (6.55 TB saved), format gain 2.00x | yes | merged in revision 3; cited in abstract, main text, Methods and SI |
| `research/qoac-hb-slab-20261007` (`f5c0ac1`) | QOAC-HB slab confirmation on 32 fresh P3b slabs; pre-registered criteria | FAIL 13/32 on criterion 1 (15 no AECCAR, 4 load failure); analysed 13/13 certified, overhead 1.000, utility 1.398x | no | keep unmerged; joint certification claimed for bulk only (48/48), slab work stopped |
| `research/hb-slab-aeccar-cohort-20261007` (`bab69ec`) | QOAC-HB slab cohort selected on AECCAR availability (N = 4) and diagnosis of 4 AECCAR loading failures | PASS on N = 4 (4/4 certified, overhead 1.010, utility 1.218x, 4/4 wins); diagnosis: 4/4 data defects | no | keep unmerged; joint certification claimed for bulk only (48/48), slab work stopped |
| `research/hb-slab-nomad-wide-20261007` (`981a7db`) | QOAC-HB wide NOMAD slab cohort with pre-screened AECCAR inputs (N = 1) | PASS on N = 1 (1/1 certified, overhead 1.000, utility 1.466x, 1/1 wins; Ni slab) | no | keep unmerged; joint certification claimed for bulk only (48/48), slab work stopped |
| `research/hb-selfslab-20261007` (`da3ea91`) | QOAC-HB self-computed slab cohort (32 VASP slabs on NUS cluster; release data-hb-selfslab-20261008) | FAIL 26/32 on criterion 1 (6 misses); criteria 2 and 3 pass (overhead 1.011, utility 1.453x, 26/32 wins) | no | keep unmerged; joint certification claimed for bulk only (48/48), slab work stopped |

## 1. `research/qoac-b3-full-50-census-20261005` at `142ddc8`

**Contents.** 18 commits on 2026-10-05 (17:35–17:53 +08:00, `d0806b7`..`142ddc8`), forked from `a0ad74b` (the
50-material B2 summary, which is in NC's history). The branch adds files only:

- QOAC-B3 compiled-partition design, a lossless partition-map codec (smallest unsigned label + zlib 6, or run length +
  zlib 6, whichever is smaller) with bit-exact invariant tests, and a 12-material engineering study
  (`analysis/operator_aware_bader_partition_compiled/`, workflow `qoac_b3_engineering.yml`). One run with a wrong
  CHGCAR normalization is documented and corrected before the recorded result (`a23fca7`, `29b919e`, `f69928b`).
- A frozen 50-material descriptive census (`analysis/operator_aware_bader_partition_compiled_census/`, workflow
  `qoac_b3_census.yml`). The 50 materials are the 12 B2 engineering and 38 B2 holdout materials, all previously used;
  no GO threshold was set after authorization.
- `analysis/QOAC_UNIFIED_FRAMEWORK_20261005.md`: three classes (diagonalizable linear operators → error allocation;
  fixed constraints → projection after generic compression; unstable discrete state → compile it and code it
  losslessly), a prior-art boundary for Bader, and the electric-field β = 1 test as the next step.

**Headline numbers.**

- Engineering (12): maximum direct-map vs Henkelman charge error 4.97e-7 e; lossless AECCAR / partition-map bytes
  median 176.85x (minimum 126.82x); complete archive 12/12 wins, median 97.39x (minimum 49.53x).
- Census (50): 50/50 complete, 0 failures, 50/50 exact decode; maximum charge error 4.97e-7 e; lossless AECCAR /
  partition map median 210.66x (P05 125.25x, minimum 121.26x); complete archive 50/50 wins, median 92.52x (P05
  46.55x, minimum 12.29x); the map is a median 41.7% of the compiled archive.
- Archive definitions: baseline = best frozen generic CHGCAR at τ_B = 1e-3 + lossless AECCAR0 + AECCAR2; compiled =
  B2 κ = 4 projected CHGCAR + lossless partition map.

**Relation to NC.** NC's "B3" is the different 10-06 study `analysis/qoac_b3_design/` (branch
`research/qoac-b3-design-20261006`, merged; results `01a3d54`): the Henkelman partition transcription matches the
compiled binary in 11/11, and on 12 fresh P2 materials a lossless label map (median 12.9 kB) is about 17-fold smaller
than a partition-faithful lossy AECCAR (SI Note 3, Supplementary Fig. 1). The 10-05 comparator is a lossless AECCAR,
a weaker baseline than the partition-faithful AECCAR, and its population is the development set. NC cites neither
92.52x nor 210.66x. NC therefore supersedes the storage comparison but not the 50-material exhaustiveness check or the
framework note.

**Decision.**

- (a) Keep unmerged as provenance. *Suggested default.*
- (b) Add one SI Note 3 sentence citing the 50-material census as a descriptive check on the development population
  (50/50 exact decode; maximum error 4.97e-7 e), stating the lossless-AECCAR comparator.
- (c) Merge the two result directories and the framework note as a design record, without citing them.

Either way, the open item "B3 has no confirmatory run" stands.

## 2. `research/qoac-electric-field-20261005` at `d3255fa`

**Contents.** All 18 commits of branch 1 plus 6 commits on 2026-10-05 (17:55 +08:00 onward, `a2e04e8`..`d3255fa`):
the QOAC-E design `analysis/operator_aware_electric_field/DESIGN.md` (β ∈ {0, 1, 2}, predicted β = 1 from the |G|^-2
weight), periodic Hartree-field metrics, a runner, frozen mechanism gates, a scaling test and the workflow
`qoac_e_engineering.yml`. No results are committed on this branch.

**Relation to NC.** Superseded. The electric-field test was re-frozen and run on
`research/general-qoac-electric-field-20261005` (design `ce9d12c`, 2026-10-05 20:47 +08:00; in NC's history;
`analysis/general_qoac_electric_field/results/RESULTS.md`): 12 materials, all three gates NO-GO (β1/β0 median error
ratio 0.8064, 12/12; β1/β2 0.928, 10/12; certified-rate ratio 1.031, 7/12). NC treats the Hartree field through the gain
predictor instead (predicted 1.151 vs measured 1.149 on bulk crystals; 1.164 vs 1.165 on slabs).

**Merge hazard.** Merging this branch also brings in all of branch 1.

**Decision.**

- (a) Keep unmerged. *Suggested default.* Nothing in NC depends on it.

## 3. `research/qoac-h-v02-heldout-20261005` at `db4761a`

**Contents.** 16 commits on 2026-10-05 (13:25–13:44 +08:00, `235846a`..`db4761a`), forked from `cfed2dd` (the v0.1
rate-floor diagnosis). It is a parallel implementation of the Nyquist-aware QOAC-H v0.2 codec, with the same law
Δ_G ∝ |G|^2. `analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py` is blob `0a37a3c` here and blob
`7c8ece7` in NC. The branch also holds its 12-material engineering study and a 242-material held-out confirmation in
`analysis/operator_aware_codec_hartree_v02_confirm/`.

**Headline numbers.**

- Engineering (12): 300/300 rows, 12/12 dual-certified at τ = 1e-6; median CR v0.2 / v0.1 10.87; v0.2 / best existing
  baseline 10.76, 12/12 wins.
- Held-out (242 = 254 development materials minus the 12 tuning materials; 180 bulk, 62 slab): 6,050/6,050 settings,
  0 failures, 242/242 dual-certified. Against the best of ZFP, SZ3 and SPERR: median 13.66x (bootstrap 95% CI 12.62–15.65),
  geometric mean 14.41x, 241/241 wins (one material without a baseline, mp-1038991, fixed in advance). Bulk median 11.96x
  (10.24–13.37), slab 29.85x (27.49–36.6). Status CONFIRMATORY_GO.

**Relation to NC.** Superseded. NC (SI Note 2) cites the merged v0.2 line instead:

- disjoint confirmation 48/48, median 15.016x (11.204–21.461), commit `31def38`;
- census at 1e-6 253/253, median 12.463x, commit `cc5d7a1`.

The 242 held-out materials come from the same development population as both, so this branch is a second
implementation, not new data.

**Merge hazard.** This branch conflicts with NC. Both lines write `analysis/operator_aware_codec_hartree_v02/` with
different code (18 files differ, +1,287 / −933 lines relative to NC). Do not merge it as is. If it is wanted, copy the
`_confirm` results under a new directory name.

**Decision.**

- (a) Keep unmerged as provenance. *Suggested default.*
- (b) Add one SI Note 2 sentence reporting it as an independent-implementation replication on the development
  population (241/241, 13.66x).

## 4. `research/hartree-baselines-mgard-qpet-20261007` at `a86be8b`

**Contents.** Strongest baselines for the Hartree contract: MGARD s = −2 (upstream `ac53ff9c`) and QPET (`5d17cb16`,
`1874108f`, SymEngine `fac9314c`) evaluated on P1 (60 MP bulk) and P3b (32 NOMAD slabs). 92 of 92 cohort materials analysed
with 0 material-level failures; 3,588 searches in total across τ ∈ {1e-6, 1e-4, 1e-8}. Protocol `16e8890`, CI run 37620406802,
sentinel `28574c3`, aggregate results commit `027e69a` (`analysis/hartree_baselines_mgard_qpet_20261007/RESULTS.md`).

**Headline numbers.**

- Primary τ = 1e-6:
  - P1 (60 MP bulk): A1 median certified CR 195 vs M2 10.2 (A1/M2 median 18.2, 95% CI 15.3–21.7, 60/60 wins), M-best 10.9 (A1/M-best 16.6, 95% CI 14.3–19.5, 60/60 wins), Q 29.4 (A1/Q 6.31, 95% CI 5.53–6.95, 60/60 wins; A3/Q 6.91, 95% CI 5.92–8.15, 60/60 wins).
  - P3b (32 NOMAD slabs): A1 median certified CR 504 vs M2 21 (A1/M2 median 21, 95% CI 17.5–27.9, 32/32 wins), M-best 23.1 (A1/M-best 19.6, 95% CI 15.7–24.9, 32/32 wins), Q 46 (A1/Q 9.47, 95% CI 8.14–12.8, 32/32 wins; A3/Q 11.3, 95% CI 9.62–16.5, 32/32 wins).
- τ = 1e-4: P1 A1/M2 median 12.5 (95% CI 11.4–15.4, 60/60 wins), A1/Q 5.22 (95% CI 4.6–5.93, 60/60 wins); P3b A1/M2 7.97 (95% CI 5.32–11.1, 32/32 wins), A1/Q 7.56 (95% CI 5.07–9.13, 32/32 wins).
- τ = 1e-8: P1 A1/M2 median 4.69 (95% CI 4.27–5.77, 60/60 wins), A1/Q 2.33 (95% CI 2–2.85, 60/60 wins); P3b A1/M2 7.99 (95% CI 5.2–11.8, 32/32 wins), A1/Q 3.84 (95% CI 2.7–4.83, 32/32 wins).

**Relation to NC.** Merged into revision 3 (`paper/nc-revision3-20261008`). Cited in abstract, main text Results, Methods,
and Fig. 5 panels e/f.

**Decision.**

- Merged into revision 3. *Suggested default.*

## 5. `research/p3b-vacuum-level-20261007` at `6f03249`

**Contents.** Work-function (|ΔΦ|) error analysis on 32 P3b NOMAD slabs across 5 arms (A1 closed-form law, A2 spectral
truncation, A3 operational optimum, A5 operator-blind RD optimum, A6 best of ZFP/SZ3/SPERR) and 3 tolerances (1e-6, 1e-4, 1e-8).
Protocol `47b110a`, sentinel `0e584d3`, CI run 37598559834 (34/34 jobs successful), results commit `4946f9f`
(`analysis/p3b_vacuum_level_20261007/RESULTS.md`). 32/32 slabs loaded; 480 planned streams recorded and reproduced exactly;
27/32 slabs qualify with vacuum run >= 3.0 Å (5 do not qualify).

**Headline numbers.**

- Primary τ = 1e-6 (n = 27 qualifying slabs):
  - A1 median |ΔΦ| 0.00401 meV (P95 0.0211 meV, max 0.0452 meV, 27/27 < 1 meV, 27/27 < 10 meV).
  - A3 median 0.00396 meV (P95 0.0136 meV, max 0.0339 meV, 27/27 < 1 meV, 27/27 < 10 meV).
  - Baselines: A2 median 0.552 meV (19/27 < 1 meV), A5 median 0.283 meV (23/27 < 1 meV), A6 median 0.340 meV (19/27 < 1 meV).
- τ = 1e-4 (n = 27):
  - A1 median 1.09 meV (P95 5.34 meV, max 6.06 meV, 12/27 < 1 meV, 27/27 < 10 meV).
  - A3 median 1.72 meV (P95 6.72 meV, max 8.26 meV, 9/27 < 1 meV, 27/27 < 10 meV).
  - Baselines: A2 median 41.0 meV (2/27 < 10 meV), A5 median 21.2 meV (10/27 < 10 meV), A6 median 35.5 meV (2/27 < 10 meV).
- τ = 1e-8 (n = 27):
  - A1 median 1.04e-5 meV, A3 median 1.53e-5 meV vs A2 0.00386 meV, A5 0.00270 meV, A6 0.00418 meV (all 27/27 < 1 meV).

**Relation to NC.** Merged into revision 3 (`paper/nc-revision3-20261008`). Cited in Results, Methods, and Fig. 5.

**Decision.**

- Merged into revision 3. *Suggested default.*

## 6. `research/wpf-cloud-completion-20261007` at `805747f`

**Contents.** Materials Project charge-density archive estimate completed in the cloud (frame 415,289 objects, 8.4976 TB
in MP json.gz; n = 300 stratified sample: 243 laptop SUCCESS checkpoints + 57 cloud objects). Evaluated under `completed_v2`
(293 succeeded, 7 failed, after rerun of 6 never-started objects per `DEVIATIONS.md` entries 12–13; results
`analysis/extensions_20260930/WP-F/results_cloud/completed_v2/RESULTS.md`), `completed` (288 succeeded, 12 failed; `completed/RESULTS.md`),
and `laptop_as_frozen` (243 succeeded, 57 failed; `laptop_as_frozen/RESULTS.md`).

**Headline numbers.**

- `completed_v2` (sample n = 300; 293 succeeded, 7 failed): primary endpoint R(1e-3 e) = 4.367 [3.637, 5.458] vs json.gz archive, estimated saving 6.55 TB
  [6.16, 6.94] (lower bound 3.64 > 1.5); format gain alone (json.gz → lossless float64 + zlib) 2.00x; R vs lossless float64 2.66 [2.21, 3.27].
- `completed` (sample n = 300; 288 succeeded, 12 failed): R(1e-3 e) = 3.815 [3.203, 4.701], estimated saving 6.27 TB [5.84, 6.69].
- `laptop_as_frozen` (sample n = 300; 243 succeeded, 57 failed): R(1e-3 e) = 1.636 [1.580, 1.698], estimated saving 3.30 TB [3.12, 3.49], format gain alone 2.05x.

**Relation to NC.** Merged into revision 3 (`paper/nc-revision3-20261008`). Cited in abstract, main text Results, Methods,
and Supplementary Note 1.12.

**Decision.**

- Merged into revision 3. *Suggested default.*

## 7. `research/qoac-hb-slab-20261007` at `f5c0ac1`

**Contents.** QOAC-HB joint Hartree + Bader confirmation on 32 fresh P3b NOMAD slabs. Protocol `7e2799c`, CI run 37579899219
(head `b006a1f`), results commit `f23c035` (`analysis/qoac_hb_slab_20261007/results/manifest/RESULTS.md`). Pre-registered
primary criteria (N = 32) and secondary criteria (N = 17 with AECCAR).

**Headline numbers.**

- Primary analysis (N = 32): Confirmatory FAIL.
  - Criterion 1: 13/32 analyzable and jointly certified (threshold >= 31/32) — FAIL.
  - Criterion 2: joint overhead at tau_B = 1e-4 e: n = 13, median 1.000, CI [1.000, 1.011] (threshold <= 1.10, CI upper <= 1.15) — PASS.
  - Criterion 3: utility at tau_B = 1e-4 e: 13/32 wins, median 1.398, CI [1.306, 1.517], min 1.141 (threshold >= 24/32) — FAIL (on count).
- Secondary analysis (N = 17 with an AECCAR reference): FAIL on criterion 1 (13/17 vs >= 17/17); criterion 2 PASS; criterion 3 PASS (13/17 wins, median 1.398, CI [1.306, 1.517], min 1.141).
- Failures: 15 entries have no AECCAR (`AECCAR0 unavailable`); 4 entries with an AECCAR failed at loading (`RuntimeError: invalid AECCAR` on `nomad-IZPVe_A6_quS`, `nomad-ViaCyatoI3FA`, `nomad-DcwYU1UzKNe8`; `ValueError: string or file could not be read to its end due to unmatched data` on `nomad-hk3gUBk-5QN5`).
- On the 13 analysed slabs: joint contract certifies at all three tau_B (39/39 streams), overhead median 1.000 at 1e-3 and 1e-4, 1.009 at 1e-5; utility median 1.398x (13/13 wins, range 1.141–1.682).

**Relation to NC.** Not merged. Per Author decision (2026-10-08), the manuscript states joint certification for bulk crystals only (48/48), and slab work stops here.

**Decision.**

- Keep unmerged as provenance. *Suggested default.*

## 8. `research/hb-slab-aeccar-cohort-20261007` at `bab69ec`

**Contents.** QOAC-HB slab cohort selected on AECCAR availability (N = 4) and diagnosis of the four AECCAR loading failures.
Protocol `69f8fc2`, CI run 37600232959 (head `4eee3f6`, 21/21 jobs), results commit `e99ba3e`
(`analysis/hb_slab_aeccar_cohort_20261007/RESULTS.md`); diagnosis in `analysis/hb_slab_aeccar_cohort_20261007/diagnosis/DIAGNOSIS.md`.

**Headline numbers.**

- Primary analysis (N = 4): Confirmatory PASS on N = 4.
  - Criterion 1: 4/4 analyzable and jointly certified (threshold >= 4/4) — PASS.
  - Criterion 2: joint overhead at tau_B = 1e-4 e: n = 4, median 1.010, CI [1.008, 1.032] (threshold <= 1.10) — PASS.
  - Criterion 3: utility at tau_B = 1e-4 e: 4/4 wins, median 1.218, CI [1.185, 1.544], min 1.185 (threshold >= 3/4) — PASS.
  - 12/12 streams certified (R3 best post).
- Diagnosis (`diagnosis/DIAGNOSIS.md`): 4/4 data defects in published NOMAD AECCAR0 files:
  - 3 all-NaN files: `nomad-IZPVe_A6_quS` (2,419,200 NaN), `nomad-ViaCyatoI3FA` (1,975,680 NaN), `nomad-DcwYU1UzKNe8` (1,658,880 NaN).
  - 1 Fortran exponent-overflow file: `nomad-hk3gUBk-5QN5` (1,229,312 non-zero tokens with magnitude 4.94e170–8.52e196, 612,201 negative; sum / N = -2.43e191).
  - AECCAR2 files of all four entries are valid and load identically across parsers.

**Relation to NC.** Not merged. Per Author decision (2026-10-08), the manuscript states joint certification for bulk crystals only (48/48), and slab work stops here.

**Decision.**

- Keep unmerged as provenance. *Suggested default.*

## 9. `research/hb-slab-nomad-wide-20261007` at `981a7db`

**Contents.** QOAC-HB wide NOMAD slab cohort with AECCAR input-validity checks applied across the entire NOMAD slab pool (N = 1).
Protocol `2ad4c68`, CI run 37714279960 (head `74116a7`, 21/21 jobs), results commit `1ecac5c`
(`analysis/hb_slab_nomad_wide_20261007/RESULTS.md`).

**Headline numbers.**

- Selection: 820 frame rows -> 556 readable CHGCAR -> 303 size window -> 188 after NOMAD id exclusion -> 20 after slab-formula exclusion -> 6 with AECCAR present and headers on CHGCAR grid (1 formula `Ni`, 6 uploads) -> drawn N = 1 (`nomad-eKxYecHu4VTk`, Ni, 279,936 points, 2 atoms).
- Primary analysis (N = 1): Confirmatory PASS on N = 1.
  - Criterion 1: 1/1 analyzable and jointly certified (threshold >= 1/1) — PASS.
  - Criterion 2: joint overhead at tau_B = 1e-4 e: n = 1, median 1.000, CI [1.000, 1.000] — PASS.
  - Criterion 3: utility at tau_B = 1e-4 e: 1/1 wins, median 1.466, CI [1.466, 1.466], min 1.466 — PASS.
  - 3/3 streams certified (joint CR 428.9).

**Relation to NC.** Not merged. Per Author decision (2026-10-08), the manuscript states joint certification for bulk crystals only (48/48), and slab work stops here.

**Decision.**

- Keep unmerged as provenance. *Suggested default.*

## 10. `research/hb-selfslab-20261007` at `da3ea91`

**Contents.** QOAC-HB self-computed slab cohort: 32 VASP slabs computed on the NUS cluster (GitHub release `data-hb-selfslab-20261008`,
96 assets, 1,805,055,269 bytes). Protocol `ae0076a`, CI run 37723028989 (head `4f22046`, 21/21 jobs), results commit `00f8b38`
(`analysis/hb_selfslab_20261007/RESULTS.md`).

**Headline numbers.**

- Selection: MP summary 2026-09-28 -> 5,524 ranked formulas; 62 visited, 40 slabs drawn; 39 converged; input QC 39/39 pass; N = 32 (draw ranks 1–10 and 12–33, npoints 1,568,000–5,376,000, 8–40 atoms).
- Primary analysis (N = 32): Confirmatory FAIL (criteria 1, 2, 3: fail, pass, pass).
  - Criterion 1: 26/32 analyzable and jointly certified (threshold >= 31/32) — FAIL (6 misses: `mp-aaabxapz` Ti2CoIr, `mp-aaaabsyn` Li2GaAu, `mp-aaacezrr` LiZrSe2, `mp-aaabxhim` Li2PdAu, `mp-aaabxbrv` Sc2PdPt, `mp-aaacpkjv` HfZrOs2).
  - Criterion 2: joint overhead at tau_B = 1e-4 e: n = 26, median 1.011, CI [1.007, 1.014] (threshold <= 1.10, CI upper <= 1.15) — PASS.
  - Criterion 3: utility at tau_B = 1e-4 e: 26/32 wins, median 1.453, CI [1.353, 1.532], min 1.229 (threshold >= 24/32, > 1.10) — PASS.
- Descriptive: certified R3 streams 29/32 at 1e-3, 26/32 at 1e-4, 26/32 at 1e-5; median R3 joint CR 1392.0 at 1e-3, 1479.6 at 1e-4 and 1e-5.

**Relation to NC.** Not merged. Per Author decision (2026-10-08), the manuscript states joint certification for bulk crystals only (48/48), and slab work stops here.

**Decision.**

- Keep unmerged as provenance. *Suggested default.*
