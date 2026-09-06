#!/usr/bin/env python3
"""Parser/provenance-only AFLOW smoke test.

This intentionally performs **no codec round trip and no Bader analysis**.  It is
used to exercise AFLOW pre-VASP5 species injection and grid parsing without
creating a rate-fidelity observation on an otherwise confirmatory material.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

import external_end_to_end as core


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--material-id", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    records = {r["material_id"]: r for r in core.load_manifest()}
    if args.material_id not in records:
        raise SystemExit(f"Material absent from frozen manifest: {args.material_id}")
    record = records[args.material_id]
    if not record["source"].startswith("AFLOW"):
        raise SystemExit("Parser-only AFLOW smoke requires an AFLOW record")

    from baderkit import Grid

    with tempfile.TemporaryDirectory(prefix="qoi_aflow_parser_") as td:
        chgcar, provenance = core.materialize_chgcar(record, Path(td))
        grid = Grid.from_dynamic(chgcar)
        core.audit_grid(record, grid)
        field = np.asarray(grid.total, dtype=np.float64)
        if not np.all(np.isfinite(field)):
            raise RuntimeError("parsed AFLOW field contains non-finite values")

        species = [str(site.specie) for site in grid.structure]
        result = {
            "status": "PASS",
            "material_id": record["material_id"],
            "domain": record["domain"],
            "parser_provenance": provenance["parser_provenance"],
            "source_sha256_verified": provenance["source_sha256_verified"],
            "source_bytes_verified": provenance["source_bytes_verified"],
            "grid_shape": [int(x) for x in field.shape],
            "npoints": int(field.size),
            "natoms_structure": len(grid.structure),
            "species_counts": dict(Counter(species)),
            "rate_fidelity_computed": False,
            "bader_computed": False,
            "codec_computed": False,
        }
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
