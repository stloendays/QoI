# The XC energy's own allocation law: steps from the linearized XC functional — protocol

Fixed 2026-10-25, before any material is run. Branch `research/xc-linearized-law-20261025`, created from
`research/server-truncation-xc-20261024` at `534126e`. Nothing under `paper/` or `figures/` changes. Execution on the NUS
Vanda cluster (author instruction, 2026-10-24: "那开始做下一个吧", following the XC study's report, whose proposed next
experiment was an allocation from the XC energy's own linearization; standing instruction "之后都用服务器来算").

## 1. Question

`nonlinear_xc_20261024` found that under a contract on the PBE exchange-correlation energy, reciprocal-space writers
certify 5–7-fold (bulk) and 2–3-fold (slabs) more than pointwise codecs, but the Hartree weight |G|^2 adds only 1–9% over
uniform reciprocal-space steps (L/U). The paper's principle is that the downstream operator sets the allocation. For a
nonlinear QoI the operator that sets the first-order error is the QoI's linearization: the XC potential v_xc = dE_xc/drho.
1. **Primary.** In one container and under one search, does the allocation from v_xc (writer X) certify more than flat
   steps (writer F)? Paired X/F per cohort and tolerance.
2. **Secondary.** How does X compare with the XC study's P (best pointwise), L (Hartree law) and U (uniform steps)?

## 2. Population and loading

Identical to `nonlinear_xc_20261024` §2: P1 (60 Materials Project bulk crystals) and P3b (32 NOMAD slabs), the
confirmatory manifests of `analysis/fresh_population_20261006/`, loaded by `development_compatibility_smoke.build_grid`
(total density in CHGCAR units); each source must match its manifest size and SHA-256.

## 3. QoI, contract and QSQ

Identical to `nonlinear_xc_20261024` §3 (`xc.py`): |E_xc^PBE[rho'] − E_xc^PBE[rho]| < tau_x per atom, tau_x ∈ {1, 0.1}
meV/atom; QSQ with five float32-scale probes (seeds 20260905, 1, 2, 3, 4), eligible iff the floor < tau_x.

## 4. Writers (`xcl.py`)

Both writers use the QOAC v0.3 shell container (`analysis/qoac_v03_rdo/codec_qoac_v03.py`, prior "flat"): the
v0.2 Hermitian-orbit topology, G = 0 stored exactly, 32 radial shells, one zlib block per shell, one step per shell on
the ladder ptp·2^(j/4), j ∈ [−160, 48]; a shell whose step is above the ladder is not stored.
- **X (linearized-XC law).** v_xc is the exact derivative of `xc.py`'s discrete PBE energy (complex-step f_rho and
  f_sigma, spectral divergence; `test_xcl.py` checks it against a finite difference of the energy). W_s is the
  multiplicity-weighted mean of |V(G)|^2 over shell s, V the orthonormal FFT of v_xc; the step of shell s is
  alpha·(W_s / W_max)^(−1/2), snapped to the nearest rung. Rationale: to first order dE = Σ_G conj(V(G)) E(G) dv, whose
  variance under independent quantization errors is Σ |V(G)|^2 Δ_G^2 / 12; the high-rate allocation is Δ_G ∝ |V(G)|^−1.
- **F (flat steps, control).** Every shell at the rung nearest alpha.

## 5. Search

For every eligible (material, tau_x) and each writer, a 60-step log bisection of alpha (`run_engineering.bisect_scale`)
in [max(1e-14·ptp, alpha_floor), 1e3·ptp] with the decoded XC certificate as predicate, keeping the smallest passing
stream. alpha_floor is the smallest alpha at which every quantized coefficient fits 0.95 of the int64 range after
snapping (the rule adopted for the XC study in its DEVIATIONS D2). The Hartree errors of each XC-certified stream are
recorded.

## 6. Reporting (`aggregate_xcl.py`; descriptive, no gate)

Per cohort and tau_x, numbers first:
1. per writer: eligible, certified, median certified compression ratio (bootstrap interval of the median);
2. paired ratios per material: X/F (primary), X/U, X/L, X/P and F/U, the last four against
   `analysis/nonlinear_xc_20261024/results/xc_contract_rows.csv` (same platform, contract, QSQ and search) — median,
   wins, interval;
3. the shell weight profiles W_s / W_max (`shell_weights.csv`).
Bootstrap of the median: seed 20261006, 10,000 resamples.

## 7. Execution on Vanda

Staging `/scratch/junbotong/qoi-xcl-20261025`, project `CFP04-CF-046`, queue `auto`, scripts in
`analysis/server_runs_20261025/vanda/`, driven end to end by a monitor (`qoi_xcl_monitor.py`, registered in the monitor
hub): stage, install, prefetch, probe, production, collect.
- `probe.pbs`: the smallest bulk (mp-2475284) and smallest slab (nomad-deLeLsqokf9I) materials end to end, both
  SUCCESS with every writer certified at both tolerances. Their checkpoints count in the run.
- Production after a passing probe: `production_xcl.pbs`, one single-threaded worker per material, checkpointed.
- Infrastructure-only changes between phases, recorded in `DEVIATIONS.md`.

## 8. Prior exposure

Before this protocol was fixed, `xcl.py` was run only on synthetic periodic fields in `test_xcl.py`; no material of P1
or P3b was encoded with X or F. The XC study's results (P, L, U) were seen; they motivate the question and are the
secondary comparison.
