#!/usr/bin/env python3
"""Verify the frozen 65/2/63 external rate-fidelity reporting split.

This check is deliberately separate from the existing 65-system frozen-input
preflight so the implementation pilot is not redefined.  It must pass before the
corpus-scale rate-fidelity workflow is launched.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "external_test_MANIFEST.json"
FLOORS = ROOT / "stability" / "stability_floor_A1.csv"
SPLIT = ROOT / "validation" / "external_rate_fidelity_split.json"

EXPECTED_SENTINELS = {
    "aflow-Ni1_ICSD_181716": "bulk",
    "nomad2d-0XHkHlmw3DQ_": "vacuum2d",
}
EXPECTED_CONFIRMATORY_N = 63
EXPECTED_CONFIRMATORY_STRATA = {"bulk": 36, "vacuum2d": 27}
EXPECTED_CONFIRMATORY_ELIGIBLE = {"1e-4": 16, "1e-3": 42, "1e-2": 57}


def main() -> int:
    manifest_payload = json.loads(MANIFEST.read_text())
    split = json.loads(SPLIT.read_text())
    assert split.get("frozen") is True, "rate-fidelity split is not frozen"

    records = {r["material_id"]: r for r in manifest_payload["records"]}
    sentinels = {
        r["material_id"]: r["domain"]
        for r in split["implementation_sentinels"]
    }
    assert sentinels == EXPECTED_SENTINELS, (sentinels, EXPECTED_SENTINELS)
    assert set(sentinels).issubset(records), "sentinel absent from frozen manifest"
    for mid, domain in sentinels.items():
        assert records[mid]["domain"] == domain

    confirmatory_ids = sorted(set(records) - set(sentinels))
    assert len(confirmatory_ids) == EXPECTED_CONFIRMATORY_N

    strata: dict[str, int] = {}
    for mid in confirmatory_ids:
        domain = records[mid]["domain"]
        strata[domain] = strata.get(domain, 0) + 1
    assert strata == EXPECTED_CONFIRMATORY_STRATA, (
        strata,
        EXPECTED_CONFIRMATORY_STRATA,
    )

    with FLOORS.open(newline="") as f:
        floor_rows = list(csv.DictReader(f))
    floors = {r["material_id"]: float(r["stability_floor_A1_e"]) for r in floor_rows}
    missing = sorted(set(confirmatory_ids) - set(floors))
    assert not missing, f"confirmatory materials missing A.1 floor: {missing}"

    eligible = {
        tau: sum(floors[mid] < float(tau) for mid in confirmatory_ids)
        for tau in EXPECTED_CONFIRMATORY_ELIGIBLE
    }
    assert eligible == EXPECTED_CONFIRMATORY_ELIGIBLE, (
        eligible,
        EXPECTED_CONFIRMATORY_ELIGIBLE,
    )

    declared = split["confirmatory_rate_fidelity_cohort"]
    assert int(declared["n"]) == EXPECTED_CONFIRMATORY_N
    assert declared["strata"] == EXPECTED_CONFIRMATORY_STRATA
    assert declared["expected_A1_eligible_counts"] == EXPECTED_CONFIRMATORY_ELIGIBLE

    result = {
        "status": "PASS",
        "full_corpus_n": len(records),
        "implementation_sentinels": sorted(sentinels),
        "confirmatory_n": len(confirmatory_ids),
        "confirmatory_strata": strata,
        "confirmatory_A1_eligible": eligible,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
