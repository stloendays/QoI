#!/usr/bin/env python3
"""Local: tasks_base.json for the 53 WP-G materials from the frozen rows (read only)."""
import csv, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parents[3]
meta = {r["material_id"]: r for r in csv.DictReader(open(REPO / "materials_metadata.csv", encoding="utf-8"))}
avail = [r for r in csv.DictReader(open(HERE.parent / "aeccar_availability.csv", encoding="utf-8")) if r["both"] == "1"]
bench = {}
for r in csv.DictReader(open(REPO / "benchmark" / "master_benchmark_full.csv", encoding="utf-8")):
    bench.setdefault(r["material_id"], []).append(r)
B = "https://materialsproject-parsed.s3.amazonaws.com/"
tasks = {}
for a in avail:
    m = a["material_id"]; rows = bench[m]
    tasks[m] = dict(task_id=a["task_id"], chgcar_url=meta[m]["url"], chgcar_sha256=meta[m]["sha256"], chgcar_bytes=int(meta[m]["source_bytes"]),
                    aeccar0_url=B + "aeccar0s/%s.json.gz" % a["task_id"], aeccar2_url=B + "aeccar2s/%s.json.gz" % a["task_id"],
                    npoints=int(meta[m]["npoints"]), value_ptp=float(rows[0]["value_ptp"]),
                    rows=[dict(codec=r["codec"].upper(), rel=float(r["nominal_tolerance_relative"]), abs=float(r["nominal_tolerance_absolute"]),
                               realized_Linf=float(r["realized_Linf"]), bader_error_e=float(r["Bader_error_resolved_e"]),
                               compressed_bytes=int(r["compressed_bytes"]))
                          for r in sorted(rows, key=lambda x: (x["codec"], float(x["nominal_tolerance_relative"])))])
assert len(tasks) == 53
json.dump(tasks, open(HERE / "tasks_base.json", "w"), indent=1)
print(len(tasks), "materials,", sum(len(t["rows"]) for t in tasks.values()), "frozen rows")
