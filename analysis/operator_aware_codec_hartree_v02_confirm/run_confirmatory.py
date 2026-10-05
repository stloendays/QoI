#!/usr/bin/env python3
"""Run one frozen shard of the QOAC-H v0.2 held-out confirmation."""
from __future__ import annotations

import argparse
import csv
import math
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
V02_DIR = HERE.parent / "operator_aware_codec_hartree_v02"
V01_DIR = HERE.parent / "operator_aware_codec_hartree"
sys.path.insert(0, str(V02_DIR))
sys.path.insert(0, str(V01_DIR))

import codec_qoac_h_v02 as qoac2  # noqa: E402
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
    p.add_argument("--shard-index", type=int, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


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


def truthy(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "t"}


def main() -> int:
    args = parse_args()
    if not 0 <= args.shard_index < 24:
        raise SystemExit("confirmatory shard index must be in [0, 23]")

    repo = args.repo_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev  # type: ignore  # noqa: E402

    with args.manifest.open(newline="", encoding="utf-8") as f:
        manifest = list(csv.DictReader(f))

    if len(manifest) != 242 or len({r["material_id"] for r in manifest}) != 242:
        raise RuntimeError("held-out manifest must contain exactly 242 unique materials")
    if any(not truthy(r["eligible_tau_1e-6"]) for r in manifest):
        raise RuntimeError("manifest contains a non-eligible material at tau=1e-6")
    if any(float(r["hartree_qsq_response_scale_rel_RMSE"]) >= TAU for r in manifest):
        raise RuntimeError("frozen QSQ response violates tau=1e-6 eligibility")

    planned = [
        r for r in manifest
        if int(r["confirmatory_shard"]) == args.shard_index
    ]

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    planned_rows = [
        {
            "material_id": r["material_id"],
            "confirmatory_shard": args.shard_index,
            "npoints": int(r["npoints"]),
        }
        for r in planned
    ]

    for meta in planned:
        mid = meta["material_id"]
        t_material = time.perf_counter()
        try:
            blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="qoac_h_v02_confirm_") as td:
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
                            "confirmatory_shard": args.shard_index,
                            "system_type": meta["system_type"],
                            "formula": meta["formula"],
                            "source": meta["source"],
                            "source_sha256": meta["sha256"],
                            "loader": loader,
                            "hartree_qsq_response_scale_rel_RMSE": float(
                                meta["hartree_qsq_response_scale_rel_RMSE"]
                            ),
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
                            "shell_count": SHELL_COUNT,
                            "zlib_level": ZLIB_LEVEL,
                        })
                    except Exception as exc:
                        failures.append({
                            "material_id": mid,
                            "confirmatory_shard": args.shard_index,
                            "stage": "setting",
                            "alpha_rel_ptp": float(alpha_rel),
                            "error": f"{type(exc).__name__}: {exc}"[:800],
                        })
        except Exception as exc:
            failures.append({
                "material_id": mid,
                "confirmatory_shard": args.shard_index,
                "stage": "material",
                "error": f"{type(exc).__name__}: {exc}"[:800],
            })

        print(
            f"QOAC_H_V02_CONFIRM_MATERIAL_DONE {mid} "
            f"seconds={time.perf_counter() - t_material:.1f} "
            f"rows={sum(r['material_id'] == mid for r in rows)} "
            f"failures={sum(r['material_id'] == mid for r in failures)}",
            flush=True,
        )

    write_csv(out / f"rows_shard_{args.shard_index:02d}.csv", rows)
    write_csv(out / f"failures_shard_{args.shard_index:02d}.csv", failures)
    write_csv(out / f"planned_shard_{args.shard_index:02d}.csv", planned_rows)

    print(
        f"QOAC_H_V02_CONFIRM_SHARD_DONE shard={args.shard_index} "
        f"materials={len(planned)} rows={len(rows)} failures={len(failures)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
