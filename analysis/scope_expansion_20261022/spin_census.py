#!/usr/bin/env python3
"""WS-S S0: census of the magnetization (spin-difference) block in MP CHGCARs.

For each Materials Project object in the input manifests (development panel MP
rows + P1/P2 engineering sets; no confirmation set is read), download the
parsed CHGCAR JSON, verify sha256 / byte count against the manifest, and record:

* whether ``data.data.diff`` is present (spin-polarized calculation);
* total magnetization M = mean(m) and absolute magnetization mean(|m|)
  (CHGCAR units: the cell mean of a block equals its integral, i.e. mu_B per cell);
* max|m| / max|rho| and ptp(m) / ptp(rho);
* descriptive per-atom moments from an on-grid partition of the *total*
  density (vectorized Henkelman on-grid transcription from QOAC-B3, -vac 1e-3):
  max |mu_atom| and the number of atoms with |mu_atom| >= 0.1 mu_B.

Descriptive only. No compression, no tolerance, no gate.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
import time
import traceback
import urllib.request
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "analysis" / "qoac_b3_design"))

FIELDS = ["material_id", "source_manifest", "status", "error", "has_diff", "shape", "npoints", "natoms",
          "formula", "source_bytes", "nelect", "M_total_muB", "M_abs_muB", "maxabs_m_over_maxabs_rho",
          "ptp_m_over_ptp_rho", "max_abs_atom_moment_muB", "atoms_moment_ge_0p1", "partition_seconds",
          "wall_seconds"]


def fetch(url: str, tries: int = 4) -> bytes:
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"download failed: {last}")


def decode(blob: bytes) -> dict:
    doc = json.loads(gzip.decompress(blob).decode("utf-8"))
    data = doc["data"] if "data" in doc and "poscar" not in doc else doc
    st = data["poscar"]["structure"] if "structure" in data["poscar"] else data["poscar"]
    blocks = data["data"]
    total = np.array(blocks["total"]["data"], dtype=np.float64)
    diff = blocks.get("diff")
    m = None
    if diff is not None:
        arr = diff["data"] if isinstance(diff, dict) and "data" in diff else diff
        m = np.array(arr, dtype=np.float64)
        if m.shape != total.shape:
            raise RuntimeError(f"diff shape {m.shape} != total {total.shape}")
    lattice = np.array(st["lattice"]["matrix"], dtype=np.float64)
    frac = np.array([s["abc"] for s in st["sites"]], dtype=np.float64)
    return {"total": total, "m": m, "lattice": lattice, "frac": frac,
            "symbols": [s["species"][0]["element"] for s in st["sites"]]}


def census_one(row: dict, manifest_name: str) -> dict:
    t0 = time.time()
    out = {"material_id": row["material_id"], "source_manifest": manifest_name, "status": "OK", "error": ""}
    try:
        blob = fetch(row["url"])
        if row.get("sha256") and hashlib.sha256(blob).hexdigest() != row["sha256"]:
            raise RuntimeError("sha256 mismatch against manifest")
        d = decode(blob)
        rho, m = d["total"], d["m"]
        out.update(has_diff=m is not None, shape="x".join(map(str, rho.shape)), npoints=int(rho.size),
                   natoms=len(d["symbols"]), formula=row.get("formula", ""), source_bytes=len(blob),
                   nelect=float(rho.mean()))
        if m is not None:
            out.update(M_total_muB=float(m.mean()), M_abs_muB=float(np.abs(m).mean()),
                       maxabs_m_over_maxabs_rho=float(np.abs(m).max() / max(np.abs(rho).max(), 1e-300)),
                       ptp_m_over_ptp_rho=float(np.ptp(m) / max(np.ptp(rho), 1e-300)))
            if np.abs(m).max() > 0:
                from ongrid import atom_map, ongrid_partition
                t = time.perf_counter()
                part = ongrid_partition(rho, d["lattice"], 1e-3)
                amap = atom_map(part, d["lattice"], d["frac"]).ravel()
                n = len(d["symbols"])
                mu = np.bincount(amap, weights=m.ravel(), minlength=n + 2)[1:n + 1] / m.size
                out.update(max_abs_atom_moment_muB=float(np.abs(mu).max()),
                           atoms_moment_ge_0p1=int(np.sum(np.abs(mu) >= 0.1)),
                           partition_seconds=time.perf_counter() - t)
    except Exception as e:  # noqa: BLE001
        out.update(status="FAILED", error=f"{type(e).__name__}: {e}")
        print(traceback.format_exc(), file=sys.stderr)
    out["wall_seconds"] = time.time() - t0
    return out


def load_rows(manifests: list[Path]) -> list[tuple[dict, str]]:
    rows = []
    for p in manifests:
        for r in csv.DictReader(p.read_text(encoding="utf-8").splitlines()):
            if r["material_id"].startswith("mp-") and r.get("url", "").startswith("https://materialsproject"):
                rows.append((r, p.name))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("count")
    c.add_argument("--manifest", type=Path, action="append", required=True)
    r = sub.add_parser("run")
    r.add_argument("--manifest", type=Path, action="append", required=True)
    r.add_argument("--shard", type=int, required=True)
    r.add_argument("--nshards", type=int, required=True)
    r.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--inputs", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "count":
        print(len(load_rows(args.manifest)))
        return 0
    if args.cmd == "run":
        rows = load_rows(args.manifest)[args.shard::args.nshards]
        res = []
        for row, name in rows:
            rec = census_one(row, name)
            print("SPIN_CENSUS", rec["material_id"], rec["status"], rec.get("has_diff"), flush=True)
            res.append(rec)
        args.out.mkdir(parents=True, exist_ok=True)
        write(res, args.out / f"census_shard{args.shard:02d}.csv")
        return 0
    res = []
    for p in sorted(args.inputs.rglob("census_shard*.csv")):
        res.extend(csv.DictReader(p.read_text(encoding="utf-8").splitlines()))
    args.out.mkdir(parents=True, exist_ok=True)
    res.sort(key=lambda r: (r["source_manifest"], r["material_id"]))
    write(res, args.out / "census.csv")
    summary = summarize(res)
    (args.out / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0


def write(rows, path: Path):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def summarize(rows) -> dict:
    ok = [r for r in rows if r["status"] == "OK"]
    spin = [r for r in ok if str(r["has_diff"]) == "True"]
    mag = [r for r in spin if (_f(r.get("max_abs_atom_moment_muB")) or 0) >= 0.1]
    by = {}
    for r in ok:
        b = by.setdefault(r["source_manifest"], {"ok": 0, "spin": 0, "moment_ge_0p1": 0})
        b["ok"] += 1
        b["spin"] += int(r in spin)
        b["moment_ge_0p1"] += int(r in mag)
    return {"objects": len(rows), "ok": len(ok), "failed": len(rows) - len(ok),
            "spin_polarized": len(spin), "with_atom_moment_ge_0p1_muB": len(mag),
            "by_manifest": by,
            "median_M_abs_muB_spin": float(np.median([_f(r["M_abs_muB"]) for r in spin])) if spin else None,
            "spin_byte_share_note": "raw float64 payload doubles when diff is present; lossless shares not measured here"}


if __name__ == "__main__":
    raise SystemExit(main())
