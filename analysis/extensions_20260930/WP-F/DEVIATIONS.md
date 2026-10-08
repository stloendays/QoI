# WP-F deviations and execution notes

Recorded before the affected step runs. No pre-declared analysis, estimator, storage rule or
acceptance criterion is changed.

1. **Execution platform.** Windows 11 with the pinned scientific stack in
   `D:\Research\QoI-final4-local\venv`, as WP-B ran (WP-B `DEVIATIONS.md` 1); the protocol names this
   stack. Certificates therefore certify this fixed pipeline.

2. **Ladder only where a certificate is possible (2026-09-30, before the first sampled density was
   read).** The protocol's D01–D09 text says the full union ladder is evaluated for every object. The
   runner evaluates it only for objects that are QSQ-eligible at the loosest τ (f_m < 1e-2 e). For an
   object not eligible at 1e-2 e it is not eligible at any τ, the storage rule assigns lossless bytes at
   every τ, and none of the pre-declared endpoints (R(τ), non-evaluable fractions, codec mix, the
   prospective writer check, which is defined over eligible objects) uses its ladder. Skipping it
   changes no reported number and saves about one sixth of the Bader solves.

3. **Processing order.** Within each group objects are processed smallest first, so that memory-heavy
   objects come last; the order cannot change any per-object result.

4. **Workers and memory (2026-09-30, before launch).** The protocol's cost note assumed 4 workers for
   D01–D09 alongside 1 for D10. Only about 5 GB of RAM was free at launch, so the groups run one after
   the other: D01–D09 with 3 workers, then D10a–D10c with 1 worker. An object whose worker process dies
   (the pool reports it; typically memory) is re-run once on its own after its group finishes; the
   second outcome is final and is what the protocol's "attempted once, then counted as failed" refers
   to, so that a failure reflects the object and not the scheduling.

5. **Known baderkit failure on the coarsest ZFP rung (execution note, 2026-09-30).** A few objects raise
   baderkit 0.10.2's `IndexError: index 3 is out of bounds for axis … with size 3` on the ZFP 1e-1 rung,
   the same crash WP-B recorded (WP-B `DEVIATIONS.md` 7). The rung is recorded in `failures.csv` with the
   object, is never certified, and the object's other rungs and its storage outcome are unaffected
   (a 1e-1 ZFP rung is far above any certifiable tolerance in these data). Object-level failures remain
   governed by the storage rule.

6. **Laptop run as recorded (stopped 2026-10-04 17:00 +08:00).** The checkpoints of the laptop run are
   committed unchanged in `results_laptop/checkpoints/` (300 files, SHA-256 in
   `results_laptop/CHECKPOINTS.sha256`): 243 SUCCESS, 57 FAILED. Every SUCCESS object is in the small
   group (D01–D09). Every FAILED object ended with `BrokenProcessPool` after its deviation-4 retry
   (`retried: true`): the worker process was killed, with about 5 GB of free RAM. Failed by stratum:
   D09 27/30, D10a 15/15, D10b 10/10, D10c 5/5. No WP-F estimator has been run on these checkpoints.

7. **Execution platform change for the 57 FAILED objects (author decision, 2026-10-07, recorded before
   any object runs on the new platform).** The author directed completion of the sample in the cloud
   ("WP-F：……在 DEVIATIONS 记下平台变更，云端重跑 5 个已完成对象核对一致后，再补完剩下的").
   - Platform: GitHub-hosted `ubuntu-24.04` runners (about 16 GB RAM), one object per job, one worker,
     with the frozen stack of deviation 1: `validation/` of commit `893f931` and its
     `requirements-external-e2e.txt`, Python 3.12, as the repository's other CI workflows install it.
     Paths that `run_wpf.py` hard-codes for the laptop (`FROZEN_VALIDATION`, `CACHE`, `CKPT`) become
     overridable by environment variables; nothing else in the runner changes.
   - Consistency check first. The five SUCCESS objects that are eligible at 1e-2 e and have the smallest
     SHA-256 of the UTF-8 task id are rerun on the new platform: `mp-2488566` (D03), `mp-2285510` (D06),
     `mp-2050393` (D03), `mp-2367698` (D07), `mp-2682232` (D05). The platforms agree if, for each of
     them, eligibility at all three τ, the certified flag of every evaluated rung and the writer choice
     (codec and rung) at each τ are identical; compressed bytes of every rung agree within 0.1%; and the
     floor, every probe response and every rung's Bader error agree within 1e-6 e. The comparison is
     committed as `results_cloud/CONSISTENCY.md`. If the platforms do not agree, the 57 objects are not
     run and the disagreement is reported.
   - Completion. If they agree, the 57 FAILED objects run once each on the new platform under the
     protocol's per-object procedure and storage rule. An object that fails there (including memory) is
     final and counted under the storage rule. The 243 laptop SUCCESS checkpoints are used as recorded.
   - Reporting. The estimators of the protocol, unchanged, are reported on (a) the completed sample (243
     laptop + 57 cloud outcomes), the endpoint the author asked for, and (b) the laptop run as frozen,
     with the 57 objects counted as failed under the storage rule, so that the effect of this change is
     visible.

8. **Cloud execution infrastructure (2026-10-07, recorded before any object runs in the cloud).** How
   deviation 7 is executed; no estimator, weight, failure rule or acceptance rule changes.
   - Workflow `.github/workflows/wpf_cloud_completion.yml`. It fires only on a push to
     `research/wpf-cloud-completion-20261007` that changes the sentinel `results_cloud/RUN_REQUEST`, whose
     first line names the phase (`consistency`, `completion`, `estimators`) and whose further lines name
     the task ids. The preflight refuses any id set other than the five consistency objects of deviation 7
     or exactly the 57 FAILED laptop objects, refuses `completion` unless `results_cloud/consistency/
     CONSISTENCY.json` records agreement, and verifies `results_laptop/CHECKPOINTS.sha256` before every
     phase.
   - Path overrides. `run_wpf.py` reads `WPF_FROZEN_VALIDATION`, `WPF_CACHE`, `WPF_CKPT`;
     `analyze_wpf.py` reads `WPF_CKPT` (checkpoint directory read) and `WPF_OUT` (directory its outputs are
     written to). Unset, both scripts behave exactly as on the laptop.
   - Per object. One GitHub-hosted `ubuntu-24.04` job per object, fresh runner, no carried-over cache:
     `run_wpf.py --group <group of its stratum> --workers 1 --only <task_id>`, i.e. D01–D09 objects with the
     full union ladder and D10a–D10c objects with the adopted WP-E policy, as on the laptop. The thread
     settings are the runner's own defaults (unchanged).
   - Job time limit. GitHub-hosted jobs stop at 6 h. The runner is given 340 min; an object still running
     then is stopped and recorded as FAILED with stage `worker` (the record the runner itself writes when its
     worker process dies) and an error naming the time limit. An object whose job ends without returning a
     checkpoint (e.g. the runner host lost to memory exhaustion) is recorded the same way by the collecting
     job. Both are final and counted under the storage rule, as deviation 7 says for any cloud failure.
   - Certified flag (deviation 7 rule). Compared for every evaluated rung as the rung's
     `certifiable_error` flag and as "certified at τ" (status OK, bound respected, Bader error < τ — the
     rule of the runner and of the estimator) at each of the three τ; the evaluated rung sets must also be
     identical. The comparison is `compare_consistency.py`; the five cloud reruns are committed under
     `results_cloud/consistency/checkpoints/` and are used by no estimator (the laptop checkpoints of these
     objects are used as recorded).
   - Estimators. `analyze_wpf.py` runs on GitHub-hosted `ubuntu-24.04` with Python 3.12.14, numpy 2.4.6
     and pandas 2.3.3 (the frozen stack's versions) and matplotlib 3.11.1 and tabulate 0.10.0 (the versions
     of the laptop's frozen environment). Input (a) is a directory holding the 243 laptop SUCCESS
     checkpoints byte-identical plus the 57 cloud checkpoints; input (b) is `results_laptop/checkpoints/`
     itself. Arial is not installed on the runner, so the figure's text is set in matplotlib's fallback
     font; no number depends on it.

9. **Author decision on platform consistency (2026-10-07, after `results_cloud/CONSISTENCY.md`, before any of
   the 57 objects runs).** The deviation-7 comparison returned DISAGREE on its literal rule: 1405 of 1409 checks
   agree. Every decision field is identical on the two platforms: eligibility at the three τ, the evaluated
   rung sets, every rung's status, certifiable-error flag and certified-at-τ flag, and the writer choice. The
   compressed bytes, floors and all 25 probe responses are also identical. The four failed checks are rung Bader
   errors that differ by 3.6e-5 to 1.8e-3 e. All four sit on the coarsest rungs (SPERR 3e-3 and 3e-2, ZFP 1e-1),
   whose Bader errors are 0.067–0.93 e and therefore far above every τ. The author judged the platforms
   consistent ("判定一致，补跑 57 个") and directed the completion phase to run.
   - Consequences:
     - the 57 FAILED objects run as deviation 7 says;
     - the completion preflight accepts this entry in place of an agreement record in
       `results_cloud/consistency/CONSISTENCY.json` (infrastructure only);
     - `CONSISTENCY.md` stays as recorded.
   - No estimator, weight, failure rule or acceptance rule changes. Reporting (a) and (b) of deviation 7 is
     unchanged.

10. **Preflight for entry 9 (infrastructure, 2026-10-07, before the completion sentinel is pushed).** The
    `completion` and `estimators` preflights of `wpf_cloud_completion.yml` now pass when `CONSISTENCY.json`
    records agreement or `DEVIATIONS.md` contains the heading of entry 9; `CONSISTENCY.md`/`.json` are unchanged.

11. **Estimators rerun (infrastructure, 2026-10-08, before the rerun).** The first estimators run (37714409792)
    computed both output sets but could not commit them: importing `figures/composite/style.py` rewrote the
    tracked `figures/composite/__pycache__/*.pyc`. The estimator step now runs with `PYTHONDONTWRITEBYTECODE=1`
    and the phase is rerun unchanged otherwise; `COMPLETION_FAILURES.md` records the cause of each of the 12
    completion failures from GitHub's job records (no artifact, hence no memory log, exists for them).

12. **Author decision: rerun the six never-started objects (2026-10-08, before they run).** Six of the 12
    completion failures never ran: their jobs acquired no runner after five attempts, so `run_wpf.py` never
    started (`COMPLETION_FAILURES.md`). These are mp-1826245, mp-2046569, mp-2234070 and mp-3092553 (D09),
    mp-1543577 (D10a) and mp-2355832 (D10b). The author directed that these six run once each ("重跑这 6 个").
   - Unchanged:
     - every other rule of deviations 7–8;
     - the six objects whose runner was lost after 114–349 min of `run_wpf.py`, which remain final failures;
     - estimate (b), the laptop run as frozen.
   - Once the six have run, estimate (a), the completed sample, is recomputed with their outcomes. Any failure
     of the rerun is final and is counted under the storage rule.
   - The first estimate (a) (`17c5b6d`) is kept in the record.

13. **Infrastructure for entry 12 (2026-10-08, before the six run).** The preflight accepts a `completion` request
    for exactly the six objects of entry 12 (once, only while entry 12 is present and their records are the
    never-started `NoArtifact` ones). Their outcomes are collected into `results_cloud/rerun_dev12/`, beside the
    first records in `results_cloud/checkpoints/`, which stay as recorded. A new phase `estimators_v2` runs
    `analyze_wpf.py` on 243 laptop + 51 first-run cloud + the 6 rerun checkpoints into
    `results_cloud/completed_v2/`. Everything else is as in entries 8 and 11.
