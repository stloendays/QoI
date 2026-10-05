#!/usr/bin/env python3
"""Freeze the QOAC-B1 12/38 engineering/holdout split before execution."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

N_ENG=12
PREFIX="QOAC-B1-ENGINEERING|"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--engineering",type=Path,required=True)
    p.add_argument("--holdout",type=Path,required=True)
    p.add_argument("--provenance",type=Path,required=True)
    a=p.parse_args()
    repo=a.repo_root.resolve()
    meta={r["material_id"]:r for r in csv.DictReader(open(repo/"materials_metadata.csv",encoding="utf-8"))}
    ref=[r for r in csv.DictReader(open(repo/"analysis/extensions_20260930/WP-G/reference.csv",encoding="utf-8")) if r["status"]=="SUCCESS"]
    avail={r["material_id"]:r for r in csv.DictReader(open(repo/"analysis/extensions_20260930/WP-G/aeccar_availability.csv",encoding="utf-8"))}
    if len(ref)!=50: raise RuntimeError(f"expected 50 successful WP-G materials, got {len(ref)}")
    rows=[]
    for r in ref:
        m=r["material_id"]; z=dict(meta[m]); z["task_id"]=avail[m]["task_id"]; rows.append(z)
    rows.sort(key=lambda r:(int(r["npoints"]),r["material_id"]))
    eng=[]; n=len(rows)
    for k in range(N_ENG):
        lo=(k*n)//N_ENG; hi=((k+1)*n)//N_ENG
        bucket=rows[lo:hi]
        if not bucket: raise RuntimeError(f"empty stratum {k}")
        q=min(bucket,key=lambda r:hashlib.sha256((PREFIX+r["material_id"]).encode()).hexdigest())
        q=dict(q); q["selection_stratum"]=f"{k+1}of{N_ENG}"
        q["selection_hash"]=hashlib.sha256((PREFIX+q["material_id"]).encode()).hexdigest()
        eng.append(q)
    eset={r["material_id"] for r in eng}
    hold=[dict(r,selection_stratum="HOLDOUT",selection_hash="") for r in rows if r["material_id"] not in eset]
    if len(eng)!=12 or len(hold)!=38 or eset & {r["material_id"] for r in hold}: raise RuntimeError("split cardinality failure")
    fields=["material_id","task_id","corpus","system_type","source","formula","ngrid","sha256","url","source_bytes","npoints","natoms","selection_stratum","selection_hash"]
    for path,data in ((a.engineering,eng),(a.holdout,hold)):
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
            for r in data: w.writerow({k:r.get(k,"") for k in fields})
    a.provenance.write_text(json.dumps({
        "freeze_date":"2026-10-05","source_population":"50 successful WP-G all-electron-reference materials",
        "engineering_rule":"12 npoints strata; min sha256('QOAC-B1-ENGINEERING|'+material_id)",
        "engineering_ids":[r["material_id"] for r in eng],
        "holdout_ids":[r["material_id"] for r in hold],
    },indent=2)+"\n",encoding="utf-8")
    print("QOAC_B1_SPLIT",len(eng),len(hold),[r["material_id"] for r in eng])
    return 0
if __name__=="__main__": raise SystemExit(main())
