#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--engineering-manifest",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    eng=pd.read_csv(a.engineering_manifest)
    js=[json.loads(p.read_text()) for p in sorted(a.shards_root.glob("mp-*.json"))]
    if len(js)!=12 or set(x["material_id"] for x in js)!=set(eng.material_id): raise RuntimeError("engineering population mismatch")
    failed=[x for x in js if x["status"]!="SUCCESS"]
    if failed: raise RuntimeError(f"material failures: {[x['material_id'] for x in failed]}")
    df=pd.DataFrame(js)
    gateA=bool(df.partition_decode_exact_raw.all() and df.partition_decode_exact_rle.all() and df.partition_decode_exact_best.all() and (df.direct_charge_max_error_e<=2e-6).all())
    gateB=bool((df.partition_replacement_ratio>1).all() and float(np.median(df.partition_replacement_ratio))>2)
    wins=int((df.archive_ratio_baseline_over_compiled>1).sum())
    med=float(np.median(df.archive_ratio_baseline_over_compiled))
    gateC=bool(wins>=10 and med>1.25)
    methods=df.best_partition_method.value_counts().to_dict()
    summary={
      "status":"COMPLETE","materials":12,
      "gate_A_semantic_equivalence":{"go":gateA,"max_direct_charge_error_e":float(df.direct_charge_max_error_e.max())},
      "gate_B_partition_efficiency":{"go":gateB,"median_partition_replacement_ratio":float(np.median(df.partition_replacement_ratio)),"min_partition_replacement_ratio":float(df.partition_replacement_ratio.min()),"method_counts":methods},
      "gate_C_archive_utility":{"go":gateC,"wins":wins,"median_archive_ratio":med,"min_archive_ratio":float(df.archive_ratio_baseline_over_compiled.min())},
      "full_50_census_authorized":bool(gateA and gateB),
    }
    df.to_csv(out/"engineering_material.csv",index=False); eng.to_csv(out/"ENGINEERING_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# QOAC-B3 compiled-partition engineering results\n\n"+
      f"- Gate A semantic equivalence: **{'GO' if gateA else 'NO-GO'}**; max direct-charge error **{df.direct_charge_max_error_e.max():.3g} e**.\n"+
      f"- Gate B partition efficiency: **{'GO' if gateB else 'NO-GO'}**; median lossless-AE / partition bytes **{np.median(df.partition_replacement_ratio):.2f}x**.\n"+
      f"- Gate C complete archive utility: **{'GO' if gateC else 'NO-GO'}**; wins **{wins}/12**; median baseline/compiled archive bytes **{med:.2f}x**.\n"+
      f"- Full 50-material descriptive census authorized: **{bool(gateA and gateB)}**.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
