# P3 numerical robustness and implementation-transfer validation

Status: **FROZEN_PRE_EXECUTION**

This protocol is fixed while the prospective P2 fresh-probe experiment is running. P3 outcomes must not be used to alter the frozen five-seed QSQ gate, P2 seed set, perturbation amplitude, or thresholds.

## Scientific question

P3 asks a narrower question than P2: does QSQ stratification survive reasonable changes in Bader implementation, and which part of the observed instability is attributable to the downstream numerical analysis rather than the compressor?

It does **not** claim that a finite implementation comparison establishes a unique physical Bader charge. It also does not equate interpolation of an existing density with an electronic-structure convergence calculation.

## Existing evidence retained as prior mechanism evidence

The completed `mechanism/independent_bader_20260908` study is retained unchanged. It contains 1,560/1,560 planned rows on 12 stratified development representatives plus one separately labelled sentinel, using BaderKit 0.10.2 on-grid and Henkelman Bader 1.05 on-grid/near-grid. That study is mechanism characterization, not population prevalence.

P3 extends the implementation-transfer test to the independently frozen 24-system convergence panel in `validation/qsq_prospective/convergence_panel.csv`.

## P3A: 24-system implementation-transfer panel

### Frozen panel

Use exactly the 24 systems already selected by deterministic SHA-256 ordering: bulk/slab crossed with four original QSQ-floor strata, three systems per stratum. Do not replace a difficult system after execution starts. Source failures are recorded as unresolved.

### Fields

For every material evaluate:

1. the unperturbed source density;
2. the five original QSQ iid-uniform perturbations with seed labels `{20260905, 1, 2, 3, 4}` and the original material-specific amplitude.

This gives 24 x 6 = 144 fields. Run each field through all three analysis implementations below, for 432 solver evaluations.

### Analysis implementations

1. BaderKit 0.10.2 on-grid with the frozen benchmark settings;
2. Henkelman Bader 1.05 on-grid with the already validated input-format adapter;
3. Henkelman Bader 1.05 near-grid with the same adapter.

Each implementation compares each perturbed field with its **own** unperturbed baseline. Keep full-precision lattice, coordinates, atom ordering, grid shape and density serialization checks. Retain the previous `2e-6 e` accounting tolerance for printed Henkelman charges. A threshold decision within `2e-6 e` of a threshold is reported as ambiguous, not forced to pass/fail.

### Primary endpoint

At `tau = 1e-3 e`, compare the original BaderKit QSQ eligibility classification with the classification obtained from each Henkelman implementation using the same five fields and the same strict rule `max response < tau`.

Report:

- 2x2 classification table and agreement fraction;
- eligible-to-rejected and rejected-to-eligible switches separately;
- Cohen's kappa as a descriptive agreement statistic;
- floor rank correlation across the 24 systems;
- baseline per-atom charge disagreement before perturbation;
- all ambiguous threshold cases;
- results separately for bulk/slab and floor stratum, without treating the stratified panel as a prevalence sample.

Secondary thresholds are `1e-4 e` and `1e-2 e` and are explicitly secondary.

### Interpretation gate

A strong result is not defined as perfect numerical equality. The scientifically relevant question is whether low-risk/high-risk stratification is preserved under a reasonable independent implementation. Large classification switches that coincide with large unperturbed baseline disagreement are reported as an implementation-definition boundary rather than hidden.

P3A can support implementation transfer of the **screening stratification**. It cannot by itself establish density-grid convergence or a universal physical Bader reference.

## P3B: genuine density-grid recomputation

P3B must not run until an execution addendum records sufficient original electronic-structure provenance for each selected case: code/version, exchange-correlation functional, pseudopotential/PAW dataset identity, spin state, k-point mesh, ENCUT, smearing, cell/coordinates, charge convention, and the settings controlling the real-space/FFT density grid.

For cases with fully recoverable provenance, perform new static electronic-structure calculations rather than resampling the archived density. Freeze at least three density-grid levels before viewing Bader outcomes: the archived/native level and two systematically finer levels. Hold the physical calculation settings fixed apart from the grid-control variable(s), and record whether the self-consistent density itself or only the output/integration grid changes.

For each level record source hashes, grid dimensions, integrated electron count, total energy consistency, Bader charges from at least BaderKit on-grid and Henkelman on-grid, and the five-seed QSQ response using a clearly defined amplitude policy. Do not silently redefine the perturbation amplitude across grid levels; if both fixed-absolute-amplitude and level-specific-float32-amplitude analyses are useful, report them as separate estimands.

### P3B endpoint

For each recoverable system quantify whether the QSQ classification at `1e-3 e` is stable to grid refinement and whether the magnitude of the measured floor converges, drifts monotonically, or remains implementation/grid dependent.

If exact source calculation provenance is not recoverable for a case, label P3B **not evaluable for genuine electronic-structure grid convergence**. Interpolation/downsampling may be used only as a separate numerical sensitivity control and must never be described as a new DFT convergence calculation.

## Provenance and no-retuning rules

- Preserve `convergence_panel.csv` byte-for-byte.
- Record source-density SHA-256 and atom order for every evaluation.
- Reuse the validated Henkelman input adapter; do not modify basin/integration code.
- Record compiler, executable hash, Python environment and solver version.
- All solver/source failures remain in the denominator for accounting and are separately reported.
- No P3 result changes the P2 analysis or original five-seed gate.
- P3 is a targeted numerical-robustness experiment, not a new population estimate.

## Completion criteria

P3A is complete only when all 432 planned solver evaluations are accounted for as success, ambiguous threshold result, or explicit failure and a machine-readable comparison table is committed.

P3B is complete only for systems whose original electronic-structure provenance is sufficiently recovered and whose newly computed density files, run metadata and analysis outputs have immutable hashes. A smaller honest P3B subset is preferable to a larger pseudo-convergence analysis based on interpolated archived fields.
