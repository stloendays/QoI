#!/usr/bin/env python3
"""Compatibility smoke for recovering the development QoI execution path.

This script is an engineering/provenance gate, not a new scientific analysis.
It reuses the byte-frozen external scientific implementation for codec and
Bader semantics, while reconstructing the development-source loader from the
published metadata. Frozen development rows are used only as compatibility
sentinels.
"""
from __future__ import annotations

import argparse
import bz2
import csv
import gzip
import hashlib
import json
import lzma
import sys
import tempfile
import time
import urllib.request
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
from monty.json import MontyDecoder
from pymatgen.io.vasp.outputs import Chgcar

SENTINELS = (
    ("mp-1009084", 1e-7),
    ("nomad--O7C25L6mxPu", 1e-7),
)
CODECS = ("zfp", "sz3", "sperr")
CODEC_LABEL = {"zfp": "ZFP", "sz3": "SZ3", "sperr": "SPERR"}

# Compatibility thresholds are deliberately much tighter than any scientific
# Bader contract in the paper. They are not statistical error tolerances.
PTP_RTOL = 1e-12
PTP_ATOL = 1e-12
LINF_RTOL = 2e-6
LINF_ATOL = 2e-12
BADER_RTOL = 2e-5
BADER_ATOL = 2e-9


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-validation-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def sha256_hex(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def fetch_exact(url: str, expected_sha: str, expected_bytes: int) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "QoI-QSQ-recovery-smoke/1.0"})
    with urllib.request.urlopen(req, timeout=300) as response:
        blob = response.read()
    got_sha = sha256_hex(blob)
    if got_sha != expected_sha:
        raise RuntimeError(f"source SHA256 mismatch: {got_sha} != {expected_sha}")
    if len(blob) != expected_bytes:
        raise RuntimeError(f"source byte-count mismatch: {len(blob)} != {expected_bytes}")
    return blob


def decode_mp_chgcar(blob: bytes) -> Chgcar:
    raw = gzip.decompress(blob) if blob.startswith(b"\x1f\x8b") else blob
    decoded = MontyDecoder().process_decoded(json.loads(raw.decode("utf-8")))

    def walk(obj: Any) -> Chgcar | None:
        if isinstance(obj, Chgcar):
            return obj
        if isinstance(obj, dict):
            # MP's supported client currently returns [0][0]["data"] for chgcars.
            for key in ("data", "chgcar", "charge_density"):
                if key in obj:
                    found = walk(obj[key])
                    if found is not None:
                        return found
            for value in obj.values():
                found = walk(value)
                if found is not None:
                    return found
        elif isinstance(obj, (list, tuple)):
            for value in obj:
                found = walk(value)
                if found is not None:
                    return found
        return None

    chgcar = walk(decoded)
    if chgcar is None:
        raise RuntimeError(f"no pymatgen Chgcar found in decoded MP object: {type(decoded)!r}")
    return chgcar


def decompress_nomad(url: str, blob: bytes) -> bytes:
    lower = url.lower()
    if lower.endswith(".bz2"):
        return bz2.decompress(blob)
    if lower.endswith(".gz"):
        return gzip.decompress(blob)
    if lower.endswith(".xz"):
        return lzma.decompress(blob)
    return blob


def parse_shape(text: str) -> tuple[int, int, int]:
    parts = tuple(int(x) for x in text.lower().split("x"))
    if len(parts) != 3:
        raise RuntimeError(f"invalid ngrid value: {text!r}")
    return parts


def load_metadata(repo_root: Path) -> dict[str, dict[str, str]]:
    with (repo_root / "materials_metadata.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["material_id"]: r for r in rows}


def load_expected(repo_root: Path) -> dict[tuple[str, float, str], dict[str, str]]:
    path = repo_root / "benchmark" / "master_benchmark_tight_ladder.csv"
    out: dict[tuple[str, float, str], dict[str, str]] = {}
    wanted = {m for m, _ in SENTINELS}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["material_id"] not in wanted:
                continue
            key = (row["material_id"], float(row["nominal_tolerance_relative"]), row["codec"])
            out[key] = row
    return out


def build_grid(meta: dict[str, str], blob: bytes, workdir: Path):
    from baderkit import Grid

    source = meta["source"]
    if source == "Materials Project":
        chgcar = decode_mp_chgcar(blob)
        data = {k: np.asarray(v, dtype=np.float64) for k, v in chgcar.data.items()}
        grid = Grid(
            structure=chgcar.structure.copy(),
            data=data,
            data_aug=deepcopy(getattr(chgcar, "data_aug", {})),
            source_format="vasp",
        )
        loader = "mp_gzip_json_monty_to_baderkit_grid"
    elif source.startswith("NOMAD"):
        raw = decompress_nomad(meta["url"], blob)
        chg_path = workdir / "CHGCAR"
        chg_path.write_bytes(raw)
        grid = Grid.from_dynamic(chg_path)
        loader = "nomad_exact_bytes_decompress_to_baderkit_grid"
    else:
        raise RuntimeError(f"unsupported development source: {source!r}")
    return grid, loader


def close(a: float, b: float, rtol: float, atol: float) -> bool:
    return bool(np.isclose(a, b, rtol=rtol, atol=atol, equal_nan=False))


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    frozen_validation = args.frozen_validation_dir.resolve()
    outdir = args.output_dir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(frozen_validation))
    import external_end_to_end as core  # type: ignore

    metadata = load_metadata(repo_root)
    expected = load_expected(repo_root)
    results: list[dict[str, Any]] = []
    material_checks: list[dict[str, Any]] = []
    all_pass = True

    for material_id, rel_tol in SENTINELS:
        if material_id not in metadata:
            raise RuntimeError(f"sentinel absent from metadata: {material_id}")
        meta = metadata[material_id]
        expected_keys = [(material_id, rel_tol, CODEC_LABEL[c]) for c in CODECS]
        missing = [k for k in expected_keys if k not in expected]
        if missing:
            raise RuntimeError(f"sentinel expected rows missing: {missing}")

        blob = fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
        with tempfile.TemporaryDirectory(prefix="qoi_dev_recovery_") as td:
            workdir = Path(td)
            grid, loader = build_grid(meta, blob, workdir)
            field = np.asarray(grid.total, dtype=np.float64)
            shape_expected = parse_shape(meta["ngrid"])
            shape_ok = tuple(int(x) for x in field.shape) == shape_expected
            npoints_ok = int(field.size) == int(meta["npoints"])
            structure_natoms = int(len(grid.structure))
            natoms_meta_ok = structure_natoms == int(meta["natoms"])
            finite_ok = bool(np.all(np.isfinite(field)))
            value_ptp = float(np.ptp(field))
            expected_ptp = float(expected[(material_id, rel_tol, "ZFP")]["value_ptp"])
            ptp_ok = close(value_ptp, expected_ptp, PTP_RTOL, PTP_ATOL)

            t0 = time.time()
            original = core.run_bader(grid)
            original_seconds = time.time() - t0
            q_orig = np.asarray(original["charges"], dtype=np.float64)
            labels_orig = np.asarray(original["atom_labels"])
            bader_natoms_ok = int(q_orig.size) == int(meta["natoms"])
            q_fixed_orig = core.fixed_basin_charges(field, labels_orig, int(q_orig.size))
            self_error = float(np.max(np.abs(q_fixed_orig - q_orig)))
            fixed_self_ok = self_error <= 1e-7

            identity_ok = all((shape_ok, npoints_ok, natoms_meta_ok, finite_ok, ptp_ok, bader_natoms_ok, fixed_self_ok))
            all_pass &= identity_ok
            material_checks.append({
                "material_id": material_id,
                "source": meta["source"],
                "loader": loader,
                "source_sha256": meta["sha256"],
                "source_bytes": int(meta["source_bytes"]),
                "parsed_shape": list(field.shape),
                "expected_shape": list(shape_expected),
                "shape_ok": shape_ok,
                "npoints_ok": npoints_ok,
                "structure_natoms": structure_natoms,
                "metadata_natoms": int(meta["natoms"]),
                "natoms_meta_ok": natoms_meta_ok,
                "bader_natoms": int(q_orig.size),
                "bader_natoms_ok": bader_natoms_ok,
                "value_ptp": value_ptp,
                "expected_value_ptp": expected_ptp,
                "value_ptp_ok": ptp_ok,
                "fixed_basin_self_error_e": self_error,
                "fixed_basin_selfcheck_ok": fixed_self_ok,
                "original_bader_seconds": original_seconds,
                "identity_gate_pass": identity_ok,
            })

            for codec in CODECS:
                label = CODEC_LABEL[codec]
                exp = expected[(material_id, rel_tol, label)]
                abs_bound = rel_tol * value_ptp
                t_codec = time.time()
                reconstructed, compressed_bytes, codec_config = core.codec_roundtrip(codec, field, abs_bound, workdir)
                codec_seconds = time.time() - t_codec
                reconstructed = np.asarray(reconstructed, dtype=np.float64)
                delta = reconstructed - field
                realized_linf = float(np.max(np.abs(delta)))
                bound_ok = bool(realized_linf <= abs_bound * (1 + 1e-6) + 1e-15)

                recon_grid = core.clone_grid_with_total(grid, reconstructed)
                t_bader = time.time()
                resolved = core.run_bader(recon_grid)
                bader_seconds = time.time() - t_bader
                q_resolved = np.asarray(resolved["charges"], dtype=np.float64)
                bader_error = float(np.max(np.abs(q_resolved - q_orig)))

                exp_linf = float(exp["realized_Linf"])
                exp_bader = float(exp["Bader_error_resolved_e"])
                exp_bytes = int(exp["compressed_bytes"])
                linf_ok = close(realized_linf, exp_linf, LINF_RTOL, LINF_ATOL)
                bader_ok = close(bader_error, exp_bader, BADER_RTOL, BADER_ATOL)
                bytes_exact = int(compressed_bytes) == exp_bytes
                config_ok = str(codec_config).lower().replace("default ", "").replace("; ", " ") in str(exp["codec_config"]).lower().replace("; ", " ") or label == "SPERR"
                scientific_match = bool(identity_ok and bound_ok and linf_ok and bader_ok)
                all_pass &= scientific_match

                results.append({
                    "material_id": material_id,
                    "codec": label,
                    "relative_tolerance": rel_tol,
                    "codec_config_recovered": codec_config,
                    "codec_config_frozen_row": exp["codec_config"],
                    "codec_config_text_compatible": config_ok,
                    "realized_Linf_recovered": realized_linf,
                    "realized_Linf_frozen": exp_linf,
                    "realized_Linf_abs_diff": abs(realized_linf - exp_linf),
                    "realized_Linf_match": linf_ok,
                    "Bader_error_resolved_recovered_e": bader_error,
                    "Bader_error_resolved_frozen_e": exp_bader,
                    "Bader_error_abs_diff_e": abs(bader_error - exp_bader),
                    "Bader_error_match": bader_ok,
                    "compressed_bytes_recovered": int(compressed_bytes),
                    "compressed_bytes_frozen": exp_bytes,
                    "compressed_bytes_exact": bytes_exact,
                    "bound_respected_recovered": bound_ok,
                    "codec_seconds": codec_seconds,
                    "resolved_bader_seconds": bader_seconds,
                    "scientific_compatibility_pass": scientific_match,
                })

    payload = {
        "status": "PASS" if all_pass else "FAIL",
        "purpose": "development-loader/scientific-stack compatibility smoke; not a new scientific endpoint",
        "frozen_validation_dir": str(frozen_validation),
        "compatibility_thresholds": {
            "value_ptp": {"rtol": PTP_RTOL, "atol": PTP_ATOL},
            "realized_Linf": {"rtol": LINF_RTOL, "atol": LINF_ATOL},
            "Bader_error_resolved_e": {"rtol": BADER_RTOL, "atol": BADER_ATOL},
            "fixed_basin_selfcheck_e": 1e-7,
            "compressed_bytes": "reported as exact/non-exact diagnostic, not a scientific gate",
        },
        "materials": material_checks,
        "rows": results,
    }
    (outdir / "compatibility_smoke.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    csv_fields = list(results[0].keys())
    with (outdir / "compatibility_rows.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(results)

    lines = [
        "# Development execution compatibility smoke",
        "",
        f"Status: **{payload['status']}**",
        "",
        "This is a provenance/engineering gate. It does not create or tune a scientific result.",
        "",
        "| Material | Codec | Linf match | Bader match | Bytes exact | Scientific gate |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in results:
        lines.append(
            f"| {row['material_id']} | {row['codec']} | {row['realized_Linf_match']} | "
            f"{row['Bader_error_match']} | {row['compressed_bytes_exact']} | {row['scientific_compatibility_pass']} |"
        )
    lines.extend([
        "",
        "Compressed-byte equality is retained as a deterministic-codec diagnostic but is not required for the scientific compatibility gate. Source identity, grid/atom invariants, realized Linf, the Bader fixed-domain self-check, and re-derived Bader response are required.",
    ])
    (outdir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if all_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
