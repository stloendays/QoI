# QoI — chemical-fidelity benchmark of lossy compression for DFT charge densities

Data release for *Chemical Fidelity Is Not a Pointwise Error: Topology-Induced
Failure Modes in Lossy Compression of Electronic Densities* (RhoCodec project,
NUS, 2026). Every number in the paper is generated from a file in this package;
nothing here is transcribed by hand.

**Frozen evaluation protocol:** `protocol/PROTOCOL_A1.md` (current) and
`protocol/PROTOCOL_A_archived.md` (superseded, kept unchanged). Claim-by-claim
status with the retracted numbers: `paper/CLAIM_EVIDENCE_MATRIX.md`.

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
| `failure_registry.csv` | 77 entries: every Bader-solver failure and every excluded case, with reason. Failures are not counted as passes. |
| `external_test_MANIFEST.json` | The frozen strict-external corpus (37 AFLOW bulk + 28 NOMAD 2D), scored once. |
| `protocol/` | Protocols A and A.1, the external-validation report, the BQB / den2bin baseline closure with unit conversions. |
| `paper/` | Claim–evidence matrix, figure map, the probe-validation section. |
| `RESULTS.md` | Full chronological record with the command behind every number, including the corrections of record. |

## Master table columns (`benchmark/master_benchmark_full.csv`)

| Column | Meaning |
|---|---|
| `material_id` | `mp-*` Materials Project bulk, `nomad-*` NOMAD slab/adsorbate. Join key to every other file. |
| `system_type` | `bulk` / `slab`. |
| `corpus` | `dev_bulk` / `dev_slab` (development corpora; the external corpora enter only the stability tables). |
| `formula` | Reduced formula from the source provenance. |
| `codec`, `codec_config` | `SZ3` (pysz 1.0.3, ABS, INTERP_LORENZO), `ZFP` (zfpy 1.0.1, fixed-accuracy), `SPERR` (hdf5plugin 7.0.0, absolute, single chunk). |
| `ladder` | `base` (1e-5 … 1e-1 relative, early-stopped once re-derived Bader error ≥ 0.05 e) or `tight` (1e-7 … 3e-6, A.1-eligible materials only). |
| `nominal_tolerance_relative` | Requested absolute error bound divided by the field's peak-to-peak range. |
| `nominal_tolerance_absolute` | The bound actually passed to the codec, in the field's units (e/Å³ × cell volume as stored). |
| `realized_Linf` | **Measured** max |reconstruction − original| over all voxels. |
| `realized_Linf_over_nominal` | `realized_Linf / nominal_tolerance_absolute`; ≤ 1 for every row (`bound_respected` is True for all 6 343 rows). ZFP typically realises well below its bound; SZ3 and SPERR sit at it. |
| `bound_respected` | `realized_Linf ≤ nominal × (1 + 1e-6)`. |
| `rmse`, `mean_signed_error` | Pointwise error statistics. |
| `raw_bytes`, `compressed_bytes`, `compression_ratio`, `bits_per_value` | Against float64 (8 B/value). Convert to other references with `protocol/EXTERNAL_BASELINES.md` §2. |
| `Bader_error_fixed_e` | max over atoms of |Q_a(recon, **original** basins) − Q_a(orig)|. The wrong metric; kept as a diagnostic. |
| `Bader_error_resolved_e` | max over atoms of |Q_a(recon, basins **re-derived** from recon) − Q_a(orig)|. The chemical contract. Units: electrons. |
| `fixed_basin_understatement` | `resolved / fixed`. |
| `electron_count_abs_dev` | |mean(recon) − mean(orig)|. |
| `n_voxels_reassigned`, `frac_voxels_reassigned` | Voxels whose Bader basin label changed after reconstruction. |
| `stability_floor_A1_e` | Protocol A.1 floor of this material (max over 5 noise seeds at the float32 L∞ amplitude). |
| `stability_floor_A_archived_e` | The archived float32-probe floor. Not used. |
| `eligible_A1_at_{τ}` | `stability_floor_A1_e < τ` — the material is admissible at that threshold. |
| `certified_at_{τ}` | `eligible_A1_at_{τ} AND Bader_error_resolved_e < τ` — this row passes the chemical contract at τ. **This is the pass flag used for every headline number.** |
| `certified_at_{τ}_ignoring_eligibility` | The pass flag without the stability qualification (Supplement S1). |
| `npoints`, `natoms`, `value_ptp` | Grid size, atom count, field peak-to-peak. |
| `encode_seconds`, `bader_seconds` | Wall time of the codec and of the Bader re-solve on the reconstruction. |
| `field_sha256_prefix` | First 32 hex characters of the SHA-256 of the source file (full hash in `materials_metadata.csv`). |

Rows for a (material, codec, tolerance) that failed inside the Bader solver
are absent from the master table and present in `failure_registry.csv`
(`category = bader_solver_failure`, 76 such entries, almost all ZFP at loose
tolerance on slabs). A material excluded at a threshold is present in the
master table with `eligible_A1_at_{τ} = False` and listed in
`stability/eligibility_by_threshold_A1.csv` with status
`NON_EVALUABLE_BADER_UNSTABLE`; it is neither a pass nor a fail there.

## Provenance

All source densities are public: Materials Project (CC BY 4.0), NOMAD
(CC BY 4.0), AFLOW (consortium terms). No DFT calculation was run for this
work. Source URLs, byte counts and SHA-256 are in `materials_metadata.csv` and
`external_test_MANIFEST.json`. Bader partitions: `baderkit` 0.10.2,
`method="ongrid"`.

Scripts that produced these files live in the RhoCodec repository
(`scripts/honest_benchmark.py`, `honest_benchmark_tight.py`,
`stability_floor_noise.py`, `probe_calibration.py`, `build_eligibility_a1.py`,
`mechanism_decomposition_per_atom.py`, `summarize_benchmark_a1.py`,
`supplement_sensitivity.py`, `build_release_package.py`).
