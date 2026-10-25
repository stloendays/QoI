# Vanda runs of 2026-10-25 (second algorithm upgrade)

Studies `analysis/sfp_spin_writer_20261025/` (W2 writer on the 92 law-protocol materials),
`analysis/archive_w2_20261025/` (300 archive objects, writers V and VP) and `analysis/archive_partition_fix_20261025/`
(revision 10's T/O and revision 11's W/Q with every decoded partition rebuilt). Staging
`/scratch/junbotong/qoi-algo2-20261025/`, project CFP04-CF-046, queue `auto`.

Driven end to end by `C:\Users\ASUS\.claude\tools\qoi_algo2_monitor.py` (stage → install → prefetch → probe →
production → collect → finalize). Do not qsub by hand; read the monitor's `STATUS.md` first.

| script | what |
|---|---|
| `vanda/install.sh` | login node: venv with the frozen pins, Bader 1.05 |
| `vanda/prefetch.py` | login node: 300 archive objects, 92 cohort sources, the development material |
| `vanda/probe.pbs` | W2 tests, development known answer, two cohort materials, two archive objects (V and the fix) |
| `vanda/production_sfp.pbs` | study 3, 92 materials |
| `vanda/production_v_small.pbs`, `production_v_large.pbs` | study 4 |
| `vanda/production_fix_small.pbs`, `production_fix_large.pbs` | study 5 |
| `vanda/collect.sh` | tarball of checkpoints, probe and logs with SHA-256 |
| `FINALIZE_TASK.md` | the headless finalization the monitor starts after collection |

Commits: protocols, writer, runners, tests and Vanda scripts `4102390` (2026-10-25 15:01 UTC); collected results, review recomputation and RESULTS.md `c68c605` (2026-10-25 22:42 UTC).
