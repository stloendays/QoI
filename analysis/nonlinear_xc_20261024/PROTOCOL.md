# A nonlinear downstream QoI: exchange-correlation energy of the stored density — protocol

Fixed 2026-10-24, before any material is run on the server. Branch `research/server-truncation-xc-20261024`, created
from `paper/nc-rev9-20261023` at `0ed782a`. Nothing under `paper/` or `figures/` changes. Execution on the NUS Vanda
cluster (author instruction, 2026-10-23: "补一个非线性下游量的测试 … 之后都用服务器来算").

## 1. Question

Every QoI certified so far is linear in the density (Hartree potential and field, gradient, Laplacian, smoothing) or a
sum over basins (Bader charges, magnetic moments). For a nonlinear functional of the stored density:
1. **Transfer.** How far do the law protocol's Hartree-certified streams (A1 law, A2 truncation, A3 operational optimum,
   A6 best pointwise codec) preserve it?
2. **Certification.** Under a contract on that functional, which writer certifies the most compression: the best
   pointwise codec (P), the closed-form Hartree law (L, Delta_G ∝ |G|^2) or uniform reciprocal-space steps (U)?

## 2. Population and loading

P1 (60 Materials Project bulk crystals) and P3b (32 NOMAD slabs), the confirmatory manifests of
`analysis/fresh_population_20261006/`, loaded exactly as the law protocol (`development_compatibility_smoke.build_grid`;
total density in CHGCAR units). Each source is downloaded on the login node and must match its manifest size and
SHA-256.

## 3. QoI and contract

- **QoI:** the spin-unpolarized exchange-correlation energy of the stored total density, E_xc[rho], in eV per atom,
  `xc.py`: rho = CHGCAR value / V_cell (converted to bohr^-3); gradients by FFT on the periodic cell (unpaired Nyquist
  modes dropped); points with rho <= 1e-12 bohr^-3 contribute zero.
  - primary: PBE (Perdew–Burke–Ernzerhof 1996, PW92 correlation);
  - secondary: LDA (Slater exchange + PW92), and the relative RMS error of V_xc^LDA on the grid.
  The implementation is checked against PySCF/libxc in the probe (§7).
- **Contract:** |E_xc^PBE[rho'] − E_xc^PBE[rho]| < tau_x per atom, tau_x ∈ {1, 0.1} meV/atom; the decoded density is
  the only approximate input.
- **QSQ for the contract:** epsilon = ||float32(rho) − rho||_inf; five probes `default_rng(s).uniform(-epsilon,
  epsilon)` for s ∈ (20260905, 1, 2, 3, 4); floor = largest response; eligible at tau_x iff floor < tau_x.

## 4. Part 1 — transfer of the Hartree certificate

For tau_H ∈ {1e-4, 1e-6, 1e-8} and arms A1, A2, A3, A6, the smallest certified stream recorded by the law protocol
(`analysis/general_qoac_law/results/run_{P1,P3B}_CONFIRMATORY/part_a_rows.csv`) is regenerated from its recorded
parameter, its bytes compared with the record and its Hartree certificate re-checked; the XC errors of the decoded
density are recorded. An arm with no certified record at a tolerance is reported as such.

## 5. Part 2 — certification under the XC contract

For every eligible (material, tau_x), each writer receives the same search with the decoded XC certificate as the
predicate: a 60-step log bisection of its scale (P: absolute tolerance of each of ZFP, SZ3 and SPERR in
[1e-14, 1]·ptp; L and U: reciprocal-space step alpha in [1e-14, 1e3]·ptp, beta = 2 and 0 of `codec_qoac_h_v02`),
keeping the smallest passing stream; the writer's result is its smallest certified stream. The Hartree error of each
XC-certified stream is recorded.

## 6. Reporting (`aggregate_xc.py`; descriptive, no gate)

Per cohort, numbers first:
1. Part 1: per arm and tau_H — median and maximum |dE_xc^PBE| (meV/atom, bootstrap interval of the median), counts
   below 1 and 0.1 meV/atom, median |dE_xc^LDA| and V_xc^LDA relative RMS;
2. Part 2: per writer and tau_x — eligible, certified, median certified compression ratio; paired L/P, U/P, L/U
   (median, wins, interval).
Bootstrap of the median: seed 20261006, 10,000 resamples (the law protocol's).

## 7. Execution on Vanda

- Shared staging and environment with the archive study (`analysis/server_runs_20261024/`), project `CFP04-CF-046`,
  route queue `auto`.
- `probe.pbs`: `libxc_check.py` on mp-2475284 (LDA energy density and potential within 1e-8 relative of libxc
  `LDA_X,LDA_C_PW`; PBE energy density within 1e-3 relative of libxc `GGA_X_PBE,GGA_C_PBE`, whose PBE correlation uses
  the PW92 parameters at libxc's precision), and the smallest bulk (mp-2475284) and smallest slab (nomad-deLeLsqokf9I) materials end to
  end, every regenerated stream within max(3 bytes, 0.1%) of the record and Hartree-certified. Their checkpoints count
  in the run.
- Production after a passing probe: `production_xc.pbs`, one single-threaded worker per material, checkpointed.
- Infrastructure-only changes between phases, recorded in `DEVIATIONS.md`.

## 8. Prior exposure

Before this protocol was fixed, `run_xc.py` was run locally on mp-2475284 to test the code (12.000 electrons; every
regenerated stream within 3 bytes of the record and Hartree-certified). Its outputs were seen. No choice of this
protocol (QoI, tolerances, writers, search, reporting) was changed after that run; the material is run again on the
server as part of the probe.
