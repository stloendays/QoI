#!/usr/bin/env python3
"""WP-G runner: all-electron-reference Bader (CHGCAR partitioned by AECCAR0+AECCAR2 basins), PROTOCOL.md WP-G.

Per development MP material with both AECCARs (53): reference solve, arm G1 (reference exact; CHGCAR
perturbed / compressed exactly as the frozen rows) and arm G2 (reference perturbed / compressed too).
One checkpoint per material under --ckpt; a restart resumes.

    python run_wpg.py --workers 3
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import logging
import os
import sys
import tempfile
import time
import traceback
import urllib.request
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("NUMBA_NUM_THREADS", "2")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FROZEN_VALIDATION = Path(r"D:\Research\QoI-final4-local\frozen_repo\validation")
DENS = Path(r"D:\Research\QoI-ext-cache\densities")               # SHA-verified CHGCAR cache of the frozen study
CACHE = Path(r"D:\Research\QoI-ext-cache\WP-G\aeccars")
CKPT = Path(r"D:\Research\QoI-ext-cache\WP-G\checkpoints")
BUCKET = "https://materialsproject-parsed.s3.amazonaws.com/"
SEEDS = (20260905, 1, 2, 3, 4)
USER_AGENT = "QoI-QSQ-WPG/1.0 (research; anonymous public bucket)"
_CORE = _DEV = None


def _init():
    global _CORE, _DEV
    logging.disable(logging.WARNING)
    sys.path.insert(0, str(FROZEN_VALIDATION))
    sys.path.insert(0, str(REPO / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev  # type: ignore
    import external_end_to_end as core  # type: ignore
    _CORE, _DEV = core, dev
    for n in ("baderkit", "pymatgen", "numba"):
        logging.getLogger(n).setLevel(logging.ERROR)


def fetch(url, dest):
    if dest.exists():
        return dest.read_bytes()
    err = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=900) as r:
                blob = r.read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".part"); tmp.write_bytes(blob); os.replace(tmp, dest)
            return blob
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("download failed: %s: %s" % (type(err).__name__, err))


def bader(charge_grid, reference_grid):
    """Frozen settings; basins from reference_grid, charges integrated from charge_grid."""
    from baderkit import Bader
    core = _CORE
    a = Bader(charge_grid=charge_grid, total_charge_grid=charge_grid, reference_grid=reference_grid,
              method=core.BADER_METHOD, vacuum_tol=core.BADER_VACUUM_TOL, persistence_tol=core.BADER_PERSISTENCE_TOL,
              nna_cutoff=core.BADER_NNA_CUTOFF)
    return np.asarray(a.atom_charges, dtype=np.float64), np.asarray(a.atom_labels)


def ae_seed(mid, seed):
    return int.from_bytes(hashlib.sha256(("QSQ-WPG|%s|%d" % (mid, seed)).encode()).digest()[:8], "little")


def f32_eps(x):
    return float(np.max(np.abs(x.astype(np.float32).astype(np.float64) - x)))


def process(task):
    core, dev = _CORE, _DEV
    mid, meta, rows = task["material_id"], task["meta"], task["rows"]
    t0 = time.time()
    out = dict(material_id=mid, task_id=task["task_id"], status="SUCCESS", probes=[], rows=[], failures=[])

    def fail(stage, e):
        out.update(status="FAILED", traceback=traceback.format_exc(), wall_seconds=time.time() - t0)
        out["failures"].append(dict(material_id=mid, stage=stage, error="%s: %s" % (type(e).__name__, e)))
        return out

    try:
        chg_blob = (DENS / (meta["sha256"] + ".bin")).read_bytes()
        if hashlib.sha256(chg_blob).hexdigest() != meta["sha256"]:
            raise RuntimeError("CHGCAR cache SHA-256 mismatch")
        a0 = fetch(BUCKET + "aeccar0s/%s.json.gz" % task["task_id"], CACHE / ("%s_aeccar0.json.gz" % task["task_id"]))
        a2 = fetch(BUCKET + "aeccar2s/%s.json.gz" % task["task_id"], CACHE / ("%s_aeccar2.json.gz" % task["task_id"]))
        out.update(aeccar0_sha256=hashlib.sha256(a0).hexdigest(), aeccar2_sha256=hashlib.sha256(a2).hexdigest(),
                   aeccar0_bytes=len(a0), aeccar2_bytes=len(a2))
    except Exception as e:  # noqa: BLE001
        return fail("inputs", e)
    with tempfile.TemporaryDirectory(prefix="qoi_wpg_") as td:
        work = Path(td)
        try:
            grid, _ = dev.build_grid(meta, chg_blob, work)
            chg = np.asarray(grid.total, dtype=np.float64)
            if abs(float(np.ptp(chg)) - float(rows[0]["value_ptp"])) > 1e-9 * max(1.0, abs(float(rows[0]["value_ptp"]))):
                raise RuntimeError("CHGCAR value_ptp differs from the frozen rows")
            ae = sum(np.asarray(dev.decode_mp_chgcar(b).data["total"], dtype=np.float64) for b in (a0, a2))
            if ae.shape != chg.shape:
                raise RuntimeError("AECCAR grid %s != CHGCAR grid %s" % (ae.shape, chg.shape))
            del chg_blob, a0, a2
            ref_grid = core.clone_grid_with_total(grid, ae)
            eps_c, eps_a = f32_eps(chg), f32_eps(ae)
            out.update(shape="x".join(map(str, chg.shape)), epsilon_chgcar=eps_c, epsilon_ae=eps_a,
                       ae_ptp=float(np.ptp(ae)), chg_ptp=float(np.ptp(chg)))
            q0, lab0 = bader(grid, ref_grid)
            out["natoms"] = int(q0.size)
            solves = 1

            def err_of(chg_field, ae_field):
                nonlocal solves
                cg = core.clone_grid_with_total(grid, chg_field)
                rg = ref_grid if ae_field is None else core.clone_grid_with_total(grid, ae_field)
                q, lab = bader(cg, rg)
                solves += 1
                return float(np.max(np.abs(q - q0))), float(np.mean(lab != lab0))
        except Exception as e:  # noqa: BLE001
            return fail("reference", e)
        try:
            for s in SEEDS:
                n_c = np.random.Generator(np.random.PCG64(s)).uniform(-eps_c, eps_c, size=chg.shape)
                e1, r1 = err_of(chg + n_c, None)
                n_a = np.random.Generator(np.random.PCG64(ae_seed(mid, s))).uniform(-eps_a, eps_a, size=ae.shape)
                e2, r2 = err_of(chg + n_c, ae + n_a)
                out["probes"].append(dict(seed=s, g1_response_e=e1, g1_reassigned_frac=r1, g2_response_e=e2, g2_reassigned_frac=r2))
                del n_c, n_a
            out["g1_floor_e"] = max(p["g1_response_e"] for p in out["probes"])
            out["g2_floor_e"] = max(p["g2_response_e"] for p in out["probes"])
        except Exception as e:  # noqa: BLE001
            return fail("qsq", e)
        ae_ptp = out["ae_ptp"]
        for r in rows:
            codec, rel, abs_c = r["codec"].upper(), float(r["nominal_tolerance_relative"]), float(r["nominal_tolerance_absolute"])
            row = dict(codec=codec, nominal_tolerance_relative=rel, nominal_tolerance_absolute=abs_c,
                       frozen_realized_Linf=float(r["realized_Linf"]), frozen_bader_error_e=float(r["Bader_error_resolved_e"]),
                       frozen_compressed_bytes=int(r["compressed_bytes"]))
            try:
                rec_c, nb_c, _ = core.codec_roundtrip(codec.lower(), chg, abs_c, work)
                rec_c = np.asarray(rec_c, dtype=np.float64)
                linf = float(np.max(np.abs(rec_c - chg)))
                row.update(realized_Linf=linf, reproduced=bool(0.95 <= linf / max(row["frozen_realized_Linf"], 1e-300) <= 1.05),
                           chgcar_bytes=int(nb_c))
                row["g1_error_e"], row["g1_reassigned_frac"] = err_of(rec_c, None)
                abs_a = rel * ae_ptp
                rec_a, nb_a, _ = core.codec_roundtrip(codec.lower(), ae, abs_a, work)
                rec_a = np.asarray(rec_a, dtype=np.float64)
                row.update(ae_abs_bound=abs_a, ae_realized_Linf=float(np.max(np.abs(rec_a - ae))), ae_bytes=int(nb_a))
                row["g2_error_e"], row["g2_reassigned_frac"] = err_of(rec_c, rec_a)
                row["status"] = "OK"
                del rec_c, rec_a
            except Exception as e:  # noqa: BLE001
                row.update(status="FAILED", error="%s: %s" % (type(e).__name__, e))
                out["failures"].append(dict(material_id=mid, stage="row %s %g" % (codec, rel), error=row["error"]))
            out["rows"].append(row)
            gc.collect()
        out["bader_solves"] = solves
    out["wall_seconds"] = time.time() - t0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    CKPT.mkdir(parents=True, exist_ok=True)
    meta = {r["material_id"]: r for r in csv.DictReader(open(REPO / "materials_metadata.csv", encoding="utf-8"))}
    avail = [r for r in csv.DictReader(open(HERE / "aeccar_availability.csv", encoding="utf-8")) if r["both"] == "1"]
    assert len(avail) == 53, len(avail)
    bench = {}
    for r in csv.DictReader(open(REPO / "benchmark" / "master_benchmark_full.csv", encoding="utf-8")):
        bench.setdefault(r["material_id"], []).append(r)
    tasks = [dict(material_id=r["material_id"], task_id=r["task_id"], meta=meta[r["material_id"]],
                  rows=sorted(bench[r["material_id"]], key=lambda x: (x["codec"], float(x["nominal_tolerance_relative"]))))
             for r in avail]
    if a.only:
        tasks = [t for t in tasks if t["material_id"] in set(a.only)]
    tasks.sort(key=lambda t: int(t["meta"]["npoints"]))
    todo = [t for t in tasks if not (CKPT / (t["material_id"] + ".json")).exists()]
    print("WP-G: %d materials, %d to do, workers %d" % (len(tasks), len(todo), a.workers), flush=True)
    with ProcessPoolExecutor(max_workers=a.workers, initializer=_init, max_tasks_per_child=1) as ex:
        futs = {ex.submit(process, t): t for t in todo}
        for f in as_completed(futs):
            t = futs[f]
            try:
                res = f.result()
            except Exception as e:  # noqa: BLE001
                res = dict(material_id=t["material_id"], task_id=t["task_id"], status="FAILED", probes=[], rows=[],
                           failures=[dict(material_id=t["material_id"], stage="worker", error="%s: %s" % (type(e).__name__, e))])
            tmp = CKPT / (t["material_id"] + ".tmp")
            tmp.write_text(json.dumps(res, indent=1), encoding="utf-8")
            os.replace(tmp, CKPT / (t["material_id"] + ".json"))
            print("%s %s %s %.0fs g1=%s g2=%s solves=%s" % (time.strftime("%H:%M:%S"), t["material_id"], res["status"],
                  res.get("wall_seconds", 0), res.get("g1_floor_e"), res.get("g2_floor_e"), res.get("bader_solves")), flush=True)


if __name__ == "__main__":
    main()
