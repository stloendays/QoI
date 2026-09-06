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
  material has entered the benchmark (for example a Bader solver failure at a
  loose ZFP tolerance). The failed row is absent from the rate–fidelity table and
  is written to `formal_external_e2e_row_failures.csv`. It is never counted as a
  pass and does **not** erase successful rows for the same material.

This row-level behavior intentionally matches the released development
`failure_registry.csv` semantics.

## Files

- `external_end_to_end.py` — low-level external E2E harness; also used by smoke tests.
- `formal_external_e2e.py` — formal driver that reproduces the frozen staged
  tolerance policy and development row-failure semantics.
- `aggregate_formal_external.py` — merges shards, audits corpus coverage and
  computes material-level certification, CCR, development-shaped summaries and
  pairwise codec comparisons.
- `preflight_formal_external.py` — verifies frozen corpus/stability/ladder
  invariants before formal computation is allowed to start.

Machine-readable workflow semantics are in
`protocol/QOI_WORKFLOW_SPEC_V1.yaml`.

## Frozen staged tolerance policy

The exact tolerance values are recovered from
`benchmark/master_benchmark_full.csv`; they are not re-entered or tuned from
external outcomes.

1. Base ladder: all external materials.
2. Tight ladder (`relative tolerance < 1e-5`): only materials with Protocol A.1
   stability floor `< 1e-3 e`, matching the development tight-ladder selection.
3. Base ladder runs from tight to loose and stops after the first **successful**
   retained point with `Bader_error_resolved_e >= 0.05 e`, including that boundary
   point. A failed row does not establish the early-stop condition.

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

## GitHub Actions layers

### `External E2E Preflight`

Cheap integrity CI. It verifies frozen invariants including 65 external systems
(37 AFLOW bulk + 28 NOMAD 2D), A.1 eligibility counts, the 6,343-row development
master table, base/tight row counts and tolerance ladders, and the historical
codec-bound contract.

### `External E2E Smoke`

Regression/protocol closure. One NOMAD 2D system and one AFLOW bulk system at a
single debug tolerance. Preflight runs first; then the test exercises both the
NOMAD analysis path and AFLOW pre-VASP5 provenance/parser path.

### `External E2E Frozen Pilot`

One frozen AFLOW bulk + one frozen NOMAD 2D system across the complete staged
frozen tolerance policy and all three codecs. Its purpose is to validate formal
sampling, row-failure isolation, early stopping, aggregation, CCR and pairwise
logic before a corpus-scale run.

### `External E2E Full`

Eight shards over the frozen 65-system corpus, gated by preflight and followed by
mandatory coverage/failure/bound auditing and material-level aggregation. The
full workflow is not triggered by ordinary code pushes.

## Formal aggregate outputs

- `formal_external_e2e_rows.csv` — successful retained row-level benchmark table.
- `material_audit.csv` — one row per selected material, including row attempts,
  row failures and early-stop boundaries.
- `formal_external_e2e_failures.csv` — hard material-level pipeline failures.
- `formal_external_e2e_row_failures.csv` — explicit failed
  `(material, codec, tolerance)` attempts, using the development failure-registry
  schema.
- `best_certified_external.csv` — complete `material x codec x tau` table with
  eligibility, status, row-failure flags and CCR when certified.
- `external_summary_a1.csv` — development-compatible material-level summary:
  admitted/non-evaluable/certified counts, certification fraction, median CCR,
  deterministic bootstrap 95% CI and quantiles.
- `pairwise_external.csv` — material-level codec win/tie/loss fractions and
  median log2 CCR ratio, analogous to `benchmark/pairwise_a1.csv`.
- `external_codec_summary.csv` — compact view of the same certification/CCR summary.
- `summary.json` — corpus coverage, hard/row-level failures, codec-bound audit,
  A.1 eligible counts and input-quality flags.

## Claim boundary

Until the full frozen 65-system run completes successfully, the correct claim is
that the workflow has been internally benchmarked, stress-tested, and externally
validated for the stability-qualification component. A successful full run
supports the narrower statement that the complete rate–fidelity workflow was
evaluated end-to-end on the frozen untouched 65-system external corpus. It does
not by itself establish a universal standard for other QoIs or scientific fields.
