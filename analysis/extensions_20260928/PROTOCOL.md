# Post-freeze research extensions — pre-declared protocol (2026-09-28)

Four additive work packages on top of the frozen QSQ manuscript (branch `paper-20260927`,
commit fa49dc8; scientific source commit for codecs/Bader: `893f931b3045b0b628329db81999c2f439d4e830`).
Nothing in `benchmark/`, `stability/`, `validation/`, `mechanism/`, `supplement/` or
`analysis/research_upgrade/` is modified. Each package writes only under
`analysis/extensions_20260928/<WP>/` on its own branch `ext/<WP>-20260928`.

Shared rules

- Frozen inputs are read only. Every number reported must come from a machine-readable file
  written by the package; nothing is transcribed by hand.
- Analysis choices below are fixed before any outcome is seen. If a rule must change for a
  technical reason, record the change and the reason in `DEVIATIONS.md` before rerunning.
- Solver or download failures are recorded per row in `failures.csv` and are never dropped
  from denominators or converted to passes.
- Every package writes `provenance.json` (commit hashes, package versions from `pip freeze`,
  SHA-256 of every input file read, wall time), `RESULTS.md` (numbers with denominators) and
  the CSVs named below. Material-level uncertainty uses a material-cluster bootstrap with
  2,000 resamples and seed 20260928.
- Reader-facing name is QSQ; `A1`/`Protocol A.1` identifiers appear only in file names.

Scientific stack (identical to the P2 execution): Ubuntu, Python 3.12.14,
`validation/requirements-external-e2e.txt` from commit 893f931 (numpy 2.4.6, baderkit 0.10.2,
pysz 1.0.3, zfpy 1.0.1, hdf5plugin 7.0.0, h5py 3.16.0, pymatgen 2025.10.7, scipy 1.18.1).
Density loading, exact-byte verification, codec round trips and Bader settings
(`method="ongrid"`, vacuum tol 1e-3, persistence tol 0.5, no NNA cutoff) are taken from
`validation/external_end_to_end.py` (commit 893f931) and
`validation/qsq_prospective/{development_compatibility_smoke.py,run_p2_fresh_probes.py}`.
Development densities are fetched by the `url` in `materials_metadata.csv` and accepted only
when the SHA-256 matches the `sha256` column.

---

## WP-A — Calibrated risk model for QSQ (no new computation)

Question. Does the continuous QSQ statistic predict fresh-perturbation exceedance risk well
enough to replace the binary gate with a calibrated risk contract?

Inputs. `validation/qsq_prospective/p2_fresh_probes/outcomes.csv` (14,986 trials, column
`bader_response_max_e`), `stability/stability_floor_A1.csv` (`stability_floor_A1_e` = f_m),
`stability/stability_floor_A1_per_seed.csv`, `materials_metadata.csv`.

Predictor. x_m(τ) = log10(f_m / τ) for τ ∈ {1e-4, 1e-3, 1e-2}. Secondary predictors:
log10 of the five-seed median, log10 of the five-seed mean, and the five-seed log10 span.

Outcome. y_{m,s}(τ) = 1[bader_response_max_e ≥ τ] per fresh trial; material-level rate
p_m(τ) = mean over the 59 trials.

Pre-declared fits, each evaluated by 10-fold cross-validation over materials (folds fixed by
SHA-256 of material_id, seed 20260928) and pooled across the three τ with τ as a covariate:
1. Binary gate (reference): risk = 1.600% if x < 0 else 81.325% (the frozen P2 rates).
2. Logistic regression of y on x (trial level, cluster-robust by material).
3. Isotonic regression of p_m on x (monotone non-decreasing).
4. Logistic on x plus the secondary predictors.

Metrics on held-out folds: Brier score, log loss, AUC, expected calibration error with 10
equal-count bins, and a reliability table (bin, n materials, mean predicted, observed).
Bootstrap materials for 95% CI of every metric.

Contract table. For risk levels p* ∈ {0.5%, 1%, 2%, 5%, 10%}, report the largest x at which
the cross-validated isotonic risk ≤ p*, the acceptance coverage (materials admitted / 254) at
that cutoff for each τ, and the observed held-out exceedance rate among the admitted. Compare
coverage with the binary gate at its realized 1.600% risk.

Acceptance. The calibrated model is reported as an improvement only if (i) held-out Brier
score is lower than the binary gate's with a bootstrap 95% CI excluding zero difference, and
(ii) at p* = 2% the coverage at τ = 1e-3 e exceeds 56.3%. Otherwise report that the binary
gate is not improved by the continuous statistic on these data.

Outputs. `WP-A/material_risk.csv`, `WP-A/cv_metrics.csv`, `WP-A/reliability.csv`,
`WP-A/contract_table.csv`, `WP-A/fig_calibration.{png,svg}` (reliability diagram and
risk-vs-x curve), `RESULTS.md`.

---

## WP-B — Second topology-sensitive QoI from the same densities: density critical points

Question. Is QSQ specific to Bader charge, or does it qualify another topology-sensitive QoI
computed from the same CHGCAR?

QoI definition (fixed). On the periodic grid, a voxel is a local maximum of ρ if it is
strictly greater than all 26 periodic neighbours; a local minimum if strictly smaller.
Q_cp = (n_max, n_min) and, atom-resolved, the count of maxima assigned to each atom's Bader
basin of the reference (n_max is the QoI whose change is scored: ΔQ_cp = |n_max(ρ̃) − n_max(ρ)|
plus the Jaccard distance between the two maximum-voxel sets, reported separately). Exact ties
are resolved by the same rule for reference and reconstruction (strict inequality, so a tied
voxel is not a maximum). No smoothing, no interpolation.

Population. All 254 development materials; every row of `benchmark/master_benchmark_full.csv`
whose codec round trip can be regenerated with the frozen wrappers at the stored
`nominal_tolerance_absolute` (reproduction gate: realized L∞ within 0.95–1.05 of the stored
`realized_Linf`; rows failing the gate are listed, not used). Plus the five QSQ perturbation
fields per material (seeds {20260905,1,2,3,4}, amplitude = the material's `probe_linf` from
`stability_floor_A1_per_seed.csv`, same PRNG construction as the frozen stability run:
NumPy Generator(PCG64(seed)) uniform on [−ε, +ε) in the stored field order) and the 59 fresh
iid fields (stream seeds from `validation/qsq_prospective/fresh_seed_jobs.csv`).

If the full ladder is prohibitive in wall time, the pre-declared reduction is: all 254
materials × 3 codecs × the base rungs {1e-6, 1e-5, 1e-4, 1e-3} relative tolerance, and the
five QSQ seeds plus the first 10 fresh seed labels (10000–10009). State which population was
run before computing any statistic.

Pre-declared analyses.
1. QSQ-cp floor: f^cp_m = max over the five seeds of ΔQ_cp. Eligibility at τ_cp ∈ {0, 1, 2}
   changed maxima (τ_cp = 0 means the maximum set must be identical).
2. Prospective test, identical in form to P2: fresh-trial exceedance rate of ΔQ_cp ≥ 1 among
   QSQ-cp-eligible versus screen-rejected materials at τ_cp = 0, with material-cluster CIs
   and the risk ratio.
3. Cross-QoI transfer: agreement (Cohen's κ) between Bader eligibility at 1e-3 e and cp
   eligibility at τ_cp = 0; Spearman ρ between log10 f_m (Bader) and f^cp_m.
4. Codec scoring: fraction of gate-passing reconstructions with ΔQ_cp = 0, by codec and
   nominal tolerance, split by cp-eligibility; certified-at-τ_cp rates with the eligible
   denominator stated.
5. Operator contrast: Spearman ρ between ΔQ_cp and re-derived Bader error on the same rows,
   and the fraction of rows with ΔQ_cp = 0 but Bader error ≥ 1e-3 e (and the converse).

Acceptance. QSQ generalizes to the cp QoI if the prospective risk ratio in analysis 2 exceeds
5 with a 95% CI lower bound above 1. Report the result either way.

Outputs. `WP-B/cp_reference.csv` (per material: n_max, n_min, per-atom maxima), `WP-B/cp_rows.csv`
(per reconstruction), `WP-B/cp_probes.csv` (per perturbation), `WP-B/summary.csv`,
`WP-B/failures.csv`, `RESULTS.md`, `provenance.json`.

---

## WP-C — Codec-shaped perturbation family for QSQ

Question. Is the iid-uniform QSQ family conservative or anti-conservative relative to
perturbations that have the spectral structure of real codec error?

Perturbation construction (fixed). For material m and codec c ∈ {ZFP, SZ3, SPERR}, regenerate
the reconstruction at the base rung with nominal relative tolerance 1e-5 (if that rung is absent
for the pair, use the smallest available base rung and record it). Residual r = ρ̃ − ρ. The
codec-shaped probe is δ_{m,c,k} = ε_m · roll(r, v_k) / ‖r‖∞ where ε_m is the material's frozen
QSQ amplitude and v_k is a periodic shift vector drawn uniformly over the grid from
Generator(PCG64(stream)) with stream = first 8 bytes of SHA-256 over
`QSQ-codecshape|material_id|codec|k`, k ∈ {1,2,3,4,5}. The shift keeps the spectrum of r and
removes its alignment with the atomic positions. Also record the unshifted probe (k = 0).
Measured L∞ of δ must equal ε_m within 1e-12 relative; record it.

Runs. 254 materials × 3 codecs × 6 probes (k = 0..5) = 4,572 Bader re-solves plus 762 codec
round trips. Pre-declared reduction if wall time is prohibitive: k ∈ {0,1,2,3} (3,048 solves);
state which was run.

Pre-declared analyses.
1. Codec-shaped floor f^c_m = max over k ≥ 1 of the Bader response; compare with the iid floor
   f_m: distribution of log10(f^c_m / f_m) by codec and stratum (bulk/slab), median with
   material-bootstrap CI, fraction of materials with f^c_m > f_m.
2. Eligibility agreement: κ between iid eligibility and codec-shaped eligibility at each τ;
   list materials whose verdict flips, with direction.
3. Alignment effect: log10(response at k = 0 / median response over k ≥ 1) by codec; a value
   far from 0 means the reconstruction error's alignment with the structure matters beyond its
   spectrum.
4. Link to the Fourier mechanism: Spearman ρ between log10(f^c_m / f_m) and the material's
   low-G error-energy fraction of that codec's residual (compute the radial spectrum of r with
   the same Nyquist-safe convention as `analysis/hartree_spectral_mechanism`).
5. Predictive value: for the 143 materials admitted at 1e-3 e, does f^c_m predict the P2 fresh
   exceedance rate better than f_m (Spearman ρ with bootstrap CI)?

Acceptance. The iid family is reported as conservative for codec c if the material-median
log10(f^c_m / f_m) is below 0 with a bootstrap 95% CI excluding 0; anti-conservative if above.
Verdict flips are reported as counts, never hidden.

Outputs. `WP-C/probe_outcomes.csv` (one row per material×codec×k with measured L∞, response,
reassigned voxels, labels hash), `WP-C/floors.csv`, `WP-C/agreement.csv`, `WP-C/spectra.csv`,
`WP-C/failures.csv`, `RESULTS.md`, `provenance.json`.

---

## WP-D — Predicting non-evaluability from reference-density descriptors

Question. Can the QSQ floor be anticipated from cheap properties of the reference density and
grid, so that non-evaluability is explained rather than only measured?

Population. All 319 systems in `stability/stability_floor_A1.csv` (254 development + 65
external). Target: log10 f_m; secondary targets: eligibility at 1e-4, 1e-3, 1e-2 e.

Descriptors (fixed list; computed once from the reference density and its reference Bader
partition, one on-grid solve per system):
1. natoms, npoints, mean grid spacing (Å) = (V_cell / npoints)^(1/3), max grid spacing along
   any axis, cell aspect ratio (max/min lattice length), vacuum fraction (voxels with
   ρ < 1e-3 × mean ρ), system type.
2. ε_m (the float32 L∞ amplitude) and ε_m / max ρ, ε_m / median ρ.
3. Boundary sensitivity: fraction of voxels that lie on a basin boundary (at least one of the 26
   periodic neighbours carries a different label); among boundary voxels, the 5th, 50th and
   95th percentiles of the absolute density difference to the neighbouring voxel with a different
   label, each divided by ε_m ("normalized boundary gap"); the fraction of boundary voxels whose
   normalized gap is < 1.
4. Near-tie density: fraction of all voxel pairs (voxel, 26-neighbour) whose absolute density
   difference is < ε_m; fraction < 0.1 ε_m.
5. Basin size: smallest basin volume in voxels and its charge; number of basins with < 100 voxels.
6. Ordering fragility: number of axis-order flips induced by the k = 20260905 seed
   (`n_axis_order_flips_noise` from the per-seed table) — included as a diagnostic only, in a
   separate model, because it requires the perturbation.

Pre-declared modelling. (a) Univariate Spearman ρ of each descriptor with log10 f_m, with
bootstrap CI, ranked. (b) Ridge regression of log10 f_m on the standardized descriptor set
(groups 1–5), α chosen by inner 5-fold CV; performance by 10-fold CV over systems (folds by
SHA-256 of material_id, seed 20260928): R², RMSE in decades, and stratified by dev/ext and
bulk/slab. (c) Logistic classification of eligibility at each τ from the same descriptors:
CV AUC, and precision/recall at the operating point that keeps false-eligible rate ≤ 5%.
(d) A held-out check: fit on the 254 development systems only, evaluate on the 65 external
systems, report R² and AUC.

Acceptance. The descriptor model is reported as explanatory if held-out R² ≥ 0.5 on the
external 65 and the top three descriptors are the same in (a) and in the ridge coefficients.
Report otherwise as "measured, not yet predictable" with the achieved numbers.

Outputs. `WP-D/descriptors.csv` (one row per system), `WP-D/univariate.csv`, `WP-D/cv_metrics.csv`,
`WP-D/coefficients.csv`, `WP-D/external_holdout.csv`, `WP-D/fig_predictor.{png,svg}`,
`WP-D/failures.csv`, `RESULTS.md`, `provenance.json`.

---

## Reporting back

Each package ends with a commit on `ext/<WP>-20260928` pushed to `origin`, and a final message
that quotes the acceptance verdict, the primary numbers with denominators, the population
actually run, wall time, and every failure count. If the push is impossible, the final message
must contain the full RESULTS.md and the CSV row counts, and the working tree must be left in
place.
