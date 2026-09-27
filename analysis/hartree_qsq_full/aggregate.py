#!/usr/bin/env python3
"""Aggregate full-population Hartree-QSQ shards and apply frozen GO criteria."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

TAUS = (1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3)
PRIMARY_TAU = 1e-6
CODECS = ("ZFP", "SZ3", "SPERR")
PAIRS = (("ZFP", "SZ3"), ("ZFP", "SPERR"), ("SZ3", "SPERR"))
MATCH_CALIPER_DEX = 0.10
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


def bool_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().isin(["true", "1", "yes", "t"])


def loglog_fit(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    if int(m.sum()) < 3:
        return np.nan, np.nan
    lx = np.log10(x[m])
    ly = np.log10(y[m])
    p = np.polyfit(lx, ly, 1)
    pred = np.polyval(p, lx)
    ss = float(np.sum((ly - ly.mean()) ** 2))
    r2 = 1.0 - float(np.sum((ly - pred) ** 2)) / ss if ss > 0 else np.nan
    return float(p[0]), float(r2)


def monotone_non_decreasing(y: np.ndarray) -> bool:
    y = np.asarray(y, float)
    if len(y) < 2:
        return True
    tol = np.maximum(1e-18, 1e-8 * np.maximum(y[:-1], y[1:]))
    return bool(np.all(np.diff(y) >= -tol))


def dedupe_series(g: pd.DataFrame) -> pd.DataFrame:
    z = g.copy()
    z["_abs_key"] = z["nominal_tolerance_absolute"].astype(float).map(lambda v: round(math.log10(v), 13) if v > 0 else v)
    z = z.sort_values(["reproduced_realized_Linf", "frozen_row_index_within_material"])
    z = z.drop_duplicates("_abs_key", keep="first")
    return z.drop(columns="_abs_key")


def greedy_match(a: pd.DataFrame, b: pd.DataFrame, caliper: float) -> list[tuple[pd.Series, pd.Series, float]]:
    aa = a.reset_index(drop=False)
    bb = b.reset_index(drop=False)
    cand: list[tuple[float, int, int, int, int]] = []
    for ia, ra in aa.iterrows():
        la = math.log10(float(ra["reproduced_realized_Linf"]))
        for ib, rb in bb.iterrows():
            lb = math.log10(float(rb["reproduced_realized_Linf"]))
            d = abs(la - lb)
            if d <= caliper + 1e-15:
                cand.append((d, int(ra["index"]), int(rb["index"]), ia, ib))
    cand.sort()
    used_a: set[int] = set()
    used_b: set[int] = set()
    out = []
    for d, _, _, ia, ib in cand:
        if ia in used_a or ib in used_b:
            continue
        used_a.add(ia)
        used_b.add(ib)
        out.append((aa.iloc[ia], bb.iloc[ib], d))
    return out


def qtile(vals: list[float], q: float) -> float:
    a = np.asarray([v for v in vals if math.isfinite(v)], dtype=float)
    return float(np.quantile(a, q)) if len(a) else np.nan


def material_bootstrap_ratio(material_logs: list[float]) -> tuple[float, float, float]:
    vals = np.asarray([v for v in material_logs if math.isfinite(v)], dtype=float)
    if not len(vals):
        return np.nan, np.nan, np.nan
    center = float(10 ** np.median(vals))
    rng = np.random.default_rng(BOOT_SEED)
    boots = np.empty(BOOT_REPS, dtype=float)
    for i in range(BOOT_REPS):
        sample = rng.choice(vals, size=len(vals), replace=True)
        boots[i] = 10 ** np.median(sample)
    return center, float(np.quantile(boots, .025)), float(np.quantile(boots, .975))


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

    manifests = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.rglob("manifest_shard_*.json"))]
    if not manifests:
        raise RuntimeError("no shard manifests")

    planned = [m for man in manifests for m in man["materials_planned"]]
    if len(planned) != len(set(planned)):
        raise RuntimeError("duplicate material assignment across shards")
    if len(planned) != 254:
        raise RuntimeError(f"planned material accounting drift: {len(planned)} != 254")

    qsq = read_many(root, "hartree_qsq_per_seed_shard_*.csv")
    rows = read_many(root, "hartree_codec_rows_shard_*.csv")
    try:
        failures = read_many(root, "failures_shard_*.csv")
    except RuntimeError:
        failures = pd.DataFrame(columns=["material_id", "stage", "error_type", "error"])

    if len(qsq):
        qsq.to_csv(out / "hartree_qsq_per_seed.csv", index=False)
    rows.to_csv(out / "hartree_codec_rows.csv", index=False)
    failures.to_csv(out / "failures.csv", index=False)

    # Material-level QSQ summary.
    if len(qsq):
        material = (
            qsq.groupby(["material_id", "corpus", "system_type", "source", "formula"], as_index=False)
            .agg(
                qsq_seed_measurements=("seed", "count"),
                epsilon=("epsilon", "first"),
                hartree_qsq_response_scale_rel_RMSE=("hartree_response_rel_RMSE", "max"),
                hartree_qsq_response_median_rel_RMSE=("hartree_response_rel_RMSE", "median"),
                npoints=("npoints", "first"),
                source_sha256=("source_sha256", "first"),
            )
        )
    else:
        material = pd.DataFrame()

    complete_seed_set = len(material) and bool((material["qsq_seed_measurements"] == 5).all())
    material.to_csv(out / "hartree_qsq_material_summary.csv", index=False)

    rows["scientific_reproduction_gate_pass"] = bool_series(rows["scientific_reproduction_gate_pass"])
    valid = rows[rows["scientific_reproduction_gate_pass"]].copy()
    valid = valid[np.isfinite(pd.to_numeric(valid["reproduced_realized_Linf"], errors="coerce"))]
    valid = valid[np.isfinite(pd.to_numeric(valid["hartree_error_rel_RMSE"], errors="coerce"))]
    valid = valid[(valid["reproduced_realized_Linf"].astype(float) > 0) & (valid["hartree_error_rel_RMSE"].astype(float) > 0)]

    # Series-level smoothness.
    mono_rows: list[dict[str, Any]] = []
    for (mid, codec), g in valid.groupby(["material_id", "codec"]):
        z = dedupe_series(g)
        x = z["reproduced_realized_Linf"].astype(float).to_numpy()
        y = z["hartree_error_rel_RMSE"].astype(float).to_numpy()
        order = np.argsort(x)
        x = x[order]
        y = y[order]
        slope, r2 = loglog_fit(x, y)
        meta = z.iloc[0]
        mono_rows.append({
            "material_id": mid,
            "codec": codec,
            "system_type": meta["system_type"],
            "corpus": meta["corpus"],
            "n_unique_rows": len(z),
            "monotone_nondecreasing": monotone_non_decreasing(y),
            "loglog_slope": slope,
            "loglog_R2": r2,
            "linf_span_decades": float(np.log10(x.max() / x.min())) if len(x) > 1 else np.nan,
            "hartree_error_dynamic_range": float(y.max() / y.min()) if len(y) and y.min() > 0 else np.nan,
        })
    mono = pd.DataFrame(mono_rows)
    mono.to_csv(out / "material_codec_monotonicity.csv", index=False)

    series_summary_rows = []
    for codec in CODECS:
        g = mono[(mono["codec"] == codec) & (mono["n_unique_rows"] >= 4)].copy()
        g["monotone_nondecreasing"] = bool_series(g["monotone_nondecreasing"])
        series_summary_rows.append({
            "codec": codec,
            "n_material_series_ge4": len(g),
            "monotone_fraction": float(g["monotone_nondecreasing"].mean()) if len(g) else np.nan,
            "median_loglog_R2": float(pd.to_numeric(g["loglog_R2"], errors="coerce").median()) if len(g) else np.nan,
            "median_loglog_slope": float(pd.to_numeric(g["loglog_slope"], errors="coerce").median()) if len(g) else np.nan,
            "p10_loglog_slope": float(pd.to_numeric(g["loglog_slope"], errors="coerce").quantile(.10)) if len(g) else np.nan,
            "p90_loglog_slope": float(pd.to_numeric(g["loglog_slope"], errors="coerce").quantile(.90)) if len(g) else np.nan,
        })
    series_summary = pd.DataFrame(series_summary_rows)
    series_summary.to_csv(out / "codec_smoothness_summary.csv", index=False)

    # Contract qualification/certification summaries.
    contract_rows: list[dict[str, Any]] = []
    valid_contract = valid.merge(
        material[["material_id", "hartree_qsq_response_scale_rel_RMSE"]],
        on="material_id", how="left", validate="many_to_one", suffixes=("", "_material")
    )
    for tau in TAUS:
        m_elig = material["hartree_qsq_response_scale_rel_RMSE"].astype(float) < tau
        eligible_materials = set(material.loc[m_elig, "material_id"].astype(str))
        for scope_type, scope_values in [
            ("ALL", ["ALL"]),
            ("codec", list(CODECS)),
            ("system_type", sorted(valid_contract["system_type"].dropna().astype(str).unique())),
        ]:
            for scope_value in scope_values:
                z = valid_contract
                if scope_type == "codec":
                    z = z[z["codec"] == scope_value]
                elif scope_type == "system_type":
                    z = z[z["system_type"].astype(str) == scope_value]
                z = z.copy()
                z["eligible"] = z["material_id"].astype(str).isin(eligible_materials)
                z["certified"] = z["eligible"] & (z["hartree_error_rel_RMSE"].astype(float) < tau)
                ez = z[z["eligible"]]
                cz = z[z["certified"]]
                best = (
                    cz.groupby(["material_id", "codec"], as_index=False)["reproduced_compression_ratio"]
                    .max()
                    if len(cz) else pd.DataFrame(columns=["material_id", "codec", "reproduced_compression_ratio"])
                )
                contract_rows.append({
                    "tau_rel_RMSE": tau,
                    "scope_type": scope_type,
                    "scope_value": scope_value,
                    "eligible_materials_global": len(eligible_materials),
                    "eligible_rows_in_scope": int(len(ez)),
                    "certified_rows_in_scope": int(len(cz)),
                    "materials_with_certified_point": int(cz["material_id"].nunique()) if len(cz) else 0,
                    "material_codec_pairs_with_certified_point": int(len(best)),
                    "best_certified_cr_median": float(best["reproduced_compression_ratio"].median()) if len(best) else np.nan,
                    "best_certified_cr_p10": float(best["reproduced_compression_ratio"].quantile(.10)) if len(best) else np.nan,
                    "best_certified_cr_p90": float(best["reproduced_compression_ratio"].quantile(.90)) if len(best) else np.nan,
                    "nontrivial_row_classification": bool(len(ez) > 0 and 0 < len(cz) < len(ez)),
                })
    contracts = pd.DataFrame(contract_rows)
    contracts.to_csv(out / "hartree_contract_summary.csv", index=False)

    # Matched-realized-Linf codec control.
    matched_rows: list[dict[str, Any]] = []
    by_material: dict[str, dict[str, pd.DataFrame]] = defaultdict(dict)
    for mid, gm in valid.groupby("material_id"):
        for codec, gc in gm.groupby("codec"):
            by_material[str(mid)][str(codec)] = dedupe_series(gc)

    for ca, cb in PAIRS:
        for mid, groups in by_material.items():
            if ca not in groups or cb not in groups:
                continue
            a = groups[ca]
            b = groups[cb]
            a = a[(a["reproduced_realized_Linf"].astype(float) > 0)]
            b = b[(b["reproduced_realized_Linf"].astype(float) > 0)]
            for ra, rb, dist in greedy_match(a, b, MATCH_CALIPER_DEX):
                ha = float(ra["hartree_error_rel_RMSE"])
                hb = float(rb["hartree_error_rel_RMSE"])
                ba = pd.to_numeric(pd.Series([ra.get("frozen_Bader_error_resolved_e")]), errors="coerce").iloc[0]
                bb = pd.to_numeric(pd.Series([rb.get("frozen_Bader_error_resolved_e")]), errors="coerce").iloc[0]
                matched_rows.append({
                    "material_id": mid,
                    "system_type": ra["system_type"],
                    "codec_a": ca,
                    "codec_b": cb,
                    "distance_dex": dist,
                    "linf_a": float(ra["reproduced_realized_Linf"]),
                    "linf_b": float(rb["reproduced_realized_Linf"]),
                    "hartree_error_a": ha,
                    "hartree_error_b": hb,
                    "hartree_ratio_a_over_b": ha / hb if hb > 0 else np.nan,
                    "hartree_abs_log10_ratio": abs(math.log10(ha / hb)) if ha > 0 and hb > 0 else np.nan,
                    "bader_error_a": float(ba) if pd.notna(ba) else np.nan,
                    "bader_error_b": float(bb) if pd.notna(bb) else np.nan,
                    "bader_ratio_a_over_b": float(ba / bb) if pd.notna(ba) and pd.notna(bb) and ba > 0 and bb > 0 else np.nan,
                    "bader_abs_log10_ratio": abs(math.log10(float(ba / bb))) if pd.notna(ba) and pd.notna(bb) and ba > 0 and bb > 0 else np.nan,
                })
    matched = pd.DataFrame(matched_rows)
    matched.to_csv(out / "matched_realized_linf_pairs_0p10dex.csv", index=False)

    matched_summary_rows = []
    if len(matched):
        for (ca, cb), g in matched.groupby(["codec_a", "codec_b"]):
            hlogs_by_mat = g.groupby("material_id")["hartree_ratio_a_over_b"].apply(
                lambda s: float(np.median(np.log10(pd.to_numeric(s, errors="coerce").dropna().astype(float))))
                if len(pd.to_numeric(s, errors="coerce").dropna()) else np.nan
            )
            hcenter, hlo, hhi = material_bootstrap_ratio([float(x) for x in hlogs_by_mat.dropna()])
            bvalid = g[np.isfinite(pd.to_numeric(g["bader_ratio_a_over_b"], errors="coerce"))].copy()
            blogs_by_mat = bvalid.groupby("material_id")["bader_ratio_a_over_b"].apply(
                lambda s: float(np.median(np.log10(pd.to_numeric(s, errors="coerce").dropna().astype(float))))
                if len(pd.to_numeric(s, errors="coerce").dropna()) else np.nan
            ) if len(bvalid) else pd.Series(dtype=float)
            bcenter, blo, bhi = material_bootstrap_ratio([float(x) for x in blogs_by_mat.dropna()])
            matched_summary_rows.append({
                "codec_a": ca,
                "codec_b": cb,
                "caliper_dex": MATCH_CALIPER_DEX,
                "n_pairs": len(g),
                "n_materials": g["material_id"].nunique(),
                "hartree_material_median_ratio_a_over_b": hcenter,
                "hartree_ratio_ci_low": hlo,
                "hartree_ratio_ci_high": hhi,
                "hartree_median_abs_log10_ratio": float(pd.to_numeric(g["hartree_abs_log10_ratio"], errors="coerce").median()),
                "bader_n_pairs": len(bvalid),
                "bader_n_materials": bvalid["material_id"].nunique() if len(bvalid) else 0,
                "bader_material_median_ratio_a_over_b": bcenter,
                "bader_ratio_ci_low": blo,
                "bader_ratio_ci_high": bhi,
                "bader_median_abs_log10_ratio": float(pd.to_numeric(bvalid["bader_abs_log10_ratio"], errors="coerce").median()) if len(bvalid) else np.nan,
            })
    matched_summary = pd.DataFrame(matched_summary_rows)
    matched_summary.to_csv(out / "matched_realized_linf_summary.csv", index=False)

    # Frozen GO criteria.
    primary_eligible_count = int((material["hartree_qsq_response_scale_rel_RMSE"].astype(float) < PRIMARY_TAU).sum()) if len(material) else 0
    primary_eligible_fraction = primary_eligible_count / 254.0

    codec_criteria: dict[str, Any] = {}
    for codec in CODECS:
        s = series_summary[series_summary["codec"] == codec].iloc[0]
        codec_criteria[codec] = {
            "monotone_fraction_at_least_0_80": bool(float(s["monotone_fraction"]) >= 0.80),
            "median_R2_at_least_0_90": bool(float(s["median_loglog_R2"]) >= 0.90),
            "median_slope_in_0_70_to_1_30": bool(0.70 <= float(s["median_loglog_slope"]) <= 1.30),
        }

    nontrivial_contract = bool(contracts["nontrivial_row_classification"].map(lambda x: str(x).lower() in {"true", "1"}).any())
    material_failure_ids = set(failures["material_id"].astype(str)) if len(failures) and "material_id" in failures else set()
    source_failure_ids = set(
        failures.loc[failures["stage"].astype(str) == "source_or_reference", "material_id"].astype(str)
    ) if len(failures) and "stage" in failures else set()

    criteria = {
        "all_254_materials_planned_accounted": len(planned) == 254,
        "all_successful_reference_materials_have_five_seed_measurements": bool(complete_seed_set),
        "primary_1e-6_eligibility_fraction_at_least_0_90": bool(primary_eligible_fraction >= 0.90),
        "per_codec_smoothness_criteria": codec_criteria,
        "at_least_one_nontrivial_contract": nontrivial_contract,
    }
    all_codec_ok = all(all(v.values()) for v in codec_criteria.values())
    go = (
        criteria["all_254_materials_planned_accounted"]
        and criteria["all_successful_reference_materials_have_five_seed_measurements"]
        and criteria["primary_1e-6_eligibility_fraction_at_least_0_90"]
        and all_codec_ok
        and criteria["at_least_one_nontrivial_contract"]
    )
    status = "GO_FULL_POPULATION_GENERALITY_SUPPORTED" if go else "NO_GO"

    summary = {
        "status": status,
        "planned_materials": 254,
        "reference_complete_materials": int(material["material_id"].nunique()) if len(material) else 0,
        "materials_with_any_failure_record": len(material_failure_ids),
        "materials_with_source_or_reference_failure": len(source_failure_ids),
        "qsq_seed_rows": int(len(qsq)),
        "codec_rows_total": int(len(rows)),
        "codec_rows_scientific_gate_pass": int(len(valid)),
        "codec_rows_scientific_gate_fail": int(len(rows) - len(valid)),
        "primary_tau_rel_RMSE": PRIMARY_TAU,
        "primary_eligible_materials_conservative_denominator_254": primary_eligible_count,
        "primary_eligibility_fraction_conservative_denominator_254": primary_eligible_fraction,
        "criteria": criteria,
        "codec_smoothness": series_summary.to_dict(orient="records"),
        "matched_realized_linf": matched_summary.to_dict(orient="records"),
        "interpretation_boundary": (
            "This extension tests downstream-operator generality on the development cohort. "
            "It does not modify the frozen P1-P4 submission scope and the Hartree contract ladder "
            "is a numerical measurement contract, not a universal chemistry threshold."
        ),
    }
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Human-readable report.
    lines = [
        "# Full-population Hartree-QSQ generality study",
        "",
        f"Status: **{status}**",
        "",
        "## Accounting",
        "",
        f"- Planned materials: **254**",
        f"- Reference-complete materials: **{summary['reference_complete_materials']}**",
        f"- Five-seed Hartree-QSQ measurements: **{len(qsq)}**",
        f"- Reconstructed codec rows: **{len(rows)}**",
        f"- Scientific reproduction-gate pass rows: **{len(valid)}**",
        f"- Scientific reproduction-gate fail rows: **{len(rows)-len(valid)}**",
        f"- Materials with source/reference failure: **{len(source_failure_ids)}**",
        "",
        "## Primary Hartree-QSQ contract",
        "",
        f"At relative-RMSE tau = {PRIMARY_TAU:.0e}, **{primary_eligible_count}/254 = {primary_eligible_fraction:.1%}** of the planned development cohort is reference-qualified (missing reference measurements counted conservatively as not eligible).",
        "",
        "## Smoothness by codec",
        "",
        "| Codec | series (>=4 points) | monotone | median R2 | median slope | GO checks |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for _, r in series_summary.iterrows():
        c = codec_criteria[str(r["codec"])]
        lines.append(
            f"| {r['codec']} | {int(r['n_material_series_ge4'])} | {float(r['monotone_fraction']):.1%} | "
            f"{float(r['median_loglog_R2']):.3f} | {float(r['median_loglog_slope']):.3f} | "
            f"{'PASS' if all(c.values()) else 'FAIL'} |"
        )

    lines.extend([
        "",
        "## Matched realized L-infinity control",
        "",
        "Primary caliper: 0.10 dex, within material, without replacement.",
        "",
        "| Pair | matched pairs | materials | Hartree ratio A/B | Hartree median |log10 ratio| | Bader ratio A/B | Bader median |log10 ratio| |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for _, r in matched_summary.iterrows():
        lines.append(
            f"| {r['codec_a']}/{r['codec_b']} | {int(r['n_pairs'])} | {int(r['n_materials'])} | "
            f"{float(r['hartree_material_median_ratio_a_over_b']):.3f} "
            f"[{float(r['hartree_ratio_ci_low']):.3f}, {float(r['hartree_ratio_ci_high']):.3f}] | "
            f"{float(r['hartree_median_abs_log10_ratio']):.3f} | "
            f"{float(r['bader_material_median_ratio_a_over_b']):.3f} "
            f"[{float(r['bader_ratio_ci_low']):.3f}, {float(r['bader_ratio_ci_high']):.3f}] | "
            f"{float(r['bader_median_abs_log10_ratio']):.3f} |"
        )

    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "The study is an additive operator-generality extension. It does not automatically alter the frozen manuscript, P1-P4 evidence hierarchy, or submission artifacts.",
        "",
        "A GO means the pre-specified population-level numerical criteria were met; it does not make the Hartree relative-RMSE ladder a universal chemical tolerance.",
    ])
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Provenance hashes.
    hashes = []
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name != "SHA256SUMS.txt":
            hashes.append(f"{sha256(p)}  {p.name}")
    (out / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": status,
        "planned": 254,
        "reference_complete": summary["reference_complete_materials"],
        "codec_rows": len(rows),
        "gate_pass_rows": len(valid),
        "primary_eligible": primary_eligible_count,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
