#!/usr/bin/env python3
"""Whole-object Hartree archive under spectral truncation (T, arm A2) and the operational optimum (O, arm A3).

Frame, sample, storage rule and estimators are those of the archive-law study
(`analysis/archive_hartree_law_20261012/PROTOCOL.md`) and of the whole-object estimates S2b/S2c/S2d
(`analysis/scope_expansion_20261022/`); see PROTOCOL.md of this study. Per object and per tau_H in {1e-6, 1e-4}:

1. if the object is Hartree-eligible at tau_H (archive-law record), search writer W with the law protocol's own
   search (A2: best of 32 cutoffs q_c = k/32, exact spectral bisection of alpha, the three smallest candidates decoded
   and certified; A3: Lagrangian selection with margin 0.995 shrinking by 0.995) and verify the decoded Hartree
   certificate (historical and Nyquist-safe < tau_H);
2. derive the Bader partition of the decoded rho' with the compiled binary and certify m against the moments read on
   that partition at tau_mu = 1e-2 mu_B (best of ZFP/SZ3/SPERR, S2 QSQ gate, final verification by the binary);
3. record the stored bytes: W's certified rho stream (lossless rho if not eligible or not certified) and the m policy
   of the manuscript (decoded-frame m where it certifies, otherwise the reference atom map plus the reference-frame
   m of S2).

Checkpoint per object: checkpoints/<task_id>.json. `aggregate` joins these with the committed L (S2b, S2c) and
P (S2d) object tables and gives every writer's whole-object ratio with the frozen stratified bootstrap (seed
20261012, 2,000 resamples, paired across writers).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import sys
import tempfile
import time
import traceback
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TAUS_H = (1e-6, 1e-4)
TAU_MU = 1e-2
WRITERS = ("T", "O")
ARM = {"T": "A2", "O": "A3"}
N_FRAME = {"D01": 41527, "D02": 41531, "D03": 41529, "D04": 41529, "D05": 41528, "D06": 41529,
           "D07": 41529, "D08": 41529, "D09": 41529, "D10a": 33105, "D10b": 6741, "D10c": 1683}
SEED, NBOOT = 20261012, 2000


def tkey(tau: float) -> str:
    """Column suffix used by the archive-law tables (1e-06, 0.0001)."""
    return f"{tau:g}"


# ----------------------------------------------------------------------------------------------- imports
def load_stack(repo: Path, frozen: Path):
    """Import the committed code paths: run_cost (A1/A3/A6 search and certificate), the law protocol's
    run_engineering (Spec, bisect_scale, MARGIN), the truncation codec, and the S1/S3 moment helpers."""
    an = repo / "analysis"
    sys.path.insert(0, str(frozen / "validation"))
    for p in (an / "scope_expansion_20261022", an / "deployment_cost_20261012", an / "qoac_v03_rdo",
              an / "qoac_h_strong_baselines", an / "operator_aware_codec_hartree_v02"):
        sys.path.insert(0, str(p))
    import run_cost as RC                      # noqa: E402  (loads qoac_v03_rdo/run_engineering as `run_engineering`)
    import run_engineering as eng              # noqa: E402
    import truncation_codec as t1              # noqa: E402
    import run_spin_s1 as s1                   # noqa: E402
    from run_spin_s3_joint import search as m_search  # noqa: E402
    import external_end_to_end as core         # noqa: E402
    v02, v3 = RC.lazy()
    return dict(RC=RC, eng=eng, t1=t1, s1=s1, m_search=m_search, core=core, v02=v02, v3=v3)


# ----------------------------------------------------------------------------------------------- writers
def writer_T(S, prep, x, lat, rh, rs, ptp, tau):
    """Arm A2 exactly as `analysis/qoac_v03_rdo/run_engineering.py` (law protocol): every cutoff k/32, exact
    spectral bisection of a uniform step, the three smallest candidates decoded and certified (alpha *= 0.99)."""
    eng, t1, RC = S["eng"], S["t1"], S["RC"]
    ref_cons, ref_safe = RC.law_refs(prep, rh)
    spec = eng.Spec(prep, ref_cons, ref_safe)
    q = prep.topology.q
    cand = []
    for k in range(1, 33):
        qc = k / 32
        keep = q <= qc
        a = eng.bisect_scale(lambda s: spec.ok(np.full(q.shape, s), tau, keep), 1e-14 * ptp, 1e3 * ptp)
        if a:
            cand.append((len(t1.encode(prep, alpha=a, q_cut=qc)), qc, a))
    best = None
    for _, qc, a in sorted(cand)[:3]:               # the protocol keeps every certified candidate; the arm is the
        for _ in range(40):                          # smallest certified stream among them
            blob = t1.encode(prep, alpha=a, q_cut=qc)
            rec = np.ascontiguousarray(t1.decode(blob), dtype=np.float64)
            eh, es = RC.certify(rec, x, lat, rh, rs)
            if eh < tau and es < tau:
                if best is None or len(blob) < best["bytes"]:
                    best = {"param": f"q_cut={qc:.6g};alpha_rel={a / ptp:.9g}", "bytes": len(blob), "rec": rec,
                            "hartree_hist": eh, "hartree_safe": es}
                break
            a *= 0.99
    return best


def writer_O(S, an, x, lat, rh, rs, tau):
    """Arm A3 exactly as `run_cost.search('A3', ...)`, keeping the decoded field."""
    RC, eng, v3 = S["RC"], S["eng"], S["v3"]
    mg = eng.MARGIN
    for _ in range(20):
        blob = v3.encode(an, v3.select(an, tau, margin=mg, polish=True))
        rec = np.ascontiguousarray(RC.F.decode_operational(blob), dtype=np.float64)
        eh, es = RC.certify(rec, x, lat, rh, rs)
        if eh < tau and es < tau:
            return {"param": f"margin={mg:.4f}", "bytes": len(blob), "rec": rec, "hartree_hist": eh,
                    "hartree_safe": es}
        mg *= 0.995
    return None


# ----------------------------------------------------------------------------------------------- moments
def certify_m(S, B, m, rec_r, mu_ref, floor, natoms, lossless_m, work):
    """S2b's decoded-frame moment certificate at TAU_MU: best of ZFP/SZ3/SPERR against the moments read on the
    partition of rec_r, final verification by the binary. Returns (bytes or None, codec, error)."""
    s1, core, m_search = S["s1"], S["core"], S["m_search"]
    if floor >= TAU_MU:
        return None, "not eligible", None
    mu_d, atom_d = B(m, rec_r, "dec")
    ptp_m = float(np.ptp(m)) or 1.0
    cands = []
    for c in s1.CODECS:
        b = m_search(c, m, ptp_m, lambda r: float(np.max(np.abs(s1.sums(r, atom_d, natoms) - mu_ref))) < TAU_MU,
                     core, work)
        if b is not None:
            cands.append((b[0], c, b[1]))
    for nb, c, rec in sorted(cands, key=lambda z: z[0]):
        if nb >= lossless_m:
            break
        mu_j, _ = B(rec, rec_r, "dec")
        ej = float(np.max(np.abs(mu_j - mu_ref)))
        if ej < TAU_MU:
            return nb, c, ej
    return None, "no certified point", None


# ----------------------------------------------------------------------------------------------- one object
def process(row: dict, blob_path: Path, S: dict, bader: Path) -> dict:
    s1, RC, v02, v3 = S["s1"], S["RC"], S["v02"], S["v3"]
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
        prep = RC.F.prepare_field(rho, lat)
        an = None
        with tempfile.TemporaryDirectory(prefix="arch_trunc_") as td:
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
                        if w == "T":
                            res = writer_T(S, prep, rho, lat, rh, rs, ptp, tau)
                        else:
                            if an is None:
                                an = v3.analyze(rho, lat, prior="operator", reference_historical_rms=rh,
                                                d_floor_rel=1e-3 * min(RC.TAUS) ** 2 / 32)
                            res = writer_O(S, an, rho, lat, rh, rs, tau)
                        if res is not None:
                            r.update(certified=True, rho_bytes=int(res["bytes"]), param=res["param"],
                                     hartree_hist=res["hartree_hist"], hartree_safe=res["hartree_safe"])
                            rec_r = res["rec"]
                    nb, codec, err = certify_m(S, B, m, rec_r, mu_ref, floor, natoms, out["lossless_m"], work)
                    r.update(m_decframe_bytes=nb, m_codec=codec, m_err_binary=err, seconds=time.time() - ts)
                    out["results"][f"{w}_{tkey(tau)}"] = r
                    print("ARCHT", row["task_id"], w, tkey(tau), r["certified"], r["rho_bytes"], codec, flush=True)
    except Exception as e:  # noqa: BLE001
        out.update(status="FAILED", error=f"{type(e).__name__}: {e}"[:500], traceback=traceback.format_exc()[-2000:])
    out["wall_seconds"] = time.time() - t0
    return out


# ----------------------------------------------------------------------------------------------- aggregate
def _tot(x, idx):
    return sum(N_FRAME[h] / len(ix) * x[ix].sum() for h, ix in idx.items())


def _read(path: Path):
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def aggregate(ckpt_dir: Path, repo: Path, out: Path) -> dict:
    se = repo / "analysis" / "scope_expansion_20261022"
    har = _read(se / "archive_hartree_objects.csv")
    s2 = {r["task_id"]: r for r in _read(se / "results" / "s2_archive_whole_object" / "objects_spin_store.csv")}
    s2b = {r["task_id"]: r for r in _read(se / "results" / "s2b_archive_hartree_decframe" / "objects.csv")}
    s2c = {r["task_id"]: r for r in _read(se / "results" / "s2c_archive_hartree_decframe_1e-4" / "objects.csv")}
    s2d = {r["task_id"]: r for r in _read(se / "results" / "s2d_archive_pointwise_decframe_1e-6" / "objects.csv")}
    ck = {}
    for p in sorted(ckpt_dir.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        ck[d["task_id"]] = d
    assert len(har) == 300
    strata = np.array([r["stratum"] for r in har])
    idx = {h: np.flatnonzero(strata == h) for h in N_FRAME}
    js = np.array([float(r["frame_bytes"]) for r in har])

    def m_map(t):                                   # reference atom map + reference-frame m (S2)
        r = s2[t]
        return float(r["m_store_0.01"]) + float(r["label_atom_xz_bytes"])

    def m_hybrid(dec_row):                          # decoded-frame m where it certifies, else map + S2 m
        return lambda t: (float(dec_row[t]["m_store_0.01"]) if dec_row.get(t, {}).get("status") == "OK"
                          and dec_row[t]["m_codec_0.01"] in ("zfp", "sz3", "sperr") else m_map(t))

    stored = {}
    failed = {}
    for tau in TAUS_H:
        k = tkey(tau)
        # L: recorded law streams (as the published estimate) + hybrid m from S2b (1e-6) / S2c (1e-4)
        mL = m_hybrid(s2b if tau == 1e-6 else s2c)
        stored[("L", k)] = np.array([float(r[f"stored_L_{k}"]) + mL(r["task_id"]) for r in har])
        if tau == 1e-6:                             # P: recorded pointwise streams + hybrid m from S2d
            mP = m_hybrid(s2d)
            stored[("P", k)] = np.array([float(r[f"stored_P_{k}"]) + mP(r["task_id"]) for r in har])
        for w in WRITERS:
            vals, nf = [], 0
            for r in har:
                c = ck.get(r["task_id"])
                if c is None or c["status"] != "SUCCESS":
                    vals.append(float(r["frame_bytes"]))     # failed object: its current json.gz bytes (WP-F rule)
                    nf += 1
                    continue
                x = c["results"][f"{w}_{k}"]
                m_b = x["m_decframe_bytes"] if x["m_decframe_bytes"] is not None else m_map(r["task_id"])
                vals.append(float(x["rho_bytes"]) + float(m_b))
            stored[(w, k)] = np.array(vals)
            failed[(w, k)] = nf
    names = sorted(stored)
    point = {n: _tot(js, idx) / _tot(stored[n], idx) for n in names}
    rng = np.random.default_rng(SEED)
    boot = {n: np.empty(NBOOT) for n in names}
    for b in range(NBOOT):
        ib = {h: rng.choice(ix, size=len(ix), replace=True) for h, ix in idx.items()}
        tj = _tot(js, ib)
        for n in names:
            boot[n][b] = tj / _tot(stored[n], ib)
    ci = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]  # noqa: E731
    summ = {"objects_checkpointed": len(ck), "objects_success": sum(c["status"] == "SUCCESS" for c in ck.values()),
            "tau_mu_muB": TAU_MU, "seed": SEED, "resamples": NBOOT, "estimates": {}, "paired": {}}
    for (w, k) in names:
        summ["estimates"][f"{w}_{k}"] = {"R": point[(w, k)], "ci95": ci(boot[(w, k)]),
                                         "objects_failed_as_json": failed.get((w, k), 0)}
    for k in (tkey(t) for t in TAUS_H):
        for a, bb in (("L", "T"), ("O", "T"), ("O", "L"), ("T", "P"), ("O", "P"), ("L", "P")):
            if (a, k) in point and (bb, k) in point:
                summ["paired"][f"{a}/{bb}_{k}"] = {"ratio": point[(a, k)] / point[(bb, k)],
                                                   "ci95": ci(boot[(a, k)] / boot[(bb, k)])}
    for w in WRITERS:
        for k in (tkey(t) for t in TAUS_H):
            xs = [c["results"][f"{w}_{k}"] for c in ck.values() if c["status"] == "SUCCESS"]
            summ[f"counts_{w}_{k}"] = {"eligible": sum(x["eligible"] for x in xs),
                                        "certified": sum(x["certified"] for x in xs),
                                        "m_decoded_frame": sum(x["m_decframe_bytes"] is not None for x in xs)}
    out.mkdir(parents=True, exist_ok=True)
    with (out / "objects.csv").open("w", newline="", encoding="utf-8") as fh:
        cols = ["task_id", "stratum", "status", "npoints"] + [f"{w}_{tkey(t)}_{f}" for t in TAUS_H for w in WRITERS
                                                              for f in ("certified", "rho_bytes", "param", "m_bytes",
                                                                        "m_codec")]
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for r in har:
            c = ck.get(r["task_id"], {"status": "MISSING", "results": {}})
            row = {"task_id": r["task_id"], "stratum": r["stratum"], "status": c["status"], "npoints": c.get("npoints")}
            for t in TAUS_H:
                for w in WRITERS:
                    x = c["results"].get(f"{w}_{tkey(t)}", {})
                    row.update({f"{w}_{tkey(t)}_certified": x.get("certified"), f"{w}_{tkey(t)}_rho_bytes": x.get("rho_bytes"),
                                f"{w}_{tkey(t)}_param": x.get("param"), f"{w}_{tkey(t)}_m_bytes": x.get("m_decframe_bytes"),
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
    r.add_argument("--inputs", type=Path, required=True, help="prefetched <task_id>.json.gz and MANIFEST.tsv")
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
    rows = {x["task_id"]: x for x in _read(a.repo_root / "analysis" / "scope_expansion_20261022" /
                                             "archive_hartree_objects.csv")}
    row = rows[a.task_id]
    a.checkpoints.mkdir(parents=True, exist_ok=True)
    ck = a.checkpoints / f"{a.task_id}.json"
    if ck.exists() and json.loads(ck.read_text(encoding="utf-8")).get("status") == "SUCCESS":
        print("SKIP complete", a.task_id)
        return 0
    S = load_stack(a.repo_root.resolve(), a.frozen_root.resolve())
    rec = process(row, a.inputs / f"{a.task_id}.json.gz", S, a.bader)
    tmp = ck.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=float) + "\n", encoding="utf-8")
    os.replace(tmp, ck)
    print("DONE", a.task_id, rec["status"], rec.get("error", ""))
    return 0 if rec["status"] == "SUCCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
