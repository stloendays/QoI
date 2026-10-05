# QOAC-H v0.1 postmortem and v0.2 engineering target

Date: 2026-10-05

This note is written after the preregistered v0.1 pilot completed. It does not alter the v0.1 gates or results.

## Frozen v0.1 outcome

- 12/12 planned materials completed.
- 600/600 settings completed with zero failures.
- Mechanism GO: passed strongly.
  - beta=2 better than beta=0 on 12/12 materials at matched storage.
  - median material-level Hartree-error ratio beta=2/beta=0 = 0.0767117.
- Competitive GO: not passed.
  - median certified CR ratio QOAC-H / best ZFP-SZ3-SPERR baseline = 1.00394.
  - bootstrap 95% CI = [0.92102, 1.58564].

The scientifically supported conclusion is therefore:
operator-derived reciprocal-space error allocation works strongly, while the v0.1 storage representation is not yet uniformly competitive with mature codecs.

## Baseline-family split

The competitive result is highly structured rather than random.

For the three materials whose best certified baseline is SPERR:
- QOAC-H / baseline CR ratios = 0.8212, 0.7708, 0.8498;
- median = 0.8212;
- QOAC-H wins = 0/3.

For the nine materials whose best certified baseline is ZFP:
- QOAC-H wins = 7/9;
- median QOAC-H / baseline CR ratio = 1.5746.

Thus the principal engineering deficit is concentrated in the SPERR-leading cases.

## Rate-floor diagnosis

v0.1 preserves G=0 and every even-grid Nyquist plane exactly. At very large alpha the active-mode payload approaches zero, so the observed maximum CR reveals the representation floor.

For the three SPERR-leading materials:

| material | special-mode fraction | encoded floor 1/max(CR) | max QOAC-H CR | best baseline CR | ceiling / baseline |
| --- | ---: | ---: | ---: | ---: | ---: |
| mp-1188002 | 0.05387 | 0.05422 | 18.44 | 22.54 | 0.818 |
| mp-1103974 | 0.03912 | 0.03945 | 25.35 | 27.90 | 0.909 |
| mp-22490 | 0.02812 | 0.02816 | 35.51 | 38.71 | 0.917 |

The encoded floor is nearly identical to the fraction of special reciprocal modes that are stored exactly. This is direct evidence that exact Nyquist-plane preservation, not the beta=2 allocation law, is the dominant rate ceiling in the three competitive failures.

## v0.2 target

Do not retune beta=2 on the same pilot.

The next engineering problem is to remove the Nyquist-plane rate floor without exploiting the historical Hartree operator's alias ambiguity.

The preferred v0.2 architecture is full-spectrum Hermitian-orbit quantization:

1. use a full orthonormal FFT;
2. group each k with its Hermitian partner -k mod N;
3. store one canonical coefficient per orbit and reconstruct its partner exactly by conjugation;
4. for any coordinate on an even-grid Nyquist index, enumerate the alias-equivalent +/- Nyquist sign choices;
5. define a conservative alias-safe reciprocal magnitude as the minimum |G|^2 across those sign choices;
6. use the unchanged operator-derived law Delta_k proportional to this conservative |G|^2;
7. keep only G=0 exact; self-conjugate modes are stored as real values;
8. certify every decoded real-space field with the actual historical Hartree metric and report the Nyquist-safe metric in parallel.

This converts the previous exact special-plane exception into an explicitly Hermitian, conservative, operator-aware quantization rule.

The 12-material v0.1 cohort may be reused only as an engineering/tuning set for v0.2. Any confirmatory competitive claim must be tested on a disjoint frozen cohort or the full development population after v0.2 is frozen.
