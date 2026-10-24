#!/usr/bin/env python3
"""Linearized-XC allocation law (PROTOCOL.md): per material of P1 (60 bulk crystals) and P3b (32 slabs), QSQ for the
PBE XC-energy contract exactly as `nonlinear_xc_20261024`, then for each eligible tau_x in {1, 0.1} meV/atom the same
equal search for two writers in the QOAC v0.3 shell container: X (steps from the XC potential's shell weights) and F
(flat steps). 60-step log bisection of alpha with the decoded XC certificate as predicate; smallest passing stream.
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
sys.path.insert(0, str(HERE.parent / "nonlinear_xc_20261024"))
import xcl  # noqa: E402
import run_xc as base  # noqa: E402  manifests, module stack, seeds and tolerances of the XC study
from xcl import xc  # noqa: E402

WRITERS = ("X", "F")


def search(eng, prep, ptp, u, x, lat, ref, natoms, tau_x):
    """Smallest passing stream over a 60-step log bisection of alpha in [max(1e-14 ptp, floor), 1e3 ptp]."""
    seen = {}

    def ok(a):
        blob = xcl.encode(prep, ptp, u, float(a))
        rec = xcl.decode(blob)
        e = xc.xc_errors(ref, rec, lat, natoms)
        good = e["dE_pbe_meV_per_atom"] < tau_x
        if good:
            seen[float(a)] = (len(blob), rec, e)
        return good

    lo = max(1e-14 * ptp, xcl.alpha_floor(prep, u, ptp))
    eng.bisect_scale(ok, lo, 1e3 * ptp)
    if not seen:
        return None
    a, (nb, rec, e) = min(seen.items(), key=lambda kv: kv[1][0])
    return {"alpha_rel": a / ptp, "bytes": nb, "rec": rec, "xc": e}


def process(meta: dict, blob_path: Path, S: dict) -> dict:
    v02, dev, RC, eng = S["v02"], S["dev"], S["RC"], S["eng"]
    mid = meta["material_id"]
    t0 = time.time()
    out = {"material_id": mid, "cohort": meta["cohort"], "status": "SUCCESS", "error": "", "xc_contract": []}
    try:
        blob = blob_path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != meta["sha256"]:
            raise RuntimeError("sha256 mismatch against the manifest")
        with tempfile.TemporaryDirectory(prefix="xcl_") as td:
            grid, _ = dev.build_grid(meta, blob, Path(td))
            x = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
            lat = np.asarray(grid.structure.lattice.matrix, float)
            natoms = len(grid.structure)
            raw, ptp = x.nbytes, float(np.ptp(x))
            rh, rs = v02.reference_hartree_rms(x, lat)
            ref = xc.exc_energies(x, lat, natoms)
            prep = v02.prepare_field(x, lat, shell_count=32)
            W = xcl.shell_weights(prep, xcl.pbe_potential(x, lat))
            out.update(npoints=int(x.size), natoms=natoms, raw_bytes=raw, E_pbe_eV_per_atom=ref["E_pbe_eV_per_atom"],
                       shell_weight_rel=[float(w / W.max()) for w in W])
            eps = float(np.max(np.abs(x.astype(np.float32).astype(np.float64) - x)))
            floor = 0.0
            for s in base.SEEDS:
                rng = np.random.default_rng(s)
                floor = max(floor, xc.xc_errors(ref, x + rng.uniform(-eps, eps, x.shape), lat, natoms)["dE_pbe_meV_per_atom"])
            out.update(epsilon=eps, xc_floor_meV_per_atom=floor)
            for tau_x in base.TAUS_X:
                for w in WRITERS:
                    r = {"writer": w, "tau_x": tau_x, "eligible": bool(floor < tau_x)}
                    if r["eligible"]:
                        res = search(eng, prep, ptp, xcl.shape_of(W, w), x, lat, ref, natoms, tau_x)
                        if res is None:
                            r.update(certified=False)
                        else:
                            eh, es = RC.certify(res["rec"], x, lat, rh, rs)
                            r.update(certified=True, alpha_rel=res["alpha_rel"], bytes=res["bytes"],
                                     cr=raw / res["bytes"], hartree_hist=eh, hartree_safe=es, **res["xc"])
                    out["xc_contract"].append(r)
                    print("XCL", mid, w, tau_x, r.get("certified"), r.get("cr"), flush=True)
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
    a = ap.parse_args(argv)
    repo = a.repo_root.resolve()
    meta = base.manifests(repo)[a.material]
    a.checkpoints.mkdir(parents=True, exist_ok=True)
    ck = a.checkpoints / f"{a.material}.json"
    if ck.exists() and json.loads(ck.read_text(encoding="utf-8")).get("status") == "SUCCESS":
        print("SKIP complete", a.material)
        return 0
    S = base.load_stack(repo, a.frozen_root.resolve())
    rec = process(meta, a.inputs / f"{a.material}.src", S)
    tmp = ck.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=float) + "\n", encoding="utf-8")
    os.replace(tmp, ck)
    print("DONE", a.material, rec["status"], rec.get("error", ""))
    return 0 if rec["status"] == "SUCCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
