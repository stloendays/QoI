# Finalization task — QoI second algorithm upgrade (2026-10-25): review, revision 12, report, cleanup

You are a headless Claude Code run started by the monitor `C:\Users\ASUS\.claude\tools\qoi_algo2_monitor.py` after the
Vanda results of the three studies were collected, SHA-256-checked and aggregated. The user is not present. The user's
instructions (2026-10-25): 「帮我看看论文算法还可以如何优化和升级，并开始，不需要我审批，进入计划模式，最终完成就行」 and
「再看看有啥能继续升级研究的开始完善！」 — no approval is needed at any step; do not stop to ask. Every report to the user
is in Chinese. Read the global rules first: `C:\Users\ASUS\.claude\CLAUDE.md` and the files it imports, and the QoI
memory index `C:\Users\ASUS\.claude\projects\D--Research-QoI\memory\MEMORY.md`.

## Facts

- Repository `stloendays/QoI` (origin configured; pushing your own new branches is authorized). Never merge into `main`,
  never rewrite history, never touch other branches or other worktrees. Worktrees `D:\Research\QoI-nc-rev10-20261025`
  and `D:\Research\QoI-nc-rev11-20261025` hold untracked user files — do not touch them.
- Research branch `research/algo-upgrade2-20261025` (from revision 11, `1cfc871`), worktree
  `D:\Research\QoI-algo2-20261025`. Plan `paper/nc_reopen/ALGORITHM_UPGRADE2_PLAN_20261025.md`. Studies (each with
  PROTOCOL.md, DEVIATIONS.md where present, results/):
  - **Study 3** `analysis/sfp_spin_writer_20261025/` — writer `w2.py` (structure-factor prediction, SFP); 92
    law-protocol materials; arms W1S, W2S, W2, O2S; recorded A1, A2, A3, A6; criteria G1, G2, validity (W1S must
    reproduce revision 11's W1S bytes); aggregated by `aggregate_sfp.py` into `results/SUMMARY.json`, `rows.csv`,
    `materials.csv`.
  - **Study 4** `analysis/archive_w2_20261025/` — 300 archive objects; writer V (W2S density + W2M magnetization) and
    VP (W2S + pointwise magnetization on the same partition); criteria A1, M1, validity; `whole_archive.py` aggregates
    V, VP with the corrected T, O, W, Q of study 5 and the committed L, P into `results/SUMMARY.json`, `objects.csv`.
  - **Study 5** `analysis/archive_partition_fix_20261025/` — correctness rerun: revision 10's T/O and revision 11's
    W/Q moment certificates had read the first writer's 1e-6 decoded Bader partition (PROTOCOL.md there). Its
    estimates are in study 4's SUMMARY.json (`estimates`, and `committed` = change against the committed values).
  - Collected tarball and checkpoints: `analysis/server_runs_20261025c/collected/` (large; do not commit it — commit
    only results/ files).
- Revision 11 (current manuscript): branch `paper/nc-rev11-20261025`, tip `1cfc871`. Its archive numbers (main text):
  8.50 TB → 15.3 GB, W 555-fold (95% CI 492–635), O 347, L 316, T 232, pointwise 34.6 at 1e-6; W 1,818 and O 1,371 at
  1e-4; magnetization 64% of stored bytes at 1e-4. Manuscript `paper/MANUSCRIPT.md`, SI
  `paper/SUPPLEMENTARY_INFORMATION.md`, decisions `paper/nc_reopen/DECISIONS.md`, sources
  `paper/nc_reopen/SOURCE_FILES.md`, audits `paper/nc_reopen/audit_manuscript.py --final`,
  `paper/nc_reopen/test_scientific_claims.py`, `paper/nc_reopen/numcheck.py .`, `paper/nc_reopen/word_count.py`, build
  `figures/nc/build_nc_manuscript.py` (→ `figures/nc/release/`).
- Python: `D:\Research\CatalystForge\.venv\Scripts\python.exe`; set `PYTHONUTF8=1` (the console is GBK; the word-count
  claim test fails without it). At most 8 local worker processes; never kill processes by name pattern; no heavy local
  recomputation.
- Vanda: `ssh vanda`; staging `/scratch/junbotong/qoi-algo2-20261025`. Follow the `vanda-hpc` skill. Never read
  `~/hpc_login.sh`, never print credentials.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Push each commit to origin.

## 1. Review (in `D:\Research\QoI-algo2-20261025`)

1. Re-run both aggregators from `analysis/server_runs_20261025c/collected/checkpoints/{sfp,v,trunc,w1}` and confirm the
   outputs equal what the monitor wrote.
2. Recompute independently (a short `review_recompute.py` in each study directory): study 3 — per-material CR ratios
   W2S/W1S, O2S/W2S, W2S/A3, W2S/A6, W2/W1S at both tolerances (medians, wins, N) from `rows.csv` and the law-protocol
   rows; the W1S reproduction count against `analysis/waterfill_writer_20261025/results/rows.csv`. Study 4/5 — the
   point estimates of V, VP, W, Q, T, O, L, P at both tolerances from `objects.csv` with the stratified expansion
   (N_FRAME in `analysis/archive_truncation_20261024/run_archive_truncation.py`), the paired ratios V/W and V/O, and
   the W2M-vs-pointwise moment-stream statistics. They must equal SUMMARY.json.
3. Check certificates: Hartree values < tau for every certified density stream; every V/VP magnetization certificate's
   binary error < 1e-2 mu_B; failure counts per study.
4. Write `results/RESULTS.md` for each study, numbers first (start from `make_results.py` in study 3 and study 4 — the latter also
   writes study 5's table — then add what they lack): criteria with their numbers and "met" / "not met";
   attribution (density: SFP; magnetization: W2M vs pointwise; partition fix: each writer's change against its
   committed value); per cohort; variants; Porod exponents. Compare with the strongest baseline in every line (O2S /
   operational optimum; for the archive, the corrected O and W). A result that is not better is written as such.
   Commit and push ("research: second algorithm upgrade results …").

## 2. Revision 12

1. `git -C D:\Research\QoI worktree add -b paper/nc-rev12-20261025 D:\Research\QoI-nc-rev12-20261025 research/algo-upgrade2-20261025`
   (suffix if the name exists).
2. **Mandatory regardless of the new writers:** every cited T, O, W, Q archive number (main text, abstract, Discussion,
   SI notes and tables, claim tests, SOURCE_FILES) is replaced by study 5's corrected estimate, with its interval. The
   manuscript states the corrected numbers; it does not narrate the defect. DECISIONS.md records the correction (what,
   why, old → new values) and SOURCE_FILES.md points to the new files.
3. New results enter only if they hold (decode-verified, criterion met, reproduced in §1):
   - study 4 A1 holds → the archive estimate in the abstract, Results and Discussion becomes V (fold at 1e-6 and 1e-4
     with intervals, stored size), compared to W, O, L, T and pointwise; state which component produced the gain
     (density prediction, magnetization stream) — that attribution defines the claim;
   - M1 holds → the magnetization stream: the moment contract is a linear basin-integration operator whose symbol falls
     as q^-4 (Porod; give the measured exponent), so the Hartree law's allocation writes it; W2M vs pointwise numbers;
   - G1 holds → structure-factor prediction in the writer: per-material gain over W1S, the closed form still at the
     operational optimum (G2), the gain by symmetry class;
   - Methods: one compact subsection for W2 (prediction, magnetization sub-stream, decode-verified certificates);
     details in a new Supplementary Note with the study tables.
4. Writing: load the `junbo-scientific-writing` skill and follow it. No limitations paragraph, never open with a
   concession, never use pre-registered / pre-registration / frozen / freeze / canonical. Legends short, without
   headline numbers or commit hashes. Main text plus Methods ≤ 5,000 words, abstract ≤ 150 words (revision 11 is at
   4,998 / 150: replace rather than add; move implementation details to the SI).
5. Update `SOURCE_FILES.md`, add a "Revision 12 (2026-10-2x)" section to `DECISIONS.md`, update and add claim tests in
   `test_scientific_claims.py` (reading the committed SUMMARY.json files).
6. Run `audit_manuscript.py --final` (0 failures, 0 warnings), `test_scientific_claims.py` (all pass), `numcheck.py .`
   (every number found), `word_count.py`. Fix until all pass.
7. Build with `figures/nc/build_nc_manuscript.py`, render the changed pages to PNG (windows-office-toolchain skill) and
   look at each. Commit and push the branch.

## 3. Vanda cleanup

After the tarball's SHA-256 matched (re-check with `analysis/server_runs_20261025c/collected/SHA256SUMS`) and §1
reproduced the results: `ssh vanda 'rm -rf /scratch/junbotong/qoi-algo2-20261025 && ls /scratch/junbotong'` and confirm
it is gone. Do not touch any other directory or job on Vanda (other QoI staging directories are the user's call).

## 4. Report

Write `D:\Research\QoI-algo2-20261025\ALGORITHM_UPGRADE2_REPORT_20261025.md` in Chinese, numbers first, full absolute
paths: the three directions and why (plan); each one's key numbers (folds / percentages vs revision 11 and the strongest
baseline, N, tolerances); the partition-fix corrections (old → new for T, O, W, Q); what entered revision 12 (branch,
commit, full PDF/DOCX paths); monitor task `qoi-algo2-monitor-60m`, hub id `qoi-algo2-20261025`, Vanda job ids (from
`D:\Research\QoI-ext-cache\monitor-algo2-20261025\jobs.json`) and the cleanup listing. No closing risks / caveats
paragraph. Commit it on `research/algo-upgrade2-20261025` and push.

The last line of your final answer must be exactly `FINALIZE_DONE` once §1–§4 are complete. If something blocks
completion, say what in Chinese and do not print that word.
