#!/usr/bin/env python3
"""One-line JSON status for the WP-I Vanda job."""
from pathlib import Path
import glob, json, os, subprocess

ROOT = Path(__file__).resolve().parent
ids = [x.strip() for x in (ROOT / "material_ids.txt").read_text().splitlines() if x.strip()] if (ROOT/"material_ids.txt").exists() else []
ck = glob.glob(str(ROOT / "results" / "checkpoints" / "*.json"))
records = []
for p in ck:
    try:
        records.append(json.load(open(p)))
    except Exception:
        records.append({"status": "CORRUPT"})
q = subprocess.run("qstat -u $USER 2>/dev/null", shell=True, capture_output=True, text=True).stdout
jobs = []
for ln in q.splitlines():
    f = ln.split()
    if len(f) >= 11 and f[0][0].isdigit() and f[3].startswith("qoi_wpi"):
        jobs.append(dict(id=f[0], state=f[9], name=f[3]))
newest = max((os.path.getmtime(p) for p in ck), default=0)
print(json.dumps({
    "total": len(ids),
    "checkpoints": len(ck),
    "success": sum(d.get("status") == "SUCCESS" for d in records),
    "failed": sum(d.get("status") == "FAILED" for d in records),
    "corrupt": sum(d.get("status") == "CORRUPT" for d in records),
    "remaining": max(0, len(ids)-len(ck)),
    "newest_checkpoint": newest,
    "jobs": jobs,
    "prepared": (ROOT/"PREPARED").exists(),
    "pilot_validated": (ROOT/"PILOT_VALIDATED").exists(),
    "production_done": (ROOT/"PRODUCTION_DONE").exists(),
    "finalized": (ROOT/"FINALIZED").exists(),
}))
