#!/usr/bin/env python3
"""Aggregate the confirmatory full-population Hartree spectral mechanism audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

EXPECTED_PAIRS = 457
EXPECTED_MATERIALS = 214
FROZEN_TARGET_RATIO = 0.07762205663818565
BOOT_REPS = 2000
BOOT_SEED = 20260927


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--shards-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def read_many(root: Path, pattern: str) -> pd.DataFrame:
    files = sorted(root.rglob(pattern))
    if not files:
        raise RuntimeError(f"no files matched {pattern}")
    frames = []
    for p in files:
        try:
            frames.append(pd.read_csv(p))
        except pd.errors.EmptyDataError:
            pass
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def center_ci(df: pd.DataFrame, column: str) -> tuple[float, float, float, int]:
    z = df[["material_id", column]].copy()
    z[column] = pd.to_numeric(z[column], errors="coerce")
    z = z[np.isfinite(z[column]) & (z[column] > 0)]
    logs = z.groupby("material_id")[column].apply(
        lambda s: float(np.median(np.log10(s.astype(float))))
    )
    vals = logs.to_numpy(float)
    center = float(10 ** np.median(vals))
    rng = np.random.default_rng(BOOT_SEED)
    boots = np.empty(BOOT_REPS, dtype=float)
    for i in range(BOOT_REPS):
        sample = rng.choice(vals, size=len(vals), replace=True)
        boots[i] = 10 ** np.median(sample)
    return center, float(np.quantile(boots, .025)), float(np.quantile(boots, .975)), int(len(vals))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    args = parse_args()
    root = args.shards_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    detail = read_many(root, "detail_shard_*.csv")
    pairs = read_many(root, "pairs_shard_*.csv")
    radial = read_many(root, "radial_shard_*.csv")
    planned = read_many(root, "planned_shard_*.csv")

    if len(pairs) != EXPECTED_PAIRS:
        raise RuntimeError(f"pair accounting drift: {len(pairs)} != {EXPECTED_PAIRS}")
    if pairs["pair_id"].nunique() != EXPECTED_PAIRS:
        raise RuntimeError("pair IDs are not unique")
    if pairs["material_id"].nunique() != EXPECTED_MATERIALS:
        raise RuntimeError(
            f"material accounting drift: {pairs['material_id'].nunique()} != {EXPECTED_MATERIALS}"
        )
    if planned["material_id"].nunique() != EXPECTED_MATERIALS:
        raise RuntimeError("planned material accounting drift")
    if len(detail) != 2 * EXPECTED_PAIRS:
        raise RuntimeError(f"detail accounting drift: {len(detail)} != {2 * EXPECTED_PAIRS}")

    pairs = pairs.sort_values("pair_id").reset_index(drop=True)
    detail = detail.sort_values(["pair_id", "codec"]).reset_index(drop=True)
    radial = radial.sort_values(["bin_index", "codec", "pair_id"]).reset_index(drop=True)

    pairs.to_csv(out / "matched_pair_mechanism.csv", index=False)
    detail.to_csv(out / "reconstruction_spectral_metrics.csv", index=False)

    radial_summary = (
        radial.groupby(["codec", "bin_index", "q_low", "q_high"], as_index=False)
        .agg(
            median_error_energy_fraction=("error_energy_fraction", "median"),
            p25_error_energy_fraction=("error_energy_fraction", lambda s: float(np.quantile(s, .25))),
            p75_error_energy_fraction=("error_energy_fraction", lambda s: float(np.quantile(s, .75))),
            median_hartree_weighted_fraction=("hartree_weighted_fraction", "median"),
            p25_hartree_weighted_fraction=("hartree_weighted_fraction", lambda s: float(np.quantile(s, .25))),
            p75_hartree_weighted_fraction=("hartree_weighted_fraction", lambda s: float(np.quantile(s, .75))),
            n=("pair_id", "count"),
        )
    )
    radial_summary.to_csv(out / "radial_spectrum_summary.csv", index=False)

    metrics = [
        "target_historical_hartree_ratio",
        "reproduced_historical_hartree_ratio",
        "nyquist_safe_hartree_ratio",
        "sqrt_hartree_weighted_ratio",
        "sqrt_total_safe_error_energy_ratio",
        "sqrt_spectral_hartree_susceptibility_ratio",
        "low_G_fraction_ratio",
        "high_G_fraction_ratio",
        "hartree_weighted_low_G_fraction_ratio",
    ]
    summary_rows: list[dict[str, Any]] = []
    centers: dict[str, float] = {}
    for col in metrics:
        c, lo, hi, nmat = center_ci(pairs, col)
        centers[col] = c
        summary_rows.append({
            "metric": col,
            "material_level_center": c,
            "ci_low": lo,
            "ci_high": hi,
            "n_materials": nmat,
        })
    pd.DataFrame(summary_rows).to_csv(out / "mechanism_ratio_summary.csv", index=False)

    max_parseval = float(pd.to_numeric(pairs["max_safe_parseval_relative_error"], errors="coerce").max())
    max_identity_log = float(
        np.max(
            np.abs(
                np.log10(pairs["nyquist_safe_hartree_ratio"].astype(float).to_numpy())
                - np.log10(pairs["sqrt_hartree_weighted_ratio"].astype(float).to_numpy())
            )
        )
    )

    target_center = centers["target_historical_hartree_ratio"]
    legacy_center = centers["reproduced_historical_hartree_ratio"]
    safe_center = centers["nyquist_safe_hartree_ratio"]
    energy_center = centers["sqrt_total_safe_error_energy_ratio"]
    susceptibility_center = centers["sqrt_spectral_hartree_susceptibility_ratio"]

    target_file_consistency = abs(math.log10(target_center / FROZEN_TARGET_RATIO)) < 1e-8
    legacy_reproduction = abs(math.log10(legacy_center / target_center)) < 1e-4
    parseval_pass = max_parseval < 1e-10
    identity_pass = max_identity_log < 1e-10
    nyquist_robust = abs(math.log10(safe_center / legacy_center)) < 0.05

    material_structure_share = pairs.groupby("material_id")["spectral_structure_abs_log_share"].median()
    median_structure_share = float(material_structure_share.median())
    structure_lt1_fraction = float(
        pairs.groupby("material_id")["sqrt_spectral_hartree_susceptibility_ratio"]
        .apply(lambda s: float(np.median(np.log10(s.astype(float)))) < 0)
        .mean()
    )
    centroid_positive_fraction = float(
        pairs.groupby("material_id")["spectral_centroid_delta_qmax"].median().gt(0).mean()
    )
    low_g_lt1_fraction = float(
        pairs.groupby("material_id")["low_G_fraction_ratio"]
        .apply(lambda s: float(np.median(np.log10(s.astype(float)))) < 0)
        .mean()
    )

    structure_direction = susceptibility_center < 1.0
    magnitude_alone_insufficient = abs(math.log10(energy_center)) < abs(math.log10(safe_center))
    frequency_structure_dominant = median_structure_share > 0.5

    if all([
        target_file_consistency,
        legacy_reproduction,
        parseval_pass,
        identity_pass,
        nyquist_robust,
        structure_direction,
        magnitude_alone_insufficient,
    ]):
        status = (
            "FREQUENCY_STRUCTURE_DOMINANT"
            if frequency_structure_dominant
            else "WEIGHTED_SPECTRAL_MECHANISM_SUPPORTED"
        )
    else:
        status = "MECHANISM_NOT_CLOSED"

    diagnostics = {
        "status": status,
        "population": {
            "matched_pairs": int(len(pairs)),
            "materials": int(pairs["material_id"].nunique()),
            "reconstructions": int(len(detail)),
        },
        "headline_centers": {
            "frozen_target_historical_hartree_ratio": FROZEN_TARGET_RATIO,
            "target_pair_file_recomputed_center": target_center,
            "reproduced_historical_hartree_ratio": legacy_center,
            "nyquist_safe_hartree_ratio": safe_center,
            "sqrt_hartree_weighted_ratio": centers["sqrt_hartree_weighted_ratio"],
            "sqrt_total_safe_error_energy_ratio": energy_center,
            "sqrt_spectral_hartree_susceptibility_ratio": susceptibility_center,
            "low_G_fraction_ratio": centers["low_G_fraction_ratio"],
        },
        "mechanism_diagnostics": {
            "median_material_spectral_structure_abs_log_share": median_structure_share,
            "materials_with_spectral_susceptibility_ZFP_lt_SZ3_fraction": structure_lt1_fraction,
            "materials_with_ZFP_centroid_higher_than_SZ3_fraction": centroid_positive_fraction,
            "materials_with_ZFP_low_G_fraction_lt_SZ3_fraction": low_g_lt1_fraction,
            "max_safe_parseval_relative_error": max_parseval,
            "max_abs_log10_safe_vs_weighted_identity_error": max_identity_log,
        },
        "checks": {
            "frozen_target_center_recomputed_exactly": bool(target_file_consistency),
            "historical_hartree_reproduction": bool(legacy_reproduction),
            "safe_parseval_identity": bool(parseval_pass),
            "safe_hartree_equals_weighted_spectrum_identity": bool(identity_pass),
            "nyquist_correction_does_not_materially_change_codec_ratio": bool(nyquist_robust),
            "ZFP_has_lower_spectral_hartree_susceptibility_than_SZ3": bool(structure_direction),
            "total_unweighted_spectral_energy_alone_is_insufficient": bool(magnitude_alone_insufficient),
            "frequency_structure_contributes_more_than_half_absolute_log_effect": bool(frequency_structure_dominant),
        },
    }
    (out / "SUMMARY.json").write_text(json.dumps(diagnostics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Hartree spectral mechanism audit",
        "",
        f"Status: **{status}**",
        "",
        "## Population",
        "",
        f"- Exact frozen ZFP/SZ3 matched pairs: **{len(pairs)}**",
        f"- Materials: **{pairs['material_id'].nunique()}**",
        f"- Regenerated selected reconstructions: **{len(detail)}**",
        "",
        "## Reproduction and operator audit",
        "",
        f"- Frozen matched-pair center: **{target_center:.6g}**",
        f"- Reproduced historical Hartree center: **{legacy_center:.6g}**",
        f"- Nyquist-safe Hartree center: **{safe_center:.6g}**",
        f"- sqrt(Hartree-weighted spectral ratio): **{centers['sqrt_hartree_weighted_ratio']:.6g}**",
        f"- maximum safe Parseval relative error: **{max_parseval:.3e}**",
        "",
        "## Spectral decomposition",
        "",
        f"- sqrt(total safe spectral-energy ratio), ZFP/SZ3: **{energy_center:.6g}**",
        f"- sqrt(spectral Hartree-susceptibility ratio), ZFP/SZ3: **{susceptibility_center:.6g}**",
        f"- material-median absolute-log share from spectral susceptibility: **{median_structure_share:.1%}**",
        f"- materials with lower ZFP spectral Hartree susceptibility: **{structure_lt1_fraction:.1%}**",
        f"- materials with higher ZFP spectral centroid: **{centroid_positive_fraction:.1%}**",
        f"- materials with lower ZFP low-G energy fraction: **{low_g_lt1_fraction:.1%}**",
        "",
        "The safe Hartree ratio is exactly constrained by the Poisson-weighted spectrum. "
        "The separate total-energy and spectral-susceptibility factors indicate whether "
        "the codec effect is primarily an L2 error-magnitude effect, a frequency-allocation "
        "effect, or a combination of both.",
        "",
        "The frozen manuscript is not modified by this audit.",
    ]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    hashes = []
    for p in sorted(out.iterdir()):
        if p.is_file():
            hashes.append(f"{sha256(p)}  {p.name}")
    (out / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")

    print(
        f"HARTREE_SPECTRAL_AGGREGATE_PASS status={status} "
        f"pairs={len(pairs)} materials={pairs['material_id'].nunique()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
