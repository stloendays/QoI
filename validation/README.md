# External end-to-end rate–fidelity validation

This directory contains the frozen external validation path for the QoI benchmark.
It is deliberately separated from development benchmarking so that external data
cannot be used for parameter tuning.

## Scientific contract

```text
frozen source
  -> provenance/integrity gate
  -> Protocol A.1 intrinsic QoI stability
  -> ELIGIBLE or NON_EVALUABLE_BADER_UNSTABLE
  -> frozen codec tolerance policy
  -> codec round trip + realized L_inf audit
  -> fixed-basin Bader diagnostic
  -> re-derived/resolved Bader QoI
  -> topology/domain-migration diagnostics
  -> CERTIFIED or NOT_CERTIFIED
  -> best certified ratio / Certified Compression Ratio (CCR)
```

The resolved-basin Bader error is the certification metric. The fixed-basin
error is retained as a mechanism diagnostic and must not replace the resolved
metric in headline certification.

## External populations: 65 descriptive, 63 confirmatory

The frozen external manifest contains **65 systems**: 37 AFLOW bulk and 28 NOMAD
2D. All 65 remain in the corpus-scale run and the complete row-level table is
released.

Two systems were used as implementation sentinels and their rate–fidelity outputs
were inspected before the corpus-scale run:

- `aflow-Ni1_ICSD_181716` — AFLOW provenance/parser + E2E sentinel;
- `nomad2d-0XHkHlmw3DQ_` — NOMAD 2D + three-codec E2E sentinel.

They therefore remain in the **all-65 descriptive analysis**, but are excluded
from the primary untouched rate–fidelity confirmation set. The primary
confirmatory cohort was frozen before corpus-scale execution as the remaining
**63 systems = 36 bulk + 27 vacuum2d**. Its expected Protocol A.1 eligible counts
are **16 / 42 / 57** at `1e-4 / 1e-3 / 1e-2 e`.

The split is machine-readable in `external_rate_fidelity_split.json` and the
pre-specified analysis is in
`../protocol/EXTERNAL_RATE_FIDELITY_ANALYSIS_PLAN.md`. No additional material may
be moved between descriptive and confirmatory sets after that freeze.

This split applies only to the new rate–fidelity analysis. The previously
completed Protocol A.1 stability validation on the frozen 65-system corpus is a
separate analysis and is unchanged.

## Verdict and failure semantics

- `CERTIFIED`: Protocol A.1 eligible and a retained codec setting has
  resolved-Bader error < tau.
- `NOT_CERTIFIED`: eligible, but no successful retained codec setting satisfies
  the resolved-Bader contract at tau.
- `NON_EVALUABLE_BADER_UNSTABLE`: intrinsic A.1 floor >= tau. Neither pass nor fail.
- material-level `PIPELINE_FAILURE`: source provenance, parser, original-grid
  audit, or original-Bader failure prevents the material from entering the
  benchmark. This is a hard validation failure.
- row-level failure: one `(material, codec, tolerance)` execution fails after the
  material has entered the benchmark. The failed row is absent from the successful
  rate–fidelity table and is written to `formal_external_e2e_row_failures.csv`.
  It is never counted as a pass and does **not** erase successful rows for the
  same material.

This row-level behavior intentionally matches the released development
`failure_registry.csv` semantics.

## Files

- `external_end_to_end.py` — low-level external E2E harness; used by the two
  implementation-sentinel smoke paths.
- `aflow_parser_smoke.py` — parser/provenance-only multi-species AFLOW check. It
  performs no codec round trip and no Bader calculation, so it does not create a
  rate–fidelity observation on a confirmatory material.
- `formal_external_e2e.py` — formal driver reproducing the frozen staged tolerance
  policy and development row-failure semantics.
- `aggregate_formal_external.py` — merges shards, audits corpus coverage and
  computes material-level certification, CCR, development-shaped summaries and
  pairwise codec comparisons.
- `build_confirmatory_external.py` — removes only the two pre-frozen sentinel IDs
  from the all-65 aggregate and re-runs the **same** aggregator for the 63-system
  confirmatory cohort.
- `preflight_formal_external.py` — verifies frozen 65-system corpus/stability/
  ladder invariants.
- `preflight_confirmatory_split.py` — verifies the frozen 65/2/63 split and
  16/42/57 confirmatory eligibility denominators.
- `test_aggregate_semantics.py` — synthetic test of eligibility, no-certification,
  row-failure, CCR and pairwise denominator semantics.
- `test_confirmatory_postprocessor.py` — synthetic all65 -> confirmatory63
  postprocessing contract test.

Machine-readable workflow semantics are in
`../protocol/QOI_WORKFLOW_SPEC_V1.yaml`.

## Frozen staged tolerance policy

The exact tolerance values are recovered from
`../benchmark/master_benchmark_full.csv`; they are not re-entered or tuned from
external outcomes.

1. Base ladder: all external materials.
2. Tight ladder (`relative tolerance < 1e-5`): only materials with Protocol A.1
   stability floor `< 1e-3 e`, matching the development tight-ladder selection.
3. Base ladder runs from tight to loose and stops after the first **successful**
   retained point with `Bader_error_resolved_e >= 0.05 e`, including that boundary
   point. A failed row does not establish the early-stop condition.
4. No tolerance is added, removed or chosen after inspecting corpus-scale external
   rate–fidelity outcomes.

## Statistical unit

The inferential unit is the **material**, not the tolerance row. For each
`material x codec x tau`, the best certified ratio is

```text
CCR_i,c(tau) = max compression_ratio among retained settings certified at tau.
```

`CCR` is therefore a formal name for the same best-certified-ratio quantity used
in the released development summaries, not a new post-hoc metric. Certification
fractions, medians, bootstrap confidence intervals and pairwise wins are computed
from these material-level records.

If a material is eligible but a codec has no certified setting, that codec has no
CCR on the material. In pairwise comparisons it is not silently removed: a codec
with a CCR beats one without a CCR; two codecs without a CCR tie. The median
`log2(CCR_a/CCR_b)` effect size is reported only for materials where both CCRs
exist.

The **63-system confirmatory summary is primary** for external rate–fidelity
generalization. The corresponding all-65 summary is descriptive and is retained
for completeness and auditability.

## GitHub Actions layers

### `External E2E Preflight`

Cheap integrity CI. It verifies:

- the frozen 65-system corpus (37 bulk + 28 NOMAD 2D);
- A.1 full-corpus eligibility counts 18 / 44 / 59;
- the 6,343-row development master table and base/tight policy;
- the frozen 65/2/63 rate–fidelity split and confirmatory counts 16 / 42 / 57;
- material-level aggregation semantics;
- the all65 -> confirmatory63 postprocessor.

### `External E2E Smoke`

Regression/protocol closure. The two already-declared implementation sentinels
exercise the NOMAD and AFLOW E2E paths. A separate multi-species AFLOW check is
**parser-only** and intentionally does not compute rate–fidelity.

### `External E2E Frozen Pilot`

The two implementation sentinels are run across the complete staged frozen
policy and all three codecs. Its purpose is to validate formal sampling,
row-failure isolation, early stopping, aggregation, CCR and pairwise logic before
corpus-scale execution. Pilot results are not part of the 63-system confirmatory
population.

### `External E2E Full`

Eight shards run all 65 frozen systems. The aggregate job then produces:

1. `formal_external_all65/` — complete 65-system descriptive result set;
2. `formal_external_confirmatory63/` — primary 63-system confirmatory result set,
   derived solely by removing the two pre-frozen sentinel IDs and invoking the
   same aggregator.

The full workflow is not triggered by ordinary code pushes.

## Formal aggregate outputs

Each analysis set contains:

- `formal_external_e2e_rows.csv` — successful retained row-level benchmark table;
- `material_audit.csv` — one row per selected material, including row attempts,
  row failures and early-stop boundaries;
- `formal_external_e2e_failures.csv` — hard material-level pipeline failures;
- `formal_external_e2e_row_failures.csv` — explicit failed
  `(material, codec, tolerance)` attempts;
- `best_certified_external.csv` — complete `material x codec x tau` table with
  eligibility, status, row-failure flags and CCR when certified;
- `external_summary_a1.csv` — development-compatible material-level summary;
- `pairwise_external.csv` — material-level codec win/tie/loss fractions and
  median log2 CCR ratio;
- `external_codec_summary.csv` — compact certification/CCR summary;
- `summary.json` — coverage, failures, codec-bound audit, eligibility counts and
  input-quality flags.

The confirmatory directory also contains `confirmatory_metadata.json`, including
the frozen split SHA-256 and the two excluded sentinel IDs.

## Claim boundary

Before the corpus-scale run succeeds, the defensible claim remains that the
workflow has been internally benchmarked, stress-tested, and externally validated
for the stability-qualification component.

After a successful confirmatory run, defensible wording is:

> The complete chemistry-aware rate–fidelity workflow was evaluated end-to-end
> on a pre-specified 63-system confirmatory cohort drawn from the frozen external
> corpus, with two previously inspected systems retained separately as
> implementation sentinels.

Do **not** describe all 65 systems as untouched rate–fidelity confirmation data,
and do not call this Bader-charge case study a universal standard.
