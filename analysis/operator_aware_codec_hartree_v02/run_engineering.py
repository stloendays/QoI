#!/usr/bin/env python3
"""Run one deterministic shard of the QOAC-H v0.2 engineering cohort."""
from __future__ import annotations

import argparse
import csv
import hashlib
import math
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import codec_qoac_h_v02 as qoac2  # noqa: E402

V01_DIR = HERE.parent / "operator_aware_codec_hartree"
sys.path.insert(0, str(V01_DIR))
import codec_qoac_h as qoac1  # noqa: E402

ALPHA_REL = np.logspace(-7.0, 1.0, 25)
BETA = 2.0
ZLIB_LEVEL = 6
SHELL_COUNT = 32
TAU = 1e-6


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--shard-count", type=int, required=True)
    p.add_argument("--shard-index", type=int, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def shard_for(material_id: str, n: int) -> int:
    d = hashlib.sha256(("QOAC-H-V02-ENGINEERING|" + material_id).encode()).digest()
    return int.from_bytes(d[:8], "big") % n


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    args = parse_args()
    if args.shard_count <= 0 or not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("invalid shard parameters")

    repo = args.repo_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev  # type: ignore  # noqa: E402

    with args.manifest.open(newline="", encoding="utf-8") as f:
        manifest = list(csv.DictReader(f))
    if len(manifest) != 12 or len({r["material_id"] for r in manifest}) != 12:
        raise RuntimeError("v0.2 engineering manifest must contain the exact 12 v0.1 materials")

    planned = [
        r for r in manifest
        if shard_for(r["material_id"], args.shard_count) == args.shard_index
    ]

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    planned_rows = [{"material_id": r["material_id"]} for r in planned]

    for meta in planned:
        mid = meta["material_id"]
        t_material = time.perf_counter()
        try:
            blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="qoac_h_v02_") as td:
                grid, loader = dev.build_grid(meta, blob, Path(td))
                field = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
                lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)

                expected_shape = tuple(int(x) for x in meta["ngrid"].split("x"))
                if tuple(field.shape) != expected_shape:
                    raise RuntimeError(f"grid shape mismatch {field.shape} != {expected_shape}")
                if int(field.size) != int(meta["npoints"]):
                    raise RuntimeError("grid npoints mismatch")
                if not np.all(np.isfinite(field)):
                    raise RuntimeError("non-finite source field")

                ptp = float(np.ptp(field))
                if not (math.isfinite(ptp) and ptp > 0):
                    raise RuntimeError("invalid source ptp")

                raw_bytes = int(field.nbytes)
                neg_ref = float(np.mean(field < 0.0))
                prepared = qoac2.prepare(field, lattice, shell_count=SHELL_COUNT)
                ref_hist, ref_safe = qoac1.reference_hartree_rms(field, lattice)

                geometry = prepared.geometry
                canonical_nonzero = int(np.count_nonzero(geometry.g2_cons > 0.0))
                self_nonzero = int(np.count_nonzero(
                    geometry.self_mask & (geometry.g2_cons > 0.0)
                ))

                for alpha_rel in ALPHA_REL:
                    alpha = float(alpha_rel * ptp)
                    try:
                        stream, enc = qoac2.encode_prepared(
                            prepared,
                            alpha=alpha,
                            beta=BETA,
                            zlib_level=ZLIB_LEVEL,
                        )
                        recon, spectrum, _, dec = qoac2.decode_blob(
                            stream,
                            return_spectrum=True,
                            geometry=geometry,
                        )
                        if not np.all(np.isfinite(recon)):
                            raise RuntimeError("non-finite reconstruction")
                        if float(dec["max_ifft_imag"]) > 1e-10:
                            raise RuntimeError(
                                f"Hermitian decode failure: max_ifft_imag={dec['max_ifft_imag']}"
                            )

                        err = recon - field
                        h_hist, h_safe = qoac1.hartree_error_metrics(
                            err,
                            lattice,
                            ref_hist,
                            ref_safe,
                        )
                        h_cons = qoac2.conservative_hartree_relative(
                            prepared,
                            spectrum,
                        )
                        dual_certified = bool(h_hist < TAU and h_cons < TAU)

                        rows.append({
                            "material_id": mid,
                            "system_type": meta["system_type"],
                            "formula": meta["formula"],
                            "source": meta["source"],
                            "source_sha256": meta["sha256"],
                            "loader": loader,
                            "npoints": int(field.size),
                            "raw_bytes": raw_bytes,
                            "beta": BETA,
                            "alpha_rel_ptp": float(alpha_rel),
                            "alpha_abs": alpha,
                            "encoded_bytes": len(stream),
                            "compression_ratio": raw_bytes / len(stream),
                            "hartree_error_rel_RMSE_historical": h_hist,
                            "hartree_error_rel_RMSE_safe": h_safe,
                            "hartree_error_rel_conservative_alias": h_cons,
                            "dual_certified_tau_1e-6": dual_certified,
                            "density_Linf": float(np.max(np.abs(err))),
                            "density_RMSE": float(np.sqrt(np.mean(err * err))),
                            "mean_density_deviation": float(
                                abs(np.mean(recon) - np.mean(field))
                            ),
                            "negative_fraction_reference": neg_ref,
                            "negative_fraction_reconstruction": float(np.mean(recon < 0.0)),
                            "negative_fraction_delta": float(np.mean(recon < 0.0) - neg_ref),
                            "max_ifft_imag": float(dec["max_ifft_imag"]),
                            "encode_seconds": float(enc["encode_seconds"]),
                            "decode_seconds": float(dec["decode_seconds"]),
                            "canonical_reps": int(enc["canonical_reps"]),
                            "self_reps": int(enc["self_reps"]),
                            "canonical_nonzero_reps": canonical_nonzero,
                            "self_nonzero_reps": self_nonzero,
                            "shell_count": SHELL_COUNT,
                            "zlib_level": ZLIB_LEVEL,
                        })
                    except Exception as exc:
                        failures.append({
                            "material_id": mid,
                            "stage": "setting",
                            "alpha_rel_ptp": float(alpha_rel),
                            "error": f"{type(exc).__name__}: {exc}"[:700],
                        })
        except Exception as exc:
            failures.append({
                "material_id": mid,
                "stage": "material",
                "error": f"{type(exc).__name__}: {exc}"[:700],
            })

        print(
            f"QOAC_H_V02_MATERIAL_DONE {mid} "
            f"seconds={time.perf_counter() - t_material:.1f} "
            f"rows={sum(r['material_id'] == mid for r in rows)} "
            f"failures={sum(r['material_id'] == mid for r in failures)}",
            flush=True,
        )

    write_csv(out / f"rows_shard_{args.shard_index:02d}.csv", rows)
    write_csv(out / f"failures_shard_{args.shard_index:02d}.csv", failures)
    write_csv(out / f"planned_shard_{args.shard_index:02d}.csv", planned_rows)

    print(
        f"QOAC_H_V02_SHARD_DONE shard={args.shard_index} "
        f"materials={len(planned)} rows={len(rows)} failures={len(failures)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
