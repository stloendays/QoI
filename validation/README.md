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
  -> Certified Compression Ratio (CCR)
```

The resolved-basin Bader error is the certification metric. The fixed-basin
error is retained as a mechanism diagnostic and must not replace the resolved
metric in headline certification.

## Verdicts

- `CERTIFIED`: Protocol A.1 eligible and resolved-Bader error < tau.
- `NOT_CERTIFIED`: eligible, but resolved-Bader error >= tau.
- `NON_EVALUABLE_BADER_UNSTABLE`: intrinsic A.1 floor >= tau. Neither pass nor fail.
- `PIPELINE_FAILURE`: provenance/parser/solver/execution failure. Never silently excluded.

## Files

- `external_end_to_end.py` — low-level external E2E harness; also used by smoke tests.
- `formal_external_e2e.py` — formal driver that reproduces the frozen staged
  tolerance policy used in the development benchmark.
- `aggregate_formal_external.py` — merges shards, audits corpus coverage and
  computes material-level certification and CCR summaries.

Machine-readable workflow semantics are in
`protocol/QOI_WORKFLOW_SPEC_V1.yaml`.

## Frozen staged tolerance policy

The exact tolerance values are recovered from
`benchmark/master_benchmark_full.csv`; they are not re-entered or tuned from
external outcomes.

1. Base ladder: all external materials.
2. Tight ladder (`relative tolerance < 1e-5`): only materials with Protocol A.1
   stability floor `< 1e-3 e`, matching the development tight-ladder selection.
3. Base-ladder reporting stops after the first retained point with
   `Bader_error_resolved_e >= 0.05 e`, including the boundary point.

## GitHub Actions layers

### `External E2E Smoke`

Regression/protocol closure. One NOMAD 2D system and one AFLOW bulk system at a
single debug tolerance. Runs automatically on relevant harness changes.

### `External E2E Frozen Pilot`

One frozen AFLOW bulk + one frozen NOMAD 2D system across the complete staged
frozen tolerance policy and all three codecs. Its purpose is to validate the
formal sampling policy, aggregation and CCR logic before a corpus-scale run.

### `External E2E Full`

Eight shards over the frozen 65-system corpus (37 AFLOW bulk + 28 NOMAD 2D),
followed by a mandatory coverage/failure/bound audit and aggregate summary.
The full workflow is not triggered by ordinary code pushes.

## Formal aggregate outputs

- `formal_external_e2e_rows.csv` — retained row-level benchmark table.
- `material_audit.csv` — one row per selected material, including failures and
  the number of computed/retained rows.
- `formal_external_e2e_failures.csv` — explicit pipeline failures.
- `best_certified_external.csv` — material x codec x tau table containing CCR.
- `external_codec_summary.csv` — certification fraction and median CCR by
  codec, tau and external stratum.
- `summary.json` — corpus coverage, codec-bound audit, input-quality flags and
  failure count.

## Claim boundary

Until the full frozen 65-system run completes successfully, the correct claim is
that the workflow has been internally benchmarked, stress-tested, and externally
validated for the stability-qualification component. A successful full run
supports the narrower statement that the complete rate–fidelity workflow was
evaluated end-to-end on the frozen untouched 65-system external corpus. It does
not by itself establish a universal standard for other QoIs or scientific fields.
