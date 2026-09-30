#!/usr/bin/env python3
"""Vanda: one-line JSON status of WP-G for the local monitor (read only)."""
import glob, json, os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent
ck = glob.glob(str(ROOT / "results" / "checkpoints" / "*.json"))
st = [json.load(open(p)).get("status") for p in ck]
q = subprocess.run("qstat -u $USER -f -F json 2>/dev/null", shell=True, capture_output=True, text=True).stdout
jobs = []
try:
    for jid, j in json.loads(q).get("Jobs", {}).items():
        if j.get("Job_Name", "").startswith("qoi_wpg"):
            jobs.append(dict(id=jid, state=j.get("job_state"), name=j["Job_Name"]))
except ValueError:
    pass
newest = max((os.path.getmtime(p) for p in ck), default=0)
print(json.dumps(dict(total=53, checkpoints=len(ck), success=st.count("SUCCESS"), failed=st.count("FAILED"),
                      newest_checkpoint=newest, jobs=jobs, armed=(ROOT / "PRODUCTION_ARMED").exists(),
                      copied_back=(ROOT / "COPIED_BACK").exists())))
