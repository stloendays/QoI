#!/usr/bin/env python3
"""WS-S S3: do the charge and moment contracts compose without storing the partition?

S1 certified m with rho exact; S2 carries the reference atom map so that the
moments stay defined when rho is stored lossy. S3 asks whether that map is
needed. Per material of the S1 engineering set, for the resolved valence Bader
contract (partition re-derived from the decoded rho, as in the main panel):

1. certified rho stream: ZFP/SZ3/SPERR, bisection on the bound for the largest
   bound whose resolved Bader charges meet tau_B (``bader CHGCAR(rho') -ref
   REFCAR(rho')``); the best codec (fewest bytes) is kept;
2. moments on the decoded partition, with m exact and with m stored at the S1
   moment contract (bisection on m's bound against reference-partition sums):
   ``bader CHGCAR(m or m') -ref REFCAR(rho')``;
3. record the per-atom moment error, the gross charge carried by voxels whose
   atom assignment changed, and whether the joint error stays below tau_mu.

Physics note: for collinear spin |m| <= rho voxel by voxel, so the moment error
caused by partition migration is bounded by the *gross* migrated charge, which
the charge certificate (a bound on the *net* per-atom change) does not control.
S3 measures how large the gap is in practice. Descriptive; no gate.
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
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_spin_s1 as s1  # noqa: E402

TAUS_B = (1e-2, 1e-3)          # e
TAUS_MU = (1e-2, 1e-3)         # mu_B
FIELDS = ["material_id", "formula", "magnetic", "npoints", "natoms", "tau_B_e", "tau_mu_muB", "status", "error",
          "rho_codec", "rho_bytes", "rho_q_err_e", "gross_migrated_charge_e", "migrated_voxels",
          "mu_err_m_exact_muB", "mu_err_joint_muB", "m_codec", "m_bytes", "joint_certified_without_map",
          "m_codec_decframe", "m_bytes_decframe", "mu_err_joint_decframe_muB", "joint_certified_decframe",
          "bader_solves"]


def search(codec, field, ptp, ok, core, work, steps=s1.STEPS):
    lo, hi = math.log10(s1.REL_LO), math.log10(s1.REL_HI)
    best = None
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        rec, nb, _ = core.codec_roundtrip(codec, field, 10 ** mid * ptp, work)
        rec = np.asarray(rec, dtype=np.float64)
        if ok(rec):
            best = (int(nb), rec)
            lo = mid
        else:
            hi = mid
    return best


def run_material(meta: dict, bader: Path, frozen: Path) -> dict:
    sys.path.insert(0, str(frozen / "validation"))
    import external_end_to_end as core
    mid = meta["material_id"]
    res = {"material_id": mid, "status": "SUCCESS", "rows": [], "failures": []}
    t0 = time.time()
    try:
        blob = s1.fetch(meta["url"])
        if hashlib.sha256(blob).hexdigest() != meta["sha256"]:
            raise RuntimeError("sha256 mismatch against manifest")
        d = s1.decode(blob)
        rho, m = d["rho"], d["m"]
        n = len(d["symbols"])
        with tempfile.TemporaryDirectory(prefix="ws_s3_") as td:
            B = s1.Bader(bader, d["lattice"], d["frac"], d["symbols"], rho.shape, Path(td))
            work = Path(td) / "codec"
            work.mkdir()
            q_ref, atom_ref = B(rho, rho, "ref")
            mu_ref, _ = B(m, rho, "ref")
            charge = rho / rho.size
            ptp_r, ptp_m = float(np.ptp(rho)) or 1.0, float(np.ptp(m)) or 1.0
            counter = [0]

            for tau_b in TAUS_B:
                cands = []
                for codec in s1.CODECS:
                    def ok(rec):
                        counter[0] += 1
                        q, _ = B(rec, rec, f"cand{counter[0]}")
                        return float(np.max(np.abs(q - q_ref))) < tau_b
                    b = search(codec, rho, ptp_r, ok, core, work)
                    if b is not None:
                        cands.append((b[0], codec, b[1]))
                base = {"material_id": mid, "formula": meta.get("formula", ""), "magnetic": meta.get("magnetic"),
                        "npoints": rho.size, "natoms": n, "tau_B_e": tau_b}
                if not cands:
                    for tau_mu in TAUS_MU:
                        res["rows"].append({**base, "tau_mu_muB": tau_mu, "status": "NO_CERTIFIED_RHO"})
                    continue
                nb_r, codec_r, rec_r = min(cands, key=lambda c: c[0])
                counter[0] += 1
                q_d, atom_d = B(rec_r, rec_r, f"best{counter[0]}")
                moved = np.asarray(atom_d) != np.asarray(atom_ref)
                gross = float(np.abs(charge[moved]).sum())
                mu_d, _ = B(m, rec_r, f"best{counter[0]}")
                for tau_mu in TAUS_MU:
                    row = {**base, "tau_mu_muB": tau_mu, "status": "OK", "error": "", "rho_codec": codec_r,
                           "rho_bytes": nb_r, "rho_q_err_e": float(np.max(np.abs(q_d - q_ref))),
                           "gross_migrated_charge_e": gross, "migrated_voxels": int(moved.sum()),
                           "mu_err_m_exact_muB": float(np.max(np.abs(mu_d - mu_ref)))}
                    try:
                        mc = []
                        for codec in s1.CODECS:
                            b = search(codec, m, ptp_m, lambda rec: float(np.max(np.abs(
                                s1.sums(rec, atom_ref, n) - mu_ref))) < tau_mu, core, work)
                            if b is not None:
                                mc.append((b[0], codec, b[1]))
                        if mc:
                            nb_m, codec_m, rec_m = min(mc, key=lambda c: c[0])
                            mu_j, _ = B(rec_m, rec_r, f"best{counter[0]}")
                            ej = float(np.max(np.abs(mu_j - mu_ref)))
                            row.update(m_codec=codec_m, m_bytes=nb_m, mu_err_joint_muB=ej,
                                       joint_certified_without_map=bool(ej < tau_mu))
                        else:
                            row.update(status="NO_CERTIFIED_M")
                        # decoded-frame variant: the encoder knows rho' and therefore the partition a user will
                        # derive, so it certifies m' against the moments read on that partition directly
                        md = []
                        for codec in s1.CODECS:
                            b = search(codec, m, ptp_m, lambda rec: float(np.max(np.abs(
                                s1.sums(rec, atom_d, n) - mu_ref))) < tau_mu, core, work)
                            if b is not None:
                                md.append((b[0], codec, b[1]))
                        if md:
                            nb_d, codec_d, rec_d = min(md, key=lambda c: c[0])
                            mu_jd, _ = B(rec_d, rec_r, f"best{counter[0]}")
                            ejd = float(np.max(np.abs(mu_jd - mu_ref)))
                            row.update(m_codec_decframe=codec_d, m_bytes_decframe=nb_d,
                                       mu_err_joint_decframe_muB=ejd, joint_certified_decframe=bool(ejd < tau_mu))
                    except Exception as e:  # noqa: BLE001
                        row.update(status="FAILED", error=f"{type(e).__name__}: {e}")
                        res["failures"].append({"stage": f"tau_B={tau_b} tau_mu={tau_mu}", "error": row["error"],
                                                "traceback": traceback.format_exc()})
                    row["bader_solves"] = B.n
                    res["rows"].append(row)
    except Exception as e:  # noqa: BLE001
        res["status"] = "FAILED"
        res["failures"].append({"stage": "material", "error": f"{type(e).__name__}: {e}",
                                "traceback": traceback.format_exc()})
    res["wall_seconds"] = time.time() - t0
    return res


def write(rows, path: Path):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def aggregate(results: list[dict]) -> dict:
    rows = [r for res in results for r in res["rows"]]
    out = {"materials": len(results), "failures": sum(len(r["failures"]) for r in results), "groups": {}}
    for tb in TAUS_B:
        for tm in TAUS_MU:
            for mag in ("True", "False"):
                g = [r for r in rows if r["tau_B_e"] == tb and r["tau_mu_muB"] == tm and str(r["magnetic"]) == mag
                     and r["status"] == "OK" and r.get("mu_err_joint_muB") is not None]
                if not g:
                    continue
                out["groups"][f"tau_B={tb:g}|tau_mu={tm:g}|magnetic={mag}"] = {
                    "n": len(g),
                    "joint_certified_without_map": sum(bool(r["joint_certified_without_map"]) for r in g),
                    "joint_certified_decframe": sum(bool(r.get("joint_certified_decframe")) for r in g),
                    "median_m_bytes_decframe_over_refframe": float(np.median([r["m_bytes_decframe"] / r["m_bytes"]
                                                                               for r in g if r.get("m_bytes_decframe")])) if any(r.get("m_bytes_decframe") for r in g) else None,
                    "median_mu_err_m_exact_over_tau_mu": float(np.median([r["mu_err_m_exact_muB"] / tm for r in g])),
                    "max_mu_err_m_exact_muB": max(r["mu_err_m_exact_muB"] for r in g),
                    "median_gross_migrated_charge_e": float(np.median([r["gross_migrated_charge_e"] for r in g])),
                    "max_rho_q_err_e": max(r["rho_q_err_e"] for r in g),
                }
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--index", type=int, required=True)
    r.add_argument("--bader", type=Path, required=True)
    r.add_argument("--frozen-root", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--inputs", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        man = list(csv.DictReader(args.manifest.read_text(encoding="utf-8").splitlines()))
        meta = man[args.index]
        res = run_material(meta, args.bader, args.frozen_root.resolve())
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / f"{meta['material_id']}.json").write_text(json.dumps(res, indent=2, default=s1._json_default) + "\n")
        write(res["rows"], args.out / f"{meta['material_id']}_rows.csv")
        print("WS_S3_DONE", meta["material_id"], res["status"], len(res["rows"]), "failures", len(res["failures"]))
        return 0
    results = []
    for p in sorted(args.inputs.rglob("*.json")):
        try:
            dd = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(dd, dict) and "rows" in dd and "material_id" in dd:
            results.append(dd)
    args.out.mkdir(parents=True, exist_ok=True)
    write([r for res in results for r in res["rows"]], args.out / "rows.csv")
    summ = aggregate(results)
    (args.out / "SUMMARY.json").write_text(json.dumps(summ, indent=2, default=s1._json_default) + "\n")
    with (args.out / "failures.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["material_id", "stage", "error"])
        w.writeheader()
        for res in results:
            for f in res["failures"]:
                w.writerow({"material_id": res["material_id"], "stage": f["stage"], "error": f["error"]})
    print(json.dumps(summ, indent=1, default=s1._json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
