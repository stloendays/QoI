#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def q(x,p): return float(np.quantile(np.asarray(x,dtype=float),p))

def stats(x):
    a=np.asarray(x,dtype=float)
    return {"min":float(a.min()),"p05":q(a,.05),"p25":q(a,.25),"median":float(np.median(a)),"p75":q(a,.75),"p95":q(a,.95),"max":float(a.max())}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    man=pd.read_csv(a.manifest)
    js=[json.loads(p.read_text()) for p in sorted(a.shards_root.glob("mp-*.json"))]
    if len(js)!=50 or set(x["material_id"] for x in js)!=set(man.material_id): raise RuntimeError("50-material census population mismatch")
    failed=[x for x in js if x["status"]!="SUCCESS"]
    if failed: raise RuntimeError(f"material failures: {[x['material_id'] for x in failed]}")
    df=pd.DataFrame(js)
    if not (df.partition_decode_exact_raw.all() and df.partition_decode_exact_rle.all() and df.partition_decode_exact_best.all()):
        raise RuntimeError("partition decode mismatch")
    maxerr=float(df.direct_charge_max_error_e.max())
    if maxerr>2e-6: raise RuntimeError(f"semantic equivalence failed: {maxerr}")
    pr=df.partition_replacement_ratio.to_numpy(float)
    ar=df.archive_ratio_baseline_over_compiled.to_numpy(float)
    summary={
      "status":"COMPLETE","materials":50,"failures":0,
      "semantic_equivalence":{"exact_decode":50,"max_direct_charge_error_e":maxerr},
      "partition_encoding_method_counts":df.best_partition_method.value_counts().to_dict(),
      "partition_replacement_ratio_lossless_AE_over_map":stats(pr),
      "complete_archive_ratio_baseline_over_compiled":{
        **stats(ar),"wins":int(np.count_nonzero(ar>1)),"win_fraction":float(np.mean(ar>1))
      },
      "partition_fraction_of_compiled_archive":stats(df.partition_fraction_of_compiled_archive),
      "b2_source_counts":df.b2_source.value_counts().to_dict(),
    }
    df.to_csv(out/"census_material.csv",index=False)
    man.to_csv(out/"CENSUS_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# QOAC-B3 full 50-material descriptive census\n\n"+
      f"- Materials: **50/50 complete**, failures: **0**.\n"+
      f"- Exact partition decode: **50/50**; max direct-map/Henkelman charge error **{maxerr:.3g} e**.\n"+
      f"- Lossless AE / exact partition bytes: median **{np.median(pr):.2f}x**, P05 **{np.quantile(pr,.05):.2f}x**, minimum **{np.min(pr):.2f}x**.\n"+
      f"- Complete archive wins: **{int(np.count_nonzero(ar>1))}/50**; median baseline/compiled bytes **{np.median(ar):.2f}x**, P05 **{np.quantile(ar,.05):.2f}x**, minimum **{np.min(ar):.2f}x**.\n"+
      f"- Partition-map encoding methods: **{df.best_partition_method.value_counts().to_dict()}**.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
