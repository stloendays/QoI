# Pilot: draw rank 1 alone (PROTOCOL.md section 8)

`mp-aaaabicq` ZrIN, (001) termination 0, 12 atoms, KPOINTS 7x7x1 (16 irreducible), NBANDS 60, NELECT 96.
PBS job `1439802.stdct-mgmt-02` (`project = CFP04-CF-046`, queue `batch_cpu`, CN-104, 36 MPI ranks, NCORE 6), Exit 0.

| check | result |
|---|---|
| SCF | converged with ALGO = Normal in 25 steps (`aborting loop because EDIFF is reached`); no fallback |
| wall time | 50.8 s (OUTCAR); PBS walltime 54 s, cput 27 min |
| memory | PBS `resources_used.mem` 5.94 GB; OUTCAR maximum 255 MB per rank |
| grid | OUTCAR NGX x NGY x NGZ = 28x32x294, NGXF x NGYF x NGZF = **56x64x588 = estimate** (`grid_estimate.py`); npoints 2,107,392 |
| copy back | CHGCAR 38,370,689 B, AECCAR0 and AECCAR2 38,355,149 B each, OUTCAR, OSZICAR: SHA-256 equal to `sha256sum` on the server (`fetch.csv`) |
| input QC | pass (`../qc/qc.csv`): same grid; 0 no-E and 0 `**` tokens; all values finite; R = 2.405 (window 0.80–50) |
| diagnostics | sum(CHGCAR)/N = 96.000 = NELECT; sum(AECCAR2)/N = 96.585 (1.006 NELECT); sum(AECCAR0)/N = 865.5 against a core count of 304 (2.85x), no atom exactly on a grid point |

Decision for the remaining 39 slabs: 36 ranks per job, NCORE 6 (inputs unchanged). A slab of this size takes about a
minute; the largest drawn slabs (32–40 atoms, up to 5.38 M fine-grid points) are expected at roughly 10x the pilot's
cost. The 39 slabs therefore go into 3 jobs of 13 slabs each, run one after another, interleaved by draw rank so that
the 32 targets finish at about the same time: bundle `b1` = draw ranks 2, 5, …, 38; `b2` = 3, 6, …, 39; `b3` = 4, 7, …, 40.
Three jobs leave the other user slots of `batch_cpu` (6 running per user) free; one other job of the user was running
at submission.
