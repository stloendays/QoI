# QSQ prospective execution addendum

Status: **BLOCKED_PENDING_COMPATIBILITY_SMOKE**

Date frozen for this recovery step: 2026-09-11.

This addendum closes the provenance gap identified before executing the prepared P1/P2 work orders. It does not modify any frozen benchmark row, QSQ label, scientific threshold, or prior result.

## 1. Scientific implementation anchor

The repository's own external-confirmatory finalization workflow explicitly identifies commit

`893f931b3045b0b628329db81999c2f439d4e830`

as the **frozen scientific implementation**. The prospective development recovery therefore reuses scientific-critical code and package pins from that commit rather than reconstructing codec/Bader semantics from prose.

Pinned frozen files:

| File at frozen commit | Blob SHA |
|---|---|
| `validation/external_end_to_end.py` | `3da20fcc2bf52cf3fb135802cfe81bac8eed4a98` |
| `validation/formal_external_e2e.py` | `5ecdc03238a885e94f32b55d50c24e65e13aa07a` |
| `validation/requirements-external-e2e.txt` | `ef5f23717f3684e0ee343ec3c12a1eefb3864b76` |
| `validation/EXTERNAL_ENVIRONMENT.md` | `3f00afaafa03c05348645aad13435d301cdd8b54` |

The external environment record states that the same released BaderKit and codec versions/configurations were used as in the development benchmark. It also explicitly does **not** claim byte-identical reconstruction of every unrecorded transitive dependency from the earlier development workstation/HPC runs. We preserve that limitation.

## 2. Scientific-critical environment

The compatibility smoke and subsequent recovered runner use the frozen external pins:

- Python 3.12.14
- NumPy 2.4.6
- BaderKit 0.10.2
- Numba 0.65.1
- llvmlite 0.47.0
- pymatgen 2025.10.7
- SZ3 / `pysz` 1.0.3
- ZFP / `zfpy` 1.0.1
- `hdf5plugin` 7.0.0
- h5py 3.16.0
- SciPy 1.18.1
- pandas 2.3.3

Every prospective shard must archive Python version, sorted `pip freeze`, requirement-file SHA-256, current repository commit, frozen scientific commit, and work-order SHA-256.

## 3. Recovered codec semantics

The prospective recovery must use the frozen implementation without local reinterpretation:

- **ZFP:** `zfpy.compress_numpy(..., tolerance=abs_bound)`; fixed-accuracy mode.
- **SZ3:** `pysz`, ABS error-bound mode, `absErrorBound=abs_bound`, default `INTERP_LORENZO` configuration.
- **SPERR:** HDF5 plugin with `Sperr(absolute=abs_bound)` and one dataset chunk equal to the full array shape; compressed size from HDF5 dataset storage size.

`abs_bound = nominal_tolerance_relative * ptp(reference_density)`.

## 4. Recovered Bader semantics

The frozen implementation pins:

- method: `ongrid`
- `vacuum_tol = 1e-3`
- `persistence_tol = 0.5`
- `nna_cutoff = False`
- charge, total-charge and reference grids all point to the same density grid for this benchmark
- Bader basins are re-derived for the scientific metric
- fixed-basin integration is retained only as a diagnostic/self-check.

The fixed-basin self-check on the uncompressed reference must reproduce BaderKit atom charges to `<= 1e-7 e` before a material is admitted to prospective execution.

## 5. Development-source recovery

The development release contains exact source URL, source byte count, SHA-256, grid shape, point count and atom count in `materials_metadata.csv`.

Two source paths must be supported independently:

1. **Materials Project bulk:** the exact gzip-compressed serialized charge-density object is downloaded and verified byte-for-byte, Monty-deserialized to the stored pymatgen `Chgcar`, and converted in memory to a BaderKit `Grid`. It is not round-tripped through a newly printed CHGCAR, avoiding precision loss from text serialization.
2. **NOMAD slab/adsorbate:** exact downloaded bytes are hash/size verified, decompressed according to the recorded suffix when needed, then parsed as the original CHGCAR by BaderKit.

For every material the runner must enforce:

- exact source SHA-256 and source byte count;
- parsed grid shape equals `ngrid`;
- flattened point count equals `npoints`;
- structure/Bader atom count equals `natoms`;
- all field values finite and peak-to-peak range positive;
- fixed-basin original self-check <= `1e-7 e`.

## 6. Compatibility sentinels before P1/P2

The recovery is not allowed to execute the 1,332 P1 rows or the 14,986 P2 perturbations until two previously frozen development cases reproduce under the recovered path:

- `mp-1009084` (Materials Project bulk, BeSnAs2), relative tolerance `1e-7`, all three codecs;
- `nomad--O7C25L6mxPu` (NOMAD slab, Cr20), relative tolerance `1e-7`, all three codecs.

These cases were chosen because frozen tight-ladder rows already exist for all codecs and exercise both development loaders. They are engineering/provenance sentinels, not new scientific endpoints.

Compatibility gates are intentionally much tighter than any paper-level Bader contract:

- reference `value_ptp`: `rtol=1e-12`, `atol=1e-12`;
- realized L-infinity: `rtol=2e-6`, `atol=2e-12`;
- re-derived Bader maximum charge error: `rtol=2e-5`, `atol=2e-9`;
- codec error bound must still be respected.

Exact compressed-byte equality is recorded as a determinism diagnostic but is not itself a scientific compatibility requirement. If any scientific gate fails, execution remains blocked and the mismatch must be diagnosed rather than widening thresholds after looking at desired P1/P2 outcomes.

## 7. Execution-state rule

Until the compatibility smoke passes, all prepared work orders remain `PREPARED_NOT_EXECUTED`.

A passing smoke changes the execution state only to **READY_FOR_P1**. It does not validate QSQ, does not create new scientific evidence, and does not authorize reinterpretation of the retrospective 95%+ result. P1 must be executed and audited before the completed common tight ladder replaces the current common-base sensitivity analysis.
