# Unmerged research branches — decision list for the author (2026-10-07)

Three branches on `origin` hold completed or prepared work that is neither merged into the Nature Communications
authority `paper/nc-reopen-20261007` (`87b3a65`, revision 2) nor cited by its manuscript. Nothing has been merged and the branches
are untouched. Numbers are copied from the result files on each branch (paths below are on that branch).

| branch (tip) | content | headline | superseded by NC? | suggested default |
|---|---|---|---|---|
| `research/qoac-b3-full-50-census-20261005` (`142ddc8`) | compiled-partition B3: lossless Bader partition map, 12-material engineering, 50-material descriptive census; unified framework note | census 50/50 exact; map 210.66x smaller than lossless AECCAR; complete archive 92.52x smaller, 50/50 | partly: NC's B3 is the different 10-06 study | keep unmerged; optional SI sentence |
| `research/qoac-electric-field-20261005` (`d3255fa`) | the B3 census branch plus a QOAC-E (electric-field) design, runner and workflow; no results | none | yes | keep unmerged |
| `research/qoac-h-v02-heldout-20261005` (`db4761a`) | a parallel QOAC-H v0.2 implementation, 12-material engineering, 242-material held-out confirmation | 241/241 wins, median 13.66x | yes | keep unmerged; optional SI replication sentence |

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
