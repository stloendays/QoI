# Research extensions WP-E, WP-F, WP-G — pre-declared protocol (2026-09-30)

Author-authorized reopening (user instruction, 2026-09-30: "开始做1，2，3吧") of the scope re-frozen in
`paper/QOI_GENERALITY_SCOPE_ADDENDUM_20260930.md`, for three additive work packages that answer the
questions a higher-tier venue asks next: *what does qualification buy in practice* (WP-F), *can it be
run as a tool* (WP-E), and *does it survive the standard all-electron Bader practice* (WP-G).

Branch `ext/WP-EFG-20260930`, created from `origin/paper/qoi-generality-integration-20260930` at
`fa6e230`. Every package writes only under `analysis/extensions_20260930/<WP>/`. Nothing in
`benchmark/`, `stability/`, `validation/`, `mechanism/`, `supplement/`, `analysis/research_upgrade/`
or `analysis/extensions_20260928/` is modified.

This file, `WP-F/frame.csv.gz`, `WP-F/strata.csv`, `WP-F/sample.csv` and `WP-G/aeccar_availability.csv`
are committed and pushed **before** any density of the WP-F sample or any AECCAR is read and before
WP-E computes any policy outcome. The frame, the strata and the sample depend only on object names
and byte sizes; the AECCAR availability table only on HTTP HEAD responses.

## Shared rules (unchanged from the 2026-09-28 protocol)

- Frozen inputs are read only; every reported number comes from a machine-readable file written by
  the package; nothing is transcribed by hand.
- Analysis choices below are fixed before any outcome is seen. A technically forced change is
  recorded in `<WP>/DEVIATIONS.md` with its reason before the affected step is rerun.
- Download, parse, memory and solver failures are recorded per row in `failures.csv` and are never
  dropped from denominators or converted to passes. WP-F additionally assigns every failed object the
  conservative storage outcome defined below.
- Each package writes `provenance.json` (commit hashes, `pip freeze`, SHA-256 of every input read,
  wall time), `RESULTS.md` (numbers with denominators) and the CSVs named below.
- Material-level uncertainty: material-cluster bootstrap, 2,000 resamples, seed 20260930. WP-F uses
  the stratified bootstrap defined in its section.

Scientific stack: the pinned stack of the frozen study and of WP-B (Python 3.12.14, numpy 2.4.6,
baderkit 0.10.2, pysz 1.0.3, zfpy 1.0.1, hdf5plugin 7.0.0, h5py 3.16.0, pymatgen 2025.10.7, scipy
1.18.1) in `D:\Research\QoI-final4-local\venv`, on Windows 11, as WP-B ran (WP-B `DEVIATIONS.md` 1).
Density loading (`development_compatibility_smoke.build_grid`, MP branch), codec round trips
(`external_end_to_end.codec_roundtrip`) and Bader settings (`method="ongrid"`, vacuum tol 1e-3,
persistence tol 0.5, no NNA cutoff) come from the frozen scientific checkout at commit
`893f931b3045b0b628329db81999c2f439d4e830`. The QSQ probe is the frozen one: amplitude ε = the
field's float32 amplitude max|float32(ρ) − ρ|, seeds {20260905, 1, 2, 3, 4},
`Generator(PCG64(seed)).uniform(−ε, ε, size=field.shape)` added in stored field order; the QSQ floor
f_m is the maximum re-derived Bader response over the five seeds; eligibility at τ is f_m < τ;
τ ∈ {1e-4, 1e-3, 1e-2} e with 1e-3 e primary. A reconstruction is certified at τ when the material is
eligible at τ and its re-derived Bader error max_atom |q(ρ̃) − q(ρ)| < τ.

---

## WP-E — A certifying writer: qualification, codec search and certificate as one tool

Question. Can the benchmark's decision procedure be run per object as a writer that emits a
compressed field together with its certificate, at a small fraction of the cost of an exhaustive
ladder, without giving up archive-level compression?

Inputs (read only). `benchmark/master_benchmark_full.csv` (6,343 rows: per row codec, nominal relative
tolerance, `compressed_bytes`, `raw_bytes`, `Bader_error_resolved_e`, `eligible_A1_at_*`),
`stability/stability_floor_A1.csv`. No new computation.

Policies (fixed). For each material and τ, the writer first runs QSQ (cost: 1 reference + 5 probe
Bader solves). A non-eligible material is not compressed by the writer. For an eligible material each
policy explores that material's recorded ladder per codec (rungs sorted by tolerance) and returns the
certified row with the largest compression ratio it has *evaluated*; a row counts as evaluated when
the policy queries its Bader error (cost 1 solve each).
1. `EXHAUSTIVE` — evaluate every rung of every codec (the oracle).
2. `SCAN` — per codec, evaluate from the loosest rung downwards and stop at the first certified rung;
   return the best of the three codecs.
3. `BISECT` — per codec, binary search over rung index assuming certification is monotone in
   tolerance (lo = tightest, hi = loosest; test the middle; certified -> move looser, not -> tighter);
   return the loosest certified rung evaluated; best of the three codecs.
4. `SCAN-<codec>` and `BISECT-<codec>` for each single codec (no codec search).

Metrics at each τ over eligible materials: archive compression = Σ raw_bytes / Σ stored bytes, where
stored bytes = the returned row's `compressed_bytes`, or `raw_bytes` when the policy returns nothing;
fraction of the oracle archive compression; per-material shortfall distribution (returned CR / oracle
CR); Bader solves per material (QSQ + evaluations); fraction of eligible materials with no certified
row found although one exists. Certificate validity is by construction (every returned row was
evaluated); it is re-checked mechanically.

Acceptance. Adopt, for WP-F, the policy with the fewest mean solves whose archive compression at
τ = 1e-3 e is ≥ 0.98 × the oracle's and whose miss rate (eligible with a certifiable row but none
returned) is ≤ 2%. If no multi-codec policy meets both, WP-F uses `SCAN`. The chosen policy and the
reason are written to `WP-E/adopted_policy.json` before WP-F reads its first density.

Outputs. `WP-E/policy_material.csv`, `WP-E/policy_summary.csv`, `WP-E/adopted_policy.json`,
`WP-E/fig_writer.{png,svg}`, `RESULTS.md`, `provenance.json`.

---

## WP-F — What qualification buys: the Materials Project charge-density archive

Question. Applied to the public Materials Project charge-density archive, how much storage does
QSQ-gated, Bader-certified compression save, and what fraction of the archive is non-evaluable?

Frame. Every object `chgcars/mp-<n>.json.gz` in the public bucket `materialsproject-parsed`, listed
anonymously on 2026-09-30 (`WP-F/frame.csv.gz`: 415,475 objects, 8.5008 TB), minus the 186 objects of
the frozen development set: N = 415,289 objects, 8.4976 TB.

Strata and sample (drawn, `WP-F/draw_sample.py`). Stored-size deciles D01–D09 of the frame, 30 objects
each; the top decile split at 80 MB and 150 MB into D10a/D10b/D10c with 15/10/5 objects. Within a
stratum the objects with the smallest SHA-256("QSQ-WPF-20260930|" + task_id) are taken. n = 300.
`WP-F/strata.csv` gives N_frame and total bytes per stratum.

Per object. Download the exact object (bytes and SHA-256 recorded; the frame's size must match),
load with the frozen MP loader, record grid shape, natoms, spin channels, crystal system and space
group (pymatgen, symprec 0.1), value range and ε. Reference Bader, five QSQ probes, f_m, eligibility at
each τ. Sizes: MP json.gz bytes (current archive), raw float64 bytes (8 × npoints), lossless bytes
(zlib level 6 on the float64 array in stored order).

Codec evaluation. Strata D01–D09: the full union ladder (ZFP and SPERR 1e-7 … 1e-1, 13 rungs; SZ3
1e-7 … 3e-2, 12 rungs; relative to the field's value range, the frozen convention) with a Bader
re-solve for every rung, which serves all three τ and is also the prospective check of the WP-E
policy. Strata D10a–D10c: the adopted WP-E policy at each τ, sharing evaluated rungs across τ.
A rung whose realized L∞ exceeds its absolute bound is recorded and never certified.

Storage rule at τ. Certified → the chosen reconstruction's compressed bytes. Eligible but nothing
certified, or non-evaluable → lossless bytes. Failed object (download, parse, memory, solver) → its
current MP json.gz bytes, i.e. no saving is credited. Objects whose loaded grid exceeds the memory this
machine can hold are attempted once and then counted as failed under this rule.

Estimators. Stratified (expansion) estimators T̂_x = Σ_h (N_h / n_h) Σ_{i∈s_h} x_i for x ∈ {json.gz
bytes, float64 bytes, lossless bytes, stored bytes at τ}. Primary endpoint: the archive reduction
factor R(τ) = T̂_json / T̂_stored(τ) at τ = 1e-3 e and the implied saving 8.4976 TB × (1 − 1/R).
Secondary: R against float64 and against lossless; the byte-weighted and count-weighted non-evaluable
fraction at each τ; the certified codec mix; per-stratum results. Uncertainty: stratified bootstrap
(resample objects with replacement within each stratum, 2,000 resamples, seed 20260930), 95% percentile
intervals. The design weights and the failure rule are applied exactly as written; no object is
dropped or reweighted after its outcome is known.

Prospective writer check (D01–D09). For each τ, the WP-E adopted policy is replayed on the full
ladders of the new objects; report its fraction of the oracle archive compression and its miss rate
with the new-object denominator.

Acceptance. The archive result is reported as a storage saving if the lower 95% bound of R(1e-3 e)
exceeds 1.5; otherwise the achieved R and interval are reported as they are.

Cost and reduction. Expected about 10–14 h on this machine (small strata 4 workers, top-decile strata
1 worker). If the projected wall time after 50 small objects exceeds 30 h, the pre-declared reduction
is: D01–D09 switch to the adopted WP-E policy (as D10), recorded in `DEVIATIONS.md` before continuing.

Outputs. `WP-F/objects.csv` (one row per sampled object: metadata, sizes, ε, f_m, eligibility, per-τ
stored bytes and chosen codec/rung), `WP-F/rungs.csv` (every evaluated reconstruction),
`WP-F/estimates.csv`, `WP-F/strata_results.csv`, `WP-F/writer_prospective.csv`, `WP-F/failures.csv`,
`WP-F/fig_archive.{png,svg}`, `RESULTS.md`, `provenance.json`.

---

## WP-G — Does qualification survive all-electron-reference Bader?

Question. Standard VASP practice partitions the valence CHGCAR with basins of the all-electron
reference ρ_AE = AECCAR0 + AECCAR2. Do eligibility, certification and the codec ranking change under
that practice, and does it matter whether the reference itself is compressed?

Population. The development MP materials whose task has both AECCAR0 and AECCAR2 published
(`WP-G/aeccar_availability.csv`: 53 of 186). AECCARs are fetched from the same task id; the AECCAR
grid must equal the CHGCAR grid (otherwise the material is a recorded failure). All 53 are paired with
their frozen valence-reference results.

Arms.
- Reference: Bader with charge_grid = total_charge_grid = CHGCAR, reference_grid = ρ_AE.
- G1 (reference kept exact): CHGCAR perturbed by the frozen five-seed QSQ probe (ε of CHGCAR) → f_m^G1;
  CHGCAR compressed at every rung of that material's frozen ladder (same codec, same absolute bound as
  the frozen row) → re-derived error with the exact ρ_AE reference.
- G2 (reference also compressed): both fields perturbed, the reference with its own float32 amplitude
  ε_AE and stream seed = first 8 bytes (little-endian) of SHA-256("QSQ-WPG|material_id|seed") → f_m^G2;
  both fields compressed with the same codec at the same relative rung of their own value range →
  re-derived error. Stored bytes in G2 are the sum of both compressed fields.

Pre-declared analyses. (1) Eligibility at each τ: frozen valence reference vs G1 vs G2, paired
(McNemar exact test), with the 53 as denominator. (2) Floors: material-median log10(f^G1_m / f_m) and
log10(f^G2_m / f_m) with bootstrap CI. (3) Certification: best certified compression ratio per codec at
each τ under each arm vs the frozen rows of the same materials; codec ranking (share of materials where
each codec is best) per arm. (4) Basin-reassignment fraction under G1 and G2 on the same rungs.

Acceptance. "QSQ is needed under the standard practice" is reported if, at τ = 1e-3 e, G2 leaves at
least 10% of the 53 materials non-evaluable; "an exact all-electron reference removes the instability"
is reported if G1 makes ≥ 95% eligible while G2 does not. Either way the numbers are reported.

Cost and reduction. About 80 Bader solves per material (≈ 4–6 h with 4 workers). If projected wall
time exceeds 16 h, the ladder is reduced to the rungs {1e-6, 1e-5, 1e-4, 1e-3} for every codec,
recorded in `DEVIATIONS.md` before continuing.

Outputs. `WP-G/reference.csv`, `WP-G/probes.csv`, `WP-G/rows.csv`, `WP-G/summary.csv`,
`WP-G/failures.csv`, `WP-G/fig_ae_reference.{png,svg}`, `RESULTS.md`, `provenance.json`.

---

## Execution and monitoring

WP-F and WP-G run as checkpoint-resumable local jobs (one checkpoint per object / material under
`D:\Research\QoI-ext-cache\WP-F` and `…\WP-G`), launched as cdesktop-detach jobs and supervised by the
registered QoI extension monitor (`C:\Users\ASUS\.claude\tools\qoi_ext_monitor.py`, shown in the
监控总台), whose restart budget, stall, failure-fraction, disk, aggregation and push checks apply
unchanged. Each package ends with a commit on `ext/WP-EFG-20260930` pushed to origin and a final
report quoting the acceptance verdict, the primary numbers with denominators, the population run,
wall time and every failure count.
