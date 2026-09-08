# Frozen external confirmatory finalization provenance

Finalization date: 2026-09-08

Scientific implementation remained frozen at `893f931b3045b0b628329db81999c2f439d4e830`.

The final input set is the frozen 65-system corpus. The primary confirmatory cohort is the pre-frozen 63-system subset defined by `validation/external_rate_fidelity_split.json`; the two implementation sentinels are excluded only from the primary rate-fidelity summary, not from the 65-system completeness audit.

Sources combined here:

- the previously successful GitHub Actions outputs that formed the 59-system primary package;
- local recovery branch `external-final4-local-recovery-20260908`, **as checked out by the finalization workflow at commit `5db7abfcc20676fe59954ff1bfeb2c8ba6d2beb9`**, for `aflow-B1C1F6K1_ICSD_1194`, `aflow-B6H2O13Sr3_ICSD_262541`, and `aflow-Mo3Na1O16P3_ICSD_66877`; those three result directories originated in commit `bcc6cf61b1ef7cc126a60c17ddb779f7e74cf147` and were unchanged by the later branch commit;
- GitHub Actions run `34221538118`, artifact `10055168501`, for `aflow-Cl1O12Pb5V3_ICSD_203074`.

The Cl recovery used the exact frozen CHGCAR bytes (2,437,424 bytes; SHA-256 `eb5872d5229ab8e3f7360c0add9e8619cf357bff1e11a7e494b68f2d5c36e983`). The broken AFLOW property endpoint was replaced only at the transport layer by metadata from the same AFLOW entry (`aflowlib.json`), cross-checked against `OUTCAR.static.xz` and the CHGCAR atom-count line. No codec, Bader, Protocol A.1, tolerance-ladder, certification, or early-stop semantics were changed.

Aggregation and confirmatory filtering were run with the byte-frozen `aggregate_formal_external.py` and `build_confirmatory_external.py` from commit `893f931...`.

Finalization workflow: GitHub Actions run `34229843650` (`Finalize frozen external confirmatory 63`). Its frozen gates passed with 65/65 full-corpus completion, 63/63 primary confirmatory completion, zero material-level pipeline failures, zero bound violations, and the frozen A.1 eligible counts 16 / 42 / 57 at `1e-4 / 1e-3 / 1e-2` e.
