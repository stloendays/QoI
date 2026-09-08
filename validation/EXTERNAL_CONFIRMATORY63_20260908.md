# External confirmatory validation — final 63/63 PASS

Date: 2026-09-08

## Frozen status

The frozen primary confirmatory cohort is now complete: **63/63 systems**, with **1,689 retained scientific rows**, **0 material-level pipeline failures**, **0 bound violations**, and **3 preserved row-level Bader solver failures** affecting two materials. The confirmatory builder returned `status = PASS` and exactly reproduced the pre-frozen Protocol A.1 eligibility counts: **16 / 42 / 57** at `1e-4 / 1e-3 / 1e-2` e.

Scientific implementation remained frozen at:

`893f931b3045b0b628329db81999c2f439d4e830`

The final frozen 65-system descriptive aggregate is also complete: **65/65 systems**, **1,755 rows**, **0 material-level failures**, **0 bound violations**.

Machine-readable outputs are in:

`validation/final_external_confirmatory63_20260908/`

The finalization workflow is GitHub Actions run `34229843650`; the committed result snapshot is rooted in commit `da8327d219216382fa16d11dd7ba9b0f754522a1` and subsequent provenance/documentation commits.

## Final primary rate–fidelity result

Median certified compression ratio (CCR), primary confirmatory 63:

| τ (e) | ZFP median CCR [95% CI] | SZ3 median CCR [95% CI] | SPERR median CCR [95% CI] | Frozen directional expectation | Result |
|---|---:|---:|---:|---|---|
| 1e-4 | 13.03 [7.09, 20.43] | 12.06 [7.28, 17.72] | 5.17 [4.23, 6.23] | ZFP > SZ3 > SPERR | reproduced |
| 1e-3 | 18.76 [14.27, 25.04] | 18.76 [12.14, 24.56] | 6.40 [5.88, 6.88] | ZFP ≈ SZ3 > SPERR | reproduced |
| 1e-2 | 40.57 [35.40, 46.03] | 65.89 [40.67, 101.85] | 10.82 [10.18, 12.44] | SZ3 > ZFP > SPERR | reproduced |

All three pre-specified directional expectations therefore reproduce on the fully completed frozen external cohort.

## Final paired comparisons

At `1e-2` e, SZ3 beats ZFP on **89.47%** of admitted materials (bootstrap interval **80.70–96.49%**). At `1e-4` e, ZFP beats SZ3 on **68.75%** of admitted materials; equivalently SZ3 wins 31.25% (SZ3-win interval 12.5–56.25%). SPERR loses to ZFP and SZ3 in the large majority of admitted systems at every threshold.

The external `1e-4` ZFP–SZ3 effect is therefore directionally consistent but materially narrower than in the development corpus; manuscript language should avoid claiming a strong separation at the tightest threshold.

## Final Cl recovery

The previously missing `aflow-Cl1O12Pb5V3_ICSD_203074` is now **COMPLETE**.

- exact frozen CHGCAR: 2,437,424 bytes;
- SHA-256: `eb5872d5229ab8e3f7360c0add9e8619cf357bff1e11a7e494b68f2d5c36e983`;
- Protocol A.1 floor: `0.0035547402881945 e`;
- 21 attempted rows, 20 retained rows, 1 row-level failure;
- no material-level failure;
- all codec bounds respected;
- one preserved Bader solver failure: ZFP at relative tolerance `0.1` (`IndexError` during resolved Bader);
- median realized-L∞ / nominal: ZFP `0.1569`, SZ3 `0.999998`, SPERR `0.999987`.

The failed AFLOW `/?species` transport endpoint was not used to alter scientific content. Species/composition metadata came from the same AFLOW entry's `aflowlib.json` and was independently cross-checked against `OUTCAR.static.xz` and the CHGCAR atom-count line. Codec, Bader, Protocol A.1, tolerance ladder, early-stop and certification semantics were unchanged.

## Failure semantics

The final 63-system primary set contains **3 row-level Bader solver failures** in two materials: the pre-existing two ZFP rows in `nomad2d-1_3Aeqri4-hc`, plus the single ZFP `0.1` row in the recovered Cl system. These rows remain explicit failures and are never counted as passes; successful rows from the same materials remain retained. There are **zero material-level pipeline failures**.

## Manuscript-safe conclusion

> All 63 pre-frozen confirmatory systems completed, and all three pre-specified rate–fidelity directional expectations reproduced. The external data also reproduce the major mechanistic diagnostics identified in development, while showing a narrower ZFP–SZ3 separation at the tightest scientific tolerance.

This supersedes the interim `EXTERNAL_CONFIRMATORY62_20260908.md` record, which is retained only as provenance of the recovery sequence.
