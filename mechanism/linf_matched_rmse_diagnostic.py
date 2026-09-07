#!/usr/bin/env python3
"""L-infinity-only matching diagnostic with RMSE balance audit.

Implements protocol/LINF_MATCHED_RMSE_DIAGNOSTIC_V0_1.md.
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
OUTDIR = ROOT / "mechanism" / "linf_matched_rmse_diagnostic_v0_1"
CALIPERS = (0.05, 0.10, 0.20, 0.30)
PRIMARY = 0.10
PAIRS = (("ZFP", "SZ3"), ("ZFP", "SPERR"), ("SZ3", "SPERR"))
BOOTSTRAP_DRAWS = 5000
MASTER_SEED = "20260907"
ERROR_FLOOR = 1e-15


def as_bool(x: Any) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes"}


def finite_positive(x: Any) -> bool:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v) and v > 0


def qtile(values: Iterable[float], q: float) -> float | None:
    xs = sorted(float(v) for v in values)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    p = (len(xs) - 1) * q
    lo, hi = math.floor(p), math.ceil(p)
    if lo == hi:
        return xs[lo]
    f = p - lo
    return xs[lo] * (1 - f) + xs[hi] * f


def bootstrap_median(log_values: list[float], label: str) -> tuple[float | None, float | None]:
    if not log_values:
        return None, None
    if len(log_values) == 1:
        return log_values[0], log_values[0]
    seed = int.from_bytes(hashlib.sha256((MASTER_SEED + "|" + label).encode()).digest()[:8], "big")
    rng = random.Random(seed)
    n = len(log_values)
    reps = []
    for _ in range(BOOTSTRAP_DRAWS):
        reps.append(statistics.median(log_values[rng.randrange(n)] for _ in range(n)))
    return qtile(reps, 0.025), qtile(reps, 0.975)


def geomedian(values: list[float]) -> float:
    return math.exp(statistics.median(math.log(v) for v in values if v > 0 and math.isfinite(v)))


def read_rows() -> list[dict[str, Any]]:
    rows = []
    with INPUT.open(newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "material_id", "corpus", "codec", "nominal_tolerance_relative",
            "realized_Linf", "rmse", "Bader_error_resolved_e", "compression_ratio",
            "bound_respected",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"missing columns {sorted(missing)}")
        for row_index, r in enumerate(reader):
            codec = r["codec"].strip().upper()
            if r["corpus"] not in {"dev_bulk", "dev_slab"} or codec not in {"ZFP", "SZ3", "SPERR"}:
                continue
            if not as_bool(r["bound_respected"]):
                continue
            if not all(finite_positive(r[k]) for k in ("realized_Linf", "rmse", "compression_ratio")):
                continue
            try:
                berr = float(r["Bader_error_resolved_e"])
            except (TypeError, ValueError):
                continue
            if not math.isfinite(berr) or berr < 0:
                continue
            rows.append({
                "row_index": row_index,
                "material_id": r["material_id"],
                "corpus": r["corpus"],
                "codec": codec,
                "tol": float(r["nominal_tolerance_relative"]),
                "linf": float(r["realized_Linf"]),
                "rmse": float(r["rmse"]),
                "error": max(berr, ERROR_FLOOR),
                "cr": float(r["compression_ratio"]),
            })
    return rows


def match(a_rows: list[dict[str, Any]], b_rows: list[dict[str, Any]], caliper: float):
    candidates = []
    for ia, a in enumerate(a_rows):
        la = math.log10(a["linf"])
        for ib, b in enumerate(b_rows):
            d = abs(la - math.log10(b["linf"]))
            if d <= caliper:
                dtol = abs(math.log10(a["tol"]) - math.log10(b["tol"]))
                candidates.append((d, dtol, max(a["tol"], b["tol"]), a["row_index"], b["row_index"], ia, ib))
    candidates.sort()
    used_a, used_b, out = set(), set(), []
    for d, _dtol, _maxtol, _ra, _rb, ia, ib in candidates:
        if ia in used_a or ib in used_b:
            continue
        used_a.add(ia); used_b.add(ib)
        out.append((a_rows[ia], b_rows[ib], d))
    return out


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def fmt(x: float | None) -> str:
    if x is None or not math.isfinite(x):
        return "NA"
    return f"{x:.3g}"


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in read_rows():
        grouped[row["material_id"]][row["codec"]].append(row)
    for by_codec in grouped.values():
        for codec in by_codec:
            by_codec[codec].sort(key=lambda r: (r["tol"], r["row_index"]))

    pair_rows = []
    material_rows = []
    for caliper in CALIPERS:
        for codec_a, codec_b in PAIRS:
            for mid in sorted(grouped):
                a_rows, b_rows = grouped[mid].get(codec_a, []), grouped[mid].get(codec_b, [])
                if not a_rows or not b_rows:
                    continue
                matched = match(a_rows, b_rows, caliper)
                if not matched:
                    continue
                err, rmse, linf, cr, shape = [], [], [], [], []
                for pair_index, (a, b, d) in enumerate(matched):
                    er = a["error"] / b["error"]
                    rr = a["rmse"] / b["rmse"]
                    lr = a["linf"] / b["linf"]
                    crv = a["cr"] / b["cr"]
                    sf = (a["rmse"] / a["linf"]) / (b["rmse"] / b["linf"])
                    err.append(er); rmse.append(rr); linf.append(lr); cr.append(crv); shape.append(sf)
                    pair_rows.append({
                        "caliper_dex": caliper, "codec_a": codec_a, "codec_b": codec_b,
                        "material_id": mid, "corpus": a["corpus"], "pair_index": pair_index,
                        "tol_a": a["tol"], "tol_b": b["tol"], "d_log10_linf": d,
                        "linf_a": a["linf"], "linf_b": b["linf"], "rmse_a": a["rmse"], "rmse_b": b["rmse"],
                        "error_a": a["error"], "error_b": b["error"],
                        "error_ratio_a_over_b": er, "rmse_ratio_a_over_b": rr,
                        "linf_ratio_a_over_b": lr, "compression_ratio_a_over_b": crv,
                        "shape_factor_ratio_a_over_b": sf,
                    })
                material_rows.append({
                    "caliper_dex": caliper, "codec_a": codec_a, "codec_b": codec_b,
                    "material_id": mid, "corpus": a_rows[0]["corpus"], "n_pairs": len(matched),
                    "material_error_ratio": geomedian(err), "material_rmse_ratio": geomedian(rmse),
                    "material_linf_ratio": geomedian(linf), "material_compression_ratio": geomedian(cr),
                    "material_shape_factor_ratio": geomedian(shape),
                })

    summary = []
    for caliper in CALIPERS:
        for codec_a, codec_b in PAIRS:
            sub = [r for r in material_rows if r["caliper_dex"] == caliper and r["codec_a"] == codec_a and r["codec_b"] == codec_b]
            pair_sub = [r for r in pair_rows if r["caliper_dex"] == caliper and r["codec_a"] == codec_a and r["codec_b"] == codec_b]
            out: dict[str, Any] = {
                "caliper_dex": caliper, "primary": caliper == PRIMARY,
                "codec_a": codec_a, "codec_b": codec_b,
                "n_materials": len(sub), "n_matched_pairs": len(pair_sub),
            }
            for field, label in (
                ("material_error_ratio", "error"),
                ("material_rmse_ratio", "rmse"),
                ("material_linf_ratio", "linf"),
                ("material_compression_ratio", "compression"),
                ("material_shape_factor_ratio", "shape"),
            ):
                logs = [math.log(float(r[field])) for r in sub]
                if logs:
                    point_log = statistics.median(logs)
                    lo, hi = bootstrap_median(logs, f"{caliper}|{codec_a}|{codec_b}|{label}")
                    out[label + "_ratio"] = math.exp(point_log)
                    out[label + "_ci_low"] = math.exp(lo)
                    out[label + "_ci_high"] = math.exp(hi)
                else:
                    out[label + "_ratio"] = out[label + "_ci_low"] = out[label + "_ci_high"] = None
            rmse_imbalanced = (
                out["rmse_ci_low"] is not None
                and (out["rmse_ci_high"] < 1 or out["rmse_ci_low"] > 1)
            )
            out["rmse_ci_excludes_1"] = rmse_imbalanced
            summary.append(out)

    write_csv(OUTDIR / "matched_pairs.csv", pair_rows)
    write_csv(OUTDIR / "material_effects.csv", material_rows)
    write_csv(OUTDIR / "summary.csv", summary)

    lines = [
        "# L-infinity-matched RMSE balance diagnostic v0.1", "",
        "Frozen input: `benchmark/master_benchmark_full.csv` (blob `633c7b2ee1b9b800382a5d0d9cfbdc9e1dc793b7`).", "",
        "A 95% CI for RMSE A/B that excludes 1 means the L-infinity-only matched comparison remains scalar-amplitude imbalanced.", "",
        "| caliper | contrast | materials | pairs | Bader error A/B [95% CI] | matched L-inf A/B | matched RMSE A/B [95% CI] | shape-factor A/B | RMSE balanced? |", 
        "|---:|---|---:|---:|---|---:|---|---:|---|",
    ]
    for r in summary:
        balanced = "yes" if not r["rmse_ci_excludes_1"] else "no"
        lines.append(
            f"| {r['caliper_dex']:.2f} | {r['codec_a']}/{r['codec_b']} | {r['n_materials']} | {r['n_matched_pairs']} | "
            f"{fmt(r['error_ratio'])} [{fmt(r['error_ci_low'])}, {fmt(r['error_ci_high'])}] | {fmt(r['linf_ratio'])} | "
            f"{fmt(r['rmse_ratio'])} [{fmt(r['rmse_ci_low'])}, {fmt(r['rmse_ci_high'])}] | {fmt(r['shape_ratio'])} | {balanced} |"
        )
    lines += ["", "## Primary 0.10-dex interpretation", ""]
    primary = [r for r in summary if r["caliper_dex"] == PRIMARY]
    for r in primary:
        if r["n_materials"] == 0:
            lines.append(f"- **{r['codec_a']}/{r['codec_b']}**: no common support at this caliper.")
        elif r["rmse_ci_excludes_1"]:
            lines.append(
                f"- **{r['codec_a']}/{r['codec_b']}**: RMSE remains imbalanced after L-infinity matching "
                f"({fmt(r['rmse_ratio'])}, 95% CI {fmt(r['rmse_ci_low'])}–{fmt(r['rmse_ci_high'])}); the residual Bader contrast cannot be uniquely assigned to spatial geometry."
            )
        else:
            lines.append(
                f"- **{r['codec_a']}/{r['codec_b']}**: RMSE is not detectably imbalanced at the material level "
                f"({fmt(r['rmse_ratio'])}, 95% CI {fmt(r['rmse_ci_low'])}–{fmt(r['rmse_ci_high'])})."
            )
    (OUTDIR / "LINF_MATCHED_RMSE_DIAGNOSTIC_REPORT.md").write_text("\n".join(lines) + "\n")
    for r in primary:
        print(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
