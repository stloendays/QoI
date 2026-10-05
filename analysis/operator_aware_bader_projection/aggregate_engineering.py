#!/usr/bin/env python3
"""Aggregate QOAC-B2 engineering frontier and frozen GO/NO-GO gates."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

KAPPAS=(1.0,2.0,4.0,8.0,16.0)
PRIMARY=4.0


def bootstrap_median_ci(x,nboot=50000,seed=20261005):
    x=np.asarray(x,dtype=float); rng=np.random.default_rng(seed); n=len(x)
    sims=np.empty(nboot,dtype=float)
    for i in range(nboot):
        sims[i]=np.median(x[rng.integers(0,n,n)])
    return float(np.quantile(sims,0.025)),float(np.quantile(sims,0.975))


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
    if len(js)!=12: raise RuntimeError(f"expected 12 JSONs, got {len(js)}")
    if set(x["material_id"] for x in js)!=set(eng.material_id): raise RuntimeError("engineering population mismatch")
    failed=[x for x in js if x.get("status")!="SUCCESS"]
    if failed: raise RuntimeError(f"material failures: {[x['material_id'] for x in failed]}")
    rows=pd.DataFrame([dict(material_id=x["material_id"],**r) for x in js for r in x["frontier"]])
    if len(rows)!=12*len(KAPPAS): raise RuntimeError(f"expected 60 frontier rows, got {len(rows)}")

    summaries=[]
    for k in KAPPAS:
        z=rows[np.isclose(rows.kappa,k)].copy()
        ratios=z.cr_ratio_over_baseline.to_numpy(float)
        lo,hi=bootstrap_median_ci(ratios)
        summaries.append({
            "kappa":k,"materials":len(z),"wins":int(np.count_nonzero(ratios>1.0)),
            "median_cr_ratio":float(np.median(ratios)),
            "bootstrap_median_95_ci":[lo,hi],
            "min_cr_ratio":float(np.min(ratios)),"max_cr_ratio":float(np.max(ratios)),
            "median_linf_ratio":float(np.median(z.linf_ratio_over_baseline)),
            "max_linf_ratio":float(np.max(z.linf_ratio_over_baseline)),
            "max_actual_bader_error_e":float(np.max(z.actual_bader_error_e)),
            "max_reassigned_frac":float(np.max(z.actual_reassigned_frac)),
            "max_side_channel_fraction":float(np.max(z.side_channel_fraction)),
        })

    p4=rows[np.isclose(rows.kappa,PRIMARY)].copy()
    gateA=bool((p4.actual_bader_error_e<=2e-6).all() and (p4.actual_reassigned_frac==0).all() and (p4.max_rel_region_sum_error_scaled<=1e-9).all())
    wins=int((p4.cr_ratio_over_baseline>1).sum())
    med=float(np.median(p4.cr_ratio_over_baseline))
    gateB=bool(wins>=9 and med>1.50)
    gateC=bool((p4.side_channel_fraction<0.01).all())
    summary={
      "status":"COMPLETE",
      "engineering_materials":12,
      "frozen_holdout_materials":int(len(hold)),
      "primary_kappa":PRIMARY,
      "gate_A_scientific_closure":{"go":gateA,"max_bader_error_e":float(p4.actual_bader_error_e.max()),"max_reassigned_frac":float(p4.actual_reassigned_frac.max()),"max_closure_scaled":float(p4.max_rel_region_sum_error_scaled.max())},
      "gate_B_useful_rate_gain":{"go":gateB,"wins":wins,"median_cr_ratio":med},
      "gate_C_side_channel":{"go":gateC,"max_side_channel_fraction":float(p4.side_channel_fraction.max())},
      "holdout_authorized":bool(gateA and gateB and gateC),
      "frontier":summaries
    }
    rows.to_csv(out/"engineering_frontier.csv",index=False)
    eng.to_csv(out/"ENGINEERING_MANIFEST.csv",index=False)
    hold.to_csv(out/"FROZEN_HOLDOUT_MANIFEST.csv",index=False)
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    lines=[
      "# QOAC-B2 projection-aware engineering results","",
      f"- Primary auxiliary density budget: **kappa = {PRIMARY:g}**.",
      f"- Gate A scientific closure: **{'GO' if gateA else 'NO-GO'}**.",
      f"- Gate B useful rate gain: **{'GO' if gateB else 'NO-GO'}**; wins **{wins}/12**; median CR ratio **{med:.3f}x**.",
      f"- Gate C side-channel practicality: **{'GO' if gateC else 'NO-GO'}**; max side-channel fraction **{p4.side_channel_fraction.max():.4%}**.",
      f"- Frozen 38-material holdout authorized: **{bool(gateA and gateB and gateC)}**.","",
      "| kappa | wins | median CR ratio | median Linf ratio | max Bader error |",
      "|---:|---:|---:|---:|---:|",
    ]
    for s in summaries:
        lines.append(f"| {s['kappa']:g} | {s['wins']}/12 | {s['median_cr_ratio']:.3f}x | {s['median_linf_ratio']:.3f}x | {s['max_actual_bader_error_e']:.3g} e |")
    (out/"RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
