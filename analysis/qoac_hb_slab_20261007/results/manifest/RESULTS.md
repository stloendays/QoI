# QOAC-HB slab confirmation (32 fresh P3b slabs) — frozen criteria (PROTOCOL.md `7e2799c`)

CI run 37579899219 (workflow `qoac_hb_slab.yml`, head `b006a1f`, 2026-10-07 06:08–07:06 UTC, conclusion success);
results commit `f23c035`. 13/32 materials successful, 19 FAILED, 0 setting failures. Criteria evaluated with
`evaluate_criteria.py` unchanged (`CRITERIA.json` in this directory); its tests pass (5/5).
Bootstrap: seed 20261007, 10,000 resamples of the median.

## Primary analysis (N = 32, all planned)

| criterion | result | threshold | pass |
|---|---|---|---|
| 1. analyzable and jointly certified (R3, best post, all three tau_B) | 13/32 | >= 31/32 | no |
| 2. joint overhead at tau_B = 1e-4 (CR_hartree_only / CR_joint) | n = 13, median 1.000, CI [1.000, 1.011] | <= 1.10, CI upper <= 1.15 | yes |
| 3. utility at tau_B = 1e-4 (R3 / max of J, T1, GF at their best posts) | 13/32 wins, median 1.398, CI [1.306, 1.517], min 1.141 | >= 24/32, > 1.10, CI lower > 1.00 | no |

**Confirmatory FAIL** (criteria 1 and 3, both on the count). PROTOCOL.md section 5 recorded before the run that
criterion 1 could reach at most 17/32, because 15/32 entries have no AECCAR.

## Pre-registered secondary analysis (N = 17 with an AECCAR reference)

| criterion | result | threshold | pass |
|---|---|---|---|
| 1. analyzable and jointly certified | 13/17 | >= 17/17 | no |
| 2. joint overhead at tau_B = 1e-4 | n = 13, median 1.000, CI [1.000, 1.011] | <= 1.10, CI upper <= 1.15 | yes |
| 3. utility at tau_B = 1e-4 | 13/17 wins, median 1.398, CI [1.306, 1.517], min 1.141 | >= 13/17, > 1.10, CI lower > 1.00 | yes |

**FAIL** (criterion 1).

## Failures (19 materials, counted as not certified and not a win)

- 15 with no AECCAR next to the CHGCAR (`AECCAR0 unavailable`), as listed in PROTOCOL.md section 2.
- 4 with an AECCAR, failed at reference loading in `run_joint_v2.process` before any compression:

| material | error | AECCAR0 / AECCAR2 bytes (gz) | grid |
|---|---|---|---|
| `nomad-IZPVe_A6_quS` | `RuntimeError: invalid AECCAR` | 149,832 / 10,705,587 | 60x84x480 |
| `nomad-ViaCyatoI3FA` | `RuntimeError: invalid AECCAR` | 122,602 / 13,702,551 | 56x140x252 |
| `nomad-DcwYU1UzKNe8` | `RuntimeError: invalid AECCAR` | 102,964 / 11,502,532 | 96x80x216 |
| `nomad-hk3gUBk-5QN5` | `ValueError: string or file could not be read to its end due to unmatched data` | 9,599,764 / 17,857,135 | 112x112x224 |

`invalid AECCAR` is raised by HB v2's check `ae.shape != chg.shape or not np.all(np.isfinite(ae))`
(`run_joint_v2.py` line 245). Byte counts and SHA-256 of all eight downloads match `aeccar_sources.csv`
(`aeccar_downloads.csv`). Per PROTOCOL.md section 6 these are per-material results inside completed shards and are not
retried.

## Descriptive (13 analysed slabs; npoints 677,376–3,870,720; 4–51 atoms)

- Certified R3 best-post streams: 39/39 (13 materials x 3 tau_B), every one with maximum atomic-charge error <= tau_B
  (largest error / tau_B 0.800) and reassigned-voxel fraction 0.
- R3 best joint post-processor: `none` in 13/13 at tau_B = 1e-3; `none` 7/13 and `hap:0.0001` 6/13 at 1e-4;
  `hap:0.0001` 12/13 and `none` 1/13 at 1e-5.
- Median joint overhead: 1.000 at 1e-3 and 1e-4, 1.009 at 1e-5. Median R3 joint CR: 678.6 at 1e-3 and 1e-4, 672.9 at
  1e-5.
- CTP decisions (R3, evaluated rows): projected 0/52 at 1e-3, 1/29 at 1e-4, 5/9 at 1e-5.
- Median joint CR at tau_B = 1e-4: R3 678.6, J 485.3, T1 333.1, GF 30.8.
- Utility ratio at 1e-4: 13/13 > 1, range 1.141–1.682.

The same descriptive script reproduces HB v2's P2 values from its committed aggregate (best posts, median overhead
1.000, median R3 CR 298.4, CTP 0/192, 0/192, 31/165, 144/144 streams, utility range 1.096–1.694).
