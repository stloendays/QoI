#!/usr/bin/env python3
"""Aggregate frozen QOAC-B1 engineering gates."""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np
import pandas as pd

PRIMARY=1e-3

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--engineering-manifest",type=Path,required=True)
    p.add_argument("--holdout-manifest",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    eng=pd.read_csv(a.engineering_manifest); hold=pd.read_csv(a.holdout_manifest)
    js=[]
    for pth in sorted(a.shards_root.glob("*.json")):
        try: js.append(json.loads(pth.read_text()))
        except Exception: pass
    if len(js)!=12: raise RuntimeError(f"expected 12 material JSONs, got {len(js)}")
    if set(x["material_id"] for x in js)!=set(eng.material_id): raise RuntimeError("engineering population mismatch")
    failed=[x for x in js if x.get("status")!="SUCCESS"]
    if failed: raise RuntimeError(f"material failures: {[x['material_id'] for x in failed]}")
    rows=pd.DataFrame([r for x in js for r in x["rows"]])
    ver=pd.DataFrame([dict(material_id=x["material_id"],**v) for x in js for v in x["verification"]])
    primary=ver[(ver.tau_e==PRIMARY)&(ver.status=="OK")].copy()
    p=primary[primary.method=="P"].copy(); r=primary[primary.method=="R"].copy()
    if len(r)!=12: raise RuntimeError(f"primary R verification count {len(r)} != 12")
    gateA=bool((r.actual_reassigned_frac==0).all() and (r.actual_bader_error_e<=2e-6).all() and (r.closure_scaled<=1e-9).all())
    wins=int((r.cr_ratio_candidate_over_baseline>1).sum())
    med=float(np.median(r.cr_ratio_candidate_over_baseline))
    gateB=bool(wins>=9 and med>1.05)
    merged=r[["material_id","candidate_cr"]].merge(p[["material_id","candidate_cr"]],on="material_id",suffixes=("_R","_P"))
    rp=merged.candidate_cr_R/merged.candidate_cr_P
    med_rp=float(np.median(rp)) if len(rp)==12 else float("nan")
    gateC=bool(len(rp)==12 and med_rp>1.02)
    summary={
      "status":"COMPLETE","engineering_materials":12,"holdout_materials_frozen":int(len(hold)),
      "rows":int(len(rows)),"verification_rows":int(len(ver)),
      "gate_A_nullspace_mechanism":{"go":gateA,"max_actual_bader_error_e":float(r.actual_bader_error_e.max()),"max_reassigned_frac":float(r.actual_reassigned_frac.max()),"max_closure_scaled":float(r.closure_scaled.max())},
      "gate_B_matched_field_utility":{"go":gateB,"wins":wins,"median_cr_ratio_R_over_G1":med},
      "gate_C_transform_over_projection":{"go":gateC,"median_cr_ratio_R_over_P":med_rp},
      "holdout_authorized":bool(gateA and gateB),
      "primary_representation":"R" if gateC else "P_or_redesign"
    }
    rows.to_csv(out/"engineering_rows.csv",index=False); ver.to_csv(out/"engineering_verification.csv",index=False)
    eng.to_csv(out/"ENGINEERING_MANIFEST.csv",index=False); hold.to_csv(out/"FROZEN_HOLDOUT_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# QOAC-B1 fixed-partition engineering results\n\n"+
      f"- Gate A — nullspace mechanism: **{'GO' if gateA else 'NO-GO'}**; max actual Bader error {r.actual_bader_error_e.max():.3g} e; max reassignment {r.actual_reassigned_frac.max():.3g}.\n"+
      f"- Gate B — matched-field utility: **{'GO' if gateB else 'NO-GO'}**; wins {wins}/12; median CR ratio R/G1 **{med:.3f}x**.\n"+
      f"- Gate C — residual transform beyond repair: **{'GO' if gateC else 'NO-GO'}**; median CR ratio R/P **{med_rp:.3f}x**.\n"+
      f"- Frozen 38-material holdout authorized: **{bool(gateA and gateB)}**.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
