#!/usr/bin/env python3
"""Diagnose the four AECCAR reference-loading failures of the QOAC-HB slab run (diagnostic only).

For each of the 8 files (AECCAR0 and AECCAR2 of the 4 failed entries) this script
- downloads it from the NOMAD raw directory (unless already in --data-dir) and checks byte count and SHA-256 against
  the frozen `analysis/qoac_hb_slab_20261007/aeccar_sources.csv`;
- reads the header (species, counts, grid) and scans every token of the volumetric data with a strict tokenizer:
  values parsed against the grid size, non-finite / NaN / zero counts, min and max, Fortran exponents written without
  `E` (`0.123-100`), `*****` overflow and any other malformed token, augmentation-occupancy lines and extra
  (spin) blocks after the first grid;
- records what baderkit `Grid.from_dynamic` (the HB slab adapter's parser) and pymatgen `Chgcar.from_file` return;
- for the entries whose AECCAR files parse, compares the parsers' arrays with the strict scan.

The raw files are not kept in the repository. Outputs (small CSV/JSON tables) go to --out-dir.

Usage: diagnose_aeccar.py --data-dir <scratch dir> [--out-dir <dir>] [--entries id ...]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import re
import sys
import tempfile
import time
import traceback
import urllib.request
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCES = REPO / "analysis" / "qoac_hb_slab_20261007" / "aeccar_sources.csv"
NOMAD_RAW = "https://nomad-lab.eu/prod/v1/api/v1/entries/{entry}/raw/{name}"
FAILED = ("IZPVe_A6_quStfuserAGgimQ2c0K", "ViaCyatoI3FA6DXSI94n9SRDzdCi", "DcwYU1UzKNe8U2KmsnBaea6HcEIN",
          "hk3gUBk-5QN5DgoiFUWeMkmDpI9m")
CONTROLS = ("gPlluuEHW2NDKnVMBb-68W6rK_Wn",)   # analysed and jointly certified in the slab run (AECCARs load)

FLOAT_RE = re.compile(rb"[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[EeDd][+-]?\d+)?")
NAN_RE = re.compile(rb"[+-]?nan", re.I)
INF_RE = re.compile(rb"[+-]?inf(?:inity)?", re.I)
NOE_RE = re.compile(rb"[+-]?(?:\d+\.\d*|\.\d+)[+-]\d{2,3}")   # Fortran E-format with exponent >= 100: E dropped
OVF_RE = re.compile(rb"\*+")
AUG_RE = re.compile(rb"augmentation occupancies", re.I)


def fetch(url: str) -> bytes:
    err = None
    for k in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "QoI-HB-slab-AECCAR-diagnosis/1.0"})
            with urllib.request.urlopen(req, timeout=900) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"download failed: {err}")


def classify(tok: bytes) -> str:
    if FLOAT_RE.fullmatch(tok):
        return "float"
    if NAN_RE.fullmatch(tok):
        return "nan"
    if INF_RE.fullmatch(tok):
        return "inf"
    if NOE_RE.fullmatch(tok):
        return "fortran_no_E"
    if OVF_RE.fullmatch(tok):
        return "overflow_stars"
    return "other"


def fortran_value(tok: bytes) -> float:
    """Value of a Fortran E-format token whose 'E' was dropped (mantissa followed by a signed 3-digit exponent)."""
    s = tok.decode()
    m = re.fullmatch(r"([+-]?(?:\d+\.\d*|\.\d+))([+-]\d{2,3})", s)
    return float(m.group(1) + "E" + m.group(2))


def strict_scan(raw: bytes) -> dict:
    """Header and token-level scan of a VASP volumetric file (first block = the 'total' grid)."""
    lines = raw.split(b"\n")
    species = lines[5].split()
    if all(re.fullmatch(rb"\d+", s) for s in species):     # VASP4 file without species line
        counts, species, hdr = [int(s) for s in species], [], 6
    else:
        counts, hdr = [int(s) for s in lines[6].split()], 7
    natoms = sum(counts)
    i = hdr + 1 + natoms            # coordinate-system line, then natoms coordinate lines
    while lines[i].strip() == b"":
        i += 1
    grid_line = lines[i].strip()
    nx, ny, nz = (int(x) for x in grid_line.split())
    n = nx * ny * nz
    first_data_line = i + 1

    vals = np.empty(n, dtype=np.float64)
    kinds = {"float": 0, "nan": 0, "inf": 0, "fortran_no_E": 0, "overflow_stars": 0, "other": 0}
    examples: dict[str, list] = {k: [] for k in kinds}
    widths: dict[int, int] = {}
    count = 0
    exp_rng = (10**9, -10**9)
    j = first_data_line
    while count < n and j < len(lines):
        line = lines[j]
        toks = line.split()
        if toks:
            widths[len(line.rstrip(b"\r"))] = widths.get(len(line.rstrip(b"\r")), 0) + 1
        for t in toks:
            if count >= n:
                break
            k = classify(t)
            kinds[k] += 1
            if k != "float" and len(examples[k]) < 5:
                examples[k].append({"line": j + 1, "token": t.decode("latin1")})
            if k in ("float", "nan", "inf"):
                vals[count] = float(t.replace(b"D", b"E").replace(b"d", b"e"))
            elif k == "fortran_no_E":
                vals[count] = fortran_value(t)
                ex = int(t[-4:]) if t[-4:-3] in (b"+", b"-") else int(t[-3:])
                exp_rng = (min(exp_rng[0], ex), max(exp_rng[1], ex))
            else:
                vals[count] = np.nan
            count += 1
        j += 1
    last_data_line = j            # 0-based index of the first line after the first block
    vals = vals[:count]

    # After the first block: augmentation occupancies, repeated grid lines (extra blocks), other lines.
    aug_lines = 0
    grid_repeats = 0
    trailing_numeric_tokens = 0
    trailing_other_lines = 0
    for line in lines[last_data_line:]:
        s = line.strip()
        if not s:
            continue
        if AUG_RE.search(s):
            aug_lines += 1
        elif s == grid_line:
            grid_repeats += 1
        elif all(classify(t) in ("float", "nan", "inf", "fortran_no_E") for t in s.split()):
            trailing_numeric_tokens += len(s.split())
        else:
            trailing_other_lines += 1

    finite = np.isfinite(vals)
    out = {
        "species": " ".join(x.decode() for x in species), "counts": " ".join(map(str, counts)), "natoms": natoms,
        "header_grid": f"{nx}x{ny}x{nz}", "n_grid": n, "n_values_parsed_block1": int(count),
        "n_values_equals_grid": int(count == n),
        "n_float": kinds["float"], "n_nan": kinds["nan"], "n_inf": kinds["inf"],
        "n_fortran_no_E": kinds["fortran_no_E"],
        "fortran_no_E_exponent_range": f"{exp_rng[0]}..{exp_rng[1]}" if kinds["fortran_no_E"] else "",
        "n_overflow_stars": kinds["overflow_stars"], "n_other_malformed": kinds["other"],
        "n_nonfinite": int((~finite).sum()), "frac_nonfinite": float((~finite).mean()) if count else math.nan,
        "n_zero": int((vals == 0).sum()), "n_negative": int((vals[finite] < 0).sum()),
        "n_abs_gt_1e100": int((np.abs(vals[finite]) > 1e100).sum()),
        "min_abs_nonzero_finite": (float(np.abs(vals[finite & (vals != 0)]).min())
                                   if (finite & (vals != 0)).any() else math.nan),
        "min_finite": float(vals[finite].min()) if finite.any() else math.nan,
        "max_finite": float(vals[finite].max()) if finite.any() else math.nan,
        "sum_over_n_finite": float(vals[finite].sum() / n) if finite.any() else math.nan,
        "first_nonfinite_index": int(np.argmax(~finite)) if (~finite).any() else -1,
        "last_nonfinite_index": int(n - 1 - np.argmax((~finite)[::-1])) if (~finite).any() else -1,
        "data_line_widths": ";".join(f"{w}:{c}" for w, c in sorted(widths.items())),
        "augmentation_occupancy_lines": aug_lines, "extra_grid_blocks": grid_repeats,
        "trailing_numeric_tokens": trailing_numeric_tokens, "trailing_other_lines": trailing_other_lines,
        "malformed_examples": json.dumps({k: v for k, v in examples.items() if v}),
    }
    return out, vals.reshape((nx, ny, nz), order="F") if count == n else None


def summarize_array(arr) -> dict:
    a = np.asarray(arr, dtype=np.float64)
    fin = np.isfinite(a)
    return {"shape": "x".join(map(str, a.shape)), "n_nonfinite": int((~fin).sum()),
            "min_finite": float(a[fin].min()) if fin.any() else math.nan,
            "max_finite": float(a[fin].max()) if fin.any() else math.nan}


def run_baderkit(path: Path) -> tuple[dict, np.ndarray | None]:
    from baderkit import Grid
    import warnings
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            g = Grid.from_dynamic(path)
            arr = np.array(g.total, dtype=np.float64, copy=True)
        del g
        warn = "; ".join(sorted({f"{x.category.__name__}: {x.message}"[:160] for x in w}))
        return {"status": "returned", **summarize_array(arr), "warnings": warn, "error": ""}, arr
    except Exception as exc:  # noqa: BLE001
        return {"status": "raised", "shape": "", "n_nonfinite": "", "min_finite": "", "max_finite": "",
                "warnings": "", "error": f"{type(exc).__name__}: {exc}"[:300]}, None


def run_pymatgen(path: Path) -> tuple[dict, np.ndarray | None]:
    from pymatgen.io.vasp.outputs import Chgcar
    try:
        c = Chgcar.from_file(str(path))
        arr = np.asarray(c.data["total"], dtype=np.float64)
        return {"status": "returned", **summarize_array(arr), "warnings": "", "error": ""}, arr
    except Exception as exc:  # noqa: BLE001
        return {"status": "raised", "shape": "", "n_nonfinite": "", "min_finite": "", "max_finite": "",
                "warnings": "", "error": f"{type(exc).__name__}: {exc}"[:300]}, None


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=HERE)
    p.add_argument("--entries", nargs="*", default=list(FAILED))
    p.add_argument("--controls", nargs="*", default=list(CONTROLS),
                   help="entries analysed successfully in the slab run, scanned the same way for comparison")
    a = p.parse_args(argv)
    with open(SOURCES, encoding="utf-8") as f:
        table = {r["entry_id"]: r for r in csv.DictReader(f)}
    files_rows, loader_rows = [], []
    for e in list(a.entries) + list(a.controls):
        row = table[e]
        role = "control" if e in a.controls else "failed"
        for k in "02":
            name = Path(row[f"aeccar{k}_path"]).name
            local = a.data_dir / e / name
            if not local.exists():
                local.parent.mkdir(parents=True, exist_ok=True)
                local.write_bytes(fetch(NOMAD_RAW.format(entry=e, name=name)))
            blob = local.read_bytes()
            sha = hashlib.sha256(blob).hexdigest()
            raw = gzip.decompress(blob) if name.endswith(".gz") else blob
            info, strict = strict_scan(raw)
            base = {"material_id": row["material_id"], "entry_id": e, "role": role, "file": f"AECCAR{k}", "name": name,
                    "bytes": len(blob), "sha256": sha,
                    "sha256_matches_frozen_listing": int(sha == row[f"aeccar{k}_sha256"] and len(blob) == int(row[f"aeccar{k}_bytes"])),
                    "decompressed_bytes": len(raw), "chgcar_grid": row["chgcar_ngrid"]}
            files_rows.append({**base, **info})
            with tempfile.TemporaryDirectory(prefix="aeccar_diag_", ignore_cleanup_errors=True) as td:
                fp = Path(td) / "AECCAR"
                fp.write_bytes(raw)
                for loader, fn in (("baderkit Grid.from_dynamic", run_baderkit), ("pymatgen Chgcar.from_file", run_pymatgen)):
                    res, arr = fn(fp)
                    if arr is not None and strict is not None and arr.shape == strict.shape:
                        same_nan = np.array_equal(np.isnan(arr), np.isnan(strict))
                        fin = np.isfinite(arr) & np.isfinite(strict)
                        dmax = float(np.max(np.abs(arr[fin] - strict[fin]))) if fin.any() else math.nan
                        res["matches_strict_scan"] = int(same_nan and (dmax == 0.0 or not fin.any()))
                        res["max_abs_diff_vs_strict"] = dmax
                    else:
                        res["matches_strict_scan"] = ""
                        res["max_abs_diff_vs_strict"] = ""
                    loader_rows.append({"material_id": row["material_id"], "entry_id": e, "role": role, "file": f"AECCAR{k}",
                                        "loader": loader, **res})
                    print(f"{e} AECCAR{k} {loader}: {res['status']} {res.get('shape')} {res.get('error')}", flush=True)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    for fname, rows in (("aeccar_file_scan.csv", files_rows), ("aeccar_loader_results.csv", loader_rows)):
        with open(a.out_dir / fname, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    import baderkit, pymatgen.core  # noqa: E401
    from importlib.metadata import version
    env = {"python": sys.version.split()[0], "numpy": np.__version__, "baderkit": version("baderkit"),
           "pymatgen": version("pymatgen")}
    (a.out_dir / "diagnosis_environment.json").write_text(json.dumps(env, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
