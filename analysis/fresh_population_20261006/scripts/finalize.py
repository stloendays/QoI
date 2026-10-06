"""Split accepted materials into engineering/confirmatory manifests and write PROVENANCE.json.

Usage: finalize.py <repo_root> <out_dir> <rule_commit>
"""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = ["material_id", "task_id", "corpus", "system_type", "source", "formula", "ngrid",
           "sha256", "url", "source_bytes", "npoints", "natoms", "selection_stratum",
           "selection_hash"]
ENG_STEP = {"P1": 6, "P2": 5, "P3": 6}
SYSTEM = {"P1": ("bulk", "Materials Project"), "P2": ("bulk", "Materials Project"),
          "P3": ("slab", "NOMAD surfaces/adsorbates")}


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dist(values: list[float]) -> dict:
    v = sorted(values)
    if not v:
        return {}
    q = statistics.quantiles(v, n=4) if len(v) > 1 else [v[0]] * 3
    return {"n": len(v), "min": v[0], "q1": q[0], "median": q[1], "q3": q[2], "max": v[-1]}


def main() -> int:
    repo, out, rule_commit = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    with (out / "attempts.csv").open(newline="", encoding="utf-8") as f:
        attempts = list(csv.DictReader(f))
    stats: dict = {"pools": {}}
    manifests = {}
    for pool in ("P1", "P2", "P3"):
        acc = [r for r in attempts if r["pool"] == pool and r["decision"] == "accept"]
        if not acc:
            continue
        acc.sort(key=lambda r: (int(r["npoints"]), r["id"]))
        step = ENG_STEP[pool]
        system_type, source = SYSTEM[pool]
        split = {"engineering": [], "confirmatory": []}
        for i, r in enumerate(acc):
            role = "engineering" if i >= 2 and (i - 2) % step == 0 else "confirmatory"
            split[role].append({
                "material_id": r["material_id"], "task_id": r["id"],
                "corpus": f"fresh_{pool.lower()}_{role}", "system_type": system_type,
                "source": source, "formula": r["formula"], "ngrid": r["ngrid"],
                "sha256": r["sha256"], "url": r["url"], "source_bytes": r["source_bytes"],
                "npoints": r["npoints"], "natoms": r["natoms"],
                "selection_stratum": r["stratum"], "selection_hash": r["selection_hash"],
            })
        for role, rows in split.items():
            name = f"{pool}_{role.upper()}_MANIFEST.csv"
            with (out / name).open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
            manifests[name] = {"rows": len(rows), "sha256": sha_file(out / name)}
        pa = [r for r in attempts if r["pool"] == pool]
        stats["pools"][pool] = {
            "n_attempts": len(pa),
            "n_accepted": len(acc),
            "n_engineering": len(split["engineering"]),
            "n_confirmatory": len(split["confirmatory"]),
            "n_strata_attempted": len({r["stratum"] for r in pa}),
            "reject_reasons": dict(Counter(r["reason"].split(":")[0] for r in pa
                                           if r["decision"] == "reject")),
            "n_downloads_chgcar": sum(1 for r in pa if r["source_bytes"]),
            "downloaded_bytes": sum(int(r["downloaded_bytes"] or 0) for r in pa),
            "accepted_source_bytes": dist([int(r["source_bytes"]) for r in acc]),
            "accepted_npoints": dist([int(r["npoints"]) for r in acc]),
            "accepted_natoms": dist([int(r["natoms"]) for r in acc]),
            "engineering_npoints": dist([int(r["npoints"]) for r in split["engineering"]]),
            "confirmatory_npoints": dist([int(r["npoints"]) for r in split["confirmatory"]]),
            "max_hash_rank_used": max(int(r["hash_rank"]) for r in acc),
            "n_distinct_material_ids": len({r["material_id"] for r in acc}),
        }
        if pool == "P2":
            stats["pools"][pool]["accepted_aeccar0_bytes"] = dist(
                [int(r["aeccar0_bytes"]) for r in acc])
            stats["pools"][pool]["accepted_aeccar2_bytes"] = dist(
                [int(r["aeccar2_bytes"]) for r in acc])
            stats["pools"][pool]["n_material_id_equals_task_id"] = sum(
                r["material_id"] == r["id"] for r in acc)
        if pool == "P1":
            stats["pools"][pool]["n_material_id_equals_task_id"] = sum(
                r["material_id"] == r["id"] for r in acc)
    stats["total_downloaded_bytes"] = sum(int(r["downloaded_bytes"] or 0) for r in attempts)
    (out / "selection_stats.json").write_text(json.dumps(stats, indent=2))

    def load(name):
        p = out / name
        return json.loads(p.read_text()) if p.exists() else None

    scripts = sorted((out / "scripts").glob("*.py"))
    prov = {
        "population": "QOAC-FRESH-20261006",
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "branch": "research/fresh-population-20261006",
        "selection_rule_sha256": sha_file(out / "SELECTION_RULE.md"),
        "selection_rule_frozen_commit": rule_commit,
        "scripts_git_commit": subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
            text=True).stdout.strip(),
        "scripts_sha256": {p.name: sha_file(p) for p in scripts},
        "loader": "validation/qsq_prospective/development_compatibility_smoke.py::build_grid / decode_mp_chgcar",
        "loader_sha256": sha_file(repo / "validation/qsq_prospective/development_compatibility_smoke.py"),
        "s3_listing": load("s3_index_log.json"),
        "nomad_listing": load("nomad_frame_log.json"),
        "s3_index_sha256": {p.name: sha_file(p) for p in sorted(out.glob("s3_index_*.csv.gz"))},
        "nomad_frame_sha256": sha_file(out / "nomad_frame_surface_vasp.csv.gz")
        if (out / "nomad_frame_surface_vasp.csv.gz").exists() else None,
        "exclusion": load("exclusion_summary.json"),
        "exclusion_files_sha256": {n: sha_file(out / n) for n in (
            "exclusion_ids.csv", "exclusion_ids_full.csv.gz", "exclusion_formulas.csv")},
        "frame_counts": load("frame_counts.json"),
        "p3_feasibility": load("p3_feasibility.json"),
        "p3_status": "not built: frozen public NOMAD frame cannot supply 72 distinct non-excluded slabs (see p3_feasibility.json)",
        "attempts_sha256": sha_file(out / "attempts.csv"),
        "manifests": manifests,
        "selection_stats": stats,
    }
    (out / "PROVENANCE.json").write_text(json.dumps(prov, indent=2))
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
