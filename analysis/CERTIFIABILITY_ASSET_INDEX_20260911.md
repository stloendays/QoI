# Certifiability audit asset index — 2026-09-11

This file is the canonical index for the 2026-09-11 benchmark-validity audit.

## Headline result

At strict Bader contracts, naive binary pass/fail benchmarking is dominated by material–threshold pairs that fail the independent Protocol A.1 numerical-eligibility test.

| threshold | naive failures | reclassified non-evaluable | genuine eligible failures | reclassified fraction |
|---:|---:|---:|---:|---:|
| 1e-4 e | 533 | 518 | 15 | 97.2% |
| 1e-3 e | 310 | 296 | 14 | 95.5% |
| 1e-2 e | 108 | 61 | 47 | 56.5% |

Eligibility is not permissive filtering: at 1e-4 e, 106 of 229 naive passes (46.3%) are also non-evaluable.

## Canonical assets

- `analysis/CERTIFIABILITY_AUDIT_20260911.md` — full derivation, interpretation, and claim boundary.
- `analysis/certifiability_reclassification_pooled_20260911.csv` — pooled machine-readable summary across 254 materials × 3 codecs.
- `analysis/certifiability_reclassification_by_codec_20260911.csv` — codec-resolved reclassification table.
- `paper/CLAIM_EVIDENCE_ADDENDUM_20260911_CERTIFIABILITY.md` — manuscript-grade claim/evidence registration.
- `paper/MANUSCRIPT_CERTIFIABILITY_PATCH_20260911.md` — text patch for the current manuscript narrative.
- `supplement/S2_floor_relative.csv` — frozen floor-normalized evidence used for the analysis-limited-regime statement.

## Canonical interpretation

The benchmark state space is three-state:

1. `eligible + certified`
2. `eligible + not certified`
3. `NON_EVALUABLE_BADER_UNSTABLE`

A non-evaluable pair is neither a pass nor a failure and must not be attributed to the codec.

The 97.2% and 95.5% reclassification fractions are approved as headline evidence for benchmark validity. The plateau/floor result is deliberately weaker: at 1e-4 e, certified Bader errors are floor-scale (median dQ/floor 1.09–1.33 across codecs), consistent with an emerging analysis-limited regime, but current frozen analysis does not establish a universal material-level plateau = floor law.

## Downstream use

Future manuscript, Word, presentation, and Figure 3 revisions should use this asset set and wording as the canonical 2026-09-11 certifiability result. Older binary-failure framing should be treated as superseded where it conflicts with Protocol A.1 eligibility semantics.