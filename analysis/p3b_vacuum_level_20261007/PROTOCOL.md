# P3b vacuum-level (work-function) error of the certified Hartree streams — frozen protocol

Freeze date: 2026-10-07. Branch `research/p3b-vacuum-level-20261007`, created from `paper/nc-reopen-20261007` at
`87b3a65`. This protocol is committed and pushed before any decoded stream of any P3b slab is computed for this work
item. After the run starts, only infrastructure may change, and every such change goes into `DEVIATIONS.md`.

## 1. Question

The manuscript certifies the Hartree potential by its relative RMS error, tau in {1e-4, 1e-6, 1e-8}. This item states
what that means physically for slabs: the error in the electrostatic vacuum level, and hence in the work function
Phi = V_vac - E_F, of each certified decoded density of the P3b law run.

- E_F belongs to the reference DFT calculation and does not change.
- The ionic potential is unchanged, and exchange-correlation vanishes in vacuum.
- The G = 0 Hartree term is zero in the reference and in the decoded field.

So the work-function error of a decoded density is the planar-averaged Hartree-potential error in the vacuum region.
This item is descriptive. It has no pass/fail criterion.

## 2. Metric definitions (units)

Fields are in CHGCAR units, F = rho * V_cell, with rho in e/A^3. `grid.total` from the frozen loader
(`dev.build_grid`) is that field, the lattice rows are a_0, a_1, a_2 (A), and grid axis n runs along a_n.
`n_electrons_mean_field` = mean(F) is recorded per slab as a units check (it equals the electron count).

- k_e = 14.399645 eV A. The reciprocal vectors are b_n = 2 pi (A^-1)^T rows, so a_m . b_n = 2 pi delta_mn. The grid
  frequencies are G = sum_n m_n b_n with signed integers m_n = `fftfreq(N_n) * N_n`.
- **Hartree potential (eV, electron potential energy):** V_H(G) = 4 pi k_e rho(G) / |G|^2, with rho = F / V_cell and
  V_H(G = 0) = 0 (`vacuum_level.hartree_potential_ev`).
- **Planar average along the normal axis n:** the mean over the two other grid axes, i.e. over the lattice plane
  spanned by the two other lattice vectors at fixed fractional coordinate along a_n. Plane k lies at normal distance
  k d_n / N_n, with interplanar spacing d_n = 2 pi / |b_n| = V_cell / |a_i x a_j|.
- **Planar-averaged Hartree error** (exact, `planar_hartree_from_profile`): with p(k) the planar average of
  Delta F = F_decoded - F_reference divided by V_cell, and p_m its DFT,
  <Delta V_H>(k) = sum_{m != 0} 4 pi k_e p_m / (m^2 |b_n|^2) exp(2 pi i m k / N_n). This equals the planar average of
  the 3-D Delta V_H (unit test).
- **Delta Phi** (meV) = mean of <Delta V_H>(k) over the vacuum window (section 4), times 1000. Sign: Delta Phi > 0 means
  the decoded density raises the vacuum level.
- **max |Delta V|** (meV) = max over the window of |<Delta V_H>(k)|, times 1000. Recorded per stream.
- **Reference Hartree RMS** (eV) per slab: `vref_rms_eV_hist` = (k_e / V_cell) * r_h, where r_h is
  `v02.reference_hartree_rms(F, lattice)[0]`, the denominator of the certified historical relative error;
  `vref_rms_eV_safe` likewise from the Nyquist-safe denominator. A stream certified at tau therefore has
  RMS(Delta V_H) < tau * `vref_rms_eV_hist`; `tau_times_vref_meV` = 1000 tau `vref_rms_eV_hist` is recorded per row.
  As a cross-check, `vref_rms_eV_own3d` is the RMS of `hartree_potential_ev(F)`, and `vref_own3d_rel_diff` its relative
  difference from `vref_rms_eV_hist`.
- `delta_electrons` = mean(Delta F), the electron-count change of the decoded density (descriptive).

Unit tests (`test_vacuum_level.py`) include the analytic periodic case rho = A cos(G0 . r), whose potential is
V = 4 pi k_e A cos(G0 . r) / |G0|^2, on an orthorhombic and a triclinic cell with mixed G0, and for the planar formula.

## 3. Population, inputs and streams

**Population.** The 32 NOMAD slabs of `analysis/fresh_population_20261006/P3B_CONFIRMATORY_MANIFEST.csv`
(`d1c1050`; SHA-256 of the committed bytes `e7c447d5f8dc3b263c7b5b4b9d1f8344ad9c8ed41e5b72fa333c37ad14b70f97`, checked
by the workflow). Every CHGCAR is downloaded from the manifest URL and must match the manifest SHA-256 and byte count
(`dev.fetch_exact`), with up to 3 download attempts; the check is recorded per slab (`source_sha256_verified`).

**Recorded streams.** P3b law run, CI 37493518929, result commit `eaa3267`:
`analysis/general_qoac_law/results/run_P3B_CONFIRMATORY/part_a_rows.csv` (SHA-256 of the committed bytes
`45553d6d973fad3b87ee0fb41549c2a838472fba439b8c65f072ae4fed74575a`, checked by the workflow) and `part_a_material.csv`.
For each slab, arm in {A1, A2, A3, A5, A6} and tau in {1e-4, 1e-6, 1e-8}, the certified stream is the certified row
with the largest CR (first in file order on ties). This is the row that `aggregate_law.py` reports in
`part_a_material.csv` (`cr.max()` over certified rows): for A2 the best of the three q_cut candidates, for A6 the best of
ZFP / SZ3 / SPERR. 32 x 5 x 3 = 480 streams are planned.

**Code.** Part A streams come from `analysis/qoac_v03_rdo/run_engineering.py` (`material`), which
`analysis/general_qoac_law/run_part_a.py` calls unchanged. `policy_codec.py` is the Part B codec and is not on the
Part A path. All files below are imported unmodified; none changed between `eaa3267` and `87b3a65`.

| file | last commit | SHA-256 (committed bytes) |
|---|---|---|
| `analysis/qoac_v03_rdo/run_engineering.py` | `7ca412e` | `6cbdf8e31b4749cebb65a78582a8bec3032baf89073524b9c21065b65a7f3123` |
| `analysis/qoac_v03_rdo/codec_qoac_v03.py` | `3b8398f` | `1d3a4f65e46c32bff9c1c7fb179a897d8bb79221c88114d7be05dcf87d4f562a` |
| `analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py` | `5b36848` | `f78dd40aba7f2a25727d4df08d621f3456244bfb14f404423551900c3504ce1a` |
| `analysis/qoac_h_strong_baselines/truncation_codec.py` | `2fcddf8` | `4e6e1d623d6ab0ddf2dec4afd7c5309cf3fc6d040df0132f9462613d5f187d54` |
| `analysis/general_qoac_law/run_part_a.py` | `fe2e08a` | `fbfd13febf5911ae342f407cf4b3e946a86bd6e20e386de1bbfbdf15beb7f2af` |
| `validation/qsq_prospective/development_compatibility_smoke.py` | `427d70f` | `d51a31d7838d09175292e5024e7f969347c4de2e011446f6de863f2f3c0683bf` |
| frozen `validation/external_end_to_end.py` @ `893f931` (codec round trip) | `475fc9a` | `a4f791b7ab60b3a6300e49c9a857891a178099c5209354ecf6392310a47ec811` |
| frozen `validation/requirements-external-e2e.txt` @ `893f931` | `7ce9e5b` | `c6da91db628ff7f30c4b627d0a87660f5481f0a261cde5f608cefaffdfdf3656` |
| `.github/workflows/general_qoac_law_p3b.yml` (workflow template) | `39ba728` | `cdea94ed923967888cf3bf8e632a5cd20fcf0f4c08c03c2adea9d369a10a4f17` |

Environment: Python 3.12.14, `frozen/validation/requirements-external-e2e.txt` of `893f931`, ubuntu-24.04 (the P3b
law run's shard environment).

**Regeneration, two routes** (`run_vacuum_level.py`):
- **R — recorded parameter.** Regenerate from the recorded parameter string with the frozen functions:
  A1 `v02.encode_prepared(prep, alpha = alpha_rel * ptp, beta = 2, zlib_level = 6)`; A2
  `t1.encode(prep, alpha = alpha_rel * ptp, q_cut)`; A3 / A5 `v3.select(analysis, tau, margin, polish = True / False)`
  then `v3.encode` on the operator-prior / density-selected flat-prior analysis built exactly as in `material`; A6
  `core.codec_roundtrip(codec, F, abs_tol_rel * ptp)`. The A3 / A5 margin is the exact float of `material`'s retry
  sequence (0.995, 0.995 * 0.995, ...) that prints as the recorded 4-decimal string.
- **S — deterministic search rerun.** The A1, A2 and A6 parameters are recorded to 9 significant digits only, which is
  not the exact parameter: on the synthetic smoke slab (section 8), a 1e-9 relative change of the A2 alpha changes the
  Hartree error by 9 %. As the task prescribes when a needed parameter is not recorded, the arm's deterministic search
  is rerun with the same code: `run_engineering.material` is called unchanged on the slab. Its module-level `certify`
  is wrapped for the duration of the call; the wrapper returns `certify`'s result unchanged and keeps only the
  planar average of (decoded - reference) along the normal axis and mean(Delta F). The rerun row with the same arm,
  tau and parameter string as the recorded row is the S stream. Route S is run for every slab and every arm.

**Reproduction check (tolerance).** A regenerated stream reproduces the recorded one if
|bytes - recorded bytes| <= 16 bytes, |e - e_rec| <= 1e-6 e_rec for both the historical and the Nyquist-safe Hartree
relative errors (`run_engineering.certify`, i.e. `v02.hartree_error_metrics`), and both errors are < tau. It is
*exact* if the bytes are identical and both errors agree to 1e-12 relative. The 16-byte allowance covers the JSON
header, which stores the float alpha (A1, A2). The 1e-6 error tolerance is far below any change of the quantized
payload and far above floating-point noise.

**Stream used.** An exact reproduction if one exists (R before S); otherwise a within-tolerance reproduction (R before
S); otherwise the stream is *not reproduced*. It is reported, excluded from the statistics and counted. Per stream, the
CSV records both routes' bytes, errors, exactness, reproduction flag and Delta Phi, plus the route used.

## 4. Surface normal and vacuum window — reference density only

1. rho_ref = F_ref / V_cell. For each grid axis n, p_n(k) = planar average of rho_ref (section 2).
2. Vacuum planes along n: p_n(k) < 1e-3 * max_k p_n(k).
3. The longest contiguous run of vacuum planes, with periodic wrap-around, has length L_n planes and thickness
   L_n d_n / N_n (A). If two runs are equally long, the first one after a non-vacuum plane, in increasing k, is used.
4. The surface normal is the axis with the largest vacuum thickness (lowest axis index on ties).
5. The slab qualifies if that thickness is >= 3.0 A, L >= 2, and not every plane along the normal is vacuum.
6. The window is the central half of that run: run offsets o with floor(L/4) <= o < L - floor(L/4), taken modulo N.

A slab that does not qualify is reported, with its per-axis vacuum thicknesses, and excluded from the vacuum
statistics. Its streams are still regenerated and their reproduction is reported.

## 5. What is computed per slab and stream

`results/slabs.csv`, one row per slab: SHA-256 check, grid, V_cell, `n_electrons_mean_field`, `vref_rms_eV_hist`,
`vref_rms_eV_safe`, the own-3-D cross-check, the vacuum thickness on each axis, the normal axis, run and window
(planes, A, first and last index), threshold, `qualifies`, timings and status.

`results/per_slab_dphi.csv`, one row per slab x arm x tau (480 rows): recorded parameter, bytes and errors; routes R
and S (bytes, errors, exact, reproduced, Delta Phi); `route_used`, `reproduced`, `exact`, `dphi_meV`, `abs_dphi_meV`,
`max_abs_dV_window_meV`, `delta_electrons`, `tau_times_vref_meV`, `evaluated` and `status` (`ok`, `not_reproduced`,
`no_qualifying_vacuum`, `no_certified_stream_recorded`).

`results/failures.csv` lists every material-level or route-level failure, including slabs with no shard output.

## 6. Statistics and report format

For each arm x tau, over the evaluated streams (stream reproduced and slab qualifies):
- n evaluated;
- median, P95 and maximum of |Delta Phi| in meV. P95 is `numpy.quantile(|Delta Phi|, 0.95, method = "linear")`;
- the fraction (and count) of slabs with |Delta Phi| < 1 meV and with |Delta Phi| < 10 meV. The thresholds are fixed
  here. The inequality is strict, and the denominator is n evaluated.

Descriptive extras in `results/summary.csv`: median and maximum of max |Delta V| over the window, the median of
tau * `vref_rms_eV_hist` (meV), and the reproduction counts per arm x tau (R reproduced / exact, S reproduced /
exact, used exact, used via R / S, not reproduced). `results/SUMMARY.json` holds the same table plus the missing and
non-qualifying slabs.

`RESULTS.md` reports, numbers first:
1. a table of median / P95 / max |Delta Phi| (meV) and the < 1 meV and < 10 meV fractions for each arm at
   tau = 1e-6, then at 1e-4 and at 1e-8, with n evaluated;
2. the reproduction outcome: counts by route and exactness, and every stream that was not reproduced;
3. the slabs without a qualifying vacuum, and the reference Hartree RMS (eV) per slab;
4. the CI run id, commit hashes and file paths;
5. every failure, counted.

No hypothesis test and no interpretation beyond the numbers.

## 7. Execution

`.github/workflows/p3b_vacuum_level.yml` is a copy of `general_qoac_law_p3b.yml`, with the changes listed in
`DEVIATIONS.md`. The run starts when the sentinel `analysis/p3b_vacuum_level_20261007/RUN_SENTINEL` is pushed. The
preflight job runs the unit tests and verifies the manifest and the recorded-rows SHA-256. Next come 32 shards, one
slab each (max 20 parallel, 360 min). The aggregate job then commits `analysis/p3b_vacuum_level_20261007/results/` to
this branch, together with the run id and one shard's `pip freeze`.

Failures are counted, never dropped:
- a slab whose download, SHA-256 check or load fails is a material failure;
- a stream that neither route reproduces is *not reproduced*;
- a slab without a qualifying vacuum is excluded from the vacuum statistics only.
All three appear in `RESULTS.md` with counts. A rerun is allowed only for an infrastructure failure, such as a runner
loss or a network outage that defeats all 3 download attempts. It must be recorded in `DEVIATIONS.md`, and no
definition in this file may change.

## 8. Checks done before freezing (no P3b decoded stream computed)

- `test_vacuum_level.py` (17 tests: analytic cosine potential on orthorhombic and triclinic cells; planar formula
  equal to the plane average of the 3-D potential; uniform field gives zero; vacuum rule on synthetic slabs, including
  wrap-around, no vacuum and thin vacuum; statistics; stream selection, parameter parsing, margin reconstruction,
  reproduction check): pass. The existing `test_policy_codec.py`, `test_codec_qoac_v03.py` and the operator tests also
  pass.
- Synthetic smoke (a 16 x 18 x 96 analytic slab, no P3b data). `run_engineering.material` produced the "recorded" rows,
  then `run_vacuum_level.material` regenerated them:
  - route S reproduced 15/15 streams exactly;
  - route R reproduced A3, A5 and A6 exactly (9/9), A1 at tau = 1e-4 within tolerance (not exact), and failed the
    other 5 A1 / A2 streams;
  - the vacuum rule found axis 2, and the own-3-D RMS agreed with `vref_rms_eV_hist` to 2e-16.
  The aggregator ran on that output.
