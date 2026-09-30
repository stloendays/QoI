#!/usr/bin/env python3
"""WP-B execution: density critical points as a second topology-sensitive QoI.

Protocol: analysis/extensions_20260928/PROTOCOL.md, section WP-B.

For every development material (sorted material_id, deterministic order) this
script
  1. fetches the exact source bytes (cached once on disk, SHA-256 verified on
     every read),
  2. builds the reference grid with the frozen development loader,
  3. runs the frozen on-grid Bader reference and the critical-point QoI on the
     raw reference density,
  4. regenerates every frozen benchmark reconstruction (codec round trip at the
     stored nominal absolute tolerance) and applies the reproduction gate
     (realized L_inf within 0.95..1.05 of the stored realized_Linf), then scores
     the critical-point QoI and re-derives the resolved Bader error,
  5. regenerates the five QSQ perturbation fields and the 59 fresh iid fields
     and scores both QoIs on them.

The critical-point QoI is fixed by the protocol: a voxel is a local maximum of
rho if it is strictly greater than all 26 periodic neighbours (local minimum:
strictly smaller). No smoothing, no interpolation, exact ties are not extrema.

Results are checkpointed per material (atomic JSON) so a restart resumes.
Every planned row and probe ends as either a result or an explicit failure. A
reconstruction row whose Bader re-solve fails keeps its critical-point result
(status CP_ONLY) and is also listed as a failure at stage "bader".
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
from collections import defaultdict
from pathlib import Path
from typing import Any

# Thread limits must be set before numpy/numba/baderkit are imported in a worker.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")
os.environ.setdefault("NUMBA_NUM_THREADS", "2")

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_FROZEN_VALIDATION = Path(r"D:\Research\QoI-final4-local\frozen_repo\validation")
DEFAULT_CACHE = Path(r"D:\Research\QoI-ext-cache\densities")
DEFAULT_CHECKPOINTS = Path(r"D:\Research\QoI-ext-cache\WP-B\checkpoints")

QSQ_SEEDS = (20260905, 1, 2, 3, 4)
FRESH_LABELS = tuple(range(10000, 10059))
GATE_LOW, GATE_HIGH = 0.95, 1.05
PTP_RTOL, PTP_ATOL = 1e-12, 1e-12
USER_AGENT = "QoI-QSQ-extensions-WPB/1.0 (research validation)"
NEIGHBOUR_OFFSETS = tuple(
    (i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1) if (i, j, k) != (0, 0, 0)
)
assert len(NEIGHBOUR_OFFSETS) == 26

_CORE = None
_LOADER = None


# ----------------------------------------------------------------------------
# critical-point QoI (fixed definition)
# ----------------------------------------------------------------------------
def critical_points(field: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Strict 26-neighbour periodic local maxima and minima on the raw grid."""
    f = np.asarray(field, dtype=np.float64)
    if f.ndim != 3:
        raise RuntimeError(f"expected a 3-D grid, got shape {f.shape}")
    is_max = np.ones(f.shape, dtype=bool)
    is_min = np.ones(f.shape, dtype=bool)
    for offset in NEIGHBOUR_OFFSETS:
        rolled = np.roll(f, offset, axis=(0, 1, 2))
        np.logical_and(is_max, f > rolled, out=is_max)
        np.logical_and(is_min, f < rolled, out=is_min)
    return is_max, is_min


def maxima_index_set(is_max: np.ndarray) -> np.ndarray:
    return np.flatnonzero(is_max.ravel(order="C")).astype(np.int64)


def jaccard_distance(a: np.ndarray, b: np.ndarray) -> tuple[float, int, int, int]:
    """Jaccard distance between two sorted unique flat-index sets.

    Returns (distance, |a & b|, |a - b| (lost), |b - a| (gained)).
    """
    inter = int(np.intersect1d(a, b, assume_unique=True).size)
    union = int(a.size + b.size - inter)
    if union == 0:
        return 0.0, 0, 0, 0
    return 1.0 - inter / union, inter, int(a.size - inter), int(b.size - inter)


def index_set_sha256(idx: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(str(int(idx.size)).encode())
    h.update(b"|")
    h.update(np.ascontiguousarray(idx, dtype=np.int64).tobytes(order="C"))
    return h.hexdigest()


def labels_sha256(labels: np.ndarray) -> str:
    x = np.ascontiguousarray(np.asarray(labels, dtype=np.int32))
    h = hashlib.sha256()
    h.update(str(tuple(x.shape)).encode())
    h.update(b"|")
    h.update(x.tobytes(order="C"))
    return h.hexdigest()


def cp_summary(is_max: np.ndarray, is_min: np.ndarray, ref_labels: np.ndarray, natoms: int) -> dict[str, Any]:
    idx = maxima_index_set(is_max)
    per_atom = np.bincount(np.asarray(ref_labels)[is_max].astype(np.int64), minlength=natoms + 1)
    return {
        "n_max": int(idx.size),
        "n_min": int(np.count_nonzero(is_min)),
        "per_atom_maxima": [int(x) for x in per_atom[:natoms]],
        "n_max_in_vacuum_basin": int(per_atom[natoms]),
        "maxima_set_sha256": index_set_sha256(idx),
        "_idx": idx,
    }


# ----------------------------------------------------------------------------
# inputs
# ----------------------------------------------------------------------------
def sha256_hex(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def expected_stream_seed(material: str, label: int) -> int:
    msg = f"QSQ-heldout|{material}|iid_uniform|{label}".encode()
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "little")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_inputs(repo: Path) -> dict[str, Any]:
    metadata = {r["material_id"]: r for r in read_csv_rows(repo / "materials_metadata.csv")}
    bench_rows = read_csv_rows(repo / "benchmark" / "master_benchmark_full.csv")
    bench: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen: set[tuple[str, str, str]] = set()
    for r in bench_rows:
        key = (r["material_id"], r["codec"], r["nominal_tolerance_relative"])
        if key in seen:
            raise RuntimeError(f"duplicate benchmark key {key}")
        seen.add(key)
        bench[r["material_id"]].append(r)
    per_seed = read_csv_rows(repo / "stability" / "stability_floor_A1_per_seed.csv")
    amp: dict[str, float] = {}
    seeds: dict[str, set[int]] = defaultdict(set)
    frozen_seed_response: dict[tuple[str, int], float] = {}
    for r in per_seed:
        mid = r["material_id"]
        seeds[mid].add(int(r["seed"]))
        val = float(r["probe_linf"])
        if mid in amp and amp[mid] != val:
            raise RuntimeError(f"probe_linf not unique for {mid}")
        amp[mid] = val
        frozen_seed_response[(mid, int(r["seed"]))] = float(r["floor_noise_resolved_e"])
    fresh_rows = read_csv_rows(repo / "validation" / "qsq_prospective" / "fresh_seed_jobs.csv")
    fresh: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in fresh_rows:
        fresh[r["material_id"]].append(r)
    frozen_fresh_response: dict[tuple[str, int], float] = {}
    outcomes = repo / "validation" / "qsq_prospective" / "p2_fresh_probes" / "outcomes.csv"
    for r in read_csv_rows(outcomes):
        frozen_fresh_response[(r["material_id"], int(r["seed_label"]))] = float(r["bader_response_max_e"])
    dev_materials = sorted(m for m, r in metadata.items() if r["corpus"].startswith("dev"))
    for mid in dev_materials:
        if seeds[mid] != set(QSQ_SEEDS):
            raise RuntimeError(f"QSQ seed set drift for {mid}: {seeds[mid]}")
        if sorted(int(r["seed_label"]) for r in fresh[mid]) != list(FRESH_LABELS):
            raise RuntimeError(f"fresh seed labels drift for {mid}")
        for r in fresh[mid]:
            if int(r["stream_seed"]) != expected_stream_seed(mid, int(r["seed_label"])):
                raise RuntimeError(f"stream seed mismatch {mid}/{r['seed_label']}")
            # fresh_seed_jobs.csv stores epsilon with 15 significant digits; the executed P2
            # run (outcomes.csv) and this package use the per-seed probe_linf verbatim.
            if not np.isclose(float(r["epsilon"]), amp[mid], rtol=1e-12, atol=0.0):
                raise RuntimeError(f"fresh epsilon mismatch {mid}/{r['seed_label']}")
        if mid not in bench:
            raise RuntimeError(f"material without benchmark rows: {mid}")
    return {
        "metadata": metadata,
        "bench": bench,
        "amp": amp,
        "fresh": fresh,
        "frozen_seed_response": frozen_seed_response,
        "frozen_fresh_response": frozen_fresh_response,
        "dev_materials": dev_materials,
    }


def fetch_cached(meta: dict[str, str], cache: Path) -> tuple[bytes, str]:
    """Return the exact source bytes, downloading once and verifying SHA-256 on every read."""
    cache.mkdir(parents=True, exist_ok=True)
    expected_sha = meta["sha256"]
    expected_bytes = int(meta["source_bytes"])
    path = cache / f"{expected_sha}.bin"
    if path.exists():
        blob = path.read_bytes()
        if sha256_hex(blob) == expected_sha and len(blob) == expected_bytes:
            return blob, "cache"
        path.unlink()
    last_err: Exception | None = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(meta["url"], headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=600) as response:
                blob = response.read()
            got = sha256_hex(blob)
            if got != expected_sha:
                raise RuntimeError(f"source SHA256 mismatch: {got} != {expected_sha}")
            if len(blob) != expected_bytes:
                raise RuntimeError(f"source byte-count mismatch: {len(blob)} != {expected_bytes}")
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(blob)
            os.replace(tmp, path)
            return blob, f"download_attempt_{attempt + 1}"
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(min(60, 5 * (attempt + 1)))
    raise RuntimeError(f"download failed after 5 attempts: {type(last_err).__name__}: {last_err}")


# ----------------------------------------------------------------------------
# worker
# ----------------------------------------------------------------------------
def _init_worker(frozen_validation: str, repo: str) -> None:
    global _CORE, _LOADER
    logging.disable(logging.WARNING)
    sys.path.insert(0, frozen_validation)
    sys.path.insert(0, str(Path(repo) / "validation" / "qsq_prospective"))
    import external_end_to_end as core  # type: ignore
    import development_compatibility_smoke as loader  # type: ignore

    _CORE = core
    _LOADER = loader
    logging.disable(logging.WARNING)
    for name in ("baderkit", "pymatgen", "numba"):
        logging.getLogger(name).setLevel(logging.ERROR)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def process_material(task: dict[str, Any]) -> dict[str, Any]:
    """Compute every WP-B quantity for one material; returns the checkpoint payload."""
    core, loader = _CORE, _LOADER
    mid: str = task["material_id"]
    meta: dict[str, str] = task["meta"]
    bench_rows: list[dict[str, str]] = task["bench_rows"]
    epsilon: float = task["epsilon"]
    fresh_jobs: list[dict[str, str]] = task["fresh_jobs"]
    frozen_seed_resp: dict[str, float] = task["frozen_seed_response"]
    frozen_fresh_resp: dict[str, float] = task["frozen_fresh_response"]
    cache = Path(task["cache"])
    t_start = time.time()
    payload: dict[str, Any] = {
        "material_id": mid,
        "status": "SUCCESS",
        "reference": None,
        "rows": [],
        "probes": [],
        "failures": [],
    }
    planned_rows = sorted(
        bench_rows, key=lambda r: (r["codec"], r["ladder"], float(r["nominal_tolerance_relative"]))
    )
    planned_probes: list[tuple[str, int, int]] = [("qsq_seed", s, s) for s in QSQ_SEEDS] + [
        ("fresh_iid", int(j["seed_label"]), int(j["stream_seed"]))
        for j in sorted(fresh_jobs, key=lambda r: int(r["seed_label"]))
    ]

    def fail_everything(stage: str, exc: Exception) -> dict[str, Any]:
        err = f"{type(exc).__name__}: {exc}"
        payload["status"] = "FAILED"
        payload["error"] = err
        payload["traceback"] = traceback.format_exc()
        for r in planned_rows:
            payload["failures"].append({
                "material_id": mid, "kind": "reconstruction", "codec": r["codec"], "ladder": r["ladder"],
                "nominal_tolerance_relative": r["nominal_tolerance_relative"], "family": "", "seed_label": "",
                "stage": stage, "error": err,
            })
        for family, label, _stream in planned_probes:
            payload["failures"].append({
                "material_id": mid, "kind": "probe", "codec": "", "ladder": "", "nominal_tolerance_relative": "",
                "family": family, "seed_label": label, "stage": stage, "error": err,
            })
        payload["wall_seconds"] = time.time() - t_start
        return payload

    try:
        blob, fetch_mode = fetch_cached(meta, cache)
    except Exception as exc:  # noqa: BLE001
        return fail_everything("source_fetch", exc)

    with tempfile.TemporaryDirectory(prefix="qoi_wpb_") as td:
        workdir = Path(td)
        try:
            t0 = time.time()
            grid, loader_name = loader.build_grid(meta, blob, workdir)
            load_seconds = time.time() - t0
            del blob
            field = np.asarray(grid.total, dtype=np.float64)
            expected_shape = loader.parse_shape(meta["ngrid"])
            if tuple(int(x) for x in field.shape) != expected_shape:
                raise RuntimeError(f"grid shape mismatch {field.shape} != {expected_shape}")
            if field.size != int(meta["npoints"]):
                raise RuntimeError(f"npoints mismatch {field.size} != {meta['npoints']}")
            if len(grid.structure) != int(meta["natoms"]):
                raise RuntimeError(f"structure natoms mismatch {len(grid.structure)} != {meta['natoms']}")
            if not np.all(np.isfinite(field)):
                raise RuntimeError("reference field contains non-finite values")
            value_ptp = float(np.ptp(field))
            frozen_ptp = float(planned_rows[0]["value_ptp"])
            if not np.isclose(value_ptp, frozen_ptp, rtol=PTP_RTOL, atol=PTP_ATOL):
                raise RuntimeError(f"value_ptp mismatch {value_ptp} != {frozen_ptp}")
            f32_eps = float(np.max(np.abs(field.astype(np.float32).astype(np.float64) - field)))
            amp_atol = max(1e-15, 16 * np.finfo(np.float64).eps * max(1.0, abs(epsilon)))
            if not np.isclose(f32_eps, epsilon, rtol=1e-10, atol=amp_atol):
                raise RuntimeError(f"float32 amplitude mismatch {f32_eps} != {epsilon}")

            t0 = time.time()
            ref = core.run_bader(grid)
            ref_bader_seconds = time.time() - t0
            q_ref = np.asarray(ref["charges"], dtype=np.float64)
            labels_ref = np.asarray(ref["atom_labels"])
            natoms = int(q_ref.size)
            if natoms != int(meta["natoms"]):
                raise RuntimeError(f"Bader natoms mismatch {natoms} != {meta['natoms']}")
            q_fixed = core.fixed_basin_charges(field, labels_ref, natoms)
            self_error = float(np.max(np.abs(q_fixed - q_ref)))
            if self_error > 1e-7:
                raise RuntimeError(f"fixed-basin reference self-check failed: {self_error:.6g} e")

            t0 = time.time()
            is_max, is_min = critical_points(field)
            cp_seconds = time.time() - t0
            cp_ref = cp_summary(is_max, is_min, labels_ref, natoms)
            idx_ref = cp_ref.pop("_idx")
            del is_max, is_min
            payload["reference"] = {
                "material_id": mid,
                "system_type": meta["system_type"],
                "corpus": meta["corpus"],
                "source": meta["source"],
                "formula": meta["formula"],
                "loader": loader_name,
                "fetch_mode": fetch_mode,
                "source_sha256": meta["sha256"],
                "source_bytes": int(meta["source_bytes"]),
                "npoints": int(field.size),
                "grid_shape": [int(x) for x in field.shape],
                "natoms": natoms,
                "value_ptp": value_ptp,
                "epsilon": epsilon,
                "n_max": cp_ref["n_max"],
                "n_min": cp_ref["n_min"],
                "per_atom_maxima_json": json.dumps(cp_ref["per_atom_maxima"], separators=(",", ":")),
                "n_max_in_vacuum_basin": cp_ref["n_max_in_vacuum_basin"],
                "n_atoms_with_zero_maxima": int(sum(1 for x in cp_ref["per_atom_maxima"] if x == 0)),
                "n_atoms_with_multiple_maxima": int(sum(1 for x in cp_ref["per_atom_maxima"] if x > 1)),
                "maxima_set_sha256": cp_ref["maxima_set_sha256"],
                "baderkit_n_maxima": int(ref["n_maxima"]),
                "baderkit_num_vacuum_voxels": int(ref["num_vacuum_voxels"]),
                "baderkit_vacuum_charge_e": float(ref["vacuum_charge_e"]),
                "reference_labels_sha256": labels_sha256(labels_ref),
                "reference_charges_json": json.dumps([float(x) for x in q_ref], separators=(",", ":")),
                "fixed_basin_self_error_e": self_error,
                "reference_min_density": float(np.min(field)),
                "reference_max_density": float(np.max(field)),
                "load_seconds": load_seconds,
                "reference_bader_seconds": ref_bader_seconds,
                "reference_cp_seconds": cp_seconds,
            }
        except Exception as exc:  # noqa: BLE001
            return fail_everything("source_or_reference", exc)

        # ---------------- reconstructions ----------------
        for r in planned_rows:
            codec = r["codec"].lower()
            base = {
                "material_id": mid,
                "system_type": meta["system_type"],
                "corpus": meta["corpus"],
                "codec": r["codec"],
                "ladder": r["ladder"],
                "nominal_tolerance_relative": float(r["nominal_tolerance_relative"]),
                "nominal_tolerance_absolute": float(r["nominal_tolerance_absolute"]),
                "stored_realized_Linf": float(r["realized_Linf"]),
                "stored_Bader_error_resolved_e": float(r["Bader_error_resolved_e"]),
                "stored_compressed_bytes": int(r["compressed_bytes"]),
                "stability_floor_A1_e": float(r["stability_floor_A1_e"]),
                "eligible_A1_at_0.001": r["eligible_A1_at_0.001"] == "True",
            }
            try:
                t0 = time.time()
                rec, nbytes, codec_config = core.codec_roundtrip(codec, field, base["nominal_tolerance_absolute"], workdir)
                codec_seconds = time.time() - t0
                rec = np.asarray(rec, dtype=np.float64)
                if rec.shape != field.shape:
                    raise RuntimeError(f"reconstruction shape mismatch {rec.shape} != {field.shape}")
                if not np.all(np.isfinite(rec)):
                    raise RuntimeError("reconstruction contains non-finite values")
                realized = float(np.max(np.abs(rec - field)))
                ratio = realized / base["stored_realized_Linf"] if base["stored_realized_Linf"] > 0 else float("inf")
                gate = bool(GATE_LOW <= ratio <= GATE_HIGH)
                row = {
                    **base,
                    "codec_config": codec_config,
                    "compressed_bytes": int(nbytes),
                    "realized_Linf": realized,
                    "realized_over_stored": ratio,
                    "reproduction_gate_pass": gate,
                    "codec_seconds": codec_seconds,
                }
                if not gate:
                    row.update({
                        "n_max": "", "n_min": "", "delta_n_max": "", "delta_n_min": "", "jaccard_distance": "",
                        "n_max_common": "", "n_max_lost": "", "n_max_gained": "", "per_atom_maxima_json": "",
                        "per_atom_max_abs_change": "", "n_max_in_vacuum_basin": "", "maxima_set_sha256": "",
                        "bader_error_resolved_e": "", "bader_error_abs_diff_vs_stored_e": "", "n_voxels_reassigned": "",
                        "labels_sha256": "", "cp_seconds": "", "bader_seconds": "", "status": "GATE_FAIL",
                    })
                    payload["rows"].append(row)
                    payload["failures"].append({
                        "material_id": mid, "kind": "reconstruction", "codec": r["codec"], "ladder": r["ladder"],
                        "nominal_tolerance_relative": r["nominal_tolerance_relative"], "family": "", "seed_label": "",
                        "stage": "reproduction_gate",
                        "error": f"realized_Linf/stored = {ratio:.6f} outside [{GATE_LOW}, {GATE_HIGH}]",
                    })
                    del rec
                    continue
                t0 = time.time()
                mx, mn = critical_points(rec)
                cp_seconds = time.time() - t0
                cp = cp_summary(mx, mn, labels_ref, natoms)
                idx = cp.pop("_idx")
                del mx, mn
                jd, n_common, n_lost, n_gained = jaccard_distance(idx_ref, idx)
                per_atom_change = int(np.max(np.abs(np.asarray(cp["per_atom_maxima"]) - np.asarray(cp_ref["per_atom_maxima"])))) if natoms else 0
                row.update({
                    "n_max": cp["n_max"],
                    "n_min": cp["n_min"],
                    "delta_n_max": abs(cp["n_max"] - cp_ref["n_max"]),
                    "delta_n_min": abs(cp["n_min"] - cp_ref["n_min"]),
                    "jaccard_distance": jd,
                    "n_max_common": n_common,
                    "n_max_lost": n_lost,
                    "n_max_gained": n_gained,
                    "per_atom_maxima_json": json.dumps(cp["per_atom_maxima"], separators=(",", ":")),
                    "per_atom_max_abs_change": per_atom_change,
                    "n_max_in_vacuum_basin": cp["n_max_in_vacuum_basin"],
                    "maxima_set_sha256": cp["maxima_set_sha256"],
                    "cp_seconds": cp_seconds,
                })
                # A failed Bader re-solve keeps the cp result: the row is written with status CP_ONLY
                # and empty Bader fields, and the failure is recorded separately at stage "bader".
                try:
                    t0 = time.time()
                    res = core.run_bader(core.clone_grid_with_total(grid, rec))
                    bader_seconds = time.time() - t0
                    q_new = np.asarray(res["charges"], dtype=np.float64)
                    labels_new = np.asarray(res["atom_labels"])
                    if q_new.shape != q_ref.shape:
                        raise RuntimeError(f"Bader charge shape mismatch {q_new.shape} != {q_ref.shape}")
                    bader_err = float(np.max(np.abs(q_new - q_ref)))
                    row.update({
                        "bader_error_resolved_e": bader_err,
                        "bader_error_abs_diff_vs_stored_e": abs(bader_err - base["stored_Bader_error_resolved_e"]),
                        "n_voxels_reassigned": int(np.count_nonzero(labels_new != labels_ref)),
                        "labels_sha256": labels_sha256(labels_new),
                        "bader_seconds": bader_seconds,
                        "status": "SUCCESS",
                    })
                    del res, q_new, labels_new
                except Exception as exc:  # noqa: BLE001
                    row.update({
                        "bader_error_resolved_e": "", "bader_error_abs_diff_vs_stored_e": "", "n_voxels_reassigned": "",
                        "labels_sha256": "", "bader_seconds": "", "status": "CP_ONLY",
                    })
                    payload["failures"].append({
                        "material_id": mid, "kind": "reconstruction", "codec": r["codec"], "ladder": r["ladder"],
                        "nominal_tolerance_relative": r["nominal_tolerance_relative"], "family": "", "seed_label": "",
                        "stage": "bader", "error": f"{type(exc).__name__}: {exc}",
                    })
                payload["rows"].append(row)
                del rec, idx
            except Exception as exc:  # noqa: BLE001
                payload["failures"].append({
                    "material_id": mid, "kind": "reconstruction", "codec": r["codec"], "ladder": r["ladder"],
                    "nominal_tolerance_relative": r["nominal_tolerance_relative"], "family": "", "seed_label": "",
                    "stage": "codec_or_qoi", "error": f"{type(exc).__name__}: {exc}",
                })
            gc.collect()

        # ---------------- perturbation probes ----------------
        for family, label, stream_seed in planned_probes:
            try:
                rng = np.random.Generator(np.random.PCG64(stream_seed))
                noise = rng.uniform(-epsilon, epsilon, size=field.shape).astype(np.float64, copy=False)
                measured_linf = float(np.max(np.abs(noise)))
                if measured_linf > epsilon * (1 + 16 * np.finfo(np.float64).eps):
                    raise RuntimeError(f"realized perturbation exceeds epsilon: {measured_linf} > {epsilon}")
                perturbed = field + noise
                mean_noise = float(np.mean(noise))
                rms_noise = float(np.sqrt(np.mean(noise * noise)))
                del noise
                if not np.all(np.isfinite(perturbed)):
                    raise RuntimeError("perturbed field contains non-finite values")
                t0 = time.time()
                mx, mn = critical_points(perturbed)
                cp_seconds = time.time() - t0
                cp = cp_summary(mx, mn, labels_ref, natoms)
                idx = cp.pop("_idx")
                del mx, mn
                jd, n_common, n_lost, n_gained = jaccard_distance(idx_ref, idx)
                per_atom_change = int(np.max(np.abs(np.asarray(cp["per_atom_maxima"]) - np.asarray(cp_ref["per_atom_maxima"])))) if natoms else 0
                t0 = time.time()
                res = core.run_bader(core.clone_grid_with_total(grid, perturbed))
                bader_seconds = time.time() - t0
                q_new = np.asarray(res["charges"], dtype=np.float64)
                labels_new = np.asarray(res["atom_labels"])
                if q_new.shape != q_ref.shape:
                    raise RuntimeError(f"Bader charge shape mismatch {q_new.shape} != {q_ref.shape}")
                bader_resp = float(np.max(np.abs(q_new - q_ref)))
                frozen = frozen_seed_resp.get(str(label)) if family == "qsq_seed" else frozen_fresh_resp.get(str(label))
                payload["probes"].append({
                    "material_id": mid,
                    "system_type": meta["system_type"],
                    "corpus": meta["corpus"],
                    "family": family,
                    "seed_label": label,
                    "stream_seed": stream_seed,
                    "epsilon": epsilon,
                    "measured_Linf": measured_linf,
                    "measured_L2_rms": rms_noise,
                    "mean_perturbation_e": mean_noise,
                    "perturbed_negative_voxels": int(np.count_nonzero(perturbed < 0)),
                    "n_max": cp["n_max"],
                    "n_min": cp["n_min"],
                    "delta_n_max": abs(cp["n_max"] - cp_ref["n_max"]),
                    "delta_n_min": abs(cp["n_min"] - cp_ref["n_min"]),
                    "jaccard_distance": jd,
                    "n_max_common": n_common,
                    "n_max_lost": n_lost,
                    "n_max_gained": n_gained,
                    "per_atom_maxima_json": json.dumps(cp["per_atom_maxima"], separators=(",", ":")),
                    "per_atom_max_abs_change": per_atom_change,
                    "n_max_in_vacuum_basin": cp["n_max_in_vacuum_basin"],
                    "maxima_set_sha256": cp["maxima_set_sha256"],
                    "bader_response_max_e": bader_resp,
                    "frozen_bader_response_max_e": frozen if frozen is not None else "",
                    "bader_response_abs_diff_vs_frozen_e": abs(bader_resp - frozen) if frozen is not None else "",
                    "n_voxels_reassigned": int(np.count_nonzero(labels_new != labels_ref)),
                    "labels_sha256": labels_sha256(labels_new),
                    "cp_seconds": cp_seconds,
                    "bader_seconds": bader_seconds,
                    "status": "SUCCESS",
                })
                del perturbed, res, q_new, labels_new, idx
            except Exception as exc:  # noqa: BLE001
                payload["failures"].append({
                    "material_id": mid, "kind": "probe", "codec": "", "ladder": "", "nominal_tolerance_relative": "",
                    "family": family, "seed_label": label, "stage": "perturbation_or_qoi",
                    "error": f"{type(exc).__name__}: {exc}",
                })
            gc.collect()

    payload["wall_seconds"] = time.time() - t_start
    payload["planned_rows"] = len(planned_rows)
    payload["planned_probes"] = len(planned_probes)
    return payload


def _run_task(task: dict[str, Any]) -> tuple[str, str, float]:
    ckpt = Path(task["checkpoint_dir"]) / f"{task['material_id']}.json"
    try:
        payload = process_material(task)
    except Exception as exc:  # noqa: BLE001
        payload = {
            "material_id": task["material_id"], "status": "FAILED", "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(), "reference": None, "rows": [], "probes": [], "failures": [],
        }
        err = payload["error"]
        for r in task["bench_rows"]:
            payload["failures"].append({
                "material_id": task["material_id"], "kind": "reconstruction", "codec": r["codec"], "ladder": r["ladder"],
                "nominal_tolerance_relative": r["nominal_tolerance_relative"], "family": "", "seed_label": "",
                "stage": "worker_crash", "error": err,
            })
        for s in QSQ_SEEDS:
            payload["failures"].append({
                "material_id": task["material_id"], "kind": "probe", "codec": "", "ladder": "",
                "nominal_tolerance_relative": "", "family": "qsq_seed", "seed_label": s, "stage": "worker_crash", "error": err,
            })
        for j in task["fresh_jobs"]:
            payload["failures"].append({
                "material_id": task["material_id"], "kind": "probe", "codec": "", "ladder": "",
                "nominal_tolerance_relative": "", "family": "fresh_iid", "seed_label": int(j["seed_label"]),
                "stage": "worker_crash", "error": err,
            })
        payload["wall_seconds"] = float("nan")
    atomic_write_json(ckpt, payload)
    return task["material_id"], payload["status"], float(payload.get("wall_seconds", float("nan")))


# ----------------------------------------------------------------------------
# aggregation of checkpoints into the protocol CSVs
# ----------------------------------------------------------------------------
REFERENCE_FIELDS = [
    "material_id", "system_type", "corpus", "source", "formula", "loader", "fetch_mode", "source_sha256",
    "source_bytes", "npoints", "grid_shape", "natoms", "value_ptp", "epsilon", "n_max", "n_min",
    "per_atom_maxima_json", "n_max_in_vacuum_basin", "n_atoms_with_zero_maxima", "n_atoms_with_multiple_maxima",
    "maxima_set_sha256", "baderkit_n_maxima", "baderkit_num_vacuum_voxels", "baderkit_vacuum_charge_e",
    "reference_labels_sha256", "reference_charges_json", "fixed_basin_self_error_e", "reference_min_density",
    "reference_max_density", "load_seconds", "reference_bader_seconds", "reference_cp_seconds", "status",
]
ROW_FIELDS = [
    "material_id", "system_type", "corpus", "codec", "ladder", "nominal_tolerance_relative",
    "nominal_tolerance_absolute", "stored_realized_Linf", "stored_Bader_error_resolved_e", "stored_compressed_bytes",
    "stability_floor_A1_e", "eligible_A1_at_0.001", "codec_config", "compressed_bytes", "realized_Linf",
    "realized_over_stored", "reproduction_gate_pass", "n_max", "n_min", "delta_n_max", "delta_n_min",
    "jaccard_distance", "n_max_common", "n_max_lost", "n_max_gained", "per_atom_maxima_json",
    "per_atom_max_abs_change", "n_max_in_vacuum_basin", "maxima_set_sha256", "bader_error_resolved_e",
    "bader_error_abs_diff_vs_stored_e", "n_voxels_reassigned", "labels_sha256", "codec_seconds", "cp_seconds",
    "bader_seconds", "status",
]
PROBE_FIELDS = [
    "material_id", "system_type", "corpus", "family", "seed_label", "stream_seed", "epsilon", "measured_Linf",
    "measured_L2_rms", "mean_perturbation_e", "perturbed_negative_voxels", "n_max", "n_min", "delta_n_max",
    "delta_n_min", "jaccard_distance", "n_max_common", "n_max_lost", "n_max_gained", "per_atom_maxima_json",
    "per_atom_max_abs_change", "n_max_in_vacuum_basin", "maxima_set_sha256", "bader_response_max_e",
    "frozen_bader_response_max_e", "bader_response_abs_diff_vs_frozen_e", "n_voxels_reassigned", "labels_sha256",
    "cp_seconds", "bader_seconds", "status",
]
FAILURE_FIELDS = [
    "material_id", "kind", "codec", "ladder", "nominal_tolerance_relative", "family", "seed_label", "stage", "error",
]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def aggregate(checkpoint_dir: Path, outdir: Path, materials: list[str]) -> dict[str, Any]:
    refs: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    probes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    material_status: list[dict[str, Any]] = []
    for mid in materials:
        ckpt = checkpoint_dir / f"{mid}.json"
        if not ckpt.exists():
            raise RuntimeError(f"missing checkpoint for {mid}")
        payload = json.loads(ckpt.read_text(encoding="utf-8"))
        material_status.append({
            "material_id": mid, "status": payload["status"], "wall_seconds": payload.get("wall_seconds"),
            "rows": len(payload["rows"]), "probes": len(payload["probes"]), "failures": len(payload["failures"]),
        })
        if payload["reference"] is not None:
            refs.append({**payload["reference"], "status": "SUCCESS"})
        else:
            refs.append({"material_id": mid, "status": "FAILED"})
        rows.extend(payload["rows"])
        probes.extend(payload["probes"])
        failures.extend(payload["failures"])
    rows.sort(key=lambda r: (r["material_id"], r["codec"], r["ladder"], float(r["nominal_tolerance_relative"])))
    probes.sort(key=lambda r: (r["material_id"], 0 if r["family"] == "qsq_seed" else 1, int(r["seed_label"])))
    failures.sort(key=lambda r: (r["material_id"], r["kind"], str(r["codec"]), str(r["nominal_tolerance_relative"]), str(r["seed_label"])))
    write_csv(outdir / "cp_reference.csv", REFERENCE_FIELDS, refs)
    write_csv(outdir / "cp_rows.csv", ROW_FIELDS, rows)
    write_csv(outdir / "cp_probes.csv", PROBE_FIELDS, probes)
    write_csv(outdir / "failures.csv", FAILURE_FIELDS, failures)
    write_csv(outdir / "material_run_status.csv", ["material_id", "status", "wall_seconds", "rows", "probes", "failures"], material_status)
    return {
        "materials": len(materials),
        "references": sum(1 for r in refs if r["status"] == "SUCCESS"),
        "rows": len(rows),
        "rows_gate_pass": sum(1 for r in rows if r["reproduction_gate_pass"]),
        "probes": len(probes),
        "failures": len(failures),
        "materials_failed": sum(1 for s in material_status if s["status"] != "SUCCESS"),
    }


# ----------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    p.add_argument("--frozen-validation-dir", type=Path, default=DEFAULT_FROZEN_VALIDATION)
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    p.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINTS)
    p.add_argument("--output-dir", type=Path, default=HERE)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--materials", type=str, default="", help="comma-separated subset (smoke only)")
    p.add_argument("--aggregate-only", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo = args.repo_root.resolve()
    outdir = args.output_dir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    ckdir = args.checkpoint_dir.resolve()
    ckdir.mkdir(parents=True, exist_ok=True)
    inputs = load_inputs(repo)
    materials = inputs["dev_materials"]
    if args.materials:
        wanted = set(args.materials.split(","))
        materials = [m for m in materials if m in wanted]
    log = outdir / "run_log.txt"

    def logline(msg: str) -> None:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with log.open("a", encoding="utf-8") as f:
            f.write(f"{stamp} {msg}\n")
        print(f"{stamp} {msg}", flush=True)

    if not args.aggregate_only:
        population = {
            "population": "FULL_LADDER",
            "declared_before_any_statistic": True,
            "materials": len(materials),
            "reconstruction_rows_planned": sum(len(inputs["bench"][m]) for m in materials),
            "qsq_seed_probes_planned": len(QSQ_SEEDS) * len(materials),
            "fresh_probes_planned": len(FRESH_LABELS) * len(materials),
            "qsq_seeds": list(QSQ_SEEDS),
            "fresh_seed_labels": [FRESH_LABELS[0], FRESH_LABELS[-1]],
            "reproduction_gate": [GATE_LOW, GATE_HIGH],
            "declared_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        (outdir / "population.json").write_text(json.dumps(population, indent=2), encoding="utf-8")
        pending = [m for m in materials if not (ckdir / f"{m}.json").exists()]
        logline(f"population FULL_LADDER: {len(materials)} materials; {len(pending)} pending, {len(materials) - len(pending)} checkpointed")
        tasks = [{
            "material_id": m,
            "meta": inputs["metadata"][m],
            "bench_rows": inputs["bench"][m],
            "epsilon": inputs["amp"][m],
            "fresh_jobs": inputs["fresh"][m],
            "frozen_seed_response": {str(s): inputs["frozen_seed_response"][(m, s)] for s in QSQ_SEEDS},
            "frozen_fresh_response": {str(l): inputs["frozen_fresh_response"][(m, l)] for l in FRESH_LABELS if (m, l) in inputs["frozen_fresh_response"]},
            "cache": str(args.cache_dir.resolve()),
            "checkpoint_dir": str(ckdir),
        } for m in pending]
        t_run = time.time()
        if tasks:
            import multiprocessing as mp

            ctx = mp.get_context("spawn")
            init_args = (str(args.frozen_validation_dir.resolve()), str(repo))
            done = 0
            with ctx.Pool(processes=args.workers, initializer=_init_worker, initargs=init_args, maxtasksperchild=8) as pool:
                for mid, status, secs in pool.imap_unordered(_run_task, tasks):
                    done += 1
                    logline(f"[{done}/{len(tasks)}] {mid} {status} {secs:.1f}s")
        logline(f"execution wall seconds this invocation: {time.time() - t_run:.1f}")

    counts = aggregate(ckdir, outdir, materials)
    logline(f"aggregate: {json.dumps(counts)}")
    (outdir / "aggregate_counts.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
