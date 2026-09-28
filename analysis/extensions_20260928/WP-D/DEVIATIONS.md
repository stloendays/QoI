# WP-D — deviations and pre-outcome analysis decisions

Recorded before any descriptor value or model outcome was inspected (2026-09-28). Items 1–3
are environment substitutions; items 4–12 fix details the protocol leaves open.

1. **Operating system.** Windows 11 (the machine available) instead of Ubuntu. Python is the
   pinned CPython 3.12.14; every package in `validation/requirements-external-e2e.txt`
   (commit 893f931) is installed at the pinned version (numpy 2.4.6, baderkit 0.10.2,
   pysz 1.0.3, zfpy 1.0.1, hdf5plugin 7.0.0, h5py 3.16.0, pymatgen 2025.10.7, scipy 1.18.1).
   Additional packages not covered by the pin file: scikit-learn 1.9.1, matplotlib 3.11.2,
   pandas 2.3.3 (versions in `provenance.json` → `pip_freeze`).
2. **Concurrency.** Two shard workers (systems split by sorted index mod 2) because the host
   had ~0.6 GB free RAM while sibling packages ran; neighbour offsets are processed one at a
   time as pre-declared. Sharding does not change any per-system value.
3. **Density cache.** Raw source bytes (verified by SHA-256 and byte count on first download)
   and the parsed field/lattice/reference labels are cached outside the repository
   (`../cache/`, not committed). Re-runs read the cache; the SHA-256 recorded per system is
   the frozen source hash.
4. **Boundary gap per boundary voxel.** "The absolute density difference to the neighbouring
   voxel with a different label" is taken as the *minimum* over all 26-neighbours carrying a
   different label (the closest competitor). The vacuum region (label = natoms in baderkit's
   `atom_labels`) counts as a label, so basin/vacuum interfaces are boundaries.
5. **Near-tie fractions.** Computed over the 13·N unordered (voxel, neighbour) pairs; the
   fraction is identical to the one over the 26·N directed pairs by symmetry.
6. **Basin size (group 5).** "Basin" = atom basin from `atom_labels` (one per atom; charge =
   the atom's Bader charge). The number of raw Bader maxima is stored as an auxiliary column
   (`n_bader_maxima`) and is not a model input.
7. **Systems with no basin boundary** (single-atom cells: every voxel carries the same label).
   Gap percentiles are undefined (NaN in `descriptors.csv`). Univariate Spearman uses the
   non-NaN subset (n reported). For the ridge/logistic models the three percentiles are imputed
   with the column maximum over all systems and `boundary_gap_lt1_fraction` with 0.
8. **Feature transforms for the linear models** (Spearman is invariant to these): log10 for
   natoms, npoints, cell aspect ratio, ε_m, ε_m/max ρ, ε_m/median ρ; log10(x + 1e-3) for the
   three normalized gap percentiles (exact ties give 0); log10(x + 1) for the smallest basin
   volume and for the group-6 flip count; identity for fractions, spacings, charge, counts and
   the two system-type indicators (`is_slab`, `is_vacuum2d`; bulk is the reference level).
   ρ_median is clipped to ≥ 1e-12·ρ_max before forming ε_m/median (count recorded).
9. **Folds.** fold = int(SHA-256("20260928|" + material_id), 16) mod 10. Inner 5-fold CV for
   α (ridge, 25 values log-spaced 1e-3…1e3, MSE) and C (logistic, 13 values log-spaced
   1e-3…1e3, log-loss) uses `KFold(5, shuffle=True, random_state=20260928)` inside each
   training set. Standardization is fitted inside each training fold.
10. **Stratified metrics.** R²/RMSE within a stratum use that stratum's own mean for the total
    sum of squares. Strata: dev/ext, bulk/slab/vacuum2d, slab∪vacuum2d, and the four
    corpus×type cells.
11. **Operating point.** "False-eligible rate ≤ 5%" is read primarily as false-positive rate
    (falsely eligible / truly non-eligible ≤ 5%); the false-discovery reading (falsely
    eligible / predicted eligible ≤ 5%) is reported alongside. The highest-recall threshold
    on the out-of-fold probabilities satisfying the constraint is chosen.
12. **Acceptance rule inputs.** "Ridge coefficients" = standardized coefficients of the ridge
    fitted on all 319 systems with α from inner CV; top three by |coefficient| are compared as
    an unordered set with the top three of (a) restricted to groups 1–5 (group 6 is a separate
    diagnostic model, as pre-declared).
13. **One external system not computed (recorded 2026-09-28 18:1x, after the compute run and
    before `aggregate.py`/`model.py` were run).** `aflow-Cl1O12Pb5V3_ICSD_203074` failed in
    `compute_system` (frozen `patch_pre_vasp5_species` → AFLOW REST `/?species`) with HTTP 500 on
    all 3 attempts of the main run and again on the monitor's retry (17:45). Re-checked by the
    takeover agent at aggregation time: the entry's `/?species`, `/?composition` and entry page
    all return HTTP 500, while another AFLOW entry (`Al1C1Ta2_ICSD_606258/?species`) returns 200,
    so the fault is server-side and entry-specific. The frozen loader was not altered. The system
    stays in `failures.csv` and in the 319 denominator; models run on 318 systems (external
    hold-out 64 of 65). No analysis rule changed.
