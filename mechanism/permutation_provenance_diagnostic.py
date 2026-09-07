#!/usr/bin/env python3
"""Diagnose unshuffled provenance mismatch without changing scientific semantics."""
from __future__ import annotations
import csv, hashlib, json, sys, tempfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mechanism"))
sys.path.insert(0, str(ROOT / "validation"))
import residual_spatial_permutation_v2 as perm
import external_end_to_end as core
from baderkit import Grid

MID = "mp-1038991"
CODEC = "ZFP"
TOL = 1e-3


def per_atom_expected():
    path = ROOT / "mechanism" / "basin_error_decomposition_per_atom.csv"
    with path.open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["material_id"] == MID and r["codec"].upper() == CODEC and abs(float(r["relative_tolerance"])-TOL) < 1e-15]
    return sorted(rows, key=lambda r: int(r["atom_index"]))


def digest_array(a):
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()


def main():
    record = perm.source_record(MID)
    expected = per_atom_expected()
    with tempfile.TemporaryDirectory(prefix="qoi_prov_diag_") as td:
        work = Path(td)
        chgcar, sha, nbytes = perm.load_mp_chgcar(record, work)
        grid = Grid.from_dynamic(chgcar)
        field = np.asarray(grid.total, dtype=np.float64)
        original = core.run_bader(grid)
        q0 = np.asarray(original["charges"], dtype=np.float64)
        ptp = float(np.ptp(field))
        recon, compressed_bytes, mode = core.codec_roundtrip("zfp", field, TOL*ptp, work)
        recon = np.asarray(recon, dtype=np.float64)
        resolved = core.run_bader(core.clone_grid_with_total(grid, recon))
        q1 = np.asarray(resolved["charges"], dtype=np.float64)
        print("source_sha", sha, "bytes", nbytes)
        print("shape", field.shape, "npoints", field.size, "min", float(field.min()), "max", float(field.max()), "ptp", ptp, "sum", float(field.sum()))
        print("field_sha256_float64", digest_array(field))
        print("recon_sha256_float64", digest_array(recon))
        print("linf", float(np.max(np.abs(recon-field))), "rmse", float(np.sqrt(np.mean((recon-field)**2))))
        print("compressed_bytes", compressed_bytes, "compression_ratio", field.nbytes/compressed_bytes, "mode", mode)
        print("actual_resolved_max_error", float(np.max(np.abs(q1-q0))))
        print("expected_mechanism_max_error", max(abs(float(r["dq_total_e"])) for r in expected))
        print("atom,element,q0_expected,q0_actual,dq0,q1_expected,q1_actual,dq1,dq_expected,dq_actual")
        for r in expected:
            i=int(r["atom_index"]); e=r["element"]
            q0e=float(r["q_original_e"]); q1e=float(r["q_recon_new_basins_e"])
            print(f"{i},{e},{q0e:.15g},{q0[i]:.15g},{q0[i]-q0e:.15g},{q1e:.15g},{q1[i]:.15g},{q1[i]-q1e:.15g},{q1e-q0e:.15g},{q1[i]-q0[i]:.15g}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
