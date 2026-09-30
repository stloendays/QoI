#!/usr/bin/env python3
"""Merge per-system checkpoints into descriptors.csv and failures.csv (WP-D)."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

COLUMNS = [
    "material_id", "corpus", "system_type", "source", "formula", "grid_shape",
    # target
    "stability_floor_A1_e", "log10_floor",
    # group 1
    "natoms", "npoints", "mean_grid_spacing_A", "max_axis_grid_spacing_A", "cell_aspect_ratio",
    "vacuum_fraction",
    # group 2
    "eps_m", "eps_over_rho_max", "eps_over_rho_median",
    # group 3
    "boundary_fraction", "boundary_gap_p05_over_eps", "boundary_gap_p50_over_eps",
    "boundary_gap_p95_over_eps", "boundary_gap_lt1_fraction",
    # group 4
    "near_tie_fraction_lt_eps", "near_tie_fraction_lt_0p1eps",
    # group 5
    "min_basin_voxels", "min_basin_charge_e", "n_basins_lt_100_voxels",
    # group 6 (diagnostic)
    "n_axis_order_flips_noise_seed20260905",
    # auxiliary / provenance (not model inputs)
    "n_boundary_voxels", "n_boundary_pairs_directed", "boundary_gap_min_over_eps",
    "n_neighbour_pairs", "min_basin_atom_index", "n_empty_basins", "n_bader_maxima",
    "n_vacuum_voxels_bader", "n_vacuum_voxels_labels", "vacuum_charge_e",
    "min_atom_charge_e", "max_atom_charge_e", "n_voxels_reassigned_noise_seed20260905",
    "probe_rel_error", "cell_volume_A3", "lattice_a_A", "lattice_b_A", "lattice_c_A",
    "rho_mean", "rho_max", "rho_min", "rho_median", "rho_ptp", "total_electrons_e",
    "fixed_basin_self_error_e", "loader", "source_sha256", "loaded_from_cache",
    "download_seconds", "bader_seconds", "neighbour_seconds", "wall_seconds", "attempts",
]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--wp-dir", type=Path, required=True)
    args = p.parse_args()
    repo = args.repo_root.resolve()
    wp = args.wp_dir.resolve()
    ck = wp / "checkpoints"

    with (repo / "stability" / "stability_floor_A1.csv").open(newline="", encoding="utf-8") as f:
        ids = sorted(r["material_id"] for r in csv.DictReader(f))

    rows = []
    failures = []
    for m in ids:
        cp = ck / f"{m}.json"
        fp = ck / f"{m}.failure.json"
        if cp.exists():
            r = json.loads(cp.read_text(encoding="utf-8"))
            rows.append({c: r.get(c, "") for c in COLUMNS})
        elif fp.exists():
            e = json.loads(fp.read_text(encoding="utf-8"))
            failures.append({
                "material_id": m, "stage": e.get("stage", ""), "attempts": e.get("attempt", ""),
                "error_type": e.get("error_type", ""), "error": e.get("error", ""), "time": e.get("time", ""),
            })
        else:
            failures.append({"material_id": m, "stage": "not_run", "attempts": 0,
                             "error_type": "MISSING", "error": "no checkpoint and no failure record", "time": ""})

    with (wp / "descriptors.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    with (wp / "failures.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["material_id", "stage", "attempts", "error_type", "error", "time"])
        w.writeheader()
        w.writerows(failures)
    print(f"descriptors rows: {len(rows)} / {len(ids)}; failures: {len(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
