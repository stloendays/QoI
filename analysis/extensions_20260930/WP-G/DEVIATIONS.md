# WP-G deviations and execution notes

Recorded before any WP-G outcome was computed. No pre-declared analysis or acceptance criterion is
changed; the comparisons are made within one Bader implementation.

1. **Bader implementation (2026-09-30).** The protocol names the frozen baderkit 0.10.2 on-grid solver.
   With an all-electron reference (reference_grid = AECCAR0 + AECCAR2) baderkit 0.10.2 — the newest
   release — terminates with a Windows access violation inside `init_by_approx_persistence`
   (`baderkit/bader/methods/base.py:162`) on the first material tried (mp-1065204, 112³ grid). The
   crash is reproducible and independent of the method (`ongrid`, `neargrid`, `weight`), of
   `persistence_tol` (0.5, 0.05), of rescaling the reference (×1e-3), and of clipping it at zero; the
   same call with the valence CHGCAR as reference (also rescaled ×1e3) succeeds. WP-G therefore uses
   Henkelman Bader 1.05 — the implementation the `-ref CHGCAR_sum` practice is defined with — built from
   the repository copy `mechanism/independent_bader_20260908/reference_source` (official 1.05 source
   with the input-format adapter validated in that study to 2e-6 e), with the settings of that study:
   `-b ongrid -vac 0.001`, plus `-p atom_index` for the voxel labels needed by analysis (4).

2. **Pairing arm V.** Because the implementation changes, a valence-reference arm V (the CHGCAR is its
   own reference) is run with the same binary, perturbations and rows. Analyses (1)–(4) compare V, G1
   and G2 within Henkelman on-grid; the frozen baderkit valence results of the same materials are
   reported alongside for context only. The protocol's acceptance statements are evaluated on G1 and
   G2 exactly as written.

3. **Platform.** NUS Vanda (Linux), `module Python/3.12.3-GCCcore-13.3.0` with the frozen pins
   (`requirements.txt`: numpy 2.4.6, pysz 1.0.3, zfpy 1.0.1, hdf5plugin 7.0.0, h5py 3.16.0, pymatgen
   2025.10.7, scipy 1.18.1, baderkit 0.10.2), the frozen codec round trip and MP decoder copied from
   commit 893f931 (`vanda/frozen/`), as the 2026-09-08 independent-Bader study ran. Inputs are
   downloaded on the login node; CHGCAR bytes must match the frozen SHA-256, AECCAR SHA-256 values are
   recorded in `tasks.json`. Charges are read from `ACF.dat` (printed to 1e-6 e).

4. **Cleanup.** Everything staged under `/scratch/junbotong/qoi-wpg-20260930` is deleted after the
   checkpoints and logs are copied back (standing Vanda rule).

5. **Published AECCAR0 entirely non-finite for 3 materials (2026-09-30, before any WP-G outcome was
   read).** For mp-1192831, mp-1193567 and mp-776331 every voxel of the published AECCAR0 is NaN
   (2,099,520 / 1,959,552 / 987,840 voxels); the other 50 materials have finite AECCAR0 and AECCAR2.
   The runner now rejects non-finite AECCAR input at the input stage (the first production attempt had
   passed the NaN reference on and failed later at the QSQ stage; those three records are kept under
   `logs/superseded_nan_checkpoints/` and replaced by input-stage failure records). The three stay in
   every table as failed. Analyses (1)–(4) and the acceptance statements are evaluated on the 50
   processed materials; RESULTS.md also states the acceptance outcome with the three failures counted
   against each claim.
