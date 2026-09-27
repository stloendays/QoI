#!/usr/bin/env python3
"""Hartree-QSQ reference-stability and certification pilot.

This is a research extension separate from the frozen submission scope.
It reuses the historical 12-material Hartree pilot, applies the same five
QSQ seed labels and the same material-specific float32-amplitude definition,
and measures the response of the periodic electronic Hartree potential.

Numerical outputs are written to an output directory supplied at runtime.
The script intentionally prints no scientific values to stdout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "analysis"))

from mp_chgcar_loader import load_mp_density, parse_ngrid  # noqa: E402
from hartree_potential_pilot.run_hartree_pilot import reciprocal_g2, hartree_potential  # noqa: E402

SEEDS = (20260905, 1, 2, 3, 4)
TAUS = (1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3)
MAX_REFERENCE_SCALE_FOR_GO = 1e-5
MIN_MONOTONE_MATERIALS_FOR_GO = 10
MIN_MEDIAN_LOGLOG_R2_FOR_GO = 0.99


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def as_bool(x) -> bool:
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    return str(x).strip().lower() in {"true", "t", "1", "yes"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    full_path = REPO / "analysis" / "hartree_potential_pilot" / "full_ladder_rows.csv"
    mono_path = REPO / "analysis" / "hartree_potential_pilot" / "monotonicity.csv"
    old_qsq_path = REPO / "stability" / "stability_floor_A1_per_seed.csv"
    meta_path = REPO / "materials_metadata.csv"

    full = pd.read_csv(full_path)
    mono = pd.read_csv(mono_path)
    old_qsq = pd.read_csv(old_qsq_path)
    meta = pd.read_csv(meta_path).set_index("material_id")

    materials = list(dict.fromkeys(full["material_id"].astype(str).tolist()))
    if len(materials) != 12:
        raise RuntimeError(f"historical Hartree pilot cohort drift: expected 12, got {len(materials)}")

    seed_rows: list[dict] = []
    material_rows: list[dict] = []

    for mid in materials:
        if mid not in meta.index:
            raise RuntimeError(f"missing metadata for {mid}")
        m = meta.loc[mid]

        old = old_qsq[old_qsq["material_id"].astype(str) == mid].copy()
        old_seed_set = set(old["seed"].astype(int).tolist())
        if old_seed_set != set(SEEDS) or len(old) != len(SEEDS):
            raise RuntimeError(f"QSQ seed-set drift for {mid}: {old_seed_set}")
        eps_values = old["probe_linf"].astype(float).to_numpy()
        if not np.allclose(eps_values, eps_values[0], rtol=0.0, atol=0.0):
            raise RuntimeError(f"QSQ amplitude drift across seeds for {mid}")
        epsilon_frozen = float(eps_values[0])

        rec = load_mp_density(
            args.cache / f"{mid}.json.gz",
            expected_sha256=str(m.sha256),
            expected_ngrid=parse_ngrid(m.ngrid),
            expected_npoints=int(m.npoints),
            expected_natoms=int(m.natoms),
        )
        rho = np.ascontiguousarray(rec["grid"], dtype=np.float64)
        rho_f32 = rho.astype(np.float32).astype(np.float64)
        epsilon_recomputed = float(np.max(np.abs(rho_f32 - rho)))
        amp_tol = max(1e-15, 16.0 * np.finfo(np.float64).eps * max(1.0, abs(epsilon_frozen)))
        if not np.isclose(epsilon_recomputed, epsilon_frozen, rtol=1e-10, atol=amp_tol):
            raise RuntimeError(
                f"float32 amplitude mismatch for {mid}: recomputed={epsilon_recomputed!r}, frozen={epsilon_frozen!r}"
            )

        g2 = reciprocal_g2(rho.shape, rec["lattice"])
        v0 = hartree_potential(rho, g2)
        v0_rms = float(np.sqrt(np.mean(v0 * v0)))
        if not np.isfinite(v0_rms) or v0_rms <= 0:
            raise RuntimeError(f"invalid reference Hartree RMS for {mid}")

        f32_dv = hartree_potential(rho_f32 - rho, g2)
        f32_rel_rmse = float(np.sqrt(np.mean(f32_dv * f32_dv)) / v0_rms)

        per_seed = []
        for seed in SEEDS:
            rng = np.random.Generator(np.random.PCG64(seed))
            noise = rng.uniform(-epsilon_frozen, epsilon_frozen, size=rho.shape).astype(np.float64, copy=False)
            measured_linf = float(np.max(np.abs(noise))) if noise.size else 0.0
            if measured_linf > epsilon_frozen * (1.0 + 16.0 * np.finfo(np.float64).eps):
                raise RuntimeError(f"realized perturbation exceeds epsilon for {mid}/{seed}")
            dv = hartree_potential(noise, g2)
            rel_rmse = float(np.sqrt(np.mean(dv * dv)) / v0_rms)
            rel_linf = float(np.max(np.abs(dv)) / v0_rms)
            if not (np.isfinite(rel_rmse) and np.isfinite(rel_linf)):
                raise RuntimeError(f"non-finite Hartree response for {mid}/{seed}")
            row = {
                "material_id": mid,
                "seed": int(seed),
                "epsilon": epsilon_frozen,
                "measured_noise_Linf": measured_linf,
                "hartree_response_rel_RMSE": rel_rmse,
                "hartree_response_rel_Linf_over_Vrms": rel_linf,
                "mean_noise": float(np.mean(noise)),
                "npoints": int(rho.size),
            }
            seed_rows.append(row)
            per_seed.append(row)

        responses = np.asarray([r["hartree_response_rel_RMSE"] for r in per_seed], dtype=float)
        material_rows.append(
            {
                "material_id": mid,
                "formula": str(full.loc[full.material_id == mid, "formula"].iloc[0]),
                "epsilon": epsilon_frozen,
                "hartree_qsq_response_scale_rel_RMSE": float(np.max(responses)),
                "hartree_qsq_response_median_rel_RMSE": float(np.median(responses)),
                "hartree_float32_roundtrip_rel_RMSE": f32_rel_rmse,
                "V_orig_rms": v0_rms,
                "npoints": int(rho.size),
                "source_sha256": str(m.sha256),
            }
        )

    seeds_df = pd.DataFrame(seed_rows)
    mats = pd.DataFrame(material_rows)
    seeds_df.to_csv(out / "hartree_qsq_per_seed.csv", index=False)
    mats.to_csv(out / "hartree_qsq_material_summary.csv", index=False)

    joined = full.merge(
        mats[["material_id", "hartree_qsq_response_scale_rel_RMSE"]],
        on="material_id",
        how="left",
        validate="many_to_one",
    )
    if joined["hartree_qsq_response_scale_rel_RMSE"].isna().any():
        raise RuntimeError("missing Hartree QSQ scale after join")

    cert_rows = []
    contract_rows = []
    for tau in TAUS:
        z = joined.copy()
        z["tau_rel_RMSE"] = tau
        z["eligible_hartree_qsq"] = z["hartree_qsq_response_scale_rel_RMSE"] < tau
        z["certified_hartree"] = z["eligible_hartree_qsq"] & (z["potential_rel_RMSE"] < tau)
        cert_rows.append(z)

        eligible = z[z["eligible_hartree_qsq"]]
        certified = z[z["certified_hartree"]]
        best = (
            certified.groupby("material_id", as_index=False)["compression_ratio_reproduced"]
            .max()
            .rename(columns={"compression_ratio_reproduced": "best_certified_compression_ratio"})
        )
        contract_rows.append(
            {
                "tau_rel_RMSE": tau,
                "eligible_materials": int(mats.loc[mats.hartree_qsq_response_scale_rel_RMSE < tau, "material_id"].nunique()),
                "eligible_rows": int(len(eligible)),
                "certified_rows": int(len(certified)),
                "materials_with_certified_point": int(best["material_id"].nunique()) if len(best) else 0,
                "best_certified_cr_median": float(best.best_certified_compression_ratio.median()) if len(best) else np.nan,
                "best_certified_cr_min": float(best.best_certified_compression_ratio.min()) if len(best) else np.nan,
                "best_certified_cr_max": float(best.best_certified_compression_ratio.max()) if len(best) else np.nan,
                "nontrivial_row_classification": bool(len(eligible) > 0 and 0 < len(certified) < len(eligible)),
            }
        )

    cert = pd.concat(cert_rows, ignore_index=True)
    contracts = pd.DataFrame(contract_rows)
    cert.to_csv(out / "hartree_certification_rows.csv", index=False)
    contracts.to_csv(out / "hartree_contract_summary.csv", index=False)

    contrast = mats.merge(
        full[["material_id", "stability_floor_A1_e"]].drop_duplicates("material_id"),
        on="material_id",
        how="left",
        validate="one_to_one",
    ).merge(
        mono[
            [
                "material_id",
                "potential_monotone_nondecreasing",
                "potential_loglog_R2",
                "bader_monotone_nondecreasing",
                "bader_loglog_R2",
            ]
        ],
        on="material_id",
        how="left",
        validate="one_to_one",
    )
    contrast.to_csv(out / "operator_contrast.csv", index=False)

    monotone_count = int(sum(as_bool(x) for x in contrast["potential_monotone_nondecreasing"]))
    median_r2 = float(pd.to_numeric(contrast["potential_loglog_R2"], errors="coerce").median())
    reference_scale_max = float(mats["hartree_qsq_response_scale_rel_RMSE"].max())
    nontrivial_contract_exists = bool(contracts["nontrivial_row_classification"].map(as_bool).any())

    criteria = {
        "all_materials_accounted": len(mats) == 12 and len(seeds_df) == 12 * len(SEEDS),
        "reference_scale_below_prespecified_ceiling": reference_scale_max < MAX_REFERENCE_SCALE_FOR_GO,
        "existing_hartree_monotone_materials_at_least_10_of_12": monotone_count >= MIN_MONOTONE_MATERIALS_FOR_GO,
        "existing_hartree_median_loglog_R2_at_least_0_99": median_r2 >= MIN_MEDIAN_LOGLOG_R2_FOR_GO,
        "at_least_one_nontrivial_contract": nontrivial_contract_exists,
    }
    status = "GO_TO_FULL_POPULATION" if all(criteria.values()) else "NO_GO"

    summary = {
        "status": status,
        "scope": "12-material Hartree-QSQ generality pilot; no new DFT; ZFP reconstruction ladder only",
        "seeds": list(SEEDS),
        "tau_rel_RMSE": list(TAUS),
        "rng": "numpy.random.Generator(PCG64(seed)); reset independently for each material/seed",
        "reference_response_metric": "RMS(V(noise))/RMS(V(reference))",
        "material_response_scale": "max over five seed responses",
        "go_criteria": criteria,
        "diagnostics": {
            "materials": int(len(mats)),
            "seed_measurements": int(len(seeds_df)),
            "reference_scale_min": float(mats.hartree_qsq_response_scale_rel_RMSE.min()),
            "reference_scale_median": float(mats.hartree_qsq_response_scale_rel_RMSE.median()),
            "reference_scale_max": reference_scale_max,
            "hartree_monotone_materials": monotone_count,
            "hartree_median_loglog_R2": median_r2,
            "bader_unstable_materials_at_1e-3_e": int(
                (contrast["stability_floor_A1_e"].astype(float) >= 1e-3).sum()
            ),
        },
        "input_sha256": {
            str(full_path.relative_to(REPO)): sha256(full_path),
            str(mono_path.relative_to(REPO)): sha256(mono_path),
            str(old_qsq_path.relative_to(REPO)): sha256(old_qsq_path),
            str(meta_path.relative_to(REPO)): sha256(meta_path),
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    hashes = []
    for p in sorted(out.iterdir()):
        if p.is_file():
            hashes.append(f"{sha256(p)}  {p.name}")
    (out / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")

    print("HARTREE_QSQ_PIPELINE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
