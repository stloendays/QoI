#!/usr/bin/env python3
"""Compact WP-I checkpoint status."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
TASKS = HERE.parents[2] / "extensions_20260930" / "WP-G" / "vanda_results" / "material_ids.txt"
CK = HERE / "results" / "checkpoints"

ids = [x.strip() for x in TASKS.read_text().splitlines() if x.strip()]
done = failed = success = 0
for mid in ids:
    p = CK / (mid + ".json")
    if not p.exists():
        continue
    done += 1
    d = json.loads(p.read_text())
    if d.get("status") == "SUCCESS":
        success += 1
    else:
        failed += 1
print("total=%d done=%d success=%d failed=%d remaining=%d" % (len(ids), done, success, failed, len(ids)-done))
