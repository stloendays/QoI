#!/usr/bin/env python3
"""Probe: xc.py energy densities and LDA potential against PySCF/libxc on one P1 density (JSON to stdout)."""
import argparse
import csv
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path("/scratch/junbotong/qoi-srv-20261024")
sys.path.insert(0, str(ROOT / "analysis/nonlinear_xc_20261024"))
sys.path.insert(0, str(ROOT / "frozen/validation"))
sys.path.insert(0, str(ROOT / "validation/qsq_prospective"))
import xc  # noqa: E402
import development_compatibility_smoke as dev  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--material", required=True)
a = ap.parse_args()
man = {r["material_id"]: r for r in csv.DictReader(open(ROOT / "analysis/fresh_population_20261006/P1_CONFIRMATORY_MANIFEST.csv", encoding="utf-8"))}
meta = man[a.material]
blob = (ROOT / "analysis/server_runs_20261024/vanda/inputs/xc" / f"{a.material}.src").read_bytes()
with tempfile.TemporaryDirectory() as td:
    grid, _ = dev.build_grid(meta, blob, Path(td))
x = np.asarray(grid.total, float)
lat = np.asarray(grid.structure.lattice.matrix, float)
res = xc.check_against_libxc(x, lat)
res["material_id"] = a.material
res["electrons"] = float(x.sum() / x.size)
print(json.dumps(res, indent=1))
