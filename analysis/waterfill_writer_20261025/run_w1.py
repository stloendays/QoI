#!/usr/bin/env python3
"""Study 1: the W1 writer arms on one law-protocol material (see PROTOCOL.md), checkpointed.

Arms (every stream decoded by `w1.decode` and certified: historical and Nyquist-safe Hartree relative RMS < tau):
  L1   law,            no symmetry        W1   water-filling law, no symmetry
  W1S  water-filling,  symmetry           T1S  truncation (A2 search), symmetry
  O1   operational allocation (A3 search on W1 curves), no symmetry
  O1S  operational allocation, symmetry
Checkpoint: <checkpoints>/<material_id>.json with one row per (arm, tau).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w1  # noqa: E402

TAUS = (1e-6, 1e-4, 1e-8)
ARMS = ("L1", "W1", "W1S", "T1S", "O1", "O1S")
COHORTS = {"P1": "P1_CONFIRMATORY_MANIFEST.csv", "P3B": "P3B_CONFIRMATORY_MANIFEST.csv",
           "ENG": "P1_ENGINEERING_MANIFEST.csv"}


def manifests(repo: Path, cohorts=("P1", "P3B")) -> dict:
    out = {}
    for c in cohorts:
        for r in csv.DictReader(open(repo / "analysis/fresh_population_20261006" / COHORTS[c], encoding="utf-8")):
            out[r["material_id"]] = dict(r, cohort=c)
    return out


def process(meta: dict, blob_path: Path, repo: Path, frozen: Path, arms=ARMS, taus=TAUS) -> dict:
    sys.path.insert(0, str(frozen / "validation"))
    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev  # noqa: E402
    v02 = w1.v02
    mid = meta["material_id"]
    t0 = time.time()
    out = {"material_id": mid, "cohort": meta["cohort"], "system_type": meta["system_type"], "status": "SUCCESS",
           "error": "", "rows": []}
    try:
        blob = blob_path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != meta["sha256"]:
            raise RuntimeError("sha256 mismatch against the manifest")
        with tempfile.TemporaryDirectory(prefix="w1_") as td:
            grid, _ = dev.build_grid(meta, blob, Path(td))
        del blob
        x = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
        lat = np.asarray(grid.structure.lattice.matrix, float)
        raw, ptp = x.nbytes, float(np.ptp(x))
        rh, rs = v02.reference_hartree_rms(x, lat)

        def certify(rec):
            return v02.hartree_error_metrics(rec - x, lat, rh, rs)

        ts = time.time()
        F0 = w1.prepare(x, lat, rh, None, use_symmetry=False)
        F1 = w1.prepare(x, lat, rh, grid.structure, use_symmetry=True)
        out.update(npoints=int(x.size), raw_bytes=raw, natoms=len(grid.structure), symmetry=F1.sym_status,
                   prepare_seconds=time.time() - ts)
        an = {}
        for tau in taus:
            for arm in arms:
                ts = time.time()
                F = F1 if arm.endswith("S") else F0
                if arm in ("L1",):
                    res = w1.search_scalar(F, "law", tau, ptp, certify)
                elif arm in ("W1", "W1S"):
                    res = w1.search_scalar(F, "wf", tau, ptp, certify)
                elif arm == "T1S":
                    res = w1.search_trunc(F, tau, ptp, certify)
                else:
                    if arm not in an:
                        t1 = time.time()
                        an[arm] = w1.rdo_analysis(F, ptp)
                        out[f"{arm}_analysis_seconds"] = time.time() - t1
                    res = w1.search_rdo(F, an[arm], tau, ptp, certify)
                row = {"material_id": mid, "cohort": meta["cohort"], "system_type": meta["system_type"],
                       "npoints": int(x.size), "raw_bytes": raw, "arm": arm, "tau": tau, "certified": res is not None,
                       "seconds": time.time() - ts}
                if res is not None:
                    row.update(param=res["param"], bytes=int(res["bytes"]), cr=raw / res["bytes"],
                               hartree_hist=float(res["hartree_hist"]), hartree_safe=float(res["hartree_safe"]),
                               shells_written=res.get("shells_written"))
                out["rows"].append(row)
                print("W1", mid, arm, tau, row["certified"], row.get("bytes"), round(row["seconds"], 1), flush=True)
    except Exception as e:  # noqa: BLE001
        out.update(status="FAILED", error=f"{type(e).__name__}: {e}"[:500], traceback=traceback.format_exc()[-2000:])
    out["wall_seconds"] = time.time() - t0
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--material", required=True)
    ap.add_argument("--inputs", type=Path, required=True, help="prefetched <material_id>.src")
    ap.add_argument("--checkpoints", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--frozen-root", type=Path, required=True)
    ap.add_argument("--cohorts", default="P1,P3B")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--taus", default=",".join(f"{t:g}" for t in TAUS))
    a = ap.parse_args(argv)
    repo = a.repo_root.resolve()
    meta = manifests(repo, a.cohorts.split(","))[a.material]
    a.checkpoints.mkdir(parents=True, exist_ok=True)
    ck = a.checkpoints / f"{a.material}.json"
    if ck.exists() and json.loads(ck.read_text(encoding="utf-8")).get("status") == "SUCCESS":
        print("SKIP complete", a.material)
        return 0
    rec = process(meta, a.inputs / f"{a.material}.src", repo, a.frozen_root.resolve(), tuple(a.arms.split(",")),
                  tuple(float(t) for t in a.taus.split(",")))
    tmp = ck.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=float) + "\n", encoding="utf-8")
    os.replace(tmp, ck)
    print("DONE", a.material, rec["status"], rec.get("error", ""))
    return 0 if rec["status"] == "SUCCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
