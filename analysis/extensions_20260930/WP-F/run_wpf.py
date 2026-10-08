#!/usr/bin/env python3
"""WP-F runner: QSQ-gated, Bader-certified compression of a stratified MP archive sample (PROTOCOL.md, WP-F).

One checkpoint per object (atomic JSON) under --ckpt; a restart resumes. Every object ends as a result or
an explicit failure. Frozen stack only (loader, codec round trip, Bader settings from commit 893f931).

    python run_wpf.py --group small --workers 4     strata D01-D09: full union ladder
    python run_wpf.py --group large --workers 1     strata D10a-D10c: adopted WP-E policy per tau
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
import zlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("NUMBA_NUM_THREADS", "2")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
# laptop defaults, overridable by environment variables for another execution platform (DEVIATIONS.md 7)
FROZEN_VALIDATION = Path(os.environ.get("WPF_FROZEN_VALIDATION", r"D:\Research\QoI-final4-local\frozen_repo\validation"))
CACHE = Path(os.environ.get("WPF_CACHE", r"D:\Research\QoI-ext-cache\WP-F\densities"))
CKPT = Path(os.environ.get("WPF_CKPT", r"D:\Research\QoI-ext-cache\WP-F\checkpoints"))
SEEDS = (20260905, 1, 2, 3, 4)
TAUS = (1e-4, 1e-3, 1e-2)
LADDER = {
    "ZFP": (1e-7, 3e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1),
    "SPERR": (1e-7, 3e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1),
    "SZ3": (1e-7, 3e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2),
}
GROUPS = {"small": tuple("D%02d" % d for d in range(1, 10)), "large": ("D10a", "D10b", "D10c")}
USER_AGENT = "QoI-QSQ-WPF/1.0 (research; anonymous public bucket)"
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


def fetch(url: str, dest: Path) -> bytes:
    if dest.exists():
        return dest.read_bytes()
    err = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=900) as r:
                blob = r.read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".part")
            tmp.write_bytes(blob)
            os.replace(tmp, dest)
            return blob
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("download failed: %s: %s" % (type(err).__name__, err))


def atomic_json(path: Path, payload):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    os.replace(tmp, path)


class Bader:
    """Reference solve once, then responses/errors of any field against it."""

    def __init__(self, grid, field):
        core = _CORE
        self.grid, self.field = grid, field
        ref = core.run_bader(grid)
        self.q = np.asarray(ref["charges"], dtype=np.float64)
        self.labels = np.asarray(ref["atom_labels"])
        self.solves = 1

    def error(self, other):
        res = _CORE.run_bader(_CORE.clone_grid_with_total(self.grid, other))
        self.solves += 1
        q = np.asarray(res["charges"], dtype=np.float64)
        lab = np.asarray(res["atom_labels"])
        return float(np.max(np.abs(q - self.q))), int(np.count_nonzero(lab != self.labels))


def bisect_codec(codec, evaluate, tau):
    """PROTOCOL WP-E BISECT over this codec's ladder; evaluate(codec, rel) -> row dict (cached)."""
    rungs = LADDER[codec]
    lo, hi, best = -1, len(rungs), None
    while hi - lo > 1:
        mid = (lo + hi) // 2
        r = evaluate(codec, rungs[mid])
        if r["certifiable_error"] and r["bader_error_e"] < tau:
            lo, best = mid, r
        else:
            hi = mid
    return best


def process(task: dict) -> dict:
    core, dev = _CORE, _DEV
    t0 = time.time()
    out = dict(task_id=task["task_id"], stratum=task["stratum"], key=task["key"], frame_bytes=int(task["bytes"]),
               group=task["group"], status="SUCCESS", rows=[], failures=[])

    def fail(stage, exc):
        out["status"] = "FAILED"
        out["failures"].append(dict(task_id=task["task_id"], stratum=task["stratum"], stage=stage,
                                    error="%s: %s" % (type(exc).__name__, exc)))
        out["traceback"] = traceback.format_exc()
        out["wall_seconds"] = time.time() - t0
        return out

    try:
        blob = fetch(task["url"], CACHE / (task["task_id"] + ".json.gz"))
    except Exception as e:  # noqa: BLE001
        return fail("download", e)
    out.update(json_bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(), size_matches_frame=len(blob) == int(task["bytes"]))
    with tempfile.TemporaryDirectory(prefix="qoi_wpf_") as td:
        work = Path(td)
        try:
            grid, _ = dev.build_grid({"source": "Materials Project", "url": task["url"]}, blob, work)
            del blob
            field = np.asarray(grid.total, dtype=np.float64)
            if not np.all(np.isfinite(field)):
                raise RuntimeError("non-finite reference field")
            st = grid.structure
            out.update(shape="x".join(map(str, field.shape)), npoints=int(field.size), natoms=len(st),
                       spin_channels=len(getattr(grid, "data", {}) or {}), formula=st.composition.reduced_formula,
                       value_ptp=float(np.ptp(field)), value_min=float(field.min()), value_max=float(field.max()))
            try:
                from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
                sga = SpacegroupAnalyzer(st, symprec=0.1)
                out.update(crystal_system=sga.get_crystal_system(), spacegroup=sga.get_space_group_number())
            except Exception as e:  # noqa: BLE001
                out.update(crystal_system="", spacegroup="", symmetry_error=str(e)[:200])
            out["raw64_bytes"] = 8 * field.size
            out["lossless_bytes"] = len(zlib.compress(np.ascontiguousarray(field).tobytes(), 6))
            eps = float(np.max(np.abs(field.astype(np.float32).astype(np.float64) - field)))
            out["epsilon"] = eps
        except MemoryError as e:
            return fail("load_memory", e)
        except Exception as e:  # noqa: BLE001
            return fail("load", e)
        try:
            B = Bader(grid, field)
            out["natoms_bader"] = int(B.q.size)
            resp = []
            for s in SEEDS:
                noise = np.random.Generator(np.random.PCG64(s)).uniform(-eps, eps, size=field.shape)
                err, nre = B.error(field + noise)
                resp.append(dict(seed=s, response_e=err, n_reassigned=nre))
                del noise
            out["probes"] = resp
            f_m = max(r["response_e"] for r in resp)
            out["floor_e"] = f_m
            out["eligible"] = {str(t): bool(f_m < t) for t in TAUS}
        except MemoryError as e:
            return fail("qsq_memory", e)
        except Exception as e:  # noqa: BLE001
            return fail("qsq", e)

        cache: dict[tuple[str, float], dict] = {}
        ptp = out["value_ptp"]

        def evaluate(codec, rel):
            k = (codec, rel)
            if k in cache:
                return cache[k]
            abs_b = rel * ptp
            row = dict(codec=codec, nominal_tolerance_relative=rel, nominal_tolerance_absolute=abs_b)
            try:
                rec, nbytes, cfg = core.codec_roundtrip(codec.lower(), field, abs_b, work)
                rec = np.asarray(rec, dtype=np.float64)
                linf = float(np.max(np.abs(rec - field)))
                bound_ok = bool(linf <= abs_b * (1 + 1e-9) + 1e-300)
                err, nre = B.error(rec)
                row.update(codec_config=cfg, compressed_bytes=int(nbytes), realized_Linf=linf, bound_respected=bound_ok,
                           bader_error_e=err, n_reassigned=nre, certifiable_error=bound_ok, status="OK")
                del rec
            except Exception as e:  # noqa: BLE001
                row.update(status="FAILED", error="%s: %s" % (type(e).__name__, e), certifiable_error=False, bader_error_e=float("inf"))
                out["failures"].append(dict(task_id=task["task_id"], stratum=task["stratum"], stage="rung %s %g" % (codec, rel),
                                            error=row["error"]))
            gc.collect()
            cache[k] = row
            return row

        any_eligible = f_m < max(TAUS)
        chosen = {}
        if any_eligible:
            if task["group"] == "small":
                for c, rungs in LADDER.items():
                    for rel in rungs:
                        evaluate(c, rel)
            for t in TAUS:
                if f_m < t:
                    picks = [bisect_codec(c, evaluate, t) for c in LADDER]
                    picks = [p for p in picks if p is not None]
                    best = max(picks, key=lambda r: out["raw64_bytes"] / r["compressed_bytes"]) if picks else None
                    chosen[str(t)] = dict(codec=best["codec"], rel=best["nominal_tolerance_relative"],
                                          compressed_bytes=best["compressed_bytes"]) if best else None
        out["rows"] = list(cache.values())
        out["writer_choice"] = chosen
        out["bader_solves"] = B.solves
    out["wall_seconds"] = time.time() - t0
    return out


def run_group(group, workers, retry, only=None):
    tasks = [dict(r, group=group) for r in csv.DictReader(open(HERE / "sample.csv", encoding="utf-8"))
             if r["stratum"] in GROUPS[group]]
    if only:
        tasks = [t for t in tasks if t["task_id"] in set(only)]
    # smallest first, so memory-heavy objects come last and a crash loses least
    tasks.sort(key=lambda t: int(t["bytes"]))

    def needs(t):
        p = CKPT / (t["task_id"] + ".json")
        if not p.exists():
            return not retry
        if not retry:
            return False
        d = json.load(open(p, encoding="utf-8"))
        return d["status"] == "FAILED" and not d.get("retried") and any(f["stage"] == "worker" for f in d["failures"])

    todo = [t for t in tasks if needs(t)]
    workers = 1 if retry else workers
    print("group %s%s: %d tasks, %d to do, workers %d" % (group, " (solo retry)" if retry else "", len(tasks), len(todo), workers), flush=True)
    if not todo:
        return
    with ProcessPoolExecutor(max_workers=workers, initializer=_init, max_tasks_per_child=1) as ex:
        futs = {ex.submit(process, t): t for t in todo}
        for f in as_completed(futs):
            t = futs[f]
            try:
                res = f.result()
            except Exception as e:  # noqa: BLE001  (worker killed, e.g. out of memory)
                res = dict(task_id=t["task_id"], stratum=t["stratum"], key=t["key"], frame_bytes=int(t["bytes"]), group=group,
                           status="FAILED", rows=[], failures=[dict(task_id=t["task_id"], stratum=t["stratum"], stage="worker",
                                                                     error="%s: %s" % (type(e).__name__, e))])
            res["retried"] = bool(retry)
            atomic_json(CKPT / (t["task_id"] + ".json"), res)
            print("%s %s %s %.0fs floor=%s solves=%s" % (time.strftime("%H:%M:%S"), t["task_id"], res["status"],
                  res.get("wall_seconds", 0), res.get("floor_e"), res.get("bader_solves")), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", choices=sorted(GROUPS) + ["all"], required=True)
    ap.add_argument("--workers", type=int, default=3, help="workers for the small group (the large group always runs 1)")
    ap.add_argument("--only", nargs="*", help="task ids (smoke test)")
    ap.add_argument("--retry-worker-failures", action="store_true",
                    help="re-run, one at a time, objects whose worker process died (e.g. memory) and were not yet retried")
    a = ap.parse_args()
    CKPT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    adopted = json.load(open(REPO / "analysis" / "extensions_20260930" / "WP-E" / "adopted_policy.json"))
    assert adopted["adopted_policy"] == "BISECT", adopted          # the writer implemented above
    if a.group == "all":                                           # DEVIATIONS.md 4: sequential groups, solo retries
        for g, w in (("small", a.workers), ("large", 1)):
            run_group(g, w, False)
            run_group(g, 1, True)
        print("ALL GROUPS DONE", flush=True)
    else:
        run_group(a.group, a.workers if a.group == "small" else 1, a.retry_worker_failures, a.only)


if __name__ == "__main__":
    main()