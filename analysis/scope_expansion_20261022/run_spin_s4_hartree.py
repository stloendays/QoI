#!/usr/bin/env python3
"""WS-S S4: moments in the decoded frame when rho is stored by the closed-form Hartree law (A1).

S2's Hartree rows were certified for m on the reference partition, so the safe
whole-object ratio carried the atom map (232x instead of 317x at 1e-6). S3 v2
showed decoded-frame certification removes the map for Bader-certified rho'.
A Hartree-law rho' does not control the Bader partition at all, so this run
checks whether decoded-frame certification of m still works there.

Per material of the S1 engineering set and tau_H in {1e-6, 1e-4}:

1. rho' = the law's certified stream, produced by the deployment-cost search
   (``run_cost.search('A1', ...)`` on the rev5 tree, the committed implementation),
   decoded with the production decoder;
2. migration-only moment error: m exact read on the partition of rho' (binary);
   Bader charge error of rho' (informative: the law does not certify charges);
3. for tau_mu in {1e-2, 1e-3}: m' certified against moments on the decoded
   partition (python sums over the decoded AtIndex map, best of ZFP/SZ3/SPERR),
   verified by the binary; bytes compared with reference-frame certification.

Descriptive; no gate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import tempfile
import time
import traceback
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_spin_s1 as s1  # noqa: E402
from run_spin_s3_joint import search  # noqa: E402

TAUS_H = (1e-6, 1e-4)
TAUS_MU = (1e-2, 1e-3)
FIELDS = ["material_id", "formula", "magnetic", "npoints", "natoms", "tau_H", "tau_mu_muB", "status", "error",
          "law_param", "law_bytes", "law_bytes_over_lossless_rho", "rho_q_err_e", "migrated_voxels",
          "mu_err_migration_muB", "m_bytes_refframe", "m_bytes_decframe", "mu_err_joint_decframe_muB",
          "joint_certified_decframe", "label_atom_xz_bytes", "bader_solves"]


def run_material(meta: dict, bader: Path, frozen: Path, lawrepo: Path) -> dict:
    sys.path.insert(0, str(frozen / "validation"))
    import external_end_to_end as core
    sys.path.insert(0, str(lawrepo / "analysis" / "deployment_cost_20261012"))
    import run_cost as RC  # committed law search and production decoder (rev5 tree)
    import lzma
    import zlib
    v02, _ = RC.lazy()
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
        lat = d["lattice"]
        lossless_rho = len(zlib.compress(rho.tobytes(), 6))
        rh, rs = v02.reference_hartree_rms(rho, lat)
        ptp = float(np.ptp(rho))
        with tempfile.TemporaryDirectory(prefix="ws_s4_") as td:
            B = s1.Bader(bader, lat, d["frac"], d["symbols"], rho.shape, Path(td))
            work = Path(td) / "codec"
            work.mkdir()
            q_ref, atom_ref = B(rho, rho, "ref")
            mu_ref, _ = B(m, rho, "ref")
            ptp_m = float(np.ptp(m)) or 1.0
            label_bytes = len(lzma.compress(np.asarray(atom_ref, dtype="<u2").tobytes(), preset=9 | lzma.PRESET_EXTREME))
            for tau_h in TAUS_H:
                base = {"material_id": mid, "formula": meta.get("formula", ""), "magnetic": meta.get("magnetic"),
                        "npoints": rho.size, "natoms": n, "tau_H": tau_h, "label_atom_xz_bytes": label_bytes}
                try:
                    sr = RC.search("A1", tau_h, rho, lat, rh, rs, ptp, work)
                    if not sr.get("bytes"):
                        for tm in TAUS_MU:
                            res["rows"].append({**base, "tau_mu_muB": tm, "status": "NO_CERTIFIED_LAW"})
                        continue
                    a_rel = float(sr["param"].split("=")[1])
                    lb = v02.encode_prepared(v02.prepare_field(rho, lat, shell_count=32), alpha=a_rel * ptp,
                                             beta=2.0, zlib_level=6)[0]
                    rec_r = np.ascontiguousarray(RC.F.decode_law(lb), dtype=np.float64)
                    eh, es = RC.certify(rec_r, rho, lat, rh, rs)
                    if not (eh < tau_h and es < tau_h):
                        raise RuntimeError("regenerated law stream not certified")
                    q_d, atom_d = B(rec_r, rec_r, f"law{tau_h:g}")
                    mu_d, _ = B(m, rec_r, f"law{tau_h:g}")
                    common = {**base, "status": "OK", "error": "", "law_param": sr["param"], "law_bytes": len(lb),
                              "law_bytes_over_lossless_rho": len(lb) / lossless_rho,
                              "rho_q_err_e": float(np.max(np.abs(q_d - q_ref))),
                              "migrated_voxels": int(np.count_nonzero(np.asarray(atom_d) != np.asarray(atom_ref))),
                              "mu_err_migration_muB": float(np.max(np.abs(mu_d - mu_ref)))}
                    for tm in TAUS_MU:
                        row = dict(common, tau_mu_muB=tm)
                        rf = [b for c in s1.CODECS if (b := search(c, m, ptp_m, lambda r: float(np.max(np.abs(
                            s1.sums(r, atom_ref, n) - mu_ref))) < tm, core, work)) is not None]
                        if rf:
                            row["m_bytes_refframe"] = min(b[0] for b in rf)
                        df = [(b[0], b[1]) for c in s1.CODECS if (b := search(c, m, ptp_m, lambda r: float(np.max(np.abs(
                            s1.sums(r, atom_d, n) - mu_ref))) < tm, core, work)) is not None]
                        if df:
                            nb, rec_m = min(df, key=lambda x: x[0])
                            mu_j, _ = B(rec_m, rec_r, f"law{tau_h:g}")
                            ej = float(np.max(np.abs(mu_j - mu_ref)))
                            row.update(m_bytes_decframe=nb, mu_err_joint_decframe_muB=ej,
                                       joint_certified_decframe=bool(ej < tm))
                        else:
                            row.update(joint_certified_decframe=False)
                        row["bader_solves"] = B.n
                        res["rows"].append(row)
                except Exception as e:  # noqa: BLE001
                    res["failures"].append({"stage": f"tau_H={tau_h}", "error": f"{type(e).__name__}: {e}",
                                            "traceback": traceback.format_exc()})
                    for tm in TAUS_MU:
                        res["rows"].append({**base, "tau_mu_muB": tm, "status": "FAILED", "error": str(e)})
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


def aggregate(results):
    rows = [r for res in results for r in res["rows"]]
    out = {"materials": len(results), "failures": sum(len(r["failures"]) for r in results), "groups": {}}
    for th in TAUS_H:
        for tm in TAUS_MU:
            g = [r for r in rows if r["tau_H"] == th and r["tau_mu_muB"] == tm and r["status"] == "OK"]
            if not g:
                continue
            ratios = [r["m_bytes_decframe"] / r["m_bytes_refframe"] for r in g
                      if r.get("m_bytes_decframe") and r.get("m_bytes_refframe")]
            out["groups"][f"tau_H={th:g}|tau_mu={tm:g}"] = {
                "n": len(g), "joint_certified_decframe": sum(bool(r.get("joint_certified_decframe")) for r in g),
                "median_mu_err_migration_muB": float(np.median([r["mu_err_migration_muB"] for r in g])),
                "max_mu_err_migration_muB": max(r["mu_err_migration_muB"] for r in g),
                "median_rho_q_err_e": float(np.median([r["rho_q_err_e"] for r in g])),
                "median_decframe_over_refframe_bytes": float(np.median(ratios)) if ratios else None,
                "max_decframe_over_refframe_bytes": max(ratios) if ratios else None,
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
    r.add_argument("--law-root", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--inputs", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        man = list(csv.DictReader(args.manifest.read_text(encoding="utf-8").splitlines()))
        meta = man[args.index]
        res = run_material(meta, args.bader, args.frozen_root.resolve(), args.law_root.resolve())
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / f"{meta['material_id']}.json").write_text(json.dumps(res, indent=2, default=s1._json_default) + "\n")
        write(res["rows"], args.out / f"{meta['material_id']}_rows.csv")
        print("WS_S4_DONE", meta["material_id"], res["status"], len(res["rows"]), "failures", len(res["failures"]))
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
