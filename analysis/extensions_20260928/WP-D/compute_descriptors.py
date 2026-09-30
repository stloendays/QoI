#!/usr/bin/env python3
"""WP-D descriptor computation: one on-grid Bader solve per system.

Reuses the frozen scientific stack:
  * development loader + exact-byte fetch: validation/qsq_prospective/development_compatibility_smoke.py
  * external loader (AFLOW/NOMAD), Bader settings: ../frozen/validation/external_end_to_end.py (commit 893f931)

Writes one checkpoint JSON per system under <out>/checkpoints/ and one failure JSON per
failed system. Densities (raw source bytes and parsed field/labels) are cached outside the
repository under --cache-dir. Nothing under the frozen directories is modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np

NEIGHBOUR_OFFSETS = [
    (dx, dy, dz)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    for dz in (-1, 0, 1)
    if (dx, dy, dz) != (0, 0, 0)
]
assert len(NEIGHBOUR_OFFSETS) == 26
# One representative per unordered neighbour pair (offset and its negative).
HALF_OFFSETS = [o for o in NEIGHBOUR_OFFSETS if o > (0, 0, 0)]
assert len(HALF_OFFSETS) == 13

QSQ_SEED = 20260905
VACUUM_FRACTION_RELATIVE_THRESHOLD = 1e-3
SMALL_BASIN_VOXELS = 100


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-validation-dir", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--worker", type=int, default=0)
    p.add_argument("--nworkers", type=int, default=1)
    p.add_argument("--only", type=str, default="", help="comma-separated material_ids (smoke)")
    p.add_argument("--max-attempts", type=int, default=3)
    return p.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    import csv

    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def roll(a: np.ndarray, off: tuple[int, int, int]) -> np.ndarray:
    return np.roll(a, shift=off, axis=(0, 1, 2))


def neighbour_descriptors(field: np.ndarray, labels: np.ndarray, eps: float) -> dict[str, Any]:
    """Groups 3 and 4. Offsets are processed one at a time to bound memory."""
    n = field.size
    boundary = np.zeros(field.shape, dtype=bool)
    min_gap = np.full(field.shape, np.inf, dtype=np.float64)
    n_boundary_pairs = 0  # directed (voxel, neighbour) pairs with differing labels
    for off in NEIGHBOUR_OFFSETS:
        ln = roll(labels, off)
        diff = ln != labels
        n_boundary_pairs += int(np.count_nonzero(diff))
        if not diff.any():
            continue
        boundary |= diff
        gap = np.abs(roll(field, off) - field)
        np.minimum(min_gap, np.where(diff, gap, np.inf), out=min_gap)
    n_boundary = int(np.count_nonzero(boundary))
    out: dict[str, Any] = {
        "n_boundary_voxels": n_boundary,
        "boundary_fraction": n_boundary / n,
        "n_boundary_pairs_directed": n_boundary_pairs,
    }
    if n_boundary > 0:
        g = min_gap[boundary] / eps
        out.update(
            {
                "boundary_gap_p05_over_eps": float(np.percentile(g, 5)),
                "boundary_gap_p50_over_eps": float(np.percentile(g, 50)),
                "boundary_gap_p95_over_eps": float(np.percentile(g, 95)),
                "boundary_gap_lt1_fraction": float(np.mean(g < 1.0)),
                "boundary_gap_min_over_eps": float(np.min(g)),
            }
        )
    else:
        out.update(
            {
                "boundary_gap_p05_over_eps": float("nan"),
                "boundary_gap_p50_over_eps": float("nan"),
                "boundary_gap_p95_over_eps": float("nan"),
                "boundary_gap_lt1_fraction": float("nan"),
                "boundary_gap_min_over_eps": float("nan"),
            }
        )
    del boundary, min_gap

    # Near-tie density over all unordered (voxel, 26-neighbour) pairs = 13 N pairs.
    n_lt_eps = 0
    n_lt_01eps = 0
    for off in HALF_OFFSETS:
        d = np.abs(roll(field, off) - field)
        n_lt_eps += int(np.count_nonzero(d < eps))
        n_lt_01eps += int(np.count_nonzero(d < 0.1 * eps))
    n_pairs = len(HALF_OFFSETS) * n
    out.update(
        {
            "n_neighbour_pairs": n_pairs,
            "near_tie_fraction_lt_eps": n_lt_eps / n_pairs,
            "near_tie_fraction_lt_0p1eps": n_lt_01eps / n_pairs,
        }
    )
    return out


def compute_system(
    material_id: str,
    meta: dict[str, str],
    manifest_records: dict[str, dict[str, Any]],
    per_seed: dict[str, dict[str, str]],
    floor: float,
    devmod: Any,
    core: Any,
    cache_dir: Path,
) -> dict[str, Any]:
    t_start = time.time()
    rec: dict[str, Any] = {"material_id": material_id}
    field_cache = cache_dir / "fields" / f"{material_id}.npz"
    blob_cache = cache_dir / "blobs" / meta["sha256"]

    from baderkit import Grid

    t0 = time.time()
    if field_cache.exists():
        z = np.load(field_cache)
        field = np.asarray(z["field"], dtype=np.float64)
        lattice = np.asarray(z["lattice"], dtype=np.float64)
        labels = np.asarray(z["labels"], dtype=np.int64)
        charges = np.asarray(z["charges"], dtype=np.float64)
        n_maxima = int(z["n_maxima"])
        num_vacuum = int(z["num_vacuum"])
        vacuum_charge = float(z["vacuum_charge"])
        natoms = int(z["natoms"])
        loader = str(z["loader"])
        rec["loaded_from_cache"] = True
        rec["download_seconds"] = 0.0
        rec["bader_seconds"] = float(z["bader_seconds"])
    else:
        rec["loaded_from_cache"] = False
        with tempfile.TemporaryDirectory(prefix="qoi_wpd_") as td:
            workdir = Path(td)
            if meta["corpus"].startswith("dev"):
                if blob_cache.exists() and sha256_file(blob_cache) == meta["sha256"]:
                    blob = blob_cache.read_bytes()
                    if len(blob) != int(meta["source_bytes"]):
                        raise RuntimeError("cached blob byte-count mismatch")
                else:
                    blob = devmod.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
                    blob_cache.parent.mkdir(parents=True, exist_ok=True)
                    blob_cache.write_bytes(blob)
                rec["download_seconds"] = time.time() - t0
                grid, loader = devmod.build_grid(meta, blob, workdir)
                del blob
            else:
                record = manifest_records[material_id]
                if record["sha256"] != meta["sha256"] or record["url"] != meta["url"]:
                    raise RuntimeError("manifest/metadata provenance mismatch")
                chg_path, prov = core.materialize_chgcar(record, workdir)
                rec["download_seconds"] = float(prov["download_seconds"])
                grid = Grid.from_dynamic(chg_path)
                core.audit_grid(record, grid)
                loader = "frozen_external_materialize_chgcar:" + prov["parser_provenance"]
        field = np.asarray(grid.total, dtype=np.float64)
        shape_expected = devmod.parse_shape(meta["ngrid"])
        if tuple(int(x) for x in field.shape) != shape_expected:
            raise RuntimeError(f"grid shape {field.shape} != metadata {shape_expected}")
        if int(field.size) != int(meta["npoints"]):
            raise RuntimeError("npoints mismatch")
        natoms = int(len(grid.structure))
        if natoms != int(meta["natoms"]):
            raise RuntimeError(f"natoms {natoms} != metadata {meta['natoms']}")
        if not np.all(np.isfinite(field)):
            raise RuntimeError("non-finite density values")
        lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)

        t1 = time.time()
        original = core.run_bader(grid)
        rec["bader_seconds"] = time.time() - t1
        charges = np.asarray(original["charges"], dtype=np.float64)
        labels = np.asarray(original["atom_labels"]).astype(np.int64, copy=False)
        n_maxima = int(original["n_maxima"])
        num_vacuum = int(original["num_vacuum_voxels"])
        vacuum_charge = float(original["vacuum_charge_e"])
        if charges.size != natoms:
            raise RuntimeError("Bader returned wrong number of atom charges")
        if labels.shape != field.shape:
            raise RuntimeError("atom_labels shape mismatch")
        field_cache.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            field_cache,
            field=field,
            lattice=lattice,
            labels=labels.astype(np.int16),
            charges=charges,
            n_maxima=n_maxima,
            num_vacuum=num_vacuum,
            vacuum_charge=vacuum_charge,
            natoms=natoms,
            loader=loader,
            bader_seconds=rec["bader_seconds"],
        )
        del grid

    rec["loader"] = loader
    rec["source_sha256"] = meta["sha256"]
    n = int(field.size)
    shape = [int(x) for x in field.shape]

    # Integrity: fixed-basin integration on the reference labels reproduces the Bader charges.
    q_fixed = core.fixed_basin_charges(field, labels, natoms)
    rec["fixed_basin_self_error_e"] = float(np.max(np.abs(q_fixed - charges)))

    # Group 1: grid/cell descriptors.
    abc = np.linalg.norm(lattice, axis=1)
    volume = float(abs(np.linalg.det(lattice)))
    mean_rho = float(field.mean())
    rec.update(
        {
            "corpus": meta["corpus"],
            "system_type": meta["system_type"],
            "source": meta["source"],
            "formula": meta["formula"],
            "grid_shape": "x".join(str(s) for s in shape),
            "natoms": natoms,
            "npoints": n,
            "cell_volume_A3": volume,
            "lattice_a_A": float(abc[0]),
            "lattice_b_A": float(abc[1]),
            "lattice_c_A": float(abc[2]),
            "mean_grid_spacing_A": float((volume / n) ** (1.0 / 3.0)),
            "max_axis_grid_spacing_A": float(max(abc[i] / shape[i] for i in range(3))),
            "cell_aspect_ratio": float(abc.max() / abc.min()),
            "vacuum_fraction": float(np.mean(field < VACUUM_FRACTION_RELATIVE_THRESHOLD * mean_rho)),
            "rho_mean": mean_rho,
            "rho_max": float(field.max()),
            "rho_min": float(field.min()),
            "rho_median": float(np.median(field)),
            "rho_ptp": float(np.ptp(field)),
            "total_electrons_e": float(field.sum() / n),
        }
    )

    # Group 2: perturbation amplitude ratios.
    seed_row = per_seed[material_id]
    eps = float(seed_row["probe_linf"])
    rec.update(
        {
            "eps_m": eps,
            "eps_over_rho_max": eps / rec["rho_max"] if rec["rho_max"] > 0 else float("inf"),
            "eps_over_rho_median": eps / rec["rho_median"] if rec["rho_median"] > 0 else float("inf"),
            "probe_rel_error": float(seed_row["probe_rel_error"]),
        }
    )

    # Groups 3-4.
    t2 = time.time()
    rec.update(neighbour_descriptors(field, labels, eps))
    rec["neighbour_seconds"] = time.time() - t2

    # Group 5: basin sizes (atom basins; label natoms = vacuum).
    counts = np.bincount(labels.ravel(), minlength=natoms + 1)
    atom_counts = counts[:natoms]
    i_min = int(np.argmin(atom_counts))
    rec.update(
        {
            "min_basin_voxels": int(atom_counts[i_min]),
            "min_basin_charge_e": float(charges[i_min]),
            "min_basin_atom_index": i_min,
            "n_basins_lt_100_voxels": int(np.count_nonzero(atom_counts < SMALL_BASIN_VOXELS)),
            "n_empty_basins": int(np.count_nonzero(atom_counts == 0)),
            "n_bader_maxima": n_maxima,
            "n_vacuum_voxels_bader": int(num_vacuum),
            "n_vacuum_voxels_labels": int(counts[natoms]),
            "vacuum_charge_e": vacuum_charge,
            "min_atom_charge_e": float(charges.min()),
            "max_atom_charge_e": float(charges.max()),
        }
    )

    # Group 6: ordering fragility (diagnostic; requires the perturbation).
    rec["n_axis_order_flips_noise_seed20260905"] = int(seed_row["n_axis_order_flips_noise"])
    rec["n_voxels_reassigned_noise_seed20260905"] = int(seed_row["n_voxels_reassigned_noise"])

    # Target.
    rec["stability_floor_A1_e"] = floor
    rec["log10_floor"] = float(np.log10(floor))
    rec["wall_seconds"] = time.time() - t_start
    return rec


def main() -> int:
    import logging

    logging.disable(logging.INFO)  # baderkit emits verbose INFO per solve stage
    args = parse_args()
    repo = args.repo_root.resolve()
    frozen_validation = args.frozen_validation_dir.resolve()
    cache_dir = args.cache_dir.resolve()
    outdir = args.output_dir.resolve()
    ck_dir = outdir / "checkpoints"
    ck_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(frozen_validation))
    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import external_end_to_end as core  # type: ignore
    import development_compatibility_smoke as devmod  # type: ignore

    metadata = {r["material_id"]: r for r in load_csv(repo / "materials_metadata.csv")}
    floors = {r["material_id"]: float(r["stability_floor_A1_e"]) for r in load_csv(repo / "stability" / "stability_floor_A1.csv")}
    per_seed = {
        r["material_id"]: r
        for r in load_csv(repo / "stability" / "stability_floor_A1_per_seed.csv")
        if int(r["seed"]) == QSQ_SEED
    }
    manifest = json.loads((repo / "external_test_MANIFEST.json").read_text(encoding="utf-8"))
    manifest_records = {r["material_id"]: r for r in manifest["records"]}

    ids = sorted(floors)
    if args.only:
        ids = [m for m in ids if m in set(args.only.split(","))]
    ids = [m for i, m in enumerate(ids) if i % args.nworkers == args.worker]
    print(f"[worker {args.worker}/{args.nworkers}] {len(ids)} systems", flush=True)

    for k, material_id in enumerate(ids):
        ck = ck_dir / f"{material_id}.json"
        if ck.exists():
            continue
        fail_path = ck_dir / f"{material_id}.failure.json"
        last_err: dict[str, Any] | None = None
        for attempt in range(1, args.max_attempts + 1):
            try:
                rec = compute_system(
                    material_id, metadata[material_id], manifest_records, per_seed,
                    floors[material_id], devmod, core, cache_dir,
                )
                rec["attempts"] = attempt
                ck.write_text(json.dumps(rec, indent=1), encoding="utf-8")
                if fail_path.exists():
                    fail_path.unlink()
                print(
                    f"[worker {args.worker}] {k+1}/{len(ids)} {material_id} ok "
                    f"npoints={rec['npoints']} bader={rec['bader_seconds']:.1f}s wall={rec['wall_seconds']:.1f}s",
                    flush=True,
                )
                last_err = None
                break
            except Exception as exc:  # noqa: BLE001
                last_err = {
                    "material_id": material_id,
                    "attempt": attempt,
                    "stage": "compute_system",
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:2000],
                    "traceback": traceback.format_exc()[-4000:],
                    "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                print(f"[worker {args.worker}] {material_id} attempt {attempt} FAILED: {type(exc).__name__}: {str(exc)[:200]}", flush=True)
                time.sleep(5 * attempt)
        if last_err is not None:
            fail_path.write_text(json.dumps(last_err, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
