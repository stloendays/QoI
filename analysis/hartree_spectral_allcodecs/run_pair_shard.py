#!/usr/bin/env python3
"""Generic pairwise shard runner for the full-population Hartree spectral audit.

The selected pair population is read verbatim from the frozen 0.10-dex
matched-realized-Linf table. Historical Hartree errors are reproduced exactly;
mechanism metrics use the same Nyquist-safe Hermitian discrete Poisson operator
that closed the confirmatory ZFP/SZ3 audit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import math
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

PAIR_A = ""
PAIR_B = ""
EXPECTED_PAIRS = 0
EXPECTED_MATERIALS = 0
LOW_Q = 0.25
HIGH_Q = 0.75
MAP_CALIPER_DEX = 1e-9
REPRO_CALIPER_DEX = 5e-6
HARTREE_REPRO_CALIPER_DEX = 5e-6


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-validation-dir", type=Path, required=True)
    p.add_argument("--shard-count", type=int, required=True)
    p.add_argument("--shard-index", type=int, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--codec-a", required=True)
    p.add_argument("--codec-b", required=True)
    p.add_argument("--expected-pairs", type=int, required=True)
    p.add_argument("--expected-materials", type=int, required=True)
    return p.parse_args()


def finite_float(x: Any) -> float | None:
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def shard_for(material_id: str, n: int) -> int:
    d = hashlib.sha256(("HARTREE-SPECTRAL-MECHANISM|" + material_id).encode()).digest()
    return int.from_bytes(d[:8], "big") % n


def load_metadata(repo: Path) -> dict[str, dict[str, str]]:
    with (repo / "materials_metadata.csv").open(newline="", encoding="utf-8") as f:
        return {r["material_id"]: r for r in csv.DictReader(f)}


def load_pairs(repo: Path) -> list[dict[str, Any]]:
    path = repo / "analysis" / "hartree_qsq_full" / "results" / "matched_realized_linf_pairs_0p10dex.csv"
    out: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["codec_a"] != PAIR_A or row["codec_b"] != PAIR_B:
                continue
            out.append({
                "pair_id": len(out),
                "material_id": row["material_id"],
                "system_type": row["system_type"],
                "distance_dex": float(row["distance_dex"]),
                "linf_a": float(row["linf_a"]),
                "linf_b": float(row["linf_b"]),
                "hartree_error_a": float(row["hartree_error_a"]),
                "hartree_error_b": float(row["hartree_error_b"]),
                "hartree_ratio_target": float(row["hartree_ratio_a_over_b"]),
            })
    if len(out) != EXPECTED_PAIRS or len({r["material_id"] for r in out}) != EXPECTED_MATERIALS:
        raise RuntimeError(
            f"frozen {PAIR_A}/{PAIR_B} matched-pair population drift: "
            f"pairs={len(out)} expected={EXPECTED_PAIRS}, "
            f"materials={len({r['material_id'] for r in out})} expected_materials={EXPECTED_MATERIALS}"
        )
    return out


def load_full_hartree_rows(
    repo: Path,
    materials: set[str],
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    path = repo / "analysis" / "hartree_qsq_full" / "results" / "hartree_codec_rows.csv"
    out: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mid = row["material_id"]
            codec = row["codec"].strip().upper()
            if mid not in materials or codec not in {PAIR_A, PAIR_B}:
                continue
            gate = str(row.get("scientific_reproduction_gate_pass", "")).strip().lower()
            if gate not in {"true", "1", "yes", "t"}:
                continue
            linf = finite_float(row.get("reproduced_realized_Linf"))
            herr = finite_float(row.get("hartree_error_rel_RMSE"))
            tol = finite_float(row.get("nominal_tolerance_absolute"))
            if linf is None or linf <= 0 or herr is None or herr <= 0 or tol is None or tol <= 0:
                continue
            r = dict(row)
            r["_reproduced_linf"] = float(linf)
            r["_historical_hartree"] = float(herr)
            r["_abs_bound"] = float(tol)
            r["_frozen_linf"] = float(row["frozen_realized_Linf"])
            r["_frozen_row_index"] = int(float(row["frozen_row_index_within_material"]))
            out[mid][codec].append(r)
    return out


def greedy_map_targets(
    targets: list[tuple[int, float, float]],
    candidates: list[dict[str, Any]],
) -> dict[int, tuple[dict[str, Any], float]]:
    edges: list[tuple[float, float, int, int, int]] = []
    for ti, (pair_id, target_linf, target_h) in enumerate(targets):
        ll = math.log10(target_linf)
        lh = math.log10(target_h)
        for ci, row in enumerate(candidates):
            d_linf = abs(ll - math.log10(float(row["_reproduced_linf"])))
            d_h = abs(lh - math.log10(float(row["_historical_hartree"])))
            if d_linf <= MAP_CALIPER_DEX + 1e-15 and d_h <= MAP_CALIPER_DEX + 1e-15:
                edges.append((max(d_linf, d_h), d_linf + d_h, int(row["_frozen_row_index"]), ti, ci))
    edges.sort()
    used_t: set[int] = set()
    used_c: set[int] = set()
    result: dict[int, tuple[dict[str, Any], float]] = {}
    for max_d, _, _, ti, ci in edges:
        if ti in used_t or ci in used_c:
            continue
        used_t.add(ti)
        used_c.add(ci)
        pair_id = targets[ti][0]
        result[pair_id] = (candidates[ci], max_d)
    if len(result) != len(targets):
        missing = sorted(set(pid for pid, _, _ in targets) - set(result))
        raise RuntimeError(f"could not uniquely map matched-pair rows to full Hartree rows: {missing[:8]}")
    return result


def reciprocal_g2(shape: tuple[int, int, int], lattice: np.ndarray) -> np.ndarray:
    nx, ny, nz = shape
    B = 2.0 * np.pi * np.linalg.inv(lattice).T
    n1 = np.fft.fftfreq(nx) * nx
    n2 = np.fft.fftfreq(ny) * ny
    n3 = np.fft.rfftfreq(nz) * nz
    N1, N2, N3 = np.meshgrid(n1, n2, n3, indexing="ij")
    G = N1[..., None] * B[0] + N2[..., None] * B[1] + N3[..., None] * B[2]
    return np.einsum("...k,...k->...", G, G)


def nyquist_mask(shape: tuple[int, int, int]) -> np.ndarray:
    nx, ny, nz = shape
    m = np.zeros((nx, ny, nz // 2 + 1), dtype=bool)
    if nx % 2 == 0:
        m[nx // 2, :, :] = True
    if ny % 2 == 0:
        m[:, ny // 2, :] = True
    if nz % 2 == 0:
        m[:, :, -1] = True
    return m


def rfft_multiplicity(shape: tuple[int, int, int]) -> np.ndarray:
    nz = shape[2]
    nr = nz // 2 + 1
    w = np.full(nr, 2.0, dtype=np.float64)
    w[0] = 1.0
    if nz % 2 == 0:
        w[-1] = 1.0
    return w.reshape(1, 1, nr)


def legacy_hartree(field: np.ndarray, g2: np.ndarray) -> np.ndarray:
    F = np.fft.rfftn(field)
    V = np.zeros_like(F)
    mask = g2 > 0
    V[mask] = 4.0 * np.pi * F[mask] / g2[mask]
    return np.fft.irfftn(V, s=field.shape, axes=(0, 1, 2))


def safe_hartree(field: np.ndarray, g2: np.ndarray, nyq: np.ndarray) -> np.ndarray:
    F = np.fft.rfftn(field)
    V = np.zeros_like(F)
    mask = (g2 > 0) & (~nyq)
    V[mask] = 4.0 * np.pi * F[mask] / g2[mask]
    return np.fft.irfftn(V, s=field.shape, axes=(0, 1, 2))


def spectral_metrics(
    err: np.ndarray,
    g2: np.ndarray,
    nyq: np.ndarray,
) -> tuple[dict[str, float], list[dict[str, float]]]:
    F = np.fft.rfftn(err)
    Ew = (np.abs(F) ** 2) * rfft_multiplicity(err.shape)
    safe = (g2 > 0) & (~nyq)
    if not np.any(safe):
        raise RuntimeError("no safe reciprocal modes")

    safe_energy = float(Ew[safe].sum())
    if not np.isfinite(safe_energy) or safe_energy <= 0:
        raise RuntimeError("invalid safe spectral energy")

    G = np.sqrt(g2)
    gmax = float(G[safe].max())
    q = np.zeros_like(G)
    q[safe] = G[safe] / gmax
    low = safe & (q <= LOW_Q)
    high = safe & (q >= HIGH_Q)

    low_energy = float(Ew[low].sum())
    high_energy = float(Ew[high].sum())
    centroid = float((Ew[safe] * q[safe]).sum() / safe_energy)

    WH = float((Ew[safe] / (g2[safe] ** 2)).sum())
    if not np.isfinite(WH) or WH <= 0:
        raise RuntimeError("invalid Hartree-weighted energy")
    low_WH = float((Ew[low] / (g2[low] ** 2)).sum()) if np.any(low) else 0.0

    full_energy = float(Ew.sum())
    nyq_energy = float(Ew[nyq].sum())
    g0 = g2 == 0
    g0_energy = float(Ew[g0].sum())

    metrics = {
        "safe_error_energy": safe_energy,
        "low_G_error_energy": low_energy,
        "high_G_error_energy": high_energy,
        "low_G_fraction": low_energy / safe_energy,
        "high_G_fraction": high_energy / safe_energy,
        "spectral_centroid_qmax": centroid,
        "hartree_weighted_error": WH,
        "hartree_weighted_low_G_fraction": low_WH / WH,
        "spectral_hartree_susceptibility": WH / safe_energy,
        "nyquist_error_energy_fraction_total": nyq_energy / full_energy if full_energy > 0 else np.nan,
        "G0_error_energy_fraction_total": g0_energy / full_energy if full_energy > 0 else np.nan,
    }

    bins: list[dict[str, float]] = []
    edges = np.linspace(0.0, 1.0, 33)
    for i in range(len(edges) - 1):
        lo = float(edges[i])
        hi = float(edges[i + 1])
        if i == len(edges) - 2:
            bm = safe & (q >= lo) & (q <= hi)
        else:
            bm = safe & (q >= lo) & (q < hi)
        ee = float(Ew[bm].sum()) if np.any(bm) else 0.0
        wh = float((Ew[bm] / (g2[bm] ** 2)).sum()) if np.any(bm) else 0.0
        bins.append({
            "bin_index": i,
            "q_low": lo,
            "q_high": hi,
            "error_energy_fraction": ee / safe_energy,
            "hartree_weighted_fraction": wh / WH,
        })
    return metrics, bins


def ratio_or_nan(num: float, den: float) -> float:
    num = float(num)
    den = float(den)
    if not (np.isfinite(num) and np.isfinite(den)) or den <= 0 or num < 0:
        return np.nan
    return num / den


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for k in row:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    global PAIR_A, PAIR_B, EXPECTED_PAIRS, EXPECTED_MATERIALS
    args = parse_args()
    PAIR_A = str(args.codec_a).upper()
    PAIR_B = str(args.codec_b).upper()
    EXPECTED_PAIRS = int(args.expected_pairs)
    EXPECTED_MATERIALS = int(args.expected_materials)
    if PAIR_A == PAIR_B:
        raise SystemExit("codec-a and codec-b must differ")
    if args.shard_count <= 0 or not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("invalid shard parameters")

    repo = args.repo_root.resolve()
    frozen_validation = args.frozen_validation_dir.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    sys.path.insert(0, str(frozen_validation))
    import development_compatibility_smoke as dev  # type: ignore
    import external_end_to_end as core  # type: ignore

    pairs = load_pairs(repo)
    by_material: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in pairs:
        by_material[p["material_id"]].append(p)
    planned = [m for m in sorted(by_material) if shard_for(m, args.shard_count) == args.shard_index]
    metadata = load_metadata(repo)
    full_rows = load_full_hartree_rows(repo, set(planned))

    slug = f"{PAIR_A.lower()}_vs_{PAIR_B.lower()}"
    detail_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    radial_rows: list[dict[str, Any]] = []

    for mid in planned:
        meta = metadata[mid]
        blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
        with tempfile.TemporaryDirectory(prefix="hartree_spectral_") as td:
            workdir = Path(td)
            grid, loader = dev.build_grid(meta, blob, workdir)
            field = np.asarray(grid.total, dtype=np.float64)
            lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)
            g2 = reciprocal_g2(tuple(field.shape), lattice)
            nyq = nyquist_mask(tuple(field.shape))
            v0_legacy = legacy_hartree(field, g2)
            v0_safe = safe_hartree(field, g2, nyq)
            v0_legacy_rms = float(np.sqrt(np.mean(v0_legacy * v0_legacy)))
            v0_safe_rms = float(np.sqrt(np.mean(v0_safe * v0_safe)))
            if not (np.isfinite(v0_legacy_rms) and v0_legacy_rms > 0 and np.isfinite(v0_safe_rms) and v0_safe_rms > 0):
                raise RuntimeError(f"invalid reference Hartree RMS for {mid}")

            material_pairs = by_material[mid]
            targets_a = [
                (int(p["pair_id"]), float(p["linf_a"]), float(p["hartree_error_a"]))
                for p in material_pairs
            ]
            targets_b = [
                (int(p["pair_id"]), float(p["linf_b"]), float(p["hartree_error_b"]))
                for p in material_pairs
            ]
            map_a = greedy_map_targets(targets_a, full_rows[mid][PAIR_A])
            map_b = greedy_map_targets(targets_b, full_rows[mid][PAIR_B])

            selected_metrics: dict[tuple[int, str], dict[str, Any]] = {}
            by_pair_id = {int(p["pair_id"]): p for p in material_pairs}
            for codec, mapping in ((PAIR_A, map_a), (PAIR_B, map_b)):
                for pair_id, (frozen, map_dist) in mapping.items():
                    target = by_pair_id[pair_id]
                    target_linf = float(target["linf_a"] if codec == PAIR_A else target["linf_b"])
                    target_h = float(target["hartree_error_a"] if codec == PAIR_A else target["hartree_error_b"])

                    reconstructed, _, codec_config = core.codec_roundtrip(
                        codec.lower(), field, float(frozen["_abs_bound"]), workdir
                    )
                    reconstructed = np.asarray(reconstructed, dtype=np.float64)
                    err = reconstructed - field
                    linf = float(np.max(np.abs(err)))
                    repro_dex = abs(math.log10(linf / target_linf))
                    if repro_dex > REPRO_CALIPER_DEX:
                        raise RuntimeError(
                            f"realized-Linf reproduction failed {mid}/{pair_id}/{codec}: "
                            f"{repro_dex} dex"
                        )

                    dv_legacy = legacy_hartree(err, g2)
                    legacy_rel = float(np.sqrt(np.mean(dv_legacy * dv_legacy)) / v0_legacy_rms)
                    h_dex = abs(math.log10(legacy_rel / target_h))
                    if h_dex > HARTREE_REPRO_CALIPER_DEX:
                        raise RuntimeError(
                            f"historical Hartree reproduction failed {mid}/{pair_id}/{codec}: "
                            f"{h_dex} dex"
                        )

                    dv_safe = safe_hartree(err, g2, nyq)
                    safe_rmse = float(np.sqrt(np.mean(dv_safe * dv_safe)))
                    safe_rel = safe_rmse / v0_safe_rms
                    sm, bins = spectral_metrics(err, g2, nyq)
                    pred_rmse2 = ((4.0 * np.pi) ** 2 / (float(err.size) ** 2)) * sm["hartree_weighted_error"]
                    direct_rmse2 = safe_rmse * safe_rmse
                    parseval_rel = abs(pred_rmse2 - direct_rmse2) / max(direct_rmse2, 1e-300)

                    row = {
                        "pair_id": pair_id,
                        "material_id": mid,
                        "system_type": target["system_type"],
                        "codec": codec,
                        "loader": loader,
                        "codec_config": codec_config,
                        "target_matched_Linf": target_linf,
                        "frozen_benchmark_Linf": float(frozen["_frozen_linf"]),
                        "full_population_reproduced_Linf": float(frozen["_reproduced_linf"]),
                        "full_population_historical_hartree_rel_RMSE": float(frozen["_historical_hartree"]),
                        "reproduced_Linf": linf,
                        "frozen_to_target_map_distance_dex": map_dist,
                        "reproduced_to_target_distance_dex": repro_dex,
                        "target_historical_hartree_rel_RMSE": target_h,
                        "reproduced_historical_hartree_rel_RMSE": legacy_rel,
                        "historical_hartree_reproduction_distance_dex": h_dex,
                        "nyquist_safe_hartree_rel_RMSE": safe_rel,
                        "safe_parseval_relative_error": parseval_rel,
                        "nominal_tolerance_absolute": float(frozen["_abs_bound"]),
                        "frozen_row_index_within_material": int(frozen["_frozen_row_index"]),
                        **sm,
                    }
                    detail_rows.append(row)
                    selected_metrics[(pair_id, codec)] = row

                    for br in bins:
                        radial_rows.append({
                            "pair_id": pair_id,
                            "material_id": mid,
                            "system_type": target["system_type"],
                            "codec": codec,
                            **br,
                        })

            for target in material_pairs:
                pid = int(target["pair_id"])
                a = selected_metrics[(pid, PAIR_A)]
                b = selected_metrics[(pid, PAIR_B)]
                safe_ratio = float(a["nyquist_safe_hartree_rel_RMSE"]) / float(b["nyquist_safe_hartree_rel_RMSE"])
                weighted_factor = math.sqrt(float(a["hartree_weighted_error"]) / float(b["hartree_weighted_error"]))
                energy_factor = math.sqrt(float(a["safe_error_energy"]) / float(b["safe_error_energy"]))
                susceptibility_factor = math.sqrt(
                    float(a["spectral_hartree_susceptibility"]) /
                    float(b["spectral_hartree_susceptibility"])
                )
                log_total = math.log10(safe_ratio)
                log_energy = math.log10(energy_factor)
                log_susc = math.log10(susceptibility_factor)
                denom = abs(log_energy) + abs(log_susc)
                pair_rows.append({
                    "pair_id": pid,
                    "pair_label": f"{PAIR_A}/{PAIR_B}",
                    "codec_a": PAIR_A,
                    "codec_b": PAIR_B,
                    "material_id": mid,
                    "system_type": target["system_type"],
                    "distance_dex": float(target["distance_dex"]),
                    "target_historical_hartree_ratio": float(target["hartree_ratio_target"]),
                    "reproduced_historical_hartree_ratio":
                        float(a["reproduced_historical_hartree_rel_RMSE"]) /
                        float(b["reproduced_historical_hartree_rel_RMSE"]),
                    "nyquist_safe_hartree_ratio": safe_ratio,
                    "sqrt_hartree_weighted_ratio": weighted_factor,
                    "sqrt_total_safe_error_energy_ratio": energy_factor,
                    "sqrt_spectral_hartree_susceptibility_ratio": susceptibility_factor,
                    "low_G_fraction_ratio": ratio_or_nan(a["low_G_fraction"], b["low_G_fraction"]),
                    "high_G_fraction_ratio": ratio_or_nan(a["high_G_fraction"], b["high_G_fraction"]),
                    "spectral_centroid_delta_qmax": float(a["spectral_centroid_qmax"]) - float(b["spectral_centroid_qmax"]),
                    "hartree_weighted_low_G_fraction_ratio": ratio_or_nan(
                        a["hartree_weighted_low_G_fraction"],
                        b["hartree_weighted_low_G_fraction"],
                    ),
                    "nyquist_energy_fraction_A": float(a["nyquist_error_energy_fraction_total"]),
                    "nyquist_energy_fraction_B": float(b["nyquist_error_energy_fraction_total"]),
                    "max_safe_parseval_relative_error": max(
                        float(a["safe_parseval_relative_error"]),
                        float(b["safe_parseval_relative_error"]),
                    ),
                    "log10_safe_hartree_ratio": log_total,
                    "log10_energy_factor": log_energy,
                    "log10_susceptibility_factor": log_susc,
                    "spectral_structure_abs_log_share": abs(log_susc) / denom if denom > 0 else np.nan,
                    "spectral_and_energy_contributions_same_direction":
                        (log_energy == 0 or log_susc == 0 or (log_energy > 0) == (log_susc > 0)),
                })

    write_csv(out / f"detail_{slug}_shard_{args.shard_index:02d}.csv", detail_rows)
    write_csv(out / f"pairs_{slug}_shard_{args.shard_index:02d}.csv", pair_rows)
    write_csv(out / f"radial_{slug}_shard_{args.shard_index:02d}.csv", radial_rows)
    write_csv(out / f"planned_{slug}_shard_{args.shard_index:02d}.csv", [{"material_id": m} for m in planned])
    print(
        f"HARTREE_SPECTRAL_PAIR_SHARD_PASS pair={PAIR_A}/{PAIR_B} "
        f"shard={args.shard_index} materials={len(planned)} pairs={len(pair_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
