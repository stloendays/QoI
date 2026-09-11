# QoI — stability-qualified chemical-fidelity benchmark for lossy DFT charge-density compression

Data release for the RhoCodec project (NUS, 2026). Every reported number is generated from a file in this package; nothing here is transcribed by hand.

## Central question

This project is **not** built around the already-established observation that pointwise reconstruction error does not automatically guarantee downstream quantity-of-interest (QoI) fidelity. The central question is stricter:

> **Can a requested downstream QoI tolerance be scientifically certified at all before a compressor is judged against it?**

For a material and requested chemical tolerance `tau`, the benchmark first qualifies whether the uncompressed Bader analysis is numerically identifiable at that scale under the frozen Protocol A.1 probe. Only then is a reconstructed density allowed to enter pass/fail certification.

Accordingly, the benchmark distinguishes three states:

- **eligible + certified** — the QoI is resolvable at `tau` and the reconstruction satisfies the Bader contract;
- **eligible + not certified** — the QoI is resolvable, but the reconstruction violates the contract;
- **NON_EVALUABLE_BADER_UNSTABLE** — the uncompressed QoI itself is not stable at `tau`, so the codec is neither credited nor penalized at that precision.

This makes the project a benchmark of **QoI certifiability and benchmark validity**, rather than a generic QoI-aware compression study.

**Frozen evaluation protocol:** `protocol/PROTOCOL_A1.md` (current) and `protocol/PROTOCOL_A_archived.md` (superseded, kept unchanged). Claim-by-claim status: `paper/CLAIM_EVIDENCE_MATRIX.md`. Current narrative reframe: `paper/NARRATIVE_REFRAME_20260911_CERTIFIABILITY.md`.

## Layout

| Path | Content |
|---|---|
| `benchmark/master_benchmark_full.csv` | **The master table.** 6 343 rows = 4 627 base-ladder rows (254 materials × 3 codecs × up to 9 tolerances) + 1 716 tight-ladder rows (143 Protocol-A.1-eligible materials × 3 codecs × 4 tolerances). One row per (material, codec, nominal tolerance). |
| `benchmark/master_benchmark_base_ladder.csv`, `..._tight_ladder.csv` | The same rows split by ladder. |
| `benchmark/summary_a1.csv`, `pairwise_a1.csv`, `best_certified_a1.csv` | Protocol-A.1-qualified statistics: best certified ratio per material, medians with paired-bootstrap 95 % CIs, pairwise win fractions. |
| `benchmark/lossless_baselines.jsonl` | f64+zstd, f64+xz, f32+zstd per material. |
| `stability/stability_floor_A1.csv` | Protocol A.1 stability floor per material (max over 5 seeds), 319 systems. |
| `stability/stability_floor_A1_per_seed.csv` | The 5 per-seed rows behind each floor, with voxel-reassignment and order-flip counts. |
| `stability/stability_floor_A_archived_float32.csv` | The archived float32 probe (Protocol A). Retained as record; not used for any statistic. |
| `stability/probe_calibration.csv` | 18-material calibration run before A.1 was frozen: float32 vs 5 noise seeds vs 3 amplitudes. |
| `stability/eligibility_by_threshold_A1.csv`, `eligibility_summary_A1.csv` | Per-material ELIGIBLE / NON_EVALUABLE_BADER_UNSTABLE at τ ∈ {1e-4, 1e-3, 1e-2} e, with the archived Protocol A verdict beside it. |
| `mechanism/basin_error_decomposition_per_atom.csv` | Every atom of 12 representative materials × 3 codecs × 3 tolerances: `dq_total = dq_integrand + dq_domain` row by row. |
| `mechanism/basin_error_decomposition_summary.csv` | The same cases summarised at the atom of largest total error. |
| `supplement/` | S1 (no exclusion), S2 (dQ / own floor), S3 (inflated threshold k=2,5,10), S4 (probe amplitude sensitivity). |
| `materials_metadata.csv` | 319 systems: corpus, system type, formula, grid, atom count, source URL, SHA-256 of the source file, licence. |
| `failure_registry.csv` | Every Bader-solver failure and excluded case, with reason. Failures are not counted as passes. |
| `external_test_MANIFEST.json` | The frozen strict-external corpus, scored once. |
| `protocol/` | Protocols A and A.1, external validation, and baseline closure. |
| `paper/` | Claim–evidence matrix, figure map, manuscript drafts, probe validation, and the 2026-09-11 certifiability reframe. |
| `RESULTS.md` | Full chronological record with the command behind every number, including corrections of record. |

## Certification semantics

For material `m` and requested QoI tolerance `tau`, let `stability_floor_A1_e(m)` be the independently measured Protocol A.1 floor.

`eligible(m, tau) := stability_floor_A1_e(m) < tau`

For reconstruction row `r`:

`certified(r, tau) := eligible(m, tau) AND Bader_error_resolved_e(r) < tau`

If `eligible(m, tau)` is false, the correct benchmark state is **non-evaluable**, not codec failure. This distinction is essential at strict tolerances, where the Bader analysis itself may not be numerically identifiable at the requested precision.

## Master table columns (`benchmark/master_benchmark_full.csv`)

| Column | Meaning |
|---|---|
| `material_id` | `mp-*` Materials Project bulk, `nomad-*` NOMAD slab/adsorbate. Join key to every other file. |
| `system_type` | `bulk` / `slab`. |
| `corpus` | `dev_bulk` / `dev_slab` (development corpora; external corpora enter the stability tables separately). |
| `formula` | Reduced formula from source provenance. |
| `codec`, `codec_config` | `SZ3`, `ZFP`, `SPERR` with frozen configurations. |
| `ladder` | `base` or `tight`. The tight ladder exists to probe the transition toward an analysis-limited regime, not merely to extend codec settings. |
| `nominal_tolerance_relative` | Requested absolute error bound divided by the field peak-to-peak range. |
| `nominal_tolerance_absolute` | Bound passed to the codec. |
| `realized_Linf` | **Measured** max |reconstruction − original| over all voxels. |
| `realized_Linf_over_nominal` | `realized_Linf / nominal_tolerance_absolute`; used to show that equal nominal tolerance is not a codec-independent distortion scale. |
| `bound_respected` | Whether the realized pointwise error satisfies the requested codec bound. |
| `rmse`, `mean_signed_error` | Pointwise reconstruction statistics. |
| `raw_bytes`, `compressed_bytes`, `compression_ratio`, `bits_per_value` | Storage-rate statistics. |
| `Bader_error_fixed_e` | Bader charge error evaluated on original basins. Diagnostic only because it suppresses domain migration. |
| `Bader_error_resolved_e` | Max per-atom Bader charge error after re-deriving basins from the reconstructed density. This is the chemical contract. |
| `fixed_basin_understatement` | `resolved / fixed`. |
| `electron_count_abs_dev` | Global electron-count deviation. |
| `n_voxels_reassigned`, `frac_voxels_reassigned` | Basin-label changes after reconstruction. |
| `stability_floor_A1_e` | Protocol A.1 material-specific numerical/topological stability scale. |
| `stability_floor_A_archived_e` | Archived Protocol A floor. Not used for current statistics. |
| `eligible_A1_at_{τ}` | Whether the material is numerically identifiable at threshold `τ`. |
| `certified_at_{τ}` | Eligibility-qualified Bader certification flag. **This is the pass flag used for headline numbers.** |
| `certified_at_{τ}_ignoring_eligibility` | Diagnostic pass flag without stability qualification. Used to quantify benchmark reclassification. |
| `npoints`, `natoms`, `value_ptp` | Field/system size information. |
| `encode_seconds`, `bader_seconds` | Wall-clock timings. |
| `field_sha256_prefix` | Provenance hash prefix. |

Rows for a (material, codec, tolerance) that fail inside the Bader solver are absent from the master table and logged in `failure_registry.csv`. A material excluded at a threshold remains present with `eligible_A1_at_{τ} = False` and status `NON_EVALUABLE_BADER_UNSTABLE`; it is neither a pass nor a fail there.

## Scientific interpretation

The current manuscript distinguishes three layers:

1. **Established background:** raw-data/pointwise error alone is not a universal downstream scientific guarantee.
2. **Benchmark-validity contribution:** a requested downstream tolerance must be independently qualified for numerical identifiability before codec scoring.
3. **Bader-specific mechanism:** density-dependent basin migration produces irregular, topology-sensitive error propagation and motivates an analysis-limited regime at very tight perturbations.

The strongest final paper should therefore quantify how naive pass/fail results change after eligibility qualification, and test whether the tight-ladder Bader plateau corresponds quantitatively to the independently measured Protocol A.1 stability scale.

## Provenance

All source densities are public. Source URLs, byte counts and SHA-256 hashes are stored in `materials_metadata.csv` and `external_test_MANIFEST.json`. Bader partitions use the frozen grid-based analysis procedure documented in the protocol and manuscript files.

Scripts that produced these files live in the RhoCodec code repository and are referenced throughout `RESULTS.md` and the paper evidence files.
