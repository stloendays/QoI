# Data and Software Availability — JCTC Submission Draft v0.1

**Status:** internal submission draft; replace archival placeholders before the manuscript is formally submitted.

## Preferred final statement

> **Data and Software Availability.** The data underlying this study, including the successful compression benchmark, Protocol A.1 stability measurements, failure registry, material metadata and provenance, mechanism-summary data, and supplementary sensitivity tables, are available in the archived research release at **[ZENODO/OTHER PERSISTENT REPOSITORY DOI]**. The scripts used for benchmark post-processing, realized-\(L_\infty\) matching, complete-case sensitivity analysis, statistical modeling, figure-data generation, and manuscript-number validation are included in the same archived release. The development repository is available at **https://github.com/stloendays/QoI**. The archived release is pinned to Git commit **[SUBMISSION COMMIT SHA]** and release tag **[SUBMISSION TAG]**. Source-dataset provenance, source URLs, checksums, and licensing information are recorded in `materials_metadata.csv` and the repository documentation.

## Minimum archive contents before submission

The persistent archive should contain, at minimum:

- `benchmark/master_benchmark_full.csv` — 6,343 successful reconstructions, including the 4,627-row base ladder and 1,716-row tight ladder.
- `failure_registry.csv` — 77 registered exceptions/failures kept outside the successful master table.
- `stability/` — Protocol A.1 per-material floor, five-seed table, archived Protocol A table, probe calibration, eligibility tables, and summaries.
- `benchmark/summary_a1.csv`, `benchmark/pairwise_a1.csv`, `benchmark/best_certified_a1.csv`, and lossless baselines.
- `mechanism/` — the representative mechanism summary; add `basin_error_decomposition_per_atom.csv` if it is available before submission.
- `supplement/` — sensitivity tables used by the Supporting Information.
- `materials_metadata.csv` — corpus provenance, system metadata, source URLs, SHA-256 values, and license fields.
- `protocol/`, `paper/`, and `RESULTS.md` — frozen protocol definitions and evidence records.
- statistical scripts and generated tables used for realized-error matching, failure sensitivity, mechanism attenuation, global-conservation negative control, and figure generation.

## Current repository-state caveat

At present, the working GitHub repository is private and the full per-atom mechanism table has not yet landed on `main`. The JCTC/JCIM reproducibility editorial effective May 1, 2026 states that original research articles should include a Data and Software Availability Statement and that data/code needed to reproduce key results should be made available at submission whenever possible. Therefore the preferred submission route is:

`frozen submission commit -> immutable release/tag -> Zenodo (or equivalent) archive -> DOI inserted into manuscript`

Do not submit the preferred statement above with placeholders still present.

## If the per-atom table is still unavailable at submission

The paper remains scientifically supportable because the direct algebraic mechanism claim is explicitly restricted to the current representative 12-material summary. In that case:

- archive and cite the current representative mechanism summary;
- do not claim that per-atom data are part of the submission archive;
- retain the representative-set scope in the manuscript and SI;
- add the per-atom table only in a later revision if it becomes available and is used to support revised claims.

## Repository integrity rule

The persistent archive should correspond exactly to the submitted scientific state. Record:

- manuscript version;
- Git commit SHA;
- release tag;
- archive DOI;
- hashes for the submitted manuscript, SI, TOC graphic, and final figure files.
