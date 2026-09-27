# Full-population Hartree-QSQ generality study

Status: **prospective research extension; separate from the frozen P1-P4 submission scope**.

Parent evidence:
- the 12-material ZFP Hartree pilot showed near-linear, predominantly monotone Hartree response versus realized pointwise distortion;
- the 12-material Hartree-QSQ pilot passed its pre-specified GO gate on 2026-09-27.

This study expands that result without adding DFT.

## Population and operators

Population: the 254 development materials used by the prospective QSQ validation, including both bulk and slab systems.

Codecs: ZFP, SZ3, SPERR.

Downstream operator:
`V(G) = 4 pi rho(G) / |G|^2`, `G != 0`, with `V(G=0)=0`.

Primary Hartree error:
`RMS(V_recon - V_ref) / RMS(V_ref)`.

Reference qualification:
- same five historical QSQ seed labels `{20260905, 1, 2, 3, 4}`;
- same material-specific perturbation amplitude encoded in the frozen QSQ tables;
- material response scale = maximum Hartree relative-RMSE response over the five seeds.

No Bader result is recomputed. Frozen Bader error is carried only as a matched-operator contrast.

## Contract ladder

The Hartree numerical-contract ladder is frozen before full-population execution:

`1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3` relative RMSE.

Primary full-population contract: **1e-6 relative RMSE**.

These are numerical contracts for the generality test, not claimed universal chemical thresholds.

## Reconstruction compatibility gate

For every reused frozen benchmark row:
- exact source bytes and metadata are verified;
- the development-source loader must reproduce the frozen field identity checks;
- the same frozen codec implementation is used;
- regenerated realized L-infinity must match the frozen row within the established development compatibility tolerance.

Compressed-byte equality is diagnostic, not the scientific gate.

Rows failing compatibility are retained and excluded from scientific summaries; failures remain explicit in the accounting.

## Pre-specified full-population GO criteria

The extension may support a full-population operator-generality claim only if all are true:

1. all 254 planned materials are accounted for and no source-level material is silently dropped;
2. at least 90% of materials are Hartree-QSQ eligible at the primary `1e-6` contract;
3. for each codec separately, at least 80% of material series with >=4 reproduced rows are monotone non-decreasing in Hartree error versus realized L-infinity;
4. for each codec separately, the median within-material log-log R-squared is at least 0.90;
5. for each codec separately, the median within-material log-log slope lies in [0.70, 1.30];
6. at least one numerical contract is non-trivial (not all eligible rows certified and not zero certified rows).

A scientific NO-GO is acceptable and must be reported as such.

## Matched-realized-distortion control

Within material, codec pairs are matched without replacement on log10(realized L-infinity) using a 0.10-dex primary caliper, matching the established benchmark control.

For the same matched pairs, report:
- Hartree relative-RMSE ratio;
- frozen re-derived Bader-error ratio, when finite.

This comparison is descriptive and is not part of the GO gate.

## Output policy

The user has authorized public storage for this research extension.

Action outputs, aggregate CSV/JSON reports, provenance hashes and the final report may therefore be committed to this public research branch.

The current frozen manuscript, SI authority and P1-P4 claims are not modified automatically.
