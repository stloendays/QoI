# Study 5 — partition fix: revision 10's T/O and revision 11's W/Q archive writers with every decoded partition rebuilt

## Defect

`run_spin_s1.Bader` caches the partition field (REFCAR) by an id and rewrites it only when the id changes.
`run_archive_truncation.certify_m` uses the id `"dec"` for every decoded density. In `archive_truncation_20261024`
(writers T then O, tau_H = 1e-6 then 1e-4) and `archive_waterfill_20261025` (W then Q), the moment certificates of all
(writer, tau) pairs after the first were therefore computed on the partition of the first writer's 1e-6 decoded
density instead of their own. Density streams, Hartree certificates, eligibility and the L and P records (one
decoded density per run, ids `"law"`) are unaffected. Found on 2026-10-25 while writing study 4.

## Rerun

`run_fix.py` runs each study's own `process` unchanged on the same frame, sample, inputs and code, with
`Bader.__call__` patched to rewrite the partition field on every `"dec"` call. Checkpoints:
`checkpoints/trunc/` and `checkpoints/w1/` (Vanda), collected under `results/`. Estimates for T, O, W and Q come from
`analysis/archive_w2_20261025/whole_archive.py` together with V, VP, L and P, with the change against each committed
estimate.

## Reporting

The corrected estimates replace the committed ones in the manuscript wherever T, O, W or Q are cited. The committed
studies and their results stay in the repository unchanged; their DEVIATIONS files point here.
