#!/usr/bin/env python3
"""Build the primary 63-system confirmatory summary from the full 65-system run.

The corpus-scale computation still runs all frozen 65 records.  This postprocessor
removes only the two pre-frozen implementation sentinels and reuses the exact same
material-level aggregator on the remaining 63 systems.  No scientific row is
changed and no outcome-dependent selection is performed here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "validation" / "external_rate_fidelity_split.json"
AGGREGATOR = ROOT / "validation" / "aggregate_formal_external.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv_with_fields(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists() or not path.read_text().strip():
        return [], []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def filter_csv(
    source: Path,
    target: Path,
    keep: Callable[[dict[str, str]], bool],
) -> int:
    fields, rows = read_csv_with_fields(source)
    kept = [row for row in rows if keep(row)]
    target.parent.mkdir(parents=True, exist_ok=True)
    if not fields:
        target.write_text("")
        return 0
    with target.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(kept)
    return len(kept)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--aggregate-dir", required=True)
    p.add_argument("--output-dir", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    aggregate_dir = Path(args.aggregate_dir)
    output_dir = Path(args.output_dir)
    split = json.loads(SPLIT.read_text())
    if split.get("frozen") is not True:
        raise SystemExit("Confirmatory split is not frozen")

    sentinels = {
        item["material_id"] for item in split["implementation_sentinels"]
    }
    expected_n = int(split["confirmatory_rate_fidelity_cohort"]["n"])
    expected_eligible = split["confirmatory_rate_fidelity_cohort"][
        "expected_A1_eligible_counts"
    ]

    audit_path = aggregate_dir / "material_audit.csv"
    _, full_audit = read_csv_with_fields(audit_path)
    observed = {r["material_id"] for r in full_audit}
    manifest = json.loads((ROOT / "external_test_MANIFEST.json").read_text())
    manifest_ids = {r["material_id"] for r in manifest["records"]}
    if observed != manifest_ids:
        raise SystemExit(
            f"Full aggregate audit does not cover frozen 65-system corpus: "
            f"missing={sorted(manifest_ids-observed)}, extra={sorted(observed-manifest_ids)}"
        )
    if not sentinels.issubset(observed):
        raise SystemExit("One or more frozen implementation sentinels are absent")

    with tempfile.TemporaryDirectory(prefix="qoi_confirmatory63_") as td:
        filtered = Path(td) / "filtered"
        keep = lambda row: row.get("material_id") not in sentinels

        counts = {
            "rows": filter_csv(
                aggregate_dir / "formal_external_e2e_rows.csv",
                filtered / "formal_external_e2e_rows.csv",
                keep,
            ),
            "materials": filter_csv(
                aggregate_dir / "material_audit.csv",
                filtered / "material_audit.csv",
                keep,
            ),
            "material_failures": filter_csv(
                aggregate_dir / "formal_external_e2e_failures.csv",
                filtered / "formal_external_e2e_failures.csv",
                keep,
            ),
            "row_failures": filter_csv(
                aggregate_dir / "formal_external_e2e_row_failures.csv",
                filtered / "formal_external_e2e_row_failures.csv",
                keep,
            ),
        }
        if counts["materials"] != expected_n:
            raise SystemExit(
                f"Confirmatory filter produced {counts['materials']} materials, expected {expected_n}"
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                sys.executable,
                str(AGGREGATOR),
                "--input-root",
                str(filtered),
                "--output-dir",
                str(output_dir),
            ],
            check=True,
        )

    summary_path = output_dir / "summary.json"
    summary = json.loads(summary_path.read_text())
    if int(summary["n_materials_observed"]) != expected_n:
        raise SystemExit("Confirmatory aggregate material count mismatch")
    if int(summary["n_materials_complete"]) != expected_n:
        raise SystemExit("Confirmatory cohort contains a hard material pipeline failure")
    if summary["eligible_A1_counts_completed_materials"] != expected_eligible:
        raise SystemExit(
            "Confirmatory eligibility counts drifted: "
            f"{summary['eligible_A1_counts_completed_materials']} != {expected_eligible}"
        )

    metadata = {
        "analysis_role": "primary_confirmatory_external_rate_fidelity",
        "confirmatory_n": expected_n,
        "excluded_implementation_sentinels": sorted(sentinels),
        "split_file": str(SPLIT.relative_to(ROOT)),
        "split_sha256": sha256(SPLIT),
        "source_full_aggregate_dir": str(aggregate_dir),
        "filtered_counts": counts,
        "expected_A1_eligible_counts": expected_eligible,
        "status": "PASS",
    }
    (output_dir / "confirmatory_metadata.json").write_text(
        json.dumps(metadata, indent=2)
    )
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
