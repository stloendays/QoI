#!/usr/bin/env python3
"""Aggregate sharded formal external E2E outputs.

The aggregation unit is the material, matching the released development
``summary_a1.csv`` and ``pairwise_a1.csv`` semantics.  Row-level codec/Bader
failures are merged into an explicit registry and are never counted as passes,
but they do not erase successful rows for the same material.

Primary rate-fidelity metric
----------------------------
For material i, codec c and scientific tolerance tau, the Certified Compression
Ratio (CCR) is the maximum compression ratio among retained rows certified at
tau.  This is the external name for the same quantity already released as the
"best certified ratio" in ``benchmark/best_certified_a1.csv``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

TAUS = ("1e-4", "1e-3", "1e-2")
CODECS = ("ZFP", "SZ3", "SPERR")
PAIR_ORDER = (("SPERR", "SZ3"), ("SPERR", "ZFP"), ("SZ3", "ZFP"))
STRATA = ("overall", "bulk", "vacuum2d")
BOOTSTRAP_DRAWS = 5000


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or not path.read_text().strip():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fields: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.add(key)
                    fields.append(key)
        fieldnames = fields
    if not rows:
        if fieldnames:
            with path.open("w", newline="") as f:
                csv.DictWriter(f, fieldnames=fieldnames).writeheader()
        else:
            path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def quantile(values: Iterable[float], q: float) -> float | None:
    xs = sorted(float(x) for x in values)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def deterministic_seed(label: str) -> int:
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def bootstrap_median_ci(values: list[float], label: str) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    if len(values) == 1:
        return float(values[0]), float(values[0])
    rng = random.Random(deterministic_seed("median:" + label))
    n = len(values)
    boot: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        boot.append(float(statistics.median(sample)))
    return quantile(boot, 0.025), quantile(boot, 0.975)


def bootstrap_fraction_ci(indicators: list[int], label: str) -> tuple[float | None, float | None]:
    if not indicators:
        return None, None
    if len(indicators) == 1:
        x = float(indicators[0])
        return x, x
    rng = random.Random(deterministic_seed("fraction:" + label))
    n = len(indicators)
    boot: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        total = sum(indicators[rng.randrange(n)] for _ in range(n))
        boot.append(total / n)
    return quantile(boot, 0.025), quantile(boot, 0.975)


def load_manifest_materials(repo_root: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads((repo_root / "external_test_MANIFEST.json").read_text())
    return {r["material_id"]: r for r in payload["records"]}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input-root", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--expect-full", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    input_root = Path(args.input_root)
    output_dir = Path(args.output_dir)
    repo_root = Path(__file__).resolve().parents[1]
    manifest = load_manifest_materials(repo_root)

    row_files = sorted(input_root.rglob("formal_external_e2e_rows.csv"))
    audit_files = sorted(input_root.rglob("material_audit.csv"))
    material_failure_files = sorted(input_root.rglob("formal_external_e2e_failures.csv"))
    row_failure_files = sorted(input_root.rglob("formal_external_e2e_row_failures.csv"))
    if not row_files:
        raise SystemExit("No formal shard row files found")

    rows = [row for path in row_files for row in read_csv(path)]
    audits = [row for path in audit_files for row in read_csv(path)]
    material_failures = [row for path in material_failure_files for row in read_csv(path)]
    row_failures = [row for path in row_failure_files for row in read_csv(path)]

    # Deterministic ordering and duplicate protection.
    rows.sort(
        key=lambda r: (
            r["material_id"],
            r["codec"],
            float(r["nominal_tolerance_relative"]),
        )
    )
    row_keys = [
        (r["material_id"], r["codec"], float(r["nominal_tolerance_relative"]))
        for r in rows
    ]
    if len(row_keys) != len(set(row_keys)):
        raise SystemExit("Duplicate material/codec/tolerance rows found across shards")

    failure_keys = [
        (
            r.get("material_id", ""),
            r.get("codec", ""),
            r.get("nominal_tolerance_relative", ""),
            r.get("stage", ""),
        )
        for r in row_failures
    ]
    if len(failure_keys) != len(set(failure_keys)):
        raise SystemExit("Duplicate row-level failures found across shards")

    audit_by_material: dict[str, dict[str, str]] = {}
    for audit in audits:
        mid = audit["material_id"]
        if mid in audit_by_material:
            raise SystemExit(f"Duplicate material audit across shards: {mid}")
        audit_by_material[mid] = audit

    completed_materials = {
        mid for mid, audit in audit_by_material.items() if audit.get("status") == "COMPLETE"
    }
    hard_failure_materials = {f["material_id"] for f in material_failures}

    if args.expect_full:
        expected = set(manifest)
        observed = set(audit_by_material)
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        if missing or extra:
            raise SystemExit(
                f"Full-corpus coverage mismatch: missing={missing}, extra={extra}"
            )

    write_csv(output_dir / "formal_external_e2e_rows.csv", rows)
    write_csv(output_dir / "material_audit.csv", sorted(audits, key=lambda r: r["material_id"]))
    write_csv(output_dir / "formal_external_e2e_failures.csv", material_failures)
    write_csv(
        output_dir / "formal_external_e2e_row_failures.csv",
        sorted(
            row_failures,
            key=lambda r: (
                r.get("material_id", ""),
                r.get("codec", ""),
                float(r.get("nominal_tolerance_relative", 0) or 0),
            ),
        ),
    )

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["material_id"], row["codec"])].append(row)

    row_failures_by_pair: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for failure in row_failures:
        row_failures_by_pair[(failure["material_id"], failure["codec"])].append(failure)

    # One row per material x codec x tau.  All completed materials are represented,
    # including non-evaluable and not-certified cases, so denominators are explicit.
    best_rows: list[dict[str, Any]] = []
    for mid in sorted(completed_materials):
        domain = manifest.get(mid, {}).get("domain", audit_by_material[mid].get("domain", ""))
        floor = float(audit_by_material[mid]["stability_floor_A1_e"])
        for codec in CODECS:
            codec_rows = grouped.get((mid, codec), [])
            pair_failures = row_failures_by_pair.get((mid, codec), [])
            for tau in TAUS:
                tau_value = float(tau)
                eligible = floor < tau_value
                certified_rows = [
                    r for r in codec_rows if as_bool(r.get(f"certified_at_{tau}", "false"))
                ]
                if not eligible:
                    status = "NON_EVALUABLE_BADER_UNSTABLE"
                elif certified_rows:
                    status = "CERTIFIED"
                elif codec_rows:
                    status = "NOT_CERTIFIED"
                elif pair_failures:
                    status = "ROW_PIPELINE_FAILURE_NO_SUCCESSFUL_POINT"
                else:
                    status = "NOT_CERTIFIED_NO_RETAINED_POINT"

                base: dict[str, Any] = {
                    "material_id": mid,
                    "domain": domain,
                    "codec": codec,
                    "tau_e": tau,
                    "stability_floor_A1_e": floor,
                    "eligible_A1": eligible,
                    "status": status,
                    "has_certified_point": bool(certified_rows),
                    "n_successful_retained_rows": len(codec_rows),
                    "n_row_failures": len(pair_failures),
                    "row_failure_present": bool(pair_failures),
                }
                if certified_rows:
                    best = max(certified_rows, key=lambda r: float(r["compression_ratio"]))
                    base.update(
                        {
                            "CCR": float(best["compression_ratio"]),
                            "bits_per_value_at_CCR": float(best["bits_per_value"]),
                            "nominal_tolerance_relative_at_CCR": float(
                                best["nominal_tolerance_relative"]
                            ),
                            "realized_Linf_at_CCR": float(best["realized_Linf"]),
                            "realized_Linf_over_nominal_at_CCR": float(
                                best["realized_Linf_over_nominal"]
                            ),
                            "Bader_error_fixed_e_at_CCR": float(best["Bader_error_fixed_e"]),
                            "Bader_error_resolved_e_at_CCR": float(
                                best["Bader_error_resolved_e"]
                            ),
                            "atom_domain_migration_fraction_at_CCR": float(
                                best["atom_domain_migration_fraction"]
                            ),
                            "ladder_stage_at_CCR": best.get("ladder_stage", ""),
                        }
                    )
                else:
                    base.update(
                        {
                            "CCR": "",
                            "bits_per_value_at_CCR": "",
                            "nominal_tolerance_relative_at_CCR": "",
                            "realized_Linf_at_CCR": "",
                            "realized_Linf_over_nominal_at_CCR": "",
                            "Bader_error_fixed_e_at_CCR": "",
                            "Bader_error_resolved_e_at_CCR": "",
                            "atom_domain_migration_fraction_at_CCR": "",
                            "ladder_stage_at_CCR": "",
                        }
                    )
                best_rows.append(base)

    write_csv(output_dir / "best_certified_external.csv", best_rows)

    best_index = {
        (r["material_id"], r["codec"], r["tau_e"]): r
        for r in best_rows
    }

    # Development-compatible summary table: statistics operate on the best
    # certified ratio per material, not on tolerance rows.
    summary_rows: list[dict[str, Any]] = []
    for tau in TAUS:
        tau_value = float(tau)
        for stratum in STRATA:
            mids = sorted(
                mid
                for mid in completed_materials
                if stratum == "overall" or manifest[mid]["domain"] == stratum
            )
            admitted_mids = [
                mid
                for mid in mids
                if float(audit_by_material[mid]["stability_floor_A1_e"]) < tau_value
            ]
            for codec in CODECS:
                records = [best_index[(mid, codec, tau)] for mid in admitted_mids]
                certified = [r for r in records if r["has_certified_point"]]
                ratios = [float(r["CCR"]) for r in certified]
                med = float(statistics.median(ratios)) if ratios else None
                ci_lo, ci_hi = bootstrap_median_ci(
                    ratios, f"{tau}:{stratum}:{codec}"
                )
                summary_rows.append(
                    {
                        "threshold_e": tau_value,
                        "stratum": stratum,
                        "codec": codec.lower(),
                        "n_admitted": len(admitted_mids),
                        "n_non_evaluable": len(mids) - len(admitted_mids),
                        "n_certified": len(certified),
                        "frac_certified": (
                            len(certified) / len(admitted_mids) if admitted_mids else ""
                        ),
                        "ratio_median": med if med is not None else "",
                        "ratio_median_ci_lo": ci_lo if ci_lo is not None else "",
                        "ratio_median_ci_hi": ci_hi if ci_hi is not None else "",
                        "ratio_p10": quantile(ratios, 0.10) if ratios else "",
                        "ratio_q1": quantile(ratios, 0.25) if ratios else "",
                        "ratio_q3": quantile(ratios, 0.75) if ratios else "",
                        "ratio_p90": quantile(ratios, 0.90) if ratios else "",
                        "n_row_failure_affected": sum(
                            bool(r["row_failure_present"]) for r in records
                        ),
                    }
                )
    write_csv(output_dir / "external_summary_a1.csv", summary_rows)

    # Pairwise material-level comparison.  A missing CCR is a non-win, not a
    # silently excluded sample.  Two missing CCRs tie.  The log2 effect size is
    # defined only where both codecs have certified positive CCRs.
    pairwise_rows: list[dict[str, Any]] = []
    for tau in TAUS:
        tau_value = float(tau)
        for stratum in STRATA:
            mids = sorted(
                mid
                for mid in completed_materials
                if (stratum == "overall" or manifest[mid]["domain"] == stratum)
                and float(audit_by_material[mid]["stability_floor_A1_e"]) < tau_value
            )
            for codec_a, codec_b in PAIR_ORDER:
                outcomes: list[int] = []  # +1 A win, 0 tie, -1 B win
                log_ratios: list[float] = []
                any_row_failure = 0
                for mid in mids:
                    a = best_index[(mid, codec_a, tau)]
                    b = best_index[(mid, codec_b, tau)]
                    a_ccr = float(a["CCR"]) if a["has_certified_point"] else None
                    b_ccr = float(b["CCR"]) if b["has_certified_point"] else None
                    if a["row_failure_present"] or b["row_failure_present"]:
                        any_row_failure += 1
                    if a_ccr is not None and b_ccr is not None:
                        log_ratios.append(math.log2(a_ccr / b_ccr))
                        if math.isclose(a_ccr, b_ccr, rel_tol=1e-12, abs_tol=0.0):
                            outcomes.append(0)
                        elif a_ccr > b_ccr:
                            outcomes.append(1)
                        else:
                            outcomes.append(-1)
                    elif a_ccr is not None:
                        outcomes.append(1)
                    elif b_ccr is not None:
                        outcomes.append(-1)
                    else:
                        outcomes.append(0)

                n = len(outcomes)
                a_win_indicators = [1 if x == 1 else 0 for x in outcomes]
                frac_a = sum(x == 1 for x in outcomes) / n if n else None
                frac_tie = sum(x == 0 for x in outcomes) / n if n else None
                frac_b = sum(x == -1 for x in outcomes) / n if n else None
                ci_lo, ci_hi = bootstrap_fraction_ci(
                    a_win_indicators, f"{tau}:{stratum}:{codec_a}:{codec_b}"
                )
                pairwise_rows.append(
                    {
                        "threshold_e": tau_value,
                        "stratum": stratum,
                        "codec_a": codec_a.lower(),
                        "codec_b": codec_b.lower(),
                        "n": n,
                        "frac_a_wins": frac_a if frac_a is not None else "",
                        "frac_ties": frac_tie if frac_tie is not None else "",
                        "frac_b_wins": frac_b if frac_b is not None else "",
                        "a_wins_ci_lo": ci_lo if ci_lo is not None else "",
                        "a_wins_ci_hi": ci_hi if ci_hi is not None else "",
                        "median_log2_ratio_a_over_b": (
                            float(statistics.median(log_ratios)) if log_ratios else ""
                        ),
                        "n_both_certified": len(log_ratios),
                        "n_row_failure_affected": any_row_failure,
                    }
                )
    write_csv(output_dir / "pairwise_external.csv", pairwise_rows)

    # Backwards-friendly compact table retained in addition to the development-
    # shaped summary above.
    compact_rows: list[dict[str, Any]] = []
    for row in summary_rows:
        compact_rows.append(
            {
                "domain": "ALL" if row["stratum"] == "overall" else row["stratum"],
                "codec": str(row["codec"]).upper(),
                "tau_e": row["threshold_e"],
                "n_materials": row["n_admitted"] + row["n_non_evaluable"],
                "n_eligible": row["n_admitted"],
                "n_certified": row["n_certified"],
                "certification_fraction_among_eligible": row["frac_certified"],
                "median_CCR": row["ratio_median"],
                "median_CCR_ci_lo": row["ratio_median_ci_lo"],
                "median_CCR_ci_hi": row["ratio_median_ci_hi"],
                "n_row_failure_affected": row["n_row_failure_affected"],
            }
        )
    write_csv(output_dir / "external_codec_summary.csv", compact_rows)

    bound_violations = [r for r in rows if not as_bool(r.get("bound_respected", "false"))]
    negative_source_materials = sorted(
        {
            r["material_id"]
            for r in rows
            if as_bool(r.get("source_has_negative_density", "false"))
        }
    )
    row_failure_categories: dict[str, int] = defaultdict(int)
    for failure in row_failures:
        row_failure_categories[failure.get("category", "UNKNOWN")] += 1

    external_eligible_counts = {
        tau: sum(
            float(audit_by_material[mid]["stability_floor_A1_e"]) < float(tau)
            for mid in completed_materials
        )
        for tau in TAUS
    }
    summary = {
        "aggregation_version": "external_a1_material_level_v2",
        "n_manifest_materials": len(manifest),
        "n_materials_observed": len(audit_by_material),
        "n_materials_complete": len(completed_materials),
        "n_material_pipeline_failures": len(hard_failure_materials),
        "material_failure_ids": sorted(hard_failure_materials),
        "n_row_failures": len(row_failures),
        "row_failure_materials": sorted({r["material_id"] for r in row_failures}),
        "row_failure_categories": dict(sorted(row_failure_categories.items())),
        "n_rows": len(rows),
        "n_bound_violations": len(bound_violations),
        "all_codec_bounds_respected": len(bound_violations) == 0,
        "eligible_A1_counts_completed_materials": external_eligible_counts,
        "n_negative_source_density_materials": len(negative_source_materials),
        "negative_source_density_materials": negative_source_materials,
        "outputs": {
            "row_table": "formal_external_e2e_rows.csv",
            "material_audit": "material_audit.csv",
            "material_failures": "formal_external_e2e_failures.csv",
            "row_failures": "formal_external_e2e_row_failures.csv",
            "best_certified": "best_certified_external.csv",
            "development_compatible_summary": "external_summary_a1.csv",
            "pairwise": "pairwise_external.csv",
            "compact_codec_summary": "external_codec_summary.csv",
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, sort_keys=True))

    # Explicit row-level failures are benchmark outcomes and do not invalidate
    # the aggregate.  Missing whole materials, hard material failures, or codec
    # bound violations do invalidate the formal external run.
    return 0 if not hard_failure_materials and not bound_violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
