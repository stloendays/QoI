#!/usr/bin/env python3
"""Print one JSON status line grouped by stratum and checkpoint status."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


STRATA = ("D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10a", "D10b", "D10c")


def read_task_files(paths: list[Path]) -> list[tuple[str, str]]:
    tasks = []
    seen = set()
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            task_id, stratum = line.split("\t", 1)
            if task_id not in seen:
                seen.add(task_id)
                tasks.append((task_id, stratum))
    return tasks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = args.root.resolve()
    checkpoint_dir = root / "checkpoints"
    tasks = read_task_files([root / "tasks_small.txt", root / "tasks_large.txt"])
    by_stratum: dict[str, Counter[str]] = defaultdict(Counter)
    overall = Counter()
    for task_id, stratum in tasks:
        path = checkpoint_dir / f"{task_id}.json"
        status = "MISSING"
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                status = str(payload.get("status", "INVALID")) if payload.get("complete") else "INCOMPLETE"
            except Exception:
                status = "INVALID"
        by_stratum[stratum][status] += 1
        overall[status] += 1
    result = {
        "total": len(tasks),
        "status": dict(sorted(overall.items())),
        "by_stratum": {
            stratum: dict(sorted(by_stratum.get(stratum, Counter()).items()))
            for stratum in STRATA
        },
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
