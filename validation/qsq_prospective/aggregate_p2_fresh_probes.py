#!/usr/bin/env python3
"""Aggregate the prospective 59-seed P2 QSQ validation without retuning the gate."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import beta

TAUS = (1e-4, 1e-3, 1e-2)
PRIMARY_TAU = 1e-3


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
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if fields:
            w.writeheader(); w.writerows(rows)


def key(r: dict[str, str]) -> tuple[str, int]:
    return r["material_id"], int(r["seed_label"])


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def exact_upper_95(k: int, n: int) -> float:
    if n <= 0:
        return float("nan")
    if k < 0 or k > n:
        raise ValueError((k, n))
    if k == n:
        return 1.0
    return float(beta.ppf(0.95, k + 1, n - k))


def load_frozen_floors(repo: Path) -> dict[str, float]:
    seen: dict[str, set[float]] = defaultdict(set)
    with (repo / "benchmark" / "master_benchmark_full.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            seen[r["material_id"]].add(float(r["stability_floor_A1_e"]))
    out: dict[str, float] = {}
    for m, vals in seen.items():
        if len(vals) != 1:
            raise RuntimeError(f"frozen QSQ floor drift for {m}: {vals}")
        out[m] = next(iter(vals))
    if len(out) != 254:
        raise RuntimeError(f"development floor population changed: {len(out)}")
    return out


def bootstrap_group(material_rows: list[dict[str, Any]], reps: int, conservative: bool, seed: int) -> tuple[float, float]:
    if not material_rows:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = np.arange(len(material_rows))
    vals: list[float] = []
    for _ in range(reps):
        sample = rng.choice(idx, size=len(idx), replace=True)
        k = n = 0
        for i in sample:
            r = material_rows[int(i)]
            if conservative:
                k += int(r["n_exceed"]) + int(r["n_fail"])
                n += int(r["n_planned"])
            else:
                k += int(r["n_exceed"])
                n += int(r["n_valid"])
        if n:
            vals.append(k / n)
    if not vals:
        return float("nan"), float("nan")
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


def main() -> int:
    args = parse_args()
    repo = args.repo_root.resolve()
    shards = args.shards_root.resolve()
    outdir = args.output_dir.resolve()
    audit = args.audit_dir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    audit.mkdir(parents=True, exist_ok=True)

    work_path = repo / "validation" / "qsq_prospective" / "fresh_seed_jobs.csv"
    work = [r for r in read_csv(work_path) if r.get("status") == "PREPARED_NOT_EXECUTED"]
    if len(work) != 14986 or len({key(r) for r in work}) != 14986:
        raise RuntimeError(f"P2 work order must contain 14,986 unique keys; got {len(work)}")

    outcomes: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []
    manifests: list[dict[str, Any]] = []
    for p in sorted(shards.rglob("outcomes_shard_*.csv")):
        outcomes.extend(read_csv(p))
    for p in sorted(shards.rglob("failures_shard_*.csv")):
        failures.extend(read_csv(p))
    for p in sorted(shards.rglob("manifest_shard_*.json")):
        manifests.append(json.loads(p.read_text(encoding="utf-8")))
    if not manifests:
        raise RuntimeError("no P2 shard manifests found")

    out_keys = [key(r) for r in outcomes]
    fail_keys = [key(r) for r in failures]
    if len(set(out_keys)) != len(out_keys):
        raise RuntimeError("duplicate successful P2 keys")
    if len(set(fail_keys)) != len(fail_keys):
        raise RuntimeError("duplicate failed P2 keys")
    if set(out_keys) & set(fail_keys):
        raise RuntimeError("P2 key appears as success and failure")
    accounted = set(out_keys) | set(fail_keys)
    work_keys = {key(r) for r in work}
    if accounted != work_keys:
        raise RuntimeError(f"P2 accounting mismatch missing={len(work_keys-accounted)} extra={len(accounted-work_keys)}")

    outcomes.sort(key=lambda r: (r["material_id"], int(r["seed_label"])))
    failures.sort(key=lambda r: (r["material_id"], int(r["seed_label"])))
    outcome_fields = list(outcomes[0].keys()) if outcomes else []
    failure_fields = list(failures[0].keys()) if failures else [
        "material_id", "family", "seed_label", "stream_seed", "epsilon", "field_fingerprint", "npoints", "status", "stage", "error"
    ]
    outcomes_path = outdir / "outcomes.csv"
    failures_path = outdir / "failures.csv"
    write_csv(outcomes_path, outcomes, outcome_fields)
    write_csv(failures_path, failures, failure_fields)

    floors = load_frozen_floors(repo)
    by_material_out: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_material_fail: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in outcomes:
        by_material_out[r["material_id"]].append(r)
    for r in failures:
        by_material_fail[r["material_id"]].append(r)

    material_summary: list[dict[str, Any]] = []
    for material in sorted(floors):
        valid = by_material_out.get(material, [])
        failed = by_material_fail.get(material, [])
        if len(valid) + len(failed) != 59:
            raise RuntimeError(f"material {material} does not account for 59 seeds")
        responses = np.array([float(r["bader_response_max_e"]) for r in valid], dtype=float)
        floor = floors[material]
        for tau in TAUS:
            k = int(np.count_nonzero(responses >= tau))
            n_valid = len(valid)
            n_fail = len(failed)
            n_planned = 59
            eligible = floor < tau
            conservative_k = k + n_fail
            max_fresh = float(np.max(responses)) if n_valid else float("nan")
            material_summary.append({
                "material_id": material,
                "tau_e": tau,
                "original_qsq_floor_e": floor,
                "original_qsq_eligible": eligible,
                "n_planned": n_planned,
                "n_valid": n_valid,
                "n_fail": n_fail,
                "n_exceed": k,
                "valid_exceedance_fraction": k / n_valid if n_valid else float("nan"),
                "valid_exact_one_sided_95_upper": exact_upper_95(k, n_valid) if n_valid else float("nan"),
                "conservative_exceedance_fraction": conservative_k / n_planned,
                "conservative_exact_one_sided_95_upper": exact_upper_95(conservative_k, n_planned),
                "any_fresh_exceedance": bool(k > 0),
                "any_unresolved": bool(n_fail > 0),
                "fresh_max_response_e": max_fresh,
                "fresh_max_over_original_floor": max_fresh / floor if n_valid and floor > 0 else float("inf") if n_valid and max_fresh > 0 else float("nan"),
            })

    cohort_summary: list[dict[str, Any]] = []
    discrimination: list[dict[str, Any]] = []
    for tau in TAUS:
        subset = [r for r in material_summary if r["tau_e"] == tau]
        n_eligible = sum(bool(r["original_qsq_eligible"]) for r in subset)
        acceptance_fraction = n_eligible / len(subset)
        group_results: dict[str, dict[str, Any]] = {}
        for group, is_eligible in (("eligible", True), ("screen_rejected", False)):
            g = [r for r in subset if bool(r["original_qsq_eligible"]) is is_eligible]
            valid_trials = sum(int(r["n_valid"]) for r in g)
            planned_trials = sum(int(r["n_planned"]) for r in g)
            unresolved = sum(int(r["n_fail"]) for r in g)
            events = sum(int(r["n_exceed"]) for r in g)
            valid_rate = events / valid_trials if valid_trials else float("nan")
            conservative_rate = (events + unresolved) / planned_trials if planned_trials else float("nan")
            ci_lo, ci_hi = bootstrap_group(g, args.bootstrap_reps, conservative=False, seed=int(tau*1e9)+20260911+(0 if is_eligible else 1))
            c_lo, c_hi = bootstrap_group(g, args.bootstrap_reps, conservative=True, seed=int(tau*1e9)+20260921+(0 if is_eligible else 1))
            per_material_rates = [float(r["valid_exceedance_fraction"]) for r in g if int(r["n_valid"]) > 0]
            row = {
                "tau_e": tau,
                "primary_endpoint": tau == PRIMARY_TAU,
                "gate_group": group,
                "n_materials": len(g),
                "acceptance_fraction_all_materials": acceptance_fraction,
                "planned_trials": planned_trials,
                "valid_trials": valid_trials,
                "unresolved_trials": unresolved,
                "exceedance_events": events,
                "valid_trial_exceedance_fraction": valid_rate,
                "material_cluster_ci_low": ci_lo,
                "material_cluster_ci_high": ci_hi,
                "conservative_exceedance_fraction": conservative_rate,
                "conservative_material_cluster_ci_low": c_lo,
                "conservative_material_cluster_ci_high": c_hi,
                "materials_with_any_exceedance": sum(bool(r["any_fresh_exceedance"]) for r in g),
                "fraction_materials_with_any_exceedance": sum(bool(r["any_fresh_exceedance"]) for r in g)/len(g) if g else float("nan"),
                "materials_with_unresolved_trials": sum(bool(r["any_unresolved"]) for r in g),
                "median_material_exceedance_fraction": float(np.median(per_material_rates)) if per_material_rates else float("nan"),
            }
            cohort_summary.append(row)
            group_results[group] = row
        er = group_results["eligible"]["valid_trial_exceedance_fraction"]
        rr = group_results["screen_rejected"]["valid_trial_exceedance_fraction"]
        er_c = group_results["eligible"]["conservative_exceedance_fraction"]
        rr_c = group_results["screen_rejected"]["conservative_exceedance_fraction"]
        discrimination.append({
            "tau_e": tau,
            "primary_endpoint": tau == PRIMARY_TAU,
            "acceptance_fraction": acceptance_fraction,
            "eligible_materials": n_eligible,
            "screen_rejected_materials": len(subset)-n_eligible,
            "eligible_valid_exceedance_fraction": er,
            "screen_rejected_valid_exceedance_fraction": rr,
            "valid_risk_ratio_rejected_over_eligible": rr/er if er > 0 else float("inf"),
            "eligible_conservative_exceedance_fraction": er_c,
            "screen_rejected_conservative_exceedance_fraction": rr_c,
            "conservative_risk_ratio_rejected_over_eligible": rr_c/er_c if er_c > 0 else float("inf"),
        })

    write_csv(audit / "p2_fresh_probe_material_summary.csv", material_summary)
    write_csv(audit / "p2_fresh_probe_cohort_summary.csv", cohort_summary)
    write_csv(audit / "p2_fresh_probe_discrimination.csv", discrimination)

    failure_stages = Counter(r.get("stage", "") for r in failures)
    manifest = {
        "status": "COMPLETE" if not failures else "COMPLETE_WITH_RECORDED_FAILURES",
        "work_order_jobs": 14986,
        "successful_outcomes": len(outcomes),
        "failed_outcomes": len(failures),
        "accounted_outcomes": len(outcomes)+len(failures),
        "materials": 254,
        "fresh_seeds_per_material": 59,
        "primary_tau_e": PRIMARY_TAU,
        "secondary_taus_e": [1e-4, 1e-2],
        "failure_stages": dict(sorted(failure_stages.items())),
        "work_order_sha256": sha256_file(work_path),
        "outcomes_sha256": sha256_file(outcomes_path),
        "failures_sha256": sha256_file(failures_path),
        "original_five_seed_gate_modified": False,
        "historical_qsq_outputs_modified": False,
    }
    (outdir / "execution_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = [
        "# P2 prospective fresh-perturbation validation",
        "",
        f"Execution status: **{manifest['status']}**",
        "",
        f"Pre-registered outcomes accounted: **{manifest['accounted_outcomes']}/14,986**; successful: **{manifest['successful_outcomes']}**; unresolved/failed: **{manifest['failed_outcomes']}**.",
        "",
        "The original five-seed QSQ gate was held fixed. These 59 streams per development material were pre-registered as held-out iid-uniform perturbations and were not used to modify the legacy gate.",
        "",
        "| tau | Gate group | Materials | Acceptance fraction | Fresh trials | Exceedances | Fresh exceedance risk | 95% material-cluster CI | Materials with >=1 exceedance |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in cohort_summary:
        report.append(
            f"| {row['tau_e']:.0e} e | {row['gate_group']} | {row['n_materials']} | {100*row['acceptance_fraction_all_materials']:.1f}% | "
            f"{row['valid_trials']} | {row['exceedance_events']} | {100*row['valid_trial_exceedance_fraction']:.3f}% | "
            f"{100*row['material_cluster_ci_low']:.3f}–{100*row['material_cluster_ci_high']:.3f}% | "
            f"{row['materials_with_any_exceedance']} ({100*row['fraction_materials_with_any_exceedance']:.1f}%) |"
        )
    report += ["", "## Frozen-gate discrimination", "", "| tau | Accepted materials | Rejected materials | Risk: eligible | Risk: rejected | Rejected/eligible risk ratio |", "|---:|---:|---:|---:|---:|---:|"]
    for row in discrimination:
        rr = row["valid_risk_ratio_rejected_over_eligible"]
        rr_text = "Inf" if math.isinf(rr) else f"{rr:.2f}x"
        report.append(
            f"| {row['tau_e']:.0e} e | {row['eligible_materials']} | {row['screen_rejected_materials']} | "
            f"{100*row['eligible_valid_exceedance_fraction']:.3f}% | {100*row['screen_rejected_valid_exceedance_fraction']:.3f}% | {rr_text} |"
        )
    report += [
        "",
        "## Interpretation boundary",
        "",
        "The primary endpoint is 1e-3 e. The 1e-4 and 1e-2 e rows are prespecified secondary endpoints and use the same 59 response vectors rather than independent experiments. Trial-level rates are descriptive within repeated perturbations; uncertainty is clustered by material. If any trials are unresolved, conservative rates count them as adverse and are stored in the machine-readable cohort table.",
        "",
        "A material with zero exceedances in 59 valid iid draws has a one-sided 95% exact per-cell upper bound of about 4.95% under the declared Bernoulli model. This is not a simultaneous guarantee across 254 materials and does not establish worst-case stability. A failed QSQ screen also does not prove that any observed codec discrepancy was caused by reference instability.",
        "",
        "The scientifically relevant test is whether the frozen gate prospectively separates low-risk from high-risk reference responses at useful acceptance coverage. This report therefore emphasizes conditional exceedance risk, acceptance fraction and rejected/eligible risk ratio rather than a large exclusion percentage alone.",
    ]
    (audit / "P2_FRESH_PROBE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
