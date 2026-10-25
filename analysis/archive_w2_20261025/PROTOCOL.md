# Study 4 — the archive under the W2 writer (V): structure-factor prediction for the density, W2M for the magnetization

Branch `research/algo-upgrade2-20261025`; plan `paper/nc_reopen/ALGORITHM_UPGRADE2_PLAN_20261025.md`. Protocol,
runner (`run_archive_w2.py`), aggregator (`whole_archive.py`) and tests committed before any archive object is run.

## Question

How small is the certified whole-object archive when the density is written by W2S and the magnetization by the
operator-aware sub-stream W2M, against every writer of the manuscript on one footing (after the partition fix of
study 5)?

## Frame, sample, contract (unchanged)

Frame, strata, the 300-object sample, loader, eligibility (archive-law QSQ record at each tau_H), storage rule,
failure rule, moment contract (per-atom moments on the Bader partition of the decoded density, |error| < 1e-2 mu_B
for every atom, against the reference moments on the reference partition; moment QSQ floor from the five f32
perturbations; final check by the compiled Henkelman binary), the reference-map fallback and the stratified
estimator with paired bootstrap (seed 20261012, 2,000 resamples): `analysis/archive_truncation_20261024/PROTOCOL.md`.

## Writers

- **V:** density by `w2.search_w2` (symmetry; smallest of the three variants), magnetization by W2M: the W1
  water-filling writer on the magnetization (Hartree-law steps; symmetry validated against the magnetization), alpha
  by log bisection against the moments on this tau's decoded partition (predicate: max error < 0.995 tau_mu), final
  check by the binary (alpha *= 0.99 until it holds, at most 40). The sub-stream omits the grid shape and lattice
  (taken from the density stream); objects whose density is stored losslessly are charged those 84 bytes.
- **VP (attribution):** the same density stream; magnetization by the pointwise policy (best of ZFP/SZ3/SPERR by
  absolute-tolerance search, final check by the binary) on the same decoded partition.
- Every decoded density's partition is computed under its own partition id (no reuse across tolerances).
- Compared, from study 5 and the committed records: T, O (revision 10), W, Q (revision 11), L, P.

## Endpoints and criteria (tau_H = 1e-6 primary, 1e-4 co-primary)

- **A1 archive:** paired whole-object ratio V/W (W from study 5) at 1e-6 >= 1.15 with 95% CI lower bound >= 1.10,
  and at 1e-4 >= 1.5 with CI lower bound >= 1.3.
- **M1 magnetization stream:** among moment-eligible objects where both certify, per-object pointwise/W2M bytes,
  median >= 2 and W2M smaller in >= 70% of objects, at both tolerances.
- **Validity:** 300/300 objects processed; every V and VP magnetization certificate confirmed by the binary.
- Descriptive: V against L, T, O, Q, P; V/VP (magnetization) and VP/W (density); magnetization share of stored bytes;
  W2S variants and W1S/W2S density bytes; Porod exponent of the decoded partition (slope of the shell-mean basin
  indicator spectrum, shells 2–24, at most 16 basins; Porod's law predicts −4).

## Development exposure

Only P1 engineering materials (laptop; nearest-atom partition in place of Bader). W2M against the best pointwise codec
at 1e-2 mu_B: mp-3148759 (CoOF, 2.9 mu_B) 273 vs 6,750 bytes; mp-23077 (2.1 mu_B) 437 vs 15,320; mp-1924242 (2.9 mu_B,
no symmetry) 715 vs 2,227; seven non-magnetic cells 26–63 vs 45–102. Porod exponents of the nearest-atom partitions
−1.9 to −4.1 (median −3.1). No archive object was used.
