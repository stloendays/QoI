#!/usr/bin/env python3
"""Fast synthetic contract test for external material-level aggregation.

No scientific computation is performed.  The test constructs two manifest-backed
materials with deliberately different eligibility/certification outcomes and one
row-level failure, runs the real aggregator, and checks denominator, CCR and
pairwise semantics.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "validation" / "aggregate_formal_external.py"

AFLOW_ID = "aflow-Ni1_ICSD_181716"
NOMAD_ID = "nomad2d-0XHkHlmw3DQ_"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def make_row(
    mid: str,
    codec: str,
    ratio: float,
    cert_1e4: bool,
    cert_1e3: bool,
    cert_1e2: bool,
) -> dict[str, object]:
    return {
        "material_id": mid,
        "codec": codec,
        "nominal_tolerance_relative": 1e-5,
        "compression_ratio": ratio,
        "bits_per_value": 8.0 / ratio,
        "realized_Linf": 1e-6,
        "realized_Linf_over_nominal": 0.5,
        "Bader_error_fixed_e": 1e-6,
        "Bader_error_resolved_e": 2e-5,
        "atom_domain_migration_fraction": 1e-4,
        "ladder_stage": "base",
        "bound_respected": True,
        "source_has_negative_density": False,
        "certified_at_1e-4": cert_1e4,
        "certified_at_1e-3": cert_1e3,
        "certified_at_1e-2": cert_1e2,
    }


def main() -> int:
    manifest = json.loads((ROOT / "external_test_MANIFEST.json").read_text())
    ids = {r["material_id"] for r in manifest["records"]}
    assert AFLOW_ID in ids and NOMAD_ID in ids

    with tempfile.TemporaryDirectory(prefix="qoi_agg_contract_") as td:
        work = Path(td)
        inp = work / "in"
        out = work / "out"

        # AFLOW is eligible already at 1e-4 in this synthetic audit. ZFP passes,
        # SZ3 has a successful row but no 1e-4 certified point, and SPERR has only
        # a row-level solver failure (no successful row).
        # NOMAD is non-evaluable at 1e-4 but eligible at 1e-3 and above.
        rows = [
            make_row(AFLOW_ID, "ZFP", 10.0, True, True, True),
            make_row(AFLOW_ID, "SZ3", 8.0, False, True, True),
            make_row(NOMAD_ID, "ZFP", 12.0, False, True, True),
            make_row(NOMAD_ID, "SZ3", 7.0, False, True, True),
            make_row(NOMAD_ID, "SPERR", 6.0, False, True, True),
        ]
        audits = [
            {
                "material_id": AFLOW_ID,
                "domain": "bulk",
                "stability_floor_A1_e": 5e-5,
                "status": "COMPLETE",
            },
            {
                "material_id": NOMAD_ID,
                "domain": "vacuum2d",
                "stability_floor_A1_e": 5e-4,
                "status": "COMPLETE",
            },
        ]
        row_failures = [
            {
                "material_id": AFLOW_ID,
                "corpus": "external",
                "domain": "bulk",
                "ladder": "base",
                "codec": "SPERR",
                "nominal_tolerance_relative": 1e-5,
                "stage": "sperr@1e-05:resolved_bader",
                "category": "bader_solver_failure",
                "detail": "SyntheticFailure: expected",
            }
        ]

        write_csv(inp / "formal_external_e2e_rows.csv", rows)
        write_csv(inp / "material_audit.csv", audits)
        write_csv(inp / "formal_external_e2e_row_failures.csv", row_failures)
        write_csv(
            inp / "formal_external_e2e_failures.csv",
            [],
        )

        subprocess.run(
            [
                sys.executable,
                str(AGG),
                "--input-root",
                str(inp),
                "--output-dir",
                str(out),
            ],
            check=True,
        )

        best = read_csv(out / "best_certified_external.csv")
        best_idx = {(r["material_id"], r["codec"], r["tau_e"]): r for r in best}
        assert best_idx[(AFLOW_ID, "ZFP", "1e-4")]["status"] == "CERTIFIED"
        assert best_idx[(AFLOW_ID, "ZFP", "1e-4")]["CCR"] == "10.0"
        assert best_idx[(AFLOW_ID, "SZ3", "1e-4")]["status"] == "NOT_CERTIFIED"
        assert (
            best_idx[(AFLOW_ID, "SPERR", "1e-4")]["status"]
            == "ROW_PIPELINE_FAILURE_NO_SUCCESSFUL_POINT"
        )
        assert best_idx[(NOMAD_ID, "ZFP", "1e-4")]["status"] == "NON_EVALUABLE_BADER_UNSTABLE"

        summary = read_csv(out / "external_summary_a1.csv")
        sidx = {
            (r["threshold_e"], r["stratum"], r["codec"]): r
            for r in summary
        }
        zfp_1e4 = sidx[("0.0001", "overall", "zfp")]
        assert zfp_1e4["n_admitted"] == "1"
        assert zfp_1e4["n_non_evaluable"] == "1"
        assert zfp_1e4["n_certified"] == "1"
        sperr_1e4 = sidx[("0.0001", "overall", "sperr")]
        assert sperr_1e4["n_admitted"] == "1"
        assert sperr_1e4["n_certified"] == "0"
        assert sperr_1e4["n_row_failure_affected"] == "1"

        pairs = read_csv(out / "pairwise_external.csv")
        pidx = {
            (r["threshold_e"], r["stratum"], r["codec_a"], r["codec_b"]): r
            for r in pairs
        }
        sz3_zfp = pidx[("0.0001", "overall", "sz3", "zfp")]
        assert sz3_zfp["n"] == "1"
        assert sz3_zfp["frac_b_wins"] == "1.0"
        sperr_sz3 = pidx[("0.0001", "overall", "sperr", "sz3")]
        assert sperr_sz3["frac_ties"] == "1.0"  # neither has CCR at 1e-4

        merged_failures = read_csv(out / "formal_external_e2e_row_failures.csv")
        assert len(merged_failures) == 1
        assert merged_failures[0]["category"] == "bader_solver_failure"

        top = json.loads((out / "summary.json").read_text())
        assert top["n_row_failures"] == 1
        assert top["n_material_pipeline_failures"] == 0
        assert top["all_codec_bounds_respected"] is True

    print("aggregate semantics contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
