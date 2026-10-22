# WS-S4 reading — moments in the decoded frame when rho is stored by the Hartree law

- **Run.** CI run 39642950633, on the 16 S1 engineering materials. 64/64 rows OK, 0 failure records.
- **rho.** Each material's rho' is the closed-form law's certified stream, regenerated with the committed
  search (`run_cost.search('A1', …)`, rev5 tree) and re-certified for the Hartree contract.
- **m.** m' is certified on the partition of rho', and the result is verified by the compiled binary.

| tau_H | tau_mu (mu_B) | joint certified, no stored map | migration-only moment error (median / max, mu_B) | decoded- / reference-frame m bytes (median / max) |
|---|---|---|---|---|
| 1e-6 | 1e-2 | **16/16** | 7.9e-5 / 9.6e-3 | 1.00 / 1.33 |
| 1e-6 | 1e-3 | 15/16 | 7.9e-5 / 9.6e-3 | 1.00 / 1.32 |
| 1e-4 | 1e-2 | 14/16 | 1.2e-3 / 1.5e-2 | 1.00 / 1.03 |
| 1e-4 | 1e-3 | 7/16 | 1.2e-3 / 1.5e-2 | 1.00 / 1.00 |

## Reading

- **The headline Hartree row needs no stored map.** At the headline tolerance tau_H = 1e-6, the law's rho'
  moves the partition little: median charge error 5.4e-3 e, although charges are not part of its contract.
  Certifying m on the decoded partition composes in 16/16 materials at 1e-2 mu_B, at the same m bytes. This
  supports the 317× whole-object Hartree ratio of S2 (`results/s2_archive_whole_object/`) without the atom
  map, for m at 1e-2 mu_B.
- **The one exception at 1e-6.** FeCo9 at 1e-3 mu_B, where migration alone moves a moment by 9.6e-3 mu_B.
- **Loose Hartree tolerance.** At tau_H = 1e-4 the partition moves more (median charge error 0.039 e). Tight
  moment tolerances then need the stored atom map (7/16 compose at 1e-3 mu_B).
- **Caveat on the archive figure.** S2 itself certified m on the reference partition. Its decoded-frame
  equivalent is supported here on 16 engineering materials, not re-measured on the 300 archive objects.
