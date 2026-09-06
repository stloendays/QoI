#!/usr/bin/env python3
"""Frozen-manifest external end-to-end rate-fidelity validation.

This runner consumes only already-frozen project artifacts:
  - external_test_MANIFEST.json
  - stability/stability_floor_A1.csv
  - protocol/PROTOCOL_A1.md
  - benchmark/master_benchmark_full.csv

No parameter is tuned on the external corpus. By default, codec tolerance ladders
are read directly from the frozen master benchmark so the external run uses the
same requested error bounds as the development benchmark.

Pipeline:
  source bytes -> SHA256/byte-count provenance gate -> parse raw charge field
  -> codec round trip -> realized L_inf audit -> fixed-basin Bader integration
  -> resolved-basin Bader re-solve -> Protocol A.1 eligibility
  -> certification at pre-existing tau values.

Any material-level failure is retained as PIPELINE_FAILURE and causes a nonzero
exit code. Failures are never silently dropped from the denominator.
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
import os
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
PROTOCOL_A1 = ROOT / "protocol" / "PROTOCOL_A1.md"
MASTER_BENCHMARK = ROOT / "benchmark" / "master_benchmark_full.csv"

TAUS = (1e-4, 1e-3, 1e-2)
USER_AGENT = "QoI-external-e2e/0.2 (research validation)"

# Explicitly pinned analysis semantics. These are written to every run metadata
# file rather than relying on BaderKit defaults.
BADER_METHOD = "ongrid"
BADER_VACUUM_TOL = 1.0e-3
BADER_PERSISTENCE_TOL = 0.5
BADER_NNA_CUTOFF = False

CODEC_NAMES = {"zfp": "ZFP", "sz3": "SZ3", "sperr": "SPERR"}


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
    return file_url.rsplit("/", 1)[0].rstrip("/") + "/"


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).replace("&quot;", '"').strip()


def _parse_aflow_property_response(text: str, key: str) -> Any:
    """Parse AFLOW REST-property responses without guessing missing values."""
    cleaned = _strip_html(text).strip()
    if not cleaned:
        raise RuntimeError(f"AFLOW REST property {key!r} returned an empty response")

    # Some endpoints return JSON; others return key=value or a bare value.
    try:
        payload = json.loads(cleaned)
        if isinstance(payload, dict) and key in payload:
            return payload[key]
        if not isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    match = re.search(rf"(?:^|[!\n\r\s]){re.escape(key)}\s*=\s*([^!\n\r<]+)", cleaned)
    if match:
        return match.group(1).strip()

    # AFLOW REST queries such as /?species may return only the requested value.
    if "=" not in cleaned and len(cleaned) < 4096:
        return cleaned

    raise RuntimeError(f"AFLOW REST property {key!r} could not be parsed")


def _as_species(value: Any) -> list[str]:
    if isinstance(value, list):
        species = [str(x).strip() for x in value]
    else:
        raw = str(value).strip()
        try:
            parsed = ast.literal_eval(raw)
            if isinstance(parsed, (list, tuple)):
                species = [str(x).strip() for x in parsed]
            else:
                species = [str(parsed).strip()]
        except (ValueError, SyntaxError):
            species = [x.strip().strip("'\"") for x in raw.strip("[]").split(",")]
    species = [x for x in species if x]
    if not species:
        raise RuntimeError("AFLOW species response parsed to an empty list")
    return species


def _as_integer_composition(value: Any) -> list[int]:
    if isinstance(value, list):
        values = value
    else:
        raw = str(value).strip()
        try:
            parsed = ast.literal_eval(raw)
            values = list(parsed) if isinstance(parsed, (list, tuple)) else [parsed]
        except (ValueError, SyntaxError):
            values = [x.strip() for x in raw.strip("[]").split(",") if x.strip()]

    floats = [float(x) for x in values]
    integers = [int(round(x)) for x in floats]
    if any(abs(x - y) > 1e-8 for x, y in zip(floats, integers)):
        raise RuntimeError(
            f"AFLOW composition is not an integer simulation-cell count: {floats}"
        )
    return integers


def fetch_aflow_species_and_counts(entry_url: str) -> tuple[list[str], list[int]]:
    """Read species/composition from AFLOW entry REST properties.

    AFLOW documents each entry URL as a REST endpoint where individual properties
    can be queried with /?property. We query the properties separately and verify
    them against the atom-count line already present in the CHGCAR.
    """
    responses: dict[str, Any] = {}
    for key in ("species", "composition"):
        blob = fetch_bytes(entry_url.rstrip("/") + f"/?{key}")
        text = blob.decode("utf-8", errors="replace")
        responses[key] = _parse_aflow_property_response(text, key)

    species = _as_species(responses["species"])
    composition = _as_integer_composition(responses["composition"])
    if len(species) != len(composition):
        raise RuntimeError(
            f"AFLOW species/composition lengths differ: {species} vs {composition}"
        )
    return species, composition


def patch_pre_vasp5_species(raw_text: str, source_url: str) -> tuple[str, str]:
    """Insert AFLOW-reported species into a pre-VASP5 CHGCAR.

    Nothing is inferred from the material_id or formula. The source atom-count line
    must agree exactly with AFLOW REST composition before species are injected.
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

    species, api_counts = fetch_aflow_species_and_counts(aflow_entry_url(source_url))
    if source_counts != api_counts:
        raise RuntimeError(
            f"AFLOW composition mismatch: CHGCAR counts {source_counts} != REST {api_counts}"
        )
    lines.insert(5, " ".join(species))
    return "\n".join(lines) + "\n", "aflow_rest_species_injected_count_verified"


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


def load_frozen_tolerance_ladders(codecs: list[str]) -> dict[str, list[float]]:
    """Extract codec-specific tolerance ladders from the frozen master table."""
    available: dict[str, set[float]] = {codec: set() for codec in codecs}
    with MASTER_BENCHMARK.open(newline="") as f:
        reader = csv.DictReader(f)
        required = {"codec", "nominal_tolerance_relative"}
        if not required.issubset(reader.fieldnames or []):
            raise RuntimeError(
                f"Master benchmark lacks required columns {sorted(required)}"
            )
        for row in reader:
            codec_name = row["codec"].strip().lower()
            if codec_name in available and row["nominal_tolerance_relative"].strip():
                available[codec_name].add(float(row["nominal_tolerance_relative"]))

    ladders: dict[str, list[float]] = {}
    for codec, values in available.items():
        if not values:
            raise RuntimeError(f"No frozen tolerance values found for codec {codec}")
        ladders[codec] = sorted(values, reverse=True)
    return ladders


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


def run_bader(grid) -> dict[str, Any]:
    from baderkit import Bader

    analysis = Bader(
        charge_grid=grid,
        total_charge_grid=grid,
        reference_grid=grid,
        method=BADER_METHOD,
        vacuum_tol=BADER_VACUUM_TOL,
        persistence_tol=BADER_PERSISTENCE_TOL,
        nna_cutoff=BADER_NNA_CUTOFF,
    )
    charges = np.asarray(analysis.atom_charges, dtype=np.float64)
    labels = np.asarray(analysis.atom_labels)
    return {
        "charges": charges,
        "atom_labels": labels,
        "n_maxima": int(len(analysis.maxima_frac)),
        "num_vacuum_voxels": int(analysis.num_vacuum),
        "vacuum_charge_e": float(analysis.vacuum_charge),
    }


def fixed_basin_charges(
    field: np.ndarray, original_atom_labels: np.ndarray, n_atoms: int
) -> np.ndarray:
    """Integrate a field on the original atom labels using BaderKit on-grid semantics.

    BaderKit's on-grid integration sums voxel values by label and divides by the
    total number of grid points. atom_labels uses n_atoms as the vacuum label.
    """
    labels = np.asarray(original_atom_labels).ravel().astype(np.int64, copy=False)
    weights = np.asarray(field, dtype=np.float64).ravel()
    if labels.size != weights.size:
        raise RuntimeError("Fixed-basin label/data sizes differ")
    if labels.min() < 0 or labels.max() > n_atoms:
        raise RuntimeError(
            f"Unexpected atom label range {labels.min()}..{labels.max()} for {n_atoms} atoms"
        )
    sums = np.bincount(labels, weights=weights, minlength=n_atoms + 1)
    return np.asarray(sums[:n_atoms] / weights.size, dtype=np.float64)


def error_metrics(delta: np.ndarray, prefix: str) -> dict[str, float]:
    absolute = np.abs(np.asarray(delta, dtype=np.float64))
    return {
        f"{prefix}_max_e": float(np.max(absolute)),
        f"{prefix}_mean_e": float(np.mean(absolute)),
        f"{prefix}_median_e": float(np.median(absolute)),
        f"{prefix}_p95_e": float(np.quantile(absolute, 0.95)),
    }


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
    tolerance_ladders: dict[str, list[float]],
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
        original = run_bader(grid)
        original_bader_cold_seconds = time.time() - t_bader0
        q_orig = original["charges"]
        labels_orig = original["atom_labels"]
        n_atoms = int(q_orig.size)

        # Internal consistency check: direct integration on BaderKit's atom labels
        # must reproduce BaderKit's own original atom charges.
        q_fixed_orig = fixed_basin_charges(field, labels_orig, n_atoms)
        fixed_self_error = float(np.max(np.abs(q_fixed_orig - q_orig)))
        if fixed_self_error > 1e-7:
            raise RuntimeError(
                f"Fixed-basin self-check failed: max difference {fixed_self_error:.3e} e"
            )

        material_meta = {
            "material_id": record["material_id"],
            "domain": record["domain"],
            "formula": record.get("formula", ""),
            "npoints": int(field.size),
            "natoms_bader": n_atoms,
            "value_ptp": value_ptp,
            "raw_bytes": int(field.nbytes),
            "source_density_min": float(np.min(field)),
            "source_density_max": float(np.max(field)),
            "source_has_negative_density": bool(np.min(field) < 0),
            "stability_floor_A1_e": floor,
            "bader_method": BADER_METHOD,
            "bader_vacuum_tol": BADER_VACUUM_TOL,
            "bader_persistence_tol": BADER_PERSISTENCE_TOL,
            "bader_nna_cutoff": BADER_NNA_CUTOFF,
            "original_n_maxima": original["n_maxima"],
            "original_num_vacuum_voxels": original["num_vacuum_voxels"],
            "original_vacuum_charge_e": original["vacuum_charge_e"],
            "fixed_basin_selfcheck_max_e": fixed_self_error,
            "original_bader_cold_seconds": original_bader_cold_seconds,
            "timing_note": "original includes cold/JIT overhead; do not compare as codec speed",
            **provenance,
        }

        for codec in codecs:
            for rel_tol in tolerance_ladders[codec]:
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
                if not np.all(np.isfinite(reconstructed)):
                    raise RuntimeError(f"{codec} produced non-finite reconstructed values")

                delta = reconstructed - field
                realized_linf = float(np.max(np.abs(delta)))
                rmse = float(np.sqrt(np.mean(delta * delta)))
                mean_signed_error = float(np.mean(delta))
                bound_respected = bool(
                    realized_linf <= abs_bound * (1.0 + 1e-6) + 1e-15
                )

                # Fixed-basin QoI: integrate reconstructed density on original
                # atom labels without changing the partition.
                q_fixed = fixed_basin_charges(reconstructed, labels_orig, n_atoms)
                fixed_metrics = error_metrics(q_fixed - q_orig, "Bader_error_fixed")

                # Resolved-basin QoI: recompute the Bader partition from scratch.
                recon_grid = clone_grid_with_total(grid, reconstructed)
                t_bader = time.time()
                resolved = run_bader(recon_grid)
                bader_seconds = time.time() - t_bader
                q_resolved = resolved["charges"]
                if q_resolved.shape != q_orig.shape:
                    raise RuntimeError(
                        f"Bader charge shape changed: {q_resolved.shape} != {q_orig.shape}"
                    )
                resolved_metrics = error_metrics(
                    q_resolved - q_orig, "Bader_error_resolved"
                )

                labels_resolved = resolved["atom_labels"]
                if labels_resolved.shape != labels_orig.shape:
                    raise RuntimeError("Resolved atom-label grid shape changed")
                atom_domain_migration_fraction = float(
                    np.mean(labels_resolved != labels_orig)
                )
                vacuum_label = n_atoms
                vacuum_mask_orig = labels_orig == vacuum_label
                vacuum_mask_resolved = labels_resolved == vacuum_label
                vacuum_mask_change_fraction = float(
                    np.mean(vacuum_mask_orig != vacuum_mask_resolved)
                )

                row: dict[str, Any] = {
                    **material_meta,
                    "codec": CODEC_NAMES[codec],
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
                    **fixed_metrics,
                    **resolved_metrics,
                    # Compatibility aliases matching the existing master table.
                    "Bader_error_fixed_e": fixed_metrics["Bader_error_fixed_max_e"],
                    "Bader_error_resolved_e": resolved_metrics[
                        "Bader_error_resolved_max_e"
                    ],
                    "resolved_n_maxima": resolved["n_maxima"],
                    "bader_maxima_count_changed": bool(
                        resolved["n_maxima"] != original["n_maxima"]
                    ),
                    "atom_domain_migration_fraction": atom_domain_migration_fraction,
                    "vacuum_mask_change_fraction": vacuum_mask_change_fraction,
                    "resolved_num_vacuum_voxels": resolved["num_vacuum_voxels"],
                    "resolved_vacuum_charge_e": resolved["vacuum_charge_e"],
                    "encode_decode_seconds": codec_seconds,
                    "resolved_bader_seconds": bader_seconds,
                }
                row.update(
                    verdict_fields(
                        floor, resolved_metrics["Bader_error_resolved_max_e"]
                    )
                )
                output_rows.append(row)
                print(
                    json.dumps(
                        {
                            "material": record["material_id"],
                            "codec": codec,
                            "rel_tol": rel_tol,
                            "linf_over_nominal": row["realized_Linf_over_nominal"],
                            "fixed_error_e": row["Bader_error_fixed_e"],
                            "resolved_error_e": row["Bader_error_resolved_e"],
                            "migration_fraction": atom_domain_migration_fraction,
                            "maxima_changed": row["bader_maxima_count_changed"],
                            "compression_ratio": row["compression_ratio"],
                            "certified_1e-4": row["certified_at_1e-4"],
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )

        (output_dir / f"{record['material_id']}_original_bader.json").write_text(
            json.dumps(
                {
                    "atom_charges": q_orig.tolist(),
                    "n_maxima": original["n_maxima"],
                    "num_vacuum_voxels": original["num_vacuum_voxels"],
                    "vacuum_charge_e": original["vacuum_charge_e"],
                },
                indent=2,
            )
        )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--material-id", action="append", default=[])
    p.add_argument("--domain", choices=["bulk", "vacuum2d"], default=None)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--shard-count", type=int, default=1)
    p.add_argument("--shard-index", type=int, default=0)
    p.add_argument(
        "--codecs",
        default="zfp,sz3,sperr",
        help="Comma-separated subset of zfp,sz3,sperr",
    )
    p.add_argument(
        "--relative-tolerances",
        default="frozen",
        help=(
            "'frozen' (default) reads codec-specific ladders from "
            "benchmark/master_benchmark_full.csv; otherwise provide a comma-separated "
            "custom ladder for smoke/debug only"
        ),
    )
    p.add_argument("--output-dir", default="validation/results")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    codecs = [x.strip().lower() for x in args.codecs.split(",") if x.strip()]
    invalid = sorted(set(codecs) - set(CODEC_NAMES))
    if invalid:
        raise SystemExit(f"Invalid codecs: {invalid}")

    if args.relative_tolerances.strip().lower() == "frozen":
        tolerance_mode = "frozen_master_benchmark"
        tolerance_ladders = load_frozen_tolerance_ladders(codecs)
    else:
        tolerance_mode = "custom_debug_only"
        custom = [
            float(x) for x in args.relative_tolerances.split(",") if x.strip()
        ]
        if not custom:
            raise SystemExit("Custom relative-tolerance list is empty")
        tolerance_ladders = {codec: custom for codec in codecs}

    records = load_manifest()
    floors = load_floors()
    if args.material_id:
        wanted = set(args.material_id)
        records = [r for r in records if r["material_id"] in wanted]
        missing = wanted - {r["material_id"] for r in records}
        if missing:
            raise SystemExit(f"Material IDs absent from frozen manifest: {sorted(missing)}")
    if args.domain:
        records = [r for r in records if r["domain"] == args.domain]
    if args.limit:
        records = records[: args.limit]

    if args.shard_count < 1:
        raise SystemExit("--shard-count must be >= 1")
    if not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("--shard-index must satisfy 0 <= index < count")
    records = [
        record
        for index, record in enumerate(records)
        if index % args.shard_count == args.shard_index
    ]
    if not records:
        raise SystemExit("No records selected")

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    metadata = {
        "protocol": "Protocol A.1 + frozen external E2E rate-fidelity",
        "manifest_sha256": sha256_hex(MANIFEST.read_bytes()),
        "stability_floor_sha256": sha256_hex(FLOORS.read_bytes()),
        "protocol_A1_sha256": sha256_hex(PROTOCOL_A1.read_bytes()),
        "master_benchmark_sha256": sha256_hex(MASTER_BENCHMARK.read_bytes()),
        "selected_materials": [r["material_id"] for r in records],
        "codecs": codecs,
        "tolerance_mode": tolerance_mode,
        "tolerance_ladders": tolerance_ladders,
        "thresholds_e": list(TAUS),
        "bader": {
            "method": BADER_METHOD,
            "vacuum_tol": BADER_VACUUM_TOL,
            "persistence_tol": BADER_PERSISTENCE_TOL,
            "nna_cutoff": BADER_NNA_CUTOFF,
            "basins_recomputed_for_resolved_metric": True,
            "fixed_metric_uses_original_atom_labels": True,
        },
        "shard_count": args.shard_count,
        "shard_index": args.shard_index,
        "packages": package_versions(),
        "python": sys.version,
        "platform": sys.platform,
        "github": {
            "actions": os.getenv("GITHUB_ACTIONS"),
            "sha": os.getenv("GITHUB_SHA"),
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "job": os.getenv("GITHUB_JOB"),
            "ref_name": os.getenv("GITHUB_REF_NAME"),
        },
    }
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2))

    for record in records:
        mid = record["material_id"]
        try:
            if mid not in floors:
                raise RuntimeError("missing Protocol A.1 stability floor")
            run_record(
                record,
                floors[mid],
                codecs,
                tolerance_ladders,
                rows,
                output_dir,
            )
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
        "all_codec_bounds_respected": bool(rows)
        and all(r["bound_respected"] for r in rows),
        "n_certified_at_1e-4": sum(bool(r["certified_at_1e-4"]) for r in rows),
        "n_certified_at_1e-3": sum(bool(r["certified_at_1e-3"]) for r in rows),
        "n_certified_at_1e-2": sum(bool(r["certified_at_1e-2"]) for r in rows),
        "n_maxima_count_changes": sum(
            bool(r["bader_maxima_count_changed"]) for r in rows
        ),
        "mean_atom_domain_migration_fraction": (
            float(np.mean([r["atom_domain_migration_fraction"] for r in rows]))
            if rows
            else None
        ),
        "failure_materials": [f["material_id"] for f in failures],
        "tolerance_mode": tolerance_mode,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"summary": summary}, sort_keys=True), flush=True)

    # Pipeline failures are validation failures, never silently excluded.
    return 0 if not failures and rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
