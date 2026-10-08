# Vanda manifest — everything this cohort created on the server

Staging root: `/scratch/junbotong/qoi_selfslab_20261007/` (scratch, not home). Nothing was created under
`/home/svu/junbotong`. Files are deleted only after the author confirms the local copies (PROTOCOL.md section 8).

| path (under the staging root) | created | what |
|---|---|---|
| `runs/` | 2026-10-08 00:26 SGT | 40 run directories `<draw_rank>_<material_id>/`, one per drawn slab |
| `runs/<dir>/POSCAR, KPOINTS, INCAR_normal, INCAR_all, POTCAR.spec` | 2026-10-08 00:26 | inputs, byte copies of `inputs/<dir>/` (SHA-256 in `inputs/inputs.csv`) |
| `runs/<dir>/POTCAR` | 2026-10-08 00:27 | assembled on the server by `make_potcar.sh` from `potpaw_PBE.54`; never copied off the server |
| `runs/<dir>/INCAR, OSZICAR*, OUTCAR*, CHGCAR, AECCAR0, AECCAR1, AECCAR2, vasp_*.out, STATUS, ...` | at run time | VASP output of each run (CHG and WAVECAR removed by the job) |
| `runs/STATUS.tsv` | at run time | one line per finished slab: dir, status, start and end epoch, job id |
| `potcar_headers.tsv` | 2026-10-08 00:27 | TITEL and ZVAL of each POTCAR entry (copied to `inputs/potcar_headers.tsv`) |
| `make_potcar.sh`, `job_bundle.pbs.template` | 2026-10-08 00:26 | copies of `vanda/` |
| `jobs/<bundle>.pbs` | 2026-10-08 onward | job scripts (copies of `vanda/jobs/`), PBS logs `qoi_ss_<bundle>.o<id>` written next to them |

Staged size before any run: 30 MB, 244 files.

## Jobs

| bundle | job id | slabs (draw rank) | submitted | state |
|---|---|---|---|---|
| pilot | 1439802.stdct-mgmt-02 | 1 | 2026-10-08 00:28 SGT | finished 00:29, Exit 0, converged_normal (`runs/PILOT.md`) |
| b1 | 1439805.stdct-mgmt-02 | 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38 | 2026-10-08 00:33 SGT | CN-104, 00:33:15–01:16:19, walltime 43 min, 7.7 GB; Exit 3 (draw rank 11 `nelm_twice`; 12 converged) |
| b2 | 1439806.stdct-mgmt-02 | 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39 | 2026-10-08 00:33 SGT | CN-112 after 10 failed starts (DEVIATIONS D1), 00:34:10–00:59:52, walltime 26 min, 7.2 GB; Exit 0 (13 converged) |
| b3 | 1439807.stdct-mgmt-02 | 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40 | 2026-10-08 00:33 SGT | CN-112 after 9 failed starts (DEVIATIONS D1), 00:34:11–01:03:24, walltime 29 min, 8.9 GB; Exit 0 (13 converged) |

`qstat -f` showed `project = CFP04-CF-046` for every job after `qsub`; the allocation was refreshed with the helper
before each `qsub` (balance 8,654,901 CPU-h at the bundle submission). Three jobs were used, which left the other
`batch_cpu` slots of the user (6 running per user) free.
