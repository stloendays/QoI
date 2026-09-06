#!/usr/bin/env python3
"""Frozen-manifest external end-to-end rate-fidelity validation.

This runner deliberately consumes only the already-frozen external manifest and
Protocol A.1 stability floors. It does not tune any parameter.

Pipeline:
  source bytes -> SHA256 audit -> parse raw charge field -> codec round trip
  -> realized L_inf audit -> Bader re-solve -> Protocol A.1 qualification
  -> certification at pre-existing tau values.
"""
from __future__ import annotations

import argparse
import ast
import csv
import gzip
import hashlib
import importlib.metadata as md
import json
import lzma
import re
import sys
import tempfile
import time
import urllib.request
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "external_test_MANIFEST.json"
FLOORS = ROOT / "stability" / "stability_floor_A1.csv"
TAUS = (1e-4, 1e-3, 1e-2)
USER_AGENT = "QoI-external-e2e/0.1 (research validation)"


def fetch_bytes(url: str, timeout: int = 180) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def sha256_hex(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def decompress_source(url: str, blob: bytes) -> bytes:
    if url.endswith(".xz"):
        return lzma.decompress(blob)
    if url.endswith(".gz"):
        return gzip.decompress(blob)
    return blob


def aflow_entry_url(file_url: str) -> str:
    return file_url.rsplit("/", 1)[0] + "/"


def parse_aflow_species_and_counts(entry_html: str) -> tuple[list[str], list[int]]:
    species_match = re.search(r"species\s*=\s*(\[[^\n<]+?\])", entry_html)
    composition_match = re.search(r"composition\s*=\s*(\[[^\n<]+?\])", entry_html)
    if not species_match or not composition_match:
        raise RuntimeError("AFLOW metadata did not expose species/composition")
    species = list(ast.literal_eval(species_match.group(1)))
    composition_raw = list(ast.literal_eval(composition_match.group(1)))
    composition = [int(round(float(x))) for x in composition_raw]
    if len(species) != len(composition):
        raise RuntimeError("AFLOW species/composition lengths differ")
    return species, composition


def patch_pre_vasp5_species(raw_text: str, source_url: str) -> tuple[str, str]:
    """Insert the AFLOW-reported species line into a pre-VASP5 CHGCAR.

    The source atom-count line is never guessed. The AFLOW entry metadata must
    reproduce it exactly, otherwise the case is rejected.
    """
    lines = raw_text.splitlines()
    if len(lines) < 8:
        raise RuntimeError("CHGCAR is unexpectedly short")

    count_tokens = lines[5].split()
    try:
        source_counts = [int(x) for x in count_tokens]
        is_pre_vasp5 = True
    except ValueError:
        is_pre_vasp5 = False

    if not is_pre_vasp5:
        return raw_text, "vasp5_species_present"

    meta_blob = fetch_bytes(aflow_entry_url(source_url))
    meta_text = meta_blob.decode("utf-8", errors="replace")
    species, api_counts = parse_aflow_species_and_counts(meta_text)
    if source_counts != api_counts:
        raise RuntimeError(
            f"AFLOW composition mismatch: file counts {source_counts} != API {api_counts}"
        )
    lines.insert(5, " ".join(species))
    return "\n".join(lines) + "\n", "aflow_species_injected_and_count_verified"


def materialize_chgcar(record: dict[str, Any], workdir: Path) -> tuple[Path, dict[str, Any]]:
    t0 = time.time()
    blob = fetch_bytes(record["url"])
    got_sha = sha256_hex(blob)
    if got_sha != record["sha256"]:
        raise RuntimeError(f"SHA256 mismatch: {got_sha} != {record['sha256']}")
    if len(blob) != int(record["source_bytes"]):
        raise RuntimeError(
            f"byte-count mismatch: {len(blob)} != {record['source_bytes']}"
        )

    raw = decompress_source(record["url"], blob)
    parser_provenance = "source_species_line"
    if record["source"].startswith("AFLOW"):
        text = raw.decode("utf-8", errors="strict")
        text, parser_provenance = patch_pre_vasp5_species(text, record["url"])
        raw = text.encode("utf-8")

    path = workdir / "CHGCAR"
    path.write_bytes(raw)
    return path, {
        "source_sha256_verified": True,
        "source_bytes_verified": True,
        "parser_provenance": parser_provenance,
        "download_seconds": time.time() - t0,
    }


def load_floors() -> dict[str, float]:
    floors: dict[str, float] = {}
    with FLOORS.open(newline="") as f:
        for row in csv.DictReader(f):
            floors[row["material_id"]] = float(row["stability_floor_A1_e"])
    return floors


def load_manifest() -> list[dict[str, Any]]:
    payload = json.loads(MANIFEST.read_text())
    if payload.get("frozen") is not True:
        raise RuntimeError("External manifest is not marked frozen")
    if len(payload["records"]) != int(payload["n_records"]):
        raise RuntimeError("External manifest record count mismatch")
    return payload["records"]


def package_versions() -> dict[str, str]:
    names = ["numpy", "baderkit", "pysz", "zfpy", "hdf5plugin", "h5py"]
    result: dict[str, str] = {}
    for name in names:
        try:
            result[name] = md.version(name)
        except md.PackageNotFoundError:
            result[name] = "NOT_INSTALLED"
    return result


def codec_roundtrip(codec: str, array: np.ndarray, abs_bound: float, workdir: Path):
    if codec == "zfp":
        import zfpy

        compressed = zfpy.compress_numpy(array, tolerance=abs_bound)
        reconstructed = zfpy.decompress_numpy(compressed)
        return np.asarray(reconstructed, dtype=array.dtype), len(compressed), "fixed-accuracy"

    if codec == "sz3":
        from pysz import sz, szConfig, szErrorBoundMode

        config = szConfig()
        config.errorBoundMode = szErrorBoundMode.ABS
        config.absErrorBound = float(abs_bound)
        compressed, _ratio = sz.compress(array, config)
        reconstructed, _config = sz.decompress(compressed, array.dtype.type, array.shape)
        return (
            np.asarray(reconstructed, dtype=array.dtype),
            int(np.asarray(compressed).nbytes),
            "ABS; default INTERP_LORENZO",
        )

    if codec == "sperr":
        import h5py
        import hdf5plugin

        h5path = workdir / "sperr.h5"
        with h5py.File(h5path, "w") as h5:
            ds = h5.create_dataset(
                "density",
                data=array,
                chunks=array.shape,
                **hdf5plugin.Sperr(absolute=float(abs_bound)),
            )
            h5.flush()
            compressed_bytes = int(ds.id.get_storage_size())
        with h5py.File(h5path, "r") as h5:
            reconstructed = h5["density"][()]
        h5path.unlink(missing_ok=True)
        return np.asarray(reconstructed, dtype=array.dtype), compressed_bytes, "absolute; single chunk"

    raise ValueError(f"Unknown codec: {codec}")


def clone_grid_with_total(grid, reconstructed: np.ndarray):
    from baderkit import Grid

    data: dict[str, np.ndarray] = {"total": np.asarray(reconstructed, dtype=np.float64)}
    return Grid(
        structure=grid.structure.copy(),
        data=data,
        data_aug=deepcopy(getattr(grid, "data_aug", {})),
        source_format=grid.source_format,
        data_type=grid.data_type,
        sig_figs=getattr(grid, "sig_figs", None),
        spin_system="not polarized",
    )


def bader_charges(grid) -> np.ndarray:
    from baderkit import Bader

    analysis = Bader(
        charge_grid=grid,
        total_charge_grid=grid,
        reference_grid=grid,
        method="ongrid",
    )
    return np.asarray(analysis.atom_charges, dtype=np.float64)


def audit_grid(record: dict[str, Any], grid) -> None:
    shape = [int(x) for x in grid.total.shape]
    expected = [int(x) for x in record["ngrid"]]
    if shape != expected:
        raise RuntimeError(f"grid shape mismatch: parsed {shape} != manifest {expected}")


def verdict_fields(floor: float, qoi_error: float) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for tau in TAUS:
        tag = f"{tau:.0e}".replace("e-0", "e-")
        eligible = bool(floor < tau)
        certified = bool(eligible and qoi_error < tau)
        if not eligible:
            verdict = "NON_EVALUABLE_BADER_UNSTABLE"
        elif certified:
            verdict = "CERTIFIED"
        else:
            verdict = "NOT_CERTIFIED"
        out[f"eligible_A1_at_{tag}"] = eligible
        out[f"certified_at_{tag}"] = certified
        out[f"verdict_at_{tag}"] = verdict
    return out


def run_record(
    record: dict[str, Any],
    floor: float,
    codecs: list[str],
    relative_tolerances: list[float],
    output_rows: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    from baderkit import Grid

    with tempfile.TemporaryDirectory(prefix="qoi_e2e_") as td:
        workdir = Path(td)
        chgcar, provenance = materialize_chgcar(record, workdir)
        grid = Grid.from_dynamic(chgcar)
        audit_grid(record, grid)
        field = np.asarray(grid.total, dtype=np.float64)
        if not np.all(np.isfinite(field)):
            raise RuntimeError("non-finite values in source field")
        value_ptp = float(np.ptp(field))
        if not value_ptp > 0:
            raise RuntimeError("source field has zero peak-to-peak range")

        t_bader0 = time.time()
        q_orig = bader_charges(grid)
        original_bader_seconds = time.time() - t_bader0

        material_meta = {
            "material_id": record["material_id"],
            "domain": record["domain"],
            "formula": record.get("formula", ""),
            "npoints": int(field.size),
            "natoms_bader": int(q_orig.size),
            "value_ptp": value_ptp,
            "raw_bytes": int(field.nbytes),
            "stability_floor_A1_e": floor,
            "original_bader_seconds": original_bader_seconds,
            **provenance,
        }

        for codec in codecs:
            for rel_tol in relative_tolerances:
                abs_bound = float(rel_tol * value_ptp)
                t_codec = time.time()
                reconstructed, compressed_bytes, codec_config = codec_roundtrip(
                    codec, field, abs_bound, workdir
                )
                codec_seconds = time.time() - t_codec
                if reconstructed.shape != field.shape:
                    raise RuntimeError(
                        f"{codec} shape mismatch {reconstructed.shape} != {field.shape}"
                    )
                delta = reconstructed - field
                realized_linf = float(np.max(np.abs(delta)))
                rmse = float(np.sqrt(np.mean(delta * delta)))
                mean_signed_error = float(np.mean(delta))
                bound_respected = bool(realized_linf <= abs_bound * (1.0 + 1e-6) + 1e-15)

                recon_grid = clone_grid_with_total(grid, reconstructed)
                t_bader = time.time()
                q_recon = bader_charges(recon_grid)
                bader_seconds = time.time() - t_bader
                if q_recon.shape != q_orig.shape:
                    raise RuntimeError(
                        f"Bader charge shape changed: {q_recon.shape} != {q_orig.shape}"
                    )
                qoi_error = float(np.max(np.abs(q_recon - q_orig)))

                row: dict[str, Any] = {
                    **material_meta,
                    "codec": codec.upper() if codec != "sperr" else "SPERR",
                    "codec_config": codec_config,
                    "nominal_tolerance_relative": rel_tol,
                    "nominal_tolerance_absolute": abs_bound,
                    "realized_Linf": realized_linf,
                    "realized_Linf_over_nominal": realized_linf / abs_bound,
                    "bound_respected": bound_respected,
                    "rmse": rmse,
                    "mean_signed_error": mean_signed_error,
                    "compressed_bytes": int(compressed_bytes),
                    "compression_ratio": float(field.nbytes / compressed_bytes),
                    "bits_per_value": float(8.0 * compressed_bytes / field.size),
                    "Bader_error_resolved_e": qoi_error,
                    "encode_decode_seconds": codec_seconds,
                    "bader_seconds": bader_seconds,
                }
                row.update(verdict_fields(floor, qoi_error))
                output_rows.append(row)
                print(
                    json.dumps(
                        {
                            "material": record["material_id"],
                            "codec": codec,
                            "rel_tol": rel_tol,
                            "linf": realized_linf,
                            "bound": abs_bound,
                            "qoi_error_e": qoi_error,
                            "compression_ratio": row["compression_ratio"],
                            "certified_1e-4": row["certified_at_1e-4"],
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )

        (output_dir / f"{record['material_id']}_original_bader.json").write_text(
            json.dumps({"atom_charges": q_orig.tolist()}, indent=2)
        )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--material-id", action="append", default=[])
    p.add_argument("--limit", type=int, default=0)
    p.add_argument(
        "--codecs",
        default="zfp,sz3,sperr",
        help="Comma-separated subset of zfp,sz3,sperr",
    )
    p.add_argument(
        "--relative-tolerances",
        default="1e-5",
        help="Comma-separated relative error-bound ladder",
    )
    p.add_argument("--output-dir", default="validation/results")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    codecs = [x.strip().lower() for x in args.codecs.split(",") if x.strip()]
    relative_tolerances = [
        float(x) for x in args.relative_tolerances.split(",") if x.strip()
    ]
    invalid = sorted(set(codecs) - {"zfp", "sz3", "sperr"})
    if invalid:
        raise SystemExit(f"Invalid codecs: {invalid}")

    records = load_manifest()
    floors = load_floors()
    if args.material_id:
        wanted = set(args.material_id)
        records = [r for r in records if r["material_id"] in wanted]
        missing = wanted - {r["material_id"] for r in records}
        if missing:
            raise SystemExit(f"Material IDs absent from frozen manifest: {sorted(missing)}")
    if args.limit:
        records = records[: args.limit]
    if not records:
        raise SystemExit("No records selected")

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    metadata = {
        "manifest_sha256": sha256_hex(MANIFEST.read_bytes()),
        "stability_floor_sha256": sha256_hex(FLOORS.read_bytes()),
        "selected_materials": [r["material_id"] for r in records],
        "codecs": codecs,
        "relative_tolerances": relative_tolerances,
        "thresholds_e": list(TAUS),
        "packages": package_versions(),
        "python": sys.version,
        "platform": sys.platform,
    }
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2))

    for record in records:
        mid = record["material_id"]
        try:
            if mid not in floors:
                raise RuntimeError("missing Protocol A.1 stability floor")
            run_record(record, floors[mid], codecs, relative_tolerances, rows, output_dir)
        except Exception as exc:
            failures.append(
                {"material_id": mid, "error_type": type(exc).__name__, "error": str(exc)}
            )
            print(
                json.dumps(
                    {"material": mid, "status": "PIPELINE_FAILURE", "error": repr(exc)}
                ),
                file=sys.stderr,
                flush=True,
            )

    result_csv = output_dir / "external_e2e_rows.csv"
    if rows:
        with result_csv.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        result_csv.write_text("")

    with (output_dir / "external_e2e_failures.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["material_id", "error_type", "error"])
        writer.writeheader()
        writer.writerows(failures)

    summary = {
        "n_materials_selected": len(records),
        "n_rows_completed": len(rows),
        "n_failures": len(failures),
        "all_codec_bounds_respected": bool(rows) and all(r["bound_respected"] for r in rows),
        "n_certified_at_1e-4": sum(bool(r["certified_at_1e-4"]) for r in rows),
        "n_certified_at_1e-3": sum(bool(r["certified_at_1e-3"]) for r in rows),
        "n_certified_at_1e-2": sum(bool(r["certified_at_1e-2"]) for r in rows),
        "failure_materials": [f["material_id"] for f in failures],
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"summary": summary}, sort_keys=True), flush=True)

    # Pipeline failures are validation failures, never silently excluded.
    return 0 if not failures and rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
