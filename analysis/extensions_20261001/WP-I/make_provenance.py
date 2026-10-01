#!/usr/bin/env python3
"""Write WP-I provenance after finalized Vanda execution and analysis."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=Path, required=True)
    args = ap.parse_args()
    stage = args.stage.resolve()
    if not (stage / "FINALIZED").exists():
        raise RuntimeError("stage is not finalized")

    checkpoint_hashes = json.loads((stage / "CHECKPOINT_SHA256.json").read_text())
    jobs = json.loads((stage / "submitted_jobs.json").read_text())
    execution_source_commit = (stage / "SOURCE_COMMIT").read_text().strip()

    outputs = [
        HERE / "RESULTS.md",
        HERE / "summary.csv",
        HERE / "material_summary.csv",
        HERE / "reference_only_probes.csv",
        HERE / "failures.csv",
        HERE / "PAIR_AUDIT.md",
        HERE / "pair_audit_summary.json",
    ]
    missing = [str(p) for p in outputs if not p.exists()]
    if missing:
        raise RuntimeError("missing analysis outputs: " + ", ".join(missing))

    try:
        git_head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        git_head = None

    package_names = ["numpy", "pandas", "scipy", "pymatgen"]
    packages = {}
    for name in package_names:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None

    bader_line = (stage / "logs" / "bader.sha256").read_text().strip().split()
    bader_sha = bader_line[0] if bader_line else None

    record = {
        "package": "WP-I",
        "protocol": "analysis/extensions_20261001/QSQ_OPTIMIZATION_PROTOCOL.md (WP-I)",
        "execution_source_commit": execution_source_commit,
        "analysis_worktree_head": git_head,
        "jobs": jobs,
        "population": {
            "planned": 53,
            "analyzable": 50,
            "predeclared_input_failures": ["mp-1192831", "mp-1193567", "mp-776331"],
        },
        "bader_sha256": bader_sha,
        "checkpoint_sha256": checkpoint_hashes,
        "source_files_sha256": {
            "protocol": sha(REPO / "analysis" / "extensions_20261001" / "QSQ_OPTIMIZATION_PROTOCOL.md"),
            "runner": sha(REPO / "analysis" / "extensions_20261001" / "WP-I" / "vanda" / "run_wpi_reference_only.py"),
            "analyzer": sha(HERE / "analyze_wpi.py"),
            "pair_audit": sha(HERE / "verify_wpi_pairs.py"),
        },
        "analysis_outputs_sha256": {p.name: sha(p) for p in outputs},
        "python": sys.version,
        "platform": platform.platform(),
        "packages": packages,
    }
    (HERE / "provenance.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
