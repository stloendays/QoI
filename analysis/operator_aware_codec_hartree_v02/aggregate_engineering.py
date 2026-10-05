#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
TAU=1e-6

def many(root,pat):
    xs=[pd.read_csv(p) for p in sorted(root.glob(pat)) if p.stat().st_size]
    return pd.concat(xs,ignore_index=True) if xs else pd.DataFrame()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    repo=a.repo_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    rows=many(a.shards_root,"rows_shard_*.csv"); fails=many(a.shards_root,"failures_shard_*.csv"); planned=many(a.shards_root,"planned_shard_*.csv")
    manifest=pd.read_csv(a.manifest)
    if set(planned.material_id)!=set(manifest.material_id): raise RuntimeError("planned population mismatch")
    if len(rows)!=12*26: raise RuntimeError(f"expected 312 successful rows, got {len(rows)}")
    if len(fails): raise RuntimeError(f"engineering failures present: {len(fails)}")

    v01=pd.read_csv(repo/"analysis/operator_aware_codec_hartree/results/pilot_rows.csv")
    comp01=pd.read_csv(repo/"analysis/operator_aware_codec_hartree/results/competitive_material.csv")
    rec=[]
    for mid in manifest.material_id:
        v2=rows[(rows.material_id==mid)&(rows.purpose=="certificate")&(rows.hartree_error_rel_RMSE_historical<TAU)]
        v1=v01[(v01.material_id==mid)&(v01.beta==2.0)&(v01.hartree_error_rel_RMSE_historical<TAU)]
        base=comp01[comp01.material_id==mid].iloc[0]
        floor=rows[(rows.material_id==mid)&(rows.purpose=="floor_probe")].iloc[0]
        best2=v2.loc[v2.compression_ratio.idxmax()] if len(v2) else None
        best1=v1.loc[v1.compression_ratio.idxmax()] if len(v1) else None
        rec.append({
            "material_id":mid,
            "baseline_codec":base.baseline_codec,
            "baseline_cr":float(base.baseline_best_cr),
            "v01_best_certified_cr":float(best1.compression_ratio) if best1 is not None else np.nan,
            "v02_best_certified_cr":float(best2.compression_ratio) if best2 is not None else np.nan,
            "v02_best_hartree_error":float(best2.hartree_error_rel_RMSE_historical) if best2 is not None else np.nan,
            "v02_alpha_rel_ptp":float(best2.alpha_rel_ptp) if best2 is not None else np.nan,
            "v02_over_v01":float(best2.compression_ratio/best1.compression_ratio) if best2 is not None and best1 is not None else np.nan,
            "v02_over_baseline":float(best2.compression_ratio/base.baseline_best_cr) if best2 is not None else np.nan,
            "floor_probe_cr":float(floor.compression_ratio),
            "floor_over_baseline":float(floor.compression_ratio/base.baseline_best_cr)
        })
    mat=pd.DataFrame(rec)
    sperr=mat[mat.baseline_codec=="SPERR"]
    gate_a=bool(len(sperr)==3 and np.all(sperr.floor_over_baseline>1.25))
    gate_b=bool(np.all(np.isfinite(mat.v02_over_v01)) and float(np.median(mat.v02_over_v01))>1.05)
    wins=int(np.count_nonzero(mat.v02_over_baseline>1.0))
    medbase=float(np.median(mat.v02_over_baseline))
    gate_c=bool(wins>=9 and medbase>1.05)
    summary={
      "status":"COMPLETE","materials":12,"rows_success":int(len(rows)),"failures":int(len(fails)),
      "tau_historical_rel_RMSE":TAU,
      "gate_A_rate_floor_removed":{"go":gate_a,"sperr_cases":int(len(sperr)),"min_floor_over_baseline":float(sperr.floor_over_baseline.min())},
      "gate_B_certified_representation_improvement":{"go":gate_b,"median_v02_over_v01":float(np.median(mat.v02_over_v01))},
      "gate_C_confirmatory_candidate":{"go":gate_c,"wins_over_best_baseline":wins,"median_v02_over_best_baseline":medbase},
      "confirmatory_authorized":bool(gate_a and gate_b and gate_c)
    }
    rows.to_csv(out/"engineering_rows.csv",index=False); mat.to_csv(out/"engineering_material.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"RESULTS.md").write_text(
      "# QOAC-H v0.2 engineering results\n\n"+
      f"- Gate A rate-floor removal: **{'GO' if gate_a else 'NO-GO'}**; minimum former-SPERR floor/baseline = **{sperr.floor_over_baseline.min():.3f}x**.\n"+
      f"- Gate B certified v0.2/v0.1 improvement: **{'GO' if gate_b else 'NO-GO'}**; median = **{np.median(mat.v02_over_v01):.3f}x**.\n"+
      f"- Gate C confirmatory-candidate performance: **{'GO' if gate_c else 'NO-GO'}**; wins = **{wins}/12**, median v0.2/best baseline = **{medbase:.3f}x**.\n"+
      f"- Confirmatory experiment authorized: **{summary['confirmatory_authorized']}**.\n",
      encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
