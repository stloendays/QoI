#!/usr/bin/env python3
"""Run qc_run.qc_run (unchanged) on several run directories with a small process pool and merge the rows into one CSV.
Usage: qc_parallel.py --out qc/qc.csv --workers 3 <run-dir> [<run-dir> ...]"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import multiprocessing as mp
import sys
import warnings
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location("qc_run", HERE / "qc_run.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["qc_run"] = mod
    spec.loader.exec_module(mod)
    return mod


def one(run: str) -> dict:
    warnings.filterwarnings("ignore")
    return _load().qc_run(Path(run))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    qc = _load()
    rows = {}
    if a.out.exists():
        rows = {r["material_id"]: r for r in csv.DictReader(open(a.out, encoding="utf-8"))}
    with mp.Pool(min(a.workers, 8)) as pool:
        for rec in pool.imap_unordered(one, a.runs):
            rows[rec["material_id"]] = rec
            print(rec["material_id"], rec["qc_pass"], rec["qc_reason"], rec.get("R_total_over_sumZ"), flush=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=qc.COLS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for k in sorted(rows):
            w.writerow({c: rows[k].get(c, "") for c in qc.COLS})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
