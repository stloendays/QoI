#!/usr/bin/env python3
"""Preregistered dual-metric matching control for Figure 6.

See protocol/ERROR_GEOMETRY_CONTROL_V0_1_PREREGISTRATION.md.
This script is descriptive/mechanistic and does not alter Protocol A.1 or any
frozen external-confirmatory semantics.
"""
from __future__ import annotations

import csv
import hashlib
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "benchmark" / "master_benchmark_full.csv"
OUTDIR = ROOT / "mechanism" / "geometry_control_v0_1"
EXPECTED_GIT_BLOB = "633c7b2ee1b9b800382a5d0d9cfbdc9e1dc793b7"
CALIPERS = (0.05, 0.10, 0.20, 0.30)
PRIMARY_CALIPER = 0.10
BOOTSTRAP_DRAWS = 5000
MASTER_SEED_LABEL = "20260907"
PAIRS = (("ZFP", "SZ3"), ("ZFP", "SPERR"), ("SZ3", "SPERR"))
ERROR_FLOOR = 1e-15


def as_bool(x: Any) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes"}


def finite_positive(x: str) -> bool:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v) and v > 0.0


def qtile(values: Iterable[float], q: float) -> float | None:
    xs = sorted(float(x) for x in values)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    p = (len(xs) - 1) * q
    lo = int(math.floor(p))
    hi = int(math.ceil(p))
    if lo == hi:
        return xs[lo]
    f = p - lo
    return xs[lo] * (1.0 - f) + xs[hi] * f


def seed_for(label: str) -> int:
    h = hashlib.sha256((MASTER_SEED_LABEL + "|" + label).encode()).digest()
    return int.from_bytes(h[:8], "big")


def bootstrap_ci(values: list[float], label: str, statistic: str) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    if len(values) == 1:
        return values[0], values[0]
    rng = random.Random(seed_for(label))
    n = len(values)
    reps: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        if statistic == "median":
            reps.append(float(statistics.median(sample)))
        elif statistic == "mean":
            reps.append(float(statistics.fmean(sample)))
        else:
            raise ValueError(statistic)
    return qtile(reps, 0.025), qtile(reps, 0.975)


def read_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with INPUT.open(newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "material_id", "corpus", "codec", "nominal_tolerance_relative",
            "realized_Linf", "rmse", "Bader_error_resolved_e", "compression_ratio",
            "bound_respected", "eligible_A1_at_0.01", "certified_at_0.01",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Input missing required columns: {sorted(missing)}")
        for idx, raw in enumerate(reader):
            if raw["corpus"] not in {"dev_bulk", "dev_slab"}:
                continue
            if raw["codec"].strip().upper() not in {"ZFP", "SZ3", "SPERR"}:
                continue
            if not as_bool(raw["bound_respected"]):
                continue
            if not all(
                finite_positive(raw[k])
                for k in ("realized_Linf", "rmse", "compression_ratio")
            ):
                continue
            try:
                berr = float(raw["Bader_error_resolved_e"])
            except (TypeError, ValueError):
                continue
            if not math.isfinite(berr) or berr < 0:
                continue
            rows.append({
                "row_index": idx,
                "material_id": raw["material_id"],
                "corpus": raw["corpus"],
                "codec": raw["codec"].strip().upper(),
                "tol": float(raw["nominal_tolerance_relative"]),
                "linf": float(raw["realized_Linf"]),
                "rmse": float(raw["rmse"]),
                "error": max(berr, ERROR_FLOOR),
                "compression_ratio": float(raw["compression_ratio"]),
                "eligible_001": as_bool(raw["eligible_A1_at_0.01"]),
                "certified_001": as_bool(raw["certified_at_0.01"]),
            })
    return rows


def match_material(a_rows: list[dict[str, Any]], b_rows: list[dict[str, Any]], caliper: float):
    candidates: list[tuple[float, float, float, int, int, float, float]] = []
    for ia, a in enumerate(a_rows):
        la = math.log10(a["linf"])
        ra = math.log10(a["rmse"])
        for ib, b in enumerate(b_rows):
            d_inf = abs(la - math.log10(b["linf"]))
            d_rmse = abs(ra - math.log10(b["rmse"]))
            if d_inf <= caliper and d_rmse <= caliper:
                distance = math.sqrt((d_inf / caliper) ** 2 + (d_rmse / caliper) ** 2)
                # Deterministic tie breaking after scientific distance.
                candidates.append((
                    distance,
                    abs(math.log10(a["tol"]) - math.log10(b["tol"])),
                    max(a["tol"], b["tol"]),
                    ia,
                    ib,
                    d_inf,
                    d_rmse,
                ))
    candidates.sort()
    used_a: set[int] = set()
    used_b: set[int] = set()
    matched = []
    for distance, _dtol, _maxtol, ia, ib, d_inf, d_rmse in candidates:
        if ia in used_a or ib in used_b:
            continue
        used_a.add(ia)
        used_b.add(ib)
        matched.append((a_rows[ia], b_rows[ib], distance, d_inf, d_rmse))
    return matched


def geomedian(values: list[float]) -> float | None:
    xs = [v for v in values if math.isfinite(v) and v > 0]
    if not xs:
        return None
    return math.exp(statistics.median([math.log(v) for v in xs]))


def fmt(x: float | None, digits: int = 3) -> str:
    if x is None or not math.isfinite(x):
        return "NA"
    return f"{x:.{digits}g}"


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    rows = read_rows()
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["material_id"]][row["codec"]].append(row)
    for by_codec in grouped.values():
        for codec in by_codec:
            by_codec[codec].sort(key=lambda r: (r["tol"], r["row_index"]))

    pair_rows: list[dict[str, Any]] = []
    material_rows: list[dict[str, Any]] = []

    for caliper in CALIPERS:
        for codec_a, codec_b in PAIRS:
            for material_id in sorted(grouped):
                a_rows = grouped[material_id].get(codec_a, [])
                b_rows = grouped[material_id].get(codec_b, [])
                if not a_rows or not b_rows:
                    continue
                matched = match_material(a_rows, b_rows, caliper)
                if not matched:
                    continue
                errs: list[float] = []
                crs: list[float] = []
                linfs: list[float] = []
                rmses: list[float] = []
                cert_diffs: list[float] = []
                corpus = a_rows[0]["corpus"]
                for pair_index, (a, b, distance, d_inf, d_rmse) in enumerate(matched):
                    er = a["error"] / b["error"]
                    cr = a["compression_ratio"] / b["compression_ratio"]
                    lr = a["linf"] / b["linf"]
                    rr = a["rmse"] / b["rmse"]
                    jointly = bool(a["eligible_001"] and b["eligible_001"])
                    cert_diff = None
                    if jointly:
                        cert_diff = 100.0 * (int(a["certified_001"]) - int(b["certified_001"]))
                        cert_diffs.append(cert_diff)
                    errs.append(er); crs.append(cr); linfs.append(lr); rmses.append(rr)
                    pair_rows.append({
                        "caliper_dex": caliper,
                        "codec_a": codec_a,
                        "codec_b": codec_b,
                        "material_id": material_id,
                        "corpus": corpus,
                        "pair_index": pair_index,
                        "tol_a": a["tol"],
                        "tol_b": b["tol"],
                        "realized_linf_a": a["linf"],
                        "realized_linf_b": b["linf"],
                        "rmse_a": a["rmse"],
                        "rmse_b": b["rmse"],
                        "resolved_bader_error_a": a["error"],
                        "resolved_bader_error_b": b["error"],
                        "compression_ratio_a": a["compression_ratio"],
                        "compression_ratio_b": b["compression_ratio"],
                        "distance": distance,
                        "d_log10_linf": d_inf,
                        "d_log10_rmse": d_rmse,
                        "error_ratio_a_over_b": er,
                        "compression_ratio_a_over_b": cr,
                        "linf_ratio_a_over_b": lr,
                        "rmse_ratio_a_over_b": rr,
                        "jointly_eligible_tau_0.01": jointly,
                        "certification_difference_pp_a_minus_b": "" if cert_diff is None else cert_diff,
                    })
                material_rows.append({
                    "caliper_dex": caliper,
                    "codec_a": codec_a,
                    "codec_b": codec_b,
                    "material_id": material_id,
                    "corpus": corpus,
                    "n_pairs": len(matched),
                    "n_jointly_eligible_cert_pairs": len(cert_diffs),
                    "material_error_ratio_a_over_b": geomedian(errs),
                    "material_compression_ratio_a_over_b": geomedian(crs),
                    "material_linf_ratio_a_over_b": geomedian(linfs),
                    "material_rmse_ratio_a_over_b": geomedian(rmses),
                    "material_certification_difference_pp": statistics.fmean(cert_diffs) if cert_diffs else "",
                })

    summary_rows: list[dict[str, Any]] = []
    for caliper in CALIPERS:
        for codec_a, codec_b in PAIRS:
            subset = [r for r in material_rows if r["caliper_dex"] == caliper and r["codec_a"] == codec_a and r["codec_b"] == codec_b]
            pair_subset = [r for r in pair_rows if r["caliper_dex"] == caliper and r["codec_a"] == codec_a and r["codec_b"] == codec_b]
            error_logs = [math.log(float(r["material_error_ratio_a_over_b"])) for r in subset]
            cr_logs = [math.log(float(r["material_compression_ratio_a_over_b"])) for r in subset]
            linf_logs = [math.log(float(r["material_linf_ratio_a_over_b"])) for r in subset]
            rmse_logs = [math.log(float(r["material_rmse_ratio_a_over_b"])) for r in subset]
            cert_effects = [float(r["material_certification_difference_pp"]) for r in subset if r["material_certification_difference_pp"] != ""]

            def ratio_summary(logs: list[float], metric: str):
                if not logs:
                    return None, None, None
                point_log = statistics.median(logs)
                lo_log, hi_log = bootstrap_ci(logs, f"{caliper}|{codec_a}|{codec_b}|{metric}", "median")
                return math.exp(point_log), math.exp(lo_log), math.exp(hi_log)

            er, er_lo, er_hi = ratio_summary(error_logs, "error")
            cr, cr_lo, cr_hi = ratio_summary(cr_logs, "compression")
            lr, lr_lo, lr_hi = ratio_summary(linf_logs, "linf")
            rr, rr_lo, rr_hi = ratio_summary(rmse_logs, "rmse")
            if cert_effects:
                cert = statistics.fmean(cert_effects)
                cert_lo, cert_hi = bootstrap_ci(cert_effects, f"{caliper}|{codec_a}|{codec_b}|cert", "mean")
            else:
                cert = cert_lo = cert_hi = None

            summary_rows.append({
                "caliper_dex": caliper,
                "primary": caliper == PRIMARY_CALIPER,
                "codec_a": codec_a,
                "codec_b": codec_b,
                "n_materials": len(subset),
                "n_matched_row_pairs": len(pair_subset),
                "n_materials_with_joint_eligibility": len(cert_effects),
                "n_jointly_eligible_cert_pairs": sum(int(r["n_jointly_eligible_cert_pairs"]) for r in subset),
                "error_ratio": er,
                "error_ratio_ci_low": er_lo,
                "error_ratio_ci_high": er_hi,
                "fraction_materials_error_ratio_lt_1": (sum(float(r["material_error_ratio_a_over_b"]) < 1 for r in subset) / len(subset)) if subset else None,
                "compression_ratio_effect": cr,
                "compression_ratio_ci_low": cr_lo,
                "compression_ratio_ci_high": cr_hi,
                "matched_linf_ratio": lr,
                "matched_linf_ratio_ci_low": lr_lo,
                "matched_linf_ratio_ci_high": lr_hi,
                "matched_rmse_ratio": rr,
                "matched_rmse_ratio_ci_low": rr_lo,
                "matched_rmse_ratio_ci_high": rr_hi,
                "certification_difference_pp": cert,
                "certification_difference_pp_ci_low": cert_lo,
                "certification_difference_pp_ci_high": cert_hi,
            })

    def write_csv(path: Path, data: list[dict[str, Any]]):
        if not data:
            path.write_text("")
            return
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader(); w.writerows(data)

    write_csv(OUTDIR / "matched_pairs.csv", pair_rows)
    write_csv(OUTDIR / "material_effects.csv", material_rows)
    write_csv(OUTDIR / "summary.csv", summary_rows)

    primary = {(r["codec_a"], r["codec_b"]): r for r in summary_rows if r["caliper_dex"] == PRIMARY_CALIPER}
    z_s = primary.get(("ZFP", "SZ3"), {})
    z_p = primary.get(("ZFP", "SPERR"), {})
    supported = bool(
        z_s.get("error_ratio_ci_high") is not None and z_s["error_ratio_ci_high"] < 1
        and z_p.get("error_ratio_ci_high") is not None and z_p["error_ratio_ci_high"] < 1
    )

    lines = [
        "# Matched realized-L-infinity + RMSE control v0.1",
        "",
        "This report implements the frozen analysis in `protocol/ERROR_GEOMETRY_CONTROL_V0_1_PREREGISTRATION.md`.",
        "It is a development-corpus mechanistic sensitivity analysis and does not modify Protocol A.1 or the external confirmatory design.",
        "",
        f"**Primary decision rule:** {'SUPPORTED' if supported else 'NOT SUPPORTED'}.",
        "",
        "Allowed interpretation if supported: the residual ZFP chemical-fidelity advantage is not explained by realized L-infinity or RMSE alone. This analysis is not, by itself, causal proof of spatial error geometry.",
        "",
        "## Summary",
        "",
        "| caliper | contrast A/B | materials | pairs | Bader error A/B [95% CI] | matched L-inf A/B | matched RMSE A/B | compression A/B | certification A-B at 0.01 e (pp) |",
        "|---:|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for r in summary_rows:
        lines.append(
            f"| {r['caliper_dex']:.2f} | {r['codec_a']}/{r['codec_b']} | {r['n_materials']} | {r['n_matched_row_pairs']} | "
            f"{fmt(r['error_ratio'])} [{fmt(r['error_ratio_ci_low'])}, {fmt(r['error_ratio_ci_high'])}] | "
            f"{fmt(r['matched_linf_ratio'])} | {fmt(r['matched_rmse_ratio'])} | {fmt(r['compression_ratio_effect'])} | "
            f"{fmt(r['certification_difference_pp'])} [{fmt(r['certification_difference_pp_ci_low'])}, {fmt(r['certification_difference_pp_ci_high'])}] |"
        )
    lines += [
        "",
        "## Scope guard",
        "",
        "A residual after dual matching rules out two scalar summaries (max error and RMS error) as sufficient explanations. It does not uniquely identify spatial geometry because other distributional or spectral summaries are not fixed. The preregistered next mechanistic intervention is a within-residual spatial permutation that preserves the residual value multiset and therefore L-infinity, L1/L2, RMSE, mean and histogram while changing only spatial assignment (optionally within density strata).",
        "",
        "## Provenance",
        "",
        f"- Frozen input Git blob: `{EXPECTED_GIT_BLOB}`",
        f"- Primary caliper: `{PRIMARY_CALIPER}` dex on both realized L-infinity and RMSE",
        f"- Bootstrap: `{BOOTSTRAP_DRAWS}` material-level resamples",
        f"- Master seed label: `{MASTER_SEED_LABEL}`",
    ]
    (OUTDIR / "MATCHED_LINF_RMSE_REPORT.md").write_text("\n".join(lines) + "\n")
    print("primary_supported=", supported)
    for r in summary_rows:
        if r["caliper_dex"] == PRIMARY_CALIPER:
            print(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
