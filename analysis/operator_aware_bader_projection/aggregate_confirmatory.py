#!/usr/bin/env python3
"""Aggregate QOAC-B2 fixed-partition holdout confirmation."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import numpy as np
import pandas as pd

TAUS=(1e-4,1e-3,1e-2)
PRIMARY=1e-3

def pct(x,p): return float(np.quantile(np.asarray(x,float),p))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); repo=a.repo_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    manifest=pd.read_csv(a.manifest)
    if len(manifest)!=38 or manifest.material_id.nunique()!=38: raise RuntimeError("holdout manifest must contain 38 unique materials")
    js=[]
    for f in sorted(a.shards_root.glob("*.json")):
        if f.name.startswith("planned_"): continue
        try:
            x=json.loads(f.read_text())
            if isinstance(x,dict) and "material_id" in x: js.append(x)
        except Exception: pass
    if set(x["material_id"] for x in js)!=set(manifest.material_id): raise RuntimeError("holdout result population mismatch")
    fail=[x for x in js if x["status"]!="SUCCESS"]
    if fail: raise RuntimeError(f"material failures: {[x['material_id'] for x in fail]}")
    rows=pd.DataFrame([r for x in js for r in x["rows"]])
    expected=sum(1 for r in csv.DictReader(open(repo/"analysis/extensions_20260930/WP-G/rows.csv",encoding="utf-8"))
                 if r["status"]=="OK" and r["material_id"] in set(manifest.material_id))
    if len(rows)!=expected: raise RuntimeError(f"row completeness {len(rows)} != {expected}")

    gateA=bool((rows.actual_bader_error_e<=2e-6).all() and (rows.actual_reassigned_frac==0).all() and (rows.max_rel_region_sum_error_scaled<=1e-9).all())
    ov=rows.rate_overhead_fraction.to_numpy(float)
    gateB=bool(np.median(ov)<0.001 and pct(ov,.95)<0.01 and np.max(ov)<0.05)
    lr=rows.linf_inflation_ratio.to_numpy(float)
    gateC=bool(np.median(lr)<=1.01 and pct(lr,.95)<=1.10 and np.max(lr)<=1.25)

    rescue=[]
    for tau in TAUS:
        bad=rows[rows.generic_bader_error_e>=tau].copy()
        rr=bad[(bad.actual_bader_error_e<tau)&(bad.actual_reassigned_frac==0)&(bad.linf_inflation_ratio<=1.05)]
        badm=set(bad.material_id); resm=set(rr.material_id)
        rescue.append({
          "tau_e":tau,"generic_failure_rows":int(len(bad)),"rescued_rows":int(len(rr)),
          "rescued_row_fraction":float(len(rr)/len(bad)) if len(bad) else float("nan"),
          "generic_failure_materials":int(len(badm)),"materials_with_rescue":int(len(resm)),
          "rescued_material_fraction":float(len(resm)/len(badm)) if badm else float("nan")
        })
    prim=next(x for x in rescue if x["tau_e"]==PRIMARY)
    gateD=bool(prim["rescued_row_fraction"]>=0.80 and prim["rescued_material_fraction"]>=0.80)
    summary={
      "status":"COMPLETE","confirmatory_pass":bool(gateA and gateB and gateC and gateD),
      "materials":38,"rows":int(len(rows)),"failures":0,
      "gate_A_actual_bader_guarantee":{"go":gateA,"max_bader_error_e":float(rows.actual_bader_error_e.max()),"max_reassigned_frac":float(rows.actual_reassigned_frac.max()),"max_closure_scaled":float(rows.max_rel_region_sum_error_scaled.max())},
      "gate_B_rate_overhead":{"go":gateB,"median":float(np.median(ov)),"p95":pct(ov,.95),"max":float(np.max(ov))},
      "gate_C_field_fidelity":{"go":gateC,"median_linf_ratio":float(np.median(lr)),"p95_linf_ratio":pct(lr,.95),"max_linf_ratio":float(np.max(lr))},
      "gate_D_primary_rescue":{"go":gateD,**prim},
      "rescue_by_tau":rescue
    }
    rows.to_csv(out/"confirmatory_rows.csv",index=False)
    manifest.to_csv(out/"HOLDOUT_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# QOAC-B2 fixed-partition projection confirmation\n\n"+
      f"Status: **{'PASS' if summary['confirmatory_pass'] else 'FAIL'}**\n\n"+
      f"- Actual Bader guarantee: **{'GO' if gateA else 'NO-GO'}**; max error {rows.actual_bader_error_e.max():.3g} e; max reassignment {rows.actual_reassigned_frac.max():.3g}.\n"+
      f"- Rate overhead: **{'GO' if gateB else 'NO-GO'}**; median {np.median(ov):.3%}, P95 {pct(ov,.95):.3%}, max {np.max(ov):.3%}.\n"+
      f"- Field Linf inflation: **{'GO' if gateC else 'NO-GO'}**; median {np.median(lr):.4f}x, P95 {pct(lr,.95):.4f}x, max {np.max(lr):.4f}x.\n"+
      f"- Rescue at 1e-3 e: **{'GO' if gateD else 'NO-GO'}**; {prim['rescued_rows']}/{prim['generic_failure_rows']} rows ({prim['rescued_row_fraction']:.1%}), {prim['materials_with_rescue']}/{prim['generic_failure_materials']} affected materials.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
