#!/usr/bin/env python3
"""Hartree-contract strongest baselines M (MGARD, s = inf/0/-1/-2) and Q (QPET block-average QoI); see PROTOCOL.md.

Reused unchanged: the material loader (`development_compatibility_smoke.fetch_exact/build_grid`, exactly as in
`analysis/qoac_v03_rdo/run_engineering.py::material`, which `analysis/general_qoac_law/run_part_a.py` calls), the
decoded Hartree certificate (`run_engineering.certify` -> `codec_qoac_h_v02.hartree_error_metrics`) and the equal
search (`run_engineering.bisect_scale`, 60 log-space bisection iterations, as used by arms A1 and A6).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import tempfile
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qoac_v03_rdo"))
import run_engineering as eng  # noqa: E402
import codecs_mq as C  # noqa: E402

TAUS = (1e-4, 1e-6, 1e-8)
INTERVAL = {"M": (1e-14, 1e3), "Q": (1e-14, 1.0)}   # x ptp(rho): M = A1 interval, Q = A6 interval
LO_ERROR_CAP = 1e-2                                 # lower bound may be raised by decades on execution errors only
FRESH = "analysis/fresh_population_20261006"
LAW = "analysis/general_qoac_law/results"
COHORTS = {"P1_CONFIRMATORY": f"{FRESH}/P1_CONFIRMATORY_MANIFEST.csv",
           "P3B_CONFIRMATORY": f"{FRESH}/P3B_CONFIRMATORY_MANIFEST.csv"}
SHAKEDOWN = (f"{FRESH}/P1_ENGINEERING_MANIFEST.csv", "mp-3148759")

# SHA-256 of the committed (LF) bytes, frozen in PROTOCOL.md before any outcome; preflight refuses to run on mismatch.
INPUT_SHA256 = {
    f"{FRESH}/P1_CONFIRMATORY_MANIFEST.csv": "3297d6c17959c7a70bf157f7157283f45ddb046fdc460acaa8a8570ab4de7331",
    f"{FRESH}/P3B_CONFIRMATORY_MANIFEST.csv": "e7c447d5f8dc3b263c7b5b4b9d1f8344ad9c8ed41e5b72fa333c37ad14b70f97",
    f"{FRESH}/P1_ENGINEERING_MANIFEST.csv": "480bc38667544eb4023276ad9def91eff451b4f1dbccb7cde76fb707b66fd6a9",
    f"{LAW}/run_P1_CONFIRMATORY/part_a_material.csv": "5760ae206af28c4d916088ce4ab8061053975934ea38f58904e34aa12bfb715e",
    f"{LAW}/run_P1_CONFIRMATORY/part_a_rows.csv": "3ebb5c0d7221b1186a1d16030c96100b7b34fd19a5079586cf33511feb433b60",
    f"{LAW}/run_P3B_CONFIRMATORY/part_a_material.csv": "cee4ec409461573f79716ef34279b6bab38416b9054b21620facb0837ecad2f1",
    f"{LAW}/run_P3B_CONFIRMATORY/part_a_rows.csv": "45553d6d973fad3b87ee0fb41549c2a838472fba439b8c65f072ae4fed74575a",
    "analysis/general_qoac_law/run_part_a.py": "fbfd13febf5911ae342f407cf4b3e946a86bd6e20e386de1bbfbdf15beb7f2af",
    "analysis/general_qoac_law/aggregate_law.py": "18304421790504c62af5d3a69d779821aade014d037f866f71f6ee4588703ada",
    "analysis/qoac_v03_rdo/run_engineering.py": "6cbdf8e31b4749cebb65a78582a8bec3032baf89073524b9c21065b65a7f3123",
    "analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py": "f78dd40aba7f2a25727d4df08d621f3456244bfb14f404423551900c3504ce1a",
    "analysis/qoac_h_strong_baselines/run_baselines.py": "ad09c4a53c2f44ea47669e941e123669ddf5fbeb5a53c4a35b799596d3d2a8c6",
    "validation/qsq_prospective/development_compatibility_smoke.py": "d51a31d7838d09175292e5024e7f969347c4de2e011446f6de863f2f3c0683bf",
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def check_inputs(repo: Path) -> list[str]:
    return [f"{p}: {lf_sha256(repo / p)} != {h}" for p, h in INPUT_SHA256.items() if lf_sha256(repo / p) != h]


def matrix(repo: Path, phase: str) -> list[dict]:
    if phase == "probe":
        return [{"manifest": SHAKEDOWN[0], "id": SHAKEDOWN[1]}]
    out = []
    for man in COHORTS.values():
        with open(repo / man, encoding="utf-8") as f:
            out += [{"manifest": man, "id": r["material_id"]} for r in csv.DictReader(f)]
    return out


def configs(arms: set[str]) -> list[tuple[str, str, dict]]:
    """(arm, config label, codec settings), slowest first."""
    out = []
    if "Q" in arms:
        out += [("Q", f"Q_{h}_b{b}", {"host": h, "block": b}) for h in C.QPET_HOSTS for b in C.QPET_BLOCKS]
    if "M" in arms:
        out += [("M", f"M_s={s}", {"s": s}) for s in C.MGARD_S]
    return out


def search(ev, tau: float, lo: float, hi: float, cap: float):
    """Equal search of A1/A6: eng.bisect_scale over the codec's single tolerance; the predicate is the decoded
    certificate at tau. Returns (best tolerance or None, passing points, decades skipped for execution errors, or -1
    if the codec never executed). The lower bound is raised by a decade only while the codec fails to execute there
    (never on a certificate failure), and at most up to `cap`."""
    skipped = 0
    while ev(lo) is None and lo * 10.0 <= cap * (1 + 1e-12):
        lo *= 10.0; skipped += 1
    if ev(lo) is None:
        return None, {}, -1   # -1: the codec did not execute at any admissible lower bound
    seen = {}

    def ok(t):
        r = ev(t)
        good = r is not None and r["hartree_hist"] < tau and r["hartree_safe"] < tau
        if good:
            seen[t] = r
        return good

    eng.bisect_scale(ok, lo, hi)
    if not seen:
        return None, seen, skipped
    best = max(seen, key=lambda t: (-seen[t]["bytes"], t))   # highest CR = fewest bytes among passing points
    return best, seen, skipped


def run_config(job):
    arm, label, cfg, npy, lat, ptp, rh, rs, base = job
    x = np.load(npy)
    raw = x.nbytes
    lo, hi = INTERVAL[arm]
    rows, evals, fails = [], [], []
    cache: dict[float, dict | None] = {}
    with tempfile.TemporaryDirectory(prefix=f"hbmq_{label}_") as tds:
        td = Path(tds)

        def codec(t):
            if arm == "M":
                return eng_mgard(x, t, cfg["s"], td)
            return C.qpet_roundtrip(x, t, cfg["host"], cfg["block"], ptp, td)

        def ev(t):
            t = float(t)
            if t in cache:
                return cache[t]
            s0 = time.perf_counter()
            try:
                rec, nb = codec(t)
                eh, es, li, rm = eng.certify(rec, x, lat, rh, rs)
                r = {"bytes": int(nb), "hartree_hist": eh, "hartree_safe": es, "density_Linf": li, "density_RMSE": rm,
                     "seconds": time.perf_counter() - s0}
                evals.append(base | {"arm": arm, "config": label, "tol": t, "tol_rel": t / ptp, "error": ""} | r)
            except Exception as exc:  # execution error: a non-passing point, recorded
                r = None
                msg = f"{type(exc).__name__}: {getattr(exc, 'stderr', None) or exc}"[:400]
                evals.append(base | {"arm": arm, "config": label, "tol": t, "tol_rel": t / ptp, "error": msg,
                                     "seconds": time.perf_counter() - s0})
                fails.append(base | {"arm": arm, "config": label, "tol": t, "tol_rel": t / ptp, "error": msg})
            cache[t] = r
            return r

        for tau in TAUS:
            ts = time.perf_counter(); n0 = len(evals)
            best, seen, skipped = search(ev, tau, lo * ptp, hi * ptp, LO_ERROR_CAP * ptp)
            row = base | {"arm": arm, "config": label, "tau": tau, "certified": best is not None,
                          "lo_decades_skipped": skipped, "n_evals_new": len(evals) - n0, "n_passing": len(seen),
                          "search_seconds": time.perf_counter() - ts}
            if best is not None:
                r = seen[best]
                row |= {"param": f"{label};tol_rel={best / ptp:.9g}", "tol": best, "bytes": r["bytes"],
                        "cr": raw / r["bytes"], "hartree_hist": r["hartree_hist"], "hartree_safe": r["hartree_safe"],
                        "density_Linf": r["density_Linf"], "density_RMSE": r["density_RMSE"]}
            rows.append(row)
    return label, rows, evals, fails


def eng_mgard(x, t, s, td):
    return C.mgard_roundtrip(x, t, s, td)


def write_csv(path: Path, data: list[dict]):
    if not data:
        return
    f = list(dict.fromkeys(k for r in data for k in r))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=f); w.writeheader(); w.writerows(data)


def material(meta: dict, a) -> tuple[list, list, list, dict]:
    sys.path.insert(0, str(a.frozen_root.resolve() / "validation"))
    sys.path.insert(0, str(a.repo_root.resolve() / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev
    mid = meta["material_id"]; t0 = time.time()
    rows, evals, fails = [], [], []
    info = {"material_id": mid}
    try:
        cp = a.cache_dir / f"{mid}.src"
        if cp.exists() and hashlib.sha256(cp.read_bytes()).hexdigest() == meta["sha256"]:
            blob = cp.read_bytes()
        else:
            blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"])); cp.write_bytes(blob)
        info["source_sha256_verified"] = hashlib.sha256(blob).hexdigest() == meta["sha256"] and len(blob) == int(meta["source_bytes"])
        with tempfile.TemporaryDirectory(prefix="hbmq_") as td:
            grid, loader = dev.build_grid(meta, blob, Path(td))
            x = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
            lat = np.asarray(grid.structure.lattice.matrix, float)
            if x.size != int(meta["npoints"]):
                raise RuntimeError(f"npoints mismatch {x.size} != {meta['npoints']}")
            ptp = float(np.ptp(x)); rh, rs = eng.v02.reference_hartree_rms(x, lat)
            npy = Path(td) / "rho.npy"; np.save(npy, x)
            base = {"material_id": mid, "system_type": meta["system_type"], "npoints": x.size, "raw_bytes": x.nbytes,
                    "shape": "x".join(str(v) for v in x.shape)}
            info |= {"loader": loader, "shape": base["shape"], "ptp": ptp, "load_seconds": time.time() - t0}
            jobs = [(arm, label, cfg, str(npy), lat, ptp, rh, rs, base) for arm, label, cfg in configs(set(a.arms.split(",")))]
            with ProcessPoolExecutor(max_workers=a.workers) as ex:
                for label, r, e, f in ex.map(run_config, jobs):
                    rows += r; evals += e; fails += f
                    print(f"HBMQ_CONFIG_DONE {mid} {label} certified_taus={sum(x['certified'] for x in r)} "
                          f"evals={len(e)} failures={len(f)}", flush=True)
    except Exception:
        fails.append({"material_id": mid, "arm": "material", "config": "", "error": traceback.format_exc()[-800:]})
    info["seconds"] = time.time() - t0
    return rows, evals, fails, info


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-root", type=Path)
    p.add_argument("--manifest", type=Path)
    p.add_argument("--cache-dir", type=Path)
    p.add_argument("--output-dir", type=Path)
    p.add_argument("--only", default="")
    p.add_argument("--arms", default="M,Q")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--check-inputs", action="store_true")
    p.add_argument("--list-matrix", default="")
    a = p.parse_args()
    if a.check_inputs:
        bad = check_inputs(a.repo_root)
        print("input hashes:", "OK" if not bad else bad)
        return 1 if bad else 0
    if a.list_matrix:
        print(json.dumps(matrix(a.repo_root, a.list_matrix)))
        return 0
    a.output_dir.mkdir(parents=True, exist_ok=True); a.cache_dir.mkdir(parents=True, exist_ok=True)
    man = list(csv.DictReader(open(a.manifest, encoding="utf-8")))
    if a.only:
        man = [m for m in man if m["material_id"] in a.only.split(",")]
    for meta in man:
        mid = meta["material_id"]
        rows, evals, fails, info = material(meta, a)
        write_csv(a.output_dir / f"rows_{mid}.csv", rows)
        write_csv(a.output_dir / f"evals_{mid}.csv", evals)
        write_csv(a.output_dir / f"failures_{mid}.csv", fails)
        (a.output_dir / f"info_{mid}.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        print(f"HBMQ_DONE {mid} rows={len(rows)} evals={len(evals)} failures={len(fails)} seconds={info['seconds']:.0f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
