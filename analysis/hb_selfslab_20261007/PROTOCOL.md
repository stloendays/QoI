# QOAC-HB self-computed slab cohort (N = 32) — frozen protocol

Freeze date: 2026-10-08. Branch `research/hb-selfslab-20261007`, created locally from
`origin/research/hb-slab-aeccar-cohort-20261007` at `bab69ec` (which holds the HB v2 slab adapter, `evaluate_criteria.py`
and the exclusion sets). This protocol is committed before the eligibility funnel and the draw are run, before any
input file is written and before any DFT job is submitted. Pushing is impossible at the time of freezing (GitHub answers
403 "You must verify your email address" for this account), so the commits are local, in this order: protocol, selection,
inputs, DFT output.

Author approval: 2026-10-07, "Vanda 上自算 32 个新 slab", on the group allocation `CFP04-CF-046` (balance about 8.66 M
CPU-h, the allocation of earlier QoI Vanda work).

Purpose: build a pre-registered cohort of 32 bulk-terminated slabs, computed here (VASP single points that write
CHGCAR, AECCAR0 and AECCAR2), on which the frozen joint Hartree + Bader certification method HB v2 is later tested
(section 9). Sections 1–7 produce inputs and input QC only; no HB quantity is computed in them.

## 1. Source

Materials Project summary collection `s3://materialsproject-build/collections/summary/version=2026-09-28/`, a single
file `part-00000-2cc5f2cc-2a79-4051-b013-2f9dec6a302e-c000.zstd.parquet`, 414,503,512 bytes, downloaded anonymously
from `https://materialsproject-build.s3.amazonaws.com/<key>` on 2026-10-07 (S3 `Last-Modified` 2026-09-28 23:20:34 GMT).
SHA-256 `669e5a3bdf1644633f8c771a98b434bf449451a9aa6ce2556d0901ba1dff235b`. 280,159 rows. Kept out of git, at
`D:\Research\QoI-ext-cache\selfslab\`. Read with pyarrow, only the columns used (`material_id`, `energy_above_hull`,
`is_magnetic`, `ordering`, `nelements`, `nsites`, `elements`, `formula_pretty`, `structure`, `task_ids`).
`selection/select_selfslab.py` refuses to run if the size or SHA-256 differ.

All `material_id` values in this build are letter-format (`mp-aaaaaabe`); no numeric legacy id (`mp-149`) occurs in
`material_id` or `task_ids`.

Environment (laptop): Python 3.12.14 (`D:\Research\CatalystForge\.venv`), pymatgen 2025.10.7, pyarrow 25.0.1,
numpy 2.3.5, spglib 2.7.0, pandas 2.3.3, baderkit 0.10.2. The versions are recorded again in every log the scripts write.

## 2. Eligibility (bulk), in this order, with a count at every step (`selection/funnel.json`)

1. `energy_above_hull == 0` (null fails).
2. Not magnetic: **field `is_magnetic`, `is_magnetic == False`** (null fails). Reason for this field rather than
   `ordering == "NM"`: in this build the ground states of canonical non-magnetic materials carry `ordering = "Unknown"`
   with `is_magnetic = False` (Si `mp-aaaaaaft`, Cu `mp-aaaaaabe`, NaCl `mp-aaaabhvi`, MgO `mp-aaaaabwr`; checked
   before freezing), so `ordering == "NM"` would drop them. After step 1, every `ordering = "NM"` row (94,053) has
   `is_magnetic = False`; `is_magnetic = False` adds 16,079 rows with `ordering = "Unknown"`.
   The cross-table of the two fields after step 1 is recorded in `funnel.json`.
3. 1–3 elements (`nelements`).
4. At most 8 sites in the primitive cell: the stored cell's site count if it is at most 8 (a primitive cell is never
   larger), otherwise `len(SpacegroupAnalyzer(structure, symprec=0.1).find_primitive())`.
5. No f-block element (La–Lu, Z = 57–71; Ac–Lr, Z = 89–103) and no noble gas (He, Ne, Ar, Kr, Xe, Rn, Og).
6. Every element has a POTCAR choice in pymatgen's `MPRelaxSet.CONFIG["POTCAR"]` (89 elements; missing: Po, At, Rn, Fr,
   Ra, Am–Lr).

## 3. Exclusions

`selection/build_exclusion_union.py` (built 2026-10-07 16:09 UTC; summary `selection/exclusion_union.json` with the commit
SHA of all 122 refs scanned). Union of
- (a) `analysis/hb_slab_aeccar_cohort_20261007/selection/exclusion_ids.csv` (1,053 ids, SHA-256
  `eae9d2d9856ae40303794e88830fca07d5304636cf5e57d90c389b03dc7a1a22`) and `exclusion_formulas.csv` (690 reduced
  formulas, SHA-256 `61cee7230137407e23d8bf26a63698c92d36269b7c0267ce0dd9c9f81df0f775`);
- (b) a new scan of every text-like data file on all 77 `origin/*` branches and all 45 local branches, including the
  agent worktree branches (local branches hold commits that could not be pushed, e.g. the wide NOMAD cohort's draw), with the identifier regexes, formula columns
  and pymatgen reduction of `analysis/fresh_population_20261006/scripts/build_exclusion.py` and the listing-file skip
  list of the N = 4 cohort (both imported), plus a regex for letter-format MP ids. The candidate-universe listings of
  the wide NOMAD cohort (`candidates.csv`, `relisted_entries.csv`) and every exclusion table are skipped as listings, as
  the earlier rules did. This covers every committed manifest: P1, P2, P3b, the N = 4 cohort, the wide NOMAD cohort,
  the WP-F sample and checkpoints (`origin/research/wpf-cloud-completion-20261007` at `c2f1a2d`), the external cohorts;
- (c) the reduced formula, in this MP collection, of every MP id in (a) or (b) matched on `material_id` or `task_ids`
  (0 matches, because the collection's ids are all letter-format; recorded for completeness).

Result: `selection/exclusion_ids_union.csv`, **1,071 ids** (510 numeric MP ids, 623 MP task ids in S3 URLs, 1
letter-format string, 138 NOMAD entry ids, 109 `nomad-` ids), SHA-256
`705709da726edb02e6efea282fafe782e9c90d34bb12afd843918ffe70ca950b`; `selection/exclusion_formulas_union.csv`,
**723 reduced formulas** (690 from (a), 33 new from (b)), SHA-256
`e31cf2355241283b69a3ed7094f021873f079ddad405c8e167c94ce6b070cfc5`. Each row lists its sources (`a:`, `b:`, `c:`), the
number of files and branches it appears in, and an example file.

Applied after step 6: drop rows whose `material_id` is in the id union (removes nothing, see above), then rows whose
reduced formula (pymatgen `Structure.composition.reduced_formula` of the summary structure) is in the formula union.

## 4. Ranking

`h(x) = SHA256_hex("QOAC-HB-SELFSLAB-20261007|" + x)`. Keep one material per reduced formula, the one with the lowest
`h(material_id)`; rank the kept materials by `h(material_id)` ascending. Output `selection/ranked.csv.gz` (every ranked
material) and `selection/structures_ranked.json.gz` (their summary structures).

## 5. Slab construction (pymatgen 2025.10.7)

For each material, in rank order (`select_selfslab.py`, function `build_slab`):
1. Bulk = the summary `structure`; conventional standard structure
   `SpacegroupAnalyzer(bulk, symprec=0.1).get_conventional_standard_structure()`.
2. Oxidation states: the conventional cell is decorated with `add_oxidation_state_by_guess()` (the first charge-balanced
   guess of `Composition.oxi_state_guesses`; all zero when none exists, e.g. intermetallics). This is what makes
   `Slab.is_polar()` measure the ionic dipole; without decoration pymatgen returns a zero dipole for every slab. The
   decoration is removed from the accepted slab before it is written.
3. Miller indices in the order (0,0,1), (1,1,0), (1,1,1), (1,0,0). An index is skipped when it is in
   `get_symmetrically_equivalent_miller_indices(conventional, earlier_index, return_hkil=False)` of an index already
   tried (recorded as `equivalent_to_<hkl>`).
4. `SlabGenerator(conventional, hkl, min_slab_size=10, min_vacuum_size=15, center_slab=True, in_unit_planes=False,
   primitive=True).get_slabs()` with all other arguments at their defaults (`lll_reduce=False`, `max_normal_search=None`,
   `reorient_lattice=True`; `get_slabs`: `tol=0.1`, `ftol=0.1`, `max_broken_bonds=0`, `symmetrize=False`,
   `repair=False`, `filter_out_sym_slabs=True`). Each slab, in the generator's order, is made orthogonal with
   `get_orthogonal_c_slab()`; all checks below are on the orthogonal slab.
5. Accept the first slab that is symmetric (`is_symmetric()`, symprec 0.1), non-polar (`not is_polar()`, default
   1e-3 e/Å), stoichiometric (element reduced formula equal to the bulk's), has at most 40 atoms, and has estimated fine-grid
   `npoints` <= 5,832,000 (the largest grid HB v2 has completed on a GitHub runner). Every termination tried is
   recorded in `selection/draw_slabs.csv` with all five checks; the first failing check is its status.
6. Grid estimate (`grid_estimate.py`): VASP 6 sets, for PREC = Accurate,
   `NG_i` = the smallest `n >= int(4 * XCUTOF_i + 0.5)` with `n = 2^p 3^q 5^r 7^s`, `p >= 1`, where
   `XCUTOF_i = sqrt(ENCUT / 13.605826) / (2 pi / (|a_i| / 0.529177249))`, and the fine grid `NGF_i = 2 NG_i`; npoints =
   `NGXF NGYF NGZF` at ENCUT 520 eV. Checked before freezing on 124 OUTCARs of the same VASP 6.3.2 binary on Vanda
   (8 distinct cell / ENCUT combinations, ENCUT 400–500 eV, cells 3.8–30 Å; `calibration/vasp_grid_validation.csv`,
   anonymised): all coarse and fine grids match; the cases 28, 98 and 196 show that factor 7 is allowed, and odd
   products are not (`python grid_estimate.py` re-checks). On 30 Materials Project AECCAR grids
   (`calibration/aeccar_integral_calibration.csv`), the estimate equals the grid at 520 eV for 22 and at 680 eV (MP's
   r2SCAN static cutoff) for 7; PuF3 matches neither. The pilot (section 8) checks it at 520 eV against a run of this
   cohort.
7. KPOINTS: Γ-centred, in-plane divisions `ceil(2π / (|a_i| × 0.25 Å⁻¹))` for the two in-plane vectors of the orthogonal
   slab, 1 along the normal.
8. POTCAR symbols: `MPRelaxSet.CONFIG["POTCAR"]` for each element, in the order of the sorted slab
   (`get_sorted_structure()`, as written to POSCAR). The PBE PAW library on Vanda is `potpaw_PBE.54`
   (`/home/svu/junbotong/software/vasp/potpaw_PBE.54`, the only PBE PAW library found by directory listing; 329
   entries). Of the 89 MPRelaxSet symbols, only `W_pv` is absent from it. A material whose slab needs a symbol absent
   from the Vanda library cannot be computed as specified: it is rejected at the draw with reason
   `potcar_symbol_absent_on_vanda:<symbol>` and the walk continues (the same treatment as a material with no acceptable
   slab).
9. A material whose slab construction does not return within 900 s is rejected `slab_generation_timeout`; an exception
   is rejected `error:<type>`. A generator exception for one Miller index is recorded (`generator_error`) and the next
   index is tried.

Materials with no acceptable slab are recorded (`no_acceptable_slab`, with every termination's checks) and skipped.
Checks before freezing, on already-used materials only (Cu, Pt, Si, WS2, TiO2, SnSe, Al2O3, MgO, GaAs, SrTiO3, ZrPd,
NaCl ground states of this collection, all in the formula exclusion): 11 accepted (GaAs at (110), SrTiO3 at (100)
termination 1 with 40 atoms, the rest at (001)), WS2 rejected `potcar_symbol_absent_on_vanda:W_pv`; 0.2–3.7 s each.

## 6. Draw, cohort and input QC

**Draw.** Walk `ranked.csv.gz` in rank order (in batches of 12 on 6 local worker processes; results are taken in rank
order and those after the 40th acceptance are discarded) until 40 materials have an accepted slab: draw ranks 1–32 are
the targets and 33–40 the spares, in rank order. Outputs `selection/draw_materials.csv` (every visited material with its
decision, reason, accepted Miller index, termination, natoms, estimated fine grid and npoints, KPOINTS, POTCAR symbols,
oxidation guess), `selection/draw_slabs.csv`, `selection/drawn.csv` and `selection/slabs/<material_id>.json`.

**Cohort.** The cohort is the first 32 materials in draw order whose DFT single point converged (section 7) and whose
CHGCAR, AECCAR0 and AECCAR2 pass the input QC. If fewer than 32 of the 40 qualify, N = the number that qualify.
DFT failures and QC failures are recorded per material (`runs/STATUS.csv`, `qc/qc.csv`) and are not retried beyond the
one declared fallback (section 7).

**Input QC** (`qc/qc_run.py`, on the gzipped files copied back; first failure is the reason):
1. converged: the final run's OUTCAR has `aborting loop because EDIFF is reached`;
2. same grid: the grid lines of CHGCAR, AECCAR0 and AECCAR2 are equal and equal to OUTCAR's `NGXF x NGYF x NGZF`;
3. no Fortran exponent-less token (`\d[+-]\d{2,3}` ending a token, e.g. `0.65466110724+193`) and no `**` overflow
   token in any of the three files — the regexes and header reader of
   `analysis/hb_slab_nomad_wide_20261007/selection/select_wide.py` (branch `research/hb-slab-nomad-wide-20261007`, blob
   `be633b88`), copied verbatim;
4. each file parses with baderkit `Grid.from_dynamic` through the slab adapter's `run_joint_slab.parse_vasp_total`
   (the HB run's parser) to an array of that grid with all values finite;
5. electron count: `R = (sum(AECCAR0) + sum(AECCAR2)) / N_grid / sum(Z)`, the AECCAR0 + AECCAR2 integral (VASP's
   rho × V convention) over the valence plus core electron count, **within 0.80 <= R <= 50**.

The tolerance of check 5 comes from `calibration/aeccar_integral_calibration.csv` (`aeccar_integral_calibration.py`),
measured before freezing on the AECCAR0 and AECCAR2 of 30 already-used MP materials (every row of the P2 confirmatory
manifest with at most 1,000,000 grid points; MP static runs at PREC = Accurate). AECCAR2 integrates to the valence count
within about 3 % (f-block excepted), but the grid sum of AECCAR0 is a point sample of the core cusp: R ranges from 0.902
(Si, no atom on a grid point) to 13.8 (Sc2AgHg, all four atoms on grid points) for the 19 materials without f-block
elements, and up to 65.6 with them (PuF3). The window is the non-f-block range widened by about 10 % below and 3.6× above.
It rejects missing, zeroed, truncated or mis-scaled files and the garbage values found in NOMAD AECCAR0s; it cannot
resolve the core count more finely than the grid does. Recorded with every run as diagnostics (no gate): sum(CHGCAR)/N
and sum(AECCAR2)/N over NELECT, sum(AECCAR0)/N over the core count `sum(Z - ZVAL)`, the atoms that sit on grid points,
SCF steps, wall time and maximum memory.

This is input generation and input QC only; no HB outcome exists at that point.

## 7. VASP settings

Single point on the unrelaxed, bulk-terminated slab, MP's standard choices where they apply:
- PBE PAW, POTCAR assembled on Vanda from the MPRelaxSet symbols (section 5.8) out of `potpaw_PBE.54`;
- INCAR: `PREC = Accurate`, `ENCUT = 520`, `EDIFF = 1E-6`, `ISMEAR = 0`, `SIGMA = 0.05`, `ISPIN = 1`,
  `LASPH = .TRUE.`, `LREAL = .FALSE.`, `LCHARG = .TRUE.`, `LAECHG = .TRUE.`, `LWAVE = .FALSE.`, `NELM = 200`,
  `ALGO = Normal`; no dipole correction (the slabs are symmetric); no other physics tag (in particular no `LDAU`, no
  `MAGMOM`, no `NSW`/`IBRION`, which default to a single point). The parallelisation tag `NCORE` is set for speed only
  and does not change the physics; its value is fixed by the pilot and recorded with the inputs;
- KPOINTS: section 5.7;
- one declared fallback: if NELM is reached (OUTCAR `EDIFF was not reached`), rerun once from scratch with
  `ALGO = All`, otherwise identical. A second failure is final (`nelm_twice`);
- program: VASP 6.3.2 on Vanda, `/nfs/home/svu/junbotong/software/vasp/NUS_HPC_VASP/vasp_632_vtst_solpp_beef_std`, with
  `module load intel/2021b`.

A DFT failure is a VASP run that ends without converging (NELM twice) or with a VASP error. A node or PBS fault, a
walltime or watchdog stop, a quota error or a missing input is an infrastructure failure: the run is repeated after the
cause is fixed, and the event is recorded in `DEVIATIONS.md`.

## 8. Execution on Vanda

- Access only through `ssh vanda`; the allocation is refreshed with the user's helper before every `qsub`; scripts
  carry `#PBS -P CFP04-CF-046`, queue `auto`; after `qsub`, `qstat -f <id>` must show `project = CFP04-CF-046`.
- Staging under `/scratch/junbotong/qoi_selfslab_20261007/`; everything created on the server is listed in
  `VANDA_MANIFEST.md`. POTCARs are assembled there and never leave the server.
- PBS script based on the vanda-hpc `job_template.pbs`: walltime 72:00:00; watchdog at 250,200 s writing
  `LABORT = .TRUE.`; `set -euo pipefail`; input checks; `OMP_NUM_THREADS=1`; per-material `OSZICAR`/`OUTCAR` kept;
  non-zero job exit when any material fails. Several slabs per job, run one after another (`batch_cpu` allows 6 running
  jobs per user).
- Pilot first: draw rank 1 alone. Its SCF convergence, wall time, memory, actual fine grid against the estimate and the
  input QC are checked before the rest is submitted; ranks per job and the bundle layout are then fixed from it and
  recorded before submission.
- Light monitoring (qstat, OSZICAR tail); OUTCAR is read at the end.
- Results: CHGCAR, AECCAR0, AECCAR2, OUTCAR and OSZICAR are copied back gzipped to
  `D:\Research\QoI-ext-cache\selfslab\runs\<material_id>\` and verified by SHA-256 against `sha256sum` on the server.
  Git holds only small tables (status, grid, npoints, timings, QC, SHA-256); no density file is committed.
- Server files are deleted only after the author confirms the local copies.

## 9. Later stage (not run now)

HB v2 unchanged on the N cohort slabs: `analysis/qoac_hb_v2/run_joint_v2.py` (SHA-256 of committed bytes
`7527629d56f41da21b88eb8f5967550619ab56a317c80ac622b53ad9c69b51aa`) and `aggregate_joint_v2.py` (`98adbf78…abab`),
through the slab adapter `analysis/qoac_hb_slab_20261007/run_joint_slab.py` (`eb3bb321…8760`), with the parameters of
the slab protocol (`analysis/hb_slab_aeccar_cohort_20261007/PROTOCOL.md` section 4). Criteria: the slab protocol's,
scaled to N = 32 (`ceil(N × 46/48)`, `ceil(N × 36/48)`):
1. >= 31/32 R3 jointly certified at all three tau_B (1e-3, 1e-4, 1e-5 e);
2. joint overhead at tau_B = 1e-4: median <= 1.10 and bootstrap CI upper bound <= 1.15;
3. utility at tau_B = 1e-4: >= 24/32 wins, median > 1.10 and CI lower bound > 1.00;
with the denominators, bootstrap (`default_rng(20261007)`, 10,000 resamples) and failure counting of that protocol's
section 6. If N < 32 the same fractions of the planned N apply. Evaluated with
`analysis/hb_slab_aeccar_cohort_20261007/evaluate_criteria.py` unchanged (SHA-256
`0729424b48056faadea6bb90d91b27ca871e974c0eb337684de94139d85eefdf`). Verdict: CONFIRMATORY PASS if and only if all
three pass. Platform: GitHub-hosted runners, with the density files served as SHA-256-verified downloads; where they are
hosted is decided later by the author, and changing the hosting is infrastructure.

## 10. Fixed after freezing

No eligibility step, field, exclusion, salt, ranking, slab rule, grid rule, VASP setting, QC check or tolerance, or
criterion changes after this commit. A crash of a script or a server fault is infrastructure: only infrastructure is
fixed, recorded in `DEVIATIONS.md` before the step is rerun. A per-material rejection in the draw, a DFT failure and a
QC failure are results and are counted.
