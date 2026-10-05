#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--metadata",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--provenance",type=Path,required=True)
    a=p.parse_args()
    with a.metadata.open(newline="",encoding="utf-8") as f:
        rows=[r for r in csv.DictReader(f) if r.get("corpus","").startswith("dev_") and r.get("system_type") in {"bulk","slab"}]
    rows.sort(key=lambda r:(r["system_type"],int(r["npoints"]),r["material_id"]))
    bulk=sum(r["system_type"]=="bulk" for r in rows); slab=sum(r["system_type"]=="slab" for r in rows)
    if (bulk,slab,len(rows))!=(186,68,254):
        raise RuntimeError(f"unexpected development population: bulk={bulk} slab={slab} total={len(rows)}")
    fields=["material_id","corpus","system_type","source","formula","ngrid","sha256","url","source_bytes","npoints","natoms"]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,"") for k in fields})
    a.provenance.write_text(json.dumps({
      "freeze_date":"2026-10-05","population":"all development bulk/slab materials",
      "bulk":bulk,"slab":slab,"total":len(rows),"material_ids":[r["material_id"] for r in rows]
    },indent=2)+"\n",encoding="utf-8")
    print("QOAC_H_V02_CENSUS_MANIFEST",len(rows),bulk,slab)
    return 0
if __name__=="__main__": raise SystemExit(main())
