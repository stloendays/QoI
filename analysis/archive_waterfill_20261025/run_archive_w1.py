#!/usr/bin/env python3
"""Whole-object Hartree archive under the W1 writer: W (water-filling law with symmetry, arm W1S) and Q (operational
allocation on the W1 curves with symmetry, arm O1S).

Frame, sample, storage rule, moment policy and estimators are those of the truncation/operational-optimum study
(`analysis/archive_truncation_20261024/`, whose `process` and `aggregate` this module follows line by line); only the
density writers differ. Per object and per tau_H in {1e-6, 1e-4}:

1. if the object is Hartree-eligible at tau_H (archive-law record), search writer W or Q (`w1.search_scalar` /
   `w1.search_rdo`) and verify the decoded Hartree certificate (historical and Nyquist-safe < tau_H);
2. derive the Bader partition of the decoded rho' with the compiled binary and certify m on it at tau_mu = 1e-2 mu_B
   (`run_archive_truncation.certify_m`, unchanged);
3. record the stored bytes: W/Q's certified rho stream (lossless rho if not eligible or not certified) and the
   manuscript's m policy (decoded-frame m where it certifies, otherwise the reference atom map plus the
   reference-frame m of S2).

Checkpoint per object: checkpoints/<task_id>.json. `aggregate` joins these with the committed L and P records and the
committed T and O objects table, and gives every writer's whole-object ratio with the archive bootstrap (seed
20261012, 2,000 resamples, paired across writers).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import time
import traceback
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
AN = HERE.parent
sys.path.insert(0, str(AN / "waterfill_writer_20261025"))
import w1  # noqa: E402

_spec = importlib.util.spec_from_file_location("run_archive_truncation", AN / "archive_truncation_20261024" /
                                               "run_archive_truncation.py")
RAT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RAT)

TAUS_H = RAT.TAUS_H
TAU_MU = RAT.TAU_MU
WRITERS = ("W", "Q")
ARM = {"W": "W1S", "Q": "O1S"}
tkey = RAT.tkey


def structure_of(d):
    from pymatgen.core import Lattice, Structure
    return Structure(Lattice(d["lattice"]), d["symbols"], d["frac"])


def process(row: dict, blob_path: Path, S: dict, bader: Path) -> dict:
    s1, RC, v02 = S["s1"], S["RC"], S["v02"]
    t0 = time.time()
    out = {"task_id": row["task_id"], "stratum": row["stratum"], "status": "SUCCESS", "error": "", "results": {}}
    try:
        blob = blob_path.read_bytes()
        if len(blob) != int(row["frame_bytes"]):
            raise RuntimeError("size mismatch against the frame")
        out["input_sha256"] = hashlib.sha256(blob).hexdigest()
        d = s1.decode(blob)
        del blob
        rho, m = d["rho"], d["m"]
        lat, natoms = d["lattice"], len(d["symbols"])
        out.update(npoints=int(rho.size), natoms=natoms, lossless_rho=int(row["lossless_bytes"]),
                   lossless_m=len(zlib.compress(m.tobytes(), 6)))
        rh, rs = v02.reference_hartree_rms(rho, lat)
        ptp = float(np.ptp(rho))

        def certify(rec):
            return RC.certify(rec, rho, lat, rh, rs)

        F = None
        an = None
        with tempfile.TemporaryDirectory(prefix="arch_w1_") as td:
            work = Path(td) / "codec"
            work.mkdir()
            B = s1.Bader(bader, lat, d["frac"], d["symbols"], rho.shape, Path(td))
            mu_ref, _ = B(m, rho, "ref")
            e_r, e_m = s1.f32_eps(rho), s1.f32_eps(m)
            floor = 0.0
            for s in s1.SEEDS:
                rng = np.random.default_rng(s)
                mu_p, _ = B(m + rng.uniform(-e_m, e_m, m.shape), rho + rng.uniform(-e_r, e_r, rho.shape), f"p{s}")
                floor = max(floor, float(np.max(np.abs(mu_p - mu_ref))))
            out["floor_muB"] = floor
            for tau in TAUS_H:
                eligible = str(row[f"eligible_{tkey(tau)}"]) == "True"
                for w in WRITERS:
                    ts = time.time()
                    r = {"eligible": eligible, "certified": False, "rho_bytes": out["lossless_rho"], "param": ""}
                    rec_r = rho
                    if eligible:
                        if F is None:
                            F = w1.prepare(rho, lat, rh, structure_of(d), use_symmetry=True)
                            out["symmetry"] = F.sym_status
                        if w == "W":
                            res = w1.search_scalar(F, "wf", tau, ptp, certify)
                        else:
                            if an is None:
                                an = w1.rdo_analysis(F, ptp)
                            res = w1.search_rdo(F, an, tau, ptp, certify)
                        if res is not None:
                            r.update(certified=True, rho_bytes=int(res["bytes"]), param=res["param"],
                                     hartree_hist=float(res["hartree_hist"]), hartree_safe=float(res["hartree_safe"]))
                            rec_r = res["rec"]
                    nb, codec, err = RAT.certify_m(S, B, m, rec_r, mu_ref, floor, natoms, out["lossless_m"], work)
                    r.update(m_decframe_bytes=nb, m_codec=codec, m_err_binary=err, seconds=time.time() - ts)
                    out["results"][f"{w}_{tkey(tau)}"] = r
                    print("ARCHW", row["task_id"], w, tkey(tau), r["certified"], r["rho_bytes"], codec, flush=True)
    except Exception as e:  # noqa: BLE001
        out.update(status="FAILED", error=f"{type(e).__name__}: {e}"[:500], traceback=traceback.format_exc()[-2000:])
    out["wall_seconds"] = time.time() - t0
    return out


# ----------------------------------------------------------------------------------------------- aggregate
def aggregate(ckpt_dir: Path, repo: Path, out: Path) -> dict:
    """Stored bytes per object for L, P (committed records), T, O (committed objects table of the truncation study)
    and W, Q (this study's checkpoints), with RAT's stratified estimator and paired bootstrap."""
    se = repo / "analysis" / "scope_expansion_20261022"
    har = RAT._read(se / "archive_hartree_objects.csv")
    s2 = {r["task_id"]: r for r in RAT._read(se / "results" / "s2_archive_whole_object" / "objects_spin_store.csv")}
    s2b = {r["task_id"]: r for r in RAT._read(se / "results" / "s2b_archive_hartree_decframe" / "objects.csv")}
    s2c = {r["task_id"]: r for r in RAT._read(se / "results" / "s2c_archive_hartree_decframe_1e-4" / "objects.csv")}
    s2d = {r["task_id"]: r for r in RAT._read(se / "results" / "s2d_archive_pointwise_decframe_1e-6" / "objects.csv")}
    to = {r["task_id"]: r for r in RAT._read(repo / "analysis" / "archive_truncation_20261024" / "results" /
                                             "objects.csv")}
    ck = {}
    for p in sorted(ckpt_dir.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        ck[d["task_id"]] = d
    assert len(har) == 300
    strata = np.array([r["stratum"] for r in har])
    idx = {h: np.flatnonzero(strata == h) for h in RAT.N_FRAME}
    js = np.array([float(r["frame_bytes"]) for r in har])

    def m_map(t):
        r = s2[t]
        return float(r["m_store_0.01"]) + float(r["label_atom_xz_bytes"])

    def m_hybrid(dec_row):
        return lambda t: (float(dec_row[t]["m_store_0.01"]) if dec_row.get(t, {}).get("status") == "OK"
                          and dec_row[t]["m_codec_0.01"] in ("zfp", "sz3", "sperr") else m_map(t))

    stored, failed = {}, {}
    for tau in TAUS_H:
        k = tkey(tau)
        mL = m_hybrid(s2b if tau == 1e-6 else s2c)
        stored[("L", k)] = np.array([float(r[f"stored_L_{k}"]) + mL(r["task_id"]) for r in har])
        if tau == 1e-6:
            mP = m_hybrid(s2d)
            stored[("P", k)] = np.array([float(r[f"stored_P_{k}"]) + mP(r["task_id"]) for r in har])
        for w in ("T", "O"):                       # committed objects table (all 300 SUCCESS)
            vals = []
            for r in har:
                x = to[r["task_id"]]
                if x["status"] != "SUCCESS":
                    vals.append(float(r["frame_bytes"]))
                    continue
                mb = x[f"{w}_{k}_m_bytes"]
                vals.append(float(x[f"{w}_{k}_rho_bytes"]) + (float(mb) if mb not in ("", "None") else m_map(r["task_id"])))
            stored[(w, k)] = np.array(vals)
        for w in WRITERS:
            vals, nf = [], 0
            for r in har:
                c = ck.get(r["task_id"])
                if c is None or c["status"] != "SUCCESS":
                    vals.append(float(r["frame_bytes"]))
                    nf += 1
                    continue
                x = c["results"][f"{w}_{k}"]
                m_b = x["m_decframe_bytes"] if x["m_decframe_bytes"] is not None else m_map(r["task_id"])
                vals.append(float(x["rho_bytes"]) + float(m_b))
            stored[(w, k)] = np.array(vals)
            failed[(w, k)] = nf
    names = sorted(stored)
    point = {n: RAT._tot(js, idx) / RAT._tot(stored[n], idx) for n in names}
    rng = np.random.default_rng(RAT.SEED)
    boot = {n: np.empty(RAT.NBOOT) for n in names}
    for b in range(RAT.NBOOT):
        ib = {h: rng.choice(ix, size=len(ix), replace=True) for h, ix in idx.items()}
        tj = RAT._tot(js, ib)
        for n in names:
            boot[n][b] = tj / RAT._tot(stored[n], ib)
    ci = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]  # noqa: E731
    summ = {"objects_checkpointed": len(ck), "objects_success": sum(c["status"] == "SUCCESS" for c in ck.values()),
            "tau_mu_muB": TAU_MU, "seed": RAT.SEED, "resamples": RAT.NBOOT, "estimates": {}, "paired": {}}
    for (w, k) in names:
        summ["estimates"][f"{w}_{k}"] = {"R": point[(w, k)], "ci95": ci(boot[(w, k)]),
                                         "objects_failed_as_json": failed.get((w, k), 0)}
    for k in (tkey(t) for t in TAUS_H):
        for a, bb in (("W", "O"), ("W", "L"), ("W", "T"), ("W", "P"), ("Q", "O"), ("Q", "W"), ("O", "L"), ("O", "T"),
                      ("L", "T"), ("O", "P")):
            if (a, k) in point and (bb, k) in point:
                summ["paired"][f"{a}/{bb}_{k}"] = {"ratio": point[(a, k)] / point[(bb, k)],
                                                   "ci95": ci(boot[(a, k)] / boot[(bb, k)])}
    for w in WRITERS:
        for k in (tkey(t) for t in TAUS_H):
            xs = [c["results"][f"{w}_{k}"] for c in ck.values() if c["status"] == "SUCCESS"]
            summ[f"counts_{w}_{k}"] = {"eligible": sum(x["eligible"] for x in xs),
                                        "certified": sum(x["certified"] for x in xs),
                                        "m_decoded_frame": sum(x["m_decframe_bytes"] is not None for x in xs)}
    syms = [c.get("symmetry", {}) for c in ck.values() if c["status"] == "SUCCESS" and c.get("symmetry")]
    summ["symmetry"] = {"objects": len(syms), "with_symmetry": sum(int(s.get("ops", 1)) > 1 for s in syms),
                        "ops_median": float(np.median([int(s.get("ops", 1)) for s in syms])) if syms else None}
    out.mkdir(parents=True, exist_ok=True)
    with (out / "objects.csv").open("w", newline="", encoding="utf-8") as fh:
        import csv
        cols = ["task_id", "stratum", "status", "npoints", "spacegroup", "ops"] + [
            f"{w}_{tkey(t)}_{f}" for t in TAUS_H for w in WRITERS
            for f in ("certified", "rho_bytes", "param", "m_bytes", "m_codec")]
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for r in har:
            c = ck.get(r["task_id"], {"status": "MISSING", "results": {}})
            sy = c.get("symmetry", {})
            row = {"task_id": r["task_id"], "stratum": r["stratum"], "status": c["status"], "npoints": c.get("npoints"),
                   "spacegroup": sy.get("spacegroup"), "ops": sy.get("ops")}
            for t in TAUS_H:
                for w in WRITERS:
                    x = c["results"].get(f"{w}_{tkey(t)}", {})
                    row.update({f"{w}_{tkey(t)}_certified": x.get("certified"),
                                f"{w}_{tkey(t)}_rho_bytes": x.get("rho_bytes"), f"{w}_{tkey(t)}_param": x.get("param"),
                                f"{w}_{tkey(t)}_m_bytes": x.get("m_decframe_bytes"),
                                f"{w}_{tkey(t)}_m_codec": x.get("m_codec")})
            wr.writerow(row)
    (out / "SUMMARY.json").write_text(json.dumps(summ, indent=2) + "\n", encoding="utf-8")
    return summ


# ----------------------------------------------------------------------------------------------- driver
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="one object, checkpointed")
    r.add_argument("--task-id", required=True)
    r.add_argument("--inputs", type=Path, required=True, help="prefetched <task_id>.json.gz")
    r.add_argument("--checkpoints", type=Path, required=True)
    r.add_argument("--repo-root", type=Path, required=True)
    r.add_argument("--frozen-root", type=Path, required=True)
    r.add_argument("--bader", type=Path, required=True)
    g = sub.add_parser("aggregate")
    g.add_argument("--checkpoints", type=Path, required=True)
    g.add_argument("--repo-root", type=Path, required=True)
    g.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "aggregate":
        print(json.dumps(aggregate(a.checkpoints, a.repo_root.resolve(), a.out), indent=1))
        return 0
    rows = {x["task_id"]: x for x in RAT._read(a.repo_root / "analysis" / "scope_expansion_20261022" /
                                                 "archive_hartree_objects.csv")}
    row = rows[a.task_id]
    a.checkpoints.mkdir(parents=True, exist_ok=True)
    ck = a.checkpoints / f"{a.task_id}.json"
    if ck.exists() and json.loads(ck.read_text(encoding="utf-8")).get("status") == "SUCCESS":
        print("SKIP complete", a.task_id)
        return 0
    S = RAT.load_stack(a.repo_root.resolve(), a.frozen_root.resolve())
    rec = process(row, a.inputs / f"{a.task_id}.json.gz", S, a.bader)
    tmp = ck.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=float) + "\n", encoding="utf-8")
    os.replace(tmp, ck)
    print("DONE", a.task_id, rec["status"], rec.get("error", ""))
    return 0 if rec["status"] == "SUCCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
