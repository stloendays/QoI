# External E2E environment freeze

The corpus-scale external rate–fidelity validation uses a separately frozen and
auditable execution environment.

## Frozen scientific-critical pins

`validation/requirements-external-e2e.txt` pins the versions exercised by the
successful external smoke immediately before corpus-scale execution, including:

- Python 3.12.14
- NumPy 2.4.6
- BaderKit 0.10.2
- Numba 0.65.1 / llvmlite 0.47.0
- pymatgen 2025.10.7
- SZ3 (`pysz`) 1.0.3
- ZFP (`zfpy`) 1.0.1
- `hdf5plugin` 7.0.0
- h5py 3.16.0
- SciPy 1.18.1
- pandas 2.3.3

Each formal shard additionally archives:

- `python_version.txt`
- a sorted complete `pip_freeze.txt`
- `requirements_sha256.txt`
- the exact Git commit in `git_commit.txt`
- the scientific/protocol hashes already written to `run_metadata.json`

This means a formal external result is tied to both immutable scientific inputs
and a reconstructable software environment.

## Claim boundary

The original development release recorded the key scientific package versions
for BaderKit and the three codecs, but it did not preserve a complete historical
`pip freeze` for every transitive numerical dependency. Therefore:

- **supported:** the external validation environment is frozen, versioned and
  auditable;
- **supported:** the external run uses the same released BaderKit and codec
  versions/configurations as the development benchmark;
- **not supported:** the claim that the new external environment is byte-for-byte
  identical to every unrecorded transitive dependency of the historical
  development environment.

The external benchmark is designed to test scientific transfer under a fully
recorded environment, not to reconstruct undocumented package state by guesswork.
