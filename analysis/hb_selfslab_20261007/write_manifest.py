#!/usr/bin/env python3
"""Write manifest.csv (the P3b / slab-cohort manifest schema) for the N cohort slabs, in cohort order, from cohort.csv.
The CHGCAR is the release asset <material_id>__CHGCAR.gz; sha256 and source_bytes are those of the gz asset (the bytes
run_joint_v2.process downloads and checks); task_id = material_id (the key of the AECCAR routing in
run_joint_selfslab.py)."""
import csv
from pathlib import Path

import run_joint_selfslab as rss

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / "cohort.csv", encoding="utf-8")))
cols = ["material_id", "task_id", "corpus", "system_type", "source", "formula", "ngrid", "sha256", "url", "source_bytes",
        "npoints", "natoms", "selection_stratum", "selection_hash"]
with open(HERE / "manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    for r in sorted(rows, key=lambda r: int(r["cohort_rank"])):
        w.writerow({"material_id": r["material_id"], "task_id": r["material_id"], "corpus": "fresh_hb_selfslab",
                    "system_type": "slab", "source": rss.SOURCE, "formula": r["reduced_formula"], "ngrid": r["ngrid"],
                    "sha256": r["CHGCAR_gz_sha256"], "url": rss.asset_url(r["material_id"], "CHGCAR"),
                    "source_bytes": r["CHGCAR_gz_bytes"], "npoints": r["npoints"], "natoms": r["natoms"],
                    "selection_stratum": f"formula:{r['reduced_formula']}", "selection_hash": r["selection_hash"]})
print(f"{len(rows)} rows")
