#!/usr/bin/env python3
"""Write the VASP inputs of the 40 drawn slabs (PROTOCOL.md sections 5.7, 5.8 and 7).

For each row of selection/drawn.csv: inputs/<draw_rank:02d>_<material_id>/ with
  POSCAR        the accepted orthogonal slab, sorted (get_sorted_structure), no site properties;
  KPOINTS       Gamma-centred, ceil(2 pi / (|a_i| 0.25)) in plane, 1 along the normal;
  INCAR_normal  the section 7 settings (ALGO = Normal) plus the performance-only NCORE;
  INCAR_all     identical except ALGO = All (the one declared fallback);
  POTCAR.spec   the MPRelaxSet POTCAR symbols in POSCAR species order (the POTCAR itself is assembled on Vanda);
and inputs/inputs.csv (one row per slab, SHA-256 of each file).

Usage: make_inputs.py --ncore N
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FILES = ("POSCAR", "KPOINTS", "INCAR_normal", "INCAR_all", "POTCAR.spec")


def incar(title: str, algo: str, ncore: int) -> str:
    tags = [("SYSTEM", title), ("PREC", "Accurate"), ("ENCUT", "520"), ("EDIFF", "1E-6"), ("ISMEAR", "0"),
            ("SIGMA", "0.05"), ("ISPIN", "1"), ("LASPH", ".TRUE."), ("LREAL", ".FALSE."), ("ALGO", algo),
            ("NELM", "200"), ("LCHARG", ".TRUE."), ("LAECHG", ".TRUE."), ("LWAVE", ".FALSE."),
            ("NCORE", f"{ncore}   ! parallelisation only")]
    return "".join(f"{k:<7}= {v}\n" for k, v in tags)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ncore", type=int, required=True)
    a = ap.parse_args(argv)
    from pymatgen.core import Lattice, Structure
    from pymatgen.core.surface import Slab
    from pymatgen.io.vasp import Kpoints, Poscar
    from pymatgen.io.vasp.sets import MPRelaxSet

    rows = list(csv.DictReader(open(ROOT / "selection" / "drawn.csv", encoding="utf-8")))
    table = []
    for r in rows:
        mid = r["material_id"]
        slab = Slab.from_dict(json.loads((ROOT / "selection" / "slabs" / f"{mid}.json").read_text(encoding="utf-8")))
        s = slab.get_sorted_structure()
        clean = Structure(Lattice(s.lattice.matrix), [site.specie.symbol for site in s], s.frac_coords,
                          coords_are_cartesian=False)
        d = HERE / f"{int(r['draw_rank']):02d}_{mid}"
        d.mkdir(parents=True, exist_ok=True)
        title = f"{mid} {r['reduced_formula']} ({r['miller']}) term {r['termination']} selfslab"
        (d / "POSCAR").write_text(Poscar(clean, comment=title).get_str(significant_figures=12), encoding="utf-8",
                                  newline="\n")
        abc = clean.lattice.abc
        kp = [math.ceil(2 * math.pi / (abc[0] * 0.25)), math.ceil(2 * math.pi / (abc[1] * 0.25)), 1]
        assert "x".join(map(str, kp)) == r["kpoints"], (mid, kp, r["kpoints"])
        (d / "KPOINTS").write_text(str(Kpoints.gamma_automatic(kp)), encoding="utf-8", newline="\n")
        (d / "INCAR_normal").write_text(incar(title, "Normal", a.ncore), encoding="utf-8", newline="\n")
        (d / "INCAR_all").write_text(incar(title, "All", a.ncore), encoding="utf-8", newline="\n")
        elems = [e.symbol for e in clean.composition.elements]
        pot = [MPRelaxSet.CONFIG["POTCAR"][e] for e in elems]
        assert pot == r["potcar_symbols"].split(), (mid, pot, r["potcar_symbols"])
        species_line = Poscar(clean).get_str().split("\n")[5].split()
        assert species_line == elems, (mid, species_line, elems)
        (d / "POTCAR.spec").write_text("\n".join(pot) + "\n", encoding="utf-8", newline="\n")
        assert len(clean) == int(r["natoms"])
        rec = {"draw_rank": r["draw_rank"], "material_id": mid, "dir": d.name, "reduced_formula": r["reduced_formula"],
               "miller": r["miller"], "termination": r["termination"], "natoms": len(clean),
               "a": f"{abc[0]:.6f}", "b": f"{abc[1]:.6f}", "c": f"{abc[2]:.6f}", "ngf_est": r["ngf"],
               "npoints_est": r["npoints_est"], "kpoints": r["kpoints"], "potcar_symbols": " ".join(pot),
               "ncore": a.ncore}
        for fn in FILES:
            rec[f"sha256_{fn}"] = hashlib.sha256((d / fn).read_bytes()).hexdigest()
        table.append(rec)
    with open(HERE / "inputs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(table)
    print(f"{len(table)} input directories written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
