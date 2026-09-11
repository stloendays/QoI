# QoI — stability-qualified chemical-fidelity benchmark for lossy DFT charge-density compression

Data release for the RhoCodec project (NUS, 2026). Every reported number is generated from a file in this package; nothing here is transcribed by hand.

## Central question

This project is **not** built around the already-established observation that pointwise reconstruction error does not automatically guarantee downstream quantity-of-interest (QoI) fidelity. The central question is stricter:

> **Can a requested downstream QoI tolerance be scientifically certified at all before a compressor is judged against it?**

For a material and requested chemical tolerance `tau`, the benchmark first applies **QoI Stability Qualification (QSQ)** to determine whether the uncompressed Bader analysis is numerically identifiable at that scale. Only then is a reconstructed density allowed to enter pass/fail certification.

Accordingly, the benchmark distinguishes three states:

- **eligible + certified** — the QoI is resolvable at `tau` and the reconstruction satisfies the Bader contract;
- **eligible + not certified** — the QoI is resolvable, but the reconstruction violates the contract;
- **NON_EVALUABLE_BADER_UNSTABLE** — the uncompressed QoI itself is not stable at `tau`, so the codec is neither credited nor penalized at that precision.

This makes the project a benchmark of **QoI certifiability and benchmark validity**, rather than a generic QoI-aware compression study.

**Reader-facing method name:** **QoI Stability Qualification (QSQ)**. The concrete operation is a **perturbation-based numerical identifiability test**, or simply a **stability probe**. The historical files `protocol/PROTOCOL_A1.md` and `protocol/PROTOCOL_A_archived.md` are retained as frozen provenance; their version-style identifiers are not the preferred scientific names. Claim-by-claim status: `paper/CLAIM_EVIDENCE_MATRIX.md`. Current narrative: `paper/CURRENT_PAPER_STORY_20260911.md`.

## Headline benchmark-validity result

The central audit uses **254 development materials × 3 codecs = 762 material–codec decisions per Bader threshold**. A conventional binary benchmark reports the following failures before eligibility is considered:

| Bader contract | Naive failures | Reclassified as non-evaluable | Genuine eligible failures | Naive failures reclassified |
|---|---:|---:|---:|---:|
| `1e-4 e` | 533 | 518 | 15 | **97.2%** |
| `1e-3 e` | 310 | 296 | 14 | **95.5%** |
| `1e-2 e` | 108 | 61 | 47 | 56.5% |

Thus, at the two strictest contracts, **more than 95% of apparent codec failures cannot be scientifically attributed to the compressor** because the reference Bader analysis is not independently resolvable at the requested precision.

This correction is not a permissive exclusion rule. It also invalidates apparent successes: at `1e-4 e`, **106 of 229 naive passes (46.3%) are themselves non-evaluable**. The benchmark therefore changes from an invalid binary label space to a three-state scientific decision.

The formal result is visualized in **Figure 3**, generated from `figures/R/figure3_certification_landscape.R`; the script recomputes all counts from `benchmark/master_benchmark_full.csv` and contains frozen assertions that fail if the headline numbers drift.

## Layout

| Path | Content |
|---|---|
| `benchmark/master_benchmark_full.csv` | **The master table.** 6 343 rows = 4 627 base-ladder rows (254 materials × 3 codecs × up to 9 tolerances) + 1 716 tight-ladder rows (143 QSQ-eligible materials × 3 codecs × 4 tolerances). One row per (material, codec, nominal tolerance). |
| `benchmark/master_benchmark_base_ladder.csv`, `..._tight_ladder.csv` | The same rows split by ladder. |
| `benchmark/summary_a1.csv`, `pairwise_a1.csv`, `best_certified_a1.csv` | QSQ-qualified statistics. Historical `_a1` filenames are preserved for reproducibility. |
| `benchmark/lossless_baselines.jsonl` | f64+zstd, f64+xz, f32+zstd per material. |
| `stability/stability_floor_A1.csv` | QSQ stability floor per material (maximum over 5 seeds), 319 systems. Historical `_A1` filename preserved. |
| `stability/stability_floor_A1_per_seed.csv` | The five per-seed rows behind each QSQ floor, with voxel-reassignment and order-flip counts. |
| `stability/stability_floor_A_archived_float32.csv` | Archived float32 predecessor. Retained as provenance; not used for current statistics. |
| `stability/probe_calibration.csv` | 18-material pre-freeze calibration comparing the archived float32 probe with QSQ perturbations and amplitude sensitivity. |
| `stability/eligibility_by_threshold_A1.csv`, `eligibility_summary_A1.csv` | Per-material ELIGIBLE / NON_EVALUABLE_BADER_UNSTABLE states at τ ∈ {1e-4, 1e-3, 1e-2} e. Historical filenames retained. |
| `analysis/CERTIFIABILITY_AUDIT_20260911.md` | Frozen binary-to-three-state reclassification audit and interpretation boundaries. |
| `analysis/certifiability_reclassification_pooled_20260911.csv` | Exact pooled decision counts behind Figure 3 and the 97.2% / 95.5% headline result. |
| `analysis/certifiability_reclassification_by_codec_20260911.csv` | The same reclassification audit split by codec. |
| `mechanism/basin_error_decomposition_per_atom.csv` | Every atom of 12 representative materials × 3 codecs × 3 tolerances: `dq_total = dq_integrand + dq_domain` row by row. |
| `mechanism/basin_error_decomposition_summary.csv` | The same cases summarised at the atom of largest total error. |
| `supplement/` | Machine-readable sensitivity, stability-floor, matching, mechanism and rate–fidelity assets used by the SI. |
| `materials_metadata.csv` | 319 systems: corpus, system type, formula, grid, atom count, source URL, SHA-256 of the source file, licence. |
| `failure_registry.csv` | Every Bader-solver failure and excluded case, with reason. Failures are not counted as passes. |
| `external_test_MANIFEST.json` | The frozen strict-external corpus, scored once. |
| `protocol/` | Frozen internal protocol/provenance records. Reader-facing method terminology is defined in `paper/NAMING_AND_TERMINOLOGY_POLICY.md`. |
| `paper/CURRENT_PAPER_STORY_20260911.md` | Compact canonical statement of what the paper now claims, the headline numbers, supporting evidence, and claim boundaries. |
| `paper/` | Claim–evidence matrix, figure map, polished manuscript, SI, naming policy, reference audits and provenance drafts. |
| `figures/R/figure3_certification_landscape.R` | Formal R source for the central binary → three-state certification figure; PNG/PDF/SVG outputs are in `figures/R/rendered/`. |
| `RESULTS.md` | Full chronological record with the command behind every number, including corrections of record. |

## Certification semantics

For material `m` and requested QoI tolerance `tau`, let `f_QSQ(m)` denote the independently measured QSQ stability floor. The underlying machine-readable column remains `stability_floor_A1_e` for frozen-schema compatibility.

`eligible(m, tau) := f_QSQ(m) < tau`

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
| `stability_floor_A1_e` | Frozen-schema field containing the **QSQ material-specific stability floor**. |
| `stability_floor_A_archived_e` | Frozen-schema field containing the archived float32-probe floor; not used for current statistics. |
| `eligible_A1_at_{τ}` | Frozen-schema field containing the **QSQ eligibility** decision at threshold `τ`. |
| `certified_at_{τ}` | Eligibility-qualified Bader certification flag. **This is the pass flag used for headline numbers.** |
| `certified_at_{τ}_ignoring_eligibility` | Diagnostic pass flag without stability qualification. Used to quantify benchmark reclassification. |
| `npoints`, `natoms`, `value_ptp` | Field/system size information. |
| `encode_seconds`, `bader_seconds` | Wall-clock timings. |
| `field_sha256_prefix` | Provenance hash prefix. |

Rows for a (material, codec, tolerance) that fail inside the Bader solver are absent from the master table and logged in `failure_registry.csv`. A material excluded at a threshold remains present with the historical-schema field `eligible_A1_at_{τ} = False` and status `NON_EVALUABLE_BADER_UNSTABLE`; it is neither a pass nor a fail there.

## Current scientific interpretation

The manuscript now separates five layers of evidence:

1. **Established background:** raw-data/pointwise error alone is not a universal downstream scientific guarantee.
2. **Central benchmark-validity result:** the downstream tolerance itself must be independently qualified for numerical identifiability before codec scoring. Figure 3 shows that 97.2% and 95.5% of naive failures at `1e-4 e` and `1e-3 e` are non-evaluable rather than genuine eligible codec failures.
3. **Qualification-method validation:** QSQ replaces the archived order-preserving float32 probe with a calibrated five-seed perturbation procedure that can excite the relevant Bader partition sensitivity.
4. **Bader-specific mechanism:** density-dependent basin migration explains why the local charge response can become irregular and why fixed-basin scoring can substantially understate the re-derived Bader error.
5. **Fair comparison and confirmation:** realized-distortion matching controls nominal-tolerance confounding, and the untouched 63-system cohort tests the frozen decision logic without retuning.

The tight-ladder evidence is intentionally phrased conservatively. At `1e-4 e`, certified Bader errors are on the same scale as the independent **QSQ stability floor** (median error/floor ≈ 1.09–1.33× across codecs), supporting the statement that the **strictest certified regime is floor-scale, consistent with an emerging analysis-limited regime**. The current evidence does not justify a universal material-level claim that `plateau = floor`.

The paper's output is therefore not an unconditional codec leaderboard. It is a **stability-qualified rate–fidelity decision problem**: only eligible material-threshold pairs enter codec success/failure scoring, and codec comparison must account for realized rather than nominal reconstruction distortion.

## Naming and provenance

Reader-facing manuscript, figure, caption, SI and presentation text should use **QoI Stability Qualification (QSQ)** rather than development-version labels. The terms **QSQ stability floor**, **QSQ eligibility**, **QSQ perturbation probe**, and **archived float32 probe** are preferred. Historical filenames, column names, commits and frozen protocol documents containing `A`, `A1`, or `_A1` remain unchanged so the released benchmark is reproducible.

All source densities are public. Source URLs, byte counts and SHA-256 hashes are stored in `materials_metadata.csv` and `external_test_MANIFEST.json`. Bader partitions use the frozen grid-based analysis procedure documented in the protocol and manuscript files.

Scripts that produced these files live in the RhoCodec code repository and are referenced throughout `RESULTS.md` and the paper evidence files.