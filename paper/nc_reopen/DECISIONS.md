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
- **Spectral truncation at loose tolerance (same day).** Request: "谱截断 … 之后都用服务器来算". The 92-material
  part of the comparison needs no new run: the law protocol already certified A2 and A3 for every material at every
  tolerance. `derive_operational_vs_truncation.py` (`02da306`) gives A3/A2 1.29 (bulk, 60/60) and 1.49 (slabs, 32/32)
  at 1e-4, and A3 ahead of truncation in every material at every tolerance. The truncation paragraph now says so, and
  Supplementary Note 3 gains the A3/A2 rows. The archive-scale truncation estimate goes to Vanda.
- **Build (same day).** `figures/nc/build_nc_manuscript.py` → `figures/nc/release/NC_manuscript_20261024.{pdf,docx}`,
  17 pages; the revised passages checked in the rendered PDF (pp. 1, 3, 5, 12).

## Revision 10 (2026-10-25)

Request: "写进去吧" — the server results of 2026-10-24 into the manuscript. Branch `paper/nc-rev10-20261025` from
revision 9 (`c2fe815`), with `research/xc-linearized-law-20261025` merged (it carries the archive-truncation and XC
studies of `research/server-truncation-xc-20261024`).
- **Archive.** The archive paragraph, the abstract and the Discussion now use operational allocation (A3): 347-fold
  (95% CI 317–387) at 1e-6 and 1,371-fold at 1e-4, with the closed-form law (316-fold), truncation (232-fold; 1,142-fold
  at 1e-4) and the pointwise writer (34.6-fold) as comparisons; Supplementary Notes 3.4 and 4.4 gain the T and O rows.
  Methods: the Hartree archive applied the design to A1, A2, A3 and A6.
- **Exchange-correlation energy.** New Results paragraph (prediction section): the linearized allocation from v_xc
  certifies as much as the closed-form law (X/L 0.99–1.00 bulk, 0.93–0.96 slabs); under an E_xc contract the law
  certifies 5.4- and 6.9-fold (bulk) and 2.9- and 1.9-fold (slabs) more than pointwise codecs; a Hartree certificate
  does not carry E_xc on slabs. New Methods subsection, new Supplementary Note 7 (Notes 7–9 become 8–10), new ref. 38
  (PBE; refs. 38–41 become 39–42), four Table 1 rows. Discussion: the operator is the unit of design "for linear analyses
  and, through its linearization, for the exchange-correlation energy"; abstract clause added.
- **Word budget.** To stay at 5,000: implementation details moved from Methods to the SI (seeds and work keys, QPET
  versions, archive strata, FFCz configurations, A0 ladder) and Results sentences tightened (truncation, QoI-preserving
  baselines, per-operator gains, archive composition). Claim test `9.15-fold` now reads the SI.
- Main text plus Methods 4,998 words, abstract 150; `audit_manuscript.py --final` 0 failures, 0 warnings;
  `test_scientific_claims.py` 17 passed (new: operational archive, XC contract, linearized allocation); number sweep
  288 numbers, all found. Build `figures/nc/release/NC_manuscript_20261025.{pdf,docx}`, 17 pages; changed pages
  (1, 8, 11, 12, 14, 15, 17) checked in the rendered PDF.

## Revision 11 (2026-10-25)

Request (scheduled task, user 2026-10-25 14:54): 「帮我看看论文算法还可以如何优化和升级，并开始，不需要我审批 … 最终完成就行」.
Branch `paper/nc-rev11-20261025` from `research/algo-upgrade-20261025` (plan
`paper/nc_reopen/ALGORITHM_UPGRADE_PLAN_20261025.md`; protocols, writer and tests `fd5646d`; results `7880324`, Vanda
probe 1491770, production 1491799/1491800/1491801, tarball SHA-256 be574d60b72a, every ratio recomputed independently).
- **Water-filling writer.** New Methods subsection and Supplementary Note 3.6: the law's steps with reverse
  water-filling at shell granularity, context-adaptive arithmetic coding (or zlib, per shell), a binary header and
  space-group symmetry prediction; truncation and operational allocation in the same writer. All study-1 criteria met on
  the 92 law-protocol materials: operational/water-filling 0.999 (0.997–1.001) at 1e-6 and 0.979 at 1e-4; water-filling
  over truncation 92/92 at both tolerances; writer over revision-10 A3 2.34-fold (2.14–2.69), 92/92.
- **Results.** The truncation paragraph now explains the 1e-4 crossover as the zlib container's cost and gives the
  water-filling result; a new paragraph gives the attribution (coder and header 1.34/2.51, symmetry 1.91) and the
  writer's gain over A3 and A6; the optimizer-share paragraph states that the share vanishes under the writer (heading
  now "…, and the closed form needs no search"); the archive paragraph uses the writer: 555-fold (492–635) at 1e-6,
  15.3 GB, and 1,818-fold at 1e-4, with the revision-10 writers as comparisons and the magnetization share at 1e-4.
- **Abstract and Discussion:** 347-fold → 555-fold; Discussion "The system class decides the encoder" → "Once zeros
  are entropy-coded, the closed form is the encoder".
- **SI:** Note 3.4 and Note 4.4 gain the W/Q rows; Note 3.6 new.
- **References:** 42 spglib, 43 arithmetic coding (Witten, Neal & Cleary); AFLOW becomes 44.
- **Word budget:** implementation details moved from Methods to the SI (joint-contract post-processor definitions →
  Note 5; QoI-preserving-baseline and work-function details → Note 3.1; acceptance-criteria lists → Notes 3 and 5).
- Table 1: two rows (`fd5646d`, `7880324`). Claim tests: `test_water_filling_writer`, `test_writer_archive`;
  `test_operational_archive` now checks the revision-10 rows as comparisons.
- Main text plus Methods 4,998 words, abstract 150; `audit_manuscript.py --final` 0 failures, 0 warnings;
  `test_scientific_claims.py` 19 passed; number sweep 304 numbers, all found.

## Revision 12 (2026-10-26)

Request (2026-10-25 21:08): 「再看看有啥能继续升级研究的开始完善！」 (and 14:54: 「…不需要我审批…最终完成就行」).
Branch `paper/nc-rev12-20261025` from `research/algo-upgrade2-20261025` (plan
`paper/nc_reopen/ALGORITHM_UPGRADE2_PLAN_20261025.md`; protocols, writer, runners and tests `4102390`; results, review
recomputation and RESULTS.md `c68c605`). Vanda (CFP04-CF-046): probe 1492816, production 1492899 (study 3),
1492900/1492901 (study 4), 1492902/1492903 (study 5); tarball SHA-256 ed7e01c1d117…; both aggregators re-run
byte-identical and every estimate recomputed independently (`review_recompute.py` in studies 3 and 4).

- **Correction of the archive moment certificates (study 5, mandatory).** In revision 10's archive run (writers T, O)
  and revision 11's (W, Q), the Bader partition used for the moment certificate was cached under one id for every
  decoded density, so every (writer, tolerance) pair after the first used the first writer's 1e-6 decoded partition.
  The rerun rebuilds each decoded density's own partition. Old → new (whole-object reduction): T 1e-6 232.5 → 232.5,
  1e-4 1,142 → 1,115 (992–1,255); O 1e-6 347.2 → 347.3 (317–387), 1e-4 1,371 → 1,325 (1,158–1,511); W 1e-6 555.2 →
  555.2 (492–635), 1e-4 1,818 → 1,735 (1,470–2,048); Q 1e-6 558.4 → 557.9 (494–638), 1e-4 1,813 → 1,726
  (1,457–2,041). At 1e-4, 4 (T), 8 (O), 8 (W) and 6 (Q) objects no longer certify the moments on the decoded partition
  and are stored with the reference atom map. Magnetization share of W at 1e-4 63.5% → 65.2%; L/T at 1e-4
  0.907 → 0.929; W/O at 1e-4 1.33 → 1.31. Density streams, Hartree certificates, L and P are unchanged. The
  manuscript and SI state the corrected numbers (main text archive paragraph; Supplementary Notes 3.4 and 5.4); the
  committed revision-10/11 result files are kept unchanged and SOURCE_FILES.md points to the rebuilt-partition files.
- **Predictive writer (study 3; G1, G2, validity met).** Structure-factor prediction in the water-filling writer on the
  92 law-protocol materials: 1.95-fold (1.79–2.07; 89/92) over the water-filling writer at 1e-6, 1.28 at 1e-4; 2.40 on
  cells with one symmetry operation, 1.06 above 24; operational allocation on the residual 0.995 / 0.947 of the closed
  form; W1S reproduced revision 11's bytes 92/92. New Results paragraph after the writer attribution, Methods paragraph
  in "Water-filling and predictive writers", Supplementary Note 4.1–4.2.
- **Archive under the predictive and magnetization writers (study 4; A1, M1, validity met).** V 1,401-fold
  (1,245–1,594) at 1e-6 (6.1 GB) and 4,719 (3,585–6,052) at 1e-4; V/W 2.52 and 2.72. Attribution (defines the claim):
  density prediction VP/W 1.74 (1e-6) and 1.13 (1e-4), magnetization writer V/VP 1.45 and 2.40. Magnetization stream:
  pointwise/W2M median 30.1 (298/300) and 31.1 (291/293). Porod exponent of the decoded partitions −2.96 (IQR −3.23 to
  −2.72), stated as measured next to Porod's −4. Abstract and Discussion: 555-fold → 1,401-fold; Discussion's
  60/62 composition sentence replaced by the magnetization-operator sentence.
- **Supplementary Information.** New Supplementary Note 4 (predictive writer, its cohort table, magnetization writer,
  archive tables); former Notes 4–10 renumbered 5–11 in manuscript, SI, SOURCE_FILES.md and claim tests (first-cited
  order). The QPET float64-host count, the work-function per-plane bound and the MGARD smoothness pointer moved from
  the main text to Supplementary Notes 3.1–3.2.
- **Word budget (5,000 / 150).** Shortened: writer attribution paragraph, Discussion (evaluability numbers, the
  Bader-at-no-cost repetition), Methods (Nyquist alias wording, A5 definition, deployment-cost streaming decoder,
  single-density codec list, spectral-audit matching, codec-order pair selection, dead-zone sentence), abstract
  (Spearman 0.978/0.979 → 0.98; "QSQ" abbreviation, used once, dropped).
- Table 1: two rows (`4102390`, `c68c605`). Claim tests: `test_operational_archive` and `test_writer_archive` read the
  rebuilt-partition SUMMARY.json; new `test_predictive_writer`, `test_predictive_archive`. `numcheck.py` reads the new
  RESULTS.md files and `analysis/server_runs_20261025c/README.md` (commit line added).
