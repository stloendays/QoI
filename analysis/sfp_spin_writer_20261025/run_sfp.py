#!/usr/bin/env python3
"""Study 3: the W2 writer (structure-factor prediction) on one law-protocol material (see PROTOCOL.md), checkpointed.

Arms (every stream decoded by its own decoder and certified: historical and Nyquist-safe Hartree relative RMS < tau):
  W1S  water-filling law with symmetry, W1 stream (revision 11's writer, recomputed)
  W2S  W2 writer with symmetry: the smallest of no prediction, prediction on every gated shell, prediction on the
       written gated shells (w2.search_w2)
  W2   the same without symmetry
  O2S  operational allocation (arm A3's selection on the W1 curves) on the SFP residual, with symmetry
Checkpoint: <checkpoints>/<material_id>.json with one row per (arm, tau).
"""
from __future__ import annotations

import argparse
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
sys.path.insert(0, str(HERE.parent / "waterfill_writer_20261025"))
import w2  # noqa: E402
import run_w1  # noqa: E402

w1 = w2.w1
TAUS = (1e-6, 1e-4)
ARMS = ("W1S", "W2S", "W2", "O2S")


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
        with tempfile.TemporaryDirectory(prefix="w2_") as td:
            grid, _ = dev.build_grid(meta, blob, Path(td))
        del blob
        x = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
        st = grid.structure
        lat = np.asarray(st.lattice.matrix, float)
        symbols = [str(s.specie.symbol) for s in st]
        frac = np.asarray(st.frac_coords, dtype=np.float64)
        raw, ptp = x.nbytes, float(np.ptp(x))
        rh, rs = v02.reference_hartree_rms(x, lat)

        def certify(rec):
            return v02.hartree_error_metrics(rec - x, lat, rh, rs)

        ts = time.time()
        F0 = w1.prepare(x, lat, rh, None, use_symmetry=False)
        F1 = w1.prepare(x, lat, rh, st, use_symmetry=True)
        I0 = w2.sfp_fit(F0, symbols, frac)
        I1 = w2.sfp_fit(F1, symbols, frac)
        out.update(npoints=int(x.size), raw_bytes=raw, natoms=len(st), nspecies=len(set(symbols)),
                   symmetry=F1.sym_status, sfp_shells=len(I1["used"]) if I1 else 0,
                   sfp_block_bytes=len(w2.sfp_block(I1)) if I1 else 0, prepare_seconds=time.time() - ts)
        if I1 is not None:
            G = w2.residual_field(F1, I1["pred"])
            e0 = np.bincount(F1.shell, F1.e_sig, minlength=w2.SHELLS)
            e1 = np.bincount(F1.shell, G.e_sig, minlength=w2.SHELLS)
            out["shell_energy_ratio"] = [float(a / b) if b > 0 else None for a, b in zip(e1, e0)]
        for tau in taus:
            for arm in arms:
                ts = time.time()
                res, extra = None, {}
                if arm == "W1S":
                    res = w1.search_scalar(F1, "wf", tau, ptp, certify)
                elif arm in ("W2S", "W2"):
                    res = w2.search_w2(F1 if arm == "W2S" else F0, I1 if arm == "W2S" else I0, tau, ptp, certify)
                    if res is not None:
                        extra = {"variant": res["variant"], "sfp_shells_used": res["sfp_shells"],
                                 "w1s_bytes": res["none_bytes"]}
                elif I1 is not None:
                    res = w2.search_rdo(F1, I1, tau, ptp, certify)
                row = {"material_id": mid, "cohort": meta["cohort"], "system_type": meta["system_type"],
                       "npoints": int(x.size), "raw_bytes": raw, "arm": arm, "tau": tau, "certified": res is not None,
                       "seconds": time.time() - ts}
                if res is not None:
                    row.update(param=res["param"], bytes=int(res["bytes"]), cr=raw / res["bytes"],
                               hartree_hist=float(res["hartree_hist"]), hartree_safe=float(res["hartree_safe"]),
                               shells_written=res.get("shells_written"), **extra)
                out["rows"].append(row)
                print("W2", mid, arm, tau, row["certified"], row.get("bytes"), round(row["seconds"], 1), flush=True)
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
    meta = run_w1.manifests(repo, a.cohorts.split(","))[a.material]
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
