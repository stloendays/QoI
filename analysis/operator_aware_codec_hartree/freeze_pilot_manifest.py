#!/usr/bin/env python3
"""Freeze the deterministic 12-material QOAC-H v0.1 pilot manifest."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
PER_TYPE = 6
PREFIX = "QOAC-H-V01|"

def pick(rows, system_type):
    x=[r for r in rows if r.get("system_type")==system_type and r.get("corpus","").startswith("dev_")]
    x.sort(key=lambda r:(int(r["npoints"]),r["material_id"]))
    if len(x)<PER_TYPE: raise RuntimeError(f"not enough {system_type} candidates: {len(x)}")
    out=[]; n=len(x)
    for k in range(PER_TYPE):
        lo=(k*n)//PER_TYPE; hi=((k+1)*n)//PER_TYPE
        bucket=x[lo:hi]
        if not bucket: raise RuntimeError(f"empty {system_type} size stratum {k}")
        chosen=min(bucket,key=lambda r:hashlib.sha256((PREFIX+r["material_id"]).encode()).hexdigest())
        q=dict(chosen)
        q["selection_stratum"]=f"{system_type}_{k+1}of{PER_TYPE}"
        q["selection_hash"]=hashlib.sha256((PREFIX+q["material_id"]).encode()).hexdigest()
        out.append(q)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--metadata",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--provenance",type=Path,required=True)
    args=ap.parse_args()
    with args.metadata.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
    selected=pick(rows,"bulk")+pick(rows,"slab")
    if len(selected)!=12 or len({r["material_id"] for r in selected})!=12:
        raise RuntimeError("pilot manifest cardinality failure")
    fields=["material_id","corpus","system_type","source","formula","ngrid","sha256","url","source_bytes","npoints","natoms","selection_stratum","selection_hash"]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in selected: w.writerow({k:r.get(k,"") for k in fields})
    prov={
        "date":"2026-10-05",
        "population":"development bulk/slab metadata only",
        "per_system_type":PER_TYPE,
        "selection":"npoints six-stratum; minimum sha256('QOAC-H-V01|'+material_id) within stratum",
        "material_ids":[r["material_id"] for r in selected],
    }
    args.provenance.write_text(json.dumps(prov,indent=2)+"\n",encoding="utf-8")
    print("QOAC_H_MANIFEST_FROZEN",len(selected),prov["material_ids"])
    return 0
if __name__=="__main__": raise SystemExit(main())
