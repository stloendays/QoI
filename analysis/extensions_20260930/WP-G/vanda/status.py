#!/usr/bin/env python3
"""Vanda: one-line JSON status of WP-G for the local monitor (read only)."""
import glob, json, os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent
ck = glob.glob(str(ROOT / "results" / "checkpoints" / "*.json"))
st = [json.load(open(p)).get("status") for p in ck]
# `qstat -u USER -f -F json` prints the plain table on this PBS, so parse the table (job names are truncated to 10 chars)
q = subprocess.run("qstat -u $USER 2>/dev/null", shell=True, capture_output=True, text=True).stdout
jobs = []
for ln in q.splitlines():
    f = ln.split()
    if len(f) >= 11 and f[0][0].isdigit() and f[3].startswith("qoi_wpg"):
        jobs.append(dict(id=f[0], state=f[9], name=f[3]))
newest = max((os.path.getmtime(p) for p in ck), default=0)
print(json.dumps(dict(total=53, checkpoints=len(ck), success=st.count("SUCCESS"), failed=st.count("FAILED"),
                      newest_checkpoint=newest, jobs=jobs, armed=(ROOT / "PRODUCTION_ARMED").exists(),
                      copied_back=(ROOT / "COPIED_BACK").exists())))
