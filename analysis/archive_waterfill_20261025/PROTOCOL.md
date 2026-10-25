# Whole-object Hartree archive under the W1 writer — protocol

Fixed 2026-10-25, before any object of the archive sample is run with this code. Branch
`research/algo-upgrade-20261025` (plan: `paper/nc_reopen/ALGORITHM_UPGRADE_PLAN_20261025.md`). Nothing under `paper/`
(other than the plan) or `figures/` changes. Execution on the NUS Vanda cluster.

## 1. Question

Revision 10 states the archive estimate with the operational allocation A3 (O): the whole served objects of the
8.50 TB Materials Project charge-density archive shrink 347.2-fold (95% CI 317.1–386.6) at tau_H = 1e-6 and 1,371-fold at
1e-4, against the law (L, 316.4 / 1,036), truncation (T, 232.5 / 1,142) and the pointwise writer (P, 34.6 at 1e-6). On the
same frame, sample, storage rule, moment policy and estimators, how much do the whole objects shrink when the density is
written by

- **W**, the W1 writer with the water-filling law and symmetry-predictive coding (study 1 arm W1S), and
- **Q**, the W1 writer with the operational allocation and symmetry-predictive coding (study 1 arm O1S),

at tau_H = 1e-6 (primary) and 1e-4?

## 2. Frame, sample, contracts, storage rule, moment policy, estimators

Unchanged from `analysis/archive_truncation_20261024/PROTOCOL.md` §2, §3, §5 and §6: the 300 objects of
`analysis/scope_expansion_20261022/archive_hartree_objects.csv` loaded by `run_spin_s1.decode`; the Hartree contract with
the archive-law eligibility; the magnetization contract tau_mu = 1e-2 mu_B on the Bader basins of the decoded density
with S2's QSQ gate and the compiled Henkelman Bader 1.05; decoded-frame m where it certifies, otherwise the reference
atom map plus the reference-frame m of S2; failed objects at their json.gz bytes; stratified expansion estimators and the
paired stratified bootstrap (2,000 resamples, seed 20261012). `run_archive_w1.py` imports `process`'s helpers and the
estimator from `run_archive_truncation.py`; only the writer calls differ. The symmetry operations are found on the
object's structure (lattice, fractional coordinates, species) and verified on its total density.

L and P enter from the committed records as before; T and O enter from the committed objects table of the truncation
study (`analysis/archive_truncation_20261024/results/objects.csv`). The aggregator reproduces the published 316.4, 1,036,
34.57, 232.5, 347.2 [317.1, 386.6], 1,142 and 1,371 from these records before any W/Q object is counted
(`test_archive_w1.py`).

## 3. Reporting

`results/RESULTS.md`, numbers first: R_W and R_Q at 1e-6 and 1e-4 with intervals; paired W/O, W/L, W/T, W/P, Q/O, Q/W;
counts (eligible, certified, decoded-frame m); objects with symmetry and the median number of operations; failures and
wall time. There is no pass/fail gate; the result is descriptive.

## 4. Execution on Vanda

Project CFP04-CF-046, route queue `auto`; staging `/scratch/junbotong/qoi-algo-20261025/` (shared with study 1, scripts
`analysis/server_runs_20261025b/vanda/`). The probe runs the smallest D01 object (mp-1795466) and the smallest D10c
object (mp-2617593) end to end; their checkpoints count. Production after a passing probe: `production_arch_small.pbs`
(D01–D09) and `production_arch_large.pbs` (D10a–c), one single-threaded worker per object, checkpoints per object,
resumable. Only infrastructure may change after this protocol, each change recorded in `DEVIATIONS.md` before any
rerun. Results are copied back with SHA-256 verification and committed under `results/`; the staging directory is then
removed.
