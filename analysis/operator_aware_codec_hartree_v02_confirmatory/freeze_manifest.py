#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
PER_TYPE=24
PREFIX="QOAC-H-V02-CONFIRM|"

def pick(rows,system_type,exclude):
    x=[r for r in rows if r.get("system_type")==system_type and r.get("corpus","").startswith("dev_") and r["material_id"] not in exclude]
    x.sort(key=lambda r:(int(r["npoints"]),r["material_id"]))
    if len(x)<PER_TYPE: raise RuntimeError(f"not enough {system_type} candidates: {len(x)}")
    out=[]; n=len(x)
    for k in range(PER_TYPE):
        lo=(k*n)//PER_TYPE; hi=((k+1)*n)//PER_TYPE
        bucket=x[lo:hi]
        if not bucket: raise RuntimeError(f"empty {system_type} stratum {k}")
        q=min(bucket,key=lambda r:hashlib.sha256((PREFIX+r["material_id"]).encode()).hexdigest())
        z=dict(q)
        z["selection_stratum"]=f"{system_type}_{k+1}of{PER_TYPE}"
        z["selection_hash"]=hashlib.sha256((PREFIX+z["material_id"]).encode()).hexdigest()
        out.append(z)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--metadata",type=Path,required=True)
    p.add_argument("--engineering-manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--provenance",type=Path,required=True)
    a=p.parse_args()
    with a.metadata.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
    with a.engineering_manifest.open(newline="",encoding="utf-8") as f: eng=list(csv.DictReader(f))
    exclude={r["material_id"] for r in eng}
    if len(exclude)!=12: raise RuntimeError("engineering exclusion set must contain 12 materials")
    chosen=pick(rows,"bulk",exclude)+pick(rows,"slab",exclude)
    if len(chosen)!=48 or len({r["material_id"] for r in chosen})!=48: raise RuntimeError("confirmatory manifest cardinality failure")
    if exclude & {r["material_id"] for r in chosen}: raise RuntimeError("confirmatory/engineering overlap")
    fields=["material_id","corpus","system_type","source","formula","ngrid","sha256","url","source_bytes","npoints","natoms","selection_stratum","selection_hash"]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in chosen: w.writerow({k:r.get(k,"") for k in fields})
    prov={
      "freeze_date":"2026-10-05","n":48,"bulk":24,"slab":24,
      "engineering_excluded":sorted(exclude),
      "rule":"24 npoints strata/type; minimum sha256('QOAC-H-V02-CONFIRM|'+material_id)",
      "material_ids":[r["material_id"] for r in chosen]
    }
    a.provenance.write_text(json.dumps(prov,indent=2)+"\n",encoding="utf-8")
    print("QOAC_H_V02_CONFIRM_MANIFEST",len(chosen))
    return 0
if __name__=="__main__": raise SystemExit(main())
