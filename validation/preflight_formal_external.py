#!/usr/bin/env python3
"""Preflight integrity checks for the formal frozen external benchmark.

This script intentionally contains no scientific computation. It verifies that
all frozen inputs and the staged sampling policy still reproduce already-public
release invariants before any external codec run is allowed to start.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "external_test_MANIFEST.json"
FLOORS = ROOT / "stability" / "stability_floor_A1.csv"
MASTER = ROOT / "benchmark" / "master_benchmark_full.csv"
TIGHT = ROOT / "benchmark" / "master_benchmark_tight_ladder.csv"

EXPECTED_EXTERNAL_N = 65
EXPECTED_DOMAINS = {"bulk": 37, "vacuum2d": 28}
EXPECTED_ELIGIBLE_A1 = {1e-4: 18, 1e-3: 44, 1e-2: 59}
EXPECTED_MASTER_ROWS = 6343
EXPECTED_BASE_ROWS = 4627
EXPECTED_TIGHT_ROWS = 1716
EXPECTED_DEV_MATERIALS = 254
EXPECTED_TIGHT_MATERIALS = 143


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    records = manifest["records"]
    assert manifest.get("frozen") is True, "external manifest lost frozen=true"
    assert len(records) == EXPECTED_EXTERNAL_N, (len(records), EXPECTED_EXTERNAL_N)

    domains: dict[str, int] = {}
    for record in records:
        domains[record["domain"]] = domains.get(record["domain"], 0) + 1
        assert len(record["sha256"]) == 64, f"invalid SHA256 for {record['material_id']}"
        assert int(record["source_bytes"]) > 0, f"invalid source size for {record['material_id']}"
    assert domains == EXPECTED_DOMAINS, (domains, EXPECTED_DOMAINS)

    floor_rows = read_csv(FLOORS)
    floors = {r["material_id"]: float(r["stability_floor_A1_e"]) for r in floor_rows}
    external_ids = {r["material_id"] for r in records}
    missing_floors = sorted(external_ids - set(floors))
    assert not missing_floors, f"external materials missing A.1 floors: {missing_floors}"

    eligible_counts = {
        tau: sum(floors[mid] < tau for mid in external_ids)
        for tau in EXPECTED_ELIGIBLE_A1
    }
    assert eligible_counts == EXPECTED_ELIGIBLE_A1, (
        eligible_counts,
        EXPECTED_ELIGIBLE_A1,
    )

    master_rows = read_csv(MASTER)
    assert len(master_rows) == EXPECTED_MASTER_ROWS, (
        len(master_rows),
        EXPECTED_MASTER_ROWS,
    )
    base_rows = [r for r in master_rows if r["ladder"] == "base"]
    tight_rows = [r for r in master_rows if r["ladder"] == "tight"]
    assert len(base_rows) == EXPECTED_BASE_ROWS, (len(base_rows), EXPECTED_BASE_ROWS)
    assert len(tight_rows) == EXPECTED_TIGHT_ROWS, (len(tight_rows), EXPECTED_TIGHT_ROWS)

    dev_materials = {r["material_id"] for r in base_rows}
    tight_materials = {r["material_id"] for r in tight_rows}
    assert len(dev_materials) == EXPECTED_DEV_MATERIALS
    assert len(tight_materials) == EXPECTED_TIGHT_MATERIALS

    # The frozen tight ladder is exactly the development materials admissible at
    # 1e-3 e under Protocol A.1. This is the policy replicated externally.
    expected_tight_materials = {mid for mid in dev_materials if floors[mid] < 1e-3}
    assert tight_materials == expected_tight_materials, (
        len(tight_materials),
        len(expected_tight_materials),
    )

    base_tols = sorted({float(r["nominal_tolerance_relative"]) for r in base_rows})
    tight_tols = sorted({float(r["nominal_tolerance_relative"]) for r in tight_rows})
    assert len(base_tols) == 9, base_tols
    assert base_tols[0] == 1e-5 and base_tols[-1] == 1e-1, base_tols
    assert len(tight_tols) == 4, tight_tols
    assert tight_tols[0] == 1e-7 and tight_tols[-1] == 3e-6, tight_tols

    # Every released row must already satisfy the codec L_inf contract.
    assert all(r["bound_respected"].strip().lower() == "true" for r in master_rows)

    result = {
        "status": "PASS",
        "external_materials": len(records),
        "domains": domains,
        "eligible_A1": {f"{tau:.0e}": n for tau, n in eligible_counts.items()},
        "development_rows": len(master_rows),
        "base_rows": len(base_rows),
        "tight_rows": len(tight_rows),
        "development_materials": len(dev_materials),
        "tight_materials": len(tight_materials),
        "base_tolerances": base_tols,
        "tight_tolerances": tight_tols,
        "all_development_bounds_respected": True,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
