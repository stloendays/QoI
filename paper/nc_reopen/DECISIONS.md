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
