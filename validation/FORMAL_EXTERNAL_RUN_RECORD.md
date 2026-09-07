# Formal external E2E run record

## Corpus-scale run 1

- GitHub Actions workflow: `External E2E Full`
- Run ID: `34074537547`
- Trigger commit: `893f931b3045b0b628329db81999c2f439d4e830`
- Trigger event: push of `validation/FULL_EXTERNAL_TRIGGER`
- Frozen descriptive corpus: 65 systems = 37 AFLOW bulk + 28 NOMAD 2D
- Primary confirmatory rate–fidelity cohort: 63 systems = 36 AFLOW bulk + 27 NOMAD 2D
- Excluded implementation sentinels: `aflow-Ni1_ICSD_181716`, `nomad2d-0XHkHlmw3DQ_`
- Confirmatory Protocol A.1 eligible counts fixed before corpus-scale execution:
  - tau = 1e-4 e: 16
  - tau = 1e-3 e: 42
  - tau = 1e-2 e: 57
- Scientific stack: installed from `validation/requirements-external-e2e.txt`; every shard archives exact `pip freeze`, Python version, requirements SHA-256 and Git commit.
- Execution: 8 shards, frozen staged development-derived tolerance policy, ZFP + SZ3 + SPERR.

### Preflight

**PASS.** Before any corpus-scale codec/Bader computation, the workflow verified:

1. frozen 65-system corpus and development sampling-policy invariants;
2. frozen 65/2/63 reporting split;
3. material-level aggregation/failure semantics;
4. all-65 to confirmatory-63 postprocessing semantics.

### Scientific-change lock

After this run was triggered, no change to Protocol A.1, codec settings, tolerance ladders, eligibility thresholds, early-stop rule, failure-accounting semantics, or confirmatory population is permitted in response to corpus-scale outcomes. Any later methodological change requires a separately versioned protocol/run and cannot replace this run retrospectively.

### Current state

At the most recent recorded check, preflight had completed successfully and all eight shard jobs were executing the frozen external sweep. Final status, aggregate hashes and headline outcomes will be appended only after the workflow reaches a terminal state.
