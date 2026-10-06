#!/usr/bin/env python3
"""Aggregate QOAC v0.3 engineering with the frozen gates G1-G3 (DESIGN.md)."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def many(root,pat):
    xs=[pd.read_csv(p) for p in sorted(root.rglob(pat)) if p.stat().st_size>2]
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir; out.mkdir(parents=True,exist_ok=True)
    man=pd.read_csv(a.manifest); rows=many(a.shards_root,"rows_*.csv"); fails=many(a.shards_root,"failures_*.csv")
    rows.to_csv(out/"engineering_rows.csv",index=False)
    if len(fails): fails.to_csv(out/"engineering_failures.csv",index=False)
    cert=rows[rows.certified.astype(str).str.lower()=="true"]
    best=cert.groupby(["material_id","tau","arm"]).cr.max().unstack("arm")
    best.reset_index().to_csv(out/"engineering_material.csv",index=False)
    summ={"status":"COMPLETE","materials":int(man.material_id.nunique()),"failures":int(len(fails)),
          "failures_by_arm":fails.groupby("arm").size().to_dict() if len(fails) else {}}
    for tau,b in best.groupby(level="tau"):
        b=b.droplevel("tau").reindex(man.material_id)
        comp=b[["A1","A2"]].max(axis=1)
        r3=b.A3/comp
        d={"A3_certified":int(b.A3.notna().sum()),"median_cr":{k:float(b[k].median()) for k in b.columns},
           "R3_vs_best_A1_A2":{"wins":int((r3>1).sum()),"median":float(r3.median()),"min":float(r3.min())},
           "A3_over_A5_median":float((b.A3/b.A5).median()),"A3_over_A4_median":float((b.A3/b.A4).median()),
           "A1_over_A0_median":float((b.A1/b.A0).median()),"A3_over_A6_median":float((b.A3/b.A6).median()),
           "A3_over_A0_median":float((b.A3/b.A0).median())}
        summ[f"tau_{tau:g}"]=d
    p6=summ["tau_1e-06"]
    g1=p6["A3_certified"]==12; g2=p6["R3_vs_best_A1_A2"]["wins"]>=10 and p6["R3_vs_best_A1_A2"]["median"]>1.20; g3=p6["A3_over_A5_median"]>2.0
    summ.update(gate_G1={"go":g1},gate_G2={"go":g2},gate_G3={"go":g3},confirmatory_authorized=bool(g1 and g2 and g3))
    (out/"SUMMARY.json").write_text(json.dumps(summ,indent=2),encoding="utf-8"); print(json.dumps(summ,indent=2))

if __name__=="__main__": raise SystemExit(main())
