# Error-geometry residual permutation v0.1 — provenance addendum

Date frozen: 2026-09-07

This addendum is frozen **before any residual-permutation scientific outcome is inspected**. It changes only the provenance gate needed to execute the already-preregistered intervention. It does not change the selected materials, codecs, relative tolerance, codec parameters, residual-permutation construction, density strata, random seeds, Bader observable, estimands, bootstrap, or interpretation thresholds defined in `ERROR_GEOMETRY_PERMUTATION_V0_1_PREREGISTRATION.md`.

## Why an addendum is required

The original preregistration required a new run to reproduce the released 2026-09-01 resolved-Bader value before applying a permutation. The implementation smoke exposed that this historical Bader value is not exactly reproducible in the current pinned execution environment even though the upstream density and codec result are reproducible.

For `mp-1038991`, ZFP, relative tolerance `1e-3`:

- the released master benchmark and the released mechanism table independently contain the same resolved-Bader error: `0.0167712761353193 e`;
- current pinned environment: Python 3.12, `baderkit==0.10.2`, `zfpy==1.0.1`, `numpy==2.4.6`, `pymatgen==2025.10.7`;
- source object SHA256 and byte count verify exactly;
- source grid, requested absolute bound, realized L-infinity (`0.47202006624999626`), RMSE (`0.04756482476818417`) and compression ratio (`41.78901168632013`) reproduce the released values;
- current resolved-Bader error is `0.017729526700000164 e`;
- three repeated Bader calculations on the identical reconstructed field are bitwise stable at the reported charge precision (`max pairwise charge difference = 0.0 e`).

The discrepancy is localized to charge transfer between symmetry-related atom pairs in the reconstructed-field Bader partition; the original-field Bader charges reproduce the released original charges to approximately `1e-11 e` per atom. Thus the source field and codec reconstruction are not the source of the discrepancy.

The 2026-09-01 release records that the development campaign was executed on Windows in a private `D:\Research\CatalystForge` Python environment, but the release did not preserve a package lock or BaderKit version for that historical environment. Therefore the historical reconstructed-field partition cannot be treated as an exactly reproducible numerical oracle on the current Linux runner.

## Frozen correction to the provenance gate

The new-run baseline for the permutation intervention is the **unshuffled Bader result computed in the same pinned process/environment as its shuffled counterfactuals**.

Before a material/codec enters the intervention, the run must still pass all upstream provenance checks that are independent of the under-specified historical Bader environment:

1. exact source URL/object, SHA256 and source byte count from `materials_metadata.csv`;
2. source grid shape / point count and finite-field checks;
3. the preregistered relative tolerance `1e-3` and the unchanged codec implementation/configuration;
4. realized L-infinity reproduced against the released mechanism operating point within numerical roundoff;
5. compression ratio reproduced against the released mechanism operating point within numerical roundoff;
6. residual-multiset audits proving that every shuffle preserves L-infinity, RMSE, mean signed error, mean absolute error and, by construction, the entire residual-value multiset;
7. Bader solver success/failure reported explicitly for every shuffled row.

The released resolved-Bader value is retained as a **legacy reconciliation field**, not silently overwritten and not used as a pass/fail gate. For every material/codec the new analysis must report current-unshuffled minus released resolved-Bader error so that the platform/environment sensitivity is visible.

## Scientific rationale

The primary intervention is paired within one pinned environment:

`same original field + same codec residual values + same Bader implementation`, with only the fine spatial assignment of those residual values changed.

Therefore the causal contrast tested by the permutation does not require the current Bader partition to numerically equal the historical Windows partition. Requiring the unrecoverable historical value would instead confound the mechanism test with an unpinned legacy execution environment.

## Interpretation guard

This addendum does **not** rehabilitate the negative dual L-infinity + RMSE matching result and does not authorize any spatial-geometry claim by itself. The preregistered spatial-permutation outcome must still satisfy its own intervention audits and interpretation rules. Any platform sensitivity in the unshuffled Bader baseline will be reported separately as a reproducibility/provenance finding.
