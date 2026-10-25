# Deviations

Infrastructure-only changes after the protocol was fixed, numbered, each recorded before the run it affects.

None so far.

## Partition reuse in the decoded-frame moment certificate (found 2026-10-25, after the results)

`certify_m` passes the partition id "dec" for every decoded density, and `run_spin_s1.Bader` rewrites the partition
field only when the id changes, so every (writer, tau) pair after the first read the first writer's 1e-6 decoded
partition. Density streams and Hartree certificates are unaffected. Rerun with every decoded partition rebuilt:
`analysis/archive_partition_fix_20261025/` (study 5 of the second algorithm upgrade); its estimates replace this
study's wherever they are cited.
