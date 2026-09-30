#!/usr/bin/env python3
"""WP-F sample: 300 MP charge-density objects, stratified by stored size (PROTOCOL.md, WP-F).

Frame: frame.csv without the 186 objects of the frozen study. Strata: size deciles 1-9 of the
frame (30 objects each) and the top decile split at 80 MB and 150 MB (15 / 10 / 5 objects).
Within a stratum, objects are ordered by SHA-256("QSQ-WPF-20260930|" + task_id) and the first
n_h are taken. Nothing but key names and byte sizes is used.

    python draw_sample.py   -> sample.csv, strata.csv, frame.csv.gz
"""
import csv
import gzip
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SALT = "QSQ-WPF-20260930|"
ALLOC_DECILES = 30
TOP_SPLIT = ((80e6, 15), (150e6, 10), (float("inf"), 5))      # (upper edge in bytes, n) inside the top decile


def main():
    rows = [r for r in csv.DictReader(open(HERE / "frame.csv", encoding="utf-8")) if r["in_frozen_study"] == "0"]
    b = np.array([int(r["bytes"]) for r in rows], dtype=np.int64)
    edges = np.quantile(b, np.linspace(0, 1, 11))
    dec = np.clip(np.searchsorted(edges[1:-1], b, side="right"), 0, 9)        # 0..9
    strata, sample = [], []
    for r, d in zip(rows, dec):
        r["decile"] = int(d) + 1
    for d in range(1, 11):
        members = [r for r in rows if r["decile"] == d]
        if d < 10:
            groups = [("D%02d" % d, members, ALLOC_DECILES)]
        else:
            groups, lo = [], edges[-2]
            for k, (hi, n) in enumerate(TOP_SPLIT):
                groups.append(("D10%s" % "abc"[k], [r for r in members if lo <= int(r["bytes"]) < hi or (hi == float("inf") and int(r["bytes"]) >= lo)], n))
                lo = hi
        for name, mem, n in groups:
            mem = sorted(mem, key=lambda r: hashlib.sha256((SALT + r["task_id"]).encode()).hexdigest())
            pick = mem[:n]
            tot = sum(int(r["bytes"]) for r in mem)
            strata.append(dict(stratum=name, N_frame=len(mem), n_sample=len(pick), bytes_total=tot,
                               bytes_min=min(int(r["bytes"]) for r in mem), bytes_max=max(int(r["bytes"]) for r in mem)))
            for i, r in enumerate(pick):
                sample.append(dict(stratum=name, rank_in_stratum=i, task_id=r["task_id"], key=r["key"], bytes=r["bytes"],
                                   url="https://materialsproject-parsed.s3.amazonaws.com/" + r["key"]))
    assert sum(s["N_frame"] for s in strata) == len(rows) and len(sample) == 300
    for name, data in (("strata.csv", strata), ("sample.csv", sample)):
        with open(HERE / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    with open(HERE / "frame.csv", "rb") as src, gzip.open(HERE / "frame.csv.gz", "wb", compresslevel=9) as dst:
        shutil.copyfileobj(src, dst)
    print(json.dumps(dict(frame=len(rows), strata=len(strata), sample=len(sample),
                          decile_edges_MB=[round(e / 1e6, 2) for e in edges],
                          sample_sha256=hashlib.sha256((HERE / "sample.csv").read_bytes()).hexdigest()), indent=1))


if __name__ == "__main__":
    main()
