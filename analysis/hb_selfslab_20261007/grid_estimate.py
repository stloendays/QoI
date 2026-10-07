#!/usr/bin/env python3
"""Estimate the VASP 6 FFT grids (NGX, NGY, NGZ) and fine grids (NGXF, NGYF, NGZF) for a cell.

Rule (VASP 6 main.F, as reproduced on every OUTCAR of calibration/vasp_grid_validation.csv):
  XCUTOF_i = sqrt(ENCUT / RYTOEV) / (2 pi / (|a_i| / AUTOA))      (RYTOEV = 13.605826, AUTOA = 0.529177249)
  NG_i     = smallest n >= int(XCUTOF_i * WFACT + 0.5) with n = 2^p 3^q 5^r 7^s and p >= 1,
             WFACT = 4 for PREC = Accurate or High, 3 otherwise
  NGF_i    = 2 NG_i for PREC = Accurate (and Normal)
The fine grid is the grid of CHGCAR, AECCAR0 and AECCAR2; npoints = NGXF NGYF NGZF.

`python grid_estimate.py` checks the rule on calibration/vasp_grid_validation.csv (exit 1 on any mismatch).
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

RYTOEV = 13.605826
AUTOA = 0.529177249
FACTORS = (2, 3, 5, 7)


def fft_ok(n: int) -> bool:
    m, twos = n, 0
    for f in FACTORS:
        while m % f == 0:
            m //= f
            twos += f == 2
    return m == 1 and twos > 0


def ng(length: float, encut: float, prec: str = "Accurate") -> int:
    wfact = 4 if prec[:1].lower() in ("a", "h") else 3
    xcut = math.sqrt(encut / RYTOEV) / (2 * math.pi / (length / AUTOA))
    n = int(xcut * wfact + 0.5)
    while not fft_ok(n):
        n += 1
    return n


def grids(lengths, encut: float = 520.0, prec: str = "Accurate"):
    """((NGX, NGY, NGZ), (NGXF, NGYF, NGZF), npoints of the fine grid) for lattice vector lengths in Angstrom."""
    g = tuple(ng(float(x), encut, prec) for x in lengths)
    gf = tuple(2 * x for x in g)
    return g, gf, gf[0] * gf[1] * gf[2]


def validate(path: Path) -> int:
    bad = 0
    n = 0
    for r in csv.DictReader(open(path, encoding="utf-8")):
        g, gf, _ = grids((r["a"], r["b"], r["c"]), float(r["encut"]), r["prec"])
        obs = tuple(int(r[k]) for k in ("NGX", "NGY", "NGZ")), tuple(int(r[k]) for k in ("NGXF", "NGYF", "NGZF"))
        ok = (g, gf) == obs
        n += int(r["n_outcars"])
        bad += 0 if ok else 1
        print(f"{r['encut']:>6} {r['prec']:<9} {r['a']:>12} {r['b']:>12} {r['c']:>12}  est {g} {gf}  obs {obs[0]} {obs[1]}"
              f"  {'OK' if ok else 'MISMATCH'}")
    print(f"{'all match' if not bad else f'{bad} mismatches'} ({n} OUTCARs)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(validate(Path(__file__).resolve().parent / "calibration" / "vasp_grid_validation.csv"))
