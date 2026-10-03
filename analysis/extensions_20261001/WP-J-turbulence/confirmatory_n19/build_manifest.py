#!/usr/bin/env python3
"""Build the second confirmatory JHTDB manifest, excluding pilot and first-confirmation keys."""
from __future__ import annotations
import csv, hashlib, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
N = 64; SIDE = 15; GRID = 1024; NFRAME = 5028; DT = 0.002; DX = 2 * math.pi / GRID


def u64(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8], "little")


used = set()
for manifest in (PARENT / "sample_manifest.csv", PARENT / "confirmatory" / "sample_manifest.csv"):
    with manifest.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            used.add((int(r["frame_index"]), int(r["x0_index"]), int(r["y0_index"]), int(r["z0_index"])))
prior = set(used)

rows = []
for i in range(N):
    salt = 0
    while True:
        base = f"QSQ-JHTDB-CONFIRM2-20261003|{i:03d}|{salt}"
        frame = u64(base + "|t") % NFRAME
        lim = GRID - SIDE + 1
        x0 = u64(base + "|x") % lim; y0 = u64(base + "|y") % lim; z0 = u64(base + "|z") % lim
        key = (frame, x0, y0, z0)
        if key not in used:
            used.add(key); break
        salt += 1
    rows.append({
        "sample_id": f"jhtdb_conf2_{i:03d}", "dataset": "isotropic1024coarse",
        "frame_index": frame, "time": f"{frame * DT:.6f}",
        "x0_index": x0, "y0_index": y0, "z0_index": z0,
        "side": SIDE, "n_points": SIDE ** 3, "dx": f"{DX:.17g}",
        "sampling_hash": hashlib.sha256(base.encode()).hexdigest(),
    })
with (HERE / "sample_manifest.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
overlap = sum((int(r["frame_index"]), int(r["x0_index"]), int(r["y0_index"]), int(r["z0_index"])) in prior for r in rows)
print("rows", len(rows), "overlap with prior cohorts", overlap)
