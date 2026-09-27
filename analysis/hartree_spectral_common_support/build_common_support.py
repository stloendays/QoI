#!/usr/bin/env python3
"""Build a deterministic three-codec common-support protocol."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

CODECS = ("ZFP", "SZ3", "SPERR")
CALIPER_DEX = 0.10


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def truthy(x: Any) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes", "t"}


def finite_float(x: Any) -> float | None:
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rows(repo: Path) -> dict[str, dict[str, list[dict[str, Any]]]]:
    path = repo / "analysis" / "hartree_qsq_full" / "results" / "hartree_codec_rows.csv"
    out: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            codec = str(row.get("codec", "")).strip().upper()
            if codec not in CODECS or not truthy(row.get("scientific_reproduction_gate_pass")):
                continue
            linf = finite_float(row.get("reproduced_realized_Linf"))
            tol = finite_float(row.get("nominal_tolerance_absolute"))
            herr = finite_float(row.get("hartree_error_rel_RMSE"))
            if linf is None or linf <= 0 or tol is None or tol <= 0 or herr is None or herr <= 0:
                continue
            r = dict(row)
            r["_linf"] = linf
            r["_tol"] = tol
            r["_herr"] = herr
            r["_row_index"] = int(float(row["frozen_row_index_within_material"]))
            out[row["material_id"]][codec].append(r)
    for mid in out:
        for codec in CODECS:
            out[mid][codec].sort(key=lambda r: (math.log10(r["_linf"]), r["_row_index"]))
    return out


def match_material(groups: dict[str, list[dict[str, Any]]]) -> list[tuple[dict[str, Any], dict[str, Any], dict[str, Any], float, float]]:
    if any(not groups.get(c) for c in CODECS):
        return []

    candidates = []
    for iz, rz in enumerate(groups["ZFP"]):
        lz = math.log10(rz["_linf"])
        for isz, rsz in enumerate(groups["SZ3"]):
            lsz = math.log10(rsz["_linf"])
            for isp, rsp in enumerate(groups["SPERR"]):
                lsp = math.log10(rsp["_linf"])
                logs = (lz, lsz, lsp)
                span = max(logs) - min(logs)
                if span > CALIPER_DEX + 1e-15:
                    continue
                mean = sum(logs) / 3.0
                sad = sum(abs(x - mean) for x in logs)
                candidates.append((
                    span,
                    sad,
                    int(rz["_row_index"]),
                    int(rsz["_row_index"]),
                    int(rsp["_row_index"]),
                    iz, isz, isp,
                    rz, rsz, rsp,
                ))

    candidates.sort(key=lambda x: x[:5])
    used = {c: set() for c in CODECS}
    selected = []
    for span, sad, _, _, _, iz, isz, isp, rz, rsz, rsp in candidates:
        if iz in used["ZFP"] or isz in used["SZ3"] or isp in used["SPERR"]:
            continue
        used["ZFP"].add(iz)
        used["SZ3"].add(isz)
        used["SPERR"].add(isp)
        selected.append((rz, rsz, rsp, float(span), float(sad)))
    return selected


def main() -> int:
    args = parse_args()
    repo = args.repo_root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    source = repo / "analysis" / "hartree_qsq_full" / "results" / "hartree_codec_rows.csv"
    rows = load_rows(repo)

    protocol: list[dict[str, Any]] = []
    triple_id = 0
    material_counts: dict[str, int] = {}

    for mid in sorted(rows):
        selected = match_material(rows[mid])
        if not selected:
            continue
        material_counts[mid] = len(selected)
        for rz, rsz, rsp, span, sad in selected:
            triple_id += 1
            rec: dict[str, Any] = {
                "triple_id": triple_id,
                "material_id": mid,
                "system_type": str(rz["system_type"]),
                "span_dex": span,
                "sum_abs_dev_from_logLinf_mean": sad,
            }
            for codec, r in (("ZFP", rz), ("SZ3", rsz), ("SPERR", rsp)):
                p = codec.lower()
                rec[f"{p}_reproduced_Linf"] = float(r["_linf"])
                rec[f"{p}_historical_hartree_rel_RMSE"] = float(r["_herr"])
                rec[f"{p}_nominal_tolerance_absolute"] = float(r["_tol"])
                rec[f"{p}_frozen_row_index_within_material"] = int(r["_row_index"])
                rec[f"{p}_source_sha256"] = str(r["source_sha256"])
            protocol.append(rec)

    if not protocol:
        raise RuntimeError("no common-support triples found")

    fields: list[str] = []
    for row in protocol:
        for k in row:
            if k not in fields:
                fields.append(k)
    protocol_path = out / "common_support_triples.csv"
    with protocol_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(protocol)

    spans = sorted(float(r["span_dex"]) for r in protocol)
    n = len(spans)
    summary = {
        "matching_rule": {
            "caliper_dex": CALIPER_DEX,
            "without_replacement": True,
            "candidate_order": [
                "span_dex",
                "sum_abs_dev_from_logLinf_mean",
                "ZFP_frozen_row_index",
                "SZ3_frozen_row_index",
                "SPERR_frozen_row_index",
            ],
        },
        "matched_triples": len(protocol),
        "matched_materials": len(material_counts),
        "bulk_triples": sum(str(r["system_type"]) == "bulk" for r in protocol),
        "slab_triples": sum(str(r["system_type"]) == "slab" for r in protocol),
        "bulk_materials": len({r["material_id"] for r in protocol if str(r["system_type"]) == "bulk"}),
        "slab_materials": len({r["material_id"] for r in protocol if str(r["system_type"]) == "slab"}),
        "triples_per_material_min": min(material_counts.values()),
        "triples_per_material_median": sorted(material_counts.values())[len(material_counts)//2],
        "triples_per_material_max": max(material_counts.values()),
        "span_dex_min": spans[0],
        "span_dex_median": spans[n//2],
        "span_dex_p95": spans[min(n-1, int(math.floor(0.95*(n-1))))],
        "span_dex_max": spans[-1],
        "source_sha256": sha256(source),
        "protocol_sha256": sha256(protocol_path),
    }
    (out / "MATCHING_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "COMMON_SUPPORT_PROTOCOL_PASS "
        f"triples={len(protocol)} materials={len(material_counts)} "
        f"bulk_triples={summary['bulk_triples']} slab_triples={summary['slab_triples']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
