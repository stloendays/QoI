#!/usr/bin/env python3
"""Print one JSON line with current task completion counts."""
from __future__ import annotations

import json
import sys
from pathlib import Path


STAGING_ROOT = Path("/scratch/junbotong/qoi-ffcz-20261012")
CODE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CODE_DIR.parents[1]
sys.path.insert(0, str(CODE_DIR))
import run_ffcz as R  # noqa: E402


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else STAGING_ROOT
    checkpoints = root / "checkpoints"
    done = failed = 0
    for path in checkpoints.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not payload.get("complete"):
            continue
        if payload.get("status") == "failed":
            failed += 1
        else:
            done += 1
    total = len(R.task_ids(REPO_ROOT, "run"))
    print(json.dumps({"total": total, "done": done, "failed": failed, "pending": max(0, total - done - failed)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
