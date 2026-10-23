# Whole-object Hartree archive under spectral truncation and the operational optimum — protocol

Fixed 2026-10-24, before any object of the archive sample is run on the server. Branch
`research/server-truncation-xc-20261024`, created from `paper/nc-rev9-20261023` at `0ed782a`. Nothing under `paper/`
or `figures/` changes. Execution on the NUS Vanda cluster (author instruction, 2026-10-23: "谱截断，之后都用服务器来算，
你5个小时之后再提交这个计算").

## 1. Question

The manuscript's archive estimate compares the closed-form law (writer L, arm A1) with the best pointwise codec
(writer P, arm A6): under the Hartree contract the whole served objects of the Materials Project charge-density archive
shrink 316-fold with L and 34.6-fold with P at tau_H = 1e-6, and 1,036-fold with L at 1e-4. Spectral truncation is the
Fourier-native baseline, and at 1e-4 it certifies more than the law on the 92 law-protocol materials. On the same frame,
sample, storage rule, moment policy and estimators, how much do the whole objects shrink when the density is written by

- **T**, spectral truncation (arm A2 of the law protocol), and
- **O**, the operational optimum (arm A3),

at tau_H = 1e-6 (primary) and 1e-4?

## 2. Frame, sample and loading

Unchanged from `analysis/archive_hartree_law_20261012/PROTOCOL.md` §2 and the whole-object studies S2b/S2c/S2d
(`analysis/scope_expansion_20261022/`): the 300 objects of `analysis/scope_expansion_20261022/archive_hartree_objects.csv`
(the archive-law per-object table: task id, stratum, URL, frame bytes, json/float64/lossless bytes, Hartree QSQ
eligibility and the L and P records), loaded by `run_spin_s1.decode` (total density `rho` and magnetization `m`,
CHGCAR units). Every object is downloaded on the login node, its size must equal the frame bytes, and its SHA-256 is
recorded in `inputs/MANIFEST.tsv`.

## 3. Contracts

- **Density:** the Hartree potential, historical and Nyquist-safe relative RMS error both < tau_H, decoded certificate
  `run_cost.certify` (as the law protocol). Hartree QSQ eligibility is taken from the archive-law record
  (`eligible_1e-06`, `eligible_0.0001`); it is a property of the object and the contract, not of the writer.
- **Magnetization:** per-atom magnetic moments on the Bader basins of the decoded density, tolerance tau_mu = 1e-2
  mu_B, with S2's QSQ gate (five probes on rho and m at their float32 scales, compiled Henkelman Bader 1.05 from
  `mechanism/independent_bader_20260908/reference_source`) and final verification by the binary.

## 4. Writers

`run_archive_truncation.py`, using the committed code paths unchanged:

- **T (A2):** `analysis/qoac_v03_rdo/run_engineering.py`'s A2 — for every cutoff q_c = k/32 (k = 1..32), exact
  spectral bisection (60 log steps) of a uniform step with the coefficients above q_c dropped; the three smallest
  candidates are encoded with `truncation_codec`, decoded and certified (step × 0.99 until certified, at most 40
  times); the writer's stream is the smallest certified one.
- **O (A3):** `run_cost.search('A3', ...)` — `codec_qoac_v03.analyze` with the operator prior, Lagrangian selection at
  margin 0.995, shrinking by 0.995 until the decoded certificate holds (at most 20 times).

Both reproduce the law protocol's recorded stream sizes (known-answer check `check_writers.py`, §7).

## 5. Storage rule and moment policy

Per object, tau_H and writer W:
- rho: eligible and W certified → W's stream bytes; otherwise the lossless bytes of the archive-law record;
- m: certified on the partition of W's decoded rho (decoded-frame m) where the S2 gate admits it and a ZFP/SZ3/SPERR
  stream certifies; otherwise the reference atom map plus the reference-frame certified m of S2
  (`objects_spin_store.csv`: `m_store_0.01` + `label_atom_xz_bytes`) — the manuscript's hybrid rule;
- failed object (download, parse, memory, solver, walltime): its current json.gz bytes (no saving).

L and P enter unchanged from the committed records: L = recorded law streams + S2b (1e-6) / S2c (1e-4) hybrid m;
P = recorded pointwise streams + S2d hybrid m (1e-6). The aggregator reproduces the published 316.4 [290.4, 349.9],
1,036.3 [926.9, 1,152.2], 34.57 [32.35, 37.21] and 9.153 from these records before any T/O object is counted
(`test_archive_truncation.py`).

## 6. Estimators and reporting

Stratified expansion estimators and the paired stratified bootstrap of the archive-law protocol (2,000 resamples,
`numpy.random.default_rng(20261012)`, 95% percentile intervals), with every writer evaluated on the same resample.
`RESULTS.md`, numbers first:
1. R_T and R_O at 1e-6 and 1e-4, with intervals;
2. paired L/T, O/T, O/L at both tolerances, and T/P, O/P at 1e-6;
3. counts: eligible, certified, decoded-frame m;
4. failures and wall time per stratum.
There is no pass/fail gate; the result is descriptive.

## 7. Execution on Vanda

- Project `CFP04-CF-046`, route queue `auto`; staging `/scratch/junbotong/qoi-srv-20261024/` (shared with the XC study,
  `analysis/server_runs_20261024/`); inputs prefetched on the login node; compute nodes read only staged files.
- `probe.pbs` (with the XC study): the known-answer writer check on P1 materials mp-2475284 and mp-1790941 (T and O
  bytes within max(3 bytes, 0.1%) of the record at 1e-6 and 1e-4), and the smallest D01 object (mp-1795466) and the
  smallest D10c object (mp-2617593) end to end. Their checkpoints count in the run.
- Production after a passing probe: `production_arch_small.pbs` (D01–D09) and `production_arch_large.pbs` (D10a–c),
  one single-threaded worker per object, checkpoints per object, resumable.
- Between and after phases only infrastructure may change (modules, paths, resources, timeouts), each recorded in
  `DEVIATIONS.md` before any rerun.
- Results are copied back with SHA-256 verification and committed under `results/`; the staging directory is then
  removed (Vanda cleanup rule).

## 8. Prior exposure

Before this protocol was fixed, the code was exercised locally on one archive object (mp-2291976, D01) with a
nearest-atom stand-in for the Bader binary (plumbing only; its moment results are not valid) and the writers on one P1
material (mp-2475284), whose A2/A3 bytes reproduced the record exactly. No decision in this protocol depends on those
outputs; mp-2291976 is run again on the server like every other object.
