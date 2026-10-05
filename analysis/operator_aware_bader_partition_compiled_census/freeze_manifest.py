#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--provenance",type=Path,required=True)
    a=p.parse_args(); repo=a.repo_root.resolve()
    meta={r["material_id"]:r for r in csv.DictReader(open(repo/"materials_metadata.csv",encoding="utf-8"))}
    avail={r["material_id"]:r for r in csv.DictReader(open(repo/"analysis/extensions_20260930/WP-G/aeccar_availability.csv",encoding="utf-8"))}
    success=[r for r in csv.DictReader(open(repo/"analysis/extensions_20260930/WP-G/reference.csv",encoding="utf-8")) if r["status"]=="SUCCESS"]
    if len(success)!=50: raise RuntimeError(f"expected 50 successful WP-G materials, got {len(success)}")
    rows=[]
    for r in success:
        mid=r["material_id"]
        z=dict(meta[mid]); z["task_id"]=avail[mid]["task_id"]; rows.append(z)
    rows.sort(key=lambda r:r["material_id"])
    fields=["material_id","task_id","corpus","system_type","source","formula","ngrid","sha256","url","source_bytes","npoints","natoms"]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,"") for k in fields})
    a.provenance.write_text(json.dumps({
      "freeze_date":"2026-10-05",
      "population":"all 50 successful WP-G all-electron-reference materials",
      "material_ids":[r["material_id"] for r in rows],
      "excluded_published_input_failures":["mp-1192831","mp-1193567","mp-776331"]
    },indent=2)+"\n",encoding="utf-8")
    print("QOAC_B3_CENSUS_MANIFEST",len(rows))
    return 0
if __name__=="__main__": raise SystemExit(main())
