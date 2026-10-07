#!/usr/bin/env python3
"""Input QC of one self-computed slab run (PROTOCOL.md section 6). Reads the gzipped files copied back from Vanda.

Run directory (D:/Research/QoI-ext-cache/selfslab/runs/<material_id>/) holds CHGCAR.gz, AECCAR0.gz, AECCAR2.gz,
OUTCAR.gz, OSZICAR.gz (and the OUTCAR/OSZICAR of a first, NELM-limited attempt when the ALGO = All fallback ran).

Checks, in order; the first failure is the reason:
  1. converged        OUTCAR has "aborting loop because EDIFF is reached" in the final run;
  2. same_grid        the grid lines of CHGCAR, AECCAR0 and AECCAR2 are equal, and equal to OUTCAR's NGXF x NGYF x NGZF;
  3. no_E_tokens      no Fortran E-format token with the E dropped (NO_E_RE) and no `**` overflow token in any file;
  4. finite           each file parses with baderkit Grid.from_dynamic through the slab adapter's
                      run_joint_slab.parse_vasp_total to an array of that grid with all values finite;
  5. electron_count   R = (sum(AECCAR0) + sum(AECCAR2)) / N / sum(Z) within [R_MIN, R_MAX] (PROTOCOL.md section 6).
Diagnostics (no gate): sum(CHGCAR)/N and sum(AECCAR2)/N against NELECT; sum(AECCAR0)/N against sum(Z - ZVAL); atoms on
grid points; SCF steps, wall time and maximum memory from OUTCAR.

NO_E_RE, STARS_RE and split_header are copied verbatim from
analysis/hb_slab_nomad_wide_20261007/selection/select_wide.py on branch research/hb-slab-nomad-wide-20261007
(blob be633b889e46bdecf0333b4c98f62a8bfa5f687f).
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
R_MIN, R_MAX = 0.80, 50.0
NO_E_RE = re.compile(rb"\d[+-]\d{2,3}(?=\s|\Z)")      # Fortran E-format with the E dropped: 0.65466110724+193
STARS_RE = re.compile(rb"\*{2,}")
FILES = ("CHGCAR", "AECCAR0", "AECCAR2")


def split_header(raw: bytes):
    """(grid 'nx x ny x nz', npoints, natoms, byte offset of the first data line) of a VASP volumetric file."""
    lines = raw.split(b"\n")
    tok5 = lines[5].split()
    if tok5 and all(re.fullmatch(rb"\d+", t) for t in tok5):
        counts, hdr = [int(t) for t in tok5], 6
    else:
        counts, hdr = [int(t) for t in lines[6].split()], 7
    if lines[hdr].strip()[:1] in (b"S", b"s"):     # Selective dynamics
        hdr += 1
    i = hdr + 1 + sum(counts)
    while not lines[i].strip():
        i += 1
    if i >= len(lines) - 1:
        raise ValueError("truncated before the end of the grid line")
    dims = [int(x) for x in lines[i].split()[:3]]
    if len(dims) != 3:
        raise ValueError("no grid line")
    off = sum(len(x) + 1 for x in lines[:i + 1])
    return "x".join(map(str, dims)), int(np.prod(dims)), sum(counts), off


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def outcar_facts(text: str) -> dict:
    f: dict = {}
    m = re.search(r"dimension x,y,z NGXF=\s*(\d+)\s+NGYF=\s*(\d+)\s+NGZF=\s*(\d+)", text)
    f["outcar_ngf"] = "x".join(m.groups()) if m else ""
    m = re.search(r"dimension x,y,z NGX =\s*(\d+)\s+NGY =\s*(\d+)\s+NGZ =\s*(\d+)", text)
    f["outcar_ng"] = "x".join(m.groups()) if m else ""
    m = re.search(r"NELECT\s*=\s*([\d.]+)", text)
    f["nelect"] = float(m.group(1)) if m else None
    m = re.search(r"Ionic Valenz\s*\n\s*ZVAL\s*=\s*([\d. ]+)", text)
    f["zval"] = [float(x) for x in m.group(1).split()] if m else []
    f["titel"] = re.findall(r"TITEL\s*=\s*(.+)", text)
    f["ions_per_type"] = [int(x) for x in (re.search(r"ions per type =\s*([\d ]+)", text) or [None, ""])[1].split()]
    f["converged"] = int("aborting loop because EDIFF is reached" in text)
    f["ediff_not_reached"] = int("EDIFF was not reached" in text)
    m = re.search(r"Elapsed time \(sec\):\s*([\d.]+)", text)
    f["elapsed_s"] = float(m.group(1)) if m else None
    m = re.search(r"Maximum memory used \(kb\):\s*([\d.]+)", text)
    f["max_memory_kb"] = float(m.group(1)) if m else None
    m = re.search(r"running\s+(\d+)\s+mpi-ranks", text) or re.search(r"running on\s+(\d+)\s+total cores", text)
    f["cores"] = int(m.group(1)) if m else None
    f["vasp_version"] = (re.search(r"(vasp\.[\d.]+)", text) or [None, ""])[1]
    return f


def scf_steps(oszicar: str) -> int:
    return sum(1 for ln in oszicar.splitlines() if re.match(r"^\s*(DAV|RMM|CG|SDA|DIA|RMMP):", ln))


def qc_run(run: Path) -> dict:
    slab = load("run_joint_slab", REPO / "analysis/qoac_hb_slab_20261007/run_joint_slab.py")
    from pymatgen.core import Element
    rec: dict = {"material_id": run.name}
    out = gzip.decompress((run / "OUTCAR.gz").read_bytes()).decode("utf-8", "replace")
    osz = gzip.decompress((run / "OSZICAR.gz").read_bytes()).decode("utf-8", "replace")
    oc = outcar_facts(out)
    rec |= {k: oc[k] for k in ("outcar_ng", "outcar_ngf", "nelect", "converged", "elapsed_s", "max_memory_kb", "cores",
                               "vasp_version")}
    rec["scf_steps"] = scf_steps(osz)
    rec["algo_all_fallback"] = int((run / "OUTCAR_normal.gz").exists())
    sums, grids = {}, {}
    natoms = None
    for name in FILES:
        gz = (run / f"{name}.gz").read_bytes()
        rec[f"{name}_gz_sha256"] = hashlib.sha256(gz).hexdigest()
        raw = gzip.decompress(gz)
        del gz
        rec[f"{name}_sha256"] = hashlib.sha256(raw).hexdigest()
        g, npts, nat, off = split_header(raw)
        grids[name] = g
        natoms = nat
        data = memoryview(raw)[off:]
        rec[f"{name}_grid"] = g
        rec[f"{name}_no_E_tokens"] = len(NO_E_RE.findall(data))
        rec[f"{name}_star_tokens"] = len(STARS_RE.findall(data))
        del data
        try:
            x = slab.parse_vasp_total(raw)
            rec[f"{name}_parsed_shape"] = "x".join(map(str, x.shape))
            rec[f"{name}_nonfinite"] = int(np.count_nonzero(~np.isfinite(x)))
            sums[name] = float(x.sum() / x.size)
            rec[f"{name}_sum_over_n"] = round(sums[name], 6)
            if name == "CHGCAR":
                from pymatgen.io.vasp import Poscar
                head = raw[:off].decode("utf-8", "replace").split("\n")
                st = Poscar.from_str("\n".join(head[: 8 + natoms])).structure
            del x
        except Exception as exc:  # noqa: BLE001
            rec[f"{name}_parse_error"] = f"{type(exc).__name__}:{str(exc)[:160]}"
        del raw
    rec["natoms"] = natoms
    if "CHGCAR_parse_error" not in rec:
        z = [s.specie.Z for s in st]
        rec["sum_Z"] = int(sum(z))
        rec["formula"] = st.composition.reduced_formula
        if oc["zval"] and oc["ions_per_type"] and len(oc["zval"]) == len(oc["ions_per_type"]):
            zval_per_site = [v for v, n in zip(oc["zval"], oc["ions_per_type"]) for _ in range(n)]
            rec["sum_core"] = round(sum(zi - v for zi, v in zip(z, zval_per_site)), 3)
        dims = np.array([int(v) for v in grids["CHGCAR"].split("x")], float)
        gpos = st.frac_coords * dims
        on = np.all(np.abs(gpos - np.round(gpos)) < 1e-4, axis=1)
        rec["n_atoms_on_grid_point"] = int(on.sum())
        rec["elements_on_grid_point"] = " ".join(sorted({s.specie.symbol for s, o in zip(st, on) if o}))
    if {"AECCAR0", "AECCAR2"} <= sums.keys() and rec.get("sum_Z"):
        rec["R_total_over_sumZ"] = round((sums["AECCAR0"] + sums["AECCAR2"]) / rec["sum_Z"], 6)
    if oc["nelect"]:
        for name in ("CHGCAR", "AECCAR2"):
            if name in sums:
                rec[f"{name}_over_nelect"] = round(sums[name] / oc["nelect"], 6)
    if "AECCAR0" in sums and rec.get("sum_core"):
        rec["AECCAR0_over_core"] = round(sums["AECCAR0"] / rec["sum_core"], 6)

    reason = ""
    if not rec["converged"]:
        reason = "not_converged"
    elif len(set(grids.values())) != 1 or grids["CHGCAR"] != rec["outcar_ngf"]:
        reason = "grid_mismatch"
    elif any(rec[f"{n}_no_E_tokens"] or rec[f"{n}_star_tokens"] for n in FILES):
        reason = "no_E_or_star_tokens"
    elif any(f"{n}_parse_error" in rec for n in FILES):
        reason = "parse_error"
    elif any(rec[f"{n}_parsed_shape"] != grids[n] for n in FILES):
        reason = "parsed_shape_mismatch"
    elif any(rec[f"{n}_nonfinite"] for n in FILES):
        reason = "nonfinite"
    elif not (R_MIN <= rec.get("R_total_over_sumZ", -1) <= R_MAX):
        reason = "electron_count_out_of_window"
    rec["qc_reason"] = reason
    rec["qc_pass"] = int(reason == "")
    return rec


COLS = ["material_id", "formula", "natoms", "qc_pass", "qc_reason", "converged", "algo_all_fallback", "scf_steps",
        "elapsed_s", "max_memory_kb", "cores", "vasp_version", "outcar_ng", "outcar_ngf", "CHGCAR_grid", "AECCAR0_grid",
        "AECCAR2_grid", "CHGCAR_parsed_shape", "AECCAR0_parsed_shape", "AECCAR2_parsed_shape", "CHGCAR_nonfinite",
        "AECCAR0_nonfinite", "AECCAR2_nonfinite", "CHGCAR_no_E_tokens", "AECCAR0_no_E_tokens", "AECCAR2_no_E_tokens",
        "CHGCAR_star_tokens", "AECCAR0_star_tokens", "AECCAR2_star_tokens", "nelect", "sum_Z", "sum_core",
        "CHGCAR_sum_over_n", "AECCAR0_sum_over_n", "AECCAR2_sum_over_n", "R_total_over_sumZ", "CHGCAR_over_nelect",
        "AECCAR2_over_nelect", "AECCAR0_over_core", "n_atoms_on_grid_point", "elements_on_grid_point",
        "CHGCAR_sha256", "AECCAR0_sha256", "AECCAR2_sha256", "CHGCAR_gz_sha256", "AECCAR0_gz_sha256",
        "AECCAR2_gz_sha256", "CHGCAR_parse_error", "AECCAR0_parse_error", "AECCAR2_parse_error"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path, help="run directories (named by material_id)")
    ap.add_argument("--out", type=Path, required=True, help="CSV to write (rows replaced by material_id)")
    a = ap.parse_args(argv)
    rows = {}
    if a.out.exists():
        rows = {r["material_id"]: r for r in csv.DictReader(open(a.out, encoding="utf-8"))}
    for run in a.runs:
        rec = qc_run(run)
        print(json.dumps({k: rec.get(k) for k in ("material_id", "qc_pass", "qc_reason", "R_total_over_sumZ",
                                                  "CHGCAR_grid", "scf_steps")}), flush=True)
        rows[rec["material_id"]] = rec
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for k in sorted(rows):
            w.writerow({c: rows[k].get(c, "") for c in COLS})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
