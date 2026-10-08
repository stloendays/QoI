#!/usr/bin/env python3
"""Fix the cohort (PROTOCOL.md section 6): the first 32 drawn materials, in draw order, whose single point converged and
whose CHGCAR, AECCAR0 and AECCAR2 pass the input QC. Reads selection/drawn.csv, runs/STATUS.csv, qc/qc.csv and
runs/fetch.csv; writes cohort.csv (one row per cohort member, with the SHA-256 of the raw and gzipped density files)
and cohort_log.json (counts and the per-material decision of all 40). Inputs and QC only; no HB quantity."""
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
N_TARGET = 32


def rd(p):
    return list(csv.DictReader(open(HERE / p, encoding="utf-8")))


drawn = rd("selection/drawn.csv")
status = {r["material_id"]: r for r in rd("runs/STATUS.csv")}
qc = {r["material_id"]: r for r in rd("qc/qc.csv")} if (HERE / "qc/qc.csv").exists() else {}
fetch = {(r["material_id"], r["file"]): r for r in rd("runs/fetch.csv")}
decisions, cohort = [], []
for r in drawn:
    mid = r["material_id"]
    st = status.get(mid, {}).get("status", "not_finished")
    q = qc.get(mid)
    if not st.startswith("converged"):
        dec = f"dft:{st}"
    elif q is None:
        dec = "qc:not_run"
    elif q["qc_pass"] != "1":
        dec = f"qc:{q['qc_reason']}"
    elif len(cohort) >= N_TARGET:
        dec = "qualified_not_needed"
    else:
        dec = "cohort"
    decisions.append({"draw_rank": int(r["draw_rank"]), "material_id": mid, "decision": dec})
    if dec == "cohort":
        row = {"cohort_rank": len(cohort) + 1, "draw_rank": int(r["draw_rank"]), "material_id": mid,
               "reduced_formula": r["reduced_formula"], "miller": r["miller"], "termination": r["termination"],
               "natoms": int(q["natoms"]), "ngrid": q["CHGCAR_grid"],
               "npoints": math.prod(int(v) for v in q["CHGCAR_grid"].split("x")), "status": st,
               "selection_hash": hashlib.sha256(("QOAC-HB-SELFSLAB-20261007|" + mid).encode()).hexdigest()}
        for n in ("CHGCAR", "AECCAR0", "AECCAR2"):
            f = fetch[(mid, n)]
            row |= {f"{n}_bytes": f["bytes"], f"{n}_sha256": f["local_sha256"], f"{n}_gz_bytes": f["gz_bytes"],
                    f"{n}_gz_sha256": f["gz_sha256"]}
        cohort.append(row)
if cohort:
    with open(HERE / "cohort.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cohort[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(cohort)
counts = {}
for d in decisions:
    counts[d["decision"]] = counts.get(d["decision"], 0) + 1
log = {"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "n_drawn": len(drawn), "N": len(cohort),
       "counts": counts, "decisions": decisions}
(HERE / "cohort_log.json").write_text(json.dumps(log, indent=1) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in log.items() if k != "decisions"}, indent=1))
