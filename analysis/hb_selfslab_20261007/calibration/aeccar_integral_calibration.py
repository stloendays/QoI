#!/usr/bin/env python3
"""Calibrate the AECCAR0 + AECCAR2 electron-count check on already-used Materials Project data (QC calibration only).

Rows: every row of analysis/fresh_population_20261006/P2_CONFIRMATORY_MANIFEST.csv with npoints <= 1,000,000, in
manifest order (all of them already used and in the exclusion set, so no candidate of this cohort is read). MP static
runs use ENCUT 520 eV and PREC = Accurate, the settings of this cohort.

For each row: download aeccar0s/<task_id>.json.gz and aeccar2s/<task_id>.json.gz from the MP parsed bucket, decode with
the development loader (decode_mp_chgcar), and record sum/N of each (electrons in VASP's rho x V convention) and the
sum of atomic numbers Z of the structure, and the atoms that sit exactly on a grid point (|frac x n - round| < 1e-4 on
all three axes), where a point-sampled core density is largest. The fine grid of grid_estimate.py for ENCUT 520 eV,
PREC = Accurate is compared with the MP grid (a second check of the estimator, on MP's VASP builds). No compression, Hartree or Bader quantity is computed.

Output: aeccar_integral_calibration.csv in this directory.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MANIFEST = REPO / "analysis/fresh_population_20261006/P2_CONFIRMATORY_MANIFEST.csv"
BUCKET = "https://materialsproject-parsed.s3.amazonaws.com/"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    dev = load("development_compatibility_smoke", REPO / "validation/qsq_prospective/development_compatibility_smoke.py")
    eng = load("run_engineering", REPO / "analysis/operator_aware_bader_fixed_partition/run_engineering.py")
    ge = load("grid_estimate", HERE.parent / "grid_estimate.py")
    rows = [r for r in csv.DictReader(open(MANIFEST, encoding="utf-8")) if int(r["npoints"]) <= 1_000_000]
    out = []
    for r in rows:
        rec = {"material_id": r["material_id"], "task_id": r["task_id"], "formula": r["formula"], "ngrid": r["ngrid"]}
        try:
            sums = {}
            for k in "02":
                blob = eng.fetch(BUCKET + f"aeccar{k}s/{r['task_id']}.json.gz")
                rec[f"aeccar{k}_sha256"] = hashlib.sha256(blob).hexdigest()
                c = dev.decode_mp_chgcar(blob)
                x = np.asarray(c.data["total"], dtype=np.float64)
                rec[f"aeccar{k}_grid"] = "x".join(map(str, x.shape))
                rec[f"aeccar{k}_finite"] = int(np.all(np.isfinite(x)))
                sums[k] = float(x.sum() / x.size)
                rec[f"aeccar{k}_sum_over_n"] = f"{sums[k]:.6f}"
                st = c.structure
                del c, x, blob
            ztot = int(sum(s.specie.Z for s in st))
            dims = np.array([int(v) for v in rec["aeccar0_grid"].split("x")], float)
            g = st.frac_coords * dims
            on = np.all(np.abs(g - np.round(g)) < 1e-4, axis=1)
            est = ge.grids(st.lattice.abc, 520.0, "Accurate")[1]
            rec |= {"a": f"{st.lattice.a:.6f}", "b": f"{st.lattice.b:.6f}", "c": f"{st.lattice.c:.6f}",
                    "estimated_fine_grid_520_accurate": "x".join(map(str, est)),
                    "estimate_matches_grid": int("x".join(map(str, est)) == rec["aeccar0_grid"])}
            rec |= {"natoms": len(st), "sum_Z": ztot, "n_atoms_on_grid_point": int(on.sum()),
                    "sum_Z_on_grid_point": int(sum(s.specie.Z for s, o in zip(st, on) if o)),
                    "total_sum_over_n": f"{sums['0'] + sums['2']:.6f}",
                    "rel_dev_total": f"{(sums['0'] + sums['2'] - ztot) / ztot:.6e}"}
        except Exception as exc:  # noqa: BLE001
            rec["error"] = f"{type(exc).__name__}:{str(exc)[:160]}"
        print(rec, flush=True)
        out.append(rec)
    cols = ["material_id", "task_id", "formula", "ngrid", "natoms", "sum_Z", "n_atoms_on_grid_point",
            "sum_Z_on_grid_point", "a", "b", "c", "estimated_fine_grid_520_accurate", "estimate_matches_grid",
            "aeccar0_grid", "aeccar2_grid",
            "aeccar0_finite", "aeccar2_finite", "aeccar0_sum_over_n", "aeccar2_sum_over_n", "total_sum_over_n",
            "rel_dev_total", "aeccar0_sha256", "aeccar2_sha256", "error"]
    with open(HERE / "aeccar_integral_calibration.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for rec in out:
            w.writerow({c: rec.get(c, "") for c in cols})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
