#!/usr/bin/env python3
"""Run one shard of the three-way common-support Hartree spectral audit."""
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

REPRO_CALIPER_DEX = 5e-6
HARTREE_REPRO_CALIPER_DEX = 5e-6
CODECS = ("ZFP", "SZ3", "SPERR")
PAIRS = (("ZFP", "SZ3"), ("ZFP", "SPERR"), ("SZ3", "SPERR"))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-validation-dir", type=Path, required=True)
    p.add_argument("--protocol", type=Path, required=True)
    p.add_argument("--shard-count", type=int, required=True)
    p.add_argument("--shard-index", type=int, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def shard_for(material_id: str, n: int) -> int:
    d = hashlib.sha256(("HARTREE-SPECTRAL-COMMON-SUPPORT|" + material_id).encode()).digest()
    return int.from_bytes(d[:8], "big") % n


def load_protocol(path: Path) -> list[dict[str, Any]]:
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r: dict[str, Any] = dict(row)
            r["triple_id"] = int(row["triple_id"])
            r["span_dex"] = float(row["span_dex"])
            for codec in CODECS:
                p = codec.lower()
                r[f"{p}_reproduced_Linf"] = float(row[f"{p}_reproduced_Linf"])
                r[f"{p}_historical_hartree_rel_RMSE"] = float(row[f"{p}_historical_hartree_rel_RMSE"])
                r[f"{p}_nominal_tolerance_absolute"] = float(row[f"{p}_nominal_tolerance_absolute"])
                r[f"{p}_frozen_row_index_within_material"] = int(row[f"{p}_frozen_row_index_within_material"])
            out.append(r)
    return out


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
    args = parse_args()
    if args.shard_count <= 0 or not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("invalid shard parameters")

    repo = args.repo_root.resolve()
    frozen_validation = args.frozen_validation_dir.resolve()
    protocol_path = args.protocol.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    common_dir = repo / "analysis" / "hartree_spectral_allcodecs"
    sys.path.insert(0, str(common_dir))
    import run_pair_shard as spec  # type: ignore

    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    sys.path.insert(0, str(frozen_validation))
    import development_compatibility_smoke as dev  # type: ignore
    import external_end_to_end as core  # type: ignore

    protocol = load_protocol(protocol_path)
    by_material: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in protocol:
        by_material[str(row["material_id"])].append(row)

    planned = [
        mid for mid in sorted(by_material)
        if shard_for(mid, args.shard_count) == args.shard_index
    ]
    metadata = spec.load_metadata(repo)

    detail_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    triple_rows: list[dict[str, Any]] = []
    radial_rows: list[dict[str, Any]] = []

    for mid in planned:
        meta = metadata[mid]
        blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
        with tempfile.TemporaryDirectory(prefix="hartree_common_support_") as td:
            workdir = Path(td)
            grid, loader = dev.build_grid(meta, blob, workdir)
            field = np.asarray(grid.total, dtype=np.float64)
            lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)
            g2 = spec.reciprocal_g2(tuple(field.shape), lattice)
            nyq = spec.nyquist_mask(tuple(field.shape))

            v0_legacy = spec.legacy_hartree(field, g2)
            v0_safe = spec.safe_hartree(field, g2, nyq)
            v0_legacy_rms = float(np.sqrt(np.mean(v0_legacy * v0_legacy)))
            v0_safe_rms = float(np.sqrt(np.mean(v0_safe * v0_safe)))
            if not (
                np.isfinite(v0_legacy_rms) and v0_legacy_rms > 0
                and np.isfinite(v0_safe_rms) and v0_safe_rms > 0
            ):
                raise RuntimeError(f"invalid reference Hartree RMS for {mid}")

            for triple in by_material[mid]:
                tid = int(triple["triple_id"])
                metrics: dict[str, dict[str, Any]] = {}

                for codec in CODECS:
                    p = codec.lower()
                    target_linf = float(triple[f"{p}_reproduced_Linf"])
                    target_h = float(triple[f"{p}_historical_hartree_rel_RMSE"])
                    tol = float(triple[f"{p}_nominal_tolerance_absolute"])

                    reconstructed, _, codec_config = core.codec_roundtrip(
                        codec.lower(), field, tol, workdir
                    )
                    reconstructed = np.asarray(reconstructed, dtype=np.float64)
                    err = reconstructed - field
                    linf = float(np.max(np.abs(err)))
                    linf_dex = abs(math.log10(linf / target_linf))
                    if linf_dex > REPRO_CALIPER_DEX:
                        raise RuntimeError(
                            f"Linf reproduction failed {mid}/{tid}/{codec}: {linf_dex} dex"
                        )

                    dv_legacy = spec.legacy_hartree(err, g2)
                    legacy_rel = float(
                        np.sqrt(np.mean(dv_legacy * dv_legacy)) / v0_legacy_rms
                    )
                    h_dex = abs(math.log10(legacy_rel / target_h))
                    if h_dex > HARTREE_REPRO_CALIPER_DEX:
                        raise RuntimeError(
                            f"historical Hartree reproduction failed {mid}/{tid}/{codec}: "
                            f"{h_dex} dex"
                        )

                    dv_safe = spec.safe_hartree(err, g2, nyq)
                    safe_rmse = float(np.sqrt(np.mean(dv_safe * dv_safe)))
                    safe_rel = safe_rmse / v0_safe_rms
                    sm, bins = spec.spectral_metrics(err, g2, nyq)
                    pred_rmse2 = (
                        ((4.0 * np.pi) ** 2 / (float(err.size) ** 2))
                        * sm["hartree_weighted_error"]
                    )
                    direct_rmse2 = safe_rmse * safe_rmse
                    parseval_rel = abs(pred_rmse2 - direct_rmse2) / max(
                        direct_rmse2, 1e-300
                    )

                    row = {
                        "triple_id": tid,
                        "material_id": mid,
                        "system_type": triple["system_type"],
                        "triple_span_dex": float(triple["span_dex"]),
                        "codec": codec,
                        "loader": loader,
                        "codec_config": codec_config,
                        "target_reproduced_Linf": target_linf,
                        "reproduced_Linf": linf,
                        "reproduction_distance_dex": linf_dex,
                        "target_historical_hartree_rel_RMSE": target_h,
                        "reproduced_historical_hartree_rel_RMSE": legacy_rel,
                        "historical_hartree_reproduction_distance_dex": h_dex,
                        "nyquist_safe_hartree_rel_RMSE": safe_rel,
                        "safe_parseval_relative_error": parseval_rel,
                        "nominal_tolerance_absolute": tol,
                        "frozen_row_index_within_material":
                            int(triple[f"{p}_frozen_row_index_within_material"]),
                        **sm,
                    }
                    detail_rows.append(row)
                    metrics[codec] = row

                    for br in bins:
                        radial_rows.append({
                            "triple_id": tid,
                            "material_id": mid,
                            "system_type": triple["system_type"],
                            "triple_span_dex": float(triple["span_dex"]),
                            "codec": codec,
                            **br,
                        })

                for a, b in PAIRS:
                    A = metrics[a]
                    B = metrics[b]
                    safe_ratio = (
                        float(A["nyquist_safe_hartree_rel_RMSE"])
                        / float(B["nyquist_safe_hartree_rel_RMSE"])
                    )
                    weighted_factor = math.sqrt(
                        float(A["hartree_weighted_error"])
                        / float(B["hartree_weighted_error"])
                    )
                    energy_factor = math.sqrt(
                        float(A["safe_error_energy"]) / float(B["safe_error_energy"])
                    )
                    susceptibility_factor = math.sqrt(
                        float(A["spectral_hartree_susceptibility"])
                        / float(B["spectral_hartree_susceptibility"])
                    )
                    log_e = math.log10(energy_factor)
                    log_s = math.log10(susceptibility_factor)
                    denom = abs(log_e) + abs(log_s)

                    pair_rows.append({
                        "triple_id": tid,
                        "material_id": mid,
                        "system_type": triple["system_type"],
                        "triple_span_dex": float(triple["span_dex"]),
                        "pair_label": f"{a}/{b}",
                        "codec_a": a,
                        "codec_b": b,
                        "historical_hartree_ratio":
                            float(A["reproduced_historical_hartree_rel_RMSE"])
                            / float(B["reproduced_historical_hartree_rel_RMSE"]),
                        "nyquist_safe_hartree_ratio": safe_ratio,
                        "sqrt_hartree_weighted_ratio": weighted_factor,
                        "sqrt_total_safe_error_energy_ratio": energy_factor,
                        "sqrt_spectral_hartree_susceptibility_ratio":
                            susceptibility_factor,
                        "low_G_fraction_ratio": ratio_or_nan(
                            A["low_G_fraction"], B["low_G_fraction"]
                        ),
                        "high_G_fraction_ratio": ratio_or_nan(
                            A["high_G_fraction"], B["high_G_fraction"]
                        ),
                        "spectral_centroid_delta_qmax":
                            float(A["spectral_centroid_qmax"])
                            - float(B["spectral_centroid_qmax"]),
                        "spectral_structure_abs_log_share":
                            abs(log_s) / denom if denom > 0 else np.nan,
                        "max_safe_parseval_relative_error": max(
                            float(A["safe_parseval_relative_error"]),
                            float(B["safe_parseval_relative_error"]),
                        ),
                    })

                susc = {
                    c: float(metrics[c]["spectral_hartree_susceptibility"])
                    for c in CODECS
                }
                centroid = {
                    c: float(metrics[c]["spectral_centroid_qmax"])
                    for c in CODECS
                }
                lowg = {c: float(metrics[c]["low_G_fraction"]) for c in CODECS}
                energy = {
                    c: float(metrics[c]["safe_error_energy"]) for c in CODECS
                }
                hartree = {
                    c: float(metrics[c]["nyquist_safe_hartree_rel_RMSE"])
                    for c in CODECS
                }

                triple_rows.append({
                    "triple_id": tid,
                    "material_id": mid,
                    "system_type": triple["system_type"],
                    "triple_span_dex": float(triple["span_dex"]),
                    "susceptibility_order_ascending":
                        "<".join(sorted(CODECS, key=lambda c: susc[c])),
                    "centroid_order_descending":
                        ">".join(sorted(CODECS, key=lambda c: centroid[c], reverse=True)),
                    "low_G_fraction_order_ascending":
                        "<".join(sorted(CODECS, key=lambda c: lowg[c])),
                    "safe_hartree_order_ascending":
                        "<".join(sorted(CODECS, key=lambda c: hartree[c])),
                    "spectral_energy_order_ascending":
                        "<".join(sorted(CODECS, key=lambda c: energy[c])),
                    "susceptibility_SPERR_lt_ZFP_lt_SZ3":
                        bool(susc["SPERR"] < susc["ZFP"] < susc["SZ3"]),
                    "centroid_SPERR_gt_ZFP_gt_SZ3":
                        bool(centroid["SPERR"] > centroid["ZFP"] > centroid["SZ3"]),
                    "low_G_SPERR_lt_ZFP_lt_SZ3":
                        bool(lowg["SPERR"] < lowg["ZFP"] < lowg["SZ3"]),
                    "max_safe_parseval_relative_error": max(
                        float(metrics[c]["safe_parseval_relative_error"])
                        for c in CODECS
                    ),
                    "max_Linf_reproduction_distance_dex": max(
                        float(metrics[c]["reproduction_distance_dex"])
                        for c in CODECS
                    ),
                    "max_historical_H_reproduction_distance_dex": max(
                        float(metrics[c]["historical_hartree_reproduction_distance_dex"])
                        for c in CODECS
                    ),
                })

    write_csv(out / f"detail_shard_{args.shard_index:02d}.csv", detail_rows)
    write_csv(out / f"pairs_shard_{args.shard_index:02d}.csv", pair_rows)
    write_csv(out / f"triples_shard_{args.shard_index:02d}.csv", triple_rows)
    write_csv(out / f"radial_shard_{args.shard_index:02d}.csv", radial_rows)
    write_csv(
        out / f"planned_shard_{args.shard_index:02d}.csv",
        [{"material_id": m} for m in planned],
    )
    print(
        f"COMMON_SUPPORT_SHARD_PASS shard={args.shard_index} "
        f"materials={len(planned)} triples={len(triple_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
