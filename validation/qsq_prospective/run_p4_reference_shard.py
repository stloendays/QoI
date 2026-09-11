#!/usr/bin/env python3
"""Run one shard of P4 uncompressed reference analyses.

This stage intentionally does not read QSQ eligibility or codec outcomes. It
re-derives source-density Bader charges with BaderKit and Henkelman on-grid for
all unique states in the frozen chemistry-pair candidate universe.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from development_compatibility_smoke import build_grid, fetch_exact, load_metadata

SOLVERS = ("baderkit_ongrid", "henkelman_ongrid")


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-validation-dir", type=Path, required=True)
    p.add_argument("--candidates", type=Path, required=True)
    p.add_argument("--henkelman-binary", type=Path, required=True)
    p.add_argument("--shard-count", type=int, required=True)
    p.add_argument("--shard-index", type=int, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fallback: list[str]):
    fields = list(rows[0]) if rows else fallback
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def shard_for(material: str, n: int) -> int:
    return int.from_bytes(hashlib.sha256(("P4-REFERENCE|" + material).encode()).digest()[:8], "big") % n


def main() -> int:
    a = args(); root = a.repo_root.resolve(); out = a.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    if a.shard_count <= 0 or not 0 <= a.shard_index < a.shard_count:
        raise RuntimeError("invalid shard parameters")

    candidates = read_csv(a.candidates)
    mids = sorted({r["state_A_material_id"] for r in candidates} | {r["state_B_material_id"] for r in candidates})
    selected = [m for m in mids if shard_for(m, a.shard_count) == a.shard_index]
    metadata = load_metadata(root)

    # Load frozen benchmark Bader implementation.
    sys.path.insert(0, str(a.frozen_validation_dir.resolve()))
    import external_end_to_end as core  # type: ignore

    # Load already validated independent Henkelman adapter.
    mech = root / "mechanism/independent_bader_20260908"
    sys.path.insert(0, str(mech))
    import run_study as study  # type: ignore
    study.BADER = a.henkelman_binary.resolve()
    if not study.BADER.is_file():
        raise RuntimeError("Henkelman binary missing")

    rows: list[dict[str, Any]] = []; failures: list[dict[str, Any]] = []
    for m in selected:
        meta = metadata.get(m)
        if meta is None:
            for solver in SOLVERS:
                failures.append({"material_id": m, "solver": solver, "status": "FAILED", "stage": "metadata", "error": "metadata missing"})
            continue
        try:
            blob = fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="qoi_p4_ref_") as td:
                work = Path(td); grid, loader = build_grid(meta, blob, work)
                field = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
                lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)
                frac = np.asarray(grid.structure.frac_coords, dtype=np.float64)
                species = [str(s.specie.symbol) for s in grid.structure]
                if field.size != int(meta["npoints"]) or len(species) != int(meta["natoms"]):
                    raise RuntimeError("source shape/atom count mismatch")

                t0 = time.time()
                try:
                    b = core.run_bader(grid)
                    qb = np.asarray(b["charges"], dtype=float)
                    if qb.size != len(species):
                        raise RuntimeError("BaderKit charge count mismatch")
                    rows.append({
                        "material_id": m, "solver": "baderkit_ongrid", "status": "SUCCESS",
                        "charges_json": json.dumps(qb.tolist(), separators=(",", ":")),
                        "species_json": json.dumps(species, separators=(",", ":")),
                        "source_sha256": meta["sha256"], "loader": loader,
                        "npoints": field.size, "natoms": len(species), "wall_seconds": time.time() - t0,
                    })
                except Exception as exc:
                    failures.append({"material_id": m, "solver": "baderkit_ongrid", "status": "FAILED", "stage": "baderkit", "error": f"{type(exc).__name__}: {exc}"})

                t0 = time.time()
                try:
                    logdir = work / "logs" / "henkelman"; logdir.mkdir(parents=True, exist_ok=True)
                    qh, _, extra = study.solve("henkelman_ongrid", field, lattice, frac, species, work / "henkelman", logdir)
                    qh = np.asarray(qh, dtype=float)
                    if qh.size != len(species):
                        raise RuntimeError("Henkelman charge count mismatch")
                    rows.append({
                        "material_id": m, "solver": "henkelman_ongrid", "status": "SUCCESS",
                        "charges_json": json.dumps(qh.tolist(), separators=(",", ":")),
                        "species_json": json.dumps(species, separators=(",", ":")),
                        "source_sha256": meta["sha256"], "loader": loader,
                        "npoints": field.size, "natoms": len(species), "wall_seconds": time.time() - t0,
                        "vacuum_charge_e": extra.get("vacuum_charge_e", ""),
                    })
                except Exception as exc:
                    failures.append({"material_id": m, "solver": "henkelman_ongrid", "status": "FAILED", "stage": "henkelman", "error": f"{type(exc).__name__}: {exc}"})
        except Exception as exc:
            existing = {(r["material_id"], r["solver"]) for r in rows + failures}
            for solver in SOLVERS:
                if (m, solver) not in existing:
                    failures.append({"material_id": m, "solver": solver, "status": "FAILED", "stage": "source", "error": f"{type(exc).__name__}: {exc}"})

    rows.sort(key=lambda r: (r["material_id"], r["solver"])); failures.sort(key=lambda r: (r["material_id"], r["solver"]))
    write_csv(out / f"reference_rows_shard_{a.shard_index:02d}.csv", rows, ["material_id", "solver", "status"])
    write_csv(out / f"reference_failures_shard_{a.shard_index:02d}.csv", failures, ["material_id", "solver", "status", "stage", "error"])
    planned = len(selected) * len(SOLVERS)
    if len(rows) + len(failures) != planned:
        raise RuntimeError(f"reference accounting mismatch {len(rows)+len(failures)} != {planned}")
    manifest = {
        "shard_index": a.shard_index, "shard_count": a.shard_count,
        "materials": len(selected), "planned_solver_calls": planned,
        "successful_rows": len(rows), "failed_rows": len(failures),
        "candidate_file_sha256": hashlib.sha256(a.candidates.read_bytes()).hexdigest(),
        "outcome_qualification_files_read": False,
    }
    (out / f"manifest_shard_{a.shard_index:02d}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
