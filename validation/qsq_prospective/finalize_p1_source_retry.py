#!/usr/bin/env python3
"""Merge targeted P1 source-timeout retries into the additive P1 result.

Only keys present in the previously committed P1 failures table may be replaced.
The historical benchmark is never modified. The script records the before/after
failure sets and recomputes the completed-common-ladder audit from the repaired
additive P1 table.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT_DEFAULT = SCRIPT_DIR.parents[1]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--retry-root", type=Path, required=True)
    p.add_argument("--bootstrap-reps", type=int, default=20000)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def key(r: dict[str, str]) -> tuple[str, str, float]:
    return r["material_id"], r["codec"], float(r["nominal_tolerance_relative"])


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    args = parse_args()
    repo = args.repo_root.resolve()
    retry_root = args.retry_root.resolve()
    p1 = repo / "validation" / "qsq_prospective" / "p1_common_tight"
    audit = repo / "analysis" / "research_upgrade"

    initial_rows = read_csv(p1 / "rows.csv")
    initial_failures = read_csv(p1 / "failures.csv")
    if len(initial_rows) + len(initial_failures) != 1332:
        raise RuntimeError("initial P1 accounting is not 1332")
    failed_keys = {key(r) for r in initial_failures}
    if not failed_keys:
        raise RuntimeError("no initial P1 failures to repair")
    if len(failed_keys) != len(initial_failures):
        raise RuntimeError("duplicate initial failure keys")

    retry_rows: list[dict[str, str]] = []
    retry_failures: list[dict[str, str]] = []
    for path in sorted(retry_root.rglob("rows_shard_*.csv")):
        retry_rows.extend(read_csv(path))
    for path in sorted(retry_root.rglob("failures_shard_*.csv")):
        retry_failures.extend(read_csv(path))
    if not retry_rows and not retry_failures:
        raise RuntimeError("no retry outputs found")

    retry_keys = [key(r) for r in retry_rows] + [key(r) for r in retry_failures]
    if len(set(retry_keys)) != len(retry_keys):
        raise RuntimeError("duplicate retry keys")
    extra = set(retry_keys) - failed_keys
    if extra:
        raise RuntimeError(f"retry contains {len(extra)} keys not in initial failure set")
    missing = failed_keys - set(retry_keys)
    if missing:
        raise RuntimeError(f"retry omitted {len(missing)} initial failure keys")

    final_rows = initial_rows + retry_rows
    final_failures = retry_failures
    final_keys = [key(r) for r in final_rows] + [key(r) for r in final_failures]
    if len(final_keys) != 1332 or len(set(final_keys)) != 1332:
        raise RuntimeError("repaired P1 accounting is not exactly 1332 unique keys")

    final_rows.sort(key=lambda r: (r["material_id"], r["codec"], float(r["nominal_tolerance_relative"])))
    final_failures.sort(key=lambda r: (r["material_id"], r["codec"], float(r["nominal_tolerance_relative"])))
    row_fields = list(initial_rows[0].keys())
    failure_fields = list(initial_failures[0].keys())

    before_path = p1 / "initial_source_timeout_failures.csv"
    if not before_path.exists():
        write_csv(before_path, initial_failures, failure_fields)
    write_csv(p1 / "rows.csv", final_rows, row_fields)
    write_csv(p1 / "failures.csv", final_failures, failure_fields)

    sys.path.insert(0, str(SCRIPT_DIR))
    import aggregate_p1_common_tight as agg  # type: ignore
    summary, decisions = agg.audit_common_ladder(repo, final_rows, args.bootstrap_reps)
    agg.write_csv(audit / "p1_common_tight_summary.csv", summary)
    agg.write_csv(audit / "p1_common_tight_decisions.csv", decisions)

    report = [
        "# P1 completed common tight-ladder audit",
        "",
        f"Execution status: **{'COMPLETE' if not final_failures else 'COMPLETE_WITH_RECORDED_FAILURES'}**",
        "",
        f"Pre-registered jobs accounted: **1332/1332**; successful rows: **{len(final_rows)}**; recorded failures: **{len(final_failures)}**.",
        "",
        "The first P1 pass recorded 24 source-download timeouts, all belonging to two NOMAD materials. Those keys were retried without changing codec, Bader, tolerance, or source-identity semantics. The original timeout table is retained as `validation/qsq_prospective/p1_common_tight/initial_source_timeout_failures.csv`.",
        "",
        "The historical 6,343-row benchmark remains unchanged. These are additive prospective measurements used only to remove unequal tight-ladder search opportunity.",
        "",
        "| Bader threshold | Numerical pass | No pass observed | QSQ screen-rejected | Screen-rejected among no-pass | 95% material-cluster CI | No-pass risk: eligible | No-pass risk: screen-rejected | Risk ratio |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in summary:
        report.append(
            f"| {s['tau_e']:.0e} e | {s['numerical_pass']} | {s['no_pass_observed']} | {s['non_evaluable']} | "
            f"{100*s['fraction_no_pass_non_evaluable']:.1f}% | {100*s['material_cluster_ci_low']:.1f}–{100*s['material_cluster_ci_high']:.1f}% | "
            f"{100*s['no_pass_risk_eligible']:.1f}% | {100*s['no_pass_risk_non_evaluable']:.1f}% | {s['risk_ratio_non_evaluable_vs_eligible']:.2f}× |"
        )
    report += [
        "",
        "## Interpretation boundary",
        "",
        "After equalizing the pre-registered tight settings, this audit estimates the association between the frozen QSQ screen and failure to find a numerically passing reconstruction. It does not establish that a particular codec discrepancy was caused by reference instability, and it does not prospectively validate the five-seed QSQ screen. P2 addresses fresh-perturbation validation.",
        "",
        "The primary quantities are no-pass risk in eligible versus screen-rejected groups and their material-cluster uncertainty. The fraction of no-pass outcomes located in the screen-rejected group must always be reported together with screen-rejection prevalence.",
    ]
    (audit / "P1_COMMON_TIGHT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    old_manifest = json.loads((p1 / "execution_manifest.json").read_text(encoding="utf-8"))
    retry_record = {
        "initial_successful_rows": len(initial_rows),
        "initial_failures": len(initial_failures),
        "initial_failure_stages": sorted({r.get("stage", "") for r in initial_failures}),
        "retry_successful_rows": len(retry_rows),
        "retry_failures": len(retry_failures),
        "final_successful_rows": len(final_rows),
        "final_failures": len(final_failures),
        "initial_failure_sha256": sha256_file(before_path),
        "retry_did_not_change_scientific_parameters": True,
    }
    (p1 / "source_retry_record.json").write_text(json.dumps(retry_record, indent=2), encoding="utf-8")
    old_manifest.update({
        "status": "COMPLETE" if not final_failures else "COMPLETE_WITH_RECORDED_FAILURES",
        "successful_rows": len(final_rows),
        "failed_rows": len(final_failures),
        "accounted_rows": 1332,
        "rows_sha256": sha256_file(p1 / "rows.csv"),
        "failures_sha256": sha256_file(p1 / "failures.csv"),
        "audit_summary_sha256": sha256_file(audit / "p1_common_tight_summary.csv"),
        "source_timeout_retry": retry_record,
    })
    (p1 / "execution_manifest.json").write_text(json.dumps(old_manifest, indent=2), encoding="utf-8")
    print(json.dumps(retry_record, indent=2))
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
