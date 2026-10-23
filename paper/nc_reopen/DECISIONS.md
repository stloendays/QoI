# Scope reopening for Nature Communications — decisions (2026-10-07)

Author decisions (user, 2026-10-07: "等云端结束之后，完成主图参数，重开冻结稿，投NC"):
1. **Reopen** the frozen manuscript `paper/qoac-integration-20261005` (`efd1e2c`). The frozen branch stays unchanged as the
   historical record; the reopened manuscript lives on `paper/nc-reopen-20261007`.
2. **Venue: Nature Communications** (Article: ~5,000 words including Methods; abstract <= 150 words; <= 10 display
   items; no Extended Data tier; ~60 references).
3. **Main-figure parameters**: the figure-studio defaults (183 mm, QoI house style, matplotlib, svg + pdf + png at 600
   dpi).

Defaults adopted by the assistant (reversible; flagged for author review):
- Title: "The downstream operator qualifies, predicts and shapes the certified compression of electronic densities".
- Encoder per system class: closed-form law for bulk crystals; operational allocation (R3) for surfaces and for the
  joint contract.
- Pre-registration register: complete in the repository; Methods points to it. NO-GO and FAIL records are not in the
  main text.
- Bader storage comparison (label map vs partition-faithful AECCAR): Supplementary Information.

Planning inputs: `paper/program_draft/v2/STORY_AND_FIGURES.md`, `paper/program_draft/v2/CLAIM_EVIDENCE_MAP.md`.

Reopening procedure (each step leaves a committed record):
1. prior-art audit addendum for the new claims;
2. claim–evidence map (v2, updated on completion);
3. figure architecture and figures;
4. manuscript story review;
5. submission QA (`audit_manuscript.py --final`, rendered PDF check).

## Revision 2 (2026-10-07)

Author reply to the five defaults: "可以改，figure可以再多一点点（不一定非要4x4，你想办法让layout比肩nature" — the
defaults may change; more figure content, Nature-level layouts, no fixed grid. Applied:
- 8 main figures + Table 1 (9 of 10 display items): new mechanism figure (Fig. 4, KCN), Figs. 5–8 re-laid out with
  added panels (certified CR vs tau; gain ladder; R3 vs best other and best post-processor; within-operator ranking),
  Fig. 1b extended with an "Allocation and prediction" band, one colour code across the data figures
  (`FIGURE_PLAN.md`).
- Lee et al. 2022 read in full (mdpi.com/2076-3417/12/13/6718, Sect. 3.2.1): the constraint step minimizes the Bregman
  divergence of x log x under linear moment constraints (multiplicative correction). The manuscript now calls the
  uniform basin projection its Euclidean counterpart (minimum L2 and L-inf additive correction).
- Supplementary Fig. 1 built (`figures/nc/si/figS1`).
Other defaults (title, encoder per system class, register in the repository, Bader storage in the SI) unchanged.

## Revision 3 (2026-10-07 to 2026-10-08)

Author decisions, in order:
1. **Four cloud work items** ("好滴，你继续做吧", then the work-item list):
   - MGARD s = −2 and QPET as QoI-preserving baselines on P1 and P3b;
   - the P3b vacuum-level (work-function) error;
   - the four AECCAR loading failures diagnosed, plus a slab cohort selected on AECCAR availability;
   - WP-F completed in the cloud.
   Each item ran on its own branch, with its protocol frozen before execution.
2. **WP-F platform consistency.** 1405 of 1409 checks agreed; the four differing Bader errors sit on never-certifiable rungs. The author ruled the platforms consistent ("判定一致，补跑 57 个"; WP-F `DEVIATIONS.md` 9). The six objects that never started were then rerun ("重跑这 6 个"; `DEVIATIONS.md` 12).
3. **Slab joint certification.**
   - The NOMAD search was widened (N = 1 qualified).
   - 32 slabs were then self-computed on Vanda. Their density files are published as release `data-hb-selfslab-20261008` ("发成 QoI 仓库的 GitHub Release").
   - After the self-computed cohort failed criterion 1 (26/32): "稿子只写 bulk，slab 到此为止". The manuscript states joint certification for bulk crystals only (48/48). The four slab cohorts stay in the repository.
4. **Fig. 5 panels.** Panels e (QoI-preserving baselines) and f (slab work-function error) approved ("可以的").

Defaults adopted by the assistant, flagged for author review:
- The abstract now leads the Hartree result with the QoI-preserving compressor (QPET; 6.3- and 9.5-fold).
- The abstract adds the archive-scale result (4.4-fold at 1e-3 e). To stay at 150 words, its near-optimality clause (A3/A1 = 1.105 on bulk crystals) moved to Results only.

## Revision 4 (2026-10-12)

Request: "你来看看云端最近完成任务的情况，并完善一下本地的任务". A cloud agent's scientific audit (PR #15,
`paper/nc-scientific-audit-20261009`) was reviewed and built on in `paper/nc-rev4-20261012`.
- **Kept from the audit:**
  - the corrected QSQ probability statement;
  - the reworded Introduction;
  - the MGARD best-smoothness comparison;
  - the slab near-optimality threshold.
- **Replaced by definitions or data,** under the standing manuscript rule ("fix it, do not confess it"):
  - the work-function, QPET, archive-writer and partition-storage caveats;
  - the Gaussian-bias sentence.

  `SCIENTIFIC_AUDIT_20261009.md` has the resolution table.
- **New pre-registered measurement:** self-contained joint storage on the 48 P2 confirmatory crystals.
  - Protocol `d084d4a`, run 38201584592, branch `research/hb-selfcontained-bytes-20261012`.
  - Implementation by Codex, reviewed and recomputed in the main session.
- **Abstract:** now ends with the self-contained result ("carrying its own partition, stayed 10.2-fold smaller than
  pointwise codecs"). 148 words; main text plus Methods 4,994.
- **Joint-contract wording (2026-10-12, author: "开始吧").** The Discussion's "two contracts differ in kind" became
  "one stream meets two linear constraints at opposite scales". Under the exact partition, the Bader charges are sums
  over fixed basins, which is also a linear constraint. No number changed.
- **CI fix after the Hartree-archive addition (2026-10-19, PR #16 Auto-fix).** Commit `4736fc5` added the
  Hartree-archive result, which took the text 245 words over budget (5,245 > 5,000), and changed the abstract wording
  that a test pinned. The research branch `research/archive-hartree-law-20261012` (`81ba218`) is merged here, so that
  the Table 1 commits and the results files are on this branch. To get back under 5,000 words (now 4,966):
  - the archive paragraph is condensed, keeping every number;
  - a forward reference is dropped;
  - development-history sentences are removed (laptop and runner split, regeneration checks, a numerical-identity
    check);
  - a duplicated overhead clause is removed;
  - two scope sentences are merged.

  The Discussion now names the 356-fold Hartree archive in place of the 0.05 meV slab reprise. A new test reads every
  archive number back from `results/estimates.csv`.

## Author block (2026-10-16)

Author instruction: "作者是junbotong，单位是nus，ORCID是0009-0006-5158-3471".
- `MANUSCRIPT.md` and `SUPPLEMENTARY_INFORMATION.md` now carry the author block:
  - Junbo Tong (the printed form of the account name `junbotong`, as in the CV vault);
  - National University of Singapore, Singapore;
  - ORCID 0009-0006-5158-3471 (check digit verified).
- The same values are kept in the personal skill `junbo-author-profile`.
- Funding and correspondence are not set. The audit's F1 check now reads the whole title block instead of the first
  six lines.

## Revision 5 merged with revision 4 (2026-10-19, PR #17 Auto-fix)

- Merging `paper/nc-rev4-20261012` at `5a1bf34` (Hartree archive, 4,966 words) into the deployment-cost revision.
- Overlapping sentences take the revision-4 wording. The deployment-cost Results subsection, Table 2, Methods paragraph
  and Table 1 rows are kept. To stay within 5,000 words (now 4,992), the following were condensed or removed:
  - the textbook-allocation sentence;
  - the QPET configuration aside, which Methods states;
  - the Discussion's repeat of the per-operator gains;
  - the pre-registration clause, which now cites Table 1;
  - the deployment opening and Methods sentences.

## Revision 8 (2026-10-22)

Request: "你看一下云端最新的稿子（谷歌文档那边等）继续修改吧". The latest cloud draft is revision 7 (PR #18,
`paper/nc-rev7-whole-object-ffcz-20261022`); the Google Docs "NC Manuscript v6 working source" is a staging copy of
revision 5. Revision 8 builds on revision 7:
- **FFCz in Fig. 5e.** The panel now plots the law against FFCz for the materials FFCz certified; `make_fig5.py`
  asserts the medians and wins against `analysis/hartree_baseline_ffcz_20261012/results/SUMMARY.json`. Methods gains
  the FFCz configuration sentence; Table 1 gains the FFCz protocol and run rows (`8f98f8b`, `eaf7427`).
- **Prose.** Revision 7 had compressed the Introduction and Discussion; their revision-5 argument is restored and
  updated for FFCz and the whole-object archive. The archive paragraphs state the magnetization contract once. The
  statements the scientific audit requires (QPET read full float64, work-function definition, per-plane bound,
  5.35-fold attribution, exact-partition Bader contract) are back in the main text.
- **Vocabulary.** Every `pre-registered`, `pre-registration`, `frozen`, `freeze` and `canonical` is removed from the
  main text, legends and SI (skill rule of 2026-10-19 and 2026-10-21). Table 1 is now "Protocol chronology".
- **Legends** rewritten short and descriptive (rule of 2026-10-21): no headline numbers, no commit hashes.
- **SI order.** The whole-object note moves to Supplementary Note 4 (first cited after Note 3); Notes 4–7 become 5–8.
  The spin figure becomes Supplementary Fig. 1 and the partition-storage figure Supplementary Fig. 2. Note 3.5 states
  the FFCz configurations and drops the self-limiting closing sentence.
- Main text plus Methods 4,997 words; abstract 146. `audit_manuscript.py --final`: 0 failures, 0 warnings;
  `test_scientific_claims.py`: 13 passed.

### Revision 8, writing pass and build (2026-10-22)

Request: "你看看有没有什么在论文写作技巧上面的提升，在渲染之前", then the rebuild with a page-by-page check.
- QoI is defined at first use (abstract and Introduction); the abstract now states the claim and ends on the
  archive consequence; the Introduction's third paragraph states the second gap instead of a second "Here".
- Reported precision is cut to what the claim needs (0.0776, 0.376/0.203, 1.60%, 81.3%); the number sweep
  (`numcheck.py`, now also reading the FFCz and whole-object results) finds all 361 numbers in committed sources.
- The Table 2 duplicate sentence is removed; the archive and gain-ladder paragraphs open with topic sentences;
  the Discussion ends on the consequence for archives.
- Build: equations are MathML in the PDF and native Word equations in the DOCX (`figures/nc/omml.py`, from the
  Catalyst-Essay builders, plus accents and lower limits): 254 inline and 5 display equations, checked in the
  Chrome PDF and in a WPS export of the DOCX. Fig. 2a axis label no longer says "frozen".
- 4,996 words; audit 0 failures; claim tests 13 passed.

## Revision 9 (2026-10-23)

Request: "新意的定位这个加进去 … 先做叙述减数字". Builds on revision 8 (`7721b8d`).
- **Narrative pass.** Each Results paragraph keeps the number that carries its claim; secondary tolerances,
  per-stratum values, repeated ladder numbers and secondary intervals move to the SI tables that already hold
  them (Supplementary Notes 1 and 3). Removed from the main text, among others: the 1e-4 / 1e-2 e QSQ rates, the
  1,332-reconstruction count, the 6.54 TB saving, the per-tolerance archive folds, the energy and susceptibility
  centres (shown in Fig. 3c), the uniform-step and per-codec KCN ratios, the per-tolerance law/pointwise and
  operator-metric lists, the MGARD best-smoothness ratios, the work-function maxima and per-slab folds, the
  per-arm search-time folds, the A3/A1 per-tolerance list, the projection counts and the slab and
  per-operator gain values. Number sweep: 284 numbers, all in committed sources (revision 8: 361).
- **Novelty positioning.** The Introduction's "Here" paragraph states that the measurement contract, not the
  field, is the object compression must satisfy. The Discussion's second paragraph now names the two ideas:
  the contract belongs to the quantity of interest (eligibility 3/50 to 50/50 when only the role of the partition
  reference changes), and for linear analyses the operator is the unit of design.
- Main text plus Methods 4,831 words; `audit_manuscript.py --final`: 0 failures, 0 warnings;
  `test_scientific_claims.py`: 13 passed.
- **Codec order at matched density error (same day).** The contract result from the private RhoCodec mechanism
  package (`stloendays/Essay-Work_Store`, `research/rhocodec-mechanism-20261023`, `9c83cd5`) is rerun on the committed
  benchmark (`analysis/contract_codec_order_20261023/`, `0a6ebf6`; identical counts) and enters the paper: one
  Results paragraph after "Evaluability belongs to the contract" (SPERR better in 185/185 with reference basins, SZ3
  in 109/185 with re-derived basins; re-derived error ratio vs reassigned-voxel ratio Spearman 0.607), one Discussion
  clause under the first idea, one Methods sentence, Supplementary Note 1.13 and a new Supplementary Fig. 1
  (`figures/nc/si/figS_order/`). The spin figure becomes Supplementary Fig. 2 and the partition-storage figure
  Supplementary Fig. 3. New claim test `test_codec_order_at_matched_distortion`.
- Final: main text plus Methods 4,980 words; audit 0 failures, 0 warnings; claim tests 14 passed; number sweep 288
  numbers, all found.
