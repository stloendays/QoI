#!/usr/bin/env python3
"""Nonlinear downstream QoI: exchange-correlation energy of the stored density (PROTOCOL.md).

Per material of P1 (60 bulk crystals) and P3b (32 slabs):

Part 1 (transfer). Regenerate the law protocol's certified Hartree streams of A1 (law), A2 (truncation), A3
(operational optimum) and A6 (best pointwise codec) at tau_H in {1e-4, 1e-6, 1e-8} from their recorded parameters
(`analysis/general_qoac_law/results/run_*_CONFIRMATORY/part_a_rows.csv`), check the bytes and the Hartree
certificate, and record the XC errors of the decoded density (xc.py): |dE_xc^PBE|, |dE_xc^LDA| (meV/atom) and the
relative RMS error of V_xc^LDA.

Part 2 (XC contract). QSQ for the contract "PBE XC energy of the stored density, tolerance tau_x meV/atom": five
float32-scale probes (seeds 20260905, 1, 2, 3, 4); eligible iff the floor < tau_x. For eligible (material, tau_x),
tau_x in {1, 0.1} meV/atom, the same equal search for three writers with the decoded XC certificate as predicate:
P (best of ZFP/SZ3/SPERR, absolute-tolerance bisection), L (closed-form Hartree law, Delta_G ~ |G|^2) and U (uniform
reciprocal-space steps), each a 60-step log bisection keeping the smallest passing stream; the Hartree error of each
XC-certified stream is recorded too.
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
import xc  # noqa: E402

TAUS_H = (1e-4, 1e-6, 1e-8)
TAUS_X = (1.0, 0.1)                       # meV per atom
ARMS = ("A1", "A2", "A3", "A6")
SEEDS = (20260905, 1, 2, 3, 4)
COHORTS = {"P1": ("P1_CONFIRMATORY_MANIFEST.csv", "run_P1_CONFIRMATORY"),
           "P3B": ("P3B_CONFIRMATORY_MANIFEST.csv", "run_P3B_CONFIRMATORY")}


def load_stack(repo: Path, frozen: Path):
    an = repo / "analysis"
    sys.path.insert(0, str(frozen / "validation"))
    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    for p in (an / "deployment_cost_20261012", an / "qoac_v03_rdo", an / "qoac_h_strong_baselines",
              an / "operator_aware_codec_hartree_v02"):
        sys.path.insert(0, str(p))
    import run_cost as RC                      # noqa: E402
    import run_engineering as eng              # noqa: E402
    import truncation_codec as t1              # noqa: E402
    import external_end_to_end as core         # noqa: E402
    import development_compatibility_smoke as dev  # noqa: E402
    v02, v3 = RC.lazy()
    return dict(RC=RC, eng=eng, t1=t1, core=core, dev=dev, v02=v02, v3=v3)


def manifests(repo: Path) -> dict:
    out = {}
    for cohort, (man, run) in COHORTS.items():
        for r in csv.DictReader(open(repo / "analysis/fresh_population_20261006" / man, encoding="utf-8")):
            out[r["material_id"]] = dict(r, cohort=cohort, run=run)
    return out


def recorded(repo: Path, run: str, mid: str) -> dict:
    """Smallest certified stream per (arm, tau) in the law protocol record: its parameter and bytes."""
    best = {}
    for r in csv.DictReader(open(repo / "analysis/general_qoac_law/results" / run / "part_a_rows.csv", encoding="utf-8")):
        if r["material_id"] != mid or r["certified"] != "True" or r["arm"] not in ARMS:
            continue
        k = (r["arm"], float(r["tau"]))
        if k not in best or int(r["bytes"]) < best[k]["bytes"]:
            best[k] = {"param": r["param"], "bytes": int(r["bytes"])}
    return best


def kv(param: str) -> dict:
    return dict(p.split("=") for p in param.split(";") if p)


def regenerate(S, arm, param, x, lat, ptp, prep, an, tau, work):
    """Decoded field and bytes of a recorded certified stream."""
    v02, v3, t1, RC, core = S["v02"], S["v3"], S["t1"], S["RC"], S["core"]
    p = kv(param)
    if arm == "A1":
        blob, _ = v02.encode_prepared(prep, alpha=float(p["alpha_rel"]) * ptp, beta=2.0, zlib_level=6)
        return np.asarray(v02.decode_blob(blob)[0], float), len(blob)
    if arm == "A2":
        blob = t1.encode(prep, alpha=float(p["alpha_rel"]) * ptp, q_cut=float(p["q_cut"]))
        return np.asarray(t1.decode(blob), float), len(blob)
    if arm == "A3":
        blob = v3.encode(an, v3.select(an, tau, margin=float(p["margin"]), polish=True))
        return np.asarray(RC.F.decode_operational(blob), float), len(blob)
    rec, nb, _ = core.codec_roundtrip(p["codec"], x, float(p["abs_tol_rel"]) * ptp, work)
    return np.asarray(rec, float), int(nb)


def search_xc(S, writer, x, lat, ptp, prep, ref, natoms, tau_x, work):
    """Equal search under the decoded XC certificate; smallest passing stream. Returns dict or None."""
    eng, v02, core = S["eng"], S["v02"], S["core"]
    seen = {}

    def run(label, enc_dec, lo, hi):
        def ok(t):
            rec, nb = enc_dec(float(t))
            e = xc.xc_errors(ref, rec, lat, natoms)
            good = e["dE_pbe_meV_per_atom"] < tau_x
            if good:
                seen[(label, float(t))] = (nb, rec, e)
            return good
        eng.bisect_scale(ok, lo, hi)

    if writer == "P":
        for codec in ("zfp", "sz3", "sperr"):
            def ed(t, c=codec):
                rec, nb, _ = core.codec_roundtrip(c, x, t, work)
                return np.asarray(rec, float), int(nb)
            run(f"codec={codec}", ed, 1e-14 * ptp, 1.0 * ptp)
    else:
        beta = 2.0 if writer == "L" else 0.0

        def ed(a):
            blob, _ = v02.encode_prepared(prep, alpha=a, beta=beta, zlib_level=6)
            return np.asarray(v02.decode_blob(blob)[0], float), len(blob)
        run(f"beta={beta:g}", ed, 1e-14 * ptp, 1e3 * ptp)
    if not seen:
        return None
    (label, t), (nb, rec, e) = min(seen.items(), key=lambda kvp: kvp[1][0])
    return {"param": f"{label};scale_rel={t / ptp:.9g}", "bytes": nb, "rec": rec, "xc": e}


def process(meta: dict, blob_path: Path, S: dict, repo: Path) -> dict:
    v02, v3, RC, dev = S["v02"], S["v3"], S["RC"], S["dev"]
    mid = meta["material_id"]
    t0 = time.time()
    out = {"material_id": mid, "cohort": meta["cohort"], "status": "SUCCESS", "error": "", "transfer": [], "xc_contract": []}
    try:
        blob = blob_path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != meta["sha256"]:
            raise RuntimeError("sha256 mismatch against the manifest")
        with tempfile.TemporaryDirectory(prefix="nlxc_") as td:
            work = Path(td)
            grid, _ = dev.build_grid(meta, blob, work)
            x = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
            lat = np.asarray(grid.structure.lattice.matrix, float)
            natoms = len(grid.structure)
            raw, ptp = x.nbytes, float(np.ptp(x))
            rh, rs = v02.reference_hartree_rms(x, lat)
            ref = xc.exc_energies(x, lat, natoms)
            out.update(npoints=int(x.size), natoms=natoms, raw_bytes=raw,
                       electrons=float(x.sum() / x.size), E_lda_eV_per_atom=ref["E_lda_eV_per_atom"],
                       E_pbe_eV_per_atom=ref["E_pbe_eV_per_atom"])
            prep = RC.F.prepare_field(x, lat)
            an = v3.analyze(x, lat, prior="operator", reference_historical_rms=rh,
                            d_floor_rel=1e-3 * min(RC.TAUS) ** 2 / 32)
            rec_params = recorded(repo, meta["run"], mid)
            for tau in TAUS_H:
                for arm in ARMS:
                    r = {"arm": arm, "tau_H": tau}
                    rp = rec_params.get((arm, tau))
                    if rp is None:
                        r["status"] = "not certified in the record"
                        out["transfer"].append(r)
                        continue
                    rec, nb = regenerate(S, arm, rp["param"], x, lat, ptp, prep, an, tau, work)
                    eh, es = RC.certify(rec, x, lat, rh, rs)
                    r.update(status="OK", param=rp["param"], bytes=nb, bytes_recorded=rp["bytes"], cr=raw / nb,
                             hartree_hist=eh, hartree_safe=es, hartree_certified=bool(eh < tau and es < tau),
                             **xc.xc_errors(ref, rec, lat, natoms))
                    out["transfer"].append(r)
            eps = float(np.max(np.abs(x.astype(np.float32).astype(np.float64) - x)))
            floor = 0.0
            for s in SEEDS:
                rng = np.random.default_rng(s)
                e = xc.xc_errors(ref, x + rng.uniform(-eps, eps, x.shape), lat, natoms)
                floor = max(floor, e["dE_pbe_meV_per_atom"])
            out.update(epsilon=eps, xc_floor_meV_per_atom=floor)
            for tau_x in TAUS_X:
                for w in ("P", "L", "U"):
                    r = {"writer": w, "tau_x": tau_x, "eligible": bool(floor < tau_x)}
                    if r["eligible"]:
                        res = search_xc(S, w, x, lat, ptp, prep, ref, natoms, tau_x, work)
                        if res is None:
                            r.update(certified=False)
                        else:
                            eh, es = RC.certify(res["rec"], x, lat, rh, rs)
                            r.update(certified=True, param=res["param"], bytes=res["bytes"], cr=raw / res["bytes"],
                                     hartree_hist=eh, hartree_safe=es, **res["xc"])
                    out["xc_contract"].append(r)
                    print("NLXC", mid, w, tau_x, r.get("certified"), r.get("cr"), flush=True)
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
    meta = manifests(repo)[a.material]
    a.checkpoints.mkdir(parents=True, exist_ok=True)
    ck = a.checkpoints / f"{a.material}.json"
    if ck.exists() and json.loads(ck.read_text(encoding="utf-8")).get("status") == "SUCCESS":
        print("SKIP complete", a.material)
        return 0
    S = load_stack(repo, a.frozen_root.resolve())
    rec = process(meta, a.inputs / f"{a.material}.src", S, repo)
    tmp = ck.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=float) + "\n", encoding="utf-8")
    os.replace(tmp, ck)
    print("DONE", a.material, rec["status"], rec.get("error", ""))
    return 0 if rec["status"] == "SUCCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
