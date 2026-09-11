#!/usr/bin/env python3
"""Aggregate frozen P4 compressed-state analyses into policy utility metrics."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

TAU = 1e-3
REF_MARGIN = 0.02
CODECS = ("ZFP", "SZ3", "SPERR")
REL_TOLS = (1e-7, 3e-7, 1e-6, 3e-6)
RANDOM_REPS = 10000
BOOT_REPS = 5000


def read_csv(p: Path):
    with p.open(newline="", encoding="utf-8") as f: return list(csv.DictReader(f))


def write_csv(p: Path, rows: list[dict[str, Any]], fallback: list[str]):
    fields = list(rows[0]) if rows else fallback
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)


def sign(x: float) -> int: return 1 if x > 0 else -1 if x < 0 else 0

def truthy(x: Any) -> bool: return str(x).strip().lower() in {"true", "1", "yes"}

def stable_hash(*parts: Any) -> int:
    return int.from_bytes(hashlib.sha256("|".join(str(x) for x in parts).encode()).digest()[:8], "big")


def load_floors(path: Path):
    per = defaultdict(list); f32 = defaultdict(list); seeds = defaultdict(set)
    for r in read_csv(path):
        m = r["material_id"]; per[m].append(float(r["floor_noise_resolved_e"])); f32[m].append(float(r["floor_f32_resolved_e"])); seeds[m].add(int(r["seed"]))
    qsq = {}; archived = {}
    for m in per:
        if len(per[m]) != 5 or len(seeds[m]) != 5: raise RuntimeError(f"unexpected frozen seed count for {m}")
        qsq[m] = max(per[m]); archived[m] = max(f32[m])
    return qsq, archived


def ci_cluster_pair(trials: list[dict[str, Any]], retain_key: str, reps: int = BOOT_REPS):
    retained = [r for r in trials if r.get(retain_key)]
    if not retained: return (float("nan"), float("nan"))
    by = defaultdict(list)
    for r in retained: by[r["pair_id"]].append(r)
    ids = sorted(by)
    if len(ids) < 2: return (float("nan"), float("nan"))
    rng = np.random.default_rng(20260911 + stable_hash(retain_key) % 100000)
    vals = []
    for _ in range(reps):
        sample = rng.choice(ids, size=len(ids), replace=True)
        n = e = 0
        for pid in sample:
            for r in by[str(pid)]: n += 1; e += int(r["direct_adverse"])
        if n: vals.append(e / n)
    if not vals: return (float("nan"), float("nan"))
    return (float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference-valid-pairs", type=Path, required=True)
    ap.add_argument("--stability-per-seed", type=Path, required=True)
    ap.add_argument("--shards-root", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    z = ap.parse_args(); out = z.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    refs = read_csv(z.reference_valid_pairs); qsq, archived = load_floors(z.stability_per_seed)

    rows = []; failures = []
    for p in sorted(z.shards_root.rglob("compressed_rows_shard_*.csv")): rows += read_csv(p)
    for p in sorted(z.shards_root.rglob("compressed_failures_shard_*.csv")): failures += read_csv(p)
    mids = sorted({r["state_A_material_id"] for r in refs} | {r["state_B_material_id"] for r in refs})
    expected = len(mids) * len(CODECS) * len(REL_TOLS) * 2
    if len(rows) + len(failures) != expected: raise RuntimeError(f"compressed solver accounting {len(rows)+len(failures)} != {expected}")
    def key(r): return (r.get("material_id", ""), r.get("codec", ""), float(r.get("relative_tolerance", 0)), r.get("solver", ""))
    keys = [key(r) for r in rows + failures]
    if len(keys) != len(set(keys)): raise RuntimeError("duplicate P4 compressed solver key")
    by = {key(r): r for r in rows}

    trials = []
    for ref in refs:
        a = ref["state_A_material_id"]; b = ref["state_B_material_id"]
        if a not in qsq or b not in qsq: raise RuntimeError(f"missing frozen QSQ floor for P4 state {a}/{b}")
        ia = int(ref["target_index_A_zero_based"]); ib = int(ref["target_index_B_zero_based"]); target = ref["target_species"]
        ref_sign = int(ref["reference_sign"])
        if ref_sign not in (-1, 1): raise RuntimeError("reference-valid pair has non-binary sign")
        pair_qsq = qsq[a] < TAU and qsq[b] < TAU
        pair_arch = archived[a] < TAU and archived[b] < TAU
        for codec in CODECS:
            for rel in REL_TOLS:
                rb_a = by.get((a, codec, rel, "baderkit_ongrid")); rb_b = by.get((b, codec, rel, "baderkit_ongrid"))
                rh_a = by.get((a, codec, rel, "henkelman_ongrid")); rh_b = by.get((b, codec, rel, "henkelman_ongrid"))
                valid_bk = rb_a is not None and rb_b is not None and truthy(rb_a.get("bound_respected")) and truthy(rb_b.get("bound_respected"))
                rec: dict[str, Any] = {
                    "trial_id": f"{ref['pair_id']}|{codec}|{rel:.0e}", "pair_id": ref["pair_id"], "upload_id": ref["upload_id"],
                    "codec": codec, "relative_tolerance": rel, "reference_sign": ref_sign,
                    "state_A_material_id": a, "state_B_material_id": b, "target_species": target,
                    "qsq_floor_A_e": qsq[a], "qsq_floor_B_e": qsq[b], "pair_qsq_score_e": max(qsq[a], qsq[b]),
                    "archived_floor_A_e": archived[a], "archived_floor_B_e": archived[b], "pair_archived_score_e": max(archived[a], archived[b]),
                    "pair_qsq_eligible": pair_qsq, "pair_archived_eligible": pair_arch,
                    "direct_valid": valid_bk,
                }
                if valid_bk:
                    qa = np.asarray(json.loads(rb_a["charges_json"]), dtype=float); qb = np.asarray(json.loads(rb_b["charges_json"]), dtype=float)
                    sa = json.loads(rb_a["species_json"]); sb = json.loads(rb_b["species_json"])
                    if ia >= len(qa) or ib >= len(qb) or sa[ia] != target or sb[ib] != target: raise RuntimeError(f"compressed target mapping mismatch {rec['trial_id']}")
                    db = float(qb[ib] - qa[ia]); s_b = sign(db)
                    rec.update({
                        "compressed_delta_q_baderkit_e": db, "direct_sign": s_b, "direct_adverse": s_b != ref_sign,
                        "direct_zero_unresolved": s_b == 0,
                        "pair_realized_Linf": max(float(rb_a["realized_Linf"]), float(rb_b["realized_Linf"])),
                        "compressed_bytes_A": int(rb_a["compressed_bytes"]), "compressed_bytes_B": int(rb_b["compressed_bytes"]),
                        "encode_seconds_A": float(rb_a["encode_seconds"]), "encode_seconds_B": float(rb_b["encode_seconds"]),
                        "baderkit_seconds_A": float(rb_a["solver_seconds"]), "baderkit_seconds_B": float(rb_b["solver_seconds"]),
                    })
                else:
                    rec.update({"direct_adverse": True, "direct_zero_unresolved": True, "pair_realized_Linf": float("nan")})

                valid_h = rh_a is not None and rh_b is not None
                rec["henkelman_available"] = valid_h
                if valid_bk and valid_h:
                    ha = np.asarray(json.loads(rh_a["charges_json"]), dtype=float); hb = np.asarray(json.loads(rh_b["charges_json"]), dtype=float)
                    dha = float(hb[ib] - ha[ia]); sh = sign(dha); sbk = int(rec["direct_sign"])
                    esc_resolved = sbk != 0 and sh == sbk and min(abs(float(rec["compressed_delta_q_baderkit_e"])), abs(dha)) >= REF_MARGIN
                    rec.update({
                        "compressed_delta_q_henkelman_e": dha, "henkelman_sign": sh,
                        "escalation_resolved": esc_resolved,
                        "escalation_sign": sbk if esc_resolved else 0,
                        "escalation_adverse_if_resolved": (sbk != ref_sign) if esc_resolved else "",
                        "henkelman_seconds_A": float(rh_a["solver_seconds"]), "henkelman_seconds_B": float(rh_b["solver_seconds"]),
                    })
                else:
                    rec.update({"escalation_resolved": False, "escalation_sign": 0, "escalation_adverse_if_resolved": ""})
                trials.append(rec)

    trials.sort(key=lambda r: (r["pair_id"], r["codec"], float(r["relative_tolerance"])))

    # Policy retention flags. Invalid direct trials remain adverse/accounted but are not ordinary valid compressed results.
    for r in trials:
        r["retain_no_qualification"] = bool(r["direct_valid"])
        r["retain_qsq"] = bool(r["direct_valid"] and r["pair_qsq_eligible"])
        r["retain_archived"] = bool(r["direct_valid"] and r["pair_archived_eligible"])
        r["retain_linf_match"] = False
    for codec in CODECS:
        valid = [r for r in trials if r["codec"] == codec and r["direct_valid"]]
        n_keep = sum(bool(r["retain_qsq"]) for r in valid)
        ranked = sorted(valid, key=lambda r: (float(r["pair_realized_Linf"]), stable_hash(r["trial_id"])))
        for r in ranked[:n_keep]: r["retain_linf_match"] = True

    policy_keys = [
        ("no_qualification", "retain_no_qualification"),
        ("realized_linf_coverage_matched", "retain_linf_match"),
        ("archived_float32_probe", "retain_archived"),
        ("frozen_qsq", "retain_qsq"),
    ]
    summaries = []
    for scope in ["ALL", *CODECS]:
        subset = [r for r in trials if scope == "ALL" or r["codec"] == scope]
        n_valid = sum(bool(r["direct_valid"]) for r in subset)
        for policy, k in policy_keys:
            kept = [r for r in subset if r[k]]; errs = sum(int(r["direct_adverse"]) for r in kept)
            lo, hi = ci_cluster_pair(subset, k)
            summaries.append({
                "scope": scope, "policy": policy, "reference_trials": len(subset), "computationally_valid_trials": n_valid,
                "retained_trials": len(kept), "coverage_of_valid": len(kept)/n_valid if n_valid else float("nan"),
                "decision_errors_or_zero": errs, "retained_error_rate": errs/len(kept) if kept else float("nan"),
                "pair_cluster_bootstrap_ci_low": lo, "pair_cluster_bootstrap_ci_high": hi,
                "unique_retained_pairs": len({r["pair_id"] for r in kept}),
            })

    # Random coverage-matched negative control by codec.
    random_rows = []
    for codec in CODECS:
        valid = [r for r in trials if r["codec"] == codec and r["direct_valid"]]
        n_keep = sum(bool(r["retain_qsq"]) for r in valid)
        vals = []
        for rep in range(RANDOM_REPS):
            ranked = sorted(valid, key=lambda r: stable_hash("P4-RANDOM", rep, r["trial_id"]))
            kept = ranked[:n_keep]
            vals.append(sum(int(r["direct_adverse"]) for r in kept)/n_keep if n_keep else float("nan"))
        finite = np.asarray([x for x in vals if math.isfinite(x)], dtype=float)
        qsq_kept = [r for r in valid if r["retain_qsq"]]; qsq_rate = sum(int(r["direct_adverse"]) for r in qsq_kept)/len(qsq_kept) if qsq_kept else float("nan")
        random_rows.append({
            "codec": codec, "valid_trials": len(valid), "matched_retained_trials": n_keep, "random_repetitions": RANDOM_REPS,
            "random_error_rate_mean": float(np.mean(finite)) if finite.size else float("nan"),
            "random_error_rate_p025": float(np.quantile(finite, .025)) if finite.size else float("nan"),
            "random_error_rate_p50": float(np.quantile(finite, .5)) if finite.size else float("nan"),
            "random_error_rate_p975": float(np.quantile(finite, .975)) if finite.size else float("nan"),
            "frozen_qsq_error_rate": qsq_rate,
        })

    # Risk-coverage curves for QSQ score and realized Linf.
    curves = []
    for codec in CODECS:
        valid = [r for r in trials if r["codec"] == codec and r["direct_valid"]]
        for score_name, score_key in (("qsq_floor", "pair_qsq_score_e"), ("realized_Linf", "pair_realized_Linf")):
            ranked = sorted(valid, key=lambda r: (float(r[score_key]), stable_hash(r["trial_id"])))
            e = 0
            for i, r in enumerate(ranked, 1):
                e += int(r["direct_adverse"])
                curves.append({"codec": codec, "score": score_name, "retained_trials": i, "coverage": i/len(ranked) if ranked else float("nan"), "error_rate": e/i, "cutoff_score": float(r[score_key])})

    # Selective escalation and escalate-all. Policy cost counts unique reconstructed-state Henkelman calls.
    escalation_rows = []
    for scope in ["ALL", *CODECS]:
        subset = [r for r in trials if (scope == "ALL" or r["codec"] == scope) and r["direct_valid"]]
        for policy in ("qsq_targeted", "escalate_all"):
            resolved = []; needs = []; henkelman_state_calls = set()
            for r in subset:
                should_escalate = policy == "escalate_all" or not r["pair_qsq_eligible"]
                if not should_escalate:
                    if int(r["direct_sign"]) != 0: resolved.append((r, int(r["direct_sign"])))
                    else: needs.append(r)
                    continue
                for m in (r["state_A_material_id"], r["state_B_material_id"]): henkelman_state_calls.add((m, r["codec"], float(r["relative_tolerance"])))
                if r["escalation_resolved"]: resolved.append((r, int(r["escalation_sign"])))
                else: needs.append(r)
            errors = sum(int(s != int(r["reference_sign"])) for r, s in resolved)
            # Sum unique Henkelman wall time from rows table.
            htime = 0.0
            for m, codec, rel in henkelman_state_calls:
                rr = by.get((m, codec, rel, "henkelman_ongrid"))
                if rr is not None: htime += float(rr["solver_seconds"])
            escalation_rows.append({
                "scope": scope, "policy": policy, "valid_trials": len(subset), "resolved_trials": len(resolved),
                "needs_review_trials": len(needs), "needs_review_fraction": len(needs)/len(subset) if subset else float("nan"),
                "errors_among_resolved": errors, "error_rate_among_resolved": errors/len(resolved) if resolved else float("nan"),
                "henkelman_reconstructed_state_calls": len(henkelman_state_calls), "henkelman_wall_seconds_policy_calls": htime,
            })

    write_csv(out / "p4_trial_decisions.csv", trials, ["trial_id"])
    write_csv(out / "p4_policy_summary.csv", summaries, ["scope", "policy"])
    write_csv(out / "p4_random_baseline.csv", random_rows, ["codec"])
    write_csv(out / "p4_risk_coverage.csv", curves, ["codec", "score"])
    write_csv(out / "p4_escalation_summary.csv", escalation_rows, ["scope", "policy"])
    write_csv(out / "p4_compressed_solver_failures.csv", failures, ["material_id", "codec", "relative_tolerance", "solver", "status", "stage", "error"])

    allsum = {(r["scope"], r["policy"]): r for r in summaries}
    lines = [
        "# P4 chemical-decision utility validation", "",
        f"Reference-valid chemistry pairs: **{len(refs)}**. This is a deliberately small case-study cohort, not a prevalence sample.",
        f"Compressed solver evaluations accounted: **{len(rows)+len(failures)}/{expected}**; successful rows: **{len(rows)}**; failed rows: **{len(failures)}**.", "",
        "## Direct decision policies", "",
        "| Policy | Retained / valid | Coverage | Adverse decisions | Retained error rate | Pair-bootstrap 95% CI |", "|---|---:|---:|---:|---:|---:|",
    ]
    for policy, _ in policy_keys:
        r = allsum.get(("ALL", policy), {})
        if not r: continue
        ci = "NA" if not math.isfinite(float(r["pair_cluster_bootstrap_ci_low"])) else f"{100*float(r['pair_cluster_bootstrap_ci_low']):.1f}-{100*float(r['pair_cluster_bootstrap_ci_high']):.1f}%"
        lines.append(f"| {policy} | {r['retained_trials']} / {r['computationally_valid_trials']} | {100*float(r['coverage_of_valid']):.1f}% | {r['decision_errors_or_zero']} | {100*float(r['retained_error_rate']):.1f}% | {ci} |")
    lines += ["", "## Selective escalation", "", "| Policy | Resolved / valid | Needs review | Errors among resolved | Henkelman state calls | Henkelman policy wall time |", "|---|---:|---:|---:|---:|---:|"]
    for r in escalation_rows:
        if r["scope"] != "ALL": continue
        lines.append(f"| {r['policy']} | {r['resolved_trials']} / {r['valid_trials']} | {r['needs_review_trials']} ({100*float(r['needs_review_fraction']):.1f}%) | {r['errors_among_resolved']} ({100*float(r['error_rate_among_resolved']):.1f}% of resolved) | {r['henkelman_reconstructed_state_calls']} | {float(r['henkelman_wall_seconds_policy_calls']):.1f} s |")
    lines += ["", "## Interpretation boundary", "", "P4 tests practical decision utility on a small, outcome-blind, provenance-constrained chemistry cohort. It does not estimate population prevalence. Zero-direction compressed outputs are treated conservatively as adverse/unresolved rather than silently dropped. The reference is a two-implementation on-grid consensus, not a grid-converged physical Bader truth. P3B new-DFT convergence was explicitly deferred before P4 execution."]
    (out / "P4_CHEMICAL_DECISION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = {
        "status": "COMPLETE" if not failures else "COMPLETE_WITH_RECORDED_FAILURES",
        "reference_valid_pairs": len(refs), "unique_states": len(mids),
        "planned_compressed_solver_evaluations": expected, "successful_solver_rows": len(rows), "failed_solver_rows": len(failures),
        "qsq_tau_e": TAU, "reference_margin_e": REF_MARGIN,
        "random_baseline_repetitions": RANDOM_REPS, "pair_bootstrap_repetitions": BOOT_REPS,
        "reference_valid_pairs_sha256": hashlib.sha256(z.reference_valid_pairs.read_bytes()).hexdigest(),
        "stability_per_seed_sha256": hashlib.sha256(z.stability_per_seed.read_bytes()).hexdigest(),
        "p3b_new_dft_used": False,
    }
    (out / "execution_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
