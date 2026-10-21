#!/usr/bin/env python3
"""WS-S S2: whole-object archive estimate with the magnetization block certified.

Same frame, stratified 300-object sample, storage rule and stratified expansion
estimator as WP-F and the archive-Hartree run. Per object, the charge-density
block keeps its published stored size (taken from the committed object tables);
this script adds the magnetization block m under the per-atom moment contract
of WS-S1 (compiled Henkelman, ``bader CHGCAR(m) -ref REFCAR(rho) -b ongrid
-vac 0.001``):

* QSQ moment floor with the five frozen seeds (rho and m both perturbed at
  their float32 round-trip amplitude); eligible(tau_mu) := floor < tau_mu;
* if eligible: best certified m stream over ZFP/SZ3/SPERR (bisection on the
  bound, moments by per-atom sums over the reference AtIndex map, final point
  re-run through the binary); otherwise, or if nothing certifies, m is stored
  losslessly (zlib-6 float64), as in the frozen storage rule.

``aggregate`` reports, per contract and tolerance pair,

  R_whole = T_json / (T_stored_rho + T_stored_m)

with stratified bootstrap intervals (seed of the respective archive protocol).
Objects whose charge-density pipeline failed keep their current file, which
already contains m, so they add no m bytes. Descriptive; no gate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
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

TAUS_MU = (1e-2, 1e-3)
N_FRAME = {"D01": 41527, "D02": 41531, "D03": 41529, "D04": 41529, "D05": 41528, "D06": 41529,
           "D07": 41529, "D08": 41529, "D09": 41529, "D10a": 33105, "D10b": 6741, "D10c": 1683}
FIELDS = ["task_id", "stratum", "status", "error", "npoints", "natoms", "max_abs_moment_muB", "floor_muB",
          "lossless_m", "lossless_rho"] + [f"{k}_{t:g}" for t in TAUS_MU for k in
                                          ("eligible", "m_store", "m_codec", "m_err_binary")] + ["bader_solves",
                                                                                                 "wall_seconds"]


def process(row: dict, bader: Path, frozen: Path) -> dict:
    sys.path.insert(0, str(frozen / "validation"))
    import external_end_to_end as core
    t0 = time.time()
    out = {"task_id": row["task_id"], "stratum": row["stratum"], "status": "OK", "error": ""}
    try:
        blob = s1.fetch(row["url"])
        if len(blob) != int(row["frame_bytes"]):
            raise RuntimeError("size mismatch against the frame")
        d = s1.decode(blob)
        del blob
        rho, m = d["rho"], d["m"]
        natoms = len(d["symbols"])
        out.update(npoints=int(rho.size), natoms=natoms,
                   lossless_m=len(zlib.compress(m.tobytes(), 6)), lossless_rho=len(zlib.compress(rho.tobytes(), 6)))
        with tempfile.TemporaryDirectory(prefix="ws_s2_") as td:
            B = s1.Bader(bader, d["lattice"], d["frac"], d["symbols"], rho.shape, Path(td))
            mu_ref, atom_ref = B(m, rho, "ref")
            e_r, e_m = s1.f32_eps(rho), s1.f32_eps(m)
            floor = 0.0
            for s in s1.SEEDS:
                rng = np.random.default_rng(s)
                mu_p, _ = B(m + rng.uniform(-e_m, e_m, m.shape), rho + rng.uniform(-e_r, e_r, rho.shape), f"p{s}")
                floor = max(floor, float(np.max(np.abs(mu_p - mu_ref))))
            out.update(max_abs_moment_muB=float(np.max(np.abs(mu_ref))), floor_muB=floor)
            ptp = float(np.ptp(m)) or 1.0
            work = Path(td) / "codec"
            work.mkdir()
            for tau in TAUS_MU:
                el = floor < tau
                out[f"eligible_{tau:g}"] = el
                out[f"m_store_{tau:g}"] = out["lossless_m"]
                out[f"m_codec_{tau:g}"] = "lossless (non-evaluable)" if not el else "lossless (no certified point)"
                if not el:
                    continue
                cands = []
                for codec in s1.CODECS:
                    lo, hi = math.log10(s1.REL_LO), math.log10(s1.REL_HI)
                    best = None
                    for _ in range(s1.STEPS):
                        mid = 0.5 * (lo + hi)
                        rec, nb, _ = core.codec_roundtrip(codec, m, 10 ** mid * ptp, work)
                        rec = np.asarray(rec, dtype=np.float64)
                        err = float(np.max(np.abs(s1.sums(rec, atom_ref, natoms) - mu_ref)))
                        if err < tau:
                            best = (int(nb), codec, rec)
                            lo = mid
                        else:
                            hi = mid
                    if best is not None:
                        cands.append(best)
                for nb, codec, rec in sorted(cands, key=lambda c: c[0]):
                    if nb >= out["lossless_m"]:
                        break
                    mu_b, _ = B(rec, rho, "ref")
                    eb = float(np.max(np.abs(mu_b - mu_ref)))
                    if eb < tau:
                        out[f"m_store_{tau:g}"] = nb
                        out[f"m_codec_{tau:g}"] = codec
                        out[f"m_err_binary_{tau:g}"] = eb
                        break
            out["bader_solves"] = B.n
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


def aggregate(mrows, wpf_csv: Path, hartree_csv: Path, B: int = 2000) -> dict:
    meas = {r["task_id"]: r for r in mrows}
    specs = [("bader", wpf_csv, "stored_0.001", "Bader 1e-3 e", 20260930),
             ("bader", wpf_csv, "stored_0.01", "Bader 1e-2 e", 20260930),
             ("hartree", hartree_csv, "stored_L_1e-06", "Hartree law 1e-6", 20261012),
             ("hartree", hartree_csv, "stored_L_0.0001", "Hartree law 1e-4", 20261012),
             ("hartree", hartree_csv, "stored_P_1e-06", "Hartree pointwise 1e-6", 20261012)]
    ok = [r for r in mrows if r["status"] == "OK"]
    summ = {"objects_measured": len(ok), "objects_failed": len(mrows) - len(ok), "estimates": []}
    for tau in TAUS_MU:
        summ[f"eligible_fraction_{tau:g}"] = float(np.mean([str(r[f"eligible_{tau:g}"]) == "True" for r in ok])) if ok else None
        summ[f"certified_fraction_{tau:g}"] = float(np.mean([r[f"m_codec_{tau:g}"] in s1.CODECS for r in ok])) if ok else None
    for contract, path, col, label, seed in specs:
        rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
        strata = np.array([r["stratum"] for r in rows])
        idx = {h: np.flatnonzero(strata == h) for h in N_FRAME}
        json_b = np.array([float(r["frame_bytes"]) for r in rows])
        stored = np.array([float(r[col]) if r.get(col) not in (None, "") else float(r["frame_bytes"]) for r in rows])
        failed = np.array([r.get("status", "SUCCESS") != "SUCCESS" for r in rows])
        for tau in TAUS_MU:
            missing = 0
            mstore = np.zeros(len(rows))
            for i, r in enumerate(rows):
                mr = meas.get(r["task_id"])
                if failed[i]:
                    continue
                if mr is None or mr["status"] != "OK":
                    missing += 1
                    mstore[i] = np.nan
                    continue
                mstore[i] = float(mr[f"m_store_{tau:g}"])
            if missing:
                # unmeasured objects: m kept losslessly at the median lossless(m)/frame ratio of measured ones
                ratio = np.nanmedian([float(meas[r["task_id"]]["lossless_m"]) / float(r["frame_bytes"])
                                      for r in rows if r["task_id"] in meas and meas[r["task_id"]]["status"] == "OK"])
                mstore = np.where(np.isnan(mstore), ratio * json_b, mstore)
            point = _tot(json_b, idx) / (_tot(stored, idx) + _tot(mstore, idx))
            rng = np.random.default_rng(seed)
            bs = np.empty(B)
            for b in range(B):
                ib = {h: rng.choice(ix, size=len(ix), replace=True) for h, ix in idx.items()}
                bs[b] = _tot(json_b, ib) / (_tot(stored, ib) + _tot(mstore, ib))
            lo, hi = np.percentile(bs, [2.5, 97.5])
            summ["estimates"].append({"contract": label, "tau_mu": tau, "objects_unmeasured": missing,
                                      "R_published": _tot(json_b, idx) / _tot(stored, idx),
                                      "R_whole": point, "R_whole_ci": [lo, hi]})
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
    r.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--inputs", type=Path, required=True)
    a.add_argument("--wpf", type=Path, required=True)
    a.add_argument("--hartree", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        rows = list(csv.DictReader(args.objects.read_text(encoding="utf-8").splitlines()))
        rows.sort(key=lambda x: -int(x["frame_bytes"]))
        args.out.mkdir(parents=True, exist_ok=True)
        res = []
        for row in rows[args.shard::args.nshards]:
            rec = process(row, args.bader, args.frozen_root.resolve())
            print("S2", rec["task_id"], rec["stratum"], rec["status"], rec.get("floor_muB"),
                  rec.get("m_codec_0.01"), flush=True)
            res.append(rec)
            write(res, args.out / f"s2_shard{args.shard:02d}.csv")   # incremental: survives a timeout
        return 0
    rows = []
    for p in sorted(args.inputs.rglob("s2_shard*.csv")):
        rows.extend(csv.DictReader(p.read_text(encoding="utf-8").splitlines()))
    args.out.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda x: (x["stratum"], x["task_id"]))
    write(rows, args.out / "objects_spin_store.csv")
    summ = aggregate(rows, args.wpf, args.hartree)
    (args.out / "SUMMARY.json").write_text(json.dumps(summ, indent=2) + "\n", encoding="utf-8")
    lines = ["# WS-S2 — whole-object archive estimate with the magnetization block certified", "",
             f"Objects measured {summ['objects_measured']}/300 (failed {summ['objects_failed']}). "
             f"Moment contract eligible: {summ['eligible_fraction_0.01']:.3f} at 1e-2 mu_B, "
             f"{summ['eligible_fraction_0.001']:.3f} at 1e-3 mu_B; certified m stream: "
             f"{summ['certified_fraction_0.01']:.3f} / {summ['certified_fraction_0.001']:.3f}.", "",
             "| charge-density contract | m contract (mu_B) | R published (rho block only stored) | R whole object (rho + m stored) [95% CI] | unmeasured |",
             "|---|---|---|---|---|"]
    for e in summ["estimates"]:
        lines.append(f"| {e['contract']} | {e['tau_mu']:g} | {e['R_published']:.3g} | {e['R_whole']:.3g} "
                     f"[{e['R_whole_ci'][0]:.3g}, {e['R_whole_ci'][1]:.3g}] | {e['objects_unmeasured']} |")
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
