#!/usr/bin/env python3
"""Matched-realized-Linf analysis for the QoI benchmark.

Purpose
-------
Compare SZ3, ZFP and SPERR at *matched realized* pointwise perturbation rather
than merely at equal nominal tolerance. Matching is performed within material
on log10(realized_Linf), without replacement, with multiple calipers.

The script uses only the Python standard library so it can run reproducibly in
GitHub Actions without environment-specific dependencies.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

DATA = Path("benchmark/master_benchmark_full.csv")
OUT = Path("analysis/matched_realized_linf_v1")
OUT.mkdir(parents=True, exist_ok=True)

CODECS = ("zfp", "sz3", "sperr")
PAIR_ORDER = (("zfp", "sz3"), ("zfp", "sperr"), ("sz3", "sperr"))
CALIPERS = (0.05, 0.10, 0.20, 0.30)  # dex; 0.10 dex ~ 1.26x Linf mismatch
PRIMARY_CALIPER = 0.10
BOOT_REPS = 2000
SEED = 20260907


def finite_float(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def boolish(x):
    if x is None:
        return None
    s = str(x).strip().lower()
    if s in {"1", "true", "t", "yes", "y", "certified", "eligible"}:
        return True
    if s in {"0", "false", "f", "no", "n", "uncertified", "ineligible"}:
        return False
    return None


def qtile(values, q):
    vals = sorted(v for v in values if v is not None and math.isfinite(v))
    if not vals:
        return None
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    w = pos - lo
    return vals[lo] * (1 - w) + vals[hi] * w


def med(values):
    vals = [v for v in values if v is not None and math.isfinite(v)]
    return statistics.median(vals) if vals else None


def mean(values):
    vals = [v for v in values if v is not None and math.isfinite(v)]
    return sum(vals) / len(vals) if vals else None


def fmt(v, sig=5):
    if v is None:
        return "NA"
    return f"{v:.{sig}g}"


def bootstrap_ci(material_values, stat="median", reps=BOOT_REPS, seed=SEED):
    """Bootstrap a material-level scalar; materials are the resampling unit."""
    vals = [v for v in material_values if v is not None and math.isfinite(v)]
    if not vals:
        return None, None
    rng = random.Random(seed)
    n = len(vals)
    boots = []
    for _ in range(reps):
        sample = [vals[rng.randrange(n)] for _ in range(n)]
        boots.append(statistics.median(sample) if stat == "median" else sum(sample) / n)
    return qtile(boots, 0.025), qtile(boots, 0.975)


def exact_col(headers, candidates):
    by_lower = {h.lower(): h for h in headers}
    for c in candidates:
        if c.lower() in by_lower:
            return by_lower[c.lower()]
    return None


def normalize_codec(x):
    s = str(x).strip().lower()
    if "sperr" in s:
        return "sperr"
    if "sz3" in s or s == "sz":
        return "sz3"
    if "zfp" in s:
        return "zfp"
    return s


def greedy_match(list_a, list_b, caliper):
    """Nearest-neighbour bipartite matching without replacement in log10 Linf.

    Globally sorts all admissible edges by distance, then accepts the closest
    currently-unmatched edge. Deterministic tie-breaks use original row index.
    """
    candidates = []
    for ia, a in enumerate(list_a):
        for ib, b in enumerate(list_b):
            d = abs(a["log_linf"] - b["log_linf"])
            if d <= caliper + 1e-15:
                candidates.append((d, a["_row_index"], b["_row_index"], ia, ib))
    candidates.sort()
    used_a, used_b, out = set(), set(), []
    for d, _, _, ia, ib in candidates:
        if ia in used_a or ib in used_b:
            continue
        used_a.add(ia)
        used_b.add(ib)
        out.append((list_a[ia], list_b[ib], d))
    return out


with DATA.open(newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames or []

    material_col = exact_col(headers, ["material_id", "material", "id"])
    codec_col = exact_col(headers, ["codec", "compressor", "scheme"])
    linf_col = exact_col(headers, ["realized_Linf", "realized_linf", "Linf_realized", "realized_L_inf"])
    nom_abs_col = exact_col(headers, ["nominal_tolerance_absolute", "nominal_tolerance_abs", "absolute_tolerance", "abs_tolerance"])
    nom_rel_col = exact_col(headers, ["nominal_tolerance_relative", "nominal_tolerance_rel", "relative_tolerance", "rel_tolerance"])
    comp_col = exact_col(headers, ["compression_ratio", "ratio", "compress_ratio"])
    bpv_col = exact_col(headers, ["bits_per_value", "bpv", "bits_per_val"])

    if not material_col or not codec_col or not linf_col:
        raise RuntimeError(
            "Required columns not found. "
            f"material={material_col}, codec={codec_col}, realized_Linf={linf_col}. "
            f"Headers: {headers}"
        )

    bader_cols = [
        h for h in headers
        if h.lower().startswith("bader_error") and h.lower().endswith("_e")
    ]
    if not bader_cols:
        bader_cols = [
            h for h in headers
            if "bader" in h.lower() and "error" in h.lower()
        ]

    cert_cols = [h for h in headers if h.lower().startswith("certified_at_")]
    elig_cols = [h for h in headers if h.lower().startswith("eligible_a1_at_")]
    elig_by_suffix = {h.lower().split("eligible_a1_at_", 1)[1]: h for h in elig_cols}

    rows = []
    for i, r in enumerate(reader):
        codec = normalize_codec(r.get(codec_col, ""))
        linf = finite_float(r.get(linf_col))
        if codec not in CODECS or linf is None or linf <= 0:
            continue
        rr = dict(r)
        rr["_row_index"] = i
        rr["_codec"] = codec
        rr["_material"] = str(r.get(material_col, "")).strip()
        rr["realized_linf_num"] = linf
        rr["log_linf"] = math.log10(linf)
        rows.append(rr)

if not rows:
    raise RuntimeError("No usable codec rows with positive realized_Linf were found.")

# Freeze detected schema for auditability.
schema = {
    "data": str(DATA),
    "n_usable_rows": len(rows),
    "headers": headers,
    "material_col": material_col,
    "codec_col": codec_col,
    "realized_linf_col": linf_col,
    "nominal_absolute_col": nom_abs_col,
    "nominal_relative_col": nom_rel_col,
    "compression_ratio_col": comp_col,
    "bits_per_value_col": bpv_col,
    "bader_error_cols": bader_cols,
    "certification_cols": cert_cols,
    "eligibility_cols": elig_cols,
    "primary_caliper_dex": PRIMARY_CALIPER,
    "calipers_dex": list(CALIPERS),
    "bootstrap_reps": BOOT_REPS,
    "bootstrap_unit": "material",
    "seed": SEED,
}
(OUT / "schema_and_protocol.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

by_material = defaultdict(lambda: defaultdict(list))
for r in rows:
    by_material[r["_material"]][r["_codec"]].append(r)
for m in by_material:
    for c in by_material[m]:
        by_material[m][c].sort(key=lambda r: (r["log_linf"], r["_row_index"]))


def make_matches(codec_a, codec_b, caliper):
    matches = []
    for material, groups in by_material.items():
        la, lb = groups.get(codec_a, []), groups.get(codec_b, [])
        if not la or not lb:
            continue
        for a, b, d in greedy_match(la, lb, caliper):
            matches.append({"material": material, "a": a, "b": b, "distance_dex": d})
    return matches


def summarize_positive_metric(matches, col, codec_a, codec_b):
    """Material-level median log10(A/B), then median across materials."""
    per_mat_logs = defaultdict(list)
    vals_a, vals_b = [], []
    usable_pairs = 0
    for p in matches:
        a = finite_float(p["a"].get(col))
        b = finite_float(p["b"].get(col))
        if a is None or b is None or a <= 0 or b <= 0:
            continue
        usable_pairs += 1
        vals_a.append(a)
        vals_b.append(b)
        per_mat_logs[p["material"]].append(math.log10(a / b))
    mat_logs = [statistics.median(v) for v in per_mat_logs.values() if v]
    effect_log = med(mat_logs)
    lo, hi = bootstrap_ci(mat_logs, stat="median")
    return {
        "metric": col,
        "effect_type": f"material-median ratio {codec_a}/{codec_b}",
        "n_usable_pairs": usable_pairs,
        "n_usable_materials": len(mat_logs),
        "a_pair_median": med(vals_a),
        "b_pair_median": med(vals_b),
        "effect": 10 ** effect_log if effect_log is not None else None,
        "ci_low": 10 ** lo if lo is not None else None,
        "ci_high": 10 ** hi if hi is not None else None,
    }


def summarize_cert_metric(matches, cert_col, codec_a, codec_b):
    suffix = cert_col.lower().split("certified_at_", 1)[1]
    elig_col = elig_by_suffix.get(suffix)
    mat_diff = defaultdict(list)
    a_all, b_all = [], []
    usable_pairs = 0
    for p in matches:
        if elig_col:
            ea = boolish(p["a"].get(elig_col))
            eb = boolish(p["b"].get(elig_col))
            if ea is not True or eb is not True:
                continue
        a = boolish(p["a"].get(cert_col))
        b = boolish(p["b"].get(cert_col))
        if a is None or b is None:
            continue
        usable_pairs += 1
        av, bv = float(a), float(b)
        a_all.append(av)
        b_all.append(bv)
        mat_diff[p["material"]].append(av - bv)
    mat_diffs = [mean(v) for v in mat_diff.values() if v]
    effect = mean(mat_diffs)
    lo, hi = bootstrap_ci(mat_diffs, stat="mean")
    return {
        "metric": cert_col + (f" | both {elig_col}=TRUE" if elig_col else ""),
        "effect_type": f"material-mean certification-rate difference {codec_a}-{codec_b}",
        "n_usable_pairs": usable_pairs,
        "n_usable_materials": len(mat_diffs),
        "a_pair_median": mean(a_all),
        "b_pair_median": mean(b_all),
        "effect": effect,
        "ci_low": lo,
        "ci_high": hi,
    }


# Equal-nominal baseline diagnostics (when a common nominal column exists).
nom_col = nom_abs_col or nom_rel_col
baseline_rows = []
if nom_col:
    for codec_a, codec_b in PAIR_ORDER:
        ratios, diffs = [], []
        mats = set()
        n = 0
        for material, groups in by_material.items():
            ga, gb = groups.get(codec_a, []), groups.get(codec_b, [])
            if not ga or not gb:
                continue
            # key by numeric nominal tolerance; round log value for safe equality.
            idx_b = defaultdict(list)
            for b in gb:
                nv = finite_float(b.get(nom_col))
                if nv is not None and nv > 0:
                    idx_b[round(math.log10(nv), 12)].append(b)
            used = set()
            for a in ga:
                nv = finite_float(a.get(nom_col))
                if nv is None or nv <= 0:
                    continue
                key = round(math.log10(nv), 12)
                options = idx_b.get(key, [])
                # deterministic one-to-one pairing among duplicate nominal points.
                b = next((x for x in options if x["_row_index"] not in used), None)
                if b is None:
                    continue
                used.add(b["_row_index"])
                la, lb = a["realized_linf_num"], b["realized_linf_num"]
                ratios.append(la / lb)
                diffs.append(abs(math.log10(la) - math.log10(lb)))
                mats.add(material)
                n += 1
        baseline_rows.append({
            "pair": f"{codec_a}_vs_{codec_b}",
            "nominal_column": nom_col,
            "n_pairs": n,
            "n_materials": len(mats),
            "median_realized_Linf_ratio_A_over_B": med(ratios),
            "median_abs_log10_Linf_difference_dex": med(diffs),
            "p95_abs_log10_Linf_difference_dex": qtile(diffs, 0.95),
        })

with (OUT / "equal_nominal_diagnostics.csv").open("w", newline="", encoding="utf-8") as f:
    fields = ["pair", "nominal_column", "n_pairs", "n_materials", "median_realized_Linf_ratio_A_over_B", "median_abs_log10_Linf_difference_dex", "p95_abs_log10_Linf_difference_dex"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(baseline_rows)

# Matched-realized analysis over several calipers.
diag_rows = []
summary_rows = []
primary_pairs = []

metric_cols = list(bader_cols)
if comp_col:
    metric_cols.append(comp_col)
if bpv_col:
    metric_cols.append(bpv_col)

for cal in CALIPERS:
    for codec_a, codec_b in PAIR_ORDER:
        matches = make_matches(codec_a, codec_b, cal)
        diffs = [p["distance_dex"] for p in matches]
        ratios_sym = [10 ** p["distance_dex"] for p in matches]
        mats = {p["material"] for p in matches}
        diag_rows.append({
            "caliper_dex": cal,
            "pair": f"{codec_a}_vs_{codec_b}",
            "n_pairs": len(matches),
            "n_materials": len(mats),
            "median_abs_log10_Linf_difference_dex": med(diffs),
            "p95_abs_log10_Linf_difference_dex": qtile(diffs, 0.95),
            "median_larger_over_smaller_realized_Linf": med(ratios_sym),
            "p95_larger_over_smaller_realized_Linf": qtile(ratios_sym, 0.95),
        })

        for col in metric_cols:
            s = summarize_positive_metric(matches, col, codec_a, codec_b)
            s.update({"caliper_dex": cal, "pair": f"{codec_a}_vs_{codec_b}"})
            summary_rows.append(s)
        for col in cert_cols:
            s = summarize_cert_metric(matches, col, codec_a, codec_b)
            s.update({"caliper_dex": cal, "pair": f"{codec_a}_vs_{codec_b}"})
            summary_rows.append(s)

        if abs(cal - PRIMARY_CALIPER) < 1e-12:
            for p in matches:
                a, b = p["a"], p["b"]
                row = {
                    "pair": f"{codec_a}_vs_{codec_b}",
                    "material_id": p["material"],
                    "distance_dex": p["distance_dex"],
                    "realized_Linf_A": a["realized_linf_num"],
                    "realized_Linf_B": b["realized_linf_num"],
                    "realized_Linf_ratio_A_over_B": a["realized_linf_num"] / b["realized_linf_num"],
                    "row_index_A": a["_row_index"],
                    "row_index_B": b["_row_index"],
                }
                for c in [nom_abs_col, nom_rel_col, *bader_cols, comp_col, bpv_col, *cert_cols, *elig_cols]:
                    if c:
                        row[c + "_A"] = a.get(c, "")
                        row[c + "_B"] = b.get(c, "")
                primary_pairs.append(row)

with (OUT / "matching_diagnostics.csv").open("w", newline="", encoding="utf-8") as f:
    fields = ["caliper_dex", "pair", "n_pairs", "n_materials", "median_abs_log10_Linf_difference_dex", "p95_abs_log10_Linf_difference_dex", "median_larger_over_smaller_realized_Linf", "p95_larger_over_smaller_realized_Linf"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(diag_rows)

with (OUT / "matched_effects_summary.csv").open("w", newline="", encoding="utf-8") as f:
    fields = ["caliper_dex", "pair", "metric", "effect_type", "n_usable_pairs", "n_usable_materials", "a_pair_median", "b_pair_median", "effect", "ci_low", "ci_high"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(summary_rows)

if primary_pairs:
    all_fields = list(primary_pairs[0].keys())
    for r in primary_pairs[1:]:
        for k in r:
            if k not in all_fields:
                all_fields.append(k)
    with (OUT / "matched_pairs_primary_0p10dex.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=all_fields)
        w.writeheader(); w.writerows(primary_pairs)

# Machine-readable compact headline for downstream plotting/reporting.
primary_diag = [r for r in diag_rows if abs(r["caliper_dex"] - PRIMARY_CALIPER) < 1e-12]
primary_sum = [r for r in summary_rows if abs(r["caliper_dex"] - PRIMARY_CALIPER) < 1e-12]
headline = {
    "primary_caliper_dex": PRIMARY_CALIPER,
    "matching_diagnostics": primary_diag,
    "effects": primary_sum,
}
(OUT / "headline_results.json").write_text(json.dumps(headline, indent=2), encoding="utf-8")

# Human-readable report.
lines = []
lines.append("# Matched realized-L∞ comparison — V1\n")
lines.append("This analysis compares codecs within the **same material** after matching on `log10(realized_Linf)`. ")
lines.append(f"Primary caliper: **{PRIMARY_CALIPER:.2f} dex** (maximum realized-L∞ mismatch ≈ **{10**PRIMARY_CALIPER:.3f}×**). ")
lines.append("Matching is without replacement. Uncertainty intervals bootstrap **materials**, not rows.\n")
lines.append("## Detected schema\n")
lines.append(f"- usable rows: **{len(rows)}**")
lines.append(f"- material: `{material_col}`; codec: `{codec_col}`; realized L∞: `{linf_col}`")
lines.append(f"- nominal: `{nom_col}`")
lines.append(f"- Bader error columns: {', '.join('`'+x+'`' for x in bader_cols) if bader_cols else 'NONE'}")
lines.append(f"- compression ratio: `{comp_col}`; bits/value: `{bpv_col}`\n")

lines.append("## Match quality at the primary 0.10-dex caliper\n")
lines.append("| pair | matched pairs | materials | median |Δ log10 L∞| | p95 |Δ log10 L∞| | median larger/smaller L∞ |")
lines.append("|---|---:|---:|---:|---:|---:|")
for r in primary_diag:
    lines.append(f"| {r['pair']} | {r['n_pairs']} | {r['n_materials']} | {fmt(r['median_abs_log10_Linf_difference_dex'])} | {fmt(r['p95_abs_log10_Linf_difference_dex'])} | {fmt(r['median_larger_over_smaller_realized_Linf'])}× |")

if baseline_rows:
    lines.append("\n## Equal-nominal baseline\n")
    lines.append("| pair | pairs | materials | median realized L∞ A/B | median |Δ log10 L∞| |")
    lines.append("|---|---:|---:|---:|---:|")
    for r in baseline_rows:
        lines.append(f"| {r['pair']} | {r['n_pairs']} | {r['n_materials']} | {fmt(r['median_realized_Linf_ratio_A_over_B'])}× | {fmt(r['median_abs_log10_Linf_difference_dex'])} |")

lines.append("\n## Effects after matching realized L∞\n")
lines.append("For positive-valued metrics, `effect` is the median across materials of the within-material median **A/B ratio**. ")
lines.append("Thus values below 1 mean codec A is lower than codec B after controlling realized L∞. Certification effects are A−B rate differences among jointly A.1-eligible pairs when the eligibility flag exists.\n")
lines.append("| pair | metric | materials | effect | 95% material-bootstrap CI |")
lines.append("|---|---|---:|---:|---:|")
for r in primary_sum:
    lines.append(f"| {r['pair']} | {r['metric']} | {r['n_usable_materials']} | {fmt(r['effect'])} | [{fmt(r['ci_low'])}, {fmt(r['ci_high'])}] |")

lines.append("\n## Sensitivity\n")
lines.append("The same analysis is repeated at 0.05, 0.10, 0.20 and 0.30 dex. A codec effect should not be interpreted as robust if its sign/direction changes materially with the caliper or if common support collapses at tighter calipers.\n")
lines.append("## Interpretation rule\n")
lines.append("- If a codec advantage seen at equal nominal tolerance shrinks toward an A/B ratio of 1 after realized-L∞ matching, the nominal-tolerance result was largely a **realized-distortion confound**.\n- If a substantial codec effect persists at tightly matched realized L∞, then a scalar L∞ magnitude is insufficient; **error geometry / spatial structure** is implicated.\n")

(OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(json.dumps({
    "status": "ok",
    "usable_rows": len(rows),
    "primary_caliper": PRIMARY_CALIPER,
    "primary_diagnostics": primary_diag,
    "output_dir": str(OUT),
}, indent=2))
