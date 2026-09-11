# P4 first-run compressed-stage failure taxonomy

Status: **COMPLETE_BEFORE_RETRY**

All **144/144** recorded failures were assigned to one of two pre-solver/solver-path engineering families; **0 unclassified failures** remain.

| Failure family | Count | Scientific computation reached? | Authorized fix |
|---|---:|---|---|
| SPERR work directory not created | 72 | Codec did not start | Create the per-condition parent directory, then call the unchanged frozen SPERR codec |
| Henkelman work directory not created | 72 | Reconstruction exists; independent solver did not start | Create the per-condition solver directory, then call the unchanged validated Henkelman adapter |

Affected states: **9**. Codec counts: SPERR 72, SZ3 36, ZFP 36. Solver counts: Henkelman 108, BaderKit 36.

## Retry boundary

The first run remains immutable. Retry may execute only the 144 recorded failure keys. No candidate pair, target atom, reference margin, codec, codec tolerance, QSQ threshold, solver definition, or decision policy may change. Previously successful 72 cells must be reused, not rerun for primary accounting.
