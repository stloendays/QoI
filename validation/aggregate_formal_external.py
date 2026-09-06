#!/usr/bin/env python3
"""Aggregate sharded formal external E2E outputs.

Produces a single auditable external table plus material-level certification and
Certified Compression Ratio (CCR) summaries. CCR_i,c(tau) is the maximum
compression ratio among retained rows certified at tau for material i and codec c.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

TAUS = ("1e-4", "1e-3", "1e-2")
CODECS = ("ZFP", "SZ3", "SPERR")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or not path.read_text().strip():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fields.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def median_or_none(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


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
    failure_files = sorted(input_root.rglob("formal_external_e2e_failures.csv"))
    if not row_files:
        raise SystemExit("No formal shard row files found")

    rows = [row for path in row_files for row in read_csv(path)]
    audits = [row for path in audit_files for row in read_csv(path)]
    failures = [row for path in failure_files for row in read_csv(path)]

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

    audit_by_material: dict[str, dict[str, str]] = {}
    for audit in audits:
        mid = audit["material_id"]
        if mid in audit_by_material:
            raise SystemExit(f"Duplicate material audit across shards: {mid}")
        audit_by_material[mid] = audit

    completed_materials = {
        mid for mid, audit in audit_by_material.items() if audit.get("status") == "COMPLETE"
    }
    failure_materials = {f["material_id"] for f in failures}

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
    write_csv(output_dir / "formal_external_e2e_failures.csv", failures)

    # One row per material x codec x tau, suitable for paired codec comparisons.
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["material_id"], row["codec"])].append(row)

    best_rows: list[dict[str, Any]] = []
    for mid in sorted(completed_materials):
        domain = manifest.get(mid, {}).get("domain", audit_by_material[mid].get("domain", ""))
        floor = float(audit_by_material[mid]["stability_floor_A1_e"])
        for codec in CODECS:
            codec_rows = grouped.get((mid, codec), [])
            for tau in TAUS:
                tau_value = float(tau)
                eligible = floor < tau_value
                certified_rows = [
                    r for r in codec_rows if as_bool(r.get(f"certified_at_{tau}", "false"))
                ]
                if certified_rows:
                    best = max(certified_rows, key=lambda r: float(r["compression_ratio"]))
                    best_rows.append(
                        {
                            "material_id": mid,
                            "domain": domain,
                            "codec": codec,
                            "tau_e": tau,
                            "eligible_A1": eligible,
                            "has_certified_point": True,
                            "CCR": float(best["compression_ratio"]),
                            "bits_per_value_at_CCR": float(best["bits_per_value"]),
                            "nominal_tolerance_relative_at_CCR": float(
                                best["nominal_tolerance_relative"]
                            ),
                            "realized_Linf_at_CCR": float(best["realized_Linf"]),
                            "Bader_error_resolved_e_at_CCR": float(
                                best["Bader_error_resolved_e"]
                            ),
                        }
                    )
                else:
                    best_rows.append(
                        {
                            "material_id": mid,
                            "domain": domain,
                            "codec": codec,
                            "tau_e": tau,
                            "eligible_A1": eligible,
                            "has_certified_point": False,
                            "CCR": "",
                            "bits_per_value_at_CCR": "",
                            "nominal_tolerance_relative_at_CCR": "",
                            "realized_Linf_at_CCR": "",
                            "Bader_error_resolved_e_at_CCR": "",
                        }
                    )

    write_csv(output_dir / "best_certified_external.csv", best_rows)

    codec_summary: list[dict[str, Any]] = []
    for domain in ("ALL", "bulk", "vacuum2d"):
        domain_rows = best_rows if domain == "ALL" else [r for r in best_rows if r["domain"] == domain]
        for codec in CODECS:
            for tau in TAUS:
                subset = [r for r in domain_rows if r["codec"] == codec and r["tau_e"] == tau]
                eligible = [r for r in subset if r["eligible_A1"]]
                certified = [r for r in eligible if r["has_certified_point"]]
                ccrs = [float(r["CCR"]) for r in certified]
                bpvs = [float(r["bits_per_value_at_CCR"]) for r in certified]
                codec_summary.append(
                    {
                        "domain": domain,
                        "codec": codec,
                        "tau_e": tau,
                        "n_materials": len(subset),
                        "n_eligible": len(eligible),
                        "n_certified": len(certified),
                        "certification_fraction_among_eligible": (
                            len(certified) / len(eligible) if eligible else ""
                        ),
                        "median_CCR": median_or_none(ccrs) if ccrs else "",
                        "median_bits_per_value_at_CCR": median_or_none(bpvs) if bpvs else "",
                    }
                )
    write_csv(output_dir / "external_codec_summary.csv", codec_summary)

    bound_violations = [r for r in rows if not as_bool(r.get("bound_respected", "false"))]
    negative_source_materials = sorted(
        {
            r["material_id"]
            for r in rows
            if as_bool(r.get("source_has_negative_density", "false"))
        }
    )
    summary = {
        "n_manifest_materials": len(manifest),
        "n_materials_observed": len(audit_by_material),
        "n_materials_complete": len(completed_materials),
        "n_pipeline_failures": len(failure_materials),
        "failure_materials": sorted(failure_materials),
        "n_rows": len(rows),
        "n_bound_violations": len(bound_violations),
        "all_codec_bounds_respected": len(bound_violations) == 0,
        "n_negative_source_density_materials": len(negative_source_materials),
        "negative_source_density_materials": negative_source_materials,
        "outputs": {
            "row_table": "formal_external_e2e_rows.csv",
            "material_audit": "material_audit.csv",
            "failures": "formal_external_e2e_failures.csv",
            "best_certified": "best_certified_external.csv",
            "codec_summary": "external_codec_summary.csv",
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, sort_keys=True))

    return 0 if not failure_materials and not bound_violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
