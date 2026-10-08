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
