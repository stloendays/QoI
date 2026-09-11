#!/usr/bin/env python3
"""Aggregate P1 shard outputs and audit the completed common tight ladder.

This script never mutates the historical master benchmark. It verifies that
every pre-registered P1 work-order row is accounted for exactly once, writes an
additive prospective table, and computes a new common-search-opportunity audit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

TAUS = (1e-4, 1e-3, 1e-2)
TAU_SUFFIX = {1e-4: "0.0001", 1e-3: "0.001", 1e-2: "0.01"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--shards-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--audit-dir", type=Path, required=True)
    p.add_argument("--bootstrap-reps", type=int, default=20000)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if fields:
            writer.writeheader()
            writer.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def key(row: dict[str, str]) -> tuple[str, str, float]:
    return row["material_id"], row["codec"], float(row["nominal_tolerance_relative"])


def boolish(x: Any) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes"}


def material_bootstrap(decisions: list[dict[str, Any]], reps: int, seed: int) -> tuple[float, float]:
    by_material: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for d in decisions:
        by_material[d["material_id"]].append(d)
    materials = np.array(sorted(by_material), dtype=object)
    rng = np.random.default_rng(seed)
    vals: list[float] = []
    for _ in range(reps):
        sample = rng.choice(materials, size=len(materials), replace=True)
        num = den = 0
        for m in sample:
            for d in by_material[str(m)]:
                if d["no_pass"]:
                    den += 1
                    num += int(d["non_evaluable"])
        if den:
            vals.append(num / den)
    if not vals:
        return float("nan"), float("nan")
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


def audit_common_ladder(repo_root: Path, p1_rows: list[dict[str, str]], reps: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base = read_csv(repo_root / "benchmark" / "master_benchmark_base_ladder.csv")
    tight = read_csv(repo_root / "benchmark" / "master_benchmark_tight_ladder.csv")
    combined = base + tight + p1_rows

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in combined:
        grouped[(row["material_id"], row["codec"])].append(row)
    if len(grouped) != 254 * 3:
        raise RuntimeError(f"expected 762 material-codec groups, found {len(grouped)}")

    decision_rows: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    for tau in TAUS:
        suffix = TAU_SUFFIX[tau]
        decisions_tau: list[dict[str, Any]] = []
        for (material, codec), rows in sorted(grouped.items()):
            eligibility_values = {boolish(r[f"eligible_A1_at_{suffix}"]) for r in rows}
            if len(eligibility_values) != 1:
                raise RuntimeError(f"eligibility drift for {material}/{codec}/{tau}")
            eligible = next(iter(eligibility_values))
            finite_errors = []
            for r in rows:
                try:
                    value = float(r["Bader_error_resolved_e"])
                    if np.isfinite(value):
                        finite_errors.append(value)
                except (ValueError, TypeError):
                    pass
            numerical_pass = any(v < tau for v in finite_errors)
            d = {
                "material_id": material,
                "codec": codec,
                "tau_e": tau,
                "eligible": eligible,
                "numerical_pass": numerical_pass,
                "no_pass": not numerical_pass,
                "non_evaluable": not eligible,
                "qualified_pass": bool(eligible and numerical_pass),
                "eligible_no_pass": bool(eligible and not numerical_pass),
                "non_evaluable_no_pass": bool((not eligible) and (not numerical_pass)),
                "non_evaluable_pass": bool((not eligible) and numerical_pass),
                "n_successful_rows_available": len(finite_errors),
            }
            decisions_tau.append(d)
            decision_rows.append(d)

        n = len(decisions_tau)
        no_pass = sum(d["no_pass"] for d in decisions_tau)
        non_eval_no_pass = sum(d["non_evaluable_no_pass"] for d in decisions_tau)
        non_eval = sum(d["non_evaluable"] for d in decisions_tau)
        numerical_pass = sum(d["numerical_pass"] for d in decisions_tau)
        non_eval_pass = sum(d["non_evaluable_pass"] for d in decisions_tau)
        qpass = sum(d["qualified_pass"] for d in decisions_tau)
        eligible_no_pass = sum(d["eligible_no_pass"] for d in decisions_tau)
        ci_lo, ci_hi = material_bootstrap(decisions_tau, reps, seed=int(tau * 1e8) + 20260911)
        eligible_decisions = n - non_eval
        no_pass_eligible = eligible_no_pass / eligible_decisions if eligible_decisions else float("nan")
        no_pass_non_eval = non_eval_no_pass / non_eval if non_eval else float("nan")
        rr = no_pass_non_eval / no_pass_eligible if no_pass_eligible > 0 else float("inf")
        summary.append({
            "design": "completed_common_tight",
            "tau_e": tau,
            "n_decisions": n,
            "numerical_pass": numerical_pass,
            "no_pass_observed": no_pass,
            "qualified_pass": qpass,
            "eligible_no_pass": eligible_no_pass,
            "non_evaluable": non_eval,
            "non_evaluable_no_pass": non_eval_no_pass,
            "non_evaluable_pass": non_eval_pass,
            "non_evaluable_share": non_eval / n,
            "fraction_no_pass_non_evaluable": non_eval_no_pass / no_pass if no_pass else float("nan"),
            "material_cluster_ci_low": ci_lo,
            "material_cluster_ci_high": ci_hi,
            "fraction_numerical_pass_non_evaluable": non_eval_pass / numerical_pass if numerical_pass else float("nan"),
            "no_pass_risk_eligible": no_pass_eligible,
            "no_pass_risk_non_evaluable": no_pass_non_eval,
            "risk_ratio_non_evaluable_vs_eligible": rr,
        })
    return summary, decision_rows


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    shard_root = args.shards_root.resolve()
    output_dir = args.output_dir.resolve()
    audit_dir = args.audit_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    work_path = repo_root / "validation" / "qsq_prospective" / "missing_tight_jobs.csv"
    work = [r for r in read_csv(work_path) if r.get("status") == "PREPARED_NOT_EXECUTED"]
    if len(work) != 1332:
        raise RuntimeError(f"expected 1332 P1 work-order rows, found {len(work)}")
    work_keys = [key(r) for r in work]
    if len(set(work_keys)) != len(work_keys):
        raise RuntimeError("duplicate keys in P1 work order")

    row_files = sorted(shard_root.rglob("rows_shard_*.csv"))
    failure_files = sorted(shard_root.rglob("failures_shard_*.csv"))
    manifest_files = sorted(shard_root.rglob("manifest_shard_*.json"))
    if not row_files or not manifest_files:
        raise RuntimeError("no P1 shard outputs found")

    rows: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []
    manifests: list[dict[str, Any]] = []
    for path in row_files:
        rows.extend(read_csv(path))
    for path in failure_files:
        failures.extend(read_csv(path))
    for path in manifest_files:
        manifests.append(json.loads(path.read_text(encoding="utf-8")))

    row_keys = [key(r) for r in rows]
    fail_keys = [key(r) for r in failures]
    if len(set(row_keys)) != len(row_keys):
        raise RuntimeError("duplicate successful P1 keys across shards")
    if len(set(fail_keys)) != len(fail_keys):
        raise RuntimeError("duplicate failed P1 keys across shards")
    if set(row_keys) & set(fail_keys):
        raise RuntimeError("P1 key appears as both success and failure")
    accounted = set(row_keys) | set(fail_keys)
    if accounted != set(work_keys):
        missing = set(work_keys) - accounted
        extra = accounted - set(work_keys)
        raise RuntimeError(f"P1 accounting mismatch: missing={len(missing)} extra={len(extra)}")

    rows.sort(key=lambda r: (r["material_id"], r["codec"], float(r["nominal_tolerance_relative"])))
    failures.sort(key=lambda r: (r["material_id"], r["codec"], float(r["nominal_tolerance_relative"])))
    row_fields = list(rows[0].keys()) if rows else []
    failure_fields = list(failures[0].keys()) if failures else [
        "material_id", "codec", "nominal_tolerance_relative", "codec_config", "field_fingerprint", "status", "stage", "error"
    ]
    rows_path = output_dir / "rows.csv"
    failures_path = output_dir / "failures.csv"
    write_csv(rows_path, rows, row_fields)
    write_csv(failures_path, failures, failure_fields)

    summary, decisions = audit_common_ladder(repo_root, rows, args.bootstrap_reps)
    summary_path = audit_dir / "p1_common_tight_summary.csv"
    decisions_path = audit_dir / "p1_common_tight_decisions.csv"
    write_csv(summary_path, summary)
    write_csv(decisions_path, decisions)

    by_codec_success = Counter(r["codec"] for r in rows)
    by_stage_failure = Counter(r.get("stage", "") for r in failures)
    manifest = {
        "status": "COMPLETE" if not failures else "COMPLETE_WITH_RECORDED_FAILURES",
        "work_order_rows": len(work),
        "successful_rows": len(rows),
        "failed_rows": len(failures),
        "accounted_rows": len(rows) + len(failures),
        "successful_by_codec": dict(sorted(by_codec_success.items())),
        "failures_by_stage": dict(sorted(by_stage_failure.items())),
        "shards_found": len(manifests),
        "work_order_sha256": sha256_file(work_path),
        "rows_sha256": sha256_file(rows_path),
        "failures_sha256": sha256_file(failures_path),
        "historical_master_unchanged": True,
        "audit_summary_sha256": sha256_file(summary_path),
    }
    (output_dir / "execution_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = [
        "# P1 completed common tight-ladder audit",
        "",
        f"Execution status: **{manifest['status']}**",
        "",
        f"Pre-registered jobs accounted: **{manifest['accounted_rows']}/{manifest['work_order_rows']}**; successful rows: **{manifest['successful_rows']}**; recorded failures: **{manifest['failed_rows']}**.",
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
    report.extend([
        "",
        "## Interpretation boundary",
        "",
        "This audit answers a narrower and cleaner question than the historical full-record Figure 3: after giving every development material the same pre-registered tight settings for all three codecs, how strongly is failure to find a numerically passing reconstruction associated with the frozen QSQ screen? It does not show that a codec discrepancy was caused by reference instability, and it does not validate the five-seed QSQ screen against fresh perturbations. P2 addresses the latter.",
        "",
        "The primary quantities to carry forward are the completed-common-ladder no-pass risks in eligible versus screen-rejected groups, their material-cluster uncertainty, and the risk ratio. The fraction of no-pass outcomes that happen to lie in the screen-rejected group must always be reported together with screen-rejection prevalence.",
    ])
    (audit_dir / "P1_COMMON_TIGHT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
