"""QSQ probe exchangeability: reproduce the frozen five-seed floor and add an independent-stream panel.

Protocol: PROTOCOL.md in this directory (declared before any probe was evaluated).

Per material: reference Bader, the five frozen QSQ seeds (panel F) and five material-specific
independent streams (panel I). Input loading, source verification, the float32 amplitude check and
Bader settings are WP-B's frozen implementation, imported unchanged.
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")
os.environ.setdefault("NUMBA_NUM_THREADS", "2")

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
WPB_DIR = REPO_ROOT / "analysis" / "extensions_20260928" / "WP-B"
sys.path.insert(0, str(WPB_DIR))
import run_wpb as wpb  # noqa: E402  (frozen WP-B helpers)

DEFAULT_CHECKPOINTS = Path(r"D:\Research\QoI-ext-cache\QSQ-exch\checkpoints")
INDEPENDENT_LABELS = (1, 2, 3, 4, 5)


def independent_stream_seed(material: str, label: int) -> int:
    msg = f"QSQ-exch-20261003|{material}|iid_uniform|{label}".encode()
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "little")


def process_material(task: dict[str, Any]) -> dict[str, Any]:
    core, loader = wpb._CORE, wpb._LOADER
    mid: str = task["material_id"]
    meta: dict[str, str] = task["meta"]
    epsilon: float = task["epsilon"]
    t_start = time.time()
    payload: dict[str, Any] = {"material_id": mid, "status": "SUCCESS", "probes": [], "failures": []}
    probes = [("frozen_qsq", s, s) for s in wpb.QSQ_SEEDS] + [
        ("independent", k, independent_stream_seed(mid, k)) for k in INDEPENDENT_LABELS
    ]
    blob, fetch_mode = wpb.fetch_cached(meta, Path(task["cache"]))
    with tempfile.TemporaryDirectory(prefix="qoi_exch_") as td:
        grid, loader_name = loader.build_grid(meta, blob, Path(td))
        del blob
        field = np.asarray(grid.total, dtype=np.float64)
        if field.size != int(meta["npoints"]):
            raise RuntimeError(f"npoints mismatch {field.size} != {meta['npoints']}")
        f32_eps = float(np.max(np.abs(field.astype(np.float32).astype(np.float64) - field)))
        amp_atol = max(1e-15, 16 * np.finfo(np.float64).eps * max(1.0, abs(epsilon)))
        if not np.isclose(f32_eps, epsilon, rtol=1e-10, atol=amp_atol):
            raise RuntimeError(f"float32 amplitude mismatch {f32_eps} != {epsilon}")
        t0 = time.time()
        ref = core.run_bader(grid)
        payload["reference_bader_seconds"] = time.time() - t0
        q_ref = np.asarray(ref["charges"], dtype=np.float64)
        if q_ref.size != int(meta["natoms"]):
            raise RuntimeError(f"Bader natoms mismatch {q_ref.size} != {meta['natoms']}")
        payload["loader"] = loader_name
        payload["fetch_mode"] = fetch_mode
        payload["npoints"] = int(field.size)
        payload["natoms"] = int(q_ref.size)
        for family, label, stream_seed in probes:
            try:
                rng = np.random.Generator(np.random.PCG64(stream_seed))
                noise = rng.uniform(-epsilon, epsilon, size=field.shape).astype(np.float64, copy=False)
                measured_linf = float(np.max(np.abs(noise)))
                perturbed = field + noise
                mean_noise = float(np.mean(noise))
                del noise
                t0 = time.time()
                res = core.run_bader(core.clone_grid_with_total(grid, perturbed))
                secs = time.time() - t0
                q_new = np.asarray(res["charges"], dtype=np.float64)
                if q_new.shape != q_ref.shape:
                    raise RuntimeError(f"Bader charge shape mismatch {q_new.shape} != {q_ref.shape}")
                payload["probes"].append({
                    "material_id": mid, "system_type": meta["system_type"], "family": family,
                    "seed_label": label, "stream_seed": stream_seed, "epsilon": epsilon,
                    "measured_Linf": measured_linf, "mean_perturbation_e": mean_noise,
                    "bader_response_max_e": float(np.max(np.abs(q_new - q_ref))),
                    "bader_seconds": secs, "status": "SUCCESS",
                })
                del perturbed, res, q_new
            except Exception as exc:  # noqa: BLE001
                payload["failures"].append({
                    "material_id": mid, "family": family, "seed_label": label,
                    "error": f"{type(exc).__name__}: {exc}",
                })
            gc.collect()
    payload["wall_seconds"] = time.time() - t_start
    return payload


def _run_task(task: dict[str, Any]) -> tuple[str, str, float]:
    ckpt = Path(task["checkpoint_dir"]) / f"{task['material_id']}.json"
    try:
        payload = process_material(task)
    except Exception as exc:  # noqa: BLE001
        payload = {
            "material_id": task["material_id"], "status": "FAILED", "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(), "probes": [],
            "failures": [{"material_id": task["material_id"], "family": "material", "seed_label": "",
                          "error": f"{type(exc).__name__}: {exc}"}],
        }
    wpb.atomic_write_json(ckpt, payload)
    return task["material_id"], payload["status"], float(payload.get("wall_seconds", 0.0))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINTS)
    p.add_argument("--materials", type=str, default="")
    args = p.parse_args()
    ckdir = args.checkpoint_dir.resolve()
    ckdir.mkdir(parents=True, exist_ok=True)
    inputs = wpb.load_inputs(REPO_ROOT)
    materials = inputs["dev_materials"]
    if args.materials:
        wanted = set(args.materials.split(","))
        materials = [m for m in materials if m in wanted]
    # smallest fields first so memory-heavy materials run last
    materials.sort(key=lambda m: int(inputs["metadata"][m]["npoints"]))
    pending = [m for m in materials if not (ckdir / f"{m}.json").exists()]
    log = HERE / "run_log.txt"

    def logline(msg: str) -> None:
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
        with log.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line, flush=True)

    logline(f"{len(materials)} materials; {len(pending)} pending")
    tasks = [{
        "material_id": m, "meta": inputs["metadata"][m], "epsilon": inputs["amp"][m],
        "cache": str(wpb.DEFAULT_CACHE), "checkpoint_dir": str(ckdir),
    } for m in pending]
    if tasks:
        import multiprocessing as mp

        ctx = mp.get_context("spawn")
        init_args = (str(wpb.DEFAULT_FROZEN_VALIDATION), str(REPO_ROOT))
        with ctx.Pool(processes=args.workers, initializer=wpb._init_worker, initargs=init_args,
                      maxtasksperchild=8) as pool:
            for done, (mid, status, secs) in enumerate(pool.imap_unordered(_run_task, tasks), 1):
                logline(f"[{done}/{len(tasks)}] {mid} {status} {secs:.1f}s")
    logline("run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
