#!/usr/bin/env python3
"""Measure the lossless Bader atom-label stream for one manifest shard.

The scientific execution path is deliberately small.  The charge-density
loader and the Henkelman wrapper are imported from the frozen QOAC-H/B1
implementation; this file only adds the self-contained label serialization
and its two protocol checks.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import lzma
import os
import struct
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
HEADER = struct.Struct("<4I")
HEADER_BYTES = HEADER.size
CHARGE_TOLERANCE_E = 1e-5

MATERIAL_FIELDS = [
    "material_id",
    "task_id",
    "shape",
    "npoints",
    "natoms",
    "label_bytes_primary",
    "label_bytes_ctx",
    "n_labels",
    "roundtrip_ok",
    "charge_check_ok",
    "max_charge_diff_e",
    "status",
    "seconds",
]
FAILURE_FIELDS = ["material_id", "task_id", "stage", "error", "traceback"]


def shard_for(material_id: str, shard_count: int) -> int:
    """Return the shard used by ``run_joint_v2.shard_for``."""
    if int(shard_count) <= 0:
        raise ValueError("shard_count must be positive")
    return int.from_bytes(
        hashlib.sha256(("QOAC-HB-V2|" + str(material_id)).encode()).digest()[:8],
        "big",
    ) % int(shard_count)


def encode_label_stream(labels: np.ndarray, natoms: int) -> bytes:
    """Serialize a 3-D atom-index map using the frozen 16-byte header.

    The payload is exactly the protocol expression: little-endian uint16
    labels in C order, compressed with LZMA preset 9 plus EXTREME.
    """
    raw = np.asarray(labels)
    if not np.issubdtype(raw.dtype, np.integer):
        raise TypeError("labels must have an integer dtype")
    lab = np.ascontiguousarray(raw, dtype=np.int64)
    if lab.ndim != 3:
        raise ValueError("label map must be three-dimensional")
    if any(int(n) <= 0 or int(n) >= 2**32 for n in lab.shape):
        raise ValueError(f"invalid grid shape for uint32 header: {lab.shape}")
    if int(natoms) < 0 or int(natoms) >= 2**32:
        raise ValueError("atom count does not fit uint32 header")
    if lab.size and (int(lab.min()) < 0 or int(lab.max()) >= 2**16):
        raise ValueError("labels do not fit uint16")
    header = HEADER.pack(*(int(n) for n in lab.shape), int(natoms))
    payload = lzma.compress(
        lab.astype("<u2", copy=False).tobytes(order="C"),
        preset=9 | lzma.PRESET_EXTREME,
    )
    return header + payload


def decode_label_stream(blob: bytes) -> tuple[tuple[int, int, int], int, np.ndarray]:
    """Decode ``encode_label_stream`` and validate its byte count."""
    if len(blob) < HEADER_BYTES:
        raise ValueError("truncated label-stream header")
    n1, n2, n3, natoms = HEADER.unpack(blob[:HEADER_BYTES])
    shape = (int(n1), int(n2), int(n3))
    npoints = int(np.prod(shape, dtype=np.int64))
    raw = lzma.decompress(blob[HEADER_BYTES:])
    expected = 2 * npoints
    if len(raw) != expected:
        raise ValueError(f"label payload byte count {len(raw)} != {expected}")
    labels = np.frombuffer(raw, dtype="<u2").reshape(shape, order="C").copy()
    return shape, int(natoms), labels.astype(np.int64, copy=False)


def charges_from_labels(chg: np.ndarray, labels: np.ndarray, natoms: int) -> np.ndarray:
    """Reproduce the binary's fixed-grid per-atom charge calculation.

    Henkelman's ACF charge for a VASP grid is the sum of the exact CHGCAR
    values in the atom-labelled voxels divided by the total number of voxels.
    Label zero is the vacuum/non-atom label and is not returned.
    """
    field = np.ascontiguousarray(np.asarray(chg, dtype=np.float64))
    lab = np.ascontiguousarray(np.asarray(labels, dtype=np.int64))
    if field.shape != lab.shape:
        raise ValueError("charge field and label map shape mismatch")
    if field.ndim != 3 or field.size == 0:
        raise ValueError("charge field must be a non-empty 3-D grid")
    if not np.all(np.isfinite(field)):
        raise ValueError("charge field contains non-finite values")
    if np.any(lab < 0):
        raise ValueError("labels must be non-negative")
    if int(natoms) < 0:
        raise ValueError("natoms must be non-negative")
    max_label = int(lab.max(initial=0))
    sums = np.bincount(
        lab.ravel(),
        weights=field.ravel(),
        minlength=max(int(natoms) + 1, max_label + 1),
    )
    return np.asarray(sums[1 : int(natoms) + 1] / field.size, dtype=np.float64)


def check_stored_labels(
    stored: bytes,
    labels: np.ndarray,
    chg: np.ndarray,
    binary_charges: np.ndarray,
    natoms: int,
) -> dict[str, Any]:
    """Run the protocol's round-trip and ACF charge checks."""
    shape, header_natoms, decoded = decode_label_stream(stored)
    expected = np.asarray(labels, dtype=np.int64)
    roundtrip_ok = bool(
        shape == tuple(int(n) for n in expected.shape)
        and header_natoms == int(natoms)
        and np.array_equal(decoded, expected)
    )
    calculated = charges_from_labels(chg, decoded, natoms)
    reference = np.asarray(binary_charges, dtype=np.float64)
    if calculated.shape != reference.shape:
        raise ValueError(f"charge vector shape mismatch: {calculated.shape} != {reference.shape}")
    max_diff = float(np.max(np.abs(calculated - reference))) if reference.size else 0.0
    return {
        "roundtrip_ok": roundtrip_ok,
        "charge_check_ok": bool(max_diff <= CHARGE_TOLERANCE_E),
        "max_charge_diff_e": max_diff,
        "decoded": decoded,
    }


def _frozen_validation_dir(repo_root: Path) -> Path | None:
    env = os.environ.get("QOAC_FROZEN_VALIDATION_DIR")
    candidates = []
    if env:
        candidates.append(Path(env))
    candidates.extend(
        [
            repo_root.parent / "frozen" / "validation",
            repo_root / "frozen" / "validation",
            repo_root / "validation",
        ]
    )
    for candidate in candidates:
        if (candidate / "external_end_to_end.py").is_file():
            return candidate.resolve()
    return None


def _load_runtime(repo_root: Path) -> tuple[Any, Any, Any]:
    """Load the existing HB runner, development loader and B3 cost helper."""
    analysis = repo_root / "analysis"
    hb_dir = analysis / "qoac_hb_v2"
    b3_dir = analysis / "qoac_b3_design"
    dev_dir = repo_root / "validation" / "qsq_prospective"
    for path in (hb_dir, b3_dir, dev_dir):
        text = str(path.resolve())
        if text not in sys.path:
            sys.path.insert(0, text)

    joint = importlib.import_module("run_joint_v2")
    b3 = importlib.import_module("b3_correct")
    # The development loader is in the research checkout; the frozen checkout
    # is needed only for the separately imported validation stack in the CI
    # environment and is kept discoverable for callers that use it.
    frozen_validation = _frozen_validation_dir(repo_root)
    if frozen_validation is not None:
        text = str(frozen_validation)
        if text not in sys.path:
            sys.path.insert(0, text)
    dev = importlib.import_module("development_compatibility_smoke")
    return joint, dev, b3


def _shape_text(shape: tuple[int, ...]) -> str:
    return "x".join(str(int(n)) for n in shape)


def _failure(material_id: str, task_id: str, stage: str, error: str, tb: str = "") -> dict[str, str]:
    return {
        "material_id": str(material_id),
        "task_id": str(task_id),
        "stage": str(stage),
        "error": str(error),
        "traceback": str(tb),
    }


def process_material(meta: dict[str, str], bader: Path, repo_root: Path | None = None) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Run the frozen reference Bader calculation and both label checks."""
    root = (repo_root or REPO_ROOT).resolve()
    material_id = str(meta["material_id"])
    task_id = str(meta["task_id"])
    t0 = time.perf_counter()
    failures: list[dict[str, str]] = []
    row: dict[str, Any] = {"material_id": material_id, "task_id": task_id, "status": "FAILED"}
    stage = "runtime import"
    try:
        joint, dev, b3 = _load_runtime(root)
        stage = "download"
        # These three calls and the CHGCAR checksum are intentionally the same
        # operations as run_joint_v2.process.
        chg_blob = joint.b1.fetch(meta["url"])
        if hashlib.sha256(chg_blob).hexdigest() != meta["sha256"]:
            raise RuntimeError("CHGCAR checksum mismatch")
        aeccar0 = joint.b1.fetch(joint.b1.BUCKET + f"aeccar0s/{task_id}.json.gz")
        aeccar2 = joint.b1.fetch(joint.b1.BUCKET + f"aeccar2s/{task_id}.json.gz")

        stage = "decode"
        with tempfile.TemporaryDirectory(prefix="hb_selfcontained_") as td:
            work = Path(td)
            grid, _ = dev.build_grid(meta, chg_blob, work)
            chg = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
            ae = np.asarray(dev.decode_mp_chgcar(aeccar0).data["total"], dtype=np.float64)
            ae += np.asarray(dev.decode_mp_chgcar(aeccar2).data["total"], dtype=np.float64)
            if ae.shape != chg.shape or not np.all(np.isfinite(ae)):
                raise RuntimeError("invalid AECCAR")

            structure = grid.structure
            lattice = np.asarray(structure.lattice.matrix, dtype=float)
            frac = np.asarray(structure.frac_coords, dtype=float)
            symbols = [site.specie.symbol for site in structure]
            natoms = len(symbols)
            row.update(
                shape=_shape_text(tuple(int(n) for n in chg.shape)),
                npoints=int(chg.size),
                natoms=int(natoms),
            )

            stage = "bader"
            solver = joint.b1.Solver(bader, lattice, frac, symbols, chg.shape, work)
            binary_charges, labels_fortran = solver(chg, ae)
            labels = joint.qb.label_grid_from_fortran_flat(labels_fortran, chg.shape)
            labels = np.ascontiguousarray(np.asarray(labels, dtype=np.int64))
            if labels.size == 0:
                raise RuntimeError("empty atom-index map")

            stage = "serialize"
            stored = encode_label_stream(labels, natoms)
            costs = b3.label_map_cost(labels)
            row.update(
                label_bytes_primary=int(len(stored)),
                label_bytes_ctx=int(costs["ctx_bytes"]),
                n_labels=int(labels.max()) + 1,
            )

            stage = "checks"
            checks = check_stored_labels(stored, labels, chg, binary_charges, natoms)
            row.update(
                roundtrip_ok=bool(checks["roundtrip_ok"]),
                charge_check_ok=bool(checks["charge_check_ok"]),
                max_charge_diff_e=float(checks["max_charge_diff_e"]),
            )
            if not checks["roundtrip_ok"]:
                failures.append(_failure(material_id, task_id, "roundtrip", "decoded label stream differs from L"))
            if not checks["charge_check_ok"]:
                failures.append(
                    _failure(
                        material_id,
                        task_id,
                        "charge_check",
                        f"max charge difference {checks['max_charge_diff_e']:.17g} e exceeds {CHARGE_TOLERANCE_E:g} e",
                    )
                )
            row["status"] = "SUCCESS" if not failures else "CHECK_FAILED"
    except Exception as exc:  # noqa: BLE001 - one material must not hide shard failures
        message = f"{type(exc).__name__}: {exc}"
        tb = traceback.format_exc()
        failures.append(_failure(material_id, task_id, stage, message, tb))
        row["status"] = "FAILED"
    row["seconds"] = float(time.perf_counter() - t0)
    return row, failures


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--bader", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.shard_count <= 0 or not 0 <= args.shard_index < args.shard_count:
        raise SystemExit("invalid shard count/index")
    with args.manifest.open(newline="", encoding="utf-8") as fh:
        manifest = list(csv.DictReader(fh))
    if not manifest:
        raise SystemExit("manifest is empty")
    planned = [
        meta
        for meta in manifest
        if shard_for(meta["material_id"], args.shard_count) == args.shard_index
    ]
    materials: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for meta in planned:
        row, material_failures = process_material(meta, args.bader, REPO_ROOT)
        materials.append(row)
        failures.extend(material_failures)
        print(
            f"HB_SELFCONTAINED_DONE {meta['material_id']} {row['status']} "
            f"seconds={float(row['seconds']):.1f}",
            flush=True,
        )
    out = args.output_dir.resolve()
    shard = f"{args.shard_index:02d}"
    _write_csv(out / f"materials_shard_{shard}.csv", materials, MATERIAL_FIELDS)
    _write_csv(out / f"failures_shard_{shard}.csv", failures, FAILURE_FIELDS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
