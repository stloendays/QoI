#!/usr/bin/env python3
"""Aggregate P4 uncompressed reference analyses and freeze binary/ambiguous pairs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

REF_MIN_MAG_E = 0.02
REF_MAX_SOLVER_DISAGREE_E = 0.01
SOLVERS = ("baderkit_ongrid", "henkelman_ongrid")


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fallback: list[str]):
    fields = list(rows[0]) if rows else fallback
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def sign(x: float) -> int:
    return 1 if x > 0 else -1 if x < 0 else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", type=Path, required=True)
    ap.add_argument("--shards-root", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    z = ap.parse_args(); out = z.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    candidates = read_csv(z.candidates)

    rows = []; failures = []
    for p in sorted(z.shards_root.rglob("reference_rows_shard_*.csv")):
        rows += read_csv(p)
    for p in sorted(z.shards_root.rglob("reference_failures_shard_*.csv")):
        failures += read_csv(p)

    expected_mids = sorted({r["state_A_material_id"] for r in candidates} | {r["state_B_material_id"] for r in candidates})
    expected = len(expected_mids) * len(SOLVERS)
    if len(rows) + len(failures) != expected:
        raise RuntimeError(f"P4 reference accounting mismatch {len(rows)+len(failures)} != {expected}")
    keys = [(r.get("material_id", ""), r.get("solver", "")) for r in rows + failures]
    if len(keys) != len(set(keys)):
        raise RuntimeError("duplicate P4 reference material-solver key")

    by = {(r["material_id"], r["solver"]): r for r in rows}
    material_fail = {(r["material_id"], r["solver"]): r for r in failures}
    pair_rows = []
    for c in candidates:
        a = c["state_A_material_id"]; b = c["state_B_material_id"]
        ia = int(c["target_index_A_zero_based"]); ib = int(c["target_index_B_zero_based"]); target = c["target_species"]
        rec: dict[str, Any] = {
            "pair_id": c["pair_id"], "upload_id": c["upload_id"], "upload_description": c["upload_description"],
            "state_A_material_id": a, "state_B_material_id": b,
            "state_A_formula": c["state_A_formula"], "state_B_formula": c["state_B_formula"],
            "target_species": target, "target_index_A_zero_based": ia, "target_index_B_zero_based": ib,
            "added_composition": c["added_composition"],
        }
        deltas = {}; reasons = []
        for solver in SOLVERS:
            ra = by.get((a, solver)); rb = by.get((b, solver))
            if ra is None or rb is None:
                reasons.append(f"{solver}:missing_solver")
                continue
            qa = np.asarray(json.loads(ra["charges_json"]), dtype=float)
            qb = np.asarray(json.loads(rb["charges_json"]), dtype=float)
            sa = json.loads(ra["species_json"]); sb = json.loads(rb["species_json"])
            if ia >= len(qa) or ib >= len(qb):
                reasons.append(f"{solver}:target_index_out_of_range")
                continue
            if sa[ia] != target or sb[ib] != target:
                reasons.append(f"{solver}:target_species_mismatch")
                continue
            delta = float(qb[ib] - qa[ia]); deltas[solver] = delta
            rec[f"delta_q_{solver}_e"] = delta
            rec[f"wall_seconds_A_{solver}"] = float(ra.get("wall_seconds", 0) or 0)
            rec[f"wall_seconds_B_{solver}"] = float(rb.get("wall_seconds", 0) or 0)

        status = "REFERENCE_AMBIGUOUS"; ref_sign = 0
        if len(deltas) == 2:
            db = deltas["baderkit_ongrid"]; dh = deltas["henkelman_ongrid"]
            sbv, shv = sign(db), sign(dh)
            rec["solver_delta_disagreement_e"] = abs(db - dh)
            rec["reference_min_abs_delta_e"] = min(abs(db), abs(dh))
            if sbv == 0 or shv == 0:
                reasons.append("zero_reference_delta")
            if sbv != shv:
                reasons.append("solver_sign_disagreement")
            if min(abs(db), abs(dh)) < REF_MIN_MAG_E:
                reasons.append("below_frozen_reference_margin")
            if abs(db - dh) > REF_MAX_SOLVER_DISAGREE_E:
                reasons.append("above_frozen_solver_disagreement_limit")
            if not reasons:
                status = "REFERENCE_VALID"
                ref_sign = sbv
        rec["reference_status"] = status
        rec["reference_sign"] = ref_sign
        rec["reference_reason"] = ";".join(sorted(set(reasons))) if reasons else "PASS"
        pair_rows.append(rec)

    pair_rows.sort(key=lambda r: r["pair_id"])
    valid = [r for r in pair_rows if r["reference_status"] == "REFERENCE_VALID"]
    write_csv(out / "p4_reference_pairs.csv", pair_rows, ["pair_id", "reference_status"])
    write_csv(out / "p4_reference_valid_pairs.csv", valid, ["pair_id", "reference_status"])
    write_csv(out / "p4_reference_solver_failures.csv", failures, ["material_id", "solver", "status", "stage", "error"])

    by_upload = {}
    for r in pair_rows:
        u = r["upload_id"]
        d = by_upload.setdefault(u, {"total": 0, "valid": 0, "description": r["upload_description"]})
        d["total"] += 1; d["valid"] += int(r["reference_status"] == "REFERENCE_VALID")
    lines = [
        "# P4 reference adjudication", "",
        f"Candidate pairs adjudicated: **{len(pair_rows)}**; reference-valid: **{len(valid)}**; reference-ambiguous/provenance-limited: **{len(pair_rows)-len(valid)}**.",
        f"Unique states: **{len(expected_mids)}**; planned source solver calls: **{expected}**; successful: **{len(rows)}**; failed: **{len(failures)}**.", "",
        "Frozen reference rule: BaderKit and Henkelman on-grid must have the same non-zero sign, each |Delta q| >= 0.02 e, and inter-solver |Delta q| disagreement <= 0.01 e. These constants were frozen before P4 charge outcomes were inspected.", "",
        "| Upload | Description | Candidate pairs | Reference-valid |", "|---|---|---:|---:|",
    ]
    for u in sorted(by_upload):
        d = by_upload[u]; lines.append(f"| {u} | {d['description']} | {d['total']} | {d['valid']} |")
    lines += ["", "## Interpretation boundary", "", "This stage establishes the P4 reference cohort only. It does not evaluate compression or QSQ utility. A reference-ambiguous pair remains in cohort accounting but is not converted into a binary correctness label."]
    (out / "P4_REFERENCE_ADJUDICATION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = {
        "status": "REFERENCE_ADJUDICATION_COMPLETE",
        "candidate_pairs": len(pair_rows), "reference_valid_pairs": len(valid),
        "reference_ambiguous_pairs": len(pair_rows) - len(valid),
        "unique_states": len(expected_mids), "planned_source_solver_calls": expected,
        "successful_source_solver_calls": len(rows), "failed_source_solver_calls": len(failures),
        "reference_min_magnitude_e": REF_MIN_MAG_E,
        "reference_max_solver_disagreement_e": REF_MAX_SOLVER_DISAGREE_E,
        "candidate_sha256": hashlib.sha256(z.candidates.read_bytes()).hexdigest(),
        "qsq_or_codec_outcomes_read": False,
    }
    (out / "execution_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
