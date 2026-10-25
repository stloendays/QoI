# Finalization task — QoI algorithm upgrade (2026-10-25): review, revision 11, report, cleanup

You are a headless Claude Code run started by the monitor `C:\Users\ASUS\.claude\tools\qoi_algo_monitor.py` after the
Vanda results of both studies were collected, SHA-256-checked and aggregated. The user is not present. The user's
instruction (2026-10-25 14:54): 「帮我看看论文算法还可以如何优化和升级，并开始，不需要我审批，进入计划模式，最终完成就行」 —
no approval is needed at any step; do not stop to ask. Every report to the user is in Chinese. Read the global rules
first: `C:\Users\ASUS\.claude\CLAUDE.md` and the files it imports, and the QoI memory index
`C:\Users\ASUS\.claude\projects\D--Research-QoI\memory\MEMORY.md`.

## Facts

- Repository `stloendays/QoI` (origin configured; pushing your own new branches is authorized). Never merge into `main`,
  never rewrite history, never touch other branches or other worktrees. Worktree `D:\Research\QoI-nc-rev10-20261025`
  holds two untracked user files — do not touch that worktree.
- Research branch `research/algo-upgrade-20261025`, worktree `D:\Research\QoI-algo-upgrade-20261025`. Plan
  `paper/nc_reopen/ALGORITHM_UPGRADE_PLAN_20261025.md`. Studies (each with PROTOCOL.md, DEVIATIONS.md, results/):
  - `analysis/waterfill_writer_20261025/` — 92 law-protocol materials; arms L1, W1, W1S, T1S, O1, O1S; recorded A1, A2,
    A3, A6; criteria H1–H3 and validity in PROTOCOL.md §5; aggregated by `aggregate_w1.py` into `results/SUMMARY.json`,
    `results/rows.csv`, `results/materials.csv`.
  - `analysis/archive_waterfill_20261025/` — 300 archive objects; writers W (W1S) and Q (O1S) against the recorded
    L, P, T, O; aggregated by `run_archive_w1.py aggregate` into `results/SUMMARY.json`, `results/objects.csv`.
  - Collected tarball and checkpoints: `analysis/server_runs_20261025b/collected/` (not to be committed: it is large;
    commit only results/ files).
- Revision 10 (current manuscript): branch `paper/nc-rev10-20261025`, tip `0d74c39`. Its numbers: archive 8.50 TB;
  at 1e-6 A3 347-fold (95% CI 317–387), law 316, truncation 232, pointwise 34.6; at 1e-4 A3 1,371, law 1,036,
  truncation 1,142. Manuscript `paper/MANUSCRIPT.md`, SI `paper/SUPPLEMENTARY_INFORMATION.md`, decisions
  `paper/nc_reopen/DECISIONS.md`, number sources `paper/nc_reopen/SOURCE_FILES.md`, audits
  `paper/nc_reopen/audit_manuscript.py --final`, `paper/nc_reopen/test_scientific_claims.py`,
  `paper/nc_reopen/numcheck.py`, `paper/nc_reopen/word_count.py`, build `figures/nc/build_nc_manuscript.py`
  (→ `figures/nc/release/NC_manuscript_<date>.{pdf,docx}`).
- Python: `D:\Research\CatalystForge\.venv\Scripts\python.exe` (numba, pymatgen, pytest available). At most 8 local
  worker processes; never kill processes by name pattern. Laptop memory is small — no heavy local recomputation.
- Vanda: `ssh vanda`; staging `/scratch/junbotong/qoi-algo-20261025`. Follow the `vanda-hpc` skill. Never read
  `~/hpc_login.sh`, never print credentials.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Push each commit to origin.

## 1. Review (in `D:\Research\QoI-algo-upgrade-20261025`)

1. Check `git status`; the monitor wrote the aggregated `results/` of both studies. Re-run both aggregators yourself
   from `analysis/server_runs_20261025b/collected/checkpoints/{w1,arch}` and confirm the outputs are identical.
2. Recompute the key ratios from the rows, independently of the aggregator (a short script you keep under
   `analysis/waterfill_writer_20261025/review_recompute.py`): per-material CR ratios O1S/W1S, W1S/T1S, W1S/A3, W1S/A1,
   W1S/A6, L1/A1, W1/L1, W1S/W1 at 1e-6 and 1e-4 (medians, win counts, N), using `results/rows.csv` and the law
   protocol rows `analysis/general_qoac_law/results/run_{P1,P3B}_CONFIRMATORY/part_a_rows.csv` (smallest certified
   stream per arm). They must equal SUMMARY.json. For the archive, recompute R_W and R_Q point estimates from
   `results/objects.csv` and the committed records with the stratified expansion formula (strata sizes N_FRAME in
   `analysis/archive_truncation_20261024/run_archive_truncation.py`).
3. Check every certified stream's certificate values (hartree_hist, hartree_safe < tau) in rows.csv and the failure
   list; count failures per study.
4. Write `results/RESULTS.md` for each study, numbers first: criteria H1, H2, H3, validity each with its number and
   "met" / "not met"; the attribution ladder; per-cohort values; symmetry statistics; the archive table (R with
   intervals for P, T, L, O, W, Q at 1e-6 and 1e-4, paired ratios). Compare with the strongest baseline in every line:
   the operational optimum under the same coder (O1S) and, for the archive, revision 10's O (347/1,371). A result that
   is not better is written as such and stays. Commit and push ("research: algorithm upgrade results …").

## 2. Revision 11 (only for results that hold)

A result "holds" if it is decode-verified, its criterion (study 1) is met or its improvement over the revision-10 value
is outside the revision-10 interval (archive), and the review in §1 reproduced it.

1. `git -C D:\Research\QoI worktree add -b paper/nc-rev11-20261025 D:\Research\QoI-nc-rev11-20261025 research/algo-upgrade-20261025`
   (add a suffix if the name exists).
2. Load the `junbo-scientific-writing` skill and follow it. Main text has no limitations paragraph, never opens with a
   concession, and never uses pre-registered / pre-registration / frozen / freeze / canonical. Figure legends stay
   short, without headline numbers or commit hashes. Main text plus Methods ≤ 5,000 words, abstract ≤ 150 words
   (revision 10 is at 4,998 / 150: replace numbers and sentences rather than add; move implementation details to the
   SI if needed).
3. Content to write (adapt to what held):
   - the archive estimate in the abstract, Results archive paragraph and Discussion: the W writer's fold reduction at
     1e-6 and 1e-4 with intervals, the comparison to the operational allocation under the same writer (Q) and to the
     revision-10 writers, stating which component produced the gain (allocation, entropy coding, symmetry) — that
     attribution defines the claim;
   - the law: the water-filling closed form needs no search and stores as little as the searched allocation under the
     same writer (H1 numbers) and beats truncation (H2), which removes the loose-tolerance crossover;
   - Methods: one compact subsection for the W1 writer (water-filling rule, container, adaptive coder, symmetry
     prediction, decode-verified certificate); details to a new Supplementary Note;
   - SI: a Supplementary Note with the study-1 tables (arms, criteria, attribution, per cohort) and the archive table;
   - `paper/nc_reopen/SOURCE_FILES.md`: every new number with its source file;
   - `paper/nc_reopen/DECISIONS.md`: a "Revision 11 (2026-10-2x)" section (request, what changed, word count, audits);
   - `paper/nc_reopen/test_scientific_claims.py`: claim tests for the new archive numbers and the H1/H2 numbers,
     reading the committed SUMMARY.json files.
4. Run `audit_manuscript.py --final` (0 failures, 0 warnings), `test_scientific_claims.py` (all pass), `numcheck.py`
   (every number found in committed sources), `word_count.py`. Fix until all pass.
5. Build with `figures/nc/build_nc_manuscript.py` (PDF and DOCX under `figures/nc/release/`), render the changed pages
   to PNG (windows-office-toolchain skill) and look at each changed page. Commit and push the branch.
6. Results that do not hold are not written into the manuscript; they stay in the studies' RESULTS.md and the report.

## 3. Vanda cleanup

After the collected tarball's SHA-256 matched (the monitor checked it; re-check with
`analysis/server_runs_20261025b/collected/SHA256SUMS`) and §1 reproduced the results, delete the staging directory:
`ssh vanda 'rm -rf /scratch/junbotong/qoi-algo-20261025 && ls /scratch/junbotong'` and confirm it is gone. Do not touch
any other directory or job on Vanda.

## 4. Report

Write `D:\Research\QoI-algo-upgrade-20261025\ALGORITHM_UPGRADE_REPORT_20261025.md` in Chinese, numbers first, with full
absolute paths: the chosen directions and why (from the plan); each direction's key numbers (folds / percentages vs
revision 10 and vs the strongest baseline, N, tolerances); what entered revision 11 (branch, commit, full PDF/DOCX
paths); monitor task `qoi-algo-monitor-60m`, hub id `qoi-algo-20261025`, Vanda job ids (from
`D:\Research\QoI-ext-cache\monitor-algo-20261025\jobs.json`) and the cleanup listing. No closing risks / caveats
paragraph. Commit it on `research/algo-upgrade-20261025` and push.

The last line of your final answer must be exactly `FINALIZE_DONE` once §1–§4 are complete. If something blocks
completion, say what in Chinese and do not print that word.
