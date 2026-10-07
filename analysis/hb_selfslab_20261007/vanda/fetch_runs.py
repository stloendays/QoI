#!/usr/bin/env python3
"""Copy finished runs back from Vanda, gzipped, and verify them against sha256sum on the server (PROTOCOL.md section 8).

For each run directory <draw_rank>_<material_id> given: read STATUS and `sha256sum` of CHGCAR, AECCAR0, AECCAR2, OUTCAR,
OSZICAR (plus OUTCAR_normal and OSZICAR_normal when the ALGO = All fallback ran) on the server; stream `gzip -c` of
each file to D:/Research/QoI-ext-cache/selfslab/runs/<material_id>/<name>.gz; decompress locally and compare the
SHA-256 with the server's. Appends/replaces rows of runs/fetch.csv (material, file, bytes, server and local SHA-256,
gz SHA-256, match). Only `ssh vanda` is used.

Usage: fetch_runs.py <dir> [<dir> ...]
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REMOTE = "/scratch/junbotong/qoi_selfslab_20261007/runs"
LOCAL = Path(r"D:\Research\QoI-ext-cache\selfslab\runs")
BASE = ["CHGCAR", "AECCAR0", "AECCAR2", "OUTCAR", "OSZICAR"]


def ssh(cmd: str) -> bytes:
    p = subprocess.run(["ssh", "-o", "BatchMode=yes", "vanda", cmd], capture_output=True, timeout=3600)
    if p.returncode != 0:
        raise RuntimeError(f"ssh failed ({p.returncode}): {p.stderr.decode(errors='replace')[-400:]}")
    return p.stdout


def fetch(d: str) -> list[dict]:
    mid = d.split("_", 1)[1]
    status = ssh(f"cat {REMOTE}/{d}/STATUS").decode().strip()
    names = list(BASE)
    if status in ("converged_all", "nelm_twice"):
        names += ["OUTCAR_normal", "OSZICAR_normal"]
    if not status.startswith("converged"):
        names = [n for n in names if n.startswith(("OUTCAR", "OSZICAR"))]
    sums = {}
    for line in ssh(f"cd {REMOTE}/{d} && sha256sum {' '.join(names)} && stat -c '%n %s' {' '.join(names)}").decode().splitlines():
        parts = line.split()
        if len(parts) == 2 and len(parts[0]) == 64:
            sums.setdefault(parts[1], {})["server_sha256"] = parts[0]
        elif len(parts) == 2:
            sums.setdefault(parts[0], {})["bytes"] = int(parts[1])
    out = LOCAL / mid
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for n in names:
        gz = ssh(f"gzip -c {REMOTE}/{d}/{n}")
        (out / f"{n}.gz").write_bytes(gz)
        raw = gzip.decompress(gz)
        local = hashlib.sha256(raw).hexdigest()
        rows.append({"material_id": mid, "dir": d, "status": status, "file": n, "bytes": sums[n]["bytes"],
                     "local_bytes": len(raw), "server_sha256": sums[n]["server_sha256"], "local_sha256": local,
                     "gz_sha256": hashlib.sha256(gz).hexdigest(), "gz_bytes": len(gz),
                     "match": int(local == sums[n]["server_sha256"] and len(raw) == sums[n]["bytes"])})
        del gz, raw
        print(rows[-1]["file"], rows[-1]["bytes"], rows[-1]["match"], flush=True)
    return rows


def main(argv=None) -> int:
    dirs = (argv or sys.argv[1:])
    path = ROOT / "runs" / "fetch.csv"
    rows = {}
    if path.exists():
        rows = {(r["material_id"], r["file"]): r for r in csv.DictReader(open(path, encoding="utf-8"))}
    for d in dirs:
        for r in fetch(d):
            rows[(r["material_id"], r["file"])] = r
    path.parent.mkdir(exist_ok=True)
    cols = ["material_id", "dir", "status", "file", "bytes", "local_bytes", "server_sha256", "local_sha256", "gz_sha256",
            "gz_bytes", "match"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for k in sorted(rows):
            w.writerow({c: rows[k][c] for c in cols})
    bad = [k for k, r in rows.items() if str(r["match"]) != "1"]
    print(f"{len(rows)} files recorded, {len(bad)} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
