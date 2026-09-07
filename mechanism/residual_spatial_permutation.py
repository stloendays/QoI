#!/usr/bin/env python3
"""Residual spatial-permutation mechanism test.

Implements protocol/ERROR_GEOMETRY_PERMUTATION_V0_1_PREREGISTRATION.md.
The intervention preserves each codec residual value multiset exactly while
permuting residual locations within 20 original-density rank strata.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import random
import statistics
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "mechanism" / "basin_error_decomposition_summary.csv"
METADATA = ROOT / "materials_metadata.csv"
MASTER = ROOT / "benchmark" / "master_benchmark_full.csv"
PRIMARY_TOL = 1e-3
CODECS = ("ZFP", "SZ3", "SPERR")
SEEDS = (1701, 1702, 1703, 1704, 1705)
N_STRATA = 20
ERROR_FLOOR = 1e-15
BOOTSTRAP_DRAWS = 5000
MASTER_SEED = "20260907"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--list-materials", action="store_true")
    p.add_argument("--material-id")
    p.add_argument("--output-dir")
    p.add_argument("--aggregate-root")
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def as_bool(x: Any) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes"}


def selected_materials() -> list[str]:
    meta = {r["material_id"]: r for r in read_csv(METADATA)}
    rows = read_csv(SUMMARY)
    by_material: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        try:
            tol = float(r["relative_tolerance"])
        except ValueError:
            continue
        if r["domain"] == "bulk" and abs(tol - PRIMARY_TOL) < 1e-15:
            by_material[r["material_id"]].add(r["codec"].strip().upper())
    out = []
    for material_id in sorted(by_material):
        m = meta.get(material_id)
        if not m:
            continue
        if m.get("source") != "Materials Project":
            continue
        if by_material[material_id] == set(CODECS):
            out.append(material_id)
    return out


def source_record(material_id: str) -> dict[str, str]:
    for r in read_csv(METADATA):
        if r["material_id"] == material_id:
            return r
    raise KeyError(material_id)


def benchmark_rows(material_id: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for r in read_csv(MASTER):
        if r["material_id"] != material_id:
            continue
        if r["codec"].strip().upper() not in CODECS:
            continue
        try:
            tol = float(r["nominal_tolerance_relative"])
        except ValueError:
            continue
        if abs(tol - PRIMARY_TOL) < 1e-15:
            out[r["codec"].strip().upper()] = r
    if set(out) != set(CODECS):
        raise RuntimeError(f"{material_id}: missing benchmark 1e-3 rows; got {sorted(out)}")
    return out


def mechanism_rows(material_id: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for r in read_csv(SUMMARY):
        if r["material_id"] != material_id or r["domain"] != "bulk":
            continue
        try:
            tol = float(r["relative_tolerance"])
        except ValueError:
            continue
        if abs(tol - PRIMARY_TOL) < 1e-15:
            out[r["codec"].strip().upper()] = r
    return out


def load_mp_chgcar(record: dict[str, str], workdir: Path):
    import urllib.request
    from monty.json import MontyDecoder
    from pymatgen.io.vasp.outputs import Chgcar

    req = urllib.request.Request(record["url"], headers={"User-Agent": "QoI-geometry-permutation/0.1"})
    with urllib.request.urlopen(req, timeout=240) as response:
        blob = response.read()
    got_sha = hashlib.sha256(blob).hexdigest()
    if got_sha != record["sha256"]:
        raise RuntimeError(f"source SHA256 mismatch {got_sha} != {record['sha256']}")
    if record.get("source_bytes") and len(blob) != int(record["source_bytes"]):
        raise RuntimeError(f"source byte-count mismatch {len(blob)} != {record['source_bytes']}")
    raw = gzip.decompress(blob) if record["url"].endswith(".gz") else blob
    payload = json.loads(raw.decode("utf-8"), cls=MontyDecoder)

    def find_chgcar(obj: Any, depth: int = 0):
        if depth > 6:
            return None
        if isinstance(obj, Chgcar):
            return obj
        if isinstance(obj, dict):
            for value in obj.values():
                hit = find_chgcar(value, depth + 1)
                if hit is not None:
                    return hit
        elif isinstance(obj, (list, tuple)):
            for value in obj:
                hit = find_chgcar(value, depth + 1)
                if hit is not None:
                    return hit
        return None

    chgcar = find_chgcar(payload)
    if chgcar is None:
        raise RuntimeError(f"{record['material_id']}: no pymatgen Chgcar found in parsed source")
    path = workdir / "CHGCAR"
    chgcar.write_file(path)
    return path, got_sha, len(blob)


def rel_close(a: float, b: float, rtol: float, atol: float) -> bool:
    return abs(a - b) <= atol + rtol * max(abs(a), abs(b))


def process_material(material_id: str, output_dir: Path) -> int:
    import numpy as np
    from baderkit import Grid

    sys.path.insert(0, str(ROOT / "validation"))
    import external_end_to_end as core

    if material_id not in selected_materials():
        raise RuntimeError(f"{material_id} is not in the preregistered selected set")
    record = source_record(material_id)
    bench = benchmark_rows(material_id)
    mech = mechanism_rows(material_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows_out: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix=f"qoi_geom_{material_id}_") as td:
        workdir = Path(td)
        chgcar_path, source_sha, source_bytes = load_mp_chgcar(record, workdir)
        grid = Grid.from_dynamic(chgcar_path)
        field = np.asarray(grid.total, dtype=np.float64)
        if int(field.size) != int(record["npoints"]):
            raise RuntimeError(f"npoints mismatch {field.size} != {record['npoints']}")
        if not np.all(np.isfinite(field)):
            raise RuntimeError("source field contains non-finite values")

        original = core.run_bader(grid)
        q_orig = np.asarray(original["charges"], dtype=np.float64)
        labels_orig = np.asarray(original["atom_labels"])
        value_ptp = float(np.ptp(field))
        field_flat = field.ravel()
        density_order = np.argsort(field_flat, kind="stable")
        strata = np.array_split(density_order, N_STRATA)

        provenance = {
            "material_id": material_id,
            "source_url": record["url"],
            "source_sha256_verified": source_sha,
            "source_bytes_verified": source_bytes,
            "npoints": int(field.size),
            "natoms_bader": int(q_orig.size),
            "value_ptp": value_ptp,
            "n_density_rank_strata": N_STRATA,
            "permutation_seeds": list(SEEDS),
            "primary_relative_tolerance": PRIMARY_TOL,
        }
        (output_dir / "provenance.json").write_text(json.dumps(provenance, indent=2))

        for codec_name in CODECS:
            codec = codec_name.lower()
            br = bench[codec_name]
            abs_bound = float(br["nominal_tolerance_absolute"])
            reconstructed, compressed_bytes, codec_mode = core.codec_roundtrip(
                codec, field, abs_bound, workdir
            )
            reconstructed = np.asarray(reconstructed, dtype=np.float64)
            delta = reconstructed - field
            delta_flat = delta.ravel()
            linf = float(np.max(np.abs(delta_flat)))
            rmse = float(np.sqrt(np.mean(delta_flat * delta_flat)))
            mean_signed = float(np.mean(delta_flat))
            mae = float(np.mean(np.abs(delta_flat)))

            observed_bader = core.run_bader(core.clone_grid_with_total(grid, reconstructed))
            observed_error = float(np.max(np.abs(np.asarray(observed_bader["charges"]) - q_orig)))
            observed_reassigned = float(np.mean(np.asarray(observed_bader["atom_labels"]) != labels_orig))

            expected_linf = float(br["realized_Linf"])
            expected_error = float(br["Bader_error_resolved_e"])
            # Tight enough to catch an implementation/provenance mismatch, while
            # allowing harmless serialization/BLAS roundoff.
            if not rel_close(linf, expected_linf, rtol=2e-6, atol=2e-10):
                raise RuntimeError(
                    f"{material_id} {codec_name}: realized Linf provenance mismatch "
                    f"{linf:.12g} vs benchmark {expected_linf:.12g}"
                )
            if not rel_close(observed_error, expected_error, rtol=2e-5, atol=2e-8):
                # The released representative mechanism record is an additional check.
                mech_error = float(mech[codec_name]["dq_total_max_e"]) if codec_name in mech else float("nan")
                raise RuntimeError(
                    f"{material_id} {codec_name}: Bader provenance mismatch "
                    f"{observed_error:.12g} vs benchmark {expected_error:.12g}; mechanism {mech_error:.12g}"
                )

            for seed in SEEDS:
                rng = np.random.default_rng(seed)
                shuffled_flat = np.empty_like(delta_flat)
                for indices in strata:
                    values = delta_flat[indices].copy()
                    rng.shuffle(values)
                    shuffled_flat[indices] = values
                shuffled_delta = shuffled_flat.reshape(field.shape)
                shuffled_field = field + shuffled_delta

                shuf_linf = float(np.max(np.abs(shuffled_flat)))
                shuf_rmse = float(np.sqrt(np.mean(shuffled_flat * shuffled_flat)))
                shuf_mean = float(np.mean(shuffled_flat))
                shuf_mae = float(np.mean(np.abs(shuffled_flat)))
                norm_audit_ok = (
                    rel_close(shuf_linf, linf, rtol=0.0, atol=1e-14 * max(1.0, linf))
                    and rel_close(shuf_rmse, rmse, rtol=1e-13, atol=1e-15)
                    and rel_close(shuf_mean, mean_signed, rtol=1e-12, atol=1e-15)
                    and rel_close(shuf_mae, mae, rtol=1e-13, atol=1e-15)
                )
                if not norm_audit_ok:
                    raise RuntimeError(f"{material_id} {codec_name} seed {seed}: residual norm preservation failed")

                try:
                    shuffled_bader = core.run_bader(core.clone_grid_with_total(grid, shuffled_field))
                    shuffled_error = float(
                        np.max(np.abs(np.asarray(shuffled_bader["charges"], dtype=np.float64) - q_orig))
                    )
                    shuffled_reassigned = float(
                        np.mean(np.asarray(shuffled_bader["atom_labels"]) != labels_orig)
                    )
                    status = "SUCCESS"
                    error_type = ""
                    error_detail = ""
                except Exception as exc:  # explicit row-level intervention outcome
                    shuffled_error = float("nan")
                    shuffled_reassigned = float("nan")
                    status = "BADER_FAILURE"
                    error_type = type(exc).__name__
                    error_detail = str(exc)
                    failures.append({
                        "material_id": material_id,
                        "codec": codec_name,
                        "seed": seed,
                        "error_type": error_type,
                        "detail": error_detail,
                    })

                rows_out.append({
                    "material_id": material_id,
                    "codec": codec_name,
                    "relative_tolerance": PRIMARY_TOL,
                    "seed": seed,
                    "status": status,
                    "observed_bader_error_e": observed_error,
                    "shuffled_bader_error_e": shuffled_error,
                    "observed_frac_voxels_reassigned": observed_reassigned,
                    "shuffled_frac_voxels_reassigned": shuffled_reassigned,
                    "observed_realized_linf": linf,
                    "shuffled_realized_linf": shuf_linf,
                    "linf_abs_difference": abs(shuf_linf - linf),
                    "observed_rmse": rmse,
                    "shuffled_rmse": shuf_rmse,
                    "rmse_abs_difference": abs(shuf_rmse - rmse),
                    "observed_mean_signed_error": mean_signed,
                    "shuffled_mean_signed_error": shuf_mean,
                    "mean_signed_abs_difference": abs(shuf_mean - mean_signed),
                    "observed_mae": mae,
                    "shuffled_mae": shuf_mae,
                    "mae_abs_difference": abs(shuf_mae - mae),
                    "compression_ratio": float(br["compression_ratio"]),
                    "compressed_bytes": compressed_bytes,
                    "codec_mode": codec_mode,
                    "benchmark_realized_linf": expected_linf,
                    "benchmark_resolved_bader_error_e": expected_error,
                    "norm_audit_ok": norm_audit_ok,
                    "error_type": error_type,
                    "error_detail": error_detail,
                })

    def write(path: Path, data: list[dict[str, Any]], fields: list[str] | None = None):
        if not data:
            if fields:
                with path.open("w", newline="") as f:
                    csv.DictWriter(f, fieldnames=fields).writeheader()
            else:
                path.write_text("")
            return
        if fields is None:
            fields = list(data[0].keys())
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader(); w.writerows(data)

    write(output_dir / "permutation_rows.csv", rows_out)
    write(output_dir / "failures.csv", failures, ["material_id", "codec", "seed", "error_type", "detail"])
    print(json.dumps({
        "material_id": material_id,
        "rows": len(rows_out),
        "failures": len(failures),
        "all_norm_audits": all(as_bool(r["norm_audit_ok"]) for r in rows_out),
    }))
    return 0


def qtile(values: Iterable[float], q: float) -> float | None:
    xs = sorted(float(x) for x in values)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    p = (len(xs) - 1) * q
    lo = int(math.floor(p)); hi = int(math.ceil(p))
    if lo == hi:
        return xs[lo]
    f = p - lo
    return xs[lo] * (1 - f) + xs[hi] * f


def bootstrap_median(values: list[float], label: str) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    if len(values) == 1:
        return values[0], values[0]
    seed = int.from_bytes(hashlib.sha256((MASTER_SEED + "|" + label).encode()).digest()[:8], "big")
    rng = random.Random(seed)
    n = len(values)
    reps = []
    for _ in range(BOOTSTRAP_DRAWS):
        reps.append(statistics.median(values[rng.randrange(n)] for _ in range(n)))
    return qtile(reps, 0.025), qtile(reps, 0.975)


def aggregate(aggregate_root: Path, output_dir: Path) -> int:
    raw: list[dict[str, str]] = []
    failure_rows: list[dict[str, str]] = []
    for path in sorted(aggregate_root.rglob("permutation_rows.csv")):
        raw.extend(read_csv(path))
    for path in sorted(aggregate_root.rglob("failures.csv")):
        rows = read_csv(path)
        failure_rows.extend([r for r in rows if any(r.values())])
    if not raw:
        raise RuntimeError("No permutation rows found for aggregation")

    selected = selected_materials()
    got_materials = sorted({r["material_id"] for r in raw})
    if got_materials != selected:
        raise RuntimeError(f"Permutation coverage mismatch: expected={selected}, got={got_materials}")
    if not all(as_bool(r["norm_audit_ok"]) for r in raw):
        raise RuntimeError("At least one norm-preservation audit failed")

    output_dir.mkdir(parents=True, exist_ok=True)
    material_codec_rows: list[dict[str, Any]] = []
    success_by_mcs: dict[tuple[str, str, int], dict[str, str]] = {}
    observed: dict[tuple[str, str], float] = {}
    for r in raw:
        observed[(r["material_id"], r["codec"])] = float(r["observed_bader_error_e"])
        if r["status"] == "SUCCESS":
            success_by_mcs[(r["material_id"], r["codec"], int(r["seed"]))] = r

    for material_id in selected:
        for codec in CODECS:
            vals = []
            success_seeds = 0
            for seed in SEEDS:
                r = success_by_mcs.get((material_id, codec, seed))
                if r is None:
                    continue
                obs = max(float(r["observed_bader_error_e"]), ERROR_FLOOR)
                shuf = max(float(r["shuffled_bader_error_e"]), ERROR_FLOOR)
                vals.append(math.log10(shuf / obs))
                success_seeds += 1
            if vals:
                med = statistics.median(vals)
                material_codec_rows.append({
                    "material_id": material_id,
                    "codec": codec,
                    "n_successful_seeds": success_seeds,
                    "median_log10_shuffle_over_observed": med,
                    "median_fold_shuffle_over_observed": 10 ** med,
                    "median_abs_log10_change": statistics.median(abs(x) for x in vals),
                })

    attenuation_rows: list[dict[str, Any]] = []
    for material_id in selected:
        for comparator in ("SZ3", "SPERR"):
            obs_z = max(observed[(material_id, "ZFP")], ERROR_FLOOR)
            obs_c = max(observed[(material_id, comparator)], ERROR_FLOOR)
            obs_log_ratio = math.log10(obs_z / obs_c)
            vals = []
            for seed in SEEDS:
                rz = success_by_mcs.get((material_id, "ZFP", seed))
                rc = success_by_mcs.get((material_id, comparator, seed))
                if rz is None or rc is None:
                    continue
                ez = max(float(rz["shuffled_bader_error_e"]), ERROR_FLOOR)
                ec = max(float(rc["shuffled_bader_error_e"]), ERROR_FLOOR)
                vals.append(math.log10(ez / ec) - obs_log_ratio)
            if vals:
                med = statistics.median(vals)
                attenuation_rows.append({
                    "material_id": material_id,
                    "comparator": comparator,
                    "n_paired_seeds": len(vals),
                    "observed_zfp_over_comparator_error_ratio": 10 ** obs_log_ratio,
                    "median_attenuation_log10": med,
                    "attenuation_fold_on_ratio": 10 ** med,
                })

    codec_summary: list[dict[str, Any]] = []
    for codec in CODECS:
        vals = [float(r["median_log10_shuffle_over_observed"]) for r in material_codec_rows if r["codec"] == codec]
        if vals:
            point = statistics.median(vals)
            lo, hi = bootstrap_median(vals, f"codec|{codec}")
            codec_summary.append({
                "codec": codec,
                "n_materials": len(vals),
                "median_log10_shuffle_over_observed": point,
                "median_fold_shuffle_over_observed": 10 ** point,
                "ci_low_fold": 10 ** lo,
                "ci_high_fold": 10 ** hi,
            })

    attenuation_summary: list[dict[str, Any]] = []
    for comparator in ("SZ3", "SPERR"):
        vals = [float(r["median_attenuation_log10"]) for r in attenuation_rows if r["comparator"] == comparator]
        if vals:
            point = statistics.median(vals)
            lo, hi = bootstrap_median(vals, f"attenuation|{comparator}")
            attenuation_summary.append({
                "contrast": f"ZFP/{comparator}",
                "n_materials": len(vals),
                "median_attenuation_log10": point,
                "attenuation_fold_on_error_ratio": 10 ** point,
                "ci_low_log10": lo,
                "ci_high_log10": hi,
                "positive_ci": lo > 0,
            })

    def write(path: Path, data: list[dict[str, Any]]):
        if not data:
            path.write_text(""); return
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader(); w.writerows(data)

    write(output_dir / "permutation_rows_all.csv", raw)
    write(output_dir / "failures_all.csv", failure_rows)
    write(output_dir / "material_codec_effects.csv", material_codec_rows)
    write(output_dir / "attenuation_material_effects.csv", attenuation_rows)
    write(output_dir / "codec_summary.csv", codec_summary)
    write(output_dir / "attenuation_summary.csv", attenuation_summary)

    both_positive = len(attenuation_summary) == 2 and all(as_bool(r["positive_ci"]) for r in attenuation_summary)
    lines = [
        "# Residual spatial-permutation mechanism test v0.1",
        "",
        "This report implements the frozen intervention in `protocol/ERROR_GEOMETRY_PERMUTATION_V0_1_PREREGISTRATION.md`.",
        "Each shuffle preserves the exact codec residual value multiset within 20 original-density rank strata while changing fine spatial assignment.",
        "",
        f"Selected representative bulk Materials Project systems: **{len(selected)}** (`{', '.join(selected)}`).",
        f"Permutation Bader failures: **{len(failure_rows)}**.",
        "",
        "## Within-codec spatial sensitivity",
        "",
        "| codec | materials | median shuffled/observed Bader error [95% CI] |",
        "|---|---:|---:|",
    ]
    for r in codec_summary:
        lines.append(f"| {r['codec']} | {r['n_materials']} | {r['median_fold_shuffle_over_observed']:.3g} [{r['ci_low_fold']:.3g}, {r['ci_high_fold']:.3g}] |")
    lines += [
        "",
        "## ZFP-advantage attenuation after destroying fine spatial organization",
        "",
        "Positive attenuation means the observed ZFP/comparator Bader-error ratio moves upward after spatial permutation, i.e. the observed ZFP advantage shrinks.",
        "",
        "| contrast | materials | median attenuation (log10) [95% CI] | fold change in ZFP/comparator error ratio | CI entirely > 0? |",
        "|---|---:|---:|---:|---|",
    ]
    for r in attenuation_summary:
        lines.append(
            f"| {r['contrast']} | {r['n_materials']} | {r['median_attenuation_log10']:.3g} "
            f"[{r['ci_low_log10']:.3g}, {r['ci_high_log10']:.3g}] | {r['attenuation_fold_on_error_ratio']:.3g}x | {r['positive_ci']} |"
        )
    lines += [
        "",
        f"**Two-comparator preregistered attenuation criterion:** {'SUPPORTED' if both_positive else 'NOT SUPPORTED'}.",
        "",
        "## Interpretation guard",
        "",
        "Because the intervention is a permutation of the *same residual values*, scalar amplitude norms and the residual histogram are fixed by construction. A reproducible Bader response to this intervention is therefore direct evidence that spatial assignment matters. The population statement remains scoped to this preregistered representative bulk mechanism set; it is not a universality claim over all materials.",
    ]
    (output_dir / "RESIDUAL_SPATIAL_PERMUTATION_REPORT.md").write_text("\n".join(lines) + "\n")
    print("selected_materials", selected)
    print("two_comparator_supported", both_positive)
    print("failures", len(failure_rows))
    return 0


def main() -> int:
    args = parse_args()
    if args.list_materials:
        print(json.dumps(selected_materials()))
        return 0
    if args.material_id:
        if not args.output_dir:
            raise SystemExit("--output-dir is required with --material-id")
        return process_material(args.material_id, Path(args.output_dir))
    if args.aggregate_root:
        if not args.output_dir:
            raise SystemExit("--output-dir is required with --aggregate-root")
        return aggregate(Path(args.aggregate_root), Path(args.output_dir))
    raise SystemExit("Choose --list-materials, --material-id, or --aggregate-root")


if __name__ == "__main__":
    raise SystemExit(main())
