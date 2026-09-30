# WP-B deviations and execution notes

Recorded before the corresponding step was (re)run. None of the pre-declared analysis
rules of PROTOCOL.md (WP-B) was changed.

1. **Execution platform.** The protocol names the P2 stack as Ubuntu / Python 3.12.14 with the
   pinned `validation/requirements-external-e2e.txt` (commit 893f931). This package ran on
   Windows 11 with the same Python 3.12.14 and the same pinned scientific packages
   (numpy 2.4.6, baderkit 0.10.2, pysz 1.0.3, zfpy 1.0.1, hdf5plugin 7.0.0, h5py 3.16.0,
   pymatgen 2025.10.7, scipy 1.18.1, numba 0.65.1, llvmlite 0.47.0, pandas 2.3.3) from the
   pre-existing environment `D:\Research\QoI-final4-local\venv`. The cross-platform
   reproduction is verified inside the package itself (RESULTS.md, "Reproduction of the frozen
   stack"): realized L∞, re-derived Bader errors and the fresh-probe Bader responses are
   compared row by row with the frozen values.

2. **Frozen checkout path.** The frozen scientific implementation (commit
   893f931b3045b0b628329db81999c2f439d4e830) was taken from the already existing detached
   worktree `D:\Research\QoI-final4-local\frozen_repo` instead of creating a new `../frozen`
   worktree. Its HEAD is recorded in `provenance.json`.

3. **Fresh work-order epsilon text.** `validation/qsq_prospective/fresh_seed_jobs.csv` stores
   `epsilon` with 15 significant digits (e.g. `3.05143749983472e-05`), whereas
   `stability/stability_floor_A1_per_seed.csv` stores `probe_linf` in full precision
   (`3.0514374998347197e-05`) and the executed P2 run (`p2_fresh_probes/outcomes.csv`) used the
   full-precision value. Following the protocol (amplitude = the material's `probe_linf`), this
   package uses `probe_linf` and checks the work-order value against it with a relative
   tolerance of 1e-12 instead of exact string equality. Stream seeds are checked exactly
   against the SHA-256 rule of `run_p2_fresh_probes.py`.

4. **Bader re-solve on perturbation probes.** The protocol requires re-derived Bader error on
   the reconstruction rows (analysis 5). Because wall time allowed it, the Bader response was
   also re-derived for all 64 perturbation probes per material; the frozen values from the
   per-seed table and from P2 are kept beside them in `cp_probes.csv` as a reproduction check.
   The frozen Bader eligibility (stability floor < 1e-3 e) used in analysis 3 is taken from the
   frozen tables, not from the re-derived values.

5. **Eligibility at τ_cp = 0 with an incomplete five-seed set.** A material with any failed
   seed has no defined floor and is counted as screen-rejected (never as eligible). The number
   of such materials is reported in RESULTS.md (analysis 1, "floor defined").

6. **Density cache and checkpoints.** Source densities are cached once at
   `D:\Research\QoI-ext-cache\densities\<sha256>.bin` and SHA-256/byte-count verified on every
   read; per-material checkpoints live in `D:\Research\QoI-ext-cache\WP-B\checkpoints` (outside
   the repository, so a restart resumes). Both paths are recorded in `provenance.json`.

7. **baderkit IndexError on coarse ZFP reconstructions (execution note, 2026-09-29).** At
   194/254 materials, 14 reconstruction rows in 13 materials failed at stage `codec_or_qoi`,
   all ZFP at nominal relative tolerance 0.01–0.1; no perturbation probe failed. A standalone
   reproduction of mp-753392 / ZFP / 0.1
   (`D:\Research\QoI-ext-cache\monitor\diag\diag_wpb_indexerror.py`) passes the reproduction gate
   (realized/stored L∞ = 1.000) and computes the critical-point QoI (n_max = 82). The exception
   is raised inside baderkit 0.10.2 during the Bader re-solve
   (`ongrid_method._run_bader` → `base.condense_images`, `shift_map[images[:,0], ...]`,
   "index -4 is out of bounds for axis 1 with size 3"). The frozen Ubuntu benchmark stores a
   Bader error for the same row, so the crash is specific to this platform/run. Following the
   shared rules these rows stay in `failures.csv` and in every denominator; no rule was changed.

8. **Critical-point result kept when the Bader re-solve fails; affected materials re-run
   (runner change, 2026-09-29).** When the first pass ended (254/254 materials, 15:21), 50 of the
   6,343 planned reconstruction rows, in 42 materials, had failed at stage `codec_or_qoi`. Every
   one raised the baderkit `IndexError` of item 7 ("index 3 / -4 is out of bounds for axis 0/1/2
   with size 3"). By codec: ZFP at nominal relative tolerance 0.003 / 0.01 / 0.03 / 0.1 had
   1 / 9 / 15 / 4 rows, and SPERR at 1e-4 / 3e-4 / 1e-3 had 5 / 14 / 2. No perturbation probe
   failed. The SPERR and low-tolerance ZFP rows were checked as in item 7, using
   `D:\Research\QoI-ext-cache\monitor\diag\diag_wpb_indexerror_codec.py` on nomad-0xMhYZKiiVKL
   SPERR / 3e-4 and ZFP / 0.003. Both pass the reproduction gate (ratio 1.000) and the
   critical-point QoI computes (n_max = 72,422 and 30). The exception is raised in baderkit 0.10.2
   `base.condense_images`.

   *What changed and why.* `run_wpb.py` scored the critical-point QoI and re-solved Bader for a
   reconstruction row inside one `try` block. A Bader crash therefore also discarded the
   critical-point result, which had already been computed on a gate-passing reconstruction. Now
   the critical-point fields are written first, and the Bader re-solve has its own inner `try`:
   - If Bader succeeds, the row is written exactly as before, with status `SUCCESS`.
   - If Bader fails, the critical-point fields are kept and the row status is `CP_ONLY`.
     `bader_error_resolved_e`, `bader_error_abs_diff_vs_stored_e`, `n_voxels_reassigned`,
     `labels_sha256` and `bader_seconds` are left empty. The row is still written to
     `cp_rows.csv`, and a separate failure record with stage `bader` goes to `failures.csv`.

   The perturbation-probe loop has the same structure. It had no failures and was not changed.

   The change affects only how a failure is recorded. No QoI definition, reproduction gate,
   eligibility rule, analysis or acceptance rule was changed. The `CP_ONLY` rows stay in
   `failures.csv` and in every denominator. `analyze_wpb.py` counts `SUCCESS` rows plus failure
   records, so each of these rows is counted once, as a failure.

   Before the re-run, a regression test of the patched runner was run on mp-753392 with
   `bader_split_20260929\test\test_patched_runner.py`. It reproduced the first-pass reference and
   two passing rows in every non-timing field, and it turned ZFP / 0.1 into `CP_ONLY`
   (n_max = 82).

   *Execution.* Everything below is stored under `D:\Research\QoI-ext-cache\WP-B\bader_split_20260929\`.
   - The first-pass checkpoints of the 42 materials were moved, not deleted, to
     `checkpoints_first_pass\`, with a SHA-256 manifest in `SHA256SUMS`.
   - The first-pass aggregate outputs are in `first_pass_outputs\`.
   - The original runner is `run_wpb.original.py` (SHA-256 4bdec8f1…55fc0b69a3).
   - The 42 materials were then re-run with the recorded command `run_wpb.py --workers 4`,
     which processes only materials without a checkpoint.

   Re-run materials: mp-1175263, mp-1247173, mp-1303576, mp-17103, mp-1841520, mp-675781,
   mp-753392, mp-756647, mp-782011, mp-864652, nomad--5wLHf6mG5_K, nomad--O7C25L6mxPu,
   nomad--maT57oivXnQ, nomad--ydxPkR4Tatz, nomad-0-ostsntWIk9, nomad-064_5lUOyDQI,
   nomad-0HydAdmxidgt, nomad-0pSeEEz7rc0X, nomad-0xMhYZKiiVKL, nomad-19wSfSWChOSI,
   nomad-1Few3hG0Dkat, nomad-1xNwoQ8q8XXI, nomad-3ermMygSkKxT, nomad-4BR68d4gtTyq,
   nomad-4CA6DwNaypkT, nomad-4hOaTvLmAUuc, nomad-4khM-ZQ6rM_L, nomad-5_7vAQzUevH0,
   nomad-8Hl4JATTj5Fp, nomad-8ZPelCNdN_TR, nomad-8eTSyDPSGSwy, nomad-9jQMkfdCbgX_,
   nomad-A5zDMCxBBUYc, nomad-BbyKgzzvPkrI, nomad-E0rr8BI_hRlR, nomad-Ek0B30z0bVyP,
   nomad-FVlJ8rpkyGT5, nomad-M8BV9zowas8w, nomad-Q4xDULo89hwd, nomad-SzuB_oB4XzfT,
   nomad-VyA9ivUfcKNR, nomad-Z7Uu-1P6k4r9.

   *Outcome.* The re-run ran on 2026-09-29 from 15:23 to 22:04 (job
   `qoi-WP-B-rerun-bader-split`) and ended with 254/254 checkpoints. `verify_rerun.py` compared
   each re-run material with its archived first-pass checkpoint:
   - The reference, all 2,688 probes and all 1,016 first-pass rows are identical in every
     non-timing field.
   - All 50 former `codec_or_qoi` rows are now `CP_ONLY`. Each has a stage-`bader` failure
     carrying the same `IndexError`.

   `cp_rows.csv` now has 6,343 rows: 6,293 `SUCCESS` and 50 `CP_ONLY`. `failures.csv` has 50
   entries, all at stage `bader` and none at `codec_or_qoi`.

   `run_wpb.py` rewrites `population.json` on every invocation. The re-run's copy differed only
   in `declared_at`, so the original declaration (2026-09-28 16:52:03) was restored, and the
   re-run's copy is kept as `population.rerun_invocation.json`. `run_log.txt` covers both
   invocations.

9. **Bootstrap interval with infinite resamples (analysis fix, 2026-09-30).** In the primary
   prospective endpoint no cp-eligible trial exceeded (0/6962), so the risk ratio and all 2,000
   bootstrap resamples are +inf. `ClusterBootstrap.ci` returned NaN whenever no resample was
   finite, and linear interpolation between two +inf order statistics also produced NaN. The
   CI lower bound was therefore reported as n/a, and the acceptance rule (RR > 5 and lower
   bound > 1) evaluated as not met although every resample satisfies it. The percentile is now
   taken over the ordered resamples with +inf kept at the top, so an interpolation touching
   +inf yields +inf; any NaN resample still gives an undefined interval, as before. Finite
   intervals are unchanged (the only RESULTS.md lines that changed are the primary RR interval,
   the secondary RR upper bound and the verdict). The acceptance rule itself is unchanged.
   The reproduction section also now reports how many re-derived Bader errors fall on the same
   side of 1e-3 e as the stored value (6290/6293); the magnitude differences are confined to
   rows already above that threshold (1320 of the 1325 rows differing by more than 1e-6 e).
