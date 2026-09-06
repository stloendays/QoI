#!/usr/bin/env python3
"""Formal frozen external rate-fidelity driver.

This script wraps ``external_end_to_end.py`` and reproduces the development
benchmark's staged tolerance policy on the untouched external corpus:

1. Base ladder: every material and codec.
2. Tight ladder: only materials that are Protocol A.1-eligible at 1e-3 e.
3. Base-ladder reporting stops after the first resolved-Bader error >= 0.05 e
   for each material/codec, matching the frozen development early-stop rule.

The runner may compute points beyond the early-stop boundary for implementation
simplicity, but those points are not retained in the formal benchmark table.
No parameter is tuned from external outcomes.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

import external_end_to_end as core

TIGHT_ELIGIBILITY_TAU = 1e-3
EARLY_STOP_QOI_E = 0.05
BASE_SPLIT_REL = 1e-5


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--material-id", action="append", default=[])
    p.add_argument("--domain", choices=["bulk", "vacuum2d"], default=None)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--shard-count", type=int, default=1)
    p.add_argument("--shard-index", type=int, default=0)
    p.add_argument("--codecs", default="zfp,sz3,sperr")
    p.add_argument("--output-dir", default="validation/formal_results")
    return p.parse_args()


def staged_ladders(codecs: list[str]) -> tuple[dict[str, list[float]], dict[str, list[float]]]:
    all_ladders = core.load_frozen_tolerance_ladders(codecs)
    base: dict[str, list[float]] = {}
    tight: dict[str, list[float]] = {}
    for codec, values in all_ladders.items():
        # Evaluate from tight -> loose so the early-stop rule has one direction.
        ascending = sorted(values)
        base[codec] = [x for x in ascending if x >= BASE_SPLIT_REL]
        tight[codec] = [x for x in ascending if x < BASE_SPLIT_REL]
        if not base[codec]:
            raise RuntimeError(f"No base-ladder tolerances recovered for {codec}")
    return base, tight


def retain_frozen_rows(
    rows: list[dict[str, Any]],
    codecs: list[str],
    tight_enabled: bool,
) -> list[dict[str, Any]]:
    retained: list[dict[str, Any]] = []
    for codec in codecs:
        codec_name = core.CODEC_NAMES[codec]
        codec_rows = [r for r in rows if r["codec"] == codec_name]
        codec_rows.sort(key=lambda r: float(r["nominal_tolerance_relative"]))

        tight_rows = [
            r for r in codec_rows if float(r["nominal_tolerance_relative"]) < BASE_SPLIT_REL
        ]
        base_rows = [
            r for r in codec_rows if float(r["nominal_tolerance_relative"]) >= BASE_SPLIT_REL
        ]

        if tight_enabled:
            for row in tight_rows:
                row["ladder_stage"] = "tight_A1_eligible_1e-3"
                row["retained_by_frozen_policy"] = True
                row["early_stop_boundary"] = False
                retained.append(row)

        stopped = False
        for row in base_rows:
            if stopped:
                continue
            row["ladder_stage"] = "base"
            row["retained_by_frozen_policy"] = True
            hit = float(row["Bader_error_resolved_e"]) >= EARLY_STOP_QOI_E
            row["early_stop_boundary"] = bool(hit)
            retained.append(row)
            if hit:
                stopped = True
    return retained


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    codecs = [x.strip().lower() for x in args.codecs.split(",") if x.strip()]
    invalid = sorted(set(codecs) - set(core.CODEC_NAMES))
    if invalid:
        raise SystemExit(f"Invalid codecs: {invalid}")

    base_ladders, tight_ladders = staged_ladders(codecs)
    records = core.load_manifest()
    floors = core.load_floors()

    if args.material_id:
        wanted = set(args.material_id)
        records = [r for r in records if r["material_id"] in wanted]
        missing = wanted - {r["material_id"] for r in records}
        if missing:
            raise SystemExit(f"Material IDs absent from frozen manifest: {sorted(missing)}")
    if args.domain:
        records = [r for r in records if r["domain"] == args.domain]
    if args.limit:
        records = records[: args.limit]

    if args.shard_count < 1:
        raise SystemExit("--shard-count must be >= 1")
    if not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("--shard-index must satisfy 0 <= index < count")
    records = [
        record
        for index, record in enumerate(records)
        if index % args.shard_count == args.shard_index
    ]
    if not records:
        raise SystemExit("No records selected")

    outdir = core.ROOT / args.output_dir
    outdir.mkdir(parents=True, exist_ok=True)

    formal_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    material_audit: list[dict[str, Any]] = []

    metadata = {
        "formal_external_protocol": "frozen_staged_v1",
        "manifest_sha256": core.sha256_hex(core.MANIFEST.read_bytes()),
        "stability_floor_sha256": core.sha256_hex(core.FLOORS.read_bytes()),
        "protocol_A1_sha256": core.sha256_hex(core.PROTOCOL_A1.read_bytes()),
        "master_benchmark_sha256": core.sha256_hex(core.MASTER_BENCHMARK.read_bytes()),
        "base_split_relative": BASE_SPLIT_REL,
        "tight_eligibility_tau_e": TIGHT_ELIGIBILITY_TAU,
        "early_stop_resolved_Bader_error_e": EARLY_STOP_QOI_E,
        "base_ladders": base_ladders,
        "tight_ladders": tight_ladders,
        "codecs": codecs,
        "selected_materials": [r["material_id"] for r in records],
        "shard_count": args.shard_count,
        "shard_index": args.shard_index,
        "packages": core.package_versions(),
        "bader": {
            "method": core.BADER_METHOD,
            "vacuum_tol": core.BADER_VACUUM_TOL,
            "persistence_tol": core.BADER_PERSISTENCE_TOL,
            "nna_cutoff": core.BADER_NNA_CUTOFF,
        },
    }
    (outdir / "run_metadata.json").write_text(json.dumps(metadata, indent=2))

    for record in records:
        mid = record["material_id"]
        try:
            if mid not in floors:
                raise RuntimeError("missing Protocol A.1 stability floor")
            floor = floors[mid]
            tight_enabled = bool(floor < TIGHT_ELIGIBILITY_TAU)
            material_ladders = {
                codec: sorted(
                    base_ladders[codec]
                    + (tight_ladders[codec] if tight_enabled else [])
                )
                for codec in codecs
            }

            raw_rows: list[dict[str, Any]] = []
            core.run_record(
                record,
                floor,
                codecs,
                material_ladders,
                raw_rows,
                outdir,
            )
            retained = retain_frozen_rows(raw_rows, codecs, tight_enabled)
            for row in retained:
                row["formal_tight_eligible_at_1e-3"] = tight_enabled
            formal_rows.extend(retained)
            material_audit.append(
                {
                    "material_id": mid,
                    "domain": record["domain"],
                    "stability_floor_A1_e": floor,
                    "tight_enabled": tight_enabled,
                    "n_rows_computed": len(raw_rows),
                    "n_rows_retained": len(retained),
                    "n_rows_dropped_post_early_stop": len(raw_rows) - len(retained),
                    "status": "COMPLETE",
                }
            )
        except Exception as exc:
            failures.append(
                {"material_id": mid, "error_type": type(exc).__name__, "error": str(exc)}
            )
            material_audit.append(
                {
                    "material_id": mid,
                    "domain": record["domain"],
                    "stability_floor_A1_e": floors.get(mid, ""),
                    "tight_enabled": "",
                    "n_rows_computed": 0,
                    "n_rows_retained": 0,
                    "n_rows_dropped_post_early_stop": 0,
                    "status": "PIPELINE_FAILURE",
                }
            )
            print(
                json.dumps(
                    {"material": mid, "status": "PIPELINE_FAILURE", "error": repr(exc)}
                ),
                file=core.sys.stderr,
                flush=True,
            )

    write_csv(outdir / "formal_external_e2e_rows.csv", formal_rows)
    write_csv(outdir / "material_audit.csv", material_audit)
    write_csv(outdir / "formal_external_e2e_failures.csv", failures)

    summary = {
        "n_materials_selected": len(records),
        "n_materials_complete": sum(x["status"] == "COMPLETE" for x in material_audit),
        "n_failures": len(failures),
        "n_rows_retained": len(formal_rows),
        "all_codec_bounds_respected": bool(formal_rows)
        and all(bool(r["bound_respected"]) for r in formal_rows),
        "n_tight_eligible_materials": sum(
            bool(x["tight_enabled"]) for x in material_audit if x["status"] == "COMPLETE"
        ),
        "n_certified_at_1e-4": sum(bool(r["certified_at_1e-4"]) for r in formal_rows),
        "n_certified_at_1e-3": sum(bool(r["certified_at_1e-3"]) for r in formal_rows),
        "n_certified_at_1e-2": sum(bool(r["certified_at_1e-2"]) for r in formal_rows),
        "n_maxima_count_changes": sum(
            bool(r["bader_maxima_count_changed"]) for r in formal_rows
        ),
        "median_realized_Linf_over_nominal_by_codec": {
            core.CODEC_NAMES[c]: (
                float(
                    np.median(
                        [
                            r["realized_Linf_over_nominal"]
                            for r in formal_rows
                            if r["codec"] == core.CODEC_NAMES[c]
                        ]
                    )
                )
                if any(r["codec"] == core.CODEC_NAMES[c] for r in formal_rows)
                else None
            )
            for c in codecs
        },
        "failure_materials": [f["material_id"] for f in failures],
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"summary": summary}, sort_keys=True), flush=True)

    return 0 if not failures and formal_rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
