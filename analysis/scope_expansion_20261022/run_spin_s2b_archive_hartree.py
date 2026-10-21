#!/usr/bin/env python3
"""WS-S S2b: whole-object Hartree archive estimate with decoded-frame moments (no stored map).

For each of the 300 frozen archive-sample objects:

1. regenerate the closed-form law's certified rho' stream at tau_H = 1e-6 with
   the committed search (``run_cost.search('A1', ...)``, rev5 tree) and check
   its size against the recorded ``writer_L_stream_bytes_1e-06``;
2. derive the Bader partition of rho' with the compiled binary;
3. certify m against the moments read on that decoded partition (best of
   ZFP/SZ3/SPERR; tau_mu in {1e-2, 1e-3} mu_B), with the QSQ gate from S2 and
   final verification by the binary; lossless m where not eligible or not
   certifiable.

``aggregate`` gives R_whole_decframe = T_json / (T_stored_L + T_m) with the
frozen estimator and seed 20261012, next to the published rho-only ratio.
Descriptive; no gate.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
import time
import traceback
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_spin_s1 as s1  # noqa: E402
from run_spin_s3_joint import search  # noqa: E402

import os
TAU_H = float(os.environ.get("S2B_TAU_H", "1e-6"))
WRITER = os.environ.get("S2B_WRITER", "A1")   # A1 = closed-form law (L); A6 = best pointwise codec (P)
WCOL = "L" if WRITER == "A1" else "P"
TAUS_MU = (1e-2, 1e-3)
N_FRAME = {"D01": 41527, "D02": 41531, "D03": 41529, "D04": 41529, "D05": 41528, "D06": 41529,
           "D07": 41529, "D08": 41529, "D09": 41529, "D10a": 33105, "D10b": 6741, "D10c": 1683}
FIELDS = ["task_id", "stratum", "status", "error", "npoints", "law_bytes", "law_bytes_recorded", "law_param",
          "floor_muB", "lossless_m", "mu_err_migration_muB"] + \
         [f"{k}_{t:g}" for t in TAUS_MU for k in ("m_store", "m_codec", "m_err_binary")] + ["wall_seconds"]


def process(row: dict, bader: Path, frozen: Path, lawrepo: Path) -> dict:
    sys.path.insert(0, str(frozen / "validation"))
    import external_end_to_end as core
    sys.path.insert(0, str(lawrepo / "analysis" / "deployment_cost_20261012"))
    import run_cost as RC
    v02, _ = RC.lazy()
    t0 = time.time()
    out = {"task_id": row["task_id"], "stratum": row["stratum"], "status": "OK", "error": "",
           "law_bytes_recorded": row.get(f"writer_{WCOL}_stream_bytes_{TAU_H:g}" if TAU_H != 1e-4 else f"writer_{WCOL}_stream_bytes_0.0001", "")}
    try:
        blob = s1.fetch(row["url"])
        if len(blob) != int(row["frame_bytes"]):
            raise RuntimeError("size mismatch against the frame")
        d = s1.decode(blob)
        del blob
        rho, m = d["rho"], d["m"]
        lat, n = d["lattice"], len(d["symbols"])
        out.update(npoints=int(rho.size), lossless_m=len(zlib.compress(m.tobytes(), 6)))
        rh, rs = v02.reference_hartree_rms(rho, lat)
        ptp = float(np.ptp(rho))
        with tempfile.TemporaryDirectory(prefix="ws_s2b_") as td:
            work = Path(td) / "codec"
            work.mkdir()
            sr = RC.search(WRITER, TAU_H, rho, lat, rh, rs, ptp, work)
            if not sr.get("bytes"):
                raise RuntimeError(f"{WRITER} search returned no certified stream")
            if WRITER == "A1":
                a_rel = float(sr["param"].split("=")[1])
                lb = v02.encode_prepared(v02.prepare_field(rho, lat, shell_count=32), alpha=a_rel * ptp, beta=2.0,
                                         zlib_level=6)[0]
                rec_r = np.ascontiguousarray(RC.F.decode_law(lb), dtype=np.float64)
                nbytes = len(lb)
            else:
                kv = dict(x.split("=") for x in sr["param"].split(";"))
                stream = RC.pointwise_encode(kv["codec"], rho, float(kv["abs_tol_rel"]) * ptp, work)
                nbytes = RC.pointwise_bytes(kv["codec"], stream)
                rec_r = np.ascontiguousarray(RC.pointwise_decode(kv["codec"], stream, rho.shape), dtype=np.float64)
            eh, es = RC.certify(rec_r, rho, lat, rh, rs)
            if not (eh < TAU_H and es < TAU_H):
                raise RuntimeError("regenerated stream not certified")
            out.update(law_bytes=nbytes, law_param=sr["param"])
            B = s1.Bader(bader, lat, d["frac"], d["symbols"], rho.shape, Path(td))
            mu_ref, _ = B(m, rho, "ref")
            e_r, e_m = s1.f32_eps(rho), s1.f32_eps(m)
            floor = 0.0
            for s in s1.SEEDS:
                rng = np.random.default_rng(s)
                mu_p, _ = B(m + rng.uniform(-e_m, e_m, m.shape), rho + rng.uniform(-e_r, e_r, rho.shape), f"p{s}")
                floor = max(floor, float(np.max(np.abs(mu_p - mu_ref))))
            out["floor_muB"] = floor
            mu_d, atom_d = B(m, rec_r, "law")
            out["mu_err_migration_muB"] = float(np.max(np.abs(mu_d - mu_ref)))
            ptp_m = float(np.ptp(m)) or 1.0
            for tm in TAUS_MU:
                out[f"m_store_{tm:g}"] = out["lossless_m"]
                out[f"m_codec_{tm:g}"] = "lossless (non-evaluable)" if floor >= tm else "lossless (no certified point)"
                if floor >= tm:
                    continue
                cands = [(b[0], c, b[1]) for c in s1.CODECS if (b := search(c, m, ptp_m, lambda r: float(np.max(
                    np.abs(s1.sums(r, atom_d, n) - mu_ref))) < tm, core, work)) is not None]
                for nb, c, rec in sorted(cands, key=lambda x: x[0]):
                    if nb >= out["lossless_m"]:
                        break
                    mu_j, _ = B(rec, rec_r, "law")
                    ej = float(np.max(np.abs(mu_j - mu_ref)))
                    if ej < tm:
                        out[f"m_store_{tm:g}"] = nb
                        out[f"m_codec_{tm:g}"] = c
                        out[f"m_err_binary_{tm:g}"] = ej
                        break
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


def _tot(x, idx):
    return sum(N_FRAME[h] / len(ix) * x[ix].sum() for h, ix in idx.items())


def aggregate(mrows, hartree_csv: Path, B: int = 2000) -> dict:
    meas = {r["task_id"]: r for r in mrows}
    rows = list(csv.DictReader(hartree_csv.read_text(encoding="utf-8").splitlines()))
    strata = np.array([r["stratum"] for r in rows])
    idx = {h: np.flatnonzero(strata == h) for h in N_FRAME}
    json_b = np.array([float(r["frame_bytes"]) for r in rows])
    col = f"stored_{WCOL}_0.0001" if TAU_H == 1e-4 else f"stored_{WCOL}_{TAU_H:g}"
    stored = np.array([float(r[col]) for r in rows])
    ok = [r for r in mrows if r["status"] == "OK"]
    rep = [r for r in ok if r.get("law_bytes_recorded")]
    summ = {"tau_H": TAU_H, "writer": WRITER, "objects_measured": len(ok), "objects_failed": len(mrows) - len(ok),
            "law_bytes_equal_recorded": sum(str(r["law_bytes"]) == str(int(float(r["law_bytes_recorded"]))) for r in rep),
            "law_bytes_compared": len(rep), "estimates": []}
    for tm in TAUS_MU:
        unmeasured = 0
        ms = np.zeros(len(rows))
        for i, r in enumerate(rows):
            mr = meas.get(r["task_id"])
            if mr is None or mr["status"] != "OK":
                unmeasured += 1
                ms[i] = np.nan
            else:
                ms[i] = float(mr[f"m_store_{tm:g}"])
        if unmeasured:
            ratio = np.nanmedian([float(meas[r["task_id"]]["lossless_m"]) / float(r["frame_bytes"]) for r in rows
                                  if r["task_id"] in meas and meas[r["task_id"]]["status"] == "OK"])
            ms = np.where(np.isnan(ms), ratio * json_b, ms)   # unmeasured objects: m kept losslessly
        point = _tot(json_b, idx) / (_tot(stored, idx) + _tot(ms, idx))
        rng = np.random.default_rng(20261012)
        bs = np.empty(B)
        for b in range(B):
            ib = {h: rng.choice(ix, size=len(ix), replace=True) for h, ix in idx.items()}
            bs[b] = _tot(json_b, ib) / (_tot(stored, ib) + _tot(ms, ib))
        lo, hi = np.percentile(bs, [2.5, 97.5])
        certified = sum(meas[r["task_id"]][f"m_codec_{tm:g}"] in s1.CODECS for r in rows
                        if r["task_id"] in meas and meas[r["task_id"]]["status"] == "OK")
        summ["estimates"].append({"tau_mu": tm, "R_published_rho_only": _tot(json_b, idx) / _tot(stored, idx),
                                  "R_whole_decframe": point, "ci": [lo, hi], "m_certified_objects": certified,
                                  "objects_unmeasured": unmeasured})
    return summ


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--objects", type=Path, required=True)
    r.add_argument("--shard", type=int, required=True)
    r.add_argument("--nshards", type=int, required=True)
    r.add_argument("--bader", type=Path, required=True)
    r.add_argument("--frozen-root", type=Path, required=True)
    r.add_argument("--law-root", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--inputs", type=Path, required=True)
    a.add_argument("--hartree", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        rows = list(csv.DictReader(args.objects.read_text(encoding="utf-8").splitlines()))
        rows.sort(key=lambda x: -int(x["frame_bytes"]))
        args.out.mkdir(parents=True, exist_ok=True)
        res = []
        for row in rows[args.shard::args.nshards]:
            rec = process(row, args.bader, args.frozen_root.resolve(), args.law_root.resolve())
            print("S2B", rec["task_id"], rec["stratum"], rec["status"], rec.get("law_bytes"), rec.get("law_bytes_recorded"),
                  rec.get("m_codec_0.01"), flush=True)
            res.append(rec)
            write(res, args.out / f"s2b_shard{args.shard:02d}.csv")
        return 0
    rows = []
    for p in sorted(args.inputs.rglob("s2b_shard*.csv")):
        rows.extend(csv.DictReader(p.read_text(encoding="utf-8").splitlines()))
    args.out.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda x: (x["stratum"], x["task_id"]))
    write(rows, args.out / "objects.csv")
    summ = aggregate(rows, args.hartree)
    (args.out / "SUMMARY.json").write_text(json.dumps(summ, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summ, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
