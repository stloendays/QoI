"""Materials Project parsed-CHGCAR loader, identical to the frozen benchmark.

This is the density loader used to build the development corpus of the frozen
benchmark (`benchmark/master_benchmark_full.csv`).  It is a verbatim extraction of
`parse_chgcar_json` from the original RhoCodec fetcher
(`D:/Research/RhoCodec/scripts/fetch_mp_corpus.py`, 2026-09-01), with the
Maggma envelope handling made explicit and with sanity checks added.  Nothing about
the returned arrays differs from the cached `.npz` grids the benchmark consumed:
verified bit-for-bit on the 12 pilot materials (see
`analysis/hartree_potential_pilot/provenance.json`).

Source object layout (`materialsproject-parsed.s3.amazonaws.com/chgcars/<task>.json.gz`),
observed on the real files rather than assumed:

    {
      "fs_id": "...", "maggma_store_type": "S3Store", "compression": "zlib",
      "task_id": "mp-XXXXXXX",
      "data": {                       # pymatgen Chgcar.as_dict(), already decoded JSON
        "@module": "pymatgen.io.vasp.outputs", "@class": "Chgcar",
        "poscar": {"@class": "Poscar", "structure": {"@class": "Structure",
                    "lattice": {"matrix": [[...],[...],[...]]},
                    "sites": [{"species": [{"element": "Hf", "occu": 1}], "abc": [...], ...}]}},
        "data": {"total": {"@module": "numpy", "@class": "array", "dtype": "float64",
                           "data": <nested list, shape (nx, ny, nz)>},
                 "diff": ... or null},
        "data_aug": {...}
      }
    }

`compression: "zlib"` describes how Maggma stored the object in S3; after the
outer gzip is removed the payload is plain JSON and `data` is a dict, not a
compressed string.  The density grid is `data.data.total.data`, a Monty-encoded
numpy array (dict with `@class: array`), which is why a search for a bare 3-D list
under `data.total` fails.

Returned grid: the VASP CHGCAR "total" block, float64, shape (nx, ny, nz) in
VASP/pymatgen axis order, values in CHGCAR units (rho * V_cell, electrons); the
per-cell mean equals the valence electron count.  Lattice is the 3x3 row matrix
in Angstrom; frac_coords (natoms, 3); symbols list of element strings.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import numpy as np


def parse_chgcar_json(blob: bytes) -> dict:
    """Decode one `chgcars/*.json.gz` object into structure plus grid.

    Verbatim logic of the frozen-benchmark fetcher.
    """
    text = gzip.decompress(blob).decode("utf-8")
    doc = json.loads(text)
    # Maggma S3Store envelope: the Chgcar dict sits under "data".
    data = doc["data"] if "data" in doc and "poscar" not in doc else doc
    poscar = data["poscar"]
    structure = poscar["structure"] if "structure" in poscar else poscar
    lattice = np.array(structure["lattice"]["matrix"], dtype=np.float64)
    sites = structure["sites"]
    frac = np.array([s["abc"] for s in sites], dtype=np.float64)
    symbols = [s["species"][0]["element"] for s in sites]
    grid = np.array(data["data"]["total"]["data"], dtype=np.float64)
    return {
        "lattice": lattice,
        "frac_coords": frac,
        "symbols": symbols,
        "grid": grid,
        "envelope": {k: doc.get(k) for k in ("fs_id", "maggma_store_type", "compression", "task_id")},
    }


def load_mp_density(path: str | Path, *, expected_sha256: str | None = None,
                    expected_ngrid=None, expected_npoints: int | None = None,
                    expected_natoms: int | None = None) -> dict:
    """Load a local `.json.gz` with the benchmark's parser and run sanity checks."""
    blob = Path(path).read_bytes()
    sha = hashlib.sha256(blob).hexdigest()
    if expected_sha256 is not None and sha != expected_sha256:
        raise ValueError(f"SHA-256 mismatch for {path}: {sha} != {expected_sha256}")
    rec = parse_chgcar_json(blob)
    g = rec["grid"]
    if g.ndim != 3:
        raise ValueError(f"density is not 3-D: shape {g.shape}")
    if expected_ngrid is not None and tuple(int(x) for x in expected_ngrid) != g.shape:
        raise ValueError(f"ngrid mismatch: metadata {tuple(expected_ngrid)} vs file {g.shape}")
    if expected_npoints is not None and int(expected_npoints) != g.size:
        raise ValueError(f"npoints mismatch: metadata {expected_npoints} vs file {g.size}")
    if expected_natoms is not None and int(expected_natoms) != len(rec["symbols"]):
        raise ValueError(f"natoms mismatch: metadata {expected_natoms} vs file {len(rec['symbols'])}")
    if not np.all(np.isfinite(g)):
        raise ValueError("density contains non-finite values")
    if abs(np.linalg.det(rec["lattice"])) <= 0:
        raise ValueError("degenerate lattice")
    rec["sha256"] = sha
    rec["source_bytes"] = len(blob)
    return rec


def parse_ngrid(s: str) -> tuple[int, int, int]:
    """`materials_metadata.csv` stores ngrid as 'AxBxC'."""
    return tuple(int(x) for x in str(s).lower().split("x"))  # type: ignore[return-value]


if __name__ == "__main__":  # minimal CLI: python analysis/mp_chgcar_loader.py file.json.gz
    import sys
    r = load_mp_density(sys.argv[1])
    print({"shape": r["grid"].shape, "natoms": len(r["symbols"]), "sha256": r["sha256"],
           "envelope": r["envelope"], "mean_electrons": float(r["grid"].mean())})
