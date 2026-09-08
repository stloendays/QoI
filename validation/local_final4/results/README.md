# Final four external E2E local recovery

This package preserves the actual local recovery outcomes of GitHub Actions run
**34113606495**. Slots 03 and 09 previously failed with HTTP 500/network timeout;
slots 10 and 16 previously exceeded the Actions six-hour limit during Bader work.
This local execution imposed no material or Bader calculation timeout.

Frozen scientific commit: `893f931b3045b0b628329db81999c2f439d4e830`.

The local host is Windows 11, using isolated CPython 3.12.14 and the exact
scientific package pins from the frozen requirements. It is not represented as a
Linux runtime. The full package freeze, platform/CPU/RAM, requirements SHA256,
timestamps, commands, exit codes, and output verification are archived.

No scientific semantics were modified: Protocol A.1, all three tau values,
frozen tolerance ladders, Bader parameters, early stopping, certification,
failure rules, corpus membership, material IDs, and codec settings are unchanged.
All tracked frozen files passed a byte-level comparison against their Git blobs.
All formal commands requested `--codecs zfp,sz3,sperr`. A request does not imply
codec execution when materialization/original Bader fails first.

Windows Git initially checked out all 63 tracked text files with CRLF line
endings. The first slot 03 attempts and slot 09 metadata therefore record hashes
of those CRLF files. During slot 09, all tracked files were restored directly
from their frozen Git blobs; all differences were verified as CRLF-to-LF only.
No Python statement, numeric value, CSV content, or scientific parameter changed.
The initial audit and timestamped before/after hashes are preserved in
`provenance/initial_frozen_audit.json` and
`provenance/checkout_newline_normalization.json`. Original run metadata is kept
unaltered; its early CRLF hashes are not misrepresented as raw Git blob hashes.
The requirements hash in runtime.json is the exact file used for installation.

The Windows orchestration wrapper runs sequentially, archives each attempt in a
separate directory, and verifies formal outputs after return. It allows up to
three identical attempts for slots 03/09 only on explicit transient I/O errors.
Every failure is retained. Retries neither replace data sources nor alter hashes.

## Observed outcomes

| Slot | Material | Status | Total seconds (all attempts) | Successful rows | Row failures | Material failures | Retries |
|---|---|---|---:|---:|---:|---:|---:|
| 03 | aflow-Cl1O12Pb5V3_ICSD_203074 | FAILED | 108.56200000003446 | 0 | 0 | 1 | 2 |
| 09 | aflow-B1C1F6K1_ICSD_1194 | SUCCESS | 350.625 | 32 | 0 | 0 | 0 |
| 10 | aflow-B6H2O13Sr3_ICSD_262541 | SUCCESS | 10539.907000000007 | 35 | 0 | 0 | 0 |
| 16 | aflow-Mo3Na1O16P3_ICSD_66877 | SUCCESS | 6626.343999999983 | 30 | 0 | 0 | 0 |

- Slot 03: Bader row failures = 0; final material errors = `[{"material_id": "aflow-Cl1O12Pb5V3_ICSD_203074", "error_type": "HTTPError", "error": "HTTP Error 500: INTERNAL SERVER ERROR"}]`.
- Slot 09: Bader row failures = 0; final material errors = `[]`.
- Slot 10: Bader row failures = 0; final material errors = `[]`.
- Slot 16: Bader row failures = 0; final material errors = `[]`.

Retry reasons and all attempt timestamps are in `provenance/recovery_status.json`
and each `attempt_*/execution.json`; matching stdout/stderr is under `logs/`.
Row failures are frozen driver outcomes and remain in the formal registry.
Zero Bader row failures for a pipeline failure does not mean Bader passed.

No aggregate or manuscript numbers have been modified. This package does not
claim 65/65 complete when any material remains failed. SUCCESS refers to verified
material pipeline completion, not universal certification or absence of row failures.

No environment, cache, temporary CHGCAR, compressed intermediate, or credentials
are included. `provenance/artifact_sha256.json` lists uploaded artifact hashes.
