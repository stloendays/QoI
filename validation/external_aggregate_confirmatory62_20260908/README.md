# External rate-fidelity aggregate, confirmatory cohort 62 / 63 (2026-09-08)

Frozen aggregation (`validation/aggregate_formal_external.py` at scientific
commit 893f931b3045b0b628329db81999c2f439d4e830) over:

- 59 primary-cohort materials completed in GitHub Actions runs 34074537547
  (full) and 34113606495 (recovery), artifact SHA-256 verified;
- 3 materials completed by the local recovery on branch
  `external-final4-local-recovery-20260908` (`aflow-B1C1F6K1_ICSD_1194`,
  `aflow-B6H2O13Sr3_ICSD_262541`, `aflow-Mo3Na1O16P3_ICSD_66877`).

Missing: `aflow-Cl1O12Pb5V3_ICSD_203074`, AFLOW upstream HTTP 500 on every
attempt (3 Actions + 3 local). It is A.1-eligible only at tau = 1e-2 e, so its
absence changes the 1e-2 denominator (56 instead of 57) and nothing else.
The two implementation sentinels are not included. This is therefore 62 of the
pre-specified 63-system confirmatory cohort, not the all-65 descriptive table;
`build_confirmatory_external.py` refuses this input by design (62 != 63) and
was not bypassed.

Integrity: 1669 rows, 0 material failures, 2 row failures
(`nomad2d-1_3Aeqri4-hc`, ZFP 0.03 / 0.1, Bader solver IndexError), 0 bound
violations. A.1 eligible counts 16 / 42 / 56 against the frozen expectation
16 / 42 / 57.

## Headline (median CCR [95 % CI], materials as units)

| tau (e) | ZFP | SZ3 | SPERR | pre-specified expectation | outcome |
|---|---|---|---|---|---|
| 1e-4 | 13.0 [7.1, 20.4] | 12.1 [7.3, 17.7] | 5.2 [4.2, 6.2] | ZFP > SZ3 > SPERR | reproduced (ZFP-SZ3 gap narrow, CIs overlap; ZFP certifies 16/16, SZ3 and SPERR 14/16) |
| 1e-3 | 18.76 [14.3, 25.0] | 18.76 [12.1, 24.6] | 6.4 [5.9, 6.9] | ZFP ~ SZ3 > SPERR | reproduced |
| 1e-2 | 40.7 [35.4, 46.6] | 68.2 [43.6, 103.8] | 10.8 [10.2, 12.5] | SZ3 > ZFP > SPERR | reproduced (SZ3 wins 89 % [80, 96]) |

Mechanism expectations: ZFP median realized/nominal L-inf 0.153 (development
0.158), SZ3 and SPERR ~1.0; fixed-basin error understates resolved-basin error
by a median 124x / 20x / 219x (ZFP / SZ3 / SPERR; development 180x / 16x /
194x); |mean signed error| / RMSE 0.005 / 0.035 / 0.001 (development
0.003 / 0.037 / 0.001).

Differences to report, none contradicting an expectation: the external corpus
is more stable (median A.1 floor 3.4e-4 e vs 7.5e-4 e), so CCRs are higher
across the board; the NOMAD vacuum-2D stratum is isolated layers, not adsorbate
slabs, and reaches SZ3 115x / ZFP 49x at 1e-2.

Files: `external_codec_summary.csv`, `external_summary_a1.csv`,
`pairwise_external.csv`, `best_certified_external.csv`,
`formal_external_e2e_rows.csv`, `material_audit.csv`, `summary.json`.
