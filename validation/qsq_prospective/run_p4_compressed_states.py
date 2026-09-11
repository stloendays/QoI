#!/usr/bin/env python3
"""Run one shard of frozen P4 compressed-state analyses.

Input states come only from the reference-valid P4 pair cohort. Every state is
reconstructed at the four P1 common-tight settings for ZFP, SZ3 and SPERR, then
analyzed with both BaderKit on-grid and Henkelman on-grid. Both solvers are run
for audit completeness; policy cost accounting later counts only calls that a
policy would actually invoke.
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

CODECS = ("zfp", "sz3", "sperr")
CODEC_LABEL = {"zfp": "ZFP", "sz3": "SZ3", "sperr": "SPERR"}
REL_TOLS = (1e-7, 3e-7, 1e-6, 3e-6)
SOLVERS = ("baderkit_ongrid", "henkelman_ongrid")


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-validation-dir", type=Path, required=True)
    p.add_argument("--reference-valid-pairs", type=Path, required=True)
    p.add_argument("--henkelman-binary", type=Path, required=True)
    p.add_argument("--shard-count", type=int, required=True)
    p.add_argument("--shard-index", type=int, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def read_csv(p: Path):
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fallback: list[str]):
    fields = list(rows[0]) if rows else fallback
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def shard_for(material: str, n: int) -> int:
    return int.from_bytes(hashlib.sha256(("P4-COMPRESSED|" + material).encode()).digest()[:8], "big") % n


def add_fail(failures, material, codec, rel_tol, solver, stage, error):
    failures.append({"material_id": material, "codec": codec, "relative_tolerance": rel_tol, "solver": solver, "status": "FAILED", "stage": stage, "error": error})


def main() -> int:
    a = args(); root = a.repo_root.resolve(); out = a.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    pairs = read_csv(a.reference_valid_pairs)
    mids = sorted({r["state_A_material_id"] for r in pairs} | {r["state_B_material_id"] for r in pairs})
    selected = [m for m in mids if shard_for(m, a.shard_count) == a.shard_index]
    metadata = load_metadata(root)

    sys.path.insert(0, str(a.frozen_validation_dir.resolve()))
    import external_end_to_end as core  # type: ignore
    mech = root / "mechanism/independent_bader_20260908"; sys.path.insert(0, str(mech))
    import run_study as study  # type: ignore
    study.BADER = a.henkelman_binary.resolve()
    if not study.BADER.is_file(): raise RuntimeError("Henkelman binary missing")

    rows: list[dict[str, Any]] = []; failures: list[dict[str, Any]] = []
    for m in selected:
        meta = metadata.get(m)
        if meta is None:
            for codec in CODECS:
                for rel in REL_TOLS:
                    for solver in SOLVERS: add_fail(failures, m, CODEC_LABEL[codec], rel, solver, "metadata", "metadata missing")
            continue
        try:
            blob = fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="qoi_p4_cmp_") as td:
                work = Path(td); grid, loader = build_grid(meta, blob, work)
                field = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64)); ptp = float(np.ptp(field))
                lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)
                frac = np.asarray(grid.structure.frac_coords, dtype=np.float64)
                species = [str(s.specie.symbol) for s in grid.structure]
                if field.size != int(meta["npoints"]) or len(species) != int(meta["natoms"]):
                    raise RuntimeError("source shape/atom count mismatch")
                for codec in CODECS:
                    label = CODEC_LABEL[codec]
                    for rel in REL_TOLS:
                        abs_bound = float(rel * ptp); condition = f"{label}_{rel:.0e}"
                        try:
                            t0 = time.time(); recon, compressed_bytes, config = core.codec_roundtrip(codec, field, abs_bound, work / condition); encode_seconds = time.time() - t0
                            recon = np.ascontiguousarray(np.asarray(recon, dtype=np.float64)); delta = recon - field
                            linf = float(np.max(np.abs(delta))); bound_ok = bool(linf <= abs_bound * (1 + 1e-6) + 1e-15)
                            recon_hash = hashlib.sha256(recon.tobytes(order="C")).hexdigest()
                            recon_grid = core.clone_grid_with_total(grid, recon)
                        except Exception as exc:
                            for solver in SOLVERS: add_fail(failures, m, label, rel, solver, "codec", f"{type(exc).__name__}: {exc}")
                            continue

                        t0 = time.time()
                        try:
                            b = core.run_bader(recon_grid); q = np.asarray(b["charges"], dtype=float)
                            if q.size != len(species): raise RuntimeError("BaderKit charge count mismatch")
                            rows.append({
                                "material_id": m, "codec": label, "relative_tolerance": rel, "absolute_bound": abs_bound,
                                "solver": "baderkit_ongrid", "status": "SUCCESS", "charges_json": json.dumps(q.tolist(), separators=(",", ":")),
                                "species_json": json.dumps(species, separators=(",", ":")), "realized_Linf": linf, "bound_respected": bound_ok,
                                "compressed_bytes": int(compressed_bytes), "codec_config": config, "encode_seconds": encode_seconds,
                                "solver_seconds": time.time()-t0, "source_sha256": meta["sha256"], "reconstructed_field_sha256": recon_hash,
                                "loader": loader, "npoints": field.size, "natoms": len(species),
                            })
                        except Exception as exc:
                            add_fail(failures, m, label, rel, "baderkit_ongrid", "baderkit", f"{type(exc).__name__}: {exc}")

                        t0 = time.time()
                        try:
                            logdir = work / "logs" / condition; logdir.mkdir(parents=True, exist_ok=True)
                            q, _, extra = study.solve("henkelman_ongrid", recon, lattice, frac, species, work / "henkelman" / condition, logdir)
                            q = np.asarray(q, dtype=float)
                            if q.size != len(species): raise RuntimeError("Henkelman charge count mismatch")
                            rows.append({
                                "material_id": m, "codec": label, "relative_tolerance": rel, "absolute_bound": abs_bound,
                                "solver": "henkelman_ongrid", "status": "SUCCESS", "charges_json": json.dumps(q.tolist(), separators=(",", ":")),
                                "species_json": json.dumps(species, separators=(",", ":")), "realized_Linf": linf, "bound_respected": bound_ok,
                                "compressed_bytes": int(compressed_bytes), "codec_config": config, "encode_seconds": encode_seconds,
                                "solver_seconds": time.time()-t0, "source_sha256": meta["sha256"], "reconstructed_field_sha256": recon_hash,
                                "loader": loader, "npoints": field.size, "natoms": len(species), "vacuum_charge_e": extra.get("vacuum_charge_e", ""),
                            })
                        except Exception as exc:
                            add_fail(failures, m, label, rel, "henkelman_ongrid", "henkelman", f"{type(exc).__name__}: {exc}")
        except Exception as exc:
            existing = {(r["material_id"], r["codec"], str(r["relative_tolerance"]), r["solver"]) for r in rows + failures}
            for codec in CODECS:
                label = CODEC_LABEL[codec]
                for rel in REL_TOLS:
                    for solver in SOLVERS:
                        key = (m, label, str(rel), solver)
                        if key not in existing: add_fail(failures, m, label, rel, solver, "source", f"{type(exc).__name__}: {exc}")

    rows.sort(key=lambda r: (r["material_id"], r["codec"], float(r["relative_tolerance"]), r["solver"]))
    failures.sort(key=lambda r: (r["material_id"], r["codec"], float(r["relative_tolerance"]), r["solver"]))
    write_csv(out / f"compressed_rows_shard_{a.shard_index:02d}.csv", rows, ["material_id", "codec", "relative_tolerance", "solver", "status"])
    write_csv(out / f"compressed_failures_shard_{a.shard_index:02d}.csv", failures, ["material_id", "codec", "relative_tolerance", "solver", "status", "stage", "error"])
    planned = len(selected) * len(CODECS) * len(REL_TOLS) * len(SOLVERS)
    if len(rows) + len(failures) != planned:
        raise RuntimeError(f"P4 compressed accounting mismatch {len(rows)+len(failures)} != {planned}")
    manifest = {
        "shard_index": a.shard_index, "shard_count": a.shard_count, "materials": len(selected),
        "planned_solver_evaluations": planned, "successful_rows": len(rows), "failed_rows": len(failures),
        "relative_tolerances": list(REL_TOLS), "codecs": [CODEC_LABEL[c] for c in CODECS],
        "reference_valid_pairs_sha256": hashlib.sha256(a.reference_valid_pairs.read_bytes()).hexdigest(),
    }
    (out / f"manifest_shard_{a.shard_index:02d}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2)); return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
