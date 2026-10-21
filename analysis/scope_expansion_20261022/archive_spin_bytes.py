#!/usr/bin/env python3
"""WS-S S0b: how much of the Materials Project archive is the magnetization block?

The archive estimates (WP-F, Bader contract; archive-Hartree-law, Hartree contract)
store only the ``total`` block of each object, but compare against the full
gzipped JSON, which also carries the magnetization block ``diff`` (S0 found it
in 210/210 sampled MP objects). This script measures, for the same stratified
sample of 300 objects:

* gz bytes of the JSON-serialized total, diff and data_aug blocks (gzip level 6,
  same serializer for all three), hence the diff share of the stored text;
* zlib-6 bytes of the float64 diff array (the WP-F lossless rule) and of the total;
* simple magnetization statistics.

``aggregate`` then recomputes the published archive ratios with the frozen
stratified expansion estimator and two sensitivity variants:

  R_current      = T_json / T_stored                         (as published)
  R_block        = T_json * (1 - diff_share) / T_stored      (charge-density block only)
  R_with_m       = T_json / (T_stored + T_lossless_diff)     (magnetization kept losslessly)

Descriptive sensitivity analysis; nothing here changes a frozen result.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
import time
import traceback
import urllib.request
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N_FRAME = {"D01": 41527, "D02": 41531, "D03": 41529, "D04": 41529, "D05": 41528, "D06": 41529,
           "D07": 41529, "D08": 41529, "D09": 41529, "D10a": 33105, "D10b": 6741, "D10c": 1683}
FIELDS = ["task_id", "stratum", "status", "error", "frame_bytes", "downloaded_bytes", "has_diff", "npoints",
          "gz_total_block", "gz_diff_block", "gz_aug_block", "diff_share_text", "lossless_total", "lossless_diff",
          "M_abs_muB", "maxabs_m_over_maxabs_rho", "wall_seconds"]


def fetch(url: str, tries: int = 4) -> bytes:
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=600) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(10 * (k + 1))
    raise RuntimeError(f"download failed: {last}")


def gz_len(obj) -> int:
    if obj is None:
        return 0
    return len(gzip.compress(json.dumps(obj, separators=(",", ":")).encode("utf-8"), 6))


def measure(row: dict) -> dict:
    t0 = time.time()
    out = {"task_id": row["task_id"], "stratum": row["stratum"], "frame_bytes": int(row["frame_bytes"]),
           "status": "OK", "error": ""}
    try:
        blob = fetch(row["url"])
        out["downloaded_bytes"] = len(blob)
        doc = json.loads(gzip.decompress(blob).decode("utf-8"))
        del blob
        data = doc["data"] if "data" in doc and "poscar" not in doc else doc
        blocks = data["data"]
        tot, diff = blocks.get("total"), blocks.get("diff")
        out["has_diff"] = diff is not None
        out["gz_total_block"] = gz_len(tot)
        out["gz_diff_block"] = gz_len(diff)
        out["gz_aug_block"] = gz_len(data.get("data_aug"))
        denom = out["gz_total_block"] + out["gz_diff_block"] + out["gz_aug_block"]
        out["diff_share_text"] = out["gz_diff_block"] / denom if denom else 0.0
        t = np.asarray(tot["data"] if isinstance(tot, dict) else tot, dtype=np.float64)
        out["npoints"] = int(t.size)
        out["lossless_total"] = len(zlib.compress(np.ascontiguousarray(t).tobytes(), 6))
        if diff is not None:
            m = np.asarray(diff["data"] if isinstance(diff, dict) else diff, dtype=np.float64)
            out["lossless_diff"] = len(zlib.compress(np.ascontiguousarray(m).tobytes(), 6))
            out["M_abs_muB"] = float(np.abs(m).mean())
            out["maxabs_m_over_maxabs_rho"] = float(np.abs(m).max() / max(np.abs(t).max(), 1e-300))
        else:
            out["lossless_diff"] = 0
    except Exception as e:  # noqa: BLE001
        out.update(status="FAILED", error=f"{type(e).__name__}: {e}")
        print(traceback.format_exc(), file=sys.stderr)
    out["wall_seconds"] = time.time() - t0
    return out


def write(rows, path: Path):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


# --------------------------------------------------------------------------
# Aggregate: stratified expansion estimator, as in the frozen WP-F protocol
# --------------------------------------------------------------------------

def strat_total(strata: np.ndarray, x: np.ndarray, idx_by_h: dict) -> float:
    return sum(N_FRAME[h] / len(ix) * x[ix].sum() for h, ix in idx_by_h.items())


def ratios(json_b, stored, share, lossless_m, idx_by_h):
    tj = strat_total(None, json_b, idx_by_h)
    ts = strat_total(None, stored, idx_by_h)
    tb = strat_total(None, json_b * (1.0 - share), idx_by_h)
    tm = strat_total(None, lossless_m, idx_by_h)
    return tj / ts, tb / ts, tj / (ts + tm)


def aggregate(meas_rows: list[dict], wpf_csv: Path, hartree_csv: Path, seed: int = 20261022, B: int = 2000) -> dict:
    meas = {r["task_id"]: r for r in meas_rows}
    out = {"objects_measured": sum(r["status"] == "OK" for r in meas_rows), "objects_failed":
           sum(r["status"] != "OK" for r in meas_rows), "estimates": []}
    ok = [r for r in meas_rows if r["status"] == "OK"]
    out["objects_with_diff"] = sum(str(r["has_diff"]) == "True" for r in ok)
    out["median_diff_share_text"] = float(np.median([float(r["diff_share_text"]) for r in ok])) if ok else None
    out["median_lossless_diff_over_total"] = float(np.median(
        [float(r["lossless_diff"]) / float(r["lossless_total"]) for r in ok])) if ok else None
    tables = []
    for r in csv.DictReader(wpf_csv.read_text(encoding="utf-8").splitlines()):
        tables.append(("bader", r))
    for r in csv.DictReader(hartree_csv.read_text(encoding="utf-8").splitlines()):
        tables.append(("hartree", r))
    specs = [("bader", "stored_0.0001", "1e-4 e"), ("bader", "stored_0.001", "1e-3 e"), ("bader", "stored_0.01", "1e-2 e"),
             ("hartree", "stored_L_0.0001", "law 1e-4"), ("hartree", "stored_L_1e-06", "law 1e-6"),
             ("hartree", "stored_L_1e-08", "law 1e-8"), ("hartree", "stored_P_1e-06", "pointwise 1e-6")]
    rng = np.random.default_rng(seed)
    for contract, col, label in specs:
        rows = [r for c, r in tables if c == contract]
        strata = np.array([r["stratum"] for r in rows])
        json_b = np.array([float(r["frame_bytes"]) for r in rows])
        stored = np.array([float(r[col]) if r.get(col) not in (None, "") else float(r["frame_bytes"]) for r in rows])
        miss = [r["task_id"] for r in rows if r["task_id"] not in meas or meas[r["task_id"]]["status"] != "OK"]
        # objects without a measurement keep share 0 and no magnetization cost (conservative toward the
        # published value); their number is reported
        share = np.array([float(meas[r["task_id"]]["diff_share_text"]) if r["task_id"] not in miss else 0.0
                          for r in rows])
        lm = np.array([float(meas[r["task_id"]]["lossless_diff"]) if r["task_id"] not in miss else 0.0 for r in rows])
        # failed pipeline objects (stored = current file) already store the magnetization: no extra cost
        failed = np.array([r.get("status", "SUCCESS") != "SUCCESS" for r in rows])
        lm = np.where(failed, 0.0, lm)
        idx = {h: np.flatnonzero(strata == h) for h in N_FRAME}
        point = ratios(json_b, stored, share, lm, idx)
        boot = np.empty((B, 3))
        for b in range(B):
            ib = {h: rng.choice(ix, size=len(ix), replace=True) for h, ix in idx.items()}
            boot[b] = ratios(json_b, stored, share, lm, ib)
        lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
        out["estimates"].append({"contract": contract, "tolerance": label, "objects_unmeasured": len(miss),
                                 "R_current": point[0], "R_current_ci": [lo[0], hi[0]],
                                 "R_block_only": point[1], "R_block_only_ci": [lo[1], hi[1]],
                                 "R_with_lossless_m": point[2], "R_with_lossless_m_ci": [lo[2], hi[2]]})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--objects", type=Path, required=True)
    r.add_argument("--shard", type=int, required=True)
    r.add_argument("--nshards", type=int, required=True)
    r.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--inputs", type=Path, required=True)
    a.add_argument("--wpf", type=Path, required=True)
    a.add_argument("--hartree", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        rows = list(csv.DictReader(args.objects.read_text(encoding="utf-8").splitlines()))
        # largest objects spread over shards: sort by size, deal round-robin
        rows.sort(key=lambda x: -int(x["frame_bytes"]))
        mine = rows[args.shard::args.nshards]
        res = []
        for row in mine:
            rec = measure(row)
            print("S0B", rec["task_id"], rec["stratum"], rec["status"], rec.get("diff_share_text"), flush=True)
            res.append(rec)
        args.out.mkdir(parents=True, exist_ok=True)
        write(res, args.out / f"s0b_shard{args.shard:02d}.csv")
        return 0
    rows = []
    for p in sorted(args.inputs.rglob("s0b_shard*.csv")):
        rows.extend(csv.DictReader(p.read_text(encoding="utf-8").splitlines()))
    args.out.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda x: (x["stratum"], x["task_id"]))
    write(rows, args.out / "objects_spin_bytes.csv")
    summ = aggregate(rows, args.wpf, args.hartree)
    (args.out / "SUMMARY.json").write_text(json.dumps(summ, indent=2) + "\n", encoding="utf-8")
    lines = ["# WS-S0b — magnetization block in the archive sample (sensitivity of the archive estimates)", "",
             f"Objects measured {summ['objects_measured']}/300, failed {summ['objects_failed']}; "
             f"objects carrying a magnetization block {summ['objects_with_diff']}; "
             f"median text share of the block {summ['median_diff_share_text']:.3f}; "
             f"median lossless(m)/lossless(rho) {summ['median_lossless_diff_over_total']:.3f}.", "",
             "| contract | tolerance | R as published [95% CI] | R vs charge-density block only | R with m stored losslessly |",
             "|---|---|---|---|---|"]
    for e in summ["estimates"]:
        f = lambda v, c: f"{v:.3g} [{c[0]:.3g}, {c[1]:.3g}]"  # noqa: E731
        lines.append(f"| {e['contract']} | {e['tolerance']} | {f(e['R_current'], e['R_current_ci'])} | "
                     f"{f(e['R_block_only'], e['R_block_only_ci'])} | {f(e['R_with_lossless_m'], e['R_with_lossless_m_ci'])} |")
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
