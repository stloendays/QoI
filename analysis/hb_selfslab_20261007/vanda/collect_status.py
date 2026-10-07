#!/usr/bin/env python3
"""Write runs/STATUS.csv from the server's runs/STATUS.tsv joined with selection/drawn.csv (read-only ssh)."""
import csv
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
p = subprocess.run(["ssh", "-o", "BatchMode=yes", "vanda",
                    "cat /scratch/junbotong/qoi_selfslab_20261007/runs/STATUS.tsv"], capture_output=True, timeout=300)
last = {}
for line in p.stdout.decode().splitlines():
    f = line.split("\t")
    if len(f) == 5:
        last[f[0]] = f            # the last line of a directory is its current status
drawn = list(csv.DictReader(open(ROOT / "selection" / "drawn.csv", encoding="utf-8")))
rows = []
for r in drawn:
    d = f"{int(r['draw_rank']):02d}_{r['material_id']}"
    f = last.get(d)
    rows.append({"draw_rank": r["draw_rank"], "material_id": r["material_id"], "reduced_formula": r["reduced_formula"],
                 "dir": d, "status": f[1] if f else "not_finished", "job_id": f[4] if f else "",
                 "start_epoch": f[2] if f else "", "end_epoch": f[3] if f else "",
                 "seconds": int(f[3]) - int(f[2]) if f and f[2] and f[3] else ""})
(ROOT / "runs").mkdir(exist_ok=True)
with open(ROOT / "runs" / "STATUS.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print({s: sum(1 for r in rows if r["status"] == s) for s in sorted({r["status"] for r in rows})})
