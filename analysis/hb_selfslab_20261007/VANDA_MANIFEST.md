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
