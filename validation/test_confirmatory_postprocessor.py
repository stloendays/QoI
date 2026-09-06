#!/usr/bin/env python3
"""Synthetic contract test for the all65 -> confirmatory63 postprocessor."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "validation" / "build_confirmatory_external.py"
CODECS = ("ZFP", "SZ3", "SPERR")
TAUS = ("1e-4", "1e-3", "1e-2")


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None and rows:
        fields = list(rows[0].keys())
    if not fields:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    manifest = json.loads((ROOT / "external_test_MANIFEST.json").read_text())
    records = manifest["records"]
    with (ROOT / "stability" / "stability_floor_A1.csv").open(newline="") as f:
        floors = {
            r["material_id"]: float(r["stability_floor_A1_e"])
            for r in csv.DictReader(f)
        }

    with tempfile.TemporaryDirectory(prefix="qoi_confirmatory_contract_") as td:
        td = Path(td)
        full = td / "all65"
        out = td / "confirmatory63"

        audits: list[dict[str, object]] = []
        rows: list[dict[str, object]] = []
        for rec in records:
            mid = rec["material_id"]
            floor = floors[mid]
            audits.append(
                {
                    "material_id": mid,
                    "domain": rec["domain"],
                    "stability_floor_A1_e": floor,
                    "status": "COMPLETE",
                }
            )
            for codec_index, codec in enumerate(CODECS):
                row: dict[str, object] = {
                    "material_id": mid,
                    "domain": rec["domain"],
                    "codec": codec,
                    "nominal_tolerance_relative": 1e-5,
                    "compression_ratio": 10.0 - codec_index,
                    "bits_per_value": 0.8 + codec_index * 0.1,
                    "realized_Linf": 1e-6,
                    "realized_Linf_over_nominal": 0.5,
                    "Bader_error_fixed_e": 1e-6,
                    "Bader_error_resolved_e": 1e-6,
                    "atom_domain_migration_fraction": 0.0,
                    "ladder_stage": "base",
                    "bound_respected": True,
                    "source_has_negative_density": False,
                }
                for tau in TAUS:
                    row[f"certified_at_{tau}"] = floor < float(tau)
                rows.append(row)

        write_csv(full / "material_audit.csv", audits)
        write_csv(full / "formal_external_e2e_rows.csv", rows)
        write_csv(
            full / "formal_external_e2e_failures.csv",
            [],
            ["material_id", "error_type", "error"],
        )
        write_csv(
            full / "formal_external_e2e_row_failures.csv",
            [],
            [
                "material_id",
                "corpus",
                "domain",
                "ladder",
                "codec",
                "nominal_tolerance_relative",
                "stage",
                "category",
                "detail",
            ],
        )

        subprocess.run(
            [
                sys.executable,
                str(BUILD),
                "--aggregate-dir",
                str(full),
                "--output-dir",
                str(out),
            ],
            check=True,
        )

        summary = json.loads((out / "summary.json").read_text())
        assert summary["n_materials_observed"] == 63
        assert summary["n_materials_complete"] == 63
        assert summary["eligible_A1_counts_completed_materials"] == {
            "1e-4": 16,
            "1e-3": 42,
            "1e-2": 57,
        }
        metadata = json.loads((out / "confirmatory_metadata.json").read_text())
        assert metadata["confirmatory_n"] == 63
        assert len(metadata["excluded_implementation_sentinels"]) == 2
        assert metadata["status"] == "PASS"

    print("confirmatory postprocessor contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
