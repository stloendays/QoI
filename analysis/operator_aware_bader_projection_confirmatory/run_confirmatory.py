#!/usr/bin/env python3
"""Run frozen QOAC-B2 confirmation on a shard of the 38-material holdout."""
from __future__ import annotations

import argparse,csv,hashlib,json,sys,tempfile,time
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
B1=HERE.parent/"operator_aware_bader_fixed_partition"
sys.path.insert(0,str(B1))
import qoac_b_core as qb
import run_engineering as b1

TAU=1e-3
KAPPA=4.0


def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--frozen-root",type=Path,required=True)
    p.add_argument("--holdout-manifest",type=Path,required=True)
    p.add_argument("--shard-count",type=int,required=True)
    p.add_argument("--shard-index",type=int,required=True)
    p.add_argument("--bader",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    return p.parse_args()


def baseline_for(mid,wp,raw_bytes):
    ok=[r for r in wp if r["material_id"]==mid and r["status"]=="OK" and float(r["g1_error_e"])<TAU]
    if not ok:
        raise RuntimeError("no frozen G1 baseline certified at tau=1e-3")
    best=max(ok,key=lambda r:raw_bytes/int(r["chgcar_bytes"]))
    return best,raw_bytes/int(best["chgcar_bytes"]),float(best["realized_Linf"])


def process(meta,a,core,dev):
    mid=meta["material_id"]
    t0=time.time()
    result={"material_id":mid,"status":"SUCCESS","projected_rows":[],"candidate":None,"failures":[]}
    try:
        chg_blob=b1.fetch(meta["url"])
        if hashlib.sha256(chg_blob).hexdigest()!=meta["sha256"] or len(chg_blob)!=int(meta["source_bytes"]):
            raise RuntimeError("CHGCAR checksum/byte mismatch")
        a0=b1.fetch(b1.BUCKET+f"aeccar0s/{meta['task_id']}.json.gz")
        a2=b1.fetch(b1.BUCKET+f"aeccar2s/{meta['task_id']}.json.gz")
        with tempfile.TemporaryDirectory(prefix="qoacb2_confirm_") as td:
            work=Path(td)
            grid,_=dev.build_grid(meta,chg_blob,work)
            chg=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
            ae=np.asarray(dev.decode_mp_chgcar(a0).data["total"],dtype=np.float64)+np.asarray(dev.decode_mp_chgcar(a2).data["total"],dtype=np.float64)
            if ae.shape!=chg.shape or not np.all(np.isfinite(ae)):
                raise RuntimeError("invalid AECCAR")
            st=grid.structure
            lattice=np.asarray(st.lattice.matrix,float)
            frac=np.asarray(st.frac_coords,float)
            symbols=[s.specie.symbol for s in st]
            S=b1.Solver(a.bader,lattice,frac,symbols,chg.shape,work)
            qref,lflat=S(chg,ae)
            labels=qb.label_grid_from_fortran_flat(lflat,chg.shape)
            side=qb.side_channel_from_field(chg,labels)
            side_bytes=len(side.to_bytes())

            wp=read_csv(a.repo_root/"analysis/extensions_20260930/WP-G/rows.csv")
            base_row,base_cr,base_linf=baseline_for(mid,wp,int(chg.nbytes))

            for rr in [r for r in wp if r["material_id"]==mid and r["status"]=="OK"]:
                rec,nb=b1.rebuild("P",rr,chg,None,labels,side,core,work)
                fm=qb.field_metrics(chg,rec)
                cm=qb.closure_metrics(chg,rec,labels)
                total=int(nb)+side_bytes
                result["projected_rows"].append({
                    "codec":rr["codec"],
                    "nominal_tolerance_relative":float(rr["nominal_tolerance_relative"]),
                    "nominal_tolerance_absolute":float(rr["nominal_tolerance_absolute"]),
                    "payload_bytes":int(nb),
                    "side_channel_bytes":side_bytes,
                    "total_bytes":total,
                    "compression_ratio":chg.nbytes/total,
                    **fm,**cm,
                })

            valid=[
                r for r in result["projected_rows"]
                if r["final_Linf"]<=KAPPA*base_linf
                and r["max_rel_region_sum_error_scaled"]<=1e-9
            ]
            if not valid:
                raise RuntimeError("no projected candidate satisfies frozen kappa=4 contract")
            cand=max(valid,key=lambda r:r["compression_ratio"])

            rr={
                "codec":cand["codec"],
                "nominal_tolerance_relative":str(cand["nominal_tolerance_relative"]),
                "nominal_tolerance_absolute":str(cand["nominal_tolerance_absolute"]),
            }
            rec,nb=b1.rebuild("P",rr,chg,None,labels,side,core,work)
            q,lab=S(rec,ae)
            actual_error=float(np.max(np.abs(q-qref)))
            reassigned=float(np.mean(lab!=lflat))

            result["candidate"]={
                **cand,
                "kappa":KAPPA,
                "baseline_codec":base_row["codec"],
                "baseline_nominal_tolerance_relative":float(base_row["nominal_tolerance_relative"]),
                "baseline_cr":base_cr,
                "baseline_Linf":base_linf,
                "cr_ratio_over_baseline":cand["compression_ratio"]/base_cr,
                "linf_ratio_over_baseline":cand["final_Linf"]/base_linf,
                "side_channel_fraction":side_bytes/cand["total_bytes"],
                "actual_bader_error_e":actual_error,
                "actual_reassigned_frac":reassigned,
            }
            result.update({
                "npoints":int(chg.size),
                "natoms":len(symbols),
                "nlabels":int(side.sums.size),
                "max_partition_label":int(labels.max()),
                "side_channel_bytes":side_bytes,
                "bader_solves":S.n,
            })
    except Exception as e:
        import traceback
        result["status"]="FAILED"
        result["failures"].append({"error":f"{type(e).__name__}: {e}"})
        result["traceback"]=traceback.format_exc()
    result["wall_seconds"]=time.time()-t0
    return result


def main():
    a=parse_args()
    if a.shard_count<=0 or not 0<=a.shard_index<a.shard_count:
        raise SystemExit("invalid shard")
    a.repo_root=a.repo_root.resolve()
    frozen=a.frozen_root.resolve()
    out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    manifest=read_csv(a.holdout_manifest)
    if len(manifest)!=38:
        raise RuntimeError(f"expected 38 frozen holdout materials, got {len(manifest)}")

    sys.path.insert(0,str(frozen/"validation"))
    sys.path.insert(0,str(a.repo_root/"validation"/"qsq_prospective"))
    import external_end_to_end as core
    import development_compatibility_smoke as dev

    planned=[m for i,m in enumerate(manifest) if i%a.shard_count==a.shard_index]
    summary=[]
    rc=0
    for meta in planned:
        z=process(meta,a,core,dev)
        (out/f"{meta['material_id']}.json").write_text(json.dumps(z,indent=2)+"\n",encoding="utf-8")
        summary.append({"material_id":meta["material_id"],"status":z["status"]})
        print("QOAC_B2_CONFIRM_DONE",meta["material_id"],z["status"],"ratio",None if not z.get("candidate") else z["candidate"]["cr_ratio_over_baseline"],flush=True)
        if z["status"]!="SUCCESS": rc=1
    (out/f"planned_shard_{a.shard_index:02d}.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return rc

if __name__=="__main__":
    raise SystemExit(main())
